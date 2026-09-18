# UPM_V1 POZİSYON SÖZLEŞMESİ

**Durum:** TASLAK — Faz 0 çıktısı, kurul onayı bekliyor
**Tarih:** 17.09.2026
**Kapsam:** V162.1c'nin dört ayrı pozisyon/yaşam-döngüsü kaynağını (`_posOpen`, `_v112*`, `portfolioPosition`, `_smState`) tek, tutarlı bir modele (Unified Position Model — UPM) bağlamanın kuralları
**Bağlı belgeler:** [[kulucka-protokolu]], V162.1_YAMA_17.09.txt, dış kurul incelemesi (17.09.2026)
**Kırmızı çizgi:** Bu belge onaylanana kadar canlı davranış DEĞİŞMEZ. Faz 0 salt tasarım/dondurma aşamasıdır — kod yazılmaz.

---

## 0. Neden bu sözleşme var

V162.1c'de dört pozisyon/istatistik kaynağı paralel çalışıyor:

| Kaynak | Şu an ne yapıyor | Sorun |
|---|---|---|
| `_posOpen` | İç işlem motoru: giriş, stop, TP, fill, PnL | En doğru kaynak (17.09 düzeltmeleriyle), ama gerçek karara (WR/PF/Kelly) bağlı değil |
| `_v112*` | WR/PF/Kelly/`regimeHistMult`'ı besliyor — **gerçek pozisyon boyutunu belirliyor** | Çıkış tanımı (`_smState=="SELL"` / panicSell / distribution) stop fiyatına hiç bakmıyor |
| `portfolioPosition` | Manuel pozisyon var/yok bilgisi | Giriş fiyatı, stop, zaman bilgisi taşımıyor |
| `_smState` | NEUTRAL→WATCH→PREP→BUY→HOLD→SELL sinyal fazı | Pozisyon kaynağı OLARAK kullanılmamalı (bkz. Madde 1) |

Bu belge, bu dört kaynağı **tek bir kanonik arayüze** indirmenin kurallarını, önce kod yazmadan, dondurur.

---

## 1. Temel ilke: `_smState` pozisyon kaynağı DEĞİLDİR

`_smState` yalnızca **sinyal/piyasa fazını** anlatır (NEUTRAL → WATCH → PREP → BUY → HOLD → SELL). BUY veya HOLD durumu, gerçek bir işlemin açıldığını KANITLAMAZ.

Gerçek pozisyon ayrı bir yaşam döngüsüdür: **FLAT → OPEN → REDUCED → CLOSED**.

Bu ikisi ilişkili olabilir (bir sinyal fazı geçişi bir pozisyon olayını tetikleyebilir) ama **asla aynı değişken üzerinden okunmaz.**

---

## 2. Source of truth: sabit değil, mod bazlı

Tek ve sabit bir kaynak seçilmez. Otorite, çalışma moduna göre belirlenir:

| Mod | Otorite | Davranış |
|---|---|---|
| `LEGACY` | Mevcut sistemler (`_posOpen`/`_v112`/`portfolioPosition` paralel) | Hiçbir karar değişmez — bugünkü hal |
| `SHADOW` | UPM resolver hesaplar ama UYGULAMAZ | Yalnız karşılaştırma/loglama |
| `INTERNAL_SIM` | Unified internal position (`_posOpen` temelli, 17.09 düzeltmeleriyle) | Simülasyon ve araştırma |
| `MANUAL_LIVE` | Manuel/harici portföy verisi | Canlı karar desteği |
| `ENFORCE` | Unified sistem tam otorite | Geçiş sonrası nihai durum |

```
positionResolverMode = input.string("LEGACY", options=["LEGACY","SHADOW","INTERNAL_SIM","MANUAL_LIVE","ENFORCE"])
```

**Kural:** Açık pozisyon varken mod değişimine izin verilmez. Değişim istenirse kullanıcıya açıkça sorulur: `ADOPT POSITION` / `CLOSE POSITION` / `CANCEL MODE CHANGE`.

