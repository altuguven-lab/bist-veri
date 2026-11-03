# ÖN KAYIT: Risk bataryası R1–R4 (Pine öncesi zorunlu testler)

**Kayıt tarihi:** 03.11.2026. Kayıt yazılırken bu dört testin hiçbir sonucu görülmedi.
**Uygulayan betik:** `risk_bataryasi.py`

**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/risk/deneme_kaydi.json` dosyasına eklenir.
- Sonuç görüldükten sonra yapılan her değişiklik ön kayıt değişikliği sayılır. O sonuç keşiftir, hüküm değildir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## Neden bu dört test zorunlu

Pine'a risk modülü eklemeden önce dört sorunun cevabı gerekiyor. Her biri bir Pine modülünün dayanağıdır:

| Test | Soru | Geçerse Pine'a eklenecek modül |
|---|---|---|
| R1 | Hissenin yakın gelecekteki oynaklığı bugünden tahmin edilebiliyor mu? | Oynaklık göstergesi; R2 ve R3'ün temeli |
| R2 | Pozisyonları oynaklığa göre boyutlandırmak, eşit TL dağıtıma göre riski azaltıyor mu? | Önerilen lot |
| R3 | Stop, rastgele bir çıkışa göre zararı daha iyi sınırlıyor mu? Hangi tip ve mesafe? | Stop tipi ve mesafesi |
| R4 | Piyasa geneli bir filtre, toplam pozisyonu azaltarak büyük düşüşleri sınırlıyor mu? | Kriz modu |

**Pine öncesi zorunlu sayılmayanlar ve gerekçeleri:**
- **R5 (çıkış sinyalleri):** POZ_AZALT'ın tersine çalıştığı canlı karnede zaten ölçüldü (32 olay, t −3,12). Pine mantığı Python'da birebir kurulamaz. Zararlı bir sinyali devre dışı bırakmak düşük riskli bir karardır.
- **R6 (yoğunlaşma) ve R7 (işlem sıklığı):** Bilgi amaçlıdır, Pine modülüne doğrudan bağlanmaz. Sonra yapılır.

**Testlerin genel yaklaşımı:**
- Yönü tahmin edemediğimiz için testler yön varsaymaz. Giriş günleri sabit bir takvimle seçilir ve evren bütün BIST 100 hisseleridir.
- Ölçütler ortalama getiri değil; maksimum düşüş, CVaR %5 (en kötü %5'lik günlerin ya da işlemlerin ortalaması) ve oynaklıktır.
- Plasebo her testte hükmün parçasıdır.

## Ortak veri

| Konu | Tanım |
|---|---|
| Evren | Her gün o gün geçerli dönemin yeniden kurulmuş XU100 üyeleri (`data/endeks_uyelik/donemsel.json`; `donem_bas` ≤ gün olan son dönem, ilk dönemden önce `ONCESI_` listesi). Bu sayede hayatta kalma yanlılığı büyük ölçüde giderilmiş olur. `config/kapsam_disi.txt` hisseleri hariçtir. |
| Fiyat | yfinance günlük açılış, yüksek, düşük ve kapanış, `auto_adjust=False`. Bedelsizler `ma610_tarama.bolunme_duzelt` ile kapanıştan bulunan çarpanla dört fiyata birden uygulanır. Başlangıç 2015-09-01. |
| Getiri | Kapanıştan kapanışa günlük getiri. Mutlak değeri %50'yi aşan günlük getiri veri hatası sayılır ve boş bırakılır. |
| ATR | 14 günlük ortalama gerçek aralık. Gerçek aralık = max(Y−D, \|Y−Ö.K\|, \|D−Ö.K\|), Ö.K = önceki kapanış. Yalnızca o güne kadarki verilerle hesaplanır. |
| Dönemler | Örneklem içi (IS) 2016-07-01 – 2022-12-31; örneklem dışı (OOS) 2023-01-01 – son veri. |
| Maliyet | Gidiş-dönüş %0,25. Tek yön işlem, devir başına %0,125. |
| Rastgelelik | Tohum 20261103. |

## R1 — Oynaklık tahmini

- **Örnekleme:** Her haftanın son işlem günü (t).
- **Tahminciler** (yalnızca t'ye kadarki bilgi):
  - s20: son 20 günün günlük getiri standart sapması.
  - s60: son 60 günün günlük getiri standart sapması.
  - ATR14/kapanış.
  - EWMA: λ = 0,94 üstel ağırlıklı oynaklık.
- **Hedef:** t+1 ile t+20 arasındaki günlük getirilerin standart sapması. En az 15 geçerli gün gerekir.
- **Ölçüm:** Her hafta, o haftanın üyeleri arasında tahminci ile hedefin Spearman sıra korelasyonu hesaplanır (en az 30 hisse). Haftalık korelasyon serisinin ortalaması ve Newey-West t'si (gecikme 4) alınır.
- **Seçim:** IS dönemindeki ortalama korelasyonu en yüksek tahminci "seçilen tahminci" olur. R2 ve R3 bu tahminciyi kullanır.
- **Plasebo:** Seçilen tahminci, her hafta hisseler arasında rastgele karıştırılır.
- **GEÇTİ şartlarının hepsi:**
  1. Seçilen tahmincinin IS ve OOS ortalama korelasyonları ≥ 0,30.
  2. OOS Newey-West t > 2,58.
  3. Plasebo ortalama korelasyonu ile |t| < 2,58.
- **Ek bilgi:** XU100'ün kendi 20 günlük oynaklığının sonraki 20 günü tahmini (zaman serisi korelasyonu).

## R2 — Oynaklığa göre pozisyon büyüklüğü

- **Portföyler:** Her ay sonu kapanışında o günün üyeleri ve seçilen tahminci kullanılır. Ağırlıklar sonraki ay boyunca sabit tutulur (günlük yeniden dengeleme varsayımı).
  - **EW:** Eşit ağırlık, 1/N.
  - **IV:** Ağırlık, tahmin edilen oynaklığın tersiyle orantılı. Tek hisse ağırlığı 3/N ile sınırlanır, sonra ağırlıklar yeniden ölçeklenir.
- **Diğer kurallar:**
  - Ay içinde verisi kesilen hissenin kalan günlerdeki getirisi 0 sayılır.
  - Maliyet: ay sonunda Σ|yeni ağırlık − eski ağırlık| × %0,125.
- **Ölçütler (IS ve OOS ayrı):** Yıllık bileşik getiri, yıllık oynaklık, maksimum düşüş, günlük CVaR %5, getiri/oynaklık.
- **Bootstrap:** Tüm dönem günlük getiri çiftleri üzerinden 1.000 tekrar, ortalama blok uzunluğu 20 gün olan durağan blok bootstrap. IV'nin maksimum düşüşünün EW'den küçük çıktığı tekrar oranı hesaplanır.
- **Plasebo:** IV ağırlıkları her ay hisseler arasında rastgele karıştırılır.
- **GEÇTİ şartlarının hepsi:**
  1. IS'de ve OOS'ta ayrı ayrı: IV oynaklığı < EW oynaklığı, IV maksimum düşüşü < EW maksimum düşüşü, IV CVaR'ı EW'den daha az negatif.
  2. IS'de ve OOS'ta IV getiri/oynaklık ≥ 0,9 × EW getiri/oynaklık.
  3. Bootstrap oranı ≥ %95.
  4. Plasebo, şart 1'in üçünü birden hem IS'de hem OOS'ta **sağlamamalı**. Sağlarsa hüküm SUPHELI olur.

## R3 — Stop kuralları

- **İşlem kurgusu:** Yön bilgisi olmadan rastgele girişlerin testi. Bugünkü bilgimiz, yani yön kenarının olmadığı durum, tam olarak budur.
  - Her üye hisse için, 2016-07-01'den itibaren her 5. işlem gününün açılışında giriş yapılır. Giriş takvimi sabittir, hisseden bağımsızdır.
  - Azami tutma süresi 20 işlem günüdür. Stop çalışmazsa çıkış 20. günün kapanışından yapılır.
  - ATR, giriş gününden önceki kapanışa kadarki 14 günlük değerdir.
- **Varyantlar:**

| Kod | Kural |
|---|---|
| V0 | Stop yok |
| S5 / S8 | Giriş fiyatının %5 / %8 altı, sabit |
| A15 / A2 / A3 | Giriş − 1,5 / 2 / 3 × ATR, sabit |
| T2 / T3 | İz süren stop: max(önceki stop, girişten beri en yüksek kapanış − 2 / 3 × giriş ATR'si). Başlangıç değeri giriş − 2 / 3 × ATR. Gün sonunda güncellenir, ertesi gün geçerli olur. |

- **Stop çalışması:**
  - Bir günün açılışı stopun altındaysa (giriş günü hariç, açılış boşluğu) çıkış açılış fiyatından yapılır.
  - Değilse ve günün düşüğü stopa değdiyse çıkış stop fiyatından yapılır.
  - Giriş günü de stopa değebilir.
- **İşlem getirisi:** çıkış / giriş − 1 − %0,25.
- **Ölçütler (varyant başına, IS ve OOS):** İşlem sayısı, ortalama, medyan, standart sapma, CVaR %5 (en kötü %5 işlemin ortalaması), en kötü işlem, stopla çıkış oranı, ortalama tutma günü.
- **Plasebo (ardışık bağımlılığı yok edilmiş fiyatlar):**
  - Her hissenin kendi günlük (açılış, yüksek, düşük, kapanış) / önceki kapanış oranları, rastgele ve iadeli olarak yeniden örneklenir. Bu sentetik fiyatlarda oynaklık, kalın kuyruklar ve gün içi şekil korunur; ortalamaya dönüş, momentum ve boşlukların kümelenmesi yok olur.
  - Aynı işlemler ve aynı varyantlar bu fiyatlarla yeniden çalıştırılır.
  - Böylece stopun mekanik etkisi (zararı kesmesi) ile BIST'e özgü etkisi (dipte sattırması ya da boşluktan geçmesi) birbirinden ayrılır.
  - Gerekçe: Tasarım aşamasında sahte, etkisiz fiyatlarla yapılan denemede "rastgele zamanda çıkış" plasebosu her stop tarafından mekanik olarak yeniliyordu. Bu yüzden ayırt edici değildi ve sonuç görülmeden yukarıdaki plaseboyla değiştirildi.
- **Seçim (yalnızca IS):** V0'a göre CVaR iyileşmesi en büyük olan varyant seçilir. Şart: ortalama getirisi V0 ortalamasından en fazla 0,30 puan düşük olmalı.
- **GEÇTİ (seçilen varyant için OOS'ta, şartların hepsi):**
  1. CVaR %5, V0'a göre en az %25 iyileşir; yani büyüklüğü V0'ınkinin 0,75 katı ya da daha azdır.
  2. Ortalama ≥ V0 ortalaması − 0,30 puan.
  3. Stopun gerçek veride ortalamaya maliyeti (varyant − V0), plasebodaki maliyetinden en fazla 0,20 puan büyüktür. Yani BIST'te stop, mekanik olarak beklenenden belirgin biçimde pahalı değildir.
- **Hüküm anlamları:**
  - Şart 1 sağlanıp şart 3 sağlanmazsa: **STOP_PAHALI**. Stop kuyruğu kesiyor, ama BIST'te dipte sattırma ya da boşluk etkisi yüzünden beklenenden çok getiri kaybettiriyor.
  - Diğer durumlarda: **KENAR_YOK**.
- **Ek bilgi:** Ortalama getiri farkının giriş günü kümelenmiş t'si.

## R4 — Piyasa geneli kriz filtresi

- **Taban:** Üyelerden oluşan eşit ağırlıklı günlük sepet (R2'deki EW). Ek bilgi olarak XU100 endeksinin kendisi de taban alınır.
- **Filtreler:** t günü kapanışındaki XU100 verisiyle hesaplanır, t+1 getirisine uygulanır.

| Kod | Kural | Pozisyon oranı |
|---|---|---|
| F1 | XU100 kapanışı < 200 günlük basit ortalama | %50 |
| F2 | XU100 20 günlük oynaklığı > son 252 gündeki 20 günlük oynaklıkların %80'lik dilimi | %50 |
| F3 | XU100 günlük mutlak değişimi ≥ %5 (sistemin mevcut kriz eşiği) → sonraki 5 gün | %50 |
| F4 | F1, F2 veya F3'ten herhangi biri | %50 |

- **Nakit getirisi:** Birincil hesapta 0'dır. Bu, filtre aleyhine muhafazakâr bir varsayımdır. Ek bilgi olarak, EVDS erişimi varsa TP.APIFON4 (TCMB ağırlıklı ortalama fonlama maliyeti) / 365 ile de hesaplanır.
- **Maliyet:** |Δpozisyon oranı| × %0,125.
- **Ölçütler:** R2 ile aynı.
- **Plasebo:** Filtrenin günlük pozisyon oranı serisi 500 kez rastgele miktarda dairesel kaydırılır. Böylece azaltılmış pozisyonda geçen süre ve kümelenme korunur, yalnızca zamanlama rastgele olur.
- **GEÇTİ (her filtre için ayrı, şartların hepsi):**
  1. IS'de ve OOS'ta maksimum düşüş, tabana göre en az %20 azalır.
  2. IS'de ve OOS'ta CVaR iyileşir.
  3. Tüm dönem maksimum düşüşü, plasebo maksimum düşüşlerinin en az %95'inden iyidir.
- Getiri bedeli raporlanır, hükmü değiştirmez.

## Raporlanacaklar

- Her testin hükmü ve tabloları.
- Fiyat kapsaması: üyelerin kaçının fiyatı bulundu.
- Seçilen tahminci ve seçilen stop varyantı.
- Pine uygulama notları (aşağıdaki sınırlar çerçevesinde).

## Pine ve TradingView sınırları (tasarım kısıtı)

Hüküm vermez, uygulama planını sınırlar. V162.3'teki mevcut kullanım:

| Kaynak | Sınır | V162.3 kullanımı | Sonuç |
|---|---|---|---|
| `plot`, `plotshape` ve benzeri çağrılar | 64 | Yaklaşık 61 | Yeni görsel çıktı ancak eskisi kaldırılarak eklenebilir |
| `request.security` çağrısı | 40 | 16 | Günlük ATR ve oynaklık için tek bir tuple çağrısı yeterli: `request.security(syminfo.tickerid, "D", [...])` |
| Üst düzey ifade sayısı ("script too long") | Yaklaşık 1.140 (deneyimle) | Tavanda | Risk modülü ancak yön puanlama kodu sadeleştirilerek eklenebilir |
| Webhook yer tutucuları | Yalnızca ilk 20 plot | İndeks 1–7 kullanımda | Yeni webhook alanı ilk 20 plot içine yerleşmeli |
| `max_bars_back` | Betikte 150 | 150 | 200 günlük ortalama gibi uzun pencereler günlük seriden `request.security` ile alınmalı; 15 dakikalık grafikte 150 bar yetmez |
| Grafik başına gösterge ve aktif alarm sayısı | Üyelik planına bağlı (Plus) | — | Yeni alarm eklemek yerine mevcut alarm sınıfları dönüştürülmeli; güncel plan sınırı TradingView'den teyit edilecek |
| Etiket, çizgi ve tablo | Betikte 100 | — | Değişiklik gerekmiyor |

**Önemli uyumsuzluk:** Pine 15 dakikalık grafikte çalışıyor ve stopu 15 dakikalık ATR ile hesaplıyor. R1–R4 günlük veriyle yapılıyor. Bu yüzden testler geçerse Pine'daki risk modülü günlük ATR ve oynaklığı `request.security(..., "D", ...)` ile almalıdır. Mevcut 15 dakikalık ATR stopu bu testlerin kapsamında değildir.

## Sınırlılıklar

- Hacim ve likidite verisi kullanılmıyor.
- Stoplar günlük veriyle test ediliyor; gün içi sıralama (önce yüksek mi düşük mü) bilinmiyor. Yalnızca açılış boşluğu ve düşük fiyat kullanılıyor.
- Ay içinde verisi kesilen hisselerin kalan getirisi 0 sayılıyor.
- Nakit getirisinin 0 alınması R4'ün getiri bedelini olduğundan büyük gösterir.
