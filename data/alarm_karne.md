# Alarm Karnesi

Uretim: 2026-11-06T21:45 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 124 | 0.646 (1.46) | -0.097 | 0.396 (0.9 / 0.8) | 0.269 (0.46) | 0.3 (0.75) | 1.072 | 55.0 | 0.001 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 98 | 0.822 (1.78) | -0.003 | 0.572 (1.24 / 1.55) | 0.314 (0.54) | 0.426 (0.57) | 0.323 | 53.4 | -0.071 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 269 | -0.43 (-1.07) | -0.344 | -0.68 (-1.7 / -2.5) | -0.736 (-1.61) | -0.52 (-0.7) | 0.702 | 39.9 | -0.483 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 99 | -0.195 (-0.38) | -0.545 | -0.445 (-0.87 / -1.04) | -0.606 (-0.99) | -0.263 (-0.86) | 0.591 | 50.6 | -0.699 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 60 | 0.175 (0.18) | -0.422 | -0.075 (-0.08 / -0.09) | -0.144 (-0.13) | -0.752 (-1.07) | -0.452 | 56.2 | -1.614 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 32 | -2.842 (-3.12) | -1.319 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 24 | -2.55 (-1.29) | -0.265 | -2.55 (-1.29 / -1.23) | -1.174 (-0.58) | -2.776 (-0.95) | -0.621 | 52.4 | 1.724 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 15 | 3.375 (1.63) | -0.32 | 3.125 (1.51 / 1.25) | 3.088 (1.59) | 2.049 (1.09) | 4.469 | 60.0 | 3.051 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 5 / 0.064 | 11 / -5.012 | 8 / -0.894 | 12.5 |
| P2_ADAY | 28 / -0.946 | 20 / 1.145 | 12 / -1.372 | 36 / 0.358 | 73.3 |
| P2_DIP_DONUS | 12 / 4.276 | 3 / -1.478 | 6 / 2.579 | 9 / 3.489 | 33.3 |
| P3_RADAR | 44 / -0.653 | 39 / -0.21 | 28 / 0.543 | 55 / -0.948 | 61.6 |
| P3_SKOR_AL | 222 / -0.862 | 21 / 1.237 | 43 / -0.211 | 67 / 0.355 | 29.4 |
| P4_HAZIRLIK | 0 / None | 100 / 0.396 | 32 / 1.452 | 68 / -0.101 | 37.9 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 18.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 86 / 0.588 | 26 / -0.5 | 62 / 1.021 | 26.5 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-06, 86 islem gunu; gunluk alarm medyani 4.0, GUNLUK_OZET medyani 15.0.
- Ham kayit 2604, eventId tekrari 434, tekil 2170.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 41, son 30 gunde 12. En yeni 15 (alarm/ozet): 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1), 2026-10-02 (0/1)
- Tamamen bos alanlar: v112wr, pozsebep
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5, 'EKLEME_ADAYI': 1}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
