"""
INBOX BIRLESTIRME (17.08.2026) - ALTYAPI, salt veri kurtarma

SORUN (17.08 denetimi): GUNLUK_OZET kayitlarinin gunde ~6-8'i
tv_alerts_latest.json'a ULASMIYOR (12-14.08 kapsama 22-24/30).
Kok neden BULUNDU: kayiplar KAYBOLMUYOR - Pipedream ana dosyaya
yazamadigi (sha yarisi) durumda tekil dosya olarak data/inbox/
altina dusuyor. Orada oturuyorlar; hicbir sey onlari ana dosyaya
geri tasimiyor.

Sonuc: hafta_denetim.py, sinyal_arsiv_gunluk.py ve brifing hep
EKSIK veriyle calisiyor - M4 rejim flip sayimi, kapsama ve
sinyal-arsiv besleme hepsi bu delikten etkileniyor.

BU BETIK: data/inbox/*.json kayitlarini tv_alerts_latest.json'un
sinyal_gecmisi listesine EKLER. Tekrar onleme anahtari:
(zaman_utc, sembol, sinyal). Idempotenttir - iki kez kosmak
hicbir sey degistirmez, bu yuzden inbox dosyalari SILINMEZ
(silme ayri ve geri donusu olmayan bir karardir).

KIRMIZI CIZGI: Pine'a dokunmaz, sinyal URETMEZ, mevcut kaydi
DEGISTIRMEZ - yalnizca eksik olani ekler.

CALISMA SIRASI: sinyal_arsiv_gunluk.py ve hafta_denetim.py'den
ONCE kosmalidir (ikisi de tv_alerts_latest.json'u okur).
"""
from json_atomik_yaz import atomik_json_yaz
import json
import glob
import os

ANA_YOL = "data/tv_alerts_latest.json"
INBOX_DESEN = "data/inbox/*.json"
# Kurtarma sonrasi ust sinir. Pipedream kendi tarafinda 100 tutuyor;
# burada biraz pay birakiyoruz ki kurtarilan kayitlar ayni kosuda
# yeniden dusmesin. Arsivleme sinyal_arsiv_gunluk.py'nin isi.
AZAMI_KAYIT = 200

ZORUNLU_ALANLAR = ("zaman_utc", "sembol", "sinyal")


def _anahtar(k):
    return (k.get("zaman_utc"), k.get("sembol"), k.get("sinyal"))


def main():
    with open(ANA_YOL, encoding="utf-8") as f:
        ana = json.load(f)

    gecmis = ana.get("sinyal_gecmisi", [])
    mevcut = {_anahtar(k) for k in gecmis}

    dosyalar = sorted(glob.glob(INBOX_DESEN))
    eklenen, atlanan, bozuk = [], 0, 0

    for yol in dosyalar:
        try:
            with open(yol, encoding="utf-8") as f:
                kayit = json.load(f)
        except Exception as e:
            print(f"BOZUK: {os.path.basename(yol)} -> {e}")
            bozuk += 1
            continue

        if not all(kayit.get(a) for a in ZORUNLU_ALANLAR):
            print(f"EKSIK ALAN: {os.path.basename(yol)}")
            bozuk += 1
            continue

        if _anahtar(kayit) in mevcut:
            atlanan += 1
            continue

        gecmis.append(kayit)
        mevcut.add(_anahtar(kayit))
        eklenen.append(kayit)

    if not eklenen:
        print(f"Yeni kayit yok ({len(dosyalar)} inbox dosyasi, "
              f"{atlanan} zaten mevcut, {bozuk} bozuk) - dosya yazilmadi.")
        return

    # Dosya duzeni: yeniden eskiye (mevcut konvansiyon)
    gecmis.sort(key=lambda k: k["zaman_utc"], reverse=True)
    if len(gecmis) > AZAMI_KAYIT:
        gecmis = gecmis[:AZAMI_KAYIT]

    ana["sinyal_gecmisi"] = gecmis
    ana["sinyal_sayisi"] = len(gecmis)
    ana["inbox_kurtarma"] = {
        "son_kosu_kurtarilan": len(eklenen),
        "inbox_dosya_sayisi": len(dosyalar),
    }

    atomik_json_yaz(ANA_YOL, ana)

    print(f"KURTARILAN: {len(eklenen)} kayit "
          f"({atlanan} zaten mevcut, {bozuk} bozuk)")
    for k in sorted(eklenen, key=lambda x: x["zaman_utc"]):
        print(f"  + {k['zaman_utc']}  {k['sembol']:7} {k['sinyal']}")
    print(f"Toplam kayit: {len(gecmis)}")


if __name__ == "__main__":
    main()
