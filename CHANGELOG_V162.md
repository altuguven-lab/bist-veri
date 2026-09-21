# CHANGELOG — V162.1c BIST IRE FOCUS

Bu dosya, Pine kodundaki token bütçesini (80.000 sınır) korumak için koddan çıkarılan uzun denetim/gerekçe yorumlarını içerir. Her madde, Pine dosyasındaki kısa `[CLxxx]` referans etiketiyle eşleşir.

---

## [CL001] @version=5

```
//@version=5
// ============================================================
// V162.1 YAMA (17.09.2026, kurul onayli istisna karari):
// Harici kod incelemesinde bulunan, dogrulanan uc kritik/orta oncelikli
// hata duzeltmesi. Kuluçka Protokolu MANTIK-freeze'i teknik olarak devam
// etse de (19.09 hukum gunu), bunlar "iyilestirme onerisi" degil "niyet
// edilenin calismamasi" turunde hata duzeltmesi oldugu icin B1-B6
// birikiminden AYRI, istisna maddesi kapsaminda simdi uygulandi:
//   1) _hardExitBreak: 'stop' (her barda yeniden hesaplanan deger) yerine
//      _stopPrice (dondurulmus/takip eden gercek pozisyon stopu) kullanildi
//      - onceki hali matematiksel olarak HER ZAMAN false donuyordu (olu kod)
//   2) P3_SKOR_AL'e _newEntryMode kontrolu eklendi (elde pozisyon varken
//      yeniden AL sinyali uretilmesin)
//   3) P3 gunluk tekillik anahtari dayofmonth'tan tam tarih kimligine
//      (year*10000+month*100+day) gecirildi (ay sinirini asan yanlis-engel
//      riski giderildi)
// KARAR MANTIGINA baska hicbir yerde DOKUNULMADI. B1-B6 (KULUCKA SONRASI
// BIRIKIM) ayri, sirayla ele alinacak.
// ============================================================
// V162.1 EK - B1 CIFTE-KAPI SADELESTIRME [DENEYSEL - dış kurul incelemesi
// madde 12: bu backtest GUNLUK BAR/yuzdelik-esik kanitina dayaniyor.
// KGS-entryScore korelasyonunun yuksek cikmasi zaten BEKLENEN bir sonuc
// (entryScore KGS'yi zaten iceriyor) - TEK BASINA kalici basari sayilmaz.
// 15 dakikalik GERCEK walk-forward/OOS sonuclari gelmeden (dusuk-KGS'li
// yeni islemlerin MAE'si, kuyruk kayiplari, islem-maliyeti-sonrasi
// expectancy, ayni-gun/sembol korelasyonu, gercek fill, max drawdown)
// DENEY BAYRAGIYLA izlenmeli.] (17.09.2026, kurul onayli istisna,
// Faz V0+V1 backtest kanitiyla): corr(KGS, entryScoreBase)=0.963 (30/30
// sembol, 0.953-0.969 bandi, data/backtest/kgs_gunluk_port_sonuc.json) ve
// gunluk-bar yuzdelik-esik backtesti (data/backtest/b1_esik_revizyon_sonuc.json)
// gosterdi ki: "_entryScore >= X and _kgs >= Y" seklindeki 8 AYRI kapida
// (asagida "17.09 B1" etiketli) KGS'yi AYRICA zorunlu tutmak isabet/getiri
// KAZANDIRMIYOR (T+3 %53.0 vs %53.2, T+10 %56.3 vs %56.5 - pratikte esit)
// ama sinyal hacmini ~%14 daraltiyor (12.877 vs 14.712 gun). Bu 8 kapida
// "and _kgs >= Y" / "and _kgs > Y" kosulu KALDIRILDI - entryScore zaten
// KGS'yi %38 agirlikla tasidigi icin bilgi kaybi yok, sadece mukerrerlik
// gitti. DOKUNULMAYANLAR (bilerek): _windowCandidate'in tek basina kgs>=70
// sarti (entryScore esdegeri yok, mukerrer degil), _kgsLotMult (lot
// boyutlandirma, ayri amac), _reloadQualityScore kgs kademeleri (ayri
// kompozit), _leadScore esikleri (test edilmedi, DOKUNULMADI).
// DURUSTLUK NOTU: kanit GUNLUK BAR yaklasikligi + yuzdelik-esik kaba
// karsiligi uzerinden - 15dk gercek veriyle henuz teyit edilmedi.
// V162.1 EK2 - B3 KOVALAMA KADEMELEME (17.09.2026, kurul onayli istisna,
// backtest kaniti data/backtest/b3_kovalama_kacirdi_sonuc.json): backlog'un
// kendi kriteri (KACIRDI T+3 isabet >%55) test edildi, GECTI (%55.1 genel;
// kademeli: 1.5-3.0%=%54.6, 3.0-6.0%=%56.2, 6.0%+=%54.0 - ilk iki kademe
// TAM ALINDI grubundan (%55.6) FARKSIZ). Sonuc: _p3Kovalama TEK ESIKLI TAM
// VETO'dan (pKovalamaPct=%1.5 ustu) İKİ KADEMELİ yapiya gecirildi -
// _p3KovalamaTamVeto (yalniz %6.0 ustu, veto DEVAM), _p3KovalamaYariBoyut
// (%1.5-6.0 arasi, ARTIK VETO EDILMIYOR, P3Ozet'e "yariBoyut" biti
// eklenerek isaretleniyor - gercek boyut karari downstream/portfoy
// tarafina birakildi, Pine yalniz ISARETLIYOR).
// V162.1 EK3 - B4 WR DONEM (ERA) AYRIMI (17.09.2026, kurul onayli istisna):
// f_perfBucket sayaclari (_trendWr/_yatayWr/_dususWr) BASLANGICTAN beri hic
// sifirlanmiyordu - 08.07 hacim tabani degisiminden once/sonraki islemler
// AYNI sayacta karisiyordu (Madde 10). Zaten var olan OOS-ayrimi deseniyle
// (devEndDate/_entryTimeMs) ESKI/YENI donem etiketli CIFT sayac eklendi.
// regimeHistMult'u besleyen _curRegimeN/_curRegimeWr ARTIK YALNIZ YENI
// donemi (hacimEraTarihi sonrasi, varsayilan 08.07.2026) kullaniyor - eski
// donem ARSIVLENDI (referans icin _trendEskiN vb. duruyor, karara GIRMIYOR).
// V0 KAPSAMI: yalniz canli karar besleyen 3 bucket duzeltildi; sektor/hacim/
// faktor/seans bucket'lari (yalniz panel, karar beslemiyor) BILEREK
// dokunulmadi, ayri B-maddesi olabilir.
// V162.1 EK4 - B6 REJIM ON 2-BAR TEYIDI [DENEYSEL - dış kurul incelemesi
// madde 12: bu YALNIZ gorsel/istatistiksel bir filtre DEGIL - teyitli
// rejim regimeHistMult uzerinden GERCEK lot buyuklugunu etkiliyor, yani
// davranis-notr degil. Ham VE teyitli rejim ayri ayri saklanip hangisinin
// daha iyi tahmin gucu oldugu (flip sayisi azaldi mi, sinyal gecikmesi
// asiri artti mi, max ters hareket/net getiri/PF en az korundu mu, lot
// kesintileri daha kararli mi) OLCULMEDEN kalici kabul edilmemeli.]
// (17.09.2026, kurul onayli istisna,
// İP-1 K2 "E3 testere" bulgusuna dayanarak): regimeTag (trendUp/trendDown'dan
// turetilen HAM etiket) tek barda flip edebiliyor, "testere" gibi cirpiniyor.
// trendUp/trendDown'IN KENDISINE DOKUNULMADI (40+ yerde kullaniliyor).
// Bunun yerine regimeTagConfirmed EKLENDI: ham okuma 2 ardisik barda AYNIYSA
// yeni rejime GECILIR, degilse ONCEKI TEYITLI rejim KORUNUR. B4'un WR
// kovalarini VE regimeHistMult'u besleyen _curRegimeN/_curRegimeWr artik
// regimeTagConfirmed kullaniyor - amac flip sayisini azaltip istatistiklerin
// gurultu yerine gercek rejimi olcmesi. Backtest ONCESI dogrudan uygulandi
// (B4 ile ayni WR-bucket mekanizmasina dogal ek oldugu icin, B1/B3 gibi ayri
// bir on-test gerektirmedi - degisiklik davranis-notru bir gecikme/sticky
// filtre, yeni bir esik/agirlik DEGIL).
// V162.2 EK - ISLEM PLANI YAMASI (17.09.2026, kurul onayli istisna, harici
// kod incelemesinden 3 madde): (1) SINYAL ANI DONDURMA - _entryPrice/
// _tradeEntryForTP/_tp1Level/_tp2Level/_stopPrice ZATEN VARDI (sinyal aninda
// donuyordu) ama PANEL bunlari KULLANMIYORDU, hala her barda close/atr'den
// yeniden hesaplanan stop/tp1/tp2'yi gosteriyordu - panel/metin hucreleri
// artik pozisyon ACIKKEN donmus degerleri gosteriyor. (2) TETIK-HEDEF
// CELISKISI - ASTOR ornegi (tetik direnc uzerinden, hedefler guncel
// kapanistan - hedefler tetigin ALTINDA kalabiliyordu): _planTp1/_planTp2
// artik _planTrigger (veya guncel kapanis, hangisi yuksekse) uzerinden
// hesaplaniyor, yalniz pozisyon YOKKEN/aday asamada. (3) BIST TICK
// YUVARLAMA - f_bistTick/f_roundDownToTick ZATEN VARDI (yalniz limit-fiyat
// hesaplarinda kullaniliyordu), f_bistRound eklendi, webhook'a giden
// _wStop ve panel STOP/TP1/TP2 ciktilarina uygulandi (eskiden 254,37 gibi
// BIST'te gercekte islem gormeyen fiyatlar gidebiliyordu).
// KAPSAM NOTU: rr1Ratio/rr2Ratio, _gbmTp2Txt panelleri ve lot-boyutlandirma
// (stopMesafe/baseLot) HAM (yuvarlanmamis/dinamik) degerlerle calismaya
// devam ediyor - bunlar surekli risk hesabi icin BILEREK degistirilmedi,
// yalniz NIHAI GORUNTU/webhook ciktisi duzeltildi.
// V162.2 EK2 - SELL KILIDI DUZELTMESI (17.09.2026, kurul onayli istisna,
// harici kod incelemesi "Yuksek oncelikli sorunlar" maddesi, dogrulandi):
// SELL'den cikisin TEK yolu skorun 30 ALTINA DUSMESIYDI - kurtulmak icin
// once DAHA KOTULESMESI gerekiyordu, skor 30 UZERINDE toparlansa bile
// _smToBuy/_smToHold PREP/BUY sart kostugu icin SELL'de KILITLI kaliyordu.
// _smSellRecovery EKLENDI: minimum 5-bar cooldown + skor>=40 (gercek
// toparlanma esigi) + fiyat EMA9/EMA21 ustune dondu + hicbir acil-cikis
// aktif degil -> SELL bu durumda da NEUTRAL'e cikiyor (dogrudan BUY/HOLD/
// WATCH'a ATLAMIYOR - raporun onerdigi "cikis olayi + cooldown" tasarimi,
// NEUTRAL->PREP->BUY dogal yoluyla devam eder).
// V162.2 EK3 - ALARM KAPANIS TEYIDI (17.09.2026, kurul onayli istisna,
// harici kod incelemesi dogrulandi): sistematik tarama yapildi - 22
// alertcondition'in altindaki tetikleyicilerden 16'sinda (13'u canAlert
// ortak kapisi uzerinden, 3'u CORE alarmlari ayri) barstate.isconfirmed
// EKSIKTI, "Once Per Bar" secilirse bar kapanmadan intrabar deger
// tetikleyebilirlerdi. canAlert'e (13 alarmin ortak kapisi) VE
// coreBuyAlert/coreWatchAlert/coreExitAlert'e (canAlert'e bagli degiller,
// ayrica) barstate.isconfirmed eklendi. P3_SKOR_AL (_p3Al, _p3Tetik
// uzerinden) zaten vardi, GERCEK STOP KIRILDI (_gStopKirildi) BILEREK
// degistirilmedi - raporun kendi istisnasi, risk yonetimi geciktirilmemeli.
// V162.1b - DIS KURUL INCELEMESI DUZELTME TURU (17.09.2026, kurul onayli
// istisna, bagimsiz bir ikinci inceleme "7/10" degerlendirmesiyle 10
// somut bulgu getirdi, hepsi kod uzerinde dogrulandi):
//  1) KRITIK: _hardExitBreak duzeltilmisti ama GERCEK _posOpen kapatma
//     blogu TAMAMEN AYRI bir degisken olan hardExitRaw'a bagliydi, stop
//     fiyatina hic referans vermiyordu - ikinci, farkli bir "olu stop"
//     sorunu. _stopHit (dogrudan low<=_stopPrice) eklendi, kapatma
//     kosuluna baglandi.
//  2) KRITIK: _tp1Level/_tp2Level'da giris fiyati donuyordu ama ATR
//     CANLIYDI - hedefler ATR degistikce kayiyordu. _entryAtr eklendi,
//     giriste donduruluyor.
//  3) _positionManaged, _posOpen'i icermiyordu - asgari guvenlik yamasi
//     olarak eklendi (tam mimari birlestirme hala ertelendi).
//  4) B4 kovalari KAPANIS anindaki rejimi kullaniyordu, GIRIS anindakini
//     degil - _entryRegime eklendi (_entryFactor ile ayni enstantanede).
//  5) RR paneli (R1/R2) hala eski rr1Ratio/rr2Ratio kullaniyordu (STOP/TP
//     hucreleri yeni degerleri gosterirken) - _displayRR1/2 eklendi,
//     SADECE panel icin (rrRatio/_buyOpsGate KARAR kapisina DOKUNULMADI).
//  6) Tick yuvarlama yonu: STOP icin ASAGI yuvarlama riski ARTIRIYORDU
//     (stopu uzaklastirir) - f_bistRoundStop (YUKARI) eklendi, stop
//     ciktilarina uygulandi. TP asagi kalmaya devam ediyor (dogru).
//  7) GUNLUK_OZET alarmina barstate.isconfirmed eklendi.
//  8) P3 soguma _urgentExitAlert (cooldown'a tabi) yerine _urgentExitRaw
//     (ham olay) kullaniyor artik.
//  9) _p3Al artik p3Enabled'a bagli - modul kapaliyken gunluk tekillik
//     tuketilmiyor.
// 10) lastAlertBar'in KISMI/tum-alarm-olmayan cooldown kapsami
//     BELGELENDI (degistirilmedi - davranis degisikligi backtest ister).
// 11) SELL toparlanma off-by-one: _smStateBars giris barinda 1'den
//     basladigi icin esik >=5'ten >=6'ya cekildi (tam 5 bar).
// BILEREK DOKUNULMAYAN (dis incelemenin de belirttigi, ayri/daha buyuk
// isler): B3 yarim-boyut hala yalniz P3Ozet biti (downstream uygulama
// yok, webhook gecikmesi cozulmeden GUVENLI degil), PAS durumunda panel
// hala aktif gorunuyor (kozmetik, ayri UI isi), HTF EMA/webhook
// gecikmesi/4 pozisyon kaynagi (mimari, ertelendi).
```

