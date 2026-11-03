# H10 Yabanci payi degisimi olay testi

Uretim 2026-11-03T07:26 UTC | on kayit `dc604c5133b94f7a` | deneme no 1 | gun 953

Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H10.md'de.

## Birincil (h = 10 islem gunu)

| Test | Gun | Ortalama % | t (NW) | IS ort (n) | OOS ort (n) | BH | Hukum |
|---|---|---|---|---|---|---|---|
| H10a ARTAN - AZALAN | 938 | -0.4193 | -0.86 | -0.487 (275) | -0.391 (663) | False | **KENAR_YOK** |
| H10b ARTAN net - BIST100 EW | 938 | 0.1887 | 0.34 | 0.66 (276) | -0.008 (662) | False | **KENAR_YOK** |
| H10c SUREKLI - BIST100 EW | 804 | 1.2221 | 3.38 | 2.063 (138) | 1.048 (666) | True | **GECTI** |

## Ikincil ufuklar (hukum vermez)

- h=5: H10a ort=-0.5025 t=-1.61, H10b ort=-0.3968 t=-1.3, H10c ort=0.676 t=2.96
- h=20: H10a ort=-0.6614 t=-0.89, H10b ort=1.057 t=0.99, H10c ort=2.764 t=4.83

## Kontroller ve kapsama

- Plasebo (63 gun geri): H10a t=-1.47, H10b t=1.59, H10c t=4.04 | supheli: False
- Pozitif kontrol (+%3): {'H10a': 'GECTI', 'H10b': 'GECTI'}
- Kapsama: {'ARTAN': {'olay': 2820, 'fiyatli': 2561, 'tavan_suphe': 34}, 'AZALAN': {'olay': 2837, 'fiyatli': 2613, 'tavan_suphe': 22}, 'SUREKLI': {'olay': 4056, 'fiyatli': 3914, 'tavan_suphe': 19}} | fiyat hatasi 37
- Yillar (h=10): H10a {'2021': 0.929, '2022': -2.057, '2023': -1.635, '2024': -0.949, '2025': 0.684, '2026': -0.971}; H10b {'2021': 0.694, '2022': -4.534, '2023': 0.809, '2024': -0.668, '2025': 0.989, '2026': -0.373}; H10c {'2021': 1.399, '2023': 2.068, '2024': 0.451, '2025': 2.279, '2026': 0.342}
- En buyuk 5 katki: [{'tarih': '2021-12-03', 'grup': 'ARTAN', 'kod': 'NIBAS', 'getiri': 147.64}, {'tarih': '2025-02-21', 'grup': 'ARTAN', 'kod': 'VSNMD', 'getiri': 145.9}, {'tarih': '2023-11-20', 'grup': 'SUREKLI', 'kod': 'SAMAT', 'getiri': 137.69}, {'tarih': '2026-05-04', 'grup': 'AZALAN', 'kod': 'OZATD', 'getiri': 135.32}, {'tarih': '2026-05-06', 'grup': 'AZALAN', 'kod': 'BIGEN', 'getiri': 135.02}]
