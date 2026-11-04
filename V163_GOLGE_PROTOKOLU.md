# V163.0 ADAY gölge protokolü

**Kayıt tarihi:** 03.11.2026. **Güncelleme:** 04.11.2026.
**Süre:** 2 hafta (10 işlem günü), 04.11 – 17.11.2026.
**Ara kontrol:** 5. işlem günü (10.11).
**Pine kaynağı:** `V163.0_BIST_IRE_FOCUS_ADAY.txt` (repo). Kaynak 04.11'de token sınırı düzeltmesiyle kaydedildi ve derlendi.

## Neden 2 hafta

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
| 04.11 | ASELS | VOL %3,2, LOT x0,77, FEL 327,5 / 317 | VOL ~%3,26 (60 dk arşivinden türetilmiş kapanışlarla, yaklaşık) | ~0,06 | **G5 doğru:** 344,75 × 0,95 = 327,51 → 327,50; × 0,92 = 317,17 → 317,00 (adım 0,25). **G1 derleme doğru.** G2 kesin ölçümü resmî günlük kapanışlarla yapılacak (arşivin 03.11 günlük dosyası Yahoo gecikmesi yüzünden eksikti; düzeltildi). |

## Sonuç

- **Hepsi sağlanırsa:** V163.0, V162.3'ün yerini alır. Alarmlar yeniden kurulur, webhook'lar "v163.0" ile gelir.
- **G1, G3 ya da G4 sağlanmazsa:** Düzeltilir ve gölge yeniden başlatılır.
- **Yalnızca G2 sağlanmazsa:** Hesap düzeltilir ve G2 tekrar ölçülür.

## Not: %5 kriz eşiği

R4'te zararlı çıkan "%5 kriz eşiği" canlı bir kural değil; yalnızca H1–H3 testlerinin bir parametresi (`h_testleri.KRIZ_ESIK`). Kaldırılacak bir şey yok. Bu kural ileride de benimsenmeyecek.
