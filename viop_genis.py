#!/usr/bin/env python3
"""
VIOP GENIS (11.11.2026) - BETIMLEYICI VERI KATMANI, SINYAL/TAVSIYE DEGILDIR.

Amac: Borsa Istanbul VIOP gunluk bulteninin (viopdata/viop_YYYYMMDD.csv) TAMAMINI
  1) ham olarak arsivlemek: data/arsiv/viop/YYYY/MM/DD.csv.gz  (gunde ~55 KB)
  2) bugune kadar atilan kisimlardan betimleyici ozet cikarmak: data/viop_genis/YYYY.json (yil basina bir dosya), viop_genis.md
     - endeks vadelileri (XU030, XLBNK): yakin/sonraki vade, uzlasma, acik pozisyon (AP), AP degisimi,
       hacim, vadeye kalan gun, takvim faizi; spot varsa baz % ve yilliklandirilmis baz
     - USD/TRY vadelileri: vade egrisi, yakin->~3 ay ima yillik faiz; spot varsa spot->yakin ima faiz
     - opsiyonlar: XU030 endeks opsiyonu put/call AP ve hacim orani; hisse opsiyonlari toplam ve ilk 10 dayanak
Mevcut viop_hisse_topla.py (hisse vadelisi) ve sqz_skoru.py'ye DOKUNULMAZ.

KURAL: Bu dosya hicbir alarma/karara baglanmaz. Yon iddiasi yalniz on kayit + plasebo ile, yeterli
gecmis birikince sinanir (H-VIOP adaylari). z-skor gecmis < MIN_Z_GUN ise "VERI_YETERSIZ".

Geri doldurma (Asama 2): VIOP_GERI_BASLANGIC=YYYY-MM-DD verilirse o tarihten bugune eksik is gunleri
indirilir (en cok VIOP_GERI_AZAMI gun / kosum, istekler arasi VIOP_BEKLE sn). Once kesif_viop_gecmis
sonucuna bakilarak kullanilir.
"""
import collections, csv, datetime as dt, glob, gzip, io, json, os, statistics, sys, time, urllib.request

DATA = os.environ.get("VIOP_DATA_DIR", "data")
ARSIV = os.path.join(DATA, "arsiv", "viop")
INBOX = os.path.join(DATA, "viop_inbox")
CIKTI_DIR = os.path.join(DATA, "viop_genis")          # yil basina bir dosya: YYYY.json
MD = os.environ.get("VIOP_GENIS_MD", "viop_genis.md")
URL = "https://www.borsaistanbul.com/viopdata/viop_{tarih}.csv"
UA = {"User-Agent": "Mozilla/5.0 (bist-veri viop_genis)"}
SON_GUN = 10
GERI_BASLANGIC = os.environ.get("VIOP_GERI_BASLANGIC", "").strip()
GERI_AZAMI = int(os.environ.get("VIOP_GERI_AZAMI", "300"))
BEKLE = float(os.environ.get("VIOP_BEKLE", "1.0"))
MIN_Z_GUN = 20
Z_PENCERE = 60
ENDEKSLER = {"XU030": "D_XU030D", "XLBNK": "D_XLBNKD"}
SPOT_YF = {"XU030": "XU030.IS", "USDTRY": "TRY=X"}
USD_MIN_AP = 1000
ZAMAN_BUTCESI = float(os.environ.get("VIOP_BUTCE_DK") or 20) * 60   # indirme icin; is akisi suresinden kisa olmali
TR = dt.timezone(dt.timedelta(hours=3))


def f(x):
    try:
        return float(str(x).strip().replace(",", "."))
    except ValueError:
        return 0.0


def tarih_coz(t):
    t = str(t).strip()
    for b in ("%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y", "%Y%m%d"):
        try:
            return dt.datetime.strptime(t, b).date()
        except ValueError:
            pass
    raise ValueError(f"tarih bicimi taninmadi: {t!r}")


def satirlar(metin):
    ilk = metin.split("\n", 1)[0]
    ayrac = max([";", "\t", ","], key=ilk.count)
    rows = list(csv.reader(io.StringIO(metin, newline=""), delimiter=ayrac))
    h = [x.strip() for x in rows[0]]
    out = []
    for r in rows[1:]:
        if len(r) < 20:
            continue
        d = dict(zip(h, [x.strip() for x in r]))
        if d.get("TARIH", "").upper().startswith("TRADE"):      # ingilizce 2. baslik satiri
            continue
        out.append(d)
    return out


