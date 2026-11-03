"""
H10 YABANCI PAYI DEGISIMI OLAY TESTI - SALT OLCUM, TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H10.md (bu betikten ONCE commit edilmis olmali).
Girdi : data/yabanci_oran_arsiv.json, data/endeks_uyelik/donemsel.json, yfinance (h_testleri.panel_kur)
Cikti : data/h10/sonuc.json, data/h10/sonuc.md, data/h10/olaylar.csv, data/h10/deneme_kaydi.json
"""
import os, json, math, datetime
import numpy as np
import pandas as pd
from h_testleri import panel_kur, fiyat_cek, sha256, newey_west

ON_KAYIT = "ON_KAYIT_H10.md"
CIKTI = "data/h10"
MALIYET = 0.25
T_ESIK, T_ZAYIF = 2.58, 1.65
OOS_BAS = "2024-01-01"
MIN_GUN = 200
UFUK_ANA, UFUKLAR = 10, (5, 10, 20)
PLASEBO_KAYMA, POZITIF_EK = 63, 3.0
ACILIS_SINIR_UTC = "06:55"
TAVAN = 9.5


def liste_oku(yol):
    if not os.path.exists(yol):
        return set()
    return {s.split("#")[0].strip().upper() for s in open(yol, encoding="utf-8") if s.split("#")[0].strip()}


def giris_idx(takvim, tarih, yayin_utc):
    t = pd.Timestamp(tarih)
    i = int(takvim.searchsorted(t, side="left"))            # R ya da sonraki ilk islem gunu
    if i >= len(takvim):
        return None
    ayni_gun = takvim[i] == t
    erken = bool(yayin_utc) and yayin_utc[:10] == tarih and yayin_utc[11:16] < ACILIS_SINIR_UTC
    if ayni_gun and not erken:
        i += 1
    return i if i < len(takvim) else None


def getiri(C, O, kod, i0, h, takvim):
    i1 = i0 + h - 1
    if kod not in C.columns or i0 is None or i0 < 0 or i1 >= len(takvim):
        return None
    g, c = O[kod].iat[i0], C[kod].iat[i1]
    if not (np.isfinite(g) and np.isfinite(c)) or g <= 0:
        return None
    return (c / g - 1) * 100


def uyelik_bul(uyelik, tarih):
    anahtar = sorted(k for k in uyelik if not k.startswith("ONCESI") and k <= tarih)
    if anahtar:
        return set(uyelik[anahtar[-1]].get("XU100", []))
    eski = [k for k in uyelik if k.startswith("ONCESI")]
    return set(uyelik[eski[0]].get("XU100", [])) if eski else set()


def olaylar(kayitlar, uyelik, kd, C, O, takvim, kayma=0):
    satir, gun = [], []
    for k in kayitlar:
        i0 = giris_idx(takvim, k["tarih"], k.get("yayin_utc"))
        if i0 is None:
            continue
        i0 -= kayma
        if i0 < 1:
            continue
        gruplar = {"ARTAN": [s for s, _ in k["artan"]], "AZALAN": [s for s, _ in k["azalan"]],
                   "SUREKLI": [s for s, _ in k["surekli_artan"]]}
        olay = {s for v in gruplar.values() for s in v}
        kiyas = [s for s in uyelik_bul(uyelik, k["tarih"]) if s not in olay and s not in kd]
        g = {"tarih": k["tarih"]}
        for h in UFUKLAR:
            kv = [x for x in (getiri(C, O, s, i0, h, takvim) for s in kiyas) if x is not None]
            g[f"kiyas_{h}"] = float(np.mean(kv)) if len(kv) >= 30 else None
            for ad, uyeler in gruplar.items():
                vals = []
                for s in uyeler:
                    if s in kd:
                        continue
                    r = getiri(C, O, s, i0, h, takvim)
                    if h == UFUK_ANA and kayma == 0:
                        onceki = C[s].iat[i0 - 1] if s in C.columns else np.nan
                        acilis = O[s].iat[i0] if s in O.columns else np.nan
                        satir.append({"tarih": k["tarih"], "grup": ad, "kod": s, "getiri": r,
                                      "tavan_suphe": bool(np.isfinite(onceki) and np.isfinite(acilis) and onceki > 0 and (acilis / onceki - 1) * 100 > TAVAN)})
                    if r is not None:
                        vals.append(r)
                g[f"{ad}_{h}"] = float(np.mean(vals)) if vals else None
        gun.append(g)
    return pd.DataFrame(gun), pd.DataFrame(satir)


def seriler(G, h, ek=0.0):
    a, z, s, k = G.get(f"ARTAN_{h}"), G.get(f"AZALAN_{h}"), G.get(f"SUREKLI_{h}"), G.get(f"kiyas_{h}")
    return {"H10a": (a + ek) - z, "H10b": (a + ek) - k - MALIYET, "H10c": s - k}


def ozet(seri, tarih, h):
    x = pd.Series(seri.values, index=tarih.values).dropna()
    nw = newey_west(list(x.values), h) or {"n": len(x), "ort": None, "t": None}
    ois, oos = x[x.index < OOS_BAS], x[x.index >= OOS_BAS]
    yil = x.groupby(x.index.str[:4]).mean().round(3).to_dict()
    return {"n": nw["n"], "ort": nw["ort"], "t": nw["t"],
            "is_n": len(ois), "is_ort": round(float(ois.mean()), 3) if len(ois) else None,
            "oos_n": len(oos), "oos_ort": round(float(oos.mean()), 3) if len(oos) else None, "yillar": yil}


