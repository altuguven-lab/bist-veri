#!/usr/bin/env python3
"""
KESIF: TURKIYE 5 YILLIK CDS KAYNAGI (19.11.2026) - SALT KESIF, VERI URETMEZ.

Neden: Kullanici 19.11'de gunluk brifinge guncel CDS istedi. Claude'un ortamindan denenen kaynaklar:
worldgovernmentbonds (deger JavaScript ile yukleniyor, sayfa bos), CNBC quote (acilmadi), doviz724 (2024 verisi).
Bu betik GitHub Actions'ta aday sayfalari robots.txt'e uyarak bir kez ceker, ham HTML'i saklar ve sayfada
CDS degerine benzeyen sayilari arar. Hangi kaynagin sunucu tarafinda deger verdigi buradan anlasilir; ancak
ondan sonra gunluk toplayici yazilir (tahminle toplayici yazilmaz).
Cikti: data/kesif/cds.json, data/kesif/cds_ham/<ad>.html (en fazla 400 KB)
"""
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
import urllib.robotparser

UA_AD = "bist-veri-arastirma"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; {UA_AD}/1.0; kisisel arastirma)", "Accept-Language": "tr-TR,en;q=0.8",
      "Accept-Encoding": "gzip, deflate"}
ADAYLAR = {
    "wgb_tr5y": "https://www.worldgovernmentbonds.com/cds-historical-data/turkey/5-years/",
    "wgb_tablo": "https://www.worldgovernmentbonds.com/sovereign-cds/",
    "tradingeconomics": "https://tradingeconomics.com/turkey/cds",
    "investing_en": "https://www.investing.com/rates-bonds/turkey-cds-5-years-usd",
    "investing_tr": "https://tr.investing.com/rates-bonds/turkey-cds-5-years-usd",
}
ANAHTAR = re.compile(r"(?:CDS|basis points|baz puan|Credit Default|Turkey|T[uü]rkiye)", re.I)


def izinli(url):
    p = urllib.parse.urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{p.scheme}://{p.netloc}/robots.txt", headers=UA), timeout=20) as r:
            ham = r.read()
            if ham[:2] == b"\x1f\x8b":
                import gzip; ham = gzip.decompress(ham)
            rp.parse(ham.decode("utf-8", "replace").splitlines())
    except Exception:
        rp.parse([])
    return rp.can_fetch(UA_AD, url) and rp.can_fetch("*", url)


def getir(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        ham, kod = r.read(3_000_000), (r.headers.get("Content-Encoding") or "").lower()
        durum = r.status
    if "gzip" in kod or ham[:2] == b"\x1f\x8b":
        import gzip; ham = gzip.decompress(ham)
    return durum, ham.decode("utf-8", "replace")


def main():
    os.makedirs("data/kesif/cds_ham", exist_ok=True)
    sonuc = {"uretim_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "adaylar": {},
             "not": "Salt kesif. 'sayi_adaylari' sayfadaki CDS benzeri (50-1500 araligi) sayilar ve cevresidir; "
                    "dogru kaynak elle teyit edilmeden toplayici yazilmaz."}
    for ad, url in ADAYLAR.items():
        k = {"url": url}
        try:
            k["robots_izin"] = izinli(url)
            if not k["robots_izin"]:
                k["durum"] = "ROBOTS_IZIN_YOK"
            else:
                durum, s = getir(url)
                k["http"] = durum
                k["boyut"] = len(s)
                open(f"data/kesif/cds_ham/{ad}.html", "w", encoding="utf-8").write(s[:400_000])
                metin = " ".join(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", s, flags=re.S | re.I).split())
                adaylar = []
                for m in re.finditer(r"(?<![\d.,])(\d{2,4}(?:[.,]\d{1,3})?)(?![\d])", metin):
                    try:
                        v = float(m.group(1).replace(",", "."))
                    except ValueError:
                        continue
                    cevre = metin[max(0, m.start() - 80):m.end() + 40]
                    if 50 <= v <= 1500 and ANAHTAR.search(cevre):
                        adaylar.append({"deger": v, "cevre": cevre})
                k["sayi_adaylari"] = adaylar[:15]
                k["placeholder_var"] = "----" in metin
                k["json_uclari"] = sorted(set(re.findall(r"https?://[^\"'\s]+(?:wp-json|ajax|api)[^\"'\s]*", s)))[:10]
                k["durum"] = "DEGER_ADAYI_VAR" if adaylar else "DEGER_YOK"
        except Exception as e:
            k["durum"] = "HATA"; k["hata"] = str(e)[:200]
        sonuc["adaylar"][ad] = k
        print(ad, k.get("durum"), k.get("http"), [a["deger"] for a in k.get("sayi_adaylari", [])][:5])
    json.dump(sonuc, open("data/kesif/cds.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
