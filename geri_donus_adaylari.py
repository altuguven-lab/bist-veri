"""
GERI_DONUS_ADAYLARI_TARAMASI (10.08.2026) - Faz V0
Kurul karari: "guclu yillik getiri + son donemde sert dusus" oruntusune
uyan sembolleri TARAR, sonra MEVCUT katmanlarimizla (analist gorusu,
yabanci akisi, panel PF) CAPRAZLAR - amac, DUSUSUN yalniz TEKNIK bir
duzeltme mi yoksa TEMEL bir zayiflamayla mi (EREGL/celik ornegindeki
gibi) DESTEKLENDIGINI ayirt etmeye CALISMAK.

METODOLOJI: 
  1. Her sembol icin YTD (yil basindan bugune) VE SON_HAFTA getirisi
     hesaplanir (yfinance gunluk kapanislardan).
  2. ESIK: YTD >= %25 VE son_hafta <= -%5 olan semboller "ADAY" sayilir.
  3. Her adayin, konsolide_degerlendirme.json'daki MEVCUT katmanlari
     (analist_gorusu, yabanci_akisi) okunur.
  4. ETIKET: analist/yabanci-akisi de AYNI yonde (ASAGI/AZALIS) ise
     "TEMEL_DESTEKLI_DUSUS_DIKKAT" (temkinli), degilse (NOTR/YUKARI
     ya da veri yok) "MUHTEMELEN_TEKNIK_DUZELTME" etiketlenir.

KIRMIZI CIZGI: bu bir "AL/SAT tavsiyesi" DEGILDIR - taramanin KENDISI
bir ON-FILTRE, SEKTOR/ORUNTU gozlemi. Nihai karar VE ek arastirma
(analist raporu OKUMA gibi) insana aittir. ETIKETLER dahi KESIN bir
hukum degil, "diger katmanlarla TUTARLI mi" sorusuna bir ilk cevaptir.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime
import yfinance as yf

YTD_ESIK_PCT = 25.0
HAFTALIK_ESIK_PCT = -5.0


def main():
    with open("config/universe.yml", encoding="utf-8") as f:
        import yaml
        evren = yaml.safe_load(f)["symbols"]

    konsolide = {}
    try:
        with open("data/konsolide_degerlendirme.json", encoding="utf-8") as f:
            for s in json.load(f).get("semboller", []):
                konsolide[s["sembol"]] = s
    except Exception:
        pass

    tum_sonuclar = []
    adaylar = []
    for sembol in evren:
        try:
            df = yf.Ticker(f"{sembol}.IS").history(period="1y", interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}")
            continue
        if df.empty or len(df) < 6:
            continue

        son_fiyat = float(df["Close"].iloc[-1])
        yil_basi_fiyat = float(df["Close"].iloc[0])
        bir_hafta_once = float(df["Close"].iloc[-6])
        ytd_pct = round((son_fiyat / yil_basi_fiyat - 1) * 100, 2)
        haftalik_pct = round((son_fiyat / bir_hafta_once - 1) * 100, 2)

        kayit = {"sembol": sembol, "ytd_pct": ytd_pct, "haftalik_pct": haftalik_pct,
                  "son_fiyat": son_fiyat, "son_tarih": str(df.index[-1].date())}
        tum_sonuclar.append(kayit)

        if ytd_pct >= YTD_ESIK_PCT and haftalik_pct <= HAFTALIK_ESIK_PCT:
            k = konsolide.get(sembol, {})
            analist = k.get("analist_gorusu")
            yabanci = k.get("yabanci_akisi")
            analist_yon = analist["yon"] if analist else None
            yabanci_yon = yabanci["yon"] if yabanci else None

            temel_negatif_sayisi = 0
            if analist_yon == "ASAGI": temel_negatif_sayisi += 1
            if yabanci_yon == "AZALIS": temel_negatif_sayisi += 1

            etiket = ("TEMEL_DESTEKLI_DUSUS_DIKKAT" if temel_negatif_sayisi >= 1
                      else "MUHTEMELEN_TEKNIK_DUZELTME")

            aday = dict(kayit)
            aday["analist_gorusu"] = analist_yon
            aday["yabanci_akisi"] = yabanci_yon
            aday["etiket"] = etiket
            adaylar.append(aday)

    adaylar.sort(key=lambda a: a["haftalik_pct"])

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Bu bir AL/SAT tavsiyesi DEGILDIR - 'guclu YTD + sert "
                "haftalik dusus' oruntusune uyan sembolleri bulan bir "
                "ON-FILTREDIR. ETIKETLER (TEMEL_DESTEKLI_DUSUS_DIKKAT / "
                "MUHTEMELEN_TEKNIK_DUZELTME) KESIN bir hukum degil - "
                "mevcut analist/yabanci-akisi katmanlariyla TUTARLILIK "
                "kontrolüdür. Nihai karar VE ek arastirma insana aittir."),
        "esikler": {"ytd_esik_pct": YTD_ESIK_PCT, "haftalik_esik_pct": HAFTALIK_ESIK_PCT},
        "toplam_sembol": len(tum_sonuclar),
        "aday_sayisi": len(adaylar),
        "adaylar": adaylar,
        "tum_semboller_ytd_haftalik": tum_sonuclar,
    }
    atomik_json_yaz("data/geri_donus_adaylari.json", rapor)
    print(f"Yazildi: data/geri_donus_adaylari.json ({len(adaylar)} aday / {len(tum_sonuclar)} sembol)")
    for a in adaylar:
        print(f"  {a['sembol']}: YTD %{a['ytd_pct']}, hafta %{a['haftalik_pct']} -> {a['etiket']}")


if __name__ == "__main__":
    main()
