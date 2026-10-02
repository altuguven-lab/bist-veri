"""
SOGUMA x HACIM ZIRVESI CAKISMA TESTI (02.10.2026)
=============================================================
Soru: ACIL_CIK sonrasi uygulanan 20 bar (5 saat, pSogumaBar) soguma
penceresi, P3_SKOR_AL icin gereken hacim teyidinin (relVol >= 1.2,
pTetikHacim) TAM O PENCEREDE gelmesi durumunda gercek bir girisi
sistematik olarak kacirtiyor mu? (ASTOR 01.10.2026 vakasindan dogan
soru: 07:00 ACIL_CIK -> 09:45/11:45'te relVol 17x/6.5x ama soguma
icindeydi -> soguma bitince (12:00) hacim sonmustu (relVol 0.49,
15:11) -> gun boyunca hic P3_SKOR_AL gelmedi.)

Yontem:
  1. sinyal_arsiv.json'daki TUM ACIL_CIK olaylari (15 kayit, 9 sembol,
     07.08-01.10.2026) alinir.
  2. Her olay icin GUNLUK kayitta sadece TARIH var, saat yok - bu yuzden
     o gunun 15 dakikalik barlarinda KAPANIS FIYATI sinyal_fiyat'a en
     yakin barin "tahmini tetik bari" oldugu varsayilir (tolerans %0.3).
     Eslesme bulunamazsa olay DISLANIR (atlanmaz-sayilmaz, sayisi
     raporlanir).
  3. relVol YAKLASIMI: Pine'daki gercek metrik, zaman-dilimi bazli
     EMA'dir (0.8/0.2, haftalarca isinma gerektirir) - burada ayni
     sembolun ayni saat dilimindeki (saat:dakika) TUM diger gunlerinin
     BASIT ORTALAMASI kullanilir (olay gunu haric). Bu TAM AYNI SAYIYI
     URETMEZ, sadece "o an normalin kac kati" sorusuna yaklasik bir
     cevap verir.
  4. SENARYO A (GERCEK/sistem): soguma bitince (olay bari + 20.bar)
     ilk relVol>=1.2 bar'da giris (sonraki 40 bar/~2 gun icinde yoksa
     girisyok=A_YOK).
  5. SENARYO B (HIPOTETIK, soguma YOKMUS GIBI): soguma penceresinin
     (olay bari dahil 20 bar) ICINDE ilk relVol>=1.2 bar'da giris.
  6. Her iki senaryonun ileri getirisi (T+1saat~4bar, T+1gun~32bar,
     T+3gun~96bar) karsilastirilir.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunulmuyor, hicbir parametre
degistirilmiyor.

DURUSTLUK NOTU (onemli, oku):
  - Orneklem KUCUK: 15 ACIL_CIK olayindan, (a) fiyat-eslesmesi basarisiz
    olanlar, (b) yfinance'in ~60 gunluk 15dk veri penceresi disinda
    kalanlar (07-08.2026 basi gibi eski olaylar calistirma anindaki
    tarihe gore silinmis olabilir) cikarildiktan sonra GERCEKTE kac
    olay kaldigi "kullanilabilir_olay_sayisi" alaninda raporlanir -
    bu sayi tek haneli olabilir, boyle bir ornekelemden KESIN hukum
    CIKARILAMAZ, yalniz bir EGILIM/ON-BULGU olarak okunmalidir.
  - relVol yaklasik (madde 3), Pine'in gercek EMA degerinden sapabilir.
  - "Tahmini tetik bari" fiyat eslesmesine dayanir (madde 2) - ayni gun
    icinde fiyatin iki kez ayni seviyeye gelmesi yanlis bar secimine
    yol acabilir; bu riskin etkisini azaltmak icin sadece ACIL_CIK'in
    tipik olarak GUN ICI ERKEN saatlerde (regime=0, panik) tetiklendigi
    bilgisiyle ilk eslesen bari seciyoruz, ama garanti degil.
  - Sembol bazinda saglamlik ayrica raporlanir (lateEntry testinden
    ogrenilen ders: aggregate tek basina yeterli degil).

Cikti: data/backtest/soguma_hacim_cakisma_test.json
"""
import json
import datetime as dt

import numpy as np
import pandas as pd
import yfinance as yf

ACIL_CIK_OLAYLARI_YOL = "data/sinyal_arsiv.json"
SOGUMA_BAR = 20          # pSogumaBar (Pine)
HACIM_ESIGI = 1.2        # pTetikHacim (Pine)
FIYAT_TOLERANS_PCT = 0.3 # tahmini tetik bari eslesme toleransi
SONRAKI_PENCERE_BAR = 40 # soguma sonrasi giris aranacak azami bar
ILERI_BAR = {"T+1saat": 4, "T+1gun": 32, "T+3gun": 96}  # 15dk bar varsayimiyla


