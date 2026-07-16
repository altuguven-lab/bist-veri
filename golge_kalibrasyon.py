"""
GOLGE KALIBRASYON (KAL-2, 16.07.2026 komite karari)
Amac: V151'e DOKUNMADAN, giris kapisinin bu rejimdeki davranisini iki
vekil katmanla olcmek. Karar degil OLCUM uretir.

Katman A - GERCEK SKOR BANDI: gecerli GUNLUK_OZET kayitlarindaki skorlar
  ile sonraki 3 islem gunu getirisi; skor esigi taramasi (15..40).
  SINIR: skorlar bir bar gecikmeli, gunde tek ornek, 14.07'den beri var.
Katman B - IP-2 VEKIL TEKRARI (01.06 -> bugun, 30 sembol):
  IP2_OZET.md tanimi: EMA 9/21/50 altin dizilim GECIS ani + hacim
  20g x1.3 + rejim ON (vekil: XU100 > EMA50). Haftalik uretim, T+3
  isabet, firsat pencereleriyle ortusme. IP-2 taban cizgisi: T+3 %54.
SEYTANIN AVUKATI SERHI (tutanaktan): vekiller V151'in ic durumunun
GOLGESIDIR, kendisi degil; sonuclar esik YONU soyler, kesin deger soylemez.
Cikti: data/denetim/golge_kalibrasyon.md + .json
"""
import json, datetime, os, sys
from collections import defaultdict

PENCERE_BASI = datetime.date(2026, 6, 1)
KULUCKA_BASI = datetime.date(2026, 7, 7)
SKOR_ESIKLERI = (15, 20, 25, 30, 35, 40)
HACIM_KATSAYI, HACIM_PENCERE = 1.3, 20

def _oku(yol):
    try:
        with open(yol, encoding="utf-8") as f: return json.load(f)
    except Exception: return None

def ema(degerler, n):
    k, e, cikti = 2/(n+1), None, []
    for v in degerler:
        e = v if e is None else v*k + e*(1-k)
        cikti.append(e)
    return cikti

def gunluk_seri(yf, kod, bas):
    df = yf.Ticker(kod).history(start=str(bas), auto_adjust=False)
    return [(ix.date(), float(r["Close"]), float(r["Volume"]))
            for ix, r in df.iterrows()]

