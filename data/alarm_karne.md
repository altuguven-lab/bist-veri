# Alarm Karnesi

Uretim: 2026-11-13T22:11 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 190 | 0.59 (1.81) | -0.195 | 0.34 (1.04 / 0.86) | 0.411 (0.92) | 0.183 (0.71) | 0.857 | 52.6 | -0.052 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 132 | 0.856 (1.95) | -0.135 | 0.606 (1.38 / 1.72) | 0.624 (1.14) | 1.219 (1.63) | 1.321 | 53.4 | 0.078 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 281 | -0.247 (-0.68) | -0.325 | -0.497 (-1.37 / -1.95) | -0.506 (-1.21) | -0.23 (-0.32) | 0.647 | 42.5 | -0.434 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 129 | -0.109 (-0.26) | -0.583 | -0.359 (-0.85 / -0.96) | -0.259 (-0.51) | 0.187 (0.41) | 0.331 | 52.3 | -0.564 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 70 | 0.177 (0.24) | -0.378 | -0.073 (-0.1 / -0.11) | -0.057 (-0.07) | 0.182 (0.19) | -0.622 | 53.1 | -1.357 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -2.585 (-2.89) | -0.957 | -2.585 (-2.89 / -3.36) | -2.485 (-2.57) | -2.888 (-1.51) | -2.114 | 35.3 | 3.018 | **TERS** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 45 | None (None) | -0.608 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| IC_STOP | KRITIK | ASAGI | 39 | None (None) | 0.617 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -2.288 (-1.4) | -0.419 | -2.288 (-1.4 / -1.33) | -1.381 (-0.82) | -3.675 (-1.41) | -0.46 | 50.0 | 1.69 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 20 | 3.375 (1.63) | -0.326 | 3.125 (1.51 / 1.25) | 3.088 (1.59) | 2.049 (1.09) | 3.765 | 60.0 | 2.645 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 8 | None (None) | 1.342 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | None (None) | 0.901 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 10 / -0.562 | 14 / -4.3 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 1 / None | 0 / None | 1 / None | 66.7 |
| IC_STOP | 0 / None | 0 / None | 0 / None | 0 / None | 82.1 |
| P2_ADAY | 28 / -0.946 | 36 / 0.606 | 16 / -0.605 | 48 / 0.104 | 75.7 |
| P2_DIP_DONUS | 12 / 4.276 | 3 / -1.478 | 6 / 2.579 | 9 / 3.489 | 50.0 |
| P3_HACIM_BEKLE | 0 / None | 0 / None | 0 / None | 0 / None | 93.3 |
| P3_RADAR | 44 / -0.653 | 65 / -0.161 | 39 / 0.834 | 70 / -1.025 | 67.4 |
| P3_SKOR_AL | 222 / -0.862 | 53 / 1.03 | 61 / 0.293 | 81 / 0.314 | 31.7 |
| P4_HAZIRLIK | 0 / None | 137 / 0.34 | 50 / 0.889 | 87 / 0.025 | 53.2 |
| POZ_AZALT | 32 / -2.842 | 2 / 1.525 | 7 / -3.343 | 20 / -1.104 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 101 / 0.621 | 35 / 0.029 | 68 / 0.903 | 41.7 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 0 / None | 0 / None | 0 / None | 100.0 |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 25 | -2.288 (-1.4) | -1.221 (-1.23) | -1.221 (-1.23) | AYNI |
| EKLEME_ADAYI | 3 / 2 | None (None) | None (None) | None (None) | - |
| IC_STOP | 39 / 39 | None (None) | None (None) | None (None) | - |
| P2_ADAY | 70 / 61 | -0.073 (-0.1) | -0.211 (-0.25) | 0.039 (0.05) | AYNI |
| P2_DIP_DONUS | 20 / 19 | 3.125 (1.51) | 3.835 (1.9) | 4.085 (2.03) | AYNI |
| P3_HACIM_BEKLE | 45 / 45 | None (None) | None (None) | None (None) | - |
| P3_RADAR | 129 / 119 | -0.359 (-0.85) | -0.34 (-0.74) | -0.09 (-0.2) | AYNI |
| P3_SKOR_AL | 281 / 278 | -0.497 (-1.37) | -0.499 (-1.36) | -0.249 (-0.68) | AYNI |
| P4_HAZIRLIK | 190 / 179 | 0.34 (1.04) | 0.415 (1.18) | 0.665 (1.9) | AYNI |
| POZ_AZALT | 39 / 24 | -2.585 (-2.89) | -1.828 (-2.16) | -1.828 (-2.16) | AYNI |
| SEKTOR_ROTASYONU | 132 / 121 | 0.606 (1.38) | 0.83 (1.81) | 1.08 (2.35) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 8 / 8 | None (None) | None (None) | None (None) | - |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 53 | 20 | -1.137 (-1.68) | 39.1 | -0.082 (-0.07) |
| ANA (10:15-12:30) | 252 | 32 | -0.692 (-1.76) | 46.4 | -0.391 (-0.95) |
| KAPANIS (>=15:45) | 194 | 31 | -0.001 (-0.0) | 50.6 | -0.082 (-0.17) |
| OGLE (12:30-15:45) | 236 | 32 | 0.526 (1.04) | 50.0 | 0.626 (0.85) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 22 | 14 | None (None) | None | None (None) |
| OBV | 20 | 12 | None (None) | None | None (None) |
| SECTOR | 5 | 5 | None (None) | None | None (None) |
| TREND | 79 | 21 | None (None) | None | None (None) |

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
