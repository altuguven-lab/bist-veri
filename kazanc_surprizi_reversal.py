"""
KAZANC_SURPRIZI_REVERSAL (10.08.2026) - Faz V0
Kurul karari: KCHOL orneginden (05.08 guclu kar surprizi -> fiyat
ANINDA sicradi -> sonraki gunlerde geri cekildi) genellestirilen bir
tarama. geri_donus_adaylari.py'den (YTD+haftalik MOMENTUM bazli)
FARKLI bir MEKANIZMA yakalar: HABER-GUDUMLU asiri tepki + duzeltme.

METODOLOJI:
  1. arastirma_hedef_fiyat.json'daki kayit_tipi=="KAR_RAKAMI" VE
     yon=="YUKARI" (pozitif kar surprizi) kayitlarini bul.
  2. Kayit TARIHINDEN BUGUNE fiyat degisimini hesapla (yfinance).
  3. Eger fiyat kayit SONRASI GERI CEKILMISSE (negatif), "GERI_
     CEKILME_ADAYI" olarak isaretle - KCHOL'deki gibi.
  4. Sembolun SEKTORUNU makro_hassasiyet_haritasi.json'a bakip, o
     sektorun YAPISAL hassasiyet faktorlerini BAGLAM olarak ekle -
     TAHMIN URETMEZ, yalniz "bu sembole hangi haberler ONEMLI
     olabilir" diye REHBERLIK eder.

KIRMIZI CIZGI: bu bir "AL/SAT tavsiyesi" DEGILDIR. "GERI_CEKILME_
ADAYI" etiketi bile KESIN bir hukum degil - KAR SURPRIZI + fiyat
GERI CEKILMESI oruntusune uyan bir ON-FILTREDIR, nihai karar VE
makro baglamin GUNCEL yorumu insana aittir.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime
import yfinance as yf

SEKTOR_HARITASI = {
    "AKBNK": "Bankacilik", "YKBNK": "Bankacilik", "GARAN": "Bankacilik",
    "ISCTR": "Bankacilik", "HALKB": "Bankacilik", "VAKBN": "Bankacilik",
    "KCHOL": "Holding", "SAHOL": "Holding", "ALARK": "Holding",
    "THYAO": "Havacilik", "PGSUS": "Havacilik", "TAVHL": "Havacilik-Altyapi",
    "EREGL": "Demir-Celik", "SISE": "Sanayi-Cam",
    "ASELS": "Savunma", "ASTOR": "Enerji-Ekipman", "ENJSA": "Enerji-Elektrik",
    "MGROS": "Perakende", "BIMAS": "Perakende",
    "TUPRS": "Petrokimya", "PETKM": "Petrokimya",
    "TOASO": "Otomotiv", "FROTO": "Otomotiv", "OTKAR": "Otomotiv",
    "ENKAI": "Insaat", "TTKOM": "Telekom",
    "AEFES": "Gida-Icecek", "ULKER": "Gida-Icecek",
    "EKGYO": "GYO", "TRMET": "Madencilik",
}


def _oku(yol, varsayilan=None):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return varsayilan if varsayilan is not None else {}


def main():
    arastirma = _oku("data/arastirma_hedef_fiyat.json", {"kayitlar": []})
    makro_harita = _oku("data/makro_hassasiyet_haritasi.json",
                          {"hassasiyet_haritasi": {}})

    kar_surprizleri = [k for k in arastirma["kayitlar"]
                        if k.get("kayit_tipi") == "KAR_RAKAMI" and k["yon"] == "YUKARI"]
    print(f"{len(kar_surprizleri)} pozitif kar surprizi kaydi bulundu")

    sonuclar = []
    for kayit in kar_surprizleri:
        sembol = kayit["sembol"]
        try:
            df = yf.Ticker(f"{sembol}.IS").history(period="3mo", interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}")
            continue
        if df.empty:
            continue

        kayit_tarih = datetime.date.fromisoformat(kayit["tarih"])
        seri = [(idx.date(), float(v)) for idx, v in df["Close"].items()]
        sonraki_fiyatlar = [(t, c) for t, c in seri if t >= kayit_tarih]
        if not sonraki_fiyatlar:
            continue
        kayit_gunu_fiyat = sonraki_fiyatlar[0][1]
        son_fiyat = seri[-1][1]
        son_tarih = seri[-1][0]

        zirve_fiyat = max(c for _, c in sonraki_fiyatlar)
        zirveden_geri_cekilme_pct = round((son_fiyat / zirve_fiyat - 1) * 100, 2)
        kayit_gununden_bugune_pct = round((son_fiyat / kayit_gunu_fiyat - 1) * 100, 2)

        sektor = SEKTOR_HARITASI.get(sembol, "DIGER")
        hassasiyet = makro_harita.get("hassasiyet_haritasi", {}).get(sektor, [])

        kayit_sonuc = {
            "sembol": sembol, "sektor": sektor,
            "kar_surprizi_tarihi": kayit["tarih"], "kar_surprizi_notu": kayit["kaynak_not"],
            "kayit_gunu_fiyat": round(kayit_gunu_fiyat, 2),
            "zirve_fiyat": round(zirve_fiyat, 2), "son_fiyat": round(son_fiyat, 2),
            "son_tarih": str(son_tarih),
            "zirveden_geri_cekilme_pct": zirveden_geri_cekilme_pct,
            "kayit_gununden_bugune_pct": kayit_gununden_bugune_pct,
            "makro_hassasiyet_faktorleri": hassasiyet,
        }
        if zirveden_geri_cekilme_pct <= -3.0:
            kayit_sonuc["etiket"] = "GERI_CEKILME_ADAYI"
        else:
            kayit_sonuc["etiket"] = "GERI_CEKILME_YOK_VEYA_KUCUK"
        sonuclar.append(kayit_sonuc)

    sonuclar.sort(key=lambda s: s["zirveden_geri_cekilme_pct"])

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Bu bir AL/SAT tavsiyesi DEGILDIR. 'GERI_CEKILME_ADAYI' "
                "etiketi, kar surprizi SONRASI fiyatin zirveden en az "
                "%3 geri cekildigi durumlari isaretler - KCHOL orneginden "
                "genellestirilen bir ON-FILTREDIR. makro_hassasiyet_"
                "faktorleri TAHMIN URETMEZ, yalniz 'bu sembole hangi "
                "haberler onemli olabilir' diye YAPISAL REHBERLIK eder."),
        "toplam_kar_surprizi": len(kar_surprizleri),
        "sonuclar": sonuclar,
    }
    atomik_json_yaz("data/kazanc_surprizi_reversal.json", rapor)
    print(f"Yazildi: data/kazanc_surprizi_reversal.json")
    for s in sonuclar:
        print(f"  {s['sembol']} ({s['sektor']}): zirveden %{s['zirveden_geri_cekilme_pct']} -> {s['etiket']}")


if __name__ == "__main__":
    main()