---

## [CL002] =====================================================================

```
// =====================================================================
// 27.08 ALTYAPI YAMASI (3. madde, GERCEKLIK_ALARM_3 kaynagindan): GERCEKCI
// (gunluk kapanis tabanli, tick-yuvarlamali) limit/gap hesabi. Perplexity'nin
// KENDI ilkesi: "Bu kapi MEVCUT karar skorunu DEGISTIRMEZ; yalnizca ISLEM
// YAPILABILIRLIK filtresi olarak CALISIR" - bu yuzden ESKI isLimitZone/
// finalDecision'a HIC DOKUNULMADAN, PARALEL bir "execution risk" katmani
// olarak eklendi. Dogrulandi (kurul analizi 2026-08-27): hicbir alertcondition
// veya _finalDecision'a girmiyor, sadece panel rengine besleniyor.
// =====================================================================
```

---

## [CL003] 17.09 B6 EKLENTI (kurul onayli istisna, İP-1 K2 "E3 testere" bulgusuna

```
// 17.09 B6 EKLENTI (kurul onayli istisna, İP-1 K2 "E3 testere" bulgusuna
// dayanarak): regimeTag HAM/ANLIK - trendUp/trendDown tek barda flip
// edebiliyor (EMA yiginlarinin sinir cizgisinde salinmasi), rejim etiketi
// gereginden sik "testere" gibi TREND<->YATAY<->TREND arasinda cirpiniyor.
// trendUp/trendDown'IN KENDISINE DOKUNULMADI (40+ yerde kullaniliyor,
// KOKTEN degisiklik riskli) - bunun yerine SADECE regimeTag'in "yapiskan"
// (sticky) 2-bar-teyitli bir varyanti eklendi: HAM okuma iki ardisik barda
// AYNIYSA yeni rejime GECILIR, degilse ONCEKI TEYITLI rejim KORUNUR. Bu,
// B4'un WR kovalarini (regimeTag=="TREND" vb.) ve regimeHistMult'u besleyen
// _curRegimeN/_curRegimeWr'yi YONLENDIRIYOR (asagida) - amac flip sayisini
// azaltip bu istatistiklerin gurultu yerine gercek rejimi olcmesi.
```

