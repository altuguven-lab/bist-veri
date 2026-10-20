"""
610 GUNLUK ORTALAMA TARAMASI (20.10.2026) - SALT OLCUM, Pine'a dokunmaz.
Girdi : config/bist100_uyeler.txt  (her satirda bir kod, '#' yorum; .IS yazilmaz)
Cikti : data/ma610_tarama.json + data/ma610_tarama.md
v2 (20.10): duzeltilmemis bolunme/bedelsiz tespiti ve yaklasik duzeltme eklendi (bolunme_duzelt).
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

ESIK_DUSUS = 0.85   # BIST gunluk fiyat siniri ~%10: tek gunde %15'ten buyuk kapanis dususu = duzeltilmemis bolunme/bedelsiz

def seri(kod):
    df = yf.Ticker(kod + ".IS").history(period="6y", interval="1d", auto_adjust=True)
    c = df["Close"].dropna()
    c = c[c > 0]
    return c

def bolunme_duzelt(c):
    """Yahoo bedelsizleri bazen DUZELTMIYOR (SASA, FENER...). Tek gunde <%85 kapanis oranini
    duzeltilmemis bolunme sayar, oncesini bu carpanla boler. YAKLASIKTIR: o gunun gercek
    fiyat hareketi (en fazla ~%10) carpana karisir. Donus: (duzeltilmis seri, [(tarih, carpan)])"""
    c = c.copy()
    olaylar = []
    oran = c / c.shift(1)
    for t in list(oran.index[oran < ESIK_DUSUS]):
        f = float(c.shift(1)[t] / c[t])
        c[c.index < t] = c[c.index < t] / f
        olaylar.append((str(t.date()), round(f, 2)))
    return c, olaylar

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
        def ort(x): return x.rolling(N).mean() if TIP == "SMA" else x.ewm(span=N, adjust=False).mean()
        son, m_ham = float(c.iloc[-1]), float(ort(c).iloc[-1])
        cd, olaylar = bolunme_duzelt(c)
        m = float(ort(cd).iloc[-1])
        kayit = {"kod": k, "kapanis": round(son, 2), "ma": round(m, 2),
                 "sapma_pct": round((son / m - 1) * 100, 2),
                 "ma_ham": round(m_ham, 2), "sapma_ham_pct": round((son / m_ham - 1) * 100, 2),
                 "bolunme_olaylari": olaylar, "son_bar": str(c.index[-1].date())}
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
           "## Ortalamanin ALTINDA (en derin once)", "| Kod | Kapanis | MA (duzeltilmis) | Sapma % | Ham sapma % | Bolunme/bedelsiz (tarih x carpan) |", "|---|---|---|---|---|---|"]
    sat += [f"| {r['kod']} | {r['kapanis']} | {r['ma']} | {r['sapma_pct']} | {r['sapma_ham_pct']} | "
            + (", ".join(f"{d} x{f}" for d, f in r['bolunme_olaylari']) or "-") + " |" for r in alti]
    if yetersiz: sat += ["", "Yetersiz veri (<%d bar): " % N + ", ".join(f"{r['kod']}({r['bar']})" for r in yetersiz)]
    if hata: sat += ["", "Cekilemedi: " + ", ".join(r["kod"] for r in hata)]
    sat += ["", "Gozlem ve olcumdur, yatirim tavsiyesi degildir."]
    open("data/ma610_tarama.md", "w", encoding="utf-8").write("\n".join(sat) + "\n")
    print("\n".join(sat))

if __name__ == "__main__":
    main()
