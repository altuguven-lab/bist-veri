# IP-4: P3_DEVAM MODULU TASARIMI (Trend-Ici Giris)
Statu: TASLAK v0.1 | Karar: Baskan, 18.07.2026 (acil istisna - B yolu)
Anayasal cerceve: Tasarim/golge dogrulama sayaci YAKMAZ. Sayac, modulun
V151'e deploy edildigi gun sifirlanir ve Kulucka v2 (42 gun) baslar.
Risk Subayi sartli olumlu gorusu tutanakta (4 sart: parametre kaydi
once, deploy PPK disi, tek-input geri alma, dogrulama kapisi).

## 1. Gerekce (veri dosyasi)
- Retro (01.06-18.07): 81 firsat penceresi; kuluckada 13/13 SINYALSIZ.
- Golge Katman B: gecis-tetikli iskelet ayni donemde ~0 uretim -
  sorun esik degil, giris SINIFI. Trend Haziran basinda dogdu;
  firsatlar trend-ICI. Sistemin bu sinif icin organi yok.
- IP-1 karakteri dogrulandi: sigorta guclu (M1 2/2), prim trend-ici
  kacirmalarla odeniyor (KF: EREGL +9.1, TUPRS +7.8 ...).

## 2. Sinyal anatomisi - P3_DEVAM_AL
Uc asama + dort bekci. TUM esikler Bolum 5'teki parametre kaydindan.

BAGLAM (trend canli mi?):
  B1. EMA dizilimi KURULU ve KALICI: e9>e21>e50 son [pKalicilikBar]
      bardir araliksiz (gecis ANI degil - suredurum).
  B2. Fiyat > e50 ve rejim != RISK-OFF (g1RejimKod >= 1).
  B3. Skor tabani: scoreSmoothed >= [pSkorTaban]
      (deger Katman A verisiyle kalibre edilecek - bkz. Bolum 6).
  B4. DNA sinifi izinli (MOMENTUM/KURUMSAL; DEFENSIVE haric - tartisilir).

KURULUM (saglikli geri cekilme):
  K1. Fiyat e21'e temas/yaklasma: dusuk <= e21 * (1 + [pTemasBandi]).
  K2. Geri cekilme derinligi son salinim yuksekliginin
      [pAzamiDerinlik]'ini asmaz (V-tuzagi ayirici).
  K3. Geri cekilme bacaklarinda hacim SONER: relvol < [pSonumEsik]
      (satis baskisi degil kar realizasyonu ayirici).

TETIK (devam kaniti):
  T1. Bar KAPANISI e9 uzerine doner VE kurulum penceresinin en
      yuksegi asilir.
  T2. Tetik barinda hacim GENISLER: relvol >= [pTetikHacim].
  T3. barstate.isconfirmed sarti (intrabar tetik YOK - alarm
      katmaninda da "bar kapanisinda bir kez").

BEKCILER (mevcut mimariden yeniden kullanim):
  G1. KOVALAMA: giris fiyati tetik seviyesinden [pKovalamaBant]'tan
      uzaksa sinyal IPTAL (mevcut blok mantigi yeniden kullanilir).
  G2. SOGUMA: ayni sembolde ACIL_CIK sonrasi [pSogumaBar] bar
      gecmeden P3 uretilmez (IP-1 V-tuzagi dersi; M5 verisi besler).
  G3. STOP MESAFESI: stop = max(kurulum dibi, e50). Stop mesafesi
      [pAzamiStopYuzde]'yi asarsa sinyal uretilmez (boyutlanamayan
      islem onerilmez - Anayasa Bolum 0 uyumu).
  G4. GUNLUK TAVAN: sembol basina gunde azami 1 P3 (alarm yuku).

## 3. Mimari kararlar
- PARALEL HAT: P3, mevcut P1/P2 zincirine ve durum makinesine
  DOKUNMAZ - bagimsiz hesaplanir, ayri alertcondition ile yayinlanir.
  Gerekce: regresyon yuzeyini kucultmek + eski sinyallerin olcum
  surekliligini korumak (M1/M2 kiyaslanabilir kalir).
- ANA SALTER: p3Enabled input (varsayilan true). Geri alma = input
  kapatma; kod degisikligi/alarm yeniden kurulumu gerektirmez.
