"""
H7 MAKRO RISK ISTAHI BAYRAGI ILE ENDEKS ZAMANLAMASI (30.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H7.md (bu betikten ONCE commit edilir). Parametre secmez.
Girdi : EVDS (TP.DK.USD.A.YTL, TP.APIFON4; anahtar TCMB_EVDS_API_KEY ortam degiskeninden), yfinance (XU100.IS, ^VIX)
Cikti : data/h7/sonuc.json, data/h7/sonuc.md, data/h7/aylik.csv, data/h7/deneme_kaydi.json
"""
import os, json, math, datetime
import numpy as np
import pandas as pd

from h_testleri import fiyat_cek, sha256

ON_KAYIT = "ON_KAYIT_H7.md"
CIKTI = "data/h7"
MALIYET = 0.25
T_ESIK = 2.0
IS_ARALIK, OOS_ARALIK = ("2012-01", "2019-12"), ("2020-01", "2026-06")
VERI_BAS = datetime.date(2009, 1, 1)


# ------------------------------------------------------------------ veri
def evds_seri(kod, anahtar):
    """Gunluk EVDS serisi -> pd.Series (tarih -> float). Yillik parcalar halinde cekilir."""
    from tcmb_evds_veri import evds_veri_cek
    alan = kod.replace(".", "_")
    out = {}
    y = VERI_BAS.year
    while y <= datetime.date.today().year:
        bas, bit = datetime.date(y, 1, 1), datetime.date(y, 12, 31)
        for kayit in (evds_veri_cek(kod, bas, bit, anahtar).get("items") or []):
            v = kayit.get(alan, kayit.get(kod))
            try:
                out[pd.to_datetime(kayit["Tarih"], format="%d-%m-%Y")] = float(v)
            except (TypeError, ValueError, KeyError):
                pass
        y += 1
    return pd.Series(out).sort_index()


def vix_seri():
    import yfinance as yf
    df = yf.Ticker("^VIX").history(start=str(VERI_BAS), interval="1d", auto_adjust=False)
    s = df["Close"].dropna()
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    return s


def son_deger(s, t):
    x = s[s.index <= t]
    return float(x.iloc[-1]) if len(x) else np.nan


# ------------------------------------------------------------------ bayraklar
def aylik_tablo(xu, usd, faiz, vix):
    idx = xu.index
    me = sorted(pd.Series(idx, index=idx).groupby([idx.year, idx.month]).max())
    satir = []
    vix_once = vix.shift(1)                                 # bir onceki ABD islem gunu
    vix_med = vix_once.shift(1).rolling(252, min_periods=200).median()   # onceki 12 ay (gozlem haric)
    for i, t in enumerate(me):
        t = pd.Timestamp(t)
        r = {"ay": t.strftime("%Y-%m"), "t": t, "xu": float(xu.loc[t]), "usd": son_deger(usd, t), "faiz": son_deger(faiz, t)}
        v = vix_once[vix_once.index <= t]
        m = vix_med[vix_med.index <= t]
        r["vix"] = float(v.iloc[-1]) if len(v) else np.nan
        r["vix_med"] = float(m.iloc[-1]) if len(m) else np.nan
        satir.append(r)
    df = pd.DataFrame(satir).set_index("ay")
    df["usd_deg"] = df["usd"].pct_change()
    df["usd_med12"] = df["usd_deg"].shift(1).rolling(12, min_periods=12).median()
    df["faiz_deg3"] = df["faiz"] - df["faiz"].shift(3)
    df["S1_kur"] = np.where(df["usd_deg"].notna() & df["usd_med12"].notna(), (df["usd_deg"] < df["usd_med12"]).astype(float), np.nan)
    df["S2_faiz"] = np.where(df["faiz_deg3"].notna(), (df["faiz_deg3"] <= 0).astype(float), np.nan)
    df["S3_vix"] = np.where(df["vix"].notna() & df["vix_med"].notna(), (df["vix"] < df["vix_med"]).astype(float), np.nan)
    say = df[["S1_kur", "S2_faiz", "S3_vix"]].notna().sum(axis=1)
    acik = df[["S1_kur", "S2_faiz", "S3_vix"]].sum(axis=1)
    df["bayrak"] = np.where(say == 3, (acik >= 2).astype(float), np.nan)
    df["trend"] = (df["xu"] > df["xu"].rolling(10, min_periods=10).mean()).astype(float).where(df["xu"].rolling(10).count() == 10)
    # sonraki ay getirileri
    df["xu_sonraki"] = (df["xu"].shift(-1) / df["xu"] - 1) * 100
    df["usd_sonraki"] = (df["usd"].shift(-1) / df["usd"] - 1) * 100
    df["rf"] = df["faiz"] / 12
    df["fazla"] = df["xu_sonraki"] - df["rf"]
    df["xu_usd_sonraki"] = ((1 + df["xu_sonraki"] / 100) / (1 + df["usd_sonraki"] / 100) - 1) * 100
    return df


