# Alarm Karnesi

Uretim: 2026-11-17T23:39 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 225 | 0.357 (1.12) | -0.259 | 0.107 (0.33 / 0.31) | 0.017 (0.04) | 0.11 (0.44) | 0.552 | 49.7 | -0.028 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 167 | 0.421 (0.94) | -0.164 | 0.171 (0.38 / 0.57) | 0.152 (0.29) | 1.105 (1.64) | 1.92 | 47.3 | 0.068 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 289 | -0.238 (-0.66) | -0.345 | -0.488 (-1.35 / -1.93) | -0.516 (-1.25) | -0.221 (-0.32) | 0.818 | 43.0 | -0.423 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 142 | -0.166 (-0.42) | -0.561 | -0.416 (-1.04 / -1.18) | -0.354 (-0.74) | 0.048 (0.13) | 0.618 | 52.5 | -0.395 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 72 | 0.186 (0.26) | -0.386 | -0.064 (-0.09 / -0.1) | -0.096 (-0.12) | 0.106 (0.13) | 0.334 | 53.7 | -1.183 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -1.931 (-1.95) | -0.957 | -1.931 (-1.95 / -2.65) | -1.792 (-1.69) | -2.524 (-1.41) | -2.114 | 43.6 | 2.393 | **KENAR_YOK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 75 | -0.643 (-7.86) | -0.457 | -0.893 (-10.92 / -1.87) | -1.575 (-9.67) | None (None) | None | 40.7 | 0.716 | **YETERSIZ_ORNEK** |
| IC_STOP | KRITIK | ASAGI | 68 | 1.504 (3.85) | 0.307 | 1.504 (3.85 / 2.88) | 1.653 (12.75) | None (None) | None | 71.4 | -0.854 | **YETERSIZ_ORNEK** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -2.1 (-1.33) | -0.393 | -2.1 (-1.33 / -1.26) | -1.23 (-0.76) | -3.123 (-1.25) | -0.46 | 51.9 | 1.646 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 21 | 2.644 (1.31) | -0.435 | 2.394 (1.19 / 1.05) | 2.283 (1.18) | 2.049 (1.09) | 3.765 | 52.9 | 2.069 | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 15 | 1.815 (None) | -1.036 | 1.565 (None / 1.34) | 1.861 (None) | None (None) | None | 100.0 | 1.342 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 3 | 0.886 (1.37) | 1.128 | 0.636 (0.99 / 0.99) | -0.003 (-0.0) | None (None) | None | 50.0 | -0.354 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 11 / -0.256 | 15 / -3.827 | 10 / -0.801 | 20.7 |
| EKLEME_ADAYI | 0 / None | 2 / 0.636 | 1 / None | 1 / None | 66.7 |
| IC_STOP | 0 / None | 21 / 1.504 | 9 / 0.872 | 12 / 1.979 | 85.3 |
| P2_ADAY | 28 / -0.946 | 39 / 0.569 | 19 / -0.489 | 48 / 0.104 | 76.4 |
| P2_DIP_DONUS | 12 / 4.276 | 5 / -2.121 | 7 / 2.209 | 10 / 2.524 | 52.4 |
| P3_HACIM_BEKLE | 0 / None | 27 / -0.893 | 8 / -1.431 | 19 / -0.667 | 94.7 |
| P3_RADAR | 44 / -0.653 | 74 / -0.275 | 44 / 0.645 | 74 / -1.047 | 70.4 |
| P3_SKOR_AL | 222 / -0.862 | 55 / 1.019 | 63 / 0.307 | 81 / 0.314 | 33.6 |
| P4_HAZIRLIK | 0 / None | 165 / 0.107 | 63 / 0.451 | 102 / -0.106 | 60.0 |
| POZ_AZALT | 32 / -2.842 | 7 / 2.236 | 8 / -2.822 | 24 / -0.429 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 129 / 0.175 | 39 / -0.051 | 92 / 0.265 | 49.7 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 2 / 1.565 | 2 / 1.565 | 0 / None | 100.0 |

## H14 haftalik ara bakis (V163, ON_KAYIT_H14.md)

Erken karar: en az 10 farkli gun, kumelenmis |t| > 2.6 ve plasebo p < 0.01 (ya da > 0.99). Gunluk deger bilgi icindir; RESMI bakis haftada bir (Cuma/Cumartesi) data/h14/ara_bakis.json'a yazilir.

