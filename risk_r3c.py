"""
R3c %5 STOPUN GERCEKCI UYGULAMA KOSULLARINDA DOGRULANMASI - SALT OLCUM, TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_R3C.md (bu betikten ONCE commit edilmis olmali).
risk_bataryasi.py (veri, sentetik panel) ve risk_r3b.py (sepet) fonksiyonlarini kullanir.
Cikti : data/risk_r3c/sonuc.json, sonuc.md, deneme_kaydi.json
"""
import os, json, datetime, itertools
import numpy as np
import pandas as pd
import risk_bataryasi as rb
from risk_r3b import sepet_seviyeleri

ON_KAYIT = "ON_KAYIT_R3C.md"
CIKTI = "data/risk_r3c"
BIRINCIL = {"kayma": 0.0025, "yeniden": 0.0025, "sepet": "aleyhte"}
VARYANTLAR = ["V0", "S5", "S8", "A15", "A2", "A3", "T2", "T3"]


def islemler(O, H, L, C, ATR, M):
    """Her islem icin: giris indeksi, hisse, varyant basina (cikis fiyati ham, cikis gunu, tur: 0 yok / 1 bosluk / 2 gun ici)."""
    idx = C.index
    giris_ix = [i for i in range(len(idx)) if str(idx[i].date()) >= rb.IS[0] and i % 5 == 0 and i + 19 < len(idx) and i >= 1]
    Ov, Lv, Cv, Av, Mv = O.values, L.values, C.values, ATR.values, M.values
    out = {v: {"cik": [], "gun": [], "tur": []} for v in VARYANTLAR}
    meta = []
    for i in giris_ix:
        for j in np.where(Mv[i])[0]:
            e, a = Ov[i, j], Av[i - 1, j]
            if not (np.isfinite(e) and e > 0 and np.isfinite(a) and a > 0) or not np.isfinite(Cv[i:i + 20, j]).all():
                continue
            meta.append((str(idx[i].date()), i, j, e))
            for v in VARYANTLAR:
                kural = rb.VARYANT[v]
                if kural is None:
                    out[v]["cik"].append(Cv[i + 19, j]); out[v]["gun"].append(19); out[v]["tur"].append(0)
                    continue
                tip, k = kural
                stop = e * (1 - k) if tip == "y" else e - k * a
                en_yuksek, cik, gun, tur = e, None, 19, 0
                for d in range(20):
                    o, l, c = Ov[i + d, j], Lv[i + d, j], Cv[i + d, j]
                    if d > 0 and np.isfinite(o) and o < stop:
                        cik, gun, tur = o, d, 1
                        break
                    if np.isfinite(l) and l <= stop:
                        cik, gun, tur = stop, d, 2
                        break
                    if tip == "t" and np.isfinite(c):
                        en_yuksek = max(en_yuksek, c)
                        stop = max(stop, en_yuksek - k * a)
                if cik is None:
                    cik = Cv[i + 19, j]
                out[v]["cik"].append(cik); out[v]["gun"].append(gun); out[v]["tur"].append(tur)
    return {v: {k: np.array(x) for k, x in d.items()} for v, d in out.items()}, meta


def fazla_getiri(T, meta, B, BO, kayma, yeniden, sepet_modu):
    ii = np.array([m[1] for m in meta])
    e = np.array([m[3] for m in meta])
    res = {}
    for v, d in T.items():
        cik, gun, tur = d["cik"].astype(float), d["gun"], d["tur"]
        stoplu = tur > 0
        fiyat = np.where(stoplu, cik * (1 - kayma), cik)
        r = fiyat / e - 1 - rb.GIDIS_DONUS - np.where(stoplu, yeniden, 0.0)
        k = ii + gun
        if sepet_modu == "kapanis":
            sv = B[k]
        else:
            sv = np.where(tur == 1, BO[k], np.where(tur == 2, np.maximum(BO[k], B[k]), B[k]))
        res[v] = {"fazla": r - (sv / BO[ii] - 1), "mutlak": r, "tur": tur}
    return res


