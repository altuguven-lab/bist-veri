# H7 Makro Risk Istahi Bayragi

Uretim 2026-10-30T07:55 UTC | on kayit `8ed1bd27551d3ae9` | deneme no 1 | t esigi 2.0

Salt olcum, tavsiye degildir. Fazla getiri = XU100 sonraki ay getirisi - TL fonlama faizi/12 (aylik, yuzde puan).

| Donem | RISK_ACIK ay (ort) | RISK_KAPALI ay (ort) | Fark | t |
|---|---|---|---|---|
| IS 2012-01..2019-12 | 19 (-1.087) | 20 (0.906) | -1.993 | -0.97 |
| OOS 2020-01..2026-06 | 39 (2.586) | 39 (0.018) | 2.568 | 1.22 |

## Hukum: **ELENDI**

- K1_oos_fark_pozitif: EVET
- K2_oos_t: HAYIR
- K3_oos_risk_kapali_ort_negatif: HAYIR
- K4_strateji_altut_ustu: HAYIR
- K5_is_fark_pozitif: HAYIR
- Strateji OOS: {'aylik_ort_fazla': 1.194, 'altut_aylik_ort_fazla': 1.302, 'risk_acik_ay_orani': 0.5, 'rejim_degisimi': 31, 'en_kotu_12_ay': -34.87}

## Tekil gostergeler ve trend (hukum vermez)

| Gosterge | IS fark (t) | OOS fark (t) | OOS acik/kapali ay |
|---|---|---|---|
| S1_kur | -2.262 (-1.11) | -0.459 (-0.22) | 37/41 |
| S2_faiz | -3.54 (-2.06) | -0.964 (-0.46) | 47/31 |
| S3_vix | -0.27 (-0.16) | 2.514 (1.19) | 37/41 |
| trend | -1.308 (-0.69) | -0.158 (-0.07) | 67/11 |

- USD bazli XU100 (bayrak) IS: {'n_acik': 19, 'n_kapali': 20, 'ort_acik': 0.068, 'ort_kapali': -0.36, 'fark': 0.428, 't': 0.14} | OOS: {'n_acik': 39, 'n_kapali': 39, 'ort_acik': 2.447, 'ort_kapali': -0.667, 'fark': 3.114, 't': 1.45}

## Guncel bayrak (2026-10): **RISK_KAPALI** (gozlem amaclidir)

- {'ay_sonu': '2026-10', 'bayrak': 'RISK_KAPALI', 'S1_kur': np.float64(0.0), 'S2_faiz': np.float64(1.0), 'S3_vix': np.float64(0.0), 'trend': np.float64(0.0), 'usd_1a_deg_pct': np.float64(1.61), 'usd_med12_pct': np.float64(1.34), 'faiz': np.float64(36.0), 'faiz_3a_deg': np.float64(-4.0), 'vix': np.float64(17.2), 'vix_med': np.float64(17.13)}

Veri baslangiclari: {'usd_ilk': '2009-01-02', 'faiz_ilk': '2011-01-03', 'vix_ilk': '2009-01-02', 'ay_sayisi': 134}
