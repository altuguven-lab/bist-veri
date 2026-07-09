"""
IP-2: GUNLUK ISKELET KARAKTER HARITASI (2018-2026)
==================================================
Nitelik: GOSTERGE NITELIGINDE yaklasik kopya. Getiri iddiasi uretmez;
sistemin YIL/REJIM bazli karakterini haritalar. Pozisyon boyutu kararlarina
girdi OLAMAZ (bkz. IP1_OZET.md Karar K3).

Icerik:
- Yil bazli: rejim ON orani, flip sayisi, vekil strateji vs al-tut, MaxDD
- Islem bazli: P1-vekili girislerin T+3 / T+10 isabetleri, ortalama sonuc
- Evren: 2018'den beri kesintisiz islem goren likit buyuk hisseler
Cikti: data/backtest/ip2_iskelet_sonuc.json
"""

import json
import os
import sys
import datetime

import numpy as np
import pandas as pd
import yfinance as yf

BAS, SON = "2017-06-01", "2026-07-09"   # 2018 oncesi isinma payi
ANALIZ_BAS = "2018-01-01"

SEMBOLLER = ["AKBNK", "GARAN", "YKBNK", "ISCTR", "HALKB", "VAKBN",
             "KCHOL", "SAHOL", "THYAO", "TUPRS", "EREGL", "ASELS",
             "BIMAS", "MGROS", "SISE", "PETKM", "TCELL", "TTKOM",
             "FROTO", "TOASO", "ARCLK", "ULKER", "PGSUS"]
ENDEKS = "XU100.IS"

EMA_H, EMA_O, EMA_Y = 9, 21, 50
HACIM_PENCERE, HACIM_ESIK = 20, 1.3
GENISLIK_ESIK = 0.4


