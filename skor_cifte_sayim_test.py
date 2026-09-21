"""
SKOR CIFTE-SAYIM TESTI (21.09.2026)
=====================================
Son buyuk incelemenin iddiasi: "RS gucu hem dogrudan skor aliyor hem
liderlik skorunu hem sektor skorunu hem bazi giris motorlarinin
kosulunu karsiliyor" - yani ayni alti-yatan bilgi (RS/rsIndex/rsSector)
birden fazla skor bileseninde TEKRAR odullendirilebilir.

B1, KGS ile entryScore ARASINDAKI (iki AYRI degisken) korelasyonu test
etmisti. Bu test farkli: KGS'nin KENDI 7 alt-skoru ARASINDAKI korelasyona
bakiyor - ozellikle kgsRs (dogrudan RS-tabanli) ile kgsSector (RS-turevi
isStockLeadingSector/isSectorStrongEff kullaniyor) arasinda.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi (kgs_gunluk_port.py'nin V0
kisitlari AYNEN gecerli - bkz. o script'in kendi durustluk notu).
Yuksek korelasyon TEK BASINA "hata" kaniti degildir - bazi alt-skorlarin
ortak bir alti-yatan gercekligi (gercek trend gucu) yansitmasi DOGAL
olabilir. Bu script yalniz BUYUKLUGU olcer, yorumu kurul yapar.

Cikti: data/backtest/skor_cifte_sayim_sonuc.json
"""
import json
import sys
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import (
    SEMBOLLER, SEKTOR, SEKTOR_ENDEKS_TICKER, ENDEKS, BAS,
    veri_cek, gostergeler, kgs_hesapla,
)

ALT_SKORLAR = ["kgsTrend", "kgsEma", "kgsRs", "kgsVol", "kgsSector", "kgsCvd", "kgsKurum"]


def main():
    endeks = veri_cek(ENDEKS, start=BAS)
    if endeks is None:
        print("HATA: XU100 verisi cekilemedi", file=sys.stderr)
        return
    idxRoc = gostergeler(endeks)["stkRoc"]

    sektor_kapanis = {}
    for sek, tkr in SEKTOR_ENDEKS_TICKER.items():
        d = veri_cek(tkr, start=BAS)
        if d is not None and len(d) > 100:
            sektor_kapanis[sek] = d["Close"]

    ham = {}
    for s in SEMBOLLER:
        d = veri_cek(f"{s}.IS", start=BAS)
        if d is not None and len(d) > 250:
            ham[s] = gostergeler(d)

    sektor_proxy = {}
    for sek in set(SEKTOR.values()):
        uyeler = [s for s, sk in SEKTOR.items() if sk == sek and s in ham]
        if len(uyeler) >= 2:
            kapaniclar = pd.concat([ham[s]["Close"].pct_change() for s in uyeler], axis=1).mean(axis=1)
            sektor_proxy[sek] = 100 * (1 + kapaniclar.fillna(0)).cumprod()

    tum_alt_skorlar = []
    for s, df in ham.items():
        sek = SEKTOR[s]
        sec_close = sektor_kapanis.get(sek, sektor_proxy.get(sek, endeks["Close"]))
        secRoc = sec_close.pct_change(20).reindex(df.index).ffill() * 100
        secStrong = (secRoc > idxRoc.reindex(df.index) + 0.5).fillna(False)
        kgs_df = kgs_hesapla(df, idxRoc, secRoc, secStrong)
        tum_alt_skorlar.append(kgs_df[ALT_SKORLAR].dropna())

    birlesik = pd.concat(tum_alt_skorlar, axis=0)
    korelasyon = birlesik.corr()

    # en yuksek ciftleri (kendisiyle olan haric) siraliyoruz
    ciftler = []
    for i, a in enumerate(ALT_SKORLAR):
        for b in ALT_SKORLAR[i + 1:]:
            ciftler.append((a, b, round(float(korelasyon.loc[a, b]), 3)))
    ciftler.sort(key=lambda x: -abs(x[2]))

    rapor = {
        "calisma": "Skor Cifte-Sayim Testi (KGS alt-skorlari arasi korelasyon)",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi (kgs_gunluk_port.py V0 kisitlari gecerli). "
            "Yuksek korelasyon TEK BASINA hata kaniti degildir, ortak alti-yatan "
            "gerceklik (gercek trend gucu) yansitiyor olabilir - yorum kurula ait."
        ),
        "gozlem_sayisi": int(len(birlesik)),
        "korelasyon_matrisi": {a: {b: round(float(korelasyon.loc[a, b]), 3) for b in ALT_SKORLAR} for a in ALT_SKORLAR},
        "ciftler_siralanmis": [{"a": a, "b": b, "korelasyon": k} for a, b, k in ciftler],
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/skor_cifte_sayim_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"Gozlem sayisi: {len(birlesik)}")
    print("En yuksek korelasyonlu ciftler:")
    for a, b, k in ciftler[:10]:
        print(f"  {a} - {b}: {k}")
    print("\nTamamlandi -> data/backtest/skor_cifte_sayim_sonuc.json")


if __name__ == "__main__":
    main()
