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
Katman C - P3_DEVAM VEKILI (IP-4 D1 kapisi): tasarimdaki anatomi gunluk
  bara cevrildi: kalici dizilim + e21 temasli hacim-sonumlu geri cekilme +
  e9 ustu hacimli devam kapanisi. Parametreler YALNIZ IP-4 Bolum 5
  kayitli araliklarindan taranir; TUM kombinasyon sonuclari raporlanir
  (yalniz en iyisi degil - asiri uyum seffafligi).
SEYTANIN AVUKATI SERHI (tutanaktan): vekiller V151'in ic durumunun
GOLGESIDIR, kendisi degil; sonuclar esik YONU soyler, kesin deger soylemez.
Gunluk vekil 15dk gercekliginin kaba golgesidir: soguma/kovalama
bekcileri gunlukte uygulanamaz, isabet oranlari iyimser sapabilir.
Cikti: data/denetim/golge_kalibrasyon.md + .json
"""
import json, datetime, os, sys, math
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
    cikti = []
    for ix, r in df.iterrows():
        try:
            kap, hac, dus = float(r["Close"]), float(r["Volume"]), float(r["Low"])
        except (TypeError, ValueError):
            continue
        if math.isnan(kap) or math.isnan(hac) or math.isnan(dus):
            continue  # v2.2: NaN bar (tatil/eksik veri) - sessizce atla, ileri tasima
        cikti.append((ix.date(), kap, hac, dus))
    return cikti

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
        sonra = [c for t, c, *_ in s if t > tarih and not math.isnan(c)]
        return sonra[n-1] if len(sonra) >= n else None

    # ---- rejim vekili: XU100 > EMA50
    rejim_on = {}
    x = seriler.get("XU100") or []
    if x:
        e50 = ema([c for _, c, *_ in x], 50)
        rejim_on = {t: c > e for (t, c, *_), e in zip(x, e50)}

    # ---- KATMAN B: IP-2 vekili
    vekiller = []
    for sem in semboller:
        s = seriler.get(sem) or []
        if len(s) < 60: continue
        k = [c for _, c, *_ in s]
        e9, e21, e50 = ema(k, 9), ema(k, 21), ema(k, 50)
        for i in range(HACIM_PENCERE + 1, len(s)):
            t, kap, hac = s[i][0], s[i][1], s[i][2]
            if t < PENCERE_BASI: continue
            dizilim = e9[i] > e21[i] > e50[i]
            dun = e9[i-1] > e21[i-1] > e50[i-1]
            h_ort = sum(r[2] for r in s[i-HACIM_PENCERE:i]) / HACIM_PENCERE
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

    # ---- KATMAN C: P3_DEVAM vekili (IP-4 D1 kapisi)
    # Kayitli araliklar (IP-4 Bolum 5) - gunluk bara uyarlanmis alt kume:
    C_GRID = {"kalicilik": (5, 8), "temas_bandi": (0.005, 0.01),
              "tetik_hacim": (1.1, 1.2, 1.3)}
    SONUM = 1.0  # geri cekilme gunlerinde hacim < 20g ort (sabit, aralik ici)

    retro = _oku("data/denetim/retro_firsat.json") or {}
    kul_pencere = [p for p in retro.get("pencereler", [])
                   if p.get("donem") == "KULUCKA"]

    def p3_vekil_kos(kalicilik, temas_bandi, tetik_hacim):
        sinyaller_c = []
        for sem in semboller:
            s = seriler.get(sem) or []
            if len(s) < 60: continue
            k = [r[1] for r in s]
            e9, e21, e50 = ema(k, 9), ema(k, 21), ema(k, 50)
            for i in range(HACIM_PENCERE + kalicilik + 2, len(s)):
                t, kap, hac, dusuk = s[i]
                if t < PENCERE_BASI: continue
                # B1 kalici dizilim (tetik gunune kadar araliksiz)
                if not all(e9[j] > e21[j] > e50[j]
                           for j in range(i - kalicilik, i + 1)): continue
                # B2 rejim + fiyat konumu
                if not rejim_on.get(t, False) or kap <= e50[i]: continue
                # KURULUM: onceki 1-4 gun icinde e21 temasi + hacim sonumu
                temas_j = None
                for j in range(i - 4, i):
                    if j <= HACIM_PENCERE: continue
                    h_ort_j = sum(r[2] for r in s[j-HACIM_PENCERE:j]) / HACIM_PENCERE
                    if s[j][3] <= e21[j] * (1 + temas_bandi) and s[j][2] < SONUM * h_ort_j:
                        temas_j = j
                if temas_j is None: continue
                # TETIK: kapanis e9 ustu + kurulum penceresi yuksegi asildi + hacim
                if kap <= e9[i]: continue
                if kap <= max(s[j][1] for j in range(temas_j, i)): continue
                h_ort = sum(r[2] for r in s[i-HACIM_PENCERE:i]) / HACIM_PENCERE
                if hac < tetik_hacim * h_ort: continue
                # G4 gunluk tavan: ayni sembolde ust uste gunleri tekille
                if sinyaller_c and sinyaller_c[-1]["sembol"] == sem and                    (t - datetime.date.fromisoformat(sinyaller_c[-1]["tarih"])).days <= 2:
                    continue
                t3 = kapanis_sonrasi(sem, t, 3)
                sinyaller_c.append({"sembol": sem, "tarih": str(t),
                    "fiyat": round(kap, 2), "t3": round(t3, 2) if t3 else None,
                    "hit": (t3 > kap) if t3 else None,
                    "donem": "KULUCKA" if t >= KULUCKA_BASI else "ONCESI"})
        # degerlendirme
        sonuclu = [v for v in sinyaller_c if v["hit"] is not None]
        hit = sum(1 for v in sonuclu if v["hit"])
        gunler = defaultdict(list)
        for v in sinyaller_c:
            gunler[v["sembol"]].append(datetime.date.fromisoformat(v["tarih"]))
        yakalanan = sum(1 for p in kul_pencere
            if any(abs((g - datetime.date.fromisoformat(p["baslangic"])).days) <= 1
                   for g in gunler.get(p["sembol"], [])))
        return sinyaller_c, hit, len(sonuclu), yakalanan

    c_sonuclar = []
    for ka in C_GRID["kalicilik"]:
        for tb in C_GRID["temas_bandi"]:
            for th in C_GRID["tetik_hacim"]:
                sc, hit, n, yak = p3_vekil_kos(ka, tb, th)
                kul_n = sum(1 for v in sc if v["donem"] == "KULUCKA")
                c_sonuclar.append({"kalicilik": ka, "temas_bandi": tb,
                    "tetik_hacim": th, "toplam": len(sc), "kulucka": kul_n,
                    "hit": hit, "sonuclu": n,
                    "isabet": round(100*hit/n, 1) if n else None,
                    "yakalama": f"{yak}/{len(kul_pencere)}"})
    # varsayilan konfig dokum icin
    c_varsayilan, c_hit, c_n, c_yak = p3_vekil_kos(8, 0.005, 1.2)

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

    md_c = ["", "## Katman C - P3_DEVAM vekili (IP-4 D1 kapisi)",
            "D1 esigi: kulucka penceresi yakalama >= %50 VE T+3 isabet >= %55",
            "| kalicilik | temas | hacim | toplam | kulucka | isabet% | yakalama |",
            "|---|---|---|---|---|---|---|"]
    for r in c_sonuclar:
        md_c.append(f"| {r['kalicilik']} | {r['temas_bandi']*100:.1f}% | "
                    f"{r['tetik_hacim']} | {r['toplam']} | {r['kulucka']} | "
                    f"{r['isabet'] if r['isabet'] is not None else '-'} | {r['yakalama']} |")
    md_c.append("")
    md_c.append("### Varsayilan konfig (8 / 0.5% / 1.2) vaka dokumu")
    for v in c_varsayilan:
        md_c.append(f"- {v['sembol']} | {v['tarih']} | {v['fiyat']} -> T+3 "
                    f"{v['t3']} | {'HIT' if v['hit'] else ('MISS' if v['hit'] is not None else 'beklemede')} | {v['donem']}")
    if not c_varsayilan:
        md_c.append("- vekil sinyal uretilmedi")

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
    md += md_c
    md += ["", "---", "Okuma: Katman B kuluckada bol uretip isabeti koruyorsa sorun",
           "V151'in EK katmanlarindadir (taban/esik); o da uretmiyorsa piyasa gercekten kurak."]

    os.makedirs("data/denetim", exist_ok=True)
    open("data/denetim/golge_kalibrasyon.md", "w", encoding="utf-8").write("\n".join(md)+"\n")
    json.dump({"vekiller": vekiller, "skor_kayitlari": kayitlar,
               "esik_tablo": esik_tablo, "katman_c": c_sonuclar,
               "katman_c_varsayilan": c_varsayilan,
               "olusturma": str(datetime.date.today())},
              open("data/denetim/golge_kalibrasyon.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\n".join(md))

if __name__ == "__main__":
    main()
