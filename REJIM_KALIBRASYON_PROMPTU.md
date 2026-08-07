REJIM/KALIBRASYON DURUM PROMPTU (05.08.2026, guncel)
Bu belge, 05.08.2026'da (gun boyu) yapilan calisma ve kurul kararlarinin
konsolide ozeti - gelecekteki oturumlarin (ve gelecekteki Claude'un) hizli
baglam kazanmasi icin. VIOP ENTEGRASYON PROMPTU ile ayni disiplinde.
1) P1/P2/P3_SKOR "kuraklik" sorusu - dort ayri olcum mekanizmasi
a) Haftalik Kirilim (golge_kalibrasyon.py, "Katman A - Haftalik Kirilim")
KOSUL (P3_SKOR deploy icin): en az iki ARDISIK haftada isabet >= %50.
W30: en iyi esik %28.6 | W31: en iyi esik %40.6 (toparlanma var).
DURUM: kosul HENUZ karsilanmadi. W32/W33 trendi izlenmeli.
b) Sektor-Baglamli Kirilim ("Katman A - Sektor Baglamli Kirilim")
Kapsam BILINCLI DAR: yalniz Bankacilik (XBANK) + Sinai (XUSIN).
DURUM: yalniz NEGATIF grup var, POZITIF karsilastirma grubu HENUZ olusmadi.
c) v112n / v112wr (V151'in kendi tarihsel giris sayaci) - BASARISIZ DENEME,
GERI ALINDI
05.08 sabahi Pine'a eklendi (RG dummy plot slotu yeniden kullanildi).
SORUN: eklendikten sonra grafik "kapatip tekrar acinca" AKBNK N80->N0'a
dustu, VE panelin TUM "_v112" ailesi (REJIM-BT, FAKTOR-BT, VOL-BT,
SEANS-BT, Kelly) bos/NO0% gosterdi. Once "grafik yukleme durumu"
hipotezi kuruldu, sonra CURUTULDU: kullanici Pine'i v157'ye (05.08
degisiklikleri ONCESI) geri alinca panel dolu geldi (AKBNK N80 WR39%
dahil TUM semboller). Yani BIZIM EKLEMEMIZ (v112n plot) bir sekilde
TUM _v112 ailesini bozuyordu - tam mekanizma NETLESMEDI (kod
yapisal olarak dogru gorunuyordu), ama kanit (geri alinca duzelmesi)
kesin.
KARAR: v112n eklemesi ARTIK YOK (v157'de kalindi). Bir DAHA denenirse,
TEK BASINA, izole test edilmeli (baska hicbir degisiklikle
BIRLESTIRILMEDEN), hemen ardindan 2-3 sembolde N/WR kontrol edilerek.
d) YENI ve GUVENILIR yontem: Panelden N/WR/PF/DD elle okuma
v112n webhook'u basarisiz olunca, kullanici DOGRUDAN TradingView
panelinden (DSS satiri, "N<sayi> WR<yuzde>%" hucresi + yanindaki
"PF#.# DD#.#" hucresi) 29 sembolun degerlerini ELLE okuyup bildirdi.
Bu, guvenilir cikti - script'in KENDI hesapladigi, tum-tarihsel
performans ozeti.
SONUC (05.08, 29 sembol, PF sirali):
ASTOR(2.0) > EREGL(1.9) > ASELS(1.7) > KCHOL/TRALT/PETKM/AKBNK(1.5)
> TAVHL/TUPRS/HALKB/PGSUS(1.4) > YKBNK/BIMAS/FROTO(1.2) >
  VAKBN/SISE/TRMET/ENKAI/OTKAR/TOASO(1.1) > GARAN/MGROS/SAHOL/ULKER/
  DMLKT(1.0) > ALARK/AEFES(0.9) > ENJSA(0.8) > TTKOM(0.7, TEK ZARAR
  EDEN ORNEK).
Tum PF>=1.0 (TTKOM haric) - sistem KUMULATIF TARIHTE net karli,
dusuk WR (%33-45) tek basina endise degil (kazananlar kaybedenlerden
buyuk - klasik trend-takip imzasi).
NOT: DMLKT'nin N'si (32) digerlerinden cok dusuk - grafik gecmisi
kisa olabilir, dogrudan karsilastirma yaniltici.
2) Volatilite-PF korelasyonu - zayif-orta, tek basina aciklayici degil
volatilite_korelasyon.py (15 sembolle, sonra 29'a genisletildi manuel
okuma ile): gunluk getiri std'si ile PF arasinda +0.402 korelasyon
(orta duzey, guclu degil).
Istisnalar cok ogretici: EREGL (dusuk volatilite, PF 1.9 - yuksek)
ve GARAN (orta volatilite, PF 1.0 - en dusuk) hipotezi cignedi.
SONUC: volatilite TEK BASINA PF'yi acikliyor degil - baska bir
faktor (anlati/tema gucu) devrede.
3) Tema-hizalanmasi hipotezi - ARASTIRILDI, GUCLU KANIT VAR
Yuksek-PF uclusunun (ASTOR/EREGL/ASELS) HER BIRI FARKLI, bagimsiz ve
GERCEK (kaynaklarla dogrulanmis) bir anlati tasiyor - "savunma teması
hepsini acikliyor" ilk varsayimi CURUTULDU:
ASELS: savunma harcamalari/jeopolitik gerilim (Is Yatirim: hedef
402->450 TL, siparis tahmini 10.6->11.7mlr $, Nisan 2026).
ASTOR: kuresel sebeke altyapisi + ABD pazar genislemesi + sirkete
ozgu buyume (Tera/Is Yatirim: hedef 217->367/452 TL, Mayis 2026) -
SAVUNMA ILE ILGISI YOK.
TRALT (Turk Altin Isletmeleri - ALTIN MADENCILIGI): ons altin fiyati
temasi - SAVUNMA ILE HIC ILGISI YOK.
Bankacilik/faiz teması de HSBC'nin 04.08.2026 raporuyla dogrulandi:
2026 Q1'de faiz-indirim beklentisiyle BIST rallisi, Orta Dogu
catismasi baslayinca petrol->enflasyon->TCMB faizi %37'de sabit
tutmasi->gevseme otelenmesi ile BIST bir banda sikisti.
Dip sirada (TTKOM 0.7, ENJSA 0.8) ortak karakter: duzenlemeye tabi,
olgun, NET bir anlati/buyume hikayesi olmayan, "kamu hizmeti" tarzi
sirketler.
SONUC/PRENSIP: temanin TURU (savunma/altyapi/altin/faiz) onemli
degil - sembolun KENDINE OZGU, GUCLU ve GUNCEL bir anlati tasiyip
tasimadigi onemli. Bunu kategori kategori (Makro-Savunma,
Makro-Altin, ...) COGALTMAK yerine, TEK EVRENSEL bir olcut secildi:
hedef fiyat revizyon yonu (bkz. Bolum 4).
4) arastirma_hedef_fiyat.py - YENI, aktif izlenen sistem
Konum: repo koku (arastirma_hedef_fiyat.py) + tek seferlik workflow
(arastirma_hedef_fiyat.yml). Ag erisimi GEREKTIRMEZ - ELLE, ama
YAPILANDIRILMIS sekilde beslenir (kayit_ekle() cagrilariyla).
Veri: data/arastirma_hedef_fiyat.json - her kayit {sembol, tarih,
kurum, eski_hedef, yeni_hedef, yuzde_degisim, yon (oto hesaplanir),
kaynak_not}. TEKRAR ONLEME var (ayni kayit iki kez eklenmez).
sembol_ozet(ay_sayisi=6): son N ayda sembol basina kac YUKARI/ASAGI
revizyon oldugunu ozetler - P1/P2'nin PF/WR degerleriyle yan yana
okunmak icin tasarlandi.
06.08 itibariyle 16 kayit, 5 acik pozisyonun TAMAMI kapsaniyor
(AKBNK, KCHOL, TAVHL, YKBNK, ASTOR) + ASELS/TRALT/TUPRS.

