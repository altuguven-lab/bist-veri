"""
2-UYELI SEKTOR ESIK SIKILASTIRMA TESTI (22.09.2026)
======================================================
IP-8'de yapilan degisiklik: 2 uyeli sektorlerde (Savunma, Rafineri,
EnerjiUretim, Otomotiv, Telekom, Ulastirma) GIR esigi SRS_adj>=52/
EQS_adj>=65'ten SRS_adj>=58/EQS_adj>=70'e sikilastirildi. Gerekce:
tek hissenin sert hareketi sektoru TEK BASINA belirleyebiliyordu.

Bu script IP-8'in TAM SRS/EQS formulunu BIREBIR replike ETMIYOR (cok
buyuk bir is olurdu) - bunun yerine ALTI YATAN HIPOTEZI dogrudan test
ediyor: "iki uyenin kendi goreli gucu birbirinden AYRISTIGINDA (biri
guclu biri zayif), sektorun 'guclu' sinyali daha az GUVENILIR mi?"

Yontem: her cift icin gunluk RS_uye1 ve RS_uye2 (20-gunluk, XU100'e
gore) hesaplanir. "Ayrisma" = |RS_uye1 - RS_uye2|. Sektor GUCLU
sayildigi gunler (ortalama RS > esik) DUSUK ayrisma (uyumlu, "TEMIZ")
ve YUKSEK ayrisma ("TEK HISSE BASKIN") olarak ikiye ayrilir, ileri
getirileri (sektor ortalamasi) karsilastirilir.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi, IP-8'in TAM formulunun
basitlestirilmis bir vekili - kesin degil, yon verir.

Cikti: data/backtest/iki_uyeli_sektor_esik_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import veri_cek, gostergeler, ENDEKS

IKI_UYELI_SEKTORLER = {
    "Savunma": ["ASELS", "OTKAR"],
    "Rafineri": ["TUPRS", "PETKM"],
    "EnerjiUretim": ["ENJSA", "AKSEN"],
    "Otomotiv": ["FROTO", "TOASO"],
    "Telekom": ["TCELL", "TTKOM"],
    "Ulastirma": ["THYAO", "TAVHL"],
}
ILERI_GUNLER = [3, 10]
GUC_ESIGI = 2.0  # sektor "GUCLU" sayilmasi icin ort. RS (20g, XU100'e gore, %)
AYRISMA_ESIGI_PCT = 75  # bu yuzdelik ustu ayrisma "TEK HISSE BASKIN" sayilir


def rs20(close, xu_close):
    stk = close.pct_change(20) * 100
    idx = xu_close.pct_change(20).reindex(close.index).ffill() * 100
    return stk - idx


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
    xu = veri_cek(ENDEKS, start="2018-06-01")
    xu_close = xu["Close"]

    temiz_g = {n: [] for n in ILERI_GUNLER}
    baskin_g = {n: [] for n in ILERI_GUNLER}
    sektor_sonuc = {}

    for sek, (u1, u2) in IKI_UYELI_SEKTORLER.items():
        d1 = veri_cek(f"{u1}.IS", start="2018-06-01")
        d2 = veri_cek(f"{u2}.IS", start="2018-06-01")
        if d1 is None or d2 is None or len(d1) < 100 or len(d2) < 100:
            continue

        ortak = d1.index.intersection(d2.index)
        c1, c2 = d1.loc[ortak, "Close"], d2.loc[ortak, "Close"]
        rs1, rs2 = rs20(c1, xu_close), rs20(c2, xu_close)
        sektor_rs = (rs1 + rs2) / 2
        sektor_close = (c1 / c1.iloc[0] + c2 / c2.iloc[0]) / 2 * 100  # esit-agirlikli sentetik seri

        ayrisma = (rs1 - rs2).abs()
        ayrisma_esigi = ayrisma.quantile(AYRISMA_ESIGI_PCT / 100)

        guclu_mask = sektor_rs > GUC_ESIGI
        temiz_mask = guclu_mask & (ayrisma <= ayrisma_esigi)
        baskin_mask = guclu_mask & (ayrisma > ayrisma_esigi)

        s_sonuc = {"temiz": {}, "baskin": {},
                   "temiz_gun_sayisi": int(temiz_mask.sum()), "baskin_gun_sayisi": int(baskin_mask.sum())}
        for n in ILERI_GUNLER:
            g = ileri_getiri(sektor_close, n)
            g_temiz = g[temiz_mask].dropna().tolist()
            g_baskin = g[baskin_mask].dropna().tolist()
            s_sonuc["temiz"][f"t{n}"] = islem_ozet(g_temiz)
            s_sonuc["baskin"][f"t{n}"] = islem_ozet(g_baskin)
            temiz_g[n].extend(g_temiz)
            baskin_g[n].extend(g_baskin)
        sektor_sonuc[sek] = s_sonuc

    genel_temiz = {f"t{n}": islem_ozet(temiz_g[n]) for n in ILERI_GUNLER}
    genel_baskin = {f"t{n}": islem_ozet(baskin_g[n]) for n in ILERI_GUNLER}

    rapor = {
        "calisma": "IP-8 Iki-Uyeli Sektor Esik Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi. IP-8'in TAM SRS/EQS formulunu BIREBIR "
            "replike ETMIYOR - basitlestirilmis bir vekil (RS ayrismasi). "
            "Sonuc yon verir, IP-8'in gercek esik degerleri icin kesin "
            "kanit degildir."
        ),
        "parametreler": {"guc_esigi_rs_pct": GUC_ESIGI, "ayrisma_esigi_percentile": AYRISMA_ESIGI_PCT},
        "genel": {"temiz_uyumlu": genel_temiz, "baskin_tek_hisse": genel_baskin},
        "sektor_bazli": sektor_sonuc,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/iki_uyeli_sektor_esik_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"TEMIZ (uyumlu)     T+3={genel_temiz['t3']}, T+10={genel_temiz['t10']}")
    print(f"BASKIN (tek hisse) T+3={genel_baskin['t3']}, T+10={genel_baskin['t10']}")
    print("Tamamlandi -> data/backtest/iki_uyeli_sektor_esik_sonuc.json")


if __name__ == "__main__":
    main()