# ---------------- arsiv ----------------
def arsiv_yolu(g):
    return os.path.join(ARSIV, f"{g:%Y}", f"{g:%m}", f"{g:%d}.csv.gz")


def arsive_yaz(g, ham):
    p = arsiv_yolu(g)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with gzip.open(p, "wb", compresslevel=9) as fh:
        fh.write(ham)


def ham_dogrula(ham, g):
    if len(ham) < 1000:
        return f"kisa yanit {len(ham)} bayt"
    try:
        rs = satirlar(ham.decode("latin-1"))
        t = tarih_coz(rs[0]["TARIH"])
    except Exception as e:
        return f"ayristirma: {type(e).__name__}"
    return None if t == g else f"tarih uyusmadi ({t})"


def indir(gunler, log):
    n, t0 = 0, time.time()
    for g in gunler:
        if time.time() - t0 > ZAMAN_BUTCESI:
            log["zaman butcesi doldu, kalan gunler sonraki kosuma"] += 1
            break
        if os.path.exists(arsiv_yolu(g)):
            continue
        url = URL.format(tarih=f"{g:%Y%m%d}")
        try:
            ham = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=12).read()
        except Exception as e:
            log[f"{type(e).__name__} {getattr(e, 'code', '')}".strip()] += 1
            time.sleep(BEKLE)
            continue
        hata = ham_dogrula(ham, g)
        if hata:
            log[hata] += 1
        else:
            arsive_yaz(g, ham)
            n += 1
            print(f"  arsivlendi {g}", flush=True)
        time.sleep(BEKLE)
    return n


def inbox_aktar(log):
    n = 0
    for yol in sorted(glob.glob(os.path.join(INBOX, "viop_*.csv"))):
        try:
            g = tarih_coz(os.path.basename(yol)[5:13])
        except ValueError:
            continue
        if os.path.exists(arsiv_yolu(g)):
            continue
        ham = open(yol, "rb").read()
        if ham_dogrula(ham, g) is None:
            arsive_yaz(g, ham)
            n += 1
        else:
            log["inbox dogrulanamadi"] += 1
    return n


# ---------------- ozet ----------------
def vadeli_ozet(rs, g):
    rs = sorted([r for r in rs if tarih_coz(r["VADE TARIHI"]) >= g], key=lambda r: tarih_coz(r["VADE TARIHI"]))
    if not rs:
        return None
    def k(r):
        return {"kod": r["SOZLESME KODU"], "vade": tarih_coz(r["VADE TARIHI"]).isoformat(),
                "kalan_gun": (tarih_coz(r["VADE TARIHI"]) - g).days, "uzlasma": f(r["UZLASMA FIYATI"]),
                "degisim_pct": f(r["UZLASMA FIYATI DEGISIMI (%)"]), "ap": f(r["ACIK POZISYON"]),
                "ap_degisim": f(r["ACIK POZISYON DEGISIMI"]), "hacim_tl": f(r["ISLEM HACMI"])}
    yakin = k(rs[0])
    sonraki = k(rs[1]) if len(rs) > 1 else None
    o = {"yakin": yakin, "sonraki": sonraki, "toplam_ap": sum(f(r["ACIK POZISYON"]) for r in rs),
         "toplam_ap_degisim": sum(f(r["ACIK POZISYON DEGISIMI"]) for r in rs),
         "toplam_hacim_tl": sum(f(r["ISLEM HACMI"]) for r in rs), "takvim_faizi_yillik_pct": None}
    if sonraki and yakin["uzlasma"] > 0 and sonraki["kalan_gun"] > yakin["kalan_gun"]:
        o["takvim_faizi_yillik_pct"] = round((sonraki["uzlasma"] / yakin["uzlasma"] - 1) * 365
                                             / (sonraki["kalan_gun"] - yakin["kalan_gun"]) * 100, 2)
    return o


