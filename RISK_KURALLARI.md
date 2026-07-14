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
