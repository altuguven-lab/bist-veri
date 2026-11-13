# Schumpeter gözlem katmanı (SALT ÖLÇÜM)

Önkayıt sürümü 2 · önkayıt tarihi 2026-10-11 · α=0.0125 · min olay 30
Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.

## H1 — Yığılma (sektör içi yayılma)

| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |
|---|---|---|---|---|---|
| BANKACILIK | 0.83 | 0.83 | 1.33 | GUCLU-YAYILMIS | 0/4 (6 üye) |
| HAVACILIK | 0.67 | 1.0 | 3.76 | GUCLU-YAYILMIS | 2/0 (3 üye) |
| SINAI | 0.0 | 0.67 | -2.53 | DAGILIYOR | 2/1 (3 üye) |
| ENERJI | 0.5 | 0.25 | 2.06 | NORMAL | 2/2 (4 üye) |
| OTOMOTIV | 1.0 | 0.0 | 3.06 | YAYILIYOR | 1/0 (2 üye) |

Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):

| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |
|---|---|---|---|---|---|---|---|
| H1 t5_kesif | 86 | -0.326 | 0.143 | -0.44 | -1.28 | 0.1991 | KESIFSEL (verdikt yok) |
| H1 t5_teyit | 7 | 2.161 | 0.143 | 2.039 | 1.09 | 0.2769 | ORNEK YETERSIZ |
| H1 t10_kesif | 87 | 0.277 | 0.209 | 0.123 | 0.23 | 0.8191 | KESIFSEL (verdikt yok) |
| H1 t10_teyit | 4 | 0.871 | 0.209 | 0.731 | 0.23 | 0.8147 | ORNEK YETERSIZ |

## H2 — Yenilik yoğunluğu (KAP)

Defter: 142 Özel Durum kaydı, bunun 12'i yenilik türü · ilk kayıt 2026-08-25
Son 20 gün sektör sayacı: {'ENERJI': 1, 'SINAI': 1}
Eşik üstü (>= 2): -

- H2 t10: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**
- H2 t20: n=0, fark=None%, t=None, p=None → **ORNEK YETERSIZ**

Son yenilik olayları:
- 2026-09-28 EKGYO (GYO): Eyüpsultan Kemerburgaz 3. Etap Sözleşme İmzalanması
- 2026-10-01 OTKAR (OTOMOTIV): Askeri araç tedariğine yönelik yeni ihracat sözleşmesi imzalanması
- 2026-10-08 EKGYO (GYO): Umman Sultanlığı Konut ve Kentsel Planlama Bakanlığı ile Mutabakat Zaptı İmzalanması
- 2026-10-16 THYAO (HAVACILIK): CFM International ile LEAP-1B Motor Mutabakat Zaptı
- 2026-10-19 EKGYO (GYO): Ankara Yenimahalle Macunköy Sözleşme İmzalanması
- 2026-10-21 SISE (SINAI): Mısır'daki İkinci Düzcam Hattı Yatırım Projesinin Tamamlanması
- 2026-11-09 ENJSA (ENERJI): Enerji Depolama Tesisi Ön Lisansının İptaline İlişkin Hukuki Süreç
- 2026-11-10 EREGL (SINAI): Alacahan Altın Projesi, Maden Kaynak Tahmini Güncellemesi (UMREK Uyumlu)

---
H3 (rant erimesi) ve H4 (kredi dalgası) bu sürümde yok.
Keşifsel (önkayıt öncesi) sonuçlar verdikt taşımaz; yalnız teyit olayları değerlendirilir.
