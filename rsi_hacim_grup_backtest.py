"""
RSI ASIRI-SATIM TERSINE-DONUS SWING CAPRAZ-DOGRULAMA (07.08.2026) - Faz V0
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
CIKTI = "data/backtest/rsi_hacim_grup_sonuc.json"
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


def ortalama_hacim_hesapla(df):
    return float(df["Volume"].mean()) if "Volume" in df.columns else None


def rsi_swing_simule(df, sembol):
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
        rsi_deger = rsi.iloc[i]
        rsi_alti_30 = rsi_deger < RSI_ALT_ESIK
        # 07.08 DUZELTME: 'is True' KULLANMA - pandas/numpy karsilastirma
        # sonuclari numpy.bool_ tipinde, Python'un yerlesik bool'u DEGIL,
        # "numpy.bool_(True) is True" HER ZAMAN False doner (kimlik
        # karsilastirmasi, deger degil). Bunun yerine dogrudan
        # truthy/falsy degerlendirmesi (None ve False ikisi de falsy).
        yukari_kesisim = bool(onceki_rsi_alti_30) and (not rsi_alti_30)
        onceki_rsi_alti_30 = rsi_alti_30

        if pozisyon is None:
            if yukari_kesisim:
                pozisyon = (kapanis, tarih)
        else:
            giris, giris_tarih = pozisyon
            gun_sayisi = (tarih - giris_tarih).days
            cikis, sebep = None, None
            if rsi_alti_30:
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


def main():
    tum_islemler = []
    hacimler = {}
    for sembol in SEMBOLLER:
        try:
            df = yf.Ticker(sembol).history(period="5y", interval="1d")
            if df.empty:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            islemler = rsi_swing_simule(df, sembol)
            tum_islemler += islemler
            hacim = ortalama_hacim_hesapla(df)
            if hacim is not None:
                hacimler[sembol] = hacim
            print(f"{sembol}: {len(islemler)} islem simule edildi, ort hacim {hacim:,.0f}" if hacim else f"{sembol}: {len(islemler)} islem")
        except Exception as e:
            print(f"HATA: {sembol} -> {e}", file=sys.stderr)

    # 07.08 EKI: hacim medyanina gore YUKSEK/DUSUK hacim grubu (buyuk-cap
    # vs kucuk/orta-cap vekili) - disposition-bias teorisini test etmek icin
    hacim_degerleri = sorted(hacimler.values())
    medyan_hacim = hacim_degerleri[len(hacim_degerleri) // 2] if hacim_degerleri else 0
    sembol_grup = {s: ("YUKSEK_HACIM" if h >= medyan_hacim else "DUSUK_HACIM")
                   for s, h in hacimler.items()}
    for t in tum_islemler:
        t["hacim_grubu"] = sembol_grup.get(t["sembol"], "BILINMIYOR")

    grup_ozet = {}
    for grup_adi in ("YUKSEK_HACIM", "DUSUK_HACIM", "BILINMIYOR"):
        grup_islemler = [t for t in tum_islemler if t["hacim_grubu"] == grup_adi]
        if not grup_islemler:
            continue
        sonuc = _ozet_hesapla(grup_islemler)
        if sonuc:
            grup_ozet[grup_adi] = sonuc

    genel = _ozet_hesapla(tum_islemler)
    if genel:
        genel = {"toplam_islem": genel["islem_sayisi"], "gecersiz_atlanan": genel["gecersiz_atlanan"],
                 "genel_isabet_pct": genel["isabet_pct"],
                 "genel_ort_net_getiri_pct": genel["ort_net_getiri_pct"]}

    from collections import Counter
    sebepler = dict(Counter(t["sebep"] for t in tum_islemler))

    sonuc_json = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 - RSI asiri-satim, YUKSEK/DUSUK ORTALAMA HACIM grup "
                "karsilastirmasi (buyuk-cap/kurumsal vs kucuk-orta-cap/"
                "bireysel vekili). Kahya&Ekinci(2022) disposition-bias "
                "bulgusunu dolayli test eder - hipotez: kucuk/dusuk-hacimli "
                "hisselerde bireysel yatirimci agirligi fazla, disposition "
                "bias daha guclu, RSI tersine-donus sinyali DAHA IYI "
                "calismali. SALT OLCUM."),
        "parametreler": {"rsi_periyot": RSI_PERIYOT, "rsi_alt_esik": RSI_ALT_ESIK,
                          "rsi_ust_esik": RSI_UST_ESIK, "maks_tutma_gun": MAKS_TUTMA_GUN,
                          "medyan_hacim": round(medyan_hacim, 0)},
        "maliyet_varsayimi_pct": MALIYET_YUZDE,
        "grup_karsilastirma": grup_ozet, "genel": genel,
        "cikis_sebebi_dagilimi": sebepler, "islem_detaylari": tum_islemler,
    }
    atomik_json_yaz(CIKTI, sonuc_json)
    print(f"\nYazildi: {CIKTI}")
    for grup, v in grup_ozet.items():
        print(f"{grup}: {v['islem_sayisi']} islem, isabet %{v['isabet_pct']}, "
              f"ort net %{v['ort_net_getiri_pct']}")


if __name__ == "__main__":
    main()
