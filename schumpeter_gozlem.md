# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.0 | 0.5 | -4.94 | DAGILIYOR | 1/4 (6 üye) |
| HAVACILIK | 0.33 | 1.0 | -0.63 | DAGILIYOR | 1/2 (3 üye) |
| SINAI | 0.67 | 0.33 | 0.24 | YAYILIYOR | 1/0 (3 üye) |
| ENERJI | 0.75 | 0.0 | 4.76 | YAYILIYOR | 2/1 (4 üye) |
| OTOMOTIV | 0.67 | 1.0 | 1.84 | GUCLU-YAYILMIS | 1/0 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.15 | -0.451 | -1.31 | 0.1902 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 9 | 1.754 | 0.15 | 1.663 | 1.1 | 0.2721 | ORNEK YETERSIZ |
| H1 t10_kesif | 87 | 0.277 | 0.266 | 0.06 | 0.11 | 0.9118 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 8 | 2.715 | 0.266 | 2.603 | 1.14 | 0.2524 | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 156 Özel Durum kaydı, bunun 14'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'BANKACILIK': 2, 'ENERJI': 1, 'SINAI': 1}
Eşik üstü (>= 2): ['BANKACILIK']

- H2 t10: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**
- H2 t20: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**

Son yenilik olayları:
- 2026-10-08 EKGYO (GYO): Umman Sultanlığı Konut ve Kentsel Planlama Bakanlığı ile Mutabakat Zaptı İmzalanması
- 2026-10-16 THYAO (HAVACILIK): CFM International ile LEAP-1B Motor Mutabakat Zaptı
- 2026-10-19 EKGYO (GYO): Ankara Yenimahalle Macunköy Sözleşme İmzalanması
- 2026-10-21 SISE (SINAI): Mısır'daki İkinci Düzcam Hattı Yatırım Projesinin Tamamlanması
- 2026-11-09 ENJSA (ENERJI): Enerji Depolama Tesisi Ön Lisansının İptaline İlişkin Hukuki Süreç
- 2026-11-10 EREGL (SINAI): Alacahan Altın Projesi, Maden Kaynak Tahmini Güncellemesi (UMREK Uyumlu)
- 2026-11-17 VAKBN (BANKACILIK): Dünya Bankası (IBRD) Kaynaklı İkiz Dönüşüm (TransformIndustry) Projesi Kapsamında Finansman Anlaşması İmzalanması
- 2026-11-23 ISCTR (BANKACILIK): Avrupa İmar ve Kalkınma Bankası ile İmzalanan Kredi Sözleşmeleri Hk.

---
H3 (rant erimesi) ve H4 (kredi dalgası) bu sürümde yok.
Keşifsel (önkayıt öncesi) sonuçlar verdikt taşımaz; yalnız teyit olayları değerlendirilir.