---

## [CL004] 17.09 GLOBAL SCOPE KUCULTME ("main body of script is too long" hatasi

```
// 17.09 GLOBAL SCOPE KUCULTME ("main body of script is too long" hatasi
// duzeltmesi - Pine'in 1000-degisken/scope siniri, TradingView belgeleri:
// "the code placed in global scope is implicitly wrapped into the main
// function, the limit of 1000 variables becomes applicable to it"):
// asagidaki ~140 satirlik bagimsiz skor alt-bileseni hesabi (coreScore/
// flowScore/riskScore ve girdileri) KENDI scope'una sahip bir fonksiyona
// tasindi - global degisken sayisini dusurur, DAVRANIS/FORMUL BIREBIR
// AYNI (yalniz nerede hesaplandigi degisti). Sadece BLOK DISINDA
// kullanilan 9 deger tuple olarak donduruluyor (scoreCalcRaw, scoreTrend,
// scoreRsIndex, scoreSectorLead, scoreFlow, scoreObv, scoreInstF,
// _trendDominance, healthyPullback - hepsi dis kullanim taranarak
// dogrulandi), blok ICI yardimci degiskenler (_rsRawVal, _xbankRs, coreScore
// vb.) fonksiyona ozel kaldi, disaridan erisilmiyor (zaten erisilmiyordu).
```

---

## [CL005] 17.09 ALARM KAPANIS TEYIDI DUZELTMESI (kurul onayli istisna, harici ko

```
// 17.09 ALARM KAPANIS TEYIDI DUZELTMESI (kurul onayli istisna, harici kod
// incelemesi dogrulandi): canAlert eskiden yalniz cooldown kontrolu
// yapiyordu (barstate.isconfirmed YOKTU) - "Once Per Bar" alarm sikligi
// secilirse, bar kapanana kadar gecerliligini yitirebilecek INTRABAR
// degerlerle 13 operasyonel alarm (_p0/_p1/_p2/_p3Alert, _urgentExitAlert,
// _pozAzaltAlert, _exitWatchAlert, _rotationAlert, _carryAlert,
// _reloadCandidateAlert, _dipDonusAlert, _p3HacimAlert, _addCandidateAlert)
// tetiklenebiliyordu. canAlert BUNLARIN HEPSININ TEK ORTAK KAPISI OLDUGU
// icin buraya eklemek 13'unu birden duzeltiyor. P3_SKOR_AL (_p3Al) zaten
// _p3Tetik uzerinden barstate.isconfirmed tasiyordu, GERCEK STOP KIRILDI
// (_gStopKirildi) BILEREK degistirilmedi - raporun kendi onerdigi istisna,
// gercek stop intrabar da tetiklenebilmeli (risk yonetimi geciktirilmemeli).
```

---

## [CL006] 17.09 GERCEK STOP DUZELTMESI (dış kurul incelemesi, kritik bulgu #1 -

```
// 17.09 GERCEK STOP DUZELTMESI (dış kurul incelemesi, kritik bulgu #1 -
// dogrulandi): 17.09'daki ilk yamada _hardExitBreak duzeltilmisti (olu
// close<close-pozitif kosulu), FAKAT _hardExitBreak yalniz ACIL_CIK
// alarmini/_pozAzaltRaw'i besliyor - asagidaki GERCEK _posOpen kapatma
// bloğu ise TAMAMEN AYRI bir degisken olan hardExitRaw'a bagli (satir
// ~2434, EMA/RSI/panicSell HEVRISTIGI - _stopPrice'a hic referans
// VERMIYOR). Yani fiyat stopu kirsa bile, hardExitRaw'in kendi heuristik
// sartlari (rsi<45, marketState vb.) AYRICA saglanmadikca ic pozisyon
// takibi (_posOpen, f_perfBucket WR/PF istatistikleri) KAPANMIYORDU -
// ölü kod ikinci kez, farkli bir yerde. COZUM: dogrudan fiyat-tabanli
// _stopHit eklendi (low<=_stopPrice, gercek bir stop emrinin calisma
// mantigi), kapatma kosuluna EKLENDI. _hardExitBreak'e (ALARM/POZ_AZALT
// icin, teyitli/daha sıkı bir "acil cikis" versiyonu) DOKUNULMADI - ikisi
// farkli amaclara hizmet ediyor (biri gercek stop, biri erken uyari).
// 17.09 (dış kurul incelemesi, "stop kronolojisi" P0 - dogrulandi): eski
// _stopHit AYNI barin (henuz o barin kapanisiyla YENI hesaplanmis/
// yukseltilmis) _stopPrice'ini o barin low'uyla kiyasliyordu - giris
// barinda bu GERIYE DONUK bir stop testi anlamina gelebiliyordu (henuz
// pozisyon acilmadan barin erken bir noktasinda olusan low, o barin
// KAPANISIYLA hesaplanan stopu "kirmis" sayilabiliyordu). COZUM: ONCEKI
// barin DONMUS stop seviyesi (_stopPrice[1]) kullaniliyor - giris
// barinda bu deger dogal olarak na (henuz pozisyon yoktu), o yuzden
// entry barinda hicbir zaman tetiklenmiyor (bar_index>_entryBar kontrolu
// da ayni korumayi acikca saglıyor).
```

