#!/usr/bin/env python3
"""
BIST100 TARAMA (19.11.2026) - SALT OLCUM, TAVSIYE DEGILDIR.

Soru: BIST100'de hangi hisseler hem (a) bilanco surprizi yuksek hem (b) tahmini degerinin altinda?
Neden bu iki suzgec: kendi testlerimizde (H6, ON_KAYIT_H6.md) test doneminde (OOS 2024-01..2026-06) yalniz
F5 bilanco surprizi anlamli cikti (evrene gore aylik +1,18 puan, t 2,37, BH anlamli). Deger (F3) tek basina
OOS'ta ise yaramadi (t 0,45); burada yalniz ikinci suzgec ve "fiyat/tahmin tutarliligi" olarak kullanilir.
H8 (14 baska etki) ve V163 alarmlari (plasebo) secici cikmadi. Kanit AYLIK ufuktadir; kisa vade icin kanit yok.

Girdi : data/deger_tarama.json (deger_tarama.py; 3 yontem medyani, guven, yontem dagilimi)
        data/h6/guncel_siralama.csv (h6_faktor_siralama.py; F5 ve bilesik sira yuzdelikleri, ust dilim)
        data/kurum_kumesi.json, data/arsiv/kap (son 10 gun pay bazli devre kesici), config/kapsam_disi.txt
Cikti : data/bist100_tarama.json, data/bist100_tarama.md
        data/bist100_tarama/arsiv/YYYY-MM-DD.json (her yeni H6 sirlamasi icin bir kez dondurulur; ileride
        "o gun listelenenler sonra evrene gore ne yapti" sorusu bu arsivden cevaplanir - ayri on kayit gerekir)

Katmanlar:
  K1: F5 >= 0.80 (ust %20) VE deger potansiyeli > 0 VE guven "orta"   (tutarlilik: yontem dagilimi kucukten buyuge)
  K2: bilesik ust dilim VE potansiyel > 0 VE guven "orta" (K1 disi)
  K3: F5 >= 0.80 ama degerlenemeyen (zarar, sermaye kalemi yok, iki yontem yok) - deger yorumu yapilmaz
Etiketler: kapsam_disi (Baskan karari 23.10: aday listesine alinmaz, etiketlenir), kucuk (piyasa degeri alt %30; yalniz temel_carpan dosyasinda piyasa_degeri_tl varsa -
  X5 kucuk buyukluk OOS'ta ise yaramadi), devre_kesici_10g, kurum_kumesi (son 14 gun; liste sirket hakkinda hukum degil).
"""
import csv
import datetime as dt
import glob
import gzip
import json
import os
import sys

TR = dt.timezone(dt.timedelta(hours=3))
CIKTI = "data/bist100_tarama.json"
MD = "data/bist100_tarama.md"
ARSIV = "data/bist100_tarama/arsiv"
F5_ESIK = 0.80


def oku_json(yol, varsayilan=None):
    try:
        return json.load(open(yol, encoding="utf-8"))
    except Exception as e:
        print(f"UYARI: {yol} okunamadi: {e}", file=sys.stderr)
        return varsayilan


def kapsam_disi():
    try:
        return {l.strip() for l in open("config/kapsam_disi.txt", encoding="utf-8")
                if l.strip() and not l.startswith("#")}
    except Exception:
        return set()


def devre_kesici(gun=10):
    say = {}
    for p in sorted(glob.glob("data/arsiv/kap/*/*/*.json.gz"))[-gun:]:
        try:
            for x in json.load(gzip.open(p)).get("bildirimler", []):
                if "Devre Kesici" in (x.get("subject") or ""):
                    for s in (x.get("relatedStocks") or x.get("stockCodes") or "").replace(" ", "").split(","):
                        if s:
                            say[s] = say.get(s, 0) + 1
        except Exception:
            pass
    return say


def kume_uyeligi(gun=14):
    k = oku_json("data/kurum_kumesi.json", {}) or {}
    sinir = (dt.datetime.now(TR).date() - dt.timedelta(days=gun)).isoformat()
    uye = {}
    for c in k.get("kumeler", []):
        if c.get("tarih", "") < sinir:
            continue
        for s in (c.get("hisseler") or c.get("kodlar") or []):
            uye.setdefault(s, []).append(f"{c.get('tarih')} {c.get('konu', '')[:45]}")
    return uye


