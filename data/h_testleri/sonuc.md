# H1-H3 Hipotez Testleri

Uretim 2026-10-27T13:18 UTC | on kayit SHA-256 `f7be58b570c7aa58` | deneme no 1 | maliyet 0.25% | t esigi 2.39 (Bonferroni)

Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H1_H3.md'de; bu rapor yalniz uygular.

## Hukumler

| Hipotez | Birincil metrik | IS ort (t) | OOS ort (t) | Taze donem ort (t) | Hukum |
|---|---|---|---|---|---|
| H1 | sektor sepetine gore net, 5 gun | -0.3009 (-4.04) | -0.2009 (-1.65) | -0.415 (-1.24) | **ELENDI** |
| H3 | XU100'e gore net, 10 gun | 0.8972 (0.6) | -3.5853 (-2.57) | -1.5112 (-0.64) | **ELENDI** |
| H2 | Kapanis girisi avantaji (puan) | - | 0.123 (0.98), n=670 | - | **ZAYIF** |

## H1 kriterleri

- K1_oos_ort_pozitif: HAYIR
- K2_oos_t: HAYIR
- K3_yillarin_60pct_pozitif: HAYIR
- K4_sektor_cikarma: HAYIR
- K5_is_ort_pozitif: HAYIR
- Sektor cikarma OOS ortalamalari: {'Banka': -0.1861, 'Enerji': -0.1416, 'GYO': -0.2332, 'Holding': -0.1674, 'Icecek': -0.2006, 'Iletisim': -0.1987, 'Insaat': -0.2167, 'Madencilik': -0.2652, 'Otomotiv': -0.1397, 'Perakende': -0.2033, 'Sanayi': -0.2073, 'Ulastirma': -0.1695}
- Yillik ortalamalar: {2015: 0.855, 2016: 0.142, 2017: -0.442, 2018: -0.252, 2019: -0.327, 2020: -0.046, 2021: -0.561, 2022: -0.643, 2023: -0.479, 2024: 0.079, 2025: -0.441, 2026: 0.273}
- XU100'e gore net: OOS {'n': 850, 'ort': -0.0635, 't': -0.66}
- evren ortalamasina gore net: OOS {'n': 850, 'ort': -0.2153, 't': -2.41}
- Temettu duzeltmeli (saglamlik) OOS: {'n': 850, 'ort': -0.2346, 't': -1.91}

## H3 kriterleri

- K1_oos_ort_pozitif: HAYIR
- K2_oos_t: HAYIR
- K3_yillarin_60pct_pozitif: HAYIR
- K4_sektor_cikarma: HAYIR
- K5_is_ort_pozitif: EVET
- Sektor cikarma OOS ortalamalari: {'Banka': np.float64(-3.9801), 'Enerji': np.float64(-2.9012), 'GYO': np.float64(-4.3385), 'Holding': np.float64(-3.5003), 'Icecek': np.float64(-3.024), 'Iletisim': np.float64(-3.5853), 'Insaat': np.float64(-3.6121), 'Madencilik': np.float64(-3.941), 'Otomotiv': np.float64(-3.1862), 'Perakende': np.float64(-3.4736), 'Sanayi': np.float64(-3.3716), 'Ulastirma': np.float64(-3.5668)}
- Yillik ortalamalar: {2015: -11.108, 2016: 2.221, 2017: 2.818, 2018: -1.573, 2019: 0.025, 2020: 9.356, 2021: -0.556, 2022: -5.621, 2023: -2.487, 2024: -4.071, 2025: -0.713, 2026: -6.804}
- sektor sepetine gore net: OOS {'n': 44, 'kume': 35, 'ort': np.float64(-3.4033), 't': np.float64(-2.7)}
- Temettu duzeltmeli (saglamlik) OOS: {'n': 40, 'kume': 32, 'ort': np.float64(-4.0039), 't': np.float64(-2.61)}

## H1 saglamlik izgarasi (OOS sektore gore net; parametre secimi icin KULLANILMAZ)