---

## [CL007] 17.09 SELL KILIDI DUZELTMESI (kurul onayli istisna, harici kod

```
// 17.09 SELL KILIDI DUZELTMESI (kurul onayli istisna, harici kod
// incelemesi "Yuksek oncelikli sorunlar" maddesi): SELL'den cikisin TEK
// yolu skorun 30 ALTINA DUSMESIYDI (_smState==SELL and scoreSmoothed<30)
// - yani kurtulmak icin once DAHA DA KOTULESMESI gerekiyordu. Skor SELL
// sonrasi 30 uzerinde toparlansa bile _smToBuy PREP, _smToHold BUY sart
// kostugu icin (satir ~2495/2500) SISTEM SELL'DE KILITLI KALIYORDU.
// COZUM (raporun onerdigi "cikis olayi + cooldown" tasarimi): SELL'e
// dogrudan BUY/HOLD/WATCH atlama YOK (bu riskli olurdu) - SELL yine
// NEUTRAL'e cikiyor (NEUTRAL->PREP->BUY dogal yoluyla devam eder), ama
// artik SADECE "daha kotu" degil "gercekten toparlandi" durumunda da:
// minimum cooldown (5 bar) + skor belirgin iyilesti (>=40, 30'dan
// YUKARIDA - "biraz daha az kotu" degil "toparlanma" esigi) + fiyat
// EMA9/EMA21 ustune dondu + hicbir acil-cikis kosulu aktif degil.
// 17.09 kucuk duzeltme (dış kurul incelemesi, off-by-one): _smStateBars
// giris barinda zaten 1 oluyor (satir ~2698, kosulsuz +1), yani eski >=5
// aslinda SELL girisi + SADECE 4 tam bar sonrasi anlamina geliyordu.
// >=6 ile tam 5 TAMAMLANMIS bar sonrasi saglaniyor.
```

---

## [CL008] 17.09 (kullanici talebi: "sagdaki WR/PF/Kelly panelleri dolu gorunsun"

```
// 17.09 (kullanici talebi: "sagdaki WR/PF/Kelly panelleri dolu gorunsun"):
// f_v114Decision _hasPortfolioPosition=true iken HICBIR ZAMAN AL/TEYITLI
// AL/ERKEN AL uretmiyor ("CIK"/"HOLD"a dusuyor) - bu YUZDEN _v112
// (arastirma/istatistik motoru) portfolioPosition isaretliyken o sembol
// icin HIC pozisyon acmiyordu, WR/PF/Kelly/rejim kovalari N=0 kaliyordu.
// COZUM: f_v114Decision AYNI GIRDILERLE ama portfolioPosition SAHTE
// olarak false verilerek IKINCI kez cagriliyor - SADECE arastirma icin,
// GERCEK karara/alarma/panele hicbir ETKISI YOK (fonksiyon SAF - yan
// etkisi/degisken mutasyonu yok, iki kez cagirmak guvenli). _v112 artik
// bu GOLGE karara bagli - portfolioPosition isaretli olsa bile "eger
// elimde olmasaydi ne olurdu" sorusunu surekli olcuyor.
```

---

## [CL009] NOT: waitReasonTxt hesaplamasi asagiya, _v113Lifecycle/_pozAzaltRaw/_u

```
// NOT: waitReasonTxt hesaplamasi asagiya, _v113Lifecycle/_pozAzaltRaw/_urgentExitRaw
// TANIMLANDIKTAN SONRAYA tasindi (bkz. asagida) - eskiden BURADA ham _finalDecision'a
// bakiyordu, ACTION hucresinin (_kararTxt) uyguladigi yasam-dongusu gecersiz kilmasini
// (orn. _v113Lifecycle=="TUT" oldugunda AL yerine IZLE gosterme) HESABA KATMIYORDU.
// Sonuc: ASELS gibi durumlarda ACTION="IZLE" derken NOTE="ISLEM ADAYI" diyordu - iki
// hucre birbiriyle CELISIYORDU.
// NOT: Orijinal onerideki f_memberDecision/f_crossSystemComment fonksiyonlari
// EKLENMEDI - asil degerli kismi (KOVALAMA uyarisi) asagida ACTION hucresine
// daha hafif bir sekilde (yeni fonksiyon acmadan) gomuldu. Kod sismesin diye
// ayni bilgiyi iki kez uretmekten kacinildi.
```

---

## [CL010] 17.09 B4 DUZELTMESI (dış kurul incelemesi, dogrulandi): B4'un rejim

```
// 17.09 B4 DUZELTMESI (dış kurul incelemesi, dogrulandi): B4'un rejim
// kovalari (asagida) regimeTagConfirmed'i KAPANIS aninda okuyordu - yani
// TREND'de acilip DUSUS'te kapanan bir islem DUSUS kovasina yaziliyordu.
// Soru "TREND'de actigimiz islemler nasil performans gosterdi" yerine
// "kapanista TREND gorunen islemler nasil kapandi"ya kayiyordu.
// _entryRegime, _entryFactor ile AYNI enstantane blogunda donduruluyor.
// 17.09 (dış kurul incelemesi madde 11): AYNI sorun _regimeRadar (BROAD
// ON/OFF kovasi) icin de gecerliydi - _entryRadarRegime EKLENDI, blok
// buraya (regOn/regOff kovasindan ONCEYE) TASINDI ki kullanilabilsin.
// volRegime/sessionTag ICIN AYNI SEY yapilamiyor - onlar bu noktada
// HENUZ hesaplanmamis (script sirasi), o yuzden kendi tanimlarindan
// hemen SONRA ayri birer enstantane bloguyla yakalaniyorlar (asagida).
```

---

## [CL011] 17.09 (dış kurul incelemesi, "LIVE/SHADOW karismasi" bulgusu -

```
// 17.09 (dış kurul incelemesi, "LIVE/SHADOW karismasi" bulgusu -
// dogrulandi, GERCEKTEN regimeHistMult'u/pozisyon boyutunu etkiliyordu):
// _v112Entered artik golge karara (portfolioPosition=false varsayimi)
// bagli - yani portfolioPosition true iken acilan "golge" islemler de
// _v112Closed'a giriyor. Bu, genel panel istatistikleri (WR/PF, "dolu
// gorunsun" istegi) icin ISTENEN davranis, ama _curRegimeWr uzerinden
// regimeHistMult'a (GERCEK lot boyutu) KARISMAMALI - bir golge islemin
// sonucu, gercek bir sinyalin sonucu degil. _entryWasManual, giriste
// portfolioPosition true miydi diye yakalıyor.
```

---

## [CL012] V0 KAPSAM NOTU: yalniz _curRegimeWr'yi (canli regimeHistMult karari) b

```
// V0 KAPSAM NOTU: yalniz _curRegimeWr'yi (canli regimeHistMult karari) besleyen
// UC bucket (trend/yatay/dusus) duzeltildi. Sektor/hacim/faktor/seans bucket'lari
// (_regOnN, _volHighN, _fTrendN, _sessOpenN vb.) AYNI mukerrer-sayim sorununu
// tasiyor ama HICBIRI canli bir karari BESLEMIYOR (yalniz panelde gorunuyor) -
// bu yuzden V0'da BILEREK dokunulmadi, ayri bir B-maddesi olarak degerlendirilebilir.
// === MODUL 2 (devam): FAKTOR-BAZLI BACKTEST - _entryFactor GIRIS aninda kaydedilip
// KAPANISA kadar sabit kaliyor (_v112Entry gibi), boylece "bu islemi hangi faktor
// tetikledi" post-mortem analizi yapilabiliyor. ===
```

