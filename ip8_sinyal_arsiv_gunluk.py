#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ip8_sinyal_arsiv_gunluk.py
===========================
IP-8 Sektor Rotasyon Motoru'nun gunluk JSON webhook ciktisini arsivler ve
ileri getiriyi (1/3/5/10/20 gun) olcer. V162'nin sinyal_arsiv_gunluk.py
mimarisine paralel calisir, ama SEKTOR bazlidir (33 hisse, 11 sektor).

MIMARI:
  1. Pine script'ten gelen webhook payload'lari (IP8_GUNLUK_SEKTOR_OZET tipi)
     bir yerde JSONL (satir-satir JSON) olarak biriktirilmis olmali - orn.
     webhook_inbox/ip8_raw.jsonl. Bu script o dosyayi okuyup arsive islerken
     her sektor-gun kaydini AYRI bir satir olarak data/ip8_sinyal_arsiv.json
     icine yazar.
  2. Yeterli gun gectiginde (>=1/3/5/10/20 islem gunu), lider hissenin ve
     XU100'un o tarihten sonraki fiyatlarini cekip ileri getiriyi hesaplar,
     ayni kaydi GUNCELLER (dogrulama_durumu: BEKLIYOR -> DOGRULANDI).
  3. Fiyat cekme fonksiyonu (get_price_series) BURADA BIR STUB - sizin
     bist-veri pipeline'inizdaki MEVCUT fiyat cekme mekanizmasina (fetch_
     bist.py veya esdegeri) BAGLANMALI. Asagida acikca isaretlendi.

KULLANIM:
  python3 ip8_sinyal_arsiv_gunluk.py --ingest    # yeni webhook'lari isle
  python3 ip8_sinyal_arsiv_gunluk.py --dogrula    # olgunlasan sinyalleri dogrula
  python3 ip8_sinyal_arsiv_gunluk.py --ingest --dogrula   # ikisi birden (varsayilan gunluk calisma)
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# YOL AYARLARI - kendi bist-veri repo yapiniza gore duzenleyin
# ============================================================
REPO_KOK = Path(__file__).resolve().parent
WEBHOOK_INBOX = REPO_KOK / "webhook_inbox" / "ip8_raw.jsonl"   # ham webhook'lar (satir-satir JSON)
ARSIV_DOSYASI = REPO_KOK / "data" / "ip8_sinyal_arsiv.json"     # islenmis arsiv
ISLEM_GUNLERI_ILERI = [1, 3, 5, 10, 20]                          # olcum ufuklari


# ============================================================
# FIYAT CEKME - yfinance ile CALISIR HALDE (BIST hisseleri .IS uzantisiyla
# Yahoo Finance'te ucretsiz mevcut - dogrulandi: THYAO.IS, XU100.IS vb.)
# ============================================================
import time as _time

_FIYAT_CACHE = {}  # ayni calisma icinde tekrar tekrar cekmemek icin bellek-ici cache

def _yf_sembol(sembol: str) -> str:
    """IP-8'in kendi isimlerini (orn. 'XU100', 'THYAO') yfinance'in
    bekledigi '.IS' formatina cevirir."""
    if sembol.upper() == "XU100":
        return "XU100.IS"
    return f"{sembol.upper()}.IS"


