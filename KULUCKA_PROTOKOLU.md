KULUCKA PROTOKOLU (IP-3) - RESMI
Baslangic: 07.07.2026 (ilk gercek sinyal gunu) | ILK BITIS: 18.08.2026 (6 hafta)

*** 08.08.2026 SAYAC SIFIRLAMA (protokolun kendi "DONDURMA" maddesi
geregi - mantik degisikligi ZORUNLU gorulunce sayac sifirlanir) ***
YENI BASLANGIC: 08.08.2026 | YENI BITIS: 19.09.2026 (6 hafta)

GEREKCE: sinyal_dogrulama.py (08.08) - kendi GERCEK sinyal gecmisimizle
(41 trade sinyali, T+1/T+2/T+3 gercek fiyat) olculdu:
  P3_SKOR_AL (n=21): T+1 ort getiri %-0.078 (NEGATIF), dogrulanan %42.9
    (yazi-turadan dusuk). Kod incelemesi: _entry esigi 30 gibi GEVSEK.
  POZ_AZALT (n=4-2): T+1/T+2 ort getiri %+3.4/%+4.7 (GUCLU TERSINE -
    risk-off sinyali sonrasi fiyat GUCLU YUKSELIYOR), dogrulanan %25/%0.
    Kod incelemesi: son alt-kosul OR-bagli (tek zayiflik sinyali yeterli).
UYGULANAN DUZELTME (08.08, V157_tam_duzeltme.txt): P3_SKOR_AL esigi
30->40, POZ_AZALT son alt-kosulu OR->AND. Ayrica (sinyal mantigi
DEGISTIRMEYEN, "kozmetik/hata duzeltme" kategorisinde) v112n plot
sirasi + atama konumu duzeltmesi.

