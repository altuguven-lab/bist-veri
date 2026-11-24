# Alarm Karnesi

Uretim: 2026-11-24T16:41 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEKTOR_ROTASYONU | BILGI | YUKARI | 306 | 0.339 (1.26) | -0.188 | 0.089 (0.33 / 0.45) | -0.292 (-0.91) | 0.396 (0.71) | 1.799 | 47.0 | -0.002 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 87 | 0.158 (0.46) | 0.157 | 0.158 (0.46 / 0.53) | 0.432 (1.28) | 0.081 (0.2) | 4.019 | 55.7 | 0.42 | **ADAY** |
| P4_HAZIRLIK | BILGI | YUKARI | 331 | 0.22 (1.07) | -0.3 | -0.03 (-0.15 / -0.13) | -0.373 (-1.21) | -0.079 (-0.41) | 0.282 | 48.0 | 0.024 | **KENAR_YOK** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.26 (-0.75) | -0.34 | -0.51 (-1.47 / -2.09) | -0.54 (-1.36) | -0.269 (-0.41) | 0.811 | 42.2 | -0.376 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 150 | -0.088 (-0.27) | -0.478 | -0.338 (-1.03 / -1.16) | -0.365 (-0.95) | 0.012 (0.04) | 0.402 | 52.0 | -0.212 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 134 | -0.045 (-0.19) | -0.333 | -0.295 (-1.22 / -1.16) | -1.029 (-5.05) | -0.298 (-1.28) | -1.987 | 44.7 | 0.379 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 75 | 0.137 (0.21) | -0.419 | -0.113 (-0.17 / -0.19) | -0.177 (-0.23) | 0.174 (0.24) | 0.007 | 51.4 | -1.165 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -1.458 | 43.6 | 2.393 | **KENAR_YOK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -2.745 (-1.16) | -0.419 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.084 (1.35) | -0.308 | 1.834 (1.19 / 1.09) | 1.448 (0.96) | 1.287 (0.82) | 3.765 | 47.8 | 1.779 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 17 | -0.339 (-0.41) | -0.87 | -0.589 (-0.7 / -0.71) | -0.714 (-0.94) | -0.058 (-0.08) | None | 40.0 | 0.585 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 2.662 (0.96) | None | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 79 / 0.158 | 41 / 0.055 | 38 / 0.268 | 88.5 |
| P2_ADAY | 28 / -0.946 | 46 / 0.394 | 25 / -0.691 | 49 / 0.182 | 77.3 |
| P2_DIP_DONUS | 12 / 4.276 | 11 / -0.829 | 12 / 1.471 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 103 / -0.295 | 32 / -0.232 | 71 / -0.324 | 97.0 |
| P3_RADAR | 44 / -0.653 | 104 / -0.204 | 58 / 0.462 | 90 / -0.853 | 72.0 |
| P3_SKOR_AL | 222 / -0.862 | 67 / 0.656 | 75 / 0.097 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 275 / -0.03 | 121 / 0.168 | 154 / -0.185 | 70.4 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 234 / 0.091 | 69 / -0.127 | 167 / 0.178 | 55.9 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 15 / -0.589 | 11 / -0.169 | 4 / -1.742 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 32 | 7 | -0.594 | -1.81 | -0.412 | 0.443 | **DEVAM (7/10 gun)** |
| H14c_cikis_yonT3 | 88 | 9 | 0.346 | 0.82 | 0.477 | 0.681 | **DEVAM (9/10 gun)** |
| H14b_hacim_tetigi | 81 | 4 | -0.335 | 0.638 | - | - | **DEVAM (4/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 85 | 10 | 0.157 | 0.206 | -0.049 | 0.609 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 79 | 8 | 0.158 | 0.444 | -0.287 | 0.841 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 75 | 36 | -0.169 | 0.159 | -0.329 | 0.907 | OLCULEBILIR |
| P2_ADAY | T3 | 74 | 35 | 0.137 | 0.731 | -0.594 | 0.912 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 23 | 15 | -0.058 | 0.149 | -0.207 | 0.686 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 23 | 15 | 2.084 | 0.464 | 1.62 | 0.028 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 120 | 10 | -0.083 | -0.132 | 0.049 | 0.376 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 103 | 8 | -0.045 | -0.296 | 0.251 | 0.146 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 150 | 44 | -0.228 | 0.109 | -0.337 | 0.979 | OLCULEBILIR |
| P3_RADAR | T3 | 148 | 42 | -0.088 | 0.35 | -0.438 | 0.929 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.029 | -0.119 | 0.836 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 289 | 40 | -0.26 | 0.047 | -0.307 | 0.912 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 311 | 30 | -0.05 | 0.033 | -0.083 | 0.785 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 275 | 28 | 0.22 | 0.24 | -0.02 | 0.546 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.098 | -1.054 | 0.999 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.244 | -2.175 | 0.999 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 278 | 29 | 0.062 | 0.039 | 0.023 | 0.424 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 236 | 27 | 0.339 | 0.256 | 0.083 | 0.342 | OLCULEBILIR |
| TASIMA | T1 | 16 | 5 | -0.62 | -0.168 | -0.452 | 0.863 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.418 | 0.08 | 0.455 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 85 | 10 | 0.157 | 0.211 | -0.054 | 0.616 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 79 | 8 | 0.158 | 0.438 | -0.281 | 0.843 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 11 | 6 | -0.178 | -0.301 | 0.123 | 0.404 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 10 | 5 | -0.117 | -0.498 | 0.381 | 0.32 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 8 | 4 | -0.035 | -0.027 | -0.007 | 0.498 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 8 | 4 | -0.336 | -0.177 | -0.158 | 0.571 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 120 | 10 | -0.083 | -0.137 | 0.054 | 0.367 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 103 | 8 | -0.045 | -0.284 | 0.239 | 0.16 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 46 | 11 | 0.068 | -0.08 | 0.148 | 0.289 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 44 | 9 | -0.131 | -0.343 | 0.212 | 0.313 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.047 | 0.0 | 0.48 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 18 | 5 | -0.301 | -0.403 | 0.102 | 0.441 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 179 | 11 | -0.183 | -0.123 | -0.06 | 0.691 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 143 | 9 | -0.145 | -0.209 | 0.064 | 0.383 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.272 | 0.43 | 0.308 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.755 | 1.48 | 0.12 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 175 | 10 | -0.045 | -0.081 | 0.036 | 0.376 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 133 | 8 | -0.062 | -0.069 | 0.007 | 0.486 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 16 | 5 | -0.62 | -0.159 | -0.461 | 0.873 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.406 | 0.067 | 0.458 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 23 | -1.93 (-1.31) | -0.43 (-0.49) | -0.43 (-0.49) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 87 / 87 | 0.158 (0.46) | 0.158 (0.46) | 0.158 (0.46) | AYNI |
| P2_ADAY | 75 / 64 | -0.113 (-0.17) | -0.168 (-0.22) | 0.082 (0.11) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.834 (1.19) | 2.227 (1.44) | 2.477 (1.6) | AYNI |
| P3_HACIM_BEKLE | 134 / 134 | -0.295 (-1.22) | -0.295 (-1.22) | -0.045 (-0.19) | AYNI |
| P3_RADAR | 150 / 140 | -0.338 (-1.03) | -0.322 (-0.94) | -0.072 (-0.21) | AYNI |
| P3_SKOR_AL | 289 / 282 | -0.51 (-1.47) | -0.522 (-1.48) | -0.272 (-0.77) | AYNI |
| P4_HAZIRLIK | 331 / 320 | -0.03 (-0.15) | -0.01 (-0.05) | 0.24 (1.12) | AYNI |
| POZ_AZALT | 39 / 19 | -1.931 (-1.95) | -0.728 (-0.58) | -0.728 (-0.58) | AYNI |
| SEKTOR_ROTASYONU | 306 / 295 | 0.089 (0.33) | 0.155 (0.56) | 0.405 (1.46) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 17 / 17 | -0.589 (-0.7) | -0.589 (-0.7) | -0.339 (-0.41) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 71 | 22 | -0.961 (-1.71) | 40.4 | 0.039 (0.04) |
| ANA (10:15-12:30) | 373 | 32 | -0.451 (-1.78) | 46.2 | -0.348 (-1.47) |
| KAPANIS (>=15:45) | 245 | 32 | -0.234 (-0.72) | 47.7 | -0.261 (-0.6) |
| OGLE (12:30-15:45) | 313 | 32 | 0.195 (0.54) | 47.8 | 0.287 (0.63) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 156 | 31 | -0.528 (-2.45) | 37.2 | -0.748 (-1.41) |
| OBV | 48 | 23 | -0.601 (-1.43) | 44.7 | -0.283 (-3.37) |
| RS | 11 | 8 | 1.205 (7.68) | 100.0 | None (None) |
| SECTOR | 9 | 9 | -0.58 (-0.76) | 55.6 | -2.38 (None) |
| TREND | 169 | 26 | -0.204 (-0.81) | 45.6 | -0.061 (-0.33) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-24, 98 islem gunu; gunluk alarm medyani 9.0, GUNLUK_OZET medyani 15.0.
- Ham kayit 3992, eventId tekrari 256, tekil 3736.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 48, son 30 gunde 2. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
