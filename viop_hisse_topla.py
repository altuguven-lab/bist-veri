#!/usr/bin/env python3
"""VİOP hisse vadeli (SSF) günlük özeti + açık pozisyon (APS) değişimi sinyalleri.

Girdi: Borsa İstanbul "VİOP Günlük Bülten" CSV'si — dosya adı viop_YYYYMMDD.csv (;-ayrık, 2 başlık satırı).
  - data/viop_inbox/viop_YYYYMMDD.csv içindeki dosyalar okunur (elle/otomatik bırakılabilir).
  - Eksik günler Borsa İstanbul'dan otomatik indirilir (repodaki fetch_viop.py'nin kanıtlı adresi önce denenir). Ham CSV
    kaydedilmez, yalnızca özet saklanır. İlk çalıştırmada son ~45 gün geriye doldurulur.
Çıktı: data/viop_hisse_gunluk.json (gün -> hisse özeti), viop_hisse_sinyal.md
Sözleşme çarpanı 100 hisse: APS TL = APS adedi x uzlaşma fiyatı x 100.
Yorum kuralı (APS x fiyat): fiyat↓+APS↑ = yeni short/satış baskısı; fiyat↓+APS↓ = long tasfiyesi;
  fiyat↑+APS↓ = short kapama (squeeze imzası); fiyat↑+APS↑ = yeni long. Kimin short olduğunu bildirmez; tavsiye değildir.
"""
import csv, collections, datetime as dt, glob, io, json, os, re, sys, urllib.request

DATA = os.environ.get("VIOP_DATA_DIR", "data")
INBOX = os.path.join(DATA, "viop_inbox")
GECMIS = os.path.join(DATA, "viop_hisse_gunluk.json")
MD = os.environ.get("VIOP_MD", "viop_hisse_sinyal.md")
ACIGA = os.path.join(DATA, "aciga_satis_squeeze.json")
URL_SABLONLARI = [u for u in [os.environ.get("VIOP_URL_SABLONU", ""),
                              "https://www.borsaistanbul.com/viopdata/viop_{tarih}.csv",
                              "https://www.borsaistanbul.com/data/vadeli/viop_{tarih}.csv"] if u]  # {tarih}=YYYYMMDD
GERI_GUN = 45          # geçmiş azken geriye doldurma (takvim günü)
SON_GUN = 8            # normal çalışmada eksik gün kontrolü
CARPAN = 100
MIN_OI_TL = 3e8        # sinyal listesi için asgari toplam APS (TL)
MIN_FIYAT = 0.5        # %, anlamlı fiyat hareketi
MIN_OI = 1.0           # %, anlamlı APS değişimi
MAX_GUN = 250


def f(x):
    try: return float(str(x).replace(",", "."))
    except ValueError: return 0.0


def ayrac_bul(metin):
    ilk = metin.split("\n", 1)[0]
    return max([";", "\t", ","], key=ilk.count)


def _tarih(t):
    t = t.strip()
    for f in ("%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d", "%Y%m%d"):
        try: return dt.datetime.strptime(t, f)
        except ValueError: pass
    raise ValueError(f"tarih biçimi tanınmadı: {t!r}")

def gun_ozeti(metin):
    rows = list(csv.reader(io.StringIO(metin, newline=""), delimiter=ayrac_bul(metin)))
    h = [x.strip() for x in rows[0]]
    g = collections.defaultdict(list)
    tarih = None
    for r in rows[2:]:
        if len(r) < 22: continue
        d = dict(zip(h, r))
        if d["PAZAR SEGMENTI"] != "SSF": continue
        tarih = tarih or _tarih(d["TARIH"]).date().isoformat()
        g[d["DAYANAK VARLIK"].split(".")[0]].append(d)
    out = {}
    for kod, rs in g.items():
        rs.sort(key=lambda r: _tarih(r["VADE TARIHI"]))
        oi_adet = sum(f(r["ACIK POZISYON"]) for r in rs)
        oi_tl = sum(f(r["ACIK POZISYON"]) * f(r["UZLASMA FIYATI"]) * CARPAN for r in rs)
        d_adet = sum(f(r["ACIK POZISYON DEGISIMI"]) for r in rs)
        d_tl = sum(f(r["ACIK POZISYON DEGISIMI"]) * f(r["UZLASMA FIYATI"]) * CARPAN for r in rs)
        n = rs[0]; sp = None
        if len(rs) > 1 and f(n["UZLASMA FIYATI"]) > 0:
            gun = (_tarih(rs[1]["VADE TARIHI"]) - _tarih(n["VADE TARIHI"])).days
            if gun > 0: sp = round((f(rs[1]["UZLASMA FIYATI"]) / f(n["UZLASMA FIYATI"]) - 1) * 365 / gun * 100, 2)
        hacim = sum(f(r["ISLEM HACMI"]) for r in rs)
        out[kod] = {"uzlasma": f(n["UZLASMA FIYATI"]), "fiyat_degisim_pct": f(n["UZLASMA FIYATI DEGISIMI (%)"]),
                    "oi_adet": oi_adet, "oi_tl": round(oi_tl), "oi_degisim_adet": d_adet, "oi_degisim_tl": round(d_tl),
                    "oi_degisim_pct": round(d_tl / (oi_tl - d_tl) * 100, 2) if oi_tl - d_tl > 0 else 0.0,
                    "hacim_tl": round(hacim), "devir_pct": round(hacim / oi_tl * 100, 1) if oi_tl else 0.0,
                    "takvim_faizi_yillik_pct": sp}
    return tarih, out


