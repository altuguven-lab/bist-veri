# Alarm Karnesi

Uretim: 2026-11-20T22:49 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEKTOR_ROTASYONU | BILGI | YUKARI | 236 | 0.293 (0.81) | -0.145 | 0.043 (0.12 / 0.17) | 0.043 (0.1) | 0.601 (0.85) | 2.165 | 44.9 | -0.045 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 79 | 0.305 (0.79) | 0.244 | 0.305 (0.79 / 0.93) | 0.535 (1.37) | 0.851 (None) | None | 58.8 | 0.253 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.26 (-0.75) | -0.34 | -0.51 (-1.47 / -2.09) | -0.54 (-1.36) | -0.232 (-0.34) | 0.829 | 42.2 | -0.376 | **KENAR_YOK** |
| P4_HAZIRLIK | BILGI | YUKARI | 275 | 0.205 (0.82) | -0.276 | -0.045 (-0.18 / -0.17) | -0.18 (-0.49) | -0.128 (-0.53) | 0.437 | 46.7 | 0.076 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 148 | -0.093 (-0.27) | -0.499 | -0.343 (-1.01 / -1.14) | -0.325 (-0.81) | 0.028 (0.08) | 0.463 | 52.1 | -0.221 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 103 | -0.211 (-0.83) | -0.284 | -0.461 (-1.81 / -1.59) | -0.96 (-3.52) | -0.716 (None) | None | 44.0 | 0.527 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 74 | 0.176 (0.26) | -0.431 | -0.074 (-0.11 / -0.12) | -0.104 (-0.13) | -0.028 (-0.03) | 0.165 | 52.8 | -1.061 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -2.114 | 43.6 | 2.393 | **KENAR_YOK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -2.745 (-1.16) | -0.958 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.102 (1.24) | -0.308 | 1.852 (1.09 / 1.0) | 1.69 (1.04) | 1.266 (0.77) | 3.765 | 42.9 | 1.993 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 15 | -0.339 (-0.41) | -0.905 | -0.589 (-0.7 / -0.71) | -0.714 (-0.94) | -0.457 (None) | None | 40.0 | 0.585 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 2.662 (0.96) | None | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 68 / 0.305 | 35 / 0.172 | 33 / 0.446 | 87.3 |
| P2_ADAY | 28 / -0.946 | 44 / 0.48 | 23 / -0.62 | 49 / 0.182 | 77.0 |
| P2_DIP_DONUS | 12 / 4.276 | 9 / -1.379 | 10 / 1.436 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 75 / -0.461 | 22 / -0.236 | 53 / -0.554 | 96.1 |
| P3_RADAR | 44 / -0.653 | 98 / -0.204 | 53 / 0.551 | 89 / -0.876 | 71.6 |
| P3_SKOR_AL | 222 / -0.862 | 67 / 0.656 | 75 / 0.097 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 225 / -0.045 | 91 / 0.286 | 134 / -0.27 | 66.2 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 165 / 0.045 | 48 / -0.214 | 119 / 0.147 | 54.7 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 15 / -0.589 | 11 / -0.169 | 4 / -1.742 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir. Bu hafta (2026-W47) resmi bakis kaydedildi.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 28 | 5 | -0.689 | -2.07 | -0.52 | 0.419 | **DEVAM (5/10 gun)** |
| H14c_cikis_yonT3 | 77 | 6 | 0.503 | 1.06 | 0.553 | 0.567 | **DEVAM (6/10 gun)** |
| H14b_hacim_tetigi | 81 | 4 | -0.335 | 0.638 | - | - | **DEVAM (4/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 74 | 7 | 0.244 | 0.231 | 0.012 | 0.481 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 68 | 5 | 0.305 | 0.516 | -0.211 | 0.771 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 74 | 35 | -0.181 | 0.158 | -0.338 | 0.915 | OLCULEBILIR |
| P2_ADAY | T3 | 72 | 34 | 0.176 | 0.728 | -0.552 | 0.886 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 23 | 15 | -0.058 | 0.157 | -0.215 | 0.699 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 21 | 14 | 2.102 | 0.397 | 1.705 | 0.024 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 94 | 7 | -0.034 | -0.158 | 0.124 | 0.252 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 75 | 5 | -0.211 | -0.519 | 0.308 | 0.141 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 146 | 41 | -0.249 | 0.111 | -0.36 | 0.983 | OLCULEBILIR |
| P3_RADAR | T3 | 142 | 39 | -0.093 | 0.36 | -0.453 | 0.935 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.031 | -0.121 | 0.831 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 289 | 40 | -0.26 | 0.043 | -0.303 | 0.908 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 260 | 27 | -0.026 | 0.062 | -0.088 | 0.764 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 225 | 25 | 0.205 | 0.241 | -0.036 | 0.554 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.103 | -1.06 | 1.0 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.245 | -2.175 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 217 | 26 | 0.105 | 0.073 | 0.032 | 0.402 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 167 | 24 | 0.293 | 0.235 | 0.058 | 0.415 | OLCULEBILIR |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.141 | -0.515 | 0.879 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.396 | 0.058 | 0.454 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 74 | 7 | 0.244 | 0.227 | 0.016 | 0.475 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 68 | 5 | 0.305 | 0.521 | -0.216 | 0.756 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 10 | 5 | -0.262 | -0.35 | 0.088 | 0.432 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 8 | 4 | 0.167 | -0.609 | 0.776 | 0.185 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 8 | 4 | -0.035 | -0.009 | -0.026 | 0.517 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 6 | 3 | -1.08 | -0.502 | -0.577 | 0.709 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 94 | 7 | -0.034 | -0.152 | 0.117 | 0.262 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 75 | 5 | -0.211 | -0.511 | 0.301 | 0.152 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 42 | 8 | 0.024 | -0.079 | 0.103 | 0.357 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 38 | 6 | -0.158 | -0.415 | 0.257 | 0.296 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.029 | 0.019 | 0.46 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 18 | 5 | -0.301 | -0.377 | 0.076 | 0.432 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 128 | 8 | -0.188 | -0.124 | -0.064 | 0.666 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 93 | 6 | -0.378 | -0.431 | 0.054 | 0.411 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.238 | 0.464 | 0.283 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.742 | 1.494 | 0.113 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 114 | 7 | -0.022 | -0.081 | 0.059 | 0.33 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 64 | 5 | -0.613 | -0.47 | -0.143 | 0.672 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.14 | -0.516 | 0.885 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.376 | 0.038 | 0.478 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 24 | -1.93 (-1.31) | -0.823 (-0.89) | -0.823 (-0.89) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 79 / 79 | 0.305 (0.79) | 0.305 (0.79) | 0.305 (0.79) | AYNI |
| P2_ADAY | 74 / 65 | -0.074 (-0.11) | -0.194 (-0.26) | 0.056 (0.07) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.852 (1.09) | 2.285 (1.34) | 2.535 (1.48) | AYNI |
| P3_HACIM_BEKLE | 103 / 103 | -0.461 (-1.81) | -0.461 (-1.81) | -0.211 (-0.83) | AYNI |
| P3_RADAR | 148 / 138 | -0.343 (-1.01) | -0.328 (-0.91) | -0.078 (-0.22) | AYNI |
| P3_SKOR_AL | 289 / 283 | -0.51 (-1.47) | -0.532 (-1.51) | -0.282 (-0.8) | AYNI |
| P4_HAZIRLIK | 275 / 264 | -0.045 (-0.18) | -0.021 (-0.08) | 0.229 (0.87) | AYNI |
| POZ_AZALT | 39 / 22 | -1.931 (-1.95) | -0.663 (-0.62) | -0.663 (-0.62) | AYNI |
| SEKTOR_ROTASYONU | 236 / 225 | 0.043 (0.12) | 0.136 (0.35) | 0.386 (1.0) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 15 / 15 | -0.589 (-0.7) | -0.589 (-0.7) | -0.339 (-0.41) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 57 | 21 | -0.923 (-1.54) | 43.4 | 0.141 (0.14) |
| ANA (10:15-12:30) | 340 | 32 | -0.641 (-2.36) | 43.6 | -0.413 (-1.42) |
| KAPANIS (>=15:45) | 220 | 31 | -0.195 (-0.58) | 47.6 | -0.248 (-0.55) |
| OGLE (12:30-15:45) | 295 | 32 | 0.256 (0.65) | 48.5 | 0.211 (0.37) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 94 | 31 | -0.756 (-1.71) | 29.3 | -1.888 (None) |
| OBV | 38 | 18 | -0.647 (-1.32) | 43.3 | -0.008 (None) |
| RS | 2 | 2 | None (None) | None | None (None) |
| SECTOR | 9 | 9 | -1.433 (-4.04) | 33.3 | -2.305 (None) |
| TREND | 160 | 26 | -0.392 (-1.52) | 43.5 | -0.496 (None) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-20, 96 islem gunu; gunluk alarm medyani 7.0, GUNLUK_OZET medyani 15.0.
- Ham kayit 3708, eventId tekrari 256, tekil 3452.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 46, son 30 gunde 3. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
