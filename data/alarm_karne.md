# Alarm Karnesi

Uretim: 2026-11-10T00:26 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 132 | 0.653 (1.6) | -0.061 | 0.403 (0.99 / 0.86) | 0.222 (0.41) | 0.245 (0.65) | 0.988 | 54.6 | -0.132 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 103 | 0.964 (2.08) | 0.046 | 0.714 (1.54 / 1.95) | 0.579 (0.94) | 0.892 (1.06) | 0.59 | 54.3 | 0.055 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 271 | -0.372 (-0.95) | -0.341 | -0.622 (-1.59 / -2.31) | -0.66 (-1.48) | -0.52 (-0.7) | 0.702 | 40.2 | -0.474 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 104 | -0.175 (-0.36) | -0.556 | -0.425 (-0.87 / -1.0) | -0.516 (-0.87) | -0.263 (-0.86) | 0.591 | 50.6 | -0.569 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 64 | 0.166 (0.19) | -0.369 | -0.084 (-0.1 / -0.11) | -0.106 (-0.1) | -0.752 (-1.07) | -0.452 | 54.7 | -1.58 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 32 | -2.842 (-3.12) | -1.319 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 24 | -2.792 (-1.47) | -0.509 | -2.792 (-1.47 / -1.4) | -1.6 (-0.8) | -2.776 (-0.95) | -0.621 | 50.0 | 1.837 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 15 | 3.375 (1.63) | -0.32 | 3.125 (1.51 / 1.25) | 3.088 (1.59) | 2.049 (1.09) | 4.469 | 60.0 | 3.051 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | TANIMSIZ | BELIRSIZ | 1 | None (None) | None | None (None / None) | None (None) | None (None) | None | None | None | **YON_TANIMSIZ** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 6 / -1.258 | 12 / -5.25 | 8 / -0.894 | 12.5 |
| EKLEME_ADAYI | 0 / None | 0 / None | 0 / None | 0 / None | 0.0 |
| P2_ADAY | 28 / -0.946 | 25 / 0.882 | 13 / -1.466 | 40 / 0.365 | 75.0 |
| P2_DIP_DONUS | 12 / 4.276 | 3 / -1.478 | 6 / 2.579 | 9 / 3.489 | 33.3 |
| P3_RADAR | 44 / -0.653 | 43 / -0.192 | 28 / 0.543 | 59 / -0.885 | 63.5 |
| P3_SKOR_AL | 222 / -0.862 | 29 / 1.211 | 45 / -0.106 | 73 / 0.391 | 29.9 |
| P4_HAZIRLIK | 0 / None | 108 / 0.403 | 36 / 1.27 | 72 / -0.03 | 39.4 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 18.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 90 / 0.733 | 30 / 0.08 | 62 / 1.021 | 29.1 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-09, 87 islem gunu; gunluk alarm medyani 4, GUNLUK_OZET medyani 15.
- Ham kayit 2472, eventId tekrari 256, tekil 2216.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 42, son 30 gunde 10. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr, pozsebep
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5, 'EKLEME_ADAYI': 1}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