def welch(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    if len(a) < 3 or len(b) < 3:
        return {"n_acik": len(a), "n_kapali": len(b)}
    d = a.mean() - b.mean()
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return {"n_acik": len(a), "n_kapali": len(b), "ort_acik": round(float(a.mean()), 3), "ort_kapali": round(float(b.mean()), 3),
            "fark": round(float(d), 3), "t": round(float(d / se), 2) if se else None}


def donem(df, aralik):
    return df[(df.index >= aralik[0]) & (df.index <= aralik[1])]


def strateji(df, sutun="bayrak"):
    d = df.dropna(subset=[sutun, "fazla"]).copy()
    d["degisim"] = (d[sutun] != d[sutun].shift(1)).astype(float)
    d.iloc[0, d.columns.get_loc("degisim")] = 0.0
    d["str_fazla"] = np.where(d[sutun] == 1, d["fazla"], 0.0) - MALIYET * d["degisim"]
    return d


def ozet(df, sutun, aralik, deger="fazla"):
    d = donem(df.dropna(subset=[sutun, deger]), aralik)
    return welch(d.loc[d[sutun] == 1, deger], d.loc[d[sutun] == 0, deger])


def main():
    anahtar = os.environ.get("TCMB_EVDS_API_KEY")
    if not anahtar:
        raise SystemExit("TCMB_EVDS_API_KEY yok")
    xu_df, _ = fiyat_cek("XU100")
    xu = xu_df["Close"]
    xu = xu[xu.index >= pd.Timestamp(VERI_BAS)]
    usd, faiz, vix = evds_seri("TP.DK.USD.A.YTL", anahtar), evds_seri("TP.APIFON4", anahtar), vix_seri()
    df = aylik_tablo(xu, usd, faiz, vix)
    st = strateji(df)

    b_oos, b_is = ozet(df, "bayrak", OOS_ARALIK), ozet(df, "bayrak", IS_ARALIK)
    s_oos = donem(st, OOS_ARALIK)
    str_ort = round(float(s_oos["str_fazla"].mean()), 3) if len(s_oos) else None
    altut_ort = round(float(s_oos["fazla"].mean()), 3) if len(s_oos) else None
    k = {"K1_oos_fark_pozitif": (b_oos.get("fark") or -1) > 0,
         "K2_oos_t": (b_oos.get("t") or -99) > T_ESIK,
         "K3_oos_risk_kapali_ort_negatif": (b_oos.get("ort_kapali") if b_oos.get("ort_kapali") is not None else 1) < 0,
         "K4_strateji_altut_ustu": str_ort is not None and altut_ort is not None and str_ort > altut_ort,
         "K5_is_fark_pozitif": (b_is.get("fark") or -1) > 0}
    e = "GECTI" if all(k.values()) else ("ZAYIF" if k["K1_oos_fark_pozitif"] and k["K5_is_fark_pozitif"] else "ELENDI")

    tekil = {s: {"IS": ozet(df, s, IS_ARALIK), "OOS": ozet(df, s, OOS_ARALIK)} for s in ("S1_kur", "S2_faiz", "S3_vix", "trend")}
    usd_bazli = {"IS": ozet(df, "bayrak", IS_ARALIK, "xu_usd_sonraki"), "OOS": ozet(df, "bayrak", OOS_ARALIK, "xu_usd_sonraki")}
    roll = s_oos["str_fazla"].rolling(12).sum()
    son = df.dropna(subset=["bayrak"]).iloc[-1]
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1", "on_kayit_sha256": sha256(ON_KAYIT),
           "hukum": e, "kriterler": k, "birincil": {"IS": b_is, "OOS": b_oos},
           "strateji_oos": {"aylik_ort_fazla": str_ort, "altut_aylik_ort_fazla": altut_ort,
                            "risk_acik_ay_orani": round(float(s_oos["bayrak"].mean()), 3) if len(s_oos) else None,
                            "rejim_degisimi": int(s_oos["degisim"].sum()) if len(s_oos) else None,
                            "en_kotu_12_ay": round(float(roll.min()), 2) if roll.notna().any() else None},
           "tekil": tekil, "usd_bazli": usd_bazli,
           "taze": donem(df, ("2026-07", "2100-12"))[["bayrak", "fazla"]].reset_index().to_dict("records"),
           "guncel": {"ay_sonu": str(son.name), "bayrak": "RISK_ACIK" if son["bayrak"] == 1 else "RISK_KAPALI",
                      "S1_kur": son["S1_kur"], "S2_faiz": son["S2_faiz"], "S3_vix": son["S3_vix"], "trend": son["trend"],
                      "usd_1a_deg_pct": round(son["usd_deg"] * 100, 2), "usd_med12_pct": round(son["usd_med12"] * 100, 2),
                      "faiz": son["faiz"], "faiz_3a_deg": son["faiz_deg3"], "vix": round(son["vix"], 2), "vix_med": round(son["vix_med"], 2)},
           "veri": {"usd_ilk": str(usd.index.min().date()) if len(usd) else None, "faiz_ilk": str(faiz.index.min().date()) if len(faiz) else None,
                    "vix_ilk": str(vix.index.min().date()) if len(vix) else None, "ay_sayisi": len(df)}}
    os.makedirs(CIKTI, exist_ok=True)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    out["deneme_no"] = len(kayit["denemeler"]) + 1
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    df.drop(columns=["t"]).round(4).to_csv(f"{CIKTI}/aylik.csv")
    g = lambda d, a: (d or {}).get(a)
    L = ["# H7 Makro Risk Istahi Bayragi", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{(out['on_kayit_sha256'] or '-')[:16]}` | deneme no {out['deneme_no']} | t esigi {T_ESIK}", "",
         "Salt olcum, tavsiye degildir. Fazla getiri = XU100 sonraki ay getirisi - TL fonlama faizi/12 (aylik, yuzde puan).", "",
         "| Donem | RISK_ACIK ay (ort) | RISK_KAPALI ay (ort) | Fark | t |", "|---|---|---|---|---|",
         f"| IS {IS_ARALIK[0]}..{IS_ARALIK[1]} | {g(b_is,'n_acik')} ({g(b_is,'ort_acik')}) | {g(b_is,'n_kapali')} ({g(b_is,'ort_kapali')}) | {g(b_is,'fark')} | {g(b_is,'t')} |",
         f"| OOS {OOS_ARALIK[0]}..{OOS_ARALIK[1]} | {g(b_oos,'n_acik')} ({g(b_oos,'ort_acik')}) | {g(b_oos,'n_kapali')} ({g(b_oos,'ort_kapali')}) | {g(b_oos,'fark')} | {g(b_oos,'t')} |",
         "", f"## Hukum: **{e}**", ""] + [f"- {a}: {'EVET' if v else 'HAYIR'}" for a, v in k.items()]
    L += [f"- Strateji OOS: {out['strateji_oos']}", "", "## Tekil gostergeler ve trend (hukum vermez)", "",
          "| Gosterge | IS fark (t) | OOS fark (t) | OOS acik/kapali ay |", "|---|---|---|---|"]
    for s, v in tekil.items():
        L.append(f"| {s} | {g(v['IS'],'fark')} ({g(v['IS'],'t')}) | {g(v['OOS'],'fark')} ({g(v['OOS'],'t')}) | {g(v['OOS'],'n_acik')}/{g(v['OOS'],'n_kapali')} |")
    L += ["", f"- USD bazli XU100 (bayrak) IS: {usd_bazli['IS']} | OOS: {usd_bazli['OOS']}",
          "", f"## Guncel bayrak ({out['guncel']['ay_sonu']}): **{out['guncel']['bayrak']}** (gozlem amaclidir)", "", f"- {out['guncel']}",
          "", f"Veri baslangiclari: {out['veri']}"]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": out["on_kayit_sha256"],
                               "git_sha": os.environ.get("GITHUB_SHA"), "hukum": e})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("H7", e, "OOS", b_oos, "IS", b_is)


if __name__ == "__main__":
    main()
