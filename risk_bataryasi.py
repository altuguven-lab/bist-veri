"""
RISK BATARYASI R1-R4 (Pine oncesi zorunlu testler) - SALT OLCUM, TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_RISK.md (bu betikten ONCE commit edilmis olmali).
Girdi : data/endeks_uyelik/donemsel.json, yfinance OHLC, (istege bagli) EVDS TP.APIFON4
Cikti : data/risk/sonuc.json, data/risk/sonuc.md, data/risk/deneme_kaydi.json
"""
import os, json, math, hashlib, datetime
import numpy as np
import pandas as pd

ON_KAYIT = "ON_KAYIT_RISK.md"
CIKTI = "data/risk"
BAS = "2015-09-01"
IS = ("2016-07-01", "2022-12-31")
OOS_BAS = "2023-01-01"
TEK_YON = 0.00125
GIDIS_DONUS = 0.0025
TOHUM = 20261103
T_ESIK = 2.58


# ------------------------------------------------------------------ yardimcilar
def sha256(yol):
    return hashlib.sha256(open(yol, "rb").read()).hexdigest() if os.path.exists(yol) else None


def liste_oku(yol):
    if not os.path.exists(yol):
        return set()
    return {s.split("#")[0].strip().upper() for s in open(yol, encoding="utf-8") if s.split("#")[0].strip()}


def newey_west(x, lag):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], dtype=float)
    n = len(x)
    if n < lag + 5:
        return {"n": n, "ort": None, "t": None}
    e = x - x.mean()
    var = (e @ e) / n
    for l in range(1, lag + 1):
        var += 2 * (1 - l / (lag + 1)) * (e[l:] @ e[:-l]) / n
    se = math.sqrt(var / n) if var > 0 else None
    return {"n": n, "ort": round(float(x.mean()), 4), "t": round(float(x.mean() / se), 2) if se else None}


def ohlc_cek(kod):
    import yfinance as yf
    from ma610_tarama import bolunme_duzelt
    df = yf.Ticker(kod + ".IS").history(start=BAS, interval="1d", auto_adjust=False)
    df = df[df["Close"] > 0].dropna(subset=["Close"])
    if df.empty:
        return df
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    ham = df["Close"]
    duz, _ = bolunme_duzelt(ham)
    if kod == "XU100" and float(ham.pct_change().abs().max()) <= 0.25:
        duz = ham
    k = duz / ham
    return pd.DataFrame({"O": df["Open"] * k, "H": df["High"] * k, "L": df["Low"] * k, "C": duz})


def panel(semboller):
    O, H, L, C, hata = {}, {}, {}, {}, {}
    for s in semboller:
        try:
            df = ohlc_cek(s)
            if len(df) < 60:
                raise ValueError(f"az veri ({len(df)})")
            O[s], H[s], L[s], C[s] = df.O, df.H, df.L, df.C
        except Exception as e:
            hata[s] = str(e)[:100]
    f = lambda d: pd.DataFrame(d).sort_index()
    return f(O), f(H), f(L), f(C), hata


def uyelik_matrisi(uyelik, takvim, kolonlar, kd):
    donemler = sorted(k for k in uyelik if not k.startswith("ONCESI"))
    oncesi = next((k for k in uyelik if k.startswith("ONCESI")), None)
    M = pd.DataFrame(False, index=takvim, columns=kolonlar)
    for i, t in enumerate(takvim):
        ts = str(t.date())
        aday = [k for k in donemler if k <= ts]
        uy = uyelik[aday[-1]]["XU100"] if aday else (uyelik[oncesi]["XU100"] if oncesi else [])
        cols = [s for s in uy if s in M.columns and s not in kd]
        M.iloc[i, [M.columns.get_loc(s) for s in cols]] = True
    return M


