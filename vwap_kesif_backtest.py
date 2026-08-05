"""
VWAP ORTALAMAYA-DONUS KESIF-BACKTEST (05.08.2026) - Faz V0
Arastirmadaki (Teknik Piyasa kaynagi) VWAP Mean Reversion desenini BIST'in
gercek verisinde test eder. KIRMIZI CIZGI: SALT OLCUM - hicbir gercek
islem/sinyal uretmez, Pine'a hic dokunmaz.

Yontem (arastirma kaynagindan):
  - Bant: VWAP +/- K standart sapma (K=2 varsayilan, gun ici genisleyen pencere)
  - Kurulum: fiyat bandin disina cikar (ust/alt banda dokunur/asar)
  - Tetik: bir sonraki barin kapanisi bandin ICINE donerse, VWAP'a dogru
    ters yonlu pozisyon acilir (bant disina cikan asiri hareketin
    "duzelecegi" varsayimi)
  - Hedef: VWAP'in kendisi
  - Stop: asirilik sirasinda goruled en uc nokta (High/Low)
  - Zorla kapat: gun sonunda, gecelik pozisyon YOK (ORB ile ayni disiplin)
  - Maliyet: %0.25 gidis-donus (Borsamix BIST gercekci varsayimi, ORB ile ayni)
"""
import json, datetime, os, sys
import pandas as pd
import yfinance as yf

SEMBOLLER = ["AKBNK.IS", "KCHOL.IS", "THYAO.IS", "GARAN.IS"]
MALIYET_YUZDE = 0.25
CIKTI = "data/backtest/vwap_kesif_v2_sonuc.json"
STD_PENCERE_MIN = 5   # en az bu kadar bar biriktikten sonra bant hesabi baslar
K_STD = 2.0            # arastirmadaki "±2 standart sapma" varsayilani

# 05.08 EKI (v2): giris anindaki VWAP hedefi bazen giris fiyatina COK
# YAKIN (hatta yanlis tarafta) cikiyordu - "HEDEF" cikan islemlerin
# ortalamasi bile negatifti (maliyeti karsilamiyordu). Artik giris
# ONCESI, VWAP'a olan projekte mesafe kontrol ediliyor - MIN_HEDEF_PCT'i
# gecmezse islem hic acilmiyor.
MIN_HEDEF_PCT = 0.75   # MALIYET_YUZDE'nin (0.25) 3 kati - kucuk/anlamsiz
                       # hedefli islemleri elemek icin.


def gunluk_vwap_ve_std(grup):
    """VWAP + fiyatin VWAP'tan sapmasinin GENISLEYEN pencere std'si."""
    tipik = (grup["High"] + grup["Low"] + grup["Close"]) / 3.0
    kum_pv = (tipik * grup["Volume"]).cumsum()
    kum_v = grup["Volume"].cumsum().replace(0, pd.NA)
    vwap = kum_pv / kum_v
    sapma = grup["Close"] - vwap
    std = sapma.expanding(min_periods=STD_PENCERE_MIN).std()
    return vwap, std


