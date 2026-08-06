"""
SUPERTREND + ADX SWING KESIF-BACKTEST (06.08.2026) - Faz V0
Arastirma raporunun onerisiyle uyumlu: gun-ici (15dk) yerine COK-GUNLU
(5-60/90 gun) ufka gecis. Ayni Supertrend+ADX matematigi (bugun sabah
test edilip dogrulandi), ama artik GUNLUK barlarla, YILLARCA geriye
giden gercek veriyle (yfinance intraday 60-gun sinirindan BAGIMSIZ).

KIRMIZI CIZGI: SALT OLCUM, Pine'a hic dokunmuyor. GRUP karsilastirmasi
(GUCLU/ZAYIF anlati) aynen koruyor - asil test edilen hipotez bu.

Yontem:
  - Supertrend+ADX AYNI parametrelerle (carpim=3, ATR=10, ADX=14,
    esik=25) - gunluk grafiklerde de standart varsayilanlar.
  - Giris: flip + ADX esigi (aynen intraday versiyonuyla ayni mantik).
  - Cikis: ST_FLIP (dogal) VEYA MAKS_TUTMA_GUN (90 gun - PEAD/analist-
    revizyon etkisinin surdugu klasik pencereyle uyumlu, arastirma
    raporundan) asilirsa zorla kapat. "Gun sonu" kisiti YOK artik -
    pozisyonlar haftalarca/aylarca acik kalabilir.
  - Maliyet: %0.25 gidis-donus (ayni varsayim, ama artik COK DAHA AZ
    islem oldugu icin toplam maliyet-orani cok daha dusuk olacak).
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, os, sys
import pandas as pd
import numpy as np
import yfinance as yf

# 06.08 EKI: Kurul karari - bugunku tema-hizalanmasi bulgusunu (ASTOR/
# KCHOL guclu anlati, AKBNK/YKBNK zayiflayan anlati - arastirma_hedef_
# fiyat.json'da kayitli) AYNI teknik motorla (Supertrend+ADX, ayni
# matematik) TEST ediyoruz: anlati gucu, teknik sinyal kalitesini
# GERCEKTEN etkiliyor mu?
GRUP_SEMBOLLER = {
    "GUCLU_ANLATI": ["ASTOR.IS", "KCHOL.IS"],   # 06.08: 4 kurumdan yukari/kar surprizi
    "ZAYIF_ANLATI": ["AKBNK.IS", "YKBNK.IS"],   # 06.08: 4+3 kurumdan tutarli asagi revizyon
}
SEMBOLLER = [s for grup in GRUP_SEMBOLLER.values() for s in grup]
SEMBOL_GRUP = {s: g for g, semboller in GRUP_SEMBOLLER.items() for s in semboller}
MALIYET_YUZDE = 0.25
CIKTI = "data/backtest/supertrend_adx_swing_sonuc.json"
ATR_PERIYOT = 10
ST_CARPAN = 3.0
ADX_PERIYOT = 14
ADX_ESIK = 25
MAKS_TUTMA_GUN = 90  # PEAD/analist-revizyon etki suresiyle uyumlu ust sinir


def atr_hesapla(df, periyot):
    yuksek, dusuk, kapanis = df["High"], df["Low"], df["Close"]
    onceki_kapanis = kapanis.shift(1)
    tr = pd.concat([
        yuksek - dusuk,
        (yuksek - onceki_kapanis).abs(),
        (dusuk - onceki_kapanis).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()


def supertrend_hesapla(df, atr, carpan):
    """Standart, dogrulanmis Supertrend formulasyonu (pandas-ta ve
    yaygin acik-kaynak implementasyonlarindaki desenle ayni):
    - final bandlar HER ZAMAN sikilastirma yonunde guncellenir (min/max)
    - trend, SU ANKI barin final bandiyla kiyaslanir (onceki degil)."""
    orta = (df["High"] + df["Low"]) / 2
    ust = (orta + carpan * atr).values
    alt = (orta - carpan * atr).values
    kapanis = df["Close"].values
    n = len(df)

    son_ust = ust.copy()
    son_alt = alt.copy()
    ilk_gecerli = atr.first_valid_index()
    ilk_i = df.index.get_loc(ilk_gecerli) if ilk_gecerli is not None else n

    for i in range(ilk_i + 1, n):
        son_ust[i] = min(ust[i], son_ust[i - 1]) if kapanis[i - 1] <= son_ust[i - 1] else ust[i]
        son_alt[i] = max(alt[i], son_alt[i - 1]) if kapanis[i - 1] >= son_alt[i - 1] else alt[i]

    yon_degeri = [None] * n
    if ilk_i < n:
        yon_degeri[ilk_i] = True  # baslangic varsayimi: yukari (True)
        for i in range(ilk_i + 1, n):
            onceki = yon_degeri[i - 1]
            if onceki and kapanis[i] < son_alt[i]:
                yon_degeri[i] = False
            elif (not onceki) and kapanis[i] > son_ust[i]:
                yon_degeri[i] = True
            else:
                yon_degeri[i] = onceki

    yon = pd.Series(
        [None if v is None else ("YUKARI" if v else "ASAGI") for v in yon_degeri],
        index=df.index)
    st_cizgisi = pd.Series(
        [son_alt[i] if yon_degeri[i] else son_ust[i] if yon_degeri[i] is not None else None
         for i in range(n)],
        index=df.index)
    return st_cizgisi, yon


def adx_hesapla(df, periyot):
    yuksek, dusuk = df["High"], df["Low"]
    onceki_yuksek, onceki_dusuk = yuksek.shift(1), dusuk.shift(1)
    yukselme = yuksek - onceki_yuksek
    dusme = onceki_dusuk - dusuk
    plus_dm = pd.Series(np.where((yukselme > dusme) & (yukselme > 0), yukselme, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((dusme > yukselme) & (dusme > 0), dusme, 0.0), index=df.index)
    atr = atr_hesapla(df, periyot)
    plus_di = 100 * plus_dm.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean() / atr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1 / periyot, adjust=False, min_periods=periyot).mean()
    return adx


def supertrend_adx_swing_simule(df, sembol):
    """SWING versiyonu: gunluk gruplama YOK, tek surekli seri. Pozisyon
    ST_FLIP'e (dogal) kadar VEYA MAKS_TUTMA_GUN asilirsa acik kalir -
    haftalarca/aylarca surebilir."""
    df = df.copy().sort_index()
    atr = atr_hesapla(df, ATR_PERIYOT)
    st_cizgi, st_yon = supertrend_hesapla(df, atr, ST_CARPAN)
    adx = adx_hesapla(df, ADX_PERIYOT)
    tum_islemler = []

    pozisyon = None  # (yon, giris_fiyat, giris_tarih)
    onceki_st_yon = None
    for i in range(len(df)):
        if pd.isna(st_yon.iloc[i]) or pd.isna(adx.iloc[i]):
            continue
        bar = df.iloc[i]
        tarih = bar.name.date() if hasattr(bar.name, "date") else bar.name
        kapanis = float(bar["Close"])
        flip_oldu = onceki_st_yon is not None and not pd.isna(onceki_st_yon) and st_yon.iloc[i] != onceki_st_yon
        onceki_st_yon = st_yon.iloc[i]

        if pozisyon is None:
            if flip_oldu and adx.iloc[i] >= ADX_ESIK:
                yeni_yon = "LONG" if st_yon.iloc[i] == "YUKARI" else "SHORT"
                pozisyon = (yeni_yon, kapanis, tarih)
        else:
            yon, giris, giris_tarih = pozisyon
            gun_sayisi = (tarih - giris_tarih).days
            cikis, sebep = None, None
            if yon == "LONG" and kapanis < st_cizgi.iloc[i]:
                cikis, sebep = kapanis, "ST_FLIP"
            elif yon == "SHORT" and kapanis > st_cizgi.iloc[i]:
                cikis, sebep = kapanis, "ST_FLIP"
            elif gun_sayisi >= MAKS_TUTMA_GUN:
                cikis, sebep = kapanis, "MAKS_TUTMA_ASILDI"
            elif i == len(df) - 1:
                cikis, sebep = kapanis, "VERI_SONU"
            if cikis is not None:
                ham = (cikis / giris - 1) * 100 * (1 if yon == "LONG" else -1)
                net = ham - MALIYET_YUZDE
                tum_islemler.append({"sembol": sembol, "giris_tarih": str(giris_tarih),
                                      "cikis_tarih": str(tarih), "tutma_gun": gun_sayisi,
                                      "yon": yon, "giris": giris, "cikis": cikis, "sebep": sebep,
                                      "ham_getiri_pct": round(ham, 3), "net_getiri_pct": round(net, 3)})
                pozisyon = None
    return tum_islemler


def main():
    tum_islemler = []
    for sembol in SEMBOLLER:
        try:
            df = yf.Ticker(sembol).history(period="5y", interval="1d")
            if df.empty:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            islemler = supertrend_adx_swing_simule(df, sembol)
            tum_islemler += islemler
            print(f"{sembol}: {len(islemler)} islem simule edildi")
        except Exception as e:
            print(f"HATA: {sembol} -> {e}", file=sys.stderr)

    ozet = {}
    for sembol in SEMBOLLER:
        alt = [t for t in tum_islemler if t["sembol"] == sembol]
        if not alt:
            continue
        kazanan = [t for t in alt if t["net_getiri_pct"] > 0]
        ozet[sembol] = {"islem_sayisi": len(alt),
                         "isabet_pct": round(100 * len(kazanan) / len(alt), 1),
                         "ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt) / len(alt), 3),
                         "toplam_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt), 2)}

    # GRUP BAZLI karsilastirma - asil test edilen hipotez burada
    grup_ozet = {}
    for grup_adi, grup_semboller in GRUP_SEMBOLLER.items():
        grup_islemler = [t for t in tum_islemler if t["sembol"] in grup_semboller]
        if not grup_islemler:
            continue
        kazanan = [t for t in grup_islemler if t["net_getiri_pct"] > 0]
        grup_ozet[grup_adi] = {
            "islem_sayisi": len(grup_islemler),
            "isabet_pct": round(100 * len(kazanan) / len(grup_islemler), 1),
            "ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in grup_islemler) / len(grup_islemler), 3),
            "toplam_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in grup_islemler), 2),
        }

    genel = None
    if tum_islemler:
        kazanan = [t for t in tum_islemler if t["net_getiri_pct"] > 0]
        genel = {"toplam_islem": len(tum_islemler),
                 "genel_isabet_pct": round(100 * len(kazanan) / len(tum_islemler), 1),
                 "genel_ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in tum_islemler) / len(tum_islemler), 3)}

    from collections import Counter
    sebepler = dict(Counter(t["sebep"] for t in tum_islemler))

    sonuc = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 SWING - Supertrend+ADX, GUNLUK barlar, 5 yillik "
                "gecmis. GUCLU vs ZAYIF anlati grup karsilastirmasi. "
                "SALT OLCUM. Hipotez: cok-gunlu ufukta, ayni teknik "
                "motor anlati gucune gore FARKLI performans gosterir mi?"),
        "parametreler": {"atr_periyot": ATR_PERIYOT, "st_carpan": ST_CARPAN,
                          "adx_periyot": ADX_PERIYOT, "adx_esik": ADX_ESIK,
                          "maks_tutma_gun": MAKS_TUTMA_GUN},
        "maliyet_varsayimi_pct": MALIYET_YUZDE,
        "sembol_bazli": ozet, "grup_karsilastirma": grup_ozet, "genel": genel,
        "cikis_sebebi_dagilimi": sebepler, "islem_detaylari": tum_islemler,
    }
    os.makedirs("data/backtest", exist_ok=True)
    atomik_json_yaz(CIKTI, sonuc)
    print(f"\nYazildi: {CIKTI}")
    for grup_adi, v in grup_ozet.items():
        print(f"{grup_adi}: {v['islem_sayisi']} islem, isabet %{v['isabet_pct']}, "
              f"ort net getiri %{v['ort_net_getiri_pct']}")
    if genel:
        print(f"GENEL: {genel['toplam_islem']} islem, isabet %{genel['genel_isabet_pct']}, "
              f"ort net getiri %{genel['genel_ort_net_getiri_pct']}")


if __name__ == "__main__":
    main()