| Iddia | Olay | Gun | Ort / fark % | t / perm p | Plasebo ort % | Plasebo p | Durum |
|---|---|---|---|---|---|---|---|
| H14a_giris_netT3 | 7 | 2 | -0.623 | -0.97 | -0.754 | 0.329 | **DEVAM (2/10 gun)** |
| H14c_cikis_yonT3 | 28 | 3 | 1.746 | 3.94 | 0.841 | 0.032 | **DEVAM (3/10 gun)** |
| H14b_hacim_tetigi | 21 | 1 | None | None | - | - | **DEVAM (1/10 gun)** |

## Plasebo karsilastirmasi (ayni gun, rastgele baska hisse)

Soru: tur, ayni gunlerde evrenden rastgele secilen baska hisselerden daha iyi mi? Gercek ile plasebo yakinsa sonuc sinyalden degil o gunlerin piyasa/sektor hareketinden gelir. p = plasebonun gercege esit ya da daha iyi cikma orani (kucuk = sinyal lehine). ayni gun, evrenden rastgele BASKA hisse, ayni yon ve ufuk; 2000 simulasyon, tohum sabit. Betimleyicidir; hukum kurallarina girmez. 20 farkli gunden azsa yorumlanmaz.

### Tum donem

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 29 | 23 | -0.393 | -0.181 | -0.212 | 0.705 | OLCULEBILIR |
| ACIL_CIK | T3 | 27 | 22 | -2.1 | -0.389 | -1.711 | 0.985 | OLCULEBILIR |
| IC_STOP | T1 | 57 | 4 | 0.307 | 0.274 | 0.032 | 0.441 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 21 | 2 | 1.504 | 0.787 | 0.717 | 0.098 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 72 | 34 | -0.136 | 0.182 | -0.318 | 0.898 | OLCULEBILIR |
| P2_ADAY | T3 | 67 | 32 | 0.186 | 0.834 | -0.648 | 0.914 | OLCULEBILIR |
| P2_DIP_DONUS | T1 | 21 | 14 | -0.185 | 0.101 | -0.285 | 0.734 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T3 | 17 | 12 | 2.644 | 0.551 | 2.093 | 0.021 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 62 | 4 | -0.207 | -0.272 | 0.065 | 0.385 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 27 | 2 | -0.643 | -0.799 | 0.156 | 0.368 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 136 | 38 | -0.311 | 0.113 | -0.423 | 0.987 | OLCULEBILIR |
| P3_RADAR | T3 | 118 | 36 | -0.166 | 0.506 | -0.672 | 0.976 | OLCULEBILIR |
| P3_SKOR_AL | T1 | 287 | 39 | -0.095 | 0.028 | -0.123 | 0.825 | OLCULEBILIR |
| P3_SKOR_AL | T3 | 277 | 37 | -0.238 | 0.077 | -0.315 | 0.915 | OLCULEBILIR |
| P4_HAZIRLIK | T1 | 208 | 24 | -0.009 | 0.089 | -0.098 | 0.751 | OLCULEBILIR |
| P4_HAZIRLIK | T3 | 165 | 22 | 0.357 | 0.43 | -0.074 | 0.594 | OLCULEBILIR |
| POZ_AZALT | T1 | 39 | 19 | -0.957 | 0.109 | -1.065 | 1.0 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 39 | 19 | -1.931 | 0.276 | -2.207 | 1.0 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 144 | 23 | 0.086 | 0.075 | 0.011 | 0.474 | OLCULEBILIR |
| SEKTOR_ROTASYONU | T3 | 131 | 21 | 0.421 | 0.352 | 0.069 | 0.408 | OLCULEBILIR |
| TASIMA | T1 | 12 | 3 | -0.786 | -0.245 | -0.541 | 0.847 | HUKUM YOK (<20 gun) |

### V163 sonrasi (2026-11-09+)

