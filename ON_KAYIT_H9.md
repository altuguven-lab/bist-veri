# ÖN KAYIT: H9 BIST 100 dönemsel endeks değişikliği olay testi

**Kayıt tarihi:** 02.11.2026. Kayıt yazılırken hiçbir fiyat sonucu görülmedi; yalnızca üyelik verisinin kendisi (kim girdi, kim çıktı) incelendi.
**Uygulayan betik:** `h9_endeks_olay.py`

**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h9/deneme_kaydi.json` dosyasına eklenir.
- Sonuç görüldükten sonra yapılan her değişiklik ön kayıt değişikliği sayılır. O sonuç keşiftir, hüküm değildir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## İddia

Borsa İstanbul dönemsel BIST 100 değişikliklerini KAP'ta duyurur. Değişiklikler birkaç gün ya da hafta sonra geçerli olur. Endeksi izleyen fonlar ve vadeli işlem hedge'leri, değişikliğin geçerli olduğu günden önceki son kapanışta alım ya da satım yapmak zorundadır. Bu zorunlu talep fiyata yansıyorsa iki şey gözlenmelidir:

- **H9a:** Endekse **alınan** hisseler, duyurudan sonraki açılıştan geçerlilikten önceki son kapanışa kadar, maliyet sonrası BIST 100 ortalamasını geçer.
- **H9b:** Endeksten **çıkarılan** hisseler aynı pencerede BIST 100 ortalamasının gerisinde kalır. Açığa satış pratik olmadığından bu bir "kaçınma" sinyali olarak ölçülür; maliyet düşülmez.
- **H9c:** Alınan hisselerde etki geçicidir. Geçerlilikten sonraki 20 işlem gününde BIST 100 ortalamasının gerisinde kalırlar (geri dönüş). Maliyet düşülmez.

Bu, fiyat geçmişine değil kurumsal bir zorunluluğa dayanan bir sinyaldir. Dünyada en çok belgelenmiş olay etkilerinden biridir. BIST'te hiç ölçmedik.

## Veri

| Konu | Tanım |
|---|---|
| Olaylar | `data/endeks_uyelik/donemsel.json → duyurular`. 42 dönemsel duyuru, 2016-07 ile 2026-10 arası. Yalnızca XU100 alınan ve çıkarılan listeleri kullanılır. Dönem arası değişiklikler (Yakın İzleme Pazarı, birleşme) olay sayılmaz. |
| D (duyuru) | KAP yayın tarihi. Gün içi saati ne olursa olsun bilgi D günü kapanışından sonra kullanılabilir sayılır. |
| E (geçerlilik) | Duyurudaki dönem başlangıcı (`donem_bas`). E−1, E'den önceki son işlem günüdür. |
| İşlem takvimi | XU100 endeksinin işlem günleri. |
| Fiyat | yfinance günlük, `h_testleri.panel_kur` ile (`auto_adjust=False`, bedelsiz düzeltmeli). Fiyatı bulunamayan hisse o olaydan düşer; kapsama oranı raporlanır. Kod değiştiren ya da borsadan çıkan hisseler eksik kalabilir. Bu bir sınırlılıktır. |
| Kıyas | Olay döneminin (E) yeniden kurulmuş XU100 üyeleri. Olay hisseleri ve kapsam dışı hisseler hariç tutulur, yalnızca o pencerede fiyatı olanlar alınır. Kıyas bu üyelerin eşit ağırlıklı getiri ortalamasıdır (H6'daki gerekçeyle XU100 endeksi değil). |
| Kapsam dışı | `config/kapsam_disi.txt` hisseleri olaylardan ve kıyastan çıkarılır (önceki testlerle tutarlılık). |
| Maliyet | H9a'da gidiş-dönüş %0,25. |

## Pencereler

| Ad | Giriş | Çıkış | Kullanım |
|---|---|---|---|
| W1 | D'den sonraki ilk işlem günü **açılış** | E−1 **kapanış** | H9a, H9b |
| W2 | E−1 kapanış | E−1'den sonraki 20. işlem günü kapanış | H9c |
| W0 | D'den 10 işlem günü önceki kapanış | D kapanış | Yalnızca tanı amaçlı (duyuru öncesi sızıntı). Hüküm vermez. |

W1 en az 1 işlem günü uzunluğunda olmalıdır. Daha kısa olan olay düşer.

## Ölçüm ve istatistik

- **Olay fazla getirisi:** Hisse getirisi − aynı penceredeki kıyas getirisi, yüzde olarak.
- **Dönem değeri:** Her dönemde gruptaki (alınan ya da çıkarılan) hisselerin fazla getirilerinin eşit ağırlıklı ortalaması. Gözlem birimi dönemdir. Aynı dönemdeki hisseler ortak piyasa hareketini paylaştığı için bu, dönem bazında kümelemeye eşdeğerdir.
- **İstatistik:** Dönem değerleri üzerinden ortalama ve t = ortalama / (std / √n). En az 20 dönem gerekir.

## Hüküm

| Test | GEÇTİ şartı |
|---|---|
| H9a | Net ortalama > 0, **t > 2,58**, ve örneklem dışı (E ≥ 2022-01-01) net ortalama > 0 |
| H9b | Brüt ortalama < 0, **t < −2,58**, ve örneklem dışı brüt ortalama < 0 |
| H9c | Brüt ortalama < 0, **t < −2,58**, ve örneklem dışı brüt ortalama < 0 |

- **ZAYIF:** |t| 1,65 ile 2,58 arasında ve işaret doğru.
- **KENAR_YOK:** Diğer bütün durumlar.
- **VERI_YETERSIZ:** 20'den az geçerli dönem.
- **Ek bilgi (hüküm değiştirmez):** Benjamini-Hochberg q = 0,05 ile üç testin düzeltilmiş durumu (normal yaklaşımla p) raporlanır.

## Kontroller

- **Negatif kontrol (plasebo):** Aynı hisseler ve aynı pencere uzunlukları, D ve E 63 işlem günü geriye kaydırılarak ölçülür. Plasebo H9a ya da H9b'de |t| > 2,58 verirse yöntem şüphelidir. Hüküm "SUPHELI" olarak işaretlenir ve geçerli sayılmaz.
- **Pozitif kontrol:** Alınan hisselerin W1 getirisine yapay olarak +%3 eklenir. Yöntem bu durumda H9a'yı GEÇTİ olarak bulmalıdır. Bulamazsa test gücü yetersizdir ve raporlanır.

## Raporlanacaklar

- Dönem sayısı ve olay sayısı; fiyat kapsama oranı.
- W0, W1 ve W2 için grup ortalamaları.
- Örneklem içi ve örneklem dışı ayrımı.
- Plasebo ve pozitif kontrol sonuçları.
- En büyük 5 olay katkısı (tek bir olayın sonucu taşıyıp taşımadığını görmek için).

## Sınırlılıklar

- Dönem arası değişiklikler uygulanmadı. Bu yüzden eski dönemlerde kıyas sepeti 100'den birkaç hisse sapabilir (2016'da 105).
- Borsadan çıkan ya da kod değiştiren hisselerin fiyatı eksik olabilir. Bu durum çıkarılan grupta daha sık görülür ve H9b'yi olumlu yöne çarpıtabilir; bu yüzden kapsama oranı gruplara göre ayrı raporlanır.
- 2026-10 dönemindeki 27 değişiklik metodoloji değişikliğinden kaynaklanıyor olabilir. Sonuç bu dönem hariç tutularak da ayrıca raporlanır, ancak hüküm tüm dönemlerle verilir.
