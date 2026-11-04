# V163.0 ADAY gölge protokolü

**Kayıt tarihi:** 03.11.2026. **Güncelleme:** 04.11.2026 (11:00, hızlandırılmış plan).
**Süre:** **3 seans, 04–06.11.2026.** Altuğ 04.11'de onayladı; ilk süre 2 haftaydı.
**Geçiş:** Ölçütler sağlanırsa 07–08.11 hafta sonu. Piyasa kapalıyken alarmlar V163'e taşınır, V162.3 alarmları silinir. Pazartesi 09.11 açılışında webhook'ların "v163.0" ile geldiği ve sayıların normal olduğu kontrol edilir.
**Pine kaynağı:** `V163.0_BIST_IRE_FOCUS_ADAY.txt` (repo). Kaynak 04.11'de token sınırı düzeltmesiyle kaydedildi ve derlendi.

## Neden kısa

V163, V162.3'ün karar mantığını, alarm koşullarını ve plot sayısını değiştirmez. Eklenen tek hesap günlük oynaklıktır. Bu değer yalnızca günlük fiyatlardan türer ve Python tarafından arşivden birebir yeniden hesaplanabilir. Oynaklığın tahmin gücü (R1) 10 yıllık veriyle zaten ölçüldü. Bu yüzden gölge döneminin amacı ileriye dönük performans ölçümü değil, **teknik doğrulamadır**.

## V163.0'ın son hâli (V162.3'e göre)

| # | Değişiklik | Davranışa etkisi |
|---|---|---|
| V163-1 | Günlük EWMA oynaklık. `request.security(..., "D", ...)`, yalnızca tamamlanmış önceki gün, `ta.ema(getiri², 32)`. | Yalnızca panel. Toplam `request.security` çağrısı 17. |
| V163-2 | Kelly hesapları çıkarıldı. | Yok. Yalnızca varsayılanı KAPALI olan lot geri beslemesine giriyordu. |
| V163-3 | Panelde felaket sınırı bilgisi: `FEL <−%5> / <−%8>`. Referans, pozisyon varsa Pine'ın giriş fiyatı, yoksa kapanış. BIST fiyat adımına aşağı yuvarlanır. | Yalnızca panel. Emir, aracı kurumda kullanıcı tarafından girilir. |
| V163-4 | `pSkorTaban` 32'ye sabitlendi. | Bir grafikte farklı değer kayıtlıysa, o grafikte P3 eşiği değişir. |
| V163-5 | Webhook `schemaVersion` "v163.0" oldu. | Alan seti aynı; Pipedream değişikliği gerekmez. |
| V163-6 | **Token sınırı düzeltmesi.** İlk sürüm 80.084 / 80.000 token ile derlenmedi. Ardışık kayıp sayacı ile Kelly ve ardışık kayıp lot çarpanları çıkarıldı; ikisi de varsayılanı KAPALI olan lot geri beslemesine giriyordu. Kullanılmayan `_volNorm*` hesabı (ölü kod) çıkarıldı. Hedef oynaklık girdisi sabit 2,5 oldu. | Varsayılan davranış değişmedi. "İstatistiksel Lot Geri Beslemesi" açılırsa artık yalnızca rejim çarpanı uygulanır. |

**Panel satırı (`RISK (R1)`):**
- `VOL %x.x`: günlük oynaklık.
- `LOT x0.xx`: hedef 2,5 / VOL, 0,4 ile 1,6 arasında sınırlı.
- `FEL a / b`: −%5 ve −%8 seviyeleri.

**Hedef 2,5:** BIST 100 günlük EWMA oynaklık medyanı. 03.11 itibarıyla %2,83 (çeyrekler arası %2,23–3,53). Arşivden aylık hesaplanır; belirgin bir sapmada Pine'daki sabit güncellenir.

**TradingView bütçesi (04.11, derlenen sürüm):**
- Token sınırı 80.000. Kalan pay küçük; yaklaşık birkaç yüz token tahmin ediliyor.
- Plot sayısı 64 sınırında.
- `request.security` 17 / 40.

