# BIST Veri Köprüsü

Bu repo, Claude'a BIST verisi aktarmak için birden çok tamamlayıcı
katman içerir: üç veri kanalı, bir ölçüm/denetim katmanı ve bir
araştırma (backtest) katmanı.

## Kanallar

| Kanal | Dosya | Ne içerir | Güncelleme sıklığı |
|---|---|---|---|
| 1. Fiyat (Yahoo Finance, çekme) | `data/bist_quotes.json`, `data/bist_intraday.json` | 30 sembolün fiyat/hacim verisi | Hafta içi seans saatlerinde (GitHub Actions, `update.yml`) |
| 2. Sinyal (TradingView Webhook, itme) | `data/tv_alerts_latest.json` | V162 BIST IRE FOCUS göstergesinin ürettiği sinyaller (P3_SKOR_AL, ACIL_CIK, GUNLUK_OZET vb.) — **son 100 sinyal** birikimli tutulur | Alarm tetiklendiği an (TradingView → Pipedream → GitHub) |
| 3. Haber (RSS, çekme) | `data/haber_akisi.json` | KAP, TCMB, ajanslar ve sembol bazlı Google News akışından süzülmüş, puanlanmış haberler (son ~100) | Düzenli aralıklarla, 7/24 (GitHub Actions, `haber_update.yml`) |

> **Not (20.08.2026):** Gösterge önceki sürümlerde V151/V195 diye
> anılıyordu — güncel adı **V162 BIST IRE FOCUS**. V195 CTRL KURUMSAL
> ayrı bir gösterge (30-sembol radar/skor paneli), sinyal üretmez.

## Mimari

```
TradingView alarmı ──► Pipedream ──► data/tv_alerts_latest.json ┐
Yahoo Finance ──► fetch_bist.py (Actions) ──► data/bist_quotes.json ├──► Claude (brifing / analiz)
RSS kaynakları ──► fetch_news.py (Actions) ──► data/haber_akisi.json ┘
```

## Evren — TEK KAYNAK (20.08.2026'dan beri)

30 sembollük evren **yalnız** `config/universe.yml`'de tutulur.
`fetch_bist.py` ve `fetch_news.py` sembol listesini `universe.py`
üzerinden buradan okur — kod içinde ayrı bir sabit liste **yoktur.**

