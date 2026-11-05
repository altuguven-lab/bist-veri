# Alarm Karnesi

Uretim: 2026-11-05T22:17 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 117 | 0.797 (1.68) | -0.099 | 0.547 (1.15 / 1.01) | 0.27 (0.41) | 0.233 (0.56) | 1.072 | 56.8 | 0.209 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 92 | 0.639 (1.38) | -0.003 | 0.389 (0.84 / 1.06) | -0.13 (-0.32) | 0.34 (0.44) | 0.323 | 51.9 | -0.168 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 265 | -0.563 (-1.46) | -0.35 | -0.813 (-2.11 / -3.06) | -0.887 (-2.01) | -0.52 (-0.7) | 0.702 | 38.9 | -0.489 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 95 | -0.521 (-1.24) | -0.592 | -0.771 (-1.84 / -1.92) | -0.965 (-1.83) | -0.242 (-0.79) | 0.591 | 48.1 | -0.785 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 58 | -0.461 (-0.56) | -0.347 | -0.711 (-0.87 / -0.89) | -0.881 (-0.9) | -0.824 (-1.17) | -0.452 | 53.3 | -1.733 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 32 | -2.842 (-3.12) | -1.319 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 22 | -2.55 (-1.29) | -0.265 | -2.55 (-1.29 / -1.23) | -1.174 (-0.58) | -2.776 (-0.95) | -0.621 | 52.4 | 1.724 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 15 | 3.375 (1.63) | -0.32 | 3.125 (1.51 / 1.25) | 3.088 (1.59) | 2.824 (1.64) | 4.469 | 60.0 | 3.051 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 5 / 0.064 | 11 / -5.012 | 8 / -0.894 | 13.6 |
| P2_ADAY | 28 / -0.946 | 17 / -0.325 | 12 / -1.372 | 33 / -0.471 | 72.4 |
| P2_DIP_DONUS | 12 / 4.276 | 3 / -1.478 | 6 / 2.579 | 9 / 3.489 | 33.3 |
| P3_RADAR | 44 / -0.653 | 35 / -0.919 | 26 / -0.223 | 53 / -1.04 | 61.1 |
| P3_SKOR_AL | 222 / -0.862 | 17 / -0.186 | 42 / -0.475 | 64 / 0.085 | 29.1 |
| P4_HAZIRLIK | 0 / None | 88 / 0.547 | 29 / 1.485 | 59 / 0.086 | 36.8 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 18.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 79 / 0.403 | 24 / -0.793 | 57 / 0.887 | 25.0 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-05, 85 islem gunu; gunluk alarm medyani 4, GUNLUK_OZET medyani 15.
- Ham kayit 2542, eventId tekrari 403, tekil 2139.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 41, son 30 gunde 13. En yeni 15 (alarm/ozet): 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1), 2026-10-02 (0/1)
- Tamamen bos alanlar: v112wr, pozsebep
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