Nitelik: Sistemin ANA kanit mekanizmasi. Geriye donuk hicbir test bunun
yerine gecemez; burada olculen sey "bu piyasada, bu evrenle, bu icraciyla"
performanstir.
Kurallar
DONDURMA: Kulucka boyunca V151/V195'in SINYAL MANTIGINDA degisiklik
yapilmaz. Kozmetik (renk/boyut/gosterim) serbesttir. Mantik degisikligi
zorunlu hale gelirse yapilir AMA kulucka sayaci o gun SIFIRLANIR ve
SURUM_NOTLARI.md'ye gerekcesiyle islenir.
KAYIT: Tum sinyaller data/tv_alerts_latest.json + aylik arsivde;
islemler islem_gunlugu.json'da; pozisyonlar portfoy.json'da tutulur.
Test/replay kayitlari (fiyat=348.50 parmak izli THYAO kayitlari ve
GERCEK_TEST) denetim disi tutulur.
DENETIM: Her Cuma kapanis sonrasi "hafta kapanisi" rutini kosulur ve
sonuc ozeti repoya haftalik dosya olarak islenir (data/denetim/).
HUKUM GUNU: 18.08.2026 haftasinda 6 haftalik toplu karne cikarilir.
Onceden ilan edilen metrikler ve esikler
Birincil (gec/kal karari bunlara baglidir):
M1 ACIL_CIK isabeti: sinyalden T+3 seans sonra fiyat sinyal fiyatinin
ALTINDA olan vakalarin orani > %60
M2 P1/P1Q isabeti: T+3'te sinyal fiyati UZERINDE kapanan orani > %55
M3 Sinyal-uyum: SINYALLI islemlerin tum islemlere orani > %80
(SINYALE_RAGMEN islem sayisi 6 haftada <= 2)
Ikincil (IP-1 kanitiyla secilen kirmizi metrikler - izlenir, esik yok):
M4 Rejim flip sikligi (V195 REJIM hucresinin haftalik degisim sayisi)
M5 Yeniden-giris gecikmesi (ACIL_CIK sonrasi ayni sembolde ilk P1/P2'ye
kadar gecen seans; V-donus tuzagi izlemesi)
M6 Haberli/habersiz sinyal isabet kiyasi (haber_akisi eslesmesiyle)
Hukum tablosu
3 birincil metrik de esigi gecerse: kulucka BASARILI -> gercek boyuta
kademeli gecis (ilk ay yari boyut), protokol "izleme" moduna alinir.
1-2 metrik gecerse: 3 hafta uzatma; zayif metrigin kok neden analizi.
Hicbiri gecmezse: sinyal mantigi revizyonu + kulucka SIFIRDAN.
Ornek yetersizligi (6 haftada <10 gercek sinyal): sonuc "hukumsuz",
kulucka sinyal sayisi 10'a ulasana kadar uzar.
Ilk veri noktalari (kayit)
08.07.2026 11:30 YKBNK + AKBNK ACIL_CIK (36.44 / 71.35): endeks ayni gun
-%2.16 kapatti -> M1 icin iki erken pozitif aday (T+3 hukmu 11.07'de).


======================================================================
*** HUKUM KAYDI - DONEM 2 (08.08 -> 19.09.2026): "HUKUMSUZ" ***
Kayit tarihi: 05.10.2026 | Karar mercii: Baskan (Altug) | Komite tavsiyesi
dogrultusunda. Sayac 05.10.2026 itibariyla 56/43'tedir; hukum gunu (19.09)
karar verilmeden gecmistir - bu kayit o boslugu kapatir.

OLCUM (kaynak: data/sinyal_arsiv.json, 08.08-19.09; data/denetim/hafta_2026-W40):
  M1 ACIL_CIK isabeti (esik >%60): 4/11 = %36 (ham T+3, n=11). Esigin ALTINDA.
     Piyasa-goreli okuma (M7, tum donem): n=13, isabet %53.8, t=0.78 - anlamli
     degil. Hafta denetim betigi M1'i "HESAPLANAMADI" yazdi; yukaridaki
     rakam arsivden ELLE hesaplandi.
  M2 P1/P1Q isabeti (esik >%55): pencerede P1/P1Q sinyali YOK (n=0). OLCULEMEZ.
  M3 Sinyal-uyum (esik >%80): islem_gunlugu.json'da 12 olay; metrik uretilmedi.
     W40'taki "%0.0 KALDI" veri yoklugu artefakti kabul edilir, basarisizlik
     sayilmaz. OLCULEMEZ.

HUKUM: HUKUMSUZ. Gerekce:
  1. Protokolun "ornek yetersizligi" maddesi: P1/P1Q n=0, M3 uretilmedi.
     "Hicbiri gecmezse -> revizyon + sifirdan" satiri, ancak uc metrik de
     OLCULEBILIR olsaydi isletilebilirdi; olculmeyen metrik basarisiz
     sayilmaz.
  2. Olcum penceresi fiilen bos kaldi: 03-04.09 webhook arizasi (alarm
     sil-yeniden-kur sirasinda checkbox bos kaldi); GUNLUK_OZET kapsami 01.10'a
     kadar eksik (30 sembolun 1'i), 02.10'da 22/30.
  3. Mantik dondurmasi 17.09.2026'da Baskan karariyla zaten kaldirildi
     (bu hukum kod kararini baglamaz; yalniz olcum donemini kapatir).
  GERCEK BOYUTA GECIS: YOK. Mevcut boyutla izleme devam eder.
  Notlar (karari degistirmez, kaydedilir): P3_SKOR_AL goreli T+3 -%0.57
  (n=208, t=-1.79, anlamli degil ama negatife yakin); P2_DIP_DONUS +%4.01
  (n=13, anlamli degil).

ACIK SORU (18.08'den beri cevapsiz): P3_SKOR_AL'in GERCEK esigi
  pSkorTaban=32 (input, grafik basina kayitli) HIC OLCULMEDI. 08.08'deki
  "30->40" duzeltmesi bu sinyale degil P3_RADAR/P4_HAZIRLIK'a inmisti.

*** DONEM 3 - YENI OLCUM DONEMI ***
BASLANGIC: [BASKAN: tarih yaz - oneri: duzeltilmis arsiv/gozlem betikleri
            repoya yuklendigi gun]  | SURE: 6 hafta  | BITIS: [baslangic + 42 gun]
ON KOSULLAR (donem baslamadan TAMAMLANMALI):
  O1. sinyal_arsiv_gunluk.py (zaman_utc + relvol alanli surum) repoda - TAMAM
      (05.10: arsivde 13 kayit zaman_utc/relvol tasiyor).
  O2. dusuk_teyit_yuksek_hareket_gozlem.py v2 (bosluk korumali) repoda.
  O3. M1'e IKINCI OKUMA eklenir: piyasa-goreli T+3 (XU100/XU30). Birincil
      hukum okumasi hangisi olacak, donem BASLAMADAN Baskan ilan eder
      (ham okuma yukselen piyasada ACIL_CIK'i yapisal cezalandirir).
  O4. M3'un veri kaynagi duzeltilir (islem_gunlugu olay tanimi / sinyal-uyum
      hesabi); hafta_denetim.py M3'u 0/0 iken "OLCULEMEDI" basar.
  O5. GUNLUK_OZET kapsami 30/30'a ulasmali: 02.10'daki 8 eksik sembolun
      (AKBNK, EKGYO, EREGL, ISCTR, OTKAR, TOASO, VAKBN, YKBNK) kok nedeni
      (TradingView mi Pipedream mi) Pipedream loglariyla belirlenir.
  O6. pSkorTaban'in sembol/grafik bazinda gercek degeri okunur ve kayda gecer.
ESIKLER: M1/M2/M3 esikleri (%60/%55/%80) donem BASINDA yeniden gozden
  gecirilir; Seytanin Avukati'nin itirazi (esikler veriden turetilmedi)
  Baskan tarafindan yanitlanir ve buraya islenir.
DONDURMA: Donem 3 boyunca ayni kural gecerli; mantik degisikligi sayaci
  sifirlar. (Boru hatti/olcum kodu dondurmadan muaftir.)