def metrikler(r):
    r = pd.Series(r).dropna()
    if len(r) < 60:
        return None
    eq = (1 + r).cumprod()
    dd = float((eq / eq.cummax() - 1).min())
    yil = len(r) / 252
    getiri = float(eq.iloc[-1] ** (1 / yil) - 1) if yil > 0 else None
    vol = float(r.std() * math.sqrt(252))
    q = r.quantile(0.05)
    cvar = float(r[r <= q].mean())
    return {"gun": len(r), "yillik_getiri": round(getiri, 4), "yillik_vol": round(vol, 4), "maks_dusus": round(dd, 4),
            "cvar5": round(cvar, 5), "getiri_vol": round(getiri / vol, 3) if vol > 0 else None}


def donem(s, kim):
    return s[(s.index >= IS[0]) & (s.index <= IS[1])] if kim == "IS" else s[s.index >= OOS_BAS]


def maks_dusus(r):
    eq = np.cumprod(1 + np.asarray(r))
    return float((eq / np.maximum.accumulate(eq) - 1).min())


# ------------------------------------------------------------------ R1
def tahminciler(O, H, L, C, R):
    s20 = R.rolling(20, min_periods=18).std()
    s60 = R.rolling(60, min_periods=54).std()
    pc = C.shift(1)
    tr = pd.concat([(H - L), (H - pc).abs(), (L - pc).abs()]).groupby(level=0).max()
    tr = tr.reindex(C.index)
    atr = tr.rolling(14, min_periods=12).mean()
    ewma = np.sqrt((R ** 2).ewm(alpha=0.06, min_periods=30).mean())
    return {"s20": s20, "s60": s60, "atr14": atr / C, "ewma": ewma}, atr


def r1(TAH, R, M, rng):
    hedef = R[::-1].rolling(20, min_periods=15).std()[::-1].shift(-1)      # t+1..t+20
    idx = R.index
    hafta_sonu = pd.Series(idx, index=idx).groupby([idx.isocalendar().year, idx.isocalendar().week]).max()
    tarihler = [t for t in sorted(hafta_sonu) if str(t.date()) >= IS[0]]
    seriler = {k: {} for k in TAH}
    plasebo = {}
    for t in tarihler:
        m = M.loc[t]
        y = hedef.loc[t][m]
        for k, P in TAH.items():
            x = P.loc[t][m]
            ok = x.notna() & y.notna()
            if ok.sum() >= 30:
                seriler[k][t] = float(x[ok].rank().corr(y[ok].rank()))
    out = {}
    for k, d in seriler.items():
        s = pd.Series(d)
        out[k] = {"tum": newey_west(s.values, 4), "IS": newey_west(donem(s, "IS").values, 4), "OOS": newey_west(donem(s, "OOS").values, 4)}
    secilen = max(out, key=lambda k: out[k]["IS"]["ort"] or -9)
    for t in tarihler:
        m = M.loc[t]
        x, y = TAH[secilen].loc[t][m], hedef.loc[t][m]
        ok = x.notna() & y.notna()
        if ok.sum() >= 30:
            xv = rng.permutation(x[ok].values)
            plasebo[t] = float(pd.Series(xv).rank().corr(pd.Series(y[ok].values).rank()))
    p = newey_west(pd.Series(plasebo).values, 4)
    o = out[secilen]
    gecti = (o["IS"]["ort"] or 0) >= 0.30 and (o["OOS"]["ort"] or 0) >= 0.30 and (o["OOS"]["t"] or 0) > T_ESIK and abs(p["t"] or 0) < T_ESIK
    return {"hukum": "GECTI" if gecti else "KENAR_YOK", "secilen": secilen, "tahminciler": out, "plasebo": p}


# ------------------------------------------------------------------ R2
def ay_sonlari(idx):
    return sorted(pd.Series(idx, index=idx).groupby([idx.year, idx.month]).max())


