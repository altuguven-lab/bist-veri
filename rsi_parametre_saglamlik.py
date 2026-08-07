"""
RSI PARAMETRE-SAGLAMLIK KONTROLU (07.08.2026) - Faz V0
RSI(14,30,70) stratejisi ISTATISTIKSEL OLARAK ANLAMLI cikti (t=7.69,
p~0) - ama TEK bir parametre kombinasyonuydu, asiri-optimize riski
var. Bu script AYNI stratejiyi bir PARAMETRE IZGARASINDA (periyot
10/14/21 x esikler 25-75/30-70/35-65 = 9 kombinasyon) tekrar calistirir.
Eger COGU kombinasyon POZITIF ve makul isabet oraniyla cikarsa, bulgu
tek bir sansli parametre secimine bagli DEGIL - saglam. Eger yalniz
14/30/70 pozitif, digerleri kotu cikarsa, asiri-optimize edilmis
olabilir.

SALT OLCUM - momentum-grup ayrimi bu turda YOK (karmasikligi azaltmak
icin), yalniz GENEL (grup-ayrimsiz) sonuclar karsilastiriliyor.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, os, sys
import pandas as pd
import numpy as np
import yfinance as yf

from konfig_yukle import sembol_evreni_yukle

_ciplak_semboller, _sonek, _ = sembol_evreni_yukle()
SEMBOLLER = [f"{s}{_sonek}" for s in _ciplak_semboller]
MOMENTUM_PENCERE_GUN = 126
MALIYET_YUZDE = 0.25
CIKTI = "data/backtest/rsi_parametre_saglamlik_sonuc.json"
RSI_PERIYOT = 14
RSI_ALT_ESIK = 30
RSI_UST_ESIK = 70
MAKS_TUTMA_GUN = 90


def rsi_hesapla(df, periyot):
    delta = df["Close"].diff()
    kazanc = delta.where(delta > 0, 0.0)
    kayip = -delta.where(delta < 0, 0.0)
    ort_kazanc = kazanc.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()
    ort_kayip = kayip.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()
    rs = ort_kazanc / ort_kayip.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(~(ort_kayip == 0), 100.0)  # kayip tam sifirsa RSI=100
    return rsi


def _ozet_hesapla(islem_listesi):
    gecerli = [t for t in islem_listesi if not (
        t["net_getiri_pct"] is None or
        (isinstance(t["net_getiri_pct"], float) and t["net_getiri_pct"] != t["net_getiri_pct"]))]
    if not gecerli:
        return None
    kazanan = [t for t in gecerli if t["net_getiri_pct"] > 0]
    return {"islem_sayisi": len(gecerli),
            "gecersiz_atlanan": len(islem_listesi) - len(gecerli),
            "isabet_pct": round(100 * len(kazanan) / len(gecerli), 1),
            "ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in gecerli) / len(gecerli), 3),
            "toplam_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in gecerli), 2)}


def rsi_swing_simule(df, sembol, rsi_periyot, alt_esik, ust_esik, maks_tutma_gun):
    """Parametrik versiyon - periyot/esikler/maks_tutma disaridan verilir."""
    df = df.copy().sort_index()
    rsi = rsi_hesapla(df, rsi_periyot)
    tum_islemler = []

    pozisyon = None  # (giris_fiyat, giris_tarih)
    onceki_rsi_alti = None
    for i in range(len(df)):
        bar = df.iloc[i]
        if pd.isna(bar["Close"]) or pd.isna(rsi.iloc[i]):
            continue
        tarih = bar.name.date() if hasattr(bar.name, "date") else bar.name
        kapanis = float(bar["Close"])
        rsi_deger = rsi.iloc[i]
        rsi_alti = rsi_deger < alt_esik
        # 07.08 DUZELTME: 'is True' KULLANMA - numpy.bool_ ile Python
        # bool'unun 'is' karsilastirmasi HER ZAMAN False doner.
        yukari_kesisim = bool(onceki_rsi_alti) and (not rsi_alti)
        onceki_rsi_alti = rsi_alti

        if pozisyon is None:
            if yukari_kesisim:
                pozisyon = (kapanis, tarih)
        else:
            giris, giris_tarih = pozisyon
            gun_sayisi = (tarih - giris_tarih).days
            cikis, sebep = None, None
            if rsi_alti:
                cikis, sebep = kapanis, "BASARISIZ_SICRAMA"
            elif rsi_deger >= ust_esik:
                cikis, sebep = kapanis, "KAR_AL_ASIRI_ALIM"
            elif gun_sayisi >= maks_tutma_gun:
                cikis, sebep = kapanis, "MAKS_TUTMA_ASILDI"
            elif i == len(df) - 1:
                cikis, sebep = kapanis, "VERI_SONU"
            if cikis is not None:
                ham = (cikis / giris - 1) * 100
                net = ham - MALIYET_YUZDE
                tum_islemler.append({"sembol": sembol, "net_getiri_pct": round(net, 3)})
                pozisyon = None
    return tum_islemler


PARAMETRE_IZGARASI = [
    {"periyot": p, "alt": a, "ust": u, "maks_tutma": MAKS_TUTMA_GUN}
    for p in (10, 14, 21)
    for a, u in ((25, 75), (30, 70), (35, 65))
]


def main():
    # veri SEMBOL basina BIR KEZ cekilir, 9 parametre kombinasyonu
    # AYNI veri uzerinde calisir - 9 kat fazla yfinance cagrisi yapmaz.
    veri_seti = {}
    for sembol in SEMBOLLER:
        try:
            df = yf.Ticker(sembol).history(period="5y", interval="1d")
            if df.empty:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            veri_seti[sembol] = df
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
    print(f"{len(veri_seti)}/{len(SEMBOLLER)} sembol icin veri cekildi\n")

    izgara_sonuclari = []
    for parametre in PARAMETRE_IZGARASI:
        tum_islemler = []
        for sembol, df in veri_seti.items():
            islemler = rsi_swing_simule(df, sembol, parametre["periyot"],
                                          parametre["alt"], parametre["ust"],
                                          parametre["maks_tutma"])
            tum_islemler += islemler
        ozet = _ozet_hesapla(tum_islemler)
        etiket = f"RSI{parametre['periyot']}_{parametre['alt']}-{parametre['ust']}"
        if ozet:
            izgara_sonuclari.append({"parametre_etiketi": etiket, **parametre, **ozet})
            print(f"{etiket}: {ozet['islem_sayisi']} islem, isabet %{ozet['isabet_pct']}, "
                  f"ort net %{ozet['ort_net_getiri_pct']}")
        else:
            print(f"{etiket}: hic islem uretilmedi")

    pozitif_sayisi = sum(1 for s in izgara_sonuclari if s["ort_net_getiri_pct"] > 0)
    sonuc_json = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 - RSI parametre-saglamlik kontrolu. RSI(14,30,70)'in "
                "istatistiksel anlamli cikan sonucunun (t=7.69) TEK bir "
                "sansli kombinasyon mu, yoksa SAGLAM bir desen mi oldugunu "
                "test eder. SALT OLCUM."),
        "izgara_boyutu": len(PARAMETRE_IZGARASI),
        "pozitif_cikan_kombinasyon_sayisi": pozitif_sayisi,
        "sembol_sayisi": len(veri_seti),
        "izgara_sonuclari": izgara_sonuclari,
    }
    atomik_json_yaz(CIKTI, sonuc_json)
    print(f"\nYazildi: {CIKTI}")
    print(f"OZET: {pozitif_sayisi}/{len(izgara_sonuclari)} kombinasyon POZITIF cikti")


if __name__ == "__main__":
    main()
