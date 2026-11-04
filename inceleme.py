"""
Inceleme listesi yardimcisi (04.11.2026). Yeni test betikleri bunu kullanir:
    from inceleme import inceleme_listesi
    il = inceleme_listesi()            # {"KRDMD": "2026-11-04", ...}
    ana = [o for o in olaylar if o["sembol"] not in il]
Kural (config/inceleme_listesi.txt): ana sonuc listedeki hisseler HARIC verilir, "dahil" sonuc ayrica raporlanir.
Veri toplama betikleri bu listeyi KULLANMAZ (arsiv surer).
"""
import os

YOL = "config/inceleme_listesi.txt"


def inceleme_listesi(yol=YOL):
    out = {}
    if not os.path.exists(yol):
        return out
    for s in open(yol, encoding="utf-8"):
        kod = s.split("#")[0].strip().upper()
        if not kod:
            continue
        tarih = s.split("|")[-1].strip() if "|" in s else None
        out[kod] = tarih
    return out


if __name__ == "__main__":
    il = inceleme_listesi()
    print(len(il), "hisse:", ", ".join(sorted(il)))
