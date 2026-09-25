"""
SEKTOR MOMENTUMU TESTI - IP-8'IN GERCEK TANIMIYLA (25.09.2026)
=================================================================
Ilk sektor momentumu testinin (sektor_momentum_test.py) DUZELTILMIS
tekrari. O test, bu oturumun basinda context'ten TAHMIN edilen bir
gruplama kullanmisti (Banka=6 uye/ISCTR DAHIL, Holding=KCHOL+SAHOL+
ENKAI, Elektrik Ekipmani HIC test edilmemis). Bu script, IP-8'in
KENDI Pine kodundan (f_liderSec cagrilari, satir 929-949) BIREBIR
CIKARILAN 11 sektoru kullaniyor - IP-8'in GERCEK hipotezini test
ediyor.

FARKLAR (onceki teste gore):
- Banka: ISCTR YOK (5 uye, IP-8'in kendi tanimi)
- Holding: AGHOL var, ENKAI/ALARK YOK
- Elektrik Ekipmani: YENI sektor (ASTOR, KONTR, ALFAS, CWENE, EUPWR,
  GESAN) - ilk kez test ediliyor
- Demir-Celik: KCAER, BRSAN da eklendi (4 uye, oncesinde 2 idi)
- Otomotiv, Savunma, Telekom, Ulastirma, Rafineri, EnerjiUretim, Tuketim:
  AYNI

NOT: Bazi uyeler (KONTR, ALFAS, CWENE, EUPWR, GESAN, AGHOL, KCAER,
BRSAN, TCELL) kullanicinin SEMBOLLER (30 hisse) evreninde YOK - bunlar
YALNIZCA sektor-gucu hesabinin dogrulugu icin YARDIMCI olarak cekiliyor,
SEMBOLLER disindaki hicbir sembol PUANLI/test EDILMIYOR (onceki
disiplinle AYNI).

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi.

Cikti: data/backtest/sektor_momentum_ip8_gercek_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler, ENDEKS

# IP-8'in kendi Pine kodundan BIREBIR (f_liderSec cagrilari, 929-949)
SEKTORLER_IP8 = {
    "Banka": ["AKBNK", "GARAN", "YKBNK", "HALKB", "VAKBN"],
    "Holding": ["KCHOL", "SAHOL", "AGHOL"],
    "Savunma": ["ASELS", "OTKAR"],
    "Rafineri": ["TUPRS", "PETKM"],
    "EnerjiUretim": ["ENJSA", "AKSEN"],
    "ElektrikEkipmani": ["ASTOR", "KONTR", "ALFAS", "CWENE", "EUPWR", "GESAN"],
    "DemirCelik": ["EREGL", "KRDMD", "KCAER", "BRSAN"],
    "Otomotiv": ["FROTO", "TOASO"],
    "Tuketim": ["BIMAS", "MGROS", "ULKER"],
    "Telekom": ["TCELL", "TTKOM"],
    "Ulastirma": ["THYAO", "TAVHL"],
}
FORMASYON_GUN = 20
ILERI_GUNLER = [5, 10]


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
    xu_ret20 = xu["Close"].pct_change(FORMASYON_GUN) * 100

    # SEMBOLLER + tum IP-8 sektor uyelerinin birlesimi (yardimci
    # semboller SADECE sektor-gucu hesabi icin, PUANLI degiller)
    tum_cekilecek = sorted(set(SEMBOLLER) | set(s for uyeler in SEKTORLER_IP8.values() for s in uyeler))
    ham = {}
    eksik = []
    for s in tum_cekilecek:
        d = veri_cek(f"{s}.IS", start="2018-06-01")
        if d is not None and len(d) > 300:
            ham[s] = gostergeler(d)
        else:
            eksik.append(s)

    rel_ret = {s: (df["Close"].pct_change(FORMASYON_GUN) * 100) - xu_ret20.reindex(df.index).ffill()
               for s, df in ham.items()}
    ortak_index = None
    for s in ham:
        ortak_index = ham[s].index if ortak_index is None else ortak_index.union(ham[s].index)

    sektor_guc = pd.DataFrame(index=ortak_index)
    for sek, uyeler in SEKTORLER_IP8.items():
        seriler = [rel_ret[s].reindex(ortak_index) for s in uyeler if s in rel_ret]
        if seriler:
            sektor_guc[sek] = pd.concat(seriler, axis=1).mean(axis=1)

    sektor_rank = sektor_guc.rank(axis=1, ascending=False)
    n_sektor = sektor_guc.shape[1]
    ust_esik, alt_esik = n_sektor / 3, n_sektor - n_sektor / 3

    guclu_g = {n: [] for n in ILERI_GUNLER}
    zayif_g = {n: [] for n in ILERI_GUNLER}
    sembol_sonuc = {}

    for sek, uyeler in SEKTORLER_IP8.items():
        if sek not in sektor_rank.columns:
            continue
        guclu_mask_base = sektor_rank[sek] <= ust_esik
        zayif_mask_base = sektor_rank[sek] > alt_esik
        for s in uyeler:
            if s not in ham or s not in SEMBOLLER:
                continue  # yalniz SEMBOLLER (kullanicinin takip evreni) PUANLANIR
            df = ham[s]
            guclu_mask = guclu_mask_base.reindex(df.index).fillna(False)
            zayif_mask = zayif_mask_base.reindex(df.index).fillna(False)
            s_sonuc = {"guclu_sektor": {}, "zayif_sektor": {}, "sektor": sek}
            for n in ILERI_GUNLER:
                g = ileri_getiri(df["Close"], n)
                g_guclu = g[guclu_mask].dropna().tolist()
                g_zayif = g[zayif_mask].dropna().tolist()
                s_sonuc["guclu_sektor"][f"t{n}"] = islem_ozet(g_guclu)
                s_sonuc["zayif_sektor"][f"t{n}"] = islem_ozet(g_zayif)
                guclu_g[n].extend(g_guclu)
                zayif_g[n].extend(g_zayif)
            sembol_sonuc[s] = s_sonuc

    genel_guclu = {f"t{n}": islem_ozet(guclu_g[n]) for n in ILERI_GUNLER}
    genel_zayif = {f"t{n}": islem_ozet(zayif_g[n]) for n in ILERI_GUNLER}

    tutarlilik = []
    for v in sembol_sonuc.values():
        a = v["guclu_sektor"]["t10"]["isabet_pct"]
        b = v["zayif_sektor"]["t10"]["isabet_pct"]
        if a is not None and b is not None:
            tutarlilik.append(1 if a > b else 0)
    guclu_lehine_oran = round(100 * sum(tutarlilik) / len(tutarlilik), 1) if tutarlilik else None

    rapor = {
        "calisma": "Sektor Momentumu Testi - IP-8'in Gercek (Kod-Ici) Tanimiyla",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi. Sektor gruplari IP-8'in Pine "
            "kodundan (f_liderSec cagrilari) BIREBIR cikarildi - tahmin "
            "DEGIL. Yardimci semboller (KONTR/ALFAS/CWENE/EUPWR/GESAN/ "
            "AGHOL/KCAER/BRSAN/TCELL) SEMBOLLER disinda, yalniz sektor-"
            "gucu hesabi icin cekildi, PUANLANMADI."
        ),
        "cekilemeyen_semboller": eksik,
        "sektorler_ip8_gercek": SEKTORLER_IP8,
        "genel": {"guclu_sektor": genel_guclu, "zayif_sektor": genel_zayif},
        "guclu_sektor_lehine_sembol_orani_T10": guclu_lehine_oran,
        "sembol_bazli": sembol_sonuc,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/sektor_momentum_ip8_gercek_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"GUCLU SEKTOR T5={genel_guclu['t5']} T10={genel_guclu['t10']}")
    print(f"ZAYIF SEKTOR  T5={genel_zayif['t5']} T10={genel_zayif['t10']}")
    print(f"Sembol bazinda guclu-sektor lehine oran (T10): %{guclu_lehine_oran}")
    print(f"Cekilemeyen semboller: {eksik}")
    print("Tamamlandi -> data/backtest/sektor_momentum_ip8_gercek_sonuc.json")


if __name__ == "__main__":
    main()
