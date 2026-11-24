# Alarm Karnesi

Uretim: 2026-11-24T03:03 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEKTOR_ROTASYONU | BILGI | YUKARI | 253 | 0.274 (0.86) | -0.161 | 0.024 (0.08 / 0.1) | -0.093 (-0.25) | 0.451 (0.61) | 2.062 | 44.7 | -0.025 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 81 | 0.259 (0.73) | 0.116 | 0.259 (0.73 / 0.83) | 0.509 (1.43) | 0.339 (None) | None | 58.9 | 0.332 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.26 (-0.75) | -0.34 | -0.51 (-1.47 / -2.09) | -0.54 (-1.36) | -0.256 (-0.38) | 0.826 | 42.2 | -0.376 | **KENAR_YOK** |
| P4_HAZIRLIK | BILGI | YUKARI | 288 | 0.203 (0.89) | -0.266 | -0.047 (-0.21 / -0.19) | -0.274 (-0.8) | -0.121 (-0.56) | 0.285 | 46.3 | 0.064 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 149 | -0.117 (-0.35) | -0.479 | -0.367 (-1.09 / -1.23) | -0.36 (-0.91) | 0.013 (0.04) | 0.364 | 51.4 | -0.218 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 110 | -0.216 (-0.97) | -0.281 | -0.466 (-2.1 / -1.68) | -1.037 (-4.14) | -0.456 (None) | None | 41.7 | 0.461 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 75 | 0.137 (0.21) | -0.431 | -0.113 (-0.17 / -0.19) | -0.177 (-0.23) | 0.191 (0.26) | 0.067 | 51.4 | -1.165 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -2.114 | 43.6 | 2.393 | **KENAR_YOK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -2.745 (-1.16) | -0.958 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.102 (1.24) | -0.308 | 1.852 (1.09 / 1.0) | 1.69 (1.04) | 1.287 (0.82) | 3.765 | 42.9 | 1.993 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 15 | -0.339 (-0.41) | -0.905 | -0.589 (-0.7 / -0.71) | -0.714 (-0.94) | -0.497 (None) | None | 40.0 | 0.585 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 2.662 (0.96) | None | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 73 / 0.259 | 38 / 0.213 | 35 / 0.309 | 87.7 |
| P2_ADAY | 28 / -0.946 | 46 / 0.394 | 25 / -0.691 | 49 / 0.182 | 77.3 |
| P2_DIP_DONUS | 12 / 4.276 | 9 / -1.379 | 10 / 1.436 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 84 / -0.466 | 26 / -0.318 | 58 / -0.532 | 96.4 |
| P3_RADAR | 44 / -0.653 | 100 / -0.242 | 55 / 0.456 | 89 / -0.876 | 71.8 |
| P3_SKOR_AL | 222 / -0.862 | 67 / 0.656 | 75 / 0.097 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 246 / -0.047 | 103 / 0.232 | 143 / -0.248 | 67.0 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 188 / 0.026 | 56 / -0.251 | 134 / 0.139 | 53.0 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 15 / -0.589 | 11 / -0.169 | 4 / -1.742 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 30 | 6 | -0.743 | -2.38 | -0.497 | 0.498 | **DEVAM (6/10 gun)** |
| H14c_cikis_yonT3 | 82 | 7 | 0.45 | 1.02 | 0.514 | 0.589 | **DEVAM (7/10 gun)** |
| H14b_hacim_tetigi | 81 | 4 | -0.335 | 0.638 | - | - | **DEVAM (4/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 79 | 8 | 0.116 | 0.209 | -0.093 | 0.697 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 73 | 6 | 0.259 | 0.492 | -0.234 | 0.777 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 74 | 35 | -0.181 | 0.162 | -0.343 | 0.919 | OLCULEBILIR |
| P2_ADAY | T3 | 74 | 35 | 0.137 | 0.703 | -0.566 | 0.898 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 23 | 15 | -0.058 | 0.14 | -0.197 | 0.685 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 21 | 14 | 2.102 | 0.44 | 1.662 | 0.028 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 103 | 8 | -0.031 | -0.132 | 0.101 | 0.282 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 84 | 6 | -0.216 | -0.452 | 0.236 | 0.193 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 148 | 42 | -0.229 | 0.108 | -0.336 | 0.979 | OLCULEBILIR |
| P3_RADAR | T3 | 144 | 40 | -0.117 | 0.364 | -0.482 | 0.947 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.025 | -0.115 | 0.822 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 289 | 40 | -0.26 | 0.046 | -0.306 | 0.914 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 275 | 28 | -0.016 | 0.066 | -0.082 | 0.75 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 246 | 26 | 0.203 | 0.217 | -0.014 | 0.525 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.099 | -1.056 | 1.0 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.229 | -2.16 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 236 | 27 | 0.089 | 0.074 | 0.015 | 0.456 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 190 | 25 | 0.274 | 0.202 | 0.072 | 0.389 | OLCULEBILIR |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.141 | -0.514 | 0.875 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.393 | 0.054 | 0.466 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 79 | 8 | 0.116 | 0.209 | -0.093 | 0.685 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 73 | 6 | 0.259 | 0.482 | -0.223 | 0.78 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 10 | 5 | -0.262 | -0.346 | 0.083 | 0.446 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 10 | 5 | -0.117 | -0.489 | 0.372 | 0.316 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 8 | 4 | -0.035 | -0.005 | -0.029 | 0.518 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 6 | 3 | -1.08 | -0.484 | -0.596 | 0.715 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 103 | 8 | -0.031 | -0.141 | 0.11 | 0.256 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 84 | 6 | -0.216 | -0.453 | 0.237 | 0.199 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 44 | 9 | 0.079 | -0.074 | 0.154 | 0.269 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 40 | 7 | -0.242 | -0.388 | 0.147 | 0.37 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.04 | 0.008 | 0.487 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 18 | 5 | -0.301 | -0.381 | 0.079 | 0.452 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 143 | 9 | -0.153 | -0.107 | -0.046 | 0.623 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 114 | 7 | -0.275 | -0.35 | 0.075 | 0.372 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.268 | 0.433 | 0.308 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.768 | 1.468 | 0.115 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 133 | 8 | -0.032 | -0.059 | 0.026 | 0.433 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 87 | 6 | -0.415 | -0.344 | -0.071 | 0.589 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.143 | -0.513 | 0.883 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.418 | 0.08 | 0.447 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 24 | -1.93 (-1.31) | -0.823 (-0.89) | -0.823 (-0.89) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 81 / 81 | 0.259 (0.73) | 0.259 (0.73) | 0.259 (0.73) | AYNI |
| P2_ADAY | 75 / 66 | -0.113 (-0.17) | -0.235 (-0.32) | 0.015 (0.02) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.852 (1.09) | 2.285 (1.34) | 2.535 (1.48) | AYNI |
| P3_HACIM_BEKLE | 110 / 110 | -0.466 (-2.1) | -0.466 (-2.1) | -0.216 (-0.97) | AYNI |
| P3_RADAR | 149 / 139 | -0.367 (-1.09) | -0.354 (-1.0) | -0.104 (-0.29) | AYNI |
| P3_SKOR_AL | 289 / 283 | -0.51 (-1.47) | -0.532 (-1.51) | -0.282 (-0.8) | AYNI |
| P4_HAZIRLIK | 288 / 277 | -0.047 (-0.21) | -0.025 (-0.11) | 0.225 (0.93) | AYNI |
| POZ_AZALT | 39 / 22 | -1.931 (-1.95) | -0.663 (-0.62) | -0.663 (-0.62) | AYNI |
| SEKTOR_ROTASYONU | 253 / 242 | 0.024 (0.08) | 0.103 (0.31) | 0.353 (1.05) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 15 / 15 | -0.589 (-0.7) | -0.589 (-0.7) | -0.339 (-0.41) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 59 | 21 | -0.965 (-1.66) | 41.8 | 0.141 (0.14) |
| ANA (10:15-12:30) | 343 | 32 | -0.598 (-2.32) | 43.3 | -0.37 (-1.39) |
| KAPANIS (>=15:45) | 229 | 32 | -0.228 (-0.69) | 47.2 | -0.31 (-0.68) |
| OGLE (12:30-15:45) | 303 | 32 | 0.235 (0.62) | 47.9 | 0.287 (0.57) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 110 | 31 | -0.676 (-2.29) | 31.1 | -1.305 (None) |
| OBV | 39 | 19 | -0.796 (-1.75) | 39.4 | -0.33 (None) |
| RS | 4 | 4 | None (None) | None | None (None) |
| SECTOR | 9 | 9 | -1.433 (-4.04) | 33.3 | -2.38 (None) |
| TREND | 163 | 26 | -0.349 (-1.44) | 42.6 | -0.18 (None) |

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
