# BIST Veri Köprüsü — İki Kanal

Bu repo, Claude'a BIST verisi aktarmak için **iki ayrı, birbirini tamamlayan**
kanal içerir:

| Kanal | Dosya | Ne içerir | Güncelleme sıklığı |
|---|---|---|---|
| **1. Yahoo Finance (çekme/pull)** | `data/bist_quotes.json` | 30 sembolün ham fiyat/hacim verisi | Hafta içi her 15 dakikada bir (GitHub Actions) |
| **2. TradingView Webhook (itme/push)** | `data/tv_alerts_latest.json` | V151/V195'in kendi ürettiği sinyaller (ACTION, ACİL ÇIK, P1 AL vb.) | Alarm tetiklendiği an (saniyeler içinde) |

## Kanal 1 — Yahoo Finance (zaten kurulu)

`fetch_bist.py` + `.github/workflows/update.yml` — önceki kurulumla aynı,
değişiklik yok. BIST işlem saatleri boyunca otomatik çalışır.

## Kanal 2 — TradingView Webhook (yeni)

### Nasıl çalışır
```
TradingView Alarm (webhook) → Pipedream → GitHub'a dosya yazar → sen linki verirsin → Claude okur
```

### Kurulum

1. **Pipedream workflow oluştur** (pipedream.com, ücretsiz):
   - Tetikleyici: **"HTTP / Webhook" → "New Requests"**. Sana bir URL verir
     (örn. `https://xxxxx.m.pipedream.net`) — bunu not al.
   - İkinci adım: **"Run Node.js code"** ekle, bu repodaki
     `pipedream_kod_adimi.js` dosyasının içeriğini oraya yapıştır.
   - Üçüncü adım: **GitHub entegrasyonu** → "Create or Update File" action'ı.
     GitHub hesabını bağla, repo/branch seç, dosya yolu olarak
     `data/tv_alerts_latest.json` yaz, dosya içeriği olarak ikinci adımın
     çıktısını (Pipedream arayüzü otomatik önerir, `steps.kod_adimi.$return_value`
     benzeri bir değişken) seç.
   - Workflow'u **"Deploy"** et.

2. **TradingView'de alarm kur:**
   - V151 IRE FOCUS grafiğinde Alarm oluştur, koşul olarak istediğin
     `alertcondition`'ı seç (örn. "P1 KALİTELİ AL", "ACİL ÇIK").
   - **Mesaj alanını JSON formatına çevir** (varsayılan düz metin yerine),
     örnek:
     ```json
     {"symbol": "{{ticker}}", "signal": "P1_KALITELI_AL", "interval": "{{interval}}", "price": "{{close}}"}
     ```
     Bu, Pipedream'in `pipedream_kod_adimi.js`'teki ayrıştırmayı düzgün
     yapabilmesi için önemli — düz metin de çalışır ama `ham_mesaj` alanına
     düşer, yapılandırılmış alanlar (`sembol`, `sinyal`) boş kalır.
   - **"Webhook URL"** kutucuğunu işaretle, Pipedream URL'ini yapıştır.
   - Kaydet.

3. **Test et:** Alarmı tetikle (ya da test amaçlı basit bir fiyat alarmı kur),
   Pipedream'in "Event History" sekmesinde isteğin geldiğini, GitHub'da
   `data/tv_alerts_latest.json` dosyasının güncellendiğini doğrula.

## Claude'a Aktarma

İki dosyanın da raw linki:
```
https://raw.githubusercontent.com/KULLANICI-ADIN/REPO-ADIN/main/data/bist_quotes.json
https://raw.githubusercontent.com/KULLANICI-ADIN/REPO-ADIN/main/data/tv_alerts_latest.json
```

Bir sohbette ikisini de verip *"bu iki linkten güncel veriyi çek"* dersin,
Claude her ikisini de `web_fetch` ile okur.

## Sınırlamalar (dürüstçe)

- **Kanal 1** birkaç dakika gecikmeli, gerçek anlık değil.
- **Kanal 2** gerçekten anlık (saniyeler) ama SADECE alarm kurduğun koşullar
  için çalışır — sistemin sürekli durumunu değil, sadece "olay" anlarını yakalar.
- **`tv_alerts_latest.json` sadece EN SON alarmı tutar** — art arda birkaç
  alarm gelirse aradakileri kaçırabilirsin. İstersen ileride bunu bir "son 50
  alarm" listesine genişletebiliriz (Pipedream'de bir okuma-ekleme adımı gerekir).
