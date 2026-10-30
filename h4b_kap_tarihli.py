"""
H4b BILANCO SURPRIZI - GERCEK KAP TARIHLI, TAKVIM ZAMANLI PORTFOY (27.10.2026)
SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR. Kurallar: ON_KAYIT_H4B.md (bu betikten ONCE commit edilir).
Girdi : data/kap_finansal_rapor_tarihleri.json, data/temel/ham_*.json, fiyat (yfinance)
Cikti : data/h4b/sonuc.json, data/h4b/sonuc.md, data/h4b/olaylar.csv, data/h4b/deneme_kaydi.json
"""
import os, json, datetime
from collections import defaultdict

import numpy as np
import pandas as pd

from h_testleri import panel_kur, sektor_sepeti, newey_west, sha256
from h4_bilanco_surprizi import sinyaller, liste_oku, SEKTOR100, MALIYET, MIN_SIRKET

ON_KAYIT = "ON_KAYIT_H4B.md"
KAP = "data/kap_finansal_rapor_tarihleri.json"
CIKTI = "data/h4b"
TUTMA = 40
TUTMA_EK = (10, 20)
NW_LAG = 20
T_ESIK = 2.58
KAPSAM_ESIK = 0.80
IS_ARALIK = ("2021-04-01", "2023-10-31")
OOS_ARALIK = ("2023-11-01", "2026-07-31")
TAZE_BAS = "2026-08-01"


def onceki(y, p):
    return (y, p - 3) if p > 3 else (y - 1, 12)


def donem_etiketi(t):
    if pd.Timestamp(IS_ARALIK[0]) <= t <= pd.Timestamp(IS_ARALIK[1]):
        return "IS"
    if pd.Timestamp(OOS_ARALIK[0]) <= t <= pd.Timestamp(OOS_ARALIK[1]):
        return "OOS"
    return "TAZE" if t >= pd.Timestamp(TAZE_BAS) else None


def olaylari_kur(S_tum, kap, gunler, kolonlar):
    olay, kapsam = [], defaultdict(lambda: [0, 0])
    tarih = {(k["sembol"], k["donem"]): k for k in kap}
    for (y, p), S in S_tum.items():
        oy, op = onceki(y, p)
        Sp = [v for k, v in S_tum.get((oy, op), {}).items() if k in kolonlar]
        for kod, s in S.items():
            if kod not in kolonlar:
                continue
            a = f"{y}/{p:02d}"
            kapsam[a][1] += 1
            k = tarih.get((kod, a))
            if not k:
                continue
            kapsam[a][0] += 1
            if len(Sp) < MIN_SIRKET:
                continue
            q33, q67 = np.percentile(Sp, [100 / 3, 200 / 3])
            sinif = "IYI" if s >= q67 else ("KOTU" if s <= q33 else "ORTA")
            yerel = pd.Timestamp(k["yayin_yerel"])
            i0 = gunler.searchsorted(yerel.normalize() + pd.Timedelta(days=1))   # ertesi ilk islem gunu
            if i0 >= len(gunler):
                continue
            hm = yerel.hour * 60 + yerel.minute
            donem_sonu = pd.Timestamp(year=y, month=p, day=1) + pd.offsets.MonthEnd(0)
            olay.append({"sembol": kod, "donem": a, "S": s, "sinif": sinif, "yayin_yerel": k["yayin_yerel"],
                         "seans_ici": 600 <= hm <= 1090, "gecikme_gun": int((yerel.normalize() - donem_sonu).days),
                         "i0": int(i0), "giris": str(gunler[i0].date()), "grup": donem_etiketi(gunler[i0]),
                         "sektor": SEKTOR100.get(kod)})
    return olay, {a: {"bulunan": v[0], "toplam": v[1], "oran": round(v[0] / v[1], 3) if v[1] else None} for a, v in kapsam.items()}


def takvim_serisi(olay, REL, sinif, grup, H, filtre=None):
    """Gunluk ortalama sektore gore net getiri serisi (pozisyon olan gunler)."""
    n_gun = REL.shape[0]
    top, say = np.zeros(n_gun), np.zeros(n_gun)
    for o in olay:
        if o["sinif"] != sinif or o["grup"] != grup or (filtre and not filtre(o)):
            continue
        j = o["_j"]
        a, b = o["i0"] + 1, min(o["i0"] + H, n_gun - 1)
        if a > b:
            continue
        v = REL[a:b + 1, j]
        ok = np.isfinite(v)
        top[a:b + 1][ok] += v[ok]
        say[a:b + 1][ok] += 1
    m = say > 0
    return pd.Series(top[m] / say[m] - MALIYET / 100 / H, index=np.flatnonzero(m))


