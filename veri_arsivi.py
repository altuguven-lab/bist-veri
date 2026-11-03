"""
VERI ARSIVI (03.11.2026) - SALT VERI TOPLAMA, test degil.
Amac: Gecmise donuk olarak sonradan TOPLANAMAYACAK verileri bugunden itibaren kalici arsivlemek ve
geriye dogru alinabilecek olanlari bir kez doldurmak. Ileride "bunu niye toplamadik" dememek icin.

Kipler (VERI_KIP ortam degiskeni ya da ilk arguman):
  gunluk       Her is gunu seans sonrasi:
               A) BIST100 + ana endeksler 15 dk barlari (son 5 gunden eksik gunler)  -> arsiv/intraday15/YYYY/MM/DD.json.gz
               B) Tum pazar (XUTUM, ~580 hisse) gunluk OHLCV, ham (duzeltmesiz)       -> arsiv/gunluk/YYYY/MM/DD.json.gz
               C) Borsa Istanbul endeks agirlik dosyasi (pay adedi, FDPO, agirlik) - degistiyse -> arsiv/endeks_agirlik/YYYY-MM-DD.csv.gz
               D) Kuresel/makro gosterge kapanislari                                    -> arsiv/kuresel/YYYY.json
               E) KAP'taki TUM bildirimlerin ust verisi (son 3 gun)                    -> arsiv/kap/YYYY/MM/DD.json.gz
  haber        Saatlik: data/haber_akisi.json'daki haberleri aylik dosyaya ekler (tekillestirir) -> arsiv/haber/YYYY-MM.jsonl
  geri_doldur  Bir kerelik (elle, birkac calisma): 15 dk barlar son 60 gun, 60 dk barlar son ~730 gun (BIST100),
               KAP tum bildirim ust verisi 2021-01-01'den bugune (MAX_GUN gun/calisma, kaldigi yerden devam).
Yalniz herkese acik kaynaklar; robots.txt'e uyulur; uye girisi gerektiren icerige dokunulmaz.
"""
import os, sys, io, csv, json, gzip, time, hashlib, datetime, urllib.request, urllib.robotparser, urllib.parse

KOK = "data/arsiv"
TR = datetime.timezone(datetime.timedelta(hours=3))
ENDEKSLER = ["XU100", "XU030", "XU050", "XBANK", "XUSIN", "XHOLD", "XUTUM", "XKTUM", "XUHIZ", "XUMAL", "XUTEK"]
KURESEL = {"VIX": "^VIX", "BRENT": "BZ=F", "ALTIN": "GC=F", "DXY": "DX-Y.NYB", "ABD10Y": "^TNX", "USDTRY": "USDTRY=X",
           "EURTRY": "EURTRY=X", "SP500": "^GSPC", "NASDAQ": "^IXIC", "DAX": "^GDAXI", "NIKKEI": "^N225", "HSI": "^HSI",
           "EEM": "EEM", "TUR_ETF": "TUR", "BTC": "BTC-USD", "GUMUS": "SI=F", "DOGALGAZ": "NG=F", "XU100": "XU100.IS"}
AGIRLIK_URL = "https://www.borsaistanbul.com/files/endeks_agirlik_ds_genel.csv"
TARAYICI = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"}
KAP_URL = "https://www.kap.org.tr/tr/api/disclosure/members/byCriteria"
KAP_H = {"Content-Type": "application/json", "Referer": "https://www.kap.org.tr/tr/bildirim-sorgu", "User-Agent": "bist-veri/1.0 (kisisel arastirma amacli)"}
KAP_ALAN = ["publishDate", "disclosureIndex", "kapTitle", "stockCodes", "relatedStocks", "subject", "summary", "disclosureClass",
            "disclosureType", "disclosureCategory", "period", "year", "isLate", "attachmentCount", "ruleType", "fundCode", "isOldKap"]
KAP_BEKLE = float(os.environ.get("KAP_BEKLE_SN", "2.0"))
HATA = []


