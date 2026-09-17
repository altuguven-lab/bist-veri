"""
B1 FAZ V0: KGS GUNLUK-BAR YAKLASIK PORTU (17.09.2026)
======================================================
Amac: KULUCKA SONRASI BIRIKIM B1 maddesi ("Skor mukerrerlik/cifte-esik
kalibrasyonu") icin gereken bilesen korelasyon matrisini kurabilmek -
KGS'nin gercek degerini, entryScore'un gercekte KGS'yi ne kadar
tekrar ettigini olcmek.

KIRMIZI CIZGI: SALT OLCUM. Pine'a (V162) hic dokunmuyor, kulucka
sayacini etkilemiyor, hicbir alarma baglanmiyor.

DURUSTLUK NOTU (zorunlu, V162'nin GUNLUK ISKELET GOSTERGESI ile ayni
ilkeyle): Bu GOSTERGE NITELIGINDE bir YAKLASIK KOPYADIR.
  1) COZUNURLUK: V162 15 dakikalik barda calisiyor; yfinance'in 15dk
     gecmis veri siniri ~60 gun oldugundan, bu script GUNLUK barda
     calisir. Gunluk KGS, 15dk KGS'nin AYNISI DEGILDIR.
  2) V0'DA BILEREK ATLANAN KGS ayarlamalari (_kgsRaw'a giren ama
     burada UYGULANMAYAN terimler): _kgsBankAdj, _kgsStateBonus
     (_smState makinesi), _kgsV103Adj, _kgsEarlyLeaderAdj (xbank),
     _kgsAccelAdj (_leaderAccel), _kgsSectorIndexAdj, ve sonrasindaki
     taban/tavan istisnalari (_kgsEliteCondition, HOLDING/HAVACILIK
     tabanlari, _recoveryBelowMain tavani). Bunlarin coju KUCUK,
     KOSULLU bonus/ceza (tipik +/-2 ila +10 puan araligi) - tum
     semboller/gunler arasinda benzer sekilde eksik oldugu icin
     KORELASYON YONU icin daha az kritik, ama MUTLAK KGS DUZEYI icin
     onemli sapma kaynagi.
  3) fakeRisk/panicSell/marketRisk/exitRiskFull/_gizliToplama/
     _gizliDagitim/_kurumBaskisi icin gercek Pine tanimlari bu
     kapsamda cikarilmadi (mum-yapisi/piyasa-genisligi agir
     formuller) - V0'da hepsi FALSE varsayilir. Bu, risk cezasini
     (_kgsRiskPenalty) ve f_kgsKurum'un "kurumsal biriktirme" ust
     dallarini SISTEMATIK OLARAK ASAGI CEKER (KGS gercek degerinden
     hafifce YUKSEK cikma egiliminde olabilir).
  4) CVD gercek tick/emir-akisi verisi gerektirir; burada OBV ile
     AYNI proxy (isaretli hacim kumulatifi) kullanildi - cvdRising/
     cvdBullDiv bu proxy uzerinden hesaplaniyor, Pine'daki BAGIMSIZ
     CVD SERISI DEGIL.
  5) Sektor endeksi (secRoc): once gercek BIST sektor endeksi
     (XBANK.IS vb.) denenir; yfinance'ta bulunamazsa o sektordeki
     evren-ici sembollerin esit-agirlikli ortalamasina duser.
  6) htfAlign (coklu zaman dilimi hizalanmasi) GUNLUK barda anlamli
     karsiligi olmadigi icin BASIT bir haftalik-EMA proxysiyle
     yaklasiklanmistir - V162'nin gercek 60dk/240dk mantigi DEGIL.

SONUC: bu script'in urettigi KGS, GERCEK V162 KGS'sinin DUZEYCE
sapabilen ama YON/GORECELI DAVRANIS acisindan ilk fikir verebilecek
bir on-gostergedir. TEK BASINA hicbir uretim agirlik degisikligine
GEREKCE OLAMAZ - yalnizca B1'in ilk keşif adimidir.

Cikti: data/backtest/kgs_gunluk_port_sonuc.json
"""
import json
import sys
import datetime

