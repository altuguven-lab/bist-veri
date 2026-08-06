"""
MACD + MFI KESIF-BACKTEST (06.08.2026) - Faz V0
Kurul karari: MACD (klasik momentum/trend kesisimi) + MFI (hacim-agirlikli
RSI - "hacim bilgisini gorme" istegine cevap) - ORB/VWAP/Supertrend'den
TAMAMEN AYRI, yeni bir gosterge ailesi. SALT OLCUM - Pine'a dokunmuyor.

Yontem:
  - MACD: EMA(12)-EMA(26), sinyal=EMA(9) (standart parametreler)
  - MFI: 14 periyot, hacim-agirlikli fiyat akisi (RSI'in hacimli hali)
  - Giris: MACD histogram isaret DEGISTIRDIGINDE (kesisim), AYNI ANDA
    MFI asiri-alim/satim BOLGESINDE DEGILSE (LONG icin MFI<70, SHORT
    icin MFI>30 - "zaten asiri uzamis harekete atlamamak" filtresi)
  - Cikis: karsit MACD kesisimi VEYA ATR tabanli koruyucu stop
    (giris +/- 2*ATR) VEYA gun sonu zorla kapat
  - Maliyet: %0.25 gidis-donus (Borsamix, ayni varsayim)
"""
import json, datetime, os, sys
import pandas as pd
import numpy as np
import yfinance as yf

SEMBOLLER = ["AKBNK.IS", "KCHOL.IS", "THYAO.IS", "GARAN.IS"]
MALIYET_YUZDE = 0.25
CIKTI = "data/backtest/macd_mfi_kesif_sonuc.json"
MACD_HIZLI, MACD_YAVAS, MACD_SINYAL = 12, 26, 9
MFI_PERIYOT = 14
MFI_UST_ESIK, MFI_ALT_ESIK = 70, 30
ATR_PERIYOT = 10
ATR_STOP_CARPAN = 2.0