> **Bakım kuralı (güncellendi):** Evren değiştiğinde tek dosya
> güncellenir: `config/universe.yml`. V195'in kendi sembol input'ları
> ayrı bir Pine ayarıdır, bu dosyadan otomatik beslenmez — elle senkron
> edilmelidir.
>
> Eski kural ("üç yer birlikte güncellenir: V195, fetch_bist.py,
> fetch_news.py") 20.08'de C3 kararıyla kaldırıldı. Dosya var olduğu
> halde hiçbir betiğin onu okumadığı fark edildiğinde düzeltildi.

Evren (30 sembol): AKBNK, YKBNK, GARAN, ISCTR, SAHOL, KCHOL, THYAO,
TAVHL, EREGL, ASELS, ASTOR, MGROS, BIMAS, TUPRS, TOASO, FROTO, ENKAI,
TTKOM, AEFES, PGSUS, HALKB, VAKBN, OTKAR, PETKM, SISE, EKGYO, TRMET,
ALARK, ENJSA, ULKER.

## Dosyalar — üretim katmanı

- `fetch_bist.py` — Kanal 1 toplayıcısı. Sembol bazında hataya
  dayanıklı; kod/unvan geçişleri için eski-kod yedeği içerir
  (`config/universe.yml`'deki `fallback_symbols`).
- `fetch_news.py` — Kanal 3 toplayıcısı. Haberleri evren sembolleri +
  makro anahtar kelimelere göre puanlar.
- `universe.py` — Evren yükleyici. `config/universe.yml`'i okur;
  dosya eksik/bozuksa sessizce eski listeye düşmez, hata verip durur.
- `json_atomik_yaz.py` — Tüm üretim betiklerinin ortak atomik yazım
  yardımcısı (yazma yarım kalırsa eski dosya bozulmaz).
- `pipedream_kod_adimi.js` — Kanal 2'nin Pipedream code adımının
  yedeği.
- `islem_gunlugu.json` — **Değişmez ana kayıt** (20.08'den beri, C2
  kararı). Olay tabanlı şema: `ACILIS_BAKIYESI`, `ALIS`, `SATIS`,
  `NAKIT_MUTABAKAT`, `STOP_GUNCELLEME`. Portföy durumu buradan
  **türetilir**, elle düzenlenmez.
- `portfoy_turet.py` — `islem_gunlugu.json`'dan `portfoy.json` üretir.
  Mutabakat tutmuyorsa (iki ardışık `NAKIT_MUTABAKAT` arası açıklanamayan
  fark eşiği aşarsa) uyarır; hiçbir zaman sessizce yanlış portföy
  yazmaz.

## Dosyalar — ölçüm / denetim katmanı

- `hafta_denetim.py` — Cuma kapanışı denetimi. M1–M6 metrikleri,
  kaçan fırsat listesi, fiyat sağlama kontrolü. Çıktı:
  `data/denetim/hafta_<YYYY-Www>.md`.
- `saglik_kontrol.py` — Kanal/şema sağlığı; arıza bulursa GitHub
  Issue açar (`FELAKET_RUNBOOK.md`'ye yönlendirir).
- `haber_teshis.py` — Haber kanalının eleme nedenlerini kaynak
  bazında raporlar (özet ve ayrıntılı mod). Elle tetiklenir.
- `bilanco_takvimi.py` + `config/bilanco_takvimi.json` — Bilanço
  açıklama takvimi. Deterministik, haber akışından bağımsız;
  açık pozisyonlar için "bilanço penceresi" risk bayrağı üretir.
  **Tahmin yazılmaz** — bilinmeyen tarih `null` kalır.

## Dosyalar — araştırma / backtest katmanı

Bu betikler **salt ölçüm** — Pine'a dokunmaz, kuluçka sayacını
etkilemez. Her biri kendi ön kayıt/karar kuralı belgesiyle gelir:

- `kirilma_testi.py` — İP-7: rejim kırılma testi (PELT + bootstrap
  güven aralığı), ön kayıt: `ON_KAYIT_IP7.md`.
- `gece_gunduz_ayristirma.py` — Gece/gündüz getiri ayrıştırması, gap
  kovaları, kısa ufuk momentum/dönüş testi.

## Workflow'lar (`.github/workflows/`)

| Dosya | Ne çalıştırır | Tetik |
|---|---|---|
| `update.yml` | `fetch_bist.py` | zamanlı, hafta içi seans saatleri |
| `haber_update.yml` | `fetch_news.py` | zamanlı, düzenli aralık |
| `haber_teshis.yml` | `haber_teshis.py` | elle (`kaynak` girdisi) |
| `hafta_denetim.yml` | `hafta_denetim.py` | zamanlı, Cuma |
| `saglik_kontrol.yml` | `saglik_kontrol.py` | zamanlı |
| `bilanco_takvimi.yml` | `bilanco_takvimi.py` | zamanlı, hafta içi sabah |
| `ip7_kirilma_testi.yml` | `kirilma_testi.py` | elle (`asama` girdisi) |
| `gece_gunduz_olcum.yml` | `gece_gunduz_ayristirma.py` | elle (`donem` girdisi) |

## Rutinler (Claude tarafında)

- **brifing** (her sabah): üç kanalın dosyaları + bilanço takvimi +
  güncel aracı kurum/haber taraması → günlük plan.
- **evren denetimi** (Pazartesi): `config/universe.yml` gözden
  geçirilir, değişiklik önerileri raporlanır.
- **hafta kapanışı** (Cuma): `hafta_denetim.py` çıktısının okunması,
  M1–M6 ve kaçan fırsat listesinin değerlendirilmesi.
- **bilanço güncelle** (çeyreklik): `config/bilanco_takvimi.json`'ın
  doğrulanması.
- **kurumsal güncelle** (aylık): KMS/kurumsal radar veri toplama.

## Revizyon geçmişi

- 07.07.2026 — SASA, KOZAL, DOAS çıkarıldı; OTKAR, ENJSA, TRMET eklendi.
- 08.07.2026 — Kanal 3 (haber akışı) devreye alındı.
- 20.08.2026 — Mimari inceleme sonrası: evren tek kaynağa
  (`config/universe.yml`) taşındı, atomik yazım tüm üretim
  betiklerine yaygınlaştırıldı, işlem günlüğü olay tabanlı şemaya
  (v4/v5) geçti.
- 24.08.2026 — `hafta_denetim.py` ve `saglik_kontrol.py`'nin işlem
  günlüğü okuma mantığı yeni şemaya güncellendi (M3 metriği tekrar
  hesaplanabilir hale geldi).

## Notlar

- Yahoo Finance verisi birkaç dakika gecikmelidir; anlık (tick) veri
  değildir.
- Kanal 2 dosyası "en son sinyal + son 100 sinyal geçmişi" yapısındadır;
  her webhook dosyayı ezmez, geçmişe ekler. `inbox_birlestir.py`,
  Pipedream'in ana dosyaya yazamadığı kayıtları `data/inbox/`'tan
  kurtarır.
- Tüm üretim scriptleri tek kaynak/sembol hatasında ÇÖKMEZ; sorunlu
  kalemi atlar ve loga uyarı yazar.
- Araştırma katmanındaki betikler bu kuralın dışındadır — onlar
  ölçüm bütünlüğü için bilerek "sessiz düşme yok, hata ver ve dur"
  ilkesiyle yazılmıştır (ör. `universe.py`, `portfoy_turet.py`).
