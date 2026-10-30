# ÖN KAYIT: H7 makro risk iştahı bayrağı ile endeks zamanlaması

**Kayıt tarihi:** 30.10.2026, H7'nin hiçbir sonucu görülmeden.
**Uygulayan betik:** `h7_makro_rejim.py`
**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h7/deneme_kaydi.json` dosyasına eklenir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## İddia

Ay sonunda bilinen üç makro gösterge "risk iştahı açık" diyorsa, XU100 sonraki ay TL faizinin üzerinde, "kapalı" diyorsa altında getiri sağlar. Kurumlardaki "yukarıdan aşağı" (top-down) varlık dağılımı katmanının basit bir karşılığıdır: hisse mi, TL nakit mi.

## Veri

| Gösterge | Kaynak | Tanım (ay sonu t) | Risk iştahı açık |
|---|---|---|---|
| S1 Kur | EVDS TP.DK.USD.A.YTL (günlük) | Son 1 aylık USD/TRY değişimi | Bu değişim, önceki 12 ayın aylık değişimlerinin medyanından düşükse. TL'nin yapısal değer kaybı medyanla dengelenir. |
| S2 Faiz yönü | EVDS TP.APIFON4 (TCMB ağırlıklı ortalama fonlama maliyeti, günlük) | t ile t−3 ay arası değişim | Değişim ≤ 0 ise (faiz sabit ya da düşüyor) |
| S3 Küresel risk | yfinance ^VIX (günlük) | t'den bir önceki ABD işlem günü kapanışı (BIST kapanışından sonra oluştuğu için bir gün geriden) | VIX, önceki 12 ayın günlük medyanından düşükse |

- **Bileşik bayrak:** Üç göstergeden en az 2'si "açık" diyorsa RİSK_AÇIK, aksi hâlde RİSK_KAPALI.
- **Endeks:** yfinance XU100.IS, fiyat bazlı. 2020'deki iki sıfır atma kırılması `bolunme_duzelt` ile düzeltilir.
- **TL faizi:** Ay sonu t'deki TP.APIFON4 / 12. Sonraki ay için basit aylık getiri varsayımı.
- **Fazla getiri:** XU100'ün t ile t+1 ay sonu arası getirisi − TL faizi.

## Strateji ve test

- **Strateji:** RİSK_AÇIK aylarda XU100 tutulur, RİSK_KAPALI aylarda TL faizi alınır. Fazla getirisi RİSK_KAPALI aylarda 0'dır.
- **Maliyet:** Her rejim değişiminde %0,25 (endeks fonu/VİOP alım-satımı).
- **Birincil fark:** RİSK_AÇIK ayların ortalama fazla getirisi − RİSK_KAPALI ayların ortalama fazla getirisi. İstatistik: Welch t.
- **Dönemler** (oluşum ayına göre). S2'nin 3 aylık ve S1/S3'ün 12 aylık geçmiş ihtiyacı yüzünden başlangıç 2012-01.
  - IS: 2012-01 – 2019-12.
  - OOS: 2020-01 – 2026-06.
  - 2026-07 sonrası "taze" olarak raporlanır.

## Geçme kriterleri (beşi birden)

- **K1.** OOS birincil fark > 0.
- **K2.** OOS Welch t > 2,0.
- **K3.** OOS'ta RİSK_KAPALI ayların ortalama fazla getirisi < 0. Bayrak gerçekten kötü ayları ayırıyor olmalı.
- **K4.** OOS'ta stratejinin aylık ortalama fazla getirisi (maliyet sonrası) > al-tut stratejisininki.
- **K5.** IS birincil fark > 0.

**Etiketler:** GEÇTİ (beşi birden). ZAYIF (K1 ve K5 tutuyor, diğerlerinden en az biri tutmuyor). ELENDİ (geri kalan her durum).

## Raporlanan ama hüküm vermeyenler

- Her göstergenin tek başına farkı (S1, S2, S3).
- USD bazlı XU100 getirisiyle aynı fark.
- Trend filtresi: XU100 > 10 aylık hareketli ortalama. Kurumlarda yaygın bir zamanlama kuralı; karşılaştırma için raporlanır, bileşiğe girmez.
- RİSK_AÇIK ay oranı, rejim değişimi sayısı, stratejinin en kötü 12 aylık dönemi.
- Güncel bayrak durumu (son ay sonu).

## Bilinen sınırlar

1. **Rejim kırılmaları.** Türkiye'de 2018 kur krizi, 2021–2023 ortodoks dışı para politikası ve 2023 sonrası sıkılaşma gibi kırılmalar var. Bir göstergenin işareti dönemden döneme değişebilir.
2. **Fon maliyeti yaklaşıktır.** TP.APIFON4, mevduat/para piyasası fonu getirisinin vekilidir.
3. **Az gözlem.** Aylık seri, OOS'ta 78 ay. Rejim değişimleri azsa etkin gözlem daha düşüktür.
4. **Temettü yok.** XU100 fiyat endeksi; temettüler hariç, bu da hisse tarafı aleyhine bir yanlılıktır.
