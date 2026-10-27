# Alarm Karnesi

Uretim: 2026-10-27T20:58 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P3_SKOR_AL | ISLEM | YUKARI | 269 | -0.603 (-1.7) | -0.412 | -0.853 (-2.4 / -3.48) | -0.509 (-0.76) | 0.64 | 38.2 | -0.493 | **KENAR_YOK** |
| P4_HAZIRLIK | IZLEME | YUKARI | 207 | -0.256 (-0.9) | -0.237 | -0.506 (-1.77 / -1.7) | -0.397 (-0.85) | -0.48 | 46.7 | -0.812 | **KENAR_YOK** |
| P3_RADAR | IZLEME | YUKARI | 158 | -0.288 (-1.02) | -0.475 | -0.538 (-1.91 / -1.96) | 0.203 (0.54) | 0.759 | 46.9 | -0.586 | **KENAR_YOK** |
| SEKTOR_ROTASYONU | IZLEME | YUKARI | 151 | 0.148 (0.56) | -0.162 | -0.102 (-0.39 / -0.39) | -0.152 (-0.28) | -0.05 | 50.0 | 0.125 | **KENAR_YOK** |
| P2_ADAY | ISLEM | YUKARI | 81 | -0.519 (-0.98) | -0.538 | -0.769 (-1.46 / -1.53) | -0.646 (-1.48) | -0.493 | 48.7 | -0.916 | **KENAR_YOK** |
| POZ_AZALT | KRITIK | ASAGI | 32 | -2.842 (-3.12) | -1.319 | -2.842 (-3.12 / -3.57) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 29 | -1.962 (-1.16) | -0.508 | -1.962 (-1.16 / -1.11) | -1.885 (-0.7) | -0.434 | 42.3 | 1.253 | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | ISLEM | YUKARI | 21 | 2.161 (1.3) | -0.283 | 1.911 (1.15 / 1.04) | 1.827 (1.34) | 4.357 | 47.6 | 1.807 | **YETERSIZ_ORNEK** |
| P1_KALITELI_AL | ISLEM | YUKARI | 9 | -0.904 (-1.21) | -0.932 | -1.154 (-1.54 / -1.54) | -1.759 (-1.34) | -3.158 | 25.0 | -0.516 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 10 / 0.286 | 14 / -3.878 | 10 / -0.544 | 24.1 |
| P1_KALITELI_AL | 7 / -1.26 | 1 / None | 0 / None | 0 / None | 11.1 |
| P2_ADAY | 28 / -0.946 | 48 / -0.665 | 19 / -1.07 | 57 / -0.668 | 70.4 |
| P2_DIP_DONUS | 12 / 4.276 | 9 / -1.241 | 7 / 2.733 | 14 / 1.5 | 33.3 |
| P3_RADAR | 44 / -0.653 | 101 / -0.487 | 47 / -0.233 | 98 / -0.684 | 62.7 |
| P3_SKOR_AL | 222 / -0.862 | 40 / -0.806 | 53 / -0.646 | 76 / -0.123 | 29.0 |
| P4_HAZIRLIK | 0 / None | 182 / -0.506 | 60 / -0.865 | 122 / -0.329 | 40.6 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 18.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 132 / -0.102 | 43 / -0.784 | 91 / 0.22 | 33.1 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-10-27, 79 islem gunu; gunluk alarm medyani 13, GUNLUK_OZET medyani 23.
- Ham kayit 3028, eventId tekrari 309, tekil 2719.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 39, son 30 gunde 1. En yeni 15 (alarm/ozet): 2026-10-07 (25/0), 2026-09-18 (3/4), 2026-09-17 (0/0), 2026-09-16 (0/0), 2026-09-15 (0/0), 2026-09-14 (0/0), 2026-09-11 (0/0), 2026-09-10 (0/0), 2026-09-09 (0/0), 2026-09-08 (0/0), 2026-09-07 (0/0), 2026-09-04 (6/0), 2026-09-03 (3/1), 2026-09-02 (4/24), 2026-09-01 (2/26)
- Tamamen bos alanlar: v112wr, pozsebep
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 5
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
