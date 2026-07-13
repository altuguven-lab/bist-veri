"""
FAZ V0 - VIOP VERI KESFI (tek seferlik)
BIST'in VIOP veri sayfalarini ceker, ham ornekleri data/kesif/ altina
kaydeder ve veri baglantilarini (bulten/csv/xlsx/zip) envanterler.
Hicbir mevcut dosyaya dokunmaz. Amac: fetch_viop.py'nin GERCEK format
uzerine yazilabilmesi (varsayimsal format uzerine kod yazilmaz).
"""

import json
import os
import re
import sys
import datetime
import urllib.request

ADAYLAR = [
    ("viop_ana", "https://borsaistanbul.com/tr/sayfa/1021"),
    ("viop_sayfa48", "https://www.borsaistanbul.com/tr/sayfa/48/vadeli-islem-ve-opsiyon-piyasasi"),
    ("veri_turev_en", "https://www.borsaistanbul.com/en/data/derivatives-market-data"),
    ("veri_turev_tr", "https://www.borsaistanbul.com/tr/veriler/vadeli-islem-ve-opsiyon-piyasasi-verileri"),
    ("bultenler", "https://www.borsaistanbul.com/tr/sayfa/3622/gunluk-bultenler"),
    ("datastore", "https://datastore.borsaistanbul.com/"),
]

ILGI_KALIPLARI = re.compile(
    r'href=["\']([^"\']*(?:bulten|bulletin|viop|vadeli|derivative|acik|pozisyon|'
    r'open[-_]?interest|\.csv|\.xlsx|\.zip)[^"\']*)["\']', re.I)

UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")}


def cek(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.headers.get("Content-Type", "?"), r.read(200_000)


def main():
    os.makedirs("data/kesif", exist_ok=True)
    ozet = {"kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "sayfalar": []}

    for ad, url in ADAYLAR:
        kayit = {"ad": ad, "url": url}
        try:
            durum, ctype, govde = cek(url)
            kayit.update({"durum": durum, "icerik_tipi": ctype, "boyut": len(govde)})
            metin = govde.decode("utf-8", errors="replace")
            # Ham ornek (ilk 50KB) - format incelemesi icin
            with open(f"data/kesif/{ad}.html", "w", encoding="utf-8") as f:
                f.write(metin[:50_000])
            # Ilgili baglanti envanteri
            linkler = sorted(set(ILGI_KALIPLARI.findall(metin)))[:60]
            kayit["ilgili_baglanti_sayisi"] = len(linkler)
            kayit["ilgili_baglantilar"] = linkler
        except Exception as e:
            kayit["hata"] = str(e)
            print(f"UYARI: {ad} -> {e}", file=sys.stderr)
        ozet["sayfalar"].append(kayit)

    with open("data/kesif/kesif_ozet.json", "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=2)
    basarili = sum(1 for s in ozet["sayfalar"] if "durum" in s)
    print(f"Kesif tamam: {basarili}/{len(ADAYLAR)} sayfa cekildi.")


if __name__ == "__main__":
    main()