**Net karar (bu sözleşmenin donduğu hali):**
- Canlıda: `MANUAL_LIVE` otorite olur.
- Simülasyon/backtest'te: `INTERNAL_SIM` (`_posOpen` temelli) otorite olur.
- `_v112` hiçbir zaman canlı pozisyon otoritesi OLMAZ — yalnız araştırma gölgesi (eski karar evrenini ölçmek, legacy/unified karşılaştırması, araştırma metrikleri).
- `_smState` sinyal fazı olarak kalır, hiçbir modda pozisyon kaynağı sayılmaz.

**MANUAL_LIVE için asgari veri şartı** — yalnız `portfolioPosition = true` YETERSİZ. En az şunlar gerekir: Position ID, giriş fiyatı, giriş zamanı, adet/portföy yüzdesi, güncel stop, (isteğe bağlı) TP1/TP2, son güncelleme zamanı. Bunlar yoksa panel `POSITION OPEN / ENTRY UNKNOWN / STOP UNKNOWN / RR UNKNOWN` gösterir — **uydurma `_posOpen` seviyeleri MANUAL_LIVE'a asla sızdırılmaz.**

---

## 3. Kanonik pozisyon arayüzü

Pine'da gerçek bir nesne sınıfı olmasa da, tüm katmanlar (panel, yeni-giriş engeli, ekleme, stop, çıkış, alarm, webhook, lot hesabı, backtest, Kelly, rejim performansı) **yalnızca bu alanları okur**, kendi başlarına `_posOpen`/`_v112*`/`portfolioPosition` karışımına bakmaz:

```
posOpen, posSource, posId, posEntry, posEntryBar, posEntryAtr,
posQtyPct, posStop, posTp1, posTp2, posInitialRisk, posOpenRisk,
posState, posExitEvent, posExitType, posExitFill,
posConflictMask, posTransitionSeq
```

---

## 4. Conflict politikası

### 4.1 Bit maskesi

| Bit | Anlam |
|---|---|
| 1 | INTERNAL/MANUAL open uyuşmazlığı |
| 2 | INTERNAL/RESEARCH uyuşmazlığı |
| 4 | Entry fiyatı uyuşmazlığı |
| 8 | Stop uyuşmazlığı |
| 16 | State/pozisyon uyuşmazlığı |
| 32 | Aynı barda giriş/çıkış |
| 64 | Manuel veri eksik |

### 4.2 Temel güvenlik kuralı (kırmızı çizgi)

```
canOpen = not posOpen and conflictMask == 0
canAdd  = posOpen and conflictMask == 0 and openRiskOk

exitNow = legacyExit or unifiedExit     // OR mantığı — fail-safe
stopNow = legacyStop or unifiedStop     // OR mantığı — fail-safe
```

**Conflict varsa:**
- ✅ Yeni AL engellenir
- ✅ EKLEME engellenir
- ✅ Pozisyon büyütme engellenir
- ⚠️ TUT/AZALT yalnız bilgi amaçlı gösterilebilir
- ❌ **STOP ve ÇIKIŞ ASLA engellenmez** — geçiş süresince iki sistemin çıkışları OR ile birleştirilir, herhangi biri çıkış derse çıkılır

Bu kural, geçişin HER fazında değişmeden kalır.

---

## 5. İşlem olay sırası (kesin, tartışmasız)

Unified motorun bar-başı işlem sırası:

