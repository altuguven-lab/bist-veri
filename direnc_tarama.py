"""
FON KRIZI DIRENC TARAMASI (23.10.2026) - SALT OLCUM, Pine'a dokunmaz.
Girdi : config/bist100_uyeler.txt, data/viop_hisse_gunluk.json (varsa)
Cikti : data/direnc_tarama.json + data/direnc_tarama.csv
Yontem: yfinance gunluk kapanis (auto_adjust=True) + ma610_tarama.bolunme_duzelt ile
        duzeltilmemis bedelsiz tespiti. Endeks referansi XU100.IS.
Olculer (hepsi %):
  r_2y, r_1y, r_1a      : 504 / 252 / 21 islem gunu getiri
  r_ytd                 : 2025 son kapanisina gore
  r_kriz                : KRIZ_ONCESI (15.09.2026) kapanisina gore son kapanis
  dd_kriz               : 15.09 sonrasi en dusuk kapanis / 15.09 kapanis - 1
  dipten                : son / kriz sonrasi dip - 1
  *_rel                 : ayni olcu eksi XU100 (puan)
  vol_1y                : yillik oynaklik (gunluk getiri std * sqrt(252))
  beta_1y               : 252 gunluk XU100'e gore beta
  viop_oi_tl_degisim    : VIOP acik pozisyon (TL) 15.09 -> son gun degisimi (varsa)
Direnc skoru: r_kriz_rel, dd_kriz_rel, r_1a_rel, r_1y_rel, r_2y_rel siralamalarinin
  ortalamasi (0-100, yuksek = daha direncli). Agirliklar asagida; YON TAHMINI DEGILDIR.
Parametre: KRIZ_ONCESI=2026-09-15 (ortam degiskeni)
"""
import json, os, datetime, math
import pandas as pd
import yfinance as yf
from ma610_tarama import uyeler, bolunme_duzelt

KRIZ = pd.Timestamp(os.environ.get("KRIZ_ONCESI", "2026-09-15"))
YIL_SONU = pd.Timestamp("2025-12-31")
AGIRLIK = {"r_kriz_rel": 0.30, "dd_kriz_rel": 0.20, "r_1a_rel": 0.20, "r_1y_rel": 0.15, "r_2y_rel": 0.15}


def seri(kod):
    df = yf.Ticker(kod).history(period="3y", interval="1d", auto_adjust=True)
    c = df["Close"].dropna()
    c = c[c > 0]
    c.index = pd.to_datetime(c.index).tz_localize(None).normalize()
    return c


def getiri(c, n):
    if len(c) <= n:
        return None
    return round((c.iloc[-1] / c.iloc[-1 - n] - 1) * 100, 2)


def tarihte(c, t):
    s = c[c.index <= t]
    return None if s.empty else float(s.iloc[-1])


def olc(c, x=None):
    o = {"son_bar": str(c.index[-1].date()), "kapanis": round(float(c.iloc[-1]), 4), "bar": len(c),
         "r_2y": getiri(c, 504), "r_1y": getiri(c, 252), "r_1a": getiri(c, 21)}
    ys = tarihte(c, YIL_SONU)
    o["r_ytd"] = round((c.iloc[-1] / ys - 1) * 100, 2) if ys else None
    k0 = tarihte(c, KRIZ)
    sonra = c[c.index > KRIZ]
    if k0 and not sonra.empty:
        dip = float(sonra.min())
        o["r_kriz"] = round((c.iloc[-1] / k0 - 1) * 100, 2)
        o["dd_kriz"] = round((dip / k0 - 1) * 100, 2)
        o["dipten"] = round((c.iloc[-1] / dip - 1) * 100, 2)
        o["dip_tarih"] = str(sonra.idxmin().date())
    else:
        o["r_kriz"] = o["dd_kriz"] = o["dipten"] = None
    g = c.pct_change().dropna().iloc[-252:]
    o["vol_1y"] = round(float(g.std() * math.sqrt(252) * 100), 1) if len(g) > 50 else None
    if x is not None:
        gx = x.pct_change().dropna()
        j = pd.concat([g, gx], axis=1, join="inner").dropna().iloc[-252:]
        if len(j) > 50 and j.iloc[:, 1].var() > 0:
            o["beta_1y"] = round(float(j.iloc[:, 0].cov(j.iloc[:, 1]) / j.iloc[:, 1].var()), 2)
        else:
            o["beta_1y"] = None
    return o


