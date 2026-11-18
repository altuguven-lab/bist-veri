# Alarm Karnesi

Uretim: 2026-11-18T23:08 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 246 | 0.263 (0.92) | -0.235 | 0.013 (0.04 / 0.04) | -0.146 (-0.34) | 0.102 (0.43) | 0.511 | 48.4 | 0.033 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 190 | 0.409 (0.92) | -0.131 | 0.159 (0.36 / 0.53) | 0.154 (0.3) | 0.787 (1.14) | 2.119 | 47.0 | 0.068 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 73 | 0.674 (1.0) | 0.204 | 0.674 (1.0 / 1.47) | 0.82 (1.22) | 3.04 (None) | None | 59.0 | -0.221 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.244 (-0.69) | -0.34 | -0.494 (-1.39 / -1.97) | -0.52 (-1.28) | -0.221 (-0.32) | 0.899 | 42.7 | -0.399 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 144 | -0.126 (-0.34) | -0.498 | -0.376 (-1.03 / -1.15) | -0.365 (-0.83) | 0.106 (0.3) | 0.657 | 52.7 | -0.267 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 84 | -0.426 (-1.99) | -0.314 | -0.676 (-3.16 / -1.79) | -1.308 (-4.69) | -0.694 (None) | None | 44.4 | 0.717 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 74 | 0.085 (0.12) | -0.386 | -0.165 (-0.24 / -0.26) | -0.215 (-0.27) | 0.065 (0.08) | 0.528 | 51.4 | -1.146 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -2.114 | 43.6 | 2.393 | **KENAR_YOK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -3.05 (-1.25) | -0.879 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 21 | 2.206 (1.24) | -0.435 | 1.956 (1.1 / 1.01) | 1.843 (1.08) | 2.049 (1.09) | 3.765 | 45.0 | 2.019 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 15 | -0.887 (-0.66) | -0.905 | -1.137 (-0.84 / -0.91) | -1.016 (-0.71) | None (None) | None | 37.5 | -0.982 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | None (None) | None | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 39 / 0.674 | 24 / 0.448 | 15 / 1.036 | 86.3 |
| P2_ADAY | 28 / -0.946 | 42 / 0.355 | 22 / -0.753 | 48 / 0.104 | 77.0 |
| P2_DIP_DONUS | 12 / 4.276 | 8 / -1.524 | 9 / 1.621 | 11 / 2.23 | 52.4 |
| P3_HACIM_BEKLE | 0 / None | 45 / -0.676 | 15 / -1.001 | 30 / -0.514 | 95.2 |
| P3_RADAR | 44 / -0.653 | 85 / -0.232 | 50 / 0.638 | 79 / -1.018 | 70.8 |
| P3_SKOR_AL | 222 / -0.862 | 59 / 0.888 | 67 / 0.234 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 190 / 0.013 | 78 / 0.27 | 112 / -0.166 | 62.6 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 130 / 0.163 | 40 / -0.085 | 92 / 0.265 | 54.2 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 8 / -1.137 | 6 / -1.021 | 2 / -1.486 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 17 | 3 | -0.99 | -2.52 | -0.495 | 0.654 | **DEVAM (3/10 gun)** |
| H14c_cikis_yonT3 | 48 | 4 | 0.923 | 1.29 | 0.65 | 0.248 | **DEVAM (4/10 gun)** |
| H14b_hacim_tetigi | 43 | 2 | 0.295 | 0.432 | - | - | **DEVAM (2/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 68 | 5 | 0.204 | 0.202 | 0.002 | 0.494 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 39 | 3 | 0.674 | 0.601 | 0.073 | 0.429 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 72 | 34 | -0.136 | 0.174 | -0.311 | 0.896 | OLCULEBILIR |
| P2_ADAY | T3 | 70 | 33 | 0.085 | 0.775 | -0.69 | 0.948 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 21 | 14 | -0.185 | 0.108 | -0.293 | 0.74 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 20 | 13 | 2.206 | 0.486 | 1.72 | 0.027 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 75 | 5 | -0.064 | -0.201 | 0.137 | 0.249 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 45 | 3 | -0.426 | -0.608 | 0.181 | 0.321 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 142 | 39 | -0.248 | 0.114 | -0.363 | 0.975 | OLCULEBILIR |
| P3_RADAR | T3 | 129 | 37 | -0.126 | 0.438 | -0.564 | 0.962 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.027 | -0.117 | 0.822 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 281 | 38 | -0.244 | 0.057 | -0.301 | 0.898 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 225 | 25 | 0.015 | 0.093 | -0.077 | 0.722 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 190 | 23 | 0.263 | 0.35 | -0.087 | 0.63 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.099 | -1.056 | 1.0 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.245 | -2.176 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 167 | 24 | 0.119 | 0.087 | 0.032 | 0.417 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 132 | 22 | 0.409 | 0.34 | 0.069 | 0.412 | OLCULEBILIR |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.15 | -0.506 | 0.877 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 8 | 2 | -0.887 | -0.411 | -0.476 | 0.688 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 68 | 5 | 0.204 | 0.213 | -0.009 | 0.522 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 39 | 3 | 0.674 | 0.605 | 0.07 | 0.43 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 8 | 4 | 0.117 | -0.282 | 0.399 | 0.265 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 6 | 3 | -0.899 | -0.574 | -0.324 | 0.626 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 6 | 3 | -0.472 | -0.211 | -0.26 | 0.625 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 5 | 2 | -1.301 | -0.435 | -0.866 | 0.785 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 75 | 5 | -0.064 | -0.199 | 0.135 | 0.267 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 45 | 3 | -0.426 | -0.618 | 0.191 | 0.315 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 38 | 6 | 0.054 | -0.091 | 0.145 | 0.3 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 25 | 4 | -0.361 | -0.447 | 0.087 | 0.434 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.042 | 0.005 | 0.481 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 10 | 3 | 0.104 | -0.279 | 0.382 | 0.345 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 93 | 6 | -0.149 | -0.113 | -0.036 | 0.573 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 58 | 4 | -0.539 | -0.508 | -0.031 | 0.524 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.238 | 0.463 | 0.289 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.753 | 1.482 | 0.103 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 64 | 5 | -0.084 | -0.16 | 0.076 | 0.349 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 29 | 3 | -1.181 | -0.843 | -0.338 | 0.763 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.15 | -0.505 | 0.872 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 8 | 2 | -0.887 | -0.374 | -0.514 | 0.713 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 25 | -1.93 (-1.31) | -0.933 (-1.04) | -0.933 (-1.04) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 73 / 73 | 0.674 (1.0) | 0.674 (1.0) | 0.674 (1.0) | AYNI |
| P2_ADAY | 74 / 65 | -0.165 (-0.24) | -0.303 (-0.39) | -0.053 (-0.07) | AYNI |
| P2_DIP_DONUS | 21 / 20 | 1.956 (1.1) | 2.418 (1.35) | 2.668 (1.49) | AYNI |
| P3_HACIM_BEKLE | 84 / 84 | -0.676 (-3.16) | -0.676 (-3.16) | -0.426 (-1.99) | AYNI |
| P3_RADAR | 144 / 134 | -0.376 (-1.03) | -0.361 (-0.93) | -0.111 (-0.29) | AYNI |
| P3_SKOR_AL | 289 / 286 | -0.494 (-1.39) | -0.496 (-1.38) | -0.246 (-0.68) | AYNI |
| P4_HAZIRLIK | 246 / 235 | 0.013 (0.04) | 0.045 (0.15) | 0.295 (0.96) | AYNI |
| POZ_AZALT | 39 / 24 | -1.931 (-1.95) | -0.922 (-0.89) | -0.922 (-0.89) | AYNI |
| SEKTOR_ROTASYONU | 190 / 179 | 0.159 (0.36) | 0.288 (0.6) | 0.538 (1.12) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 15 / 15 | -1.137 (-0.84) | -1.137 (-0.84) | -0.887 (-0.66) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 55 | 20 | -0.923 (-1.54) | 43.4 | -0.082 (-0.07) |
| ANA (10:15-12:30) | 307 | 32 | -0.605 (-1.97) | 46.4 | -0.421 (-1.12) |
| KAPANIS (>=15:45) | 216 | 31 | -0.217 (-0.61) | 47.4 | -0.076 (-0.17) |
| OGLE (12:30-15:45) | 280 | 32 | 0.235 (0.52) | 47.9 | 0.472 (0.81) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 61 | 28 | -1.486 (-8.93) | 22.7 | None (None) |
| OBV | 33 | 17 | -0.198 (-0.95) | 50.0 | None (None) |
| RS | 1 | 1 | None (None) | None | None (None) |
| SECTOR | 6 | 6 | -1.414 (-2.95) | 40.0 | None (None) |
| TREND | 148 | 25 | -0.633 (-1.8) | 43.0 | -0.27 (None) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-18, 94 islem gunu; gunluk alarm medyani 6.0, GUNLUK_OZET medyani 15.0.
- Ham kayit 3462, eventId tekrari 256, tekil 3206.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 44, son 30 gunde 5. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
