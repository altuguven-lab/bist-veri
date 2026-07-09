"""
IP-1: OLAY PENCERESI CALISMASI (rejim davranisi backtest'i)
===========================================================
Amac: V151/V195'in ceviri KABUL ETMEYEN kismini degil, GUNLUK bara cevrilebilen
cekirdek REJIM iskeletini (EMA dizilimi + hacim teyitli cikis + genislik) 2023
sonrasi bes kritik epizotta test etmek. Soru "para kazanir miydi" DEGIL;
"rejim anahtari dogru gunlerde mi dondu, cikis mantigi dususlerin neresinde
konustu" sorusudur.

DURUSTLUK NOTLARI (sonuc dosyasina da yazilir):
- Bu, sistemin YAKLASIK GUNLUK KOPYASIDIR; 15dk seans-ici mantik (saat-ayarli
  hacim, bar-ici teyit, KGS'nin tam hali) burada YOKTUR.
- Evren, 2023'te de likit olan buyuk hisselerle sinirlandi (point-in-time
  savunulabilirlik); bugunku 30'luk evren BILEREK kullanilmadi.
- Parametreler V151'in ruhundan (EMA 9/21/50, hacim 20g ort, 1.3x esik)
  alindi ve bu calisma icin AYARLANMADI - ayarlanirsa calisma gecersiz olur.

Cikti: data/backtest/olay_penceresi_sonuc.json (+ ozet md)
GitHub Actions ile calistirilir (backtest.yml, elle tetikleme).
"""

import json
import os
import sys
import datetime

import numpy as np
import pandas as pd
import yfinance as yf

# --- Epizotlar: (kod, ad, baslangic, bitis, baglam) -----------------------
EPIZOTLAR = [
    ("E1", "Secim + Simsek/faiz soku", "2023-05-01", "2023-07-31",
     "28 Mayis secim, 4 Haziran Simsek atamasi, TL devaluasyonu, TCMB'nin ilk buyuk artirimi"),
    ("E2", "2023 yaz rallisi ve Ekim duzeltmesi", "2023-07-01", "2023-10-31",
     "Rasyonellesme rallisi + ilk sert duzeltme"),
    ("E3", "Mart 2024 yerel secim penceresi", "2024-02-15", "2024-05-15",
     "31 Mart yerel secimi oncesi/sonrasi; secim sonrasi banka rallisi"),
    ("E4", "Mart 2025 ic siyaset soku", "2025-02-15", "2025-05-15",
     "19 Mart 2025 soku, devre kesiciler, sonrasi toparlanma denemesi"),
    ("E5", "Haziran 2025 Israil-Iran savasi", "2025-05-15", "2025-07-31",
     "12 gun savasi (13-24 Haziran 2025), petrol soku, Hurmuz riski"),
]

# --- Evren: 2023'te de likit/mevcut buyuk hisseler (point-in-time savunulabilir)
SEMBOLLER = ["AKBNK", "GARAN", "YKBNK", "ISCTR", "THYAO",
             "TUPRS", "ASELS", "BIMAS", "EREGL", "SISE"]

ENDEKS = "XU100.IS"

# --- V151 ruhundan gunluk iskelet parametreleri (AYARLANMAZ) ---------------
EMA_H, EMA_O, EMA_Y = 9, 21, 50
HACIM_PENCERE, HACIM_ESIK = 20, 1.3
GENISLIK_ESIK = 0.4   # sembollerin bu orani EMA50 ustundeyse piyasa saglikli