def ozet(x, tur=None):
    o = rb.islem_ozet(x)
    if o and tur is not None:
        o["stop_orani"] = round(float((tur > 0).mean()), 3)
        o["bosluk_orani_stoplular"] = round(float((tur == 1).sum() / max(1, (tur > 0).sum())), 3)
    return o


def degerlendir(G, P, tarih, ptarih):
    mk = lambda t: {"IS": (t >= rb.IS[0]) & (t <= rb.IS[1]), "OOS": t >= rb.OOS_BAS}
    m, pm = mk(tarih), mk(ptarih)
    tablo = {v: {d: ozet(G[v]["fazla"][m[d]], G[v]["tur"][m[d]]) for d in m} for v in G}
    ptablo = {v: {d: ozet(P[v]["fazla"][pm[d]]) for d in pm} for v in ("V0", "S5")}
    mutlak = {v: {d: ozet(G[v]["mutlak"][m[d]]) for d in m} for v in ("V0", "S5")}
    sart = {}
    for d in ("IS", "OOS"):
        s, b = tablo["S5"][d], tablo["V0"][d]
        fg, fp = s["ort"] - b["ort"], ptablo["S5"][d]["ort"] - ptablo["V0"][d]["ort"]
        sart[d] = {"cvar_25pct": abs(s["cvar5"]) <= 0.75 * abs(b["cvar5"]), "ort_kaybi_0_30": s["ort"] >= b["ort"] - 0.30,
                   "plasebodan_pahali_degil": fg >= fp - 0.20, "ort_fark_gercek": round(fg, 3), "ort_fark_plasebo": round(fp, 3)}
    return tablo, ptablo, mutlak, sart


