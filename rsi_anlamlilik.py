"""
RSI ASIRI-SATIM ISTATISTIKSEL ANLAMLILIK TESTI (07.08.2026) - Faz V0
07.08 caprazdogrulama turunda, RSI(14) asiri-satim tersine-donus
stratejisinin KENDISI (momentum-grup ayriminda BAGIMSIZ, TUM 276
islem) guclu bir sonuc verdi: isabet %52.2, ort net %+6.718. Momentum
hipotezi capraz-dogrulamada basarisiz oldu (ayri konu), ama RSI'in
KENDI performansi HENUZ istatistiksel olarak test edilmedi. Bu script
onu test eder: bu +%6.718 ortalama GERCEK bir kenar mi, yoksa 276
islemlik rastgele bir varyasyon mu?

SALT ANALIZ - yeni backtest calistirmaz, ONCEKI committed sonucu okur.

Yontem:
  - Tek-orneklem t-testi (TUM RSI islemleri): H0: ortalama getiri = 0.
    p<0.05 ise, ortalamanin sifirdan GERCEKTEN farkli oldugu soylenebilir.
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
    veri = _oku("data/backtest/rsi_asiri_satim_swing_sonuc.json")
    detaylar = veri["islem_detaylari"]

    tumu = [t["net_getiri_pct"] for t in detaylar
            if t["net_getiri_pct"] == t["net_getiri_pct"]]  # NaN disla

    print(f"TUM RSI ISLEMLERI: n={len(tumu)}, ortalama=%{ortalama(tumu):.3f}, "
          f"std=%{std_sapma(tumu):.3f}")

    # TEST: RSI stratejisinin GENEL ortalamasi GERCEKTEN sifirdan farkli mi?
    t1, sd1 = t_testi_tek_orneklem(tumu, 0.0)
    p1 = t_dagilimi_iki_kuyruklu_p(t1, sd1)
    print(f"\nTEST - RSI GENEL ortalamasi != 0 mi?")
    print(f"  t={t1:.3f}, sd~{sd1}, p={p1:.6f}")
    print(f"  {'ANLAMLI (p<0.05)' if p1 < 0.05 else 'ANLAMLI DEGIL (p>=0.05)'}")

    sonuc = {
        "test_rsi_genel_sifirdan_farkli": {"n": len(tumu), "ortalama_pct": round(ortalama(tumu), 3),
                                             "t": round(t1, 3), "sd": sd1, "p": round(p1, 6),
                                             "anlamli_mi": p1 < 0.05},
        "not": ("t-dagilimi normal yaklasimla hesaplandi (scipy'siz) - "
                "orneklem buyuklugumuz (n>30) icin yeterli dogrulukta."),
    }
    with open("data/backtest/rsi_anlamlilik_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print("\nYazildi: data/backtest/rsi_anlamlilik_sonuc.json")


if __name__ == "__main__":
    main()
