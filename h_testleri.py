"""
H1-H3 HIPOTEZ TESTLERI (27.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Tanimlar ve gecme kriterleri: ON_KAYIT_H1_H3.md (bu betikten ONCE commit edilir).
Bu betik on kayittaki parametreleri UYGULAR; parametre secmez. Sonuca on kayit dosyasinin
SHA-256 parmak izi yazilir; her calisma data/h_testleri/deneme_kaydi.json'a eklenir.

H1 kisa vadeli sektore gore donus | H2 giris zamanlamasi | H3 sert dusus sonrasi T+10
Cikti: data/h_testleri/sonuc.json, data/h_testleri/sonuc.md, data/h_testleri/deneme_kaydi.json
"""
import os, json, math, hashlib, datetime
from collections import defaultdict

import numpy as np
import pandas as pd

from alarm_karne import SEKTOR, kumelenmis

ON_KAYIT = "ON_KAYIT_H1_H3.md"
CIKTI = "data/h_testleri"
BAS = "2015-09-01"
IS_BAS, IS_SON = "2016-01-01", "2022-12-31"
OOS_BAS, OOS_SON = "2023-01-01", "2026-06-30"
MALIYET = 0.25           # %, gidis-donus
T_ESIK = 2.39            # Bonferroni, 3 birincil test
KRIZ_ESIK = 0.05         # XU100 |gunluk| >= %5 -> yeni pozisyon yok
H1_P = {"geri": 5, "dilim": 0.20, "tutma": 5, "min_hisse": 10, "min_secim": 2}
H3_P = {"dusus": -0.08, "tutma": 10, "piyasa_dusus": -0.04}
H2_P = {"esik_puan": 0.10}
SAGLAMLIK_BIST100 = os.environ.get("SAGLAMLIK_BIST100", "1") == "1"


# ------------------------------------------------------------------ veri
def evren_oku():
    import yaml
    u = yaml.safe_load(open("config/universe.yml", encoding="utf-8"))
    return list(u["symbols"]), dict(u.get("fallback_symbols") or {})


def bist100_oku():
    out = []
    for s in open("config/bist100_uyeler.txt", encoding="utf-8"):
        s = s.split("#")[0].strip().upper()
        if s and s not in out:
            out.append(s)
    return out


def _cek(kod, adj):
    import yfinance as yf
    df = yf.Ticker(kod + ".IS").history(start=BAS, interval="1d", auto_adjust=adj)
    df = df[df["Close"] > 0].dropna(subset=["Close"])
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df[["Open", "Close"]]


def fiyat_cek(kod, adj=False, eski=None):
    """(DataFrame[Open, Close], bolunme_gunleri). Bedelsiz duzeltmesi ayni carpanla Open'a da uygulanir.
    Yeni kodun gecmisi kisaysa eski kodla (fallback) eklenir, birlesme noktasinda olceklenir."""
    from ma610_tarama import bolunme_duzelt
    df = _cek(kod, adj)
    if eski and (df.empty or df.index[0] > pd.Timestamp("2016-06-30")):
        try:
            od = _cek(eski, adj)
            if not df.empty:
                od = od[od.index < df.index[0]]
                if not od.empty:
                    od = od * (df["Close"].iloc[0] / od["Close"].iloc[-1])
            df = pd.concat([od, df]).sort_index()
        except Exception:
            pass
    if df.empty:
        return df, set()
    ham = df["Close"]
    duz, olay = bolunme_duzelt(ham)
    if kod == "XU100" and float(ham.pct_change().abs().max()) <= 0.25:
        duz, olay = ham, []
    carpan = duz / ham
    return pd.DataFrame({"Open": df["Open"] * carpan, "Close": duz}), {pd.Timestamp(t) for t, _ in olay}


def panel_kur(semboller, fallback, adj=False):
    C, O, bol, hata = {}, {}, {}, {}
    for k in semboller:
        try:
            df, b = fiyat_cek(k, adj, fallback.get(k))
            if len(df) < 60:
                raise ValueError(f"az veri ({len(df)})")
            C[k], O[k], bol[k] = df["Close"], df["Open"], b
        except Exception as e:
            hata[k] = str(e)[:120]
    return pd.DataFrame(C).sort_index(), pd.DataFrame(O).sort_index(), bol, hata


