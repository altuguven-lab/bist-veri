"""
B2 FAZ V0: SEKTOR-GUCLU-AMA-HISSE-GERIDE TESTI (17.09.2026)
=============================================================
KULUCKA SONRASI BIRIKIM B2: "Sektore-gore RS" (Madde 14). Test plani:
"XBANK/XUSIN referansli RS ile 2024 banka rallisi geriye-donuk kiyas".

BULUNAN KOD SORUNU (V162_1_yama.txt, f_kgsSector cagrisi ~satir 2572):
kgsSectorBase dalinda isSectorStrongEff (sektor bir butun olarak
endeksi geciyor mu) TEK BASINA +8 puan veriyor - hissenin KENDI
SEKTORU ICINDE lider mi kuyruk mu oldugu bakilmadan. Guclu bir sektor
rallisinde (2024 banka rallisi gibi) sektordeki EN ZAYIF hisse bile
bu +8'i otomatik aliyor.

TEST: BANKACILIK+GYO evreninde, her gun icin cross-sectional (o gunku
sektor uyeleri arasinda) rsSector yuzdelik sirasi hesaplanir. Iki grup
karsilastirilir (yalniz isSectorStrongEff=True olan gunlerde, yani
"kod zaten +8 puan veriyor" durumunda):
  LIDER: rsSectorRnk_crosssec >= 50 (sektorun ustteki yarisinda)
  KUYRUK: rsSectorRnk_crosssec < 50 (sektorun alttaki yarisinda)
Ikisinin de T+3/T+10 ileri getirisi/isabet orani karsilastirilir.
Once TUM DONEM (2019-), sonra 2024 banka rallisi penceresi AYRI
raporlanir (backlog'un istedigi gibi).

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi (V0/B1 ile AYNI kisitlar).
Cross-sectional siralama GUNLUK kapanis verisiyle yapiliyor, gercek
15dk ici sektor rotasyonunu YAKALAYAMAZ.

Cikti: data/backtest/b2_sektor_lider_kuyruk_sonuc.json
"""
import json
import sys
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import veri_cek, gostergeler, ENDEKS, BAS

BANKA_GYO = ["AKBNK", "YKBNK", "GARAN", "ISCTR", "HALKB", "VAKBN", "EKGYO"]
SEKTOR_TICKER = "XBANK.IS"  # EKGYO da dahil edildi (Madde 14 "Banka/GYO" diyor) -
# tek endeks yeterli olmayabilir ama XBANK bankacilik agirlikli evrenin
# cogunu temsil ediyor; EKGYO icin XGMYO da denenir, yoksa evren-ici kalir.
GYO_TICKER = "XGMYO.IS"

BANKA_RALLI_BAS, BANKA_RALLI_SON = "2024-01-01", "2024-12-31"
ILERI_GUNLER = [3, 10]


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
        print("HATA: XU100 verisi cekilemedi", file=sys.stderr)
        return
    idxRoc = gostergeler(endeks)["stkRoc"]

    xbank = veri_cek(SEKTOR_TICKER, start=BAS)
    xgmyo = veri_cek(GYO_TICKER, start=BAS)
    if xbank is None:
        print("UYARI: XBANK.IS bulunamadi, durduruluyor", file=sys.stderr)
        return

    ham = {}
    for s in BANKA_GYO:
        d = veri_cek(f"{s}.IS", start=BAS)
        if d is not None and len(d) > 250:
            ham[s] = gostergeler(d)

    # her sembol icin secRoc: bankalar XBANK, EKGYO varsa XGMYO yoksa XBANK
    secRoc_map = {}
    for s in ham:
        sec_close = xgmyo["Close"] if (s == "EKGYO" and xgmyo is not None) else xbank["Close"]
        secRoc_map[s] = sec_close.pct_change(20).reindex(ham[s].index).ffill() * 100

    isSectorStrongEff_map = {s: (secRoc_map[s] > idxRoc.reindex(ham[s].index) + 0.5).fillna(False)
                              for s in ham}
    rsSector_map = {s: ham[s]["stkRoc"] - secRoc_map[s] for s in ham}

    # cross-sectional (gunluk, sektor-ici) yuzdelik sira
    tum_rsSector = pd.DataFrame({s: rsSector_map[s] for s in ham})
    crosssec_rank = tum_rsSector.rank(axis=1, pct=True) * 100  # her SATIRDA (gun) siralanir

    def grup_ayir(tarih_bas=None, tarih_son=None):
        lider_g = {n: [] for n in ILERI_GUNLER}
        kuyruk_g = {n: [] for n in ILERI_GUNLER}
        for s in ham:
            df = ham[s]
            maske = isSectorStrongEff_map[s].copy()
            if tarih_bas:
                maske = maske & (df.index >= tarih_bas) & (df.index <= tarih_son)
            rnk = crosssec_rank[s].reindex(df.index)
            lider_mask = maske & (rnk >= 50)
            kuyruk_mask = maske & (rnk < 50)
            for n in ILERI_GUNLER:
                g = ileri_getiri(df["Close"], n)
                lider_g[n].extend(g[lider_mask].dropna().tolist())
                kuyruk_g[n].extend(g[kuyruk_mask].dropna().tolist())
        return (
            {f"t{n}": islem_ozet(lider_g[n]) for n in ILERI_GUNLER},
            {f"t{n}": islem_ozet(kuyruk_g[n]) for n in ILERI_GUNLER},
        )

    tum_donem_lider, tum_donem_kuyruk = grup_ayir()
    ralli_lider, ralli_kuyruk = grup_ayir(BANKA_RALLI_BAS, BANKA_RALLI_SON)

    rapor = {
        "calisma": "B2 Faz V0 - Sektor-Guclu-Ama-Hisse-Geride Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GUNLUK BAR yaklasikligi. Cross-sectional siralama gunluk kapanisla "
            "yapildi, 15dk ici sektor rotasyonunu yakalayamaz. TEK BASINA hicbir "
            "kod degisikligine GEREKCE OLAMAZ - B2'nin ilk kesif adimidir."
        ),
        "evren": list(ham.keys()),
        "tum_donem": {"lider_ustteki_yari": tum_donem_lider, "kuyruk_alttaki_yari": tum_donem_kuyruk},
        "banka_rallisi_2024": {"lider_ustteki_yari": ralli_lider, "kuyruk_alttaki_yari": ralli_kuyruk},
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/b2_sektor_lider_kuyruk_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print(json.dumps(rapor, ensure_ascii=False, indent=2))
    print("\nTamamlandi -> data/backtest/b2_sektor_lider_kuyruk_sonuc.json")


if __name__ == "__main__":
    main()
