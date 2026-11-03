"""
R3b STOP KURALLARI - PIYASAYA GORE FAZLA GETIRI - SALT OLCUM, TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_R3B.md (bu betikten ONCE commit edilmis olmali).
risk_bataryasi.py'deki veri, islem ve plasebo fonksiyonlarini kullanir.
Cikti : data/risk_r3b/sonuc.json, sonuc.md, deneme_kaydi.json
"""
import os, json, datetime
import numpy as np
import pandas as pd
import risk_bataryasi as rb

ON_KAYIT = "ON_KAYIT_R3B.md"
CIKTI = "data/risk_r3b"


def sepet_seviyeleri(O, C, M):
    """Uyelerin esit agirlikli sepeti: kapanis seviyesi B ve acilis seviyesi BO."""
    R = C.pct_change(fill_method=None)
    R = R.where(R.abs() <= 0.5)
    RO = (O / C.shift(1) - 1).where(lambda x: x.abs() <= 0.5)
    m = M.shift(1).fillna(False).astype(bool)          # dunku uyelik (bugunun getirisini tasiyan sepet)
    rc = R.where(m).mean(axis=1).fillna(0.0)
    ro = RO.where(m).mean(axis=1).fillna(0.0)
    B = (1 + rc).cumprod()
    BO = B.shift(1).fillna(1.0) * (1 + ro)
    return B.values, BO.values


def islemler_fazla(O, H, L, C, ATR, M):
    ret, gun, meta = rb.r3_islemler(O, H, L, C, ATR, M)
    B, BO = sepet_seviyeleri(O, C, M)
    ii = np.array([m[1] for m in meta])
    tarih = np.array([m[0] for m in meta])
    fazla = {}
    for v in rb.VARYANT:
        k = ii + gun[v]
        sepet = B[k] / BO[ii] - 1
        fazla[v] = ret[v] - sepet
    return fazla, ret, gun, tarih


def main():
    os.makedirs(CIKTI, exist_ok=True)
    sha = rb.sha256(ON_KAYIT)
    if not sha:
        raise SystemExit("ON_KAYIT_R3B.md yok")
    rng = np.random.default_rng(rb.TOHUM)
    uyelik = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))["uyelik"]
    kd = rb.liste_oku("config/kapsam_disi.txt")
    semboller = sorted({s for v in uyelik.values() for s in v.get("XU100", [])} - kd)
    xu = rb.ohlc_cek("XU100")
    takvim = xu.index
    O, H, L, C, hata = rb.panel(semboller)
    O, H, L, C = (d.reindex(takvim) for d in (O, H, L, C))
    M = rb.uyelik_matrisi(uyelik, takvim, C.columns, kd)
    ATR = rb.atr_hesap(H, L, C)

    fz, mutlak, gun, tarih = islemler_fazla(O, H, L, C, ATR, M)
    sO, sH, sL, sC = rb.sentetik_panel(O, H, L, C, rng)
    pfz, _, pgun, ptarih = islemler_fazla(sO, sH, sL, sC, rb.atr_hesap(sH, sL, sC), M)

    def tablo_kur(x, g, t):
        mk = {"IS": (t >= rb.IS[0]) & (t <= rb.IS[1]), "OOS": t >= rb.OOS_BAS}
        return {v: {d: rb.islem_ozet(x[v][m], g[v][m]) for d, m in mk.items()} for v in rb.VARYANT}

    T, P, A = tablo_kur(fz, gun, tarih), tablo_kur(pfz, pgun, ptarih), tablo_kur(mutlak, gun, tarih)
    v0 = T["V0"]
    adaylar = [v for v in rb.VARYANT if v != "V0" and T[v]["IS"]["ort"] >= v0["IS"]["ort"] - 0.30]
    secilen = max(adaylar, key=lambda v: T[v]["IS"]["cvar5"]) if adaylar else None
    hukum, kosul, kum = "KENAR_YOK", {}, None
    if secilen:
        s, b = T[secilen]["OOS"], v0["OOS"]
        fg = s["ort"] - b["ort"]
        fp = P[secilen]["OOS"]["ort"] - P["V0"]["OOS"]["ort"]
        k1 = abs(s["cvar5"]) <= 0.75 * abs(b["cvar5"])
        k2 = s["ort"] >= b["ort"] - 0.30
        k3 = fg >= fp - 0.20
        kosul = {"cvar_25pct": k1, "ort_kaybi_0_30": k2, "plasebodan_pahali_degil": k3, "ort_fark_gercek": round(fg, 3), "ort_fark_plasebo": round(fp, 3)}
        hukum = "GECTI" if (k1 and k2 and k3) else ("STOP_PAHALI" if (k1 and not k3) else "KENAR_YOK")
        df = pd.DataFrame({"t": tarih, "f": fz[secilen] - fz["V0"]}).groupby("t").f.mean()
        kum = rb.newey_west(df.values * 100, 4)
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "on_kayit_sha256": sha,
           "git_sha": os.environ.get("GITHUB_SHA"), "hukum": hukum, "secilen": secilen, "kosullar": kosul,
           "fazla_getiri": T, "plasebo_fazla": P, "mutlak_bilgi": A, "ort_fark_kume_t": kum, "fiyat_hatasi": hata}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    ky = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(ky, encoding="utf-8")) if os.path.exists(ky) else {"denemeler": []}
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": out["git_sha"], "hukum": hukum})
    json.dump(kayit, open(ky, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L_ = ["# R3b Stop kurallari - piyasaya gore fazla getiri", "",
          f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{sha[:16]}` | deneme no {len(kayit['denemeler'])}", "",
          "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_R3B.md'de.", "", f"## Hukum: **{hukum}** (secilen: {secilen})", "",
          f"Kosullar: {kosul}", f"Ortalama fark (secilen - V0) giris gunu kumelenmis: {kum}", "",
          "| Varyant | Donem | n | Fazla ort | Medyan | CVaR5 | En kotu | Stop orani | Plasebo ort / CVaR5 | Mutlak ort |", "|---|---|---|---|---|---|---|---|---|---|"]
    for v in rb.VARYANT:
        for d in ("IS", "OOS"):
            m, p, a = T[v][d], P[v][d], A[v][d]
            L_.append(f"| {v} | {d} | {m['n']} | {m['ort']} | {m['medyan']} | {m['cvar5']} | {m['en_kotu']} | {m.get('stop_orani')} | {p['ort']} / {p['cvar5']} | {a['ort']} |")
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L_) + "\n")
    print("\n".join(L_))


if __name__ == "__main__":
    main()
