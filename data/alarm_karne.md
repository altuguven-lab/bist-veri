# Alarm Karnesi

Uretim: 2026-11-12T22:26 UTC | maliyet 0.25% (gidis-donus) | kriz esigi 2026-09-15 | BH q=0.1 | MIN_N=30

Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.

## Tur karnesi (net, XU100'e gore)

| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P4_HAZIRLIK | BILGI | YUKARI | 165 | 0.615 (1.82) | -0.131 | 0.365 (1.08 / 0.9) | 0.397 (0.86) | 0.226 (0.83) | 0.876 | 53.0 | -0.081 | **ADAY** |
| SEKTOR_ROTASYONU | BILGI | YUKARI | 131 | 0.856 (1.95) | -0.153 | 0.606 (1.38 / 1.72) | 0.624 (1.14) | 1.224 (1.53) | 1.357 | 53.4 | 0.078 | **ADAY** |
| P3_SKOR_AL | BILGI | YUKARI | 277 | -0.257 (-0.7) | -0.327 | -0.507 (-1.37 / -1.96) | -0.531 (-1.26) | -0.228 (-0.31) | 0.647 | 42.1 | -0.452 | **KENAR_YOK** |
| P3_RADAR | BILGI | YUKARI | 118 | -0.07 (-0.16) | -0.535 | -0.32 (-0.72 / -0.82) | -0.299 (-0.56) | 0.189 (0.4) | 0.327 | 52.9 | -0.539 | **KENAR_YOK** |
| P2_ADAY | BILGI | YUKARI | 67 | 0.177 (0.24) | -0.414 | -0.073 (-0.1 / -0.11) | -0.057 (-0.07) | 0.178 (0.18) | -0.655 | 53.1 | -1.357 | **KENAR_YOK** |
| POZ_AZALT | BILGI | ASAGI | 39 | -2.842 (-3.12) | -0.957 | -2.842 (-3.12 / -3.57) | -2.623 (-2.58) | -2.888 (-1.51) | -2.114 | 31.2 | 3.189 | **TERS** |
| ACIL_CIK | KRITIK | ASAGI | 27 | -2.637 (-1.51) | -0.419 | -2.637 (-1.51 / -1.44) | -1.545 (-0.85) | -3.325 (-1.2) | -0.46 | 50.0 | 1.963 | **YETERSIZ_ORNEK** |
| P3_HACIM_BEKLE | BILGI | YUKARI | 27 | None (None) | -0.786 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| IC_STOP | KRITIK | ASAGI | 21 | None (None) | 1.52 | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| P2_DIP_DONUS | BILGI | YUKARI | 17 | 3.375 (1.63) | -0.32 | 3.125 (1.51 / 1.25) | 3.088 (1.59) | 2.049 (1.09) | 4.469 | 60.0 | 2.645 | **YETERSIZ_ORNEK** |
| STOP_KIRILDI | KRITIK | ASAGI | 3 | -2.307 (-0.95) | -0.657 | -2.307 (-0.95 / -0.95) | -2.405 (-0.94) | 0.303 (None) | -1.517 | 33.3 | 4.503 | **YETERSIZ_ORNEK** |
| EKLEME_ADAYI | BILGI | YUKARI | 2 | None (None) | None | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |
| TASIMA | BILGI | YUKARI | 2 | None (None) | None | None (None / None) | None (None) | None (None) | None | None | None | **YETERSIZ_ORNEK** |

## Rejim kirilimi (net T+3)

| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |
|---|---|---|---|---|---|
| ACIL_CIK | 16 / -3.367 | 8 / -1.176 | 13 / -5.025 | 9 / -0.743 | 14.8 |
| EKLEME_ADAYI | 0 / None | 1 / None | 0 / None | 1 / None | 50.0 |
| IC_STOP | 0 / None | 0 / None | 0 / None | 0 / None | 81.0 |
| P2_ADAY | 28 / -0.946 | 36 / 0.606 | 16 / -0.605 | 48 / 0.104 | 74.6 |
| P2_DIP_DONUS | 12 / 4.276 | 3 / -1.478 | 6 / 2.579 | 9 / 3.489 | 41.2 |
| P3_HACIM_BEKLE | 0 / None | 0 / None | 0 / None | 0 / None | 88.9 |
| P3_RADAR | 44 / -0.653 | 60 / -0.075 | 37 / 0.906 | 67 / -0.996 | 64.4 |
| P3_SKOR_AL | 222 / -0.862 | 49 / 1.099 | 59 / 0.265 | 79 / 0.341 | 30.7 |
| P4_HAZIRLIK | 0 / None | 132 / 0.365 | 50 / 0.889 | 82 / 0.046 | 48.5 |
| POZ_AZALT | 32 / -2.842 | 0 / None | 6 / -4.095 | 19 / -1.261 | 30.8 |
| SEKTOR_ROTASYONU | 2 / -0.139 | 101 / 0.621 | 35 / 0.029 | 68 / 0.903 | 41.2 |
| STOP_KIRILDI | 3 / -2.307 | 0 / None | 0 / None | 0 / None | 33.3 |
| TASIMA | 0 / None | 0 / None | 0 / None | 0 / None | 100.0 |