### KRITIK BULGU (06.08): AKBNK/YKBNK vs ASTOR/KCHOL karsitligi -
   tema-hizalanmasi hipotezinin ilk GERCEK izlenebilir test cifti
- AKBNK: 4 kurumdan (Is/Vakif/Seker/GCM) TUTARLI ASAGI hedef fiyat
  revizyonu (29.07, net faiz marji/ROE beklentisi asagi cekildi).
- YKBNK: 3 kurumdan (Garanti BBVA/Vakif/Alnus) TUTARLI ASAGI revizyon
  (31.07, ayni banka-sektoru-geneli zayiflama temasi).
- KCHOL: 2C26 net kari 19.7mlr TL, piyasa beklentisi 13.6mlr TL'nin
  COK uzerinde (05.08, %93 yillik artis) - GUCLU pozitif.
- ASTOR: zaten guclu yukari (bkz. Bolum 3).
- 06.08 sabahi haber akisi teyidi: "TUFE-TCMB faiz makasi 5 ayin en
  yuksegi" - bankacilik temasinin zayifladigi tezini destekliyor.
- TEST EDILECEK HIPOTEZ: bu anlati karsitligi (bankacilik zayif,
  ASTOR/KCHOL guclu) onumuzdeki haftalarda P1/P2'nin PF/WR
  degerlerinde AKBNK/YKBNK'de dusus, ASTOR/KCHOL'de istikrar/artis
  olarak GORULECEK Mİ? Panelden N/WR/PF/DD tekrar okunup (birkac
  hafta sonra) bugunku degerlerle (Bolum 1d) KARSILASTIRILMALI. Bu,
  tema-hizalanmasi hipotezinin ilk somut, onceden-belirlenmis test
  senaryosu.
