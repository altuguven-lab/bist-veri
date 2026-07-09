KULUCKA PROTOKOLU (IP-3) - RESMI
Baslangic: 07.07.2026 (ilk gercek sinyal gunu) | Bitis: 18.08.2026 (6 hafta)
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