def portfoy(R, M, sigma, tip, rng=None):
    idx = R.index
    aylar = [t for t in ay_sonlari(idx) if str(t.date()) >= "2016-06-01"]
    getiri = pd.Series(0.0, index=idx)
    w_eski = pd.Series(dtype=float)
    for a, b in zip(aylar, aylar[1:] + [idx[-1] + pd.Timedelta(days=1)]):
        m = M.loc[a] & sigma.loc[a].notna() & (sigma.loc[a] > 0)
        uy = list(m[m].index)
        if len(uy) < 30:
            continue
        n = len(uy)
        if tip == "EW":
            w = pd.Series(1.0 / n, index=uy)
        else:
            w = 1.0 / sigma.loc[a, uy]
            w = w / w.sum()
            for _ in range(5):
                w = w.clip(upper=3.0 / n)
                w = w / w.sum()
            if tip == "PLASEBO":
                w = pd.Series(rng.permutation(w.values), index=uy)
        gunler = idx[(idx > a) & (idx < b)]
        if len(gunler) == 0:
            continue
        rr = R.loc[gunler, uy].fillna(0.0)
        getiri.loc[gunler] = rr.values @ w.values
        tum = w.index.union(w_eski.index)
        devir = float((w.reindex(tum, fill_value=0) - w_eski.reindex(tum, fill_value=0)).abs().sum())
        getiri.loc[gunler[0]] -= devir * TEK_YON
        w_eski = w
    bas = idx[idx > aylar[0]][0]
    return getiri[getiri.index >= bas]


def bootstrap_dd(a, b, rng, n=1000, blok=20):
    a, b = np.asarray(a), np.asarray(b)
    T = len(a)
    say = 0
    for _ in range(n):
        ix = np.empty(T, dtype=int)
        i = 0
        while i < T:
            bas = rng.integers(0, T)
            L = max(1, int(rng.geometric(1.0 / blok)))
            for j in range(L):
                if i >= T:
                    break
                ix[i] = (bas + j) % T
                i += 1
        say += maks_dusus(a[ix]) > maks_dusus(b[ix])          # a'nin dususu daha kucuk (daha az negatif)
    return say / n


def r2(R, M, sigma, rng):
    ew, iv = portfoy(R, M, sigma, "EW"), portfoy(R, M, sigma, "IV")
    pl = portfoy(R, M, sigma, "PLASEBO", rng)
    tablo = {ad: {d: metrikler(donem(s, d)) for d in ("IS", "OOS")} | {"tum": metrikler(s)} for ad, s in (("EW", ew), ("IV", iv), ("PLASEBO", pl))}
    def risk_iyi(x, y, d):
        a, b = tablo[x][d], tablo[y][d]
        return a["yillik_vol"] < b["yillik_vol"] and a["maks_dusus"] > b["maks_dusus"] and a["cvar5"] > b["cvar5"]
    def oran_ok(d):
        a, b = tablo["IV"][d]["getiri_vol"], tablo["EW"][d]["getiri_vol"]
        return a is not None and b is not None and (a >= 0.9 * b if b > 0 else a >= b)
    bs = bootstrap_dd(iv.values, ew.values, rng)
    k1 = all(risk_iyi("IV", "EW", d) for d in ("IS", "OOS"))
    k2 = all(oran_ok(d) for d in ("IS", "OOS"))
    k4_plasebo_sagladi = all(risk_iyi("PLASEBO", "EW", d) for d in ("IS", "OOS"))
    if k1 and k2 and bs >= 0.95:
        h = "SUPHELI" if k4_plasebo_sagladi else "GECTI"
    else:
        h = "KENAR_YOK"
    return {"hukum": h, "tablo": tablo, "bootstrap_iv_dusus_kucuk_orani": round(bs, 3),
            "sartlar": {"risk_IS_OOS": k1, "getiri_vol": k2, "bootstrap": bs >= 0.95, "plasebo_risk_sagladi": k4_plasebo_sagladi}}, ew


# ------------------------------------------------------------------ R3
VARYANT = {"V0": None, "S5": ("y", 0.05), "S8": ("y", 0.08), "A15": ("a", 1.5), "A2": ("a", 2.0), "A3": ("a", 3.0), "T2": ("t", 2.0), "T3": ("t", 3.0)}


