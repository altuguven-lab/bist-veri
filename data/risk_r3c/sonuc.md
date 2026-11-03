# R3c %5 stop - gercekci uygulama

Uretim 2026-11-03T09:06 UTC | on kayit `cc1e512e450b80bd` | deneme no 1

Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_R3C.md'de.

## Hukum: **STOP_PAHALI**

Sartlar: {'IS': {'cvar_25pct': True, 'ort_kaybi_0_30': False, 'plasebodan_pahali_degil': False, 'ort_fark_gercek': -0.944, 'ort_fark_plasebo': -0.49}, 'OOS': {'cvar_25pct': True, 'ort_kaybi_0_30': False, 'plasebodan_pahali_degil': False, 'ort_fark_gercek': -0.967, 'ort_fark_plasebo': -0.49}}
Ortalama fark S5 - V0 (giris gunu kumelenmis): {'n': 512, 'ort': -0.9516, 't': -12.91}

| Varyant | Donem | n | Fazla ort | CVaR5 | En kotu | Stop orani | Bosluk payi | Plasebo ort / CVaR5 |
|---|---|---|---|---|---|---|---|---|
| V0 | IS | 30894 | -0.194 | -19.993 | -70.19 | 0.0 | 0.0 | -0.246 / -24.099 |
| V0 | OOS | 17595 | -0.142 | -24.866 | -73.08 | 0.0 | 0.0 | -0.27 / -26.42 |
| S5 | IS | 30894 | -1.138 | -13.688 | -29.97 | 0.531 | 0.083 | -0.736 / -10.126 |
| S5 | OOS | 17595 | -1.109 | -12.473 | -31.87 | 0.657 | 0.08 | -0.76 / -10.499 |
| S8 | IS | 30894 | -0.956 | -15.716 | -32.97 | 0.367 | 0.108 |  |
| S8 | OOS | 17595 | -0.902 | -14.781 | -31.66 | 0.486 | 0.097 |  |
| A15 | IS | 30894 | -1.078 | -15.392 | -33.19 | 0.52 | 0.097 |  |
| A15 | OOS | 17595 | -1.093 | -15.57 | -38.74 | 0.594 | 0.09 |  |
| A2 | IS | 30894 | -0.974 | -16.789 | -36.91 | 0.419 | 0.109 |  |
| A2 | OOS | 17595 | -0.938 | -17.442 | -49.53 | 0.48 | 0.104 |  |
| A3 | IS | 30894 | -0.769 | -18.424 | -50.3 | 0.268 | 0.123 |  |
| A3 | OOS | 17595 | -0.634 | -20.117 | -68.26 | 0.292 | 0.135 |  |
| T2 | IS | 30894 | -1.514 | -15.586 | -36.91 | 0.73 | 0.091 |  |
| T2 | OOS | 17595 | -1.343 | -16.009 | -49.53 | 0.783 | 0.096 |  |
| T3 | IS | 30894 | -1.178 | -17.772 | -50.3 | 0.473 | 0.107 |  |
| T3 | OOS | 17595 | -0.941 | -19.132 | -68.26 | 0.514 | 0.116 |  |

## Duyarlilik (hukum vermez)

| Varsayim | Donem | S5 ort | V0 ort | Fark |
|---|---|---|---|---|
| kayma 0.00 / yeniden 0.10 | IS | -0.932 | -0.194 | -0.738 |
| kayma 0.00 / yeniden 0.10 | OOS | -0.854 | -0.142 | -0.712 |
| kayma 0.00 / yeniden 0.25 | IS | -1.012 | -0.194 | -0.818 |
| kayma 0.00 / yeniden 0.25 | OOS | -0.953 | -0.142 | -0.811 |
| kayma 0.25 / yeniden 0.10 | IS | -1.058 | -0.194 | -0.864 |
| kayma 0.25 / yeniden 0.10 | OOS | -1.01 | -0.142 | -0.868 |
| kayma 0.25 / yeniden 0.25 | IS | -1.138 | -0.194 | -0.944 |
| kayma 0.25 / yeniden 0.25 | OOS | -1.109 | -0.142 | -0.967 |
| kayma 0.50 / yeniden 0.10 | IS | -1.184 | -0.194 | -0.99 |
| kayma 0.50 / yeniden 0.10 | OOS | -1.166 | -0.142 | -1.024 |
| kayma 0.50 / yeniden 0.25 | IS | -1.264 | -0.194 | -1.07 |
| kayma 0.50 / yeniden 0.25 | OOS | -1.264 | -0.142 | -1.122 |
| sepet kapanis (R3b gibi), birincil maliyetler | IS | -0.375 | -0.194 | -0.181 |
| sepet kapanis (R3b gibi), birincil maliyetler | OOS | -0.186 | -0.142 | -0.044 |
| R3b esdegeri (kayma 0, yeniden 0, sepet kapanis) | IS | -0.116 | -0.194 | 0.078 |
| R3b esdegeri (kayma 0, yeniden 0, sepet kapanis) | OOS | 0.134 | -0.142 | 0.276 |

Mutlak (stoplanan para nakitte): {'V0': {'IS': {'n': 30894, 'ort': 3.075, 'medyan': 1.424, 'std': 14.489, 'cvar5': -22.628, 'en_kotu': -67.77}, 'OOS': {'n': 17595, 'ort': 0.996, 'medyan': -0.25, 'std': 15.453, 'cvar5': -29.147, 'en_kotu': -87.23}}, 'S5': {'IS': {'n': 30894, 'ort': 2.033, 'medyan': -5.737, 'std': 12.499, 'cvar5': -7.608, 'en_kotu': -24.39}, 'OOS': {'n': 17595, 'ort': 0.3, 'medyan': -5.737, 'std': 11.523, 'cvar5': -8.181, 'en_kotu': -21.1}}}