---

## [CL013] 17.09 ASGARI GUVENLIK YAMASI (dış kurul incelemesi, bulgu #6 - dogrula

```
// 17.09 ASGARI GUVENLIK YAMASI (dış kurul incelemesi, bulgu #6 - dogrulandi):
// _positionManaged, _posOpen kaynagini icermiyordu. Senaryo: _posOpen=true
// ama portfolioPosition=false ve _v112Open=false olabilir - bu durumda
// _newEntryMode=true KALIYOR, P3 gibi "yeni giris" alarmlari ic motor
// zaten pozisyondayken bile ates alabiliyordu. Dort pozisyon kaynaginin
// TAM birlestirilmesi (mimari, ertelendi) AYRI bir konu - bu yalniz
// asgari, guvenli bir ekleme (OR mantigi geriye donuk davranisi BOZMAZ,
// yalniz eksik bir kaynagi ekler).
```

---

## [CL014] 17.09 (dış kurul incelemesi, madde 6 - "pozisyon kaynaklari hala tam

```
// 17.09 (dış kurul incelemesi, madde 6 - "pozisyon kaynaklari hala tam
// birlesmedi"): TAM mimari birlestirme (dort ayri yasam dongusunu -
// _posOpen/_v112Open/portfolioPosition/_smState - TEK sisteme indirmek)
// BUYUK bir proje, ERTELENDI. Bunun yerine reviewer'in onerdigi GUVENLI
// ARA COZUM uygulandi: hangi kaynagin aktif oldugu GORUNUR kilindi ve
// BIRDEN FAZLA kaynak AYNI ANDA aktifse acikca UYARILIYOR (yeni alim/
// ekleme DURDURULMUYOR - bu davranis degisikligi olurdu, sadece
// GORUNURLUK saglaniyor).
```

---

## [CL015] 17.09 DUZELTME (kurul onayli, istisna karari - MANTIK ama hata duzeltm

```
// 17.09 DUZELTME (kurul onayli, istisna karari - MANTIK ama hata duzeltmesi,
// KULUCKA_PROTOKOLU C.5/C.6 istisna maddesi kapsaminda B1-B6 birikiminden
// AYRI ele alindi): 'stop' degiskeni HER BARDA close'dan yeniden hesaplaniyor
// (satir 1748: stop = close - atr*slMult1) - o yuzden AYNI barda close<stop
// matematiksel olarak HICBIR ZAMAN dogru olamiyordu (close < close - pozitif
// sayi). Sonuc: _hardExitBreak yapisal olarak HER ZAMAN false donuyordu,
// ACIL_CIK'in (_urgentExitRaw = panicSell or _hardExitBreak) bu bacagi tamamen
// olu kod idi, yalniz panicSell calisiyordu. Harici kod incelemesiyle bulundu,
// kaynak koddan (satir 1748, 2795) dogrulandi.
// COZUM: pozisyonun GERCEK/donmus takip stopu olan _stopPrice ile karsilastir
// (satir ~2106'da girişte atanir, yalniz yukari tasinir - satir 2191/2210).
// _posOpen/na kontrolu: pozisyon yokken _stopPrice na, kiyaslama guvenli olsun.
```

---

## [CL016] === EK MODUL D (kurumsal, onaylandi): KELLY-BAZLI BOYUT AYARI - artik 

```
// === EK MODUL D (kurumsal, onaylandi): KELLY-BAZLI BOYUT AYARI - artik SADECE bilgi
// degil, gercekten uygulaniyor. Muhafazakar (yari-Kelly benzeri) kurallar:
// - N<20 ise: ORNEKLEM KUCUK, Kelly'nin etkisi YOK (carpan=1.0) - erken donemde
//   guvenilmez istatistige gore boyut degistirmek riskli olurdu.
// - Kelly<=0 (edge YOK/negatif): boyut YARIYA indirilir (0.5x) - sistem su an
//   kazandirmiyor demektir, agresif kalinmamali.
// - Kelly>0: boyut EN FAZLA %30 artirilir (1.0+kelly, tavan 1.3x) - tam Kelly'nin
//   agresifligi yerine kontrollu bir artis.
// === EK MODUL E (kurumsal): SEANS BAZLI BACKTEST - CTRL RADAR'daki ayni saat dilimi
// mantigi (ACILIS/ANA SEANS/OGLE SONRASI/KAPANIS), yeni hesaplama minimal. ===
```

---

## [CL017] 17.09 (dış kurul incelemesi, P0 - "SHADOW sonuclari lota karismiyor"

```
// 17.09 (dış kurul incelemesi, P0 - "SHADOW sonuclari lota karismiyor"
// iddiasi TAM DOGRU DEGILDI): regimeHistMult'u golge veriden ayirdik
// ama kellyMult (_v112Wr/_v112AvgW/_v112AvgL) ve consecLossMult
// (_v112Closed dongusu) HALA golge/SHADOW verisinden besleniyor ve
// dogrudan GERCEK lota giriyordu. Tam bir ikinci sayac sistemi (Kelly/
// ArdisikKayip icin de _entryWasManual filtresi) token acisindan
// pahalı olurdu - bunun yerine reviewer'in onerdigi DUSUK MALIYETLI
// anahtar eklendi: varsayilan KAPALI, ucu carpan da PANELDE hesaplanip
// GOSTERILMEYE devam ediyor (izlemek icin), ama gercek lot formulunde
// anahtar acilana kadar 1.0 kullaniliyor - yani SHADOW/manuel-karisik
// donemin Kelly/ArdisikKayip etkisi lota SIZMIYOR, yeterli temiz
// donem biriktiginde (P1: logicEraStart sonrasi, _entryWasManual
// haric) bilinçli olarak acilabilir.
```

---

## [CL018] 17.09 BELGELENDI (dış kurul incelemesi, bulgu dogrulandi, DEGISTIRILME

```
// 17.09 BELGELENDI (dış kurul incelemesi, bulgu dogrulandi, DEGISTIRILMEDI -
// davranis degisikligi backtest gerektirir, riskli): lastAlertBar SADECE
// _p1Alert/_p2Alert/_p3Alert/exitRiskFull/hardExitRaw tarafindan
// guncelleniyor - _urgentExitAlert, _pozAzaltAlert, _exitWatchAlert,
// _rotationAlert, _carryAlert, _reloadCandidateAlert, _dipDonusAlert,
// _p3HacimAlert, _addCandidateAlert bu sayaci GUNCELLEMIYOR. Yani
// canAlert cooldown'u KURESEL/TUM-ALARM degil, yalnix bu 5 tetikleyici
// arasinda paylasiliyor - orn. ACIL_CIK'tan hemen sonra bir P1 alarmi
// cooldown'a takilmadan atesleyebilir. BILINCLI/mevcut tasarim olarak
// kaldi, degistirilmedi - global cooldown'a gecmek onceden olculmemis
// bir davranis degisikligi olurdu.
```

---

## [CL019] 17.09 RR PANEL TUTARLILIGI (dış kurul incelemesi, bulgu #5 - dogruland