def seri_ozet(s, H):
    r = newey_west(list(s.values * 100), NW_LAG)
    if not r:
        return {"gun": len(s)}
    return {"gun": r["n"], "ort_esdeger": round(r["ort"] * H, 3), "t": r["t"]}


def pozisyon_getirisi(o, REL, H):
    a, b = o["i0"] + 1, o["i0"] + H
    if b >= REL.shape[0]:
        return None
    v = REL[a:b + 1, o["_j"]]
    return None if not np.isfinite(v).all() else float(v.sum()) * 100 - MALIYET


def main():
    os.makedirs(CIKTI, exist_ok=True)
    kap = json.load(open(KAP, encoding="utf-8")) if os.path.exists(KAP) else {}
    kd = set(liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in liste_oku("config/bist100_uyeler.txt") if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    sha = sha256(ON_KAYIT)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1", "on_kayit_sha256": sha,
           "deneme_no": len(kayit["denemeler"]) + 1}

    if kap.get("surum") != 2 or not kap.get("tamamlandi"):
        # 30.10: v1 dosyasi (donem atama hatali) "tamamlandi" gosterse de kullanilmaz; yalniz toplayici v2 verisi.
        out.update({"hukum": "VERI_YETERSIZ", "neden": f"KAP verisi v2 degil ya da tamamlanmadi (surum: {kap.get('surum')}, kalan gun: {kap.get('kalan_gun')})"})
    else:
        C, _, _, hata = panel_kur(evren, {})
        C = C[C.index >= pd.Timestamp("2021-01-01")]
        gunler = C.index
        R = C.pct_change()
        REL = (R - sektor_sepeti(R, SEKTOR100)).to_numpy(float)
        S_tum = sinyaller(list(C.columns))
        olay, kapsam = olaylari_kur(S_tum, kap.get("kayitlar", []), gunler, set(C.columns))
        kol = {k: j for j, k in enumerate(C.columns)}
        for o in olay:
            o["_j"] = kol[o["sembol"]]
        test_donem = [a for a in kapsam if "2021/03" <= a <= "2026/03"]
        toplam_b = sum(kapsam[a]["bulunan"] for a in test_donem)
        toplam_t = sum(kapsam[a]["toplam"] for a in test_donem)
        kapsam_oran = toplam_b / toplam_t if toplam_t else 0
        out.update({"kapsam_orani": round(kapsam_oran, 3), "kapsam_donem": kapsam, "fiyat_hatalari": hata,
                    "tavan_suphesi": kap.get("tavan_suphesi")})
        if kapsam_oran < KAPSAM_ESIK:
            out.update({"hukum": "VERI_YETERSIZ", "neden": f"kapsam %{kapsam_oran*100:.1f} < %{KAPSAM_ESIK*100:.0f}"})
        else:
            for o in olay:
                for h in (TUTMA, *TUTMA_EK):
                    o[f"getiri_{h}"] = pozisyon_getirisi(o, REL, h)

            def birincil(filtre=None):
                return {g: seri_ozet(takvim_serisi(olay, REL, "IYI", g, TUTMA, filtre), TUTMA) for g in ("IS", "OOS", "TAZE")}

            b = birincil()
            sezon = defaultdict(list)
            for o in olay:
                if o["sinif"] == "IYI" and o["grup"] == "OOS" and o.get(f"getiri_{TUTMA}") is not None:
                    sezon[o["donem"]].append(o[f"getiri_{TUTMA}"])
            sezon_ort = {a: round(float(np.mean(v)), 3) for a, v in sorted(sezon.items())}
            k4 = {}
            for s in sorted({o["sektor"] for o in olay if o["sektor"]}):
                k4[s] = birincil(lambda o, s=s: o["sektor"] != s)["OOS"].get("ort_esdeger")
            o_, i_ = b["OOS"], b["IS"]
            k = {"K1_oos_ort_pozitif": (o_.get("ort_esdeger") or -1) > 0,
                 "K2_oos_t": (o_.get("t") or -99) > T_ESIK,
                 "K3_oos_sezonlarin_60pct_pozitif": bool(sezon_ort) and sum(v > 0 for v in sezon_ort.values()) / len(sezon_ort) >= 0.6,
                 "K4_sektor_cikarma": bool(k4) and all(v is not None and v > 0 for v in k4.values()),
                 "K5_is_ort_pozitif": (i_.get("ort_esdeger") or -1) > 0}
            e = "GECTI" if all(k.values()) else ("ZAYIF" if k["K1_oos_ort_pozitif"] and k["K5_is_ort_pozitif"] else "ELENDI")
            ek = {}
            for g in ("IS", "OOS"):
                kotu = takvim_serisi(olay, REL, "KOTU", g, TUTMA)
                iyi = takvim_serisi(olay, REL, "IYI", g, TUTMA)
                ek[f"KOTU {TUTMA}g {g}"] = seri_ozet(kotu, TUTMA)
                ortak = iyi.index.intersection(kotu.index)
                ek[f"IYI-KOTU fark {TUTMA}g {g}"] = seri_ozet(iyi[ortak] - kotu[ortak], TUTMA)
                for h in TUTMA_EK:
                    ek[f"IYI {h}g {g}"] = seri_ozet(takvim_serisi(olay, REL, "IYI", g, h), h)
                ek[f"IYI bankalar haric {TUTMA}g {g}"] = seri_ozet(takvim_serisi(olay, REL, "IYI", g, TUTMA, lambda o: o["sektor"] != "Banka"), TUTMA)
                ek[f"IYI seans ici aciklama {TUTMA}g {g}"] = seri_ozet(takvim_serisi(olay, REL, "IYI", g, TUTMA, lambda o: o["seans_ici"]), TUTMA)
                ek[f"IYI seans disi aciklama {TUTMA}g {g}"] = seri_ozet(takvim_serisi(olay, REL, "IYI", g, TUTMA, lambda o: not o["seans_ici"]), TUTMA)
            sinif_orani = defaultdict(lambda: defaultdict(int))
            for o in olay:
                sinif_orani[o["donem"]][o["sinif"]] += 1
            out.update({"hukum": e, "kriterler": k, "birincil": b, "oos_sezon_ortalamalari": sezon_ort, "sektor_cikarma_oos": k4,
                        "ek": ek, "sinif_dagilimi": {a: dict(v) for a, v in sorted(sinif_orani.items())},
                        "ort_gecikme_gun": round(float(np.mean([o["gecikme_gun"] for o in olay])), 1) if olay else None,
                        "olay_sayisi": len(olay)})
            pd.DataFrame([{k_: v for k_, v in o.items() if not k_.startswith("_")} for o in olay]).to_csv(f"{CIKTI}/olaylar.csv", index=False)

    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    L = ["# H4b Bilanco Surprizi (KAP tarihli, takvim zamanli)", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{(sha or '-')[:16]}` | deneme no {out['deneme_no']} | t esigi {T_ESIK}", "",
         "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H4B.md'de.", "", f"## Hukum: **{out['hukum']}**", ""]
    if out.get("neden"):
        L.append(f"Neden: {out['neden']}")
    if out.get("birincil"):
        L += ["| Grup | Gun | 40g esdeger ort | t |", "|---|---|---|---|"]
        for g, v in out["birincil"].items():
            L.append(f"| IYI {g} | {v.get('gun')} | {v.get('ort_esdeger')} | {v.get('t')} |")
        L += [""] + [f"- {k_}: {'EVET' if v else 'HAYIR'}" for k_, v in out["kriterler"].items()]
        L += [f"- OOS sezon ortalamalari: {out['oos_sezon_ortalamalari']}", f"- Sektor cikarma OOS: {out['sektor_cikarma_oos']}",
              "", "## Hukum vermeyenler", "", "| Metrik | Gun | 40g/h esdeger ort | t |", "|---|---|---|---|"]
        for ad, v in out["ek"].items():
            L.append(f"| {ad} | {v.get('gun')} | {v.get('ort_esdeger')} | {v.get('t')} |")
        L += ["", f"Kapsam orani {out.get('kapsam_orani')} | olay {out.get('olay_sayisi')} | ort. aciklama gecikmesi {out.get('ort_gecikme_gun')} gun | tavan suphesi: {out.get('tavan_suphesi') or 'yok'}"]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": os.environ.get("GITHUB_SHA"), "hukum": out["hukum"]})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("H4b", out["hukum"], out.get("neden") or out.get("birincil", {}).get("OOS"))


if __name__ == "__main__":
    main()