def usd_ozet(rs, g):
    fut = [r for r in rs if r["SOZLESME TIPI"] == "D_CR_FUT" and r["DAYANAK VARLIK"].startswith("D_USDTRY")
           and f(r["UZLASMA FIYATI"]) > 0 and tarih_coz(r["VADE TARIHI"]) >= g
           and f(r["ACIK POZISYON"]) >= USD_MIN_AP]                 # haftalik/olu vadeler egriyi bozmasin
    fut.sort(key=lambda r: tarih_coz(r["VADE TARIHI"]))
    if not fut:
        return None
    egri = [{"vade": tarih_coz(r["VADE TARIHI"]).isoformat(), "kalan_gun": (tarih_coz(r["VADE TARIHI"]) - g).days,
             "uzlasma": f(r["UZLASMA FIYATI"]), "ap": f(r["ACIK POZISYON"]), "hacim_tl": f(r["ISLEM HACMI"])} for r in fut]
    o = {"egri": egri, "toplam_ap": sum(e["ap"] for e in egri), "yakin_3ay_ima_faiz_pct": None}
    y = egri[0]
    hedef = [e for e in egri if 75 <= e["kalan_gun"] - y["kalan_gun"] <= 110]
    if hedef:
        e = hedef[0]
        o["yakin_3ay_ima_faiz_pct"] = round((e["uzlasma"] / y["uzlasma"] - 1) * 365 / (e["kalan_gun"] - y["kalan_gun"]) * 100, 2)
    return o


def opsiyon_ozet(rs):
    def topla(tip, dayanak=None):
        x = [r for r in rs if r["SOZLESME TIPI"] == tip and (dayanak is None or r["DAYANAK VARLIK"] == dayanak)]
        return sum(f(r["ACIK POZISYON"]) for r in x), sum(f(r["ISLEM HACMI"]) for r in x)
    c_ap, c_h = topla("D_IX_ECO", "D_XU030D")
    p_ap, p_h = topla("D_IX_EPO", "D_XU030D")
    endeks = {"call_ap": c_ap, "put_ap": p_ap, "call_hacim_tl": c_h, "put_hacim_tl": p_h,
              "pc_ap": round(p_ap / c_ap, 3) if c_ap else None, "pc_hacim": round(p_h / c_h, 3) if c_h else None}
    hs = collections.defaultdict(lambda: [0.0, 0.0])
    for r in rs:
        if r["SOZLESME TIPI"] in ("D_EQ_ECP", "D_EQ_EPP"):
            hs[r["DAYANAK VARLIK"].split(".")[0]][0 if r["SOZLESME TIPI"] == "D_EQ_ECP" else 1] += f(r["ACIK POZISYON"])
    tc, tp = sum(v[0] for v in hs.values()), sum(v[1] for v in hs.values())
    ilk = sorted(hs.items(), key=lambda kv: -(kv[1][0] + kv[1][1]))[:10]
    hisse = {"call_ap": tc, "put_ap": tp, "pc_ap": round(tp / tc, 3) if tc else None,
             "ilk10": [{"dayanak": k, "call_ap": v[0], "put_ap": v[1], "pc_ap": round(v[1] / v[0], 3) if v[0] else None} for k, v in ilk]}
    return {"xu030_endeks": endeks, "hisse": hisse}


def gun_ozeti(g):
    rs = satirlar(gzip.open(arsiv_yolu(g)).read().decode("latin-1"))
    o = {"satir": len(rs), "endeks_vadeli": {}, "usdtry": usd_ozet(rs, g), "opsiyon": opsiyon_ozet(rs)}
    for ad, dayanak in ENDEKSLER.items():
        o["endeks_vadeli"][ad] = vadeli_ozet([r for r in rs if r["DAYANAK VARLIK"] == dayanak and r["SOZLESME TIPI"] == "D_IX_FUT"], g)
    return o


# ---------------- spot ----------------
def spot_cek(bas):
    try:
        import yfinance as yf
    except Exception:
        return {}
    out = {}
    for ad, kod in SPOT_YF.items():
        try:
            df = yf.download(kod, start=bas, progress=False, auto_adjust=False)
            s = df["Close"].squeeze().dropna()
            out[ad] = {i.date().isoformat(): float(v) for i, v in s.items()}
        except Exception as e:
            print(f"  spot {kod}: {type(e).__name__}")
    return out


