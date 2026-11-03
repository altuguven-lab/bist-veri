# Alarm Karnesi

Uretim: 2026-11-03T22:01 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | IZLEME | YUKARI | 100 | 0.948 (1.87) | -0.005 | 0.698 (1.37 / 1.19) | 0.605 (0.94) | 0.332 (0.59) | 1.072 | 60.0 | 0.371 | **ADAY** |
| SEKTOR_ROTASYONU | IZLEME | YUKARI | 88 | 0.442 (1.03) | 0.023 | 0.192 (0.45 / 0.53) | -0.106 (-0.23) | 0.32 (0.35) | 0.323 | 50.0 | -0.353 | **ADAY** |
| P3_SKOR_AL | ISLEM | YUKARI | 243 | -0.563 (-1.46) | -0.407 | -0.813 (-2.11 / -3.06) | -0.887 (-2.01) | -0.481 (-0.63) | 0.702 | 38.9 | -0.489 | **KENAR_YOK** |
| P3_RADAR | IZLEME | YUKARI | 83 | -0.517 (-1.22) | -0.65 | -0.767 (-1.81 / -1.88) | -0.971 (-1.82) | -0.222 (-0.62) | 0.591 | 48.7 | -0.83 | **KENAR_YOK** |
| P2_ADAY | ISLEM | YUKARI | 48 | -0.513 (-0.61) | -0.633 | -0.763 (-0.91 / -0.94) | -0.931 (-0.93) | -0.907 (-1.14) | -0.452 | 52.3 | -1.733 | **KENAR_YOK** |
| POZ_AZALT | KRITIK | ASAGI | 32 | -2.842 (-3.12) | -1.319 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 21 | -2.55 (-1.29) | -0.153 | -2.55 (-1.29 / -1.23) | -1.174 (-0.58) | -3.017 (-0.94) | -0.621 | 52.4 | 1.724 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | ISLEM | YUKARI | 15 | 4.085 (2.03) | -0.32 | 3.835 (1.9 / 1.48) | 3.844 (2.08) | 2.824 (1.64) | 4.469 | 64.3 | 4.04 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 5 / 0.064 | 11 / -5.012 | 8 / -0.894 | 14.3 |
| P2_ADAY | 28 / -0.946 | 16 / -0.444 | 12 / -1.372 | 32 / -0.535 | 66.7 |
| P2_DIP_DONUS | 12 / 4.276 | 2 / 1.19 | 5 / 4.458 | 9 / 3.489 | 33.3 |
| P3_RADAR | 44 / -0.653 | 34 / -0.914 | 26 / -0.223 | 52 / -1.039 | 57.8 |
| P3_SKOR_AL | 222 / -0.862 | 17 / -0.186 | 42 / -0.475 | 64 / 0.085 | 23.9 |
| P4_HAZIRLIK | 0 / None | 80 / 0.698 | 29 / 1.485 | 51 / 0.251 | 32.0 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 18.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 70 / 0.201 | 23 / -0.742 | 49 / 0.63 | 21.6 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-03, 83 islem gunu; gunluk alarm medyani 4, GUNLUK_OZET medyani 14.
- Ham kayit 2262, eventId tekrari 263, tekil 1999.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 41, son 30 gunde 14. En yeni 15 (alarm/ozet): 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1), 2026-10-02 (0/1)
- Tamamen bos alanlar: v112wr, pozsebep
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
