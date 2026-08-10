"""
SAGKALIM_YANLILIGI_DUYARLILIK (10.08.2026) - Faz V0
SWING_PINE_SPESIFIKASYONU.md Bolum 4B Madde 1'in cevabi: TAM bir
sagkalim-yanliligindan-arindirilmis backtest MUMKUN DEGIL (yfinance,
borsadan TAMAMEN cikmis/birlesmis sirketler icin veri SUNMUYOR) - bu
DURUST bir SINIRLAMA, cozulemez. Ama YAPILABILIR, DURUST bir
DUYARLILIK ANALIZI var: evrenimizdeki hangi sembollerin GERCEKTEN
TAM 5 yillik gecmisi VAR, hangilerinin YOK (orn. sonradan halka
acilmis/IPO olmus) - VE backtest'i yalniz "TAM gecmisli" alt-kumeyle
TEKRAR calistirip, SONUCUN degisip degismedigini gormek.

MANTIK: eger "tam gecmisli" alt-kume SONUCU, TUM evren SONUCUNA
YAKINSA, sagkalim yanliligi BUYUK bir CARPITMA yapmiyor OLABILIR
(KESIN kanit degil, ama GUVEN ARTIRICI bir isaret). Eger BUYUK
FARKLILIK varsa, bu SORGULANMASI gereken bir bulgu.
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
TAM_GECMIS_ESIK_GUN = 1200


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


def rsi_swing_simule(df, sembol):
    df = df.copy().sort_index()
    rsi = rsi_hesapla(df["Close"], RSI_PERIYOT)
    tum_islemler = []
    pozisyon = None
    onceki_alti_30 = None
    for i in range(len(df)):
        if pd.isna(df["Close"].iloc[i]) or pd.isna(rsi.iloc[i]):
            continue
        tarih = df.index[i].date()
        kapanis = float(df["Close"].iloc[i])
        rsi_deger = float(rsi.iloc[i])
        simdi_alti_30 = rsi_deger < RSI_ALT_ESIK
        yukari_kesisim = bool(onceki_alti_30) and (not simdi_alti_30)
        onceki_alti_30 = simdi_alti_30
        if pozisyon is None:
            if yukari_kesisim:
                pozisyon = (kapanis, tarih)
        else:
            giris, giris_tarih = pozisyon
            gun_sayisi = (tarih - giris_tarih).days
            cikis, sebep = None, None
            if simdi_alti_30:
                cikis, sebep = kapanis, "BASARISIZ_SICRAMA"
            elif rsi_deger >= RSI_UST_ESIK:
                cikis, sebep = kapanis, "KAR_AL_ASIRI_ALIM"
            elif gun_sayisi >= MAKS_TUTMA_GUN:
                cikis, sebep = kapanis, "MAKS_TUTMA_ASILDI"
            elif i == len(df) - 1:
                cikis, sebep = kapanis, "VERI_SONU"
            if cikis is not None:
                ham = (cikis / giris - 1) * 100
                net = ham - MALIYET_YUZDE
                tum_islemler.append({"sembol": sembol, "net_getiri_pct": round(net, 3)})
                pozisyon = None
    return tum_islemler


def ozet_hesapla(islemler):
    if not islemler:
        return None
    getiriler = [t["net_getiri_pct"] for t in islemler]
    kazananlar = [g for g in getiriler if g > 0]
    return {"islem_sayisi": len(getiriler), "isabet_pct": round(100 * len(kazananlar) / len(getiriler), 1),
            "ort_net_getiri_pct": round(sum(getiriler) / len(getiriler), 3)}


def main():
    import yaml
    with open("config/universe.yml", encoding="utf-8") as f:
        evren = yaml.safe_load(f)["symbols"]

    tam_gecmisli, kisa_gecmisli = [], []
    tum_islemler_tam = []
    tum_islemler_hepsi = []
    veri_uzunluklari = {}

    for sembol in evren:
        try:
            df = yf.Ticker(f"{sembol}.IS").history(period="5y", interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
            continue
        if df.empty:
            continue
        veri_gun_sayisi = (df.index[-1].date() - df.index[0].date()).days
        veri_uzunluklari[sembol] = veri_gun_sayisi

        islemler = rsi_swing_simule(df, sembol)
        tum_islemler_hepsi += islemler

        if veri_gun_sayisi >= TAM_GECMIS_ESIK_GUN:
            tam_gecmisli.append(sembol)
            tum_islemler_tam += islemler
        else:
            kisa_gecmisli.append(sembol)

    ozet_tum_evren = ozet_hesapla(tum_islemler_hepsi)
    ozet_tam_gecmisli = ozet_hesapla(tum_islemler_tam)

    rapor = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("SWING_PINE_SPESIFIKASYONU.md Bolum 4B Madde 1 cevabi - TAM "
                "sagkalim-yanliligindan-arindirilmis backtest MUMKUN DEGIL "
                "(yfinance borsadan TAMAMEN cikmis sirketler icin veri "
                "SUNMUYOR - bu COZULEMEZ bir sinirlama). Bu, YAPILABILIR bir "
                "DUYARLILIK analizi: 'tam gecmisli' (>=1200 gun) alt-kume "
                "sonucu, TUM evren sonucuna YAKINSA, sagkalim yanliligi "
                "BUYUK bir carpitma yapmiyor OLABILIR (kesin kanit degil, "
                "guven artirici bir isaret)."),
        "tam_gecmis_esik_gun": TAM_GECMIS_ESIK_GUN,
        "tam_gecmisli_semboller": tam_gecmisli,
        "kisa_gecmisli_semboller": kisa_gecmisli,
        "veri_uzunluklari_gun": veri_uzunluklari,
        "ozet_tum_evren": ozet_tum_evren,
        "ozet_tam_gecmisli_alt_kume": ozet_tam_gecmisli,
    }
    atomik_json_yaz("data/backtest/sagkalim_yanliligi_duyarlilik_sonuc.json", rapor)
    print(f"Yazildi: data/backtest/sagkalim_yanliligi_duyarlilik_sonuc.json")
    print(f"Tam gecmisli: {len(tam_gecmisli)}/{len(evren)} sembol")
    print(f"Kisa gecmisli (dikkat): {kisa_gecmisli}")
    if ozet_tum_evren:
        print(f"TUM EVREN: {ozet_tum_evren}")
    if ozet_tam_gecmisli:
        print(f"TAM GECMISLI ALT-KUME: {ozet_tam_gecmisli}")


if __name__ == "__main__":
    main()
