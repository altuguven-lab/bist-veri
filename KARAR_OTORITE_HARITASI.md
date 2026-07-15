# KARAR OTORITESI HARITASI - V151 IRE FOCUS
Karar O1 (14.07.2026) | Etiket: ALTYAPI-dokuman | Kod DEGISTIRILMEMISTIR.
Kaynak: V151_IRE_FOCUS_KURUMSAL_WEBHOOK (3.323 satir). Satir numaralari bu
kopyaya gore; kod degisirse harita ayni commit'te guncellenir.

## Amac
"Hangi katman otorite?" sorusunu bitirmek. Her degisiklik onerisi once bu
haritada HANGI katmana dokundugunu soyler; triyaj etiketi ona gore verilir.

## Karar zinciri (yukaridan asagi, her katman bir ustundekini TUKETIR)

KATMAN 0 - HAM SKOR
  ~281-282: _rawScore (puan toplami) -> _score clamp
  1416: score = f_clamp(scoreCalcRaw, stateFloor, scoreCeiling)
  1418-1426: sektorel tabanlar (math.max ile 42/48/44/25...)
  Otorite: skor DEGERINI yalnizca bu katman uretir.
  Not: stateFloor (1245-1256) sektor/rejime gore taban kaydirir -
  "skor neden dusmuyor" sorularinin cevabi genelde buradadir.

KATMAN 1 - YUMUSATILMIS SKOR (tek gercek: SON atama)
  1608: baslangic secimi (momentum/defansif/normal EMA'lari)
  1956 ve 2016: ara yeniden atamalar (kol bazli)
  2106: NIHAI deger = ta.ema(score + viopBonus, scoreSmLen)
  2107: f_clamp(stateFloor, scoreCeiling) - son soz clamp'indir
  KURAL: scoreSmoothed tuketen HICBIR katman 2107 oncesi degeri gormez;
  Pine sirali calisir, 2107 sonrasi okuyan herkes ayni degeri okur.
  Ara atamalarin varligi BAKIM riskidir, davranis riski degildir.
  (Yeniden adlandirma birikimde: O6 / MANTIK.)

KATMAN 2 - DURUM MAKINESI (_smState)
  2259-2260: var tanimlari (NEUTRAL baslangic)
  2286+: gecis kosullari (WATCH'a gecis, banka PREP bypass 2290...)
  Girdi: scoreSmoothed (katman 1), panik/sektor bayraklari.
  Otorite: "sistem hangi fazda" sorusunun TEK sahibi.

KATMAN 3 - NIHAI KARAR (_finalDecision)
  AL / TEYITLI AL / ERKEN AL / ADAY AL / IZLE / PAS GEC / CIK uretir.
  Girdi: katman 2 durumu + skor esikleri + risk bayraklari.
  Otorite: "islem karari" burada dogar; ama SON SOZ degildir (bkz. 4-5).

KATMAN 4 - YASAM DONGUSU (_v113Lifecycle, 2678+)
  _v112Entered -> "YENI AL", acik pozisyon -> "TUT", cikis -> "CIKIS".
  2716: _actionOverridden = lifecycle=="TUT" or portfolioPosition
  Otorite: pozisyon BAGLAMI karari GECERSIZ KILABILIR (AL'i IZLE'ye
  cevirir). 2551-2573 yorum blogu bu gecersiz kilmanin tarihcesidir
  (ASELS vakasi: ACTION=IZLE iken NOTE=ISLEM ADAYI tutarsizligi cozumu).

KATMAN 5 - PANEL ACTION (_kararTxt, 3025-3028)
  Girdi: katman 3+4 + _urgentExitRaw.
  Otorite: KULLANICININ GORDUGU son karar. CIK > TUT/IZLE > digerleri
  oncelik sirasi 3025'te kodludur.
  DIKKAT: panel gercek zamanlidir (724 yorumu) - bar icinde degisebilir.

KATMAN 6 - ALARM SINIFI (alertcondition, 3304-3322; 19 adet)
  _alarmP1/P2/P3 (424-428): finalDecision + saglik filtrelerinden turer.
  CORE seti (3285-3289): alertMode=="CORE" kapili 3 alarm.
  GUNLUK_OZET (3304): session.islastbar_regular - karar DEGIL, veri yayini.
  Otorite: dis dunyaya NE duyurulacagi. Karar uretmez, karar YAYINLAR.
  BILINEN UYUMSUZLUK (O4/O6): eski 14 alarm alertMode=="FULL" sartina
  bagli DEGIL -> CORE secilse de tanimli/ateslenebilir kalirlar.
  Metin duzeltmesi O4 (dogrulama sonrasi), davranis kapilamasi O6
  (kulucka sonrasi - ALARM SETI = OLCUM AYGITI, tuzuk eki C.4).

## Degisiklik-katman-etiket rehberi
- Katman 0-3'e dokunan her sey: MANTIK (kulucka: otomatik ret)
- Katman 4-5 gosterim mantigi: cogunlukla MANTIK; salt metin KOZMETIK
- Katman 6 alarm SETI/kosulu: kulucka boyunca MANTIK muamelesi (C.4)
- Katman 6 mesaj ICERIGI (yeni alan, tasiyici plot): ALTYAPI + dogrulama
- Plot ekleme: VARSAYILAN RET (tasiyicilar ilk 20'de kalmali - C.4)

## Bilinen riskler (birikim referanslari)
- 1680: stopMesafe = math.max(entry - stop, mintick) -> stop >= entry
  ise sessizce mintick'e sikisir, teorik lot buyur. Birikim ONCELIK-1
  (O5). Ara onlem: panel lot onerisi Anayasa Bolum 0 formulunun yerine
  GECMEZ; stop >= giris goruluyorsa oneri GECERSIZDIR.
- scoreSmoothed coklu atama (katman 1) - birikim O6.

