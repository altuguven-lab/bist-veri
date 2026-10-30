"""
BIST ENDEKS UYELIK GECMISI - INTERNET ARSIVI (30.10.2026). SALT VERI TOPLAMA, test degil.
Kaynak: Borsa Istanbul'un endeks agirlik dosyasi (files/endeks_agirlik_ds_genel.csv) her donem guncellenir.
Gecmis surumleri Internet Archive (web.archive.org) anlik goruntulerinden alinir.
Adimlar:
  1) CDX API ile dosyanin (ve bilinen eski adres bicimlerinin) tum anlik goruntulerini listeler.
  2) Icerigi ayni olanlari (digest) tekillestirir, her birini indirir (data/endeks_uyelik/ham/).
  3) Dosyadaki TARIH sutunuyla BIST 30 / 50 / 100 uyelerini cikarir.
Cikti: data/endeks_uyelik/uyelik.json  {tarih: {"XU030": [...], "XU050": [...], "XU100": [...]}, ...}
       data/endeks_uyelik/ozet.json   (anlik goruntu listesi, hatalar)
Kaldigi yerden devam eder (indirilen digest'ler atlanir).
"""
import os, re, csv, io, json, time, datetime, urllib.request, urllib.parse

CIKTI = "data/endeks_uyelik"
UA = {"User-Agent": "Mozilla/5.0 (compatible; bist-veri-arastirma/1.0; kisisel arastirma)"}
ADRESLER = [
    "borsaistanbul.com/files/endeks_agirlik_ds_genel.csv",
    "www.borsaistanbul.com/files/endeks_agirlik_ds_genel.csv",
    "borsaistanbul.com/data/endeks/endeks_agirlik_ds_genel.csv",
    "www.borsaistanbul.com/data/endeks/endeks_agirlik_ds_genel.csv",
]
ENDEKSLER = {"XU030", "XU050", "XU100"}
BEKLE = float(os.environ.get("BEKLE_SN", "2.0"))


def getir(url, ikili=True, zaman=60):
    son = None
    for deneme in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=zaman) as r:
                v = r.read()
            return v if ikili else v.decode("utf-8", errors="replace")
        except Exception as e:
            son = e
            time.sleep(6 * (deneme + 1))
    raise son


def cdx(adres):
    q = urllib.parse.urlencode({"url": adres, "output": "json", "filter": "statuscode:200", "collapse": "digest"})
    satirlar = json.loads(getir(f"https://web.archive.org/cdx/search/cdx?{q}", ikili=False, zaman=90) or "[]")
    if not satirlar:
        return []
    bas = satirlar[0]
    return [dict(zip(bas, s)) for s in satirlar[1:]]


def ayristir(veri):
    for kod in ("utf-8-sig", "cp1254", "latin-1"):
        try:
            metin = veri.decode(kod)
            break
        except UnicodeDecodeError:
            continue
    satirlar = list(csv.reader(io.StringIO(metin), delimiter=";"))
    if not satirlar:
        return {}
    bas = [h.strip().upper() for h in satirlar[0]]
    def sutun(*adaylar):
        for a in adaylar:
            for i, h in enumerate(bas):
                if h.startswith(a):
                    return i
        return None
    i_tarih, i_endeks, i_pay = sutun("TARIH", "DATE"), sutun("ENDEKS KODU", "INDEX CODE"), sutun("PAY KODU", "EQUITY CODE")
    i_duz = sutun("DUZELTME", "BEFORE ADJ")
    if None in (i_tarih, i_endeks, i_pay):
        return {"_hata": f"sutun bulunamadi: {bas[:8]}"}
    out = {}
    for s in satirlar[1:]:
        if len(s) <= max(i_tarih, i_endeks, i_pay):
            continue
        e = s[i_endeks].strip().upper()
        if e not in ENDEKSLER:
            continue
        if i_duz is not None and len(s) > i_duz and "BEFORE" in s[i_duz].upper():
            continue                       # duzeltme oncesi satirlar degil, sonrasi esas
        t = s[i_tarih].strip()
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", t)
        if not m:
            continue
        tarih = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        kod = s[i_pay].strip().upper().split(".")[0]
        out.setdefault(tarih, {}).setdefault(e, set()).add(kod)
    return {t: {e: sorted(v) for e, v in d.items()} for t, d in out.items()}


def main():
    os.makedirs(f"{CIKTI}/ham", exist_ok=True)
    yol_u, yol_o = f"{CIKTI}/uyelik.json", f"{CIKTI}/ozet.json"
    uyelik = json.load(open(yol_u, encoding="utf-8")) if os.path.exists(yol_u) else {}
    ozet = json.load(open(yol_o, encoding="utf-8")) if os.path.exists(yol_o) else {"goruntuler": {}, "hatalar": []}
    for adres in ADRESLER:
        try:
            liste = cdx(adres)
        except Exception as e:
            ozet["hatalar"].append(f"cdx {adres}: {str(e)[:80]}")
            continue
        for g in liste:
            dg = g.get("digest")
            if not dg or dg in ozet["goruntuler"]:
                continue
            url = f"https://web.archive.org/web/{g['timestamp']}id_/{g['original']}"
            try:
                veri = getir(url)
                open(f"{CIKTI}/ham/{g['timestamp']}_{dg[:8]}.csv", "wb").write(veri)
                p = ayristir(veri)
                if "_hata" in p:
                    ozet["goruntuler"][dg] = {"zaman": g["timestamp"], "adres": adres, "hata": p["_hata"]}
                else:
                    for t, d in p.items():
                        uyelik.setdefault(t, {}).update(d)
                    ozet["goruntuler"][dg] = {"zaman": g["timestamp"], "adres": adres, "tarihler": sorted(p)}
            except Exception as e:
                ozet["goruntuler"][dg] = {"zaman": g["timestamp"], "adres": adres, "hata": str(e)[:80]}
            json.dump(dict(sorted(uyelik.items())), open(yol_u, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
            json.dump(ozet, open(yol_o, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            time.sleep(BEKLE)
    ozet["guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ozet["tarih_sayisi"] = len(uyelik)
    ozet["ilk_son"] = [min(uyelik), max(uyelik)] if uyelik else None
    json.dump(dict(sorted(uyelik.items())), open(yol_u, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(ozet, open(yol_o, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"goruntu {len(ozet['goruntuler'])}, uyelik tarihi {len(uyelik)}, aralik {ozet['ilk_son']}, hata {len(ozet['hatalar'])}")


if __name__ == "__main__":
    main()
