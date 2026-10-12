# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.83 | 0.83 | 1.36 | GUCLU-YAYILMIS | 3/3 (6 üye) |
| HAVACILIK | 0.33 | 1.0 | -1.11 | DAGILIYOR | 0/1 (3 üye) |
| SINAI | 1.0 | 0.33 | 3.24 | YAYILIYOR | 1/0 (3 üye) |
| ENERJI | 0.75 | 0.25 | 0.82 | YAYILIYOR | 0/2 (4 üye) |
| OTOMOTIV | 1.0 | 0.67 | 1.66 | GUCLU-YAYILMIS | 1/1 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 84 | -0.277 | 0.108 | -0.346 | -1.0 | 0.3161 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 0 | None | 0.108 | None | None | None | ORNEK YETERSIZ |
| H1 t10_kesif | 85 | 0.407 | 0.168 | 0.319 | 0.59 | 0.5526 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 0 | None | 0.168 | None | None | None | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 69 Özel Durum kaydı, bunun 7'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'GYO': 2, 'HAVACILIK': 1, 'OTOMOTIV': 1}
Eşik üstü (>= 2): ['GYO']

- H2 t10: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**
- H2 t20: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**

Son yenilik olayları:
- 2026-08-26 EKGYO (GYO): İstanbul Küçükçekmece Halkalı Batı 1. Etap Sözleşme İmzalanması
- 2026-09-14 EKGYO (GYO): İstanbul Ümraniye Tepeüstü Sözleşme İmzalanması
- 2026-09-18 ASELS (SAVUNMA): Devreye Alınan Yatırımımız Hakkında
- 2026-09-23 THYAO (HAVACILIK): Ortaklığımızın Stratejik Planı Çerçevesindeki Uçak Siparişleri
- 2026-09-28 EKGYO (GYO): Eyüpsultan Kemerburgaz 3. Etap Sözleşme İmzalanması
- 2026-10-01 OTKAR (OTOMOTIV): Askeri araç tedariğine yönelik yeni ihracat sözleşmesi imzalanması
- 2026-10-08 EKGYO (GYO): Umman Sultanlığı Konut ve Kentsel Planlama Bakanlığı ile Mutabakat Zaptı İmzalanması

---
H3 (rant erimesi) ve H4 (kredi dalgası) bu sürümde yok.
Keşifsel (önkayıt öncesi) sonuçlar verdikt taşımaz; yalnız teyit olayları değerlendirilir.
