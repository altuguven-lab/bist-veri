# SWING PINE SISTEMI - TEKNIK SPESIFIKASYON VE YOL HARITASI
Olusturma: 10.08.2026 | Kurul karari sonrasi hazirlanmistir.

## 0. KAPSAM VE ILISKI

Bu, V151/V16x (P1/P2/P3/POZ_AZALT/ACIL_CIK sistemi) ile **AYRI, bagimsiz**
bir Pine Script'tir. V151'in YERINE GECMEZ, YANINDA calisir. Kendi izole
sermaye "kovasi" ile calisir (bkz. REJIM_KALIBRASYON_PROMPTU.md Bolum 25,
Madde 3 karari - miras P1/P2 portfoyunden TAMAMEN IZOLE).

## 1. KANITLANMIS CEKIRDEK MANTIK (v1'e GIRMELI)

### 1.1 Giris Sinyali
**RSI(14) esik 30'un ALTINDAN YUKARI KESISIM.**
Kanit: rsi_asiri_satim_swing.py backtest'i, 5 yil, 30 sembol, 276 islem.
Isabet %52.2, ort net getiri +%6.746, t=7.694 (istatistiksel anlamli,
p<0.001). Parametre-saglamlik: 9/9 kombinasyon (RSI 10/14/21 x esikler
25-75/30-70/35-65) POZITIF cikti.
DURUST SINIRLAMA: XU100 karsilastirmasinda edge MUTEVAZI - islemlerin
yalniz %43.8'inde basit al-tut'u geciyor, ortalama fark yalniz +%1.86.
Bu, "kanitlanmis buyuk edge" DEGIL, "hafif ama istatistiksel anlamli
sinyal" olarak ele alinmali.

### 1.2 Cikis Mantigi (UC KURAL, HANGISI ONCE GELIRSE)
  a) SABIT STOP: giris fiyatindan -%12 (GUN ICI DUSUK/Low fiyatiyla
     kontrol edilir, GERCEKCI). Kanit: rsi_stop_loss_grid.py - -12
     esigi isabeti yalniz 1.8pp, ort getiriyi yalniz 0.3pp azaltirken,
     en kotu senaryoyu %33 iyilestirdi (-18.1 -> -12.2). -5/-8 esikleri
     edge'i COK fazla yiyordu (bu bir TERSINE-DONUS stratejisi, dar
     stop erken cikarip iyilesecek pozisyonlari kesiyor).
  b) BASARISIZ SICRAMA: RSI tekrar 30'un ALTINA duserse cik.
  c) KAR AL: RSI 70'in USTUNE cikarsa cik (asiri-alim).
  d) MAKS TUTMA: 90 gun gecerse cik (veri sonu/asiri uzama guvenligi).

