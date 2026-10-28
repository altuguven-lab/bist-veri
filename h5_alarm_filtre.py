"""
H5 BILANCO LISTESIYLE ALARM FILTRESI (28.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H5.md (bu betikten ONCE commit edilir). Parametre secmez.
Girdi : data/alarm_karne_olaylar.csv, data/temel/ham_*.json, (giris gunleri icin) XU100 islem gunleri
Cikti : data/h5/sonuc.json, data/h5/sonuc.md, data/h5/deneme_kaydi.json
"""
import os, json, math, datetime
import pandas as pd

from alarm_karne import kumelenmis, TEST_IMZALARI
from h_testleri import fiyat_cek, sha256
from h4_bilanco_surprizi import sinyaller, bilgi_tarihi, liste_oku, MIN_SIRKET

ON_KAYIT = "ON_KAYIT_H5.md"
CIKTI = "data/h5"
KESIN_SON_TABAN = pd.Timestamp("2026-12-31")
KESIN_HUKUM_TARIHI = pd.Timestamp("2027-01-09")
MIN_N = 30
T_ESIK = 2.0


def gecerli_listeler(gunler, semboller):
    """[(baslangic, bitis_haric, (y,p), {kod: sinif})], giris gunune gore sirali."""
    S_tum = sinyaller(semboller)
    liste = []
    for (y, p), S in sorted(S_tum.items()):
        if len(S) < MIN_SIRKET:
            continue
        i = gunler.searchsorted(bilgi_tarihi(y, p))
        if i >= len(gunler):
            continue
        sira = sorted(S, key=lambda k: S[k])
        n3 = len(sira) // 3
        sinif = {k: "ORTA" for k in sira}
        sinif.update({k: "KOTU" for k in sira[:n3]})
        sinif.update({k: "IYI" for k in sira[-n3:]})
        liste.append([gunler[i], None, (y, p), sinif])
    for j in range(len(liste) - 1):
        liste[j][1] = liste[j + 1][0]
    return liste


def sinif_bul(kod, gun, listeler):
    for bas, bit, yp, sinif in listeler:
        if gun >= bas and (bit is None or gun < bit):
            return sinif.get(kod, "LISTE_YOK"), f"{yp[0]}/{yp[1]:02d}"
    return "LISTE_YOK", None


def ozet(df, alan):
    x = df.dropna(subset=[alan])
    if len(x) < 2:
        return {"n": len(x)}
    k = kumelenmis(list(x[alan]), list(x["taban_gun"]))
    return {"n": len(x), "gun": k["G"], "ort": round(k["ort"], 3), "se": None if k["se"] is None else round(k["se"], 4),
            "t": None if k["t"] is None else round(k["t"], 2), "isabet_pct": round(100 * float((x[alan] > 0).mean()), 1)}


def fark(a, b):
    if not a.get("se") or not b.get("se"):
        return {}
    d = a["ort"] - b["ort"]
    se = math.sqrt(a["se"] ** 2 + b["se"] ** 2)
    return {"fark": round(d, 3), "t": round(d / se, 2) if se else None}


def hukum(iyi, kotu, iyi5, fk, kesin):
    if not kesin:
        return "ARA_RAPOR"
    if iyi.get("n", 0) < MIN_N or kotu.get("n", 0) < MIN_N:
        return "YETERSIZ_ORNEK"
    if (fk.get("fark") or 0) <= 0:
        return "ELENDI"
    if (iyi.get("ort") or 0) > 0 and (iyi.get("t") or 0) > T_ESIK and (fk.get("t") or 0) > T_ESIK and (iyi5.get("ort") or 0) > 0:
        return "GECTI"
    return "ZAYIF"


