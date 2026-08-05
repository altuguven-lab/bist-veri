"""
VOLATILITE - PF/DD/WR KORELASYON ANALIZI (05.08.2026) - Faz V0
Kurul hipotezi: P1/P2'nin "EMA dizilim dogusu" mantigi, yuksek/net-trendli
volatiliteye sahip hisselerde mi daha iyi calisiyor? SALT OLCUM - Pine'a
hic dokunmuyor, gunluk (daily) veri kullaniyor (intraday'in 60 gunluk
kisitindan bagimsiz, yillarca geriye gidebiliyor).

PF/DD/WR/N degerleri, kullanicinin V151/V156 panelinden ELLE okuyup
bildirdigi degerler (_v112Total/_v112Wr/_v112Pf/_v112MaxDd) - script'in
KENDI tum-tarihsel performans ozeti. Bu script yalniz volatilite tarafini
hesaplayip, panel verisiyle ESLESTIRIYOR.
"""
import json, datetime, os, sys
import yfinance as yf

# Panelden elle okunan veri (05.08.2026) - N=islem sayisi, WR=kazanma
# orani (%), PF=kar faktoru, DD=maksimum dusus (%)
PANEL_VERISI = {
    "AKBNK": {"n": 80,  "wr": 39, "pf": 1.5, "dd": 14.0},
    "YKBNK": {"n": 82,  "wr": 38, "pf": 1.2, "dd": 22.6},
    "KCHOL": {"n": 149, "wr": 40, "pf": 1.5, "dd": 15.5},
    "TAVHL": {"n": 164, "wr": 37, "pf": 1.4, "dd": 16.3},
    "ASTOR": {"n": 244, "wr": 45, "pf": 2.0, "dd": 11.8},
    "TUPRS": {"n": 49,  "wr": 37, "pf": 1.4, "dd": 28.6},
    "GARAN": {"n": 98,  "wr": 36, "pf": 1.0, "dd": 14.4},
    "HALKB": {"n": 174, "wr": 36, "pf": 1.4, "dd": 32.7},
    "VAKBN": {"n": 165, "wr": 33, "pf": 1.1, "dd": 18.4},
    "EREGL": {"n": 100, "wr": 47, "pf": 1.9, "dd": 7.6},
    "ASELS": {"n": 317, "wr": 42, "pf": 1.7, "dd": 14.6},
    "TRALT": {"n": 235, "wr": 34, "pf": 1.5, "dd": 24.8},
    "BIMAS": {"n": 234, "wr": 35, "pf": 1.2, "dd": 18.8},
    "PETKM": {"n": 160, "wr": 39, "pf": 1.5, "dd": 28.8},
    "MGROS": {"n": 223, "wr": 38, "pf": 1.0, "dd": 21.8},
}
GECMIS_PERIYOD = "2y"  # gunluk veri - yillarca geriye gidebilir
CIKTI = "data/backtest/volatilite_korelasyon_sonuc.json"


def volatilite_hesapla(sembol):
    df = yf.Ticker(f"{sembol}.IS").history(period=GECMIS_PERIYOD)
    if df.empty or len(df) < 30:
        return None
    getiriler = df["Close"].pct_change().dropna()
    gunluk_getiri_std_pct = round(getiriler.std() * 100, 3)
    gunluk_araligi_pct = ((df["High"] - df["Low"]) / df["Close"] * 100)
    ort_gunluk_aralik_pct = round(gunluk_araligi_pct.mean(), 3)
    return {"gunluk_getiri_std_pct": gunluk_getiri_std_pct,
            "ort_gunluk_aralik_pct": ort_gunluk_aralik_pct,
            "bar_sayisi": len(df)}


def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    kov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    vx = sum((a - mx) ** 2 for a in x)
    vy = sum((b - my) ** 2 for b in y)
    if vx <= 0 or vy <= 0:
        return None
    return round(kov / (vx ** 0.5 * vy ** 0.5), 3)


def main():
    birlesik = {}
    for sembol, panel in PANEL_VERISI.items():
        try:
            vol = volatilite_hesapla(sembol)
            if vol is None:
                print(f"UYARI: {sembol} icin veri yok", file=sys.stderr)
                continue
            birlesik[sembol] = {**panel, **vol}
            print(f"{sembol}: getiri_std=%{vol['gunluk_getiri_std_pct']}, "
                  f"aralik=%{vol['ort_gunluk_aralik_pct']}, PF={panel['pf']}")
        except Exception as e:
            print(f"HATA: {sembol} -> {e}", file=sys.stderr)

    # korelasyonlar: iki volatilite metrigi x uc panel metrigi (PF/DD/WR)
    korelasyonlar = {}
    for vol_metrik in ("gunluk_getiri_std_pct", "ort_gunluk_aralik_pct"):
        for panel_metrik in ("pf", "dd", "wr"):
            x = [v[vol_metrik] for v in birlesik.values()]
            y = [v[panel_metrik] for v in birlesik.values()]
            korelasyonlar[f"{vol_metrik}_vs_{panel_metrik}"] = pearson(x, y)

    sonuc = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 - volatilite ile PF/DD/WR korelasyonu, SALT OLCUM. "
                "Panel verisi 05.08.2026'da elle okundu, gunluk fiyat "
                f"verisi son {GECMIS_PERIYOD} - Pearson korelasyon katsayilari "
                "-1 ile +1 arasi (0'a yakin = iliski yok)."),
        "sembol_verisi": birlesik,
        "korelasyonlar": korelasyonlar,
    }
    os.makedirs("data/backtest", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"\nYazildi: {CIKTI}")
    print("\nKORELASYONLAR:")
    for k, v in korelasyonlar.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
