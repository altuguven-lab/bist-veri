"""
H6 KURUMSAL TARZDA COK FAKTORLU AYLIK SIRALAMA (30.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H6.md (bu betikten ONCE commit edilir). Parametre secmez.
Girdi : data/temel/ham_*.json, config/bist100_uyeler.txt, config/kapsam_disi.txt, fiyat (yfinance)
Cikti : data/h6/sonuc.json, data/h6/sonuc.md, data/h6/aylik.csv, data/h6/guncel_siralama.csv, data/h6/deneme_kaydi.json
"""
import os, json, math, datetime
import numpy as np
import pandas as pd

from h_testleri import panel_kur, fiyat_cek, newey_west, sha256
from h4_bilanco_surprizi import kalem, liste_oku, SEKTOR100, GECIKME

ON_KAYIT = "ON_KAYIT_H6.md"
CIKTI = "data/h6"
MALIYET = 0.25
T_ESIK = 2.0
DILIM = 0.20
MIN_SIRALI = 30
MIN_FAKTOR = 3
NW_LAG = 2
BH_Q = 0.10
BIL_IS, BIL_OOS = ("2021-04", "2023-12"), ("2024-01", "2026-06")
FIY_IS, FIY_OOS = ("2016-01", "2022-12"), ("2023-01", "2026-06")
FAKTORLER = ["F1_momentum", "F2_dusuk_oynaklik", "F3_deger", "F4_kalite", "F5_bilanco_surprizi"]


# ------------------------------------------------------------------ temel veri
def temel_tablo(kod):
    """Bilinirlik tarihine gore sirali liste: [(bilinir_tarih, ttm, oz, oz_onceki_yil, S)], guncel adet."""
    yol = f"data/temel/ham_{kod}.json"
    if not os.path.exists(yol):
        return [], None
    ham = json.load(open(yol, encoding="utf-8"))
    kar, oz, sermaye = kalem(ham, "TRY", "3Z"), kalem(ham, "TRY", "2O"), kalem(ham, "TRY", "2OA")
    adet = sermaye[max(sermaye)] if sermaye else None
    out = []
    for (y, p) in sorted(kar):
        if p == 12:
            ttm = kar[(y, p)]
        elif (y - 1, 12) in kar and (y - 1, p) in kar:
            ttm = kar[(y, p)] + kar[(y - 1, 12)] - kar[(y - 1, p)]
        else:
            ttm = None
        o, o0 = oz.get((y, p)), oz.get((y - 1, p))
        k0 = kar.get((y - 1, p))
        S = (kar[(y, p)] - k0) / o0 if (k0 is not None and o0 and o0 > 0) else None
        son = pd.Timestamp(year=y, month=p, day=1) + pd.offsets.MonthEnd(0)
        out.append((son + pd.Timedelta(days=GECIKME[p]), ttm, o, o0, S))
    out.sort(key=lambda x: x[0])
    return out, adet


def bilinen(tablo, t):
    son = None
    for x in tablo:
        if x[0] <= t:
            son = x
        else:
            break
    return son


# ------------------------------------------------------------------ faktorler
def yuzdelik(s, ters=False):
    s = s.dropna()
    if len(s) < 2:
        return pd.Series(dtype=float)
    r = s.rank(pct=True)
    return 1 - r + 1 / len(s) if ters else r


def faktor_tablosu(C, R, temel, t_idx):
    t = C.index[t_idx]
    f = pd.DataFrame(index=C.columns, columns=FAKTORLER, dtype=float)
    if t_idx >= 252:
        f["F1_momentum"] = C.iloc[t_idx - 21] / C.iloc[t_idx - 252] - 1
        w = R.iloc[t_idx - 251:t_idx + 1]
        vol = w.std()
        vol[w.notna().sum() < 200] = np.nan
        f["F2_dusuk_oynaklik"] = vol
    ep, bp = {}, {}
    for k in C.columns:
        tab, adet = temel.get(k, ([], None))
        x = bilinen(tab, t)
        if not x:
            continue
        _, ttm, o, o0, S = x
        fiyat = C.iat[t_idx, C.columns.get_loc(k)]
        mc = fiyat * adet if (adet and pd.notna(fiyat)) else None
        if mc and mc > 0:
            if ttm is not None:
                ep[k] = ttm / mc
            if o is not None:
                bp[k] = o / mc
        if ttm is not None and o:
            ort = (o + o0) / 2 if o0 else o
            if ort > 0:
                f.at[k, "F4_kalite"] = ttm / ort
        if S is not None:
            f.at[k, "F5_bilanco_surprizi"] = S
    r_ep, r_bp = yuzdelik(pd.Series(ep, dtype=float)), yuzdelik(pd.Series(bp, dtype=float))
    deger = pd.concat([r_ep, r_bp], axis=1).mean(axis=1)
    f["F3_deger"] = deger.reindex(C.columns)
    return f


