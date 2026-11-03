# H9 BIST 100 donemsel endeks degisikligi olay testi

Uretim 2026-11-03T06:49 UTC | on kayit `16cf194138c1fcdf` | deneme no 1

Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H9.md'de.

| Test | Donem | Ortalama % | t | IS ort | OOS ort (n) | BH | Hukum |
|---|---|---|---|---|---|---|---|
| H9a Alinan W1 net | 42 | 1.381 | 1.5 | 1.179 | 1.603 (20) | False | **KENAR_YOK** |
| H9b Cikarilan W1 brut | 42 | 0.565 | 0.66 | 2.072 | -1.093 (20) | False | **KENAR_YOK** |
| H9c Alinan W2 brut | 42 | 2.71 | 1.68 | 2.179 | 3.295 (20) | False | **KENAR_YOK** |

Plasebo (63 gun geri): H9a t=1.91, H9b t=1.56, H9c t=3.42 | supheli: False
Pozitif kontrol (+%3): H9a GECTI
2026-10 haric: H9a ort=1.334 t=1.42, H9b ort=1.163 t=1.84, H9c ort=2.826 t=1.71
Kapsama: {'al': {'olay': 322, 'fiyatli': 310}, 'cik': {'olay': 327, 'fiyatli': 314}} | fiyat hatasi 11
W0 (duyuru oncesi 10 gun, tani): {'al': 0.87, 'cik': 0.323}
En buyuk 5 katki (H9a): [{'donem_bas': '2020-04-01', 'kod': 'RYGYO', 'w1': 68.25}, {'donem_bas': '2025-10-01', 'kod': 'ECILC', 'w1': 45.36}, {'donem_bas': '2021-07-01', 'kod': 'ERBOS', 'w1': 44.94}, {'donem_bas': '2022-10-01', 'kod': 'SMRTG', 'w1': 41.6}, {'donem_bas': '2018-04-02', 'kod': 'CEMAS', 'w1': -33.1}]
