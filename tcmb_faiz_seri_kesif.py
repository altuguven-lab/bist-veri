"""
TCMB_FAIZ_SERI_KESIF (11.08.2026) - Faz V0
Politika faizi (1 hafta repo) icin KESIN, DOGRULANMIS bir EVDS seri
kodu internet aramasinda bulunamadi - adaylar (orn. TP.APIFON4)
GERCEKTE farkli bir seyi (agirlikli fonlama maliyeti) ifade ediyor
olabilir. TAHMIN etmek yerine, EVDS'nin KENDI "categories" ve
"serieList" servislerini kullanarak "Faiz Oranlari" konu basligi
altindaki GERCEK veri gruplarini/serileri KESFEDER.

KIRMIZI CIZGI: SALT KESIF/ARASTIRMA, hicbir veri KAYDETMEZ, hicbir
sinyal URETMEZ - yalniz DOGRU seri kodunu BULMAMIZA yardimci olur.
"""
import json, os, sys, time
import urllib.request

EVDS_TEMEL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/{yol}"


def turkce_kucuk(metin):
    """11.08 DUZELTME: Python'un standart .lower()'i Turkce buyuk 'I'
    (noktali - U+0130) harfini 'i' yerine 'i' + GORUNMEZ nokta
    isaretine (U+0307) cevirir - bu yuzden "FAIZ".lower() "faiz" ile
    ESLESMIYORDU (aralarinda GORUNMEZ bir karakter kaliyordu). Bu,
    Turkce harfleri ELLE degistirerek dogru kucuk harfe cevirir."""
    return metin.replace("İ", "i").replace("I", "ı").lower()


def evds_istek(yol, anahtar, deneme_sayisi=3):
    url = EVDS_TEMEL.format(yol=yol)
    istek = urllib.request.Request(url, headers={
        "User-Agent": "bist-veri-arastirma-botu",
        "Accept": "application/json",
        "key": anahtar,
    })
    # 11.08 EKI: GECICI SSL/aglama zaman asimlarini tolere etmek icin
    # basit yeniden-deneme (bugunku benzer git-push deseniyle AYNI ruh).
    son_hata = None
    for deneme in range(1, deneme_sayisi + 1):
        try:
            with urllib.request.urlopen(istek, timeout=30) as yanit:
                ham = yanit.read().decode("utf-8", errors="replace")
            if not ham.strip():
                raise ValueError(f"BOS yanit (yol: {yol})")
            return json.loads(ham)
        except Exception as e:
            son_hata = e
            print(f"UYARI: istek basarisiz (deneme {deneme}/{deneme_sayisi}) -> {e}", file=sys.stderr)
            if deneme < deneme_sayisi:
                time.sleep(3 * deneme)
    raise son_hata


def main():
    anahtar = os.environ.get("TCMB_EVDS_API_KEY")
    if not anahtar:
        print("HATA: TCMB_EVDS_API_KEY ortam degiskeni bulunamadi", file=sys.stderr)
        sys.exit(1)

    print("=== ADIM 1: Tum konu basliklarini listele (Faiz ile ilgili olani bul) ===")
    try:
        kategoriler = evds_istek("categories/type=json", anahtar)
    except Exception as e:
        print(f"HATA: kategoriler cekilemedi -> {e}", file=sys.stderr)
        sys.exit(1)

    kategori_listesi = kategoriler if isinstance(kategoriler, list) else kategoriler.get("items", kategoriler)
    faiz_kategorileri = [k for k in kategori_listesi
                          if "faiz" in turkce_kucuk(str(k.get("TOPIC_TITLE_TR", "")))]
    print(f"Toplam {len(kategori_listesi)} konu basligi bulundu, "
          f"{len(faiz_kategorileri)} tanesi 'faiz' iceriyor:")
    for k in faiz_kategorileri:
        print(f"  ID={k.get('CATEGORY_ID')}: {k.get('TOPIC_TITLE_TR')}")

    if not faiz_kategorileri:
        print("UYARI: 'faiz' iceren konu basligi bulunamadi - kategori "
              "adlandirmasi farkli olabilir, TUM listeyi inceleyin:")
        for k in kategori_listesi[:30]:
            print(f"  ID={k.get('CATEGORY_ID')}: {k.get('TOPIC_TITLE_TR')}")
        return

    print("\n=== ADIM 2: Faiz kategorisi/kategorileri altindaki veri gruplarini listele ===")
    for kat in faiz_kategorileri:
        kat_id = kat.get("CATEGORY_ID")
        print(f"\n--- Konu basligi ID={kat_id} ({kat.get('TOPIC_TITLE_TR')}) altindaki veri gruplari ---")
        try:
            gruplar = evds_istek(f"datagroups/mode=0&type=json", anahtar)
        except Exception as e:
            print(f"  HATA: veri gruplari cekilemedi -> {e}", file=sys.stderr)
            continue
        grup_listesi = gruplar if isinstance(gruplar, list) else gruplar.get("items", gruplar)
        ilgili = [g for g in grup_listesi
                  if any(kelime in turkce_kucuk(str(g.get("DATAGROUP_NAME", "")))
                         for kelime in ["repo", "politika", "gecelik", "fonlama"])]
        for g in ilgili[:20]:
            print(f"  KOD={g.get('DATAGROUP_CODE')}: {g.get('DATAGROUP_NAME')}")
        break

    print("\n=== ADIM 3: 'Merkez Bankalari Politika Faiz Orani' grubu icindeki "
          "GERCEK seri kodlarini listele (bie_bispolfaiz) ===")
    try:
        seriler = evds_istek("serieList/type=json&code=bie_bispolfaiz", anahtar)
    except Exception as e:
        print(f"HATA: seri listesi cekilemedi -> {e}", file=sys.stderr)
        return
    seri_listesi = seriler if isinstance(seriler, list) else seriler.get("items", seriler)
    for s in seri_listesi[:20]:
        print(f"  SERI_KODU={s.get('SERIE_CODE')}: {s.get('SERIE_NAME')}")


if __name__ == "__main__":
    main()
