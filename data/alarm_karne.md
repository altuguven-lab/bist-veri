# Alarm Karnesi

Uretim: 2026-11-28T00:15 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEKTOR_ROTASYONU | BILGI | YUKARI | 343 | 0.28 (1.21) | -0.19 | 0.03 (0.13 / 0.17) | -0.269 (-0.96) | 0.279 (0.61) | 1.658 | 46.4 | -0.005 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 91 | 0.19 (0.61) | 0.162 | 0.19 (0.61 / 0.67) | 0.45 (1.46) | 0.014 (0.03) | 0.809 | 55.3 | 0.406 | **ADAY** |
| P4_HAZIRLIK | BILGI | YUKARI | 363 | 0.092 (0.47) | -0.332 | -0.158 (-0.81 / -0.77) | -0.531 (-1.86) | -0.103 (-0.62) | 0.082 | 46.9 | -0.007 | **KENAR_YOK** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.26 (-0.75) | -0.34 | -0.51 (-1.47 / -2.09) | -0.54 (-1.36) | -0.269 (-0.41) | 0.809 | 42.2 | -0.376 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 156 | -0.114 (-0.35) | -0.48 | -0.364 (-1.12 / -1.26) | -0.393 (-1.03) | 0.062 (0.21) | 0.303 | 52.0 | -0.194 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 154 | -0.285 (-1.1) | -0.391 | -0.535 (-2.06 / -2.27) | -1.26 (-5.25) | -0.347 (-2.64) | -0.748 | 40.8 | 0.185 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 75 | 0.111 (0.17) | -0.419 | -0.139 (-0.21 / -0.23) | -0.222 (-0.29) | 0.174 (0.24) | 0.082 | 50.7 | -1.158 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -1.458 | 43.6 | 2.393 | **KENAR_YOK** |
| ACIL_CIK | KRITIK | ASAGI | 30 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -2.745 (-1.16) | -0.168 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.084 (1.35) | -0.308 | 1.834 (1.19 / 1.09) | 1.448 (0.96) | 1.507 (1.06) | 2.615 | 47.8 | 1.779 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 17 | -0.287 (-0.37) | -1.036 | -0.537 (-0.7 / -0.69) | -0.685 (-0.98) | -0.058 (-0.08) | 0.159 | 43.8 | 0.699 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 2.662 (0.96) | 5.107 | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 23.3 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 85 / 0.19 | 46 / 0.145 | 39 / 0.243 | 89.0 |
| P2_ADAY | 28 / -0.946 | 47 / 0.342 | 26 / -0.743 | 49 / 0.182 | 77.3 |
| P2_DIP_DONUS | 12 / 4.276 | 11 / -0.829 | 12 / 1.471 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 120 / -0.535 | 40 / -0.693 | 80 / -0.456 | 96.8 |
| P3_RADAR | 44 / -0.653 | 106 / -0.244 | 60 / 0.37 | 90 / -0.853 | 72.4 |
| P3_SKOR_AL | 222 / -0.862 | 67 / 0.656 | 75 / 0.097 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 311 / -0.158 | 148 / -0.02 | 163 / -0.284 | 71.9 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 276 / 0.031 | 85 / -0.33 | 193 / 0.189 | 56.0 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 16 / -0.537 | 12 / -0.135 | 4 / -1.742 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir. Bu hafta (2026-W48) resmi bakis kaydedildi.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 33 | 8 | -0.638 | -2.02 | -0.398 | 0.489 | **DEVAM (8/10 gun)** |
| H14c_cikis_yonT3 | 94 | 11 | 0.363 | 0.93 | 0.491 | 0.682 | **DEVAM** |
| H14b_hacim_tetigi | 81 | 4 | -0.335 | 0.638 | - | - | **DEVAM (4/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 88 | 12 | 0.162 | 0.206 | -0.044 | 0.596 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 85 | 10 | 0.19 | 0.45 | -0.26 | 0.821 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 75 | 36 | -0.169 | 0.162 | -0.331 | 0.907 | OLCULEBILIR |
| P2_ADAY | T3 | 75 | 36 | 0.111 | 0.705 | -0.593 | 0.916 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 23 | 15 | -0.058 | 0.14 | -0.198 | 0.687 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 23 | 15 | 2.084 | 0.435 | 1.649 | 0.019 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 137 | 12 | -0.141 | -0.145 | 0.004 | 0.495 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 120 | 10 | -0.285 | -0.322 | 0.037 | 0.432 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 151 | 45 | -0.23 | 0.104 | -0.334 | 0.977 | OLCULEBILIR |
| P3_RADAR | T3 | 150 | 44 | -0.114 | 0.353 | -0.466 | 0.951 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.03 | -0.12 | 0.838 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 289 | 40 | -0.26 | 0.046 | -0.305 | 0.904 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 340 | 32 | -0.082 | 0.02 | -0.102 | 0.836 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 311 | 30 | 0.092 | 0.147 | -0.055 | 0.623 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.105 | -1.062 | 0.998 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.265 | -2.195 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 326 | 31 | 0.06 | 0.016 | 0.045 | 0.334 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 278 | 29 | 0.28 | 0.134 | 0.146 | 0.196 | OLCULEBILIR |
| TASIMA | T1 | 17 | 6 | -0.786 | -0.158 | -0.628 | 0.935 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 16 | 5 | -0.287 | -0.407 | 0.12 | 0.412 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 88 | 12 | 0.162 | 0.211 | -0.048 | 0.616 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 85 | 10 | 0.19 | 0.45 | -0.26 | 0.831 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 11 | 6 | -0.178 | -0.283 | 0.106 | 0.426 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 11 | 6 | -0.269 | -0.507 | 0.238 | 0.386 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 8 | 4 | -0.035 | -0.02 | -0.014 | 0.506 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 8 | 4 | -0.336 | -0.131 | -0.205 | 0.606 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 137 | 12 | -0.141 | -0.148 | 0.007 | 0.485 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 120 | 10 | -0.285 | -0.316 | 0.032 | 0.449 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 47 | 12 | 0.055 | -0.069 | 0.125 | 0.304 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 46 | 11 | -0.214 | -0.341 | 0.127 | 0.377 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.032 | 0.015 | 0.478 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 18 | 5 | -0.301 | -0.384 | 0.083 | 0.444 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 208 | 13 | -0.218 | -0.125 | -0.093 | 0.787 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 179 | 11 | -0.294 | -0.277 | -0.017 | 0.535 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.263 | 0.439 | 0.293 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.74 | 1.496 | 0.103 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 223 | 12 | -0.025 | -0.089 | 0.064 | 0.275 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 175 | 10 | -0.059 | -0.188 | 0.129 | 0.263 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 17 | 6 | -0.786 | -0.181 | -0.605 | 0.93 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 16 | 5 | -0.287 | -0.428 | 0.142 | 0.414 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 30 / 24 | -1.93 (-1.31) | -0.43 (-0.49) | -0.43 (-0.49) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 91 / 91 | 0.19 (0.61) | 0.19 (0.61) | 0.19 (0.61) | AYNI |
| P2_ADAY | 75 / 64 | -0.139 (-0.21) | -0.197 (-0.27) | 0.053 (0.07) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.834 (1.19) | 2.227 (1.44) | 2.477 (1.6) | AYNI |
| P3_HACIM_BEKLE | 154 / 154 | -0.535 (-2.06) | -0.535 (-2.06) | -0.285 (-1.1) | AYNI |
| P3_RADAR | 156 / 146 | -0.364 (-1.12) | -0.35 (-1.03) | -0.1 (-0.29) | AYNI |
| P3_SKOR_AL | 289 / 282 | -0.51 (-1.47) | -0.522 (-1.48) | -0.272 (-0.77) | AYNI |
| P4_HAZIRLIK | 363 / 352 | -0.158 (-0.81) | -0.145 (-0.71) | 0.105 (0.51) | AYNI |
| POZ_AZALT | 39 / 19 | -1.931 (-1.95) | -0.728 (-0.58) | -0.728 (-0.58) | AYNI |
| SEKTOR_ROTASYONU | 343 / 332 | 0.03 (0.13) | 0.084 (0.35) | 0.334 (1.41) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 17 / 17 | -0.537 (-0.7) | -0.537 (-0.7) | -0.287 (-0.37) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 71 | 22 | -0.866 (-1.67) | 40.3 | 0.11 (0.12) |
| ANA (10:15-12:30) | 397 | 32 | -0.535 (-2.1) | 45.3 | -0.24 (-1.01) |
| KAPANIS (>=15:45) | 252 | 32 | -0.315 (-1.02) | 46.9 | -0.258 (-0.61) |
| OGLE (12:30-15:45) | 340 | 32 | 0.127 (0.36) | 46.9 | 0.159 (0.35) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 196 | 32 | -0.876 (-3.24) | 34.6 | -0.606 (-1.41) |
| OBV | 58 | 26 | -0.639 (-1.63) | 44.2 | -0.383 (-4.78) |
| RS | 18 | 14 | -0.514 (-1.15) | 55.6 | -1.338 (None) |
| SECTOR | 9 | 9 | -0.58 (-0.76) | 55.6 | -1.447 (-1.16) |
| TREND | 170 | 27 | -0.227 (-0.96) | 45.2 | 0.028 (0.1) |

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
