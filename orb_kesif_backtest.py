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

# 05.08 EKI (v3) - kurul karari: AKBNK/KCHOL v2'de neredeyse basabas
# cikti (THYAO/GARAN hala kotu) - onlara odaklanip parametre TARAMASI
# yapiyoruz (tek deneme yerine, tek kosumda cok kombinasyon).
SEMBOLLER = ["AKBNK.IS", "KCHOL.IS"]
ACILIS_DAKIKA = 15  # ilk 15 dakika = acilis araligi
MALIYET_YUZDE = 0.25  # Borsamix gercekci varsayimi, gidis-donus
CIKTI = "data/backtest/orb_kesif_v3_grid_sonuc.json"
HACIM_PENCERE = 5       # ortalama hacim icin kac onceki bar kullanilsin

# GRID: her kombinasyon ayri simule edilir, sonuclar karsilastirilir.
HACIM_KATSAYI_LISTE = [1.0, 1.3, 1.8]
RTR_LISTE = [1.5, 2.0, 3.0]
STOP_ORAN_LISTE = [0.5, 1.0]  # 1.0 = v2 ile ayni (aralik kadar stop),
                              # 0.5 = daha siki stop (aralik yarisi)


def gunluk_vwap(grup):
    """Gun icinde biriken VWAP serisi (tipik fiyat x hacim / hacim)."""
    tipik = (grup["High"] + grup["Low"] + grup["Close"]) / 3.0
    kum_pv = (tipik * grup["Volume"]).cumsum()
    kum_v = grup["Volume"].cumsum().replace(0, pd.NA)
    return kum_pv / kum_v


def orb_simule(df, sembol, hacim_katsayi, rtr, stop_oran):
    """Gunluk bazda ORB: ilk bar (10:00-10:15) araligini kirilinca gir,
    T1'de ya da gun sonunda kapat. df: DatetimeIndex'li 15dk OHLC.
    v3: hacim teyidi + VWAP filtresi + parametrik hedef/stop orani."""
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
                               float(bar["Volume"]) >= hacim_katsayi * ort_hacim)
                # VWAP FILTRESI: LONG icin fiyat VWAP ustunde, SHORT icin altinda.
                vwap_deger = vwap_serisi.iloc[i]
                vwap_gecerli = not pd.isna(vwap_deger)

                if kapanis > ust and hacim_teyit and vwap_gecerli and kapanis > vwap_deger:
                    pozisyon = ("LONG", kapanis, i)
                elif kapanis < alt and hacim_teyit and vwap_gecerli and kapanis < vwap_deger:
                    pozisyon = ("SHORT", kapanis, i)
            else:
                yon, giris, giris_i = pozisyon
                # v3: hedef VE stop artik parametrik. stop_oran=1.0 -> v2 ile
                # ayni (tam aralik disi), 0.5 -> stop mesafesi yariya iner.
                hedef = giris + aralik * rtr if yon == "LONG" else giris - aralik * rtr
                stop = (giris - aralik * stop_oran if yon == "LONG"
                        else giris + aralik * stop_oran)
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
    # Veriyi HER SEMBOL icin BIR KEZ cek (grid taramasinda tekrar tekrar
    # yfinance cagirmamak icin - performans).
    veriler = {}
    for sembol in SEMBOLLER:
        try:
            df = yf.Ticker(sembol).history(period="60d", interval="15m")
            if df.empty:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            veriler[sembol] = df
            print(f"{sembol}: {len(df)} bar cekildi")
        except Exception as e:
            print(f"HATA: {sembol} -> {e}", file=sys.stderr)

    grid_sonuclari = []
    for hacim_katsayi in HACIM_KATSAYI_LISTE:
        for rtr in RTR_LISTE:
            for stop_oran in STOP_ORAN_LISTE:
                tum_islemler = []
                for sembol, df in veriler.items():
                    islemler = orb_simule(df, sembol, hacim_katsayi, rtr, stop_oran)
                    tum_islemler += islemler
                if not tum_islemler:
                    continue
                kazanan = [t for t in tum_islemler if t["net_getiri_pct"] > 0]
                grid_sonuclari.append({
                    "hacim_katsayi": hacim_katsayi, "rtr": rtr, "stop_oran": stop_oran,
                    "islem_sayisi": len(tum_islemler),
                    "isabet_pct": round(100 * len(kazanan) / len(tum_islemler), 1),
                    "ort_net_getiri_pct": round(
                        sum(t["net_getiri_pct"] for t in tum_islemler) / len(tum_islemler), 3),
                    "toplam_net_getiri_pct": round(
                        sum(t["net_getiri_pct"] for t in tum_islemler), 2),
                })
                print(f"  hacim={hacim_katsayi} rtr={rtr} stop_oran={stop_oran} -> "
                      f"{len(tum_islemler)} islem, ort net %{grid_sonuclari[-1]['ort_net_getiri_pct']}")

    # en iyi ortalama net getiriye gore sirala
    grid_sonuclari.sort(key=lambda x: x["ort_net_getiri_pct"], reverse=True)

    sonuc = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 kesif-backtest v3 - SALT OLCUM, gercek islem/sinyal degil. "
                "yfinance 60 gunluk 15dk pencereyle sinirli - uzun donemli kanit degil. "
                "Yalniz AKBNK+KCHOL (v2'de en iyi ikisi). Parametre taramasi: "
                f"{len(HACIM_KATSAYI_LISTE)}x{len(RTR_LISTE)}x{len(STOP_ORAN_LISTE)} "
                "kombinasyon, en iyi ortalama net getiriye gore siralandi."),
        "maliyet_varsayimi_pct": MALIYET_YUZDE,
        "semboller": SEMBOLLER,
        "grid_sonuclari": grid_sonuclari,
        "en_iyi_3": grid_sonuclari[:3],
    }
    os.makedirs("data/backtest", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"\nYazildi: {CIKTI}")
    if grid_sonuclari:
        en_iyi = grid_sonuclari[0]
        print(f"EN IYI: hacim={en_iyi['hacim_katsayi']} rtr={en_iyi['rtr']} "
              f"stop_oran={en_iyi['stop_oran']} -> ort net getiri %{en_iyi['ort_net_getiri_pct']}, "
              f"isabet %{en_iyi['isabet_pct']}, {en_iyi['islem_sayisi']} islem")


if __name__ == "__main__":
    main()
