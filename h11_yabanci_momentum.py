"""
H11 YABANCI ALIM SERISI vs MOMENTUM ESLESTIRMELI KONTROL - SALT OLCUM, TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H11.md (bu betikten ONCE commit edilmis olmali).
Girdi : data/yabanci_oran_arsiv.json, data/endeks_uyelik/donemsel.json, yfinance (h_testleri.panel_kur)
Cikti : data/h11/sonuc.json, data/h11/sonuc.md, data/h11/olaylar.csv, data/h11/deneme_kaydi.json
"""
import os, json, datetime
import numpy as np
import pandas as pd
from h_testleri import panel_kur, fiyat_cek, sha256, newey_west
from h10_yabanci_olay import giris_idx, uyelik_bul, liste_oku

ON_KAYIT = "ON_KAYIT_H11.md"
CIKTI = "data/h11"
MALIYET = 0.25
T_ESIK, T_ZAYIF = 2.58, 1.65
OOS_BAS = "2024-01-01"
MIN_GUN = 200
UFUK_ANA, UFUKLAR = 10, (5, 10, 20)
PLASEBO_KAYMA, POZITIF_EK = 63, 3.0
K_KONTROL, YAKIN_GUN, MIN_GECMIS = 5, 20, 253
OZELLIK = ("R21", "R63", "R252", "OYN")


class Panel:
    """Hiz icin numpy diziler. Ozellikler i-1 kapanisina kadarki bilgiyle hesaplanir (ileriye bakmaz)."""
    def __init__(self, C, O):
        self.kod = list(C.columns)
        self.ix = {k: j for j, k in enumerate(self.kod)}
        self.C, self.O = C.values.astype(float), O.values.astype(float)
        c = pd.DataFrame(self.C)
        self.R21 = (c / c.shift(21) - 1).values
        self.R63 = (c / c.shift(63) - 1).values
        self.R252 = (c / c.shift(252) - 1).values
        self.OYN = c.pct_change(fill_method=None).rolling(63, min_periods=58).std().values
        self.GEC = c.notna().rolling(MIN_GECMIS, min_periods=1).sum().values

    def ozellik(self, i):
        j = i - 1
        if j < MIN_GECMIS:
            return None
        F = np.column_stack([self.R21[j], self.R63[j], self.R252[j], self.OYN[j]])
        ok = np.isfinite(F).all(axis=1) & (self.GEC[j] >= MIN_GECMIS - 10)
        return F, ok

    def getiri(self, i0, h):
        i1 = i0 + h - 1
        if i0 < 0 or i1 >= len(self.C):
            return None
        g, c = self.O[i0], self.C[i1]
        with np.errstate(divide="ignore", invalid="ignore"):
            r = (c / g - 1) * 100
        r[~(np.isfinite(r) & (g > 0))] = np.nan
        return r


def yuzdelik(F):
    return np.column_stack([pd.Series(F[:, k]).rank(pct=True).values for k in range(F.shape[1])])


def gun_olaylari(k, i0, h_list, PN, havuz_tum, kd, yakin_set, uyelik, ek=0.0):
    fo = PN.ozellik(i0)
    if fo is None:
        return []
    F, ok = fo
    olaylar = [s for s, _ in k["surekli_artan"] if s not in kd]
    havuz = (uyelik_bul(uyelik, k["tarih"]) | havuz_tum) - set(olaylar) - yakin_set - kd
    aday = [s for s in havuz if s in PN.ix and ok[PN.ix[s]]]
    ola = [s for s in olaylar if s in PN.ix and ok[PN.ix[s]]]
    if len(aday) < 30 or not ola:
        return []
    evren = aday + ola
    P = yuzdelik(F[[PN.ix[s] for s in evren]])
    A, nA = P[:len(aday)], len(aday)
    ai = np.array([PN.ix[s] for s in aday])
    R = {h: PN.getiri(i0, h) for h in h_list}
    out = []
    for m, s in enumerate(ola):
        ps = P[nA + m]
        sec = np.argsort(np.sqrt(((A - ps) ** 2).sum(axis=1)))[:K_KONTROL]
        satir = {"tarih": k["tarih"], "kod": s, "kontrol": ",".join(aday[q] for q in sec), "havuz": nA}
        for q, o in enumerate(OZELLIK):
            satir[f"fark_{o}"] = float(ps[q] - A[sec, q].mean())
        for h in h_list:
            r = R[h]
            if r is None:
                satir[f"es_{h}"] = satir[f"ham_{h}"] = None
                continue
            rs, rk, rh = r[PN.ix[s]], r[ai[sec]], r[ai]
            rk, rh = rk[np.isfinite(rk)], rh[np.isfinite(rh)]
            satir[f"es_{h}"] = None if not np.isfinite(rs) or len(rk) < 3 else float(rs + ek - rk.mean())
            satir[f"ham_{h}"] = None if not np.isfinite(rs) or len(rh) < 30 else float(rs + ek - rh.mean())
        out.append(satir)
    return out