def main():
    deger = oku_json("data/deger_tarama.json")
    if not deger:
        print("HATA: deger_tarama.json yok"); return 1
    d = {r["kod"]: r for r in deger["satirlar"]}
    atlanan = {a.split(":")[0]: a.split(":", 1)[1].strip() for a in deger.get("atlanan", []) if ":" in a}
    h6 = {}
    try:
        for r in csv.DictReader(open("data/h6/guncel_siralama.csv", encoding="utf-8")):
            kod = r.get("") or r.get("kod")
            h6[kod] = {"bilesik": float(r["skor"]) if r.get("skor") else None,
                       "f5": float(r["F5_bilanco_surprizi"]) if r.get("F5_bilanco_surprizi") else None,
                       "f3": float(r["F3_deger"]) if r.get("F3_deger") else None,
                       "sektor": r.get("sektor"), "ust": r.get("ust_dilim") == "True"}
    except Exception as e:
        print("HATA: h6 siralamasi okunamadi:", e); return 1
    h6_tarih = None
    try:
        h6_tarih = (oku_json("data/h6/sonuc.json", {}) or {}).get("uretim_utc") or \
                   dt.datetime.fromtimestamp(os.path.getmtime("data/h6/guncel_siralama.csv"), dt.timezone.utc).isoformat()
    except Exception:
        pass

    kd, dk, kume = kapsam_disi(), devre_kesici(), kume_uyeligi()
    # kucukluk: piyasa degeri yok ise fiyat x adet bilinmiyor -> temel_carpan'dan 'piyasa_degeri' varsa kullan
    pd_ = {}
    tc = (oku_json("data/temel_carpan_bist100.json", {}) or {}).get("semboller", {})
    for k, v in tc.items():
        pdv = (v.get("ek_olculer") or {}).get("piyasa_degeri_tl") or v.get("piyasa_degeri_tl")
        if pdv:
            pd_[k] = pdv
    kucuk_sinir = sorted(pd_.values())[int(len(pd_) * 0.3)] if len(pd_) >= 10 else None

    def satir(kod):
        r, h = d.get(kod, {}), h6.get(kod, {})
        et = []
        if kod in kd: et.append("kapsam_disi")
        if kucuk_sinir and pd_.get(kod) and pd_[kod] <= kucuk_sinir: et.append("kucuk")
        if dk.get(kod): et.append(f"devre_kesici_10g={dk[kod]}")
        if kume.get(kod): et.append(f"kurum_kumesi={len(kume[kod])}")
        return {"kod": kod, "sektor": h.get("sektor"), "f5": h.get("f5"), "bilesik": h.get("bilesik"),
                "bilesik_ust": h.get("ust"), "fiyat": r.get("fiyat"), "tahmini_deger": r.get("tahmini_deger"),
                "potansiyel_pct": r.get("potansiyel_pct"), "guven": r.get("guven"),
                "yontem_dagilimi_pct": r.get("yontem_dagilimi_pct"), "yahoo_potansiyel_pct": r.get("yahoo_potansiyel_pct"),
                "yahoo_analist": r.get("yahoo_analist"), "son_bilanco": r.get("son_bilanco"),
                "degerlenmedi": atlanan.get(kod) if kod not in d else None, "etiketler": et,
                "kume_ayrinti": kume.get(kod, [])}

    k1, k2, k3 = [], [], []
    for kod, h in h6.items():
        r = d.get(kod)
        if h.get("f5") is not None and h["f5"] >= F5_ESIK:
            if r and r["guven"] == "orta" and r["potansiyel_pct"] > 0:
                k1.append(satir(kod))
            elif not r:
                k3.append(satir(kod))
        if h.get("ust") and r and r["guven"] == "orta" and r["potansiyel_pct"] > 0 and not (h.get("f5") and h["f5"] >= F5_ESIK):
            k2.append(satir(kod))
    k1.sort(key=lambda x: x["yontem_dagilimi_pct"])
    k2.sort(key=lambda x: -x["potansiyel_pct"])
    k3.sort(key=lambda x: -(x["f5"] or 0))

    simdi = dt.datetime.now(TR)
    out = {"uretim_tr": simdi.strftime("%Y-%m-%d %H:%M"),
           "deger_tarama_uretim_utc": deger.get("uretim_utc"), "h6_siralama_tarihi": h6_tarih,
           "not": "Salt olcum, tavsiye degildir. K1 = bilanco surprizi ust %20 + tahmini degerin altinda (orta guven). "
                  "Kanit AYLIK ufukta (H6 F5); kisa vade icin kanit yok. Deger tek basina OOS'ta ise yaramadi (H6 F3). "
                  "Kurum kumesi/MKK listesinde yer almak sirket hakkinda hukum degildir.",
           "k1": k1, "k2": k2, "k3": k3}

    # arsiv: ayni H6 siralamasi icin bir kez (siralama yenilenince yeni anlik goruntu)
    os.makedirs(ARSIV, exist_ok=True)
    anahtar = (h6_tarih or "")[:10] or simdi.strftime("%Y-%m-%d")
    yol = f"{ARSIV}/{anahtar}.json"
    if not os.path.exists(yol):
        json.dump({**out, "dondurma_tr": out["uretim_tr"]}, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # onceki anlik goruntulerin K1 listesi, bugunku deger_tarama fiyatiyla (gozlem; hukum degil)
    gecmis = []
    for p in sorted(glob.glob(f"{ARSIV}/*.json")):
        if p == yol:
            continue
        g = oku_json(p, {})
        sat = []
        for x in g.get("k1", []):
            simdiki = (d.get(x["kod"]) or {}).get("fiyat")
            if simdiki and x.get("fiyat"):
                sat.append({"kod": x["kod"], "o_gun": x["fiyat"], "bugun": simdiki,
                            "degisim_pct": round((simdiki / x["fiyat"] - 1) * 100, 1)})
        gecmis.append({"anlik": os.path.basename(p)[:-5], "k1": sat,
                       "k1_ort_pct": round(sum(s["degisim_pct"] for s in sat) / len(sat), 1) if sat else None})
    out["onceki_anliklar"] = gecmis

    tmp = CIKTI + ".tmp"
    json.dump(out, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, CIKTI)

    def tablo(liste, baslik):
        L = [f"## {baslik}", ""]
        if not liste:
            return L + ["(yok)", ""]
        L += ["| Hisse | Sektor | F5 | Bilesik | Fiyat | Tahmini deger | Potansiyel % | Yontem dagilimi % | Analist ort % (n) | Bilanco | Etiket |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in liste:
            L.append(f"| {x['kod']} | {x['sektor'] or '-'} | {x['f5']} | {x['bilesik']} | {x['fiyat'] or '-'} | "
                     f"{x['tahmini_deger'] or '-'} | {x['potansiyel_pct'] if x['potansiyel_pct'] is not None else '-'} | "
                     f"{x['yontem_dagilimi_pct'] if x['yontem_dagilimi_pct'] is not None else '-'} | "
                     f"{x['yahoo_potansiyel_pct'] if x['yahoo_potansiyel_pct'] is not None else '-'} ({x['yahoo_analist'] or 0}) | "
                     f"{x['son_bilanco'] or '-'} | {', '.join(([x['degerlenmedi']] if x['degerlenmedi'] else []) + x['etiketler']) or '-'} |")
        return L + [""]

    L = [f"# BIST100 tarama - {out['uretim_tr']}", "",
         f"Deger taramasi: {out['deger_tarama_uretim_utc']} | H6 siralamasi: {h6_tarih}", "", out["not"], ""]
    L += tablo(k1, "K1 - Bilanco surprizi ust %20 + tahmini degerin altinda (orta guven; tutarliliga gore)")
    L += tablo(k2, "K2 - Bilesik skor ust dilim + tahmini degerin altinda (orta guven)")
    L += tablo(k3, "K3 - Bilanco surprizi ust %20 ama degerlenemeyen (deger yorumu yok)")
    if gecmis:
        L += ["## Onceki anlik goruntuler (gozlem, hukum degil)", ""]
        for g in gecmis:
            L.append(f"- {g['anlik']}: K1 ort {g['k1_ort_pct']}% | " +
                     ", ".join(f"{s['kod']} {s['degisim_pct']}%" for s in g["k1"]))
        L.append("")
    L += ["Gozlem amaclidir, tavsiye degildir."]
    open(MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(json.dumps({"k1": [x["kod"] for x in k1], "k2": [x["kod"] for x in k2], "k3": [x["kod"] for x in k3]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
