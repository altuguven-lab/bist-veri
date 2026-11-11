# V163.0 ADAY gölge protokolü

**Kayıt tarihi:** 03.11.2026. **Güncelleme:** 11.11.2026 (geçiş tamamlandı; V163.1 ve V163.2 ara sürümleri).
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

### G2 – resmî kapanışlarla (05.11, Claude)

Yöntem: Günlük kapanışlar, 03.11'e kadar 60 dk arşivinin gün sonu barlarından türetildi. 27.10, 28.10, 30.10, 02.11 ve 03.11 için `data/arsiv/gunluk`'taki resmî kapanışlar kullanıldı (03.11 kapanışları TradeMaster "Ö.Gün.K." ile birebir aynı). Hesap: basit getiri, `ema(getiri², 32)`, α = 2/33, 729 işlem günü. Panelin 04.11 değeri, 03.11'e kadarki veriyi kullanır (`[1]` + lookahead).

| Sembol | Panel 04.11 | Python (03.11'e kadar) | Fark | Sonuç |
|---|---|---|---|---|
| THYAO | 2,7 | 2,67 | −0,03 | Geçti |
| AKBNK | 2,4 | 2,35 | −0,05 | Geçti |
| KCHOL | 2,0 | 1,98 | −0,02 | Geçti |
| EREGL | 3,2 | 3,19 | −0,01 | Geçti |
| ASELS | 3,2 | 3,26 | +0,06 | Geçti |

**G2 1. gün: 5/5 geçti** (eşik ≤ 0,15; panel tek ondalık gösterdiği için ±0,05 yuvarlama payı fark içinde).

**05.11 için beklenen panel değerleri** (04.11 kapanışı yerine 17:45 barı kullanıldı; resmî kapanış bu gece arşive girince kesinleşir): THYAO ~3,5; AKBNK ~2,8; KCHOL ~2,1–2,2; EREGL ~3,2; ASELS ~3,3. THYAO'daki sıçrama 04.11'deki ~%9,6'lık yükselişten gelir; EWMA'nın beklenen davranışıdır.

### G2 – 2. ve 3. gün (06.11, Claude)

| Sembol | 05.11 panel | Python (04.11 resmî) | Fark | 06.11 panel | Python (05.11 17:45 barı) | Fark |
|---|---|---|---|---|---|---|
| THYAO | 3,6 | 3,56 | −0,04 | 3,5 | 3,47 | −0,03 |
| AKBNK | 2,8 | 2,76 | −0,04 | 2,7 | 2,70 | 0 |
| KCHOL | 2,2 | 2,14 | −0,06 | 2,1 | 2,08 | −0,02 |
| EREGL | 3,2 | 3,18 | −0,02 | 3,2 | 3,20 | 0 |
| ASELS | 3,2 | 3,26 | +0,06 | 3,6 | 3,64 | +0,04 |

**G2: 3 gün × 5 sembol = 15/15 geçti.** En büyük fark 0,06. 3. gün, 05.11 resmî kapanışları arşive girince yeniden doğrulanacak (fark beklenmiyor).

**G3:** VOL her gün seans açılışında değişti (örnek ASELS 3,2 → 3,6; THYAO 3,6 → 3,5), gün içinde sabit kaldı (ASELS 04.11, EREGL 05.11 13:49 → 14:11). Geçti.

**G5 (06.11):** THYAO ref 289,75 → 275,25 / 266,50; ASELS ref 333,50 → 316,75 / 306,75; AKBNK ref 66,20 → 62,85 / 60,90; KCHOL ref 200,0 → 190 / 184; EREGL ref 30,60 → 29,06 / 28,14. Hepsi doğru.

**G4 (05–06.11):** ASELS, THYAO (05.11), AKBNK, KCHOL, EREGL (F5 sonrası) birebir aynı. 06.11'de THYAO'da yalnızca geçmiş işlem sayaçları farklı (SH-BT N27/N30, ANA N13/N14 vb.); karar satırları aynı. BIMAS ve EREGL'de aynı durum F5 ile kapanmıştı: yükleme (geçmiş bar sayısı) farkı. Sayaçlar alarm koşullarına girmez.

**Skor Tabanı kontrolü:** Ekran görüntülerindeki 8 V162.3 grafiğinin (ASELS, THYAO, AKBNK, KCHOL, EREGL, YKBNK, BIMAS ve V162.1) durum satırında "FULL 32" görünüyor, yani skor tabanı 32. Kalan grafiklerde de kontrol edilecek.

## Hızlandırılmış takvim

| Gün | İş | Sorumlu |
|---|---|---|
| 04.11 | G1, G3, G4, G5 ekran görüntüleriyle. 30 V162.3 grafiğinde "Skor Tabanı" girdisinin 32 olduğunun kontrolü. | Altuğ |
| 05–06.11 | G2: **15/15 geçti.** G3, G4, G5 geçti (THYAO 06.11 sayaç farkı için F5 kontrolü). | Claude / Altuğ |
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


## Geçiş ve ara sürümler (09–11.11.2026)

| Tarih | Olay | Sonuç |
|---|---|---|
| 06.11 | G1–G5 sağlandı (G2 15/15) | Geçiş onayı |
| 06–09.11 | V163.0 alarmları kuruldu | GUNLUK_OZET alarmlarında webhook adresi eski Pipedream adresine (`eo3ivw22…`) gidiyordu; 06.11 akşamı ~29 kayıt kayboldu. Adres `eobd0rr5ue7os4m` olarak düzeltildi. |
| 09–10.11 | V163.0 giriş alarmları hiç gelmedi | Neden: grafiklerde "Portföyde Pozisyon Var" açıktı; TradingView alarmı kurulduğu andaki girdileri kullanır, giriş modu kapalı kaldı. |
| 10.11 | **V163.1** | (1) Kutu artık giriş sinyallerini susturmuyor (karar ve `_newEntryMode` kutudan bağımsız; kutu kapalıyken davranış V163.0 ile birebir). (2) 22 `alertcondition` → `alert()`, sembol başına tek alarm. (3) Yeni webhook alanları: skor0, kgs0, relvol0, manuel_poz, poz_kaynak, karar, faktor. (4) Token: CORE alarm üçlüsü (FULL modda hiç üretilmiyordu), ölü istatistik kovaları, panelin VOL-BT, FAKTÖR-BT, SEANS-BT satırları çıkarıldı; panel 15 → 13 satır. Faktör/seans kırılımı Python karnesine taşındı. |
| 10.11 | Pipedream v5 | Yeni alanlar arşive yazılıyor; aynı eventId tekrar yazılmıyor. |
| 11.11 | V163.1 alarmları 10:00'da "çok sık tetiklenme" ile durduruldu | Neden: `alert.freq_all` + `barstate.isconfirmed`; TradingView kapanmış barı yeniden hesaplayınca aynı sinyaller tekrar gitti (10.11'deki çift gönderim de buydu). |
| 11.11 | **V163.2** + Pipedream v6 | Sembol başına bar başına **tek webhook**; sinyaller `"signals"` alanında virgüllü liste, sıklık `alert.freq_once_per_bar_close`. Pipedream listeyi ayrı kayıtlara bölüyor (eventId = sembol\|interval\|sinyal\|barTime), tek commit'te yazıyor. 11.11 10:30'dan itibaren çalışıyor; tekrar yok. |

**Doğrulanan:** 10.11 18:11 GUNLUK_OZET 32/32 sembol (ilk kez eksiksiz). V163.2 ile OTKAR'ın aynı bardaki iki sinyali (P3_HACIM_BEKLE, P4_HAZIRLIK) tek commit'te iki kayıt olarak yazıldı.

**Karne ve H12 sürekliliği:** Kayıt formatı değişmedi (her sinyal ayrı kayıt, aynı alan adları). "Portföyde Pozisyon Var" kutusu kapalıyken sinyal tanımları V162.3/V163.0 ile aynı; H12 ön kaydı etkilenmez. V163.1+ ile ilk kez veri üreten türler (P3_HACIM_BEKLE, IC_STOP, TASIMA, KAR_KORU) karnede ayrı izlenir; yönleri varsayımdır.

**TradingView bütçesi (V163.2):** Token sınırının altında (tam sayı yalnız aşımda görünür). Plot 64, `request.security` 17/40.