Arastirma yontemi - AGGREGATOR kaynaklar once
Bireysel araci kurum siteleri (Is Yatirim, Ziraat, Ak Yatirim, YK
Yatirim, Garanti BBVA arastirma sayfalari) TEST EDILDI - basliklar/
ozet cumleleri ACIK, ama TAM rapor metni bir KOTA/uyelik sistemiyle
KILITLI ("Not enough quota to unlock this post").
DAHA VERIMLI YOL bulundu: ucuncu-taraf AGGREGATOR kaynaklari - Rota
Borsa (haftalik "aracı kurumlar X hisse icin hedef fiyat belirledi"
ozetleri), CNBC-e/CNN Turk Finans/BorsaninGundemi (uc ayda bir,
"36 banka ve araci kurumun 821 hisse tavsiyesi" tarzi Matriks
kaynakli konsensus raporlari - kac kurum onerdigi bilgisi dahil),
borsaveyatirim.com (TEB/Tera/A1 Capital/Ahlatci/Ak/ALB/Alnus/Ata/
OYAK/Seker/Tacirler/Trive gibi onlarca kurumun hedef fiyat
sayfalarina tek yerden baglanti veren hub).
ISLEYIS: arastirma yaparken ONCE bu aggregator/ozet kaynaklari
taramak (birden fazla sembolu tek seferde yakalamak icin), gerektiginde
(kesin rakam icin) birincil kaynaga (kurumun kendi raporu, web_search
ile) inmek.
Ziraat Yatirim - MUKEMMEL kaynak, TAM acik
www.ziraatyatirim.com.tr/sabah-stratejisi: kota/uyelik duvari YOK,
gunluk detayli sirket bilanco analizleri (net kar, FAVOK, rehber
revizyonlari, piyasa beklentisi karsilastirmasi) tamamen ucretsiz.
06.08.2026 raporundan dogrulandi: TUPRS 2C26 net kar 45.9mlr TL
(piyasa beklentisi 30.7mlr'nin ~%50 uzeri), net rafineri marji
rehberi 6-7$'dan 13-15$/varile yukseltildi - TUPRS'in 05.08'deki
%6 hareketinin GERCEK, dogrulanmis nedeni. ASELS de benzer sekilde
net kar piyasa beklentisinin uzerinde (%61.3 yillik artis).
arastirma_hedef_fiyat.py'ye eklendi (marj rehberi/net kar degerleri
"hedef fiyat" alanina proxy olarak kondu, kaynak_not'ta acikca
belirtildi).
Ak Yatirim - JS ile render ediliyor, DOGRUDAN erisilemez
akyatirim.com.tr/tr/raporlarimiz/arastirma-raporlari, DataStore'daki
gibi bir SPA (JavaScript render) - statik metin cekme aracimizla
rapor listesi/icerigi GORUNMUYOR. Icerik kotu degil, yalniz mevcut
aracla erisilemez. Ileride gerekirse web_search ile Ak Yatirim'in
belirli bir raporunu (baslik bilindiginde) dolayli aramak mumkun.

