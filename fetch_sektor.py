"""
FETCH_SEKTOR.PY (04.08.2026, ALTYAPI)
Kesif dogrulamasi: BIST sektor endeksleri yfinance'te "{KOD}.IS" formatiyla
calisiyor (XBANK.IS, XHOLD.IS, XULAS.IS, XUSIN.IS, XU100.IS hepsi basarili).
fetch_kuresel.py'deki "kapanmis_hesap" ile AYNI mantik: dunku kapanis vs
onceki gun kapanisi - cunku sabah brifing icin "sektorler DUN nasil
kapandi" sorusu, henuz olusmamis "bugun" verisinden daha degerli.

Portfoyumuzun kapsadigi sektorler:
  XBANK  - Bankacilik   (AKBNK, YKBNK)
  XHOLD  - Holding      (KCHOL)
  XULAS  - Ulastirma    (TAVHL)
  XUSIN  - Sinai/Sanayi (ASTOR'a en yakin)
  XILTM  - Iletisim     (dogrudan pozisyonumuz yok, genel piyasa baglami)
  XU100  - Genel referans
"""
import json, datetime, math, os, sys
import yfinance as yf

ENDEKSLER = [
    ("Bankacilik", "XBANK.IS", "AKBNK, YKBNK"),
    ("Holding",    "XHOLD.IS", "KCHOL"),
    ("Ulastirma",  "XULAS.IS", "TAVHL"),
    ("Sinai",      "XUSIN.IS", "ASTOR (en yakin)"),
    ("Iletisim",   "XILTM.IS", "pozisyon yok - genel baglam"),
    ("XU100",      "XU100.IS", "genel referans"),
]
DOSYA = "data/sektor_gosterge.json"


def kapanmis_hesap(kod):
    """fetch_kuresel.py ile ayni NaN-guvenli desen: onceki iki gunluk
    kapanisi kiyaslar."""
    df = yf.Ticker(kod).history(period="5d")
    kapanislar = [float(c) for c in df["Close"] if not math.isnan(float(c))]
    if len(kapanislar) < 2:
        return None, None, "yetersiz veri (NaN bar/tatil)"
    son, onceki = kapanislar[-1], kapanislar[-2]
    return round((son / onceki - 1) * 100, 2), round(son, 2), None


def main():
    sonuc = {
        "guncelleme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "endeksler": [],
    }
    for isim, kod, ilgili in ENDEKSLER:
        try:
            degisim, kapanis, hata = kapanmis_hesap(kod)
            kayit = {"isim": isim, "kod": kod, "ilgili_pozisyon": ilgili}
            if hata:
                kayit["hata"] = hata
            else:
                kayit["degisim_yuzde"] = degisim
                kayit["kapanis"] = kapanis
            sonuc["endeksler"].append(kayit)
            print(f"{isim} ({kod}): {'basarisiz - ' + hata if hata else f'%{degisim}'}")
        except Exception as e:
            sonuc["endeksler"].append({"isim": isim, "kod": kod, "ilgili_pozisyon": ilgili,
                                        "hata": str(e)})
            print(f"UYARI: {isim} ({kod}) -> {e}", file=sys.stderr)

    gecerli = [e["degisim_yuzde"] for e in sonuc["endeksler"]
               if "degisim_yuzde" in e and e["isim"] != "XU100"]
    if gecerli:
        sonuc["portfoy_sektorleri_ortalama_yuzde"] = round(sum(gecerli) / len(gecerli), 2)

    os.makedirs("data", exist_ok=True)
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"Yazildi: {DOSYA}")


if __name__ == "__main__":
    main()