def spot_ekle(gun, o, spot):
    xu = spot.get("XU030", {}).get(gun)
    ev = (o.get("endeks_vadeli") or {}).get("XU030")
    if xu and ev and ev["yakin"]["uzlasma"] > 0:
        y = ev["yakin"]
        # eski yillarda vadeli fiyat olcegi spot endeksten 10'un kati kadar farkli olabilir (sifir atma, endeks/1000)
        carpan = next((c for c in (1, 1000, 100, 10, 0.1, 0.01, 0.001) if abs(y["uzlasma"] * c / xu - 1) < 0.15), None)
        if carpan is None:
            ev["baz_not"] = f"olcek uyusmazligi (spot {xu:.2f}, vadeli {y['uzlasma']:.3f}) - baz hesaplanmadi"
        else:
            baz = (y["uzlasma"] * carpan / xu - 1) * 100
            if carpan != 1:
                ev["olcek_carpani"] = carpan
            ev["spot"] = round(xu, 2)
            ev["baz_pct"] = round(baz, 3)
            ev["baz_yillik_pct"] = round(baz * 365 / max(y["kalan_gun"], 1), 2)
    us = spot.get("USDTRY", {}).get(gun)
    u = o.get("usdtry")
    if us and u and u["egri"]:
        y = u["egri"][0]
        u["spot"] = round(us, 4)
        u["spot_yakin_ima_faiz_pct"] = round((y["uzlasma"] / us - 1) * 365 / max(y["kalan_gun"], 1) * 100, 2)


def z(seri, deger):
    s = [x for x in seri if x is not None][-Z_PENCERE:]
    if len(s) < MIN_Z_GUN or deger is None:
        return "VERI_YETERSIZ"
    sd = statistics.pstdev(s)
    return round((deger - statistics.mean(s)) / sd, 2) if sd else None


