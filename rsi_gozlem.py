"""
RSI GOZLEM DEFTERI + KURUMSAL TEYIT + RISK CERCEVESI (07.08.2026) - Faz V0
07.08 EKI (Denetim Madde 2+4): bagimsiz denetim sonrasi eklenen risk
katmanlari:
  - STOP-LOSS (-%12, grid testiyle secildi - bkz. rsi_stop_loss_grid.py):
    giris fiyatindan %12 dususte GUN ICI DUSUK fiyatiyla kontrol edilip
    cikilir - RSI kosullarindan ONCE kontrol edilir (oncelikli).
  - POZISYON/SEKTOR LIMITLERI: RSI-swing sistemi, miras P1/P2
    portfoyunden IZOLE, kendi SOYUT "kova"siyla (100 birim = kova
    tamami) calisir - gercek TL tutari SAKLANMAZ, ORANSAL sistem.
    Pozisyon basina kovanin %12'si, en fazla 5 esizamanli pozisyon,
    ayni sektorden en fazla 2 pozisyon. LIMIT asilirsa sinyal
    REDDEDILIR (sessizce atlanmaz - "reddedilen_sinyaller" listesine
    KAYDEDILIR, seffaflik icin).

ORIJINAL (07.08.2026) - Faz V0
07.08 EKI (Katman 2): her YENI sanal giris acildiginda, o sembolun
yabanci_takas_takip.json'daki EN SON kaydinin yonu (ARTIS/AZALIS)
"kurumsal_teyit" olarak etiketlenir - islem MANTIGINI degistirmez
(hicbir sinyal FILTRELENMIYOR), yalniz GOZLEM icin ek bilgi ekler.
Amac: zamanla "kurumsal_teyit=ARTIS olan sinyaller, AZALIS olanlardan
DAHA IYI mi performans gosteriyor" sorusuna CEVAP biriktirmek.

ORIJINAL (07.08.2026) - Faz V0
RSI(14,30,70) asiri-satim stratejisinin CANLI performansini, GERCEK
PARA RISKE ATMADAN izler. Her gun calisir (cron ile): yeni giris
sinyali olan sembolerde SANAL pozisyon acar, acik sanal pozisyonlarda
cikis kosullarini kontrol eder, defteri (data/rsi_gozlem_defteri.json)
gunceller.

KIRMIZI CIZGI: hicbir gercek islem/webhook/uyari uretmez - yalniz
GOZLEM. Backtest'teki AYNI mantik (giris: RSI 30'u yukari kesisim,
cikis: RSI tekrar 30 alti / RSI>=70 / 90 gun) - ama artik GECMISE
DONUK degil, GUNLUK olarak ILERIYE DOGRU calisiyor.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import pandas as pd
import numpy as np
import yfinance as yf

from konfig_yukle import sembol_evreni_yukle

DEFTER_YOL = "data/rsi_gozlem_defteri.json"
RSI_PERIYOT = 14
RSI_ALT_ESIK = 30
RSI_UST_ESIK = 70
MAKS_TUTMA_GUN = 90
MALIYET_YUZDE = 0.25
GECMIS_PENCERE = "90d"  # RSI(14) isinmasi icin fazlasiyla yeterli

# 07.08 EKI - Denetim Madde 2: stop-loss grid testiyle secildi
STOP_LOSS_YUZDE = 12

# 07.08 EKI - Denetim Madde 4: risk cercevesi (SOYUT birim, gercek TL YOK)
KOVA_TOPLAM_BIRIM = 100.0
POZISYON_BASINA_YUZDE = 12.0
# 10.08 GUNCELLEME (Bolum 4C, SWING_PINE_SPESIFIKASYONU.md): rsi_limit_
# grid.py + portfoy_risk_olcumu.py testleri sonucu 5 -> 8. Kanit: 8
# pozisyonda (12%x8=96%, matematiksel tutarli maksimum) edge onemli
# olcude iyilesiyor (5-yillik toplam getiri +%74.08 -> +%126.51),
# portfoy maks drawdown yalniz 1.08 PUAN kotulesiyor (-%9.04 -> -%10.12) -
# COK ASIMETRIK, OLUMLU bir risk/getiri degisimi.
MAKS_ESZAMANLI_POZISYON = 8
SEKTOR_BASINA_MAKS_POZISYON = 2

# Yaklasik, elle siniflandirilmis sektor haritasi (kesin BIST resmi
# siniflandirmasi degil, risk-cesitlendirme amacli kaba gruplama)
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
    "EKGYO": "GYO", "TRMET": "Madencilik", "TRALT": "Madencilik",
}


def sektor_bul(sembol):
    return SEKTOR_HARITASI.get(sembol, "DIGER")


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


def kurumsal_teyit_bul(sembol):
    """yabanci_takas_takip.json'dan sembolun EN SON kaydinin yonunu
    dondurur. Dosya/kayit yoksa 'BILINMIYOR' - script COKMEZ."""
    try:
        with open("data/yabanci_takas_takip.json", encoding="utf-8") as f:
            veri = json.load(f)
    except Exception:
        return "BILINMIYOR"
    kayitlar = [k for k in veri.get("kayitlar", []) if k["sembol"] == sembol]
    if not kayitlar:
        return "BILINMIYOR"
    en_son = max(kayitlar, key=lambda k: k["tarih"])
    return en_son["yon"]  # "ARTIS" / "AZALIS" / "SABIT"


def _oku_defter():
    try:
        with open(DEFTER_YOL, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"acik_pozisyonlar": {}, "kapanan_pozisyonlar": []}


def main():
    semboller, sonek, _ = sembol_evreni_yukle()
    defter = _oku_defter()
    defter.setdefault("reddedilen_sinyaller", [])
    bugun_utc = datetime.datetime.now(datetime.timezone.utc)

    giris_adaylari = []  # [(sembol, son_kapanis, son_rsi), ...]

    # ASAMA 1: TUM semboller icin veri/RSI hesapla, ACIK pozisyonlarda
    # CIKIS kontrolu (stop-loss DAHIL) yap - LIMIT kisitlamasi YOK,
    # mevcut pozisyonu kapatmak HICBIR ZAMAN engellenmez.
    for sembol in semboller:
        ticker_id = f"{sembol}{sonek}"
        try:
            df = yf.Ticker(ticker_id).history(period=GECMIS_PENCERE, interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
            continue
        if df.empty or len(df) < RSI_PERIYOT + 2:
            print(f"UYARI: {sembol} icin yetersiz veri", file=sys.stderr)
            continue

        kapanislar = df["Close"]
        rsi = rsi_hesapla(kapanislar, RSI_PERIYOT)
        if pd.isna(kapanislar.iloc[-1]) or pd.isna(rsi.iloc[-1]) or pd.isna(rsi.iloc[-2]):
            print(f"UYARI: {sembol} son bar NaN, atlandi", file=sys.stderr)
            continue

        son_kapanis = float(kapanislar.iloc[-1])
        son_tarih = kapanislar.index[-1].date()
        son_dusuk = (float(df["Low"].iloc[-1])
                     if "Low" in df.columns and not pd.isna(df["Low"].iloc[-1])
                     else son_kapanis)
        onceki_rsi = float(rsi.iloc[-2])
        son_rsi = float(rsi.iloc[-1])
        onceki_alti_30 = onceki_rsi < RSI_ALT_ESIK
        simdi_alti_30 = son_rsi < RSI_ALT_ESIK
        # 07.08 dersi: 'is True' KULLANMA, numpy.bool_/Python bool
        # kimlik karsilastirmasi hep False doner - dogrudan truthy kullan.
        yukari_kesisim = bool(onceki_alti_30) and (not simdi_alti_30)

        acik = defter["acik_pozisyonlar"].get(sembol)
        if acik is None:
            if yukari_kesisim:
                giris_adaylari.append((sembol, son_kapanis, son_rsi))
        else:
            giris_tarih = datetime.date.fromisoformat(acik["giris_tarih"])
            gun_sayisi = (son_tarih - giris_tarih).days
            stop_seviyesi = acik["giris_fiyat"] * (1 - STOP_LOSS_YUZDE / 100)
            cikis, sebep = None, None
            if son_dusuk <= stop_seviyesi:
                cikis, sebep = stop_seviyesi, "SABIT_STOP_LOSS"
            elif simdi_alti_30:
                cikis, sebep = son_kapanis, "BASARISIZ_SICRAMA"
            elif son_rsi >= RSI_UST_ESIK:
                cikis, sebep = son_kapanis, "KAR_AL_ASIRI_ALIM"
            elif gun_sayisi >= MAKS_TUTMA_GUN:
                cikis, sebep = son_kapanis, "MAKS_TUTMA_ASILDI"
            if cikis is not None:
                ham = (cikis / acik["giris_fiyat"] - 1) * 100
                net = round(ham - MALIYET_YUZDE, 3)
                defter["kapanan_pozisyonlar"].append({
                    "sembol": sembol, "giris_tarih": acik["giris_tarih"],
                    "cikis_tarih": str(son_tarih), "tutma_gun": gun_sayisi,
                    "giris_fiyat": acik["giris_fiyat"], "cikis_fiyat": cikis,
                    "sebep": sebep, "net_getiri_pct": net,
                    "kurumsal_teyit": acik.get("kurumsal_teyit", "BILINMIYOR"),
                    "sektor": acik.get("sektor", sektor_bul(sembol)),
                })
                del defter["acik_pozisyonlar"][sembol]
                print(f"{sembol}: SANAL CIKIS @ {round(cikis,2)} ({sebep}), net %{net}")

    # ASAMA 2: giris ADAYLARINI kova/pozisyon/sektor LIMITINE gore isle.
    # Cikislar YUKARIDA zaten islendigi icin, bugun kapanan bir pozisyonun
    # yeri, ayni kosumda YENI bir girise acik olabilir.
    for sembol, son_kapanis, son_rsi in giris_adaylari:
        sektor = sektor_bul(sembol)
        acik_sayisi = len(defter["acik_pozisyonlar"])
        sektor_sayisi = sum(1 for s in defter["acik_pozisyonlar"] if sektor_bul(s) == sektor)

        if acik_sayisi >= MAKS_ESZAMANLI_POZISYON:
            defter["reddedilen_sinyaller"].append({
                "sembol": sembol, "tarih": str(bugun_utc.date()),
                "sebep": "ESZAMANLI_POZISYON_LIMITI",
                "not": f"{acik_sayisi}/{MAKS_ESZAMANLI_POZISYON} pozisyon zaten acik"})
            print(f"{sembol}: REDDEDILDI (esizamanli limit {acik_sayisi}/{MAKS_ESZAMANLI_POZISYON})")
            continue
        if sektor_sayisi >= SEKTOR_BASINA_MAKS_POZISYON:
            defter["reddedilen_sinyaller"].append({
                "sembol": sembol, "tarih": str(bugun_utc.date()),
                "sebep": "SEKTOR_LIMITI",
                "not": f"{sektor}: {sektor_sayisi}/{SEKTOR_BASINA_MAKS_POZISYON} pozisyon zaten acik"})
            print(f"{sembol}: REDDEDILDI (sektor limiti - {sektor})")
            continue

        kurumsal = kurumsal_teyit_bul(sembol)
        defter["acik_pozisyonlar"][sembol] = {
            "giris_tarih": str(bugun_utc.date()), "giris_fiyat": son_kapanis,
            "giris_rsi": round(son_rsi, 1), "kurumsal_teyit": kurumsal,
            "sektor": sektor, "pozisyon_birim_yuzde": POZISYON_BASINA_YUZDE,
        }
        print(f"{sembol}: YENI SANAL GIRIS @ {son_kapanis} (RSI {son_rsi:.1f}, "
              f"sektor={sektor}, kurumsal_teyit={kurumsal})")

    defter["son_guncelleme_utc"] = bugun_utc.isoformat()
    kapananlar = defter["kapanan_pozisyonlar"]
    if kapananlar:
        kazanan = [k for k in kapananlar if k["net_getiri_pct"] > 0]
        defter["ozet"] = {
            "toplam_kapanan": len(kapananlar),
            "isabet_pct": round(100 * len(kazanan) / len(kapananlar), 1),
            "ort_net_getiri_pct": round(sum(k["net_getiri_pct"] for k in kapananlar) / len(kapananlar), 3),
        }
    atomik_json_yaz(DEFTER_YOL, defter)
    print(f"\nDefter guncellendi: {len(defter['acik_pozisyonlar'])} acik, "
          f"{len(kapananlar)} kapanmis sanal pozisyon")


if __name__ == "__main__":
    main()
