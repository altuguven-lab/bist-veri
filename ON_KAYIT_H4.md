# ÖN KAYIT: H4 bilanço sürprizi sonrası seyir

**Kayıt tarihi:** 27.10.2026, sonuçlar görülmeden.
**Uygulayan betik:** `h4_bilanco_surprizi.py`
**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h4/deneme_kaydi.json` dosyasına eklenir.
- Sonuç görüldükten sonra yapılan her değişiklik "ön kayıt değişikliği" sayılır; o sonuç keşiftir, hüküm değildir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

---

## İddia

Kârı bir önceki yılın aynı dönemine göre özkaynağına oranla en çok artan şirketler, bilanço açıklandıktan sonraki 40 işlem gününde kendi sektörlerini geçer. Akademik literatürde bu etki "kazanç açıklaması sonrası sürüklenme" (PEAD) olarak bilinir.

**Dayanak:**
- Fiyat ve hacme dayalı sinyaller (alarm karnesi, H1–H3) kenar üretmedi.
- Bilanço fiyattan bağımsız bir bilgi kaynağıdır.

## Veri

| Konu | Tanım |
|---|---|
| Evren | `config/bist100_uyeler.txt` ile `data/temel/ham_*.json` kesişimi. `config/kapsam_disi.txt` içindeki hisseler tamamen çıkarılır. |
| Mali veri | `data/temel/ham_<KOD>.json`, TRY tabloları (İş Yatırım). Kalem 3Z: dönem net kârı, yılbaşından itibaren birikimli. Kalem 2O: ana ortaklık özkaynağı. |
| Fiyat | yfinance günlük, `auto_adjust=False`. Bedelsizler `bolunme_duzelt` ile düzeltilir. Fonksiyonlar `h_testleri.py` ile ortaktır. |
| Sektör sepeti | Bu betikteki `SEKTOR100` eşlemesi (yaklaşık; 19 grup). Aynı sektördeki diğer hisselerin eşit ağırlıklı ortalaması, hisse hariç. Sektörde tek hisse varsa evrenin geri kalanı. |
| Maliyet | Gidiş-dönüş %0,25. |

## Sinyal

Her şirket ve her dönem (yıl y, çeyrek p) için:

**S = (NetKâr_YTD(y, p) − NetKâr_YTD(y−1, p)) / Özkaynak(y−1, p)**

- Özkaynak(y−1, p) ≤ 0 ya da verilerden biri eksikse şirket o dönem dışarıda kalır.
- Aynı dönemdeki şirketler S'ye göre sıralanır. En az 30 geçerli şirket gerekir; daha azsa o dönem atlanır.
- **İYİ:** en üst üçte bir.
- **KÖTÜ:** en alt üçte bir.

## Zamanlama (ileriye bakma yanlılığını önlemek için tutucu)

- **Bilgi tarihi:** dönem sonu + {Ç1: 60, Ç2: 70, Ç3: 60, Ç4: 80} takvim günü.
- Bu süreler yasal son tarihlerin (konsolide 40 / 50 / 40 / 70 gün) üzerindedir. Ç4'e 10 gün ek pay verildi; 2023 depremi sonrası olduğu gibi süre uzatmalarına karşı.
- **Giriş:** bilgi tarihine eşit ya da ondan sonraki ilk işlem gününün kapanışı. O dönemin bütün şirketleri aynı gün girer.
- **Sonuç:** Açıklama günü tepkisi ölçülmez. Yalnızca, herkes açıkladıktan sonra yakalanabilecek sürüklenme ölçülür.

## Birincil test

- **Portföy:** Her dönem İYİ üçte bir, eşit ağırlık.
- **Tutma:** 40 işlem günü.
- **Metrik:** Sektör sepetine göre net getiri (brüt − %0,25).
- **İstatistik birimi:** Dönem; dönem başına tek portföy. Portföyler üst üste binmez. t = ortalama / (standart sapma / √dönem sayısı).
- **Dönemler** (dönem sonu tarihine göre):
  - Örneklem içi (IS): 2021/03 – 2023/06.
  - Örneklem dışı (OOS): 2023/09 – 2026/03.
  - 2026/06 ve sonrası "taze" dönem olarak ayrı raporlanır; 40 günü dolmamışsa yer almaz.
- **Neden 2021'den başlıyor:** YTD karşılaştırması için bir önceki yılın verisi gerekir ve mali veri 2020/03'te başlıyor.

## Geçme kriterleri (beşi birden)

- **K1.** OOS ortalama > 0.
- **K2.** OOS t > 2,23. Yaklaşık 11 dönem için iki yönlü %5'lik t eşiği. Tek birincil test olduğu için ek düzeltme yok.
- **K3.** OOS dönemlerinin en az %60'ında getiri > 0.
- **K4.** Tek bir sektör çıkarıldığında her durumda OOS ortalama > 0 kalır.
- **K5.** IS ortalama > 0.

**Etiketler:** GEÇTİ (beşi birden). ZAYIF (K1 ve K5 tutuyor, diğerlerinden en az biri tutmuyor). ELENDİ (geri kalan her durum).

**Güç uyarısı:** 11 OOS dönemle yalnızca büyük etkiler yakalanabilir. Kaba hesap: dönem başına 40 günde 1,5 puan ve üzeri. ZAYIF etiketi "etki yok" anlamına gelmez; "bu veriyle kanıtlanamadı" anlamına gelir.

## Raporlanan ama hüküm vermeyenler

- İYİ eksi KÖTÜ farkı, brüt. Bilgi var mı sorusunun saf ölçüsü; açığa satış gerektirdiği için işlem stratejisi değildir.
- KÖTÜ üçte birin sektöre göre net getirisi. "Kötü bilanço sonrası uzak dur" kuralı adayı.
- Tutma süresi 10, 20 ve 60 gün; XU100'e göre net getiri.
- Bankalar hariç sürüm. Bankalar TMS 29 uygulamıyor, karşılaştırılabilirlik farklı.
- USD tablolarla aynı sinyal.
- Dönem bazında tablo: tarih, şirket sayısı, İYİ / KÖTÜ / fark.

## Bilinen sınırlar

1. **Hayatta kalma yanlılığı.** Bugünkü BIST100 üyeleri geçmişe uygulanıyor.
2. **Nokta-zaman verisi değil.** İş Yatırım'daki geçmiş rakamlar sonradan düzeltilmiş olabilir; o tarihte bilinenle birebir aynı değildir.
3. **TMS 29 kırılması.** 2024'ten itibaren enflasyon muhasebesi, aynı şirketin yıllar arası karşılaştırmasını bozabilir. Kesitsel sıralama bunu kısmen dengeler; bankalar hariç ve USD sürümleri bu yüzden raporlanır.
4. **Uzlaşı tahmini yok.** Sürpriz, analist beklentisine göre değil, geçen yılın aynı dönemine göre ölçülüyor. Basit bir vekildir.
5. **Açıklama tarihleri yaklaşık.** Şirket bazında gerçek KAP tarihi kullanılmıyor.
