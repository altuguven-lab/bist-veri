#!/usr/bin/env python3
"""TEMEL VERI TOPLAYICI - ADIM 1 (KESIF) - SALT OLCUM, Pine'a dokunmaz (Kulucka/IP-3 uyumlu).
Is Yatirim MaliTablo servisinden 30 sembol icin ceyreklik mali tablo ham verisini ceker (TL ve USD).
KESIF=1 (varsayilan): yalniz 4 sembol, ham kalemleri + hatalari data/temel/kesif.json'a yazar
(sandbox servise erisemedigi icin kalem kodlari ve yanit bicimi buradan dogrulanir).
KESIF=0: 30 sembol, ham veriyi data/temel/ham_<SEMBOL>.json'a yazar."""
import json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

SEMBOLLER = ["AKBNK","YKBNK","GARAN","ISCTR","SAHOL","KCHOL","THYAO","TAVHL","EREGL","ASELS","ASTOR","MGROS",
 "BIMAS","TUPRS","TOASO","FROTO","ENKAI","TTKOM","AEFES","PGSUS","HALKB","VAKBN","OTKAR","PETKM","SISE",
 "EKGYO","TRMET","ALARK","ENJSA","ULKER"]
KESIF_SEMBOLLER = ["AKBNK","KCHOL","THYAO","EREGL"]   # banka, holding, sanayi, havacilik
GRUPLAR = ["XI_29","UFRS","UFRS_K"]                   # sirket tipine gore denenir
URL = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
UA = "Mozilla/5.0 (bist-veri temel_veri_topla)"
BASLANGIC_YIL = 2021
KESIF = os.environ.get("KESIF", "1") == "1"
CIKTI = "data/temel"

def ceyrekler():
    t = datetime.now(timezone.utc) + timedelta(hours=3)
    out = []
    for y in range(BASLANGIC_YIL, t.year + 1):
        for p in (3, 6, 9, 12):
            if (y, p) <= (t.year, t.month):
                out.append((y, p))
    return out

def cek(sembol, borsa, grup, donemler):
    q = {"companyCode": sembol, "exchange": borsa, "financialGroup": grup}
    for i, (y, p) in enumerate(donemler, 1):
        q[f"year{i}"] = y; q[f"period{i}"] = p
    req = urllib.request.Request(URL + "?" + urllib.parse.urlencode(q), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sembol_ham(sembol, hata_log):
    """Her borsa (TRY/USD) icin tum ceyrekleri 4'lu paketlerle ceker; ilk islevsel grubu secer."""
    sonuc = {}
    donemler = ceyrekler()
    for borsa in ("TRY", "USD"):
        secilen, kalemler = None, {}
        for grup in GRUPLAR:
            deneme, ok = {}, False
            for i in range(0, len(donemler), 4):
                paket = donemler[i:i+4]
                if len(paket) < 4:      # servis 4 donem ister: son paketi geriye dogru tamamla
                    paket = donemler[-4:]
                try:
                    d = cek(sembol, borsa, grup, paket)
                    for it in d.get("value") or []:
                        kod = it.get("itemCode")
                        e = deneme.setdefault(kod, {"ad": it.get("itemDescTr"), "v": {}})
                        for j, (y, p) in enumerate(paket, 1):
                            v = it.get(f"value{j}")
                            if v is not None:
                                e["v"][f"{y}/{p:02d}"] = v
                        ok = ok or bool(d.get("value"))
                except Exception as ex:
                    hata_log.append(f"{sembol} {borsa} {grup} {paket[0]}: {type(ex).__name__}: {str(ex)[:120]}")
                time.sleep(0.4)
            if ok and deneme:
                secilen, kalemler = grup, deneme
                break
        sonuc[borsa] = {"grup": secilen, "kalem_sayisi": len(kalemler), "kalemler": kalemler}
    return sonuc

def main():
    os.makedirs(CIKTI, exist_ok=True)
    liste = KESIF_SEMBOLLER if KESIF else SEMBOLLER
    hata_log, ozet = [], {}
    for s in liste:
        ham = sembol_ham(s, hata_log)
        if KESIF:
            ozet[s] = {b: {"grup": ham[b]["grup"], "kalem_sayisi": ham[b]["kalem_sayisi"],
                           "ornek_kalemler": [{"kod": k, "ad": v["ad"], "ornek": dict(list(v["v"].items())[-2:])}
                                              for k, v in list(ham[b]["kalemler"].items())]}
                       for b in ham}
        else:
            json.dump(ham, open(f"{CIKTI}/ham_{s}.json", "w", encoding="utf-8"), ensure_ascii=False)
            ozet[s] = {b: ham[b]["kalem_sayisi"] for b in ham}
    kayit = {"olusturma_utc": datetime.now(timezone.utc).isoformat(), "mod": "KESIF" if KESIF else "TAM",
             "ceyrek_sayisi": len(ceyrekler()), "hatalar": hata_log[:60], "ozet": ozet}
    json.dump(kayit, open(f"{CIKTI}/kesif.json" if KESIF else f"{CIKTI}/toplama_ozeti.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps({s: {b: (v if not KESIF else v["kalem_sayisi"]) for b, v in d.items()} for s, d in ozet.items()}, ensure_ascii=False))
    print("hata sayisi:", len(hata_log))

if __name__ == "__main__":
    main()