def get_price_series(sembol: str, baslangic_tarih: str, bitis_tarih: str) -> dict:
    """
    sembol icin baslangic-bitis arasindaki GUNLUK KAPANIS fiyatlarini
    {tarih_str: kapanis_float} seklinde dondurur. yfinance kullanir.

    NOT: yfinance Yahoo Finance'in GECIKMELI/ucretsiz verisidir - kesin
    dogruluk icin (ozellikle T+1 acilis/VWAP giris fiyatlari gibi hassas
    olcumler icin) ileride TradeMaster/Matriks gibi birincil kaynaginizla
    CAPRAZ KONTROL etmenizi oneririm. Baslangic icin (isabet oranı /
    fazla getiri YONU olcumu) yfinance'in gunluk kapanis hassasiyeti
    yeterlidir.
    """
    cache_anahtar = (sembol, baslangic_tarih, bitis_tarih)
    if cache_anahtar in _FIYAT_CACHE:
        return _FIYAT_CACHE[cache_anahtar]

    import yfinance as yf
    yf_sembol = _yf_sembol(sembol)

    for deneme in range(3):  # yfinance ara sira gecici hata verebiliyor, 3 deneme
        try:
            df = yf.download(
                yf_sembol,
                start=baslangic_tarih,
                end=bitis_tarih,
                progress=False,
                auto_adjust=False,
            )
            break
        except Exception as e:
            if deneme == 2:
                print(f"UYARI: {yf_sembol} icin fiyat cekilemedi: {e}")
                return {}
            _time.sleep(2)

    if df is None or df.empty:
        print(f"UYARI: {yf_sembol} icin veri bos dondu.")
        return {}

    sonuc = {}
    for tarih_idx, satir in df.iterrows():
        tarih_str = tarih_idx.strftime("%Y-%m-%d")
        kapanis = float(satir["Close"]) if "Close" in satir else float(satir["Close"].iloc[0])
        sonuc[tarih_str] = kapanis

    _FIYAT_CACHE[cache_anahtar] = sonuc
    return sonuc


def n_islem_gunu_sonrasi_fiyat(fiyat_serisi: dict, sinyal_tarihi: str, n: int):
    """fiyat_serisi icindeki tarihleri siralayip sinyal_tarihi'nden N ISLEM
    GUNU sonraki kapanisi dondurur. Yetersizse None doner (henuz olgunlasmamis)."""
    tarihler = sorted(fiyat_serisi.keys())
    if sinyal_tarihi not in tarihler:
        return None
    idx = tarihler.index(sinyal_tarihi)
    hedef_idx = idx + n
    if hedef_idx >= len(tarihler):
        return None
    return fiyat_serisi[tarihler[hedef_idx]]


# ============================================================
# ARSIV OKUMA/YAZMA
# ============================================================
def arsiv_yukle() -> dict:
    if ARSIV_DOSYASI.exists():
        with open(ARSIV_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"versiyon": "ip8-v1", "kayitlar": []}


