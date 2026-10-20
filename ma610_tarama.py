"""
610 GUNLUK ORTALAMA TARAMASI (20.10.2026) - SALT OLCUM, Pine'a dokunmaz.
Girdi : config/bist100_uyeler.txt  (her satirda bir kod, '#' yorum; .IS yazilmaz)
Cikti : data/ma610_tarama.json + data/ma610_tarama.md
Yontem: gunluk kapanis, BASIT hareketli ortalama (SMA) son 610 islem gunu.
        yfinance auto_adjust=True (bolunme/temettu duzeltmeli kapanis) - TradingView'in
        ayarsiz grafigiyle kucuk sapma olabilir, ozellikle temettu/bedelsiz sonrasi.
        610 bar yoksa hisse 'YETERSIZ_VERI' sayilir, listeye KATILMAZ (sessizce atlanmaz).
Parametre: MA_PERIYOT=610 (ortam degiskeni), MA_TIP=SMA|EMA
"""
import json, os, sys, datetime
import pandas as pd
import yfinance as yf

N = int(os.environ.get("MA_PERIYOT", "610"))
TIP = os.environ.get("MA_TIP", "SMA").upper()
UYE_YOL = "config/bist100_uyeler.txt"

def uyeler():
    out = []
    with open(UYE_YOL, encoding="utf-8") as f:
        for s in f:
            s = s.split("#")[0].strip().upper().replace(".IS", "")
            if s and s not in out:
                out.append(s)
    return out

def seri(kod):
    df = yf.Ticker(kod + ".IS").history(period="6y", interval="1d", auto_adjust=True)
    c = df["Close"].dropna()
    c = c[c > 0]
    return c

def main():
    kodlar = uyeler()
    alti, ustu, yetersiz, hata = [], [], [], []
    for k in kodlar:
        try:
            c = seri(k)
        except Exception as e:
            hata.append({"kod": k, "hata": str(e)[:120]}); continue
        if len(c) < N:
            yetersiz.append({"kod": k, "bar": int(len(c))}); continue
        ma = c.rolling(N).mean() if TIP == "SMA" else c.ewm(span=N, adjust=False).mean()
        son, m = float(c.iloc[-1]), float(ma.iloc[-1])
        kayit = {"kod": k, "kapanis": round(son, 2), "ma": round(m, 2),
                 "sapma_pct": round((son / m - 1) * 100, 2), "son_bar": str(c.index[-1].date())}
        (alti if son < m else ustu).append(kayit)
    alti.sort(key=lambda r: r["sapma_pct"])
    ustu.sort(key=lambda r: r["sapma_pct"])
    sonuc = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "ma": f"{TIP}{N}", "uye_sayisi": len(kodlar),
             "ma_alti_sayisi": len(alti), "ma_ustu_sayisi": len(ustu),
             "yetersiz_veri": yetersiz, "hata": hata, "ma_alti": alti, "ma_ustu": ustu}
    os.makedirs("data", exist_ok=True)
    with open("data/ma610_tarama.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)
    sat = [f"# {TIP}{N} taramasi", f"Uye: {len(kodlar)} | Altinda: {len(alti)} | Ustunde: {len(ustu)} | "
           f"Yetersiz veri: {len(yetersiz)} | Hata: {len(hata)}", "",
           "## Ortalamanin ALTINDA (en derin once)", "| Kod | Kapanis | MA | Sapma % | Son bar |", "|---|---|---|---|---|"]
    sat += [f"| {r['kod']} | {r['kapanis']} | {r['ma']} | {r['sapma_pct']} | {r['son_bar']} |" for r in alti]
    if yetersiz: sat += ["", "Yetersiz veri (<%d bar): " % N + ", ".join(f"{r['kod']}({r['bar']})" for r in yetersiz)]
    if hata: sat += ["", "Cekilemedi: " + ", ".join(r["kod"] for r in hata)]
    sat += ["", "Gozlem ve olcumdur, yatirim tavsiyesi degildir."]
    open("data/ma610_tarama.md", "w", encoding="utf-8").write("\n".join(sat) + "\n")
    print("\n".join(sat))

if __name__ == "__main__":
    main()