# ------------------------------------------------------------------ istatistik
def newey_west(x, lag):
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], dtype=float)
    n = len(x)
    if n < lag + 5:
        return None
    m = x.mean()
    e = x - m
    var = (e @ e) / n
    for l in range(1, lag + 1):
        var += 2 * (1 - l / (lag + 1)) * (e[l:] @ e[:-l]) / n
    se = math.sqrt(var / n) if var > 0 else None
    return {"n": n, "ort": round(float(m), 4), "t": round(float(m / se), 2) if se else None}


def hafta_kume(seri):
    s = seri.dropna()
    if len(s) < 3:
        return {"n": len(s)}
    kume = ["%d-W%02d" % d.isocalendar()[:2] for d in s.index]
    k = kumelenmis(list(s.values), kume)
    return {"n": len(s), "kume": k["G"], "ort": round(k["ort"], 4), "t": None if k["t"] is None else round(k["t"], 2)}


def donem(seri, bas, son):
    return seri[(seri.index >= pd.Timestamp(bas)) & (seri.index <= pd.Timestamp(son))]


def yillik(seri):
    s = seri[seri.index <= pd.Timestamp(OOS_SON)].dropna()
    g = s.groupby(s.index.year).mean()
    return {int(y): round(float(v), 3) for y, v in g.items()}


# ------------------------------------------------------------------ yardimci paneller
def sektor_sepeti(R, sektor_map):
    """R: getiri paneli (tarih x sembol). Donus: her hisse icin akran (ayni sektor, kendisi haric) ortalamasi;
    akran yoksa evrenin geri kalaninin ortalamasi."""
    akran = pd.DataFrame(index=R.index, columns=R.columns, dtype=float)
    gecerli = R.notna()
    top_hepsi, say_hepsi = R.sum(axis=1, min_count=1).fillna(0), gecerli.sum(axis=1)
    gruplar = defaultdict(list)
    for k in R.columns:
        gruplar[sektor_map.get(k, "_" + k)].append(k)
    for s, uyeler in gruplar.items():
        top_s = R[uyeler].sum(axis=1, min_count=1).fillna(0)
        say_s = gecerli[uyeler].sum(axis=1)
        for k in uyeler:
            kendi = R[k].fillna(0)
            ks = gecerli[k].astype(int)
            n_s = say_s - ks
            n_h = say_hepsi - ks
            sek = (top_s - kendi) / n_s.where(n_s > 0)
            hep = (top_hepsi - kendi) / n_h.where(n_h > 0)
            akran[k] = sek.where(n_s > 0, hep)
    return akran


def kriz_gunleri(xu):
    r = xu.pct_change().abs()
    return set(r[r >= KRIZ_ESIK].index)


# ------------------------------------------------------------------ H1
def h1_seri(C, xu, sektor_map, geri, dilim, tutma, haric_sektor=None):
    if haric_sektor:
        C = C[[k for k in C.columns if sektor_map.get(k) != haric_sektor]]
    rg = C / C.shift(geri) - 1
    artik = rg - sektor_sepeti(rg, sektor_map)
    f = C.shift(-tutma) / C - 1
    f_akran = sektor_sepeti(f, sektor_map)
    f_ew = f.mean(axis=1)
    xu_f = (xu.shift(-tutma) / xu - 1).reindex(C.index)
    kriz = kriz_gunleri(xu)
    A, F, FA = artik.to_numpy(float), f.to_numpy(float), f_akran.to_numpy(float)
    XF, EW = xu_f.to_numpy(float), f_ew.to_numpy(float)
    satir = []
    for i, t in enumerate(C.index):
        if t in kriz or not np.isfinite(XF[i]):
            continue
        ok = np.isfinite(A[i]) & np.isfinite(F[i]) & np.isfinite(FA[i])
        n = int(ok.sum())
        if n < H1_P["min_hisse"]:
            continue
        k = max(H1_P["min_secim"], int(math.floor(dilim * n)))
        idx = np.flatnonzero(ok)
        sec = idx[np.argsort(A[i, idx], kind="stable")[:k]]
        brut = float(F[i, sec].mean()) * 100
        sek = float((F[i, sec] - FA[i, sec]).mean()) * 100
        satir.append({"t": t, "n": n, "secim": k, "brut": brut,
                      "sek_net": sek - MALIYET, "xu_net": brut - XF[i] * 100 - MALIYET,
                      "ew_net": brut - EW[i] * 100 - MALIYET})
    return pd.DataFrame(satir).set_index("t") if satir else pd.DataFrame()


