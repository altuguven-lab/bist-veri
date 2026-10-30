# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.17 | 0.83 | -1.37 | DAGILIYOR | 0/5 (6 üye) |
| HAVACILIK | 0.0 | 0.67 | -3.8 | DAGILIYOR | 0/2 (3 üye) |
| SINAI | 0.0 | 0.33 | -6.26 | NORMAL | 0/3 (3 üye) |
| ENERJI | 0.75 | 0.25 | 3.93 | YAYILIYOR | 0/3 (4 üye) |
| OTOMOTIV | 1.0 | 0.0 | 4.98 | YAYILIYOR | 0/1 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.092 | -0.388 | -1.14 | 0.2547 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 2 | 1.737 | 0.092 | 1.834 | 1.12 | 0.2623 | ORNEK YETERSIZ |
| H1 t10_kesif | 87 | 0.277 | 0.171 | 0.163 | 0.3 | 0.7618 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 1 | 4.018 | 0.171 | None | None | None | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 102 Özel Durum kaydı, bunun 10'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'HAVACILIK': 1, 'GYO': 1, 'SINAI': 1}
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
