# ÖN KAYIT: H1–H3 hipotez testleri

**Kayıt tarihi:** 27.10.2026, sonuçlar görülmeden.
**Uygulayan betik:** `h_testleri.py`
**Kural:** Bu belge, betik ilk kez çalışmadan önce repoya commit edilir. Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar. Sonuç görüldükten sonra yapılan her değişiklik "ön kayıt değişikliği" olarak işaretlenir ve o sonuçlar keşif sayılır, hüküm sayılmaz. Her çalışma `data/h_testleri/deneme_kaydi.json` dosyasına eklenir; deneme sayısı gizlenmez.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

---

## Ortak tanımlar

| Konu | Tanım |
|---|---|
| Evren (birincil) | `config/universe.yml` içindeki 31 sembol. Alarm sisteminin evreni budur. TRMET ve TRALT için geçmiş kısa kalırsa eski kodlar (KOZAA, KOZAL) denenir. |
| Evren (sağlamlık) | `config/bist100_uyeler.txt`. Yalnızca raporlanır, hüküm vermez. |
| Fiyat | yfinance günlük, `auto_adjust=False`; fiyat bazlı, XU100 fiyat endeksiyle tutarlı. Bedelsizler `ma610_tarama.bolunme_duzelt` ile düzeltilir. |
| Temettü sağlamlığı | Aynı test temettü düzeltmeli kapanışla (`auto_adjust=True`) tekrarlanır. Yalnızca raporlanır. |
| Sektör sepeti | Evrende aynı sektördeki diğer hisselerin eşit ağırlıklı ortalaması; hissenin kendisi hariç. Sektörde tek hisse varsa evrenin geri kalanının eşit ağırlıklı ortalaması kullanılır. Sektör eşlemesi `alarm_karne.SEKTOR` ile aynıdır. |
| Maliyet | Gidiş-dönüş %0,25 (komisyon + kayma). Net getiri = brüt − 0,25. |
| Dönemler | Örneklem içi (IS): 01.01.2016–31.12.2022. Örneklem dışı (OOS): 01.01.2023–30.06.2026. Sonrası (01.07.2026–bugün) "taze dönem" olarak ayrı raporlanır, hükme girmez. |
| Kriz dışlaması | XU100'ün günlük değişiminin mutlak değeri ≥ %5 olan günlerde yeni pozisyon açılmaz (devre kesici / tek fiyat vekili). |
| Giriş / çıkış | Giriş, oluşum gününün kapanışı. Çıkış, tutma süresi sonundaki kapanış. Seans içi giriş modellenmez. |
| Anlamlılık eşiği | Üç birincil test olduğu için Bonferroni düzeltmesi: \|t\| > 2,39 (iki yönlü, p < 0,05 / 3). |

## Ortak geçme kriterleri (H1 ve H3)

Bir hipotez yalnızca **beşinin de** sağlanmasıyla GEÇER sayılır:

- **K1.** OOS döneminde birincil metriğin ortalaması > 0.
- **K2.** OOS t istatistiği > 2,39. H1'de gecikme sayısı tutma süresi − 1 olan Newey-West; H3'te ISO hafta kümelenmiş t.
- **K3.** Tüm dönemde (2016–30.06.2026) takvim yıllarının en az %60'ında yıllık ortalama > 0.
- **K4.** Tek sektör dışarıda bırakılarak test tekrarlandığında, her durumda OOS ortalama > 0 kalır.
- **K5.** IS ortalaması da > 0 (tutarlılık).

**Sonuç etiketleri:**
- GEÇTİ: beşi de sağlandı.
- ZAYIF: K1 ve K5 sağlandı ama diğerlerinden en az biri tutmadı.
- ELENDİ: diğer tüm durumlar.

Yalnızca GEÇTİ alan hipotez gölge alarm aşamasına geçer. Gölge aşaması 60 işlem günü sürer. Gölge aşamasında kalma kriteri: ortalama ≥ 0 ve t ≥ −1.

---

## H1: Kısa vadeli sektöre göre dönüş

**İddia:** Son 5 günde kendi sektörüne göre en çok geride kalan hisseler, sonraki 5 günde sektörlerini geçer.

**Dayanak:**
- Alarm karnesinde al alarmları sektöre göre T+3'te −0,29 (t −2,5).
- Çıkış alarmlarından sonra hisseler sektörü +2,45 geçti (t 2,9).

