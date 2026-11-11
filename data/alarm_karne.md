# Alarm Karnesi

Uretim: 2026-11-11T23:03 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 143 | 0.672 (1.89) | -0.106 | 0.422 (1.19 / 0.98) | 0.341 (0.69) | 0.228 (0.77) | 0.979 | 54.0 | -0.209 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 116 | 1.0 (2.3) | -0.005 | 0.75 (1.72 / 2.09) | 0.633 (1.1) | 1.224 (1.53) | 1.409 | 55.1 | 0.138 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 275 | -0.271 (-0.73) | -0.327 | -0.521 (-1.4 / -2.0) | -0.544 (-1.28) | -0.277 (-0.37) | 0.661 | 42.0 | -0.474 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 113 | 0.012 (0.03) | -0.566 | -0.238 (-0.52 / -0.59) | -0.288 (-0.52) | 0.086 (0.2) | 0.403 | 54.5 | -0.548 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 65 | 0.202 (0.26) | -0.418 | -0.048 (-0.06 / -0.07) | -0.058 (-0.06) | 0.185 (0.17) | -0.708 | 55.0 | -1.62 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -2.842 (-3.12) | -1.376 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 27 | -2.637 (-1.51) | -0.443 | -2.637 (-1.51 / -1.44) | -1.545 (-0.85) | -3.325 (-1.2) | -0.515 | 50.0 | 1.963 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 15 | 3.375 (1.63) | -0.32 | 3.125 (1.51 / 1.25) | 3.088 (1.59) | 2.049 (1.09) | 4.469 | 60.0 | 2.645 | **YETERSIZ_ORNEK** |
| IC_STOP | KRITIK | ASAGI | 8 | None (None) | None | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 8 | None (None) | None | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 1 | None (None) | None | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 8 / -1.176 | 13 / -5.025 | 9 / -0.743 | 14.8 |
| EKLEME_ADAYI | 0 / None | 0 / None | 0 / None | 0 / None | 0.0 |
| IC_STOP | 0 / None | 0 / None | 0 / None | 0 / None | 50.0 |
| P2_ADAY | 28 / -0.946 | 32 / 0.739 | 15 / -0.632 | 45 / 0.147 | 75.4 |
| P2_DIP_DONUS | 12 / 4.276 | 3 / -1.478 | 6 / 2.579 | 9 / 3.489 | 33.3 |
| P3_HACIM_BEKLE | 0 / None | 0 / None | 0 / None | 0 / None | 75.0 |
| P3_RADAR | 44 / -0.653 | 55 / 0.095 | 35 / 1.044 | 64 / -0.938 | 62.8 |
| P3_SKOR_AL | 222 / -0.862 | 47 / 1.085 | 59 / 0.265 | 77 / 0.312 | 30.2 |
| P4_HAZIRLIK | 0 / None | 124 / 0.422 | 46 / 0.983 | 78 / 0.092 | 41.3 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 96 / 0.769 | 32 / 0.368 | 66 / 0.935 | 33.6 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 27 / 23 | -2.637 (-1.51) | -1.532 (-1.47) | -1.532 (-1.47) | AYNI |
| EKLEME_ADAYI | 1 / 0 | None (None) | None (None) | None (None) | - |
| IC_STOP | 8 / 8 | None (None) | None (None) | None (None) | - |
| P2_ADAY | 65 / 56 | -0.048 (-0.06) | -0.211 (-0.25) | 0.039 (0.05) | AYNI |
| P2_DIP_DONUS | 15 / 14 | 3.125 (1.51) | 3.835 (1.9) | 4.085 (2.03) | AYNI |
| P3_HACIM_BEKLE | 8 / 8 | None (None) | None (None) | None (None) | - |
| P3_RADAR | 113 / 103 | -0.238 (-0.52) | -0.295 (-0.62) | -0.045 (-0.09) | AYNI |
| P3_SKOR_AL | 275 / 272 | -0.521 (-1.4) | -0.509 (-1.36) | -0.259 (-0.69) | AYNI |
| P4_HAZIRLIK | 143 / 132 | 0.422 (1.19) | 0.445 (1.22) | 0.695 (1.91) | AYNI |
| POZ_AZALT | 39 / 24 | -2.842 (-3.12) | -2.223 (-2.63) | -2.223 (-2.63) | AYNI |
| SEKTOR_ROTASYONU | 116 / 105 | 0.75 (1.72) | 0.83 (1.81) | 1.08 (2.35) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 46 | 20 | -1.137 (-1.68) | 39.1 | -0.042 (-0.04) |
| ANA (10:15-12:30) | 196 | 31 | -0.676 (-1.61) | 46.4 | -0.619 (-1.67) |
| KAPANIS (>=15:45) | 176 | 30 | -0.009 (-0.02) | 50.9 | 0.043 (0.08) |
| OGLE (12:30-15:45) | 201 | 31 | 0.63 (1.15) | 51.4 | 0.613 (0.77) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 1 | 1 | None (None) | None | None (None) |
| OBV | 1 | 1 | None (None) | None | None (None) |
| TREND | 8 | 6 | None (None) | None | None (None) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-11, 89 islem gunu; gunluk alarm medyani 5, GUNLUK_OZET medyani 15.
- Ham kayit 2713, eventId tekrari 256, tekil 2457.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 44, son 30 gunde 10. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
