"""
H8 KESIF BATARYASI (30.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H8.md (bu betikten ONCE commit edilir). 15 test, tek aile, Benjamini-Hochberg q=0.10.
Cikti : data/h8/sonuc.json, data/h8/sonuc.md, data/h8/deneme_kaydi.json
"""
import os, json, math, datetime
import numpy as np
import pandas as pd

from alarm_karne import kumelenmis
from h_testleri import panel_kur, newey_west, sha256
from h4_bilanco_surprizi import liste_oku, SEKTOR100
from h6_faktor_siralama import temel_tablo

ON_KAYIT = "ON_KAYIT_H8.md"
CIKTI = "data/h8"
MALIYET = 0.25
DILIM = 0.20
MIN_SIRALI = 30
BH_Q = 0.10
X_IS, X_OOS = ("2016-01", "2022-12"), ("2023-01", "2026-06")
T_IS, T_OOS = ("2006-01", "2017-12"), ("2018-01", "2026-06")
BEKLENEN = {"X1_temettu_verimi": 1, "X2_1ay_donus": 1, "X3_52h_zirve": 1, "X4_momentum_6_1": 1, "X5_kucuk_buyukluk": 1,
            "X6_likidite_primi": 1, "X7_dusuk_beta": 1, "X8_sektor_momentum": 1,
            "E1_bedelsiz_oncesi": 1, "E2_bedelsiz_sonrasi": -1, "E3_temettu_oncesi": 1,
            "T1_ay_donumu": 1, "T2_tatil_oncesi": 1, "T3_kasim_nisan": 1, "T4_pazartesi": -1}


# ------------------------------------------------------------------ veri
def ek_veri(kod):
    """(hacim, ham_kapanis, temettu, bolunme) - yfinance."""
    import yfinance as yf
    t = yf.Ticker(kod + ".IS")
    df = t.history(start="2015-01-01", interval="1d", auto_adjust=False)
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    def temiz(s):
        s = s.copy()
        s.index = pd.to_datetime(s.index).tz_localize(None).normalize() if len(s) else s.index
        return s
    try:
        div = temiz(t.dividends)
    except Exception:
        div = pd.Series(dtype=float)
    try:
        spl = temiz(t.splits)
    except Exception:
        spl = pd.Series(dtype=float)
    return df["Volume"], df["Close"], div, spl


def xu_uzun():
    import yfinance as yf
    from ma610_tarama import bolunme_duzelt
    df = yf.Ticker("XU100.IS").history(start="2005-01-01", interval="1d", auto_adjust=False)
    c = df["Close"].dropna()
    c = c[c > 0]
    c.index = pd.to_datetime(c.index).tz_localize(None).normalize()
    if float(c.pct_change().abs().max()) > 0.25:
        c, _ = bolunme_duzelt(c)
    return c


# ------------------------------------------------------------------ istatistik
def p_deger(t):
    return None if t is None else math.erfc(abs(t) / math.sqrt(2))


def welch(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    if len(a) < 5 or len(b) < 5:
        return {"n1": len(a), "n2": len(b)}
    d = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"n1": len(a), "n2": len(b), "ort": round(float(d), 4), "t": round(float(d / se), 2) if se else None}


def aralik_maske(idx_str, aralik):
    return (idx_str >= aralik[0]) & (idx_str <= aralik[1])


# ------------------------------------------------------------------ kesitsel motor
def ay_pozisyonlari(idx):
    s = pd.Series(range(len(idx)), index=idx)
    return list(s.groupby([idx.year, idx.month]).max().values)


def aylik_seri(C, ay_pos, secici):
    satir, onceki = [], set()
    for a in range(len(ay_pos) - 1):
        i0, i1 = ay_pos[a], ay_pos[a + 1]
        r = secici(i0)
        if not r:
            continue
        sec, evren = r
        g = (C.iloc[i1] / C.iloc[i0] - 1)
        rs, re = g[sec].dropna(), g[evren].dropna()
        if rs.empty or re.empty:
            continue
        devir = 1.0 if not onceki else len(set(sec) - onceki) / len(sec)
        satir.append({"ay": C.index[i0].strftime("%Y-%m"), "net_ew": (rs.mean() - re.mean()) * 100 - MALIYET * devir})
        onceki = set(sec)
    return pd.DataFrame(satir)


