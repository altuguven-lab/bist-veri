"""
SERT DUSUS SONRASI TOPARLANMA TESTI v2 (23.10.2026) - SALT OLCUM, Pine'a dokunmaz.
Soru: BIST'te gecmis sert dususlerden sonraki ilk toparlanmayi, dususte en cok kaybeden /
      yuksek betali hisseler mi cekti?
Girdi : config/bist100_uyeler.txt (bugunku uyeler -> hayatta kalma yanliligi VAR, raporda yazilir)
        config/bist50_uyeler.txt varsa her hisseye bist50=True/False etiketi
        config/fon_krizi_baglantili.txt varsa fon_krizi=True etiketi
Cikti : data/toparlanma_testi.json
Yontem:
  1) XU100 10 yillik gunluk kapanis. Epizot = kapanisin onceki 60 islem gunu zirvesinden
     en az ESIK (%15) dustugu bolge. v2: dip, endeks bolge icindeki en dusuk kapanistan %15
     toparlanana (veya 250 gun dolana) kadar aranir; v1 sabit 60 gunluk pencere kullaniyordu ve
     2018'de Agustos kur sokunu disarida birakip dibi erken isaretliyordu. Epizotlar arasi en az 120 gun.
     Fiyat bazli kapanis (auto_adjust=False): XU100 fiyat endeksiyle tutarli, temettu haric.
     Zirve = dipten onceki 60 gunun en yuksek kapanisi. Dip ex-post belirlenir (gercek zamanda bilinmez).
  2) Her epizot ve hisse icin: dusus (zirve->dip), beta (zirveden onceki 252 gun),
     toparlanma T+10/T+20/T+60 (dipten sonra), XU100'e gore fark.
  3) Epizot bazinda Spearman korelasyonu (dusus ~ toparlanma, beta ~ toparlanma) ve
     dusus besliklerinde (en cok dusen %20 - en az dusen %20) toparlanma farki.
  4) Havuz OLS: rel_T20 = a + b*dusus_rel + c*beta ; bugunku durum icin ayni degiskenler.
"""
import json, os, datetime, math
import numpy as np
import pandas as pd
import yfinance as yf
from ma610_tarama import bolunme_duzelt

ESIK = float(os.environ.get("ESIK", "0.15"))
PENCERE = 60
ARA = 120
UFUK = (10, 20, 60)


def oku_liste(yol):
    if not os.path.exists(yol):
        return None
    out = []
    for s in open(yol, encoding="utf-8"):
        s = s.split("#")[0].strip().upper().replace(".IS", "")
        if s and s not in out:
            out.append(s)
    return out


def seri(kod, tam=False):
    df = yf.Ticker(kod).history(period="10y", interval="1d", auto_adjust=False)
    df = df[df["Close"] > 0].dropna(subset=["Close"])
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df if tam else df["Close"]


def epizotlar(x):
    dd = (x / x.rolling(PENCERE, min_periods=20).max() - 1).values
    secilen, i, n = [], 0, len(x)
    while i < n:
        if dd[i] <= -ESIK:
            # dip: en dusuk kapanistan %15 toparlanana ya da 250 gun dolana kadar ara
            j, p = i, i
            while j < n and j - i <= 250:
                if x.values[j] < x.values[p]:
                    p = j
                elif x.values[j] >= x.values[p] * (1 + ESIK):
                    break
                j += 1
            if p + max(UFUK) >= n:                              # sonrasi yetersiz: bugunku epizot, test disi
                break
            z0 = max(0, i - PENCERE)                             # zirve: tetik oncesi 60 gun ile dip arasi
            z = z0 + int(np.argmax(x.values[z0:p + 1]))
            secilen.append({"zirve": x.index[z], "dip": x.index[p],
                            "xu_dusus": round((x.iloc[p] / x.iloc[z] - 1) * 100, 2)})
            i = p + ARA
        else:
            i += 1
    return secilen


def getiri(c, t0, t1):
    a, b = c[c.index <= t0], c[c.index <= t1]
    if a.empty or b.empty or a.index[-1] < t0 - pd.Timedelta(days=7):
        return None
    return (b.iloc[-1] / a.iloc[-1] - 1) * 100


def beta(c, x, son, n=252):
    g = pd.concat([c.pct_change(), x.pct_change()], axis=1, join="inner").dropna()
    g = g[g.index <= son].iloc[-n:]
    if len(g) < 100 or g.iloc[:, 1].var() == 0:
        return None
    return float(g.iloc[:, 0].cov(g.iloc[:, 1]) / g.iloc[:, 1].var())


def spearman(a, b):
    d = pd.DataFrame({"a": a, "b": b}).dropna()
    if len(d) < 15:
        return None, len(d)
    return round(float(d["a"].rank().corr(d["b"].rank())), 3), len(d)