- BUTCE: V151 statement tavani ~1.138/1.145. Modul butcesi azami
  [~40] statement. ONKOSUL: V112 olu kod temizliginden en az bu
  kadar yer acilmasi (K7 raporu). Yeni plot YOK (tasiyici gerekmez;
  mesaj mevcut 5 tasiyiciyi kullanir). Yeni alertcondition: 1 adet
  (P3_DEVAM_AL, const string, G1 alan setiyle ayni format).
- OTORITE HARITASI guncellemesi ayni commit'te (yeni paralel hat
  katman 6'ya nasil baglaniyor).

## 4. Olcum plani
- YENI METRIK M2D: P3 sinyallerinin T+3 isabeti (kapanis > giris),
  esik: > %55 (M2 ile ayni dil, ayri havuz - eski/yeni karisMAZ).
- M5 baglantisi: G2 soguma parametresi M5 medyaniyla haftalik
  karsilastirilir.
- Kacan Firsat bolumu P3 sonrasi "yakalanan/kacan" kirilimi ekler.

## 5. Parametre kaydi (ASIRI UYUM KAPISI)
Kural: Asagidaki araliklar backtest ONCESI donduruldu. Dogrulama
kosumlari YALNIZ bu araliklari tarayabilir; aralik disi deger
denenmez, denenirse sonuc gecersizdir. Nihai degerler tek commit'le
secilir ve kulucka v2 boyunca donuktur.
  pKalicilikBar:   [5..15]     baslangic 8
  pSkorTaban:      [25..45]    baslangic Katman A Carsamba verisi
  pTemasBandi:     [%0.2..1.0] baslangic %0.5
  pAzamiDerinlik:  [%38..%62]  baslangic %50 (salinim orani)
  pSonumEsik:      [0.7..1.0]  baslangic 0.9
  pTetikHacim:     [1.1..1.5]  baslangic 1.2
  pKovalamaBant:   [%1..%2]    baslangic %1.5 (anayasa %2 tavani icinde)
  pSogumaBar:      [10..40]    baslangic 20 (15dk bar; ~1 seans)
  pAzamiStopYuzde: [%2..%5]    baslangic %4

## 6. Dogrulama kapisi (deploy on kosullari - HEPSI sart)
  D1. Golge Katman C (gunluk vekil, 01.06-bugun): P3 vekili kulucka
      penceresindeki 13 firsatin >= [%50]'sini yakalar VE vekil T+3
      isabeti >= %55.
  D2. Katman A skor bandi (Carsamba tamamlanir): pSkorTaban secimi
      gercek skor-getiri verisine dayanir, varsayimla degil.
  D3. Test Muhendisi protokolu: Pine derleme + statement sayimi +
      alarm/webhook uctan uca GERCEK_TEST + placeholder dogrulama.
  D4. Deploy gunu PPK penceresi disinda (23.07 haftasi degil).
D1 veya D2 gecilemezse tasarim REVIZE edilir, deploy edilmez -
"nasilsa karar verildi" gerekcesiyle kapi atlanamaz.

## 7. Takvim (hedef)
  18-19.07 (hafta sonu): Katman C vekil kosumu (ALTYAPI, sayac guvenli)
  20.07 Pzt: Kalibrasyon oturumu - Katman C + KCHOL T+3 sonuclari
  22.07 Car: Katman A tam veri -> pSkorTaban kalibrasyonu
  23.07 Per: PPK - kod isi YOK (24.07 azaltim plani ayrica yuruyor)
  24-26.07: Pine uygulamasi + V112 yer acma + test protokolu
  27.07 Pzt hedef: DEPLOY -> sayac sifirlanir, KULUCKA v2 baslar
  Yeni hukum gunu: ~07.09.2026 (deploy + 42 gun)
  Not: 18.08 eski hukum gunu IPTAL olur; birikimdeki diger maddeler
  kulucka v2 sonuna ertelenir (Urun Stratejisti yeniden onceliklendirir).

## 8. Acik sorular (Pazartesi oturumuna)
  A1. DEFENSIVE DNA'ya P3 izni verilsin mi? (banka mean-reversion
      moduyla etkilesim)
  A2. P3 kulucka v2'de yari boyut mu tam boyut mu? (Anayasa 1.
      bolum kulucka carpani zaten yari - ek indirim gerekli mi)
  A3. KCHOL-50.6 / TUPRS-97 vakalari ic tikaniklik da gosterirse
      (katman 2-4), o duzeltme bu pakete dahil mi ayri mi?