def arsiv_kaydet(arsiv: dict):
    ARSIV_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    with open(ARSIV_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(arsiv, f, ensure_ascii=False, indent=1)


# ============================================================
# 1) INGEST - webhook inbox'taki gunluk ozet JSON'larini sektor bazinda
#    ayri kayitlara bolup arsive ekler (henuz arside yoksa)
# ============================================================
def ingest():
    if not WEBHOOK_INBOX.exists():
        print(f"UYARI: {WEBHOOK_INBOX} bulunamadi - islenecek yeni webhook yok.")
        return

    arsiv = arsiv_yukle()
    mevcut_anahtarlar = {
        (k["tarih"], k["sektor"]) for k in arsiv["kayitlar"]
    }

    yeni_sayisi = 0
    with open(WEBHOOK_INBOX, "r", encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            try:
                payload = json.loads(satir)
            except json.JSONDecodeError:
                continue
            if payload.get("tip") != "IP8_GUNLUK_SEKTOR_OZET":
                continue

            tarih = payload["tarih"]
            rejim = payload.get("rejim")
            breadth_ham = payload.get("breadthYumusatilmamis")
            xu_kapanis = payload.get("xuKapanis")
            xu_gunluk_getiri = payload.get("xuGunlukGetiri")
            isinma_tamam = payload.get("isinmaTamamMi")
            kesitsel_kapsam = payload.get("kesitselKapsam")

            for sek in payload.get("sektorler", []):
                anahtar = (tarih, sek["sektor"])
                if anahtar in mevcut_anahtarlar:
                    continue  # zaten arsivde

                kayit = {
                    "tarih": tarih,
                    "sektor": sek["sektor"],
                    "rejim": rejim,
                    "breadthHam": breadth_ham,
                    "xuKapanis": xu_kapanis,
                    "xuGunlukGetiri": xu_gunluk_getiri,
                    "isinmaTamamMi": isinma_tamam,
                    "kesitselKapsam": kesitsel_kapsam,
                    "srs": sek.get("srs"),
                    "srsAdj": sek.get("srsAdj"),
                    "evre": sek.get("evre"),
                    "eqs": sek.get("eqs"),
                    "eqsAdj": sek.get("eqsAdj"),
                    "aksiyon": sek.get("aksiyon"),
                    "guven": sek.get("guven"),
                    "gecerliUye": sek.get("gecerliUye"),
                    "lider": sek.get("lider"),
                    "liderSkor": sek.get("liderSkor"),
                    "liderGunlukPct": sek.get("liderGunlukPct"),
                    "delta1": sek.get("delta1"),
                    "delta3": sek.get("delta3"),
                    "ret5Pct": sek.get("ret5Pct"),
                    "breadthSektorHam": sek.get("breadthHam"),
                    "breadthSektorYumus": sek.get("breadthYumus"),
                    # Dogrulama alanlari - baslangicta bos, dogrula() doldurur
                    "dogrulama_durumu": "BEKLIYOR",
                    "lider_fiyat_sinyal_gunu": None,
                    "ileri_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},
                    "xu100_ileri_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},
                    "fazla_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},
                }
                arsiv["kayitlar"].append(kayit)
                mevcut_anahtarlar.add(anahtar)
                yeni_sayisi += 1

    arsiv_kaydet(arsiv)
    print(f"Ingest tamamlandi: {yeni_sayisi} yeni sektor-gun kaydi eklendi. "
          f"Toplam arsiv: {len(arsiv['kayitlar'])} kayit.")


# ============================================================
# 2) DOGRULA - yeterince gun gecmis kayitlarda ileri getiriyi hesaplar
#    Not: GIR/TEYIT BEKLE disindaki (BEKLE/KACIN) sinyaller icin de ileri
#    getiri OLCULUR (karsilastirma/kontrol grubu olarak deger tasir - "biz
#    KACIN dedik, gercekten dustu mu" sorusunu cevaplamak icin).
# ============================================================
def dogrula():
    arsiv = arsiv_yukle()
    bugun = datetime.now().strftime("%Y-%m-%d")

    # Hangi sembollerin fiyat serisine ihtiyacimiz var, toplu cekelim
    gerekli_semboller = set()
    for k in arsiv["kayitlar"]:
        if k["dogrulama_durumu"] == "BEKLIYOR" and k.get("lider") and k["lider"] != "LIDER YOK":
            gerekli_semboller.add(k["lider"])
    gerekli_semboller.add("XU100")

    fiyat_cache = {}
    for sem in gerekli_semboller:
        try:
            fiyat_cache[sem] = get_price_series(sem, "2026-01-01", bugun)
        except NotImplementedError as e:
            print(f"HATA: {e}")
            sys.exit(1)

    guncellenen = 0
    for k in arsiv["kayitlar"]:
        if k["dogrulama_durumu"] != "BEKLIYOR":
            continue
        lider = k.get("lider")
        if not lider or lider == "LIDER YOK":
            # lider yoksa sadece SEKTOR REJIMI/EVRESI dogrulanabilir - fiyat
            # bazli ileri getiri olculemez, KAPSAM_DISI isaretle
            k["dogrulama_durumu"] = "KAPSAM_DISI_LIDER_YOK"
            continue

        lider_fiyatlar = fiyat_cache.get(lider, {})
        xu_fiyatlar = fiyat_cache.get("XU100", {})
        if k["tarih"] not in lider_fiyatlar or k["tarih"] not in xu_fiyatlar:
            continue  # bu sembol icin veri henuz yok, bir sonraki calismada tekrar denenir

        sinyal_fiyat = lider_fiyatlar[k["tarih"]]
        sinyal_xu = xu_fiyatlar[k["tarih"]]
        k["lider_fiyat_sinyal_gunu"] = sinyal_fiyat

        tumu_olgunlasti = True
        for n in ISLEM_GUNLERI_ILERI:
            ileri_fiyat = n_islem_gunu_sonrasi_fiyat(lider_fiyatlar, k["tarih"], n)
            ileri_xu = n_islem_gunu_sonrasi_fiyat(xu_fiyatlar, k["tarih"], n)
            if ileri_fiyat is None or ileri_xu is None:
                tumu_olgunlasti = False
                continue
            getiri = (ileri_fiyat / sinyal_fiyat - 1) * 100
            xu_getiri = (ileri_xu / sinyal_xu - 1) * 100
            k["ileri_getiri"][str(n)] = round(getiri, 3)
            k["xu100_ileri_getiri"][str(n)] = round(xu_getiri, 3)
            k["fazla_getiri"][str(n)] = round(getiri - xu_getiri, 3)

        if tumu_olgunlasti:
            k["dogrulama_durumu"] = "DOGRULANDI"
            guncellenen += 1

    arsiv_kaydet(arsiv)
    print(f"Dogrulama tamamlandi: {guncellenen} kayit tam olgunlasip DOGRULANDI "
          f"olarak isaretlendi.")


# ============================================================
# 3) OZET RAPOR - aksiyon turune gore isabet/ortalama fazla getiri
#    (M7 tarzi, V162'deki hafta_denetim.py'ye benzer mantik)
# ============================================================
def ozet_rapor():
    arsiv = arsiv_yukle()
    dogrulanan = [k for k in arsiv["kayitlar"] if k["dogrulama_durumu"] == "DOGRULANDI"]
    if not dogrulanan:
        print("Henuz DOGRULANDI durumunda kayit yok.")
        return

    print(f"{'Aksiyon':<20}{'n':>5}{'T+1 FazlaGet':>14}{'T+5 FazlaGet':>14}{'T+20 FazlaGet':>15}{'Isabet(T+5>0)':>16}")
    aksiyonlar = sorted(set(k["aksiyon"] for k in dogrulanan))
    for aks in aksiyonlar:
        alt = [k for k in dogrulanan if k["aksiyon"] == aks]
        n = len(alt)
        def ort(gun):
            degerler = [k["fazla_getiri"][str(gun)] for k in alt if k["fazla_getiri"][str(gun)] is not None]
            return sum(degerler) / len(degerler) if degerler else float("nan")
        isabet5 = [k["fazla_getiri"]["5"] for k in alt if k["fazla_getiri"]["5"] is not None]
        isabet_oran = (sum(1 for x in isabet5 if x > 0) / len(isabet5) * 100) if isabet5 else float("nan")
        print(f"{aks:<20}{n:>5}{ort(1):>14.2f}{ort(5):>14.2f}{ort(20):>15.2f}{isabet_oran:>15.1f}%")


# ============================================================
# ANA CALISMA
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IP-8 sektor sinyal arsivi ve dogrulama")
    parser.add_argument("--ingest", action="store_true", help="webhook inbox'i arsive isle")
    parser.add_argument("--dogrula", action="store_true", help="olgunlasan sinyalleri dogrula")
    parser.add_argument("--ozet", action="store_true", help="aksiyon-bazli ozet rapor yazdir")
    args = parser.parse_args()

    if not (args.ingest or args.dogrula or args.ozet):
        # varsayilan: hepsini sirayla calistir (gunluk cron kullanim senaryosu)
        ingest()
        dogrula()
        ozet_rapor()
    else:
        if args.ingest:
            ingest()
        if args.dogrula:
            dogrula()
        if args.ozet:
            ozet_rapor()
