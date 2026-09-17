"""
B1 FAZ V1: CIFTE-ESIK vs TEK-ESIK GATE KIYASI (17.09.2026)
============================================================
Faz V0'in bulgusu: corr(KGS, entryScoreBase) = 0.963, 30/30 sembolde
0.953-0.969 bandinda, sektor farki yok (data/backtest/
kgs_gunluk_port_sonuc.json).

Bu faz o bulguyu ISLEME SOKAR: V162 kodunda onlarca yerde gordugumuz
"_entryScore >= X and _kgs >= Y" cifte-kapi deseninin (ornegin
f_v114Decision'daki _scoreAlGate = _entryScore>=85 and _kgs>=75),
neredeyse mukerrer iki degiskeni AYNI ANDA yuksek isteyerek huniyi
gerekenden fazla dararttigi hipotezini test eder.

YONTEM (ONEMLI KISIT): Faz V0'in entryScoreBase'i TAM entryScore
DEGIL (yalniz _base terimi - trend/sektor/akis/CVD/pencere/momentum/
HTF/RR/volatilite/yas cezasi haric). Bu yuzden gercek Pine esikleri
(85, 75 gibi MUTLAK puanlar) buraya DOGRUDAN uygulanamaz - olcek
uyusmuyor. Bunun yerine YUZDELIK (percentile) esdegerligi kullanilir:
gercek kod "KGS ve entryScore ikisi de USTTE %25'te olsun" diyor
gibi YORUMLANIR (75/100 esigi kabaca ustteki dortte-bir bolgeye
denk dusuyor), ve iki senaryo ayni yuzdelik esikle kiyaslanir:

  IKI_KAPI (mevcut kod deseni): KGS yuzdelik >= P VE entryScoreBase
    yuzdelik >= P (ikisi AYNI ANDA yuksek olmali)
  TEK_KAPI (B1 onerisi): yalniz entryScoreBase yuzdelik >= P
    (KGS zaten _base'in %38'i, ayri sart KOYMUYOR - entryScoreBase
    KGS'yi ZATEN tasiyor)

Yuzdelik, HER SEMBOLUN KENDI GECMISI icinde (rolling 252 gun ~ 1 yil)
hesaplanir - boylece "bugun bu hisse icin gorece guclu bir gun mu"
sorusuna cevap verir, ham puan degil.

KIYAS: iki kapi turunun (a) ne siklikta ates ettigi (b) T+3/T+10
ileri getiri ve isabet orani (İP-2 ile AYNI metrik, dogrudan
kiyaslanabilir olsun diye).

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor. Bu script'in ciktisi
DOGRUDAN bir esik/agirlik degisikligi DEGIL - B1 icin kurula
sunulacak KARAR DESTEK verisi, GUNLUK YAKLASIKLIK seviyesinde
(V0'in durustluk notu AYNEN GECERLI).

Cikti: data/backtest/b1_esik_revizyon_sonuc.json
"""
import json
import sys
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import (
    SEMBOLLER, SEKTOR, SEKTOR_ENDEKS_TICKER, ENDEKS, BAS,
    veri_cek, gostergeler, kgs_hesapla, volume_quality_ve_accel,
    entry_score_base,
)

YUZDELIK_ESIGI = 75  # "ustteki dortte-bir" - Pine'daki >=70/>=75 esiklerine kaba karsilik
PENCERE = 252  # ~1 islem yili, yuzdelik hesaplaninca kullanilan gecmis pencere
ILERI_GUNLER = [3, 10]  # İP-2 ile AYNI (T+3, T+10) - dogrudan kiyaslanabilir olsun


