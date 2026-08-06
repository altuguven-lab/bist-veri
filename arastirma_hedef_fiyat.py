"""
HEDEF FIYAT REVIZYON TAKIBI (05.08.2026) - Faz V0
Kurul karari: tema TURUNE (savunma/altyapi/altin vb.) gore kategori
COGALTMAK yerine, TUM temalari kapsayabilecek TEK bir olcut - aracik
kurumlarin hedef fiyat revizyon YONU - yapilandirilmis sekilde kaydedilir.

Veri KAYNAGI: otomatik degil - arastirma sirasinda (web_search/analist
raporu okurken) ELLE, ama YAPILANDIRILMIS sekilde eklenir. Amac: zamanla
"bu sembulde son N ayda kac YUKARI, kac ASAGI revizyon oldu" sorusuna
cevap veren bir gorunum olusturmak, ve bunu P1/P2'nin PF/WR'siyle
(kullanicinin panelden okudugu degerlerle) karsilastirmak.

KIRMIZI CIZGI: bu veri Pine'a HIC baglanmiyor, salt arastirma/baglam
kaydidir - otomatik bir sinyal/filtre uretmez.
"""
import json, datetime, os

DOSYA = "data/arastirma_hedef_fiyat.json"


def _oku():
    try:
        with open(DOSYA, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"kayitlar": []}