| Tur | Ufuk | Olay | Gun | Gercek yon ort % | Plasebo ort % | Fark | p | Durum |
|---|---|---|---|---|---|---|---|---|
| ACIL_CIK | T1 | 5 | 3 | 0.163 | -0.057 | 0.22 | 0.416 | HUKUM YOK (<20 gun) |
| IC_STOP | T1 | 57 | 4 | 0.307 | 0.279 | 0.028 | 0.456 | HUKUM YOK (<20 gun) |
| IC_STOP | T3 | 21 | 2 | 1.504 | 0.782 | 0.722 | 0.095 | HUKUM YOK (<20 gun) |
| P2_ADAY | T1 | 8 | 4 | 0.117 | -0.272 | 0.389 | 0.281 | HUKUM YOK (<20 gun) |
| P2_DIP_DONUS | T1 | 6 | 3 | -0.472 | -0.214 | -0.257 | 0.649 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T1 | 62 | 4 | -0.207 | -0.274 | 0.068 | 0.384 | HUKUM YOK (<20 gun) |
| P3_HACIM_BEKLE | T3 | 27 | 2 | -0.643 | -0.795 | 0.152 | 0.364 | HUKUM YOK (<20 gun) |
| P3_RADAR | T1 | 32 | 5 | -0.154 | -0.129 | -0.024 | 0.524 | HUKUM YOK (<20 gun) |
| P3_RADAR | T3 | 14 | 3 | -0.883 | -0.545 | -0.337 | 0.63 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T1 | 16 | 4 | -0.019 | 0.002 | -0.021 | 0.509 | HUKUM YOK (<20 gun) |
| P3_SKOR_AL | T3 | 6 | 2 | 0.609 | -0.268 | 0.877 | 0.287 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T1 | 76 | 5 | -0.252 | -0.174 | -0.078 | 0.632 | HUKUM YOK (<20 gun) |
| P4_HAZIRLIK | T3 | 33 | 3 | -0.677 | -0.634 | -0.043 | 0.545 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T1 | 7 | 2 | 0.701 | 0.278 | 0.423 | 0.314 | HUKUM YOK (<20 gun) |
| POZ_AZALT | T3 | 7 | 2 | 2.236 | 0.711 | 1.525 | 0.112 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T1 | 41 | 4 | -0.312 | -0.323 | 0.011 | 0.481 | HUKUM YOK (<20 gun) |
| SEKTOR_ROTASYONU | T3 | 28 | 2 | -1.181 | -0.852 | -0.329 | 0.742 | HUKUM YOK (<20 gun) |
| TASIMA | T1 | 12 | 3 | -0.786 | -0.224 | -0.562 | 0.859 | HUKUM YOK (<20 gun) |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 29 / 25 | -2.1 (-1.33) | -1.046 (-1.08) | -1.046 (-1.08) | AYNI |
| EKLEME_ADAYI | 3 / 2 | 0.636 (0.99) | None (None) | None (None) | - |
| IC_STOP | 68 / 68 | 1.504 (3.85) | 1.504 (3.85) | 1.504 (3.85) | AYNI |
| P2_ADAY | 72 / 63 | -0.064 (-0.09) | -0.193 (-0.24) | 0.057 (0.07) | AYNI |
| P2_DIP_DONUS | 21 / 20 | 2.394 (1.19) | 2.97 (1.48) | 3.22 (1.6) | AYNI |
| P3_HACIM_BEKLE | 75 / 75 | -0.893 (-10.92) | -0.893 (-10.92) | -0.643 (-7.86) | AYNI |
| P3_RADAR | 142 / 132 | -0.416 (-1.04) | -0.404 (-0.94) | -0.154 (-0.36) | AYNI |
| P3_SKOR_AL | 289 / 286 | -0.488 (-1.35) | -0.49 (-1.34) | -0.24 (-0.66) | AYNI |
| P4_HAZIRLIK | 225 / 214 | 0.107 (0.33) | 0.151 (0.44) | 0.401 (1.17) | AYNI |
| POZ_AZALT | 39 / 24 | -1.931 (-1.95) | -0.922 (-0.89) | -0.922 (-0.89) | AYNI |
| SEKTOR_ROTASYONU | 167 / 156 | 0.171 (0.38) | 0.303 (0.62) | 0.553 (1.13) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 15 / 15 | 1.565 (None) | 1.565 (None) | 1.815 (None) | AYNI |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 53 | 20 | -0.98 (-1.6) | 42.3 | -0.082 (-0.07) |
| ANA (10:15-12:30) | 291 | 32 | -0.651 (-1.84) | 47.2 | -0.421 (-1.12) |
| KAPANIS (>=15:45) | 210 | 31 | -0.156 (-0.42) | 48.9 | -0.067 (-0.14) |
| OGLE (12:30-15:45) | 270 | 32 | 0.305 (0.64) | 47.9 | 0.492 (0.81) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 41 | 22 | -1.692 (-4.31) | 30.0 | None (None) |
| OBV | 30 | 14 | 0.039 (0.11) | 63.6 | None (None) |
| SECTOR | 6 | 6 | -1.115 (None) | 50.0 | None (None) |
| TREND | 138 | 24 | -1.065 (-5.42) | 35.1 | None (None) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-17, 93 islem gunu; gunluk alarm medyani 6, GUNLUK_OZET medyani 15.
- Ham kayit 3335, eventId tekrari 256, tekil 3079.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 44, son 30 gunde 5. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