### 1.3 Pozisyon/Sektor Limitleri
Kanit: Denetim Madde 4 karari (REJIM_KALIBRASYON_PROMPTU.md Bolum 25).
  - Pozisyon basina: kova'nin %12'si (SOYUT birim - GERCEK TL tutari
    Pine'da SAKLANMAZ/BILINMEZ, oransal sistem).
  - Maksimum 5 esizamanli pozisyon.
  - Ayni sektorden maksimum 2 esizamanli pozisyon (30 sembollük evren
    icin sektor haritasi: rsi_gozlem.py'deki SEKTOR_HARITASI referans
    alinmali - Pine'a AYNI haritanin manuel kopyasi gerekir, Pine
    disaridan JSON okuyamaz).
  - Limit asilirsa sinyal REDDEDILIR, SESSIZCE ATLANMAZ (webhook'ta
    "limit_disi_atlandi" gibi ayri bir alarm/etiket dusunulmeli).

## 2. DENEYSEL/OPSIYONEL KATMANLAR (v1'de KAPALI baslamali)

Bunlarin HICBIRI henuz sinyal_arsiv_gunluk.py / kazanc_reversal_izleme.py
disipliniyle YETERINCE dogrulanmadi. Pine'a eklenirse, ACIK/KAPALI bir
input.bool() ile, VARSAYILAN KAPALI olarak eklenmeli - "kanitlanmamis
bir katmani sessizce ana mantiga karistirma" hatasindan kacinmak icin
(bkz. Bolum 29 - radarTradeSrc guvenlik notu, AYNI mantik).

### 2.1 Yuksek-Hacim Filtresi (opsiyonel)
rsi_hacim_grup_backtest.py: YUKSEK_HACIM grubu (isabet %53.9/+%7.89)
DUSUK_HACIM grubundan (%49.6/+%5.49) DAHA IYI cikti - ama NEDEN
(likidite/guvenilirlik mi, disposition-bias mi) belirsiz kaldi
(Bolum 25-26, disposition-bias hattı VERI EKSIKLIGI nedeniyle
KAPATILMISTI). Eklenirse: sembolun ORTALAMA GUNLUK HACMI, evrenin
MEDYANININ ustundeyse sinyal "guclendirilmis" sayilabilir - ama
BU, HENUZ bagimsiz dogrulanmadi, v1'de kullanilmamali.

### 2.2 Kurumsal Teyit (Yabanci Takas Akisi)
rsi_gozlem.py'ye ZATEN eklendi (kurumsal_teyit alani) ama SALT
GOZLEM icin - filtre olarak KULLANILMIYOR. Henuz "kurumsal_teyit=
ARTIS olan sinyaller GERCEKTEN daha mi iyi" sorusuna cevap YOK
(orneklem cok kucuk). Pine'a eklenecekse, yabanci_takas_takip.json
Pine'a DOGRUDAN ERISILEMEZ (Pine disaridan dosya okuyamaz) - bu
katman ANCAK webhook/harici bir kopru (V195 benzeri input.source())
ile MUMKUN olur, v1 icin KAPSAM DISI birakilmali.

### 2.3 Kazanc Surprizi Reversal Cikisi
kazanc_surprizi_reversal.py + kazanc_reversal_izleme.py KURULDU ama
HENUZ SONUC gelmedi (ilk KCHOL sonucu ~24.08 civari beklenir). Bu,
FARKLI bir MEKANIZMA (haber-gudumlu asiri-tepki + duzeltme, RSI'nin
YAKALADIGI "trend-tersine-donus"ten AYRI) - eger ILERIDE dogrulanirsa,
AYRI bir giris kosulu (RSI'ya EK, RSI'nin YERINE DEGIL) olarak
eklenebilir. v1'de YOK.

## 3. KESINLIKLE KACINILACAK HATALAR (bugunku derslerden)

1. **GEVSEK ESIK KULLANMA:** V151'in P3_SKOR_AL'i (`_entry > 30`) COK
   gevsekti, istatistiksel olarak zayif cikti (T+1 dogrulanan %42.9).
   HER esik, mumkunse GERIYE-TEST edilmis olmali.
2. **OR yerine AND'e DIKKAT:** POZ_AZALT'in son alt-kosulu
   (`cvdFalling OR trendWeakening`) tek-sinyalle tetikleniyordu,
   erken/asiri-hassas cikislara yol acti. Cok-kosullu (birkac
   gostergenin AYNI ANDA dogrulanmasi gereken) kurallar TERCIH
   edilmeli.
3. **PLOT/ALARM SIRASI:** TradingView placeholder'lari yalniz ILK 20
   plotu degistirir - yeni webhook alanlari EKLENIRKEN MEVCUT
   carrier plot sirasi BOZULMAMALI (v112n hatasindan ders).
4. **SIFIRA BOLME VARSAYILANI:** "kayip YOK" (mukemmel) ile "veri
   YOK" (bilgisiz) durumlarini AYNI (0.0) DEGERLE GOSTERME - PF=0
   hatasindan ders (bkz. Bolum 28).
5. **KUMULATIF PANEL YANILGISI:** N/WR/PF/DD gibi panel gostergeleri
   KUMULATIF ise (07.07'den beri biriken TUM islemler), YENI bir
   duzeltmenin etkisini GORMEK icin AYRI, KALICI bir arsiv (sinyal_
   arsiv_gunluk.py gibi) SART - panel TEK BASINA yetersiz.

## 4. ACIK SORULAR - CEVAPLANDI (10.08, kullanici + kurul)

1. **Sermaye:** 750.000 TL baslangic - portfoy.json'daki miras
   pozisyonlardan TAMAMEN AYRI, Pine'a `capital` input olarak girilir.
2. **Webhook:** MEVCUT Pipedream zinciri (AYNI URL) kullanilacak.
3. **Alarm isimlendirmesi:** P1/P2/P3'e PARALEL, SW1/SW2/SW3 (RSI
   swing sinyalleri) - IKI AYRI panel/alarm grubu, TEK birlesik
   gosterim DEGIL (karisikligi onlemek icin).
4. **Backtest cografyasi (kurul karari):** config/universe.yml'deki
   AYNI 30 sembol, AYNI 5 yillik pencere (rsi_asiri_satim_swing.py
   ile TUTARLI). RSI hesaplama yontemimiz (ewm alpha=1/periyot,
   adjust=False - Wilder duzeltmesi) Pine'in yerlesik ta.rsi()
   fonksiyonuyla AYNI yontem - uyumsuzluk riski DUSUK. Pine
   YAZILDIKTAN SONRA, 3-5 sembolde birkac GECMIS kesisim tarihi/
   fiyati ELLE karsilastirilarak dogrulanacak.

## 4B. CEKIRDEK MANTIK ICIN EK VERI IHTIYACI (10.08 kurul tartismasi)

Asagidaki DORT boslugun HICBIRI "deneysel katman" (Bolum 2) DEGIL -
CEKIRDEK mantigin (Bolum 1) GUVENILIRLIGINI dogrudan etkiliyorlar:

1. **SAGKALIM YANLILIGI kontrol edilmedi** - 5 yillik backtest BUGUNKU
   30 sembollük evreni kullaniyor, o donemde borsadan cikan/kucülen
   ya da SONRADAN eklenen (ASTOR gibi) semboller test disi kalmis
   olabilir - sonuclari OLDUGUNDAN IYI gosteriyor olabilir.
2. **POZISYON/SEKTOR KISITLARIYLA calistirilmis bir backtest HIC
   yapilmadi** (EN ONEMLI boşluk) - 276 islemlik backtest HER
   sinyalin ALINDIGINI varsayiyor, ama v1'de "maks 5 esizamanli,
   sektor basina maks 2" kurali BAZI sinyalleri REDDEDECEK. Kisitlar
   UYGULANINCA performans AYNI mi KALIR - hic TEST EDILMEDI.
3. **ORNEKLEM BAGIMSIZLIGI supheli** - 276 islem "bagimsiz" sayildi
   ama RSI asiri-satim genelde PIYASA GENELI bir dususte BIRDEN FAZLA
   sembolde AYNI ANDA tetikleniyor olabilir - bu, istatistiksel
   anlamliligi (p<0.001) OLDUGUNDAN GUCLU gosteriyor olabilir.
4. **CANLI DOGRULAMA cok erken** - rsi_gozlem.py yalniz birkac gundur
   calisiyor, GERCEK kapanmis islem sayisi SIFIRA yakin. Backtest'in
   CANLI kosullarda tekrarlanmasi, v1'i BUYUK sermayeyle calistirmadan
   ONCE SART.

KARAR: Madde 1 ve 3, Pine YAZILMADAN ONCE Python'da EK test olarak ele
alinmali (SIRADAKI ADIM). Madde 2 ve 4 ise Pine yazildiktan/gozlemlendikten
SONRA dogal olarak GELECEK.

## 4C. MADDE 1 VE 3 SONUCLANDI (10.08) - ONEMLI BIR SURPRIZ BULUNDU

**Madde 3 (kisit-uygulanmis backtest) - rsi_kisitli_backtest.py:**
KISITSIZ (276 islem, isabet %52.2, ort net +%6.746) vs KISITLI (134
islem, isabet %43.3, ort net +%4.471). ISABET 8.9 PUAN, ORT GETIRI
%34 DUSTU. 141 reddedilen sinyalin TAMAMI "ESZAMANLI_LIMIT" (maks 5
pozisyon) - HIC "SEKTOR_LIMIT" reddi YOK. Sorun sektor cesitlendirme
DEGIL, "maks 5 esizamanli" kuralinin KENDISI.

YORUM (kurul): "maks 5" limiti muhtemelen PIYASA GENELI asiri-satim
anlarinda (cok sayida sembolde AYNI ANDA RSI sinyali) devreye giriyor
- bu anlar TAM DA en guclu toparlanma potansiyeli tasiyan anlar
OLABILIR. Alfabetik siralama (KALITE DEGIL) hangi sinyalin alinacagini
belirliyor - bu, RASTGELE bir kayip yaratiyor olabilir.

**ACIK KARAR (Pine yazilmadan ONCE cozulmeli):** eszamanli limit
degeri (5/7/10) VE siralama kriteri (alfabetik yerine "en derin RSI"
gibi basit bir kural) test edilip KARARLASTIRILMALI - bu, v1'in
CEKIRDEK mantiginin (Bolum 1.3) SAYISINI DEGISTIREBILIR.

**Madde 1 (sagkalim yanliligi) - sagkalim_yanliligi_duyarlilik.py:**
30/30 sembol "tam gecmisli" (>=1200 gun) cikti - TAM EVREN ve TAM-
GECMISLI ALT-KUME AYNI sonucu verdi (279 islem, isabet %52.0, ort net
+%6.633 - orijinal 276/52.2/6.746'ya YAKIN, kucuk fark VERI CEKME
zamanlamasindan kaynaklaniyor olabilir). BU BOYUTTA bir surpriz YOK -
guven artirici, ama TAM sagkalim-yanliligindan-arindirma HALA MUMKUN
DEGIL (yfinance borsadan TAMAMEN cikmis sirketler icin veri sunmuyor,
COZULEMEZ bir sinirlama olarak KALIYOR).

## 5. ONERILEN SIRA (yol haritasi)

  1. Acik sorulari (Bolum 4) kullanicidan netlestir.
  2. v1 Pine'ini YALNIZ Bolum 1'deki (kanitlanmis) mantikla yaz -
     Bolum 2'deki HICBIR deneysel katman OLMADAN.
  3. Pine ciktisini, rsi_asiri_satim_swing.py'nin Python backtest
     sonuclariyla KARSILASTIR (Bolum 4.4) - buyuk sapma varsa
     KOD/mantik farkini bul, DUZELT.
  4. TradingView'de KUCUK bir alt-kume sembolde (orn. 5 sembol)
     PAPER/gozlem modunda calistir, sinyal_arsiv_gunluk.py'ye
     BENZER bir arsivle sonuclari IZLE.
  5. Yeterli veri birikince (en az 4-8 hafta, Denetim Madde 5
     kapisi ile AYNI disiplin), Bolum 2'deki deneysel katmanlari
     TEK TEK, IZOLE test ederek DEGERLENDIR - hepsini BIRDEN
     EKLEMEK YERINE.
