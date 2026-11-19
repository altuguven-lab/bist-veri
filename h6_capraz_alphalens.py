"""
H6/F5 BAGIMSIZ CAPRAZ KONTROL - alphalens-reloaded (19.11.2026). SALT OLCUM, TAVSIYE DEGILDIR, Pine'a dokunmaz.
Kurallar: ON_KAYIT_H6_CAPRAZ.md (bu betikten ONCE commit edilir). Tek seferlik; tekrarlanmaz.
Bagimsiz katman: dilimleme, dilim getirileri, arindirma, IC (alphalens). Ortak: fiyat paneli ve F5 degerleri.
Cikti: data/h6/capraz_alphalens.json, data/h6/capraz_alphalens.md
"""
import datetime
import json
import os
import sys

import numpy as np
import pandas as pd
import alphalens as al

import h6_faktor_siralama as h6
from h_testleri import newey_west, sha256

ON_KAYIT = "ON_KAYIT_H6_CAPRAZ.md"
CIKTI = "data/h6"
F5 = "F5_bilanco_surprizi"
PLASEBO_N, TOHUM = 200, 20261119


def donem(s, aralik):
    ay = s.index.strftime("%Y-%m")
    return s[(ay >= aralik[0]) & (ay <= aralik[1])]


def ozet(s, aralik):
    x = donem(s.dropna(), aralik)
    r = newey_west(list(x.values), h6.NW_LAG) or {"n": len(x)}
    if len(x):
        r["pozitif_pct"] = round(100 * float((x > 0).mean()), 1)
    return r


def faktor_serisi(C2, ay_pos, tekil):
    satir = []
    for i0 in ay_pos:
        s = tekil[F5].get(i0)
        if s is None:
            continue
        s = s.dropna()
        if len(s) < h6.MIN_SIRALI:      # H6 ile ayni asgari kosul
            continue
        t = C2.index[i0]
        satir += [(t, k, float(v)) for k, v in s.items()]
    df = pd.DataFrame(satir, columns=["date", "asset", "f"]).set_index(["date", "asset"])["f"]
    return df


def alphalens_hesap(faktor, M):
    """faktor: MultiIndex (date, asset); M: aylik kapanis (ay sonlari). Donus: q5, q1, yayilim, ic serileri (puan)."""
    fwd = (M.shift(-1) / M - 1)
    ileri = fwd.stack().rename("1D").to_frame()
    ileri.index.names = ["date", "asset"]
    ileri = ileri.loc[ileri.index.intersection(faktor.index)]
    fd = al.utils.get_clean_factor(faktor, ileri, quantiles=5, max_loss=1.0)
    q, _ = al.performance.mean_return_by_quantile(fd, by_date=True, demeaned=True)
    q = q["1D"].unstack(level="factor_quantile") * 100
    ic = al.performance.factor_information_coefficient(fd)["1D"]
    return q[5], q[1], q[5] - q[1], ic, fd