def atr_hesapla(df, periyot):
    yuksek, dusuk, kapanis = df["High"], df["Low"], df["Close"]
    onceki_kapanis = kapanis.shift(1)
    tr = pd.concat([
        yuksek - dusuk,
        (yuksek - onceki_kapanis).abs(),
        (dusuk - onceki_kapanis).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()


def macd_hesapla(df, hizli, yavas, sinyal):
    ema_hizli = df["Close"].ewm(span=hizli, adjust=False, min_periods=hizli).mean()
    ema_yavas = df["Close"].ewm(span=yavas, adjust=False, min_periods=yavas).mean()
    macd = ema_hizli - ema_yavas
    sinyal_cizgisi = macd.ewm(span=sinyal, adjust=False, min_periods=sinyal).mean()
    histogram = macd - sinyal_cizgisi
    return macd, sinyal_cizgisi, histogram


def mfi_hesapla(df, periyot):
    tipik = (df["High"] + df["Low"] + df["Close"]) / 3.0
    ham_akis = tipik * df["Volume"]
    onceki_tipik = tipik.shift(1)
    pozitif_akis = ham_akis.where(tipik > onceki_tipik, 0.0)
    negatif_akis = ham_akis.where(tipik < onceki_tipik, 0.0)
    pozitif_toplam = pozitif_akis.rolling(periyot, min_periods=periyot).sum()
    negatif_toplam = negatif_akis.rolling(periyot, min_periods=periyot).sum()
    # EDGE-CASE: negatif akis TAM SIFIRSA (surekli yukselen fiyat gibi),
    # oran teorik olarak sonsuzdur -> MFI = 100 olmali, nan DEGIL.
    mfi = pd.Series(index=df.index, dtype=float)
    gecerli = pozitif_toplam.notna() & negatif_toplam.notna()
    sifir_negatif = gecerli & (negatif_toplam == 0)
    normal = gecerli & (negatif_toplam > 0)
    mfi[sifir_negatif] = 100.0
    oran = pozitif_toplam[normal] / negatif_toplam[normal]
    mfi[normal] = 100 - (100 / (1 + oran))
    return mfi


def macd_mfi_simule(df, sembol):
    """06.08 DUZELTME: MACD(12,26,9) 38 bar isinma gerektiriyor ama tek
    bir gunluk oturum yalniz ~32 bar tasiyor - GUN GUN sifirlanan eski
    tasarim HICBIR gunun isinmasina izin vermiyordu (0 islem sonucunun
    kok nedeni). Simdi gostergeler TUM seri uzerinde (gunler arasi
    KESINTISIZ) hesaplaniyor - yalniz GIRISLER hala saat>=10:00'a VE
    ACIK POZISYONLAR hala gun sonunda zorla kapatmaya kisitli (gecelik
    pozisyon disiplini aynen koruniyor, yalniz gosterge isinmasi
    artik gun sinirina takilmiyor)."""
    df = df.copy().sort_index()
    df["gun"] = df.index.date
    tum_islemler = []

    _, _, hist = macd_hesapla(df, MACD_HIZLI, MACD_YAVAS, MACD_SINYAL)
    mfi = mfi_hesapla(df, MFI_PERIYOT)
    atr = atr_hesapla(df, ATR_PERIYOT)
    gun_son_index = df.groupby("gun").apply(lambda g: g.index[-1])

    pozisyon = None  # (yon, giris, stop)
    onceki_hist_isaret = None
    for i in range(len(df)):
        bar = df.iloc[i]
        bugun = bar["gun"]
        acilis_sonrasi = bar.name.time() >= datetime.time(10, 0)
        gunun_son_bari = bar.name == gun_son_index[bugun]

        if pd.isna(hist.iloc[i]):
            continue
        kapanis = float(bar["Close"])
        isaret = "POZ" if hist.iloc[i] > 0 else "NEG"
        kesisim = onceki_hist_isaret is not None and isaret != onceki_hist_isaret
        onceki_hist_isaret = isaret

        if pozisyon is None:
            if (acilis_sonrasi and not gunun_son_bari and kesisim
                    and not pd.isna(mfi.iloc[i]) and not pd.isna(atr.iloc[i])):
                if isaret == "POZ" and mfi.iloc[i] < MFI_UST_ESIK:
                    stop = kapanis - ATR_STOP_CARPAN * atr.iloc[i]
                    pozisyon = ("LONG", kapanis, stop)
                elif isaret == "NEG" and mfi.iloc[i] > MFI_ALT_ESIK:
                    stop = kapanis + ATR_STOP_CARPAN * atr.iloc[i]
                    pozisyon = ("SHORT", kapanis, stop)
        else:
            yon, giris, stop = pozisyon
            cikis, sebep = None, None
            if yon == "LONG" and float(bar["Low"]) <= stop:
                cikis, sebep = stop, "ATR_STOP"
            elif yon == "SHORT" and float(bar["High"]) >= stop:
                cikis, sebep = stop, "ATR_STOP"
            elif kesisim:
                cikis, sebep = kapanis, "MACD_KARSIT"
            elif gunun_son_bari:
                cikis, sebep = kapanis, "GUN_SONU"
            if cikis is not None:
                ham = (cikis / giris - 1) * 100 * (1 if yon == "LONG" else -1)
                net = ham - MALIYET_YUZDE
                tum_islemler.append({"sembol": sembol, "gun": str(bugun), "yon": yon,
                                      "giris": giris, "cikis": cikis, "sebep": sebep,
                                      "ham_getiri_pct": round(ham, 3), "net_getiri_pct": round(net, 3)})
                pozisyon = None
    return tum_islemler


def main():
    tum_islemler = []
    for sembol in SEMBOLLER:
        try:
            df = yf.Ticker(sembol).history(period="60d", interval="15m")
            if df.empty:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            islemler = macd_mfi_simule(df, sembol)
            tum_islemler += islemler
            print(f"{sembol}: {len(islemler)} islem simule edildi")
        except Exception as e:
            print(f"HATA: {sembol} -> {e}", file=sys.stderr)

    ozet = {}
    for sembol in SEMBOLLER:
        alt = [t for t in tum_islemler if t["sembol"] == sembol]
        if not alt:
            continue
        kazanan = [t for t in alt if t["net_getiri_pct"] > 0]
        ozet[sembol] = {"islem_sayisi": len(alt),
                         "isabet_pct": round(100 * len(kazanan) / len(alt), 1),
                         "ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt) / len(alt), 3),
                         "toplam_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt), 2)}

    genel = None
    if tum_islemler:
        kazanan = [t for t in tum_islemler if t["net_getiri_pct"] > 0]
        genel = {"toplam_islem": len(tum_islemler),
                 "genel_isabet_pct": round(100 * len(kazanan) / len(tum_islemler), 1),
                 "genel_ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in tum_islemler) / len(tum_islemler), 3)}

    from collections import Counter
    sebepler = dict(Counter(t["sebep"] for t in tum_islemler))

    sonuc = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": "Faz V0 - MACD+MFI, SALT OLCUM. yfinance 60 gunluk 15dk pencere.",
        "parametreler": {"macd": [MACD_HIZLI, MACD_YAVAS, MACD_SINYAL],
                          "mfi_periyot": MFI_PERIYOT, "mfi_esikler": [MFI_ALT_ESIK, MFI_UST_ESIK],
                          "atr_periyot": ATR_PERIYOT, "atr_stop_carpan": ATR_STOP_CARPAN},
        "maliyet_varsayimi_pct": MALIYET_YUZDE,
        "sembol_bazli": ozet, "genel": genel, "cikis_sebebi_dagilimi": sebepler,
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
