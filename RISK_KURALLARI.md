RISK KURALLARI (Risk Anayasasi)
> Bu belge sistemin degil, SENIN anayasandir. `[...]` alanlarini kendi sermaye
> buyuklugune ve risk istahina gore doldur; Claude degerleri ONERMEZ, yalnizca
> tutarlilik denetimi yapar ve brifingde ihlalleri raporlar. Doldurulunca bu
> notu silme - kurallarin kimin karari oldugu kayitta kalsin.
> Kurallarin degistirilmesi = bu dosyada commit. Sozlu/anlik istisna YOKTUR;
> istisna gerekiyorsa once kural degisir, sonra islem yapilir.
1. Pozisyon boyutu
Tek pozisyon azami buyuklugu: portfoyun %[...]'i
Ayni anda azami acik pozisyon sayisi: [...]
ERKEN AL / P2 sinyalleriyle acilan pozisyon, P1'in azami %[...]'i boyutunda olur
2. Konsantrasyon
Ayni sektorde azami pozisyon sayisi: [...]
Ayni sektorde azami toplam agirlik: %[...]
Bankacilik + holding toplami azami: %[...] (BIST korelasyon riski)
3. Zarar durdurma
Islem bazli: sistemin STOP seviyesi asilirsa pozisyon ayni gun kapatilir,
"toparlar" beklenmez. Azami islem zarari: %[...]
Gun bazli: portfoy gunluk %[...] eksiye gecerse o gun YENI GIRIS YOK
Hafta bazli: haftalik %[...] eksi sonrasi pozisyon boyutlari yariya iner
Ardisik [...] zararli islem sonrasi: [...] gun islem molasi + hafta kapanisi
denetimi beklenir
4. Sinyal disiplini
ACIL_CIK sinyaline azami tepki suresi: [...] dakika / bar
SINYALSIZ islem: [ayda azami ... adet | yasak]
SINYALE_RAGMEN islem (sistem cikis derken tutmak vb.): [yasak | yazili
gerekce ile islem gunlugune not dusulur]
KOVALAMA etiketi tasiyan girisler: [yasak | yari boyut]
5. Rejim kurallari
V195 REJIM = RISK OFF iken: yeni giris [yasak | yari boyut | serbest]
Makro panel MAKRO = OFF iken kaldiracli enstruman (VIOP): [...]
6. Denetim
Bu kurallarin ihlali brifingde "IHLAL" bolumu olarak raporlanir.
Hafta kapanisi denetimi, ihlal sayisini ve ihlalli islemlerin K/Z'sini
ayrica gosterir (ihlaller para kazandiriyorsa bile kural degisikligi
tartismasi hafta kapanisinda yapilir, islem aninda degil).