def h1_ozet(df, tutma, alan="sek_net"):
    s = df[alan]
    return {"IS": newey_west(donem(s, IS_BAS, IS_SON), tutma - 1),
            "OOS": newey_west(donem(s, OOS_BAS, OOS_SON), tutma - 1),
            "taze": newey_west(donem(s, "2026-07-01", "2100-01-01"), tutma - 1),
            "yillik": yillik(s)}


# ------------------------------------------------------------------ H3
def h3_seri(C, xu, sektor_map, bol, haric_sektor=None):
    tut = H3_P["tutma"]
    d = C / C.shift(1) - 1
    f = C.shift(-tut) / C - 1
    f_akran = sektor_sepeti(f, sektor_map)
    xu_d = xu.pct_change().reindex(C.index)
    xu_f = (xu.shift(-tut) / xu - 1).reindex(C.index)
    D, F, FA = d.to_numpy(float), f.to_numpy(float), f_akran.to_numpy(float)
    XD, XF = xu_d.to_numpy(float), xu_f.to_numpy(float)
    kolon = list(C.columns)
    izin = np.array([not haric_sektor or sektor_map.get(k) != haric_sektor for k in kolon])
    bol_maske = np.zeros(D.shape, dtype=bool)
    poz = {t: i for i, t in enumerate(C.index)}
    for j, k in enumerate(kolon):
        for t in bol.get(k, set()):
            if t in poz:
                bol_maske[poz[t], j] = True
    OLAY = (D <= H3_P["dusus"]) & np.isfinite(F) & ~bol_maske & izin[None, :]
    satir = []
    for i, t in enumerate(C.index):
        if not np.isfinite(XD[i]) or abs(XD[i]) >= KRIZ_ESIK or not np.isfinite(XF[i]):
            continue
        sec = np.flatnonzero(OLAY[i])
        if not len(sec):
            continue
        brut = float(F[i, sec].mean()) * 100
        fa = FA[i, sec]
        sek = float(np.nanmean(F[i, sec] - fa)) * 100 if np.isfinite(fa).any() else np.nan
        satir.append({"t": t, "olay_sayisi": len(sec), "semboller": ",".join(kolon[j] for j in sec), "brut": brut,
                      "xu_net": brut - XF[i] * 100 - MALIYET, "sek_net": sek - MALIYET})
    return pd.DataFrame(satir).set_index("t") if satir else pd.DataFrame()


def h3_ozet(df, alan="xu_net"):
    s = df[alan]
    return {"IS": hafta_kume(donem(s, IS_BAS, IS_SON)), "OOS": hafta_kume(donem(s, OOS_BAS, OOS_SON)),
            "taze": hafta_kume(donem(s, "2026-07-01", "2100-01-01")), "yillik": yillik(s),
            "olay_toplam": int(df.loc[df.index <= pd.Timestamp(OOS_SON), "olay_sayisi"].sum())}


def h3_piyasa(xu):
    tut = H3_P["tutma"]
    r = xu.pct_change()
    f = (xu.shift(-tut) / xu - 1) * 100
    gun = r[r <= H3_P["piyasa_dusus"]].index
    sart = f.reindex(gun).dropna()
    return {"olay": int(len(sart)), "sonrasi_10g_ort": round(float(sart.mean()), 3) if len(sart) else None,
            "kosulsuz_10g_ort": round(float(f.dropna().mean()), 3),
            "not": "Mutlak (nominal) getiri; yalniz bilgi. Ust uste binen pencereler."}


