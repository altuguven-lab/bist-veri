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
WEBHOOK_INBOX = REPO_KOK / "webhook_inbox" / "ip8_raw.jsonl"   # ham webhook'lar (satir-satir JSON) - ARTIK KULLANILMIYOR, bkz. GITHUB_KAYNAK
# 14.09 DUZELTME: gercek mimari yerel dosya degil - Pipedream, V162'nin
# tv_alerts_latest.json'una PARALEL sekilde data/ip8_sinyal_latest.json'a
# GitHub uzerinden yaziyor (bkz. ip8_pipedream_kod_adimi.js). ingest()
# artik bu GitHub dosyasini okuyor.
GITHUB_OWNER = "altuguven-lab"
GITHUB_REPO = "bist-veri"
GITHUB_IP8_YOL = "data/ip8_sinyal_latest.json"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/{GITHUB_IP8_YOL}"
ARSIV_DOSYASI = REPO_KOK / "data" / "ip8_sinyal_arsiv.json"     # islenmis arsiv
ISLEM_GUNLERI_ILERI = [1, 3, 5, 10, 20]                          # olcum ufuklari

# 15.09 EKLENTI (denetim - "Model ve lider performansı ayrılmalı"): Pine
# kaynagindaki (IP8_FAZ03A.pine) KANONIK sektor uyeligiyle BIREBIR ayni -
# sektorun esit-agirlikli GERCEK getirisini olcebilmek icin gerekli.
SEKTOR_UYELERI = {
    "Banka": ["AKBNK", "GARAN", "YKBNK", "HALKB", "VAKBN"],
    "Holding": ["KCHOL", "SAHOL", "AGHOL"],
    "Savunma": ["ASELS", "OTKAR"],
    "Rafineri": ["TUPRS", "PETKM"],
    "EnerjiUretimi": ["ENJSA", "AKSEN"],
    "Elektrik": ["ASTOR", "KONTR", "ALFAS", "CWENE", "EUPWR", "GESAN"],
    "DemirCelik": ["EREGL", "KRDMD", "KCAER", "BRSAN"],
    "Otomotiv": ["FROTO", "TOASO"],
    "Tuketim": ["BIMAS", "MGROS", "ULKER"],
    "Telekom": ["TCELL", "TTKOM"],
    "Ulastirma": ["THYAO", "TAVHL"],
}


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
    """ESKI YONTEM - artik SADECE XU100'un kendi ileri fiyatini bulmak icin
    kullaniliyor (XU100 zaten referans takvimin kendisi oldugu icin guvenli).
    Diger tum sembollerde n_islem_gunu_sonrasi_tarih() + tarih bazli lookup
    kullanilmali (bkz. asagisi, denetim maddesi "ileri gun eslestirmesinde
    tarih riski")."""
    tarihler = sorted(fiyat_serisi.keys())
    if sinyal_tarihi not in tarihler:
        return None
    idx = tarihler.index(sinyal_tarihi)
    hedef_idx = idx + n
    if hedef_idx >= len(tarihler):
        return None
    return fiyat_serisi[tarihler[hedef_idx]]


def n_islem_gunu_sonrasi_tarih(xu_takvim: list, sinyal_tarihi: str, n: int):
    """15.09 EKLENTI (denetim maddesi 'ileri gun eslestirmesinde tarih
    riski'): HER sembol icin kendi takviminde N adim ilerlemek yerine,
    TEK BIR REFERANS TAKVIM (XU100'un islem gunleri) kullanip hedef TAKVIM
    TARIHINI belirliyoruz. Hedef hisse o G+N tarihinde islem gormemisse
    (tatil, gecici durdurma vb.) DIGER olcumlerle (XU100, diger sektor
    uyeleri) YANLIS hizalanmis bir gun karsilastirilmaz - o hisse icin
    sadece o tarihte veri var mi diye AYRICA kontrol edilir."""
    if sinyal_tarihi not in xu_takvim:
        return None
    idx = xu_takvim.index(sinyal_tarihi)
    hedef_idx = idx + n
    if hedef_idx >= len(xu_takvim):
        return None
    return xu_takvim[hedef_idx]


