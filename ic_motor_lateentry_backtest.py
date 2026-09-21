"""
IC MOTOR lateEntry BACKTEST (21.09.2026)
==========================================
Denetimde bulunan sorun: ic pozisyon motorunun (_posOpen) 16 ayri giris
tetikleyicisinin (eliteBuy, realBuy, bankEngine_any, retailEngine_signal
vb.) HICBIRINDE not _lateEntry kontrolu yok - gorunen alarmlar (P1/CORE_AL)
korumali ama ic motor (WR/PF/Kelly'yi besleyen) degil.

Bu script f_v107MarketQuality'nin GERCEK lateEntry formulunu (satir 344)
birebir kullanarak, JENERIK bir giris-adayi sinyalinin (tepe asimi+hacim -
B3'te kullandigimiz AYNI pattern, 16 motorun ortak ruhunu temsil eden bir
vekil) lateEntry=true (kovalama) ve lateEntry=false (temiz) durumlarindaki
ileri getirisini karsilastirir.

GERCEK FORMUL (V162, satir 344):
  lateEntry = close > emaFast + atr*1.8 OR close > emaFast*1.035
  (emaFast = EMA9, atr = ATR14, lateAtrMult=1.8, lateEmaExtPct=1.035 varsayilan)

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi. "Aday" sinyali 16 motorun TAMAMINI
BIREBIR temsil ETMIYOR - jenerik bir breakout+hacim vekili. Sonuc yon
verir, kesin degil.

Cikti: data/backtest/ic_motor_lateentry_sonuc.json
"""
import json
import sys
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler

LATE_ATR_MULT_SABIT = 4.0  # onceki testte 2.5+'ta hic etkisi kalmadigi dogrulandi - artik sabit/etkisiz tutuluyor
LATE_EMA_EXT_PCT_LISTESI = [1.020, 1.035, 1.050, 1.070, 1.100]  # %2.0/%3.5(Pine varsayilani)/%5/%7/%10
ILERI_GUNLER = [3, 10]


def atr_hesapla(df, n=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def ileri_getiri(close, n):
    return (close.shift(-n) / close - 1) * 100


def islem_ozet(getiriler):
    g = [x for x in getiriler if not np.isnan(x)]
    if not g:
        return {"adet": 0, "isabet_pct": None, "ort_getiri_pct": None}
    return {
        "adet": len(g),
        "isabet_pct": round(100 * float(np.mean([x > 0 for x in g])), 1),
        "ort_getiri_pct": round(float(np.mean(g)), 3),
    }


def main():
    ham = {}
    for s in SEMBOLLER:
        d = veri_cek(f"{s}.IS", start="2018-06-01")
        if d is not None and len(d) > 250:
            ham[s] = gostergeler(d)

    esik_sonuclari = {}
    for ema_pct in LATE_EMA_EXT_PCT_LISTESI:
        temiz_g = {n: [] for n in ILERI_GUNLER}
        kovalama_g = {n: [] for n in ILERI_GUNLER}
        sembol_sonuc = {}

        for s, df in ham.items():
            atr = atr_hesapla(df, 14)
            tetikSeviye = df["High"].shift(1).rolling(10).max()
            tepeAsim = df["Close"] > tetikSeviye
            hacimVar = df["relVol"] >= 1.2
            aday = tepeAsim & hacimVar

            # ATR tarafi SABIT/gevsek (onceki testte etkisiz oldugu dogrulandi) -
            # boylece fark TAMAMEN EMA-yuzdesi tarafindan geliyor
            lateEntry = (df["Close"] > df["e9"] + atr * LATE_ATR_MULT_SABIT) | (df["Close"] > df["e9"] * ema_pct)

            temiz_mask = aday & (~lateEntry)
            kovalama_mask = aday & lateEntry

            s_sonuc = {"temiz": {}, "kovalama": {},
                       "temiz_gun_sayisi": int(temiz_mask.sum()), "kovalama_gun_sayisi": int(kovalama_mask.sum())}
            for n in ILERI_GUNLER:
                g = ileri_getiri(df["Close"], n)
                g_temiz = g[temiz_mask].dropna().tolist()
                g_kovalama = g[kovalama_mask].dropna().tolist()
                s_sonuc["temiz"][f"t{n}"] = islem_ozet(g_temiz)
                s_sonuc["kovalama"][f"t{n}"] = islem_ozet(g_kovalama)
                temiz_g[n].extend(g_temiz)
                kovalama_g[n].extend(g_kovalama)
            sembol_sonuc[s] = s_sonuc

        genel_temiz = {f"t{n}": islem_ozet(temiz_g[n]) for n in ILERI_GUNLER}
        genel_kovalama = {f"t{n}": islem_ozet(kovalama_g[n]) for n in ILERI_GUNLER}
        esik_sonuclari[f"ema_pct_{ema_pct}"] = {
            "genel": {"temiz": genel_temiz, "kovalama": genel_kovalama},
            "sembol_bazli": sembol_sonuc,
        }
        print(f"EMA x{ema_pct}: TEMIZ T+3={genel_temiz['t3']}, KOVALAMA T+3={genel_kovalama['t3']}")
        print(f"EMA x{ema_pct}: TEMIZ T+10={genel_temiz['t10']}, KOVALAMA T+10={genel_kovalama['t10']}")

    rapor = {
        "calisma": "IC MOTOR lateEntry Backtest - EMA Yuzdesi Izole Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi. 'Aday' sinyali 16 ic motorun TAMAMINI degil, "
            "jenerik bir breakout+hacim vekilini temsil ediyor (B3 ile ayni pattern). "
            "ATR tarafi SABIT/gevsek (x4.0, onceki testte etkisiz dogrulandi) tutuldu - "
            "fark TAMAMEN EMA-yuzdesi (1.035 Pine varsayilani + 4 alternatif) tarafindan "
            "geliyor. Sonuc yon verir, 16 motorun her biri icin kesin degildir."
        ),
        "esikler": esik_sonuclari,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/ic_motor_lateentry_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print("Tamamlandi -> data/backtest/ic_motor_lateentry_sonuc.json")


if __name__ == "__main__":
    main()
