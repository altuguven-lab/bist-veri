# Cloudflare köprüsü kurulumu (V163 alarmları)

**Neden:** Pipedream ücretsiz planda eşzamanlılık ve uyanma gecikmesi ayarı yok (16.11 ekran görüntüsü: "Not available"). Aynı bara düşen alarmların bir kısmı Pipedream'e hiç ulaşmıyor. Cloudflare köprüsü her alarmı milisaniyeler içinde kabul eder, depoya 2 dakikada bir tek commit'le yazar.

**Süre:** yaklaşık 30 dakika. **Maliyet:** ücretsiz plan yeterli (günde 100.000 istek; bizim kullanımımız birkaç yüz).

**Güvenlik kuralı:** GitHub anahtarını, webhook anahtarını ve Telegram anahtarını Claude'a göndermeyin. Yalnızca Cloudflare'e girin.

## 1. Hesap ve Worker

1. [dash.cloudflare.com](https://dash.cloudflare.com) üzerinden ücretsiz hesap açın.
2. Sol menü: **Workers & Pages → Create → Create Worker**. Ad: `bist-kopru`. **Deploy**.
3. **Edit code** → editördeki örnek kodu tamamen silin → `cloudflare_kopru.js` içeriğini yapıştırın → **Deploy**.
4. Worker'ın adresini not edin: `https://bist-kopru.<hesap-adiniz>.workers.dev`.

## 2. KV deposu

1. Sol menü: **Storage & Databases → KV → Create namespace**. Ad: `bist-olaylar`.
2. Worker'a dönün: **bist-kopru → Settings → Bindings → Add → KV namespace**.
   - Variable name: `OLAYLAR` (büyük harf, tam olarak bu)
   - KV namespace: `bist-olaylar`
3. **Deploy**.

## 3. GitHub anahtarı (yeni, yalnız bu iş için)

1. GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Ad: `bist-kopru-cloudflare`. Süre: 1 yıl.
3. **Repository access:** Only select repositories → `altuguven-lab/bist-veri`.
4. **Permissions → Repository permissions → Contents:** Read and write. Başka izin vermeyin.
5. **Generate** → anahtarı kopyalayın (bir kez gösterilir).

## 4. Gizli değişkenler

**bist-kopru → Settings → Variables and Secrets → Add**. Her birinde Type: **Secret**.

| Ad | Değer |
|---|---|
| `GITHUB_TOKEN` | 3. adımdaki anahtar |
| `WEBHOOK_KEY` | Kendi üreteceğiniz uzun rastgele bir metin (en az 24 karakter; harf ve rakam). Parola yöneticisi kullanabilirsiniz. |
| `PIPEDREAM_URL` | Mevcut V163 Pipedream adresi (`https://eobd0rr…m.pipedream.net`). **Yalnız geçiş haftası için**; bir hafta sonra silinecek. |

**Deploy**.

## 5. Zamanlayıcı

**bist-kopru → Settings → Trigger events → Cron Triggers → Add** (iki tane):

- `*/2 6-15 * * 2-6` (hafta içi 09:00–18:58 TR, 2 dakikada bir depoya aktarma; Cloudflare gün numaraları Pazar=1 ile başlar, 2-6 = Pazartesi–Cuma)
- `30 20 * * MON-FRI` (her akşam 23:30 TR, kalan varsa son aktarma)

Not: Cloudflare'de gün numaraları 1 = Pazar'dan başlar; `1-5` Pazar–Perşembe demektir. Panelde ilk satır için `2-6`, ikinci için `MON-FRI` girildi; ikisi de Pazartesi–Cuma. Saatler UTC'dir.

## 6. Deneme

1. Tarayıcıda Worker adresini açın. "bist-veri kopru v1" yazmalı.
2. **İki alarmı taşıyın** (örneğin KCHOL ve THYAO): TradingView'de alarmı düzenleyin → Bildirimler → Webhook URL:
   `https://bist-kopru.<hesap-adiniz>.workers.dev/?k=<WEBHOOK_KEY>`
   Alarmı silip yeniden kurmak gerekmez; adres değişikliği yeterli.
3. O hisselerden bir sinyal geldikten sonra 2–4 dakika içinde depoda `TV sinyal: CF ...` ile başlayan bir commit görünmeli. `PIPEDREAM_URL` tanımlı olduğu için aynı alarm Pipedream'den de yazılır; depo bunları kimlikle tekilleştirir.
4. Claude'a haber verin; kayıtları karşılaştırıp onay verir.

## 7. Tam geçiş

1. Onaydan sonra kalan 30 alarmın webhook adresini aynı şekilde değiştirin.
2. Bir hafta boyunca akşam kapsama denetimi 32/32 çıkıyorsa `PIPEDREAM_URL` değişkenini silin. Pipedream V163 iş akışını kapatın (silmeyin; Mart 2027'ye kadar yedek dursun).

## 8. Okunabilir bildirim (Telegram, isteğe bağlı)

1. Telegram'da **@BotFather** → `/newbot` → ad verin → verdiği anahtarı alın.
2. Kendi botunuza bir mesaj gönderin. Tarayıcıda `https://api.telegram.org/bot<ANAHTAR>/getUpdates` adresini açın; `"chat":{"id": ...}` değerini not edin.
3. Worker gizli değişkenlerine ekleyin: `TELEGRAM_TOKEN` (anahtar) ve `TELEGRAM_CHAT` (id).
4. Bundan sonra yalnızca karar sinyalleri gelir: giriş türleri (P1, P2, P3 SKOR AL, EKLEME ADAYI) ve çıkış/risk türleri (STOP KIRILDI, ACİL ÇIK, POZ AZALT, İÇ STOP, KÂR KORU). Her mesajda nihai karar yazar; sinyal ile karar çelişiyorsa "(sinyal ile karar çelişiyor)" notu eklenir. Bilgi sinyalleri (P4, P3 RADAR, SEKTÖR ROTASYONU, P3 HACİM BEKLE, TAŞIMA, GÜNLÜK ÖZET) gönderilmez, ama depoya hepsi yazılır.

## Notlar

- Depoya yazma artık 2 dakikada bir yapılır; bir sinyal depoda en geç yaklaşık 3 dakika sonra görünür. Telefondaki TradingView bildirimi bundan etkilenmez.
- Webhook adresindeki `?k=` anahtarı, adresi bilmeyen birinin sahte sinyal yazmasını engeller (raporun 2.3 maddesi).
- IP-8 ve V195 kayıtları şimdilik Pipedream'de kalıyor; günde iki alarm olduğu için kayıp riski yok. Mart 2027'den önce aynı köprüye taşınacak.
