# ÖN KAYIT: R3b Stop kuralları, piyasaya göre fazla getiriyle

**Kayıt tarihi:** 03.11.2026.
**Uygulayan betik:** `risk_r3b.py`

**Neden yazıldı:** R3'te seçim aşamasında ölçüt mutlak TL getirisiydi. Şart, "varyantın ortalaması stopsuz işlemden en fazla 0,30 puan düşük olsun" idi. Örneklem içi dönemde (2016–2022) yüksek enflasyon nedeniyle her hisse 20 günde ortalama yaklaşık %3 nominal yükseldi. Bu ortamda stopla erken çıkmak, stopun kalitesinden bağımsız olarak piyasa sürüklenmesini kaçırmak anlamına geliyordu. Bu yüzden hiçbir varyant 0,30 puan sınırını geçemedi ve seçim yapılamadı. R3'ün hükmü (KENAR_YOK) kayıtta öyle kalır.

R3b, stopun değerini piyasa sürüklenmesinden arındırarak ölçer: her işlemin getirisi, aynı penceredeki BIST 100 eşit ağırlıklı sepetin getirisiyle karşılaştırılır.

**Görülmüş olan:** R3'ün mutlak getiri tablosu görüldü; örneklem dışı dönemde S8'in kuyruğu belirgin biçimde kestiği biliniyor. Fazla getiri ile ölçülmüş hiçbir sonuç görülmedi. Bu, kısmen görülmüş veriyle yapılan bir yeniden testtir ve hüküm buna göre yorumlanacaktır.

**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/risk_r3b/deneme_kaydi.json` dosyasına eklenir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## Tasarım (R3'ten farkları)

R3'teki evren, fiyat verisi, giriş takvimi, 20 günlük azami tutma, stop çalışma kuralları, sekiz varyant (V0, S5, S8, A15, A2, A3, T2, T3), plasebo yöntemi (ardışık bağımlılığı yok edilmiş sentetik fiyatlar) ve IS/OOS ayrımı **aynen** kullanılır. Değişen yalnızca şunlardır:

- **İşlem fazla getirisi:** (çıkış / giriş − 1 − %0,25) − sepet getirisi.
  - Sepet getirisi, aynı gün geçerli XU100 üyelerinin eşit ağırlıklı sepetinin giriş günü açılışından çıkış günü kapanışına kadarki getirisidir.
  - Sepetin açılış seviyesi: önceki gün kapanış seviyesi × (1 + üyelerin açılış/önceki kapanış oranlarının ortalaması − 1).
  - Stopla gün içinde çıkılan işlemlerde de sepet o günün kapanışıyla ölçülür. Bu küçük bir yaklaşıklıktır.
- **Plasebo:** Sentetik fiyatlardan aynı yöntemle kurulmuş sentetik sepet kullanılır.
- **Seçim (yalnızca IS):** Ortalama fazla getirisi V0'ınkinden en fazla 0,30 puan düşük olan varyantlar arasından, fazla getiri CVaR %5'i en iyi olan seçilir.
- **GEÇTİ (seçilen varyant için OOS'ta, şartların hepsi):**
  1. Fazla getiri CVaR %5, V0'a göre en az %25 iyileşir.
  2. Ortalama fazla getiri ≥ V0 − 0,30 puan.
  3. Ortalama fazla getiri farkı (varyant − V0) ≥ plasebodaki fark − 0,20 puan.
- **Hüküm anlamları:**
  - Şart 1 sağlanıp şart 3 sağlanmazsa: **STOP_PAHALI**.
  - Seçim yapılamazsa ya da diğer durumlarda: **KENAR_YOK**.
- **Ek bilgi (hüküm vermez):** Mutlak getiri tablosu (R3 ile aynı), giriş günü kümelenmiş t, varyant başına stopla çıkış oranı.

## Pine için anlamı

GEÇTİ durumunda seçilen varyant, Pine'da günlük ATR'ye ya da yüzdeye dayalı stop olarak önerilir. Günlük ATR tek bir `request.security(syminfo.tickerid, "D", ...)` çağrısıyla alınır. Mevcut 15 dakikalık ATR stopunun yerine mi geçeceği, yanında mı duracağı kurul kararıdır.