def vwap_reversion_simule(df, sembol, k_std=K_STD):
    """Gunluk bazda VWAP ortalamaya-donus: bant disina cikip ICERI donunce
    VWAP'a dogru ters pozisyon ac. df: DatetimeIndex'li 15dk OHLCV."""
    df = df.copy()
    df["gun"] = df.index.date
    islemler = []

    for gun, grup in df.groupby("gun"):
        grup = grup.sort_index()
        grup = grup[grup.index.time >= datetime.time(10, 0)]
        if len(grup) < STD_PENCERE_MIN + 3:
            continue
        vwap, std = gunluk_vwap_ve_std(grup)

        pozisyon = None  # ("LONG"/"SHORT", giris_fiyat, hedef_vwap, stop)
        disarda = None   # "UST" / "ALT" - hangi bandin disina cikildi + en uc deger
        for i in range(len(grup)):
            bar = grup.iloc[i]
            if pd.isna(std.iloc[i]) or std.iloc[i] <= 0:
                continue
            ust_bant = vwap.iloc[i] + k_std * std.iloc[i]
            alt_bant = vwap.iloc[i] - k_std * std.iloc[i]
            kapanis = float(bar["Close"])

            if pozisyon is None:
                if disarda is None:
                    # kurulum asamasi: bant disina cikan bar'i not al
                    if float(bar["High"]) > ust_bant:
                        disarda = ("UST", float(bar["High"]))
                    elif float(bar["Low"]) < alt_bant:
                        disarda = ("ALT", float(bar["Low"]))
                else:
                    yon_disi, uc_deger = disarda
                    hedef_aday = vwap.iloc[i]
                    # v2: hedefe olan mesafe (%) minimum esigi gecmiyorsa
                    # islem HIC ACILMASIN - "hedefe ulasti ama maliyeti bile
                    # karsilamadi" sorununun kok cozumu.
                    if yon_disi == "UST" and kapanis < ust_bant:
                        mesafe_pct = (kapanis - hedef_aday) / kapanis * 100
                        if mesafe_pct >= MIN_HEDEF_PCT:
                            pozisyon = ("SHORT", kapanis, hedef_aday, uc_deger)
                        disarda = None
                    elif yon_disi == "ALT" and kapanis > alt_bant:
                        mesafe_pct = (hedef_aday - kapanis) / kapanis * 100
                        if mesafe_pct >= MIN_HEDEF_PCT:
                            pozisyon = ("LONG", kapanis, hedef_aday, uc_deger)
                        disarda = None
                    else:
                        # hala disarida, daha ucta yeni bir nokta olabilir
                        if yon_disi == "UST" and float(bar["High"]) > uc_deger:
                            disarda = ("UST", float(bar["High"]))
                        elif yon_disi == "ALT" and float(bar["Low"]) < uc_deger:
                            disarda = ("ALT", float(bar["Low"]))
            else:
                yon, giris, hedef, stop = pozisyon
                cikis, sebep = None, None
                if yon == "SHORT" and float(bar["Low"]) <= hedef:
                    cikis, sebep = hedef, "HEDEF"
                elif yon == "SHORT" and float(bar["High"]) >= stop:
                    cikis, sebep = stop, "STOP"
                elif yon == "LONG" and float(bar["High"]) >= hedef:
                    cikis, sebep = hedef, "HEDEF"
                elif yon == "LONG" and float(bar["Low"]) <= stop:
                    cikis, sebep = stop, "STOP"
                elif i == len(grup) - 1:
                    cikis, sebep = kapanis, "GUN_SONU"
                if cikis is not None:
                    ham_getiri = (cikis / giris - 1) * 100 * (1 if yon == "LONG" else -1)
                    net_getiri = ham_getiri - MALIYET_YUZDE
                    islemler.append({"sembol": sembol, "gun": str(gun), "yon": yon,
                                      "giris": giris, "cikis": cikis, "sebep": sebep,
                                      "ham_getiri_pct": round(ham_getiri, 3),
                                      "net_getiri_pct": round(net_getiri, 3)})
                    pozisyon = None
    return islemler


def main():
    tum_islemler = []
    for sembol in SEMBOLLER:
        try:
            df = yf.Ticker(sembol).history(period="60d", interval="15m")
            if df.empty:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            islemler = vwap_reversion_simule(df, sembol)
            tum_islemler += islemler
            print(f"{sembol}: {len(islemler)} islem simule edildi")
        except Exception as e:
            print(f"HATA: {sembol} -> {e}", file=sys.stderr)

    ozet = {}
    for sembol in SEMBOLLER:
        alt_kume = [t for t in tum_islemler if t["sembol"] == sembol]
        if not alt_kume:
            continue
        kazanan = [t for t in alt_kume if t["net_getiri_pct"] > 0]
        ozet[sembol] = {
            "islem_sayisi": len(alt_kume),
            "isabet_pct": round(100 * len(kazanan) / len(alt_kume), 1),
            "ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt_kume) / len(alt_kume), 3),
            "toplam_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt_kume), 2),
        }

    genel = None
    if tum_islemler:
        kazanan = [t for t in tum_islemler if t["net_getiri_pct"] > 0]
        genel = {
            "toplam_islem": len(tum_islemler),
            "genel_isabet_pct": round(100 * len(kazanan) / len(tum_islemler), 1),
            "genel_ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in tum_islemler) / len(tum_islemler), 3),
        }

    from collections import Counter
    sebepler = dict(Counter(t["sebep"] for t in tum_islemler))
    sebep_detay = {}
    for sebep in ("HEDEF", "STOP", "GUN_SONU"):
        alt = [t for t in tum_islemler if t["sebep"] == sebep]
        if alt:
            sebep_detay[sebep] = {"adet": len(alt),
                                   "ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt) / len(alt), 3)}

    sonuc = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 kesif-backtest - VWAP ortalamaya-donus, SALT OLCUM. "
                "yfinance 60 gunluk 15dk pencereyle sinirli."),
        "maliyet_varsayimi_pct": MALIYET_YUZDE, "k_std": K_STD,
        "sembol_bazli": ozet,
        "genel": genel,
        "cikis_sebebi_dagilimi": sebepler,
        "cikis_sebebi_detay": sebep_detay,
        "islem_detaylari": tum_islemler,
    }
    os.makedirs("data/backtest", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"\nYazildi: {CIKTI}")
    if genel:
        print(f"GENEL: {genel['toplam_islem']} islem, isabet %{genel['genel_isabet_pct']}, "
              f"ort net getiri %{genel['genel_ort_net_getiri_pct']}")


if __name__ == "__main__":
    main()