## Tam gunler duyarliligi (net T+3)

Supheli eksik gunlerde taban alan olaylar cikarilinca sonuc degisiyor mu? Betimleyicidir; hukum kurallarina girmez. Isaret degisiyorsa ya da t belirgin kayiyorsa o turun hukmu eksik veriden etkileniyor olabilir.

| Tur | Olay (tum / tam gun) | Net T+3 tum (t_kume) | Net T+3 tam gun (t_kume) | Brut yon T+3 tam gun (t_kume) | Isaret |
|---|---|---|---|---|---|
| ACIL_CIK | 27 / 23 | -2.637 (-1.51) | -1.532 (-1.47) | -1.532 (-1.47) | AYNI |
| EKLEME_ADAYI | 2 / 1 | None (None) | None (None) | None (None) | - |
| IC_STOP | 21 / 21 | None (None) | None (None) | None (None) | - |
| P2_ADAY | 67 / 58 | -0.073 (-0.1) | -0.211 (-0.25) | 0.039 (0.05) | AYNI |
| P2_DIP_DONUS | 17 / 16 | 3.125 (1.51) | 3.835 (1.9) | 4.085 (2.03) | AYNI |
| P3_HACIM_BEKLE | 27 / 27 | None (None) | None (None) | None (None) | - |
| P3_RADAR | 118 / 108 | -0.32 (-0.72) | -0.295 (-0.62) | -0.045 (-0.09) | AYNI |
| P3_SKOR_AL | 277 / 274 | -0.507 (-1.37) | -0.509 (-1.36) | -0.259 (-0.69) | AYNI |
| P4_HAZIRLIK | 165 / 154 | 0.365 (1.08) | 0.445 (1.22) | 0.695 (1.91) | AYNI |
| POZ_AZALT | 39 / 24 | -2.842 (-3.12) | -2.223 (-2.63) | -2.223 (-2.63) | AYNI |
| SEKTOR_ROTASYONU | 131 / 120 | 0.606 (1.38) | 0.83 (1.81) | 1.08 (2.35) | AYNI |
| STOP_KIRILDI | 3 / 3 | -2.307 (-0.95) | -2.307 (-0.95) | -2.307 (-0.95) | AYNI |
| TASIMA | 2 / 2 | None (None) | None (None) | None (None) | - |

## Seans kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Alarm alis saatine gore; tum gecmis alarmlar. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| ACILIS (<10:15) | 52 | 20 | -1.137 (-1.68) | 39.1 | -0.042 (-0.04) |
| ANA (10:15-12:30) | 218 | 31 | -0.687 (-1.68) | 46.3 | -0.409 (-1.0) |
| KAPANIS (>=15:45) | 182 | 30 | -0.001 (-0.0) | 50.6 | -0.019 (-0.04) |
| OGLE (12:30-15:45) | 219 | 32 | 0.545 (1.04) | 50.0 | 0.606 (0.82) |

## Faktor kirilimi (giris adayi turleri havuzlu, net T+3 / T+5)

Sinyal barinda baskin skor bileseni; yalniz V163.1 (10.11.2026+) alarmlari tasir. Betimleyicidir, hukum vermez.

| Dilim | Olay | Sembol | Net T+3 ort (t_kume) | Isabet T+3 | Net T+5 ort (t_kume) |
|---|---|---|---|---|---|
| FLOW | 10 | 6 | None (None) | None | None (None) |
| OBV | 11 | 8 | None (None) | None | None (None) |
| SECTOR | 4 | 4 | None (None) | None | None (None) |
| TREND | 37 | 16 | None (None) | None | None (None) |

## Veri butunlugu

- Aralik 2026-07-07 - 2026-11-12, 90 islem gunu; gunluk alarm medyani 5.0, GUNLUK_OZET medyani 15.0.
- Ham kayit 2880, eventId tekrari 255, tekil 2625.
- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam 44, son 30 gunde 9. En yeni 15 (alarm/ozet): 2026-11-06 (29/2), 2026-10-28 (10/0), 2026-10-21 (0/0), 2026-10-20 (0/0), 2026-10-19 (0/0), 2026-10-16 (0/0), 2026-10-15 (0/0), 2026-10-14 (0/0), 2026-10-13 (0/0), 2026-10-12 (0/0), 2026-10-09 (0/0), 2026-10-08 (0/0), 2026-10-07 (0/0), 2026-10-06 (0/0), 2026-10-05 (0/1)
- Tamamen bos alanlar: v112wr
- Tanimsiz sinyal adlari: {'GERCEK_TEST': 1, 'GERCEK_TEST_KANAL_KONTROL': 1, 'GERCEK_TEST_P3_KONTROL': 1, '?': 5}
- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): 0
- Fiyati cekilemeyen: yok; bedelsiz duzeltmesi: yok

## Hukum kurallari (on kayit)

KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= 10 olan her donemde net T+3 > 0. TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < 30. KENAR_YOK zarar kaniti degildir.
