"""
H12 YUKSEK HACIMLI P4_HAZIRLIK - ILERIYE DONUK TEST. SALT OLCUM, TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H12.md (bu betikten ONCE commit edilmis olmali).
Girdi : data/alarm_karne_olaylar.csv (alarm_karne.py ciktisi), yfinance (plasebo icin, alarm_karne.fiyat_cek)
Cikti : data/h12/durum.json, data/h12/durum.md (her gun ara rapor), data/h12/deneme_kaydi.json (yalniz nihai hukum)
"""
import os, csv, json, math, datetime, hashlib
from collections import defaultdict
import pandas as pd

ON_KAYIT = "ON_KAYIT_H12.md"
CIKTI = "data/h12"
BASLANGIC = "2026-11-05T00:00:00Z"
BITIS_TARIH = "2027-04-30"
HEDEF_N, ASGARI_N = 100, 40
T_ESIK, T_ZAYIF = 2.0, 1.65
PLASEBO_KAYMA = 63
MALIYET = 0.25


def sha256(yol):
    return hashlib.sha256(open(yol, "rb").read()).hexdigest() if os.path.exists(yol) else None


def f(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def olaylari_oku():
    out = []
    for r in csv.DictReader(open("data/alarm_karne_olaylar.csv", encoding="utf-8")):
        if r["sinyal"] != "P4_HAZIRLIK" or r["zaman_utc"] < BASLANGIC:
            continue
        r["relvol_f"], r["net_T3_f"] = f(r["relvol"]), f(r["net_T3"])
        r["sek_T3_f"], r["net_T5_f"] = f(r["sek_rel_T3"]), f(r["net_T5"])
        out.append(r)
    return out


def ozet(rows, alan):
    from alarm_karne import kumelenmis
    v = [(r[alan], r["taban_gun"]) for r in rows if r.get(alan) is not None]
    if len(v) < 2:
        return {"n": len(v), "ort": None, "t": None}
    k = kumelenmis([a for a, _ in v], [g for _, g in v])
    return {"n": len(v), "ort": round(k["ort"], 3), "t": None if k["t"] is None else round(k["t"], 2), "gun": k["G"]}


def plasebo(rows):
    """Ayni sembol, taban gun 63 islem gunu once; XU100'e gore T+3, maliyet dusulu."""
    from alarm_karne import fiyat_cek
    bas = (pd.Timestamp(min(r["taban_gun"] for r in rows)) - pd.Timedelta(days=130)).date()
    xu, _ = fiyat_cek("XU100", bas)
    gunler = list(xu.index)
    poz = {g: i for i, g in enumerate(gunler)}
    cache, out = {}, []
    for r in rows:
        g0 = pd.Timestamp(r["taban_gun"])
        if g0 not in poz or poz[g0] - PLASEBO_KAYMA < 0:
            continue
        i0 = poz[g0] - PLASEBO_KAYMA
        a, b = gunler[i0], gunler[i0 + 3]
        kod = r["sembol"]
        if kod not in cache:
            try:
                cache[kod] = fiyat_cek(kod, bas)[0]
            except Exception:
                cache[kod] = None
        df = cache[kod]
        if df is None or a not in df.index or b not in df.index:
            continue
        rs = (df.at[b, "Close"] / df.at[a, "Close"] - 1) * 100
        rx = (xu.at[b, "Close"] / xu.at[a, "Close"] - 1) * 100
        out.append({"net_T3_f": rs - rx - MALIYET, "taban_gun": str(a.date())})
    return out


def main():
    os.makedirs(CIKTI, exist_ok=True)
    sha = sha256(ON_KAYIT)
    if not sha:
        raise SystemExit("ON_KAYIT_H12.md yok")
    tum = olaylari_oku()
    ana = [r for r in tum if r["relvol_f"] is not None and r["relvol_f"] >= 1.0]
    kar = [r for r in tum if r["relvol_f"] is not None and r["relvol_f"] < 1.0]
    ana_t3 = [r for r in ana if r["net_T3_f"] is not None]
    bugun = datetime.date.today().isoformat()
    bitti = len(ana_t3) >= HEDEF_N or bugun >= BITIS_TARIH

    o_ana, o_kar = ozet(ana, "net_T3_f"), ozet(kar, "net_T3_f")
    ek = {"sektore_gore_T3": ozet(ana, "sek_T3_f"), "net_T5": ozet(ana, "net_T5_f")}
    aylik = defaultdict(list)
    for r in ana_t3:
        aylik[r["taban_gun"][:7]].append(r["net_T3_f"])
    ek["aylik_ort"] = {k: round(sum(v) / len(v), 3) for k, v in sorted(aylik.items())}
    ek["en_buyuk_5"] = [{"sembol": r["sembol"], "gun": r["taban_gun"], "net_T3": round(r["net_T3_f"], 2)}
                        for r in sorted(ana_t3, key=lambda r: -abs(r["net_T3_f"]))[:5]]
    o_pl = {"n": 0, "ort": None, "t": None}
    if bitti and ana_t3:
        o_pl = ozet(plasebo(ana_t3), "net_T3_f")

    hukum = "ARA_RAPOR"
    if bitti:
        if len(ana_t3) < ASGARI_N or o_ana["t"] is None:
            hukum = "VERI_YETERSIZ"
        elif o_ana["ort"] > 0 and o_ana["t"] > T_ESIK:
            pl_ok = o_pl["t"] is not None and abs(o_pl["t"]) < T_ESIK and (o_pl["ort"] is None or o_ana["ort"] > o_pl["ort"])
            hukum = "GECTI" if pl_ok else "SUPHELI"
        elif o_ana["ort"] > 0 and o_ana["t"] > T_ZAYIF:
            hukum = "ZAYIF"
        else:
            hukum = "KENAR_YOK"

    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "on_kayit_sha256": sha,
           "git_sha": os.environ.get("GITHUB_SHA"), "hukum": hukum, "baslangic": BASLANGIC,
           "ilerleme": {"ana_T3_hesaplanan": len(ana_t3), "hedef": HEDEF_N, "bitis_tarihi": BITIS_TARIH},
           "ana_relvol_ge1": o_ana, "karsilastirma_relvol_lt1": o_kar, "plasebo_63g": o_pl, "ek": ek,
           "not": "Ara raporlar hukum degildir (ON_KAYIT_H12.md)."}
    json.dump(out, open(f"{CIKTI}/durum.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if hukum != "ARA_RAPOR":
        ky = f"{CIKTI}/deneme_kaydi.json"
        kayit = json.load(open(ky, encoding="utf-8")) if os.path.exists(ky) else {"denemeler": []}
        if not kayit["denemeler"]:                       # nihai hukum yalniz bir kez yazilir
            kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": out["git_sha"], "hukum": hukum})
            json.dump(kayit, open(ky, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# H12 Yuksek hacimli P4_HAZIRLIK - ileriye donuk", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit `{sha[:16]}` | durum **{hukum}**", "",
         "Salt olcum, tavsiye degildir. Ara raporlar hukum degildir.", "",
         f"Ilerleme: ana grupta T+3 hesaplanmis olay {len(ana_t3)} / {HEDEF_N} (bitis en gec {BITIS_TARIH})", "",
         "| Grup | n | Net T+3 ort % | t (gun kumelenmis) |", "|---|---|---|---|",
         f"| relvol >= 1 (ana) | {o_ana['n']} | {o_ana['ort']} | {o_ana['t']} |",
         f"| relvol < 1 (karsilastirma) | {o_kar['n']} | {o_kar['ort']} | {o_kar['t']} |",
         f"| Plasebo (63 gun once, yalniz nihai hukumde) | {o_pl['n']} | {o_pl['ort']} | {o_pl['t']} |", "",
         f"Ek: {json.dumps(ek, ensure_ascii=False)}"]
    open(f"{CIKTI}/durum.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
