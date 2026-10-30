# H8 Kesif Bataryasi

Uretim 2026-10-30T08:13 UTC | on kayit `ad6ad73645164dd6` | deneme no 1 | BH q=0.1, 15 test

Salt olcum, tavsiye degildir. X: aylik, evren ortalamasina gore net (yuzde puan). E: olay penceresi, evrene gore. T: XU100 gun/ay getiri farki. En iyi etiket ADAY; aday ancak ayri on kayitla golgeye alinir.

| Test | Beklenen | IS ort (t, n) | OOS ort (t, n) | OOS p | BH | Hukum |
|---|---|---|---|---|---|---|
| X1_temettu_verimi | + | -0.2194 (-0.59, 77) | 0.2049 (0.38, 42) | 0.7039 | hayir | **KENAR_YOK** |
| X2_1ay_donus | + | -0.2106 (-0.65, 77) | 0.0074 (0.01, 42) | 0.992 | hayir | **KENAR_YOK** |
| X3_52h_zirve | + | 0.586 (1.67, 77) | 0.6438 (1.26, 42) | 0.2077 | hayir | **KENAR_YOK** |
| X4_momentum_6_1 | + | 0.6179 (1.03, 77) | 0.6955 (1.27, 42) | 0.2041 | hayir | **KENAR_YOK** |
| X5_kucuk_buyukluk | + | 2.9076 (3.91, 77) | 0.4218 (0.64, 42) | 0.5222 | hayir | **KENAR_YOK** |
| X6_likidite_primi | + | 1.2547 (2.37, 77) | 1.5096 (2.69, 42) | 0.0071 | hayir | **KENAR_YOK** |
| X7_dusuk_beta | + | -0.4342 (-1.1, 77) | 0.6718 (1.02, 42) | 0.3077 | hayir | **KENAR_YOK** |
| X8_sektor_momentum | + | 0.6305 (1.22, 77) | 0.3881 (0.8, 42) | 0.4237 | hayir | **KENAR_YOK** |
| E1_bedelsiz_oncesi | + | 8.33 (1.62, 57) | 1.659 (1.11, 51) | 0.267 | hayir | **KENAR_YOK** |
| E2_bedelsiz_sonrasi | - | 4.396 (1.03, 58) | 0.741 (0.26, 51) | 0.7949 | hayir | **KENAR_YOK** |
| E3_temettu_oncesi | + | 0.009 (0.02, 381) | 1.172 (2.34, 230) | 0.0193 | hayir | **KENAR_YOK** |
| T1_ay_donumu | + | 0.0804 (1.03, 576) | 0.0678 (0.76, 408) | 0.4473 | hayir | **KENAR_YOK** |
| T2_tatil_oncesi | + | -0.0251 (-0.17, 73) | -0.3323 (-2.12, 70) | 0.034 | hayir | **KENAR_YOK** |
| T4_pazartesi | - | 0.0316 (0.38, 603) | 0.1389 (1.37, 425) | 0.1707 | hayir | **KENAR_YOK** |
| T3_kasim_nisan | + | 0.7562 (0.6, 72) | 0.6271 (0.37, 52) | 0.7114 | hayir | **KENAR_YOK** |

Veri: {'evren': 95, 'fiyatli': 95, 'hata': {}, 'bedelsiz_olay': 253, 'temettu_olay': 1154, 'xu_ilk': '2005-01-03'}

Test edilemeyenler (veri yok): endeks degisiklikleri, analist revizyonlari, yabanci payi/takas/AKD, VIOP acik pozisyon ve aciga satis gecmisi, fon portfoy dagilimlari, haber/duygu, opsiyon, emir defteri.
