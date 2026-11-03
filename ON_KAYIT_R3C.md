# ÖN KAYIT: R3c %5 stopun gerçekçi uygulama koşullarında doğrulanması

**Kayıt tarihi:** 03.11.2026.
**Uygulayan betik:** `risk_r3c.py`

**Neden yazıldı:** R3b GEÇTİ ve sabit %5 stop (S5) seçildi. 03.11 denetiminde ölçüm yönteminde, sonucu stop lehine çarpıtabilecek üç nokta bulundu. R3c bu üç noktayı düzeltir ve **yalnızca önceden seçilmiş S5'i** doğrular. Yeniden varyant seçimi yapılmaz.

1. **Sepet zamanlaması:** Stop gün içinde çalıştığında hisse stop fiyatından satılıyor, ama sepet o günün kapanışıyla ölçülüyordu. Stopların çoğu piyasanın düştüğü günlerde çalışır. Stoptan sonraki gün içi düşüş sepetten düşülünce, stoplu işlemin piyasaya göre sonucu olduğundan iyi görünür. Açılış boşluğuyla çıkılan işlemlerde de sepetin açılış değeri yerine kapanış değeri kullanılıyordu.
2. **Stop kayması:** Stop emri tam stop fiyatından değil, genellikle biraz altından gerçekleşir. Hızlı düşüşte ve taban yakınında fark büyür. S5'te işlemlerin yaklaşık üçte ikisi stopla kapandığı için küçük bir kayma bile sonucu etkiler.
3. **Yeniden yatırım maliyeti:** R3b'nin piyasaya göre ölçümü, stoplanan paranın sepete aktarıldığını örtük olarak varsayar ("stopla çık, endekse geç"). Bu geçişin işlem maliyeti hesaba katılmamıştı.

**Görülmüş olan:** R3 ve R3b sonuçları. R3c'nin düzeltilmiş ölçümleri hiç görülmedi.

**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/risk_r3c/deneme_kaydi.json` dosyasına eklenir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## Tasarım

R3b'deki evren, fiyat, giriş takvimi (her 5. işlem günü açılış), 20 günlük azami tutma, stop çalışma sırası ve IS/OOS ayrımı aynen kullanılır. Karşılaştırma yalnızca **S5** ile **V0** arasındadır. Diğer varyantlar bilgi için raporlanır.

### Birincil varsayımlar (hüküm bunlarla verilir)

| Konu | Kural |
|---|---|
| Stop kayması | Stopla çıkışta gerçekleşen fiyat = stop fiyatı × (1 − %0,25). Açılış boşluğunda = açılış × (1 − %0,25). |
| Sepet, açılış boşluğu çıkışı | Sepet çıkış günü **açılış** seviyesiyle ölçülür. |
| Sepet, gün içi stop çıkışı | Sepet, çıkış günü açılış ve kapanış seviyelerinden **hangisi stoplu işlem aleyhineyse** (yüksek olanı) onunla ölçülür. Bu bir alt sınır tahminidir. |
| Yeniden yatırım maliyeti | Stopla kapanan her işlemden ek %0,25 düşülür (sepete giriş ve 20. gün sonunda çıkış). |
| Normal maliyet | Her işlemde gidiş-dönüş %0,25 (R3b ile aynı). |

### Duyarlılık (hüküm vermez)

- Kayma 0, %0,25 ve %0,50 ile yeniden yatırım maliyeti %0,10 ve %0,25'in bütün birleşimleri.
- Sepetin R3b'deki gibi çıkış günü kapanışıyla ölçüldüğü hâl, karşılaştırma için.

## Hüküm

**GEÇTİ şartlarının hepsi, birincil varsayımlarla, hem IS'de hem OOS'ta ayrı ayrı sağlanmalıdır:**
1. S5'in fazla getiri CVaR %5'i, V0'ınkinin büyüklükçe 0,75 katı ya da daha az.
2. S5'in ortalama fazla getirisi ≥ V0 − 0,30 puan.
3. **Plasebo:** Ardışık bağımlılığı yok edilmiş sentetik fiyatlarla, aynı varsayımlarla hesaplanan fark (S5 − V0) en fazla 0,20 puan daha iyidir. Yani gerçek fark ≥ plasebo farkı − 0,20.

**Diğer hükümler:**
- Şart 1 sağlanıp şart 2 ya da 3 sağlanmazsa: **STOP_PAHALI**. Stop kuyruğu kesiyor, ama gerçekçi maliyetlerle piyasaya göre kabul edilenden fazla getiri kaybettiriyor.
- Aksi hâlde: **KENAR_YOK**.

**Ek bilgi (hüküm vermez):**
- Ortalama fark (S5 − V0) ve giriş günü kümelenmiş Newey-West t'si (gecikme 4).
- Stopla çıkışların türü: açılış boşluğu ya da gün içi.
- Mutlak getiri, yani stoplanan paranın nakitte beklediği hâl.

## Kurul için anlamı

- **GEÇTİ:** %5 stop, Pine'da ana stop olarak önerilebilir. Uygulama talimatı: "stopla çıkınca serbest kalan parayı endeks sepetine (ETF ya da VİOP) aktar."
- **STOP_PAHALI:** %5 stop yalnızca "felaket sınırı" (kuyruk sigortası) olarak, maliyeti bilinerek kullanılabilir.
- **KENAR_YOK:** %5 stop önerilmez.
