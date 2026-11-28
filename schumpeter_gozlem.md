# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.33 | 0.33 | -1.42 | NORMAL | 1/5 (6 üye) |
| HAVACILIK | 1.0 | 1.0 | 1.58 | GUCLU-YAYILMIS | 1/0 (3 üye) |
| SINAI | 0.33 | 0.67 | -2.2 | DAGILIYOR | 3/0 (3 üye) |
| ENERJI | 0.75 | 0.0 | 2.28 | YAYILIYOR | 4/0 (4 üye) |
| OTOMOTIV | 0.67 | 1.0 | 1.5 | GUCLU-YAYILMIS | 0/0 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.149 | -0.45 | -1.31 | 0.191 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 9 | 1.754 | 0.149 | 1.662 | 1.1 | 0.2722 | ORNEK YETERSIZ |
| H1 t10_kesif | 87 | 0.277 | 0.263 | 0.064 | 0.12 | 0.9061 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 8 | 2.715 | 0.263 | 2.608 | 1.15 | 0.2521 | ORNEK YETERSIZ |

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
