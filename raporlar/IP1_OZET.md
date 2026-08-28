IP-1 OLAY PENCERESI CALISMASI - KOMITE OZETI
Tarih: 09.07.2026 | Veri: data/backtest/olay_penceresi_sonuc.json
Nitelik: Rejim-davranis haritasi. GETIRI IDDIASI DEGILDIR.
Yontem ve sinirlar
15dk canli sistemin (V151/V195) gunluk bara cevrilebilen cekirdek iskeleti
(EMA 9/21/50 dizilimi + hacim teyitli cikis + genislik) 2023 sonrasi bes
kritik epizotta test edildi. Evren: 2023'te de likit 10 buyuk hisse
(point-in-time savunulabilirlik; bugunku 30'luk evren KULLANILMADI).
Parametreler calisma icin ayarlanmadi. Gunluk iskelette V151'in ADX/KGS/
seans-ici katmanlari YOKTUR - sonuclar gercek sistemin ALT SINIRI sayilmali.
Bilinen metrik kusuru: pencere_max_drawdown alani kronolojik degil min/max
oranidir (E1'deki -39 dusus degil, dip-once-zirve-sonra artefakti);
strateji/al-tut MaxDD degerleri kumulatif seriden ve dogrudur.
Karne (vekil strateji: rejim ON=endeks, OFF=nakit, 1 gun gecikmeli)
Epizot	Getiri v/BH	MaxDD v/BH	Davranis
E1 Secim+Simsek 2023	+47.7 / +60.2	-7.8 / -8.7	Secim cokusune OFF girdi; 31 May ON (Simsek'ten 4 gun once)
E2 Yaz rallisi 2023	+30.4 / +24.9	-7.9 / -12.8	Ralli boyunca sifir flip; zirve+%8'de cikis, Ekim'i disarida izledi
E3 Yerel secim 2024	-0.9 / +9.9	-14.0 / -7.0	1 ayda 6 flip - TESTERE. Tek kirmizi karne
E4 Mart 2025 soku	-4.8 / -3.0	-10.7 / -16.7	Sokun GUNU OFF; dip 2 gun sonra %8 asagidaydi
E5 Iran savasi 2025	+0.8 / +12.6	-7.9 / -6.8	V-donus tuzagi: panik ortasi cikis, toparlanma sonrasi donus
Karakter bulgulari
TREND = ANA VATAN: E2'de al-tut getiride VE dususte yenildi.
SOK KORUMASI GERCEK: Iki siyasi sokta da ayni-gun/ertesi-gun kacis;
ACIL_CIK vekilleri dogru gunlerde kume halinde atesledi (15-17 May 2023,
19-21 Mar 2025). 08.07.2026 canli cifte ACIL_CIK bu desenin ikizi.
ZAAF #1 - OLAY ONCESI TESTERE (E3): yatay-gergin bekleyis piyasasi en
kotu rejim; flip maliyeti getiriyi ve dususu birlikte bozuyor.
ZAAF #2 - V-DONUS TUZAGI (E5): hizli panik+hizli toparlanmada cikis dibe
yakin, donus gec.
Hukum
Sistem bir SIGORTALI GETIRI urunu: primi trend baslangiclarindaki gec donus
ve testere donemlerinde oder; tazminati cokus gunlerinde alir. 5 epizotun
4'unde MaxDD belirgin dusuk. Ham getiri kiyasinda al-tut onde - pencereler
bilerek sok/ralli etrafinda secildigi ve iskelet 15dk sistemin altkumesi
oldugu icin bu beklenen sonuctur.
Kararlar
K1. Kulucka (IP-3) kirmizi metrikleri kanitla secildi: aylik flip sayisi ve
yeniden-giris gecikmesi. Hafta kapanisi denetimine eklenir.
K2. Rejim ON donusunde 2-bar teyit fikri NOT EDILDI; kulucka SIRASINDA
uygulanmaz (parametre degisikligi = kulucka sifirlanir).
K3. "Gecmiste kazanirdi" hicbir zaman pozisyon gerekcesi degildir; gerekce
yalnizca "su an sinyal var + risk anayasasi izin veriyor" olabilir.
