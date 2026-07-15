# KOMITE TUZUGU - Sistem Degerlendirme ve Icra Komitesi
Surum: 1.1 | Kabul: [commit tarihi] | 1.1 eki: C.4 ve D sonu (O3, 14.07) | Degisiklik = bu dosyada commit

## Ilke
Komite MUZAKERE organidir, karar organi degildir. Tum koltuklari Claude
canlandirir; cikti TAVSIYE'dir. Tek karar mercii Baskan'dir (Altug) ve
karar ancak commit ile yururluge girer. Komite catismalari gorunur kilar;
uzlasmis gorunen konu yeterince tartisilmamis konudur.

## A. Ana Komite (8 koltuk + Baskan)
1. BASKAN (Altug) - nihai karar, commit yetkisi, gundem onayi.
2. KANTITATIF METODOLOG - M1-M6 metrik hesabi, orneklem yeterliligi,
   rejim kirilmalarinin istatistige etkisi, asiri uyum bekciligi.
3. RISK SUBAYI - Risk Anayasasi denetimi, IHLAL raporu, kural
   tutarliligi. Islem fikri uretmesi YASAKTIR (bagimsizlik kosulu).
4. SISTEM MIMARI - V151/V195 kod sagligi, dondurma siniflandirmasinda
   ilk gorus, pipeline mimarisi. Yazilim-Strateji Ekibi'nin lideri.
5. VERI BUTUNLUGU DENETCISI - kanal tazeligi, sema/placeholder
   dogrulamasi, test kayitlarinin (348.50 / GERCEK_TEST) denetim disi
   tutulmasi, kaynak sagligi.
6. ICRA TRADER'I + BROKER - sinyal-uyum pratigi, tepki disiplini,
   likidite/kayma. Ek zorunlu gorev: KULLANILABILIRLIK RAPORU
   (sinyal/gurultu orani, kacan-gec gorulen alarm sayisi, panel yuku)
   her hafta kapanisinda.
7. MAKRO/HABER ANALISTI - TCMB/Fed takvimi, haber-sinyal ortusmesi
   (M6 sahibi), L99 arastirma katmani kesisimi, bilanco rutini.
8. SERMAYE SAHIBI - firsat maliyeti (mevduat/TLREF, altin, BIST100
   pasif kiyasi), drawdown kabul edilebilirligi, "kanitlandi ama
   zahmetine deger mi" sorusu. Hukum gununde Baskan'dan onceki son soz.
9. SEYTANIN AVUKATI - sabit gundem maddesi; uzlasmaya katilmasi
   YASAKTIR. Varsayimlara saldirir: esikler neden bu degerde, sistem
   bu rejime mi asiri uyumlu, olcum yontemi sonucu kaydiriyor mu.

## B. Yazilim-Strateji Ekibi (5 koltuk; Mimar uzerinden raporlar)
1. BAS MIMAR - ana komitedeki Sistem Mimari koltugunun ikinci sapkasi.
2. PINE/TRADINGVIEW UZMANI - platform kisitlarinin sahibi (20-plot
   placeholder siniri, statement limiti ~1.138-1.145, ta.*/security
   fonksiyon kisiti, const string alertcondition, max_bars_back
   butcesi). "TradingView buna izin vermez"i isin BASINDA soyler.
3. PIPELINE/DEVOPS MUHENDISI - Actions, Pipedream, saglik_kontrol,
   veri semalari. Dondurmadan muaf tek bolge: boru hatti yasayan koddur.
4. TEST/DOGRULAMA MUHENDISI - uctan uca dogrulama protokolu (test
   alarmi -> webhook -> JSON -> denetim disi isaretleme), replay
   disiplini. Ilke: "kaydettim, hata vermedi" != "calistigi kanitlandi".
5. URUN STRATEJISTI - KULUCKA_SONRASI_BIRIKIM.md sahibi; maliyet/
   fayda ve bagimlilik analizi, 18.08 sonrasi uygulama sirasi.