5) Bugun ELE ALINAN, dogrulanan diger bulgular
THYAO-348.50 sahte sinyali
05.08 sabahi "P1_KALITELI_AL 348.50" kaydi geldi, gercek fiyat (313)
ile hic uyusmuyordu. TradingView'de eski/statik bir alarm OLMADIGI
DOGRULANDI (kullanici kontrol etti) - kok neden tam netlesmedi,
muhtemelen tek seferlik veri/tik anomalisi. Kayit data'dan silindi.
hafta_denetim.py'ye GENEL bir "fiyat sapmasi saglama kontrolu"
eklendi (GUNLUK_OZET referansindan >%7 sapan her sinyali INCELE
diye isaretler, otomatik dislamaz) - benzer olaylari gelecekte
yakalamak icin.
saglik_kontrol.yml gercek bir arizayi haftalardir DOGRU bildiriyordu
"failed" (kirmizi) Actions sonucu, script'in KASITLI exit(1) davranisi
(ariza varsa gorunur olsun diye) - bizim "bozuk workflow" sanip
gormezden geldigimiz seyler aslinda GERCEK arizaydi (fiyat kanali
30dk esigini asiyordu).
Duzeltildi: update.yml cron'u saatte 4->2'ye (GitHub'in yuksek-siklik
zamanlamalarda sessizce atlama riski, haber_update.yml'deki kok
nedenin ayni ailesi), saglik_kontrol.py'nin QUOTES_ESIK_DK'si 30->40.
Olay-Tabanli vs Teknik Kacan Firsat (retro_firsat.py)
TUPRS'in 05.08'deki %6 bilanco hareketi sinyal uretmedi - bu soruyu
dogurdu: kuraklik ne kadari HABER/BILANCO kaynakli?
SONUC: 39 kacan firsattan yalniz 3'u (%7.7) bilancoya yakin (+/-3
gun), 36'si (%92.3) teknik/aciklanamayan. SINIRLAMA: bilanco_takvimi.
json yalniz 20.07'den itibaren + dar kapsamli - gercek oran
muhtemelen biraz yuksek ama BUYUK RESIMDE kuraklik ANA OLARAK
teknik/kalibrasyon kaynakli gorunuyor.
Gun-ici alim-satim (ORB/VWAP/Supertrend+ADX/MACD+MFI) - 05-06.08
KONSOLIDE DURUM

05.08: 5 deneme (ORB v1/v2/v3-grid, VWAP v1/v2), hicbiri pozitife
gecmedi. En iyi: ORB v3, AKBNK/KCHOL, ort net getiri %-0.076.

06.08: 2 YENI gosterge ailesi test edildi:
- Supertrend+ADX (genel, 4 sembol filtresiz): 11 islem, isabet
  %36.4, ort net %-0.246 - yine negatif, YETERSIZ orneklem.
- MACD+MFI (4 sembol filtresiz): 287 islem, isabet %26.5 (bugune
  kadarki EN DUSUK), ort net %-0.256.

KRITIK BULGU (06.08): Supertrend+ADX'i GUCLU_ANLATI (ASTOR+KCHOL)
vs ZAYIF_ANLATI (AKBNK+YKBNK) gruplarina ayirinca (bkz. Bolum 3):
  GUCLU_ANLATI: 8 islem, isabet %62.5, ort net getiri +%0.863 (POZITIF!)
  ZAYIF_ANLATI: 5 islem, isabet %40.0, ort net getiri -%0.358
Bu, 6 denemenin (ORB v1-3, VWAP v1-2, Supertrend genel) ILK KEZ
pozitif cikan alt-kumesi. Orneklem KUCUK (13 islem toplam) - kesin
kanit degil, ama yon net.

ARASTIRMA RAPORU (06.08, launch_extended_search_task ile, Turkce
ceviri repo'da BIST_Arastirma_Raporu_TR.md olarak mevcut - repo
disinda, yalniz kullanicinin masaustunde) - ANA SONUC:
- Teknik gostergelerin tek basina kaybetmesi ANOMALI DEGIL, beklenen
  sonuc (Sullivan-Timmermann-White 1999; McLean & Pontiff 2016 -
  yayinlanmis stratejiler yayin-sonrasi %58 daha az kazandiriyor).
  Kalabalik piyasada herkesin bildigi gostergeler kalabalıklastıkça
  kar penceresi kapaniyor.
- Supertrend+ADX'in anlati-gucune gore ters isaret vermesi TESADUF
  DEGIL: PEAD (bilanco-sonrasi fiyat surklenmesi) ve kazanc/analist-
  revizyon momentumu literatürü (Chan-Jegadeesh-Lakonishok 1996;
  Bernard-Thomas 1989) TAM bu deseni ongoruyor - piyasa temel habere
  KADEMELI tepki veriyor, teknik trend sinyali bu surklenmenin erken
  fazini yakaliyor (gercek katalizoru olan hissede), katalizorsuz
  hissede ise gurultu.
