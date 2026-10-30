# ÖN KAYIT: H6 kurumsal tarzda çok faktörlü aylık sıralama

**Kayıt tarihi:** 30.10.2026, H6'nın hiçbir sonucu görülmeden.
**Uygulayan betik:** `h6_faktor_siralama.py`
**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h6/deneme_kaydi.json` dosyasına eklenir.
- Sonuç görüldükten sonra yapılan her değişiklik "ön kayıt değişikliği" sayılır; o sonuç keşiftir, hüküm değildir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## İddia

Sistematik fonların kullandığı beş faktörün eşit ağırlıklı bileşik skoruna göre her ay BIST100'ün en üst %20'sini tutan portföy, maliyet sonrası **evrenin eşit ağırlıklı ortalamasını** geçer. Yani faktörler gerçekten iyi hisseleri seçer.

**Dayanak:**
- Kısa ufuklu fiyat sinyalleri (alarm karnesi, H1–H3) kenar üretmedi.
- Bilgi taşıyan tek kaynak, bilanço (H4), orta ufukta çalıştı.
- Uluslararası literatürde bu beş faktörün orta ufukta getiriyle ilişkisi belgelenmiştir. BIST'te bulgular karışıktır; bu test bunu ölçecek.

## Veri

| Konu | Tanım |
|---|---|
| Evren | `config/bist100_uyeler.txt` ile `data/temel/ham_*.json` kesişimi. `config/kapsam_disi.txt` hisseleri tamamen çıkarılır. |
| Fiyat | yfinance günlük, `auto_adjust=False`. Bedelsizler `bolunme_duzelt` ile düzeltilir (`h_testleri.panel_kur`). |
| Mali veri | İş Yatırım TRY tabloları. 3Z: dönem net kârı, yılbaşından birikimli. 2O: ana ortaklık özkaynağı. 2OA: ödenmiş sermaye. |
| Bilinirlik | Bir çeyreğin mali verisi, dönem sonu + {Ç1: 60, Ç2: 70, Ç3: 60, Ç4: 80} gün sonra kullanılabilir sayılır (H4 ile aynı). Her ay sonunda yalnızca o güne kadar bilinir olan en son çeyrek kullanılır. |
| Piyasa değeri | Düzeltilmiş kapanış × **güncel** hisse adedi (en son 2OA / 1 TL nominal). `temel_carpan_gozlem.py` ile aynı yöntem. Bedelli sermaye artırımı olan hisselerde geçmiş değer sapabilir. |
| Sektör | `h4_bilanco_surprizi.SEKTOR100` (19 grup). |
| Maliyet | Gidiş-dönüş %0,25 × aylık devir oranı (portföyün değişen payı; ilk ay 1). |

## Faktörler

Her ayın son işlem günü hesaplanır; yalnızca o güne kadarki bilgi kullanılır.

| # | Faktör | Tanım | Yön |
|---|---|---|---|
| F1 | Momentum | t−252 ile t−21 işlem günü arası getiri (son ay hariç 12 ay) | Yüksek iyi |
| F2 | Düşük oynaklık | Son 252 işlem günü günlük getirilerinin standart sapması | Düşük iyi |
| F3 | Değer | Kazanç getirisi (TTM net kâr / piyasa değeri) ile defter/piyasa (özkaynak / piyasa değeri) sıralamalarının ortalaması | Yüksek iyi |
| F4 | Kalite | TTM net kâr / ortalama özkaynak (dönem ve bir yıl önceki aynı dönem) | Yüksek iyi |
| F5 | Bilanço sürprizi | H4'teki S: (YTD net kâr − bir yıl önceki aynı YTD) / bir yıl önceki aynı dönem özkaynağı | Yüksek iyi |

**Tanımlar:**
- **TTM net kâr:** Yıl sonu (Ç4) için yıllık kâr. Diğer çeyrekler için: dönem YTD + önceki yıl yıllık − önceki yıl aynı dönem YTD.
- **Geçerlilik şartları:** F1 ve F2 için en az 252 günlük fiyat geçmişi gerekir. F3–F5 için ilgili kalemler bulunmalı. F3'te piyasa değeri > 0 olmalı.

## Bileşik skor ve portföy

- **Bileşik skor:** Her faktör, o ay geçerli hisseler içinde 0–1 arası yüzdelik sıraya çevrilir; ters yönlü faktörde sıra tersine çevrilir. Bileşik skor = geçerli faktörlerin ortalaması. En az 3 faktörü geçerli olmayan hisse o ay sıralanmaz.
- **Portföy:** Bileşik skorda en üst %20, eşit ağırlık. En az 30 sıralanan hisse gerekir.
- **Tutma:** Bir ay, bir sonraki ayın son işlem gününe kadar.
- **Birincil metrik:** Aylık net fazla getiri = portföy getirisi − maliyet − evren ortalaması getirisi. Evren ortalaması, o ay sıralanan bütün hisselerin eşit ağırlıklı getirisidir.
- **Neden XU100 değil:** Ön kayıt yazılırken sahte, etkisiz fiyatlarla yapılan denemede eşit ağırlıklı ve aylık yenilenen bir sepet hiçbir faktör bilgisi olmadan XU100'ü geçti. Bu, oynak hisselerin aritmetik ortalaması ve küçük hisselerin artan ağırlığından doğan matematiksel bir etkidir. XU100'e göre ölçüm faktör becerisini değil, eşit ağırlığı da ölçerdi.
- **XU100'e göre net getiri** yatırımcı açısından önemlidir; ikincil olarak raporlanır.
- **İstatistik:** Aylık seri üzerinde ortalama ve 2 gecikmeli Newey-West t.

## Dönemler (oluşum ayına göre)

- Temel faktörler ancak 2020 yıllık verisi bilinir olduktan sonra kullanılabiliyor. Bu yüzden bileşik testin ilk ayı Nisan 2021.
- **Bileşik IS:** 2021-04 – 2023-12.
- **Bileşik OOS:** 2024-01 – 2026-06.
- 2026-07 ve sonrası "taze" olarak ayrı raporlanır, hükme girmez.
- **Tek faktör testleri (raporlanır):**
  - F1 ve F2: IS 2016-01 – 2022-12, OOS 2023-01 – 2026-06.
  - F3–F5: bileşikle aynı dönemler.

## Geçme kriterleri (bileşik, beşi birden)

- **K1.** OOS aylık net fazla getiri ortalaması > 0.
- **K2.** OOS t > 2,0.
- **K3.** OOS takvim yıllarının (2024, 2025, 2026 ilk yarı) en az 2'sinde ortalama > 0.
- **K4.** Tek bir sektör çıkarıldığında her durumda OOS ortalama > 0 kalır.
- **K5.** IS ortalama > 0.

**Etiketler:** GEÇTİ (beşi birden). ZAYIF (K1 ve K5 tutuyor, diğerlerinden en az biri tutmuyor). ELENDİ (geri kalan her durum).

**Güç uyarısı:** OOS 30 aydır. Aylık fazla getirinin oynaklığı %4 civarındaysa, t > 2 için ayda yaklaşık 1,5 puanlık bir üstünlük gerekir; bu büyük bir etkidir. ZAYIF etiketi "etki yok" anlamına gelmez. Bu durumda gölge izlemeye alınır, H4'te olduğu gibi.

## Raporlanan ama hüküm vermeyenler

- Her faktör için üst %20 portföyün evren ortalamasına göre net getirisi. Beş faktör aynı anda test edildiği için Benjamini-Hochberg (q = 0,10) düzeltmesiyle. XU100'e göre değerleri de raporlanır.
- Her faktör için üst %20 − alt %20 farkı, brüt. Bilgi var mı sorusunun saf ölçüsüdür; açığa satış gerektirdiği için işlem stratejisi değildir.
- Bileşik portföyün XU100'e göre net getirisi.
- Bankalar hariç bileşik.
- Ortalama aylık devir oranı ve portföydeki ortalama hisse sayısı.
- Güncel (en son ay sonu) bileşik sıralama listesi. Gözlem amaçlıdır.

## Bilinen sınırlar

1. **Hayatta kalma yanlılığı.** Bugünkü BIST100 üyeleri geçmişe uygulanıyor. Bu, momentum ve kaliteyi olduğundan iyi gösterebilir.
2. **Nokta-zaman verisi değil.** Geçmiş mali rakamlar sonradan düzeltilmiş olabilir.
3. **TMS 29.** 2024'ten itibaren enflasyon muhasebesi, değer ve kalite ölçülerini etkiler. Aynı ay içindeki kesitsel sıralama bunu kısmen dengeler.
4. **Piyasa değeri yaklaşık.** Güncel adetle hesaplanıyor; bedelli artırımlarda sapma olabilir.
5. **Temettü yok.** Getiriler fiyat bazlı, temettü hariç. Yüksek temettülü (çoğu zaman değer) hisseler aleyhine bir yanlılık yaratır.
6. **Tek kaynak.** Fiyatlar Yahoo'dan, mali tablolar İş Yatırım'dan.
