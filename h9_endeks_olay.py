"""
H9 BIST 100 DONEMSEL ENDEKS DEGISIKLIGI OLAY TESTI - SALT OLCUM, TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H9.md (bu betikten ONCE commit edilmis olmali).
Girdi : data/endeks_uyelik/donemsel.json, yfinance fiyatlari (h_testleri.panel_kur)
Cikti : data/h9/sonuc.json, data/h9/sonuc.md, data/h9/olaylar.csv, data/h9/deneme_kaydi.json
"""
import os, json, math, datetime
import numpy as np
import pandas as pd
from h_testleri import panel_kur, fiyat_cek, sha256

ON_KAYIT = "ON_KAYIT_H9.md"
CIKTI = "data/h9"
MALIYET = 0.25
T_ESIK, T_ZAYIF = 2.58, 1.65
OOS_BAS = "2022-01-01"
MIN_DONEM = 20
W2_GUN, W0_GUN, PLASEBO_KAYMA = 20, 10, 63
POZITIF_EK = 3.0


def liste_oku(yol):
    if not os.path.exists(yol):
        return set()
    return {s.split("#")[0].strip().upper() for s in open(yol, encoding="utf-8") if s.split("#")[0].strip()}


def gun_idx(takvim, tarih, sonra=True):
    """tarih'ten sonraki (sonra=True: kesin sonra) ya da tarih dahil onceki son islem gununun indeksi."""
    t = pd.Timestamp(tarih)
    if sonra:
        i = takvim.searchsorted(t, side="right")
        return i if i < len(takvim) else None
    i = takvim.searchsorted(t, side="left") - 1
    return i if i >= 0 else None


def getiri(C, O, kod, i_giris, i_cikis, takvim, acilis=False):
    if kod not in C.columns or i_giris is None or i_cikis is None or i_cikis <= i_giris - (1 if acilis else 0):
        return None
    g = (O if acilis else C)[kod].get(takvim[i_giris])
    c = C[kod].get(takvim[i_cikis])
    if g is None or c is None or not (np.isfinite(g) and np.isfinite(c)) or g <= 0:
        return None
    return (c / g - 1) * 100


def olay_seti(duyurular, uyelik, kd, C, O, takvim, kayma=0):
    satir = []
    for d in duyurular:
        iD = gun_idx(takvim, d["duyuru_tarihi"], sonra=False)          # D (dahil, son islem gunu)
        iE1 = takvim.searchsorted(pd.Timestamp(d["donem_bas"]), side="left") - 1   # E-1: E'den kesin once
        if iD is None or iE1 < 0:
            continue
        iD, iE1 = iD - kayma, iE1 - kayma
        i_giris = iD + 1
        if i_giris > iE1 or iD - W0_GUN < 0 or iE1 + W2_GUN >= len(takvim):
            continue
        uy = set(uyelik.get(d["donem_bas"], {}).get("XU100", []))
        olay = set(d["XU100"]["al"]) | set(d["XU100"]["cik"])
        kiyas = [k for k in uy if k not in olay and k not in kd]
        def kiyas_ort(i1, i2, acilis):
            v = [getiri(C, O, k, i1, i2, takvim, acilis) for k in kiyas]
            v = [x for x in v if x is not None]
            return (float(np.mean(v)), len(v)) if len(v) >= 30 else (None, len(v))
        k1, n1 = kiyas_ort(i_giris, iE1, True)
        k2, _ = kiyas_ort(iE1, iE1 + W2_GUN, False)
        k0, _ = kiyas_ort(iD - W0_GUN, iD, False)
        for grup in ("al", "cik"):
            for kod in d["XU100"][grup]:
                if kod in kd:
                    continue
                r1 = getiri(C, O, kod, i_giris, iE1, takvim, True)
                r2 = getiri(C, O, kod, iE1, iE1 + W2_GUN, takvim, False)
                r0 = getiri(C, O, kod, iD - W0_GUN, iD, takvim, False)
                satir.append({"donem_bas": d["donem_bas"], "duyuru": d["duyuru_tarihi"], "grup": grup, "kod": kod,
                              "w1_gun": int(iE1 - i_giris + 1), "kiyas_n": n1,
                              "w1": None if r1 is None or k1 is None else r1 - k1,
                              "w2": None if r2 is None or k2 is None else r2 - k2,
                              "w0": None if r0 is None or k0 is None else r0 - k0,
                              "fiyat_var": r1 is not None})
    return pd.DataFrame(satir)


def donem_seri(df, grup, alan, net=False, ek=0.0):
    x = df[(df.grup == grup) & df[alan].notna()].copy()
    if x.empty:
        return pd.Series(dtype=float)
    x[alan] = x[alan] + ek - (MALIYET if net else 0.0)
    return x.groupby("donem_bas")[alan].mean().sort_index()


def ozet(s):
    n = len(s)
    if n < 2:
        return {"n": n, "ort": None, "t": None}
    sd = float(s.std(ddof=1))
    t = float(s.mean() / (sd / math.sqrt(n))) if sd > 0 else None
    return {"n": n, "ort": round(float(s.mean()), 3), "t": None if t is None else round(t, 2),
            "oos_n": int((s.index >= OOS_BAS).sum()), "oos_ort": round(float(s[s.index >= OOS_BAS].mean()), 3) if (s.index >= OOS_BAS).any() else None,
            "is_ort": round(float(s[s.index < OOS_BAS].mean()), 3) if (s.index < OOS_BAS).any() else None}


