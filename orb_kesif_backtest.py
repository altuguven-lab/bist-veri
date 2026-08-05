"""
GUN ICI ORB KESIF-BACKTEST (05.08.2026) - Faz V0
GitHub/acik kaynak referanslarindan (umerdawood23, je-suis-tm) alinan
parametrelerle, BIST'in kendi gercek verisinde ORB (Acilis Araligi
Kirilimi) stratejisini test eder. KIRMIZI CIZGI: bu SALT OLCUM -
hicbir gercek islem/sinyal uretmez, Pine'a hic dokunmaz.

Kisit: yfinance 15dk barlarda yalniz ~60 gun geriye gidebiliyor -
bu, uzun donemli bir kanit degil, ilk yaklasik bir bakis.

Yontem (acik kaynak referanslarindan):
  - Acilis araligi: ilk 15 dakika (10:00-10:15 TSI) yuksek/dusuk
  - Kirilim: bir sonraki barin kapanisi araligin disina ciktiginda giris
  - Hedef (T1): aralik genisliginin %100'u kadar (umerdawood23 deseni)
  - Stop: aralik disi
  - Zorla kapat: seans sonunda (18:00 TSI civarinda), gecelik pozisyon YOK
  - Maliyet: %0.25 gidis-donus (Borsamix'in BIST gercekci varsayimi)
"""
import json, datetime, os, sys
import pandas as pd
import yfinance as yf

SEMBOLLER = ["AKBNK.IS", "KCHOL.IS", "THYAO.IS", "GARAN.IS"]
ACILIS_DAKIKA = 15  # ilk 15 dakika = acilis araligi
MALIYET_YUZDE = 0.25  # Borsamix gercekci varsayimi, gidis-donus
CIKTI = "data/backtest/orb_kesif_v2_sonuc.json"

# 05.08 EKI (v2) - uc iyilestirme, kurulun onerisiyle:
HACIM_KATSAYI = 1.3     # kirilim barinin hacmi, onceki N barin ortalamasinin
                        # kacini gecmeli (acik kaynak referanslarindaki
                        # "yuksek hacim" filtresi)
HACIM_PENCERE = 5       # ortalama hacim icin kac onceki bar kullanilsin
RTR = 2.0               # Risk:Odul orani (umerdawood23 varsayilani "2:1")
                        # hedef = giris +/- (aralik * RTR), stop degismedi
                        # (aralik disinda) - yalniz hedef genisletildi.


def gunluk_vwap(grup):
    """Gun icinde biriken VWAP serisi (tipik fiyat x hacim / hacim)."""
    tipik = (grup["High"] + grup["Low"] + grup["Close"]) / 3.0
    kum_pv = (tipik * grup["Volume"]).cumsum()
    kum_v = grup["Volume"].cumsum().replace(0, pd.NA)
    return kum_pv / kum_v


def orb_simule(df, sembol):
    """Gunluk bazda ORB: ilk bar (10:00-10:15) araligini kirilinca gir,
    T1'de ya da gun sonunda kapat. df: DatetimeIndex'li 15dk OHLC.
    v2: hacim teyidi + VWAP filtresi + 2:1 hedef/risk orani."""
    df = df.copy()
    df["gun"] = df.index.date
    islemler = []

    for gun, grup in df.groupby("gun"):
        grup = grup.sort_index()
        # 05.08 DUZELTME: 09:45 bari acik artirma (call auction) tek-fiyat
        # ani olabilir (O=H=L=C, aralik=0) - BIST surekli seansi 10:00'da
        # baslar, acilis araligini ORADAN itibaren al.
        grup = grup[grup.index.time >= datetime.time(10, 0)]
        if len(grup) < 3:
            continue
        acilis_bar = grup.iloc[0]
        ust, alt = float(acilis_bar["High"]), float(acilis_bar["Low"])
        aralik = ust - alt
        if aralik <= 0:
            continue
        vwap_serisi = gunluk_vwap(grup)

        pozisyon = None  # ("LONG"/"SHORT", giris_fiyat)
        for i in range(1, len(grup)):
            bar = grup.iloc[i]
            kapanis = float(bar["Close"])
            if pozisyon is None:
                # HACIM TEYIDI: kirilim barinin hacmi, onceki HACIM_PENCERE
                # barin ortalamasinin HACIM_KATSAYI kati kadar olmali.
                pencere_bas = max(0, i - HACIM_PENCERE)
                ort_hacim = grup["Volume"].iloc[pencere_bas:i].mean()
                hacim_teyit = (ort_hacim > 0 and
                               float(bar["Volume"]) >= HACIM_KATSAYI * ort_hacim)
                # VWAP FILTRESI: LONG icin fiyat VWAP ustunde, SHORT icin altinda.
                vwap_deger = vwap_serisi.iloc[i]
                vwap_gecerli = not pd.isna(vwap_deger)

                if kapanis > ust and hacim_teyit and vwap_gecerli and kapanis > vwap_deger:
                    pozisyon = ("LONG", kapanis, i)
                elif kapanis < alt and hacim_teyit and vwap_gecerli and kapanis < vwap_deger:
                    pozisyon = ("SHORT", kapanis, i)
            else:
                yon, giris, giris_i = pozisyon
                # v2: hedef artik RTR kati genisletildi (2:1), stop degismedi.
                hedef = giris + aralik * RTR if yon == "LONG" else giris - aralik * RTR
                stop = alt if yon == "LONG" else ust
                cikis, sebep = None, None
                if yon == "LONG" and (bar["High"] >= hedef):
                    cikis, sebep = hedef, "HEDEF"
                elif yon == "LONG" and (bar["Low"] <= stop):
                    cikis, sebep = stop, "STOP"
                elif yon == "SHORT" and (bar["Low"] <= hedef):
                    cikis, sebep = hedef, "HEDEF"
                elif yon == "SHORT" and (bar["High"] >= stop):
                    cikis, sebep = stop, "STOP"
                elif i == len(grup) - 1:
                    cikis, sebep = kapanis, "GUN_SONU"
                if cikis is not None:
                    ham_getiri = (cikis / giris - 1) * 100 * (1 if yon == "LONG" else -1)
                    net_getiri = ham_getiri - MALIYET_YUZDE
                    islemler.append({"sembol": sembol, "gun": str(gun), "yon": yon,
                                      "giris": giris, "cikis": cikis, "sebep": sebep,
                                      "ham_getiri_pct": round(ham_getiri, 3),
                                      "net_getiri_pct": round(net_getiri, 3)})
                    pozisyon = None
    return islemler