def yukle():
    if os.path.exists(GECMIS):
        with open(GECMIS, encoding="utf-8") as fh: return json.load(fh)
    return {"gunler": {}}


def indir(g):
    """Eksik iş günlerini indirip özetler (ham dosya saklanmaz). Dönüş: eklenen gün sayısı."""
    n = 0; bugun = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).date()
    geri = GERI_GUN if len(g["gunler"]) < 10 else SON_GUN
    hatalar = collections.Counter(); ardisik_basarisiz = 0; denenen = 0
    for i in range(0, geri + 1):
        d = bugun - dt.timedelta(days=i)
        if d.weekday() >= 5 or d.isoformat() in g["gunler"]: continue
        denenen += 1; bulundu = False
        for sablon in URL_SABLONLARI:
            url = sablon.format(tarih=f"{d:%Y%m%d}")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (bist-veri fetch_viop)"})
                veri = urllib.request.urlopen(req, timeout=30).read()
            except Exception as e:
                hatalar[f"{url.split('/')[3]}: {type(e).__name__} {getattr(e, 'code', '')}"] += 1; continue
            if len(veri) < 1000:
                hatalar[f"{url.split('/')[3]}: kısa yanıt {len(veri)} bayt"] += 1; continue
            try: tarih, o = gun_ozeti(veri.decode("latin-1"))
            except Exception as e: hatalar[f"ayrıştırma: {e}"] += 1; continue
            if tarih == d.isoformat() and len(o) >= 20:
                g["gunler"][tarih] = o; n += 1; bulundu = True; print(f"  indirildi {tarih}: {len(o)} hisse"); break
            hatalar[f"tarih/satır uyuşmadı ({tarih}, {len(o)} satır)"] += 1
        ardisik_basarisiz = 0 if bulundu else ardisik_basarisiz + 1
        if n == 0 and ardisik_basarisiz >= 6:
            print("  ilk 6 gün hiç indirilemedi, geri doldurma durduruldu"); break
    print(f"  indirme özeti: denenen gün {denenen}, eklenen {n}; hatalar: {dict(hatalar) or '-'}")
    g["indirme_log"] = f"{dt.datetime.now(dt.timezone(dt.timedelta(hours=3))):%Y-%m-%d %H:%M} TR | denenen {denenen}, eklenen {n} | hatalar: {dict(hatalar) or '-'}"
    return n


def sinif(v):
    px, dp = v["fiyat_degisim_pct"], v["oi_degisim_pct"]
    if abs(px) < MIN_FIYAT or abs(dp) < MIN_OI: return None
    if px < 0: return "yeni short / satış baskısı" if dp > 0 else "long tasfiyesi"
    return "short kapama" if dp < 0 else "yeni long"


