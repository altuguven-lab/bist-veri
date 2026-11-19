# Alarm Karnesi

Uretim: 2026-11-19T23:13 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SEKTOR_ROTASYONU | BILGI | YUKARI | 217 | 0.286 (0.68) | -0.203 | 0.036 (0.09 / 0.13) | 0.059 (0.12) | 0.624 (0.89) | 2.119 | 45.1 | -0.023 | **ADAY** |
| IC_STOP | KRITIK | ASAGI | 74 | 0.479 (1.07) | 0.236 | 0.479 (1.07 / 1.33) | 0.735 (1.7) | 2.102 (None) | None | 57.9 | 0.119 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.258 (-0.74) | -0.34 | -0.508 (-1.46 / -2.07) | -0.539 (-1.35) | -0.203 (-0.29) | 0.839 | 42.5 | -0.392 | **KENAR_YOK** |
| P4_HAZIRLIK | BILGI | YUKARI | 260 | 0.183 (0.68) | -0.3 | -0.067 (-0.25 / -0.24) | -0.203 (-0.52) | -0.074 (-0.3) | 0.445 | 46.6 | 0.042 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 146 | -0.157 (-0.45) | -0.509 | -0.407 (-1.16 / -1.31) | -0.38 (-0.92) | 0.033 (0.09) | 0.414 | 52.2 | -0.277 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 74 | 0.176 (0.26) | -0.431 | -0.074 (-0.11 / -0.12) | -0.104 (-0.13) | 0.132 (0.17) | 0.254 | 52.8 | -1.061 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -1.962 (-1.12) | -2.114 | 43.6 | 2.393 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 94 | -0.427 (-2.91) | -0.398 | -0.677 (-4.61 / -2.12) | -1.122 (-4.22) | -1.017 (None) | None | 41.9 | 0.605 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.93 (-1.31) | -0.393 | -1.93 (-1.31 / -1.24) | -1.192 (-0.79) | -3.05 (-1.25) | -0.879 | 55.2 | 1.597 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 23 | 2.102 (1.24) | -0.435 | 1.852 (1.09 / 1.0) | 1.69 (1.04) | 1.415 (0.76) | 3.765 | 42.9 | 1.993 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 15 | -0.742 (-0.89) | -0.905 | -0.992 (-1.19 / -1.07) | -1.006 (-1.21) | 1.369 (None) | None | 41.7 | 0.14 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 2.051 (1.68) | 1.128 | 1.801 (1.47 / 1.47) | 1.046 (0.71) | 0.003 (0.0) | None | 66.7 | 1.455 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 13 / -0.161 | 17 / -3.334 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 3 / 1.801 | 2 / 2.061 | 1 / None | 66.7 |
| IC_STOP | 0 / None | 57 / 0.479 | 30 / 0.529 | 27 / 0.423 | 86.5 |
| P2_ADAY | 28 / -0.946 | 44 / 0.48 | 23 / -0.62 | 49 / 0.182 | 77.0 |
| P2_DIP_DONUS | 12 / 4.276 | 9 / -1.379 | 10 / 1.436 | 11 / 2.23 | 56.5 |
| P3_HACIM_BEKLE | 0 / None | 62 / -0.677 | 20 / -0.536 | 42 / -0.744 | 95.7 |
| P3_RADAR | 44 / -0.653 | 92 / -0.289 | 51 / 0.601 | 85 / -1.012 | 71.2 |
| P3_SKOR_AL | 222 / -0.862 | 65 / 0.698 | 73 / 0.119 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 208 / -0.067 | 84 / 0.229 | 124 / -0.269 | 64.2 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 142 / 0.039 | 42 / -0.255 | 102 / 0.156 | 54.8 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 12 / -0.992 | 9 / -0.626 | 3 / -2.093 | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir. Bu hafta (2026-W47) resmi bakis kaydedildi.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 26 | 4 | -0.687 | -1.86 | -0.569 | 0.399 | **DEVAM (4/10 gun)** |
| H14c_cikis_yonT3 | 66 | 5 | 0.687 | 1.29 | 0.657 | 0.465 | **DEVAM (5/10 gun)** |
| H14b_hacim_tetigi | 66 | 3 | -0.103 | 0.56 | - | - | **DEVAM (3/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 29 | 23 | -1.93 | -0.36 | -1.571 | 0.984 | OLCULEBILIR |
| IC_STOP | T1 | 73 | 6 | 0.236 | 0.242 | -0.006 | 0.518 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 57 | 4 | 0.479 | 0.628 | -0.149 | 0.683 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 74 | 35 | -0.181 | 0.154 | -0.335 | 0.904 | OLCULEBILIR |
| P2_ADAY | T3 | 72 | 34 | 0.176 | 0.727 | -0.551 | 0.895 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 21 | 14 | -0.185 | 0.102 | -0.286 | 0.742 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 21 | 14 | 2.102 | 0.417 | 1.685 | 0.02 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 84 | 6 | -0.148 | -0.242 | 0.093 | 0.319 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 62 | 4 | -0.427 | -0.64 | 0.213 | 0.268 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 144 | 40 | -0.259 | 0.104 | -0.363 | 0.974 | OLCULEBILIR |
| P3_RADAR | T3 | 136 | 38 | -0.157 | 0.373 | -0.53 | 0.952 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 289 | 40 | -0.09 | 0.032 | -0.122 | 0.833 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 287 | 39 | -0.258 | 0.057 | -0.315 | 0.912 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 246 | 26 | -0.05 | 0.031 | -0.081 | 0.73 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 208 | 24 | 0.183 | 0.245 | -0.063 | 0.597 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.099 | -1.056 | 0.999 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.233 | -2.164 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 190 | 25 | 0.047 | -0.005 | 0.053 | 0.344 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 144 | 23 | 0.286 | 0.262 | 0.024 | 0.46 | OLCULEBILIR |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.143 | -0.512 | 0.876 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 12 | 3 | -0.742 | -0.472 | -0.27 | 0.646 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| ACIL_CIK | T3 | 5 | 3 | 1.463 | 0.309 | 1.154 | 0.235 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 73 | 6 | 0.236 | 0.243 | -0.007 | 0.522 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 57 | 4 | 0.479 | 0.627 | -0.148 | 0.676 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 10 | 5 | -0.262 | -0.341 | 0.079 | 0.444 | HUKUM YOK (<20 gun) |
| P2_ADAY | T3 | 8 | 4 | 0.167 | -0.599 | 0.766 | 0.204 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 6 | 3 | -0.472 | -0.206 | -0.266 | 0.645 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 6 | 3 | -1.08 | -0.493 | -0.587 | 0.703 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 84 | 6 | -0.148 | -0.246 | 0.098 | 0.302 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 62 | 4 | -0.427 | -0.632 | 0.205 | 0.265 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 40 | 7 | 0.0 | -0.121 | 0.121 | 0.336 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 32 | 5 | -0.441 | -0.506 | 0.065 | 0.443 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 18 | 5 | 0.047 | 0.018 | 0.029 | 0.468 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 16 | 4 | -0.281 | -0.422 | 0.14 | 0.422 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 114 | 7 | -0.26 | -0.216 | -0.044 | 0.603 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 76 | 5 | -0.569 | -0.551 | -0.017 | 0.511 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.276 | 0.426 | 0.306 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.74 | 1.496 | 0.099 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 87 | 6 | -0.186 | -0.289 | 0.103 | 0.275 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 41 | 4 | -1.146 | -0.771 | -0.375 | 0.829 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 15 | 4 | -0.655 | -0.153 | -0.503 | 0.878 | HUKUM YOK (<20 gun) |
| TASIMA | T3 | 12 | 3 | -0.742 | -0.516 | -0.226 | 0.63 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 25 | -1.93 (-1.31) | -0.933 (-1.04) | -0.933 (-1.04) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 1.801 (1.47) | 2.061 (1.0) | 2.311 (1.12) | AYNI |
| IC_STOP | 74 / 74 | 0.479 (1.07) | 0.479 (1.07) | 0.479 (1.07) | AYNI |
| P2_ADAY | 74 / 65 | -0.074 (-0.11) | -0.194 (-0.26) | 0.056 (0.07) | AYNI |
| P2_DIP_DONUS | 23 / 22 | 1.852 (1.09) | 2.285 (1.34) | 2.535 (1.48) | AYNI |
| P3_HACIM_BEKLE | 94 / 94 | -0.677 (-4.61) | -0.677 (-4.61) | -0.427 (-2.91) | AYNI |
| P3_RADAR | 146 / 136 | -0.407 (-1.16) | -0.396 (-1.07) | -0.146 (-0.39) | AYNI |
| P3_SKOR_AL | 289 / 286 | -0.508 (-1.46) | -0.51 (-1.45) | -0.26 (-0.74) | AYNI |
| P4_HAZIRLIK | 260 / 249 | -0.067 (-0.25) | -0.043 (-0.15) | 0.207 (0.73) | AYNI |
| POZ_AZALT | 39 / 24 | -1.931 (-1.95) | -0.922 (-0.89) | -0.922 (-0.89) | AYNI |
| SEKTOR_ROTASYONU | 217 / 206 | 0.036 (0.09) | 0.144 (0.32) | 0.394 (0.87) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 15 / 15 | -0.992 (-1.19) | -0.992 (-1.19) | -0.742 (-0.89) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 55 | 20 | -0.923 (-1.54) | 43.4 | 0.026 (0.03) |
| ANA (10:15-12:30) | 327 | 32 | -0.652 (-2.27) | 44.0 | -0.45 (-1.32) |
| KAPANIS (>=15:45) | 217 | 31 | -0.258 (-0.75) | 46.6 | -0.2 (-0.43) |
| OGLE (12:30-15:45) | 287 | 32 | 0.224 (0.54) | 48.8 | 0.338 (0.6) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 75 | 30 | -1.183 (-3.83) | 24.1 | -2.485 (None) |
| OBV | 36 | 18 | -0.735 (-1.45) | 41.4 | 0.622 (None) |
| RS | 1 | 1 | None (None) | None | None (None) |
| SECTOR | 9 | 9 | -1.433 (-4.04) | 33.3 | -1.604 (None) |
| TREND | 156 | 25 | -0.579 (-2.49) | 42.5 | -0.871 (None) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-19, 95 islem gunu; gunluk alarm medyani 6, GUNLUK_OZET medyani 15.
- Ham kayit 3583, eventId tekrari 256, tekil 3327.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 44, son 30 gunde 4. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
