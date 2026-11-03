# ÖN KAYIT: H11 Yabancı alım serisi, momentum eşleştirmeli kontrol grubuna karşı

**Kayıt tarihi:** 03.11.2026.
**Uygulayan betik:** `h11_yabanci_momentum.py`

**Neden yazıldı:** H10c kurala göre GEÇTİ. Ancak plasebo, aynı hisselerin seriden 3 ay önce de ortalamayı geçtiğini gösterdi (+%1,44, t 4,04). Bu, ölçülen etkinin yabancı alımından değil momentumdan ya da seçimden gelebileceği anlamına geliyor. H11 bu iki açıklamayı birbirinden ayırır.

**Görülmüş olan:** H10'un sonuçları biliniyor. H11'in eşleştirmeli sonucu hiç görülmedi.

**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h11/deneme_kaydi.json` dosyasına eklenir.
- Sonuç görüldükten sonra yapılan her değişiklik ön kayıt değişikliği sayılır. O sonuç keşiftir, hüküm değildir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## İddia

**H11:** Yabancı payı en uzun süredir kesintisiz artan 5 hisse, geçmiş fiyat davranışı kendisine en çok benzeyen hisselerden oluşan kontrol grubunu 10 işlem gününde geçer. Yani yabancı alım serisi, momentumun ötesinde ek bilgi taşır.

H11 GEÇTİ çıkmazsa H10c'deki etki momentum ya da seçim etkisi olarak kayda geçer ve yabancı serisi ayrı bir sinyal olarak kullanılmaz.

## Veri

| Konu | Tanım |
|---|---|
| Olaylar | `data/yabanci_oran_arsiv.json`, yalnızca `ayristi: true` kayıtların `surekli_artan` listesi (günde 5 hisse). |
| Giriş ve çıkış | H10 ile aynı. Giriş: yayın 06:55 UTC'den önceyse R günü açılışı, değilse sonraki işlem günü açılışı. Çıkış: giriş günü dahil 10. işlem gününün kapanışı (h = 10). İkincil ufuklar h = 5 ve h = 20, hüküm vermez. |
| Fiyat | `h_testleri.panel_kur` (yfinance, `auto_adjust=False`, bedelsiz düzeltmeli). |
| Aday havuzu | O gün geçerli dönemin yeniden kurulmuş XU100 üyeleri ile arşivde herhangi bir gün geçen bütün hisselerin birleşimi. Böylece havuzda küçük ve orta boy hisseler de bulunur. Hariç tutulanlar: o günün SÜREKLİ listesi, son 20 işlem gününde SÜREKLİ listesine girmiş hisseler ve kapsam dışı hisseler. |
| Kapsam dışı | `config/kapsam_disi.txt` hisseleri olaylardan ve havuzdan çıkarılır. |

## Eşleştirme

Eşleştirme, giriş gününden önceki son kapanışa kadarki bilgiyle yapılır; ileriye bakılmaz.

**Özellikler:** Her hisse için o güne kadarki getiriler:
- son 21 işlem günü (R21),
- son 63 işlem günü (R63),
- son 252 işlem günü (R252),
- son 63 günün günlük getiri standart sapması (OYN).

Her özellik o gün geçerli havuzla birlikte (olay hisseleri dahil) 0–1 arası yüzdelik sıraya çevrilir. Bir hissenin eşleştirmeye girebilmesi için en az 253 günlük fiyat geçmişi ve çıkış günü fiyatı gerekir.

**Kontrol grubu:** Her olay hissesi için, dört yüzdelik sıra üzerinden Öklid uzaklığı en küçük olan **5 aday** seçilir. Aynı aday aynı günde birden fazla olay hissesine kontrol olabilir.

**Eşleştirme kalitesi:** Olay hissesi ile kontrollerinin ortalaması arasındaki yüzdelik sıra farkı her özellik için raporlanır. Ortalama mutlak fark 0,10'u aşan özellik varsa sonuçta "EŞLEŞTİRME_ZAYIF" notu düşülür.

## Ölçüm ve istatistik

- **Olay değeri:** Olay hissesinin getirisi − 5 kontrol hissesinin ortalama getirisi, aynı giriş ve çıkış günleriyle. Maliyet düşülmez; bu bir bilgi testidir. Net değer (−%0,25) ayrıca raporlanır.
- **Gün değeri:** O gündeki olay değerlerinin ortalaması.
- **İstatistik:** Gün değerleri üzerinden ortalama ve Newey-West t (`h_testleri.newey_west`, gecikme = h). En az 200 gün gerekir.
- **Dönemler:** Örneklem içi R < 2024-01-01; örneklem dışı R ≥ 2024-01-01.

## Hüküm

**GEÇTİ şartlarının hepsi sağlanmalıdır:**
1. Ortalama > 0 ve t > 2,58.
2. Örneklem dışı ortalama > 0.
3. **Plasebo** (aynı hisseler, giriş günü 63 işlem günü geriye kaydırılmış, eşleştirme de o güne göre yeniden yapılmış) |t| < 2,58.
4. **Pozitif kontrol:** Olay hisselerine yapay olarak +%3 eklendiğinde ortalama > 0 ve t > 2,58 çıkmalı. Çıkmazsa sonuç GUC_YETERSIZ olur.

**Diğer hükümler:**
- Şart 1 ve 2 sağlanıp plasebo |t| ≥ 2,58 ise: **SUPHELI**.
- İşaret doğru ve 1,65 < t ≤ 2,58 ise: **ZAYIF**.
- t < −2,58 ise: **TERS**.
- Aksi hâlde: **KENAR_YOK**.
- 200'den az gün varsa: **VERI_YETERSIZ**.

Bu kural, H10'daki açık nedeniyle, plaseboyu hükmün parçası yapar.

## Raporlanacaklar

- Gün sayısı, olay sayısı, eşleştirilebilen olay oranı ve ortalama havuz büyüklüğü.
- h = 5, 10, 20 için sonuçlar; örneklem içi ve örneklem dışı ayrımı; yıllara göre ortalamalar.
- Eşleştirme kalitesi tablosu.
- Plasebo ve pozitif kontrol sonuçları.
- **Bilgi için H10c tekrarı:** Aynı olaylarda kontrolsüz fark (olay − havuz ortalaması). Eşleştirmenin etkiyi ne kadar azalttığını gösterir.
- En büyük 5 olay katkısı.

## Sınırlılıklar

- Hacim verisi yok; likidite eşleştirilemedi. Oynaklık, kısmen bunun yerine kullanılıyor.
- 2022-01 ile 2023-05 arası boş.
- Kod değiştiren ya da borsadan çıkan hisselerin fiyatı eksik olabilir.
