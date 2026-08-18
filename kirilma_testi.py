"""
IP-7 KIRILMA TESTI (17.08.2026) - SALT OLCUM

"19 Mart 2025 sonrasi BIST davranisi farkli" hipotezinin testi.
Sinyal uretmez, Pine'a dokunmaz, karar dosyalarina yazmaz.

ON KAYIT: ON_KAYIT_IP7.md - bu betik o belgeyi UYGULAR, yorumlamaz.
Esikler, pencereler ve karar kurallari orada kilitlidir; burada
degistirilemez.

--- IKI ASAMALI KOSU (korleme mekanizmasi) ---------------------------
  python kirilma_testi.py --asama 1   # yalniz kunye + gozlem + MDE
  python kirilma_testi.py --asama 2   # tam sonuc

Asama 1 KIRILMA SONUCU BASMAZ. Amac: sonucu gorup esik ayarlamayi
mekanik olarak imkansiz kilmak. On kayit belgesi Asama 1 ile Asama 2
ARASINDA commit'lenir.

Gerekce (17.08 dersi): ayni gun sabah "08.08 sonrasi performans
kotulesti" denildi; gun-agirliklama duzeltmesi iddiayi TERSINE cevirdi.
Sonuc gorulduikten sonra kurulan gerekce, gerekce degildir.

NOT: yfinance + ruptures + arch gerektirir - Actions runner'inda kosar.
"""
from json_atomik_yaz import atomik_json_yaz
import argparse
import datetime
import json
import statistics
import sys

import numpy as np
import ruptures as rpt
import yfinance as yf
from arch import arch_model
from scipy import stats

CIKTI = "data/denetim/ip7_kirilma_testi.json"

# --- ON KAYIT §3: sabit tarihler, kayan pencere YOK -------------------
BASLANGIC = "2018-01-01"
BITIS = "2026-08-16"
SANSUR = ("2025-03-19", "2025-04-04")     # devre kesici + Yahoo riski
OLAY_TARIHI = "2025-03-19"
REJIM2_BASLANGIC = "2025-09-01"           # EBDKS
SAKLI_BASLANGIC = "2026-02-17"

# K1 KESINLIK SARTI (17.08, pozitif kontrolden ogrenildi — gercek veri
# gorulmeden eklendi, korleme bozulmadi).
# Ilk yazimda K1 yalnizca "GA 19 Mart'i iceriyor mu" diye soruyordu.
# Sentetik kontrolde koşullu volatilite serisi 5,5 YIL genisliginde bir
# GA uretti ve 19 Mart'i "iceriyor" oldugu icin K1'i GECTI. Yani kural,
# belirsizligi odullendiriyordu.
# Duzeltme: GA, iki aday kirilma olayini birbirinden AYIRT edebilecek
# kadar dar olmali. 19.03.2025 ile 01.09.2025 (EBDKS) arasi 166 gun;
# bundan genis bir GA, siyasi soku kural degisikliginden ayiramaz.
K1_AZAMI_GA_GUN = 166
EBDKS_TARIHI = "2025-09-01"

ENDEKS = "XU100.IS"
EVREN = [
    "AKBNK", "GARAN", "YKBNK", "ISCTR", "VAKBN", "HALKB",
    "KCHOL", "SAHOL", "ALARK", "ENKAI", "THYAO", "PGSUS", "TAVHL",
    "ASELS", "OTKAR", "ASTOR", "ENJSA", "TUPRS", "PETKM", "EREGL",
    "TRMET", "SISE", "TOASO", "FROTO", "TTKOM", "BIMAS", "MGROS",
    "ULKER", "AEFES", "EKGYO",
]
# On kayit §5: erisilebilen emsaller kullanilir, veri vermeyen emsal
# SESSIZCE dusurulmez - rapora yazilir.
EM_EMSALLERI = ["^BVSP", "^MXX", "^JKSE", "^NSEI", "EEM"]
FAKTORLER = ["USDTRY=X", "^VIX", "EEM"]

