# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 1.0 | 0.83 | 3.76 | GUCLU-YAYILMIS | 0/2 (6 üye) |
| HAVACILIK | 0.33 | 0.33 | 0.64 | NORMAL | 0/2 (3 üye) |
| SINAI | 0.33 | 1.0 | -2.36 | DAGILIYOR | 0/3 (3 üye) |
| ENERJI | 0.75 | 0.75 | -2.35 | GUCLU-YAYILMIS | 0/4 (4 üye) |
| OTOMOTIV | 0.0 | 1.0 | -4.1 | DAGILIYOR | 0/0 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.104 | -0.402 | -1.18 | 0.2369 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 0 | None | 0.104 | None | None | None | ORNEK YETERSIZ |
| H1 t10_kesif | 85 | 0.407 | 0.186 | 0.301 | 0.56 | 0.5756 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 0 | None | 0.186 | None | None | None | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 81 Özel Durum kaydı, bunun 8'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'GYO': 2, 'OTOMOTIV': 1, 'HAVACILIK': 1}
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
- 2026-10-16 THYAO (HAVACILIK): CFM International ile LEAP-1B Motor Mutabakat Zaptı

---
H3 (rant erimesi) ve H4 (kredi dalgası) bu sürümde yok.
Keşifsel (önkayıt öncesi) sonuçlar verdikt taşımaz; yalnız teyit olayları değerlendirilir.