def main():
    tum_islemler = []
    for sembol in SEMBOLLER:
        try:
            df = yf.Ticker(sembol).history(period="60d", interval="15m")
            if df.empty:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            # 05.08 TANI EKI: 0 islem cikinca korlemeden once veri yapisina bak
            gun_sayilari = df.groupby(df.index.date).size()
            ilk_bar = df.iloc[0]
            print(f"  {sembol} TANI: toplam bar={len(df)}, gun sayisi={len(set(df.index.date))}, "
                  f"gun basi ort bar={gun_sayilari.mean():.1f}, ilk bar zamani={df.index[0]}, "
                  f"ilk bar OHLC=O{ilk_bar['Open']:.2f}/H{ilk_bar['High']:.2f}/"
                  f"L{ilk_bar['Low']:.2f}/C{ilk_bar['Close']:.2f}")
            islemler = orb_simule(df, sembol)
            tum_islemler += islemler
            print(f"{sembol}: {len(islemler)} islem simule edildi")
        except Exception as e:
            print(f"HATA: {sembol} -> {e}", file=sys.stderr)

    ozet = {}
    for sembol in SEMBOLLER:
        alt_kume = [t for t in tum_islemler if t["sembol"] == sembol]
        if not alt_kume:
            continue
        kazanan = [t for t in alt_kume if t["net_getiri_pct"] > 0]
        ozet[sembol] = {
            "islem_sayisi": len(alt_kume),
            "isabet_pct": round(100 * len(kazanan) / len(alt_kume), 1),
            "ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt_kume) / len(alt_kume), 3),
            "toplam_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in alt_kume), 2),
        }

    genel = None
    if tum_islemler:
        kazanan = [t for t in tum_islemler if t["net_getiri_pct"] > 0]
        genel = {
            "toplam_islem": len(tum_islemler),
            "genel_isabet_pct": round(100 * len(kazanan) / len(tum_islemler), 1),
            "genel_ort_net_getiri_pct": round(sum(t["net_getiri_pct"] for t in tum_islemler) / len(tum_islemler), 3),
        }

    sonuc = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 kesif-backtest v2 - SALT OLCUM, gercek islem/sinyal degil. "
                "yfinance 60 gunluk 15dk pencereyle sinirli - uzun donemli kanit degil. "
                "v1'den fark: hacim teyidi + VWAP filtresi + 2:1 hedef/risk orani."),
        "maliyet_varsayimi_pct": MALIYET_YUZDE,
        "hacim_katsayi": HACIM_KATSAYI, "hacim_pencere": HACIM_PENCERE, "rtr": RTR,
        "sembol_bazli": ozet,
        "genel": genel,
        "islem_detaylari": tum_islemler,
    }
    os.makedirs("data/backtest", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"\nYazildi: {CIKTI}")
    if genel:
        print(f"GENEL: {genel['toplam_islem']} islem, isabet %{genel['genel_isabet_pct']}, "
              f"ort net getiri %{genel['genel_ort_net_getiri_pct']}")


if __name__ == "__main__":
    main()