# ============================================================
# ARSIV OKUMA/YAZMA
# ============================================================
def arsiv_migrate(arsiv: dict) -> dict:
    """15.09 EKLENTI (denetim - KRITIK, dogrulanmis cokme): eski semali
    kayitlar ("dogrulama_durumu": "BEKLIYOR" gibi) yeni dogrula()
    fonksiyonunun bekledigi ("dogrulama": {"1":"BEKLIYOR",...}) yapisinda
    DEGILDI - calistirildiginda KeyError: 'dogrulama' ile COKUYORDU.
    Bu fonksiyon HER yuklemede otomatik calisir: eski semali kayitlari
    gunceller, unutulmus test kayitlarini temizler, versiyon damgasini
    ilerletir. Boylece elle GitHub'a girip JSON duzenlemeye GEREK KALMAZ."""
    arsiv.setdefault("ham_gunler", {})
    arsiv.setdefault("kayitlar", [])

    yeni_kayitlar = []
    for k in arsiv["kayitlar"]:
        # Unutulmus/eski test kayitlarini burada da temizle (ikinci guvenlik agi)
        if k.get("evre") == "TEST" or k.get("aksiyon") == "TEST" or k.get("lider") == "TESTHISSE":
            continue
        # Eski sema -> yeni sema donusumu
        if "dogrulama" not in k:
            k["dogrulama"] = {str(n): "BEKLIYOR" for n in ISLEM_GUNLERI_ILERI}
        if "lider_ileri_getiri" not in k:
            k["lider_ileri_getiri"] = {str(n): None for n in ISLEM_GUNLERI_ILERI}
        if "sektor_ileri_getiri" not in k:
            k["sektor_ileri_getiri"] = {str(n): None for n in ISLEM_GUNLERI_ILERI}
        if "lider_fazla_getiri" not in k:
            k["lider_fazla_getiri"] = {str(n): None for n in ISLEM_GUNLERI_ILERI}
        if "sektor_fazla_getiri" not in k:
            k["sektor_fazla_getiri"] = {str(n): None for n in ISLEM_GUNLERI_ILERI}
        if "lider_katkisi" not in k:
            k["lider_katkisi"] = {str(n): None for n in ISLEM_GUNLERI_ILERI}
        # Artik kullanilmayan eski alanlari temizle (opsiyonel, temiz tutmak icin)
        k.pop("dogrulama_durumu", None)
        k.pop("ileri_getiri", None)
        k.pop("fazla_getiri", None)
        yeni_kayitlar.append(k)

    arsiv["kayitlar"] = yeni_kayitlar
    arsiv["versiyon"] = "ip8-v2"
    return arsiv


def arsiv_yukle() -> dict:
    if ARSIV_DOSYASI.exists():
        with open(ARSIV_DOSYASI, "r", encoding="utf-8") as f:
            ham = json.load(f)
        return arsiv_migrate(ham)
    # 15.09 EKLENTI (denetim - "Ham veri ve normalize veri ayrılmalı"):
    # "ham_gunler" alani, GitHub'dan gelen her GUNUN TAM/HAM JSON'unu
    # (tarih -> orijinal payload) ayrica saklar. Boylece "kayitlar" (sektor
    # bazina bolunmus, normalize edilmis) yapisi ILERIDE degisirse/
    # duzeltilirse, orijinal veri KAYBOLMADAN yeniden islenebilir. (NOT:
    # GitHub'daki data/ip8_sinyal_latest.json zaten son 500 gunun hamini
    # tutuyor - bu, ayni verinin YEREL/YEDEKLI bir kopyasidir.)
    return {"versiyon": "ip8-v2", "kayitlar": [], "ham_gunler": {}}