- BIST'e ozgu kanit ELVERISLI: PEAD Turkiye'de dogrudan belgelendi
  (Ahlatcioglu & Okay 2021, Borsa Istanbul Review - bilanco sonrasi
  60 gunde %2.9 kumulatif anormal getiri farki). Turk piyasasi
  perakende-akis-baskin (TSPB: yerli yatirimcilar 2025 sonu itibariyle
  portfoyun %63.7'sini elinde tutuyor) - bu, eksik-tepki/asiri-tepki
  paternlerinin (PEAD + kisa-vadeli tersine donus, Bildik & Gulay 2007)
  GUCLU oldugu tam ortam.

STRATEJIK YON DEGISIKLIGI ONERISI (arastirmadan, HENUZ KARAR
ALINMADI - kullaniciyla konusulacak):
Gun-ici (15dk bar, scalping) yaklasimini BIRAKIP, projeyi COK-GUNLU
(5-60 gun) KATALIZOR-GUDUMLU SWING sistemine donusturmek - temel/
anlati sinyali (arastirma_hedef_fiyat.py) hisseyi/yonu secsin, teknik
sinyal (Supertrend/ORB) yalniz GIRIS ZAMANLAMASI+STOP icin kullanilsin.
4 asamali yol haritasi: (1) ufku 5-60 gune uzat, (2) anlati gucunu
OLCULEBILIR degiskenlere don (SUE, analist revizyon genisligi) -
zaten arastirma_hedef_fiyat.py bunun cekirdegi, (3) istatistikleri
duzelt (BIST-100 tam evren, 5-10 yil, anlamlilik testi - 13 islem
YETERSIZ), (4) orta/kucuk-cap'lere yonel (PEAD en guclu, kurumsal
arbitraj en zayif, ama spread/maliyet daha yuksek - gercekci
modellenmeli).

KARAR: Gun-ici proje (dar anlamda, 15dk scalping) suresiz ASKIYA
ALINMIS durumda kaliyor. Anlati+teknik sentezi fikri ise CANLI ve
bir sonraki adayin bu olmasi onerilir - ama COK-GUNLU ufuk ile,
gun-ici degil.

ANLATI-TEKNIK CAPRAZ REFERANS (06.08, YENI arac) - anlati_teknik_
capraz_referans.py: sentetik backtest yerine, P1/P2'nin GERCEK
tarihsel sinyallerini (tv_alerts_latest+arsiv) arastirma_hedef_
fiyat.json'daki anlati gucuyle (90 gunluk pencere) capraz referanslar.
T+3/T+10/T+20 ufuklarinda olcer (PEAD/revizyon etkisi haftalar surer).
Mimari: Pine'a HIC dokunmuyor, sentez tamamen Python/GitHub
katmaninda - yeni bir Pine script'i GEREKMEDI.

ILK KOSUM SONUCU (06.08) - orneklem HENUZ cok kucuk, KESIN DEGIL:
  GUCLU_ANLATI: 9 sinyal, T+3 hesaplanan yalniz 2 (isabet %100, +%6.18)
  ZAYIF_ANLATI: 7 sinyal, T+3 hesaplanan yalniz 2 (isabet %100, +%5.57)
  BILINMIYOR:  26 sinyal, T+3 hesaplanan 9 (isabet %44.4, -%1.579)
DIKKAT: ZAYIF_ANLATI'nin da %100 isabetli cikmasi, Supertrend+ADX'in
tema-karsilastirma bulgusuyla (ZAYIF -%0.358) CELISIYOR gibi
gorunuyor - ama 2'ser hesaplanan sinyalle bu bir CELISKI DEGIL,
gurultu. T+10/T+20 hic gorunmedi (kulucka ~1 ay, cogu sinyal icin
henuz dolmadi - beklenen). BILINMIYOR grubunun buyuklugu (%62),
arastirma_hedef_fiyat.json'un HENUZ dar kapsamli oldugunu gosteriyor.
SONUC: bu, TEK SEFERLIK bir kanit degil - ZAMANLA (T+10/T+20 dolup,
arastirma_hedef_fiyat.json genisledikce) guclenecek bir olcum
sistemi. Her hafta kapanisinda tekrar kosulup takip edilmeli.

7) BIST-ROS entegrasyonu (06.08, oglenden sonra) - parca parca kabul

ChatGPT'nin hazirladigi "BIST-ROS Master Blueprint" paketi (PDF +
sprint01-foundation.zip) incelendi. KARAR: paket OLDUGU GIBI
uygulanmadi (asiri genis kapsam, "additionalProperties: False" gibi
kirilgan semalar, ayni anda cok fazla sistemi degistirme riski -
bugunku "tek degisiklik, izole test" dersimize aykiri). Bunun yerine
FIKIRLER tek tek, test edilerek benimsendi:
- json_atomik_yaz.py (atomik JSON yazma - fsync+os.replace) -
  arastirma_hedef_fiyat.py'ye entegre edildi, 4 senaryoda test edildi.
- config/market_calendar.yml + piyasa_takvimi.py - BIST 2026 tatil
  takvimi 4->15 gune genisletildi (Ramazan/Kurban dahil, 3 kaynaktan
  capraz dogrulandi). saglik_kontrol.py'nin kendi sabit-kodlanmis
  (ayni sekilde eksik) TATIL_GUNLERI listesi buna baglandi - dosya/
  modul bulunamazsa SESSIZCE eski listeye doner (cokme yok).
  saglik_kontrol.yml'e `pip install pyyaml` eklendi (once eksikti,
  "No module named yaml" hatasi verdi, duzeltildi).
