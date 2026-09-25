"""
DEVRE KESICI SONRASI DAVRANIS TESTI (25.09.2026)
===================================================
Soru: BIST'te sert tek-gunluk dususlerden (devre kesici tetikleyici
duzeyde) SONRA hisseler toparlaniyor mu, yoksa zayiflik devam mi
ediyor? 16 Eylul 2026 krizi (BIST 100 %5,54 kayip, devre kesici) ve
sonrasindaki gunler dogrudan bu sorunun ozel bir ornegi.

YONTEM (proxy): Gercek intraday devre-kesici tetikleme verisi (tick
bazinda) elde YOK - GUNLUK bar kullaniliyor. Vekil: bir gunluk
DEGISIMI <= -%8 olan gunler "SERT DUSUS" (devre-kesici-duzeyinde)
olarak etiketleniyor - BIST'in pay-bazinda devre kesici esikleri
tipik olarak bu buyuklukte tetikleniyor (bu oturumda TRMET orneginde
gordugumuz gibi). Bu gunlerin SONRASINDAKI (T+1, T+3, T+5, T+10)
getiri, KOSULSUZ (tum gunler) ortalamayla karsilastiriliyor.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi - gercek intraday devre kesici
tetiklenmesini BIREBIR YAKALAMIYOR, sert tek-gunluk dusus bir VEKIL.

Cikti: data/backtest/devre_kesici_sonrasi_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler

SERT_DUSUS_ESIGI = -8.0  # gunluk % degisim
ILERI_GUNLER = [1, 3, 5, 10]


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

    sert_g = {n: [] for n in ILERI_GUNLER}
    kosulsuz_g = {n: [] for n in ILERI_GUNLER}
    sembol_sonuc = {}
    ornek_tarihler = []

    for s, df in ham.items():
        gunluk_chg = df["Close"].pct_change() * 100
        sert_mask = gunluk_chg <= SERT_DUSUS_ESIGI

        for tarih in df.index[sert_mask]:
            ornek_tarihler.append({"sembol": s, "tarih": str(tarih.date()), "degisim_pct": round(float(gunluk_chg.loc[tarih]), 2)})

        s_sonuc = {"sert_dusus_sonrasi": {}, "kosulsuz_ortalama": {}}
        for n in ILERI_GUNLER:
            g = ileri_getiri(df["Close"], n)
            g_sert = g[sert_mask].dropna().tolist()
            g_kosulsuz = g.dropna().tolist()
            s_sonuc["sert_dusus_sonrasi"][f"t{n}"] = islem_ozet(g_sert)
            s_sonuc["kosulsuz_ortalama"][f"t{n}"] = islem_ozet(g_kosulsuz)
            sert_g[n].extend(g_sert)
            kosulsuz_g[n].extend(g_kosulsuz)
        sembol_sonuc[s] = s_sonuc

    genel_sert = {f"t{n}": islem_ozet(sert_g[n]) for n in ILERI_GUNLER}
    genel_kosulsuz = {f"t{n}": islem_ozet(kosulsuz_g[n]) for n in ILERI_GUNLER}

    tutarlilik = []
    for v in sembol_sonuc.values():
        a = v["sert_dusus_sonrasi"]["t5"]["isabet_pct"]
        b = v["kosulsuz_ortalama"]["t5"]["isabet_pct"]
        if a is not None and b is not None:
            tutarlilik.append(1 if a > b else 0)
    toparlanma_lehine_oran = round(100 * sum(tutarlilik) / len(tutarlilik), 1) if tutarlilik else None

    rapor = {
        "calisma": "Devre Kesici (Sert Dusus) Sonrasi Davranis Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi - gercek intraday devre kesici "
            "tetiklenmesini BIREBIR YAKALAMIYOR, gunluk degisim <= -%8 "
            "bir VEKIL olarak kullanildi."
        ),
        "sert_dusus_esigi_pct": SERT_DUSUS_ESIGI,
        "genel": {"sert_dusus_sonrasi": genel_sert, "kosulsuz_ortalama": genel_kosulsuz},
        "toparlanma_lehine_sembol_orani_T5": toparlanma_lehine_oran,
        "toplam_sert_dusus_olayi": len(ornek_tarihler),
        "en_son_10_ornek": sorted(ornek_tarihler, key=lambda x: x["tarih"])[-10:],
        "sembol_bazli": sembol_sonuc,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/devre_kesici_sonrasi_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"Toplam sert dusus olayi: {len(ornek_tarihler)}")
    print(f"SERT DUSUS SONRASI T1={genel_sert['t1']} T5={genel_sert['t5']} T10={genel_sert['t10']}")
    print(f"KOSULSUZ ORTALAMA    T1={genel_kosulsuz['t1']} T5={genel_kosulsuz['t5']} T10={genel_kosulsuz['t10']}")
    print(f"Sembol bazinda toparlanma-lehine oran (T5): %{toparlanma_lehine_oran}")
    print("Tamamlandi -> data/backtest/devre_kesici_sonrasi_sonuc.json")


if __name__ == "__main__":
    main()