def ust_dilim(skor):
    skor = skor.dropna()
    if len(skor) < MIN_SIRALI:
        return None
    n = max(5, int(math.floor(DILIM * len(skor))))
    return list(skor.nlargest(n).index), list(skor.index)


def x_ozet(df):
    out = {}
    for ad, ar in (("IS", X_IS), ("OOS", X_OOS)):
        x = df[aralik_maske(df["ay"], ar)]["net_ew"] if len(df) else pd.Series(dtype=float)
        out[ad] = newey_west(list(x.values), 2) or {"n": len(x)}
    return out


# ------------------------------------------------------------------ ana
def main():
    kd = set(liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in liste_oku("config/bist100_uyeler.txt") if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    C, _, bol, hata = panel_kur(evren, {})
    C = C[C.index >= pd.Timestamp("2015-09-01")]
    R = C.pct_change()
    xu = xu_uzun()
    xr = xu.pct_change().reindex(C.index)
    hacim, carpan, div, spl = {}, {}, {}, {}
    for k in C.columns:
        try:
            v, ham, d, s = ek_veri(k)
            hacim[k] = v.reindex(C.index)
            carpan[k] = (C[k] / ham.reindex(C.index))
            div[k], spl[k] = d, s
        except Exception as e:
            hata[k] = f"ek veri: {str(e)[:80]}"
    V = pd.DataFrame(hacim).reindex(columns=C.columns)
    adet = {k: temel_tablo(k)[1] for k in C.columns}
    ay_pos = [p for p in ay_pozisyonlari(C.index) if p >= 252]
    sonuc = {}

    # X1 temettu verimi (bolunme duzeltmesi temettuye de uygulanir)
    def x1(i0):
        t = C.index[i0]
        sk = {}
        for k in C.columns:
            d = div.get(k)
            if d is None or not len(d) or pd.isna(C.iat[i0, C.columns.get_loc(k)]):
                continue
            pencere = d[(d.index > t - pd.Timedelta(days=365)) & (d.index <= t)]
            if not len(pencere):
                sk[k] = 0.0
                continue
            cp = carpan[k].reindex(pencere.index, method="nearest") if k in carpan else 1.0
            sk[k] = float((pencere * cp).sum()) / C.iat[i0, C.columns.get_loc(k)]
        return ust_dilim(pd.Series(sk, dtype=float))
    sonuc["X1_temettu_verimi"] = x_ozet(aylik_seri(C, ay_pos, x1))
    sonuc["X2_1ay_donus"] = x_ozet(aylik_seri(C, ay_pos, lambda i0: ust_dilim(-(C.iloc[i0] / C.iloc[i0 - 21] - 1))))
    sonuc["X3_52h_zirve"] = x_ozet(aylik_seri(C, ay_pos, lambda i0: ust_dilim(C.iloc[i0] / C.iloc[i0 - 251:i0 + 1].max())))
    sonuc["X4_momentum_6_1"] = x_ozet(aylik_seri(C, ay_pos, lambda i0: ust_dilim(C.iloc[i0 - 21] / C.iloc[i0 - 126] - 1)))
    sonuc["X5_kucuk_buyukluk"] = x_ozet(aylik_seri(C, ay_pos, lambda i0: ust_dilim(
        -pd.Series({k: C.iat[i0, j] * adet[k] for j, k in enumerate(C.columns) if adet.get(k) and pd.notna(C.iat[i0, j])}, dtype=float))))

    def x6(i0):
        w = slice(i0 - 62, i0 + 1)
        tl = (C.iloc[w] * V.iloc[w]).replace(0, np.nan)
        am = (R.iloc[w].abs() / tl).mean()
        am[(tl.notna().sum() < 40)] = np.nan
        return ust_dilim(am)
    sonuc["X6_likidite_primi"] = x_ozet(aylik_seri(C, ay_pos, x6))

    def x7(i0):
        w = R.iloc[i0 - 251:i0 + 1]
        x = xr.iloc[i0 - 251:i0 + 1]
        b = {}
        for k in C.columns:
            j = pd.concat([w[k], x], axis=1).dropna()
            if len(j) >= 200 and j.iloc[:, 1].var() > 0:
                b[k] = j.iloc[:, 0].cov(j.iloc[:, 1]) / j.iloc[:, 1].var()
        return ust_dilim(-pd.Series(b, dtype=float))
    sonuc["X7_dusuk_beta"] = x_ozet(aylik_seri(C, ay_pos, x7))

    def x8(i0):
        m = C.iloc[i0 - 21] / C.iloc[i0 - 252] - 1
        m = m.dropna()
        if len(m) < MIN_SIRALI:
            return None
        sek = pd.Series({k: SEKTOR100.get(k) for k in m.index}).dropna()
        gm = m[sek.index].groupby(sek).agg(["mean", "count"])
        gm = gm[gm["count"] >= 2]
        if len(gm) < 5:
            return None
        n = max(1, int(math.ceil(DILIM * len(gm))))
        iyi = set(gm["mean"].nlargest(n).index)
        return [k for k in sek.index if sek[k] in iyi], list(m.index)
    sonuc["X8_sektor_momentum"] = x_ozet(aylik_seri(C, ay_pos, x8))

    # E olay testleri
    gun = C.index
    def olay_getirisi(kod, p, a, b):
        if p + b >= len(gun) or p + a < 0:
            return None
        g = C.iloc[p + b] / C.iloc[p + a] - 1
        if pd.isna(g.get(kod)):
            return None
        return (float(g[kod]) - float(g.drop(kod).dropna().mean())) * 100

    def olay_ozet(olaylar, a, b, maliyet):
        satir = []
        for kod, d in olaylar:
            p = gun.searchsorted(d)
            if p >= len(gun):
                continue
            v = olay_getirisi(kod, p, a, b)
            if v is None:
                continue
            satir.append({"t": gun[p], "v": v - maliyet})
        df = pd.DataFrame(satir)
        out = {}
        for ad, ar in (("IS", X_IS), ("OOS", X_OOS)):
            x = df[aralik_maske(df["t"].dt.strftime("%Y-%m"), ar)] if len(df) else df
            if len(x) < 5:
                out[ad] = {"n": len(x)}
                continue
            k = kumelenmis(list(x["v"]), ["%d-W%02d" % t.isocalendar()[:2] for t in x["t"]])
            out[ad] = {"n": len(x), "kume": k["G"], "ort": round(k["ort"], 3), "t": None if k["t"] is None else round(k["t"], 2)}
        return out

    bed = []
    for k in C.columns:
        tarih = set()
        s = spl.get(k)
        if s is not None and len(s):
            tarih |= {pd.Timestamp(x) for x, r in s.items() if r >= 1.2}
        tarih |= {pd.Timestamp(x) for x in bol.get(k, set())}
        son = None
        for t in sorted(tarih):
            if son is None or (t - son).days > 30:
                bed.append((k, t))
                son = t
    sonuc["E1_bedelsiz_oncesi"] = olay_ozet(bed, -11, -1, MALIYET)
    sonuc["E2_bedelsiz_sonrasi"] = olay_ozet(bed, -1, 19, 0.0)
    tem = [(k, pd.Timestamp(t)) for k in C.columns for t in (div.get(k).index if div.get(k) is not None else [])]
    sonuc["E3_temettu_oncesi"] = olay_ozet(tem, -11, -1, MALIYET)

    # T takvim testleri (XU100)
    r = xu.pct_change().dropna() * 100
    d = r.index
    ay_str = pd.Series(d.strftime("%Y-%m"), index=d)
    son_gun = pd.Series(d, index=d).groupby([d.year, d.month]).transform("max")
    sira = pd.Series(1, index=d).groupby([d.year, d.month]).cumsum()
    tom = (pd.Series(d, index=d) == son_gun) | (sira <= 3)
    sonraki = pd.Series(list(d[1:]) + [pd.NaT], index=d)
    tatil = pd.Series([bool(pd.notna(n) and np.busday_count(t.date() + datetime.timedelta(days=1), n.date()) > 0) for t, n in sonraki.items()], index=d)
    pzt = pd.Series(d.weekday == 0, index=d)

    def t_ozet(maske):
        out = {}
        for ad, ar in (("IS", T_IS), ("OOS", T_OOS)):
            m = aralik_maske(ay_str, ar)
            out[ad] = welch(r[m & maske], r[m & ~maske])
        return out
    sonuc["T1_ay_donumu"] = t_ozet(tom)
    sonuc["T2_tatil_oncesi"] = t_ozet(tatil)
    sonuc["T4_pazartesi"] = t_ozet(pzt)
    me = xu.groupby([xu.index.year, xu.index.month]).last()
    aylik = me.pct_change().dropna() * 100
    aylik.index = [f"{y}-{m:02d}" for y, m in aylik.index]
    kis = pd.Series([int(a[5:]) in (11, 12, 1, 2, 3, 4) for a in aylik.index], index=aylik.index)
    sonuc["T3_kasim_nisan"] = {ad: welch(aylik[aralik_maske(pd.Series(aylik.index, index=aylik.index), ar) & kis],
                                         aylik[aralik_maske(pd.Series(aylik.index, index=aylik.index), ar) & ~kis])
                               for ad, ar in (("IS", T_IS), ("OOS", T_OOS))}

    # coklu test ve hukum
    pler = {k: p_deger((v.get("OOS") or {}).get("t")) for k, v in sonuc.items()}
    g = sorted([(p, k) for k, p in pler.items() if p is not None])
    m, esik = len(g), 0
    for i, (p, _) in enumerate(g, 1):
        if p <= BH_Q * i / m:
            esik = i
    anl = {k: (i <= esik) for i, (_, k) in enumerate(g, 1)}
    for k, v in sonuc.items():
        o, s_ = (v.get("OOS") or {}).get("ort"), (v.get("IS") or {}).get("ort")
        b = BEKLENEN[k]
        if o is None:
            h = "VERI_YETERSIZ"
        elif anl.get(k) and o * b > 0 and s_ is not None and s_ * b > 0:
            h = "ADAY"
        elif anl.get(k) and o * b < 0:
            h = "TERS"
        else:
            h = "KENAR_YOK"
        v.update({"beklenen": "+" if b > 0 else "-", "p_oos": None if pler[k] is None else round(pler[k], 4),
                  "bh_anlamli": bool(anl.get(k)), "hukum": h})

    os.makedirs(CIKTI, exist_ok=True)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    sha = sha256(ON_KAYIT)
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1", "on_kayit_sha256": sha,
           "deneme_no": len(kayit["denemeler"]) + 1, "testler": sonuc,
           "veri": {"evren": len(evren), "fiyatli": len(C.columns), "hata": hata, "bedelsiz_olay": len(bed), "temettu_olay": len(tem),
                    "xu_ilk": str(xu.index.min().date())}}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    G = lambda x, a: (x or {}).get(a)
    L = ["# H8 Kesif Bataryasi", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{(sha or '-')[:16]}` | deneme no {out['deneme_no']} | BH q={BH_Q}, 15 test",
         "", "Salt olcum, tavsiye degildir. X: aylik, evren ortalamasina gore net (yuzde puan). E: olay penceresi, evrene gore. "
         "T: XU100 gun/ay getiri farki. En iyi etiket ADAY; aday ancak ayri on kayitla golgeye alinir.", "",
         "| Test | Beklenen | IS ort (t, n) | OOS ort (t, n) | OOS p | BH | Hukum |", "|---|---|---|---|---|---|---|"]
    for k, v in sonuc.items():
        i_, o_ = v.get("IS") or {}, v.get("OOS") or {}
        n_i = i_.get("n", i_.get("n1")); n_o = o_.get("n", o_.get("n1"))
        L.append(f"| {k} | {v['beklenen']} | {G(i_,'ort')} ({G(i_,'t')}, {n_i}) | {G(o_,'ort')} ({G(o_,'t')}, {n_o}) | {v['p_oos']} | "
                 f"{'evet' if v['bh_anlamli'] else 'hayir'} | **{v['hukum']}** |")
    L += ["", f"Veri: {out['veri']}", "", "Test edilemeyenler (veri yok): endeks degisiklikleri, analist revizyonlari, yabanci payi/takas/AKD, "
          "VIOP acik pozisyon ve aciga satis gecmisi, fon portfoy dagilimlari, haber/duygu, opsiyon, emir defteri."]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": os.environ.get("GITHUB_SHA"),
                               "hukum": {k: v["hukum"] for k, v in sonuc.items()}})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("H8", {k: v["hukum"] for k, v in sonuc.items()})


if __name__ == "__main__":
    main()