def siralar(f):
    r = pd.DataFrame(index=f.index)
    for c in FAKTORLER:
        r[c] = yuzdelik(f[c], ters=(c == "F2_dusuk_oynaklik")).reindex(f.index)
    return r


# ------------------------------------------------------------------ portfoy
def ay_sonlari(idx):
    s = pd.Series(idx, index=idx)
    return list(s.groupby([idx.year, idx.month]).max().values)


def portfoy_serisi(C, xu, ay_pos, skorlar, alt_dilim=False):
    """skorlar: {t_idx: Series}. Donus DataFrame (ay, net_xu, net_ew, brut, maliyet, devir, n)."""
    satir, onceki = [], set()
    for a in range(len(ay_pos) - 1):
        i0, i1 = ay_pos[a], ay_pos[a + 1]
        sk = skorlar.get(i0)
        if sk is None:
            continue
        sk = sk.dropna()
        if len(sk) < MIN_SIRALI:
            continue
        n = max(5, int(math.floor(DILIM * len(sk))))
        sec = list(sk.nsmallest(n).index if alt_dilim else sk.nlargest(n).index)
        r = (C.iloc[i1][sec] / C.iloc[i0][sec] - 1).dropna()
        if r.empty:
            continue
        brut = float(r.mean()) * 100
        ew = float((C.iloc[i1][sk.index] / C.iloc[i0][sk.index] - 1).dropna().mean()) * 100
        xr = float(xu.iloc[i1] / xu.iloc[i0] - 1) * 100
        yeni = set(sec)
        devir = 1.0 if not onceki else len(yeni - onceki) / len(yeni)
        mal = MALIYET * devir
        satir.append({"ay": C.index[i0].strftime("%Y-%m"), "brut": brut, "maliyet": mal, "devir": devir, "n": len(sec),
                      "net_xu": brut - mal - xr, "net_ew": brut - mal - ew, "xu": xr})
        onceki = yeni
    return pd.DataFrame(satir)


def donem_ozet(df, alan, aralik):
    if df.empty:
        return {"n": 0}
    x = df[(df["ay"] >= aralik[0]) & (df["ay"] <= aralik[1])][alan]
    r = newey_west(list(x.values), NW_LAG)
    if not r:
        return {"n": len(x)}
    r["pozitif_pct"] = round(100 * float((x > 0).mean()), 1)
    return r


def p_deger(t):
    return None if t is None else math.erfc(abs(t) / math.sqrt(2))


def bh(pler):
    g = sorted([(p, k) for k, p in pler.items() if p is not None])
    m, esik = len(g), 0
    for i, (p, _) in enumerate(g, 1):
        if p <= BH_Q * i / m:
            esik = i
    return {k: (i <= esik) for i, (_, k) in enumerate(g, 1)}


# ------------------------------------------------------------------ ana
def calistir(C, xu, temel, haric_sektor=None, banka_haric=False):
    kol = [k for k in C.columns if not (haric_sektor and SEKTOR100.get(k) == haric_sektor)
           and not (banka_haric and SEKTOR100.get(k) == "Banka")]
    C = C[kol]
    R = C.pct_change()
    ay_pos = [C.index.get_loc(t) for t in ay_sonlari(C.index)]
    bilesik, tekil = {}, {c: {} for c in FAKTORLER}
    for i0 in ay_pos:
        r = siralar(faktor_tablosu(C, R, temel, i0))
        say = r.notna().sum(axis=1)
        bilesik[i0] = r.mean(axis=1).where(say >= MIN_FAKTOR)
        for c in FAKTORLER:
            tekil[c][i0] = r[c]
    return C, ay_pos, bilesik, tekil