| geri | dilim | tutma | n | ort | t |
|---|---|---|---|---|---|
| 3 | 0.1 | 3 | 850 | -0.362 | -3.2 |
| 3 | 0.1 | 5 | 850 | -0.3251 | -1.99 |
| 3 | 0.1 | 10 | 850 | -0.3763 | -1.52 |
| 3 | 0.2 | 3 | 850 | -0.3051 | -3.89 |
| 3 | 0.2 | 5 | 850 | -0.2444 | -2.07 |
| 3 | 0.2 | 10 | 850 | -0.3544 | -1.87 |
| 3 | 0.3 | 3 | 850 | -0.3253 | -5.19 |
| 3 | 0.3 | 5 | 850 | -0.2887 | -3.12 |
| 3 | 0.3 | 10 | 850 | -0.3912 | -2.56 |
| 5 | 0.1 | 3 | 850 | -0.2715 | -2.42 |
| 5 | 0.1 | 5 | 850 | -0.2088 | -1.2 |
| 5 | 0.1 | 10 | 850 | -0.2385 | -0.79 |
| 5 | 0.2 | 3 | 850 | -0.2481 | -3.13 |
| 5 | 0.2 | 5 | 850 | -0.2009 | -1.65 |
| 5 | 0.2 | 10 | 850 | -0.3366 | -1.51 |
| 5 | 0.3 | 3 | 850 | -0.234 | -3.74 |
| 5 | 0.3 | 5 | 850 | -0.1914 | -1.96 |
| 5 | 0.3 | 10 | 850 | -0.3388 | -1.93 |
| 10 | 0.1 | 3 | 850 | -0.2326 | -2.1 |
| 10 | 0.1 | 5 | 850 | -0.1937 | -1.11 |
| 10 | 0.1 | 10 | 850 | -0.301 | -0.9 |
| 10 | 0.2 | 3 | 850 | -0.2854 | -3.67 |
| 10 | 0.2 | 5 | 850 | -0.2992 | -2.42 |
| 10 | 0.2 | 10 | 850 | -0.2632 | -1.09 |
| 10 | 0.3 | 3 | 850 | -0.2939 | -4.54 |
| 10 | 0.3 | 5 | 850 | -0.2905 | -2.84 |
| 10 | 0.3 | 10 | 850 | -0.2524 | -1.32 |

H1 BIST100 evreni (saglamlik) OOS: {'n': 853, 'ort': -0.4311, 't': -5.46}

## H2 ayrintisi

- Seans dilimi: {'10:00-10:30': {'n': 136, 'gun': 46, 'ort': 0.384, 't': 1.76}, '10:30-12:30': {'n': 189, 'gun': 48, 'ort': 0.204, 't': 1.14}, '12:30-16:00': {'n': 204, 'gun': 45, 'ort': -0.129, 't': -0.86}, '16:00-18:10': {'n': 141, 'gun': 42, 'ort': 0.126, 't': 1.37}}
- Ture gore: {'P1_KALITELI_AL': {'n': 1}, 'P2_ADAY': {'n': 40, 'gun': 24, 'ort': 0.268, 't': 0.76}, 'P2_DIP_DONUS': {'n': 18, 'gun': 14, 'ort': 0.059, 't': 0.14}, 'P3_RADAR': {'n': 99, 'gun': 38, 'ort': 0.222, 't': 1.39}, 'P3_SKOR_AL': {'n': 211, 'gun': 33, 'ort': 0.063, 't': 0.37}, 'P4_HAZIRLIK': {'n': 175, 'gun': 27, 'ort': -0.086, 't': -0.42}, 'SEKTOR_ROTASYONU': {'n': 126, 'gun': 25, 'ort': 0.36, 't': 1.57}}
- 10 yillik gece/gunduz (bilgi): {'gunduz': -0.0653, 'gece': 0.2104, 'gunduz_rel': 0.0107, 'gece_rel': 0.021}

## H3 ek bilgi

- Piyasa geneli <= -4% gunleri: {'olay': 34, 'sonrasi_10g_ort': 2.068, 'kosulsuz_10g_ort': 1.106, 'not': 'Mutlak (nominal) getiri; yalniz bilgi. Ust uste binen pencereler.'}

## Veri

- Fiyati cekilemeyen: yok
- Sembol baslangic tarihleri: {'AKBNK': '2015-10-01', 'YKBNK': '2015-10-01', 'GARAN': '2015-10-01', 'ISCTR': '2015-10-01', 'SAHOL': '2015-10-01', 'KCHOL': '2015-10-01', 'THYAO': '2015-10-01', 'TAVHL': '2015-10-01', 'EREGL': '2015-10-01', 'ASELS': '2015-10-01', 'ASTOR': '2023-01-18', 'MGROS': '2015-10-01', 'BIMAS': '2015-10-01', 'TUPRS': '2015-10-01', 'TOASO': '2015-10-01', 'FROTO': '2015-10-01', 'ENKAI': '2015-10-01', 'TTKOM': '2015-10-01', 'AEFES': '2015-10-01', 'PGSUS': '2015-10-01', 'HALKB': '2015-10-01', 'VAKBN': '2015-10-01', 'OTKAR': '2015-10-01', 'PETKM': '2015-10-01', 'SISE': '2015-10-01', 'EKGYO': '2015-10-01', 'TRMET': '2015-10-01', 'ALARK': '2015-10-01', 'ENJSA': '2018-02-08', 'ULKER': '2015-10-01', 'TRALT': '2015-10-01'}

Bilinen sinirlar: hayatta kalma yanliligi (donus stratejilerini olumlu yanli gosterir), tek kaynak Yahoo, fiyat limiti ve acik satis modellenmedi.