# ------------------------------------------------------------------ H2
def h2_alarm():
    yol = "data/alarm_karne_olaylar.csv"
    if not os.path.exists(yol):
        return {"durum": "alarm_karne_olaylar.csv yok"}
    d = pd.read_csv(yol)
    d = d[d["yon"] == "YUKARI"].copy()
    d["t_yerel"] = pd.to_datetime(d["zaman_utc"], utc=True).dt.tz_convert(None) + pd.Timedelta(hours=3)
    d = d[d["t_yerel"].dt.date.astype(str) == d["taban_gun"]]        # alarm, taban gunu seans icinde
    hm = d["t_yerel"].dt.hour * 60 + d["t_yerel"].dt.minute
    d = d[(hm >= 600) & (hm <= 1090)]                                   # 10:00 - 18:10
    if "fiyat_uyusmazligi" in d.columns:
        d = d[d["fiyat_uyusmazligi"] != True]                            # noqa: E712
    d = d.dropna(subset=["giris_kaymasi_pct"]).sort_values("zaman_utc").drop_duplicates(["sembol", "taban_gun"])
    d["avantaj"] = (1 / (1 + d["giris_kaymasi_pct"] / 100) - 1) * 100
    hm = d["t_yerel"].dt.hour * 60 + d["t_yerel"].dt.minute
    dilimler = [("10:00-10:30", 600, 630), ("10:30-12:30", 630, 750), ("12:30-16:00", 750, 960),
                ("16:00-18:10", 960, 1091)]

    def ozet(x):
        if len(x) < 3:
            return {"n": len(x)}
        k = kumelenmis(list(x["avantaj"]), list(x["taban_gun"]))
        return {"n": len(x), "gun": k["G"], "ort": round(k["ort"], 3), "t": None if k["t"] is None else round(k["t"], 2)}

    tum = ozet(d)
    o, t = tum.get("ort"), tum.get("t")
    if o is None or o <= 0:
        etiket = "ELENDI"
    elif o > H2_P["esik_puan"] and t is not None and t > T_ESIK:
        etiket = "GECTI"
    else:
        etiket = "ZAYIF"
    return {"tum": tum, "seans_dilimi": {ad: ozet(d[(hm >= a) & (hm < b)]) for ad, a, b in dilimler},
            "tur": {tur: ozet(x) for tur, x in d.groupby("sinyal")},
            "aralik": [str(d["taban_gun"].min()), str(d["taban_gun"].max())] if len(d) else None,
            "hukum": etiket}


def h2_gece_gunduz(C, O, xu_o, xu_c):
    gunduz = (C / O - 1).mean(axis=1) * 100
    gece = (O / C.shift(1) - 1).mean(axis=1) * 100
    xg = (xu_c / xu_o - 1) * 100
    xn = (xu_o / xu_c.shift(1) - 1) * 100
    df = pd.DataFrame({"gunduz": gunduz, "gece": gece, "gunduz_rel": gunduz - xg, "gece_rel": gece - xn}).dropna()
    df = df[df.index >= pd.Timestamp(IS_BAS)]
    yil = df.groupby(df.index.year).mean().round(3)
    top = df.mean()
    return {"ort_gunluk_pct": {k: round(float(v), 4) for k, v in top.items()},
            "yillik": {int(y): r.to_dict() for y, r in yil.iterrows()},
            "not": "Yahoo XU100 acilis verisi guvenilir olmayabilir; _rel sutunlari dikkatle okunmali. Yalniz bilgi."}


# ------------------------------------------------------------------ hukum
def hukum_ver(ana, k4):
    o_oos, t_oos = (ana["OOS"] or {}).get("ort"), (ana["OOS"] or {}).get("t")
    o_is = (ana["IS"] or {}).get("ort")
    yil = ana["yillik"]
    k = {"K1_oos_ort_pozitif": o_oos is not None and o_oos > 0,
         "K2_oos_t": t_oos is not None and t_oos > T_ESIK,
         "K3_yillarin_60pct_pozitif": bool(yil) and sum(v > 0 for v in yil.values()) / len(yil) >= 0.60,
         "K4_sektor_cikarma": bool(k4) and all(v is not None and v > 0 for v in k4.values()),
         "K5_is_ort_pozitif": o_is is not None and o_is > 0}
    if all(k.values()):
        e = "GECTI"
    elif k["K1_oos_ort_pozitif"] and k["K5_is_ort_pozitif"]:
        e = "ZAYIF"
    else:
        e = "ELENDI"
    return e, k


def sha256(yol):
    return hashlib.sha256(open(yol, "rb").read()).hexdigest() if os.path.exists(yol) else None


