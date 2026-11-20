"""
RISK RAPORU (20.11.2026) - quantstats-lumi ile. SALT OLCUM, TAVSIYE DEGILDIR. Pine'a dokunmaz.
Neden: Komite promptundaki "risk raporu" bolumu hazir, denetlenmis bir kutuphaneye dayansin (kendi kodumuz degil).
Girdiler:
  data/h6/aylik.csv   H6 bilesik ust %20 GERIYE DONUK TEST serisi (aylik; brut, maliyet, xu, net_ew)
  data/h6/golge.json  H6 golge portfoyleri G1/G2/G3 (ileriye donuk; ay tamamlandikca)
Cikti: data/risk_raporu.json, data/risk_raporu.md, data/risk_raporu_h6.html (quantstats tearsheet)
Notlar: Getiriler TL nominaldir (enflasyondan arindirilmamis). Risksiz faiz 0 alinir; bu yuzden mutlak Sharpe
yaniltici olabilir, esas karsilastirma XU100'e ve evren ortalamasina gore bilgi oranidir.
"""
import datetime as dt
import json
import os
import sys

import pandas as pd
import quantstats_lumi as qs

PER = 12


def olcu(r, bench=None):
    r = r.dropna()
    if len(r) < 6:
        return {"ay": int(len(r)), "not": "en az 6 ay gerekir"}
    o = {"ay": int(len(r)), "bas": str(r.index[0].date()), "son": str(r.index[-1].date()),
         "toplam_getiri_pct": qs.stats.comp(r) * 100,
         "yillik_bilesik_pct": qs.stats.cagr(r, periods=PER) * 100,
         "yillik_oynaklik_pct": qs.stats.volatility(r, periods=PER) * 100,
         "sharpe_rf0": qs.stats.sharpe(r, periods=PER),
         "sortino_rf0": qs.stats.sortino(r, periods=PER),
         "azami_dusus_pct": qs.stats.max_drawdown(r) * 100,
         "calmar": qs.stats.calmar(r, periods=PER) if qs.stats.max_drawdown(r) < 0 else None,
         "kazanan_ay_pct": qs.stats.win_rate(r) * 100,
         "en_kotu_ay_pct": float(r.min()) * 100, "en_iyi_ay_pct": float(r.max()) * 100,
         "var95_aylik_pct": qs.stats.value_at_risk(r) * 100,
         "cvar95_aylik_pct": qs.stats.cvar(r) * 100}
    if bench is not None:
        b = bench.reindex(r.index)
        te = float((r - b).std())
        o["bilgi_orani_yillik"] = qs.stats.information_ratio(r, b) * (PER ** 0.5) if te > 1e-9 else None
        o["beta"] = float(r.cov(b) / b.var()) if b.var() > 0 else None
        o["kiyas_toplam_getiri_pct"] = qs.stats.comp(b) * 100
        o["kiyas_azami_dusus_pct"] = qs.stats.max_drawdown(b) * 100
    return {k: (round(float(v), 3) if isinstance(v, (int, float)) and not isinstance(v, bool) and k != "ay" else v) for k, v in o.items()}


def h6_backtest():
    d = pd.read_csv("data/h6/aylik.csv")
    ix = pd.to_datetime(d["ay"]) + pd.offsets.MonthEnd(0)
    port = pd.Series(((d["brut"] - d["maliyet"]) / 100).values, index=ix, name="H6 bilesik ust %20 (net)")
    xu = pd.Series((d["xu"] / 100).values, index=ix, name="XU100")
    ew = pd.Series(((d["brut"] - d["maliyet"] - d["net_ew"]) / 100).values, index=ix, name="Evren esit agirlik")
    return port, xu, ew


