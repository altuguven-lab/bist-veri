"""
FAZ V0 - VIOP VERI KESFI, TUR 3 (son tur)
Tur 2 bulgusu: verilerdosyaisimleri_viop.xls (dosya yolu indeksi) repoda.
Bu tur: XLS satirlari JSON'a dokulur + kayitli bulten HTML'lerinden
veri linkleri suzulur. Cikti = fetch_viop.py'nin insa plani.
"""

import json
import os
import re
import sys
import datetime

import pandas as pd

CIKTI = "data/kesif/kesif_dosya_yollari.json"
XLS = "data/kesif/zip_verilerdosyaisimleri_viop.xls"
HTMLLER = ["data/kesif/bulten_ve_piyasa.html", "data/kesif/gunluk_bulten.html"]

LINK_KALIBI = re.compile(
    r'href=["\']([^"\']*(?:\.zip|\.csv|\.xlsx?|bulten|bulletin)[^"\']*)["\']', re.I)


def main():
    sonuc = {"kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "tur": 3}

    # 1) XLS indeksini oku (eski .xls icin xlrd, yenisi icin openpyxl dener)
    try:
        sayfalar = pd.read_excel(XLS, sheet_name=None)
        sonuc["xls_sayfalari"] = {}
        for ad, df in sayfalar.items():
            df = df.fillna("").astype(str)
            sonuc["xls_sayfalari"][ad] = {
                "kolonlar": list(df.columns.astype(str)),
                "satir_sayisi": int(len(df)),
                "satirlar": df.head(120).values.tolist(),
            }
    except Exception as e:
        sonuc["xls_hata"] = str(e)
        print(f"UYARI: XLS -> {e}", file=sys.stderr)

    # 2) Bulten HTML'lerinden veri linkleri
    sonuc["html_linkleri"] = {}
    for yol in HTMLLER:
        try:
            metin = open(yol, encoding="utf-8", errors="replace").read()
            sonuc["html_linkleri"][os.path.basename(yol)] = sorted(set(LINK_KALIBI.findall(metin)))[:80]
        except Exception as e:
            sonuc["html_linkleri"][os.path.basename(yol)] = [f"HATA: {e}"]

    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print("Tur 3 tamam.")


if __name__ == "__main__":
    main()