# ------------------------------------------------------------------ rapor
def md_yaz(out):
    L = ["# H1-H3 Hipotez Testleri", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit SHA-256 `{(out['on_kayit_sha256'] or '-')[:16]}` | "
         f"deneme no {out['deneme_no']} | maliyet {MALIYET}% | t esigi {T_ESIK} (Bonferroni)", "",
         "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H1_H3.md'de; bu rapor yalniz uygular.", "",
         "## Hukumler", "", "| Hipotez | Birincil metrik | IS ort (t) | OOS ort (t) | Taze donem ort (t) | Hukum |", "|---|---|---|---|---|---|"]
    for ad, r in (("H1", out["H1"]), ("H3", out["H3"])):
        a = r["birincil"]
        f = lambda x: f"{(x or {}).get('ort')} ({(x or {}).get('t')})"
        L.append(f"| {ad} | {r['metrik']} | {f(a['IS'])} | {f(a['OOS'])} | {f(a['taze'])} | **{r['hukum']}** |")
    h2 = out["H2"]["alarm"]
    L.append(f"| H2 | Kapanis girisi avantaji (puan) | - | {(h2.get('tum') or {}).get('ort')} ({(h2.get('tum') or {}).get('t')}), "
             f"n={(h2.get('tum') or {}).get('n')} | - | **{h2.get('hukum')}** |")
    for ad in ("H1", "H3"):
        r = out[ad]
        L += ["", f"## {ad} kriterleri", ""] + [f"- {k}: {'EVET' if v else 'HAYIR'}" for k, v in r["kriterler"].items()]
        L.append(f"- Sektor cikarma OOS ortalamalari: {r['sektor_cikarma_oos']}")
        L.append(f"- Yillik ortalamalar: {r['birincil']['yillik']}")
        for k, v in r.get("diger_metrikler", {}).items():
            L.append(f"- {k}: OOS {v['OOS']}")
        if "temettu_duzeltmeli" in r:
            L.append(f"- Temettu duzeltmeli (saglamlik) OOS: {r['temettu_duzeltmeli']['OOS']}")
    g = out["H1"].get("izgara")
    if g:
        L += ["", "## H1 saglamlik izgarasi (OOS sektore gore net; parametre secimi icin KULLANILMAZ)", "",
              "| geri | dilim | tutma | n | ort | t |", "|---|---|---|---|---|---|"]
        for s in g:
            L.append(f"| {s['geri']} | {s['dilim']} | {s['tutma']} | {s.get('n')} | {s.get('ort')} | {s.get('t')} |")
    if out["H1"].get("bist100"):
        L.append(f"\nH1 BIST100 evreni (saglamlik) OOS: {out['H1']['bist100']['OOS']}")
    L += ["", "## H2 ayrintisi", "", f"- Seans dilimi: {h2.get('seans_dilimi')}", f"- Ture gore: {h2.get('tur')}",
          f"- 10 yillik gece/gunduz (bilgi): {out['H2']['gece_gunduz']['ort_gunluk_pct']}",
          "", "## H3 ek bilgi", "", f"- Piyasa geneli <= -4% gunleri: {out['H3']['piyasa_geneli']}",
          "", "## Veri", "", f"- Fiyati cekilemeyen: {out['veri']['hata'] or 'yok'}",
          f"- Sembol baslangic tarihleri: {out['veri']['ilk_tarih']}",
          "", "Bilinen sinirlar: hayatta kalma yanliligi (donus stratejilerini olumlu yanli gosterir), tek kaynak Yahoo, "
          "fiyat limiti ve acik satis modellenmedi."]
    return "\n".join(L) + "\n"