Yeni bir özellik ancak eşdeğer kod çıkarılarak eklenebilir. İlk aday, panelin "VOL-BT" satırıdır (Pine'ın kendi işlemlerinin geçmiş istatistiği).

## Kurulum

- V162.3 olduğu gibi kalır; bütün alarmlar ve webhook'lar ona bağlıdır.
- V163.0 ADAY yalnızca 5 sembolde, ayrı bir düzende açılır: THYAO, AKBNK, ASELS, EREGL, KCHOL.
- V163'e alarm kurulmaz. Böylece mükerrer webhook olmaz ve alarm kotası tüketilmez.

## Ölçütler (hepsi sağlanmalı)

| # | Ölçüt | Nasıl ölçülür | Eşik |
|---|---|---|---|
| G1 | Derleme ve çalışma | 5 grafikte hata (token, plot, zaman aşımı) yok | Sıfır hata |
| G2 | Oynaklık doğruluğu | Panelin VOL değeri 5 sembolde 3 farklı günde okunur. Claude aynı değeri `data/arsiv/gunluk` resmî günlük kapanışlarıyla hesaplar. | Mutlak fark ≤ 0,15 puan |
| G3 | Tekrar boyama yok | VOL gün içinde sabit kalır, yalnızca seans açılışında değişir | Gün içinde değişim yok |
| G4 | Mantık değişmedi | Aynı anda 5 sembolde V162.3 ve V163 panellerinde KARAR, KGS ve STATE karşılaştırılır | Birebir aynı (pSkorTaban 32 olan grafiklerde) |
| G5 | Felaket satırı | Referans × 0,95 ve × 0,92, BIST fiyat adımına aşağı yuvarlanmış | Doğru |

## Ölçüm kaydı

| Tarih | Sembol | Panel | Python | Fark | Not |
|---|---|---|---|---|---|
| 04.11 sabah | ASELS | VOL %3,2, LOT x0,77, FEL 327,5 / 317 | VOL ~%3,26 (60 dk arşivinden türetilmiş kapanışlarla, yaklaşık) | ~0,06 | **G5 doğru:** 344,75 × 0,95 = 327,51 → 327,50; × 0,92 = 317,17 → 317,00 (adım 0,25). **G1 derleme doğru.** G2 kesin ölçümü resmî günlük kapanışlarla yapılacak (arşivin 03.11 günlük dosyası Yahoo gecikmesi yüzünden eksikti; düzeltildi). |
| 04.11 ~10:50 | ASELS | VOL %3,2, LOT x0,77, FEL 334,25 / 323,75 (kapanış 352,00) | 02.11'e kadar %3,36 | — | **G3:** ASELS'te VOL ve LOT, yaklaşık 1 saat arayla ve fiyat 344'ten 352'ye çıkmışken değişmedi. **G5 doğru.** |
| 04.11 ~10:50 | THYAO | VOL %2,7, LOT x0,92, FEL 261,25 / 253 | %2,70 (02.11'e kadar) | ~0 | **G5 doğru.** |
| 04.11 ~10:50 | AKBNK | VOL %2,4, LOT x1,05, FEL 59,9 / 58,05 | %2,34 | ~0,06 | **G5 doğru.** Referans, Pine'ın açık simüle pozisyonunun giriş fiyatı (~63,10); kapanış değil. Tasarıma uygun. |
| 04.11 ~10:50 | KCHOL | VOL %2,0, LOT x1,22, FEL 188,2 / 182,3 | %2,04 | ~0 | **G5 doğru.** |
| 04.11 ~10:50 | EREGL | VOL %3,2, LOT x0,78, FEL 29,86 / 28,92 | %3,19 | ~0 | **G5 doğru.** |
| 04.11 ~10:50 | YKBNK, BIMAS (ek) | YKBNK VOL %2,6 / x0,97; BIMAS %2,5 / x1,02 | — | — | **G5 doğru** (33,28 / 32,22; 342,75 / 332). |

### G4 karşılaştırması (04.11 ~10:50, aynı grafikte V163 solda, V162.3 sağda)

| Sembol | Sonuç |
|---|---|
| ASELS, AKBNK, KCHOL, EREGL, YKBNK | ACTION, LIFE, TREND, KGS, EKLEME, RISK, STOP, BLOCK ve NOTE aynı. AKBNK'te DSS yüzdesi ve INVALID seviyesi bir fiyat adımı kadar farklı; aynı anda farklı tike göre çizilmiş olmalı. |
| THYAO | KGS A+97 / A+96; RISK MID / LOW; BLOCK "GEC" / "NONE"; NOTE "GEC GIRIS / KOVALAMA" / "GUC VAR / GIRIS KAPALI"; STOP, TP ve INVALID 0,25 TL farklı; DSS %3,77 / %3,68. **Bütün farklar 0,25 TL'lik bir fiyat farkıyla tutarlı** (275,00 / 274,75). THYAO o anda hızlı hareket ediyordu ve iki gösterge aynı ekranda farklı tiklerde güncellenmiş görünüyor. **Seans kapandıktan sonra tekrar karşılaştırılacak.** |
| BIMAS | Karar değerleri aynı. Ancak Pine'ın kendi geçmiş işlem sayaçları farklı: SH-BT N253 / N232, OOS N12 / N10, SEANS-BT N87 / N80. Diğer sembollerde bu sayaçlar birebir aynı (ASELS N263, THYAO N27, AKBNK N68). Muhtemel neden: iki göstergenin yüklendiği geçmiş bar sayısının farklı olması. **Kontrol:** sayfa yenilenir (F5) ve BIMAS yeniden karşılaştırılır. Sayaçlar eşitlenirse sebep yükleme farkıdır. Eşitlenmezse geçmişteki simüle pozisyonlar farklı demektir ve geçiş öncesinde incelenir. |

**Skor Tabanı kontrolü:** Ekran görüntülerindeki 8 V162.3 grafiğinin (ASELS, THYAO, AKBNK, KCHOL, EREGL, YKBNK, BIMAS ve V162.1) durum satırında "FULL 32" görünüyor, yani skor tabanı 32. Kalan grafiklerde de kontrol edilecek.

## Sonuç

## Hızlandırılmış takvim

| Gün | İş | Sorumlu |
|---|---|---|
| 04.11 | G1, G3, G4, G5 ekran görüntüleriyle. 30 V162.3 grafiğinde "Skor Tabanı" girdisinin 32 olduğunun kontrolü. | Altuğ |
| 05.11 sabah | G2: resmî günlük kapanışlarla oynaklık karşılaştırması (04.11 gecesi günlük arşiv) | Claude |
| 05–06.11 | THYAO kapanış sonrası G4 tekrarı; BIMAS sayfa yenileme kontrolü | Altuğ |
| 06.11 akşam | Geçiş kararı | Altuğ |
| 07–08.11 | Alarm taşıma | Altuğ |
| 09.11 açılış | Webhook ve alarm sayısı kontrolü | Claude |

## Sonuç

- **Hepsi sağlanırsa:** V163.0, V162.3'ün yerini alır. Alarmlar yeniden kurulur, webhook'lar "v163.0" ile gelir.
- **G1, G3 ya da G4 sağlanmazsa:** Düzeltilir ve gölge yeniden başlatılır.
- **Yalnızca G2 sağlanmazsa:** Hesap düzeltilir ve G2 tekrar ölçülür.

## Not: %5 kriz eşiği

R4'te zararlı çıkan "%5 kriz eşiği" canlı bir kural değil; yalnızca H1–H3 testlerinin bir parametresi (`h_testleri.KRIZ_ESIK`). Kaldırılacak bir şey yok. Bu kural ileride de benimsenmeyecek.