def main():
    d = pd.read_csv("data/alarm_karne_olaylar.csv")
    d = d[d["yon"] == "YUKARI"].copy()
    d = d[[(r.sembol, r.sinyal, f"{r.alarm_fiyat:.2f}" if pd.notna(r.alarm_fiyat) else "") not in TEST_IMZALARI for r in d.itertuples()]]
    d["taban_ts"] = pd.to_datetime(d["taban_gun"])
    bugun = pd.Timestamp(datetime.date.today())
    kesin = bugun >= KESIN_HUKUM_TARIHI
    if kesin:
        d = d[d["taban_ts"] <= KESIN_SON_TABAN]
    xu = fiyat_cek("XU100")[0]["Close"]
    gunler = xu.index[xu.index >= pd.Timestamp("2025-06-01")]
    kd = set(liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in liste_oku("config/bist100_uyeler.txt") if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    listeler = gecerli_listeler(gunler, evren)
    sn = [sinif_bul(r.sembol, r.taban_ts, listeler) for r in d.itertuples()]
    d["liste_sinif"] = [x[0] for x in sn]
    d["liste_ceyrek"] = [x[1] for x in sn]

    grup = {g: d[d["liste_sinif"] == g] for g in ("IYI", "ORTA", "KOTU", "LISTE_YOK")}
    tablo = {g: {a: ozet(x, a) for a in ("net_T3", "net_T5", "sek_rel_T3")} for g, x in grup.items()}
    tablo["TUMU"] = {a: ozet(d, a) for a in ("net_T3", "net_T5", "sek_rel_T3")}
    fk3 = fark(tablo["IYI"]["net_T3"], tablo["KOTU"]["net_T3"])
    fk5 = fark(tablo["IYI"]["net_T5"], tablo["KOTU"]["net_T5"])
    e = hukum(tablo["IYI"]["net_T3"], tablo["KOTU"]["net_T3"], tablo["IYI"]["net_T5"], fk3, kesin)
    tur = {}
    for t, x in d.groupby("sinyal"):
        tur[t] = {g: ozet(x[x["liste_sinif"] == g], "net_T3") for g in ("IYI", "KOTU")}
    ay = {}
    for m, x in d.groupby(d["taban_ts"].dt.strftime("%Y-%m")):
        ay[m] = {g: ozet(x[x["liste_sinif"] == g], "net_T3") for g in ("IYI", "KOTU")}

    os.makedirs(CIKTI, exist_ok=True)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    sha = sha256(ON_KAYIT)
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1", "on_kayit_sha256": sha,
           "deneme_no": len(kayit["denemeler"]) + 1, "kesin_hukum": kesin, "hukum": e,
           "olay_araligi": [str(d["taban_gun"].min()), str(d["taban_gun"].max())] if len(d) else None,
           "gruplar": tablo, "fark_iyi_kotu_T3": fk3, "fark_iyi_kotu_T5": fk5, "ture_gore_T3": tur, "aya_gore_T3": ay,
           "listeler": [{"ceyrek": f"{yp[0]}/{yp[1]:02d}", "baslangic": str(b.date()), "bitis_haric": None if t is None else str(t.date()),
                         "sirket": len(s)} for b, t, yp, s in listeler if t is None or t >= pd.Timestamp("2026-06-01")]}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    g = lambda grp, a, k: tablo[grp][a].get(k)
    L = ["# H5 Bilanco Listesiyle Alarm Filtresi", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{(sha or '-')[:16]}` | deneme no {out['deneme_no']} | "
         f"{'KESIN HUKUM' if kesin else 'ARA RAPOR (kesin hukum 09.01.2027 sonrasi, 31.12.2026 dahil alarmlarla)'}", "",
         "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H5.md'de.", "", f"## Hukum: **{e}**", "",
         "| Grup | Olay | Gun | Net T+3 (t) | Isabet % | Net T+5 (t) | Sektore gore T+3 |", "|---|---|---|---|---|---|---|"]
    for grp in ("IYI", "ORTA", "KOTU", "LISTE_YOK", "TUMU"):
        L.append(f"| {grp} | {g(grp,'net_T3','n')} | {g(grp,'net_T3','gun')} | {g(grp,'net_T3','ort')} ({g(grp,'net_T3','t')}) | "
                 f"{g(grp,'net_T3','isabet_pct')} | {g(grp,'net_T5','ort')} ({g(grp,'net_T5','t')}) | {g(grp,'sek_rel_T3','ort')} |")
    L += ["", f"- IYI - KOTU fark T+3: {fk3} | T+5: {fk5}", f"- Olay araligi: {out['olay_araligi']}",
          f"- Gecerli listeler: {out['listeler']}", "", "## Ture gore net T+3 (IYI / KOTU)", ""]
    for t, v in tur.items():
        L.append(f"- {t}: IYI {v['IYI'].get('n')} olay ort {v['IYI'].get('ort')} | KOTU {v['KOTU'].get('n')} olay ort {v['KOTU'].get('ort')}")
    L += ["", "## Aya gore net T+3 (IYI / KOTU)", ""]
    for m, v in ay.items():
        L.append(f"- {m}: IYI {v['IYI'].get('n')} / {v['IYI'].get('ort')} | KOTU {v['KOTU'].get('n')} / {v['KOTU'].get('ort')}")
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": os.environ.get("GITHUB_SHA"),
                               "hukum": e, "kesin": kesin})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("H5", e, "IYI", tablo["IYI"]["net_T3"], "KOTU", tablo["KOTU"]["net_T3"], "fark", fk3)


if __name__ == "__main__":
    main()
