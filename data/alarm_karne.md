# Alarm Karnesi

Uretim: 2026-11-27T00:49 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEKTOR_ROTASYONU | BILGI | YUKARI | 326 | 0.322 (1.29) | -0.213 | 0.072 (0.29 / 0.38) | -0.318 (-1.06) | 0.33 (0.67) | 1.691 | 46.2 | 0.005 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 88 | 0.167 (0.51) | 0.205 | 0.167 (0.51 / 0.58) | 0.437 (1.34) | 0.087 (0.23) | 1.767 | 55.6 | 0.397 | **ADAY** |
| P4_HAZIRLIK | BILGI | YUKARI | 340 | 0.149 (0.72) | -0.32 | -0.101 (-0.49 / -0.47) | -0.452 (-1.5) | -0.087 (-0.48) | 0.189 | 47.2 | 0.003 | **KENAR_YOK** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.26 (-0.75) | -0.34 | -0.51 (-1.47 / -2.09) | -0.54 (-1.36) | -0.269 (-0.41) | 0.829 | 42.2 | -0.376 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 151 | -0.118 (-0.36) | -0.478 | -0.368 (-1.13 / -1.27) | -0.397 (-1.03) | 0.024 (0.08) | 0.359 | 51.7 | -0.212 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 137 | -0.169 (-0.66) | -0.389 | -0.419 (-1.64 / -1.7) | -1.151 (-5.02) | -0.279 (-1.2) | -1.057 | 42.7 | 0.254 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 75 | 0.111 (0.17) | -0.419 | -0.139 (-0.21 / -0.23) | -0.222 (-0.29) | 0.174 (0.24) | 0.183 | 50.7 | -1.158 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -1.458 | 43.6 | 2.393 | **KENAR_YOK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -2.745 (-1.16) | -0.419 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.084 (1.35) | -0.308 | 1.834 (1.19 / 1.09) | 1.448 (0.96) | 1.507 (1.06) | 3.354 | 47.8 | 1.779 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 17 | -0.339 (-0.41) | -1.036 | -0.589 (-0.7 / -0.71) | -0.714 (-0.94) | -0.058 (-0.08) | 1.56 | 40.0 | 0.585 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 2.662 (0.96) | 1.835 | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 81 / 0.167 | 42 / 0.096 | 39 / 0.243 | 88.6 |
| P2_ADAY | 28 / -0.946 | 47 / 0.342 | 26 / -0.743 | 49 / 0.182 | 77.3 |
| P2_DIP_DONUS | 12 / 4.276 | 11 / -0.829 | 12 / 1.471 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 110 / -0.419 | 36 / -0.447 | 74 / -0.406 | 97.1 |
| P3_RADAR | 44 / -0.653 | 105 / -0.248 | 59 / 0.372 | 90 / -0.853 | 72.2 |
| P3_SKOR_AL | 222 / -0.862 | 67 / 0.656 | 75 / 0.097 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 288 / -0.101 | 131 / 0.052 | 157 / -0.228 | 70.9 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 251 / 0.073 | 76 / -0.239 | 177 / 0.205 | 54.6 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 15 / -0.589 | 11 / -0.169 | 4 / -1.742 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir. Bu hafta (2026-W48) resmi bakis kaydedildi.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 33 | 8 | -0.638 | -2.02 | -0.398 | 0.489 | **DEVAM (8/10 gun)** |
| H14c_cikis_yonT3 | 90 | 10 | 0.351 | 0.86 | 0.478 | 0.684 | **DEVAM** |
| H14b_hacim_tetigi | 81 | 4 | -0.335 | 0.638 | - | - | **DEVAM (4/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 87 | 11 | 0.205 | 0.207 | -0.002 | 0.511 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 81 | 9 | 0.167 | 0.44 | -0.273 | 0.841 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 75 | 36 | -0.169 | 0.168 | -0.337 | 0.915 | OLCULEBILIR |
| P2_ADAY | T3 | 75 | 36 | 0.111 | 0.682 | -0.571 | 0.907 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 23 | 15 | -0.058 | 0.133 | -0.191 | 0.666 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 23 | 15 | 2.084 | 0.448 | 1.636 | 0.018 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 134 | 11 | -0.139 | -0.156 | 0.017 | 0.47 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 110 | 9 | -0.169 | -0.307 | 0.137 | 0.282 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 150 | 44 | -0.228 | 0.105 | -0.332 | 0.976 | OLCULEBILIR |
| P3_RADAR | T3 | 149 | 43 | -0.118 | 0.35 | -0.468 | 0.95 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.032 | -0.122 | 0.836 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 289 | 40 | -0.26 | 0.055 | -0.315 | 0.911 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 331 | 31 | -0.07 | 0.016 | -0.085 | 0.775 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 288 | 29 | 0.149 | 0.208 | -0.059 | 0.621 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.102 | -1.059 | 0.999 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.252 | -2.183 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 306 | 30 | 0.037 | 0.001 | 0.036 | 0.37 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 253 | 28 | 0.322 | 0.204 | 0.117 | 0.267 | OLCULEBILIR |
| TASIMA | T1 | 17 | 6 | -0.786 | -0.17 | -0.616 | 0.928 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.392 | 0.054 | 0.481 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 87 | 11 | 0.205 | 0.218 | -0.013 | 0.539 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 81 | 9 | 0.167 | 0.444 | -0.277 | 0.85 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 11 | 6 | -0.178 | -0.274 | 0.096 | 0.423 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 11 | 6 | -0.269 | -0.497 | 0.228 | 0.363 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 8 | 4 | -0.035 | -0.04 | 0.005 | 0.493 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 8 | 4 | -0.336 | -0.133 | -0.203 | 0.593 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 134 | 11 | -0.139 | -0.159 | 0.02 | 0.433 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 110 | 9 | -0.169 | -0.293 | 0.123 | 0.284 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 46 | 11 | 0.068 | -0.067 | 0.135 | 0.298 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 45 | 10 | -0.229 | -0.329 | 0.099 | 0.4 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.013 | 0.035 | 0.449 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 18 | 5 | -0.301 | -0.386 | 0.085 | 0.435 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 199 | 12 | -0.203 | -0.138 | -0.065 | 0.706 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 156 | 10 | -0.245 | -0.224 | -0.021 | 0.537 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.258 | 0.443 | 0.286 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.756 | 1.479 | 0.12 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 203 | 11 | -0.069 | -0.122 | 0.053 | 0.312 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 150 | 9 | -0.045 | -0.112 | 0.067 | 0.364 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 17 | 6 | -0.786 | -0.156 | -0.63 | 0.934 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 15 | 4 | -0.339 | -0.384 | 0.046 | 0.462 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 23 | -1.93 (-1.31) | -0.43 (-0.49) | -0.43 (-0.49) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 88 / 88 | 0.167 (0.51) | 0.167 (0.51) | 0.167 (0.51) | AYNI |
| P2_ADAY | 75 / 64 | -0.139 (-0.21) | -0.197 (-0.27) | 0.053 (0.07) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.834 (1.19) | 2.227 (1.44) | 2.477 (1.6) | AYNI |
| P3_HACIM_BEKLE | 137 / 137 | -0.419 (-1.64) | -0.419 (-1.64) | -0.169 (-0.66) | AYNI |
| P3_RADAR | 151 / 141 | -0.368 (-1.13) | -0.355 (-1.03) | -0.105 (-0.31) | AYNI |
| P3_SKOR_AL | 289 / 282 | -0.51 (-1.47) | -0.522 (-1.48) | -0.272 (-0.77) | AYNI |
| P4_HAZIRLIK | 340 / 329 | -0.101 (-0.49) | -0.084 (-0.39) | 0.166 (0.77) | AYNI |
| POZ_AZALT | 39 / 19 | -1.931 (-1.95) | -0.728 (-0.58) | -0.728 (-0.58) | AYNI |
| SEKTOR_ROTASYONU | 326 / 315 | 0.072 (0.29) | 0.133 (0.51) | 0.383 (1.48) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 17 / 17 | -0.589 (-0.7) | -0.589 (-0.7) | -0.339 (-0.41) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 71 | 22 | -0.952 (-1.76) | 39.0 | 0.039 (0.04) |
| ANA (10:15-12:30) | 382 | 32 | -0.458 (-1.82) | 46.1 | -0.256 (-1.07) |
| KAPANIS (>=15:45) | 248 | 32 | -0.326 (-1.0) | 46.7 | -0.265 (-0.62) |
| OGLE (12:30-15:45) | 314 | 32 | 0.139 (0.39) | 47.2 | 0.221 (0.49) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 164 | 31 | -0.742 (-2.63) | 36.4 | -0.7 (-1.5) |
| OBV | 50 | 24 | -0.726 (-1.73) | 43.6 | -0.317 (-15.19) |
| RS | 14 | 11 | -0.189 (-0.18) | 50.0 | None (None) |
| SECTOR | 9 | 9 | -0.58 (-0.76) | 55.6 | -1.447 (-1.16) |
| TREND | 169 | 26 | -0.217 (-0.88) | 44.8 | 0.024 (0.08) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-26, 100 islem gunu; gunluk alarm medyani 10.0, GUNLUK_OZET medyani 15.0.
- Ham kayit 4236, eventId tekrari 256, tekil 3980.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 48, son 30 gunde 2. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
