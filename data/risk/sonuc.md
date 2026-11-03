# Risk bataryasi R1-R4

Uretim 2026-11-03T08:30 UTC | on kayit `29456f67c7b4c551` | deneme no 1

Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_RISK.md'de.

## Hukumler

- **R1: GECTI**
- **R2: KENAR_YOK**
- **R3: KENAR_YOK**
- **R4_F1: KENAR_YOK**
- **R4_F2: KENAR_YOK**
- **R4_F3: KENAR_YOK**
- **R4_F4: KENAR_YOK**

Kapsama: {'uye_gun': 270997, 'fiyatli_uye_gun': 266011, 'oran': 0.9816} | fiyat hatasi 8

## R1 Oynaklik tahmini (haftalik Spearman, NW t)

| Tahminci | IS ort (t) | OOS ort (t) |
|---|---|---|
| s20 | 0.3848 (27.1) | 0.3731 (20.83) |
| s60 | 0.448 (26.87) | 0.4321 (22.11) |
| atr14 | 0.4291 (27.57) | 0.4231 (21.71) |
| ewma (secilen) | 0.449 (29.93) | 0.4289 (23.13) |
| plasebo | 0.0072 (1.79) | |

## R2 Oynakliga gore agirlik

| Portfoy | Donem | Yillik getiri | Yillik vol | Maks dusus | CVaR5 | Getiri/vol |
|---|---|---|---|---|---|---|
| EW | IS | 0.4653 | 0.2288 | -0.3034 | -0.03816 | 2.034 |
| EW | OOS | 0.0597 | 0.2866 | -0.4187 | -0.04203 | 0.208 |
| IV | IS | 0.4481 | 0.2214 | -0.2994 | -0.03677 | 2.024 |
| IV | OOS | 0.1063 | 0.2833 | -0.3395 | -0.04117 | 0.375 |
| PLASEBO | IS | 0.4518 | 0.2285 | -0.3053 | -0.0381 | 1.977 |
| PLASEBO | OOS | 0.039 | 0.2862 | -0.4393 | -0.0423 | 0.136 |

Bootstrap (IV dususu daha kucuk) orani: 0.919 | sartlar: {'risk_IS_OOS': True, 'getiri_vol': True, 'bootstrap': False, 'plasebo_risk_sagladi': False}

## R3 Stoplar (islem basi %, net) - secilen: None

| Varyant | Donem | n | Ort | Medyan | CVaR5 | En kotu | Stop orani | Plasebo ort / CVaR5 |
|---|---|---|---|---|---|---|---|---|
| V0 | IS | 30894 | 3.075 | 1.424 | -22.628 | -67.77 | 0.0 | 2.244 / -21.818 |
| V0 | OOS | 17595 | 0.996 | -0.25 | -29.147 | -87.23 | 0.0 | 2.084 / -24.039 |
| S5 | IS | 30894 | 2.292 | -5.25 | -6.249 | -23.95 | 0.523 | 1.01 / -8.096 |
| S5 | OOS | 17595 | 0.62 | -5.25 | -7.7 | -20.65 | 0.645 | 0.924 / -8.307 |
| S8 | IS | 30894 | 2.538 | -0.25 | -9.757 | -26.62 | 0.354 | 1.406 / -9.476 |
| S8 | OOS | 17595 | 0.714 | -5.757 | -9.503 | -24.88 | 0.472 | 1.298 / -10.781 |
| A15 | IS | 30894 | 2.409 | -3.153 | -11.445 | -29.22 | 0.511 | 1.09 / -9.948 |
| A15 | OOS | 17595 | 0.611 | -4.715 | -13.108 | -41.93 | 0.581 | 1.086 / -11.15 |
| A2 | IS | 30894 | 2.562 | -1.165 | -13.939 | -38.87 | 0.409 | 1.398 / -11.99 |
| A2 | OOS | 17595 | 0.685 | -4.89 | -16.28 | -57.1 | 0.467 | 1.329 / -13.563 |
| A3 | IS | 30894 | 2.687 | 0.712 | -17.869 | -41.03 | 0.258 | 1.806 / -15.726 |
| A3 | OOS | 17595 | 0.823 | -1.263 | -20.973 | -81.63 | 0.279 | 1.656 / -17.652 |
| T2 | IS | 30894 | 2.13 | -0.796 | -12.893 | -38.87 | 0.708 | 0.902 / -11.211 |
| T2 | OOS | 17595 | 0.661 | -2.561 | -14.787 | -57.1 | 0.763 | 0.745 / -12.579 |
| T3 | IS | 30894 | 2.499 | 0.17 | -16.874 | -41.03 | 0.45 | 1.452 / -15.013 |
| T3 | OOS | 17595 | 0.817 | -1.719 | -19.635 | -81.63 | 0.487 | 1.394 / -16.819 |

Kosullar: {}
Ortalama farki (secilen - V0) giris gunu kumelenmis: None

## R4 Kriz filtresi (taban: EW sepet, nakit 0)

| Filtre | Donem | Yillik getiri | Yillik vol | Maks dusus | CVaR5 | Azaltilmis gun | Plasebodan iyi | Hukum |
|---|---|---|---|---|---|---|---|---|
| taban | IS | 0.4653 | 0.2288 | -0.3034 | -0.03816 | | | |
| taban | OOS | 0.0597 | 0.2866 | -0.4187 | -0.04203 | | | |
| F1 | IS | 0.4198 | 0.2059 | -0.2256 | -0.03444 | 0.205 | 0.88 | KENAR_YOK |
| F1 | OOS | 0.0808 | 0.2715 | -0.3076 | -0.04035 | 0.205 | 0.88 | KENAR_YOK |
| F2 | IS | 0.4404 | 0.1985 | -0.2368 | -0.0329 | 0.2 | 0.84 | KENAR_YOK |
| F2 | OOS | 0.0644 | 0.2469 | -0.3407 | -0.03729 | 0.2 | 0.84 | KENAR_YOK |
| F3 | IS | 0.4665 | 0.2144 | -0.2817 | -0.03509 | 0.063 | 0.042 | KENAR_YOK |
| F3 | OOS | 0.0328 | 0.2565 | -0.4309 | -0.03843 | 0.063 | 0.042 | KENAR_YOK |
| F4 | IS | 0.4096 | 0.1869 | -0.2039 | -0.03089 | 0.342 | 0.762 | KENAR_YOK |
| F4 | OOS | 0.046 | 0.2353 | -0.323 | -0.03661 | 0.342 | 0.762 | KENAR_YOK |

Nakit faizli (APIFON4) sonuc ve XU100 tabanli tekrar sonuc.json'da (bilgi).
