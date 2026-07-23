RISK KURALLARI (Risk Anayasasi) - v2 TASLAK
> Bu belge sistemin degil, SENIN anayasandir. Asagidaki degerler
> 14.07.2026 tarihli dort-perspektif analiziyle (stratejist / broker /
> yazilimci / trader) TASLAK olarak onerildi; commit edildigi an
> kurallarin sahibi ve karari SANA aittir. Claude yalnizca tutarlilik
> denetimi yapar ve brifingde ihlalleri raporlar.
> Kurallarin degistirilmesi = bu dosyada commit. Sozlu/anlik istisna
> YOKTUR; istisna gerekiyorsa once kural degisir, sonra islem yapilir.
0. Boyutlama ilkesi (tum kurallarin temeli)
Pozisyon buyuklugu POZISYON YUZDESI ile degil, RISK ile tanimlanir:
    pozisyon_tutari = (portfoy_degeri x islem_riski) / stop_mesafesi_yuzde

Islem basina risk: portfoyun %1'i (stop calisirsa kaybedilecek tutar)
Sistemin STOP seviyesi boyutlamanin girdisidir; stop genisse pozisyon
otomatik kuculur.
1. Pozisyon boyutu
Tek pozisyon azami buyuklugu: portfoyun %10'u (risk-tabanli boyut daha
kucuk cikarsa kucuk olan gecerlidir)
Ayni anda azami acik pozisyon sayisi: 5
ERKEN AL / P2 sinyalleriyle acilan pozisyon, P1 boyutunun azami %50'si
KULUCKA MODU (18.08.2026'ya kadar): tum boyutlar yukaridakilerin
YARISI. Kulucka basariyla biterse ilk ay yari boyut zaten protokol
geregi; bu satir o gun guncellenir.
2. Konsantrasyon
Ayni sektorde azami pozisyon sayisi: 2
Ayni sektorde azami toplam agirlik: %30
Bankacilik + holding TOPLAMI azami: %40 (BIST korelasyon riski;
evrenin ~yarisi bu iki gruptadir, sinir bilincli olarak dusuktur)
3. Zarar durdurma (kademeli fren)
Islem bazli: sistemin STOP seviyesi asilirsa pozisyon AYNI GUN
kapatilir, "toparlar" beklenmez. Azami islem zarari: portfoyun %1'i
(bkz. Bolum 0; stop kaymasi/gap durumunda fiili zarar kaydedilir,
%1.5 ustu fiili zarar hafta kapanisinda ayrica incelenir)
Gun bazli: portfoy gunluk %-3'e gecerse o gun YENI GIRIS YOK
(acik pozisyonlar kendi stoplariyla yonetilir)
Hafta bazli: haftalik %-5 sonrasi yeni pozisyon boyutlari YARIYA iner,
normale donus bir sonraki hafta kapanisi denetimiyle
Ardisik 3 zararli islem sonrasi: 2 seans yeni giris molasi + mini
gozden gecirme notu (islem_gunlugu'ne "MOLA" kaydi)
4. Sinyal disiplini
ACIL_CIK sinyaline tepki: sinyal barini IZLEYEN barin kapanisina
kadar (15dk grafikte azami ~30dk), PIYASA EMRIYLE. Limit emirle
fiyat avcligi yapilmaz.
SINYALSIZ islem: KULUCKA BOYUNCA YASAK (M3 metrigi %80 sinyal-uyum
ister; her sinyalsiz islem deneyin kendisini bozar). Kulucka sonrasi
bu satir yeniden degerlendirilir.
SINYALE_RAGMEN islem: yazili gerekce ile islem gunlugune islenir,
6 haftalik kulucka penceresinde azami 2 adet (protokol esigiyle ayni)
KOVALAMA etiketi tasiyan girisler: YASAK (sinyal fiyatindan %2'den
fazla uzaklasmis giris "kovalama" sayilir ve etiketlenir)
5. Rejim kurallari
V195 REJIM = RISK OFF iken: yeni giris KULUCKADA YASAK; kulucka
sonrasi yari boyut olarak gevsetilebilir (hafta kapanisi verisiyle)
Makro panel MAKRO = OFF iken kaldiracli enstruman (VIOP): YASAK
TCMB/Fed karar gunleri: karar saatinden onceki 2 saat ve sonrasindaki
1 saat yeni giris yapilmaz (spread/volatilite penceresi)
6. Likidite (BIST gercegi)
Pozisyon tutari, sembolun son 20 seans ortalama gunluk TL hacminin
%1'ini asamaz (ince kagitlarda cikis maliyeti pozisyonun kendisidir)
7. Denetim ve veri sozlesmesi
Bu kurallarin ihlali brifingde "IHLAL" bolumu olarak raporlanir.
Hafta kapanisi denetimi, ihlal sayisini ve ihlalli islemlerin K/Z'sini
ayrica gosterir. Ihlaller para kazandiriyorsa bile kural degisikligi
tartismasi hafta kapanisinda yapilir, islem aninda degil.
Denetlenebilirlik icin veri gereksinimleri (sema v2):
portfoy.json'a eklenecek alanlar: "baslangic_sermaye_tl",
"nakit_tl" (gunluk/haftalik fren hesabi icin zorunlu)
islem_gunlugu.json islem kaydina eklenecek alanlar:
"kovalama": true/false, "stop_seviye_girisde": float
Hesaplanamayan kural = olmayan kural: yeni kural eklerken hangi
dosyadan hangi alanla denetlenecegi bu bolume islenir.
## 8. GECICI BOLUM - Miras Pozisyonlar (17.07.2026 milati)
Bu bolum, sistemin devreye girisinden ONCE acilmis pozisyonlarin
anayasaya gecis rejimini tanimlar. Kalici degildir; hedef tarihte
kendiliginden yururlukten kalkar ve dosyadan silinir.

8.1 TANIM: "MIRAS" etiketi, 17.07.2026 milatinda devralinan ve
    sinyal_etiketi=MIRAS olan pozisyonlari kapsar (AKBNK, KCHOL,
    TAVHL, YKBNK). Yeni pozisyon MIRAS etiketi ALAMAZ.

8.2 MUAF OLANLAR (yalnizca miras pozisyonlar icin):
    - Bolum 1 tek pozisyon tavani (%10)
    - Bolum 2 konsantrasyon tavanlari (sektor ve banka+holding)
    - Bolum 4 gecmis sinyal uyumu (milat oncesi sinyaller sorgulanmaz;
      islem gunlugune geriye donuk kayit girilmez, M3 etkilenmez)

8.3 MUAF OLMAYANLAR (milat aninda yururlukte):
    - STOP ZORUNLULUGU: her miras pozisyona 31.07.2026'ya kadar
      stop_seviye tanimlanir. Stop tanimlanmamis pozisyon 31.07.2026
      sonrasi dogrudan IHLAL olarak raporlanir.
    - MILAT SONRASI SINYALLER: bu tarihten itibaren gelen ACIL_CIK /
      POZ_AZALT sinyalleri miras pozisyonlar icin de Bolum 4 tepki
      kurallarina tabidir.
    - Gunluk/haftalik fren hesaplari (Bolum 3) milat ozkaynagi
      (2.857.000 TL) uzerinden tum portfoye uygulanir.
    - MIRAS pozisyona EKLEME yapilamaz (boyut buyutme = yeni giris
      sayilir ve tum kurallara tabidir).

8.4 UYUM TAKVIMI (Baskan doldurur; denetim bu takvime karsi raporlar):
    - 31.07.2026: tum miras pozisyonlarda stop tanimli
    - 24.07.2026: banka+holding birlesik agirlik <= % 50 ara hedefi
    - 07.08.2026: tam uyum (Bolum 1-2 tavanlari) veya bu bolumun
      gozden gecirilmis takvimle yeniden commit'i
    Denetim, ihlal yerine "MIRAS-UYUM" basligi altinda takvime gore
    ilerlemeyi raporlar; takvim asimi IHLAL'e doner.

8.5 SONA ERME: 07.08.2026'de bu bolum yururlukten kalkar; kalan
    uyumsuzluk o gunden itibaren standart IHLAL olarak raporlanir.

8.6 GECIS PENCERESI - Stop Kalibrasyonu (17.07 - 24.07.2026)
    Gerekce: milat stoplari 17.07'de tek seansta belirlendi; seviye
    kalitesi dogrulanmadi. Bu pencere SEVIYELERI olgunlastirmak icindir,
    stop DISIPLININI askiya almak icin degildir.
    - Stop revizyonu yalnizca KIRILMADAN ONCE yapilabilir; her revizyon
      commit + tek satir gerekce ister.
    - Kirilan stop TASINAMAZ: kirilma anindaki yururlukteki seviye
      baglar, Bolum 3 ayni-gun kapanis hukmu istisnasiz uygulanir.
    - 24.07.2026 kapanisinda pencere biter; o gunku seviyeler kalici
      sayilir, sonraki degisiklikler standart surece tabidir.
    - Kayit: 17.07 YKBNK vakasi IHLAL-1 olarak tutanakta KALIR; bu
      madde geriye yururlu af degildir.
## 9. P3_SKOR OLGUNLASMA DONEMI (deploy sonrasi, 27.07'den itibaren)
9.1 GEREKCE: P3_SKOR yeni bir sinyal SINIFI; canlida hic ateslenmedi,
    yalniz 2 geriye-donuk vekil vakasiyla (KCHOL, TUPRS) dogrulandi.
    Kulucka v2'nin kendi yari-boyut carpani (Bolum 1) otomatik
    uygulanir; bu bolum ONUN USTUNE ek bir olgunlasma katmani ekler.

9.2 KURAL: P3_SKOR_AL sinyaliyle acilan ilk 5 canli pozisyon, standart
    kulucka-yari boyutunun YARISIYLA (yani normal boyutun ceyregiyle)
    acilir. 5. pozisyon kapandiktan sonra standart kulucka-yari boyutuna
    gecilir.

9.3 SAYAC: P3_OLGUNLASMA_SAYAC, islem_gunlugu.json'da sinyal_etiketi=
    "P3_SKOR_AL" olan kapanmis islem sayisidir; 5'e ulasinca bu bolum
    o an itibariyla yururlukten kalkar (kendiliginden, yeniden commit
    gerekmez).

9.4 ISTISNA YOK: olgunlasma sayaci P3_SKOR'un kendi kulucka v2
    penceresine bagli degildir - deploy tarihinden itibaren, sinyal
    sayisina gore isler.