def _yaz(veri):
    os.makedirs(os.path.dirname(DOSYA), exist_ok=True)
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def kayit_ekle(sembol, tarih, kurum, eski_hedef, yeni_hedef, kaynak_not):
    """Tek bir hedef fiyat revizyonunu ekler. Yon otomatik hesaplanir
    (eski/yeni karsilastirmasindan) - elle girilmez, hata riski azalir.
    TEKRAR ONLEME: ayni (sembol,tarih,kurum,eski,yeni) zaten varsa
    eklenmez - __main__ bloğu her workflow kosumunda tekrar
    calistigi icin bu sart, aksi halde kayitlar katlanarak cogalir."""
    veri = _oku()
    for k in veri["kayitlar"]:
        if (k["sembol"], k["tarih"], k["kurum"], k["eski_hedef"], k["yeni_hedef"]) == \
           (sembol, tarih, kurum, eski_hedef, yeni_hedef):
            return k  # zaten var, tekrar ekleme
    if yeni_hedef > eski_hedef:
        yon = "YUKARI"
    elif yeni_hedef < eski_hedef:
        yon = "ASAGI"
    else:
        yon = "SABIT"
    kayit = {"sembol": sembol, "tarih": tarih, "kurum": kurum,
             "eski_hedef": eski_hedef, "yeni_hedef": yeni_hedef,
             "yuzde_degisim": round((yeni_hedef / eski_hedef - 1) * 100, 1),
             "yon": yon, "kaynak_not": kaynak_not,
             "eklenme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    veri["kayitlar"].append(kayit)
    _yaz(veri)
    return kayit


def sembol_ozet(ay_sayisi=6):
    """Her sembol icin son N ayda kac YUKARI/ASAGI revizyon oldugunu
    ozetler - P1/P2'nin PF/WR degerleriyle yan yana okunmak icin."""
    veri = _oku()
    esik_tarih = (datetime.date.today() - datetime.timedelta(days=30 * ay_sayisi))
    ozet = {}
    for k in veri["kayitlar"]:
        try:
            t = datetime.date.fromisoformat(k["tarih"])
        except ValueError:
            continue
        if t < esik_tarih:
            continue
        s = ozet.setdefault(k["sembol"], {"yukari": 0, "asagi": 0, "sabit": 0, "kayitlar": []})
        s[{"YUKARI": "yukari", "ASAGI": "asagi", "SABIT": "sabit"}[k["yon"]]] += 1
        s["kayitlar"].append(k)
    return ozet




def makro_not_ekle(tarih, konu, metin, ilgili_semboller):
    """06.08 EKI: bazi gelismeler (TCMB faiz patikasi gibi) TEK bir
    sembolun hedef fiyat revizyonu DEGIL - coklu sembolu etkileyen
    MAKRO/tematik bir gelisme. Bunu sahte bir eski/yeni hedef ciftine
    ZORLAMAK (uydurma rakam) yerine, AYRI bir "makro_notlar" listesinde
    tutuyoruz - kayitlar listesiyle KARISTIRILMAZ."""
    veri = _oku()
    veri.setdefault("makro_notlar", [])
    for n in veri["makro_notlar"]:
        if (n["tarih"], n["konu"]) == (tarih, konu):
            return n  # zaten var, tekrar ekleme
    not_kaydi = {"tarih": tarih, "konu": konu, "metin": metin,
                 "ilgili_semboller": ilgili_semboller,
                 "eklenme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    veri["makro_notlar"].append(not_kaydi)
    _yaz(veri)
    return not_kaydi


if __name__ == "__main__":
    # 05.08.2026 arastirmasindan dogrulanan gercek revizyonlar (kaynak:
    # is Yatirim, Tera Yatirim raporlari - web_search ile dogrulandi)
    kayit_ekle("ASELS", "2026-04-01", "Is Yatirim", 402, 450,
               "Nisan 2026 Hisse Stratejisi - artan jeopolitik gerilim, "
               "2026 siparis tahmini 10.6mlr->11.7mlr dolar")
    kayit_ekle("ASTOR", "2025-12-01", "Tera Yatirim", 217.45, 217.45,
               "Aralik 2025 baslangic hedefi - saha ziyareti raporunun "
               "referans noktasi")
    kayit_ekle("ASTOR", "2026-05-18", "Is Yatirim", 217.45, 367,
               "Mayis 2026 - global arz yetersizligi, yeni siparisler, "
               "AL tavsiyesi korundu")
    kayit_ekle("ASTOR", "2026-05-21", "Tera Yatirim", 311.20, 452.60,
               "Mayis 2026 - guclu 1Q sonuclari, yatirimci toplantisi "
               "sinyalleri, endeks-ustu getiri tavsiyesi")
    kayit_ekle("TRALT", "2026-05-15", "Is Yatirim", 53, 57,
               "Mayis 2026 - 1. ceyrek degerlendirmesi, tavsiye TUT "
               "(digerlerinden daha temkinli)")

    kayit_ekle("TUPRS", "2026-08-06", "Ziraat Yatirim", 6.5, 14,
               "Sabah Stratejisi - 2C26 net kar 45.9mlr TL (piyasa "
               "beklentisi 30.7mlr TL'nin ~%50 uzerinde). Net rafineri "
               "marji rehberi 6-7$'dan 13-15$/varile yukseltildi "
               "(deger hedef fiyat DEGIL, $/varil marj rehberi - "
               "orta nokta kullanildi).")
    kayit_ekle("ASELS", "2026-08-06", "Ziraat Yatirim", 6.9, 8.5,
               "Sabah Stratejisi - 2C26 net kar 8.5mlr TL, piyasa "
               "beklentisi 6.9mlr TL'nin uzerinde (%61.3 yillik artis). "
               "Bakiye siparis 20.7mlr USD'den 23.2mlr USD'ye yukseldi. "
               "(deger hedef fiyat DEGIL, milyar TL net kar - piyasa "
               "beklentisi vs gerceklesen kullanildi).")
    kayit_ekle("AKBNK", "2026-07-29", "Is Yatirim", 107, 93,
               "2C26 bilancosu sonrasi - net faiz marji ve ozkaynak "
               "karliligi beklentileri asagi revize edildi, 'Al' "
               "tavsiyesi korundu.")
    kayit_ekle("AKBNK", "2026-07-29", "Vakif Yatirim", 107.9, 97.0,
               "2C26 bilancosu sonrasi - karlilik beklentilerindeki "
               "asagi revizyon nedeniyle, tavsiye degismedi.")
    kayit_ekle("AKBNK", "2026-07-29", "Seker Yatirim", 108.10, 96.76,
               "2C26 bilancosu sonrasi - tavsiye 'Al' olarak korundu.")
    kayit_ekle("AKBNK", "2026-07-29", "GCM Yatirim", 116.80, 92.00,
               "2C26 bilancosu sonrasi - 4 kurumdan TUTARLI asagi "
               "revizyon deseni (Is/Vakif/Seker/GCM hepsi asagi).")
    kayit_ekle("TAVHL", "2026-02-26", "Deniz Yatirim", 436.60, 454.40,
               "Bilanco sonrasi guncelleme - Tiflis Havalimani "
               "degerlemesi 149->166mn Euro yukseldi (net etki pozitif), "
               "ama ciro/FAVOK beklentileri asagi revize edildi - "
               "KARISIK sinyal, tarih 1C26'ya ait olabilir (2C26 "
               "DEGIL, daha eski).")
    kayit_ekle("KCHOL", "2026-08-05", "Piyasa Konsensusu", 13.6, 19.7,
               "2C26 net kari 19.7mlr TL, piyasa beklentisi 13.6mlr "
               "TL'nin cok uzerinde (%93 yillik artis, onceki "
               "ceyrekten -558mn TL'den sert sicrama). (deger hedef "
               "fiyat DEGIL, milyar TL net kar - konsensus vs "
               "gerceklesen kullanildi, TUPRS/ASELS Ziraat kaydiyla "
               "ayni desen).")
    kayit_ekle("YKBNK", "2026-07-31", "Garanti BBVA Yatirim", 53.40, 51.00,
               "2C26 bilancosu sonrasi, 'endeks ustu getiri' tavsiyesi "
               "korundu.")
    kayit_ekle("YKBNK", "2026-07-31", "Vakif Yatirim", 52.60, 48.40,
               "2C26 net donem kari ceyreksel bazda geriledi, "
               "beklentilere paralel. 'AL' tavsiyesi korundu.")
    kayit_ekle("YKBNK", "2026-07-31", "Alnus Yatirim", 55.32, 44.30,
               "2C26 bilancosu sonrasi - 3 kurumdan (Garanti BBVA/"
               "Vakif/Alnus) TUTARLI asagi revizyon deseni - AKBNK "
               "ile AYNI banka-sektoru-geneli zayiflama temasi.")
    makro_not_ekle("2026-08-06", "TCMB faiz patikasi yumusama sinyali",
                   "BBVA: Eylul'de faiz koridorunda normallesme sinyali "
                   "bekleniyor. TCMB Baskani: faiz indirimleri enflasyon "
                   "kontrol altinda. 'Yil sonuna dogru TCMB'nin faiz "
                   "indirimi icin alani olabilir' yorumu. 05.08'deki "
                   "'faiz indirimi otelendi' temasinin HAFIF yumusamasi - kesin donus DEGIL, izlenmeye deger.",
                   ["AKBNK", "YKBNK", "GARAN", "HALKB", "VAKBN"])
    print("Ornek kayitlar eklendi.")
    print(json.dumps(sembol_ozet(), ensure_ascii=False, indent=2))
