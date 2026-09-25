"""
SEKTOR MOMENTUMU TESTI (25.09.2026)
=====================================
IP-8 Sektor Rotasyon Motoru'nun temel onermesi: "guclu sektordeki
hisseleri al". Bu onerme sistem kurulalidan beri HIC DOGRUDAN test
edilmedi. Moskowitz&Grinblatt (1999): sektor-duzeyi momentum, tekil
hisse momentumundan daha guclu.

Yontem: Her gun, her sektorun 20-gunluk goreli getirisi (XU100'e gore)
hesaplanir - bu "sektor gucu". Sektorler bu guce gore siralanir. Bugun
EN GUCLU sektorlerdeki (ust 1/3) hisselerle EN ZAYIF sektorlerdeki (alt
1/3) hisselerin ileri getirisi karsilastirilir.

DURUSTLUK NOTU: Sektor uyeligi, bu oturumdaki onceki testlerden (iki-
uyeli sektor testi) VE genel bilgiden derlendi - IP-8'in kendi TAM 11-
sektor/33-hisse statik listesini BIREBIR REPLIKE ETMIYOR (Elektrik
Ekipmani ve Demir-Celik sektorlerinin TAM uyeligi bu oturumda net
degildi, DISLANDI). 9 sektor / 21 hisse ile calisiyor - GUNLUK BAR
yaklasikligi.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.

Cikti: data/backtest/sektor_momentum_sonuc.json
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

    ham = {}
    for sek, uyeler in SEKTORLER.items():
        for s in uyeler:
            if s not in ham:
                d = veri_cek(f"{s}.IS", start="2018-06-01")
                if d is not None and len(d) > 300:
                    ham[s] = gostergeler(d)

    # her sembolun kendi 20g getirisi (XU100'e gore goreli)
    rel_ret = {}
    for s, df in ham.items():
        stk_ret20 = df["Close"].pct_change(FORMASYON_GUN) * 100
        rel_ret[s] = stk_ret20 - xu_ret20.reindex(df.index).ffill()

    # sektor gucu: uye hisselerin goreli getirisinin GUNLUK ortalamasi
    ortak_index = None
    for s in ham:
        ortak_index = ham[s].index if ortak_index is None else ortak_index.union(ham[s].index)

    sektor_guc = pd.DataFrame(index=ortak_index)
    for sek, uyeler in SEKTORLER.items():
        uye_serileri = [rel_ret[s].reindex(ortak_index) for s in uyeler if s in rel_ret]
        sektor_guc[sek] = pd.concat(uye_serileri, axis=1).mean(axis=1)

    # her gun icin sektorlerin siralamasi (rank 1 = en guclu)
    sektor_rank = sektor_guc.rank(axis=1, ascending=False)
    n_sektor = len(SEKTORLER)
    ust_esik = n_sektor / 3
    alt_esik = n_sektor - n_sektor / 3

    guclu_g = {n: [] for n in ILERI_GUNLER}
    zayif_g = {n: [] for n in ILERI_GUNLER}
    sembol_sonuc = {}

    for sek, uyeler in SEKTORLER.items():
        sek_guclu_mask_base = sektor_rank[sek] <= ust_esik
        sek_zayif_mask_base = sektor_rank[sek] > alt_esik
        for s in uyeler:
            if s not in ham:
                continue
            df = ham[s]
            guclu_mask = sek_guclu_mask_base.reindex(df.index).fillna(False)
            zayif_mask = sek_zayif_mask_base.reindex(df.index).fillna(False)
            s_sonuc = {"guclu_sektor": {}, "zayif_sektor": {}}
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
        "calisma": "Sektor Momentumu Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi. Sektor uyeligi 9 sektor/21 hisse ile "
            "KISITLI - Elektrik Ekipmani ve Demir-Celik sektorleri TAM "
            "uyelik netligi olmadigi icin DISLANDI, IP-8'in TAM 11-sektor "
            "listesini birebir replike ETMIYOR."
        ),
        "sektorler_kullanilan": SEKTORLER,
        "genel": {"guclu_sektor": genel_guclu, "zayif_sektor": genel_zayif},
        "guclu_sektor_lehine_sembol_orani_T10": guclu_lehine_oran,
        "sembol_bazli": sembol_sonuc,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/sektor_momentum_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"GUCLU SEKTOR T5={genel_guclu['t5']} T10={genel_guclu['t10']}")
    print(f"ZAYIF SEKTOR  T5={genel_zayif['t5']} T10={genel_zayif['t10']}")
    print(f"Sembol bazinda guclu-sektor lehine oran (T10): %{guclu_lehine_oran}")
    print("Tamamlandi -> data/backtest/sektor_momentum_sonuc.json")


if __name__ == "__main__":
    main()