def rapor(d):
    gunler = sorted(d["gunler"])
    son = gunler[-1]
    o = d["gunler"][son]
    gecmis = [d["gunler"][g] for g in gunler[:-1]]
    L = [f"# VİOP geniş özet — {son}", "", "Betimleyicidir; alarm/karar girdisi değildir. Gözlem amaçlıdır, tavsiye değildir.", "",
         f"Arşivdeki gün: {len(gunler)} ({gunler[0]} → {son}). z-skor penceresi {Z_PENCERE} gün, en az {MIN_Z_GUN} gün gerekir.", ""]
    L += ["## Endeks vadelileri", "", "| Endeks | Yakın vade | Kalan gün | Uzlaşma | Baz % | Baz yıllık % | Baz z | Toplam AP | AP Δ | Hacim mlr TL | Takvim faizi % |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for ad in ENDEKSLER:
        ev = o["endeks_vadeli"].get(ad)
        if not ev:
            continue
        y = ev["yakin"]
        zb = z([(g["endeks_vadeli"].get(ad) or {}).get("baz_yillik_pct") for g in gecmis], ev.get("baz_yillik_pct"))
        L.append(f"| {ad} | {y['kod']} | {y['kalan_gun']} | {y['uzlasma']:g} | {ev.get('baz_pct', '–')} | {ev.get('baz_yillik_pct', '–')} | {zb} | "
                 f"{ev['toplam_ap']:,.0f} | {ev['toplam_ap_degisim']:+,.0f} | {ev['toplam_hacim_tl'] / 1e9:.2f} | {ev['takvim_faizi_yillik_pct'] if ev['takvim_faizi_yillik_pct'] is not None else '–'} |")
    u = o.get("usdtry")
    if u:
        zf = z([(g.get("usdtry") or {}).get("yakin_3ay_ima_faiz_pct") for g in gecmis], u["yakin_3ay_ima_faiz_pct"])
        L += ["", "## USD/TRY vadeli eğrisi", "",
              f"Yakın→~3 ay ima yıllık faiz: **{u['yakin_3ay_ima_faiz_pct']}%** (z {zf}) · spot→yakın: {u.get('spot_yakin_ima_faiz_pct', '–')}% · toplam AP {u['toplam_ap']:,.0f}", "",
              "| Vade | Kalan gün | Uzlaşma | AP |", "|---|---|---|---|"]
        for e in u["egri"][:8]:
            L.append(f"| {e['vade']} | {e['kalan_gun']} | {e['uzlasma']:g} | {e['ap']:,.0f} |")
    op = o["opsiyon"]
    e = op["xu030_endeks"]
    zpc = z([g["opsiyon"]["xu030_endeks"]["pc_ap"] for g in gecmis], e["pc_ap"])
    L += ["", "## Opsiyonlar", "",
          f"XU030 endeks opsiyonu: put/call AP **{e['pc_ap']}** (z {zpc}), put/call hacim {e['pc_hacim']} · call AP {e['call_ap']:,.0f}, put AP {e['put_ap']:,.0f}",
          f"Hisse opsiyonları toplam: put/call AP {op['hisse']['pc_ap']} (call {op['hisse']['call_ap']:,.0f}, put {op['hisse']['put_ap']:,.0f})", "",
          "| Dayanak | Call AP | Put AP | P/C |", "|---|---|---|---|"]
    for x in op["hisse"]["ilk10"]:
        L.append(f"| {x['dayanak']} | {x['call_ap']:,.0f} | {x['put_ap']:,.0f} | {x['pc_ap']} |")
    L += ["", "Notlar: AP = açık pozisyon (sözleşme adedi). Baz = yakın vade uzlaşma / spot kapanış − 1; uzlaşma ile spot kapanışı aynı anı "
          "göstermeyebilir, küçük farklar gürültüdür. Put/call oranı korunma talebini betimler, yön söylemez. Hiçbir satır sinyal değildir."]
    return "\n".join(L) + "\n"


def is_gunleri(bas, bit):
    g = bas
    while g <= bit:
        if g.weekday() < 5:
            yield g
        g += dt.timedelta(days=1)


def main():
    bugun = dt.datetime.now(TR).date()
    log = collections.Counter()
    d = {"gunler": {}}
    for p in sorted(glob.glob(os.path.join(CIKTI_DIR, "[0-9][0-9][0-9][0-9].json"))):
        d["gunler"].update(json.load(open(p, encoding="utf-8"))["gunler"])
    onceki = json.dumps(d["gunler"], sort_keys=True)
    n_inbox = inbox_aktar(log)
    if GERI_BASLANGIC:
        hedef = [g for g in is_gunleri(dt.date.fromisoformat(GERI_BASLANGIC), bugun) if not os.path.exists(arsiv_yolu(g))][:GERI_AZAMI]
    else:
        hedef = list(is_gunleri(bugun - dt.timedelta(days=SON_GUN), bugun))
    n_ind = indir(hedef, log)
    arsiv = sorted(tarih_coz("".join(p.split(os.sep)[-3:])[:8]) for p in glob.glob(os.path.join(ARSIV, "*", "*", "*.csv.gz")))
    yeni = [g for g in arsiv if g.isoformat() not in d["gunler"] or "hata" in d["gunler"][g.isoformat()]]
    for g in yeni:
        try:
            d["gunler"][g.isoformat()] = gun_ozeti(g)
        except Exception as e:
            d["gunler"][g.isoformat()] = {"hata": f"{type(e).__name__}: {e}"}
    # spot: baz alani eksik gunler icin
    eksik = [g for g, o in d["gunler"].items() if "hata" not in o and "spot" not in ((o.get("endeks_vadeli") or {}).get("XU030") or {})
             and "baz_not" not in ((o.get("endeks_vadeli") or {}).get("XU030") or {})]
    if eksik:
        spot = spot_cek(min(eksik))
        for g in eksik:
            spot_ekle(g, d["gunler"][g], spot)
    d["gunler"] = dict(sorted(d["gunler"].items()))
    log_satiri = f"inbox {n_inbox}, indirilen {n_ind}/{len(hedef)}, yeni ozet {len(yeni)}, hatalar {dict(log) or '-'}"
    os.makedirs(CIKTI_DIR, exist_ok=True)
    eski = json.loads(onceki)
    for yil in sorted({g[:4] for g in d["gunler"]}):
        yg = {g: o for g, o in d["gunler"].items() if g[:4] == yil}
        if yg == {g: o for g, o in eski.items() if g[:4] == yil}:
            continue                                            # degismeyen yil dosyasina dokunma (depo gecmisi sismesin)
        tmp = os.path.join(CIKTI_DIR, yil + ".json.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"not": "Betimleyici; alarm/karar girdisi degildir. Yon iddiasi yalniz on kayit + plasebo ile sinanir.",
                       "son_guncelleme_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "gunler": yg},
                      fh, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, os.path.join(CIKTI_DIR, yil + ".json"))
    gecerli = {g: o for g, o in d["gunler"].items() if "hata" not in o}
    if gecerli:
        with open(MD, "w", encoding="utf-8") as fh:
            fh.write(rapor({"gunler": gecerli}))
    print(log_satiri, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