def main():
    kd = set(liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in liste_oku("config/bist100_uyeler.txt") if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    C, _, _, hata = panel_kur(evren, {})
    C = C[C.index >= pd.Timestamp("2015-01-01")]
    xu = fiyat_cek("XU100")[0]["Close"].reindex(C.index).ffill()
    temel = {k: temel_tablo(k) for k in C.columns}

    C2, ay_pos, bilesik, tekil = calistir(C, xu, temel)
    ana = portfoy_serisi(C2, xu, ay_pos, bilesik)
    # BIRINCIL: evren esit agirlikli ortalamasina gore (net_ew). XU100'e gore (net_xu) ikincil.
    b_oos, b_is = donem_ozet(ana, "net_ew", BIL_OOS), donem_ozet(ana, "net_ew", BIL_IS)
    yil = {}
    if not ana.empty:
        x = ana[(ana["ay"] >= BIL_OOS[0]) & (ana["ay"] <= BIL_OOS[1])]
        yil = {y: round(float(v), 3) for y, v in x.groupby(x["ay"].str[:4])["net_ew"].mean().items()}
    k4 = {}
    for s in sorted({SEKTOR100[k] for k in C.columns if k in SEKTOR100}):
        Cs, ps, bs, _ = calistir(C, xu, temel, haric_sektor=s)
        k4[s] = donem_ozet(portfoy_serisi(Cs, xu, ps, bs), "net_ew", BIL_OOS).get("ort")
    k = {"K1_oos_ort_pozitif": (b_oos.get("ort") or -1) > 0,
         "K2_oos_t": (b_oos.get("t") or -99) > T_ESIK,
         "K3_oos_yillarin_2si_pozitif": sum(v > 0 for v in yil.values()) >= 2,
         "K4_sektor_cikarma": bool(k4) and all(v is not None and v > 0 for v in k4.values()),
         "K5_is_ort_pozitif": (b_is.get("ort") or -1) > 0}
    e = "GECTI" if all(k.values()) else ("ZAYIF" if k["K1_oos_ort_pozitif"] and k["K5_is_ort_pozitif"] else "ELENDI")

    faktor = {}
    for c in FAKTORLER:
        IS, OOS = (FIY_IS, FIY_OOS) if c in ("F1_momentum", "F2_dusuk_oynaklik") else (BIL_IS, BIL_OOS)
        ust = portfoy_serisi(C2, xu, ay_pos, tekil[c])
        alt = portfoy_serisi(C2, xu, ay_pos, tekil[c], alt_dilim=True)
        fark = pd.DataFrame()
        if not ust.empty and not alt.empty:
            fark = ust[["ay", "brut"]].merge(alt[["ay", "brut"]], on="ay", suffixes=("_ust", "_alt"))
            fark["fark"] = fark["brut_ust"] - fark["brut_alt"]
        faktor[c] = {"donem": {"IS": IS, "OOS": OOS},
                     "ust_net_ew": {"IS": donem_ozet(ust, "net_ew", IS), "OOS": donem_ozet(ust, "net_ew", OOS)},
                     "ust_net_xu": {"IS": donem_ozet(ust, "net_xu", IS), "OOS": donem_ozet(ust, "net_xu", OOS)},
                     "ust_eksi_alt_brut": {"IS": donem_ozet(fark, "fark", IS) if not fark.empty else {},
                                           "OOS": donem_ozet(fark, "fark", OOS) if not fark.empty else {}}}
    anl = bh({c: p_deger(v["ust_net_ew"]["OOS"].get("t")) for c, v in faktor.items()})
    for c in faktor:
        faktor[c]["bh_anlamli_oos"] = anl.get(c, False)

    Cb, pb, bb, _ = calistir(C, xu, temel, banka_haric=True)
    banka_haric = donem_ozet(portfoy_serisi(Cb, xu, pb, bb), "net_ew", BIL_OOS)
    son_i = ay_pos[-1]
    guncel = bilesik[son_i].dropna().sort_values(ascending=False)
    gt = pd.DataFrame({"skor": guncel.round(3), "sektor": [SEKTOR100.get(x) for x in guncel.index]})
    r_son = siralar(faktor_tablosu(C2, C2.pct_change(), temel, son_i))
    gt = gt.join(r_son.round(2))
    n_ust = max(5, int(math.floor(DILIM * len(guncel))))
    gt["ust_dilim"] = [i < n_ust for i in range(len(gt))]

    os.makedirs(CIKTI, exist_ok=True)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    sha = sha256(ON_KAYIT)
    taze = ana[ana["ay"] > BIL_OOS[1]] if not ana.empty else ana
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1", "on_kayit_sha256": sha,
           "deneme_no": len(kayit["denemeler"]) + 1, "hukum": e, "kriterler": k,
           "bilesik": {"IS": b_is, "OOS": b_oos, "oos_yillik": yil, "taze": taze[["ay", "net_ew", "net_xu"]].round(3).to_dict("records"),
                       "xu100e_gore_IS": donem_ozet(ana, "net_xu", BIL_IS), "xu100e_gore_OOS": donem_ozet(ana, "net_xu", BIL_OOS),
                       "bankalar_haric_OOS": banka_haric,
                       "ort_devir": round(float(ana["devir"].mean()), 3) if not ana.empty else None,
                       "ort_hisse": round(float(ana["n"].mean()), 1) if not ana.empty else None},
           "sektor_cikarma_oos": k4, "faktorler": faktor,
           "guncel_siralama_tarihi": str(C2.index[son_i].date()),
           "veri": {"evren": len(evren), "fiyatli": len(C.columns), "hata": hata,
                    "adet_eksik": [k_ for k_, (_, a) in temel.items() if not a]}}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    ana.round(4).to_csv(f"{CIKTI}/aylik.csv", index=False)
    gt.to_csv(f"{CIKTI}/guncel_siralama.csv")
    g = lambda d, a: (d or {}).get(a)
    L = ["# H6 Cok Faktorlu Aylik Siralama", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{(sha or '-')[:16]}` | deneme no {out['deneme_no']} | maliyet {MALIYET}% x devir | t esigi {T_ESIK}",
         "", "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H6.md'de. Degerler aylik, yuzde puan.", "",
         "## Bilesik (ust %20, evren esit agirlikli ortalamasina gore aylik net) - BIRINCIL", "", "| Donem | Ay | Ort | t | Pozitif ay % |", "|---|---|---|---|---|",
         f"| IS {BIL_IS[0]}..{BIL_IS[1]} | {g(b_is,'n')} | {g(b_is,'ort')} | {g(b_is,'t')} | {g(b_is,'pozitif_pct')} |",
         f"| OOS {BIL_OOS[0]}..{BIL_OOS[1]} | {g(b_oos,'n')} | {g(b_oos,'ort')} | {g(b_oos,'t')} | {g(b_oos,'pozitif_pct')} |",
         "", f"## Hukum: **{e}**", ""] + [f"- {a}: {'EVET' if v else 'HAYIR'}" for a, v in k.items()]
    L += [f"- OOS yillik: {yil}", f"- Sektor cikarma OOS: {k4}",
          f"- XU100'e gore (ikincil) IS: {out['bilesik']['xu100e_gore_IS']} | OOS: {out['bilesik']['xu100e_gore_OOS']}",
          f"- Bankalar haric OOS: {banka_haric}", f"- Ortalama devir {out['bilesik']['ort_devir']}, ortalama hisse {out['bilesik']['ort_hisse']}",
          "", "## Tek faktorler (hukum vermez)", "",
          "| Faktor | Ust %20 net evren IS (t) | Ust %20 net evren OOS (t) | BH anlamli | Ust %20 net XU100 OOS (t) | Ust-alt brut OOS (t) |", "|---|---|---|---|---|---|"]
    for c, v in faktor.items():
        L.append(f"| {c} | {g(v['ust_net_ew']['IS'],'ort')} ({g(v['ust_net_ew']['IS'],'t')}) | {g(v['ust_net_ew']['OOS'],'ort')} ({g(v['ust_net_ew']['OOS'],'t')}) | "
                 f"{'evet' if v['bh_anlamli_oos'] else 'hayir'} | {g(v['ust_net_xu']['OOS'],'ort')} ({g(v['ust_net_xu']['OOS'],'t')}) | "
                 f"{g(v['ust_eksi_alt_brut']['OOS'],'ort')} ({g(v['ust_eksi_alt_brut']['OOS'],'t')}) |")
    L += ["", f"## Guncel siralama ({out['guncel_siralama_tarihi']}, ust dilim; gozlem amaclidir)", "",
          ", ".join(f"{i}({r.skor})" for i, r in gt[gt["ust_dilim"]].iterrows()),
          "", f"Fiyati cekilemeyen: {hata or 'yok'} | adet (2OA) eksik: {out['veri']['adet_eksik'] or 'yok'}",
          "", "Bilinen sinirlar: hayatta kalma yanliligi, nokta-zaman verisi degil, TMS 29, yaklasik piyasa degeri, temettu haric, tek kaynak."]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": os.environ.get("GITHUB_SHA"), "hukum": e})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("H6", e, "OOS", b_oos, "IS", b_is)


if __name__ == "__main__":
    main()