def r3_islemler(O, H, L, C, ATR, M):
    idx = C.index
    giris_ix = [i for i in range(len(idx)) if str(idx[i].date()) >= IS[0] and i % 5 == 0 and i + 19 < len(idx) and i >= 1]
    Ov, Hv, Lv, Cv, Av, Mv = O.values, H.values, L.values, C.values, ATR.values, M.values
    kayit = {v: [] for v in VARYANT}
    cikis_gun = {v: [] for v in VARYANT}
    meta = []
    for i in giris_ix:
        for j in np.where(Mv[i])[0]:
            e, a = Ov[i, j], Av[i - 1, j]
            blok_c = Cv[i:i + 20, j]
            if not (np.isfinite(e) and e > 0 and np.isfinite(a) and a > 0) or not np.isfinite(blok_c).all():
                continue
            meta.append((str(idx[i].date()), i, j))
            for v, kural in VARYANT.items():
                if kural is None:
                    kayit[v].append(Cv[i + 19, j] / e - 1 - GIDIS_DONUS)
                    cikis_gun[v].append(19)
                    continue
                tip, k = kural
                stop = e * (1 - k) if tip == "y" else e - k * a
                en_yuksek = e
                cik, gun = None, 19
                for d in range(20):
                    o, l, c = Ov[i + d, j], Lv[i + d, j], Cv[i + d, j]
                    if d > 0 and np.isfinite(o) and o < stop:
                        cik, gun = o, d
                        break
                    if np.isfinite(l) and l <= stop:
                        cik, gun = stop, d
                        break
                    if tip == "t" and np.isfinite(c):
                        en_yuksek = max(en_yuksek, c)
                        stop = max(stop, en_yuksek - k * a)
                if cik is None:
                    cik = Cv[i + 19, j]
                kayit[v].append(cik / e - 1 - GIDIS_DONUS)
                cikis_gun[v].append(gun)
    return {v: np.array(x) for v, x in kayit.items()}, {v: np.array(x) for v, x in cikis_gun.items()}, meta


def islem_ozet(x, gun=None):
    x = np.asarray(x)
    if len(x) < 100:
        return None
    q = np.quantile(x, 0.05)
    o = {"n": int(len(x)), "ort": round(float(x.mean()) * 100, 3), "medyan": round(float(np.median(x)) * 100, 3),
         "std": round(float(x.std()) * 100, 3), "cvar5": round(float(x[x <= q].mean()) * 100, 3), "en_kotu": round(float(x.min()) * 100, 2)}
    if gun is not None:
        o["stop_orani"] = round(float((np.asarray(gun) < 19).mean()), 3)
        o["ort_tutma"] = round(float(np.asarray(gun).mean()) + 1, 2)
    return o


def sentetik_panel(O, H, L, C, rng):
    """Her hissenin kendi gunluk (O,H,L,C)/onceki kapanis oranlari iid yeniden ornekleniyor: oynaklik, kalin kuyruk ve
    gun ici sekil korunur; ardisik bagimlilik (ortalamaya donus, momentum, bosluk kumelenmesi) yok edilir."""
    pc = C.shift(1)
    ro, rh, rl, rc = (O / pc).values, (H / pc).values, (L / pc).values, (C / pc).values
    So, Sh, Sl, Sc = (np.full(C.shape, np.nan) for _ in range(4))
    for j in range(C.shape[1]):
        ok = np.isfinite(ro[:, j]) & np.isfinite(rh[:, j]) & np.isfinite(rl[:, j]) & np.isfinite(rc[:, j]) & (np.abs(rc[:, j] - 1) <= 0.5)
        satir = np.where(ok)[0]
        mevcut = np.where(np.isfinite(C.values[:, j]))[0]
        if len(satir) < 60 or len(mevcut) < 2:
            continue
        sec = rng.choice(satir, size=len(mevcut))
        cc = 100 * np.cumprod(rc[sec, j])
        onceki = np.concatenate([[100.0], cc[:-1]])
        So[mevcut, j], Sh[mevcut, j], Sl[mevcut, j], Sc[mevcut, j] = onceki * ro[sec, j], onceki * rh[sec, j], onceki * rl[sec, j], cc
    f = lambda v: pd.DataFrame(v, index=C.index, columns=C.columns)
    return f(So), f(Sh), f(Sl), f(Sc)


def atr_hesap(H, L, C):
    pc = C.shift(1)
    tr = pd.concat([(H - L), (H - pc).abs(), (L - pc).abs()]).groupby(level=0).max().reindex(C.index)
    return tr.rolling(14, min_periods=12).mean()