def main():
    sembol, fb = evren_oku()
    C, O, bol, hata = panel_kur(sembol, fb)
    xu_df, _ = fiyat_cek("XU100")
    xu, xu_o = xu_df["Close"].reindex(C.index).ffill(), xu_df["Open"].reindex(C.index).ffill()
    C = C[C.index >= pd.Timestamp("2015-10-01")]
    xu, xu_o, O = xu.reindex(C.index), xu_o.reindex(C.index), O.reindex(C.index)
    sektor_map = dict(SEKTOR)
    sektorler = sorted({sektor_map[k] for k in C.columns if k in sektor_map})

    # H1
    p = H1_P
    h1 = h1_seri(C, xu, sektor_map, p["geri"], p["dilim"], p["tutma"])
    h1_ana = h1_ozet(h1, p["tutma"])
    h1_k4 = {}
    for s in sektorler:
        hs = h1_seri(C, xu, sektor_map, p["geri"], p["dilim"], p["tutma"], haric_sektor=s)
        h1_k4[s] = (h1_ozet(hs, p["tutma"])["OOS"] or {}).get("ort") if len(hs) else None
    e1, k1 = hukum_ver(h1_ana, h1_k4)
    izgara = []
    for g in (3, 5, 10):
        for dl in (0.10, 0.20, 0.30):
            for tt in (3, 5, 10):
                hs = h1_seri(C, xu, sektor_map, g, dl, tt)
                o = h1_ozet(hs, tt)["OOS"] or {}
                izgara.append({"geri": g, "dilim": dl, "tutma": tt, **o})
    out_h1 = {"metrik": "sektor sepetine gore net, 5 gun", "birincil": h1_ana, "hukum": e1, "kriterler": k1,
              "sektor_cikarma_oos": h1_k4, "izgara": izgara,
              "diger_metrikler": {"XU100'e gore net": h1_ozet(h1, p["tutma"], "xu_net"),
                                  "evren ortalamasina gore net": h1_ozet(h1, p["tutma"], "ew_net")},
              "ort_secim": round(float(h1["secim"].mean()), 1) if len(h1) else None}

    # H3
    h3 = h3_seri(C, xu, sektor_map, bol)
    h3_ana = h3_ozet(h3) if len(h3) else {"IS": None, "OOS": None, "taze": None, "yillik": {}}
    h3_k4 = {}
    for s in sektorler:
        hs = h3_seri(C, xu, sektor_map, bol, haric_sektor=s)
        h3_k4[s] = (h3_ozet(hs)["OOS"] or {}).get("ort") if len(hs) else None
    e3, k3 = hukum_ver(h3_ana, h3_k4)
    out_h3 = {"metrik": "XU100'e gore net, 10 gun", "birincil": h3_ana, "hukum": e3, "kriterler": k3,
              "sektor_cikarma_oos": h3_k4, "piyasa_geneli": h3_piyasa(xu),
              "diger_metrikler": {"sektor sepetine gore net": h3_ozet(h3, "sek_net") if len(h3) else {}}}

    # temettu duzeltmeli saglamlik
    try:
        Ca, _, bola, _ = panel_kur(list(C.columns), fb, adj=True)
        Ca = Ca.reindex(C.index)
        out_h1["temettu_duzeltmeli"] = h1_ozet(h1_seri(Ca, xu, sektor_map, p["geri"], p["dilim"], p["tutma"]), p["tutma"])
        h3a = h3_seri(Ca, xu, sektor_map, bola)
        if len(h3a):
            out_h3["temettu_duzeltmeli"] = h3_ozet(h3a)
    except Exception as e:
        out_h1["temettu_duzeltmeli_hata"] = str(e)[:150]

    # BIST100 saglamlik (H1)
    if SAGLAMLIK_BIST100:
        try:
            C1, _, _, _ = panel_kur(bist100_oku(), fb)
            C1 = C1.reindex(C.index)
            out_h1["bist100"] = h1_ozet(h1_seri(C1, xu, sektor_map, p["geri"], p["dilim"], p["tutma"]), p["tutma"])
        except Exception as e:
            out_h1["bist100_hata"] = str(e)[:150]

    # H2
    out_h2 = {"alarm": h2_alarm(), "gece_gunduz": h2_gece_gunduz(C, O, xu_o, xu)}

    os.makedirs(CIKTI, exist_ok=True)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    sha = sha256(ON_KAYIT)
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1",
           "on_kayit_sha256": sha, "deneme_no": len(kayit["denemeler"]) + 1,
           "parametreler": {"MALIYET": MALIYET, "T_ESIK": T_ESIK, "KRIZ_ESIK": KRIZ_ESIK, "H1": H1_P, "H2": H2_P,
                            "H3": H3_P, "IS": [IS_BAS, IS_SON], "OOS": [OOS_BAS, OOS_SON]},
           "H1": out_h1, "H2": out_h2, "H3": out_h3,
           "veri": {"hata": hata, "ilk_tarih": {k: str(C[k].first_valid_index().date()) for k in C.columns
                                                if C[k].first_valid_index() is not None},
                    "son_gun": str(C.index[-1].date())}}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write(md_yaz(out))
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": os.environ.get("GITHUB_SHA"),
                               "hukum": {"H1": e1, "H2": out_h2["alarm"].get("hukum"), "H3": e3}})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("H1", e1, h1_ana["OOS"], "| H2", out_h2["alarm"].get("hukum"), out_h2["alarm"].get("tum"), "| H3", e3, h3_ana["OOS"])


if __name__ == "__main__":
    main()
