# ÖN KAYIT: H8 keşif bataryası (kalan bütün seçenekler)

**Kayıt tarihi:** 30.10.2026, H8 testlerinin hiçbirinin sonucu görülmeden.
**Uygulayan betik:** `h8_kesif_bataryasi.py`
**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h8/deneme_kaydi.json` dosyasına eklenir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## Amaç

Başkan kararı (30.10): "Bakmadığımız seçenek kalmasın; böylece neye bakmayacağımızı da öğreniyoruz." Elimizdeki veriyle test edilebilen bütün yaygın hisse seçimi, olay ve takvim etkileri tek bir ön kayıt altında, **birlikte** test edilir.

**Çok sayıda test olduğu için iki önlem:**
1. 15 testin hepsi aynı aileye konur; Benjamini-Hochberg (q = 0,10) çoklu test düzeltmesi uygulanır.
2. Hiçbir test "GEÇTİ" almaz. En iyi etiket **ADAY**'dır; aday ancak ayrı bir ön kayıtla gölge izlemeye alınabilir.

## Ortak tanımlar

- **Evren, fiyat, mali veri, sektör:** `ON_KAYIT_H6.md` ile aynı (BIST100 ∩ `data/temel`, kapsam dışı hariç, `SEKTOR100`).
- **Kesitsel testler (X):** Her ay sonu skora göre üst %20 (en az 5 hisse), eşit ağırlık, bir ay tutulur. Metrik: evrenin eşit ağırlıklı ortalamasına göre aylık net getiri, maliyet %0,25 × devir. İstatistik: 2 gecikmeli Newey-West t.
  - IS: 2016-01 – 2022-12.
  - OOS: 2023-01 – 2026-06.
- **Olay testleri (E):** Olay penceresindeki hisse getirisi − aynı penceredeki evren eşit ağırlıklı ortalaması. İstatistik: ISO hafta kümelenmiş t. Alınabilir (uzun) olaylarda %0,25 maliyet düşülür. Dönemler kesitsel testlerle aynı, olay tarihine göre.
- **Takvim testleri (T):** XU100 günlük ya da aylık getirileri. Yahoo'dan 2005'ten itibaren çekilir; 2020 sıfır atma kırılması düzeltilir. İstatistik: iki grup arasındaki ortalama farkı için Welch t. Maliyet yok; bunlar endeks düzeyinde desen testidir.
  - IS: 2006-01 – 2017-12.
  - OOS: 2018-01 – 2026-06.

## Testler ve beklenen yön

| Kod | Test | Tanım | Beklenen |
|---|---|---|---|
| X1 | Temettü verimi | Son 12 ayda dağıtılan temettü (yfinance) / fiyat; yüksek olan üst %20 | + |
| X2 | 1 aylık dönüş | Son 21 işlem gününde en çok düşen %20 | + |
| X3 | 52 hafta zirvesine yakınlık | Fiyat / son 252 günün en yüksek kapanışı; zirveye en yakın %20 | + |
| X4 | 6 aylık momentum | t−126 ile t−21 arası getiri; en yüksek %20 | + |
| X5 | Küçük büyüklük | Piyasa değeri (fiyat × güncel adet); en küçük %20 | + |
| X6 | Düşük likidite primi | Amihud ölçüsü: son 63 günde ortalama \|günlük getiri\| / TL işlem hacmi; en az likit %20 | + |
| X7 | Düşük beta | Son 252 günde XU100'e göre beta; en düşük %20 | + |
| X8 | Sektör momentumu | Sektörlerin eşit ağırlıklı 12−1 aylık getirisi; en iyi %20 sektördeki (en az 2 hisseli sektörler arasında, en az 1 sektör) bütün hisseler | + |
| E1 | Bedelsiz öncesi | Bedelsiz/bölünme yürürlük günü d. Kapanış(d−11) → kapanış(d−1), net | + |
| E2 | Bedelsiz sonrası | Kapanış(d−1) → kapanış(d+19), brüt (kaçınma kuralı adayı) | − |
| E3 | Temettü öncesi | Hak kullanım günü d. Kapanış(d−11) → kapanış(d−1), net | + |
| T1 | Ay dönümü | Ayın son işlem günü ve sonraki ayın ilk 3 işlem günü, diğer günlere göre günlük getiri farkı | + |
| T2 | Tatil öncesi | Ertesi iş günü tatil olan işlem günleri, diğer günlere göre | + |
| T3 | Kasım–Nisan | Kasım–Nisan ayları, Mayıs–Ekim aylarına göre aylık getiri farkı | + |
| T4 | Pazartesi | Pazartesi günleri, diğer günlere göre | − |

**Olay tarihleri:**
- **Bedelsiz:** yfinance `splits` (oran ≥ 1,2) ile `bolunme_duzelt`'in Yahoo'nun düzeltmediği bölünmeler için bulduğu günlerin birleşimi; aynı hissede 30 gün içinde tekrar edenler tek olay.
- **Temettü:** yfinance `dividends` tarihleri (hak kullanım günü).
- **Not:** Yürürlük ve hak kullanım tarihleri genellikle haftalar önce açıklanır (SPK onayı, genel kurul). Ama açıklama günü veride yok; d−11 girişinin o tarihte bilindiği varsayılır.

## Hüküm (her test için ayrı)

- **ADAY:** OOS'ta işaret beklenen yönde, BH-anlamlı (15 testin OOS p değerleri birlikte), IS'te de işaret beklenen yönde.
- **TERS:** OOS'ta işaret beklenenin tersine ve BH-anlamlı.
- **KENAR_YOK:** Diğer durumlar. Bu, "bu konuya artık bakmayacağız" demektir; yeniden test ancak yeni veriyle ve yeni ön kayıtla açılır.

## Bu bataryada da test edilemeyenler (veri yok)

Kayda geçmesi için listelenir. Yeniden açılmaları ancak veri bulunursa mümkün:
- **BIST endeks değişiklikleri** (giriş/çıkış öncesi fon alımı): Geçmiş değişiklik listesi repoda yok.
- **Aracı kurum hedef fiyat / tahmin revizyonları:** Repodaki kayıtlar Ağustos 2026'dan beri; geçmişe dönük konsensüs yok.
- **Yabancı payı / takas / AKD:** Takas verisi lisanslı; yabancı payı kayıtları bayat ve kısa.
- **VİOP açık pozisyon ve açığa satış:** Repodaki seri birkaç aylık.
- **Fon portföy dağılımları (TEFAS/KAP aylık raporlar):** Toplanmadı.
- **Haber/duygu analizi, opsiyon verisi, emir defteri:** Yok.

## Bilinen sınırlar

- H6'nın altı sınırı aynen geçerli.
- Yahoo temettü ve bölünme kayıtları BIST için eksik olabilir.
- Hacim verisi Yahoo'dan; bazı günlerde eksik ya da hatalı olabilir.
- Takvim testlerinin bir kısmı (T1, T2, T4) işlem maliyeti nedeniyle doğrudan uygulanabilir olmayabilir; desen bilgisi olarak okunur.
