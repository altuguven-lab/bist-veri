"""
sqz_skoru.py — FAZ V2 (SQZ SKORU)

VIOP ENTEGRASYON PROMPTU'nda (13.07.2026) ONCEDEN KILITLENMIS formulun
UYGULAMASI - burada yeni bir formul TASARLANMIYOR, sadece o gun yazilan
formul kodlaniyor. Kirmizi cizgi (18.08.2026) gecti, FAZ V2 baslayabilir.

SQZ (0-100) = 30 x iskonto_derinligi (baz_z negatif bolge, kirpilmis)
            + 25 x OI_yuzdeligi (90g pencere)
            + 20 x kadran_puani (fiyat-yatay/OI-artan=tam, fiyat-dusen/
              OI-artan=yarim, digerleri 0)
            + 15 x spot_guc (20g goreli guc yuzdeligi, evren-ici)
            + 10 x tetik (spot hacimli yukari gun + dOI negatif)
Esikler: SQZ>=65 "SIKISMA ADAYI", >=80 "KURULU". Gunluk en cok 3 aday.

KIRMIZI CIZGI (degismez): bu skor hicbir alertcondition/portfoy/islem
dosyasina baglanmaz - SADECE gozlem. Plan geregi: "gercek veride ilk
hafta yalniz GOZLEM". Formul agirliklari SONUCA BAKILMADAN kilitlendi
(13.07 tarihli, veri gorulmeden yazildi) - bu betik onu bozmadan
uyguluyor.

VERI YETERSIZLIGI: baz_z ve OI_yuzdeligi icin en az MIN_GECMIS_GUN
(20) gunluk seri gerekir - azsa o bilesen 0 verilmez, tum SKOR
"VERI_YETERSIZ" olarak isaretlenir (0 vermek yanlis dusuk skor
uretir, en dogrusu sonucu hic uretmemek).
"""
import datetime
import json
import os
import statistics
import sys

import yfinance as yf

from json_atomik_yaz import atomik_json_yaz

VIOP_YOL = "data/viop_analiz.json"
SERI_YOL = "data/viop_seri.json"
CIKTI_YOL = "data/sqz_skoru.json"
MIN_GECMIS_GUN = 20
SERI_TUTMA_GUN = 90
GUNLUK_AZAMI_ADAY = 3
ESIK_ADAY = 65
ESIK_KURULU = 80


def _en_yakin_futures(sembol_veri):
    fut = [x for x in sembol_veri.get("sozlesmeler", []) if x["sozlesme_turu"] == "FUTURES"]
    return fut[0] if fut else None


def _sayiya_cevir(deger):
    """VIOP CSV'sinden gelen ACIK POZISYON gibi alanlar bazen string
    bazen sayi olarak geliyor - guvenli sekilde int/float'a cevirir,
    olmuyorsa None doner (sessizce yanlis tip birakmaz)."""
    if deger is None:
        return None
    if isinstance(deger, (int, float)):
        return deger
    try:
        s = str(deger).strip().replace(",", ".")
        return float(s) if "." in s else int(s)
    except (TypeError, ValueError):
        return None


