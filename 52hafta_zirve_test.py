"""
52-HAFTALIK ZIRVEYE YAKINLIK ETKISI TESTI (25.09.2026)
=========================================================
George&Hwang (2004): fiyatin 52-haftalik ZIRVEYE YAKINLIGI, salt son-
donem getiriden DAHA GUCLU bir momentum sinyali olabilir. Bir hisse
%20 yukselmis olabilir ama hala kendi 52-haftalik zirvesinin cok
altindaysa (once daha buyuk dusmus), bu farkli bir durum - zirveye
YAKIN olan hisseler literatur'e gore DAHA GUCLU devam ediyor.

YONTEM: yakinlik = Kapanis / (252-gunluk kayan maksimum Yuksek). 1.0'a
yakin = zirvede/zirveye yakin. Bu olcuye gore GUNLUK olarak ust %20
("ZIRVEYE_YAKIN") ve alt %20 ("ZIRVEDEN_UZAK") etiketlenip ileri
getirileri karsilastiriliyor. AYRICA karsilastirma icin, ayni gunlerde
basit 20-gunluk getiriye gore siralama da hesaplanip iki sinyalin
UYUSTUGU/UYUSMADIGI gunler ayri raporlaniyor (George&Hwang'in "salt
getiriden daha guclu" iddiasini dogrudan test etmek icin).

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi. 252-gunluk pencere ilk yil
verisi olmayan donemlerde NaN doner (dogal).

Cikti: data/backtest/52hafta_zirve_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler

ILERI_GUNLER = [5, 10]
PERCENTILE = 20
PENCERE = 252


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
        if d is not None and len(d) > 350:
            ham[s] = gostergeler(d)

    yakin_g = {n: [] for n in ILERI_GUNLER}
    uzak_g = {n: [] for n in ILERI_GUNLER}
    uyusan_yakin_g = {n: [] for n in ILERI_GUNLER}  # zirveye yakin AMA getiri-sirasi dusuk
    sembol_sonuc = {}

    for s, df in ham.items():
        zirve_252 = df["High"].rolling(PENCERE, min_periods=200).max()
        yakinlik = df["Close"] / zirve_252

        yakinlik_valid = yakinlik.dropna()
        if len(yakinlik_valid) < 100:
            continue
        ust_esik = yakinlik.quantile(1 - PERCENTILE / 100)
        alt_esik = yakinlik.quantile(PERCENTILE / 100)
        yakin_mask = yakinlik >= ust_esik
        uzak_mask = yakinlik <= alt_esik

        # basit 20-gunluk getiri sirasi ile karsilastirma: zirveye yakin AMA
        # son 20 gunde ORTALAMA/dusuk getirili gunler (George&Hwang'in
        # "yakinlik, getiriden bagimsiz ek bilgi tasiyor mu" sorusu)
        ret20 = df["Close"].pct_change(20) * 100
        ret20_medyan_alti = ret20 < ret20.quantile(0.5)
        yakin_ama_dusuk_getiri_mask = yakin_mask & ret20_medyan_alti

        s_sonuc = {"zirveye_yakin": {}, "zirveden_uzak": {}, "yakin_ama_dusuk_getirili": {}}
        for n in ILERI_GUNLER:
            g = ileri_getiri(df["Close"], n)
            g_yakin = g[yakin_mask].dropna().tolist()
            g_uzak = g[uzak_mask].dropna().tolist()
            g_uyusan = g[yakin_ama_dusuk_getiri_mask].dropna().tolist()
            s_sonuc["zirveye_yakin"][f"t{n}"] = islem_ozet(g_yakin)
            s_sonuc["zirveden_uzak"][f"t{n}"] = islem_ozet(g_uzak)
            s_sonuc["yakin_ama_dusuk_getirili"][f"t{n}"] = islem_ozet(g_uyusan)
            yakin_g[n].extend(g_yakin)
            uzak_g[n].extend(g_uzak)
            uyusan_yakin_g[n].extend(g_uyusan)
        sembol_sonuc[s] = s_sonuc

    genel_yakin = {f"t{n}": islem_ozet(yakin_g[n]) for n in ILERI_GUNLER}
    genel_uzak = {f"t{n}": islem_ozet(uzak_g[n]) for n in ILERI_GUNLER}
    genel_uyusan = {f"t{n}": islem_ozet(uyusan_yakin_g[n]) for n in ILERI_GUNLER}

    tutarlilik = []
    for v in sembol_sonuc.values():
        a = v["zirveye_yakin"]["t10"]["isabet_pct"]
        b = v["zirveden_uzak"]["t10"]["isabet_pct"]
        if a is not None and b is not None:
            tutarlilik.append(1 if a > b else 0)
    yakin_lehine_oran = round(100 * sum(tutarlilik) / len(tutarlilik), 1) if tutarlilik else None

    rapor = {
        "calisma": "52-Haftalik Zirveye Yakinlik Etkisi Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": "GUNLUK BAR yaklasikligi. 252-gunluk pencere min 200 gozlem gerektiriyor.",
        "genel": {"zirveye_yakin": genel_yakin, "zirveden_uzak": genel_uzak},
        "zirveye_yakin_lehine_sembol_orani_T10": yakin_lehine_oran,
        "ek_test_yakin_ama_dusuk_20g_getirili": {
            "aciklama": "Zirveye yakin AMA son-20-gun getiri siralamasinda medyanin altinda olan gunler - yakinligin getiriden BAGIMSIZ ek bilgi tasiyip tasimadigini gosterir",
            "genel": genel_uyusan,
        },
        "sembol_bazli": sembol_sonuc,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/52hafta_zirve_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"ZIRVEYE YAKIN  T5={genel_yakin['t5']} T10={genel_yakin['t10']}")
    print(f"ZIRVEDEN UZAK  T5={genel_uzak['t5']} T10={genel_uzak['t10']}")
    print(f"YAKIN-AMA-DUSUK-GETIRILI T5={genel_uyusan['t5']} T10={genel_uyusan['t10']}")
    print(f"Sembol bazinda zirveye-yakin lehine oran (T10): %{yakin_lehine_oran}")
    print("Tamamlandi -> data/backtest/52hafta_zirve_sonuc.json")


if __name__ == "__main__":
    main()
