"""
PIYASA_REJIMI_FILTRESI_TESTI (10.08.2026) - Faz V0
Kurul karari (Bolum 4D onceligi): mevcut RSI edge'imiz zaten MUTEVAZI
(XU100'e karsi islemlerin yalniz %43.8'inde ustun - bkz. rsi_vs_
xu100_kiyas.py). Bu script, edge'in PIYASA REJIMINE (XU100'un KENDI
200-gunluk ortalamasina gore YUKARI/ASAGI trendde olmasi) gore
DEGISIP DEGISMEDIGINI test eder - eger REJIME BAGIMLIYSA, Pine'a
(v1'e DEGIL, Bolum 2 deneysel katman olarak) bir REJIM FILTRESI
eklenmesi DUSUNULEBILIR.

METODOLOJI: HER RSI sinyalinin GIRIS ANINDAKI XU100 rejimini
(close > 200-gunluk SMA = YUKARI_TREND, degilse ASAGI_TREND) etiketler,
ISABET/ORT GETIRIYI rejim bazinda AYIRIR.

KIRMIZI CIZGI: SALT OLCUM, Pine'a hic dokunmuyor. Rejim filtresi
KANITLANMADAN v1'e EKLENMEZ (Bolum 2 deneysel katman kurallariyla
AYNI disiplin).
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import yfinance as yf
import pandas as pd
import numpy as np
import yaml

RSI_PERIYOT = 14
RSI_ALT_ESIK = 30
RSI_UST_ESIK = 70
MAKS_TUTMA_GUN = 90
MALIYET_YUZDE = 0.25
XU100_SMA_PERIYOT = 200


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


def xu100_rejim_haritasi():
    try:
        df = yf.Ticker("XU100.IS").history(period="6y", interval="1d")
    except Exception as e:
        print(f"HATA: XU100 veri cekilemedi -> {e}", file=sys.stderr)
        return {}
    if df.empty:
        print("UYARI: XU100 verisi bos", file=sys.stderr)
        return {}
    df = df.sort_index()
    sma = df["Close"].rolling(XU100_SMA_PERIYOT).mean()
    harita = {}
    for i in range(len(df)):
        if pd.isna(sma.iloc[i]):
            continue
        tarih = df.index[i].date()
        harita[tarih] = "YUKARI_TREND" if df["Close"].iloc[i] > sma.iloc[i] else "ASAGI_TREND"
    return harita


def rsi_swing_simule(df, sembol, rejim_haritasi):
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
        rsi_deger = float(rsi.iloc[i])
        simdi_alti_30 = rsi_deger < RSI_ALT_ESIK
        yukari_kesisim = bool(onceki_alti_30) and (not simdi_alti_30)
        onceki_alti_30 = simdi_alti_30
        if pozisyon is None:
            if yukari_kesisim:
                giris_rejimi = rejim_haritasi.get(tarih)
                pozisyon = (kapanis, tarih, giris_rejimi)
        else:
            giris, giris_tarih, giris_rejimi = pozisyon
            gun_sayisi = (tarih - giris_tarih).days
            cikis = None
            if simdi_alti_30:
                cikis = kapanis
            elif rsi_deger >= RSI_UST_ESIK:
                cikis = kapanis
            elif gun_sayisi >= MAKS_TUTMA_GUN:
                cikis = kapanis
            elif i == len(df) - 1:
                cikis = kapanis
            if cikis is not None:
                ham = (cikis / giris - 1) * 100
                net = round(ham - MALIYET_YUZDE, 3)
                tum_islemler.append({"sembol": sembol, "giris_tarih": str(giris_tarih),
                                      "giris_rejimi": giris_rejimi or "BILINMIYOR",
                                      "net_getiri_pct": net})
                pozisyon = None
    return tum_islemler


def ozet_hesapla(islemler):
    if not islemler:
        return None
    getiriler = [t["net_getiri_pct"] for t in islemler]
    kazananlar = [g for g in getiriler if g > 0]
    return {"islem_sayisi": len(getiriler), "isabet_pct": round(100 * len(kazananlar) / len(getiriler), 1),
            "ort_net_getiri_pct": round(sum(getiriler) / len(getiriler), 3)}


def main():
    with open("config/universe.yml", encoding="utf-8") as f:
        evren = yaml.safe_load(f)["symbols"]

    print("XU100 rejim haritasi hazirlaniyor...")
    rejim_haritasi = xu100_rejim_haritasi()
    print(f"{len(rejim_haritasi)} gun icin rejim verisi hazir\n")

    tum_islemler = []
    for sembol in evren:
        try:
            df = yf.Ticker(f"{sembol}.IS").history(period="5y", interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
            continue
        if df.empty:
            continue
        tum_islemler += rsi_swing_simule(df, sembol, rejim_haritasi)

    ozet_genel = ozet_hesapla(tum_islemler)
    ozet_rejim = {}
    for rejim in ("YUKARI_TREND", "ASAGI_TREND", "BILINMIYOR"):
        alt = [t for t in tum_islemler if t["giris_rejimi"] == rejim]
        sonuc = ozet_hesapla(alt)
        if sonuc:
            ozet_rejim[rejim] = sonuc

    rapor = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("SWING_PINE_SPESIFIKASYONU.md Bolum 4D - RSI edge'inin XU100 "
                "REJIMINE (kendi 200-gunluk SMA'sina gore yukari/asagi trend) "
                "gore DEGISIP degismedigini test eder. Rejim filtresi "
                "KANITLANMADAN v1'e EKLENMEZ - Bolum 2 deneysel katman "
                "disipliniyle AYNI."),
        "xu100_sma_periyot": XU100_SMA_PERIYOT,
        "genel_ozet": ozet_genel,
        "rejim_bazinda_ozet": ozet_rejim,
    }
    atomik_json_yaz("data/backtest/piyasa_rejimi_filtresi_sonuc.json", rapor)
    print(f"Yazildi: data/backtest/piyasa_rejimi_filtresi_sonuc.json")
    print(f"GENEL: {ozet_genel}")
    for rejim, v in ozet_rejim.items():
        print(f"{rejim}: {v['islem_sayisi']} islem, isabet %{v['isabet_pct']}, ort net %{v['ort_net_getiri_pct']}")


if __name__ == "__main__":
    main()