def main():
    os.makedirs(CIKTI, exist_ok=True)
    sha = rb.sha256(ON_KAYIT)
    if not sha:
        raise SystemExit("ON_KAYIT_R3C.md yok")
    rng = np.random.default_rng(rb.TOHUM)
    uyelik = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))["uyelik"]
    kd = rb.liste_oku("config/kapsam_disi.txt")
    semboller = sorted({s for v in uyelik.values() for s in v.get("XU100", [])} - kd)
    xu = rb.ohlc_cek("XU100")
    takvim = xu.index
    O, H, L, C, hata = rb.panel(semboller)
    O, H, L, C = (d.reindex(takvim) for d in (O, H, L, C))
    M = rb.uyelik_matrisi(uyelik, takvim, C.columns, kd)

    T, meta = islemler(O, H, L, C, rb.atr_hesap(H, L, C), M)
    B, BO = sepet_seviyeleri(O, C, M)
    sO, sH, sL, sC = rb.sentetik_panel(O, H, L, C, rng)
    PT, pmeta = islemler(sO, sH, sL, sC, rb.atr_hesap(sH, sL, sC), M)
    sB, sBO = sepet_seviyeleri(sO, sC, M)
    tarih = np.array([m[0] for m in meta]); ptarih = np.array([m[0] for m in pmeta])

    def hesap(kayma, yeniden, sepet):
        G = fazla_getiri(T, meta, B, BO, kayma, yeniden, sepet)
        P = fazla_getiri(PT, pmeta, sB, sBO, kayma, yeniden, sepet)
        return G, degerlendir(G, P, tarih, ptarih)

    G, (tablo, ptablo, mutlak, sart) = hesap(BIRINCIL["kayma"], BIRINCIL["yeniden"], BIRINCIL["sepet"])
    hepsi = all(all(v for k, v in sart[d].items() if isinstance(v, bool)) for d in ("IS", "OOS"))
    k1 = all(sart[d]["cvar_25pct"] for d in ("IS", "OOS"))
    hukum = "GECTI" if hepsi else ("STOP_PAHALI" if k1 else "KENAR_YOK")
    df = pd.DataFrame({"t": tarih, "f": G["S5"]["fazla"] - G["V0"]["fazla"]}).groupby("t").f.mean()
    kum = rb.newey_west(df.values * 100, 4)

    duyarlilik = {}
    for kayma, yeniden in itertools.product((0.0, 0.0025, 0.005), (0.001, 0.0025)):
        _, (tb, _, _, sr) = hesap(kayma, yeniden, "aleyhte")
        duyarlilik[f"kayma {kayma*100:.2f} / yeniden {yeniden*100:.2f}"] = {
            d: {"S5_ort": tb["S5"][d]["ort"], "V0_ort": tb["V0"][d]["ort"], "S5_cvar": tb["S5"][d]["cvar5"], "V0_cvar": tb["V0"][d]["cvar5"],
                "fark": sr[d]["ort_fark_gercek"]} for d in ("IS", "OOS")}
    _, (tbk, _, _, srk) = hesap(BIRINCIL["kayma"], BIRINCIL["yeniden"], "kapanis")
    duyarlilik["sepet kapanis (R3b gibi), birincil maliyetler"] = {d: {"S5_ort": tbk["S5"][d]["ort"], "V0_ort": tbk["V0"][d]["ort"], "fark": srk[d]["ort_fark_gercek"]} for d in ("IS", "OOS")}
    _, (tb0, _, _, sr0) = hesap(0.0, 0.0, "kapanis")
    duyarlilik["R3b esdegeri (kayma 0, yeniden 0, sepet kapanis)"] = {d: {"S5_ort": tb0["S5"][d]["ort"], "V0_ort": tb0["V0"][d]["ort"], "fark": sr0[d]["ort_fark_gercek"]} for d in ("IS", "OOS")}

    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "on_kayit_sha256": sha, "git_sha": os.environ.get("GITHUB_SHA"),
           "hukum": hukum, "sartlar": sart, "birincil": BIRINCIL, "tablo": tablo, "plasebo": ptablo, "mutlak_bilgi": mutlak,
           "ort_fark_kume_t": kum, "duyarlilik": duyarlilik, "fiyat_hatasi": hata}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    ky = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(ky, encoding="utf-8")) if os.path.exists(ky) else {"denemeler": []}
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": out["git_sha"], "hukum": hukum})
    json.dump(kayit, open(ky, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    L_ = ["# R3c %5 stop - gercekci uygulama", "", f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{sha[:16]}` | deneme no {len(kayit['denemeler'])}", "",
          "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_R3C.md'de.", "", f"## Hukum: **{hukum}**", "",
          f"Sartlar: {sart}", f"Ortalama fark S5 - V0 (giris gunu kumelenmis): {kum}", "",
          "| Varyant | Donem | n | Fazla ort | CVaR5 | En kotu | Stop orani | Bosluk payi | Plasebo ort / CVaR5 |", "|---|---|---|---|---|---|---|---|---|"]
    for v in VARYANTLAR:
        for d in ("IS", "OOS"):
            m = tablo[v][d]; p = ptablo.get(v, {}).get(d)
            L_.append(f"| {v} | {d} | {m['n']} | {m['ort']} | {m['cvar5']} | {m['en_kotu']} | {m.get('stop_orani')} | {m.get('bosluk_orani_stoplular')} | {(str(p['ort']) + ' / ' + str(p['cvar5'])) if p else ''} |")
    L_ += ["", "## Duyarlilik (hukum vermez)", "", "| Varsayim | Donem | S5 ort | V0 ort | Fark |", "|---|---|---|---|---|"]
    for k, v in duyarlilik.items():
        for d in ("IS", "OOS"):
            L_.append(f"| {k} | {d} | {v[d]['S5_ort']} | {v[d]['V0_ort']} | {v[d]['fark']} |")
    L_ += ["", f"Mutlak (stoplanan para nakitte): {mutlak}"]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L_) + "\n")
    print("\n".join(L_))


if __name__ == "__main__":
    main()
