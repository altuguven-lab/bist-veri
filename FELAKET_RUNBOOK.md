FELAKET RUNBOOK - Ariza/Kurtarma Rehberi
Amac: Herhangi bir katman coktugunde, bu sohbetlerin gecmisini aramadan
sistemin dakikalar icinde ayaga kaldirilmasi. Senaryo bazli, sirali adimlar.
Mimari hatirlatma
```
TradingView alarmlari ──► Pipedream (BIST TradingView Koprusu) ──► data/tv_alerts_latest.json
Yahoo Finance ──► fetch_bist.py (update.yml, 15dk seans ici) ──► data/bist_quotes.json + bist_intraday.json
RSS ──► fetch_news.py (haber_update.yml, 30dk 7/24) ──► data/haber_akisi.json
saglik_kontrol.py (saglik_kontrol.yml, gunde 2x) ──► ariza durumunda GitHub Issue
```
SENARYO A: Pipedream erisilemez / workflow silindi
pipedream.com'da yeni workflow: HTTP / Webhook trigger olustur.
Code adimi (Node.js) ekle, icerigini repodaki `pipedream_kod_adimi.js`
dosyasindan aynen yapistir. GitHub hesabini props alanindan bagla.
Deploy et; YENI webhook URL'sini not al.
TradingView'de TUM aktif alarmlari ac -> Bildirimler -> Webhook URL alanini
yeni adresle degistir (alarm basina ~10 sn).
Test: "Generate Event" ile sahte POST -> GitHub'da yeni commit dogrula.
SENARYO B: GitHub Actions kosmiyor (kota/devre disi)
Repo -> Settings -> Actions: etkin mi ve dakika kotasi dolu mu bak.
Kota doluysa: ay basini bekle veya cron sikligini azalt
(update.yml */15 -> */30; haber */30 -> saatlik).
Workflow "disabled by inactivity" ise (60 gun push olmayinca olur):
Actions sekmesinden Enable'a bas.
SENARYO C: Yahoo/yfinance veri vermiyor
`bist_quotes.json` -> `basarili_cekim` dusukse hangi sembollerin
eksik oldugunu stderr loglarindan (Actions kosum sayfasi) bul.
Tek sembolse: kod/unvan degisikligi olabilir -> `ESKI_KOD_YEDEK`
sozlugune eski kodu ekle (TRMET/KOZAA ornegi).
Toplu cokusse: yfinance surumu -> requirements.txt'te surum sabitle/yukselt,
Actions'i elle kostur.
SENARYO D: Haber kaynagi oldu
`haber_akisi.json` -> `kaynak_sagligi` alaninda 0 veren kaynagi bul.
RSS adresi degismis olabilir: kaynagin sitesinden yeni RSS'i bul,
`fetch_news.py` KAYNAKLAR listesinde guncelle.
Kaynak kalici oluyse satiri sil - script zaten kaynak dususlerine dayanikli.
SENARYO E: TradingView gosterge/alarm sorunlari
Guncel .pine dosyalari Claude sohbet ciktilarinda ve surum kaydi
SURUM_NOTLARI.md'de. Pine Editor'e komple yapistir -> Save.
MANTIK degisikligi iceren her guncellemeden sonra alarmlar
Duzenle -> Kaydet turuyla yeni koda baglanir (kozmetikte gerekmez).
Alarm listesi tamamen kaybolduysa: katman planina gore yeniden kur -
pozisyon hisseleri: ACIL_CIK, POZ_AZALT, KAR_KORU, TASIMA, EKLEME_ADAYI;
aday hisseler: P1_KALITELI_AL, P1_AL, P2_DIP_DONUS, P2_DESTEK_DONUS;
webhook URL ve "Her cubuk kapanisinda bir kez" ayarlariyla.
SENARYO F: tv_alerts dosyasi bozuldu (gecersiz JSON)
Dosyanin History'sinden son saglikli commit'i bul -> o surumu geri yukle
(dosya sayfasi -> History -> ilgili commit -> ... -> View file -> kopyala).
Pipedream tarafinda degisiklik gerekmez; bir sonraki sinyal normal ekler.
Iletisim/izleme
Ariza bildirimi: GitHub Issues (etiket: saglik) + e-posta bildirimi.
Manuel saglik kontrolu: Actions -> Saglik Kontrolu -> Run workflow.