def hukum(o):
    if o["n"] < MIN_GUN or o["t"] is None:
        return "VERI_YETERSIZ"
    if o["t"] < -T_ESIK:
        return "TERS"
    if o["t"] > T_ESIK and (o["oos_ort"] or 0) > 0 and o["ort"] > 0:
        return "GECTI"
    if o["t"] > T_ZAYIF:
        return "ZAYIF"
    return "KENAR_YOK"


def testler(G, h, ek=0.0):
    return {ad: {**(o := ozet(s, G["tarih"], h)), "hukum": hukum(o)} for ad, s in seriler(G, h, ek).items()}


def bh(pler, q=0.05):
    m, sira, gecen = len(pler), sorted(range(len(pler)), key=lambda i: pler[i]), set()
    for r, i in enumerate(sira, 1):
        if pler[i] <= q * r / m:
            gecen = set(sira[:r])
    return [i in gecen for i in range(m)]


def main():
    os.makedirs(CIKTI, exist_ok=True)
    sha = sha256(ON_KAYIT)
    if not sha:
        raise SystemExit("ON_KAYIT_H10.md yok")
    kay = [k for k in json.load(open("data/yabanci_oran_arsiv.json", encoding="utf-8"))["kayitlar"] if k.get("ayristi") and k.get("tarih")]
    kay.sort(key=lambda k: k["tarih"])
    uyelik = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))["uyelik"]
    kd = liste_oku("config/kapsam_disi.txt")
    semboller = sorted({s for k in kay for g in ("artan", "azalan", "surekli_artan") for s, _ in k[g]} |
                       {s for v in uyelik.values() for s in v.get("XU100", [])})
    xu, _ = fiyat_cek("XU100")
    takvim = xu.index
    C, O, _, hata = panel_kur([s for s in semboller if s not in kd], {}, adj=False)
    C, O = C.reindex(takvim), O.reindex(takvim)

    G, S = olaylar(kay, uyelik, kd, C, O, takvim)
    S.to_csv(f"{CIKTI}/olaylar.csv", index=False)
    ana = testler(G, UFUK_ANA)
    ufuk = {h: testler(G, h) for h in UFUKLAR if h != UFUK_ANA}
    Gp, _ = olaylar(kay, uyelik, kd, C, O, takvim, kayma=PLASEBO_KAYMA)
    plasebo = testler(Gp, UFUK_ANA)
    pozitif = {k: v["hukum"] for k, v in testler(G, UFUK_ANA, ek=POZITIF_EK).items() if k in ("H10a", "H10b")}
    supheli = any(abs(plasebo[k]["t"] or 0) > T_ESIK for k in ("H10a", "H10b"))
    if supheli:
        for k in ana:
            if ana[k]["hukum"] == "GECTI":
                ana[k]["hukum"] = "SUPHELI"
    pler = [2 * (1 - 0.5 * (1 + math.erf(abs(ana[k]["t"] or 0) / math.sqrt(2)))) for k in ("H10a", "H10b", "H10c")]
    for k, g in zip(("H10a", "H10b", "H10c"), bh(pler)):
        ana[k]["bh_q05"] = g
    kapsama = {g: {"olay": int((S.grup == g).sum()), "fiyatli": int(S[S.grup == g].getiri.notna().sum()),
                   "tavan_suphe": int(S[S.grup == g].tavan_suphe.sum())} for g in ("ARTAN", "AZALAN", "SUREKLI")}
    katki = S[S.getiri.notna()].assign(m=lambda d: d.getiri.abs()).sort_values("m", ascending=False).head(5)[["tarih", "grup", "kod", "getiri"]].round(2).to_dict("records")
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "on_kayit_sha256": sha,
           "git_sha": os.environ.get("GITHUB_SHA"), "gun_sayisi": len(G), "testler_h10": ana,
           "diger_ufuklar": {str(h): v for h, v in ufuk.items()}, "plasebo": plasebo, "pozitif_kontrol": pozitif,
           "supheli": supheli, "kapsama": kapsama, "en_buyuk_5_katki": katki,
           "fiyat_hatasi_sayisi": len(hata), "fiyat_hatasi": dict(list(hata.items())[:80])}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": out["git_sha"],
                               "hukum": {k: v["hukum"] for k, v in ana.items()}})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ad = {"H10a": "ARTAN - AZALAN", "H10b": "ARTAN net - BIST100 EW", "H10c": "SUREKLI - BIST100 EW"}
    L = ["# H10 Yabanci payi degisimi olay testi", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{sha[:16]}` | deneme no {len(kayit['denemeler'])} | gun {len(G)}", "",
         "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H10.md'de.", "",
         "## Birincil (h = 10 islem gunu)", "",
         "| Test | Gun | Ortalama % | t (NW) | IS ort (n) | OOS ort (n) | BH | Hukum |", "|---|---|---|---|---|---|---|---|"]
    for k, v in ana.items():
        L.append(f"| {k} {ad[k]} | {v['n']} | {v['ort']} | {v['t']} | {v['is_ort']} ({v['is_n']}) | {v['oos_ort']} ({v['oos_n']}) | {v['bh_q05']} | **{v['hukum']}** |")
    L += ["", "## Ikincil ufuklar (hukum vermez)", ""]
    for h, t in ufuk.items():
        L.append(f"- h={h}: " + ", ".join(f"{k} ort={v['ort']} t={v['t']}" for k, v in t.items()))
    L += ["", "## Kontroller ve kapsama", "",
          "- Plasebo (63 gun geri): " + ", ".join(f"{k} t={v['t']}" for k, v in plasebo.items()) + f" | supheli: {supheli}",
          f"- Pozitif kontrol (+%3): {pozitif}",
          f"- Kapsama: {kapsama} | fiyat hatasi {len(hata)}",
          "- Yillar (h=10): " + "; ".join(f"{k} {v['yillar']}" for k, v in ana.items()),
          f"- En buyuk 5 katki: {katki}"]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
