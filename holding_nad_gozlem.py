#!/usr/bin/env python3
"""HOLDING NAD ISKONTO GOZLEMI (14.10.2026) - SALT OLCUM, Pine'a dokunmaz, alarm uretmez (Kulucka/IP-3 uyumlu).
Girdi : holding_nad_tablosu.json (elle, birincil kaynakli), yfinance piyasa degerleri, data/temel/ham_<HOLDING>.json (odenmis sermaye).
Cikti : data/holding_nad.json, holding_nad.md   (TAVSIYE DEGILDIR)
Iskonto = holding piyasa degeri / (pay x iştirak piyasa degeri toplami [+ net nakit]) - 1.  Negatif = iskontolu.
Holding piyasa degeri = fiyat x odenmis sermaye (1 TL nominal). Iştirak piyasa degeri: yfinance fast_info market_cap (USD'ye cevrilir).
Pay orani null olan iştirak HESABA GIRMEZ ve 'eksik' listesinde yazilir; eksik varsa sonuc TAM DEGIL diye etiketlenir."""
import json, os, sys
from datetime import datetime, timezone

def piyasa_degeri_usd(kod, kur, test=False):
    if test: return {"YKBNK": 7280, "TUPRS": 9410, "FROTO": 6313, "ARCLK": 1429, "TOASO": 3274, "OTKAR": 977, "TTRAK": 941, "AYGAZ": 1000}.get(kod)
    import yfinance as yf
    try:
        mc = yf.Ticker(f"{kod}.IS").fast_info.get("market_cap")
        return (float(mc) / kur / 1e6) if mc and kur else None
    except Exception as ex:
        print("mc hata", kod, ex, file=sys.stderr); return None

def hesapla(cfg, hold_mc_usd_mn, kur, test=False):
    top, eksik, satirlar = 0.0, [], []
    for p in cfg["paylar"]:
        if p.get("pay_pct") is None:
            eksik.append(f"{p['kod']} (pay yok)"); continue
        mc = piyasa_degeri_usd(p["kod"], kur, test)
        if mc is None:
            eksik.append(f"{p['kod']} (piyasa degeri yok)"); continue
        v = mc * p["pay_pct"] / 100.0; top += v
        satirlar.append({"kod": p["kod"], "pay_pct": p["pay_pct"], "pay_degeri_usd_mn": round(v)})
    sabit = sum(x["deger"] for x in cfg.get("sabit_degerler_usd_mn", []))
    nn = cfg.get("net_nakit_usd_mn")
    liste = top + sabit
    out = {"satirlar": satirlar, "eksik": eksik, "sabit_usd_mn": sabit, "halka_acik_toplam_usd_mn": round(liste),
           "holding_piyasa_degeri_usd_mn": round(hold_mc_usd_mn) if hold_mc_usd_mn else None,
           "tam": not eksik}
    if hold_mc_usd_mn and liste > 0:
        out["iskonto_halka_acik_pct"] = round(100 * (hold_mc_usd_mn / liste - 1), 1)
        if nn is not None:
            out["iskonto_net_nakit_dahil_pct"] = round(100 * (hold_mc_usd_mn / (liste + nn) - 1), 1)
    out["sirket_beyani"] = cfg.get("sirket_beyani")
    return out

def main():
    test = os.environ.get("NAD_TEST") == "1"
    cfg = json.load(open("holding_nad_tablosu.json", encoding="utf-8"))
    sonuc = {}
    kur = 49.4 if test else None
    if not test:
        import yfinance as yf
        df = yf.download("USDTRY=X", period="5d", progress=False, threads=False)
        c = df["Close"]; c = c.iloc[:, 0] if hasattr(c, "columns") else c
        kur = float(c.dropna().iloc[-1])
    for h in ("KCHOL", "SAHOL"):
        c = cfg[h]
        try:
            if test: hold_mc = 10100.0
            else:
                import yfinance as yf
                p = yf.Ticker(f"{h}.IS").fast_info.get("last_price")
                ham = json.load(open(f"data/temel/ham_{h}.json", encoding="utf-8"))
                oa = ham["TRY"]["kalemler"]["2OA"]["v"]; adet = float(oa[max(oa)])
                hold_mc = p * adet / kur / 1e6
            sonuc[h] = hesapla(c, hold_mc, kur, test)
            sonuc[h]["kaynak"] = c.get("kaynak"); sonuc[h]["kaynak_tarihi"] = c.get("kaynak_tarihi")
        except Exception as ex:
            sonuc[h] = {"hata": str(ex)[:150]}
    kayit = {"olusturma_utc": datetime.now(timezone.utc).isoformat(), "usdtry": kur, "mod": "TEST" if test else "GERCEK", "holdingler": sonuc}
    json.dump(kayit, open("/tmp/holding_nad_test.json" if test else "data/holding_nad.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = rapor(kayit)
    open("/tmp/holding_nad_test.md" if test else "holding_nad.md", "w", encoding="utf-8").write(md)
    print(md)

def rapor(k):
    L = ["# Holding NAD iskonto gözlemi (SALT ÖLÇÜM)", "",
         f"Üretim: {k['olusturma_utc'][:16]} UTC · USDTRY {k['usdtry']:.2f} · mod {k['mod']}. Tavsiye değildir. Negatif = iskontolu. Pay oranları birincil kaynaktan elle girilir; null olanlar hesaba girmez.", ""]
    for h, d in k["holdingler"].items():
        L += [f"## {h}", ""]
        if "hata" in d: L += [f"Hesaplanamadı: {d['hata']}", ""]; continue
        L += [f"Kaynak: {d.get('kaynak')} ({d.get('kaynak_tarihi')})", "",
              f"- Holding piyasa değeri: {d['holding_piyasa_degeri_usd_mn']} mn $",
              f"- Halka açık iştirak payları toplamı (sabit değerler dahil): {d['halka_acik_toplam_usd_mn']} mn $",
              f"- **İskonto (yalnız halka açık): {d.get('iskonto_halka_acik_pct', '-')}%**",
              f"- **İskonto (+ net nakit): {d.get('iskonto_net_nakit_dahil_pct', '-')}%**",
              f"- Sonuç tam mı: {'EVET' if d['tam'] else 'HAYIR (eksik: ' + ', '.join(d['eksik']) + ')'}"]
        sb = d.get("sirket_beyani")
        if sb: L.append(f"- Şirket beyanı: {sb}")
        if d["satirlar"]:
            L += ["", "| İştirak | Pay % | Pay değeri mn $ |", "|---|---|---|"] + [f"| {s['kod']} | {s['pay_pct']} | {s['pay_degeri_usd_mn']} |" for s in d["satirlar"]]
        L.append("")
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    main()