**Kurallar:**
- **Sinyal:** Her işlem günü t için `artik5 = hisse 5 günlük getiri − sektör sepeti 5 günlük getiri`.
- **Portföy:** O gün geçerli verisi olan hisseler (en az 10 hisse) `artik5`'e göre sıralanır. En düşük %20'lik dilim seçilir; en az 2 hisse olur. Eşit ağırlık.
- **Tutma süresi:** 5 işlem günü. Her gün yeni bir portföy oluşur; portföyler üst üste biner. Bu nedenle t istatistiği 4 gecikmeli Newey-West ile hesaplanır.
- **Birincil metrik:** Portföyün sektör sepetine göre net getirisi.
- **Raporlanan ama hüküm vermeyen metrikler:** XU100'e göre net, evren ortalamasına göre net, brüt değerler.
- **Sağlamlık ızgarası (yalnızca raporlanır, parametre seçmek için kullanılmaz):** geriye bakış {3, 5, 10} × dilim {%10, %20, %30} × tutma {3, 5, 10}. Birincil parametre (5, %20, 5) değiştirilemez.

## H2: Giriş zamanlaması (kapanış mı, seans içi alarm anı mı)

**İddia:** Aynı sinyalde kapanışta girmek, seans içinde alarm fiyatından girmekten daha iyidir.

**Dayanak:** Getirinin büyük bölümü gece oluşuyor. İlk 30 dakikadaki alarmlarda kapanış, alarm fiyatının ortalama %0,56 altında.

**Kurallar:**
- **A (hüküm veren):** `data/alarm_karne_olaylar.csv` içindeki YUKARI yönlü alarmlar alınır; aynı sembolde aynı gün tek olay sayılır.
  - `avantaj = (alarm_fiyat / kapanış − 1) × 100`. Pozitif değer, kapanışta girmenin daha ucuz olduğunu gösterir.
  - Gün kümelenmiş t hesaplanır.
  - Seans dilimine göre (10:00–10:30, 10:30–12:30, 12:30–16:00, 16:00–18:10, 18:10 sonrası) ayrı raporlanır.
  - **GEÇTİ:** ortalama avantaj > 0,10 puan **ve** t > 2,39.
  - **ELENDİ:** ortalama ≤ 0.
  - **ZAYIF:** diğer durumlar.
- **B (raporlanır, hüküm vermez):** 10 yıllık günlük veride evrenin gündüz (açılış→kapanış) ve gece (kapanış→ertesi açılış) getirileri, XU100'e göre ve yıl bazında.
- **Sınır:** A bölümünün verisi yalnızca Temmuz–Ekim 2026 alarmlarıdır, örneklem dışı ayrımı yoktur. GEÇTİ alırsa bile sonraki 60 işlem gününde gölge alarmla teyit edilmesi zorunludur.

## H3: Sert düşüş sonrası 10 günlük toparlanma

**İddia:** Bir günde %8 ya da daha fazla düşen hisse, sonraki 10 günde XU100'ü geçer.

**Dayanak:** Kurul raporundaki nominal bulgu: T+10'da +%2,64'e karşı koşulsuz taban +%1,81. Bu karşılaştırma göreli değildi.

**Kurallar:**
- **Olay:** Hissenin günlük fiyat değişimi ≤ −%8. Bedelsiz düzeltmesi yapılan gün olay sayılmaz. Kriz dışlaması uygulanır: XU100 aynı gün ≥ %5 hareket ettiyse olay alınmaz. Not: bu, piyasa geneli çöküş günlerini dışarıda bırakır; test hisseye özgü sert düşüşü ölçer.
- **Portföy:** Her olay gününde, o günün olay hisselerinden eşit ağırlıklı portföy kurulur. Giriş, olay günü kapanışı.
- **Tutma süresi:** 10 işlem günü.
- **Birincil metrik:** XU100'e göre net getiri. Sektör sepetine göre net ayrıca raporlanır.
- **t istatistiği:** Olay günü portföyleri ISO haftaya göre kümelenir.
- **Raporlanan ama hüküm vermeyen ek test:** XU100 günlük ≤ −%4 olan günlerden sonra XU100'ün 10 günlük getirisi, koşulsuz 10 günlük ortalamayla karşılaştırılır.

---

## Bilinen sınırlar (sonuç ne çıkarsa çıksın geçerli)

1. **Hayatta kalma yanlılığı.** Bugünkü üyeler geçmişe uygulanıyor. Bu, dönüş stratejisini (H1, H3) büyük ihtimalle olduğundan iyi gösterir: geçmişte batıp endeksten çıkan hisseler örneklemde yok.
2. **Tek veri kaynağı Yahoo.** Bedelsiz düzeltmesi yaklaşık bir yöntemdir.
3. **Fiyat limitleri.** Kapanışta taban fiyatta alım mümkündür. Ertesi gün taban serisi olursa çıkış gecikebilir; bu modellenmiyor.
4. **Açığa satış yok.** Bütün testler yalnızca uzun pozisyon içindir.
5. **Bu üç test ilk denemedir.** Hiçbiri geçmezse bu da bir sonuçtur. Yeni hipotez eklemek ancak Başkan kararıyla ve yeni bir ön kayıtla yapılır.
