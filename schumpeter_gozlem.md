# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.5 | 0.17 | 0.77 | NORMAL | 0/2 (6 üye) |
| HAVACILIK | 1.0 | 0.67 | 5.27 | GUCLU-YAYILMIS | 0/1 (3 üye) |
| SINAI | 0.33 | 0.67 | -1.55 | DAGILIYOR | 0/1 (3 üye) |
| ENERJI | 0.0 | 0.25 | -3.96 | NORMAL | 0/3 (4 üye) |
| OTOMOTIV | 1.0 | 0.33 | 4.57 | YAYILIYOR | 0/2 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.141 | -0.441 | -1.28 | 0.199 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 8 | 2.248 | 0.141 | 2.185 | 1.35 | 0.178 | ORNEK YETERSIZ |
| H1 t10_kesif | 87 | 0.277 | 0.258 | 0.071 | 0.13 | 0.8957 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 7 | 2.514 | 0.258 | 2.291 | 0.88 | 0.3815 | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 149 Özel Durum kaydı, bunun 13'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'ENERJI': 1, 'SINAI': 1, 'BANKACILIK': 1}
Eşik üstü (>= 2): -

- H2 t10: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**
- H2 t20: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**

Son yenilik olayları:
- 2026-10-01 OTKAR (OTOMOTIV): Askeri araç tedariğine yönelik yeni ihracat sözleşmesi imzalanması
- 2026-10-08 EKGYO (GYO): Umman Sultanlığı Konut ve Kentsel Planlama Bakanlığı ile Mutabakat Zaptı İmzalanması
- 2026-10-16 THYAO (HAVACILIK): CFM International ile LEAP-1B Motor Mutabakat Zaptı
- 2026-10-19 EKGYO (GYO): Ankara Yenimahalle Macunköy Sözleşme İmzalanması
- 2026-10-21 SISE (SINAI): Mısır'daki İkinci Düzcam Hattı Yatırım Projesinin Tamamlanması
- 2026-11-09 ENJSA (ENERJI): Enerji Depolama Tesisi Ön Lisansının İptaline İlişkin Hukuki Süreç
- 2026-11-10 EREGL (SINAI): Alacahan Altın Projesi, Maden Kaynak Tahmini Güncellemesi (UMREK Uyumlu)
- 2026-11-17 VAKBN (BANKACILIK): Dünya Bankası (IBRD) Kaynaklı İkiz Dönüşüm (TransformIndustry) Projesi Kapsamında Finansman Anlaşması İmzalanması

---
H3 (rant erimesi) ve H4 (kredi dalgası) bu sürümde yok.
Keşifsel (önkayıt öncesi) sonuçlar verdikt taşımaz; yalnız teyit olayları değerlendirilir.
