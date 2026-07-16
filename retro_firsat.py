"""
RETRO FIRSAT ENVANTERI (16.07.2026 - Baskan talebi)
Pencere: 2026-06-01 -> bugun. Iki katman:
  1) Kulucka oncesi (01.06-06.07): sinyal kaydi YOK -> yalnizca firsat
     yogunlugu (evrenin urettigi +ESIK/T+3 hareket envanteri, taban orani)
  2) Kulucka (07.07->): ayni envanter + tv_alerts'e karsi kacan kontrolu
Cikti: data/denetim/retro_firsat.md + .json
Calistirma: Actions -> Retro Firsat -> Run workflow (yfinance gerekir)
Yontem: gunluk kapanis, ortusmeyen pencereler (bulununca T+3 atlanir),
kova dagilimi 3-5 / 5-8 / 8+%. Karar gerekcesi tek basina DEGILDIR;
hukum gunu bilancosunda M1 (onlenen zarar) ile yan yana okunur.
"""
import json, datetime, os, sys
from collections import defaultdict

PENCERE_BASI = datetime.date(2026, 6, 1)
KULUCKA_BASI = datetime.date(2026, 7, 7)
ESIK = 0.03
GIRIS_ONEK = ("P1", "P2")

def _oku(yol):
    try:
        with open(yol, encoding="utf-8") as f: return json.load(f)
    except Exception: return None

def main():
    import yfinance as yf
    q = _oku("data/bist_quotes.json") or {}
    semboller = [v["sembol"] for v in q.get("veriler", []) if v.get("sembol")]
    if not semboller:
        print("Evren bulunamadi (bist_quotes bos)"); sys.exit(1)

    a = _oku("data/tv_alerts_latest.json") or {}
    giris = defaultdict(list)
    for s in a.get("sinyal_gecmisi", []):
        if str(s.get("sinyal","")).startswith(GIRIS_ONEK) and "TEST" not in str(s.get("sinyal","")).upper():
            try:
                t = datetime.datetime.fromisoformat(s["zaman_utc"].replace("Z","+00:00")).date()
                giris[s["sembol"]].append(t)
            except Exception: pass

    pencereler = []
    for sem in semboller:
        try:
            df = yf.Ticker(f"{sem}.IS").history(
                start=str(PENCERE_BASI - datetime.timedelta(days=7)), auto_adjust=False)
            seri = [(ix.date(), float(v)) for ix, v in df["Close"].items()
                    if ix.date() >= PENCERE_BASI]
        except Exception as e:
            print(f"UYARI: {sem} cekilemedi: {e}", file=sys.stderr); continue
        i = 0
        while i < len(seri) - 3:
            getiri = seri[i+3][1] / seri[i][1] - 1
            if getiri >= ESIK:
                gun = seri[i][0]
                donem = "KULUCKA" if gun >= KULUCKA_BASI else "ONCESI"
                sinyalli = any(abs((g - gun).days) <= 1 for g in giris.get(sem, [])) \
                           if donem == "KULUCKA" else None
                pencereler.append({"sembol": sem, "baslangic": str(gun),
                                   "yuzde": round(getiri*100, 1), "donem": donem,
                                   "sinyalli": sinyalli})
                i += 3
            i += 1

    def kova(y): return "3-5%" if y < 5 else ("5-8%" if y < 8 else "8%+")
    ozet = {"ONCESI": defaultdict(int), "KULUCKA": defaultdict(int)}
    hafta_sayim = defaultdict(int)
    for p in pencereler:
        ozet[p["donem"]][kova(p["yuzde"])] += 1
        y, w, _ = datetime.date.fromisoformat(p["baslangic"]).isocalendar()
        hafta_sayim[f"{y}-W{w:02d}"] += 1
    kul = [p for p in pencereler if p["donem"] == "KULUCKA"]
    kacan = [p for p in kul if p["sinyalli"] is False]

    hafta_adet = max(1, (datetime.date.today() - PENCERE_BASI).days / 7)
    md = [f"# Retro Firsat Envanteri ({PENCERE_BASI} -> {datetime.date.today()})",
          f"Evren: {len(semboller)} sembol | Esik: T->T+3 >= +{ESIK*100:.0f}% | "
          f"Toplam pencere: {len(pencereler)} (haftada ort. {len(pencereler)/hafta_adet:.1f})",
          "", "## Donem karsilastirmasi (taban orani)",
          f"- Kulucka ONCESI (5 hafta): {sum(ozet['ONCESI'].values())} firsat | kova: {dict(ozet['ONCESI'])}",
          f"- KULUCKA donemi: {sum(ozet['KULUCKA'].values())} firsat | kova: {dict(ozet['KULUCKA'])}",
          f"- Kuluckada SINYALSIZ kacan: {len(kacan)} / {len(kul)}",
          "", "## Haftalik dagilim"]
    for h in sorted(hafta_sayim): md.append(f"- {h}: {hafta_sayim[h]} firsat")
    md += ["", "## Kuluckada kacan pencereler (buyukten kucuge)"]
    for p in sorted(kacan, key=lambda x: -x["yuzde"])[:20]:
        md.append(f"- {p['sembol']} | {p['baslangic']} | +{p['yuzde']}%")
    md += ["", "## En buyuk 10 pencere (tum donem)"]
    for p in sorted(pencereler, key=lambda x: -x["yuzde"])[:10]:
        md.append(f"- {p['sembol']} | {p['baslangic']} | +{p['yuzde']}% | {p['donem']}")
    md += ["", "---", "Okuma kurali: taban orani, P1 uretimiyle YAN YANA okunur;",
           "kural degisikligi karari komitede, MANTIK etiketi ve sayac bedeliyle tartisilir."]

    os.makedirs("data/denetim", exist_ok=True)
    open("data/denetim/retro_firsat.md", "w", encoding="utf-8").write("\n".join(md)+"\n")
    json.dump({"olusturma": str(datetime.date.today()), "pencereler": pencereler},
              open("data/denetim/retro_firsat.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\n".join(md))

if __name__ == "__main__":
    main()