def main():
    try:
        import yfinance as yf
    except Exception as e:
        print(f"yfinance yok ({e}) - golge yalnizca Actions'ta kosar"); sys.exit(1)

    q = _oku("data/bist_quotes.json") or {}
    semboller = [v["sembol"] for v in q.get("veriler", []) if v.get("sembol")]
    a = _oku("data/tv_alerts_latest.json") or {}

    # ---- fiyat/hacim serileri (EMA50 isinma payi: -120 gun)
    seriler = {}
    for sem in semboller + ["XU100"]:
        kod = "XU100.IS" if sem == "XU100" else f"{sem}.IS"
        try:
            seriler[sem] = gunluk_seri(yf, kod, PENCERE_BASI - datetime.timedelta(days=120))
        except Exception as e:
            print(f"UYARI: {sem}: {e}", file=sys.stderr)

    def kapanis_sonrasi(sem, tarih, n):
        s = seriler.get(sem) or []
        sonra = [c for t, c, _ in s if t > tarih]
        return sonra[n-1] if len(sonra) >= n else None

    # ---- rejim vekili: XU100 > EMA50
    rejim_on = {}
    x = seriler.get("XU100") or []
    if x:
        e50 = ema([c for _, c, _ in x], 50)
        rejim_on = {t: c > e for (t, c, _), e in zip(x, e50)}

    # ---- KATMAN B: IP-2 vekili
    vekiller = []
    for sem in semboller:
        s = seriler.get(sem) or []
        if len(s) < 60: continue
        k = [c for _, c, _ in s]
        e9, e21, e50 = ema(k, 9), ema(k, 21), ema(k, 50)
        for i in range(HACIM_PENCERE + 1, len(s)):
            t, kap, hac = s[i]
            if t < PENCERE_BASI: continue
            dizilim = e9[i] > e21[i] > e50[i]
            dun = e9[i-1] > e21[i-1] > e50[i-1]
            h_ort = sum(v for _, _, v in s[i-HACIM_PENCERE:i]) / HACIM_PENCERE
            if dizilim and not dun and hac >= HACIM_KATSAYI * h_ort and rejim_on.get(t, False):
                t3 = kapanis_sonrasi(sem, t, 3)
                vekiller.append({"sembol": sem, "tarih": str(t), "fiyat": round(kap, 2),
                                 "t3": round(t3, 2) if t3 else None,
                                 "hit": (t3 > kap) if t3 else None,
                                 "donem": "KULUCKA" if t >= KULUCKA_BASI else "ONCESI"})
    hafta = defaultdict(int)
    for v in vekiller:
        y, w, _ = datetime.date.fromisoformat(v["tarih"]).isocalendar()
        hafta[f"{y}-W{w:02d}"] += 1
    sonuclu = [v for v in vekiller if v["hit"] is not None]
    hit = sum(1 for v in sonuclu if v["hit"])

    # firsat ortusmesi (retro dosyasindan)
    retro = _oku("data/denetim/retro_firsat.json") or {}
    kul_pencere = [p for p in retro.get("pencereler", []) if p.get("donem") == "KULUCKA"]
    vekil_gunleri = defaultdict(list)
    for v in vekiller:
        vekil_gunleri[v["sembol"]].append(datetime.date.fromisoformat(v["tarih"]))
    yakalanan = 0
    for p in kul_pencere:
        g = datetime.date.fromisoformat(p["baslangic"])
        if any(abs((vg - g).days) <= 1 for vg in vekil_gunleri.get(p["sembol"], [])):
            yakalanan += 1

    # ---- KATMAN A: gercek skor bandi
    kayitlar = []
    for s in a.get("sinyal_gecmisi", []):
        if s.get("sinyal") != "GUNLUK_OZET": continue
        try: skor = float(s.get("skor"))
        except (TypeError, ValueError): continue
        try:
            t = datetime.datetime.fromisoformat(s["zaman_utc"].replace("Z","+00:00")).date()
            f = float(s.get("fiyat"))
        except Exception: continue
        t3 = kapanis_sonrasi(s["sembol"], t, 3)
        kayitlar.append({"sembol": s["sembol"], "tarih": str(t), "skor": round(skor, 1),
                         "fiyat": f, "t3": round(t3, 2) if t3 else None,
                         "getiri3": round((t3/f - 1) * 100, 2) if t3 else None})
    esik_tablo = []
    for E in SKOR_ESIKLERI:
        u = [k for k in kayitlar if k["skor"] >= E and k["getiri3"] is not None]
        h = sum(1 for k in u if k["getiri3"] > 0)
        esik_tablo.append((E, len([k for k in kayitlar if k["skor"] >= E]),
                           len(u), h, round(100*h/len(u), 1) if u else None))

    md = [f"# Golge Kalibrasyon ({datetime.date.today()})",
          "SERH: vekiller V151'in golgesidir; sonuclar esik YONU soyler, kesin deger degil.",
          "", "## Katman B - IP-2 vekili (EMA dizilim gecisi + hacim + rejim)",
          f"- Toplam vekil-P1: {len(vekiller)} | T+3 isabet: {hit}/{len(sonuclu)}"
          f" ({round(100*hit/len(sonuclu),1) if sonuclu else '-'}%) | IP-2 taban cizgisi: %54",
          f"- Kulucka donemi vekil-P1: {sum(1 for v in vekiller if v['donem']=='KULUCKA')}"
          f" (canli V151: 0) | firsat penceresi yakalama: {yakalanan}/{len(kul_pencere)}"]
    for h in sorted(hafta): md.append(f"  - {h}: {hafta[h]} vekil sinyal")
    md += ["", "### Kulucka donemi vekil dokumu"]
    for v in [v for v in vekiller if v["donem"] == "KULUCKA"]:
        md.append(f"- {v['sembol']} | {v['tarih']} | {v['fiyat']} -> T+3 {v['t3']} | "
                  f"{'HIT' if v['hit'] else ('MISS' if v['hit'] is not None else 'beklemede')}")
    md += ["", "## Katman A - gercek skor bandi (bir bar gecikmeli, gunde tek ornek)",
           f"- Gecerli kayit: {len(kayitlar)}",
           "| Esik | Kayit>=E | T+3 sonuclu | Pozitif | Isabet% |", "|---|---|---|---|---|"]
    for E, n, u, h, o in esik_tablo:
        md.append(f"| {E} | {n} | {u} | {h} | {o if o is not None else '-'} |")
    md += ["", "### Skor-getiri dokumu"]
    for k in sorted(kayitlar, key=lambda x: -x["skor"]):
        md.append(f"- {k['sembol']} | {k['tarih']} | skor {k['skor']} | T+3 "
                  f"{'%+.2f%%' % k['getiri3'] if k['getiri3'] is not None else 'beklemede'}")
    md += ["", "---", "Okuma: Katman B kuluckada bol uretip isabeti koruyorsa sorun",
           "V151'in EK katmanlarindadir (taban/esik); o da uretmiyorsa piyasa gercekten kurak."]

    os.makedirs("data/denetim", exist_ok=True)
    open("data/denetim/golge_kalibrasyon.md", "w", encoding="utf-8").write("\n".join(md)+"\n")
    json.dump({"vekiller": vekiller, "skor_kayitlari": kayitlar,
               "esik_tablo": esik_tablo, "olusturma": str(datetime.date.today())},
              open("data/denetim/golge_kalibrasyon.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\n".join(md))

if __name__ == "__main__":
    main()