def r3(O, H, L, C, ATR, M, rng):
    ret, gun, meta = r3_islemler(O, H, L, C, ATR, M)
    tarih = np.array([m[0] for m in meta])
    maske = {"IS": (tarih >= IS[0]) & (tarih <= IS[1]), "OOS": tarih >= OOS_BAS}
    tablo = {v: {d: islem_ozet(ret[v][mk], gun[v][mk]) for d, mk in maske.items()} for v in VARYANT}
    v0 = tablo["V0"]
    adaylar = [v for v in VARYANT if v != "V0" and tablo[v]["IS"] and tablo[v]["IS"]["ort"] >= v0["IS"]["ort"] - 0.30]
    secilen = max(adaylar, key=lambda v: tablo[v]["IS"]["cvar5"]) if adaylar else None
    # plasebo: ayni kurallar, ardisik bagimliligi yok edilmis sentetik fiyatlarla
    sO, sH, sL, sC = sentetik_panel(O, H, L, C, rng)
    pret, pgun, pmeta = r3_islemler(sO, sH, sL, sC, atr_hesap(sH, sL, sC), M)
    ptarih = np.array([m[0] for m in pmeta])
    pmaske = {"IS": (ptarih >= IS[0]) & (ptarih <= IS[1]), "OOS": ptarih >= OOS_BAS}
    plasebo = {v: {d: islem_ozet(pret[v][mk], pgun[v][mk]) for d, mk in pmaske.items()} for v in VARYANT}
    hukum, kosul = "KENAR_YOK", {}
    if secilen:
        s, b = tablo[secilen]["OOS"], v0["OOS"]
        fark_gercek = s["ort"] - b["ort"]
        fark_plasebo = plasebo[secilen]["OOS"]["ort"] - plasebo["V0"]["OOS"]["ort"]
        k1 = abs(s["cvar5"]) <= 0.75 * abs(b["cvar5"])
        k2 = s["ort"] >= b["ort"] - 0.30
        k3 = fark_gercek >= fark_plasebo - 0.20
        kosul = {"cvar_25pct": k1, "ort_kaybi_0_30": k2, "plasebodan_pahali_degil": k3,
                 "ort_fark_gercek": round(fark_gercek, 3), "ort_fark_plasebo": round(fark_plasebo, 3)}
        hukum = "GECTI" if (k1 and k2 and k3) else ("STOP_PAHALI" if (k1 and not k3) else "KENAR_YOK")
    kum = None
    if secilen:
        df = pd.DataFrame({"t": tarih, "f": ret[secilen] - ret["V0"]}).groupby("t").f.mean()
        kum = newey_west(df.values * 100, 4)
    # bosluk: stopla cikan islemlerde acilis boslugu payi (secilen varyant, bilgi)
    return {"hukum": hukum, "secilen": secilen, "kosullar": kosul, "tablo": tablo, "plasebo": plasebo, "ort_fark_kume_t": kum}