```
// 17.09 RR PANEL TUTARLILIGI (dış kurul incelemesi, bulgu #5 - dogrulandi):
// panel STOP/TP1/TP2 artik dogru cift'i (aday: _planTp1/2, acik pozisyon:
// _tp1Level/2) gosteriyor ama R1/R2 metni HALA eski rr1Ratio/rr2Ratio'yu
// (raw entry/tp1/tp2/stopMesafe) kullaniyordu - AYNI panelde UC farkli
// islem modeli goruluyordu. rrRatio/rrGrade'e DOKUNULMADI (rrRatio zaten
// _buyOpsGate KARAR kapisinda kullaniliyor - MANTIK degisikligi, kanit
// gerektirir). Bunun yerine SADECE GOSTERIM icin ayri, dogru cift ile
// hesaplanan _displayRR1/2 eklendi.
// 17.09 KRITIK DUZELTME (gercek kullanici raporu - STOP NaN gosteriyordu):
// _stopPrice/_entryPrice/_tp1Level/_tp2Level YALNIZ ic simulasyon motoru
// (_posOpen) GERCEKTEN bir giris tespit ettiyse doluyor. "Portfoyde
// Pozisyon Var" (portfolioPosition) ise KULLANICININ ELLE isaretledigi,
// TAMAMEN BAGIMSIZ bir bayrak - ic motor o hisseye hic giris tespit
// etmemis olabilir (orn. pozisyon gostergeyi eklemeden ONCE alinmissa).
// O durumda _stopPrice hep na kalir, panel NaN gosteriyordu - UYDURMA
// bir ic deger goster YERINE artik acikca "BILINMIYOR" diyor (UPM_V1
// sozlesmesi Madde 2'nin oneriyle AYNI ilke: MANUAL_LIVE'da gercek veri
// yoksa STOP UNKNOWN goster, ic degeri sizdirma).
```

---

## [CL020] 17.09 (dış kurul incelemesi, tick yuvarlama tablosu - kalan kısım):

```
// 17.09 (dış kurul incelemesi, tick yuvarlama tablosu - kalan kısım):
// STOP/TP zaten yuvarlaniyordu, AL BOLGE/TETIK ise HIC yuvarlanmiyordu.
// Tablo: Alim tetik->YUKARI (f_bistRoundStop, ayni yukari-yuvarlama
// fonksiyonu - isim "Stop" olsa da islevi genel "yukari yuvarla"),
// Limit alim->ASAGI (f_bistRound).
// 17.09 (dış kurul incelemesi, madde 10 - "PAS gorunumu yanıltıcı"):
// ACTION=PAS GEC iken panel STOP/TP1/TP2'yi AKTIF bir islem planiymis
// gibi kirmizi/yesil gosteriyordu. _planPasif eklendi - pozisyon YOK ve
// karar PAS GEC ise plan cizgileri/metni PASIF (gri, "AKTIF DEGIL")
// gosteriliyor. Pozisyon ACIKKEN bu hicbir zaman true olmaz (gercek bir
// islem var), yalniz ADAY planlama asamasinda devreye giriyor.
// 17.09 (dış kurul incelemesi madde 6): positionSource/positionConflict
// ZATEN daha once eklenmisti (bkz. yukarida, satir ~3108-3118) - burada
// TEKRAR tanimlamiyorum, sadece kullaniyorum.
```

---

## [CL021] 17.09 V162.2: math.round(*100)/100 -> f_bistRound. Eskiden 254,37 gibi

```
// 17.09 V162.2: math.round(*100)/100 -> f_bistRound. Eskiden 254,37 gibi
// BIST'te gercekte islem gormeyen (250 uzeri tick 0,25) bir fiyat webhook'a
// gidebiliyordu.
// 17.09 (dış kurul incelemesi madde 14, "stop alani yanlis semantik"):
// webhook eskiden HER ZAMAN ham aday stop'u ('stop', close-tabanli)
// gonderiyordu - ic pozisyon ACIKKEN bile gercek takip stopu (_stopPrice)
// DEGIL, sanki hicbir pozisyon yokmus gibi surekli kayan bir deger
// gidiyordu. Artik panel ile AYNI mantik: ic pozisyon acikken _stopPrice,
// degilse (aday/PAS) _planStop. TAM alan ayrimi (candidateStop/
// internalTrailStop/manualPortfolioStop/stopSource) plot butcesi (64,
// zaten sinirda) yeni tasiyici eklemeye izin vermedigi icin YAPILMADI -
// bu, tek bir dogru deger secmekle sinirli bir iyilestirme.
// 17.09: stop kirilma barinin KENDISINDE (_stopHitEvent) latch edilen
// _lastStopFill kullanilir - _stopPrice o an zaten temizlenmis olabilir.
```

---

## [CL022] 03.09: zaman damgasi ({{time}}) ve 2 ondalik yuvarlama kaldi.

```
// 03.09: zaman damgasi ({{time}}) ve 2 ondalik yuvarlama kaldi.
// htf/dnadef/skortb -> P3Ozet (asagida, pSkorTaban tanimindan sonra) tasindi.
// ============================================================
// P3_SKOR - IP-4 EK-1 (23.07.2026): skor-tabanli giris modulu
// KONUM: bu blogu V151 icinde, alertcondition(...) satirlarindan
// HEMEN ONCE (yaklasik satir 3270 civari, "coreBuyAlert" alarmindan
// once) yapistir. scoreSmoothed/relVol/regimeTag/_urgentExitAlert
// o noktada zaten tanimli oluyor.
//
// PARALEL HAT: P1/P2/CORE/ACIL_CIK/POZ_AZALT zincirine ve durum
// makinesine (_smState vb.) DOKUNMAZ. Yeni plot yok, yeni bir
// alertcondition var. Ana salter: p3Enabled - kapatilinca hicbir
// P3 hesaplamasi/alarmi uretilmez (geri alma = tek input).
//
// KAYITLI PARAMETRE ARALIGI (IP-4 Bolum 5 / EK-1 - backtest oncesi
// donduruldu, bu araliklar disi deger denenmez):
//   pSkorTaban   [25-40] Katman A 23.07 verisiyle: 25=%60, 30=%57,
//                35=%67, 40=%80 isabet (kucuk orneklem, n=5-13)
//   pSkorMomBar  [3-10], pTepePencere [5-20], pTetikHacim [1.1-1.5]
//   pKovalamaPct [1.0-2.0], pSogumaBar [10-40], pAzamiStopPct [2.0-5.0]
//   pAzamiHtf [0-2] (23.07 eki - EREGL vakasi, htfAlign>=1 varsayilan)
//   DEFENSIVE DNA HARIC (23.07 A1 karari - v1'de sabit, parametre degil)
// ============================================================
```

---

## [CL023] 03.09 (2. tur) GECICI DENEME PLOTU: bar-gecikme sorununun kaynagi olan

```
// 03.09 (2. tur) GECICI DENEME PLOTU: bar-gecikme sorununun kaynagi olan
// "ilk 20 plot" kisitinin ISIMLI placeholder'lar icin de gecerli olup
// olmadigini test etmek icin. Bu plot script'teki plot() sirasinda 20.
// sinirin OTESINDE (S/R2 kaldirilinca acilan 2. bos slot kullanildi).
// Eger alarmda {{plot("SkorGecTest")}} DOLU gelirse: isimli placeholder
// pozisyondan bagimsizdir, tasiyicilari GEC POZISYONA tasimak guvenlidir
// (gercek bar-gecikme duzeltmesi boylece kuluckayi bozmadan yapilabilir).
// Bos/"?" gelirse: kisit gercek, zamanlama-tabanli duzeltme gerekir.
// KARAR MANTIGINA HICBIR ETKISI YOK - sadece deneme amacli ekstra plot.
```

---

## [CL024] ---- BEKCILER: kovalama / ACIL_CIK sonrasi soguma / asiri stop mesafes