def hukum(o, yon):
    if o["n"] < MIN_DONEM or o["t"] is None:
        return "VERI_YETERSIZ"
    t, oos = o["t"] * yon, (o["oos_ort"] or 0) * yon
    if t > T_ESIK and oos > 0:
        return "GECTI"
    if t > T_ZAYIF:
        return "ZAYIF"
    return "KENAR_YOK"


def bh(pler, q=0.05):
    m = len(pler)
    sira = sorted(range(m), key=lambda i: pler[i])
    gecen = set()
    for r, i in enumerate(sira, 1):
        if pler[i] <= q * r / m:
            gecen = set(sira[:r])
    return [i in gecen for i in range(m)]


def testler(df, ek=0.0):
    s = {"H9a": (donem_seri(df, "al", "w1", net=True, ek=ek), 1),
         "H9b": (donem_seri(df, "cik", "w1"), -1),
         "H9c": (donem_seri(df, "al", "w2"), -1)}
    return {k: {**ozet(v), "hukum": hukum(ozet(v), y)} for k, (v, y) in s.items()}


def main():
    os.makedirs(CIKTI, exist_ok=True)
    sha = sha256(ON_KAYIT)
    if not sha:
        raise SystemExit("ON_KAYIT_H9.md yok")
    u = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))
    duy, uyelik = u["duyurular"], u["uyelik"]
    kd = liste_oku("config/kapsam_disi.txt")
    semboller = sorted({k for d in duy for g in ("al", "cik") for k in d["XU100"][g]} |
                       {k for v in uyelik.values() for k in v.get("XU100", [])})
    xu, _ = fiyat_cek("XU100")
    takvim = xu.index
    C, O, _, hata = panel_kur([s for s in semboller if s not in kd], {}, adj=False)
    C, O = C.reindex(takvim), O.reindex(takvim)

    df = olay_seti(duy, uyelik, kd, C, O, takvim)
    df.to_csv(f"{CIKTI}/olaylar.csv", index=False)
    ana = testler(df)
    plasebo = testler(olay_seti(duy, uyelik, kd, C, O, takvim, kayma=PLASEBO_KAYMA))
    pozitif = testler(df, ek=POZITIF_EK)["H9a"]["hukum"]
    df_2610 = df[df.donem_bas != "2026-10-01"]
    haric_2610 = testler(df_2610)

    supheli = any(abs(plasebo[k]["t"] or 0) > T_ESIK for k in ("H9a", "H9b"))
    if supheli:
        for k in ana:
            if ana[k]["hukum"] == "GECTI":
                ana[k]["hukum"] = "SUPHELI"
    pler = [2 * (1 - 0.5 * (1 + math.erf(abs(ana[k]["t"] or 0) / math.sqrt(2)))) for k in ("H9a", "H9b", "H9c")]
    for k, g in zip(("H9a", "H9b", "H9c"), bh(pler)):
        ana[k]["bh_q05"] = g
    kapsama = {g: {"olay": int((df.grup == g).sum()), "fiyatli": int(df[(df.grup == g)].fiyat_var.sum())} for g in ("al", "cik")}
    w0 = {g: round(float(df[(df.grup == g) & df.w0.notna()].groupby("donem_bas").w0.mean().mean()), 3) for g in ("al", "cik")}
    katki = df[(df.grup == "al") & df.w1.notna()].sort_values("w1", key=abs, ascending=False).head(5)[["donem_bas", "kod", "w1"]].round(2).to_dict("records")
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "on_kayit_sha256": sha,
           "git_sha": os.environ.get("GITHUB_SHA"), "testler": ana, "plasebo": plasebo, "pozitif_kontrol_H9a": pozitif,
           "supheli": supheli, "haric_2026_10": haric_2610, "kapsama": kapsama, "w0_tani": w0,
           "en_buyuk_5_katki_H9a": katki, "fiyat_hatasi": dict(list(hata.items())[:60]), "fiyat_hatasi_sayisi": len(hata)}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": out["git_sha"],
                               "hukum": {k: v["hukum"] for k, v in ana.items()}})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    L = [f"# H9 BIST 100 donemsel endeks degisikligi olay testi", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{sha[:16]}` | deneme no {len(kayit['denemeler'])}", "",
         "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H9.md'de.", "",
         "| Test | Donem | Ortalama % | t | IS ort | OOS ort (n) | BH | Hukum |", "|---|---|---|---|---|---|---|---|"]
    ad = {"H9a": "Alinan W1 net", "H9b": "Cikarilan W1 brut", "H9c": "Alinan W2 brut"}
    for k, v in ana.items():
        L.append(f"| {k} {ad[k]} | {v['n']} | {v['ort']} | {v['t']} | {v.get('is_ort')} | {v.get('oos_ort')} ({v.get('oos_n')}) | {v.get('bh_q05')} | **{v['hukum']}** |")
    L += ["", f"Plasebo (63 gun geri): " + ", ".join(f"{k} t={v['t']}" for k, v in plasebo.items()) + f" | supheli: {supheli}",
          f"Pozitif kontrol (+%3): H9a {pozitif}",
          f"2026-10 haric: " + ", ".join(f"{k} ort={v['ort']} t={v['t']}" for k, v in haric_2610.items()),
          f"Kapsama: {kapsama} | fiyat hatasi {len(hata)}", f"W0 (duyuru oncesi 10 gun, tani): {w0}",
          f"En buyuk 5 katki (H9a): {katki}"]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
