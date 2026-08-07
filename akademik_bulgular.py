"""
AKADEMIK_BULGULAR (07.08.2026) - Faz V0
BIST'e ozel algoritmik ticaret/piyasa mikro-yapisi/davranissal finans
literaturunu YAPILANDIRILMIS olarak kaydeder - arastirma_hedef_fiyat.py
ile AYNI disiplin (kayit_ekle deseni, tekrar onleme, atomik yazma).

Veri KAYNAGI: otomatik degil - arastirma sirasinda (web_search ile)
ELLE, ama YAPILANDIRILMIS sekilde eklenir. Amac: zamanla "BIST icin
hangi akademik bulgular var, bizim sistemimize nasil uygulanabilir"
sorusuna cevap veren, BUYUYEN bir arsiv olusturmak.

TAKIP EDILEN CAPA KAYNAKLAR (periyodik taramada ONCE bakilacaklar):
  - Cumhur Ekinci (ITU) - sites.google.com/view/cumhurekinci/research
    BIST mikro-yapisi/HFT/yatirimci davranisi uzerine en uretken
    Turk akademisyen, sayfasi kendi kendini guncelliyor.
  - Borsa Istanbul Review - Borsa Istanbul'un kendi SSCI/Scopus
    indeksli dergisi, en yuksek kalite kaynak.
  - DergiPark - Turkiye akademik dergi platformu, genis tarama icin.
  - YOK Ulusal Tez Merkezi (tez.yok.gov.tr) - tum Turkiye tezleri.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime

DOSYA = "data/akademik_bulgular.json"


def _oku():
    try:
        with open(DOSYA, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"makaleler": []}


def makale_ekle(baslik, yazarlar, yil, dergi_veya_kaynak, url, ana_bulgu,
                 sistemimize_ilgisi, ilgili_semboller=None):
    """Tek bir akademik kaynak kaydi. Tekrar onleme: (baslik, yil) ciftiyle."""
    veri = _oku()
    for m in veri["makaleler"]:
        if (m["baslik"], m["yil"]) == (baslik, yil):
            return m
    kayit = {
        "baslik": baslik, "yazarlar": yazarlar, "yil": yil,
        "dergi_veya_kaynak": dergi_veya_kaynak, "url": url,
        "ana_bulgu": ana_bulgu, "sistemimize_ilgisi": sistemimize_ilgisi,
        "ilgili_semboller": ilgili_semboller or [],
        "eklenme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    veri["makaleler"].append(kayit)
    atomik_json_yaz(DOSYA, veri)
    return kayit


if __name__ == "__main__":
    # 07.08 arastirmasindan dogrulanan bulgular (web_search ile)
    makale_ekle(
        "Algorithmic and High-frequency Trading in Borsa Istanbul",
        "Ersan, O., Ekinci, C.", 2016, "Borsa Istanbul Review 16(4), 233-248",
        "https://doi.org/10.1016/j.bir.2016.09.005",
        "BIST'te HFT payi islem hacminin ~%6'sina kadar cikiyor (2013-2014 "
        "verisiyle), buyuk emirlerde ve portfoy/fon yonetim firmalarinin "
        "emirlerinde daha yuksek (~%10-12). Algoritmik ticaret NASDAQ'in "
        "2003-2005 seviyelerine paralel.",
        "Bize kurumlarla/algoritmalarla 'ne kadar rekabet ettigimiz' "
        "konusunda somut, olculebilir bir referans veriyor - %6 hala "
        "gelismis piyasalara (ABD %50+) gore DUSUK, yani BIST'te "
        "insan/perakende akisinin agirligi hala buyuk.",
        [],
    )
    makale_ekle(
        "The Performance of Selected High-Frequency Trading Proxies: "
        "An Application on Turkish Index Futures Market",
        "Olgun, O., Ekinci, C., Arikan, R.", 2024, "Finance Research Letters, Vol 65, 105523",
        "https://www.sciencedirect.com/science/article/pii/S1544612324005531",
        "Turk vadeli islemler piyasasinda HFT vekillerinin (proxy) "
        "performansini karsilastiriyor - COK YENI (2024).",
        "Metodolojik referans - HFT tespiti icin kullanilan vekillerin "
        "hangisinin daha guvenilir oldugu, ileride kendi analizimizde "
        "faydali olabilir.",
        [],
    )
    makale_ekle(
        "Disposition bias among Borsa Istanbul investors: What do we "
        "know about type, size and trading frequency?",
        "Kahya, E.H., Ekinci, C.", 2022, "Journal of Behavioral and Experimental Finance, Vol 35, 100682",
        "https://www.sciencedirect.com/science/article/pii/S2214635022000351",
        "BIST yatirimcilarinin (turlere gore) 'disposition bias' "
        "(kaybedeni elde tutma, kazananı erken satma) egilimini olcuyor.",
        "COK ONEMLI - bu, bugunku RSI asiri-satim tersine-donus "
        "bulgumuzun (p=0.032 anlamli, 9/9 parametre saglam) OLASI "
        "DAVRANISSAL ACIKLAMASI olabilir: eger yatirimcilar kaybeden "
        "hisseleri INATLA elde tutuyorsa, bu satis baskisini YAVAS "
        "TUKETIR (kademeli dusus), tukenince SERT toparlanma (bizim "
        "yakaladigimiz sicrama) olusabilir. Test edilmeli.",
        [],
    )
    makale_ekle(
        "Daily and Intraday Herding within Different Types of "
        "Investors in Borsa Istanbul",
        "Dalgic, N., Ekinci, C., Ersan, O.", 2021, "Emerging Markets Finance and Trade, Vol 57, 1793-1810",
        "https://www.tandfonline.com/doi/full/10.1080/1540496X.2019.1641082",
        "BIST'te farkli yatirimci turleri arasinda gunluk/gun-ici suru "
        "davranisini olcuyor.",
        "Bizim 'perakende-baskin piyasa' temamizla dogrudan ilgili - "
        "suru davranisinin GUCLU oldugu zaman dilimleri/kosullar "
        "varsa, sinyallerimizin GUVENILIRLIGINI zamanla iliskilendirebiliriz.",
        [],
    )
    makale_ekle(
        "Google search and stock returns: A study on BIST 100 stocks",
        "Ekinci, C., Bulut, A.E.", 2021, "Global Finance Journal, Vol 47, 100518",
        "https://www.sciencedirect.com/science/article/pii/S1044028319302017",
        "Google arama hacmi ile BIST 100 hisse getirileri arasindaki "
        "iliskiyi inceliyor - arama-ilgisi bir 'dikkat' vekili olarak "
        "kullaniliyor.",
        "YENI bir sinyal TURU fikri - fiyat/hacim/RSI disinda, "
        "'yatirimci ilgisi' (Google Trends gibi) bagimsiz bir veri "
        "kaynagi olabilir. Henuz test EDILMEDI - yeni veri kaynagi "
        "gerektiriyor (Google Trends API).",
        [],
    )
