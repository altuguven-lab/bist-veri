"""
MOMENTUM-KARSITI ORGUNTU: REJIM-KOSULLU DOGRULAMA (25.09.2026)
=================================================================
Onceki iki testin (sektor momentumu, 52-hafta zirve) IKISI de BIST'te
"guc/zirve yakinligi" sinyallerinin BEKLENENIN TERSINE calistigini
gosterdi (zayiflik, guclulukten daha iyi ileri getiri verdi). Bu script
o bulgunun KRIZE OZGU (yalniz RISK-OFF donemde gecerli) mi, yoksa
BIST'in GENEL bir yapisal ozelligi mi oldugunu ayirt ediyor.

YONTEM: Ayni iki sinyal (sektor gucu, 52-hafta zirve yakinligi),
XU100'un EMA60 uzerinde/altinda olmasina gore RISK-ON/RISK-OFF
ayriminda AYRI AYRI test ediliyor.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi. Rejim siniflandirmasi
BASITLESTIRILMIS bir vekil (onceki rejim-kosullu testle AYNI yontem).
Sektor listesi onceki sektor-momentumu testiyle AYNI (9 sektor/21
hisse, IP-8'in tam 11-sektor listesini birebir kapsamiyor).

Cikti: data/backtest/momentum_karsiti_rejim_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import veri_cek, gostergeler, ENDEKS

SEKTORLER = {
    "Banka": ["AKBNK", "GARAN", "ISCTR", "YKBNK", "HALKB", "VAKBN"],
    "Holding": ["KCHOL", "SAHOL", "ENKAI"],
    "Savunma": ["ASELS", "OTKAR"],
    "Rafineri": ["TUPRS", "PETKM"],
    "EnerjiUretim": ["ENJSA", "AKSEN"],
    "Otomotiv": ["FROTO", "TOASO"],
    "Telekom": ["TCELL", "TTKOM"],
    "Ulastirma": ["THYAO", "TAVHL"],
    "Tuketim": ["BIMAS", "MGROS", "ULKER"],
}
FORMASYON_GUN = 20
PENCERE_52H = 252
ILERI_GUNLER = [5, 10]
PERCENTILE = 20


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
    xu_ema60 = xu["Close"].ewm(span=60, adjust=False).mean()
    xu_ret20 = xu["Close"].pct_change(FORMASYON_GUN) * 100
    risk_on_seri = xu["Close"] > xu_ema60

    tum_semboller = sorted(set(s for uyeler in SEKTORLER.values() for s in uyeler))
    ham = {}
    for s in tum_semboller:
        d = veri_cek(f"{s}.IS", start="2018-06-01")
        if d is not None and len(d) > 350:
            ham[s] = gostergeler(d)

    rapor = {"calisma": "Momentum-Karsiti Orguntu - Rejim-Kosullu Dogrulama",
             "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}

    # === [1] SEKTOR MOMENTUMU - rejim kosullu ===
    rel_ret = {s: (df["Close"].pct_change(FORMASYON_GUN) * 100) - xu_ret20.reindex(df.index).ffill() for s, df in ham.items()}
    ortak_index = None
    for s in ham:
        ortak_index = ham[s].index if ortak_index is None else ortak_index.union(ham[s].index)
    sektor_guc = pd.DataFrame(index=ortak_index)
    for sek, uyeler in SEKTORLER.items():
        seriler = [rel_ret[s].reindex(ortak_index) for s in uyeler if s in rel_ret]
        sektor_guc[sek] = pd.concat(seriler, axis=1).mean(axis=1)
    sektor_rank = sektor_guc.rank(axis=1, ascending=False)
    n_sektor = len(SEKTORLER)
    ust_esik, alt_esik = n_sektor / 3, n_sektor - n_sektor / 3
    risk_on_reindexed = risk_on_seri.reindex(ortak_index).ffill().fillna(False)

    sektor_sonuc = {}
    for rejim_adi, rejim_kosulu in [("RISK_ON", risk_on_reindexed), ("RISK_OFF", ~risk_on_reindexed)]:
        guclu_g = {n: [] for n in ILERI_GUNLER}
        zayif_g = {n: [] for n in ILERI_GUNLER}
        for sek, uyeler in SEKTORLER.items():
            guclu_mask_base = (sektor_rank[sek] <= ust_esik) & rejim_kosulu
            zayif_mask_base = (sektor_rank[sek] > alt_esik) & rejim_kosulu
            for s in uyeler:
                if s not in ham:
                    continue
                df = ham[s]
                guclu_mask = guclu_mask_base.reindex(df.index).fillna(False)
                zayif_mask = zayif_mask_base.reindex(df.index).fillna(False)
                for n in ILERI_GUNLER:
                    g = ileri_getiri(df["Close"], n)
                    guclu_g[n].extend(g[guclu_mask].dropna().tolist())
                    zayif_g[n].extend(g[zayif_mask].dropna().tolist())
        sektor_sonuc[rejim_adi] = {
            "guclu_sektor": {f"t{n}": islem_ozet(guclu_g[n]) for n in ILERI_GUNLER},
            "zayif_sektor": {f"t{n}": islem_ozet(zayif_g[n]) for n in ILERI_GUNLER},
        }
        print(f"[SEKTOR-{rejim_adi}] GUCLU T10={sektor_sonuc[rejim_adi]['guclu_sektor']['t10']} "
              f"ZAYIF T10={sektor_sonuc[rejim_adi]['zayif_sektor']['t10']}")
    rapor["sektor_momentumu_rejim_kosullu"] = sektor_sonuc

    # === [2] 52-HAFTA ZIRVE - rejim kosullu ===
    zirve_sonuc = {}
    for rejim_adi, rejim_kosulu_seri in [("RISK_ON", risk_on_seri), ("RISK_OFF", ~risk_on_seri)]:
        yakin_g = {n: [] for n in ILERI_GUNLER}
        uzak_g = {n: [] for n in ILERI_GUNLER}
        for s, df in ham.items():
            zirve_252 = df["High"].rolling(PENCERE_52H, min_periods=200).max()
            yakinlik = df["Close"] / zirve_252
            if yakinlik.dropna().shape[0] < 100:
                continue
            ust = yakinlik.quantile(1 - PERCENTILE / 100)
            alt = yakinlik.quantile(PERCENTILE / 100)
            rejim_mask = rejim_kosulu_seri.reindex(df.index).ffill().fillna(False)
            yakin_mask = (yakinlik >= ust) & rejim_mask
            uzak_mask = (yakinlik <= alt) & rejim_mask
            for n in ILERI_GUNLER:
                g = ileri_getiri(df["Close"], n)
                yakin_g[n].extend(g[yakin_mask].dropna().tolist())
                uzak_g[n].extend(g[uzak_mask].dropna().tolist())
        zirve_sonuc[rejim_adi] = {
            "zirveye_yakin": {f"t{n}": islem_ozet(yakin_g[n]) for n in ILERI_GUNLER},
            "zirveden_uzak": {f"t{n}": islem_ozet(uzak_g[n]) for n in ILERI_GUNLER},
        }
        print(f"[ZIRVE-{rejim_adi}] YAKIN T10={zirve_sonuc[rejim_adi]['zirveye_yakin']['t10']} "
              f"UZAK T10={zirve_sonuc[rejim_adi]['zirveden_uzak']['t10']}")
    rapor["zirve_yakinligi_rejim_kosullu"] = zirve_sonuc

    rapor["durustluk_notu"] = (
        "GUNLUK BAR yaklasikligi. Rejim siniflandirmasi BASITLESTIRILMIS "
        "bir vekil (XU100 EMA60 ustunde/altinda). Sektor listesi 9/11 "
        "sektoru kapsiyor."
    )

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/momentum_karsiti_rejim_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print("\nTamamlandi -> data/backtest/momentum_karsiti_rejim_sonuc.json")


if __name__ == "__main__":
    main()