def viop_oi():
    yol = "data/viop_hisse_gunluk.json"
    if not os.path.exists(yol):
        return {}, None
    g = json.load(open(yol, encoding="utf-8")).get("gunler", {})
    ds = sorted(g)
    onc = [d for d in ds if d <= str(KRIZ.date())]
    if not onc or not ds:
        return {}, None
    b, s = onc[-1], ds[-1]
    out = {}
    for kod, v in g[s].items():
        v0 = g[b].get(kod)
        if v0 and v0.get("oi_tl"):
            out[kod] = {"viop_oi_tl_degisim": round((v["oi_tl"] / v0["oi_tl"] - 1) * 100, 1),
                        "viop_uzlasma_kriz": round((v["uzlasma"] / v0["uzlasma"] - 1) * 100, 2),
                        "viop_takvim_faizi": v.get("takvim_faizi_yillik_pct")}
    return out, (b, s)


def yuzdelik(degerler):
    v = [(k, x) for k, x in degerler.items() if x is not None]
    v.sort(key=lambda t: t[1])
    n = len(v)
    return {k: (100.0 * i / (n - 1) if n > 1 else 50.0) for i, (k, _) in enumerate(v)}


def main():
    x = seri("XU100.IS")
    xo = olc(x)
    viop, viop_gun = viop_oi()
    satir, hata = [], []
    for kod in uyeler():
        try:
            c, olay = bolunme_duzelt(seri(kod + ".IS"))
            if len(c) < 30:
                hata.append({"kod": kod, "neden": "az veri", "bar": len(c)})
                continue
            o = {"kod": kod, **olc(c, x), "bolunme_olaylari": [[str(t.date()) if hasattr(t, "date") else str(t), r] for t, r in olay]}
            for k in ("r_2y", "r_1y", "r_1a", "r_ytd", "r_kriz", "dd_kriz"):
                o[k + "_rel"] = round(o[k] - xo[k], 2) if o.get(k) is not None and xo.get(k) is not None else None
            o.update(viop.get(kod, {}))
            satir.append(o)
        except Exception as e:  # sessizce atlanmaz, listelenir
            hata.append({"kod": kod, "neden": str(e)[:160]})
    # direnc skoru
    yz = {k: yuzdelik({s["kod"]: s.get(k) for s in satir}) for k in AGIRLIK}
    for s in satir:
        top = ag = 0.0
        for k, w in AGIRLIK.items():
            if s["kod"] in yz[k]:
                top += w * yz[k][s["kod"]]
                ag += w
        s["direnc_skoru"] = round(top / ag, 1) if ag else None
        s["direnc_olcu_kapsami"] = round(ag, 2)
    satir.sort(key=lambda s: -(s["direnc_skoru"] or -1))
    for i, s in enumerate(satir, 1):
        s["sira"] = i
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "kriz_oncesi_referans": str(KRIZ.date()), "agirliklar": AGIRLIK,
           "viop_gunleri": viop_gun, "xu100": xo, "uye_sayisi": len(satir), "hata": hata,
           "not": "Salt olcum. Direnc skoru gecmis goreli fiyat davranisidir; yon tahmini veya tavsiye degildir. "
                  "Seans icinde calisirsa son bar anliktir.",
           "satirlar": satir}
    os.makedirs("data", exist_ok=True)
    json.dump(out, open("data/direnc_tarama.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    kol = ["sira", "kod", "direnc_skoru", "r_kriz", "r_kriz_rel", "dd_kriz", "dipten", "r_1a", "r_1a_rel",
           "r_1y", "r_1y_rel", "r_2y", "r_2y_rel", "r_ytd", "vol_1y", "beta_1y", "viop_oi_tl_degisim",
           "viop_takvim_faizi", "kapanis", "son_bar"]
    pd.DataFrame(satir).reindex(columns=kol).to_csv("data/direnc_tarama.csv", index=False)
    print(f"XU100 kriz {xo.get('r_kriz')}% 1a {xo.get('r_1a')}% 1y {xo.get('r_1y')}% 2y {xo.get('r_2y')}%")
    print(f"{len(satir)} hisse, {len(hata)} hata. Ilk 15:")
    for s in satir[:15]:
        print(s["sira"], s["kod"], s["direnc_skoru"], s.get("r_kriz_rel"), s.get("r_1y_rel"), s.get("r_2y_rel"))


if __name__ == "__main__":
    main()
