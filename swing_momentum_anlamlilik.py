"""
SWING MOMENTUM ISTATISTIKSEL ANLAMLILIK TESTI (07.08.2026) - Faz V0
Arastirma raporunun Asama 3 onerisi: "sermaye koymadan once istatistikleri
duzelt". supertrend_adx_swing_momentum_sonuc.json'daki ZAYIF_MOMENTUM
bulgusunun (+%4.545 ort. net getiri, 51 islem) GERCEK bir kenar mi,
yoksa rastgele varyasyon mu oldugunu test eder.

SALT ANALIZ - yeni backtest calistirmaz, ONCEKI committed sonucu okur.

Yontem:
  - Tek-orneklem t-testi (ZAYIF_MOMENTUM): H0: ortalama getiri = 0.
    p<0.05 ise, ortalamanin sifirdan GERCEKTEN farkli oldugu (rastgele
    olmadigi) soylenebilir.
  - Iki-orneklem Welch t-testi (ZAYIF vs GUCLU): H0: iki grubun
    ortalamasi AYNI. p<0.05 ise, aralarindaki fark rastgele DEGIL.
"""
import json
import math


def _oku(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def ortalama(x):
    return sum(x) / len(x)


def std_sapma(x):
    m = ortalama(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def t_testi_tek_orneklem(x, h0_deger=0.0):
    """Tek orneklem t-testi. Doner: (t_istatistigi, serbestlik_derecesi)."""
    n = len(x)
    m = ortalama(x)
    s = std_sapma(x)
    se = s / math.sqrt(n)
    t = (m - h0_deger) / se
    return t, n - 1


def t_testi_welch(x, y):
    """Welch t-testi (esit olmayan varyans varsayimi). Doner:
    (t_istatistigi, yaklasik_serbestlik_derecesi)."""
    n1, n2 = len(x), len(y)
    m1, m2 = ortalama(x), ortalama(y)
    v1, v2 = std_sapma(x) ** 2, std_sapma(y) ** 2
    se = math.sqrt(v1 / n1 + v2 / n2)
    t = (m1 - m2) / se
    sd = (v1 / n1 + v2 / n2) ** 2 / (
        (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    return t, sd


def t_dagilimi_iki_kuyruklu_p(t, sd):
    """t-dagiliminin iki-kuyruklu p-degerinin YAKLASIK hesaplanmasi
    (scipy'siz - GitHub Actions'ta ekstra bagimlilik gerekmesin diye).
    Buyuk serbestlik derecelerinde (sd>30) t-dagilimi normal dagilima
    yakinsar - normal yaklasimi kullanilir. Bu, tam kesin degil ama
    bizim orneklem buyukluklerimiz (sd>30) icin YETERLI dogrulukta."""
    z = abs(t)
    # Normal dagilim kuyruk olasiligi (hata fonksiyonu ile)
    p_tek_kuyruk = 0.5 * math.erfc(z / math.sqrt(2))
    return 2 * p_tek_kuyruk


def main():
    veri = _oku("data/backtest/supertrend_adx_swing_momentum_sonuc.json")
    detaylar = veri["islem_detaylari"]

    guclu = [t["net_getiri_pct"] for t in detaylar
             if t["momentum_durumu"] == "GUCLU_MOMENTUM"
             and t["net_getiri_pct"] == t["net_getiri_pct"]]  # NaN disla
    zayif = [t["net_getiri_pct"] for t in detaylar
             if t["momentum_durumu"] == "ZAYIF_MOMENTUM"
             and t["net_getiri_pct"] == t["net_getiri_pct"]]

    print(f"GUCLU_MOMENTUM: n={len(guclu)}, ortalama=%{ortalama(guclu):.3f}, "
          f"std=%{std_sapma(guclu):.3f}")
    print(f"ZAYIF_MOMENTUM: n={len(zayif)}, ortalama=%{ortalama(zayif):.3f}, "
          f"std=%{std_sapma(zayif):.3f}")

    # TEST 1: ZAYIF_MOMENTUM ortalamasi GERCEKTEN sifirdan farkli mi?
    t1, sd1 = t_testi_tek_orneklem(zayif, 0.0)
    p1 = t_dagilimi_iki_kuyruklu_p(t1, sd1)
    print(f"\nTEST 1 - ZAYIF_MOMENTUM ortalamasi != 0 mi?")
    print(f"  t={t1:.3f}, sd~{sd1}, p={p1:.4f}")
    print(f"  {'ANLAMLI (p<0.05)' if p1 < 0.05 else 'ANLAMLI DEGIL (p>=0.05)'}")

    # TEST 2: ZAYIF_MOMENTUM ile GUCLU_MOMENTUM arasindaki fark anlamli mi?
    t2, sd2 = t_testi_welch(zayif, guclu)
    p2 = t_dagilimi_iki_kuyruklu_p(t2, sd2)
    print(f"\nTEST 2 - ZAYIF_MOMENTUM vs GUCLU_MOMENTUM farki anlamli mi?")
    print(f"  t={t2:.3f}, sd~{sd2:.1f}, p={p2:.4f}")
    print(f"  {'ANLAMLI (p<0.05)' if p2 < 0.05 else 'ANLAMLI DEGIL (p>=0.05)'}")

    sonuc = {
        "test1_zayif_sifirdan_farkli": {"t": round(t1, 3), "sd": sd1, "p": round(p1, 4),
                                          "anlamli_mi": p1 < 0.05},
        "test2_zayif_vs_guclu_farki": {"t": round(t2, 3), "sd": round(sd2, 1), "p": round(p2, 4),
                                         "anlamli_mi": p2 < 0.05},
        "not": ("t-dagilimi normal yaklasimla hesaplandi (scipy'siz) - "
                "orneklem buyuklugumuz (n>30) icin yeterli dogrulukta."),
    }
    with open("data/backtest/swing_momentum_anlamlilik_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print("\nYazildi: data/backtest/swing_momentum_anlamlilik_sonuc.json")


if __name__ == "__main__":
    main()
