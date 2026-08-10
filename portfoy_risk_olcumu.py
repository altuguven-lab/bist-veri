"""
PORTFOY_SEVIYESI_RISK_OLCUMU (10.08.2026) - Faz V0
SWING_PINE_SPESIFIKASYONU.md Bolum 4C'de acik birakilan risk-tarafi:
rsi_limit_grid.py yalniz EDGE'i (isabet/ort getiri) olctu, limit=8'in
limit=5'e gore PORTFOY-SEVIYESINDE (esizamanli toplam maruziyet,
GERCEK equity curve, maksimum drawdown) NE KADAR RISKLI oldugunu
HENUZ olcmedi. Bu script bu boslugu kapatir.

METODOLOJI: HER LIMIT DEGERI icin (5 vs 8), gunluk PORTFOY DEGERINI
(kova basi %100'den baslayarak, her acik pozisyonun GUNLUK MARK-TO-
MARKET degeriyle) hesaplar, GERCEK equity curve'u insa eder, PEAK-TO-
TROUGH maksimum drawdown'i olcer. Bu, TEK ISLEM stop'undan (-%12)
FARKLI bir olcum - COKLU pozisyon AYNI ANDA zararda oldugunda
PORTFOYUN NE KADAR duştugunu gosterir.

KIRMIZI CIZGI: SALT OLCUM, Pine'a hic dokunmuyor.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import yfinance as yf
import pandas as pd
import numpy as np

RSI_PERIYOT = 14
RSI_ALT_ESIK = 30
RSI_UST_ESIK = 70
MAKS_TUTMA_GUN = 90
MALIYET_YUZDE = 0.25
STOP_LOSS_YUZDE = 12
SEKTOR_BASINA_MAKS = 2
POZISYON_BUYUKLUGU_PCT = 12.0

SEKTOR_HARITASI = {
    "AKBNK": "Bankacilik", "YKBNK": "Bankacilik", "GARAN": "Bankacilik",
    "ISCTR": "Bankacilik", "HALKB": "Bankacilik", "VAKBN": "Bankacilik",
    "KCHOL": "Holding", "SAHOL": "Holding", "ALARK": "Holding",
    "THYAO": "Havacilik", "PGSUS": "Havacilik", "TAVHL": "Havacilik-Altyapi",
    "EREGL": "Demir-Celik", "SISE": "Sanayi-Cam",
    "ASELS": "Savunma", "ASTOR": "Enerji-Ekipman", "ENJSA": "Enerji-Elektrik",
    "MGROS": "Perakende", "BIMAS": "Perakende",
    "TUPRS": "Petrokimya", "PETKM": "Petrokimya",
    "TOASO": "Otomotiv", "FROTO": "Otomotiv", "OTKAR": "Otomotiv",
    "ENKAI": "Insaat", "TTKOM": "Telekom",
    "AEFES": "Gida-Icecek", "ULKER": "Gida-Icecek",
    "EKGYO": "GYO", "TRMET": "Madencilik",
}


def rsi_hesapla(kapanislar, periyot):
    delta = kapanislar.diff()
    kazanc = delta.where(delta > 0, 0.0)
    kayip = -delta.where(delta < 0, 0.0)
    ort_kazanc = kazanc.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()
    ort_kayip = kayip.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()
    rs = ort_kazanc / ort_kayip.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(~(ort_kayip == 0), 100.0)
    return rsi


def sektor_bul(sembol):
    return SEKTOR_HARITASI.get(sembol, "DIGER")


def gunluk_veri_hazirla(semboller):
    gunluk = {}
    for sembol in semboller:
        try:
            df = yf.Ticker(f"{sembol}.IS").history(period="5y", interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
            continue
        if df.empty:
            continue
        df = df.sort_index()
        rsi = rsi_hesapla(df["Close"], RSI_PERIYOT)
        onceki_alti_30 = None
        for i in range(len(df)):
            if pd.isna(df["Close"].iloc[i]) or pd.isna(rsi.iloc[i]):
                continue
            tarih = df.index[i].date()
            rsi_deger = float(rsi.iloc[i])
            simdi_alti_30 = rsi_deger < RSI_ALT_ESIK
            yukari_kesisim = bool(onceki_alti_30) and (not simdi_alti_30)
            onceki_alti_30 = simdi_alti_30
            gunluk.setdefault(tarih, {})[sembol] = {
                "close": float(df["Close"].iloc[i]),
                "low": float(df["Low"].iloc[i]) if "Low" in df.columns and not pd.isna(df["Low"].iloc[i]) else float(df["Close"].iloc[i]),
                "rsi": rsi_deger, "rsi_alti_30": simdi_alti_30, "yukari_kesisim": yukari_kesisim,
            }
    return gunluk


def simulasyon_calistir(gunluk, tum_tarihler, maks_eszamanli):
    acik_pozisyonlar = {}
    nakit_pct = 100.0
    equity_curve = []
    maks_eszamanli_gozlenen = 0

    for tarih in tum_tarihler:
        gunun_verisi = gunluk[tarih]

        for sembol in list(acik_pozisyonlar.keys()):
            if sembol not in gunun_verisi:
                continue
            veri = gunun_verisi[sembol]
            giris = acik_pozisyonlar[sembol]
            gun_sayisi = (tarih - giris["giris_tarih"]).days
            stop_seviyesi = giris["giris_fiyat"] * (1 - STOP_LOSS_YUZDE / 100)
            cikis = None
            if veri["low"] <= stop_seviyesi:
                cikis = stop_seviyesi
            elif veri["rsi_alti_30"]:
                cikis = veri["close"]
            elif veri["rsi"] >= RSI_UST_ESIK:
                cikis = veri["close"]
            elif gun_sayisi >= MAKS_TUTMA_GUN:
                cikis = veri["close"]
            if cikis is not None:
                getiri_pct = (cikis / giris["giris_fiyat"] - 1) * 100 - MALIYET_YUZDE
                nakit_pct += POZISYON_BUYUKLUGU_PCT * (1 + getiri_pct / 100)
                del acik_pozisyonlar[sembol]

        adaylar = sorted(s for s, v in gunun_verisi.items()
                          if v["yukari_kesisim"] and s not in acik_pozisyonlar)
        for sembol in adaylar:
            sektor = sektor_bul(sembol)
            acik_sayisi = len(acik_pozisyonlar)
            sektor_sayisi = sum(1 for s in acik_pozisyonlar if sektor_bul(s) == sektor)
            if acik_sayisi >= maks_eszamanli or sektor_sayisi >= SEKTOR_BASINA_MAKS:
                continue
            if nakit_pct < POZISYON_BUYUKLUGU_PCT:
                continue
            acik_pozisyonlar[sembol] = {"giris_fiyat": gunun_verisi[sembol]["close"], "giris_tarih": tarih}
            nakit_pct -= POZISYON_BUYUKLUGU_PCT

        maks_eszamanli_gozlenen = max(maks_eszamanli_gozlenen, len(acik_pozisyonlar))

        acik_deger_pct = 0.0
        for sembol, giris in acik_pozisyonlar.items():
            if sembol in gunun_verisi:
                guncel_getiri = (gunun_verisi[sembol]["close"] / giris["giris_fiyat"] - 1) * 100
                acik_deger_pct += POZISYON_BUYUKLUGU_PCT * (1 + guncel_getiri / 100)
            else:
                acik_deger_pct += POZISYON_BUYUKLUGU_PCT
        toplam_deger_pct = nakit_pct + acik_deger_pct
        equity_curve.append((tarih, toplam_deger_pct))

    maks_dd_pct = 0.0
    zirve = equity_curve[0][1] if equity_curve else 100.0
    for _, deger in equity_curve:
        zirve = max(zirve, deger)
        dd = (deger / zirve - 1) * 100
        maks_dd_pct = min(maks_dd_pct, dd)

    son_deger = equity_curve[-1][1] if equity_curve else 100.0
    toplam_getiri_pct = son_deger - 100.0

    return {
        "maks_eszamanli_limit": maks_eszamanli,
        "maks_eszamanli_gozlenen": maks_eszamanli_gozlenen,
        "maks_portfoy_drawdown_pct": round(maks_dd_pct, 2),
        "toplam_donem_getirisi_pct": round(toplam_getiri_pct, 2),
        "son_equity_pct": round(son_deger, 2),
    }


def main():
    import yaml
    with open("config/universe.yml", encoding="utf-8") as f:
        evren = yaml.safe_load(f)["symbols"]

    print(f"{len(evren)} sembol icin veri hazirlaniyor...")
    gunluk = gunluk_veri_hazirla(evren)
    tum_tarihler = sorted(gunluk.keys())
    print(f"{len(tum_tarihler)} islem gunu islenecek\n")

    sonuclar = []
    for limit in [5, 8]:
        sonuc = simulasyon_calistir(gunluk, tum_tarihler, limit)
        sonuclar.append(sonuc)
        print(f"LIMIT={limit}: gozlenen maks eszamanli={sonuc['maks_eszamanli_gozlenen']}, "
              f"PORTFOY maks drawdown=%{sonuc['maks_portfoy_drawdown_pct']}, "
              f"5-yillik toplam getiri=%{sonuc['toplam_donem_getirisi_pct']}")

    rapor = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("SWING_PINE_SPESIFIKASYONU.md Bolum 4C'de acik birakilan RISK "
                "tarafi - limit=5 vs limit=8'in PORTFOY-SEVIYESINDE (esizamanli "
                "TOPLAM maruziyet, GERCEK equity curve, maksimum drawdown) "
                "karsilastirmasi. Tek-islem stop'undan (-%12) FARKLI bir olcum - "
                "COKLU pozisyon AYNI ANDA zararda oldugunda PORTFOYUN ne kadar "
                "dustugunu gosterir."),
        "pozisyon_buyuklugu_pct": POZISYON_BUYUKLUGU_PCT,
        "sonuclar": sonuclar,
    }
    atomik_json_yaz("data/backtest/portfoy_risk_olcumu_sonuc.json", rapor)
    print(f"\nYazildi: data/backtest/portfoy_risk_olcumu_sonuc.json")


if __name__ == "__main__":
    main()
