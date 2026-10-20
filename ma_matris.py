"""MA MATRISI (20.10.2026) - data/ma<P>_tarama.json dosyalarindan 100 x periyot sapma matrisi.
Cikti: data/ma_matris.json (satirlar) + data/ma_matris.csv. Salt olcum.
Sapma % = (fiyat/SMA-1)*100; fiyat seans ici olabilir; bedelsiz duzeltmesi yaklasiktir."""
import json, glob, re, csv
dosyalar = {}
for y in glob.glob("data/ma*_tarama.json"):
    m = re.search(r"ma(\d+)_tarama\.json$", y)
    if m: dosyalar[int(m.group(1))] = y
P = sorted(dosyalar)
S, uretim = {}, ""
for p in P:
    d = json.load(open(dosyalar[p], encoding="utf-8"))
    uretim = max(uretim, d.get("uretim_utc", ""))
    for r in d["ma_alti"] + d["ma_ustu"]:
        S.setdefault(r["kod"], {})[p] = r["sapma_pct"]
    for r in d.get("yetersiz_veri", []):
        S.setdefault(r["kod"], {})
rows = []
for k, v in S.items():
    row = {"kod": k}
    for p in P: row[f"ma{p}"] = v.get(p)
    vals = [v[p] for p in P if p in v]
    row["alti_sayisi"] = sum(1 for x in vals if x < 0)
    row["olculen"] = len(vals)
    row["ort_sapma"] = round(sum(vals) / len(vals), 1) if vals else None
    rows.append(row)
rows.sort(key=lambda r: (-r["alti_sayisi"], r["ort_sapma"] if r["ort_sapma"] is not None else 0))
json.dump({"uretim_utc": uretim, "periyotlar": P, "satirlar": rows},
          open("data/ma_matris.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open("data/ma_matris.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} hisse, periyotlar {P}")
