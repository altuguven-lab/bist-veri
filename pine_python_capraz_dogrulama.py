"""
PINE_PYTHON_CAPRAZ_DOGRULAMA (10.08.2026) - Faz V0
SW_RSI_v1.pine'daki mantikla BIREBIR AYNI kurallari (RSI 30 yukari
kesisim giris, -%12 stop GUN ICI DUSUK ile, RSI<30 basarisiz sicrama,
RSI>=70 kar-al, 90 gun maks tutma) SEMBOL BAZINDA ayristirilmis olarak
kosturur. AMAC: kullanicinin TradingView Pine panelinde GORDUGU N/
Isabet/PF/DD sayilariyla DOGRUDAN karsilastirilabilecek, AYNI mantikla
uretilmis bir Python referansi saglamak.

10.08 BULGU: onceki karsilastirmamiz (rsi_asiri_satim_swing_sonuc.json)
STOP-LOSS'SUZ (orijinal, ilk backtest) veriydi - Pine v1 ISE stop-
loss'lu. Bu, apples-to-oranges bir karsilastirmaydi. Bu script o
hatayi DUZELTIR.

KIRMIZI CIZGI: SALT OLCUM, Pine'a hic dokunmuyor.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import yfinance as yf
import pandas as pd
import numpy as np

RSI_PERIYOT = 14
RSI_ALT_ESIK = 30
RSI_UST_ESIK = 70
MAKS_TUTMA_GUN = 90
MALIYET_YUZDE = 0.25
STOP_YUZDE = 12


def rsi_hesapla(kapanislar, periyot):
    delta = kapanislar.diff()
    kazanc = delta.where(delta > 0, 0.0)
    kayip = -delta.where(delta < 0, 0.0)
    ort_kazanc = kazanc.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()
    ort_kayip = kayip.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()
    rs = ort_kazanc / ort_kayip.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(~(ort_kayip == 0), 100.0)
    return rsi


def rsi_swing_simule_pine_esdeger(df, sembol):
    df = df.copy().sort_index()
    rsi = rsi_hesapla(df["Close"], RSI_PERIYOT)
    tum_islemler = []
    pozisyon = None
    onceki_alti_30 = None
    for i in range(len(df)):
        if pd.isna(df["Close"].iloc[i]) or pd.isna(rsi.iloc[i]):
            continue
        tarih = df.index[i].date()
        kapanis = float(df["Close"].iloc[i])
        dusuk = float(df["Low"].iloc[i]) if "Low" in df.columns and not pd.isna(df["Low"].iloc[i]) else kapanis
        rsi_deger = float(rsi.iloc[i])
        simdi_alti_30 = rsi_deger < RSI_ALT_ESIK
        yukari_kesisim = bool(onceki_alti_30) and (not simdi_alti_30)
        onceki_alti_30 = simdi_alti_30

        if pozisyon is None:
            if yukari_kesisim:
                pozisyon = (kapanis, tarih)
        else:
            giris, giris_tarih = pozisyon
            gun_sayisi = (tarih - giris_tarih).days
            stop_seviyesi = giris * (1 - STOP_YUZDE / 100)
            cikis, sebep = None, None
            if dusuk <= stop_seviyesi:
                cikis, sebep = stop_seviyesi, "STOP"
            elif simdi_alti_30:
                cikis, sebep = kapanis, "BASARISIZ_SICRAMA"
            elif rsi_deger >= RSI_UST_ESIK:
                cikis, sebep = kapanis, "KAR_AL"
            elif gun_sayisi >= MAKS_TUTMA_GUN:
                cikis, sebep = kapanis, "MAKS_TUTMA"
            if cikis is not None:
                ham = (cikis / giris - 1) * 100
                net = round(ham - MALIYET_YUZDE, 3)
                tum_islemler.append({"sembol": sembol, "giris_tarih": str(giris_tarih),
                                      "cikis_tarih": str(tarih), "sebep": sebep, "net_getiri_pct": net})
                pozisyon = None
    return tum_islemler


def ozet_hesapla(islemler):
    if not islemler:
        return None
    getiriler = [t["net_getiri_pct"] for t in islemler]
    kazananlar = [g for g in getiriler if g > 0]
    kaybedenler = [abs(g) for g in getiriler if g <= 0]
    pf = (sum(kazananlar) / sum(kaybedenler)) if kaybedenler and sum(kaybedenler) > 0.001 else (999.0 if kazananlar else None)
    esitlik, zirve, maks_dd = 100.0, 100.0, 0.0
    for g in getiriler:
        esitlik *= (1 + g / 100)
        zirve = max(zirve, esitlik)
        maks_dd = min(maks_dd, (esitlik / zirve - 1) * 100)
    return {"islem_sayisi": len(getiriler), "isabet_pct": round(100 * len(kazananlar) / len(getiriler), 1),
            "ort_net_getiri_pct": round(sum(getiriler) / len(getiriler), 3),
            "profit_factor": round(pf, 2) if pf is not None else None,
            "maks_dd_pct": round(maks_dd, 2)}


def main():
    HEDEF_SEMBOLLER = ["TTKOM", "ENJSA", "TAVHL", "KCHOL", "AKBNK"]

    sonuclar = {}
    for sembol in HEDEF_SEMBOLLER:
        try:
            df = yf.Ticker(f"{sembol}.IS").history(period="max", interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
            continue
        if df.empty:
            continue
        islemler = rsi_swing_simule_pine_esdeger(df, sembol)
        ozet = ozet_hesapla(islemler)
        sonuclar[sembol] = {
            "veri_baslangic": str(df.index[0].date()), "veri_bitis": str(df.index[-1].date()),
            "toplam_bar": len(df), "ozet": ozet,
        }
        if ozet:
            print(f"{sembol} (veri: {sonuclar[sembol]['veri_baslangic']} - {sonuclar[sembol]['veri_bitis']}): "
                  f"N={ozet['islem_sayisi']}, Isabet=%{ozet['isabet_pct']}, "
                  f"PF={ozet['profit_factor']}, MaksDD=%{ozet['maks_dd_pct']}")

    rapor = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("SW_RSI_v1.pine mantigiyla BIREBIR AYNI kurallar (stop-12 "
                "DAHIL) kullanilarak, 'max' (mumkun olan TUM) gecmisle "
                "kosturulan Python referansi. Kullanicinin TradingView "
                "panelinde okudugu N/Isabet/PF/DD ile DOGRUDAN "
                "karsilastirilmalidir."),
        "semboller": sonuclar,
    }
    atomik_json_yaz("data/backtest/pine_python_capraz_dogrulama_sonuc.json", rapor)
    print(f"\nYazildi: data/backtest/pine_python_capraz_dogrulama_sonuc.json")


if __name__ == "__main__":
    main()