def calistir(kay, PN, takvim, havuz_tum, kd, uyelik, kayma=0, ek=0.0, h_list=UFUKLAR):
    rows, gecmis = [], []          # gecmis: (i0, set) - son 20 islem gunundeki SUREKLI listeleri
    for k in kay:
        i0 = giris_idx(takvim, k["tarih"], k.get("yayin_utc"))
        if i0 is None:
            continue
        yakin = set().union(*[s for i, s in gecmis if i0 - YAKIN_GUN <= i < i0]) if gecmis else set()
        gecmis.append((i0, {s for s, _ in k["surekli_artan"]}))
        i0 -= kayma
        if i0 < MIN_GECMIS + 1 or i0 + max(h_list) - 1 >= len(takvim):
            continue
        rows += gun_olaylari(k, i0, h_list, PN, havuz_tum, kd, yakin, uyelik, ek)
    return pd.DataFrame(rows)


def ozet(D, alan, h, maliyet=0.0):
    if D.empty or alan not in D:
        return {"n": 0, "ort": None, "t": None}
    g = D[D[alan].notna()].groupby("tarih")[alan].mean().sort_index() - maliyet
    nw = newey_west(list(g.values), h) or {"n": len(g), "ort": None, "t": None}
    ois, oos = g[g.index < OOS_BAS], g[g.index >= OOS_BAS]
    return {"n": nw["n"], "ort": nw["ort"], "t": nw["t"],
            "is_n": len(ois), "is_ort": round(float(ois.mean()), 3) if len(ois) else None,
            "oos_n": len(oos), "oos_ort": round(float(oos.mean()), 3) if len(oos) else None,
            "yillar": g.groupby(g.index.str[:4]).mean().round(3).to_dict()}


def hukum(o, plasebo_t, pozitif):
    if o["n"] < MIN_GUN or o["t"] is None:
        return "VERI_YETERSIZ"
    if not (pozitif.get("t") is not None and pozitif["t"] > T_ESIK and (pozitif.get("ort") or 0) > 0):
        return "GUC_YETERSIZ"
    if o["t"] < -T_ESIK:
        return "TERS"
    if o["ort"] > 0 and o["t"] > T_ESIK and (o["oos_ort"] or 0) > 0:
        return "GECTI" if abs(plasebo_t or 0) < T_ESIK else "SUPHELI"
    if o["ort"] > 0 and o["t"] > T_ZAYIF:
        return "ZAYIF"
    return "KENAR_YOK"


