"""
ACILIS GAP'I SONRASI DAVRANIS TESTI (25.09.2026)
===================================================
Bugun konustugumuz tek-fiyat acilis mekanizmasiyla dogrudan ilgili:
buyuk bir acilis sicramasi (gap up/down) GUN ICINDE devam mi ediyor,
yoksa tersine mi donuyor (fade)? V162'nin kendi gapRisk/isLimitZoneBist
mantigiyla iliskili.

YONTEM: gap_pct = (Acilis - Onceki Kapanis) / Onceki Kapanis * 100.
Ust %10 "BUYUK GAP YUKARI", alt %10 "BUYUK GAP ASAGI" olarak
etiketleniyor. Iki ayri olcum:
  (1) GUN ICI DEVAM: kapanis, aciliftan ayni yonde mi hareket etti
      (gap devam etti) yoksa ters yonde mi (fade/tersine donus)?
  (2) ILERI GETIRI: gap gununun KAPANISINDAN itibaren T+3/T+5/T+10
      getirisi - buyuk gap sonrasi cok-gunluk davranis.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi.

Cikti: data/backtest/gap_sonrasi_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler

PERCENTILE = 10
ILERI_GUNLER = [3, 5, 10]


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

    gap_yukari_devam, gap_yukari_fade = [], []
    gap_asagi_devam, gap_asagi_fade = [], []
    ileri_yukari_g = {n: [] for n in ILERI_GUNLER}
    ileri_asagi_g = {n: [] for n in ILERI_GUNLER}
    sembol_sonuc = {}

    for s, df in ham.items():
        onceki_kapanis = df["Close"].shift(1)
        gap_pct = (df["Open"] - onceki_kapanis) / onceki_kapanis * 100
        ust_esik = gap_pct.quantile(1 - PERCENTILE / 100)
        alt_esik = gap_pct.quantile(PERCENTILE / 100)

        gap_yukari_mask = gap_pct >= ust_esik
        gap_asagi_mask = gap_pct <= alt_esik

        gun_ici_hareket = (df["Close"] - df["Open"]) / df["Open"] * 100
        # gap yukariyken kapanis da yukari devam ederse "DEVAM", asagi donerse "FADE"
        yukari_devam_mask = gap_yukari_mask & (gun_ici_hareket > 0)
        yukari_fade_mask = gap_yukari_mask & (gun_ici_hareket <= 0)
        asagi_devam_mask = gap_asagi_mask & (gun_ici_hareket < 0)
        asagi_fade_mask = gap_asagi_mask & (gun_ici_hareket >= 0)

        gap_yukari_devam.append(int(yukari_devam_mask.sum()))
        gap_yukari_fade.append(int(yukari_fade_mask.sum()))
        gap_asagi_devam.append(int(asagi_devam_mask.sum()))
        gap_asagi_fade.append(int(asagi_fade_mask.sum()))

        s_sonuc = {
            "gap_yukari_devam_gun": int(yukari_devam_mask.sum()),
            "gap_yukari_fade_gun": int(yukari_fade_mask.sum()),
            "gap_asagi_devam_gun": int(asagi_devam_mask.sum()),
            "gap_asagi_fade_gun": int(asagi_fade_mask.sum()),
            "gap_yukari_sonrasi_ileri": {}, "gap_asagi_sonrasi_ileri": {},
        }
        for n in ILERI_GUNLER:
            g = ileri_getiri(df["Close"], n)
            g_yukari = g[gap_yukari_mask].dropna().tolist()
            g_asagi = g[gap_asagi_mask].dropna().tolist()
            s_sonuc["gap_yukari_sonrasi_ileri"][f"t{n}"] = islem_ozet(g_yukari)
            s_sonuc["gap_asagi_sonrasi_ileri"][f"t{n}"] = islem_ozet(g_asagi)
            ileri_yukari_g[n].extend(g_yukari)
            ileri_asagi_g[n].extend(g_asagi)
        sembol_sonuc[s] = s_sonuc

    toplam_yukari = sum(gap_yukari_devam) + sum(gap_yukari_fade)
    toplam_asagi = sum(gap_asagi_devam) + sum(gap_asagi_fade)

    rapor = {
        "calisma": "Acilis Gap'i Sonrasi Davranis Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": "GUNLUK BAR yaklasikligi.",
        "percentile_esigi": PERCENTILE,
        "gun_ici_devam_analizi": {
            "gap_yukari": {
                "devam_gun": sum(gap_yukari_devam), "fade_gun": sum(gap_yukari_fade),
                "devam_orani_pct": round(100 * sum(gap_yukari_devam) / toplam_yukari, 1) if toplam_yukari else None,
            },
            "gap_asagi": {
                "devam_gun": sum(gap_asagi_devam), "fade_gun": sum(gap_asagi_fade),
                "devam_orani_pct": round(100 * sum(gap_asagi_devam) / toplam_asagi, 1) if toplam_asagi else None,
            },
        },
        "ileri_getiri_analizi": {
            "gap_yukari_sonrasi": {f"t{n}": islem_ozet(ileri_yukari_g[n]) for n in ILERI_GUNLER},
            "gap_asagi_sonrasi": {f"t{n}": islem_ozet(ileri_asagi_g[n]) for n in ILERI_GUNLER},
        },
        "sembol_bazli": sembol_sonuc,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/gap_sonrasi_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print("GUN ICI DEVAM:", rapor["gun_ici_devam_analizi"])
    print("ILERI GETIRI GAP YUKARI:", rapor["ileri_getiri_analizi"]["gap_yukari_sonrasi"])
    print("ILERI GETIRI GAP ASAGI :", rapor["ileri_getiri_analizi"]["gap_asagi_sonrasi"])
    print("Tamamlandi -> data/backtest/gap_sonrasi_sonuc.json")


if __name__ == "__main__":
    main()