```
// ---- BEKCILER: kovalama / ACIL_CIK sonrasi soguma / asiri stop mesafesi
// 17.09 B3 DUZELTME (kurul onayli istisna, backtest kanitiyla - bkz.
// data/backtest/b3_kovalama_kacirdi_sonuc.json): eskiden pKovalamaPct
// (%1.5) uzerindeki HER sey TAM VETO idi. Backlog'un kendi karar
// kriteri (>%55 T+3 isabet) test edildi: KACIRDI vakalari genel %55.1
// (GECTI). Kademeli test 1.5-3.0/3.0-6.0/6.0-uzeri banta ayirdi -
// ilk iki kademe (%54.6-56.2 T+3 isabet, TAM ALINDI grubundan (%55.6)
// FARKSIZ) ile son kademe (%54.0, en zayif) arasinda BELIRGIN fark
// yok ama en uzak kademe en dusuk - o yuzden TAM VETO yalniz 4x banda
// (%6.0) tasindi, 1x-4x bandi (%1.5-6.0) artik VETO EDILMIYOR, yalniz
// YARIM BOYUT olarak isaretleniyor (asagida webhook'a "boyut" alani
// eklendi - gercek boyut kararini downstream/portfoy tarafi versin,
// Pine sadece ISARETLIYOR).
```

---

## [CL025] ---- GORSEL (opsiyonel - grafikte P3 girisini isaretler)

```
// ---- GORSEL (opsiyonel - grafikte P3 girisini isaretler)
// v2 (23.07) DUZELTME: plotshape() kullanilmiyor - V151 zaten 64 plot
// tavanina yakin/ustunde (RE10140 hatasi: "65 plots, limit 64").
// label.new() ayri bir butceden harcar (indicator() tanimindaki
// max_labels_count=100), plot sayacini hic etkilemez.
// GECICI DEBUG (23.07): tarih dogrudan etikete yaziliyor - mouse ile
// tarih okuma/ay karistirma riskini ortadan kaldirir. D2' onaylanip
// bu tartisma kapaninca "GECICI DEBUG" satiri kaldirilabilir.
```

---

## [CL026] ============================================================

```
// ============================================================
// GERCEK STOP ALARMI (31.07.2026 EKI): portfoy.json'daki gercek
// stop_seviye ile senkron, dogrudan "SAT" anlamina gelen tek alarm.
// GEREKCE: V151'in 18 alertcondition'inin HICBIRI kullanicinin
// gercek stop rakamlarina (65.00, 32.50, 190.00, 258.00, 290.00 gibi)
// bagli degil - ACIL_CIK/POZ_AZALT V151'in KENDI ic hesabina dayanir.
// Ekran basinda olunmayan anlarda hicbir otomatik uyari gitmiyordu.
//
// KULLANIM: Her pozisyon grafiginde (AKBNK/YKBNK/KCHOL/TAVHL/ASTOR)
// asagidaki iki input'u portfoy.json'daki GUNCEL stop_seviye ile
// SENKRON tut - stop her degistiginde (temettu duzeltmesi gibi) bu
// inputu da guncelle. PARALEL HAT: V151'in kendi motoruna dokunmaz.
// ============================================================
```

---

## [CL027] Rejim kovaları logicEraStart'a geçirildi

```
"Yeni" rejim kovalari (regimeHistMult'u besleyen) artik logicEraStart'tan
(17.09.2026, son mantik degisikligi) besleniyor, hacimEraTarihi'nden
(08.07.2026) DEGIL. Eskiden 08.07-16.09 arasi islemler de "yeni" sayiliyordu,
ama o donem hala eski mantikla hesaplaniyordu - bu, gercek lot boyutuna
(sizingFeedbackEnabled acildiginda) tutarsiz bir donem karisimi tasiyordu.
hacimEraTarihi, Eski/panel kovalarinda (_trendEskiN vb.) referans/karsilastirma
amacli degismeden kaliyor.
```

---


---

## Alarm Önceliklendirme Rehberi (17.09.2026, son dış inceleme madde 7)

Bir sonraki token/plot sıkışmasında **önce hangi alarmların kırpılabileceğini**
önceden belirlemek için. Kritik ve İşlem alarmları LIVE'da her koşulda kalır.

| Öncelik | Alarm türleri | Kırpma sırası |
|---|---|---|
| **Kritik** | STOP_KIRILDI, IC_STOP, ACIL_CIK, POZ_AZALT | Asla — LIVE'da mutlaka kalır |
| **İşlem** | CORE_AL, CORE_CIKIS, P1_KALITELI_AL, P2_ADAY | Asla — LIVE'da mutlaka kalır |
| **İzleme** | CORE_IZLE, P3_HACIM_BEKLE, HAZIRLIK, ROTASYON | İsteğe bağlı, gerekirse 3. sırada kırpılır |
| **Araştırma** | GUNLUK_OZET, SkorGecTest alanı | İlk kırpılacaklar — 1. sırada |

Not: SkorGecTest (webhook bar-gecikmesi test amaçlı alan) kaldırılması için
öneri: en az 20-30 gerçek alarm örneği toplanıp bar-gecikmesi kesinleşince.

---

## [CL028] positionConflict güvenlik açığı (EKLEME dışında YENİ AL da bloke edilmeliydi)

```
17.09 (dış kurul incelemesi, doğrulandı - güvenlik açığı): positionConflict
(_v112Open'a bağlı olduğu için _finalAlertEvent'ten SONRA tanımlanıyor - o
yüzden orada KULLANILAMIYOR, "Undeclared identifier" verirdi) eskiden
YALNIZ EKLEME_ADAYI'nı engelliyordu - P1/P2/CORE_AL gibi YENİ giriş
alarmları çakışma sırasında bile ateşleyebiliyordu. _erkenPosCakisma
(yalnız _posOpen/portfolioPosition - ikisi de o noktada ZATEN hazır,
_v112Open'ı BEKLEMEDEN) ile _finalAlertEvent (TÜM AL alarmlarının
ortak tetikleyicisi, ÇIKIŞ için değil) artık korunuyor. ÇIKIŞ/STOP
yollarına (hardExitRaw/exitRiskFull) DOKUNULMADI. _shadowAlertEvent
(araştırma) BİLEREK DEĞİŞTİRİLMEDİ.
```


---

## [CL029] entryScore P3Ozet'e eklendi (alarm kalitesi teşhisi için)

```
21.09.2026 (kullanıcı talebi - "AL/ERKEN AL neredeyse hiç gelmiyor" şikayetinin
teşhisi için): sinyal_arsiv.json'un yalnız FİİLEN ateşlenen sinyalleri
kaydettiği, "entryScore eşiğe ne kadar yaklaştı ama geçemedi" bilgisini
tutmadığı fark edildi. GUNLUK_OZET zaten her sembol için günde bir kez
(AL/PAS fark etmeksizin) ateşlendiği için, entryScore'u P3Ozet taşıyıcısına
(yeni plot GEREKMEDEN, 100000'lik basamakta) eklemek en ucuz veri-biriktirme
yolu. Decode: entryScore = deger // 100000, yariBoyut = (deger % 100000) // 10000,
htf = (deger % 10000) // 1000, dnadef = (deger % 1000) // 100, skortb = deger % 100.
Bir hafta biriktikten sonra entryScore dağılımı analiz edilip hangi eşiğin/
koşulun en sık engellediği teşhis edilecek.
```

---

## [CL030] SkorGecTest kaldırıldı (amacına ulaştı)

```
21.09.2026: SkorGecTest (1 plot + 22 JSON alan referansı, 24 yer) 03.09'da
"bar-gecikme sorunu... KESİNLEŞTİ" diye zaten doğrulanmıştı - kaldırma
kriteri (20-30 alarm örneği + bar-gecikmesi kesinleşmesi) çoktan
karşılanmıştı, unutulmuş bir kalıntıydı. Token/plot bütçesinde gerçek
alan açmak için kaldırıldı.
```

