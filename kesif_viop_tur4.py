"""
FAZ V0 - VIOP VERI KESFI, TUR 4
Tur 3 bulgusu: dosya yolu haritasi cikti - /viopdata/ altinda
viop_YYYYAAGG.csv (gunluk bulten), viopgs_YYYYAAGG.csv (gunsonu
pozisyon), viopms_YYYYAAGG.csv (mevcut sozlesmeler).
Bu tur: son birkac is gunu icin bu ucunu GERCEKTEN indirir, kolon
haritasini + ornek satirlari cikarir. KESIF_VIOP.md'nin kabul kriteri
(alan haritasi + ornek ham kayit + likit liste) icin taban veri budur.
"""
import json
import os
import sys
import datetime
import urllib.request
import io

import pandas as pd

CIKTI = "data/kesif/kesif_viop_tur4.json"
TABAN_URL = "https://www.borsaistanbul.com/viopdata/"
DOSYA_KALIPLARI = {
    "gunluk_bulten": "viop_{yyyymmdd}.csv",
    "gunsonu_pozisyon": "viopgs_{yyyymmdd}.csv",
    "mevcut_sozlesmeler": "viopms_{yyyymmdd}.csv",
}
# BIST bulten dosyalari genelde Windows-1254 (Turkce) kodlamali, noktali
# virgul ayracli olur - ikisini de deneriz.
KODLAMALAR = ["windows-1254", "utf-8", "iso-8859-9"]
AYRACLAR = [";", ","]

BIZIM_SEMBOLLER = ["AKBNK", "YKBNK", "KCHOL", "TAVHL", "ASTOR"]


def indir(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (bist-veri kesif)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def csv_dene(ham_bayt):
    """Kodlama + ayrac kombinasyonlarini dener, ilk makul sonucu dondurur."""
    for kod in KODLAMALAR:
        for ayrac in AYRACLAR:
            try:
                df = pd.read_csv(io.BytesIO(ham_bayt), encoding=kod, sep=ayrac,
                                  on_bad_lines="skip", engine="python", nrows=500)
                if df.shape[1] >= 2:  # tek kolona sikismis = yanlis ayrac
                    return df, kod, ayrac
            except Exception:
                continue
    return None, None, None


def gun_dene(anahtar, kalip, gun):
    yyyymmdd = gun.strftime("%Y%m%d")
    url = TABAN_URL + kalip.format(yyyymmdd=yyyymmdd)
    try:
        ham = indir(url)
    except Exception as e:
        return {"url": url, "hata": str(e)}

    if len(ham) < 200:  # bos/404 sayfasi genelde kisa doner
        return {"url": url, "hata": f"supheli kucuk yanit ({len(ham)} bayt)"}

    df, kod, ayrac = csv_dene(ham)
    if df is None:
        return {"url": url, "hata": "CSV ayristirilamadi (kodlama/ayrac denemeleri basarisiz)",
                "ham_ilk_200": ham[:200].decode("latin-1", errors="replace")}

    kolonlar = [str(c) for c in df.columns]
    sonuc = {
        "url": url, "kodlama": kod, "ayrac": ayrac,
        "kolonlar": kolonlar, "satir_sayisi": int(len(df)),
        "ornek_satirlar": df.head(15).astype(str).values.tolist(),
    }
    # bizim sembollerimizi iceren satirlari ayrica isaretle (herhangi bir
    # kolonda sembol adi geciyorsa)
    metin_df = df.astype(str)
    eslesen = {}
    for sem in BIZIM_SEMBOLLER:
        maske = metin_df.apply(lambda col: col.str.contains(sem, case=False, na=False)).any(axis=1)
        adet = int(maske.sum())
        if adet:
            eslesen[sem] = {"adet": adet, "ornek": metin_df[maske].head(3).values.tolist()}
    sonuc["bizim_sembol_eslesmeleri"] = eslesen
    return sonuc


def main():
    bugun = datetime.date.today()
    sonuc = {"kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "tur": 4, "denenen_gunler": []}

    for anahtar, kalip in DOSYA_KALIPLARI.items():
        sonuc[anahtar] = None
        # bugunden geriye dogru son 5 gun dene (hafta sonu/henuz
        # yayinlanmamis olabilir)
        for geri in range(0, 6):
            gun = bugun - datetime.timedelta(days=geri)
            if gun.weekday() >= 5:  # hafta sonu atla
                continue
            deneme = gun_dene(anahtar, kalip, gun)
            sonuc["denenen_gunler"].append({"anahtar": anahtar, "gun": str(gun),
                                             "basarili": "hata" not in deneme})
            if "hata" not in deneme:
                deneme["kullanilan_gun"] = str(gun)
                sonuc[anahtar] = deneme
                print(f"BASARILI: {anahtar} -> {gun} ({deneme['satir_sayisi']} satir)")
                break
            else:
                print(f"denendi, basarisiz: {anahtar} {gun} -> {deneme['hata']}", file=sys.stderr)

    os.makedirs("data/kesif", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"Yazildi: {CIKTI}")


if __name__ == "__main__":
    main()