- REDDEDILEN/ERTELENEN parcalar: fetch_bist.py'nin tam yeniden yazimi,
  update.yml'in degistirilmesi, additionalProperties:False semasi -
  hicbiri canliya alinmadi, cok riskli/erken bulundu.

YAN BULGU: 16:15 duz-bar deseni (cozulmedi, IZLENIYOR)
06.08 13:30 UTC kosumunda, TRMET disindaki TUM sembollerin en son
bari (16:15) DUZ gorundu (acilis=yuksek=dusuk=kapanis, hacim=0) -
TRMET ise bir onceki (16:00) barda GERCEK degerler tasidi. Muhtemel
aciklama: Yahoo'nun en taze bari henuz "olgunlasmamis" olmasi (fetch,
tam o bar YENI basladigi anda calismis olabilir). ORB/Supertrend gibi
GECMISE-DONUK analizler (ayri 60-gunluk cagriyla calisiyorlar) muhtemelen
ETKILENMIYOR - yalniz ANLIK brifing/stop-kontrolu birkac dakikalik
gecikme tasiyabilir. DUZELTME YAPILMADI - once TEKRARLANIYOR MU
(her kosumda mi, nadiren mi) izlenmeli, sistemikse o zaman (orn.
"en yeni bar duzse bir onceki barı kullan" mantigi) duzeltme
dusunulmeli.

8) KCHOL vakasi (06.08, oglenden sonra) - tek-hisse uyari boslugu
KAPATILDI