def rapor(g, aciga):
    gun = sorted(g["gunler"]); son = gun[-1]; b = g["gunler"][son]
    toplam = sum(v["oi_tl"] for v in b.values()); dt_ = sum(v["oi_degisim_tl"] for v in b.values())
    L = [f"# VİOP hisse vadeli — açık pozisyon sinyalleri — {son}", "",
         f"Toplam APS: {toplam/1e9:.1f} mlr TL (gün içi değişim {dt_/1e9:+.2f} mlr TL) · hacim {sum(v['hacim_tl'] for v in b.values())/1e9:.1f} mlr TL · {len(b)} hisse", ""]
    sat = {k: v for k, v in b.items() if v["oi_tl"] >= MIN_OI_TL}
    for ad in ("yeni short / satış baskısı", "short kapama", "long tasfiyesi", "yeni long"):
        l = sorted([(k, v) for k, v in sat.items() if sinif(v) == ad], key=lambda kv: -abs(kv[1]["oi_degisim_tl"]))[:8]
        L.append(f"**{ad}:** " + (", ".join(f"{k} (fiyat {v['fiyat_degisim_pct']:+.1f}%, APS {v['oi_degisim_pct']:+.1f}% / {v['oi_degisim_tl']/1e6:+.0f} mn TL)" for k, v in l) or "–"))
    # çok günlü birikim: son 3 günde toplam APS değişimi ve fiyat
    if len(gun) >= 3:
        L += ["", "**Son 3 gün birikim (APS % değişim, kümülatif fiyat %)** — fiyat düşerken APS sürekli artıyorsa short birikiyor:", ""]
        sat3 = []
        for k in sat:
            ser = [g["gunler"][d].get(k) for d in gun[-3:]]
            if any(s is None for s in ser): continue
            px = 1.0
            for s in ser: px *= 1 + s["fiyat_degisim_pct"] / 100
            dapa = sum(s["oi_degisim_tl"] for s in ser) / max(ser[0]["oi_tl"] - ser[0]["oi_degisim_tl"], 1) * 100
            sat3.append((k, (px - 1) * 100, dapa, sum(s["oi_degisim_tl"] for s in ser)))
        for k, px, dp, d in sorted([x for x in sat3 if x[1] < -1 and x[2] > 3], key=lambda x: -x[3])[:6]:
            L.append(f"- {k}: fiyat {px:+.1f}%, APS {dp:+.1f}% ({d/1e6:+.0f} mn TL)")
    # açığa satış ile kesişim
    if aciga and aciga.get("adaylar"):
        ac = {x["kod"]: x for x in aciga["adaylar"]}
        kes = [(k, ac[k]) for k, v in sat.items() if k in ac and sinif(v) == "yeni short / satış baskısı" and ac[k]["skor"] >= 1]
        if kes:
            L += ["", f"**Açığa satış taramasıyla kesişim ({aciga['tarih']}):** " + ", ".join(f"{k} (AS pay {x['oran_pct']:.1f}%, skor {x['skor']}/4)" for k, x in kes)]
    L += ["", "| Hisse | APS mlr TL | APS Δ% | Fiyat Δ% | Devir % | Takvim faizi % | Sinyal |", "|---|---|---|---|---|---|---|"]
    for k, v in sorted(b.items(), key=lambda kv: -kv[1]["oi_tl"])[:20]:
        L.append(f"| {k} | {v['oi_tl']/1e9:.2f} | {v['oi_degisim_pct']:+.1f} | {v['fiyat_degisim_pct']:+.2f} | {v['devir_pct']:.0f} | {v['takvim_faizi_yillik_pct'] if v['takvim_faizi_yillik_pct'] is not None else '–'} | {sinif(v) or ''} |")
    L += ["", "Not: APS artışı yeni pozisyon demektir, kimin short/long olduğunu söylemez; fiyat yönüyle birlikte okunur. Takvim faizi = yakın ve sonraki vade arasındaki yıllıklandırılmış fark (spot gerektirmez). Tavsiye değildir."]
    return "\n".join(L) + "\n"


def main():
    os.makedirs(INBOX, exist_ok=True)
    g = yukle(); yeni = 0
    try: yeni += indir(g)
    except Exception as e: print("indirme hatası:", e)
    for yol in sorted(glob.glob(os.path.join(INBOX, "viop_*.csv"))):
        m = re.search(r"viop_(\d{4})(\d\d)(\d\d)\.csv$", yol)
        if not m or f"{m[1]}-{m[2]}-{m[3]}" in g["gunler"]: continue
        try: tarih, o = gun_ozeti(open(yol, encoding='latin-1').read())
        except Exception as e: print(f"  {yol}: {e}"); continue
        if tarih and len(o) >= 20: g["gunler"][tarih] = o; yeni += 1; print(f"  {tarih}: {len(o)} hisse")
    for d in sorted(g["gunler"])[:-MAX_GUN]: del g["gunler"][d]
    if g["gunler"]:
        tmp = GECMIS + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh: json.dump(g, fh, ensure_ascii=False)
        os.replace(tmp, GECMIS)
        aciga = None
        if os.path.exists(ACIGA):
            try: aciga = json.load(open(ACIGA, encoding="utf-8"))
            except Exception: pass
        with open(MD, "w", encoding="utf-8") as fh: fh.write(rapor(g, aciga))
    print(f"Yeni gün: {yeni}; toplam gün: {len(g['gunler'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
