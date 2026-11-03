# ÖN KAYIT: H10 Yabancı payı değişimi olay testi

**Kayıt tarihi:** 03.11.2026. Kayıt yazılırken hiçbir fiyat sonucu görülmedi. Yalnızca arşivin yapısı incelendi: kaç gün var, her günde kaç hisse var, yayın saatleri ne.
**Uygulayan betik:** `h10_yabanci_olay.py`

**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h10/deneme_kaydi.json` dosyasına eklenir.
- Sonuç görüldükten sonra yapılan her değişiklik ön kayıt değişikliği sayılır. O sonuç keşiftir, hüküm değildir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## İddia

Yabancı yatırımcıların bir hissedeki payını sert biçimde artırması bilgili ya da kalıcı bir talebe işaret ediyorsa, bu hisseler sonraki günlerde payı sert azalan hisseleri geçer.

- **H10a (birincil, piyasa nötr):** Rapor günü yabancı payı en çok artan 3 hissenin ortalama getirisi, en çok azalan 3 hissenin ortalama getirisini 10 işlem günü boyunca geçer. Fark > 0. İki grup da aynı türden hisselerdir (olağan dışı yabancı akışı görmüş, çoğu küçük ve orta boy). Bu yüzden kendi kendini kıyaslar ve büyüklük etkisi büyük ölçüde nötrlenir.
- **H10b (uygulanabilir taraf):** Payı en çok artan 3 hisse, 10 işlem günü boyunca maliyet sonrası BIST 100 eşit ağırlıklı ortalamasını geçer.
- **H10c:** Yabancı payı en uzun süredir kesintisiz artan 5 hisse, 10 işlem günü boyunca BIST 100 eşit ağırlıklı ortalamasını geçer. Maliyet düşülmez; süreklilik sinyalinin kendisi ölçülür.

**Önemli zamanlama notu:** Yabancı payı takas (saklama) verisinden hesaplanır. Rapor günü R'de yayımlanan değişim, birkaç gün önceki işlemleri yansıtır. Bu yüzden sinyal doğası gereği gecikmelidir. Test, bilginin herkesin eline geçtiği andan sonrasını ölçer.

## Veri

| Konu | Tanım |
|---|---|
| Olaylar | `data/yabanci_oran_arsiv.json`, yalnızca `ayristi: true` kayıtlar. Yaklaşık 950 rapor günü: 2021-03 – 2022-01 ve 2023-06 – bugün. Arada herkese açık veri yok. |
| Gruplar | ARTAN = `artan` (3 hisse), AZALAN = `azalan` (3 hisse), SÜREKLİ = `surekli_artan` (5 hisse). |
| Fiyat | yfinance günlük, `h_testleri.panel_kur` (`auto_adjust=False`, bedelsiz düzeltmeli). Fiyatı bulunamayan hisse o olaydan düşer; kapsama oranı gruplara göre ayrı raporlanır. |
| Kıyas (H10b, H10c) | Rapor tarihinde geçerli dönemin yeniden kurulmuş XU100 üyeleri (`data/endeks_uyelik/donemsel.json`: `donem_bas` ≤ R olan en son dönem). Olay hisseleri ve kapsam dışı hisseler hariç, eşit ağırlıklı. Penceresinde fiyatı olan en az 30 hisse gerekir. |
| Kapsam dışı | `config/kapsam_disi.txt` hisseleri olaylardan ve kıyastan çıkarılır. |
| Maliyet | H10b'de gidiş-dönüş %0,25. |

## Zamanlama

- **Giriş:** Rapor `yayin_utc` saati 06:55 UTC'den (TR 09:55) önceyse R günü açılış fiyatı. Değilse ya da saat bilinmiyorsa, R'den sonraki ilk işlem günü açılış fiyatı. R işlem günü değilse sonraki ilk işlem günü açılışı.
- **Çıkış (birincil, h = 10):** Giriş günü dahil 10. işlem gününün kapanışı.
- **İkincil ufuklar (hüküm vermez):** h = 5 ve h = 20.
- İşlem takvimi XU100 işlem günleridir.

## Ölçüm ve istatistik

- **Gün değeri:**
  - H10a: o rapor gününde ARTAN hisselerin ortalama getirisi − AZALAN hisselerin ortalama getirisi. İki grupta da en az 1 fiyatlı hisse gerekir.
  - H10b: ARTAN ortalama getirisi − kıyas getirisi − %0,25.
  - H10c: SÜREKLİ ortalama getirisi − kıyas getirisi.
- **İstatistik:** Gün değerleri tarih sırasıyla dizilir. Ortalama ve Newey-West t hesaplanır (gecikme = h, çünkü 10 günlük pencereler ardışık günlerde çakışır). Bunun için `h_testleri.newey_west` kullanılır. En az 200 gün gerekir.
- **Dönemler:** Örneklem içi R < 2024-01-01; örneklem dışı R ≥ 2024-01-01.

## Hüküm

| Test | GEÇTİ şartı |
|---|---|
| H10a | Ortalama > 0, **t > 2,58**, örneklem dışı ortalama > 0 |
| H10b | Net ortalama > 0, **t > 2,58**, örneklem dışı net ortalama > 0 |
| H10c | Ortalama > 0, **t > 2,58**, örneklem dışı ortalama > 0 |

- **ZAYIF:** İşaret doğru ve t 1,65 ile 2,58 arasında.
- **TERS:** t < −2,58. Ters yönde güçlü bir bulgu. Hüküm GEÇTİ değildir, ayrıca raporlanır.
- **KENAR_YOK:** Diğer bütün durumlar.
- **VERI_YETERSIZ:** 200'den az gün.
- **Ek bilgi (hüküm değiştirmez):** Benjamini-Hochberg q = 0,05 ile üç testin düzeltilmiş durumu (normal yaklaşımla p) raporlanır.

## Kontroller

- **Negatif kontrol (plasebo):** Aynı hisseler ve aynı ufuk, giriş günü 63 işlem günü geriye kaydırılarak ölçülür. Plasebo H10a ya da H10b'de |t| > 2,58 verirse hüküm SUPHELI olur ve geçerli sayılmaz.
- **Pozitif kontrol:** ARTAN hisselerin getirisine yapay olarak +%3 eklenir. Yöntem H10a ve H10b'de GEÇTİ bulmalıdır.

## Raporlanacaklar

- Gün sayısı; gruplara göre olay sayısı ve fiyat kapsaması.
- h = 5, 10, 20 için üç testin ortalaması ve t değeri; örneklem içi ve örneklem dışı ayrımı.
- Yıllara göre ortalamalar (tek bir dönemin sonucu taşıyıp taşımadığını görmek için).
- Plasebo ve pozitif kontrol.
- En büyük 5 olay katkısı.
- Tavan ve taban şüphesi: giriş günü açılışının bir önceki kapanışa göre %9,5'ten fazla yukarıda olduğu olay sayısı. Bu olaylarda fiilen alım yapılamamış olabilir.

## Sınırlılıklar

- Günde yalnızca 3+3+5 hisse var; tam yabancı payı tablosu kullanılamadı.
- 2022-01 ile 2023-05 arası boş.
- ARTAN ve AZALAN hisselerin çoğu küçük ve sığ hisseler. Açılış fiyatından alım her zaman mümkün olmayabilir; H10b bu nedenle iyimser olabilir.
- Kod değiştiren ya da borsadan çıkan hisselerin fiyatı eksik olabilir.