def main():
    uyeler = oku_liste("config/bist100_uyeler.txt")
    b50 = set(oku_liste("config/bist50_uyeler.txt") or [])
    fon = set(oku_liste("config/fon_krizi_baglantili.txt") or [])
    kd = set(oku_liste("config/kapsam_disi.txt") or [])
    x = seri("XU100.IS")
    xg = float(x.pct_change().abs().max())
    if xg > 0.25:   # endeks serisinde kirilma (or. 2020 iki sifir) -> duzelt
        x, _ = bolunme_duzelt(x)
    xi = list(x.index)
    eps = epizotlar(x)
    veri, hata = {}, []
    for k in uyeler:
        try:
            df = seri(k + ".IS", tam=True)
            c, _ = bolunme_duzelt(df["Close"])
            veri[k] = {"c": c, "tl_hacim_60": float((df["Close"] * df["Volume"]).iloc[-60:].mean())}
        except Exception as e:
            hata.append({"kod": k, "neden": str(e)[:150]})

    havuz, ep_ozet = [], []
    for e in eps:
        p = xi.index(e["dip"])
        satir = []
        for k, v in veri.items():
            c = v["c"]
            d = getiri(c, e["zirve"], e["dip"])
            if d is None:
                continue
            r = {"kod": k, "dusus": d, "beta": beta(c, x, e["zirve"])}
            for h in UFUK:
                t1 = xi[p + h]
                g = getiri(c, e["dip"], t1)
                gx = (x[t1] / x[e["dip"]] - 1) * 100
                r[f"T{h}"] = g
                r[f"rel_T{h}"] = None if g is None else g - gx
            r["dusus_rel"] = d - e["xu_dusus"]
            satir.append(r)
        df = pd.DataFrame(satir)
        oz = {"zirve": str(e["zirve"].date()), "dip": str(e["dip"].date()), "xu_dusus": e["xu_dusus"],
              "hisse_sayisi": len(df)}
        for h in UFUK:
            oz[f"xu_T{h}"] = round((x[xi[p + h]] / x[e["dip"]] - 1) * 100, 2)
        if len(df) >= 15:
            for h in UFUK:
                oz[f"spearman_dusus_T{h}"], _ = spearman(df["dusus"], df[f"T{h}"])
                oz[f"spearman_beta_T{h}"], _ = spearman(df["beta"], df[f"T{h}"])
            q = df["dusus"].quantile([0.2, 0.8])
            cok = df[df["dusus"] <= q[0.2]]
            az = df[df["dusus"] >= q[0.8]]
            for h in UFUK:
                oz[f"en_cok_dusen20_T{h}"] = round(float(cok[f"T{h}"].mean()), 2)
                oz[f"en_az_dusen20_T{h}"] = round(float(az[f"T{h}"].mean()), 2)
            oz["ilk10_T20"] = [[r["kod"], round(r["T20"], 1), round(r["dusus"], 1)]
                               for r in df.dropna(subset=["T20"]).sort_values("T20", ascending=False).head(10).to_dict("records")]
            havuz += [dict(r, epizot=oz["dip"]) for r in satir]
        ep_ozet.append(oz)

    # havuz OLS: rel_T20 ~ dusus_rel + beta
    H = pd.DataFrame(havuz).dropna(subset=["rel_T20", "dusus_rel", "beta"]) if havuz else pd.DataFrame()
    model = None
    if len(H) >= 50:
        X = np.column_stack([np.ones(len(H)), H["dusus_rel"], H["beta"]])
        y = H["rel_T20"].values
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ coef
        r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
        model = {"sabit": round(float(coef[0]), 3), "b_dusus_rel": round(float(coef[1]), 4), "c_beta": round(float(coef[2]), 3),
                 "r2": round(float(r2), 3), "n": int(len(H)),
                 "yorum": "b_dusus_rel < 0 ise: endeksten fazla dusen hisse T+20'de endeksten fazla toparlanmis."}

    # bugun: kriz oncesi referanstan (varsayilan 15.09.2026) bugune
    kr = pd.Timestamp(os.environ.get("KRIZ_ONCESI", "2026-09-15"))
    zt = x[x.index <= kr].index[-1]
    xu_simdi = (x.iloc[-1] / x[zt] - 1) * 100
    simdi = []
    for k, v in veri.items():
        c = v["c"]
        d = getiri(c, zt, x.index[-1])
        if d is None:
            continue
        b = beta(c, x, x.index[-1])
        r = {"kod": k, "dusus_zirveden": round(d, 2), "dusus_rel": round(d - xu_simdi, 2),
             "beta_1y": None if b is None else round(b, 2), "tl_hacim_60_mn": round(v["tl_hacim_60"] / 1e6, 1),
             "bist50": (k in b50) if b50 else None, "fon_krizi": k in fon, "kapsam_disi": k in kd}
        if model and b is not None:
            r["model_rel_T20"] = round(model["sabit"] + model["b_dusus_rel"] * r["dusus_rel"] + model["c_beta"] * b, 2)
        simdi.append(r)
    simdi.sort(key=lambda r: -(r.get("model_rel_T20") if r.get("model_rel_T20") is not None else -999))

    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "esik": ESIK, "surum": "v2", "xu100_en_buyuk_gunluk_degisim_pct": round(xg * 100, 2),
           "kriz_oncesi_referans": str(zt.date()), "xu100_zirveden_dusus": round(xu_simdi, 2),
           "epizotlar": ep_ozet, "havuz_model": model, "bugun": simdi, "hata": hata,
           "uyari": ["Hayatta kalma yanliligi: bugunku BIST 100 uyeleri gecmise uygulandi.",
                     "Dip ex-post belirlenir; gercek zamanda dibi bilmek mumkun degildir.",
                     "Salt olcum; yon tahmini veya tavsiye degildir."]}
    os.makedirs("data", exist_ok=True)
    json.dump(out, open("data/toparlanma_testi.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("Epizot:", len(ep_ozet))
    for o in ep_ozet:
        print(o["zirve"], "->", o["dip"], o["xu_dusus"], "| rho dusus~T20", o.get("spearman_dusus_T20"),
              "| cok dusen T20", o.get("en_cok_dusen20_T20"), "az dusen", o.get("en_az_dusen20_T20"))
    print("Model:", model)


if __name__ == "__main__":
    main()