## XBANK/Brent/Altın/HTF nz() incelemesi (21.09.2026, dış kurul incelemesi doğrulaması)

```
Dış kurul incelemesi "nz(external, close) risk" maddesini iddia etmişti.
Kod incelendiğinde: Brent (_brentEma20 = na(_brentClose)?na:...) ve Altın
AYNI desenle ZATEN korumalı - ara hesaplamanın nz() fallback'i, orijinal
veri eksikse na-check ile eleniyor. HTF (htfBull/htf2Bull) acik bir
na-check TASIMIYOR ama Pine'in "na ile karsilastirma = false" davranisi
sayesinde ORTUK olarak guvenli (veri yoksa sessizce false donuyor,
yanlis-pozitif URETMIYOR). Yalniz XBANK'ta dusme noktasi hissenin kendi
fiyati yerine xu100Close'a cevrildi (zararsiz iyilestirme, XBANK zaten
_xbankBear'da ayrica na-check tasiyordu). SONUC: bu madde buyuk olcude
zaten guvenliydi, ek is GEREKMEDI.
```

---

## [CL031] Saat-slot hacim modeline örneklem güveni eklendi

```
21.09.2026 (dış kurul incelemesi, doğrulandı): _todSlotVol her saat-dilimi
için üstel ortalama tutuyordu (_todBase*0.8+volume*0.2), ama SADECE
na(_todBase) kontrolü vardı - slot bir kez doldu mu (tek örneklemle bile)
hemen tam güvenilir sayılıyordu. Kısa geçmişte/tatil sonrası/yarım gün
seanslarında bu aşırı oynak bir relVol tabanı üretebilirdi. _todSlotN
(paralel dizi, her slotun örneklem sayısını tutuyor) eklendi - artık
volAvg yalnız o slot en az 10 kez görülmüşse slot-bazlı ortalamayı
kullanıyor, aksi halde klasik N-bar ortalamasına (volAvgSma) düşüyor.
Panel gösterimine (VOL BASE: SLOT/N=18) DOKUNULMADI - token bütçesi,
kozmetik ekleme değil çekirdek düzeltme önceliklendirildi.
```

---

## [CL031-geri alındı] Saat-slot örneklem güveni geri alındı (token bütçesi)

```
21.09.2026: [CL031]'de eklenen _todSlotN dizisi (yeni dizi + 2 array
işlemi + degisen kosul) gercek token maliyetiydi - string/yorum icerik
kisaltmalarinin (SkorGecTest metin kaldirma gibi) token sayisini
DEGISTIRMEDIGI anlasilinca (yalniz GERCEK kod ifadeleri sayiliyor),
80073/80000 asimini kapatmak icin EN SON eklenen, EN PAHALI gercek kod
geri alindi - pozisyon-cakisma guvenlik duzeltmesi ve entryScore tanisi
KORUNDU. Saat-slot ornek guveni fikri gecerliligini koruyor, token
bütçesi daha rahat oldugunda (orn. LIVE/RESEARCH ayrimi gibi daha buyuk
bir sadelestirmeden sonra) tekrar denenebilir.
```

---

## lateEntry / kovalama eşiği testi — SONUÇ: değişiklik önerilmiyor (21.09.2026)

```
Denetimde bulunan bulgu: ic pozisyon motorunun (_posOpen, 16 ayri
tetikleyici) hicbirinde not _lateEntry korumasi yok - gorunen alarmlar
(P1/CORE_AL) korumali ama ic motor (WR/PF/Kelly'yi besleyen) degil.

TEST 1 (ATR carpani 1.8/2.5/3.0/4.0): kucuk, tutarsiz fark. 2.5+'tan
sonra sonuc DEGISMIYOR - cunku lateEntry = (ATR kosulu) OR (EMA yuzdesi
kosulu), EMA-yuzdesi (sabit %3.5) baskin hale geliyor, ATR tarafi
etkisiz kaliyor.

TEST 2 (EMA yuzdesi izole, ATR sabit/gevsek): %3.5 (Pine varsayilani)
ve %5.0'da fark yok/ters. %7-10 araliginda GENEL toplamda belirgin,
tutarli fark ortaya cikti (kovalama grubu T+10'da hem isabet hem
getiride daha kotu).

TEST 3 (sembol bazinda saglamlik kontrolu, %10 esigi): KRITIK BULGU -
23 sembolden yalniz 13'unde "temiz > kovalama" yonu dogrulandi, 10
sembolde TAM TERSI (bazilari cok guclu: ASTOR -30pp, ULKER -18pp,
ASELS -16pp - yani bu hisselerde "kovalama" gunleri AKBNK/TUPRS/PETKM
gibi bankacilik/savunma agirlikli hisselerde ise "kovalama" GERCEKTEN
kotu (TUPRS +46pp, AKBNK +34pp, PETKM +30pp)).

SONUC: Genel toplam sonucu, IKI ZIT EGILIMIN ORTALAMASIYDI - tek bir
kuresel lateEmaExtPct/lateAtrMult degeri (sistemde HER yerde - tum
f_v114Decision kapilari, panel metinleri - kullanilan) bu heterojenligi
yansitamaz, evrenin yarisi icin dogru yarisi icin yanlis olurdu.

KARAR: Ne "16 motora lateEntry ekleme" ne "esik kalibrasyonu" su an
UYGULANMIYOR. Mimari tutarsizlik (16 motorun korumasiz olmasi) hala
duruyor ama tek kuresel esikle DUZELTILMEMELI - ileride ele alinacaksa
SEMBOL/SEKTOR BAZLI bir esik gerekir, cok daha buyuk bir proje
(muhtemelen UPM_V1 olceginde).
```

---

## Skor motorunda çifte-sayım testi — SONUÇ: kod değişikliği gerekmiyor (21.09.2026)

```
Son buyuk incelemenin iddiasi: "RS gucu hem dogrudan skor aliyor hem
liderlik skorunu hem sektor skorunu hem bazi giris motorlarinin
kosulunu karsiliyor" - yani ayni alti-yatan bilginin birden fazla
skor bileseninde TEKRAR odullendirilebilecegi.

TEST: KGS'nin 7 alt-skoru (Trend/EMA/RS/Vol/Sektor/CVD/Kurum) arasindaki
korelasyon matrisi olculdu (n=57.300, 30 sembol x ~7.7 yil).

SONUC: En yuksek korelasyon kgsTrend-kgsKurum (0.623), en dusuk
kgsVol-kgsSector (0.025). Reviewer'in ozellikle isaret ettigi
kgsRs-kgsSector cifti 0.529 - orta duzeyde, ama B1'de bulunan
KGS-entryScore korelasyonunun (0.963, %92 paylasilan varyans - B1'in
kod degisikligini gerektiren esik) COK ALTINDA (0.529 = %28 paylasilan
varyans). Alt-skorlar birbiriyle ILISKILI (beklenen - hepsi gercek
piyasa gucunun farkli yuzlerini olcuyor) ama COGUNLUKLA BAGIMSIZ bilgi
tasiyor, mukerrer degil.

KARAR: Bu, B1 capinda bir "gereksiz cifte-kapi" sorunu DEGIL. Kod
degisikligi ONERILMIYOR - KGS'nin cok-faktorlu tasarimi cesitlendirilmis
gorunuyor. B2/B5 ile ayni sonuc turu: test edildi, hipotez guclu
desteklenmedi.
```