def veri_cek(t):
    try:
        df = yf.download(t, start=BAS, end=SON, interval="1d",
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna() if not df.empty else None
    except Exception as e:
        print(f"UYARI: {t} -> {e}", file=sys.stderr)
        return None


def gostergeler(df):
    df = df.copy()
    df["e9"] = df["Close"].ewm(span=EMA_H, adjust=False).mean()
    df["e21"] = df["Close"].ewm(span=EMA_O, adjust=False).mean()
    df["e50"] = df["Close"].ewm(span=EMA_Y, adjust=False).mean()
    df["vAvg"] = df["Volume"].rolling(HACIM_PENCERE).mean()
    df["relVol"] = df["Volume"] / df["vAvg"]
    df["gunluk"] = df["Close"].pct_change() * 100
    return df


def rejim_seri(endeks, genislik):
    rejim, durum = [], "ON"
    for t, row in endeks.iterrows():
        g = genislik.get(t, np.nan)
        if durum == "ON":
            if row["Close"] < row["e21"] and (row["e9"] < row["e21"] or (not np.isnan(g) and g < GENISLIK_ESIK)):
                durum = "OFF"
        else:
            if row["Close"] > row["e21"] and row["e9"] >= row["e21"]:
                durum = "ON"
        rejim.append(durum)
    return pd.Series(rejim, index=endeks.index)


def p1_girisleri(df, rejim):
    """P1-vekili: altin dizilim (e9>e21>e50) + kapanis>e21 + hacim>=1.3x,
    onceki gun dizilim YOKKEN bugun olusmasi (gecis ani) + rejim ON."""
    diz = (df["e9"] > df["e21"]) & (df["e21"] > df["e50"]) & (df["Close"] > df["e21"])
    tetik = diz & (~diz.shift(1).fillna(False)) & (df["relVol"] >= HACIM_ESIK)
    girisler = []
    for t in df.index[tetik.fillna(False)]:
        if t in rejim.index and rejim.loc[t] == "ON":
            i = df.index.get_loc(t)
            def ileri(n):
                return float(df["Close"].iloc[i+n] / df["Close"].iloc[i] - 1) * 100 if i + n < len(df) else np.nan
            girisler.append({"tarih": str(t.date()), "t3": ileri(3), "t10": ileri(10)})
    return girisler


def main():
    endeks = veri_cek(ENDEKS)
    semboller = {}
    for s in SEMBOLLER:
        df = veri_cek(f"{s}.IS")
        if df is not None and len(df) > 300:
            semboller[s] = gostergeler(df)

    if endeks is None or endeks.empty:
        print("UYARI: endeks yok, esit agirlik vekili", file=sys.stderr)
        birlesik = pd.concat([d["Close"].pct_change() for d in semboller.values()], axis=1).mean(axis=1)
        endeks = pd.DataFrame({"Close": 100 * (1 + birlesik.fillna(0)).cumprod(),
                               "Volume": pd.concat([d["Volume"] for d in semboller.values()], axis=1).sum(axis=1)}).dropna()
    endeks = gostergeler(endeks)

    genislik = {}
    for t in endeks.index:
        ust, top = 0, 0
        for d in semboller.values():
            if t in d.index and not np.isnan(d.loc[t, "e50"]):
                top += 1
                ust += int(d.loc[t, "Close"] > d.loc[t, "e50"])
        genislik[t] = ust / top if top else np.nan

    rejim = rejim_seri(endeks, genislik)

    # --- Yil bazli karakter ---
    yillik = []
    for yil in range(2018, 2027):
        b, s = f"{yil}-01-01", f"{yil}-12-31"
        p = endeks.loc[b:s]
        if len(p) < 30:
            continue
        r = rejim.loc[b:s]
        flip = int((r != r.shift(1)).sum() - 1)
        poz = (r == "ON").astype(int).shift(1).fillna(1)
        g = p["Close"].pct_change().fillna(0)
        strat = float((1 + g * poz).prod() - 1) * 100
        bh = float((1 + g).prod() - 1) * 100
        def mdd(seri):
            k = (1 + seri).cumprod()
            return float(((k / k.cummax()) - 1).min() * 100)
        yillik.append({"yil": yil, "on_orani_pct": round(float((r == "ON").mean() * 100), 1),
                       "flip_sayisi": flip,
                       "vekil_getiri_pct": round(strat, 1), "al_tut_pct": round(bh, 1),
                       "vekil_maxdd_pct": round(mdd(g * poz), 1), "al_tut_maxdd_pct": round(mdd(g), 1)})

    # --- Islem bazli: P1-vekili girisler ---
    tum_girisler = []
    for s, df in semboller.items():
        for g in p1_girisleri(df.loc[ANALIZ_BAS:], rejim):
            g["sembol"] = s
            tum_girisler.append(g)
    t3 = [g["t3"] for g in tum_girisler if not np.isnan(g["t3"])]
    t10 = [g["t10"] for g in tum_girisler if not np.isnan(g["t10"])]
    def yil_grup():
        grup = {}
        for g in tum_girisler:
            y = g["tarih"][:4]
            grup.setdefault(y, []).append(g)
        return {y: {"adet": len(v),
                    "t3_isabet_pct": round(100 * np.mean([x["t3"] > 0 for x in v if not np.isnan(x["t3"])]), 1) if v else None}
                for y, v in sorted(grup.items())}

    sonuc = {
        "calisma": "IP-2 Gunluk Iskelet Karakter Haritasi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": ("Gosterge niteliginde yaklasik kopya; 15dk sistemin altkumesi. "
                           "Pozisyon boyutu kararlarina girdi olamaz (IP1 Karar K3)."),
        "evren": list(semboller.keys()),
        "yillik_karakter": yillik,
        "p1_vekili_istatistik": {
            "toplam_giris": len(tum_girisler),
            "t3_isabet_pct": round(100 * np.mean([x > 0 for x in t3]), 1) if t3 else None,
            "t3_ortalama_pct": round(float(np.mean(t3)), 2) if t3 else None,
            "t10_isabet_pct": round(100 * np.mean([x > 0 for x in t10]), 1) if t10 else None,
            "t10_ortalama_pct": round(float(np.mean(t10)), 2) if t10 else None,
            "yil_bazli": yil_grup(),
        },
    }

    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/ip2_iskelet_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"Tamamlandi: {len(semboller)} sembol, {len(tum_girisler)} P1-vekili giris.")


if __name__ == "__main__":
    main()
