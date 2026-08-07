"""
YABANCI_TAKAS_TAKIP (07.08.2026) - Faz V0
"Buyuk oyuncularin ayak izini" gorme sistemi - MKK/BIST kaynakli,
sembol-bazinda yabanci yatirimci takas payi degisimini yapilandirilmis
kaydeder. arastirma_hedef_fiyat.py ile AYNI disiplin (kayit_ekle
deseni, tekrar onleme/upsert, atomik yazma).

Veri KAYNAGI: otomatik degil - web_search ile (paraajansi.com.tr,
Is Yatirim gunluk yabanci oranlari raporu gibi kaynaklardan) ELLE,
YAPILANDIRILMIS olarak eklenir. MKK'nin kendisi API sunmuyor, bu
kaynaklar MKK verisini derleyip HABER olarak yayinliyor.

07.08 ILK DOGRULAMA: portfoyumuzdeki 4 sembolun (AKBNK/YKBNK azalis,
KCHOL/TUPRS artis) yabanci payi degisimi, BAGIMSIZ olarak
arastirma_hedef_fiyat.json'daki analist hedef-fiyat bulgularimizla
TAM ORTUSUYOR - iki bagimsiz kaynagin ayni yone isaret etmesi,
GUCLU bir tutarlilik isareti.

KIRMIZI CIZGI: SALT VERI KAYDI, hicbir otomatik islem/sinyal uretmez.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime

DOSYA = "data/yabanci_takas_takip.json"


def _oku():
    try:
        with open(DOSYA, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"kayitlar": []}


def kayit_ekle(sembol, tarih, periyot, puan_degisimi, son_yabanci_payi_pct, kaynak_not):
    """periyot: 'gunluk'/'haftalik'/'aylik'. puan_degisimi: yuzde puan
    (orn. -10.83, +4.51). Tekrar onleme: (sembol, tarih, periyot)."""
    veri = _oku()
    for k in veri["kayitlar"]:
        if (k["sembol"], k["tarih"], k["periyot"]) == (sembol, tarih, periyot):
            return k
    yon = "ARTIS" if puan_degisimi > 0 else ("AZALIS" if puan_degisimi < 0 else "SABIT")
    kayit = {
        "sembol": sembol, "tarih": tarih, "periyot": periyot,
        "puan_degisimi": puan_degisimi, "yon": yon,
        "son_yabanci_payi_pct": son_yabanci_payi_pct, "kaynak_not": kaynak_not,
        "eklenme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    veri["kayitlar"].append(kayit)
    atomik_json_yaz(DOSYA, veri)
    return kayit


if __name__ == "__main__":
    # 07.08 arastirmasindan (paraajansi.com.tr) dogrulanan, portfoyumuzdeki
    # semboller icin gercek kayitlar
    kayit_ekle("YKBNK", "2026-07-31", "aylik", -10.83, 24.37,
               "Temmuz ayinda EN COK azalan sirket - AKBNK/analist "
               "hedef-fiyat asagi revizyonuyla (29.07/31.07 kayitlari) "
               "TUTARLI - iki bagimsiz kaynak ayni yonde.")
    kayit_ekle("AKBNK", "2026-07-24", "gunluk", -1.00, 49.15,
               "Gun icinde EN COK azalan hisse - analist hedef-fiyat "
               "asagi revizyonuyla TUTARLI.")
    kayit_ekle("AKBNK", "2026-07-20", "haftalik", -1.23, None,
               "Haftalik bazda azalis - ayni yonde ikinci teyit.")
    kayit_ekle("KCHOL", "2026-07-31", "aylik", 4.51, None,
               "Temmuz ayinda artan - KCHOL'un 19.7mlr TL net kar "
               "surprizi (piyasa beklentisinin cok ustunde) ile "
               "TUTARLI.")
    kayit_ekle("KCHOL", "2026-07-20", "haftalik", 1.02, None,
               "Haftalik bazda artis - ayni yonde ikinci teyit.")
    kayit_ekle("TUPRS", "2026-07-31", "aylik", 4.59, None,
               "Temmuz ayinda artan - TUPRS'in rafineri marji rehberi "
               "ikiye katlanmasi (Ziraat Yatirim, 06.08) ile TUTARLI.")
    kayit_ekle("TUPRS", "2026-07-20", "haftalik", 1.57, None,
               "Haftalik bazda artis - ayni yonde ikinci teyit.")
    kayit_ekle("ASTOR", "2026-07-24", "gunluk", -0.84, None,
               "Gun icinde hafif azalis - ASTOR'un genel guclu "
               "anlatisina ragmen KISA VADELI, tek-gunluk bir "
               "dalgalanma olabilir, TREND DEGIL.")
    print("Kayitlar eklendi.")