# ------------------------------------------------------------------ R4
def r4(taban, xu, nakit, rng):
    c = xu.reindex(taban.index).ffill()
    r = c.pct_change()
    sma = c.rolling(200, min_periods=190).mean()
    v20 = r.rolling(20, min_periods=18).std()
    p80 = v20.rolling(252, min_periods=200).quantile(0.80)
    f1 = (c < sma)
    f2 = (v20 > p80)
    sok = (r.abs() >= 0.05)
    f3 = sok.rolling(5, min_periods=1).max().astype(bool)          # sok gunu dahil 5 gun -> t+1..t+5 uygulanir
    filtreler = {"F1": f1, "F2": f2, "F3": f3, "F4": f1 | f2 | f3}
    out = {"taban": {d: metrikler(donem(taban, d)) for d in ("IS", "OOS")} | {"tum": metrikler(taban)}}
    for ad, f in filtreler.items():
        oran = pd.Series(np.where(f, 0.5, 1.0), index=taban.index).shift(1).fillna(1.0)
        maliyet = oran.diff().abs().fillna(0) * TEK_YON
        def seri(oranlar, nk):
            return oranlar * taban + (1 - oranlar) * nk - oranlar.diff().abs().fillna(0) * TEK_YON
        s0 = seri(oran, 0.0)
        tab = {d: metrikler(donem(s0, d)) for d in ("IS", "OOS")} | {"tum": metrikler(s0)}
        sn = seri(oran, nakit.reindex(taban.index).ffill().fillna(0)) if nakit is not None else None
        dd_f = maks_dusus(s0.values)
        pl = []
        n = len(oran)
        for _ in range(500):
            k = int(rng.integers(1, n))
            o2 = pd.Series(np.roll(oran.values, k), index=oran.index)
            pl.append(maks_dusus(seri(o2, 0.0).values))
        pl = np.array(pl)
        yuzde = float((dd_f > pl).mean())
        k1 = all(tab[d]["maks_dusus"] >= 0.8 * out["taban"][d]["maks_dusus"] for d in ("IS", "OOS"))
        k2 = all(tab[d]["cvar5"] > out["taban"][d]["cvar5"] for d in ("IS", "OOS"))
        k3 = yuzde >= 0.95
        out[ad] = {"hukum": "GECTI" if (k1 and k2 and k3) else "KENAR_YOK", "tablo": tab,
                   "nakit_faizli": ({d: metrikler(donem(sn, d)) for d in ("IS", "OOS")} if sn is not None else None),
                   "azaltilmis_gun_orani": round(float((oran < 1).mean()), 3), "plasebodan_iyi_orani": round(yuzde, 3),
                   "sartlar": {"dusus_20pct": k1, "cvar": k2, "plasebo": k3}}
    return out