def veri_cek(ticker, bas, son):
    try:
        df = yf.download(ticker, start=bas, end=son, interval="1d",
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna() if not df.empty else None
    except Exception as e:
        print(f"UYARI: {ticker} cekilemedi -> {e}", file=sys.stderr)
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


def rejim_hesapla(endeks, genislik):
    """Gunluk rejim: RISK_ON / RISK_OFF.
    OFF kosulu (V151 ruhunda): endeks e21 altinda VE (e9<e21 VEYA genislik zayif).
    ON'a donus: endeks e21 ustune kapanis VE e9>=e21."""
    rejim = []
    durum = "ON"
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


def acil_cik_taramasi(df):
    """Sembol bazli gunluk ACIL_CIK vekili: e21 alti kapanis + hacim>=1.3x + gun<-2%."""
    kosul = (df["Close"] < df["e21"]) & (df["relVol"] >= HACIM_ESIK) & (df["gunluk"] < -2.0)
    return df.index[kosul.fillna(False)]


def epizot_analiz(kod, ad, bas, son, baglam, endeks_all, sembol_all):
    # Gosterge isinmasi icin pencereden 100 gun once veri gerekir; dilimle
    e = endeks_all.loc[:son].copy()
    pencere = e.loc[bas:son]
    if len(pencere) < 10:
        return {"kod": kod, "ad": ad, "hata": "yetersiz veri"}

    # Genislik: her gun EMA50 ustundeki sembol orani
    genislik = {}
    for t in e.index:
        ustunde, toplam = 0, 0
        for s, df in sembol_all.items():
            if t in df.index and not np.isnan(df.loc[t, "e50"]):
                toplam += 1
                if df.loc[t, "Close"] > df.loc[t, "e50"]:
                    ustunde += 1
        genislik[t] = ustunde / toplam if toplam else np.nan

    rejim = rejim_hesapla(e, genislik)

    # Pencere ici: endeks zirve/dip, rejimin dondugu gunler
    p_close = pencere["Close"]
    zirve_t, dip_t = p_close.idxmax(), p_close.idxmin()
    dd = (p_close.min() / p_close.max() - 1) * 100

    r_pencere = rejim.loc[bas:son]
    donusler = []
    for i in range(1, len(r_pencere)):
        if r_pencere.iloc[i] != r_pencere.iloc[i-1]:
            donusler.append({"tarih": str(r_pencere.index[i].date()),
                             "yeni_durum": r_pencere.iloc[i],
                             "endeks": round(float(p_close.reindex(r_pencere.index).iloc[i]), 1)})

    # Strateji vekili: rejim ON iken endekste long, OFF iken nakit (bir gun gecikmeli)
    pozisyon = (r_pencere == "ON").astype(int).shift(1).fillna(1)
    gunluk_getiri = p_close.pct_change().fillna(0)
    strat = (1 + gunluk_getiri * pozisyon).prod() - 1
    bh = (1 + gunluk_getiri).prod() - 1

    def max_dd(seri):
        kum = (1 + seri).cumprod()
        return float(((kum / kum.cummax()) - 1).min() * 100)

    # Sembol bazli ACIL_CIK vekil sinyalleri (pencere ici)
    cikislar = {}
    for s, df in sembol_all.items():
        gunler = [str(t.date()) for t in acil_cik_taramasi(df.loc[bas:son])]
        if gunler:
            cikislar[s] = gunler

    return {
        "kod": kod, "ad": ad, "baglam": baglam,
        "pencere": f"{bas} / {son}",
        "endeks_zirve": {"tarih": str(zirve_t.date()), "deger": round(float(p_close.max()), 1)},
        "endeks_dip": {"tarih": str(dip_t.date()), "deger": round(float(p_close.min()), 1)},
        "pencere_max_drawdown_pct": round(dd, 2),
        "rejim_donusleri": donusler,
        "strateji_vekili": {
            "aciklama": "ON=endeks long, OFF=nakit, 1 gun gecikmeli",
            "strateji_getiri_pct": round(float(strat) * 100, 2),
            "al_tut_getiri_pct": round(float(bh) * 100, 2),
            "strateji_maxdd_pct": round(max_dd(gunluk_getiri * pozisyon), 2),
            "al_tut_maxdd_pct": round(max_dd(gunluk_getiri), 2),
        },
        "acil_cik_vekil_gunleri": cikislar,
    }


def main():
    bas_genel = "2022-10-01"  # isinme payi
    son_genel = "2026-07-09"

    endeks = veri_cek(ENDEKS, bas_genel, son_genel)
    sembol_all = {}
    for s in SEMBOLLER:
        df = veri_cek(f"{s}.IS", bas_genel, son_genel)
        if df is not None and len(df) > 100:
            sembol_all[s] = gostergeler(df)

    if endeks is None or endeks.empty:
        # Endeks yoksa esit agirlikli sepetten vekil endeks kur
        print("UYARI: XU100 cekilemedi, esit agirlikli sepet vekili kullaniliyor", file=sys.stderr)
        birlesik = pd.concat([d["Close"].pct_change() for d in sembol_all.values()], axis=1).mean(axis=1)
        fiyat = 100 * (1 + birlesik.fillna(0)).cumprod()
        hacim = pd.concat([d["Volume"] for d in sembol_all.values()], axis=1).sum(axis=1)
        endeks = pd.DataFrame({"Close": fiyat, "Volume": hacim}).dropna()

    endeks = gostergeler(endeks)

    sonuc = {
        "calisma": "IP-1 Olay Penceresi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": ("Bu sonuclar 15dk sistemin GUNLUK YAKLASIK KOPYASINA aittir; "
                           "getiri iddiasi degil, rejim-davranis haritasidir. Parametreler "
                           "bu calisma icin ayarlanmamistir."),
        "evren": SEMBOLLER,
        "veri_kapsami": {s: [str(d.index.min().date()), str(d.index.max().date())] for s, d in sembol_all.items()},
        "epizotlar": [epizot_analiz(*e, endeks, sembol_all) for e in EPIZOTLAR],
    }

    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/olay_penceresi_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"Tamamlandi: {len(sonuc['epizotlar'])} epizot, {len(sembol_all)} sembol.")


if __name__ == "__main__":
    main()