Bilanco beklentiyi asmasina (19.7mlr TL net kar, arastirma_hedef_
fiyat.json'da GUCLU_ANLATI kaydi) RAGMEN KCHOL gun icinde -%4.85
dustu. Portfoy-geneli gunluk esik (-%3) TETIKLENMEDI (KCHOL portfoyun
kucuk payi), stop (190 TL) henuz KIRILMADI (fiyat 196) - HICBIR
otomatik uyari gelmedi. Kullanici fark etti, sorguladi.

KOK NEDEN: sistemde TEK BIR hissenin gun icinde buyuk (ama henuz
stop'u kirmayan, portfoy-geneli esigi de asmayan) hareketini
yakalayan bir kontrol HIC yoktu - yalniz portfoy-geneli (toplam
deger) ve mutlak-stop-seviyesi katmanlari vardi, ikisi de bu
senaryoyu KACIRACAK sekilde tasarlanmisti.

DUZELTME (ayni gun, test edilip DOGRULANDI): portfoy_risk_kontrol.py'ye
TEK_HISSE_ESIK_YUZDE=-3.5 kontrolu eklendi - her acik pozisyon icin,
onceki GUNLUK_OZET kapanisindan (tv_alerts_latest.json) bugunku
anlik fiyata (bist_quotes.json) gore degisim hesaplanir, esik asilirsa
ayri bir GitHub Issue acilir (saglik_kontrol.py'nin kanitlanmis
mekanizmasiyla). AYNI GUN gercek KCHOL vakasinda TEST EDILDI:
"ISSUE ACILDI: TEK HISSE HAREKETI: KCHOL" - dogru calisti, digerleri
(AKBNK -1.11%, YKBNK -0.82%, ASTOR +2.25%) dogru sekilde SESSIZ
kaldi (esigi asmadilar).

DERS: uc ayri koruma katmani (stop-seviyesi, portfoy-geneli esik,
GUNLUK_OZET) birbirini TAMAMLIYOR sanilirken, aralarinda GERCEK bir
bosluk varmis - kullanicinin "hicbir uyari gelmedi" gozlemi olmasaydi
fark edilmeyebilirdi. Benzer bosluklar baska katmanlarda da olabilir -
periyodik olarak "hangi senaryo hicbir mekanizmayi tetiklemez"
sorusu soruta sorulmali.

10) SWING MOMENTUM VEKILI - bugunun EN GUCLU bulgusu (06-07.08)

Statik anlati etiketinin (Bolum 3/7) metodolojik hatasi (5 yila SABIT
uygulanmasi) sonrasi, kurul DINAMIK, SAF FIYATTAN tureyen bir vekile
gecti: sinyal ANINDAKI 6-aylik (126 is gunu) trailing getiri.
supertrend_adx_swing_momentum_backtest.py - GUNLUK barlar, 5 yil,
TUM 30 sembollük evren.

Yol boyunca IKI GERCEK veri-kalitesi hatasi bulunup DUZELTILDI:
- Son (bugunku, gun tamamlanmadan cekilen) barin Close'u NaN
  gelebiliyor - TEK bir NaN kayit, Python sum() davranisi yuzunden
  TUM grup istatistigini bozuyordu. Iki katmanli duzeltme: (1) NaN
  barlari kaynakta atla, (2) _ozet_hesapla() ile TUM istatistik
  hesaplarini NaN'a karsi genel olarak dayanikli yap.
- Commit/CDN gorunurlugu sorunu (bugunku tanidik desen) - dosya
  3 kez "yuklendi" denmesine ragmen repoda gorunmedi, GERCEKTEN
  guncellenene kadar (grep ile dogrulanarak) 3 tur surdu.

SONUC (291 islem, 5 yil, 30 sembol):
  GUCLU_MOMENTUM (son 6 ay YUKARI): 196 islem, isabet %30.6, ort net
    %-2.236 (NEGATIF)
  ZAYIF_MOMENTUM (son 6 ay ASAGI): 51 islem, isabet %49.0, ort net
    %+4.545, TOPLAM +%231.78 (POZITIF, tutarli bir orneklemle)
  Genel (karisik): %-1.303 (gruplara ayrilmadan negatif - AYRISMA
    onemli olan)

YORUM: klasik "momentum" beklentisinin TERSI, ama TESADUF DEGIL -
bugunku arastirma raporunun BIST-ozgu bulgusuyla (Bildik & Gulay 2007:
Turk piyasasinda EN GUCLU tekrarlanan anomali KISA-VADELI TERSINE
DONUS/asiri-tepki, momentum DEGIL) TAM ORTUSUYOR. Sinyal ("6 ay dusmus
hissede Supertrend YUKARI flip + ADX teyidi") fiilen bir "asiri-satilmis
toparlanma" sinyali gibi davraniyor.

DIKKAT: 51 islem HALA kesin kanit degil - istatistiksel anlamlilik
testi (arastirma raporu Asama 3) HENUZ yapilmadi. Bir sonraki adim
bu.

12) CAPRAZ-DOGRULAMA SONUCU (07.08) - momentum hipotezi TERK EDILDI,
ama RSI kendi basina umut verici cikti

Iki paralel test yapildi: (a) Supertrend swing 5y->10y genisletme,
(b) RSI(14) asiri-satim tersine-donus (RSI<30'dan yukari kesisim,
RSI>=70'te kar-al, 90 gun maks tutma) - AYNI momentum-grup ayrimiyla.

BULGULAR:
- Supertrend 10y (544 islem): ZAYIF_MOMENTUM hala GUCLU_MOMENTUM'dan
  iyi (+1.434 vs -2.366) AMA etki 5y'deki +4.545'ten ZAYIFLADI -
  orneklem buyuyunce sinyal kuculdu, bu once-kanitin sansa dayali
  olabilecegi endisesini GUCLENDIRIYOR.
- RSI (276 islem): momentum iliskisi TERSINE cikti (GUCLU_MOMENTUM
  +8.709, ZAYIF_MOMENTUM +5.214 - Supertrend'in TAM TERSI). CAPRAZ-
  DOGRULAMA BASARISIZ - iki bagimsiz gosterge TUTARSIZ sonuc verdi.

KARAR: "anlati/momentum gucu, teknik sinyal kalitesini etkiler"
hipotezini ARTIK AKTIF TAKIP ETMIYORUZ - yeterince test edildi,
tutarli cikmadi. BIST-ROS/arastirma raporu baglaminda BASLATILAN bu
hat, bugun itibariyle KAPATILDI (gelecekte yeni kanit cikarsa yeniden
acilabilir).

AMA: RSI stratejisinin KENDISI (momentum filtresinden BAGIMSIZ,
TUM 276 islem) cok guclu: isabet %52.2, ort net getiri +%6.718.
Bu, bugunun EN TEMIZ, ayri bir bulgusu - istatistiksel anlamliligi
AYRICA test ediliyor (bkz. asagi).

14) RSI ISTATISTIKSEL ANLAMLILIK - GECTI, bugunun en guclu sonucu

rsi_anlamlilik.py: RSI(14) asiri-satim stratejisinin GENEL +%6.718
ortalama net getirisi (276 islem) test edildi: t=7.694, p~0 (istatistiksel
hassasiyetin altinda) - KESINLIKLE anlamli, finansal backtest
standartlarinda ISTISNAI derecede guclu (t>3 zaten "guclu" sayilir).

Bugunku 8-9 denemenin (ORB, VWAP, MACD+MFI, Supertrend gun-ici/swing,
tema/momentum-etiketli) icinde ISTATISTIKSEL OLARAK ANLAMLI cikan ILK
ve TEK strateji. Momentum-grup hipotezinden BAGIMSIZ - RSI'in KENDISI
(basit, 30/70 esikleri, 90 gun maks tutma) yeterli.

DIKKAT/SINIRLAMA: TEK bir parametre seti (periyot=14, esikler=30/70,
maks_tutma=90) test edildi - asiri-optimize edilmis tek bir kombinasyon
olabilir mi, HENUZ bilinmiyor. Sonraki adim: parametre-saglamlik
kontrolu (farkli periyot/esik kombinasyonlarinda sonuc bozuluyor mu).

16) RSI PARAMETRE-SAGLAMLIK KONTROLU - GECTI, bugunun EN SAGLAM sonucu

9 kombinasyon (RSI periyot 10/14/21 x esikler 25-75/30-70/35-65),
TUM 30 sembol, 5 yil. SONUC: 9/9 kombinasyon POZITIF (hicbiri negatif
degil). Ayrica MANTIKLI bir ic tutarlilik var - sikilik arttikca
kalite artiyor (RSI21_25-75: 4 islem, isabet %75, ort net +%13.35;
RSI10_35-65: 1146 islem, isabet %37.2, ort net +%1.32 - hala pozitif
ama zayif). Bu, sinyal kalitesi/miktari odunlesmesi - RASTGELE
gurultunun degil, GERCEK bir piyasa fenomeninin imzasi.

DURUM: RSI asiri-satim tersine-donus (14/30/70, 90 gun maks tutma),
bugunku 9-10 denemenin ICINDE Pine'a gecmeyi dusunebilecegimiz ILK
GERCEK aday statusune ulasti - hem istatistiksel anlamli (t=7.69,
p~0) hem parametre-saglam (9/9 pozitif).

18) RSI vs XU100 BENCHMARK - onemli DUZELTME, bulgu MUTEVAZILASTI

