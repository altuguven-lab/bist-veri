# Alarm Karnesi

Uretim: 2026-11-02T23:41 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | IZLEME | YUKARI | 88 | 0.993 (1.69) | -0.036 | 0.743 (1.26 / 1.11) | 0.484 (0.65) | 0.129 (0.21) | 1.072 | 59.4 | 0.37 | **ADAY** |
| SEKTOR_ROTASYONU | IZLEME | YUKARI | 81 | 0.444 (0.99) | -0.176 | 0.194 (0.43 / 0.53) | -0.167 (-0.35) | 0.356 (0.35) | 0.323 | 50.7 | -0.323 | **ADAY** |
| P3_SKOR_AL | ISLEM | YUKARI | 239 | -0.553 (-1.41) | -0.407 | -0.803 (-2.05 / -2.98) | -0.864 (-1.93) | -0.481 (-0.63) | 0.702 | 38.7 | -0.477 | **KENAR_YOK** |
| P3_RADAR | IZLEME | YUKARI | 79 | -0.597 (-1.26) | -0.65 | -0.847 (-1.79 / -1.87) | -1.073 (-1.81) | -0.032 (-0.11) | 0.591 | 46.4 | -1.151 | **KENAR_YOK** |
| P2_ADAY | ISLEM | YUKARI | 45 | -0.577 (-0.64) | -0.633 | -0.827 (-0.92 / -0.96) | -1.099 (-1.03) | -0.907 (-1.14) | -0.452 | 53.7 | -1.759 | **KENAR_YOK** |
| POZ_AZALT | KRITIK | ASAGI | 32 | -2.842 (-3.12) | -1.319 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 21 | -2.69 (-1.3) | -0.153 | -2.69 (-1.3 / -1.23) | -1.258 (-0.59) | -3.385 (-1.02) | -0.621 | 50.0 | 1.969 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | ISLEM | YUKARI | 15 | 4.085 (2.03) | -0.32 | 3.835 (1.9 / 1.48) | 3.844 (2.08) | 2.824 (1.64) | 4.469 | 64.3 | 4.04 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 4 / 0.022 | 11 / -5.012 | 7 / -1.055 | 14.3 |
| P2_ADAY | 28 / -0.946 | 13 / -0.57 | 12 / -1.372 | 29 / -0.601 | 64.4 |
| P2_DIP_DONUS | 12 / 4.276 | 2 / 1.19 | 5 / 4.458 | 9 / 3.489 | 33.3 |
| P3_RADAR | 44 / -0.653 | 25 / -1.189 | 24 / -0.145 | 45 / -1.222 | 57.0 |
| P3_SKOR_AL | 222 / -0.862 | 13 / 0.194 | 40 / -0.435 | 62 / 0.139 | 22.6 |
| P4_HAZIRLIK | 0 / None | 69 / 0.743 | 26 / 1.513 | 43 / 0.277 | 31.8 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 18.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 67 / 0.204 | 23 / -0.742 | 46 / 0.662 | 19.8 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-02, 82 islem gunu; gunluk alarm medyani 3.5, GUNLUK_OZET medyani 14.0.
- Ham kayit 2127, eventId tekrari 196, tekil 1931.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 41, son 30 gunde 14. En yeni 15 (alarm/ozet): 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1), 2026-10-02 (0/1)
- Tamamen bos alanlar: v112wr, pozsebep
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
