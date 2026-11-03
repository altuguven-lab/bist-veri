"""
BIST 30/50/100 DONEMSEL UYELIK GECMISI (02.11.2026) - SALT VERI ISLEME, test degil.
Girdi: data/endeks_kap/liste.json + data/endeks_kap/ekler/*.pdf (KAP'taki Borsa Istanbul "BIST Pay Endeksleri"
       donemsel degisiklik ekleri, Turkce surum) ve guncel agirlik dosyasi (capa).
Yontem:
  1) Her donemsel duyurunun PDF'i pdftotext -layout ile metne cevrilir; "BIST 100/50/30 ENDEKSI" bolumlerinde
     ALINACAK / CIKARILACAK / YEDEK sutunlari baslik konumlarina gore ayrilir (kod = sira no'dan sonraki 3-6 harf).
  2) Capa (guncel liste) uzerinden geriye yurunur: onceki = simdiki - alinan + cikarilan.
  3) Tutarsizliklar (alinan listede yok / cikarilan listede var) kaydedilir: bunlar donem ARASI degisikliklerdir
     (Yakin Izleme Pazari, birlesme, kod degisikligi). Bu surumde ara degisiklikler uygulanmaz -> eski donemlerde
     uye sayisi 100'den sapabilir (2016'da ~107). Kullanan test bunu sinirlilik olarak yazar.
Cikti: data/endeks_uyelik/donemsel.json
  {"duyurular": [{idx, duyuru_tarihi, donem_bas, dosya, XU100:{al,cik,yedek}, ...}],
   "uyelik": {donem_bas: {XU100:[...], XU050:[...], XU030:[...]}}, "tutarsizlik": [...], "capa": ...}
Gereken: pdftotext (poppler-utils)
"""
import os, re, csv, json, subprocess, unicodedata, datetime

K = "data/endeks_kap"
CAPA = "data/endeks_kesif/dosyalar/guncel_endeks_agirlik_ds_genel.csv"
CIKTI = "data/endeks_uyelik/donemsel.json"
ENDEKS = {"100": "XU100", "50": "XU050", "30": "XU030"}
AD_RE = re.compile(r"\d{4}_0?\d_d[oö]nemsel|d[oö]nemsel_2016|donemsel_degisiklikler_2016|DYR_\d{4}_\d_TUR", re.I)


def pdf_metin(yol):
    return subprocess.run(["pdftotext", "-layout", yol, "-"], capture_output=True, text=True).stdout


def ayristir(txt):
    out, cur, cols = {}, None, None
    for s in txt.splitlines():
        u = s.upper()
        us = u.replace(" ", "")                      # bazi PDF'lerde basliklar harf aralikli: "B I ST 1 0 0 E N D E K Sİ"
        m = re.match(r"BIST(100|50|30)ENDEKS", us)
        if m:
            cur, cols = ENDEKS[m.group(1)], None
            out.setdefault(cur, {"al": [], "cik": [], "yedek": []})
            continue
        if us.startswith("BIST") and "ENDEKS" in us:
            cur = None
            continue
        if cur is None:
            continue
        if "ALINACAK" in u:
            c2 = u.find("ÇIKARILACAK") if "ÇIKARILACAK" in u else u.find("CIKARILACAK")
            cols = [c for c in (u.find("ALINACAK"), c2, u.find("YEDEK")) if c >= 0]
            continue
        if not cols:
            continue
        sinir = [(cols[j] + cols[j + 1]) / 2 for j in range(len(cols) - 1)]
        for mm in re.finditer(r"(?<![\w/.])(\d{1,2})\.?\s+([A-Z][A-Z0-9.]{2,7})(?!\w)", s):
            kod = mm.group(2).replace(".", "")
            if 3 <= len(kod) <= 6:
                out[cur][["al", "cik", "yedek"][sum(mm.start(2) > b for b in sinir)]].append(kod)
    return out