def golge():
    """Donus: {G1/G2/G3: (net mutlak getiri serisi, evren ortalamasi serisi)}; performans alani h6_golge.py'den."""
    yol = "data/h6/golge.json"
    if not os.path.exists(yol):
        return {}
    g = json.load(open(yol, encoding="utf-8"))
    seri, ew = {"G1": {}, "G2": {}, "G3": {}}, {}
    for ay, v in sorted(g.get("aylar", {}).items()):
        pf = v.get("performans")
        if not pf:
            continue
        t = pd.Timestamp(pf["bitis"])
        ew[t] = pf["evren_ort"] / 100
        for kod in seri:
            if isinstance(pf.get(kod), dict):
                seri[kod][t] = (pf[kod]["net_ew"] + pf["evren_ort"]) / 100
    e = pd.Series(ew, dtype=float).sort_index()
    return {k: (pd.Series(v, dtype=float).sort_index(), e) for k, v in seri.items()}


def main():
    port, xu, ew = h6_backtest()
    oos = port[port.index >= "2024-01-01"]
    out = {"uretim_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "kutuphane": f"quantstats-lumi {getattr(qs, '__version__', '?')}",
           "not": "TL nominal, aylik. Risksiz faiz 0. Geriye donuk test: hayatta kalma yanliligi, nokta-zaman verisi degil. "
                  "Salt olcum, tavsiye degildir.",
           "h6_backtest": {"tum_donem_xu100e_gore": olcu(port, xu), "tum_donem_evrene_gore": olcu(port, ew),
                           "2024_sonrasi_xu100e_gore": olcu(oos, xu), "xu100": olcu(xu), "evren": olcu(ew)},
           "golge": {}}
    gs = golge()
    for k, (s, e) in gs.items():
        if len(s) >= 6:
            out["golge"][k] = olcu(s, e)
        else:
            out["golge"][k] = {"ay": int(len(s)), "durum": "BEKLIYOR (olcu icin en az 6 tamamlanmis ay; ilki 30.11.2026)",
                               "aylik_net_evrene_gore_pct": [round((a - b) * 100, 3) for a, b in zip(s.values, e.reindex(s.index).values)]}
    os.makedirs("data", exist_ok=True)
    json.dump(out, open("data/risk_raporu.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    try:
        qs.reports.html(port, benchmark=xu, periods_per_year=PER, output="data/risk_raporu_h6.html",
                        title="H6 bilesik ust %20 - geriye donuk test (TL nominal, aylik)", download_filename="risk_raporu_h6.html")
    except Exception as e:
        out["html_hata"] = str(e)[:300]
        print("UYARI: html uretilemedi:", e, file=sys.stderr)
    satir = lambda ad, o: (f"| {ad} | {o.get('ay')} | {o.get('yillik_bilesik_pct')} | {o.get('yillik_oynaklik_pct')} | "
                           f"{o.get('azami_dusus_pct')} | {o.get('sharpe_rf0')} | {o.get('bilgi_orani_yillik', '-')} | "
                           f"{o.get('en_kotu_ay_pct')} | {o.get('cvar95_aylik_pct')} |")
    h = out["h6_backtest"]
    L = ["# Risk raporu (quantstats)", "", out["not"], "",
         "| Seri | Ay | Yillik bilesik % | Yillik oynaklik % | Azami dusus % | Sharpe (rf 0) | Bilgi orani | En kotu ay % | CVaR95 ay % |",
         "|---|---|---|---|---|---|---|---|---|",
         satir("H6 bilesik (tum, kiyas XU100)", h["tum_donem_xu100e_gore"]),
         satir("H6 bilesik (tum, kiyas evren)", h["tum_donem_evrene_gore"]),
         satir("H6 bilesik (2024-01 sonrasi: OOS + taze, kiyas XU100)", h["2024_sonrasi_xu100e_gore"]),
         satir("XU100", h["xu100"]), satir("Evren esit agirlik", h["evren"]), "",
         "## Golge (ileriye donuk)", ""]
    for k, o in out["golge"].items():
        L.append(f"- {k}: " + (o.get("durum") or f"{o['ay']} ay, bilgi orani (evrene gore) {o.get('bilgi_orani_yillik')}, toplam {o.get('toplam_getiri_pct')}%, azami dusus {o.get('azami_dusus_pct')}%"))
    L += ["", "Ayrintili grafikler: `data/risk_raporu_h6.html`.", "", "Gozlem amaclidir, tavsiye degildir."]
    open("data/risk_raporu.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    json.dump(out, open("data/risk_raporu.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
