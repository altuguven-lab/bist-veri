#!/usr/bin/env python3
"""
ANALIST HEDEF ARSIVI VE REVIZYON GENISLIGI (19.11.2026) - SALT OLCUM, TAVSIYE DEGILDIR.

Neden: kurumlar "kazanc/hedef revizyon genisligi"ni (yukari revize edilen / asagi revize edilen oran) izler.
Bizde aracı kurum hedefleri elle giriliyordu (data/arastirma_hedef_fiyat.json, son kayit Agustos); deger_tarama.py
her calismada Yahoo analist ortalama hedefini (targetMeanPrice) ve analist sayisini cekiyor ama ARSIVLEMIYORDU.

Ne yapar: data/deger_tarama.json'daki yahoo_hedef / yahoo_analist / fiyat alanlarini gun tarihli anlik goruntu
olarak saklar (data/analist_hedef/arsiv/YYYY-MM-DD.json; ayni gun bir kez). En az 21 gun onceki en yakin anlik
goruntuyle karsilastirip hisse ve sektor bazinda hedef degisimini ve revizyon genisligini yazar.
Revizyon esigi: hedefteki degisim |%| >= 1 (Yahoo ortalamasi kucuk oynamalar yapar).
Sinirlar: Yahoo ortalamasi kac kurumdan olustugu ve ne zaman guncellendigi belirsiz bir toplamdir; analist sayisi
degisince ortalama kendiliginden kayar (bu durum ayrica isaretlenir). Getiri ongorusu test edilmedi.
Cikti: data/analist_hedef/revizyon.json, data/analist_hedef/revizyon.md
"""
import csv
import datetime as dt
import glob
import json
import os
import sys

ARSIV = "data/analist_hedef/arsiv"
ESIK = 1.0
MIN_GUN = 21


def main():
    try:
        d = json.load(open("data/deger_tarama.json", encoding="utf-8"))
    except Exception as e:
        print("HATA: deger_tarama.json okunamadi:", e); return 1
    gun = (d.get("uretim_utc") or dt.datetime.now(dt.timezone.utc).isoformat())[:10]
    os.makedirs(ARSIV, exist_ok=True)
    anlik = {r["kod"]: {"fiyat": r.get("fiyat"), "hedef": r.get("yahoo_hedef"), "analist": r.get("yahoo_analist")}
             for r in d.get("satirlar", []) if r.get("yahoo_hedef")}
    yol = f"{ARSIV}/{gun}.json"
    if not os.path.exists(yol) and anlik:
        json.dump({"gun": gun, "kaynak": "Yahoo targetMeanPrice (deger_tarama.py)", "hisseler": anlik},
                  open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sektor = {}
    try:
        for r in csv.DictReader(open("data/h6/guncel_siralama.csv", encoding="utf-8")):
            sektor[r.get("") or r.get("kod")] = r.get("sektor")
    except Exception:
        pass
    # karsilastirma: bugunden en az MIN_GUN once olan en YENI anlik goruntu
    sinir = (dt.date.fromisoformat(gun) - dt.timedelta(days=MIN_GUN)).isoformat()
    onceki = [p for p in sorted(glob.glob(f"{ARSIV}/*.json")) if os.path.basename(p)[:10] <= sinir]
    out = {"uretim_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "anlik_gun": gun,
           "anlik_sayisi": len(glob.glob(f"{ARSIV}/*.json")),
           "not": "Salt olcum, tavsiye degildir. Yahoo analist ortalama hedefi; analist sayisi degisirse ortalama "
                  "kendiliginden kayar (analist_degisti=true). Getiri ongorusu test edilmedi."}
    if not onceki:
        out["durum"] = f"KARSILASTIRMA_YOK: en az {MIN_GUN} gun onceki anlik goruntu bekleniyor (ilk arsiv {gun})"
        hisse, sek = [], {}
    else:
        o = json.load(open(onceki[-1], encoding="utf-8"))
        out["durum"] = "OK"; out["karsilastirma_gunu"] = o["gun"]
        hisse, sek = [], {}
        for k, v in anlik.items():
            e = o["hisseler"].get(k)
            if not e or not e.get("hedef") or not v.get("hedef"):
                continue
            deg = round((v["hedef"] / e["hedef"] - 1) * 100, 1)
            yon = "YUKARI" if deg >= ESIK else ("ASAGI" if deg <= -ESIK else "SABIT")
            satir = {"kod": k, "sektor": sektor.get(k), "eski_hedef": round(e["hedef"], 2), "yeni_hedef": round(v["hedef"], 2),
                     "degisim_pct": deg, "yon": yon, "analist_eski": e.get("analist"), "analist_yeni": v.get("analist"),
                     "analist_degisti": e.get("analist") != v.get("analist")}
            hisse.append(satir)
            s = sek.setdefault(sektor.get(k) or "?", {"YUKARI": 0, "ASAGI": 0, "SABIT": 0})
            s[yon] += 1
        for s in sek.values():
            n = s["YUKARI"] + s["ASAGI"] + s["SABIT"]
            s["genislik_pct"] = round((s["YUKARI"] - s["ASAGI"]) / n * 100, 1) if n else None
        hisse.sort(key=lambda x: -x["degisim_pct"])
        y = sum(1 for x in hisse if x["yon"] == "YUKARI"); a = sum(1 for x in hisse if x["yon"] == "ASAGI")
        out["genel"] = {"hisse": len(hisse), "yukari": y, "asagi": a,
                        "genislik_pct": round((y - a) / len(hisse) * 100, 1) if hisse else None}
    out["hisseler"] = hisse; out["sektorler"] = sek
    os.makedirs("data/analist_hedef", exist_ok=True)
    json.dump(out, open("data/analist_hedef/revizyon.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = [f"# Analist hedef revizyonlari - anlik {gun}", "", out["not"], "", f"Durum: {out['durum']}", ""]
    if hisse:
        g = out["genel"]
        L += [f"Karsilastirma: {out['karsilastirma_gunu']} -> {gun} | {g['hisse']} hisse | yukari {g['yukari']}, asagi {g['asagi']} | genislik %{g['genislik_pct']}", "",
              "## Sektorler", "", "| Sektor | Yukari | Asagi | Sabit | Genislik % |", "|---|---|---|---|---|"]
        for k, s in sorted(sek.items(), key=lambda kv: -(kv[1]["genislik_pct"] or 0)):
            L.append(f"| {k} | {s['YUKARI']} | {s['ASAGI']} | {s['SABIT']} | {s['genislik_pct']} |")
        L += ["", "## En cok yukari / asagi revize edilenler", "", "| Hisse | Eski | Yeni | Degisim % | Analist |", "|---|---|---|---|---|"]
        for x in hisse[:10] + hisse[-10:]:
            L.append(f"| {x['kod']} | {x['eski_hedef']} | {x['yeni_hedef']} | {x['degisim_pct']} | {x['analist_eski']}->{x['analist_yeni']}{' (degisti)' if x['analist_degisti'] else ''} |")
    L += ["", "Gozlem amaclidir, tavsiye degildir."]
    open("data/analist_hedef/revizyon.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(out["durum"], out.get("genel"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