rsi_vs_xu100_kiyas.py: HER RSI isleminin giris->cikis tarih araliginda
XU100'un (basit al-tut) ne kazandiracagi hesaplanip, ISLEM-BAZLI
eslestirilerek kiyaslandi (276 eslesme).

SONUC: RSI ort +%6.718, XU100 (AYNI donemler) ort +%4.862 - fark
yalniz +%1.856. RSI, islemlerin YALNIZCA %43.8'inde (121/276) XU100'u
GECTI - COGUNLUKTA (%56.2) basit al-tut DAHA IYI performans gosterdi.

YORUM: onceki "t=7.69, cok guclu" bulgunun BUYUK KISMI (yaklasik %72'si,
4.862/6.718) aslinda GENEL PIYASA YUKSELISINDEN (son 5 yilda BIST
zaten yukseldi) geliyormus. GERCEK strateji-ozgu katki (alpha) cok
daha MUTEVAZI (+1.86 puan ort, %43.8 ustunluk orani - yazi-turadan
bile dusuk).

KARAR: bu, Pine'a gecmek icin HENUZ yeterli guven vermiyor. RSI hala
en iyi aday ama "kanitlanmis edge" degil, "hafif umut verici,
temkinli izlenmesi gereken bir sinyal" statusunde. Sonraki adim:
GERCEK PARA OLMADAN gozlem/kagit-uzerinde-takip modu.

19) Bir sonraki oturum icin kontrol listesi
1. Haftalik Kirilim - W32 esik durumu ne?
2. Sektor-Baglamli Kirilim - POZITIF grup olustu mu?
3. arastirma_hedef_fiyat.json - yeni kayitlar eklendi mi, sembol_ozet()
   ile P1/P2 PF/WR karsilastirmasi anlamli bir sey gosteriyor mu?
4. hafta_denetim.py'nin "supheli fiyat" bolumu - yeni bir anomali
   yakaladi mi?
5. v112n'i TEKRAR denemek istenirse: TEK BASINA, izole test - baska
   hicbir Pine degisikligiyle BIRLESTIRMEDEN.
6. Bilanco takvimini genisletmek hala dusuk oncelikli (olay-tabanli
   payin kucuk cikmasi nedeniyle).
7. YENI: kullaniciyla "cok-gunlu katalizor-gudumlu swing" yon
   degisikligi konusuldu mu, karar verildi mi? Verildiyse, Faz 1
   (ufku 5-60 gune uzatma) baslatildi mi?
8. YENI: Supertrend+ADX tema-karsilastirma orneklemi genisletildi mi
   (13 islemden daha buyuk bir orneklem icin GUCLU/ZAYIF anlati
   ciftleri coğaltilip tekrar test edildi mi)?
9. YENI: anlati_teknik_capraz_referans.py tekrar kosuldu mu - T+10/
   T+20 doldu mu, BILINMIYOR grubu kuculdu mu (arastirma_hedef_fiyat.
   json genisledikce), GUCLU/ZAYIF orneklem buyudu mu?
