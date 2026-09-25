"""
DIP vs KOVALAMA - UC EK VARYASYON (24.09.2026)
=================================================
Onceki testin (dip_vs_kovalama_test.py) devami. Literatur taramasindan
uc ek boyut test ediliyor:

A) FORMASYON PENCERESI TARAMASI - onceki test yalniz 5/10 gunluk oncul
   pencere kullanmisti. Klasik momentum literaturu (Jegadeesh&Titman
   1993) 3-12 AYLIK ufuktan bahsediyor - 20 (1 ay) ve 60 (3 ay) gunluk
   pencereler eklendi.

B) HACIM-KOSULLU DUSUS - Lee&Swaminathan (2000): hacim, momentum/
   tersine-donus etkisini guclendiriyor. "Kapitulasyon" (yuksek hacimli
   sert dusus) ile "sessiz dip" (dusuk hacimli, dikkat cekmeyen dusus)
   ayri test ediliyor - BIST'in devre-kesici gecmisiyle (16 Eylul vb.)
   dogrudan ilgili.

C) REJIM-KOSULLU TEST - Daniel&Moskowitz (2016): momentum stratejileri
   ozellikle PIYASA COKUSU SONRASI donemde ciddi zarar edebiliyor.
   XU100'un kendi 60-gunluk trendine gore RISK-ON/RISK-OFF ayrimi
   yapilip, dip/kovalama avantaji ikisinde ayri olculuyor.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi. Rejim siniflandirmasi
BASITLESTIRILMIS bir vekil (XU100'un kendi EMA60 uzerinde/altinda
olmasi) - V162/IP-8'in KENDI rejim mantigini BIREBIR REPLIKE ETMIYOR.

Cikti: data/backtest/dip_kovalama_varyasyon_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler, ENDEKS

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


def sembol_tutarlilik(sembol_sonuc, grup_a, grup_b, ufuk="t10"):
    say = []
    for v in sembol_sonuc.values():
        a = v[grup_a][ufuk]["isabet_pct"]
        b = v[grup_b][ufuk]["isabet_pct"]
        if a is not None and b is not None:
            say.append(1 if a > b else 0)
    return round(100 * sum(say) / len(say), 1) if say else None


def main():
    xu = veri_cek(ENDEKS, start="2018-06-01")
    xu_ema60 = xu["Close"].ewm(span=60, adjust=False).mean()
    xu_riskOn = (xu["Close"] > xu_ema60).reindex  # asagida her sembolun index'ine hizalanacak

    ham = {}
    for s in SEMBOLLER:
        d = veri_cek(f"{s}.IS", start="2018-06-01")
        if d is not None and len(d) > 300:
            ham[s] = gostergeler(d)

    rapor = {"calisma": "Dip vs Kovalama - Ek Varyasyonlar", "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}

    # === A) FORMASYON PENCERESI TARAMASI (20 ve 60 gun) ===
    formasyon_sonuc = {}
    for geri in [20, 60]:
        dip_g = {n: [] for n in ILERI_GUNLER}
        kov_g = {n: [] for n in ILERI_GUNLER}
        sembol_sonuc = {}
        for s, df in ham.items():
            oncul = df["Close"].pct_change(geri) * 100
            alt_esik = oncul.quantile(PERCENTILE / 100)
            ust_esik = oncul.quantile(1 - PERCENTILE / 100)
            dip_mask = oncul <= alt_esik
            kov_mask = oncul >= ust_esik
            s_sonuc = {"dip": {}, "kovalama": {}}
            for n in ILERI_GUNLER:
                g = ileri_getiri(df["Close"], n)
                g_dip = g[dip_mask].dropna().tolist()
                g_kov = g[kov_mask].dropna().tolist()
                s_sonuc["dip"][f"t{n}"] = islem_ozet(g_dip)
                s_sonuc["kovalama"][f"t{n}"] = islem_ozet(g_kov)
                dip_g[n].extend(g_dip)
                kov_g[n].extend(g_kov)
            sembol_sonuc[s] = s_sonuc
        formasyon_sonuc[f"{geri}gun"] = {
            "genel": {"dip": {f"t{n}": islem_ozet(dip_g[n]) for n in ILERI_GUNLER},
                      "kovalama": {f"t{n}": islem_ozet(kov_g[n]) for n in ILERI_GUNLER}},
            "dip_lehine_sembol_orani_T10": sembol_tutarlilik(sembol_sonuc, "dip", "kovalama"),
        }
        print(f"[A] {geri} gun oncul: DIP T10={formasyon_sonuc[f'{geri}gun']['genel']['dip']['t10']} "
              f"KOVALAMA T10={formasyon_sonuc[f'{geri}gun']['genel']['kovalama']['t10']} "
              f"sembol_orani={formasyon_sonuc[f'{geri}gun']['dip_lehine_sembol_orani_T10']}%")
    rapor["A_formasyon_penceresi_taramasi"] = formasyon_sonuc

    # === B) HACIM-KOSULLU DUSUS (5-gunluk oncul, kapitulasyon vs sessiz dip) ===
    kap_g = {n: [] for n in ILERI_GUNLER}
    sessiz_g = {n: [] for n in ILERI_GUNLER}
    sembol_sonuc_b = {}
    for s, df in ham.items():
        oncul5 = df["Close"].pct_change(5) * 100
        dip_esigi = oncul5.quantile(PERCENTILE / 100)
        dip_mask = oncul5 <= dip_esigi
        # dip GUNUNDEKI relVol (kgs_gunluk_port.gostergeler zaten relVol uretiyor)
        relvol_dip_gunu = df["relVol"]
        kapitulasyon_mask = dip_mask & (relvol_dip_gunu >= relvol_dip_gunu[dip_mask].median())
        sessiz_mask = dip_mask & (relvol_dip_gunu < relvol_dip_gunu[dip_mask].median())
        s_sonuc = {"kapitulasyon": {}, "sessiz_dip": {}}
        for n in ILERI_GUNLER:
            g = ileri_getiri(df["Close"], n)
            g_kap = g[kapitulasyon_mask].dropna().tolist()
            g_sessiz = g[sessiz_mask].dropna().tolist()
            s_sonuc["kapitulasyon"][f"t{n}"] = islem_ozet(g_kap)
            s_sonuc["sessiz_dip"][f"t{n}"] = islem_ozet(g_sessiz)
            kap_g[n].extend(g_kap)
            sessiz_g[n].extend(g_sessiz)
        sembol_sonuc_b[s] = s_sonuc
    rapor["B_hacim_koşullu_dusus"] = {
        "genel": {"kapitulasyon": {f"t{n}": islem_ozet(kap_g[n]) for n in ILERI_GUNLER},
                  "sessiz_dip": {f"t{n}": islem_ozet(sessiz_g[n]) for n in ILERI_GUNLER}},
        "kapitulasyon_lehine_sembol_orani_T10": sembol_tutarlilik(sembol_sonuc_b, "kapitulasyon", "sessiz_dip"),
        "sembol_bazli": sembol_sonuc_b,
    }
    print(f"[B] KAPITULASYON T10={rapor['B_hacim_koşullu_dusus']['genel']['kapitulasyon']['t10']} "
          f"SESSIZ_DIP T10={rapor['B_hacim_koşullu_dusus']['genel']['sessiz_dip']['t10']}")

    # === C) REJIM-KOSULLU TEST (XU100 EMA60 ustunde/altinda, 5-gunluk oncul) ===
    rejim_sonuc = {}
    for rejim_adi, rejim_mask_fn in [("RISK_ON", lambda idx: (xu["Close"] > xu_ema60).reindex(idx).ffill().fillna(False)),
                                       ("RISK_OFF", lambda idx: (xu["Close"] <= xu_ema60).reindex(idx).ffill().fillna(False))]:
        dip_g = {n: [] for n in ILERI_GUNLER}
        kov_g = {n: [] for n in ILERI_GUNLER}
        for s, df in ham.items():
            oncul5 = df["Close"].pct_change(5) * 100
            dip_esigi = oncul5.quantile(PERCENTILE / 100)
            ust_esigi = oncul5.quantile(1 - PERCENTILE / 100)
            rejim_mask = rejim_mask_fn(df.index)
            dip_mask = (oncul5 <= dip_esigi) & rejim_mask
            kov_mask = (oncul5 >= ust_esigi) & rejim_mask
            for n in ILERI_GUNLER:
                g = ileri_getiri(df["Close"], n)
                dip_g[n].extend(g[dip_mask].dropna().tolist())
                kov_g[n].extend(g[kov_mask].dropna().tolist())
        rejim_sonuc[rejim_adi] = {
            "dip": {f"t{n}": islem_ozet(dip_g[n]) for n in ILERI_GUNLER},
            "kovalama": {f"t{n}": islem_ozet(kov_g[n]) for n in ILERI_GUNLER},
        }
        print(f"[C] {rejim_adi}: DIP T10={rejim_sonuc[rejim_adi]['dip']['t10']} "
              f"KOVALAMA T10={rejim_sonuc[rejim_adi]['kovalama']['t10']}")
    rapor["C_rejim_kosullu_test"] = rejim_sonuc

    rapor["durustluk_notu"] = (
        "GUNLUK BAR yaklasikligi. Rejim siniflandirmasi (C) BASITLESTIRILMIS "
        "bir vekil (XU100 EMA60 ustunde/altinda) - V162/IP-8'in KENDI rejim "
        "mantigini BIREBIR REPLIKE ETMIYOR. Sonuclar yon verir, kesin kanit "
        "degildir."
    )

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/dip_kovalama_varyasyon_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print("\nTamamlandi -> data/backtest/dip_kovalama_varyasyon_sonuc.json")


if __name__ == "__main__":
    main()