def _seri_guncelle(viop, bugun_str):
    """Bugunku baz/OI degerlerini seriye ekler (varsa UZERINE YAZMAZ -
    ayni gun tekrar calisirsa idempotent olsun diye once kontrol eder)."""
    try:
        with open(SERI_YOL, encoding="utf-8") as f:
            seri = json.load(f)
    except FileNotFoundError:
        seri = {"semboller": {}}

    for sem, veri in viop["semboller"].items():
        fut = _en_yakin_futures(veri)
        if fut is None or fut.get("baz_yuzde_ham") is None:
            continue
        oi = _sayiya_cevir(fut.get("acik_pozisyon"))
        doi = _sayiya_cevir(fut.get("acik_pozisyon_degisim"))
        gecmis = seri["semboller"].setdefault(sem, [])
        if gecmis and gecmis[-1]["gun"] == bugun_str:
            gecmis[-1] = {"gun": bugun_str, "baz_yuzde": fut["baz_yuzde_ham"],
                          "oi": oi, "doi": doi}
        else:
            gecmis.append({"gun": bugun_str, "baz_yuzde": fut["baz_yuzde_ham"],
                           "oi": oi, "doi": doi})
        seri["semboller"][sem] = gecmis[-SERI_TUTMA_GUN:]

    seri["son_guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    atomik_json_yaz(SERI_YOL, seri)
    return seri


def _baz_z_hesapla(gecmis):
    """Son kayit haric onceki en cok 60 gunun ortalama/std'sine gore z-skor."""
    if len(gecmis) < MIN_GECMIS_GUN:
        return None
    onceki = [g["baz_yuzde"] for g in gecmis[:-1][-60:] if g.get("baz_yuzde") is not None]
    if len(onceki) < MIN_GECMIS_GUN - 1:
        return None
    ort = statistics.mean(onceki)
    std = statistics.stdev(onceki) if len(onceki) > 1 else 0
    if std == 0:
        return None
    return (gecmis[-1]["baz_yuzde"] - ort) / std


def _oi_yuzdelik_hesapla(gecmis):
    if len(gecmis) < MIN_GECMIS_GUN:
        return None
    tum_oi = [g["oi"] for g in gecmis if g.get("oi") is not None]
    if len(tum_oi) < MIN_GECMIS_GUN:
        return None
    bugun_oi = gecmis[-1]["oi"]
    if bugun_oi is None:
        return None
    altinda = sum(1 for x in tum_oi if x <= bugun_oi)
    return 100.0 * altinda / len(tum_oi)


def _fiyat_verisi_cek(semboller, gun_sayisi=30):
    """Kadran ve spot_guc icin son ~30 is gunu kapanis+hacim ceker."""
    veri = {}
    bugun = datetime.date.today()
    baslangic = (bugun - datetime.timedelta(days=gun_sayisi * 2)).isoformat()
    bitis = (bugun + datetime.timedelta(days=1)).isoformat()
    for sem in semboller:
        try:
            df = yf.Ticker(f"{sem}.IS").history(start=baslangic, end=bitis, interval="1d")
            if not df.empty:
                veri[sem] = df
        except Exception as e:
            print(f"UYARI: {sem} fiyat verisi cekilemedi: {e}", file=sys.stderr)
    return veri


def _kadran_puani(df):
    """fiyat-yatay/OI-artan=100, fiyat-dusen/OI-artan=50, digerleri=0.
    Bu fonksiyon SADECE fiyat tarafini donuyor (OI-artan disaridan and'lenir)."""
    if df is None or len(df) < 6:
        return None, None
    son5 = df["Close"].tail(6).tolist()
    degisim_pct = (son5[-1] / son5[0] - 1) * 100
    if abs(degisim_pct) < 1.0:
        return "YATAY", degisim_pct
    elif degisim_pct < -1.0:
        return "DUSEN", degisim_pct
    else:
        return "YUKSELEN", degisim_pct


def _spot_guc_yuzdelikleri(fiyat_verisi):
    """20 gunluk getiriye gore EVREN-ICI yuzdelik (cross-sectional rank)."""
    getiriler = {}
    for sem, df in fiyat_verisi.items():
        if len(df) < 21:
            continue
        kapaniclar = df["Close"].tolist()
        getiriler[sem] = kapaniclar[-1] / kapaniclar[-21] - 1
    if len(getiriler) < 5:
        return {}
    siralanan = sorted(getiriler.items(), key=lambda x: x[1])
    n = len(siralanan)
    return {sem: 100.0 * i / (n - 1) for i, (sem, _) in enumerate(siralanan)}


def _tetik_kontrol(df, doi):
    """spot hacimli yukari gun + dOI negatif = kapatma basladi isareti."""
    if df is None or len(df) < 21 or doi is None:
        return None
    son_hacim = df["Volume"].iloc[-1]
    ort_hacim = df["Volume"].tail(21).iloc[:-1].mean()
    son_degisim = df["Close"].iloc[-1] / df["Close"].iloc[-2] - 1
    hacimli_yukari = son_hacim > ort_hacim * 1.3 and son_degisim > 0
    return bool(hacimli_yukari and doi < 0)


def main():
    try:
        with open(VIOP_YOL, encoding="utf-8") as f:
            viop = json.load(f)
    except FileNotFoundError:
        print(f"HATA: {VIOP_YOL} yok, once fetch_viop.py calismali", file=sys.stderr)
        sys.exit(1)

    bugun_str = viop["bulten_gunu"]
    seri = _seri_guncelle(viop, bugun_str)

    semboller = list(viop["semboller"].keys())
    fiyat_verisi = _fiyat_verisi_cek(semboller)
    spot_guc = _spot_guc_yuzdelikleri(fiyat_verisi)

    sonuclar = {}
    for sem, veri in viop["semboller"].items():
        fut = _en_yakin_futures(veri)
        if fut is None:
            continue
        gecmis = seri["semboller"].get(sem, [])

        baz_z = _baz_z_hesapla(gecmis)
        oi_yuzdelik = _oi_yuzdelik_hesapla(gecmis)
        if baz_z is None or oi_yuzdelik is None:
            sonuclar[sem] = {"durum": "VERI_YETERSIZ",
                             "gecmis_gun_sayisi": len(gecmis),
                             "gereken_asgari": MIN_GECMIS_GUN}
            continue

        df = fiyat_verisi.get(sem)
        yon, degisim_pct = _kadran_puani(df)
        doi = _sayiya_cevir(fut.get("acik_pozisyon_degisim"))
        oi_artan = doi is not None and doi > 0

        if yon == "YATAY" and oi_artan:
            kadran_puan = 100.0
        elif yon == "DUSEN" and oi_artan:
            kadran_puan = 50.0
        else:
            kadran_puan = 0.0

        iskonto_puan = max(0.0, min(3.0, -baz_z)) / 3.0 * 100.0
        spot_guc_puan = spot_guc.get(sem, 50.0)  # veri yoksa notr 50
        tetik = _tetik_kontrol(df, doi)
        tetik_puan = 100.0 if tetik else 0.0

        sqz = (0.30 * iskonto_puan + 0.25 * oi_yuzdelik + 0.20 * kadran_puan
               + 0.15 * spot_guc_puan + 0.10 * tetik_puan)
        sqz = round(sqz, 1)

        etiket = "KURULU" if sqz >= ESIK_KURULU else "SIKISMA ADAYI" if sqz >= ESIK_ADAY else None

        sonuclar[sem] = {
            "durum": "HESAPLANDI", "sqz_skoru": sqz, "etiket": etiket,
            "baz_z": round(baz_z, 3), "oi_yuzdeligi": round(oi_yuzdelik, 1),
            "kadran": yon, "kadran_puani": kadran_puan,
            "fiyat_degisim_5g_pct": round(degisim_pct, 2) if degisim_pct is not None else None,
            "spot_guc_yuzdeligi": round(spot_guc_puan, 1),
            "tetik": tetik, "dOI": doi,
        }

    # Gunluk en cok 3 aday (gurultu tavani) - SQZ>=65 olanlar arasindan en yuksek 3
    adaylar = sorted(
        [(sem, v) for sem, v in sonuclar.items() if v.get("etiket") is not None],
        key=lambda x: -x[1]["sqz_skoru"])
    for sem, v in adaylar[GUNLUK_AZAMI_ADAY:]:
        v["not"] = "esigi gecti ama gunluk 3 aday tavanina takildi, raporlanmiyor"
        v["etiket"] = None

    cikti = {
        "son_guncelleme_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "bulten_gunu": bugun_str,
        "faz": "V2 - ilk hafta GOZLEM modu, hicbir alarma baglanmadi (VIOP_ENTEGRASYON_PROMPTU kirmizi cizgi)",
        "gunluk_aday_tavani": GUNLUK_AZAMI_ADAY,
        "adaylar": [sem for sem, v in adaylar[:GUNLUK_AZAMI_ADAY]],
        "semboller": sonuclar,
    }
    atomik_json_yaz(CIKTI_YOL, cikti)

    yeterli = sum(1 for v in sonuclar.values() if v.get("durum") == "HESAPLANDI")
    yetersiz = len(sonuclar) - yeterli
    print(f"{yeterli} sembol hesaplandi, {yetersiz} sembol VERI_YETERSIZ")
    if adaylar[:GUNLUK_AZAMI_ADAY]:
        print("Bugunun adaylari:", [f"{s}({v['sqz_skoru']})" for s, v in adaylar[:GUNLUK_AZAMI_ADAY]])
    print(f"Yazildi: {CIKTI_YOL}")


if __name__ == "__main__":
    main()