def main():
    os.makedirs(CIKTI, exist_ok=True)
    sha = sha256(ON_KAYIT)
    if not sha:
        raise SystemExit("ON_KAYIT_H11.md yok")
    kay = sorted([k for k in json.load(open("data/yabanci_oran_arsiv.json", encoding="utf-8"))["kayitlar"]
                  if k.get("ayristi") and k.get("tarih")], key=lambda k: k["tarih"])
    uyelik = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))["uyelik"]
    kd = liste_oku("config/kapsam_disi.txt")
    havuz_tum = {s for k in kay for g in ("artan", "azalan", "surekli_artan") for s, _ in k[g]}
    semboller = sorted(havuz_tum | {s for v in uyelik.values() for s in v.get("XU100", [])})
    xu, _ = fiyat_cek("XU100")
    takvim = xu.index
    C, O, _, hata = panel_kur([s for s in semboller if s not in kd], {}, adj=False)
    C, O = C.reindex(takvim), O.reindex(takvim)

    PN = Panel(C, O)
    D = calistir(kay, PN, takvim, havuz_tum, kd, uyelik)
    D.to_csv(f"{CIKTI}/olaylar.csv", index=False)
    P = calistir(kay, PN, takvim, havuz_tum, kd, uyelik, kayma=PLASEBO_KAYMA, h_list=(UFUK_ANA,))
    Z = D.copy()
    Z[f"es_{UFUK_ANA}"] = Z[f"es_{UFUK_ANA}"] + POZITIF_EK
    ana = ozet(D, f"es_{UFUK_ANA}", UFUK_ANA)
    plasebo = ozet(P, f"es_{UFUK_ANA}", UFUK_ANA)
    pozitif = ozet(Z, f"es_{UFUK_ANA}", UFUK_ANA)
    ana["hukum"] = hukum(ana, plasebo["t"], pozitif)
    net = ozet(D, f"es_{UFUK_ANA}", UFUK_ANA, maliyet=MALIYET)
    ufuk = {h: ozet(D, f"es_{h}", h) for h in UFUKLAR if h != UFUK_ANA}
    ham = {h: ozet(D, f"ham_{h}", h) for h in UFUKLAR}
    kalite = {o: round(float(D[f"fark_{o}"].abs().mean()), 3) for o in OZELLIK} if not D.empty else {}
    zayif_es = any(v > 0.10 for v in kalite.values())
    toplam_olay = sum(len([s for s, _ in k["surekli_artan"] if s not in kd]) for k in kay)
    katki = D[D[f"es_{UFUK_ANA}"].notna()].assign(m=lambda x: x[f"es_{UFUK_ANA}"].abs()).sort_values("m", ascending=False).head(5)[
        ["tarih", "kod", f"es_{UFUK_ANA}", "kontrol"]].round(2).to_dict("records") if not D.empty else []
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "on_kayit_sha256": sha,
           "git_sha": os.environ.get("GITHUB_SHA"), "hukum": ana["hukum"], "eslestirme_zayif": zayif_es,
           "h10": ana, "h10_net": net, "diger_ufuklar": {str(h): v for h, v in ufuk.items()},
           "kontrolsuz_fark": {str(h): v for h, v in ham.items()}, "plasebo": plasebo, "pozitif_kontrol": pozitif,
           "eslestirme_kalitesi_ort_mutlak_fark": kalite, "olay_toplam": toplam_olay,
           "olay_eslesen": int(D[f"es_{UFUK_ANA}"].notna().sum()) if not D.empty else 0,
           "ort_havuz": round(float(D.havuz.mean()), 1) if not D.empty else None,
           "en_buyuk_5_katki": katki, "fiyat_hatasi_sayisi": len(hata)}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": out["git_sha"], "hukum": ana["hukum"]})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    f = lambda v: f"ort={v['ort']} t={v['t']}"
    L = ["# H11 Yabanci alim serisi vs momentum eslestirmeli kontrol", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{sha[:16]}` | deneme no {len(kayit['denemeler'])}", "",
         "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H11.md'de.", "",
         f"## Hukum: **{ana['hukum']}**" + (" (ESLESTIRME_ZAYIF)" if zayif_es else ""), "",
         "| Olcu (h=10) | Gun | Ortalama % | t (NW) | IS ort (n) | OOS ort (n) |", "|---|---|---|---|---|---|",
         f"| Eslestirmeli fark (SUREKLI - 5 kontrol) | {ana['n']} | {ana['ort']} | {ana['t']} | {ana.get('is_ort')} ({ana.get('is_n')}) | {ana.get('oos_ort')} ({ana.get('oos_n')}) |",
         f"| Ayni, net (-%0,25) | {net['n']} | {net['ort']} | {net['t']} | {net.get('is_ort')} | {net.get('oos_ort')} |",
         f"| Plasebo (63 gun geri) | {plasebo['n']} | {plasebo['ort']} | {plasebo['t']} | {plasebo.get('is_ort')} | {plasebo.get('oos_ort')} |",
         f"| Pozitif kontrol (+%3) | {pozitif['n']} | {pozitif['ort']} | {pozitif['t']} | | |", "",
         "## Ek bilgi", "",
         "- Diger ufuklar (eslestirmeli): " + "; ".join(f"h={h} {f(v)}" for h, v in ufuk.items()),
         "- Kontrolsuz fark (SUREKLI - havuz ortalamasi, H10c benzeri): " + "; ".join(f"h={h} {f(v)}" for h, v in ham.items()),
         f"- Yillar (h=10): {ana.get('yillar')}",
         f"- Eslestirme kalitesi (ort. mutlak yuzdelik farki): {kalite}",
         f"- Olay {out['olay_toplam']}, eslesen {out['olay_eslesen']}, ort. havuz {out['ort_havuz']}, fiyat hatasi {len(hata)}",
         f"- En buyuk 5 katki: {katki}"]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