import numpy as np
import pandas as pd
import yfinance as yf

# ---- Evren + sektor haritasi (V162 f_autoSector'un README evrenine
# (30 sembol) uygulanmis hali, yalnizca ilgili dallar) ----
SEKTOR = {
    "AKBNK": "BANKACILIK", "YKBNK": "BANKACILIK", "GARAN": "BANKACILIK",
    "ISCTR": "BANKACILIK", "HALKB": "BANKACILIK", "VAKBN": "BANKACILIK",
    "KCHOL": "HOLDING", "SAHOL": "HOLDING",
    "BIMAS": "PERAKENDE", "MGROS": "PERAKENDE",
    "ASELS": "SAVUNMA",
    "THYAO": "HAVACILIK", "PGSUS": "HAVACILIK", "TAVHL": "HAVACILIK",
    "TTKOM": "ILETISIM",
    "EREGL": "SINAI", "SISE": "SINAI", "TRMET": "SINAI",
    "TUPRS": "ENERJI", "PETKM": "ENERJI", "ASTOR": "ENERJI", "ENJSA": "ENERJI",
    "ENKAI": "INSAAT",
    "EKGYO": "GYO",
    "FROTO": "OTOMOTIV", "TOASO": "OTOMOTIV", "OTKAR": "OTOMOTIV",
    "AEFES": "GENEL", "ALARK": "GENEL", "ULKER": "GENEL",
}
SEMBOLLER = list(SEKTOR.keys())

SEKTOR_ENDEKS_TICKER = {
    "BANKACILIK": "XBANK.IS", "HOLDING": "XHOLD.IS", "PERAKENDE": "XGIDA.IS",
    "SAVUNMA": "XUSIN.IS", "HAVACILIK": "XULAS.IS", "ILETISIM": "XILTM.IS",
    "SINAI": "XMANA.IS", "ENERJI": "XELKT.IS", "INSAAT": "XINSA.IS",
    "GYO": "XGMYO.IS", "OTOMOTIV": "XMESY.IS",
}

ENDEKS = "XU100.IS"
BAS, SON = "2019-01-01", None  # 2018 EMA200 isinma payi icin biraz once baslanir yfinance'ta ayarlanacak
FASTLEN, MIDLEN, SLOWLEN, MAINLEN = 9, 21, 50, 200
VOLLEN, RSILEN, OBVLEN, CVDSMALEN = 20, 14, 20, 14


def f_clamp(v, lo, hi):
    return np.clip(v, lo, hi)