def yuzdelik_rank(seri, pencere):
    return seri.rolling(pencere, min_periods=60).apply(
        lambda s: pd.Series(s).rank(pct=True).iloc[-1] * 100, raw=False)


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
    endeks = veri_cek(ENDEKS, start=BAS)
    if endeks is None:
        print("HATA: XU100 verisi cekilemedi, durduruluyor", file=sys.stderr)
        return
    endeks_g = gostergeler(endeks)
    idxRoc = endeks_g["stkRoc"]

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

    sembol_sonuc = {}
    iki_kapi_havuz = {n: [] for n in ILERI_GUNLER}
    tek_kapi_havuz = {n: [] for n in ILERI_GUNLER}
    iki_kapi_gun_toplam = 0
    tek_kapi_gun_toplam = 0

    for s, df in ham.items():
        sek = SEKTOR[s]
        sec_close = sektor_kapanis.get(sek, sektor_proxy.get(sek, endeks["Close"]))
        secRoc = sec_close.pct_change(20).reindex(df.index).ffill() * 100
        secStrong = (secRoc > idxRoc.reindex(df.index) + 0.5).fillna(False)

        kgs_df = kgs_hesapla(df, idxRoc, secRoc, secStrong)
        volQ, accel = volume_quality_ve_accel(df)
        entryBase = entry_score_base(kgs_df["kgs"], volQ, accel)

        kgs_yzd = yuzdelik_rank(kgs_df["kgs"], PENCERE)
        entry_yzd = yuzdelik_rank(entryBase, PENCERE)

        iki_kapi = (kgs_yzd >= YUZDELIK_ESIGI) & (entry_yzd >= YUZDELIK_ESIGI)
        tek_kapi = entry_yzd >= YUZDELIK_ESIGI

        getiri = {n: ileri_getiri(df["Close"], n) for n in ILERI_GUNLER}

        sonuc_bu_sembol = {"iki_kapi": {}, "tek_kapi": {}}
        for n in ILERI_GUNLER:
            g_iki = getiri[n][iki_kapi].dropna().tolist()
            g_tek = getiri[n][tek_kapi].dropna().tolist()
            sonuc_bu_sembol["iki_kapi"][f"t{n}"] = islem_ozet(g_iki)
            sonuc_bu_sembol["tek_kapi"][f"t{n}"] = islem_ozet(g_tek)
            iki_kapi_havuz[n].extend(g_iki)
            tek_kapi_havuz[n].extend(g_tek)

        iki_kapi_gun = int(iki_kapi.sum())
        tek_kapi_gun = int(tek_kapi.sum())
        iki_kapi_gun_toplam += iki_kapi_gun
        tek_kapi_gun_toplam += tek_kapi_gun

        sembol_sonuc[s] = {
            "sektor": sek,
            "iki_kapi_gun_sayisi": iki_kapi_gun,
            "tek_kapi_gun_sayisi": tek_kapi_gun,
            "iki_kapi_tek_kapi_orani_pct": round(100 * iki_kapi_gun / tek_kapi_gun, 1) if tek_kapi_gun else None,
            **sonuc_bu_sembol,
        }
        print(f"{s}: iki_kapi_gun={iki_kapi_gun}, tek_kapi_gun={tek_kapi_gun}")

    genel = {
        "iki_kapi": {f"t{n}": islem_ozet(iki_kapi_havuz[n]) for n in ILERI_GUNLER},
        "tek_kapi": {f"t{n}": islem_ozet(tek_kapi_havuz[n]) for n in ILERI_GUNLER},
        "iki_kapi_toplam_gun": iki_kapi_gun_toplam,
        "tek_kapi_toplam_gun": tek_kapi_gun_toplam,
        "iki_kapi_tek_kapi_orani_pct": round(100 * iki_kapi_gun_toplam / tek_kapi_gun_toplam, 1) if tek_kapi_gun_toplam else None,
    }

    rapor = {
        "calisma": "B1 Faz V1 - Cifte-Esik vs Tek-Esik Gate Kiyasi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "yontem_notu": (
            f"Yuzdelik esdegerligi kullanildi (esik={YUZDELIK_ESIGI}. yuzdelik, "
            f"{PENCERE} gunluk kayan pencerede), gercek Pine'daki MUTLAK puan "
            "esikleriyle (85, 75 vb.) DOGRUDAN AYNI DEGIL - kaba karsiliktir."
        ),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi (V0 ile AYNI kisitlar - bkz. "
            "kgs_gunluk_port_sonuc.json). Bu TEK BASINA hicbir esik/agirlik "
            "degisikligine GEREKCE OLAMAZ - kurula sunulacak karar-destek "
            "verisidir, 15dk gercek veriyle teyit gerektirir."
        ),
        "genel": genel,
        "sembol_bazli": sembol_sonuc,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/b1_esik_revizyon_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print(f"\nTamamlandi -> data/backtest/b1_esik_revizyon_sonuc.json")
    print(f"IKI_KAPI toplam gun={iki_kapi_gun_toplam}, TEK_KAPI toplam gun={tek_kapi_gun_toplam}, "
          f"oran=%{genel['iki_kapi_tek_kapi_orani_pct']}")


if __name__ == "__main__":
    main()