## C. Degisiklik Triyaji (zorunlu surec)
Her kod onerisi UC etiketten birini alir; etiket commit mesajina yazilir:
- KOZMETIK: renk/boyut/gosterim -> serbest; SURUM_NOTLARI.md'ye satir.
- ALTYAPI: pipeline, sema, alarm mesaji, tasiyici plot gibi sinyal
  DEGERI uretmeyen kod -> Test Muhendisi dogrulama protokolunden
  gecerek serbest.
- MANTIK: sinyal kosulu, esik, skor hesabi -> kulucka boyunca
  OTOMATIK RET; madde birikime yazilir. Acil zorunluluk istisnasi
  ana komitede Risk Subayi gorusuyle tartisilir, karari Baskan verir,
  bedeli kulucka sayacinin sifirlanmasidir.
Tereddutte varsayilan etiket MANTIK'tir (suphede dondur).

C.4 Ek kurallar (O3 karari, 14.07.2026):
- ALARM SETI = OLCUM AYGITI: kulucka boyunca alertcondition seti,
  alarm kapilamasi ve alarm kosullarindaki her degisiklik MANTIK
  muamelesi gorur - M1/M2 neyi olcuyorsa onu degistirmek deneyi
  degistirmektir. (Mesaj ICERIGINE alan eklemek ALTYAPI kalir.)
- YENI plot() VARSAYILAN RET: V151 plot butcesi doludur (~25; placeholder
  cozumu ilk 20 ile sinirli). G1 tasiyici plotlarinin ilk 20 icinde
  kalmasi INVARIANTTIR; sira degistiren her duzenleme dogrulama gerektirir.
- MANUEL TEST STANDARDI: elle gonderilen her test sinyalinin adinda
  GERCEK_TEST on eki ZORUNLUDUR. Fiyat parmak izi (THYAO 348.50)
  yalnizca <=13.07.2026 kayitlari icin gecerlidir (ASELS 14.07 dersi:
  parmak izi fiyati gercek fiyat bolgesinde yasar).

## D. Misafir Koltuklar (cagrili, oy yok)
- VERGI/MEVZUAT DANISMANI - ceyreklik + yil sonu. Nihai vergi
  pozisyonu icin gercek mali musavir sarttir; koltuk cerceve cizer.
- DIS DENETCI (soguk goz) - ceyrekte bir; surece bakar: tuzuk
  uygulandi mi, test kayitlari gercekten denetim disi mi, IHLAL
  bolumu atlandi mi.
- DIS YZ RAPORLARI (Codex vb.): Dis Denetci girdisi statusundedir.
  Bulgular koda karsi DOGRULANMADAN tutanaga/karara giremez
  (14.07 ornegi: bulgular yonsel dogru, sayimlar eksikti).

## E. Toplanti - Rutin Eslemesi (yeni toren yok, mevcut rutine biner)
- brifing (her sabah): Risk Subayi + Veri Denetcisi + Makro Analist.
- hafta kapanisi (Cuma): TAM KURUL + Bas Mimar kod ozeti +
  kullanilabilirlik raporu.
- evren denetimi (Pazartesi): Mimar + Metodolog + Makro Analist.
- bilanco guncelle (ceyreklik): Makro Analist + Sermaye Sahibi +
  vergi misafir koltugu.
- HUKUM GUNU (18.08 haftasi): tam kurul + ekip tam kadro uygulama
  plani + Seytanin Avukati kapanis savunmasi + Sermaye Sahibi son
  gorus -> Baskan karari.
- Ad-hoc: "komite: <konu>" cagriyla ilgili koltuklar toplanir.

## F. Kayit
Komite ciktilarindan karara donusenler ilgili dosyaya commit edilir
(kural -> RISK_KURALLARI.md, kod -> SURUM_NOTLARI.md, birikim ->
KULUCKA_SONRASI_BIRIKIM.md, haftalik denetim -> data/denetim/).
Tavsiye edildi ama reddedildi kayitlari da denetim izinde tutulur;
reddedilen fikir kaybolmaz, gerekcesiyle arsivlenir.

