BIST Veri Köprüsü — Üç Kanal
Bu repo, Claude'a BIST verisi aktarmak için üç ayrı, birbirini tamamlayan kanal içerir:
Kanal	Dosya	Ne içerir	Güncelleme sıklığı
1. Fiyat (Yahoo Finance, çekme/pull)	`data/bist_quotes.json`	30 sembolün ham fiyat/hacim verisi	Hafta içi her 15 dakikada bir (GitHub Actions, `update.yml`)
2. Sinyal (TradingView Webhook, itme/push)	`data/tv_alerts_latest.json`	V151/V195'in ürettiği sinyaller (P1_KALITELI_AL, ACIL_CIK vb.) — son 30 sinyal birikimli tutulur	Alarm tetiklendiği an (TradingView → Pipedream → GitHub)
3. Haber (RSS, çekme/pull)	`data/haber_akisi.json`	KAP, TCMB, ajanslar ve sembol bazlı Google News akışından süzülmüş, puanlanmış haberler (son ~100)	Her 30 dakikada bir, 7/24 (GitHub Actions, `haber_update.yml`)
Mimari
```
TradingView alarmı ──► Pipedream ──► data/tv_alerts_latest.json ┐
Yahoo Finance ──► fetch_bist.py (Actions) ──► data/bist_quotes.json ├──► Claude (brifing / analiz)
RSS kaynakları ──► fetch_news.py (Actions) ──► data/haber_akisi.json ┘
```
Dosyalar
`fetch_bist.py` — Kanal 1 toplayıcısı. Sembol bazında hataya dayanıklı; kod/unvan
geçişleri için eski-kod yedeği içerir (`ESKI_KOD_YEDEK`).
`fetch_news.py` — Kanal 3 toplayıcısı. Haberleri evren sembolleri + makro anahtar
kelimelere göre puanlar; eşik altı, 7 günden eski ve şablon/gürültü başlıkları elenir.
`pipedream_kod_adimi.js` — Kanal 2'nin Pipedream code adımının yedeği. Gelen webhook'u
okur, sinyal geçmişine ekler (son 30), GitHub'a commit eder.
`.github/workflows/update.yml` — Kanal 1 zamanlayıcısı (hafta içi seans saatleri).
`.github/workflows/haber_update.yml` — Kanal 3 zamanlayıcısı (7/24, 30 dk).
Rutinler (Claude tarafında)
"brifing" (her sabah): üç kanalın dosyaları + güncel aracı kurum/haber taraması → günlük plan.
"evren denetimi" (Pazartesi): kurum listeleri 30'luk evrenle karşılaştırılır,
yalnızca değişiklik önerileri raporlanır.
Evren (30 sembol)
AKBNK, YKBNK, GARAN, ISCTR, SAHOL, KCHOL, THYAO, TAVHL, EREGL, ASELS,
ASTOR, MGROS, BIMAS, TUPRS, TOASO, FROTO, ENKAI, TTKOM, AEFES, PGSUS,
HALKB, VAKBN, OTKAR, PETKM, SISE, EKGYO, TRMET, ALARK, ENJSA, ULKER
> **Bakım kuralı:** Evren değiştiğinde ÜÇ yer birlikte güncellenir:
> V195 (sembol inputları + fundTier), `fetch_bist.py` ve `fetch_news.py`.
Revizyon geçmişi
07.07.2026 — SASA, KOZAL, DOAS çıkarıldı; OTKAR, ENJSA, TRMET eklendi.
08.07.2026 — Kanal 3 (haber akışı) devreye alındı; README üç kanala güncellendi.
Notlar
Yahoo Finance verisi birkaç dakika gecikmelidir; anlık (tick) veri değildir.
Kanal 2 dosyası "en son sinyal + son 30 sinyal geçmişi" yapısındadır; her webhook
dosyayı ezmez, geçmişe ekler.
Tüm scriptler tek kaynak/sembol hatasında ÇÖKMEZ; sorunlu kalemi atlar ve loga uyarı yazar.