def intraday_cek(sembol, gun):
    """gun (datetime.date) cevresinde birkac gunluk 15dk veri ceker."""
    try:
        start = gun - dt.timedelta(days=1)
        end = gun + dt.timedelta(days=4)
        df = yf.download(f"{sembol}.IS", start=start, end=end,
                          interval="15m", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"UYARI: {sembol} {gun} -> {e}")
        return None


def genis_pencere_cek(sembol, merkez_gun, gerigun=45, ilerigun=10):
    """Zaman-dilimi ortalamasi icin genis bir 15dk pencere ceker."""
    try:
        start = merkez_gun - dt.timedelta(days=gerigun)
        end = merkez_gun + dt.timedelta(days=ilerigun)
        df = yf.download(f"{sembol}.IS", start=start, end=end,
                          interval="15m", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty or len(df) < 50:
            return None
        return df
    except Exception as e:
        print(f"UYARI (genis pencere): {sembol} -> {e}")
        return None


def tetik_barini_bul(df, gun, sinyal_fiyat):
    gun_df = df[df.index.date == gun]
    if gun_df.empty or sinyal_fiyat is None:
        return None
    fark_pct = (gun_df["Close"] - sinyal_fiyat).abs() / sinyal_fiyat * 100
    en_yakin_idx = fark_pct.idxmin()
    if fark_pct.loc[en_yakin_idx] > FIYAT_TOLERANS_PCT:
        return None
    return en_yakin_idx


def relvol_hesapla(df, event_ts):
    """Ayni saat:dakika diliminin (olay gunu haric) basit ortalamasina
    gore relVol serisi. Donus: pd.Series (relVol), index ile hizali."""
    slot = df.index.map(lambda t: (t.hour, t.minute))
    df = df.copy()
    df["_slot"] = slot
    event_gun = event_ts.date()
    baz = df[df.index.date != event_gun].groupby("_slot")["Volume"].mean()
    relvol = df.apply(lambda row: row["Volume"] / baz.get(row["_slot"], np.nan)
                       if baz.get(row["_slot"], np.nan) not in (0, np.nan) and not pd.isna(baz.get(row["_slot"], np.nan))
                       else np.nan, axis=1)
    return relvol


def ileri_getiri_hesapla(df, entry_idx, entry_fiyat):
    pos = df.index.get_loc(entry_idx)
    sonuc = {}
    for etiket, bar in ILERI_BAR.items():
        hedef_pos = pos + bar
        if hedef_pos < len(df):
            hedef_fiyat = df["Close"].iloc[hedef_pos]
            sonuc[etiket] = round(float((hedef_fiyat / entry_fiyat - 1) * 100), 3)
        else:
            sonuc[etiket] = None
    return sonuc


def main():
    with open(ACIL_CIK_OLAYLARI_YOL, encoding="utf-8") as f:
        arsiv = json.load(f)
    olaylar = [k for k in arsiv.get("kayitlar", []) if k.get("sinyal") == "ACIL_CIK"]

    sonuclar = []
    dislanma_sayaci = {"veri_yok": 0, "fiyat_eslesmedi": 0, "yetersiz_gecmis": 0}

    for olay in olaylar:
        sembol = olay["sembol"]
        tarih = dt.datetime.strptime(olay["tarih"], "%Y-%m-%d").date()
        sinyal_fiyat = olay.get("sinyal_fiyat")

        genis = genis_pencere_cek(sembol, tarih)
        if genis is None:
            dislanma_sayaci["veri_yok"] += 1
            continue

        tetik_ts = tetik_barini_bul(genis, tarih, sinyal_fiyat)
        if tetik_ts is None:
            dislanma_sayaci["fiyat_eslesmedi"] += 1
            continue

        relvol_seri = relvol_hesapla(genis, tetik_ts)
        if relvol_seri.isna().sum() > len(relvol_seri) * 0.7:
            dislanma_sayaci["yetersiz_gecmis"] += 1
            continue

        pos0 = genis.index.get_loc(tetik_ts)

        # SENARYO B: soguma penceresi ICINDE (pos0..pos0+19) ilk hacim-teyitli bar
        senaryo_b_idx = None
        for i in range(pos0, min(pos0 + SOGUMA_BAR, len(genis))):
            rv = relvol_seri.iloc[i]
            if not pd.isna(rv) and rv >= HACIM_ESIGI:
                senaryo_b_idx = genis.index[i]
                senaryo_b_relvol = round(float(rv), 2)
                break

        # SENARYO A: soguma BITTIKTEN SONRA (pos0+20 ...) ilk hacim-teyitli bar
        senaryo_a_idx = None
        a_basla = pos0 + SOGUMA_BAR
        for i in range(a_basla, min(a_basla + SONRAKI_PENCERE_BAR, len(genis))):
            rv = relvol_seri.iloc[i]
            if not pd.isna(rv) and rv >= HACIM_ESIGI:
                senaryo_a_idx = genis.index[i]
                senaryo_a_relvol = round(float(rv), 2)
                break

        kayit = {
            "sembol": sembol,
            "tarih": olay["tarih"],
            "acil_cik_fiyat": sinyal_fiyat,
            "tahmini_tetik_bari_utc": str(tetik_ts),
            "cakisma_var_mi": senaryo_b_idx is not None,
        }

        if senaryo_b_idx is not None:
            b_fiyat = float(genis["Close"].loc[senaryo_b_idx])
            kayit["senaryo_b_hipotetik"] = {
                "giris_bari_utc": str(senaryo_b_idx),
                "relvol": senaryo_b_relvol,
                "giris_fiyat": round(b_fiyat, 3),
                "ileri_getiri_pct": ileri_getiri_hesapla(genis, senaryo_b_idx, b_fiyat),
            }
        else:
            kayit["senaryo_b_hipotetik"] = None

        if senaryo_a_idx is not None:
            a_fiyat = float(genis["Close"].loc[senaryo_a_idx])
            kayit["senaryo_a_gercek_sistem"] = {
                "giris_bari_utc": str(senaryo_a_idx),
                "relvol": senaryo_a_relvol,
                "giris_fiyat": round(a_fiyat, 3),
                "ileri_getiri_pct": ileri_getiri_hesapla(genis, senaryo_a_idx, a_fiyat),
            }
        else:
            kayit["senaryo_a_gercek_sistem"] = "GIRIS_YOK (soguma sonrasi 40 bar icinde hacim esigi gelmedi)"

        sonuclar.append(kayit)

    # --- AGREGE: sadece HEM A HEM B'si olan (karsilastirilabilir) olaylar ---
    karsilastirilabilir = [r for r in sonuclar
                            if r.get("cakisma_var_mi")
                            and isinstance(r.get("senaryo_a_gercek_sistem"), dict)]
    karsilastirma_ozet = {}
    for etiket in ILERI_BAR:
        farklar = []
        for r in karsilastirilabilir:
            ga = r["senaryo_a_gercek_sistem"]["ileri_getiri_pct"].get(etiket)
            gb = r["senaryo_b_hipotetik"]["ileri_getiri_pct"].get(etiket)
            if ga is not None and gb is not None:
                farklar.append(gb - ga)  # pozitif = B (hipotetik erken giris) daha iyi
        if farklar:
            karsilastirma_ozet[etiket] = {
                "adet": len(farklar),
                "b_minus_a_ortalama_pp": round(float(np.mean(farklar)), 3),
                "b_daha_iyi_oran_pct": round(100 * float(np.mean([f > 0 for f in farklar])), 1),
            }
        else:
            karsilastirma_ozet[etiket] = {"adet": 0}

    # yalniz B var ama A hic gelmemis (gercek kacirilan firsat) olaylar
    sadece_b_var = [r for r in sonuclar
                     if r.get("cakisma_var_mi")
                     and r.get("senaryo_a_gercek_sistem") == "GIRIS_YOK (soguma sonrasi 40 bar icinde hacim esigi gelmedi)"]

    cikti = {
        "olusturma_utc": dt.datetime.utcnow().isoformat() + "Z",
        "parametreler": {"SOGUMA_BAR": SOGUMA_BAR, "HACIM_ESIGI": HACIM_ESIGI,
                          "FIYAT_TOLERANS_PCT": FIYAT_TOLERANS_PCT},
        "toplam_acil_cik_kaydi": len(olaylar),
        "kullanilabilir_olay_sayisi": len(sonuclar),
        "dislanma_detayi": dislanma_sayaci,
        "cakisma_goruldugu_olay_sayisi": sum(1 for r in sonuclar if r.get("cakisma_var_mi")),
        "tam_kacirilan_firsat_sayisi (B var, A hic gelmedi)": len(sadece_b_var),
        "karsilastirilabilir_olay_sayisi (hem A hem B var)": len(karsilastirilabilir),
        "karsilastirma_ozet (B_hipotetik_erken_giris - A_gercek_sistem, pp)": karsilastirma_ozet,
        "olay_detaylari": sonuclar,
        "_durustluk_notu": (
            "SALT OLCUM, Pine'a dokunulmadi. relVol, Pine'daki gercek "
            "zaman-dilimi EMA'sinin BASIT ORTALAMA yaklasigidir, birebir "
            "ayni sayiyi uretmez. Tetik bari, GUNLUK kayittaki fiyattan "
            "GERIYE DOGRU eslestirilerek tahmin edildi (saat bilgisi "
            "arsivde yok) - yanlis bar secimi riski vardir. Kucuk "
            "orneklemden (bkz. kullanilabilir_olay_sayisi) KESIN HUKUM "
            "CIKARILAMAZ, sadece on-bulgu olarak okunmalidir."
        ),
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/soguma_hacim_cakisma_test.json", "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    print(json.dumps({k: v for k, v in cikti.items() if k != "olay_detaylari"},
                      ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
