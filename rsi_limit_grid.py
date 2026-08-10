"""
RSI KISIT-UYGULANMIS BACKTEST (10.08.2026) - Faz V0
SWING_PINE_SPESIFIKASYONU.md Bolum 4B Madde 2'nin cevabi: mevcut 276
islemlik rsi_asiri_satim_swing.py backtest'i HER sinyalin ALINDIGINI
varsayiyordu - bu script, v1'in GERCEK kisitlarini (maks 5 esizamanli
pozisyon, sektor basina maks 2) PORTFOY-SEVIYESINDE, KRONOLOJIK olarak
UYGULAYARAK ayni 30 sembol/5 yil verisini yeniden kosturur.

METODOLOJI: TUM sembollerin GUNLUK barlari, TARIH SIRASINA gore
BIRLIKTE islenir (sembol-sembol BAGIMSIZ degil). Her gun:
  1. ONCE tum ACIK pozisyonlarda CIKIS kontrolu (stop/RSI/maks-tutma) -
     bu HICBIR ZAMAN kisitlanmaz.
  2. SONRA o gun YENI kesisim yapan semboller (aday) toplanir.
  3. Adaylar, SEMBOL ADI ALFABETIK SIRAYLA (basit, degerlendirilmemis
     bir kriterle SIRALAMA yapmamak icin BILINCLI tercih - "hangi
     sinyal daha kaliteli" diye bir puanlama henuz KANITLANMADI)
     islenir - kapasite/sektor limiti UYGUNSA ACILIR, DEGILSE REDDEDILIR.

KIRMIZI CIZGI: SALT OLCUM, Pine'a hic dokunmuyor.

10.08 EKI: SWING_PINE_SPESIFIKASYONU.md Bolum 4C'de bulunan surpriz
uzerine - "maks 5 esizamanli" kisitinin edge'in %34'unu SILDIGI
tespit edildi (kisitsiz 276/52.2%/+6.746 vs kisitli-5 134/43.3%/
+4.471). Bu script, esizamanli limit DEGERINI (3/5/7/10/15) GRID
olarak test eder - hangi deger, EN KOTU senaryoyu makul tutarken
edge kaybini EN AZA indiriyor. Sektor limiti (2) SABIT tutulur -
onceki testte HIC sektor-limit reddi CIKMAMISTI, darbogaz DEGIL.
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
MAKS_ESZAMANLI_POZISYON = 5
SEKTOR_BASINA_MAKS = 2

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


LIMIT_GRID = [3, 5, 7, 10, 15]


def simulasyon_calistir(gunluk, tum_tarihler, maks_eszamanli, sektor_basina_maks):
    acik_pozisyonlar = {}
    kapanan_islemler = []
    reddedilen_sinyaller = []

    for tarih in tum_tarihler:
        gunun_verisi = gunluk[tarih]

        for sembol in list(acik_pozisyonlar.keys()):
            if sembol not in gunun_verisi:
                continue
            veri = gunun_verisi[sembol]
            giris = acik_pozisyonlar[sembol]
            gun_sayisi = (tarih - giris["giris_tarih"]).days
            stop_seviyesi = giris["giris_fiyat"] * (1 - STOP_LOSS_YUZDE / 100)
            cikis, sebep = None, None
            if veri["low"] <= stop_seviyesi:
                cikis, sebep = stop_seviyesi, "SABIT_STOP_LOSS"
            elif veri["rsi_alti_30"]:
                cikis, sebep = veri["close"], "BASARISIZ_SICRAMA"
            elif veri["rsi"] >= RSI_UST_ESIK:
                cikis, sebep = veri["close"], "KAR_AL_ASIRI_ALIM"
            elif gun_sayisi >= MAKS_TUTMA_GUN:
                cikis, sebep = veri["close"], "MAKS_TUTMA_ASILDI"
            if cikis is not None:
                ham = (cikis / giris["giris_fiyat"] - 1) * 100
                net = round(ham - MALIYET_YUZDE, 3)
                kapanan_islemler.append({"sembol": sembol, "giris_tarih": str(giris["giris_tarih"]),
                                          "cikis_tarih": str(tarih), "sebep": sebep, "net_getiri_pct": net})
                del acik_pozisyonlar[sembol]

        adaylar = sorted(s for s, v in gunun_verisi.items()
                          if v["yukari_kesisim"] and s not in acik_pozisyonlar)
        for sembol in adaylar:
            sektor = sektor_bul(sembol)
            acik_sayisi = len(acik_pozisyonlar)
            sektor_sayisi = sum(1 for s in acik_pozisyonlar if sektor_bul(s) == sektor)
            if acik_sayisi >= maks_eszamanli:
                reddedilen_sinyaller.append({"sembol": sembol, "tarih": str(tarih), "sebep": "ESZAMANLI_LIMIT"})
                continue
            if sektor_sayisi >= sektor_basina_maks:
                reddedilen_sinyaller.append({"sembol": sembol, "tarih": str(tarih), "sebep": "SEKTOR_LIMIT"})
                continue
            acik_pozisyonlar[sembol] = {"giris_fiyat": gunun_verisi[sembol]["close"], "giris_tarih": tarih}

    if kapanan_islemler:
        getiriler = [t["net_getiri_pct"] for t in kapanan_islemler]
        kazananlar = [g for g in getiriler if g > 0]
        ozet = {"islem_sayisi": len(getiriler), "isabet_pct": round(100 * len(kazananlar) / len(getiriler), 1),
                "ort_net_getiri_pct": round(sum(getiriler) / len(getiriler), 3)}
    else:
        ozet = None
    return ozet, len(reddedilen_sinyaller)


def main():
    import yaml
    with open("config/universe.yml", encoding="utf-8") as f:
        evren = yaml.safe_load(f)["symbols"]

    print(f"{len(evren)} sembol icin veri hazirlaniyor (BIR KEZ cekilir, TUM grid icin kullanilir)...")
    gunluk = gunluk_veri_hazirla(evren)
    tum_tarihler = sorted(gunluk.keys())
    print(f"{len(tum_tarihler)} islem gunu islenecek\n")

    izgara_sonuclari = []
    for limit in LIMIT_GRID:
        ozet, reddedilen_sayisi = simulasyon_calistir(gunluk, tum_tarihler, limit, SEKTOR_BASINA_MAKS)
        if ozet:
            izgara_sonuclari.append({"maks_eszamanli": limit, **ozet, "reddedilen_sinyal_sayisi": reddedilen_sayisi})
            print(f"LIMIT={limit}: {ozet['islem_sayisi']} islem, isabet %{ozet['isabet_pct']}, "
                  f"ort net %{ozet['ort_net_getiri_pct']}, reddedilen={reddedilen_sayisi}")
        else:
            print(f"LIMIT={limit}: hic islem uretilmedi")

    rapor = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("SWING_PINE_SPESIFIKASYONU.md Bolum 4C takibi - esizamanli "
                "pozisyon LIMIT DEGERININ (3/5/7/10/15) edge uzerindeki "
                "etkisini test eder. Sektor limiti (2) SABIT - onceki "
                "testte darbogaz DEGILDI. KISITSIZ referans: 276 islem/"
                "isabet %52.2/ort net +%6.746 (rsi_asiri_satim_swing.py)."),
        "sektor_basina_maks_sabit": SEKTOR_BASINA_MAKS,
        "kisitsiz_referans": {"islem_sayisi": 276, "isabet_pct": 52.2, "ort_net_getiri_pct": 6.746},
        "sembol_sayisi": len(evren),
        "izgara_sonuclari": izgara_sonuclari,
    }
    atomik_json_yaz("data/backtest/rsi_limit_grid_sonuc.json", rapor)
    print(f"\nYazildi: data/backtest/rsi_limit_grid_sonuc.json")


if __name__ == "__main__":
    main()
