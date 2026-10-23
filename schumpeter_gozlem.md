# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.5 | 1.0 | 1.16 | NORMAL | 0/1 (6 üye) |
| HAVACILIK | 0.67 | 0.33 | 1.81 | YAYILIYOR | 0/0 (3 üye) |
| SINAI | 0.0 | 0.33 | -5.92 | NORMAL | 0/2 (3 üye) |
| ENERJI | 0.5 | 0.75 | -0.94 | NORMAL | 0/1 (4 üye) |
| OTOMOTIV | 0.33 | 0.0 | -0.42 | NORMAL | 0/0 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.101 | -0.397 | -1.17 | 0.2433 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 1 | 3.734 | 0.101 | None | None | None | ORNEK YETERSIZ |
| H1 t10_kesif | 87 | 0.277 | 0.18 | 0.154 | 0.29 | 0.7752 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 0 | None | 0.18 | None | None | None | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 95 Özel Durum kaydı, bunun 10'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'GYO': 2, 'HAVACILIK': 1, 'SINAI': 1}
Eşik üstü (>= 2): ['GYO']

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