# ------------------------------------------------------------------ ana
def main():
    os.makedirs(CIKTI, exist_ok=True)
    sha = sha256(ON_KAYIT)
    if not sha:
        raise SystemExit("ON_KAYIT_RISK.md yok")
    rng = np.random.default_rng(TOHUM)
    uyelik = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))["uyelik"]
    kd = liste_oku("config/kapsam_disi.txt")
    semboller = sorted({s for v in uyelik.values() for s in v.get("XU100", [])} - kd)
    xu = ohlc_cek("XU100")
    takvim = xu.index
    O, H, L, C, hata = panel(semboller)
    O, H, L, C = (d.reindex(takvim) for d in (O, H, L, C))
    R = C.pct_change(fill_method=None)
    R = R.where(R.abs() <= 0.5)
    M = uyelik_matrisi(uyelik, takvim, C.columns, kd)

    TAH, ATR = tahminciler(O, H, L, C, R)
    o1 = r1(TAH, R, M, rng)
    o2, ew = r2(R, M, TAH[o1["secilen"]], rng)
    o3 = r3(O, H, L, C, ATR, M, rng)
    nakit = None
    if os.environ.get("TCMB_EVDS_API_KEY"):
        try:
            from h7_makro_rejim import evds_seri
            nakit = evds_seri("TP.APIFON4", os.environ["TCMB_EVDS_API_KEY"]) / 100 / 365
        except Exception as e:
            nakit = None
            hata["EVDS"] = str(e)[:100]
    o4 = r4(ew, xu.C, nakit, rng)
    o4_xu = r4(xu.C.pct_change().reindex(ew.index).fillna(0), xu.C, None, rng)

    uye_gun = int(M.values.sum())
    fiyatli = int((M & C.notna()).values.sum())
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "on_kayit_sha256": sha,
           "git_sha": os.environ.get("GITHUB_SHA"),
           "hukumler": {"R1": o1["hukum"], "R2": o2["hukum"], "R3": o3["hukum"], **{f"R4_{k}": o4[k]["hukum"] for k in ("F1", "F2", "F3", "F4")}},
           "R1": o1, "R2": o2, "R3": o3, "R4": o4, "R4_taban_XU100_bilgi": o4_xu,
           "kapsama": {"uye_gun": uye_gun, "fiyatli_uye_gun": fiyatli, "oran": round(fiyatli / max(1, uye_gun), 4)},
           "fiyat_hatasi_sayisi": len(hata), "fiyat_hatasi": dict(list(hata.items())[:80])}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": out["git_sha"], "hukum": out["hukumler"]})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    L_ = ["# Risk bataryasi R1-R4", "", f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{sha[:16]}` | deneme no {len(kayit['denemeler'])}", "",
          "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_RISK.md'de.", "", "## Hukumler", ""]
    L_ += [f"- **{k}: {v}**" for k, v in out["hukumler"].items()]
    L_ += ["", f"Kapsama: {out['kapsama']} | fiyat hatasi {len(hata)}", "", "## R1 Oynaklik tahmini (haftalik Spearman, NW t)", "",
           "| Tahminci | IS ort (t) | OOS ort (t) |", "|---|---|---|"]
    for k, v in o1["tahminciler"].items():
        L_.append(f"| {k}{' (secilen)' if k == o1['secilen'] else ''} | {v['IS']['ort']} ({v['IS']['t']}) | {v['OOS']['ort']} ({v['OOS']['t']}) |")
    L_.append(f"| plasebo | {o1['plasebo']['ort']} ({o1['plasebo']['t']}) | |")
    L_ += ["", "## R2 Oynakliga gore agirlik", "", "| Portfoy | Donem | Yillik getiri | Yillik vol | Maks dusus | CVaR5 | Getiri/vol |", "|---|---|---|---|---|---|---|"]
    for ad in ("EW", "IV", "PLASEBO"):
        for d in ("IS", "OOS"):
            m = o2["tablo"][ad][d]
            L_.append(f"| {ad} | {d} | {m['yillik_getiri']} | {m['yillik_vol']} | {m['maks_dusus']} | {m['cvar5']} | {m['getiri_vol']} |")
    L_ += [f"", f"Bootstrap (IV dususu daha kucuk) orani: {o2['bootstrap_iv_dusus_kucuk_orani']} | sartlar: {o2['sartlar']}", "",
           f"## R3 Stoplar (islem basi %, net) - secilen: {o3['secilen']}", "",
           "| Varyant | Donem | n | Ort | Medyan | CVaR5 | En kotu | Stop orani | Plasebo ort / CVaR5 |", "|---|---|---|---|---|---|---|---|---|"]
    for v in VARYANT:
        for d in ("IS", "OOS"):
            m = o3["tablo"][v][d]
            pc = o3["plasebo"].get(v, {}).get(d)
            if m:
                L_.append(f"| {v} | {d} | {m['n']} | {m['ort']} | {m['medyan']} | {m['cvar5']} | {m['en_kotu']} | {m.get('stop_orani')} | {(str(pc['ort']) + ' / ' + str(pc['cvar5'])) if pc else ''} |")
    L_ += [f"", f"Kosullar: {o3['kosullar']}", f"Ortalama farki (secilen - V0) giris gunu kumelenmis: {o3['ort_fark_kume_t']}", "", "## R4 Kriz filtresi (taban: EW sepet, nakit 0)", "",
           "| Filtre | Donem | Yillik getiri | Yillik vol | Maks dusus | CVaR5 | Azaltilmis gun | Plasebodan iyi | Hukum |", "|---|---|---|---|---|---|---|---|---|"]
    for d in ("IS", "OOS"):
        m = o4["taban"][d]
        L_.append(f"| taban | {d} | {m['yillik_getiri']} | {m['yillik_vol']} | {m['maks_dusus']} | {m['cvar5']} | | | |")
    for ad in ("F1", "F2", "F3", "F4"):
        for d in ("IS", "OOS"):
            m = o4[ad]["tablo"][d]
            L_.append(f"| {ad} | {d} | {m['yillik_getiri']} | {m['yillik_vol']} | {m['maks_dusus']} | {m['cvar5']} | {o4[ad]['azaltilmis_gun_orani']} | {o4[ad]['plasebodan_iyi_orani']} | {o4[ad]['hukum']} |")
    L_ += ["", "Nakit faizli (APIFON4) sonuc ve XU100 tabanli tekrar sonuc.json'da (bilgi)."]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L_) + "\n")
    print("\n".join(L_))


if __name__ == "__main__":
    main()
