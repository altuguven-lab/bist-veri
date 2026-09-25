"""
DUSUS SONRASI ALIM vs YUKSELIS KOVALAMA TESTI (24.09.2026)
=============================================================
Soru: BIST'te N-gunluk dusus sonrasi alim (dip/mean-reversion), N-gunluk
yukselis sonrasi alim (momentum/kovalama) stratejisinden daha mi karli?

Yontem: Her gun icin N-gunluk (5 ve 10) getiri hesaplanir. Bu getiri
dagiliminin ALT %20'si "DIP" (sert dusus sonrasi), UST %20'si "KOVALAMA"
(sert yukselis sonrasi) olarak etiketlenir. Her ikisinin de ileri
getirisi (T+3, T+5, T+10) karsilastirilir.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi. Mean-reversion/momentum
literatur genelde UFKA gore DEGISIR (kisa ufukta mean-reversion,
uzun ufukta momentum daha sik gorulur) - bu yuzden BIRDEN FAZLA
ufuk (3/5/10 gun) birlikte raporlaniyor, tek bir "kazanan" iddia
edilmeden. Sembol bazinda saglamlik kontrolu da yapiliyor (lateEntry
testinde ogrendigimiz ders: aggregate tek basina yeterli degil).

Cikti: data/backtest/dip_vs_kovalama_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler

GERI_DONEMLER = [5, 10]   # N-gunluk oncul getiri penceresi
ILERI_GUNLER = [3, 5, 10]
PERCENTILE = 20            # alt/ust %20


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

    sonuc_per_geri_donem = {}

    for geri in GERI_DONEMLER:
        dip_g = {n: [] for n in ILERI_GUNLER}
        kov_g = {n: [] for n in ILERI_GUNLER}
        sembol_sonuc = {}

        for s, df in ham.items():
            oncul = df["Close"].pct_change(geri) * 100
            alt_esik = oncul.quantile(PERCENTILE / 100)
            ust_esik = oncul.quantile(1 - PERCENTILE / 100)

            dip_mask = oncul <= alt_esik
            kov_mask = oncul >= ust_esik

            s_sonuc = {"dip": {}, "kovalama": {},
                       "dip_gun_sayisi": int(dip_mask.sum()), "kovalama_gun_sayisi": int(kov_mask.sum())}
            for n in ILERI_GUNLER:
                g = ileri_getiri(df["Close"], n)
                g_dip = g[dip_mask].dropna().tolist()
                g_kov = g[kov_mask].dropna().tolist()
                s_sonuc["dip"][f"t{n}"] = islem_ozet(g_dip)
                s_sonuc["kovalama"][f"t{n}"] = islem_ozet(g_kov)
                dip_g[n].extend(g_dip)
                kov_g[n].extend(g_kov)
            sembol_sonuc[s] = s_sonuc

        genel_dip = {f"t{n}": islem_ozet(dip_g[n]) for n in ILERI_GUNLER}
        genel_kov = {f"t{n}": islem_ozet(kov_g[n]) for n in ILERI_GUNLER}

        # saglamlik: T+10'da kac sembolde DIP > KOVALAMA (isabet)
        tutarlilik = []
        for s, v in sembol_sonuc.items():
            di = v["dip"]["t10"]["isabet_pct"]
            ki = v["kovalama"]["t10"]["isabet_pct"]
            if di is not None and ki is not None:
                tutarlilik.append(1 if di > ki else 0)
        dip_lehine_sembol_orani = round(100 * sum(tutarlilik) / len(tutarlilik), 1) if tutarlilik else None

        sonuc_per_geri_donem[f"geri_{geri}gun"] = {
            "genel": {"dip": genel_dip, "kovalama": genel_kov},
            "dip_lehine_sembol_orani_pct_T10": dip_lehine_sembol_orani,
            "sembol_bazli": sembol_sonuc,
        }
        print(f"=== Oncul pencere: {geri} gun ===")
        print(f"DIP      T+3={genel_dip['t3']}, T+10={genel_dip['t10']}")
        print(f"KOVALAMA T+3={genel_kov['t3']}, T+10={genel_kov['t10']}")
        print(f"Sembol bazinda DIP lehine oran (T+10 isabet): %{dip_lehine_sembol_orani}")
        print()

    rapor = {
        "calisma": "Dusus Sonrasi Alim vs Yukselis Kovalama Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi. Mean-reversion/momentum ufka gore "
            "degisebilir - birden fazla ufuk (T+3/5/10) ve iki oncul "
            "pencere (5/10 gun) birlikte raporlaniyor. Sembol bazinda "
            "saglamlik kontrolu dahil (lateEntry testinden ogrenilen ders)."
        ),
        "percentile_esigi": PERCENTILE,
        "sonuclar": sonuc_per_geri_donem,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/dip_vs_kovalama_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print("Tamamlandi -> data/backtest/dip_vs_kovalama_sonuc.json")


if __name__ == "__main__":
    main()