def arsiv_kaydet(arsiv: dict):
    ARSIV_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    with open(ARSIV_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(arsiv, f, ensure_ascii=False, indent=1)


# ============================================================
# 1) INGEST - GitHub'daki data/ip8_sinyal_latest.json dosyasini (Pipedream'in
#    yazdigi, "gunluk_gecmis" dizisi iceren) okuyup sektor bazinda ayri
#    kayitlara boler, arsive ekler (henuz arside yoksa)
# ============================================================
def ingest():
    import urllib.request
    import urllib.error

    try:
        with urllib.request.urlopen(GITHUB_RAW_URL, timeout=20) as r:
            ham_metin = r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"UYARI: {GITHUB_RAW_URL} henuz yok - ilk webhook henuz "
                  f"GitHub'a yazilmamis olabilir (Pipedream kurulumunu kontrol edin).")
        else:
            print(f"HATA: GitHub'dan okuma basarisiz ({e.code}): {e}")
        return
    except Exception as e:
        print(f"HATA: GitHub'dan okuma basarisiz: {e}")
        return

    # 15.09 DUZELTME: dosya GitHub'da mevcut ama BOS/gecersiz JSON icerebilir
    # (orn. "sil" yerine yanlislikla icerigi bosaltip kaydetmek, ya da
    # raw.githubusercontent.com'un kisa sureli eski/bos onbellegi). Eskiden
    # bu durum cig gibi bir JSONDecodeError ile duruyordu - artik ayni
    # "henuz yok" mesajiyla ZARARSIZCA atlaniyor.
    if not ham_metin.strip():
        print(f"UYARI: {GITHUB_RAW_URL} BOS donuyor - dosya GitHub'da var ama "
              f"icerigi bos olabilir (yanlislikla icerik silinip 'sil' yerine "
              f"kaydedilmis olabilir) YA DA GitHub'in onbellegi henuz "
              f"guncellenmemis olabilir (birkac dakika sonra tekrar deneyin).")
        return
    try:
        dosya_icerik = json.loads(ham_metin)
    except json.JSONDecodeError as e:
        print(f"UYARI: {GITHUB_RAW_URL} icerigi GECERLI JSON DEGIL "
              f"(ilk 200 karakter: {ham_metin[:200]!r}). Dosyayi GitHub'da "
              f"elle kontrol edin.")
        return

    gunluk_gecmis = dosya_icerik.get("gunluk_gecmis", [])
    if not gunluk_gecmis:
        print("UYARI: gunluk_gecmis bos - islenecek gun yok.")
        return

    arsiv = arsiv_yukle()
    arsiv.setdefault("ham_gunler", {})  # eski arsiv dosyalarinda bu alan olmayabilir
    mevcut_anahtarlar = {
        (k["tarih"], k["sektor"]) for k in arsiv["kayitlar"]
    }

    yeni_sayisi = 0
    for gun_payload in gunluk_gecmis:
        tarih = gun_payload.get("tarih")
        if not tarih:
            continue

        # 15.09 EKLENTI: bu gunun TAM/HAM payload'unu ayrica sakla (sektor
        # bazina bolunmeden once) - ileride normalize mantigi degisirse
        # orijinal veriden yeniden turetilebilsin diye.
        arsiv["ham_gunler"].setdefault(tarih, gun_payload)

        rejim = gun_payload.get("rejim")
        breadth_ham = gun_payload.get("breadthYumusatilmamis")
        xu_kapanis = gun_payload.get("xuKapanis")
        xu_gunluk_getiri = gun_payload.get("xuGunlukGetiri")
        isinma_tamam = gun_payload.get("isinmaTamamMi")
        kesitsel_kapsam = gun_payload.get("kesitselKapsam")
        universe_versiyon = gun_payload.get("universeVersion")
        state_age_days = gun_payload.get("stateAgeDays")

        for sek in gun_payload.get("sektorler", []):
            anahtar = (tarih, sek["sektor"])
            if anahtar in mevcut_anahtarlar:
                continue  # zaten arsivde

            # 15.09 EKLENTI (denetim maddesi 3): TEST kayitlari (evre/aksiyon
            # "TEST" veya lider "TESTHISSE" olanlar) atlaniyor - boylece
            # gercek bir gunun ayni (tarih,sektor) anahtari "zaten var"
            # denilip yanlislikla es gecilmez. NOT: Pipedream tarafi da
            # (ip8_pipedream_kod_adimi.js) artik test payload'larini
            # gunluk_gecmis'e hic yazmiyor - bu ikinci bir guvenlik katmani.
            if sek.get("evre") == "TEST" or sek.get("aksiyon") == "TEST" or sek.get("lider") == "TESTHISSE":
                continue

            kayit = {
                "tarih": tarih,
                "sektor": sek["sektor"],
                "rejim": rejim,
                "breadthHam": breadth_ham,
                "xuKapanis": xu_kapanis,
                "xuGunlukGetiri": xu_gunluk_getiri,
                "isinmaTamamMi": isinma_tamam,
                "kesitselKapsam": kesitsel_kapsam,
                "universeVersion": universe_versiyon,
                "stateAgeDays": state_age_days,
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
                # 15.09 DUZELTME (denetim maddesi "Doğrulama durumu daha
                # ayrıntılı olmalı" + "Model ve lider performansı ayrılmalı"):
                # eskiden TEK bir "dogrulama_durumu" (hep-ya-da-hic, 20 gun
                # dolmadan hicbir sonuc gorunmuyordu) VE sadece LIDER hissenin
                # getirisi olculuyordu (sektor secimi ile lider secimi
                # birbirine karisiyordu). Artik:
                #  - her vade (1/3/5/10/20) AYRI ayri "BEKLIYOR"/"DOGRULANDI"
                #  - LIDER getirisi VE SEKTOR (esit agirlikli uye) getirisi
                #    AYRI olculuyor, boylece "sektor secimi mi dogru, lider
                #    secimi mi dogru" sorusu ayristirilabiliyor
                "dogrulama": {str(n): "BEKLIYOR" for n in ISLEM_GUNLERI_ILERI},
                "lider_fiyat_sinyal_gunu": None,
                "lider_ileri_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},
                "sektor_ileri_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},
                "xu100_ileri_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},
                "lider_fazla_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},   # lider - XU100
                "sektor_fazla_getiri": {str(n): None for n in ISLEM_GUNLERI_ILERI},  # sektor - XU100
                "lider_katkisi": {str(n): None for n in ISLEM_GUNLERI_ILERI},        # lider - sektor
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

    # 15.09 DUZELTME (denetim - "Model ve lider performansı ayrılmalı"):
    # artik sadece lider degil, o sektorun TUM UYELERI icin de fiyat
    # gerekiyor (esit-agirlikli sektor getirisini olcebilmek icin).
    guncellenmemis = [k for k in arsiv["kayitlar"] if any(
        k["dogrulama"][str(n)] == "BEKLIYOR" for n in ISLEM_GUNLERI_ILERI)]
    if not guncellenmemis:
        print("Tum kayitlar zaten tum vadelerde dogrulanmis.")
        return

    gerekli_semboller = {"XU100"}
    for k in guncellenmemis:
        lider = k.get("lider")
        if lider and lider != "LIDER YOK":
            gerekli_semboller.add(lider)
        for uye in SEKTOR_UYELERI.get(k["sektor"], []):
            gerekli_semboller.add(uye)

    fiyat_cache = {}
    for sem in gerekli_semboller:
        try:
            fiyat_cache[sem] = get_price_series(sem, "2026-01-01", bugun)
        except NotImplementedError as e:
            print(f"HATA: {e}")
            sys.exit(1)

    xu_fiyatlar = fiyat_cache.get("XU100", {})
    xu_takvim = sorted(xu_fiyatlar.keys())  # 15.09: TEK referans takvim

    guncellenen_kayit = 0
    for k in guncellenmemis:
        tarih = k["tarih"]
        if tarih not in xu_fiyatlar:
            continue  # XU100 icin bile veri yoksa bu gun henuz islenemez
        sinyal_xu = xu_fiyatlar[tarih]

        lider = k.get("lider")
        lider_var = lider and lider != "LIDER YOK"
        lider_fiyatlar = fiyat_cache.get(lider, {}) if lider_var else {}
        if lider_var and tarih in lider_fiyatlar:
            k["lider_fiyat_sinyal_gunu"] = lider_fiyatlar[tarih]

        uyeler = SEKTOR_UYELERI.get(k["sektor"], [])
        # Sektorun sinyal-gunundeki "baz" fiyatlarini (esit-agirlik icin
        # her uyenin KENDI sinyal-gunu fiyatina ihtiyac var) hazirla
        uye_sinyal_fiyat = {}
        for uye in uyeler:
            fs = fiyat_cache.get(uye, {})
            if tarih in fs:
                uye_sinyal_fiyat[uye] = fs[tarih]

        herhangi_biri_guncellendi = False
        for n in ISLEM_GUNLERI_ILERI:
            if k["dogrulama"][str(n)] == "DOGRULANDI":
                continue  # bu vade zaten olgunlasmis, tekrar hesaplama

            # 15.09: hedef TAKVIM TARIHI, XU100 referansindan belirleniyor -
            # her sembolun kendi eksik-gun'lerinden BAGIMSIZ tek bir "G+N"
            hedef_tarih = n_islem_gunu_sonrasi_tarih(xu_takvim, tarih, n)
            if hedef_tarih is None:
                continue  # XU100'de bile henuz o kadar gun gecmemis

            # XU100 ileri getiri (referans oldugu icin her zaman mevcut)
            if hedef_tarih not in xu_fiyatlar:
                continue
            xu_ileri = xu_fiyatlar[hedef_tarih]
            xu_getiri = (xu_ileri / sinyal_xu - 1) * 100
            k["xu100_ileri_getiri"][str(n)] = round(xu_getiri, 3)

            # LIDER ileri getiri (o TAM takvim tarihinde lider islem
            # gormemisse None kalir - farkli bir gunle YANLIS hizalanmaz)
            if lider_var and tarih in lider_fiyatlar and hedef_tarih in lider_fiyatlar:
                lider_getiri = (lider_fiyatlar[hedef_tarih] / lider_fiyatlar[tarih] - 1) * 100
                k["lider_ileri_getiri"][str(n)] = round(lider_getiri, 3)
                k["lider_fazla_getiri"][str(n)] = round(lider_getiri - xu_getiri, 3)

            # SEKTOR esit-agirlikli ileri getiri (LIDER YOK olsa BILE
            # hesaplanabilir - sektor secimi lider seciminden bagimsiz
            # olculebilsin diye)
            uye_getirileri = []
            for uye, baz_fiyat in uye_sinyal_fiyat.items():
                fs = fiyat_cache.get(uye, {})
                if hedef_tarih in fs:
                    uye_getirileri.append((fs[hedef_tarih] / baz_fiyat - 1) * 100)
            if uye_getirileri:
                sektor_getiri = sum(uye_getirileri) / len(uye_getirileri)
                k["sektor_ileri_getiri"][str(n)] = round(sektor_getiri, 3)
                k["sektor_fazla_getiri"][str(n)] = round(sektor_getiri - xu_getiri, 3)
                if lider_var and k["lider_ileri_getiri"][str(n)] is not None:
                    k["lider_katkisi"][str(n)] = round(
                        k["lider_ileri_getiri"][str(n)] - sektor_getiri, 3)

            # 15.09: bu VADE icin "DOGRULANDI" - en az sektor getirisi
            # hesaplanabildiyse yeterli (lider yoksa bile sektor olculur)
            if uye_getirileri:
                k["dogrulama"][str(n)] = "DOGRULANDI"
                herhangi_biri_guncellendi = True

        if herhangi_biri_guncellendi:
            guncellenen_kayit += 1

    arsiv_kaydet(arsiv)
    print(f"Dogrulama tamamlandi: {guncellenen_kayit} kayitta en az bir vade guncellendi.")


# ============================================================
# 3) OZET RAPOR - aksiyon turune gore isabet/ortalama fazla getiri
#    (M7 tarzi, V162'deki hafta_denetim.py'ye benzer mantik)
#    15.09 DUZELTME: artik SEKTOR ve LIDER getirisi AYRI raporlaniyor, ve
#    her vade (1/3/5/10/20) kendi olgunlastigi anda goruluyor - 20 gun
#    dolmasini beklemeye gerek yok.
# ============================================================
def ozet_rapor():
    arsiv = arsiv_yukle()
    if not arsiv["kayitlar"]:
        print("Arsiv bos.")
        return

    print(f"{'Aksiyon':<20}{'Vade':>5}{'n':>5}{'SektorFazlaGet':>16}{'LiderFazlaGet':>15}{'LiderKatkisi':>14}{'SektorIsabet%':>15}")
    aksiyonlar = sorted(set(k["aksiyon"] for k in arsiv["kayitlar"] if k.get("aksiyon")))
    for aks in aksiyonlar:
        alt = [k for k in arsiv["kayitlar"] if k["aksiyon"] == aks]
        for n in ISLEM_GUNLERI_ILERI:
            sektor_degerler = [k["sektor_fazla_getiri"][str(n)] for k in alt if k["sektor_fazla_getiri"][str(n)] is not None]
            lider_degerler = [k["lider_fazla_getiri"][str(n)] for k in alt if k["lider_fazla_getiri"][str(n)] is not None]
            katki_degerler = [k["lider_katkisi"][str(n)] for k in alt if k["lider_katkisi"][str(n)] is not None]
            if not sektor_degerler and not lider_degerler:
                continue
            n_sayisi = len(sektor_degerler) if sektor_degerler else len(lider_degerler)
            sek_ort = sum(sektor_degerler) / len(sektor_degerler) if sektor_degerler else float("nan")
            lid_ort = sum(lider_degerler) / len(lider_degerler) if lider_degerler else float("nan")
            katki_ort = sum(katki_degerler) / len(katki_degerler) if katki_degerler else float("nan")
            isabet = (sum(1 for x in sektor_degerler if x > 0) / len(sektor_degerler) * 100) if sektor_degerler else float("nan")
            print(f"{aks:<20}{('T+'+str(n)):>5}{n_sayisi:>5}{sek_ort:>16.2f}{lid_ort:>15.2f}{katki_ort:>14.2f}{isabet:>14.1f}%")


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
