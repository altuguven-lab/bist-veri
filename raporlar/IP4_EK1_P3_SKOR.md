IP-4 EK-1: v0.2 REVIZYONU - P3_SKOR (skor-tabanli giris)
Statu: TASLAK | 20.07.2026 | Gerekce: D1 basarisizligi (pullback sinifi
%12-25 isabet, 0/13 yakalama) + TUPRS vakasi (16.07 skor 97.2 ->
20.07 +%6; skor GORDU, donusturucu katmanlar cevirmedi).
Yeni anatomi - P3_SKOR_AL (v0.1'in BAGLAM/KURULUM blogu degisir,
bekciler AYNEN kalir)
BAGLAM:
S1. scoreSmoothed >= [pSkorTaban]  (Katman A tablosundan kalibre)
S2. Skor YUKSELIYOR: scoreSmoothed > scoreSmoothed[pSkorMom] bar once
S3. REJIM - SEMBOL BAZLI: sembolun kendi g1RejimKod'u >= 1
(evren-geneli RISK-OFF olsa bile guclu sembol kapida kalmaz -
20.07 dersi; tartisma A4'e)
TETIK:
T1. Bar kapanisi son [pTepePencere] barin en yukseginin ustunde
T2. relvol >= [pTetikHacim]
T3. barstate.isconfirmed
BEKCILER: v0.1 G1-G4 aynen (kovalama / ACIL_CIK sogumasi / azami
stop mesafesi / gunluk tavan).
Ek parametreler (kayit - backtest oncesi donduruldu)
pSkorTaban:   [30..60]  baslangic: Katman A en iyi esik (Carsamba)
pSkorMom:     [3..10]   baslangic 5
pTepePencere: [5..20]   baslangic 10
(pTetikHacim, pKovalamaBant, pSogumaBar, pAzamiStopYuzde v0.1 kaydindan)
Dogrulama kapisi (revize)
D1'. Katman A esik tablosu (Carsamba tam): en az bir kayitli-aralik
esiginde T+3 isabet >= %55 VE o esik kulucka doneminde >= 5
gun/sinyal ureteceklerdi (uretim kanitli olmali, isabet tek
basina yetmez).
D2'. Vaka retrosu: KCHOL-50.6 (bugun kesinlesir) + TUPRS-97.2
(Sali kesinlesir) + bugunku 4 kacirilan sembolun aksam
ozetindeki skor/rejim degerleri "modul bugunu yakalar miydi"
sorusuna EVET demeli.
D3, D4 v0.1'den aynen (test protokolu; PPK disi deploy).
Acik soru A4 (Pazartesi oturumu)
Rejim kapisi sembol-bazli olunca IP-1'in "dusuk rejimde isabet
cokuyor" bulgusuyla celiski dogar mi? Yanit Katman A'nin
rejim-kirilimli okumasinda (esik tablosuna rejim sutunu eklenebilir).
Takvim (revize)
20.07 aksam: golge tetik + KCHOL hukmu + Katman A ilk 5 -> oturum
21.07 Sali: TUPRS-97 hukmu
22.07 Car:  Katman A TAM -> D1' karari + pSkorTaban secimi
23.07 Per:  PPK, kod yok
24-26.07:   D kapilari gecilirse Pine uygulamasi (v0.1 butce
kurallari: paralel hat, p3Enabled, ~40 statement, 1
alertcondition, plot yok)
27.07 hedef deploy -> Kulucka v2 (hukum ~07.09)
Kapi gecilemezse: deploy YOK, 18.08 hukum gunu yururlukte kalir.