def main():
    kd = set(h6.liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in h6.liste_oku("config/bist100_uyeler.txt")
             if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    C, _, _, hata = h6.panel_kur(evren, {})
    C = C[C.index >= pd.Timestamp("2015-01-01")]
    xu = h6.fiyat_cek("XU100")[0]["Close"].reindex(C.index).ffill()
    temel = {k: h6.temel_tablo(k) for k in C.columns}
    C2, ay_pos, _, tekil = h6.calistir(C, xu, temel)
    sonuc = capraz(C2, xu, ay_pos, tekil)
    sonuc["veri"] = {"evren": len(evren), "fiyatli": len(C.columns), "hata": hata}
    yaz(sonuc)
    return 0


def capraz(C2, xu, ay_pos, tekil):
    M = C2.iloc[ay_pos]
    faktor = faktor_serisi(C2, ay_pos, tekil)
    q5, q1, yay, ic, fd = alphalens_hesap(faktor, M)

    # H6'nin kendi portfoy hesabi, ayni panel uzerinde
    ust = h6.portfoy_serisi(C2, xu, ay_pos, tekil[F5])
    alt = h6.portfoy_serisi(C2, xu, ay_pos, tekil[F5], alt_dilim=True)
    ust_brut_ew = ust["net_ew"] + ust["maliyet"]
    ust_net = ust["net_ew"]
    h6_ust_brut_ew = pd.Series(ust_brut_ew.values, index=pd.to_datetime(ust["ay"]))
    h6_ust_net = pd.Series(ust_net.values, index=pd.to_datetime(ust["ay"]))
    fark_df = ust[["ay", "brut"]].merge(alt[["ay", "brut"]], on="ay", suffixes=("_u", "_a"))
    h6_fark = pd.Series((fark_df["brut_u"] - fark_df["brut_a"]).values, index=pd.to_datetime(fark_df["ay"]))
    # alphalens serilerini ay etiketine cevir (karsilastirma ay bazinda)
    ay = lambda s: pd.Series(s.values, index=pd.to_datetime(s.index.strftime("%Y-%m")))
    q5, q1, yay, ic = ay(q5), ay(q1), ay(yay), ay(ic)

    # plasebo: her ay F5'i hisseler arasinda karistir
    rng = np.random.default_rng(TOHUM)
    pl = []
    for _ in range(PLASEBO_N):
        k = faktor.groupby(level="date", group_keys=False).apply(
            lambda s: pd.Series(rng.permutation(s.values), index=s.index))
        _, _, y, _, _ = alphalens_hesap(k, M)
        y = ay(y)
        pl.append(float(donem(y.dropna(), h6.BIL_OOS).mean()))
    pl = np.array(pl)

    O, I = h6.BIL_OOS, h6.BIL_IS
    a_yay, a_q5, a_ic = ozet(yay, O), ozet(q5, O), ozet(ic, O)
    h_q5 = ozet(h6_ust_brut_ew, O)
    gercek = a_yay.get("ort")
    yuzdelik = round(100 * float((pl < gercek).mean()), 1) if gercek is not None else None
    U = {"U1_yayilim_pozitif_t2": (gercek or -1) > 0 and (a_yay.get("t") or -99) > 2.0,
         "U2_q5_h6_farki_0_50": (a_q5.get("ort") is not None and h_q5.get("ort") is not None
                                  and abs(a_q5["ort"] - h_q5["ort"]) <= 0.50),
         "U3_ic_pozitif": (a_ic.get("ort") or -1) > 0,
         "U4_plasebo_95": yuzdelik is not None and yuzdelik > 95.0}
    etiket = "UYUMLU" if all(U.values()) else ("KISMI" if U["U1_yayilim_pozitif_t2"] and U["U3_ic_pozitif"] else "UYUMSUZ")
    return {
        "uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "on_kayit_sha256": sha256(ON_KAYIT) if os.path.exists(ON_KAYIT) else None,
        "alphalens_surum": al.__version__, "pandas_surum": pd.__version__,
        "etiket": etiket, "kriterler": U,
        "alphalens": {"q5_arindirilmis": {"IS": ozet(q5, I), "OOS": a_q5}, "q1_arindirilmis": {"IS": ozet(q1, I), "OOS": ozet(q1, O)},
                      "q5_eksi_q1": {"IS": ozet(yay, I), "OOS": a_yay}, "ic_spearman": {"IS": ozet(ic, I), "OOS": a_ic},
                      "ay_sayisi": int(fd.index.get_level_values(0).nunique())},
        "h6_ayni_panel": {"ust_brut_eksi_evren": {"IS": ozet(h6_ust_brut_ew, I), "OOS": h_q5},
                          "ust_net_evren": {"IS": ozet(h6_ust_net, I), "OOS": ozet(h6_ust_net, O)},
                          "ust_eksi_alt_brut": {"IS": ozet(h6_fark, I), "OOS": ozet(h6_fark, O)}},
        "h6_ekim_kaydi": {"ust_net_evren_OOS": 1.1791, "t": 2.37, "ust_eksi_alt_brut_OOS": 3.3178, "t2": 3.97},
        "plasebo": {"n": PLASEBO_N, "tohum": TOHUM, "ort": round(float(pl.mean()), 4), "p95": round(float(np.percentile(pl, 95)), 4),
                    "gercek_yuzdelik": yuzdelik},
    }


def yaz(r):
    os.makedirs(CIKTI, exist_ok=True)
    json.dump(r, open(f"{CIKTI}/capraz_alphalens.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    a, h = r["alphalens"], r["h6_ayni_panel"]
    f = lambda d: f"{d.get('ort')} (t {d.get('t')}, n {d.get('n')})"
    L = ["# H6/F5 bagimsiz capraz kontrol (alphalens)", "",
         f"On kayit `{(r['on_kayit_sha256'] or '-')[:16]}` | alphalens {r['alphalens_surum']} | Salt olcum, tavsiye degildir.", "",
         f"## Etiket: **{r['etiket']}**", ""] + [f"- {k}: {'EVET' if v else 'HAYIR'}" for k, v in r["kriterler"].items()] + [
         "", "| Olcu (aylik, puan) | IS | OOS |", "|---|---|---|",
         f"| alphalens Q5-Q1 brut | {f(a['q5_eksi_q1']['IS'])} | {f(a['q5_eksi_q1']['OOS'])} |",
         f"| H6 ust-alt brut (ayni panel) | {f(h['ust_eksi_alt_brut']['IS'])} | {f(h['ust_eksi_alt_brut']['OOS'])} |",
         f"| alphalens Q5 arindirilmis brut | {f(a['q5_arindirilmis']['IS'])} | {f(a['q5_arindirilmis']['OOS'])} |",
         f"| H6 ust brut - evren (ayni panel) | {f(h['ust_brut_eksi_evren']['IS'])} | {f(h['ust_brut_eksi_evren']['OOS'])} |",
         f"| H6 ust net - evren (ayni panel) | {f(h['ust_net_evren']['IS'])} | {f(h['ust_net_evren']['OOS'])} |",
         f"| alphalens IC (Spearman) | {f(a['ic_spearman']['IS'])} | {f(a['ic_spearman']['OOS'])} |", "",
         f"Plasebo ({r['plasebo']['n']} karistirma): OOS Q5-Q1 ort {r['plasebo']['ort']}, %95 {r['plasebo']['p95']}; "
         f"gercek deger plasebonun %{r['plasebo']['gercek_yuzdelik']}'sinden buyuk.", "",
         f"Ekim kaydi (H6 deneme 1): ust net-evren OOS {r['h6_ekim_kaydi']['ust_net_evren_OOS']} (t {r['h6_ekim_kaydi']['t']}), "
         f"ust-alt brut OOS {r['h6_ekim_kaydi']['ust_eksi_alt_brut_OOS']} (t {r['h6_ekim_kaydi']['t2']}).", "",
         "Kapsam: dilimleme/istatistik katmani bagimsizdir; fiyat paneli ve F5 degerleri H6 ile ortaktir.",
         "Gozlem amaclidir, tavsiye degildir."]
    open(f"{CIKTI}/capraz_alphalens.md", "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