def veri_cek(ticker, start="2018-06-01"):
    try:
        df = yf.download(ticker, start=start, interval="1d",
                          auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna() if not df.empty else None
    except Exception as e:
        print(f"UYARI: {ticker} -> {e}", file=sys.stderr)
        return None


def mfi_hesapla(df, periyot):
    tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
    rmf = tp * df["Volume"]
    delta = tp.diff()
    pos_mf = rmf.where(delta > 0, 0.0).rolling(periyot).sum()
    neg_mf = rmf.where(delta < 0, 0.0).rolling(periyot).sum()
    mr = pos_mf / neg_mf.replace(0, np.nan)
    mfi = 100 - (100 / (1 + mr))
    return mfi.fillna(50.0)


def gostergeler(df):
    df = df.copy()
    df["e9"] = df["Close"].ewm(span=FASTLEN, adjust=False).mean()
    df["e21"] = df["Close"].ewm(span=MIDLEN, adjust=False).mean()
    df["e50"] = df["Close"].ewm(span=SLOWLEN, adjust=False).mean()
    df["e200"] = df["Close"].ewm(span=MAINLEN, adjust=False).mean()
    df["volAvg"] = df["Volume"].rolling(VOLLEN).mean()
    df["relVol"] = df["Volume"] / df["volAvg"]
    # V0: htfAlign yaklaşıklaması - haftalık EMA21 üzerinde mi (basit proxy)
    haftalik_e21 = df["Close"].resample("W").last().ewm(span=MIDLEN, adjust=False).mean()
    haftalik_e21_gunluk = haftalik_e21.reindex(df.index, method="ffill")
    df["htfAlign_proxy"] = np.where(df["Close"] > haftalik_e21_gunluk, 1, 0)
    # sinyalli hacim (CVD/OBV ortak proxy)
    isaret = np.sign(df["Close"].diff()).fillna(0)
    df["obv"] = (isaret * df["Volume"]).cumsum()
    df["obvSma"] = df["obv"].rolling(OBVLEN).mean()
    df["obvTrend"] = df["obv"] > df["obvSma"]
    df["obvFalling"] = df["obv"] < df["obv"].shift(1)
    df["cvd"] = df["obv"]  # V0 proxy (durustluk notu madde 4)
    df["cvdSma"] = df["cvd"].rolling(CVDSMALEN).mean()
    df["cvdRising"] = (df["cvd"] > df["cvd"].shift(3)) & (df["cvd"] > df["cvdSma"])
    df["cvdBullDiv"] = ((df["Close"] < df["Close"].shift(5)) & (df["cvd"] > df["cvd"].shift(5)) &
                         df["cvdRising"])
    df["mfi"] = mfi_hesapla(df, RSILEN)
    df["mfiBull"] = df["mfi"] > 50
    df["stkRoc"] = df["Close"].pct_change(20) * 100
    # hidden distribution (Pine'daki gercek formul - upperWick/candleBody
    # icin OHLC'den turetiliyor)
    body = (df["Close"] - df["Open"]).abs().replace(0, np.nan)
    upper_wick = df["High"] - df[["Close", "Open"]].max(axis=1)
    df["hiddenDist"] = ((df["Close"] > df["Open"]) & df["obvFalling"] &
                         (df["relVol"] > 1.5) & (upper_wick > body * 0.5)).fillna(False)
    df["volumeSpike"] = df["Volume"] > df["volAvg"] * 1.3
    df["volumeHuge"] = df["Volume"] > df["volAvg"] * 2.5
    df["volumeDry"] = df["Volume"] < df["volAvg"] * 0.60
    return df


def kgs_hesapla(df, idx_roc, sec_roc, sec_strong):
    n = len(df)
    idxRoc = idx_roc.reindex(df.index)
    secRoc = sec_roc.reindex(df.index)
    secStrong = sec_strong.reindex(df.index).fillna(False)

    rsIndex = df["stkRoc"] - idxRoc
    rsSector = df["stkRoc"] - secRoc
    rsRank = rsIndex.rolling(100, min_periods=20).apply(
        lambda s: pd.Series(s).rank(pct=True).iloc[-1] * 100, raw=False)
    rsSectorRnk = rsSector.rolling(100, min_periods=20).apply(
        lambda s: pd.Series(s).rank(pct=True).iloc[-1] * 100, raw=False)
    rsMomentum = rsRank > rsRank.shift(5) + 5
    isSectorStrongEff = secStrong  # V0: isMomStock dali atlandi
    isStockLeadingSector = (rsSector > 1.0) & (rsIndex > 0)
    kgsSecAlpha = df["stkRoc"] - secRoc

    aboveMain = df["Close"] > df["e200"]
    emaStrongStack = (df["e9"] > df["e21"]) & (df["e21"] > df["e50"]) & (df["Close"] > df["e9"])
    emaWeakBreak = (df["Close"] < df["e9"]) & (df["Close"] > df["e21"])
    emaCritBreak = df["Close"] < df["e21"]
    htf = df["htfAlign_proxy"]  # V0 basitlestirilmis (0 veya 1; gercek 0/1/2 degil)

    # --- 7 alt-skor (Pine formulleriyle BIREBIR - V162_1_yama.txt
    # satir 276-293) ---
    kgsTrend = np.where(emaStrongStack & (htf == 2), 18,
               np.where(emaStrongStack, 15,
               np.where((~emaWeakBreak) & (~emaCritBreak), 13,
               np.where(emaWeakBreak, 6, 2))))

    kgsEma = f_clamp(
        np.where(aboveMain, 7, -4) + np.where(df["Close"] > df["e50"], 4, -2) +
        np.where(df["Close"] > df["e21"], 2, -1) + np.where(htf >= 1, 3, -2), -6, 14)

    kgsRsBase = np.select(
        [rsRank >= 80, rsRank >= 70, rsRank >= 55, rsRank >= 40, rsRank >= 25, rsRank >= 10],
        [np.where(rsSectorRnk >= 70, 20, 16), 16, 12, 8, 5, 2], default=0)
    # yukaridaki ilk kosul ikili (rsRank>=80 AND secRank>=70 -> 20,
    # yoksa rsRank>=70 AND secRank>=55 -> 16) - Pine'daki tam mantik:
    kgsRsBase = np.where((rsRank >= 80) & (rsSectorRnk >= 70), 20,
                np.where((rsRank >= 70) & (rsSectorRnk >= 55), 16,
                np.where(rsRank >= 55, 12,
                np.where(rsRank >= 40, 8,
                np.where(rsRank >= 25, 5,
                np.where(rsRank >= 10, 2, 0))))))
    kgsRs = kgsRsBase + np.where(rsMomentum & df["volumeSpike"], 5,
                          np.where(rsMomentum, 3, 0))

    green = df["Close"] > df["Open"]
    kgsVol = np.where(df["volumeHuge"] & green, 12,
              np.where(df["volumeSpike"], 9,
              np.where((df["relVol"] > 1.2) & (~df["volumeDry"]), 7,
              np.where((df["relVol"] > 0.9) & (~df["volumeDry"]), 5,
              np.where(df["volumeDry"], 1, 3)))))
    # not: fakeRisk V0'da False varsayildigi icin _fake kollari dustu

    kgsSectorBase = np.where(isSectorStrongEff & isStockLeadingSector & (kgsSecAlpha > 2.0), 12,
                     np.where(isSectorStrongEff & isStockLeadingSector, 10,
                     np.where(isSectorStrongEff, 8,
                     np.where(secStrong, 5,
                     np.where(rsSector > 0.0, 3,
                     np.where(rsSector < -2.0, 1, 2))))))
    kgsSector = kgsSectorBase  # V0: _secLeadScore atlandi (+0)

    kgsCvd = np.where(df["cvdBullDiv"] & df["obvTrend"], 10,
              np.where(df["cvdBullDiv"], 8,
              np.where(df["cvdRising"] & df["obvTrend"] & (~df["hiddenDist"]), 7,
              np.where(df["cvdRising"] & (~df["hiddenDist"]), 4,
              np.where(df["hiddenDist"], 0, 3)))))

    # V0: _gizliToplama/_gizliDagitim/_kurumBaskisi False -> yalniz
    # obvTrend/mfiBull dallari canli
    kgsKurum = np.where(df["obvTrend"] & df["mfiBull"], 6,
               np.where(df["obvTrend"], 4, 2))

    # V0: panicSell/marketRisk/exitRiskFull/fakeRisk hepsi False
    kgsRiskPenalty = np.zeros(n)

    kgsRaw = kgsTrend + kgsEma + kgsRs + kgsVol + kgsSector + kgsCvd + kgsKurum
    kgs = f_clamp(kgsRaw - kgsRiskPenalty, 0, 100)

    return pd.DataFrame({
        "kgs": kgs, "kgsTrend": kgsTrend, "kgsEma": kgsEma, "kgsRs": kgsRs,
        "kgsVol": kgsVol, "kgsSector": kgsSector, "kgsCvd": kgsCvd,
        "kgsKurum": kgsKurum, "rsRank": rsRank, "rsSectorRnk": rsSectorRnk,
    }, index=df.index)


def volume_quality_ve_accel(df):
    # f_volumeQuality (satir 328-338) + f_leaderAcceleration/f_v105Setup
    # (satir 298-318) - V0: _fake=False varsayildi
    green = (df["Close"] > df["Open"]) & (df["Close"] >= df["Low"] + (df["High"] - df["Low"]) * 0.60) & (df["relVol"] > 1.2)
    breakout = df["Close"] > df["High"].shift(1).rolling(20).max()
    breakCond = breakout & (df["relVol"] > 1.2)
    greenPts = np.where(green, 35, 0)
    breakPts = np.where(breakCond, 40, 0)
    relPts = np.select([df["relVol"] >= 2.0, df["relVol"] >= 1.5, df["relVol"] > 1.2, df["relVol"] > 0.9],
                        [25, 20, 15, 8], default=0)
    raw = greenPts + breakPts + relPts
    volQuality = pd.Series(f_clamp(np.maximum(20, raw), 0, 100), index=df.index)

    rsDelta = df["stkRoc"] - df["stkRoc"].shift(3)
    cvdDelta = df["cvd"] - df["cvd"].shift(3)
    cvdNorm = df["cvd"].diff().abs().rolling(20).mean() * 3.0
    atr = (df["High"] - df["Low"]).rolling(14).mean()
    emaSlope = df["e9"] - df["e9"].shift(3)
    rsPart = pd.Series(f_clamp(np.round((rsDelta / 100 + 0.25) * 12.5), 0, 25), index=df.index)
    volPart = pd.Series(f_clamp(np.round((df["relVol"] - 0.8) * 20.0), 0, 25), index=df.index)
    cvdPart = pd.Series(f_clamp(np.round((cvdDelta / np.maximum(cvdNorm, 1.0) + 0.2) * 31.25), 0, 25), index=df.index)
    emaPart = pd.Series(f_clamp(np.round((emaSlope / atr.replace(0, np.nan)) * 125.0), 0, 25), index=df.index)
    accel = (rsPart + volPart + cvdPart + emaPart).fillna(0)
    return volQuality, accel


def entry_score_base(kgs, volQuality, accel):
    # f_entryScore'un _base terimi (satir 384) - TAM entryScore DEGIL,
    # yalniz KGS'nin entryScore icindeki DOGRUDAN agirlikli girdisi.
    return kgs * 0.38 + volQuality * 0.12 + accel * 0.10


def main():
    endeks = veri_cek(ENDEKS, start=BAS)
    if endeks is None:
        print("HATA: XU100 verisi cekilemedi, durduruluyor", file=sys.stderr)
        return
    endeks_g = gostergeler(endeks)
    idxRoc = endeks_g["stkRoc"]

    sektor_kapanis = {}
    for sek, tkr in SEKTOR_ENDEKS_TICKER.items():
        d = veri_cek(tkr, start=BAS)
        if d is not None and len(d) > 100:
            sektor_kapanis[sek] = d["Close"]
            print(f"Sektor endeksi bulundu: {sek} -> {tkr}")
        else:
            print(f"UYARI: {sek} sektor endeksi ({tkr}) bulunamadi, "
                  f"evren-ici proxy'ye dusulecek", file=sys.stderr)

    ham = {}
    for s in SEMBOLLER:
        d = veri_cek(f"{s}.IS", start=BAS)
        if d is not None and len(d) > 250:
            ham[s] = gostergeler(d)

    # evren-ici sektor proxy (sektor endeksi bulunamayanlar icin)
    sektor_proxy = {}
    for sek in set(SEKTOR.values()):
        uyeler = [s for s, sk in SEKTOR.items() if sk == sek and s in ham]
        if len(uyeler) >= 2:
            kapaniclar = pd.concat([ham[s]["Close"].pct_change() for s in uyeler], axis=1).mean(axis=1)
            sektor_proxy[sek] = 100 * (1 + kapaniclar.fillna(0)).cumprod()

    sonuclar = {}
    birlesik_parcalar = []
    for s, df in ham.items():
        sek = SEKTOR[s]
        if sek in sektor_kapanis:
            sec_close = sektor_kapanis[sek]
        elif sek in sektor_proxy:
            sec_close = sektor_proxy[sek]
        else:
            sec_close = endeks["Close"]  # son care: genel endekse dus
        secRoc = sec_close.pct_change(20).reindex(df.index).ffill() * 100
        secStrong = (secRoc > idxRoc.reindex(df.index) + 0.5).fillna(False)

        kgs_df = kgs_hesapla(df, idxRoc, secRoc, secStrong)
        volQ, accel = volume_quality_ve_accel(df)
        entryBase = entry_score_base(kgs_df["kgs"], volQ, accel)

        birlesik = df.join(kgs_df).assign(volQuality=volQ, accel=accel, entryScoreBase=entryBase)
        birlesik = birlesik.dropna(subset=["kgs", "entryScoreBase"])
        birlesik_parcalar.append(birlesik[["kgs", "entryScoreBase"]])

        korelasyon = float(birlesik["kgs"].corr(birlesik["entryScoreBase"])) if len(birlesik) > 30 else None

        sonuclar[s] = {
            "sektor": sek,
            "bar_sayisi": len(birlesik),
            "kgs_ortalama": round(float(birlesik["kgs"].mean()), 2) if len(birlesik) else None,
            "kgs_std": round(float(birlesik["kgs"].std()), 2) if len(birlesik) else None,
            "entryScoreBase_ortalama": round(float(birlesik["entryScoreBase"].mean()), 2) if len(birlesik) else None,
            "kgs_entryScoreBase_korelasyon": round(korelasyon, 3) if korelasyon is not None else None,
            "alt_skor_ortalamalari": {
                k: round(float(birlesik[k].mean()), 2)
                for k in ["kgsTrend", "kgsEma", "kgsRs", "kgsVol", "kgsSector", "kgsCvd", "kgsKurum"]
            },
        }
        print(f"{s} ({sek}): n={len(birlesik)}, KGS ort={sonuclar[s]['kgs_ortalama']}, "
              f"korelasyon(KGS, entryScoreBase)={sonuclar[s]['kgs_entryScoreBase_korelasyon']}")

    genel_korelasyon = None
    if birlesik_parcalar:
        tum_veri = pd.concat(birlesik_parcalar, axis=0)
        if len(tum_veri) > 30:
            genel_korelasyon = round(float(tum_veri["kgs"].corr(tum_veri["entryScoreBase"])), 3)

    rapor = {
        "calisma": "B1 Faz V0 - KGS Gunluk-Bar Yaklasik Portu",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "GOSTERGE NITELIGINDE yaklasik kopya, GUNLUK barda (15dk DEGIL). "
            "V0'da atlanan KGS ayarlamalari: kgsBankAdj, kgsStateBonus, kgsV103Adj, "
            "kgsEarlyLeaderAdj, kgsAccelAdj, kgsSectorIndexAdj, elite/holding/havacilik "
            "taban istisnalari, risk cezasi (hepsi False varsayildi). CVD, OBV proxy'si "
            "ile yaklasiklanmistir, bagimsiz tick verisi degildir. TEK BASINA hicbir "
            "uretim agirlik degisikligine GEREKCE OLAMAZ - B1'in ilk kesif adimidir."
        ),
        "evren": list(ham.keys()),
        "sembol_bazli": sonuclar,
        "genel_kgs_entryScoreBase_korelasyon": genel_korelasyon,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/kgs_gunluk_port_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print(f"\nTamamlandi: {len(ham)} sembol -> data/backtest/kgs_gunluk_port_sonuc.json")


if __name__ == "__main__":
    main()
