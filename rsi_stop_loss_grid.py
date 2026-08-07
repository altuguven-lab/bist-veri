"""
RSI ASIRI-SATIM - SABIT STOP-LOSS GRID TESTI (07.08.2026) - Faz V0
Denetim bulgusu Madde 2: mevcut RSI cikis mantigi (RSI<30 tekrar/
RSI>=70/90 gun) TEK BASINA yeterli risk kontrolu mu, yoksa SABIT
yuzde stop-loss EKLENMELI mi? Birden fazla stop seviyesini (-%5/-%8/
-%12 + stopSUZ referans) AYNI veride PARALEL test eder. Stop kontrolu
GUN ICI DUSUK (Low) fiyatiyla yapilir - yalniz kapanisla degil, GERCEK
bir stop emrinin calisma bicimine daha yakin.

ORIJINAL (07.08.2026) - Faz V0
Bugunku Supertrend+ADX swing bulgusunu (ZAYIF_MOMENTUM'da tersine-donus
sinyalleri daha iyi calisiyor, p=0.032 anlamli) TAMAMEN FARKLI bir
gosterge mekanigiyle (RSI, trend-takip DEGIL, osilator) capraz-dogrular.
Eger AYNI desen burada da cikarsa, bu "tesadufi Supertrend garipligi"
degil, GERCEK bir piyasa fenomeni oldugunun kaniti guclenir.

Yontem:
  - RSI(14) standart formul.
  - Giris: RSI 30'un ALTINDAN YUKARI kesisirse (asiri-satimdan cikis,
    "sicrama" sinyali) = LONG.
  - Cikis: RSI tekrar 30'un ALTINA duserse (basarisiz sicrama, ATR
    stop YERINE RSI'in kendi mantigi) VEYA RSI 70'i GECERSE (kar al)
    VEYA MAKS_TUTMA_GUN (90) asilirsa.
  - AYNI momentum-grup ayrimi (6 aylik trailing getiri, giris ANINDA,
    bakis-oncesi yanlilik YOK) - bugunku Supertrend bulgusuyla
    DOGRUDAN karsilastirilabilir olmasi icin.
  - Maliyet: %0.25 gidis-donus (ayni varsayim).
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
CIKTI = "data/backtest/rsi_stop_loss_grid_sonuc.json"
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


def rsi_swing_simule(df, sembol, stop_yuzde=None):
    """stop_yuzde: None ise stop-loss YOK (orijinal mantik). Pozitif
    bir sayi (orn. 8) verilirse, giris fiyatindan %8 dususte (GUN ICI
    DUSUK/Low fiyatiyla kontrol edilir) STOP_LOSS ile cikilir - bu,
    RSI cikis kosullarindan (BASARISIZ_SICRAMA/KAR_AL/MAKS_TUTMA)
    ONCE kontrol edilir (ayni gunde ikisi de olusabilecek olsa bile
    stop ONCELIKLI - gercek bir stop emri boyle calisir)."""
    df = df.copy().sort_index()
    rsi = rsi_hesapla(df, RSI_PERIYOT)
    tum_islemler = []

    pozisyon = None  # (giris_fiyat, giris_tarih)
    onceki_rsi_alti_30 = None
    for i in range(len(df)):
        bar = df.iloc[i]
        if pd.isna(bar["Close"]) or pd.isna(rsi.iloc[i]):
            continue
        tarih = bar.name.date() if hasattr(bar.name, "date") else bar.name
        kapanis = float(bar["Close"])
        gun_ici_dusuk = float(bar["Low"]) if "Low" in df.columns and not pd.isna(bar["Low"]) else kapanis
        rsi_deger = rsi.iloc[i]
        rsi_alti_30 = rsi_deger < RSI_ALT_ESIK
        yukari_kesisim = bool(onceki_rsi_alti_30) and (not rsi_alti_30)
        onceki_rsi_alti_30 = rsi_alti_30

        if pozisyon is None:
            if yukari_kesisim:
                pozisyon = (kapanis, tarih)
        else:
            giris, giris_tarih = pozisyon
            gun_sayisi = (tarih - giris_tarih).days
            cikis, sebep = None, None
            stop_seviyesi = giris * (1 - stop_yuzde / 100) if stop_yuzde else None
            if stop_seviyesi is not None and gun_ici_dusuk <= stop_seviyesi:
                cikis, sebep = stop_seviyesi, "SABIT_STOP_LOSS"
            elif rsi_alti_30:
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
                tum_islemler.append({"sembol": sembol, "giris_tarih": str(giris_tarih),
                                      "cikis_tarih": str(tarih), "tutma_gun": gun_sayisi,
                                      "giris": giris, "cikis": cikis, "sebep": sebep,
                                      "ham_getiri_pct": round(ham, 3), "net_getiri_pct": round(net, 3)})
                pozisyon = None
    return tum_islemler


STOP_GRID = [None, 5, 8, 12]  # None = stopsuz referans


def main():
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
    for stop_yuzde in STOP_GRID:
        tum_islemler = []
        for sembol, df in veri_seti.items():
            tum_islemler += rsi_swing_simule(df, sembol, stop_yuzde=stop_yuzde)
        ozet = _ozet_hesapla(tum_islemler)
        etiket = "STOPSUZ" if stop_yuzde is None else f"STOP_%{stop_yuzde}"
        if ozet:
            from collections import Counter
            sebepler = dict(Counter(t["sebep"] for t in tum_islemler))
            en_kotu_5 = sorted((t["net_getiri_pct"] for t in tum_islemler))[:5]
            izgara_sonuclari.append({
                "stop_etiketi": etiket, "stop_yuzde": stop_yuzde,
                **ozet, "cikis_sebebi_dagilimi": sebepler,
                "en_kotu_5_islem_net_pct": [round(x, 2) for x in en_kotu_5],
            })
            print(f"{etiket}: {ozet['islem_sayisi']} islem, isabet %{ozet['isabet_pct']}, "
                  f"ort net %{ozet['ort_net_getiri_pct']}, en kotu: {round(min(en_kotu_5),1) if en_kotu_5 else None}")
        else:
            print(f"{etiket}: hic islem uretilmedi")

    sonuc_json = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 - Denetim Madde 2: sabit stop-loss grid testi. "
                "Mevcut RSI cikis mantigina (RSI<30 tekrar/RSI>=70/90 gun) "
                "SABIT YUZDE stop EKLENMESI edge'i (isabet/ort getiri) "
                "koruyup EN KOTU islemleri sinirliyor mu test eder. "
                "Stop kontrolu GUN ICI DUSUK (Low) fiyatiyla, GERCEKCI. "
                "SALT OLCUM."),
        "parametreler": {"rsi_periyot": RSI_PERIYOT, "rsi_alt_esik": RSI_ALT_ESIK,
                          "rsi_ust_esik": RSI_UST_ESIK, "maks_tutma_gun": MAKS_TUTMA_GUN},
        "maliyet_varsayimi_pct": MALIYET_YUZDE,
        "sembol_sayisi": len(veri_seti),
        "izgara_sonuclari": izgara_sonuclari,
    }
    atomik_json_yaz(CIKTI, sonuc_json)
    print(f"\nYazildi: {CIKTI}")


if __name__ == "__main__":
    main()