1. Önceki bardan pozisyon ve stop snapshot'ı alınır
2. Yeni barın stop/gap kontrolü yapılır (önceki barın DONMUŞ stop seviyesiyle — 17.09'daki `_stopHit` düzeltmesiyle aynı ilke)
3. Stop/çıkış varsa ÖNCE çıkış gerçekleşir
4. **Aynı barda yeniden giriş yapılmaz** (kırmızı çizgi)
5. Çıkış yoksa kısmi satış/ekleme değerlendirilir
6. Pozisyon flat ise giriş değerlendirilir
7. Yeni trailing stop SONRAKİ bar için güncellenir
8. `_smState` sinyal fazı güncellenir
9. Research shadow sonuçları hesaplanır
10. Panel, alarm ve webhook oluşturulur

**Kural:** Aynı barda hem çıkış hem yeniden giriş varsayılan olarak yasaktır. Bu, geriye-dönük stop, stop-sonrası-aynı-bar-yeniden-alım ve çift lifecycle risklerini yapısal olarak ortadan kaldırır.

---

## 6. İstatistik politikası (WR / PF / Kelly)

**Karar:** Unified sistemin istatistikleri **SIFIRDAN başlar**. Eski `_v112` istatistikleri yeni havuza TAŞINMAZ.

**Gerekçe:** `_v112` ve `_posOpen` aynı stratejiyi ölçmüyor — giriş olayları, çıkış olayları, stop tanımı, fill fiyatları, pozisyonda kalma süreleri, gap/stop davranışları farklı. Bunları aynı WR/PF serisinde birleştirmek istatistiksel anlamı bozar (tıpkı B4'ün 08.07 dönem-karışması sorunundaki gibi, ama daha büyük ölçekte).

**Versiyon alanları:**
```
signalModelVersion    = "V162.1c"
positionModelVersion  = "UPM_V1"
executionPolicyVersion = "EXEC_V1"
statsEraStart          = <gerçek devreye alma zamanı>
schemaVersion          = "v163.0"
```

**Kademeli güven eşiği:**
- N < 30 işlem: yalnız ön değerlendirme, Kelly=1.0, regime mult=1.0
- N = 30-59: sınırlı kullanım
- N = 60-99: daha güvenilir kullanım
- N ≥ 100: adaptif pozisyon çarpanlarına geçiş

**Manuel işlem uygunluğu:** Giriş/fill/çıkış verisi eksikse `statsEligible = false` — Kelly/PF hesabına **asla** dahil edilmez.

---

## 7. Shadow çalışma şartı

**Karar:** Doğrudan geçiş YOK. Shadow zorunlu.

- Süre: en az 4-6 hafta
- Olay sayısı: tercihen 60-100 pozisyon-geçiş olayı
- Kapanmış işlem: en az 30
- Farklı piyasa rejimleri gözlenmiş olmalı (yalnız tek yönlü bir dönem yetmez)

Shadow sırasında **legacy davranış değişmez**. Her olayda karşılaştırılacaklar:

| Ölçüm | Açıklama |
|---|---|
| Open agreement | Legacy ve UPM aynı anda pozisyonda mı? |
| Entry agreement | Aynı bar/fiyatta mı açtı? |
| Exit agreement | Aynı nedenle ve zamanda mı kapattı? |
| Stop difference | Stop seviyeleri ne kadar farklı? |
| Holding bars | Pozisyonda kalma süreleri |
| Fill difference | Close-stop-gap farkı |
| PnL difference | İşlem sonucu farkı |
| Conflict duration | Uyuşmazlık kaç bar sürdü? |

---

## 8. Kabul kriterleri

### 8.1 Yapısal doğruluk
- Aynı anda en fazla bir canonical pozisyon
- `entries − exits = openPosition`
- Açık pozisyon yokken çıkış yok
- Açık pozisyon varken ikinci giriş yok
- Aynı bar retroaktif stop yok
- Aynı bar exit + re-entry yok
- Yetim çıkış yok
- Duplicate `eventId` yok

### 8.2 Legacy-UPM uyumu
- Açık/kapalı uyumu ≥ %99
- Kaçırılan stop/çıkış = 0
- Açıkken duplicate AL = 0
- Açıklanamayan entry/exit farkı = 0
- Her fark bir `reasonCode` taşımalı
- Pine ve webhook işlem adetleri birebir eşleşmeli

### 8.3 İstatistik bütünlüğü
```
wins + losses + flat           = eligible closed trades
trend + yatay + düşüş          = eligible closed trades
volHigh + volNormal + volLow   = eligible closed trades
session bucket'ları toplamı    = eligible closed trades
```
Kelly ve rejim çarpanı yalnız GİRİŞTEN ÖNCE kapanmış işlemleri kullanır — mevcut işlemin kendi sonucu kendi lotuna asla sızmaz.

---

## 9. Shadow event şeması (referans)

```json
{
  "schemaVersion": "v163.0",
  "eventId": "BIST:ASTOR|15|POSITION_CLOSE|<timestamp>|<transitionSeq>",
  "eventType": "POSITION_CLOSE_CONFIRMED",
  "signalBarTime": 0,
  "emittedAt": 0,
  "symbol": "ASTOR",
  "tickerId": "BIST:ASTOR",
  "interval": "15",
  "signalModelVersion": "V162.1c",
  "positionModelVersion": "UPM_V1",
  "executionPolicyVersion": "EXEC_V1",
  "position": {
    "mode": "SHADOW",
    "source": "INTERNAL_SIM",
    "legacyOpen": true,
    "resolvedOpen": false,
    "entry": 260.5,
    "stop": 248.25,
    "exitFill": 247.5,
    "tp1": 264.75,
    "tp2": 269.25,
    "qtyPct": 25,
    "conflictMask": 0,
    "transitionSeq": 17,
    "statsEligible": true
  },
  "signal": {
    "phase": "SELL",
    "action": "CIK",
    "reasonCodes": ["STOP_GAP"],
    "score": 27,
    "kgs": 19,
    "regime": "RISK_OFF"
  },
  "telemetry": { "shadow": true, "carrierLagBars": 0 }
}
```
Sayılar string değil gerçek number/null olmalı.

---

## 10. Geçiş fazları (özet — her faz kendi ayrı onayını gerektirir)

| Faz | İçerik | Canlı davranış |
|---|---|---|
| **0** | Bu sözleşme — durumlar, olay sırası, kaynak önceliği, invariant testleri, legacy isimleri dondurma | Değişmez |
| **1** | UPM Shadow — `upm_*` değişkenleri hesaplanır | Alarm/lot/Kelly/panel ETKİLENMEZ, yalnız loglanır |
| **2** | Panel ve webhook'ta LEGACY/UPM/CONFLICT ayrı gösterilir | Bilgi amaçlı, karar hâlâ legacy'de |
| **3** | Giriş kapısı canary — 5 sembolde (ASTOR, ASELS, AKBNK, KCHOL, TUPRS) yeni giriş UPM'den, çıkış legacy OR unified | Sınırlı canlı etki |
| **4** | Unified execution — tüm girişler UPM'den, çıkışta iki sürüm dual safety | Geniş canlı etki |
| **5** | İstatistik geçişi — UPM WR/PF devreye girer, Kelly kademeli açılır, `regimeHistMult` UPM'e geçer | Tam geçiş |

**Rollback:** Her fazda tek satırlık geri dönüş korunur: `positionResolverMode = "LEGACY"`.

---

## 11. Bu sözleşme kapsamı DIŞINDA kalanlar

Aşağıdakiler UPM'den BAĞIMSIZ, ayrı konular — bu belgeyi beklemez:
- HTF EMA gölge ölçümü (ayrı, zaten yürüyor)
- Webhook bir-bar-gecikmesi (mimari, bu Pine yapısıyla çözülemez)
- B1/B6'nın 15dk gerçek doğrulaması (ayrı backtest işi)

---

## 12. Onay

Bu belge, Faz 1 kodu yazılmadan önce şu sorulara "evet" cevabı gerektirir:
- [ ] Madde 2'deki mod tablosu ve MANUAL_LIVE asgari veri şartı kabul edildi mi?
- [ ] Madde 4'teki conflict bit maskesi ve "stop/çıkış asla engellenmez" kuralı kabul edildi mi?
- [ ] Madde 5'teki 10 adımlık olay sırası kabul edildi mi?
- [ ] Madde 6'daki "istatistikler sıfırdan başlar" kararı kabul edildi mi?
- [ ] Madde 7'deki shadow süresi (4-6 hafta / 30+ kapanmış işlem) kabul edildi mi?

Hepsi onaylanınca bu belge "TASLAK"tan "YÜRÜRLÜKTE"ye geçer ve Faz 1 oturumu bu sözleşmeye bağlı kalarak kodlanır.
