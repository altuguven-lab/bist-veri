# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.83 | 0.33 | 4.92 | YAYILIYOR | 2/0 (6 üye) |
| HAVACILIK | 1.0 | 0.0 | 14.78 | YAYILIYOR | 2/0 (3 üye) |
| SINAI | 0.67 | 0.0 | 3.47 | YAYILIYOR | 2/1 (3 üye) |
| ENERJI | 0.25 | 0.5 | -2.7 | DAGILIYOR | 2/1 (4 üye) |
| OTOMOTIV | 0.67 | 0.67 | 2.94 | GUCLU-YAYILMIS | 2/0 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.108 | -0.405 | -1.19 | 0.236 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 4 | 0.188 | 0.108 | 0.115 | 0.07 | 0.9433 | ORNEK YETERSIZ |
| H1 t10_kesif | 87 | 0.277 | 0.165 | 0.168 | 0.31 | 0.7547 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 2 | 3.249 | 0.165 | 3.403 | 38.88 | 0.0 | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 124 Özel Durum kaydı, bunun 10'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'GYO': 1, 'SINAI': 1}
Eşik üstü (>= 2): -

- H2 t10: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**
- H2 t20: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**

Son yenilik olayları:
- 2026-09-18 ASELS (SAVUNMA): Devreye Alınan Yatırımımız Hakkında
- 2026-09-23 THYAO (HAVACILIK): Ortaklığımızın Stratejik Planı Çerçevesindeki Uçak Siparişleri
- 2026-09-28 EKGYO (GYO): Eyüpsultan Kemerburgaz 3. Etap Sözleşme İmzalanması
- 2026-10-01 OTKAR (OTOMOTIV): Askeri araç tedariğine yönelik yeni ihracat sözleşmesi imzalanması
- 2026-10-08 EKGYO (GYO): Umman Sultanlığı Konut ve Kentsel Planlama Bakanlığı ile Mutabakat Zaptı İmzalanması
- 2026-10-16 THYAO (HAVACILIK): CFM International ile LEAP-1B Motor Mutabakat Zaptı
- 2026-10-19 EKGYO (GYO): Ankara Yenimahalle Macunköy Sözleşme İmzalanması
- 2026-10-21 SISE (SINAI): Mısır'daki İkinci Düzcam Hattı Yatırım Projesinin Tamamlanması

---
H3 (rant erimesi) ve H4 (kredi dalgası) bu sürümde yok.
Keşifsel (önkayıt öncesi) sonuçlar verdikt taşımaz; yalnız teyit olayları değerlendirilir.
