"""
FAZ V0 - VIOP VERI KESFI, TUR 2 (hedefli)
Tur 1 bulgusu: EN veri sayfasi erisilir; datafilepaths_viop.zip kesfedildi.
Bu tur: zip indirilip icerigi cikarilir + bulten sayfalari cekilir.
"""

import json
import os
import io
import sys
import zipfile
import datetime
import urllib.request

TABAN = "https://www.borsaistanbul.com"
ADAYLAR = [
    ("bulten_ve_piyasa", TABAN + "/en/data/derivatives-market-data/bulletin-and-market-data"),
    ("gunluk_bulten", TABAN + "/en/data/daily-bulletin"),
]
ZIP_URL = TABAN + "/files/datafilepaths_viop.zip"

UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36")}


def cek(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.status, r.headers.get("Content-Type", "?"), r.read()


def main():
    os.makedirs("data/kesif", exist_ok=True)
    ozet = {"kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "tur": 2, "sonuclar": []}

    # 1) datafilepaths_viop.zip - asil hedef
    kayit = {"ad": "datafilepaths_zip", "url": ZIP_URL}
    try:
        durum, ctype, govde = cek(ZIP_URL)
        kayit.update({"durum": durum, "icerik_tipi": ctype, "boyut": len(govde)})
        zf = zipfile.ZipFile(io.BytesIO(govde))
        kayit["zip_icerigi"] = zf.namelist()
        # Kucuk metin uyelerini oldugu gibi kaydet (yol kaliplari burada olmali)
        for ad in zf.namelist()[:10]:
            veri = zf.read(ad)
            if len(veri) < 200_000:
                guvenli = ad.replace("/", "_")
                with open(f"data/kesif/zip_{guvenli}", "wb") as f:
                    f.write(veri)
        kayit["cikarilan"] = True
    except Exception as e:
        kayit["hata"] = str(e)
        print(f"UYARI: zip -> {e}", file=sys.stderr)
    ozet["sonuclar"].append(kayit)

    # 2) Bulten sayfalari (ham ornek olarak)
    for ad, url in ADAYLAR:
        kayit = {"ad": ad, "url": url}
        try:
            durum, ctype, govde = cek(url)
            metin = govde.decode("utf-8", errors="replace")
            kayit.update({"durum": durum, "boyut": len(govde)})
            with open(f"data/kesif/{ad}.html", "w", encoding="utf-8") as f:
                f.write(metin[:80_000])
        except Exception as e:
            kayit["hata"] = str(e)
            print(f"UYARI: {ad} -> {e}", file=sys.stderr)
        ozet["sonuclar"].append(kayit)

    with open("data/kesif/kesif_ozet.json", "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=2)
    print("Tur 2 tamam.")


if __name__ == "__main__":
    main()