# C.7 (specification curve) — tuzuk eki. Duyarlilik analizleri
# secilerek degil, TUMU tek sirali egride raporlanir. Tek bir
# spesifikasyonun gecmesi bulgu DEGILDIR.
SPEC_CEZA_CARPANLARI = [1.0, 1.5, 2.0, 3.0, 4.0]
SPEC_MIN_BOYUT = [20, 30, 60]
SPEC_PENCERE_GUN = 60     # kirilma "19 Mart penceresinde" sayilma toleransi

BLOK_UZUNLUGU = 21        # bootstrap blok uzunlugu (on kayit §5)
BOOTSTRAP_N = 1000
GA_ALT, GA_UST = 2.5, 97.5


def _seri(ticker):
    try:
        df = yf.Ticker(ticker).history(start=BASLANGIC, end=BITIS,
                                       interval="1d")
    except Exception as e:
        print(f"UYARI: {ticker} cekilemedi -> {e}", file=sys.stderr)
        return {}
    out = {}
    for idx, r in df.iterrows():
        try:
            o, c = float(r["Open"]), float(r["Close"])
            if o > 0 and c > 0:
                out[idx.date()] = (o, c)
        except (TypeError, ValueError):
            continue
    return out


def _gece_gunduz(ham):
    """tarih -> (gece%, gunduz%, toplam%). Sansur penceresi CIKARILIR."""
    s0 = datetime.date.fromisoformat(SANSUR[0])
    s1 = datetime.date.fromisoformat(SANSUR[1])
    tarihler = sorted(ham)
    out = {}
    for i in range(1, len(tarihler)):
        t, y = tarihler[i], tarihler[i - 1]
        if s0 <= t <= s1:
            continue                      # on kayit §3: sansur
        (o, c), (_, pc) = ham[t], ham[y]
        out[t] = ((o / pc - 1) * 100, (c / o - 1) * 100, (c / pc - 1) * 100)
    return out


def _kirilma(dizi):
    """PELT + BIC cezasi. Ceza gozle SECILMEZ (on kayit §5)."""
    x = np.asarray(dizi, dtype=float).reshape(-1, 1)
    n = len(x)
    if n < 100:
        return []
    pen = 2 * float(np.var(x)) * np.log(n)
    try:
        noktalar = rpt.Pelt(model="l2", min_size=30).fit(x).predict(pen=pen)
    except Exception as e:
        print(f"UYARI: kirilma tespiti basarisiz -> {e}", file=sys.stderr)
        return []
    return [p for p in noktalar if p < n]


def _birincil_kirilma(dizi):
    """En buyuk seviye kaymasini ureten kirilma."""
    noktalar = _kirilma(dizi)
    if not noktalar:
        return None
    x = np.asarray(dizi, dtype=float)
    en_iyi, en_buyuk = None, -1.0
    for p in noktalar:
        if p < 30 or len(x) - p < 30:
            continue
        fark = abs(float(np.mean(x[p:])) - float(np.mean(x[:p])))
        if fark > en_buyuk:
            en_iyi, en_buyuk = p, fark
    return en_iyi


