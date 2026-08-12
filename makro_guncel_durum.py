"""
MAKRO_GUNCEL_DURUM (11.08.2026) - Faz V0
makro_hassasiyet_haritasi.json'daki "USD_TRY_KURU" gibi faktorleri
ARTIK SADECE ISIM olarak DEGIL, tcmb_evds_veri.json'dan gelen GERCEK
GUNCEL deger ve SON 30 GUNLUK % degisimle BIRLESTIRIR. "USD_TRY_KURU"
faktoru TASIYAN HER sektore, bu GUNCEL veri EKLENIR.

KIRMIZI CIZGI: SALT VERI BIRLESTIRME - hicbir TAHMIN/SINYAL uretmez,
yalniz "bu faktorun GUNCEL degeri su" diye GOSTERIR. Yorumlama VE
karar insana aittir (makro_hassasiyet_haritasi.py'nin KENDI ilkesiyle
AYNI disiplin).
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime


def _oku(yol, varsayilan=None):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return varsayilan if varsayilan is not None else {}


def seri_ozet(kayitlar, alan_adi):
    # 12.08 DUZELTME: tcmb_evds_veri.py ARTIK USD/TRY ve politika
    # faizini AYRI ALANLARDA (usd_try_kayitlar/politika_faiz_kayitlar)
    # tutuyor (coklu-seri istegindeki frekans-karisma HATASI DUZELTILDI) -
    # bu fonksiyon artik DOGRUDAN kayit LISTESI alir, "evds_veri" sozlugu
    # DEGIL.
    gecerli = [(k["Tarih"], float(k[alan_adi])) for k in kayitlar
               if k.get(alan_adi) not in (None, "")]
    if not gecerli:
        return None
    guncel_tarih, guncel_deger = gecerli[-1]
    ilk_tarih, ilk_deger = gecerli[0]
    degisim_pct = round((guncel_deger / ilk_deger - 1) * 100, 2) if ilk_deger else None
    return {
        "guncel_deger": guncel_deger, "guncel_tarih": guncel_tarih,
        "donem_basi_deger": ilk_deger, "donem_basi_tarih": ilk_tarih,
        "donem_ici_degisim_pct": degisim_pct,
        "gecerli_gun_sayisi": len(gecerli),
    }


def usd_try_ozet(evds_veri):
    return seri_ozet(evds_veri.get("usd_try_kayitlar", []), "TP_DK_USD_A_YTL")


def politika_faiz_ozet(evds_veri):
    return seri_ozet(evds_veri.get("politika_faiz_kayitlar", []), "TP_BISPOLFAIZ_TUR")


def main():
    harita = _oku("data/makro_hassasiyet_haritasi.json", {"hassasiyet_haritasi": {}})
    evds = _oku("data/tcmb_evds_veri.json", {"kayitlar": []})

    usd_try = usd_try_ozet(evds)
    if usd_try:
        print(f"USD/TRY guncel: {usd_try['guncel_deger']} ({usd_try['guncel_tarih']}), "
              f"donem ici degisim: %{usd_try['donem_ici_degisim_pct']}")
    else:
        print("UYARI: USD/TRY icin gecerli kayit bulunamadi")

    politika_faiz = politika_faiz_ozet(evds)
    if politika_faiz:
        print(f"Politika faizi guncel: %{politika_faiz['guncel_deger']} "
              f"({politika_faiz['guncel_tarih']})")
    else:
        print("UYARI: politika faizi icin gecerli kayit bulunamadi")

    guncellenmis_harita = {}
    etkilenen_sektor_sayisi = 0
    for sektor, faktorler in harita.get("hassasiyet_haritasi", {}).items():
        yeni_faktorler = []
        for faktor_adi, aciklama in faktorler:
            kayit = {"faktor": faktor_adi, "aciklama": aciklama}
            if faktor_adi == "USD_TRY_KURU" and usd_try:
                kayit["guncel_veri"] = usd_try
                etkilenen_sektor_sayisi += 1
            elif faktor_adi == "TCMB_FAIZ_KARARI" and politika_faiz:
                kayit["guncel_veri"] = politika_faiz
                etkilenen_sektor_sayisi += 1
            yeni_faktorler.append(kayit)
        guncellenmis_harita[sektor] = yeni_faktorler

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("makro_hassasiyet_haritasi.json'daki faktorlere, MEVCUT "
                "GERCEK veriyle (su an yalniz USD_TRY_KURU icin TCMB EVDS) "
                "GUNCEL deger eklenmis halidir. Bu bir TAHMIN/SINYAL "
                "DEGILDIR - yalniz 'bu faktorun guncel degeri su' diye "
                "GOSTERIR, yorumlama insana aittir."),
        "usd_try_ozet": usd_try,
        "usd_try_etkilenen_sektor_sayisi": etkilenen_sektor_sayisi,
        "hassasiyet_haritasi_guncel": guncellenmis_harita,
    }
    atomik_json_yaz("data/makro_guncel_durum.json", rapor)
    print(f"\nYazildi: data/makro_guncel_durum.json "
          f"({etkilenen_sektor_sayisi} sektor USD_TRY_KURU/TCMB_FAIZ_KARARI verisiyle zenginlestirildi)")


if __name__ == "__main__":
    main()