# ------------------------------------------------------------------ yardimcilar
def yaz_gz(yol, nesne):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with gzip.open(yol, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(nesne, f, ensure_ascii=False, separators=(",", ":"))


def oku_json(yol, varsayilan):
    try:
        return json.load(open(yol, encoding="utf-8"))
    except Exception:
        return varsayilan


def izinli(url):
    p = urllib.parse.urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{p.scheme}://{p.netloc}/robots.txt", headers=TARAYICI), timeout=20) as r:
            rp.parse(r.read().decode("utf-8", errors="replace").splitlines())
    except Exception:
        rp.parse([])
    return rp.can_fetch("*", url)


def getir(url, basliklar, govde=None, zaman=60):
    son = None
    for d in range(3):
        try:
            req = urllib.request.Request(url, data=govde, headers=basliklar, method="POST" if govde else "GET")
            with urllib.request.urlopen(req, timeout=zaman) as r:
                return r.read()
        except Exception as e:
            son = e
            time.sleep((45 if "429" in str(e) else 5) * (d + 1))
    raise son


def agirlik_dosyasi():
    """(ham bayt, {endeks: [paylar]}) ya da (None, {})."""
    try:
        if not izinli(AGIRLIK_URL):
            raise PermissionError("robots_yasak")
        ham = getir(AGIRLIK_URL, TARAYICI)
        satir = list(csv.reader(io.StringIO(ham.decode("utf-8-sig", errors="replace")), delimiter=";"))
        uy = {}
        for s in satir[1:]:
            if len(s) > 9 and s[1].strip() and s[1].strip() not in ("INDEX CODE",):
                uy.setdefault(s[1].strip(), set()).add(s[9].split(".")[0].strip())
        return ham, {k: sorted(v) for k, v in uy.items()}
    except Exception as e:
        HATA.append(f"agirlik: {str(e)[:100]}")
        return None, {}


def evren():
    ham, uy = agirlik_dosyasi()
    xu100 = uy.get("XU100") or [s.split("#")[0].strip().upper() for s in open("config/bist100_uyeler.txt", encoding="utf-8") if s.split("#")[0].strip()]
    xutum = uy.get("XUTUM") or xu100
    return ham, xu100, xutum


def yf_indir(semboller, **kw):
    import yfinance as yf
    out = {}
    for i in range(0, len(semboller), 80):
        parca = semboller[i:i + 80]
        try:
            df = yf.download(parca, group_by="ticker", auto_adjust=False, threads=True, progress=False, **kw)
        except Exception as e:
            HATA.append(f"yf {parca[0]}..: {str(e)[:80]}")
            continue
        for s in parca:
            try:
                try:
                    d = df[s]
                except Exception:
                    d = df
                d = d.dropna(subset=["Close"])
                if not d.empty:
                    out[s] = d
            except Exception:
                pass
        time.sleep(2)
    return out


def bar_listesi(d, saat=True):
    rows = []
    for t, r in d.iterrows():
        ts = t.tz_convert(TR) if getattr(t, "tzinfo", None) else t
        rows.append([ts.strftime("%Y-%m-%d %H:%M") if saat else ts.strftime("%Y-%m-%d"),
                     *[None if r[k] != r[k] else round(float(r[k]), 4) for k in ("Open", "High", "Low", "Close")],
                     None if r["Volume"] != r["Volume"] else int(r["Volume"])])
    return rows


# ------------------------------------------------------------------ A) 15 dk
def intraday(semboller, period, aralik, hedef_klasor, gunluk_dosya=True):
    tick = [s + ".IS" for s in semboller]
    veri = yf_indir(tick, period=period, interval=aralik)
    if not gunluk_dosya:                                  # 60 dk geri doldurma: sembol basina tek dosya
        for t, d in veri.items():
            yaz_gz(f"{KOK}/{hedef_klasor}/{t.replace('.IS', '')}.json.gz", bar_listesi(d))
        return len(veri)
    gunler = {}
    for t, d in veri.items():
        for row in bar_listesi(d):
            gunler.setdefault(row[0][:10], {}).setdefault(t.replace(".IS", ""), []).append([row[0][11:], *row[1:]])
    bugun = datetime.datetime.now(TR).strftime("%Y-%m-%d")
    yazilan = 0
    for g, v in gunler.items():
        yol = f"{KOK}/{hedef_klasor}/{g[:4]}/{g[5:7]}/{g[8:]}.json.gz"
        if os.path.exists(yol) and g != bugun:
            continue
        yaz_gz(yol, {"tarih": g, "aralik": aralik, "saat_dilimi": "Europe/Istanbul", "kaynak": "yfinance", "veri": v})
        yazilan += 1
    return yazilan


# ------------------------------------------------------------------ B) gunluk OHLCV
def gunluk_ohlcv(xutum):
    veri = yf_indir([s + ".IS" for s in xutum], period="5d", interval="1d")
    gunler = {}
    for t, d in veri.items():
        for row in bar_listesi(d, saat=False):
            gunler.setdefault(row[0], {})[t.replace(".IS", "")] = row[1:]
    for g, v in gunler.items():
        yaz_gz(f"{KOK}/gunluk/{g[:4]}/{g[5:7]}/{g[8:]}.json.gz",
               {"tarih": g, "alanlar": ["acilis", "yuksek", "dusuk", "kapanis", "hacim"], "duzeltme": "yok (ham)", "kaynak": "yfinance", "veri": v})
    return len(gunler), len(veri)


# ------------------------------------------------------------------ C) endeks agirlik
def agirlik_arsivle(ham):
    if not ham:
        return False
    kl = f"{KOK}/endeks_agirlik"
    os.makedirs(kl, exist_ok=True)
    ozet_yol = f"{kl}/son_ozet.json"
    oz = oku_json(ozet_yol, {})
    h = hashlib.sha256(ham).hexdigest()
    if oz.get("sha256") == h:
        return False
    g = datetime.datetime.now(TR).strftime("%Y-%m-%d")
    with gzip.open(f"{kl}/{g}.csv.gz", "wb", compresslevel=9) as f:
        f.write(ham)
    json.dump({"sha256": h, "tarih": g}, open(ozet_yol, "w"))
    return True


# ------------------------------------------------------------------ D) kuresel
def kuresel():
    veri = yf_indir(list(KURESEL.values()), period="10d", interval="1d")
    ters = {v: k for k, v in KURESEL.items()}
    yillar = {}
    for t, d in veri.items():
        for row in bar_listesi(d, saat=False):
            yillar.setdefault(row[0][:4], {}).setdefault(row[0], {})[ters[t]] = row[4]
    for y, gun in yillar.items():
        yol = f"{KOK}/kuresel/{y}.json"
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        mevcut = oku_json(yol, {})
        for g, v in gun.items():
            mevcut.setdefault(g, {}).update(v)
        json.dump(dict(sorted(mevcut.items())), open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    return len(veri)


# ------------------------------------------------------------------ E) KAP
def kap_gun(gun):
    g = json.dumps({"fromDate": gun.isoformat(), "toDate": gun.isoformat(), "mkkMemberOidList": [], "subjectList": []}).encode("utf-8")
    liste = json.loads(getir(KAP_URL, KAP_H, g, zaman=40).decode("utf-8"))
    return [{k: b.get(k) for k in KAP_ALAN if b.get(k) not in (None, "", "-")} for b in liste]


def kap_arsivle(gunler, ustune_yaz=False):
    yazilan, ardisik = 0, 0
    for gun in gunler:
        yol = f"{KOK}/kap/{gun:%Y/%m/%d}.json.gz"
        if os.path.exists(yol) and not ustune_yaz:
            continue
        try:
            b = kap_gun(gun)
            yaz_gz(yol, {"tarih": gun.isoformat(), "adet": len(b), "bildirimler": b})
            yazilan, ardisik = yazilan + 1, 0
        except Exception as e:
            HATA.append(f"kap {gun}: {str(e)[:80]}")
            ardisik += 1
            if ardisik >= 3:
                break
        time.sleep(KAP_BEKLE)
    return yazilan


# ------------------------------------------------------------------ haber
def haber():
    h = oku_json("data/haber_akisi.json", {})
    yeni = 0
    aylar = {}
    for x in h.get("haberler", []):
        z = (x.get("zaman_utc") or x.get("yayin_zamani") or datetime.datetime.now(datetime.timezone.utc).isoformat())[:7]
        aylar.setdefault(z if len(z) == 7 and z[4] == "-" else datetime.datetime.now(TR).strftime("%Y-%m"), []).append(x)
    for ay, liste in aylar.items():
        yol = f"{KOK}/haber/{ay}.jsonl"
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        gorulen = set()
        if os.path.exists(yol):
            for s in open(yol, encoding="utf-8"):
                try:
                    o = json.loads(s)
                    gorulen.add(o.get("link") or o.get("baslik"))
                except Exception:
                    pass
        with open(yol, "a", encoding="utf-8") as f:
            for x in liste:
                k = x.get("link") or x.get("baslik")
                if k and k not in gorulen:
                    x = dict(x, arsiv_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
                    f.write(json.dumps(x, ensure_ascii=False) + "\n")
                    gorulen.add(k)
                    yeni += 1
    return yeni


# ------------------------------------------------------------------ ana
def main():
    kip = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VERI_KIP", "gunluk")).strip()
    os.makedirs(KOK, exist_ok=True)
    ozet_yol = f"{KOK}/durum.json"
    durum = oku_json(ozet_yol, {})
    bugun = datetime.datetime.now(TR).date()
    rapor = {"kip": kip, "zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if kip == "haber":
        rapor["haber_yeni"] = haber()
    elif kip == "gunluk":
        ham, xu100, xutum = evren()
        rapor["agirlik_yeni_surum"] = agirlik_arsivle(ham)
        rapor["intraday15_gun"] = intraday(sorted(set(xu100)) + ENDEKSLER, "5d", "15m", "intraday15")
        rapor["gunluk_gun_sembol"] = gunluk_ohlcv(sorted(set(xutum) | set(ENDEKSLER)))
        rapor["kuresel_sembol"] = kuresel()
        rapor["kap_gun"] = kap_arsivle([bugun - datetime.timedelta(days=i) for i in (2, 1, 0)], ustune_yaz=True)
        rapor["evren"] = {"xu100": len(xu100), "xutum": len(xutum)}
    elif kip == "geri_doldur":
        ham, xu100, _ = evren()
        sem = sorted(set(xu100)) + ENDEKSLER
        if not durum.get("intraday15_geri"):
            rapor["intraday15_gun"] = intraday(sem, "60d", "15m", "intraday15")
            durum["intraday15_geri"] = bugun.isoformat()
        if not durum.get("intraday60_geri"):
            rapor["intraday60_sembol"] = intraday(sem, "730d", "60m", "intraday60_geri", gunluk_dosya=False)
            durum["intraday60_geri"] = bugun.isoformat()
        max_gun = int(os.environ.get("MAX_GUN", "900"))
        bas = datetime.date(2021, 1, 1)
        eksik = [bas + datetime.timedelta(days=i) for i in range((bugun - bas).days + 1)]
        eksik = [g for g in eksik if not os.path.exists(f"{KOK}/kap/{g:%Y/%m/%d}.json.gz")][:max_gun]
        rapor["kap_geri_yazilan"] = kap_arsivle(eksik)
        tum = (bugun - bas).days + 1
        rapor["kap_kalan_gun"] = sum(1 for i in range(tum) if not os.path.exists(f"{KOK}/kap/{(bas + datetime.timedelta(days=i)):%Y/%m/%d}.json.gz"))
    rapor["hatalar"] = HATA[-30:]
    durum[f"son_{kip}"] = rapor
    json.dump(durum, open(ozet_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(rapor, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
