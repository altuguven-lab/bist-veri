# Alarm Karnesi

Uretim: 2026-10-30T21:02 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P3_SKOR_AL | ISLEM | YUKARI | 269 | -0.603 (-1.7) | -0.409 | -0.853 (-2.4 / -3.48) | -0.888 (-2.19) | -0.515 (-0.77) | 0.64 | 38.2 | -0.493 | **KENAR_YOK** |
| P4_HAZIRLIK | IZLEME | YUKARI | 210 | -0.057 (-0.17) | -0.211 | -0.307 (-0.9 / -0.98) | -0.387 (-0.99) | -0.457 (-0.99) | -0.483 | 47.9 | -0.484 | **KENAR_YOK** |
| P3_RADAR | IZLEME | YUKARI | 159 | -0.358 (-1.25) | -0.454 | -0.608 (-2.12 / -2.21) | -0.856 (-2.53) | 0.129 (0.36) | 0.719 | 46.3 | -0.729 | **KENAR_YOK** |
| SEKTOR_ROTASYONU | IZLEME | YUKARI | 154 | 0.152 (0.61) | -0.146 | -0.098 (-0.39 / -0.39) | -0.457 (-1.57) | -0.154 (-0.29) | -0.005 | 48.9 | 0.006 | **KENAR_YOK** |
| P2_ADAY | ISLEM | YUKARI | 82 | -0.519 (-0.98) | -0.493 | -0.769 (-1.46 / -1.53) | -0.798 (-1.3) | -0.688 (-1.6) | -0.493 | 48.7 | -0.916 | **KENAR_YOK** |
| POZ_AZALT | KRITIK | ASAGI | 32 | -2.842 (-3.12) | -1.319 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.829 (-1.12) | -0.502 | -1.829 (-1.12 / -1.07) | -1.523 (-0.89) | -1.885 (-0.7) | -0.095 | 44.4 | 1.1 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | ISLEM | YUKARI | 22 | 2.161 (1.3) | -0.283 | 1.911 (1.15 / 1.05) | 1.879 (1.22) | 1.827 (1.34) | 4.357 | 47.6 | 1.807 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 11 / 0.409 | 15 / -3.51 | 10 / -0.544 | 24.1 |
| P2_ADAY | 28 / -0.946 | 48 / -0.665 | 19 / -1.07 | 57 / -0.668 | 69.5 |
| P2_DIP_DONUS | 12 / 4.276 | 9 / -1.241 | 7 / 2.733 | 14 / 1.5 | 31.8 |
| P3_RADAR | 44 / -0.653 | 103 / -0.588 | 48 / -0.307 | 99 / -0.754 | 61.6 |
| P3_SKOR_AL | 222 / -0.862 | 40 / -0.806 | 53 / -0.646 | 76 / -0.123 | 29.0 |
| P4_HAZIRLIK | 0 / None | 190 / -0.307 | 68 / -0.269 | 122 / -0.329 | 40.0 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 18.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 139 / -0.098 | 48 / -0.752 | 93 / 0.239 | 32.5 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-10-30, 81 islem gunu; gunluk alarm medyani 13, GUNLUK_OZET medyani 23.
- Ham kayit 3155, eventId tekrari 373, tekil 2782.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 40, son 30 gunde 2. En yeni 15 (alarm/ozet): 2026-10-28 (10/0), 2026-10-07 (25/0), 2026-09-18 (3/4), 2026-09-17 (0/0), 2026-09-16 (0/0), 2026-09-15 (0/0), 2026-09-14 (0/0), 2026-09-11 (0/0), 2026-09-10 (0/0), 2026-09-09 (0/0), 2026-09-08 (0/0), 2026-09-07 (0/0), 2026-09-04 (6/0), 2026-09-03 (3/1), 2026-09-02 (4/24)
- Tamamen bos alanlar: v112wr, pozsebep
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
