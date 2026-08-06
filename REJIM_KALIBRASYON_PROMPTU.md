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
Gun-ici alim-satim (ORB/VWAP) - KARAR: ASKIYA ALINDI
5 deneme (ORB v1/v2/v3-grid, VWAP v1/v2), hicbiri pozitife gecmedi.
En iyi: ORB v3, AKBNK/KCHOL, hacim=1.8/rtr=3.0/stop_oran=1.0,
ort net getiri %-0.076 (hala eksi). Proje suresiz ASKIYA ALINDI.
6) Bir sonraki oturum icin kontrol listesi
Haftalik Kirilim - W32 esik durumu ne?
Sektor-Baglamli Kirilim - POZITIF grup olustu mu?
arastirma_hedef_fiyat.json - yeni kayitlar eklendi mi, sembol_ozet()
ile P1/P2 PF/WR karsilastirmasi anlamli bir sey gosteriyor mu?
hafta_denetim.py'nin "supheli fiyat" bolumu - yeni bir anomali
yakaladi mi?
v112n'i TEKRAR denemek istenirse: TEK BASINA, izole test - baska
hicbir Pine degisikligiyle BIRLESTIRMEDEN.
Bilanco takvimini genisletmek hala dusuk oncelikli (olay-tabanli
payin kucuk cikmasi nedeniyle).
