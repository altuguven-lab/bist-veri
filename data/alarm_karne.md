# Alarm Karnesi

Uretim: 2026-11-14T14:26 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 208 | 0.538 (1.7) | -0.216 | 0.288 (0.91 / 0.75) | 0.32 (0.73) | 0.096 (0.37) | 0.728 | 52.4 | 0.006 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 144 | 0.52 (1.04) | -0.148 | 0.27 (0.54 / 0.82) | 0.303 (0.53) | 1.105 (1.64) | 1.798 | 49.1 | 0.048 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 287 | -0.247 (-0.68) | -0.329 | -0.497 (-1.37 / -1.95) | -0.506 (-1.21) | -0.217 (-0.3) | 0.647 | 42.5 | -0.434 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 136 | -0.091 (-0.22) | -0.533 | -0.341 (-0.83 / -0.94) | -0.262 (-0.54) | 0.118 (0.31) | 0.331 | 53.1 | -0.422 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 72 | 0.134 (0.18) | -0.423 | -0.116 (-0.16 / -0.17) | -0.117 (-0.14) | 0.106 (0.13) | -0.622 | 52.3 | -1.317 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -2.888 (-1.51) | -2.114 | 43.6 | 2.393 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 62 | -0.505 (None) | -0.512 | -0.755 (None / -0.88) | -1.3 (None) | None (None) | None | 50.0 | 1.594 | **YETERSIZ_ORNEK** |
| IC_STOP | KRITIK | ASAGI | 57 | 2.017 (None) | 0.488 | 2.017 (None / 2.19) | 1.823 (None) | None (None) | None | 87.5 | -1.681 | **YETERSIZ_ORNEK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -2.1 (-1.33) | -0.393 | -2.1 (-1.33 / -1.26) | -1.23 (-0.76) | -3.675 (-1.41) | -0.46 | 51.9 | 1.646 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 21 | 3.375 (1.63) | -0.438 | 3.125 (1.51 / 1.25) | 3.088 (1.59) | 2.049 (1.09) | 3.765 | 60.0 | 2.645 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 12 | None (None) | -1.367 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | None (None) | 1.128 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 11 / -0.256 | 15 / -3.827 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 1 / None | 0 / None | 1 / None | 66.7 |
| IC_STOP | 0 / None | 8 / 2.017 | 3 / 2.599 | 5 / 1.668 | 82.5 |
| P2_ADAY | 28 / -0.946 | 37 / 0.512 | 17 / -0.737 | 48 / 0.104 | 76.4 |
| P2_DIP_DONUS | 12 / 4.276 | 3 / -1.478 | 6 / 2.579 | 9 / 3.489 | 52.4 |
| P3_HACIM_BEKLE | 0 / None | 8 / -0.755 | 2 / -0.462 | 6 / -0.853 | 93.5 |
| P3_RADAR | 44 / -0.653 | 69 / -0.141 | 42 / 0.877 | 71 / -1.061 | 69.1 |
| P3_SKOR_AL | 222 / -0.862 | 53 / 1.03 | 61 / 0.293 | 81 / 0.314 | 33.1 |
| P4_HAZIRLIK | 0 / None | 143 / 0.288 | 51 / 0.811 | 92 / -0.002 | 57.2 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 114 / 0.277 | 36 / 0.03 | 80 / 0.378 | 44.4 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 0 / None | 0 / None | 0 / None | 100.0 |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 25 | -2.1 (-1.33) | -1.046 (-1.08) | -1.046 (-1.08) | AYNI |
| EKLEME_ADAYI | 3 / 2 | None (None) | None (None) | None (None) | - |
| IC_STOP | 57 / 57 | 2.017 (None) | 2.017 (None) | 2.017 (None) | AYNI |
| P2_ADAY | 72 / 63 | -0.116 (-0.16) | -0.258 (-0.31) | -0.008 (-0.01) | AYNI |
| P2_DIP_DONUS | 21 / 20 | 3.125 (1.51) | 3.835 (1.9) | 4.085 (2.03) | AYNI |
| P3_HACIM_BEKLE | 62 / 62 | -0.755 (None) | -0.755 (None) | -0.505 (None) | AYNI |
| P3_RADAR | 136 / 126 | -0.341 (-0.83) | -0.32 (-0.73) | -0.07 (-0.16) | AYNI |
| P3_SKOR_AL | 287 / 284 | -0.497 (-1.37) | -0.499 (-1.36) | -0.249 (-0.68) | AYNI |
| P4_HAZIRLIK | 208 / 197 | 0.288 (0.91) | 0.355 (1.05) | 0.605 (1.79) | AYNI |
| POZ_AZALT | 39 / 24 | -1.931 (-1.95) | -0.922 (-0.89) | -0.922 (-0.89) | AYNI |
| SEKTOR_ROTASYONU | 144 / 133 | 0.27 (0.54) | 0.431 (0.79) | 0.681 (1.25) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 12 / 12 | None (None) | None (None) | None (None) | - |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 53 | 20 | -1.137 (-1.68) | 39.1 | -0.082 (-0.07) |
| ANA (10:15-12:30) | 275 | 32 | -0.692 (-1.76) | 46.4 | -0.409 (-1.05) |
| KAPANIS (>=15:45) | 204 | 31 | -0.039 (-0.11) | 50.6 | -0.067 (-0.14) |
| OGLE (12:30-15:45) | 254 | 32 | 0.468 (0.96) | 50.2 | 0.513 (0.82) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 29 | 18 | None (None) | None | None (None) |
| OBV | 29 | 14 | None (None) | None | None (None) |
| SECTOR | 6 | 6 | None (None) | None | None (None) |
| TREND | 113 | 22 | -0.61 (None) | 50.0 | None (None) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-13, 91 islem gunu; gunluk alarm medyani 5, GUNLUK_OZET medyani 15.
- Ham kayit 3036, eventId tekrari 256, tekil 2780.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 44, son 30 gunde 8. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
