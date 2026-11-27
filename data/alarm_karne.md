# Alarm Karnesi

Uretim: 2026-11-27T16:41 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IC_STOP | KRITIK | ASAGI | 98 | 0.127 (0.41) | 0.085 | 0.127 (0.41 / 0.46) | 0.401 (1.32) | 0.112 (0.35) | 0.671 | 54.0 | 0.428 | **ADAY** |
| P4_HAZIRLIK | BILGI | YUKARI | 389 | 0.081 (0.44) | -0.342 | -0.169 (-0.92 / -0.86) | -0.596 (-2.18) | -0.146 (-0.96) | 0.044 | 46.8 | -0.021 | **KENAR_YOK** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 347 | 0.219 (1.01) | -0.158 | -0.031 (-0.15 / -0.18) | -0.403 (-1.45) | 0.313 (0.74) | 1.522 | 46.4 | -0.011 | **KENAR_YOK** |
| P3_SKOR_AL | BILGI | YUKARI | 296 | -0.26 (-0.75) | -0.34 | -0.51 (-1.47 / -2.09) | -0.54 (-1.36) | -0.269 (-0.41) | 0.788 | 42.2 | -0.376 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 161 | -0.114 (-0.35) | -0.492 | -0.364 (-1.12 / -1.26) | -0.393 (-1.03) | 0.044 (0.15) | 0.292 | 52.0 | -0.194 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 83 | 0.111 (0.17) | -0.419 | -0.139 (-0.21 / -0.23) | -0.222 (-0.29) | 0.078 (0.11) | 0.319 | 50.7 | -1.158 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -1.458 | 43.6 | 2.393 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 172 | -0.304 (-1.31) | -0.42 | -0.554 (-2.38 / -2.32) | -1.344 (-5.79) | -0.442 (-27.2) | -0.461 | 41.0 | 0.119 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 34 | -1.93 (-1.31) | -0.431 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -2.745 (-1.16) | -0.168 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.084 (1.35) | -0.308 | 1.834 (1.19 / 1.09) | 1.448 (0.96) | 1.507 (1.06) | 2.44 | 47.8 | 1.779 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 19 | -0.113 (-0.15) | -1.036 | -0.363 (-0.47 / -0.48) | -0.648 (-1.0) | -0.058 (-0.08) | 0.388 | 47.1 | 0.825 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 2.662 (0.96) | 5.107 | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 29.4 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 87 / 0.127 | 47 / 0.09 | 40 / 0.171 | 88.8 |
| P2_ADAY | 28 / -0.946 | 47 / 0.342 | 26 / -0.743 | 49 / 0.182 | 78.3 |
| P2_DIP_DONUS | 12 / 4.276 | 11 / -0.829 | 12 / 1.471 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 134 / -0.554 | 43 / -0.899 | 91 / -0.391 | 97.1 |
| P3_RADAR | 44 / -0.653 | 106 / -0.244 | 60 / 0.37 | 90 / -0.853 | 72.7 |
| P3_SKOR_AL | 222 / -0.862 | 67 / 0.656 | 75 / 0.097 | 81 / 0.314 | 35.1 |
| P4_HAZIRLIK | 0 / None | 331 / -0.169 | 159 / -0.016 | 172 / -0.31 | 73.0 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 304 / -0.031 | 96 / -0.462 | 210 / 0.165 | 56.5 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 17 / -0.363 | 13 / 0.061 | 4 / -1.742 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir. Bu hafta (2026-W48) resmi bakis kaydedildi.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 33 | 8 | -0.638 | -2.02 | -0.398 | 0.489 | **DEVAM (8/10 gun)** |
| H14c_cikis_yonT3 | 96 | 12 | 0.303 | 0.79 | 0.477 | 0.748 | **DEVAM** |
| H14b_hacim_tetigi | 81 | 4 | -0.335 | 0.638 | - | - | **DEVAM (4/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 30 | 24 | -0.431 | -0.172 | -0.259 | 0.743 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.377 | -1.553 | 0.981 | OLCULEBILIR |
| IC_STOP | T1 | 91 | 13 | 0.085 | 0.206 | -0.121 | 0.745 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 87 | 11 | 0.127 | 0.45 | -0.323 | 0.878 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 75 | 36 | -0.169 | 0.163 | -0.333 | 0.909 | OLCULEBILIR |
| P2_ADAY | T3 | 75 | 36 | 0.111 | 0.707 | -0.596 | 0.918 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 23 | 15 | -0.058 | 0.134 | -0.192 | 0.675 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 23 | 15 | 2.084 | 0.433 | 1.651 | 0.019 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 154 | 13 | -0.17 | -0.135 | -0.035 | 0.594 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 134 | 11 | -0.304 | -0.31 | 0.006 | 0.485 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 156 | 46 | -0.242 | 0.097 | -0.34 | 0.976 | OLCULEBILIR |
| P3_RADAR | T3 | 150 | 44 | -0.114 | 0.355 | -0.468 | 0.946 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.032 | -0.122 | 0.846 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 289 | 40 | -0.26 | 0.039 | -0.298 | 0.902 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 363 | 33 | -0.092 | 0.012 | -0.105 | 0.854 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 331 | 31 | 0.081 | 0.126 | -0.044 | 0.608 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.1 | -1.057 | 0.998 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.262 | -2.192 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 343 | 32 | 0.092 | 0.011 | 0.081 | 0.217 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 306 | 30 | 0.219 | 0.107 | 0.112 | 0.267 | OLCULEBILIR |
| TASIMA | T1 | 17 | 6 | -0.786 | -0.177 | -0.61 | 0.921 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 17 | 6 | -0.113 | -0.412 | 0.299 | 0.315 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 6 | 4 | -0.122 | -0.071 | -0.051 | 0.54 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.285 | 1.178 | 0.236 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 91 | 13 | 0.085 | 0.207 | -0.122 | 0.749 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 87 | 11 | 0.127 | 0.442 | -0.315 | 0.883 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 11 | 6 | -0.178 | -0.291 | 0.113 | 0.4 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 11 | 6 | -0.269 | -0.493 | 0.223 | 0.382 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 8 | 4 | -0.035 | 0.019 | -0.053 | 0.545 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 8 | 4 | -0.336 | -0.169 | -0.167 | 0.581 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 154 | 13 | -0.17 | -0.132 | -0.038 | 0.592 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 134 | 11 | -0.304 | -0.313 | 0.009 | 0.488 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 52 | 13 | -0.01 | -0.064 | 0.054 | 0.412 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 46 | 11 | -0.214 | -0.341 | 0.128 | 0.368 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.014 | 0.033 | 0.462 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 18 | 5 | -0.301 | -0.4 | 0.099 | 0.431 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 231 | 14 | -0.22 | -0.119 | -0.102 | 0.801 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 199 | 12 | -0.273 | -0.261 | -0.012 | 0.521 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.25 | 0.451 | 0.287 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.765 | 1.471 | 0.114 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 240 | 13 | 0.026 | -0.085 | 0.111 | 0.158 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 203 | 11 | -0.105 | -0.188 | 0.083 | 0.328 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 17 | 6 | -0.786 | -0.173 | -0.614 | 0.936 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 17 | 6 | -0.113 | -0.41 | 0.297 | 0.322 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 34 / 28 | -1.93 (-1.31) | -0.43 (-0.49) | -0.43 (-0.49) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 98 / 98 | 0.127 (0.41) | 0.127 (0.41) | 0.127 (0.41) | AYNI |
| P2_ADAY | 83 / 72 | -0.139 (-0.21) | -0.197 (-0.27) | 0.053 (0.07) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.834 (1.19) | 2.227 (1.44) | 2.477 (1.6) | AYNI |
| P3_HACIM_BEKLE | 172 / 172 | -0.554 (-2.38) | -0.554 (-2.38) | -0.304 (-1.31) | AYNI |
| P3_RADAR | 161 / 151 | -0.364 (-1.12) | -0.35 (-1.03) | -0.1 (-0.29) | AYNI |
| P3_SKOR_AL | 296 / 289 | -0.51 (-1.47) | -0.522 (-1.48) | -0.272 (-0.77) | AYNI |
| P4_HAZIRLIK | 389 / 378 | -0.169 (-0.92) | -0.157 (-0.82) | 0.093 (0.49) | AYNI |
| POZ_AZALT | 39 / 19 | -1.931 (-1.95) | -0.728 (-0.58) | -0.728 (-0.58) | AYNI |
| SEKTOR_ROTASYONU | 347 / 336 | -0.031 (-0.15) | 0.015 (0.07) | 0.265 (1.19) | **DEGISTI** |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 19 / 19 | -0.363 (-0.47) | -0.363 (-0.47) | -0.113 (-0.15) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 71 | 22 | -0.74 (-1.59) | 40.8 | 0.006 (0.01) |
| ANA (10:15-12:30) | 418 | 32 | -0.601 (-2.34) | 44.5 | -0.276 (-1.24) |
| KAPANIS (>=15:45) | 260 | 32 | -0.28 (-0.91) | 47.3 | -0.267 (-0.66) |
| OGLE (12:30-15:45) | 375 | 32 | 0.145 (0.42) | 47.3 | 0.113 (0.25) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 242 | 32 | -0.988 (-4.01) | 34.0 | -0.663 (-1.96) |
| OBV | 65 | 28 | -0.429 (-1.03) | 47.9 | -0.439 (-2.72) |
| RS | 23 | 17 | 0.876 (0.55) | 63.6 | -2.734 (None) |
| SECTOR | 10 | 9 | -0.58 (-0.76) | 55.6 | -1.447 (-1.16) |
| TREND | 175 | 27 | -0.211 (-0.89) | 45.6 | -0.03 (-0.14) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-27, 101 islem gunu; gunluk alarm medyani 10, GUNLUK_OZET medyani 15.
- Ham kayit 4393, eventId tekrari 256, tekil 4137.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 48, son 30 gunde 2. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
