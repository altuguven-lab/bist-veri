# Alarm Karnesi

Uretim: 2026-11-23T16:41 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEKTOR_ROTASYONU | BILGI | YUKARI | 278 | 0.358 (1.23) | -0.164 | 0.108 (0.37 / 0.51) | -0.242 (-0.69) | 0.468 (0.74) | 2.062 | 46.5 | -0.026 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 85 | 0.279 (0.81) | 0.135 | 0.279 (0.81 / 0.9) | 0.536 (1.54) | 0.084 (0.2) | None | 59.5 | 0.329 | **ADAY** |
| P4_HAZIRLIK | BILGI | YUKARI | 311 | 0.22 (1.01) | -0.272 | -0.03 (-0.14 / -0.13) | -0.35 (-1.07) | -0.081 (-0.38) | 0.316 | 46.9 | 0.03 | **KENAR_YOK** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.26 (-0.75) | -0.34 | -0.51 (-1.47 / -2.09) | -0.54 (-1.36) | -0.269 (-0.41) | 0.811 | 42.2 | -0.376 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 150 | -0.103 (-0.31) | -0.479 | -0.353 (-1.07 / -1.2) | -0.371 (-0.95) | 0.043 (0.14) | 0.316 | 51.4 | -0.21 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 120 | -0.046 (-0.17) | -0.29 | -0.296 (-1.1 / -1.11) | -1.003 (-4.49) | -0.259 (-0.8) | None | 43.6 | 0.433 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 75 | 0.137 (0.21) | -0.419 | -0.113 (-0.17 / -0.19) | -0.177 (-0.23) | 0.191 (0.26) | 0.067 | 51.4 | -1.165 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -1.829 | 43.6 | 2.393 | **KENAR_YOK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -2.745 (-1.16) | -0.542 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.084 (1.35) | -0.308 | 1.834 (1.19 / 1.09) | 1.448 (0.96) | 1.287 (0.82) | 3.765 | 47.8 | 1.779 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 16 | -0.339 (-0.41) | -0.905 | -0.589 (-0.7 / -0.71) | -0.714 (-0.94) | -0.058 (-0.08) | None | 40.0 | 0.585 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 2.662 (0.96) | None | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 74 / 0.279 | 38 / 0.213 | 36 / 0.349 | 88.2 |
| P2_ADAY | 28 / -0.946 | 46 / 0.394 | 25 / -0.691 | 49 / 0.182 | 77.3 |
| P2_DIP_DONUS | 12 / 4.276 | 11 / -0.829 | 12 / 1.471 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 94 / -0.296 | 29 / -0.204 | 65 / -0.337 | 96.7 |
| P3_RADAR | 44 / -0.653 | 102 / -0.224 | 57 / 0.463 | 89 / -0.876 | 72.0 |
| P3_SKOR_AL | 222 / -0.862 | 67 / 0.656 | 75 / 0.097 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 260 / -0.03 | 111 / 0.22 | 149 / -0.216 | 68.5 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 215 / 0.11 | 62 / -0.143 | 155 / 0.208 | 54.7 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 15 / -0.589 | 11 / -0.169 | 4 / -1.742 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 32 | 7 | -0.594 | -1.81 | -0.412 | 0.443 | **DEVAM (7/10 gun)** |
| H14c_cikis_yonT3 | 83 | 8 | 0.466 | 1.08 | 0.502 | 0.559 | **DEVAM (8/10 gun)** |
| H14b_hacim_tetigi | 81 | 4 | -0.335 | 0.638 | - | - | **DEVAM (4/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 81 | 9 | 0.135 | 0.195 | -0.06 | 0.625 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 74 | 7 | 0.279 | 0.462 | -0.183 | 0.735 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 75 | 36 | -0.169 | 0.163 | -0.333 | 0.909 | OLCULEBILIR |
| P2_ADAY | T3 | 74 | 35 | 0.137 | 0.697 | -0.559 | 0.904 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 23 | 15 | -0.058 | 0.152 | -0.209 | 0.684 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 23 | 15 | 2.084 | 0.424 | 1.661 | 0.017 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 110 | 9 | -0.04 | -0.11 | 0.07 | 0.342 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 94 | 7 | -0.046 | -0.311 | 0.265 | 0.162 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 149 | 43 | -0.229 | 0.11 | -0.339 | 0.978 | OLCULEBILIR |
| P3_RADAR | T3 | 146 | 41 | -0.103 | 0.36 | -0.463 | 0.93 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.037 | -0.127 | 0.854 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 289 | 40 | -0.26 | 0.045 | -0.305 | 0.905 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 288 | 29 | -0.022 | 0.075 | -0.097 | 0.815 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 260 | 27 | 0.22 | 0.255 | -0.035 | 0.561 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.107 | -1.064 | 1.0 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.276 | -2.206 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 253 | 28 | 0.086 | 0.084 | 0.002 | 0.493 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 217 | 26 | 0.358 | 0.289 | 0.069 | 0.369 | OLCULEBILIR |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.136 | -0.519 | 0.879 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.388 | 0.049 | 0.477 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 81 | 9 | 0.135 | 0.198 | -0.063 | 0.634 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 74 | 7 | 0.279 | 0.46 | -0.181 | 0.749 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 11 | 6 | -0.178 | -0.293 | 0.115 | 0.411 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 10 | 5 | -0.117 | -0.481 | 0.364 | 0.32 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 8 | 4 | -0.035 | -0.011 | -0.024 | 0.522 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 8 | 4 | -0.336 | -0.163 | -0.173 | 0.582 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 110 | 9 | -0.04 | -0.11 | 0.07 | 0.34 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 94 | 7 | -0.046 | -0.312 | 0.266 | 0.151 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 45 | 10 | 0.072 | -0.07 | 0.141 | 0.298 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 42 | 8 | -0.186 | -0.335 | 0.149 | 0.376 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.026 | 0.021 | 0.486 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 18 | 5 | -0.301 | -0.386 | 0.085 | 0.442 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 156 | 10 | -0.151 | -0.067 | -0.084 | 0.738 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 128 | 8 | -0.188 | -0.223 | 0.035 | 0.44 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.251 | 0.45 | 0.289 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.734 | 1.502 | 0.112 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 150 | 9 | -0.023 | -0.019 | -0.004 | 0.517 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 114 | 7 | -0.092 | -0.047 | -0.045 | 0.574 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.133 | -0.522 | 0.88 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.406 | 0.067 | 0.457 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 24 | -1.93 (-1.31) | -0.823 (-0.89) | -0.823 (-0.89) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 85 / 85 | 0.279 (0.81) | 0.279 (0.81) | 0.279 (0.81) | AYNI |
| P2_ADAY | 75 / 66 | -0.113 (-0.17) | -0.235 (-0.32) | 0.015 (0.02) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.834 (1.19) | 2.227 (1.44) | 2.477 (1.6) | AYNI |
| P3_HACIM_BEKLE | 120 / 120 | -0.296 (-1.1) | -0.296 (-1.1) | -0.046 (-0.17) | AYNI |
| P3_RADAR | 150 / 140 | -0.353 (-1.07) | -0.339 (-0.97) | -0.089 (-0.25) | AYNI |
| P3_SKOR_AL | 289 / 283 | -0.51 (-1.47) | -0.532 (-1.51) | -0.282 (-0.8) | AYNI |
| P4_HAZIRLIK | 311 / 300 | -0.03 (-0.14) | -0.009 (-0.04) | 0.241 (1.06) | AYNI |
| POZ_AZALT | 39 / 22 | -1.931 (-1.95) | -0.663 (-0.62) | -0.663 (-0.62) | AYNI |
| SEKTOR_ROTASYONU | 278 / 267 | 0.108 (0.37) | 0.181 (0.6) | 0.431 (1.43) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 16 / 16 | -0.589 (-0.7) | -0.589 (-0.7) | -0.339 (-0.41) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 62 | 22 | -0.965 (-1.66) | 41.8 | 0.141 (0.14) |
| ANA (10:15-12:30) | 360 | 32 | -0.482 (-1.83) | 45.3 | -0.378 (-1.51) |
| KAPANIS (>=15:45) | 241 | 32 | -0.243 (-0.74) | 47.0 | -0.225 (-0.5) |
| OGLE (12:30-15:45) | 305 | 32 | 0.218 (0.59) | 47.4 | 0.3 (0.63) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 130 | 31 | -0.521 (-1.91) | 33.3 | -0.725 (-0.88) |
| OBV | 43 | 20 | -0.674 (-1.55) | 41.7 | -0.229 (-1.17) |
| RS | 9 | 8 | None (None) | None | None (None) |
| SECTOR | 9 | 9 | -0.58 (-0.75) | 55.6 | -2.38 (None) |
| TREND | 168 | 26 | -0.252 (-1.0) | 44.2 | -0.111 (-0.98) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-23, 97 islem gunu; gunluk alarm medyani 8, GUNLUK_OZET medyani 15.
- Ham kayit 3840, eventId tekrari 256, tekil 3584.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 46, son 30 gunde 2. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