def _kirilma_ga(dizi, p_hat, rng):
    """Kirilma tarihi guven araligi — ARTIK bootstrap'i.

    17.08 DUZELTMESI. Ilk surum hareketli blok bootstrap kullaniyordu:
    bloklar rastgele siralanarak yeni seri kuruluyordu. Bu YANLISTI —
    blok karistirma kirilmanin KENDISINI yok eder, dolayisiyla yeniden
    tahmin edilen "kirilma" gurultudur. Pozitif kontrolde yakalandi:
    seriye 19.03.2025'e gomulen kayma icin GA uretilemedi, uretilen
    yerlerde de 7 yila yayilan anlamsiz aralik cikti.

    Dogrusu: tahmin edilen kirilma YAPISINI koru (oncesi/sonrasi
    ortalamalari), yalnizca ARTIKLARI blok halinde yeniden ornekle,
    seriyi yeniden kur ve kirilmayi yeniden tahmin et. Boylece olculen
    sey "kirilma var mi" degil, "kirilmanin YERI ne kadar belirsiz" -
    ki K1'in sordugu tam budur.
    """
    x = np.asarray(dizi, dtype=float)
    n = len(x)
    if p_hat is None or p_hat < 30 or n - p_hat < 30:
        return None
    uydurma = np.empty(n)
    uydurma[:p_hat] = np.mean(x[:p_hat])
    uydurma[p_hat:] = np.mean(x[p_hat:])
    artik = x - uydurma

    bloklar = max(1, n // BLOK_UZUNLUGU + 1)
    tahminler = []
    for _ in range(BOOTSTRAP_N):
        parcalar = []
        for _ in range(bloklar):
            b = int(rng.integers(0, max(1, n - BLOK_UZUNLUGU)))
            parcalar.append(artik[b:b + BLOK_UZUNLUGU])
        yeni_artik = np.concatenate(parcalar)[:n]
        p = _birincil_kirilma(uydurma + yeni_artik)
        if p is not None:
            tahminler.append(p)
    if len(tahminler) < 50:
        return None
    return (float(np.percentile(tahminler, GA_ALT)),
            float(np.percentile(tahminler, GA_UST)))


def _kosullu_vol(getiriler):
    """GJR-GARCH(1,1), Student-t. Kosullu sigma serisi doner."""
    try:
        m = arch_model(np.asarray(getiriler, dtype=float), p=1, o=1, q=1,
                       dist="t")
        return list(m.fit(disp="off").conditional_volatility)
    except Exception as e:
        print(f"UYARI: GARCH basarisiz -> {e}", file=sys.stderr)
        return []


def _mde(n_once, n_sonra, alpha, guc=0.80):
    za = stats.norm.ppf(1 - alpha / 2)
    zb = stats.norm.ppf(guc)
    return (za + zb) * float(np.sqrt(1 / n_once + 1 / n_sonra))


def _k2_esik(dizi, p_hat, pencere=250):
    """K2 — kayma, ONCESI donemin 250 gunluk kayan dagiliminin 99.
    yuzdeligini asiyor mu? Yalniz istatistiksel anlamlilik yetersizdir
    (on kayit §5); esik, serinin kendi tarihsel oynakliginden turer."""
    x = np.asarray(dizi, dtype=float)
    if p_hat is None or p_hat < pencere + 30:
        return None
    once = x[:p_hat]
    once_ort = float(np.mean(once))
    kayanlar = [abs(float(np.mean(once[i:i + pencere])) - once_ort)
                for i in range(len(once) - pencere)]
    if len(kayanlar) < 50:
        return None
    return float(np.percentile(kayanlar, 99))


def _standardize(getiriler, kosullu_vol):
    """K3 — kosullu volatiliteye gore standardize getiri. Etki burada
    kayboluyorsa bulgu 'olcek degisimi'dir, 'davranis degisimi' DEGIL."""
    n = min(len(getiriler), len(kosullu_vol))
    g = np.asarray(getiriler[-n:], dtype=float)
    v = np.asarray(kosullu_vol[-n:], dtype=float)
    gecerli = v > 1e-9
    out = np.zeros(n)
    out[gecerli] = g[gecerli] / v[gecerli]
    return list(out)


def _artiklastir(hedef_map, faktor_maps):
    """K4 — faktorlere (USD/TRY, VIX, EEM) regres et, artiklari don.
    Kirilma artiklarda da korunuyorsa makro karistiricilarla
    aciklanamiyor demektir."""
    ortak = sorted(set(hedef_map) & set.intersection(
        *[set(m) for m in faktor_maps.values()])) if faktor_maps else []
    if len(ortak) < 300:
        return None, []
    y = np.asarray([hedef_map[t] for t in ortak], dtype=float)
    X = np.column_stack(
        [np.ones(len(ortak))] +
        [[faktor_maps[f][t] for t in ortak] for f in sorted(faktor_maps)])
    try:
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    except Exception as e:
        print(f"UYARI: regresyon basarisiz -> {e}", file=sys.stderr)
        return None, []
    return list(y - X @ beta), ortak


def _spec_egrisi(dizi, tarihler, olay):
    """C.7 — tum ceza x min_boyut kombinasyonlarinin kirilma tarihi.
    Secilmis spesifikasyon degil, TUM egri raporlanir."""
    x = np.asarray(dizi, dtype=float).reshape(-1, 1)
    n = len(x)
    if n < 100:
        return []
    taban = float(np.var(x)) * np.log(n)
    egri = []
    for carpan in SPEC_CEZA_CARPANLARI:
        for mb in SPEC_MIN_BOYUT:
            try:
                nk = rpt.Pelt(model="l2", min_size=mb).fit(x).predict(
                    pen=carpan * taban)
            except Exception:
                continue
            nk = [q for q in nk if q < n and q >= mb and n - q >= mb]
            if not nk:
                egri.append({"ceza_carpani": carpan, "min_boyut": mb,
                             "kirilma_tarihi": None, "pencerede": False})
                continue
            en_iyi = max(nk, key=lambda q: abs(
                float(np.mean(x[q:])) - float(np.mean(x[:q]))))
            t = tarihler[min(en_iyi, len(tarihler) - 1)]
            egri.append({
                "ceza_carpani": carpan, "min_boyut": mb,
                "kirilma_tarihi": str(t),
                "pencerede": abs((t - olay).days) <= SPEC_PENCERE_GUN,
            })
    return sorted(egri, key=lambda d: (d["kirilma_tarihi"] or "9999"))


def _holm(p_degerleri):
    """Holm-FWER duzeltmesi (on kayit §5, birincil %5)."""
    sirali = sorted(p_degerleri.items(), key=lambda x: x[1])
    m = len(sirali)
    out, onceki = {}, 0.0
    for i, (ad, p) in enumerate(sirali):
        d = min(1.0, max(onceki, (m - i) * p))
        out[ad] = d
        onceki = d
    return out


def _kesitsel_korelasyon(sembol_gg, tarihler):
    """Gunluk kesitsel corr(gece_i, gunduz_i) - S4."""
    out = {}
    for t in tarihler:
        g = [v[t][0] for v in sembol_gg.values() if t in v]
        d = [v[t][1] for v in sembol_gg.values() if t in v]
        if len(g) >= 10 and statistics.pstdev(g) > 0 and statistics.pstdev(d) > 0:
            out[t] = float(np.corrcoef(g, d)[0, 1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asama", type=int, choices=(1, 2), required=True)
    ap.add_argument("--tohum", type=int, default=20260817)
    args = ap.parse_args()
    rng = np.random.default_rng(args.tohum)

    print(f"IP-7 KIRILMA TESTI — ASAMA {args.asama}")
    print(f"Pencere {BASLANGIC}..{BITIS} | sansur {SANSUR[0]}..{SANSUR[1]}")

    endeks_gg = _gece_gunduz(_seri(ENDEKS))
    if not endeks_gg:
        print("HATA: endeks serisi yok.", file=sys.stderr)
        return
    tarihler = sorted(endeks_gg)
    olay = datetime.date.fromisoformat(OLAY_TARIHI)
    n_once = sum(1 for t in tarihler if t < olay)
    n_sonra = len(tarihler) - n_once

    sembol_gg = {}
    for s in EVREN:
        gg = _gece_gunduz(_seri(f"{s}.IS"))
        if len(gg) > 200:
            sembol_gg[s] = gg

    S1 = [endeks_gg[t][0] for t in tarihler]
    S2 = [endeks_gg[t][1] for t in tarihler]
    toplam = [endeks_gg[t][2] for t in tarihler]
    S3 = _kosullu_vol(toplam)
    s4_map = _kesitsel_korelasyon(sembol_gg, tarihler)
    s4_tarihler = sorted(s4_map)
    S4 = [s4_map[t] for t in s4_tarihler]

    kunye = {
        "zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "asama": args.asama, "tohum": args.tohum,
        "pencere": [BASLANGIC, BITIS], "sansur": list(SANSUR),
        "endeks_gun": len(tarihler),
        "sembol_veri_veren": len(sembol_gg), "sembol_istenen": len(EVREN),
        "n_once": n_once, "n_sonra": n_sonra,
        "seri_uzunluklari": {"S1": len(S1), "S2": len(S2),
                             "S3": len(S3), "S4": len(S4)},
        "MDE_sigma": {
            "alpha_0.05": round(_mde(n_once, n_sonra, 0.05), 4),
            "alpha_0.01": round(_mde(n_once, n_sonra, 0.01), 4),
        },
        "betimleyici": {
            ad: {"ort": round(float(np.mean(v)), 5),
                 "std": round(float(np.std(v)), 5)}
            for ad, v in (("S1", S1), ("S2", S2), ("S3", S3), ("S4", S4)) if v
        },
    }

    print(f"\nEndeks gun: {len(tarihler)} | oncesi {n_once} / sonrasi {n_sonra}")
    print(f"Sembol verisi gelen: {len(sembol_gg)}/{len(EVREN)}")
    print(f"Seri uzunluklari: S1={len(S1)} S2={len(S2)} S3={len(S3)} S4={len(S4)}")
    print(f"\nMDE (sigma birimi, %80 guc): "
          f"a=0.05 -> {kunye['MDE_sigma']['alpha_0.05']:.3f} | "
          f"a=0.01 -> {kunye['MDE_sigma']['alpha_0.01']:.3f}")

    if args.asama == 1:
        atomik_json_yaz(CIKTI.replace(".json", "_asama1.json"), kunye)
        print("\nASAMA 1 TAMAM. Kirilma sonuclari BILEREK basilmadi.")
        print("Simdi ON_KAYIT_IP7.md commit'lenir, sonra --asama 2 kosulur.")
        return

    # ---------------- ASAMA 2 ----------------
    sonuc = dict(kunye)
    seriler = {"S1": (S1, tarihler), "S2": (S2, tarihler),
               "S3": (S3, tarihler[-len(S3):] if S3 else []),
               "S4": (S4, s4_tarihler)}
    sonuc["kirilmalar"] = {}
    ham_p = {}
    print(f"\n{'SERI':6}{'KIRILMA TARIHI':>16}{'%95 GA':>28}{'K1':>6}{'K2':>5}")
    for ad, (dizi, tar) in seriler.items():
        if not dizi or not tar:
            continue
        p = _birincil_kirilma(dizi)
        if p is None or p >= len(tar):
            sonuc["kirilmalar"][ad] = {"kirilma": None}
            print(f"{ad:6}{'yok':>16}")
            continue
        ga = _kirilma_ga(dizi, p, rng)
        ga_tarih, ga_genislik = None, None
        k1 = False
        k1_neden = "GA uretilemedi"
        if ga:
            a = tar[max(0, min(len(tar) - 1, int(ga[0])))]
            b = tar[max(0, min(len(tar) - 1, int(ga[1])))]
            ga_tarih = [str(a), str(b)]
            ga_genislik = (b - a).days
            ebdks = datetime.date.fromisoformat(EBDKS_TARIHI)
            iceriyor = a <= olay <= b
            yeterince_dar = ga_genislik <= K1_AZAMI_GA_GUN
            ayirt_ediyor = not (a <= ebdks <= b)
            k1 = iceriyor and yeterince_dar and ayirt_ediyor
            if not iceriyor:
                k1_neden = "GA 19 Mart'i icermiyor"
            elif not yeterince_dar:
                k1_neden = f"GA cok genis ({ga_genislik}g > {K1_AZAMI_GA_GUN}g) — BELIRSIZ"
            elif not ayirt_ediyor:
                k1_neden = "GA hem 19 Mart'i hem 01 Eylul'u iceriyor — ayirt edemiyor"
            else:
                k1_neden = "gecti"
        once, sonra = float(np.mean(dizi[:p])), float(np.mean(dizi[p:]))
        kayma = sonra - once
        k2_esik = _k2_esik(dizi, p)
        k2 = bool(k2_esik is not None and abs(kayma) > k2_esik)
        t_ist, p_deg = stats.ttest_ind(dizi[p:], dizi[:p], equal_var=False)
        ham_p[ad] = float(p_deg)
        sonuc["kirilmalar"][ad] = {
            "kirilma_tarihi": str(tar[p]), "ga_95": ga_tarih,
            "K1": k1, "K1_neden": k1_neden, "ga_genislik_gun": ga_genislik,
            "once_ort": round(once, 5), "sonra_ort": round(sonra, 5),
            "kayma": round(kayma, 5),
            "K2": k2,
            "K2_esik_99p": round(k2_esik, 5) if k2_esik is not None else None,
            "ham_p": round(float(p_deg), 6),
            "spec_egrisi": _spec_egrisi(dizi, tar, olay),
        }
        print(f"{ad:6}{str(tar[p]):>16}"
              f"{(ga_tarih[0] + '..' + ga_tarih[1]) if ga_tarih else '-':>28}"
              f"{'EVET' if k1 else 'hayir':>6}"
              f"{'EVET' if k2 else 'hayir':>5}  {k1_neden}")

    # --- K3: yapi mi olcek mi -----------------------------------------
    print("\nK3 — STANDARDIZE GETIRILERDE KORUNUYOR MU?")
    print("  (kayboluyorsa bulgu 'olcek degisimi'dir, 'davranis' DEGIL)")
    sonuc["K3"] = {}
    if S3:
        for ad, ham in (("S1", S1), ("S2", S2)):
            std = _standardize(ham, S3)
            tar_std = tarihler[-len(std):]
            p2 = _birincil_kirilma(std)
            if p2 is None or p2 >= len(tar_std):
                sonuc["K3"][ad] = {"kirilma": None, "korunuyor": False}
                print(f"  {ad}n  kirilma YOK -> K3 dustu")
                continue
            ga2 = _kirilma_ga(std, p2, rng)
            korunuyor = False
            ga2_str = "-"
            if ga2:
                a = tar_std[max(0, min(len(tar_std) - 1, int(ga2[0])))]
                b = tar_std[max(0, min(len(tar_std) - 1, int(ga2[1])))]
                ga2_str = f"{a}..{b}"
                korunuyor = (a <= olay <= b
                             and (b - a).days <= K1_AZAMI_GA_GUN)
            sonuc["K3"][ad] = {"kirilma_tarihi": str(tar_std[p2]),
                               "ga_95": ga2_str, "korunuyor": korunuyor}
            print(f"  {ad}n  kirilma {tar_std[p2]}  GA {ga2_str}  "
                  f"-> {'KORUNUYOR' if korunuyor else 'dustu'}")
    else:
        print("  GARCH serisi yok — K3 hesaplanamadi")

    # --- K4a: faktor arindirma ----------------------------------------
    print("\nK4a — FAKTOR ARINDIRMA (USD/TRY, VIX, EEM)")
    faktor_maps = {}
    for f in FAKTORLER:
        fg = _gece_gunduz(_seri(f))
        if len(fg) > 300:
            faktor_maps[f] = {t: v[2] for t, v in fg.items()}
        else:
            print(f"  {f:10} VERI YOK — raporlandi, sessizce dusurulmedi")
    sonuc["K4a_faktorler"] = sorted(faktor_maps)
    if faktor_maps:
        hedef = {t: endeks_gg[t][0] for t in tarihler}
        artik, artik_tar = _artiklastir(hedef, faktor_maps)
        if artik:
            p3 = _birincil_kirilma(artik)
            if p3 is not None and p3 < len(artik_tar):
                ga3 = _kirilma_ga(artik, p3, rng)
                korunuyor = False
                ga3_str = "-"
                if ga3:
                    a = artik_tar[max(0, min(len(artik_tar) - 1, int(ga3[0])))]
                    b = artik_tar[max(0, min(len(artik_tar) - 1, int(ga3[1])))]
                    ga3_str = f"{a}..{b}"
                    korunuyor = (a <= olay <= b
                                 and (b - a).days <= K1_AZAMI_GA_GUN)
                sonuc["K4a_artik"] = {"kirilma_tarihi": str(artik_tar[p3]),
                                      "ga_95": ga3_str,
                                      "korunuyor": korunuyor}
                print(f"  S1 artiklari: kirilma {artik_tar[p3]}  GA {ga3_str}"
                      f"  -> {'KORUNUYOR' if korunuyor else 'dustu'}")
            else:
                sonuc["K4a_artik"] = {"kirilma": None, "korunuyor": False}
                print("  S1 artiklarinda kirilma YOK -> K4a dustu")
        else:
            print("  ortak tarih yetersiz — K4a hesaplanamadi")

    # K4b — EM emsal plasebosu
    print("\nEM EMSAL PLASEBOSU (on kayit §5: veri vermeyen emsal raporlanir)")
    sonuc["em_plasebo"] = {}
    for tic in EM_EMSALLERI:
        gg = _gece_gunduz(_seri(tic))
        if len(gg) < 300:
            sonuc["em_plasebo"][tic] = {"durum": "VERI_YOK"}
            print(f"  {tic:10} VERI YOK — dusurulmedi, raporlandi")
            continue
        tt = sorted(gg)
        p = _birincil_kirilma([gg[t][0] for t in tt])
        kt = str(tt[p]) if p is not None and p < len(tt) else None
        yakin = bool(kt and abs((datetime.date.fromisoformat(kt) - olay).days) <= 45)
        sonuc["em_plasebo"][tic] = {"durum": "OK", "kirilma_tarihi": kt,
                                    "19mart_penceresinde": yakin}
        print(f"  {tic:10} kirilma {kt}  {'KIRLI' if yakin else 'temiz'}")

    kirli = [k for k, v in sonuc["em_plasebo"].items()
             if v.get("19mart_penceresinde")]
    sonuc["K4b_em_temiz"] = len(kirli) == 0

    # --- Coklu test duzeltmesi ----------------------------------------
    if ham_p:
        sonuc["holm_duzeltilmis_p"] = {k: round(v, 6)
                                       for k, v in _holm(ham_p).items()}
        print("\nHOLM-FWER DUZELTILMIS p (birincil esik %5)")
        for ad, pv in sorted(sonuc["holm_duzeltilmis_p"].items()):
            print(f"  {ad:6} ham {ham_p[ad]:.5f} -> holm {pv:.5f}"
                  f"  {'anlamli' if pv < 0.05 else 'anlamsiz'}")

    # --- Specification curve ozeti (C.7) ------------------------------
    print("\nSPECIFICATION CURVE (C.7 — secilmis degil, TUM egri)")
    for ad, v in sonuc["kirilmalar"].items():
        egri = v.get("spec_egrisi") or []
        if not egri:
            continue
        icinde = sum(1 for e in egri if e["pencerede"])
        print(f"  {ad:6} {len(egri)} spesifikasyon | 19 Mart +-"
              f"{SPEC_PENCERE_GUN}g penceresinde: {icinde}/{len(egri)}")

    atomik_json_yaz(CIKTI, sonuc)

    print(f"\nK4b (EM emsalleri): {'TEMIZ' if not kirli else 'KIRLI -> ' + str(kirli)}")
    print(f"Yazildi: {CIKTI}")
    print("\nHATIRLATMA: 'DESTEKLENDI' hukmu icin K1+K2+K3+K4'un TAMAMI")
    print("gerekir. K5 (mekanizma) takas verisi olmadan BLOKE — yani bu")
    print("test hicbir kosulda kompozisyon iddiasini dogrulayamaz.")
    print("Specification curve'de spesifikasyonlarin cogunlugu pencere")
    print("disindaysa, tek bir spesifikasyonun gecmesi bulgu SAYILMAZ.")


if __name__ == "__main__":
    main()
