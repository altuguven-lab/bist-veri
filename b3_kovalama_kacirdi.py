"""
B3 FAZ V0: KOVALAMA VETOSU - KACIRDI VAKALARI TESTI (17.09.2026)
==================================================================
KULUCKA SONRASI BIRIKIM B3: "KOVALAMA yumusatma (yasak->WATCH/yarim
boyut)". Dayanak: Madde 21, 10.07 TRMET KACIRDI vakasi. Test kriteri
(backlog'un kendi sozleriyle): "KACIRDI vakalarinin T+3 sonuclari
>%55 pozitifse gecis [yapilsin]".

BULUNAN KOD (V162_1_yama.txt satir 3531-3537):
  _p3TetikSeviye = ta.highest(high[1], pTepePencere)      // pTepePencere=10
  _p3TepeAsim    = close > _p3TetikSeviye
  _p3HacimVar    = relVol >= pTetikHacim                   // pTetikHacim=1.2
  _p3Kovalama    = close > _p3TetikSeviye * (1 + pKovalamaPct/100)  // pKovalamaPct=1.5

_p3Kovalama SERT VETO - bandin (%1.5) uzerindeyse P3_SKOR_AL hic
uretilmiyor (not _p3Kovalama sarti P3_AL'de VAR).

V0 KISITI (durustluk notu): _p3Baglam (skor tabani/yukselis/rejim/
HTF/DNA filtreleri, scoreSmoothedFinal'a bagli - KGS gibi Python'a
tasinmadi) burada ATLANDI. Bu script yalnizca TETIK+HACIM+KOVALAMA
UCLUSUNU test ediyor - gercek P3_SKOR_AL'in TAM baglam suzgeci degil.
Yani "KACIRDI" burada "tepe asimi + hacim VAR ama kovalama bandinin
disinda" demek - gercek P3 skor/rejim baglamini da gecmis olan
alt-kumeyi AYRICA daraltmiyor (V0'da daha genis bir aday havuzu).

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.

Cikti: data/backtest/b3_kovalama_kacirdi_sonuc.json
"""
import json
import sys
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler

PENCERE = 10          # pTepePencere
HACIM_ESIGI = 1.2     # pTetikHacim
KOVALAMA_PCT = 1.5    # pKovalamaPct (varsayilan)
ILERI_GUNLER = [3, 10]

# kovalama bandini kademelere ayiralim - "ne kadar disinda" sorusuna
# cevap versin, tek-esikli degil (WATCH/yarim boyut tasarimina girdi olsun)
BANT_KADEME = [(1.5, 3.0, "1.5-3.0_bant"), (3.0, 6.0, "3.0-6.0_bant"), (6.0, None, "6.0_uzeri")]


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

    alindi_g = {n: [] for n in ILERI_GUNLER}
    kacirdi_g = {n: [] for n in ILERI_GUNLER}
    kacirdi_kademe_g = {k[2]: {n: [] for n in ILERI_GUNLER} for k in BANT_KADEME}

    sembol_sonuc = {}
    trmet_2024_07_ornekler = []

    for s, df in ham.items():
        tetikSeviye = df["High"].shift(1).rolling(PENCERE).max()
        tepeAsim = df["Close"] > tetikSeviye
        hacimVar = df["relVol"] >= HACIM_ESIGI
        aday = tepeAsim & hacimVar  # _p3Baglam ATLANDI (V0 kisiti)

        asimYuzde = (df["Close"] / tetikSeviye - 1) * 100  # bandin ne kadar disinda
        kovalama = df["Close"] > tetikSeviye * (1 + KOVALAMA_PCT / 100)

        alindi_mask = aday & (~kovalama)
        kacirdi_mask = aday & kovalama

        s_sonuc = {"alindi": {}, "kacirdi": {}, "kacirdi_gun_sayisi": int(kacirdi_mask.sum()),
                   "alindi_gun_sayisi": int(alindi_mask.sum())}
        for n in ILERI_GUNLER:
            g = ileri_getiri(df["Close"], n)
            g_alindi = g[alindi_mask].dropna().tolist()
            g_kacirdi = g[kacirdi_mask].dropna().tolist()
            s_sonuc["alindi"][f"t{n}"] = islem_ozet(g_alindi)
            s_sonuc["kacirdi"][f"t{n}"] = islem_ozet(g_kacirdi)
            alindi_g[n].extend(g_alindi)
            kacirdi_g[n].extend(g_kacirdi)

            for alt, ust, etiket in BANT_KADEME:
                if ust is None:
                    kademe_mask = kacirdi_mask & (asimYuzde >= alt)
                else:
                    kademe_mask = kacirdi_mask & (asimYuzde >= alt) & (asimYuzde < ust)
                kacirdi_kademe_g[etiket][n].extend(g[kademe_mask].dropna().tolist())

        sembol_sonuc[s] = s_sonuc

        if s == "TRMET":
            ornekler = df.index[kacirdi_mask & (df.index >= "2024-06-15") & (df.index <= "2024-07-31")]
            trmet_2024_07_ornekler = [str(d.date()) for d in ornekler]

    genel_alindi = {f"t{n}": islem_ozet(alindi_g[n]) for n in ILERI_GUNLER}
    genel_kacirdi = {f"t{n}": islem_ozet(kacirdi_g[n]) for n in ILERI_GUNLER}
    genel_kacirdi_kademeli = {
        etiket: {f"t{n}": islem_ozet(kacirdi_kademe_g[etiket][n]) for n in ILERI_GUNLER}
        for etiket in kacirdi_kademe_g
    }

    t3_kacirdi_pozitif = genel_kacirdi.get("t3", {}).get("isabet_pct")
    karar_kriteri_gecti = (t3_kacirdi_pozitif is not None and t3_kacirdi_pozitif > 55.0)

    rapor = {
        "calisma": "B3 Faz V0 - Kovalama Vetosu Kacirdi Vakalari Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi. _p3Baglam (skor/rejim/HTF/DNA filtreleri) "
            "ATLANDI - burada 'aday' yalniz tepe-asimi+hacim, gercek P3_SKOR_AL'in "
            "TAM on-sartlarini tasimiyor (daha genis havuz). TEK BASINA hicbir kod "
            "degisikligine GEREKCE OLAMAZ - B3'un ilk kesif adimidir."
        ),
        "backlog_karar_kriteri": "KACIRDI vakalarinin T+3 sonuclari >%55 pozitifse gecis yapilsin",
        "t3_kacirdi_isabet_pct": t3_kacirdi_pozitif,
        "karar_kriteri_gecti_mi": karar_kriteri_gecti,
        "genel": {"alindi": genel_alindi, "kacirdi": genel_kacirdi},
        "kacirdi_bant_kademeli": genel_kacirdi_kademeli,
        "sembol_bazli": sembol_sonuc,
        "trmet_2024_06_07_kacirdi_gunleri": trmet_2024_07_ornekler,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/b3_kovalama_kacirdi_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print(f"T+3 KACIRDI isabet: %{t3_kacirdi_pozitif} (kriter: >%55) -> "
          f"{'GECTI' if karar_kriteri_gecti else 'GECMEDI'}")
    print("Tamamlandi -> data/backtest/b3_kovalama_kacirdi_sonuc.json")


if __name__ == "__main__":
    main()