def donem_bas(txt):
    t = re.sub(r"(?<=\d) (?=[\d/.])|(?<=[/.]) (?=\d)", "", txt[:400])
    m = re.search(r"(\d{2})[/.](\d{2})[/.](\d{4})\s*[-–]", t)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def capa_oku():
    rows = list(csv.reader(open(CAPA, encoding="utf-8-sig", errors="replace"), delimiter=";"))
    h = [x.strip().upper() for x in rows[0]]
    ie = next(i for i, x in enumerate(h) if x.startswith(("ENDEKS KODU", "INDEX CODE")))
    ip = next(i for i, x in enumerate(h) if x.startswith(("PAY KODU", "EQUITY CODE")))
    tarih = sorted({r[0].strip() for r in rows[1:] if re.match(r"\d{2}/\d{2}/\d{4}", r[0].strip())})
    uy = {k: sorted({r[ip].split(".")[0].strip() for r in rows[1:] if len(r) > ip and r[ie].strip() == k}) for k in ENDEKS.values()}
    return uy, tarih[-1] if tarih else None


def main():
    e = json.load(open(f"{K}/liste.json", encoding="utf-8"))
    duyurular = []
    for idx, b in e["tum"].items():
        if b.get("subject") != "BIST Pay Endeksleri":
            continue
        for x in e["indirilen"].get(idx, []):
            ad = unicodedata.normalize("NFC", x.get("ad", ""))
            if not x.get("dosya") or re.search(r"periodic|_eng", ad, re.I) or not AD_RE.search(ad):
                continue
            txt = pdf_metin(f"{K}/ekler/{x['dosya']}")
            r = ayristir(txt)
            if not any(r.get(k, {}).get("al") or r.get(k, {}).get("cik") for k in ENDEKS.values()) and "XU100" not in r:
                continue
            g, a, y = b["publishDate"][:10].split(".")
            duyurular.append({"idx": int(idx), "duyuru_tarihi": f"{y}-{a}-{g}", "duyuru_saati": b["publishDate"][11:],
                              "donem_bas": donem_bas(txt), "dosya": ad, **{k: r.get(k, {"al": [], "cik": [], "yedek": []}) for k in ENDEKS.values()}})
    duyurular.sort(key=lambda d: d["idx"])
    capa, capa_tarih = capa_oku()
    uyelik, tutarsiz = {}, []
    m = {k: set(v) for k, v in capa.items()}
    for d in reversed(duyurular):
        uyelik[d["donem_bas"]] = {k: sorted(v) for k, v in m.items()}
        for k in ENDEKS.values():
            al, cik = d[k]["al"], d[k]["cik"]
            for a in al:
                if a not in m[k]:
                    tutarsiz.append({"donem_bas": d["donem_bas"], "endeks": k, "tur": "alinan_listede_yok", "kod": a})
            for c in cik:
                if c in m[k]:
                    tutarsiz.append({"donem_bas": d["donem_bas"], "endeks": k, "tur": "cikarilan_listede_var", "kod": c})
            m[k] = (m[k] - set(al)) | set(cik)
    ilk = duyurular[0]
    uyelik["ONCESI_" + ilk["donem_bas"]] = {k: sorted(v) for k, v in m.items()}
    os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
    json.dump({"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "capa_tarihi": capa_tarih,
               "not": "Donem arasi degisiklikler uygulanmadi; tutarsizlik listesi bunlari gosterir.",
               "duyurular": duyurular, "uyelik": dict(sorted(uyelik.items())), "tutarsizlik": tutarsiz},
              open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    n = {k: sum(len(d[k]["al"]) for d in duyurular) for k in ENDEKS.values()}
    print(f"duyuru {len(duyurular)} ({duyurular[0]['donem_bas']} - {duyurular[-1]['donem_bas']}), alinan {n}, "
          f"tutarsizlik {len(tutarsiz)}, en eski XU100 uye sayisi {len(m['XU100'])}")


if __name__ == "__main__":
    main()
