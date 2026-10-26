#!/usr/bin/env python3
"""TEMEL CARPAN GOZLEM (14.10.2026) - SALT OLCUM, Pine'a dokunmaz, alarm uretmez (Kulucka/IP-3 uyumlu).
30 sembol icin F/K ve PD/DD'yi TL ve USD bazinda, 2021 sonrasi tarihsel dagilimiyla birlikte uretir.
Girdi : data/temel/ham_<SEMBOL>.json (temel_veri_topla.py), yfinance fiyat ve USDTRY.
Cikti : data/temel_carpan.json, temel_carpan.md   (TAVSIYE DEGILDIR, aday taramasidir)

YONTEM (sonuclara bakmadan sabit):
 - Net kar (3Z) ve ozkaynak (2O) YTD kumulatif gelir. TTM = YTD(y,p) + YTD(y-1,12) - YTD(y-1,p).
 - Bilanco kullanilabilirlik gecikmesi (yarina bakma onyargisini onlemek icin): 03:+60g, 06:+70g, 09:+60g, 12:+70g.
 - Piyasa degeri = split-duzeltmeli kapanis x guncel hisse adedi (odenmis sermaye / 1 TL nominal). Bedelli
   sermaye artirimi olan hisselerde gecmis deger sapabilir.
 - USD piyasa degeri = TL piyasa degeri / o gunun USDTRY'si. USD kar/ozkaynak servisten doner (donem kuruyla).
 - F/K = piyasa degeri / TTM net kar (TTM<=0 ise yok). PD/DD = piyasa degeri / son kullanilabilir ozkaynak.
 - Dip aday: PD/DD yuzdelik<=20 (TL VE USD), banka disi icin F/K yuzdelik<=20 (TL VE USD) de gerekir;
   kalite filtresi: TTM kar (USD) son 2 ceyrekten beri >= %90'i ve ozkaynak (USD) 4 ceyrek once >= %90'i.
 - Yuzdelik: hissenin KENDI 2021 sonrasi gunluk dagilimina gore (guncel deger kac yuzde dilimde).
 - UYARI: TMS 29 enflasyon muhasebesi 2023 sonu sonrasi bilanco birimlerini degistirdi; TL carpanlari donemler arasi
   karisik birimle hesaplanir, USD carpanlari daha kararlidir. Dongusel hisselerde dusuk F/K zirve kari olabilir.
"""
import json, os, sys, math
from datetime import datetime, timezone, timedelta, date

SEMBOLLER = ["AKBNK","YKBNK","GARAN","ISCTR","SAHOL","KCHOL","THYAO","TAVHL","EREGL","ASELS","ASTOR","MGROS",
 "BIMAS","TUPRS","TOASO","FROTO","ENKAI","TTKOM","AEFES","PGSUS","HALKB","VAKBN","OTKAR","PETKM","SISE",
 "EKGYO","TRMET","ALARK","ENJSA","ULKER"]
BANKALAR = {"AKBNK","YKBNK","GARAN","ISCTR","HALKB","VAKBN"}

# 26.10 EKI: EVREN=BIST100 ortam degiskeniyle 100 sembol (config/bist100_uyeler.txt). Varsayilan davranis (30 sembol) DEGISMEDI.
_EVREN = os.environ.get("EVREN", "")
if _EVREN == "BIST100":
    SEMBOLLER = [l.split("#")[0].strip().upper().replace(".IS", "") for l in open("config/bist100_uyeler.txt", encoding="utf-8") if l.split("#")[0].strip()]
    BANKALAR = BANKALAR | {"TSKB", "ALBRK"}
YEDEK = {"TRMET": "KOZAA", "TRALT": "KOZAL"}
GECIKME = {3: 60, 6: 70, 9: 60, 12: 70}
DIP_YUZDELIK = 20.0
MIN_GUN = 250
POLITIKA_FAIZI = 37.0   # % (TCMB politika faizi, PPK 22.10.2026 sonrasi elle guncellenir); kazanc getirisi farki icin
CIKTI = "data/temel"
BAS = date(2021, 1, 1)
TMS29_BAS = date(2024, 4, 1)   # FY2023 enflasyon duzeltmeli bilanco sonrasi: ikinci (kararli) pencere

def f(x):
    try: return float(x)
    except Exception: return None

def seri(ham, borsa, kod):
    """{(yil,per): YTD deger}"""
    k = ((ham.get(borsa) or {}).get("kalemler") or {}).get(kod) or {}
    out = {}
    for ky, v in (k.get("v") or {}).items():
        y, p = ky.split("/"); v = f(v)
        if v is not None: out[(int(y), int(p))] = v
    return out

def ttm_ve_ozkaynak(ham, borsa):
    """Kullanilabilirlik tarihli liste: [(tarih, ttm_kar, ozkaynak)]"""
    kar, oz = seri(ham, borsa, "3Z"), seri(ham, borsa, "2O")
    out = []
    for (y, p) in sorted(set(kar) | set(oz)):
        ttm = None
        if (y, p) in kar:
            if p == 12: ttm = kar[(y, p)]
            elif (y - 1, 12) in kar and (y - 1, p) in kar:
                ttm = kar[(y, p)] + kar[(y - 1, 12)] - kar[(y - 1, p)]
        ay = {3: 3, 6: 6, 9: 9, 12: 12}[p]
        donem_sonu = date(y, ay, 28) + timedelta(days=4); donem_sonu -= timedelta(days=donem_sonu.day)  # ay sonu
        out.append({"tarih": donem_sonu + timedelta(days=GECIKME[p]), "donem": f"{y}/{p:02d}",
                    "ttm": ttm, "oz": oz.get((y, p))})
    return out

def gunluk_oran(fiyat_serisi, usd_serisi, ham, sembol):
    """fiyat_serisi: {date: kapanis}; usd_serisi: {date: usdtry}. Doner (tarih listesi, dict seriler, kuyruk bilgisi)."""
    tl = ttm_ve_ozkaynak(ham, "TRY"); us = ttm_ve_ozkaynak(ham, "USD")
    sermaye = seri(ham, "TRY", "2OA")
    if not sermaye: return None
    adet = sermaye[max(sermaye)]          # 1 TL nominal varsayimi
    gunler = sorted(g for g in fiyat_serisi if g >= BAS)
    res = {k: [] for k in ("fk_tl", "fk_usd", "pddd_tl", "pddd_usd")}
    tg = []
    def son(liste, g):
        s = [x for x in liste if x["tarih"] <= g]
        return s[-1] if s else None
    for g in gunler:
        mc = fiyat_serisi[g] * adet
        kur = usd_serisi.get(g)
        a, b = son(tl, g), son(us, g)
        # son gecerli ttm / ozkaynak (en yeni kayit TTM'si eksik olabilir)
        def gecerli(liste, anahtar):
            for x in reversed([x for x in liste if x["tarih"] <= g]):
                if x[anahtar] is not None: return x[anahtar]
            return None
        ttm_tl, oz_tl = gecerli(tl, "ttm"), gecerli(tl, "oz")
        ttm_us, oz_us = gecerli(us, "ttm"), gecerli(us, "oz")
        mcu = mc / kur if kur else None
        res["fk_tl"].append(mc / ttm_tl if ttm_tl and ttm_tl > 0 else None)
        res["pddd_tl"].append(mc / oz_tl if oz_tl and oz_tl > 0 else None)
        res["fk_usd"].append(mcu / ttm_us if mcu and ttm_us and ttm_us > 0 else None)
        res["pddd_usd"].append(mcu / oz_us if mcu and oz_us and oz_us > 0 else None)
        tg.append(g)
    return tg, res, {"tl": tl, "usd": us, "adet": adet}

def istat(v):
    xs = [x for x in v if x is not None]
    if len(xs) < MIN_GUN or v[-1] is None: return None
    son = v[-1]; xs_s = sorted(xs)
    yuzdelik = 100.0 * sum(1 for x in xs if x <= son) / len(xs)
    lg = [math.log(x) for x in xs]; m = sum(lg) / len(lg)
    sd = (sum((x - m) ** 2 for x in lg) / len(lg)) ** 0.5
    z = (math.log(son) - m) / sd if sd > 0 else None
    return {"son": round(son, 2), "medyan": round(xs_s[len(xs_s) // 2], 2), "min": round(xs_s[0], 2),
            "maks": round(xs_s[-1], 2), "yuzdelik": round(yuzdelik, 1), "z": None if z is None else round(z, 2), "n": len(xs)}

def kalite(bilgi):
    """USD TTM kar ve ozkaynak trend filtresi."""
    us = bilgi["usd"]
    ttm = [x for x in us if x["ttm"] is not None]
    oz = [x for x in us if x["oz"] is not None]
    ok_kar = ok_oz = None
    if len(ttm) >= 3: ok_kar = ttm[-1]["ttm"] >= 0.9 * ttm[-3]["ttm"] if ttm[-3]["ttm"] > 0 else ttm[-1]["ttm"] > 0
    if len(oz) >= 5: ok_oz = oz[-1]["oz"] >= 0.9 * oz[-5]["oz"]
    return ok_kar, ok_oz

def fiyatlari_cek():
    import yfinance as yf
    out, usd = {}, {}
    syms = SEMBOLLER + ["TRALT"]
    for s in SEMBOLLER:
        for deneme in (s, YEDEK.get(s)):
            if not deneme: continue
            try:
                df = yf.download(f"{deneme}.IS", start="2020-12-01", auto_adjust=False, progress=False, threads=False)
                if df is not None and len(df) > 100:
                    c = df["Close"]; c = c.iloc[:, 0] if hasattr(c, "columns") else c
                    out[s] = {d.date(): float(v) for d, v in c.dropna().items()}
                    break
            except Exception as ex:
                print("fiyat hata", s, ex, file=sys.stderr)
    try:
        df = yf.download("USDTRY=X", start="2020-12-01", progress=False, threads=False)
        c = df["Close"]; c = c.iloc[:, 0] if hasattr(c, "columns") else c
        usd = {d.date(): float(v) for d, v in c.dropna().items()}
    except Exception as ex:
        print("usdtry hata", ex, file=sys.stderr)
    return out, usd


def son_deger(v):
    """YALNIZ son gunun degeri; yoksa None (eski degere sessizce dusmez)."""
    return v[-1] if v else None

def ek_olcular(res, bilgi, fiyat_son, temettu_12ay):
    """ACIKLAYICI sutunlar (aday kriterine GIRMEZ). Tumu son gune ait anlik degerler."""
    us = bilgi["usd"]
    out = {}
    ttm_l = [x for x in us if x["ttm"] is not None]
    oz_l = [x for x in us if x["oz"] is not None]
    roe = None
    if ttm_l and oz_l:
        oz_son = oz_l[-1]["oz"]
        oz_once = next((x["oz"] for x in reversed(oz_l[:-1]) if x["donem"][:4] == str(int(oz_l[-1]["donem"][:4]) - 1)
                        and x["donem"][5:] == oz_l[-1]["donem"][5:]), None)
        ort = (oz_son + oz_once) / 2 if oz_once else oz_son
        if ort > 0: roe = 100.0 * ttm_l[-1]["ttm"] / ort
    out["roe_usd"] = None if roe is None else round(roe, 1)
    pd_usd = son_deger(res["pddd_usd"])
    out["pddd_roe"] = round(pd_usd / (roe / 100.0), 1) if (pd_usd and roe and roe > 0) else None
    # normalize F/K: son piyasa degeri(USD) / son 3 yillik (12. ay) TTM USD kar ortalamasi
    yillik = [x["ttm"] for x in us if x["donem"].endswith("/12") and x["ttm"] is not None][-3:]
    fk_usd = son_deger(res["fk_usd"]); 
    mcu = (pd_usd * oz_l[-1]["oz"]) if (pd_usd and oz_l) else None
    out["norm_fk_usd"] = round(mcu / (sum(yillik) / len(yillik)), 1) if (mcu and len(yillik) == 3 and sum(yillik) > 0) else None
    out["norm_fk_yil_sayisi"] = len(yillik)
    fk_tl = son_deger(res["fk_tl"])
    kg = 100.0 / fk_tl if fk_tl else None
    out["kazanc_getirisi"] = None if kg is None else round(kg, 1)
    out["kazanc_getirisi_eksi_faiz"] = None if kg is None else round(kg - POLITIKA_FAIZI, 1)
    out["temettu_verimi"] = None if (temettu_12ay is None or not fiyat_son) else round(100.0 * temettu_12ay / fiyat_son, 2)
    return out

BORC_ATLA = {"AKBNK","YKBNK","GARAN","ISCTR","HALKB","VAKBN","SAHOL","KCHOL"}   # banka + finans kolu konsolide holding: FD anlamsiz
if _EVREN == "BIST100":
    BORC_ATLA = BORC_ATLA | {"TSKB", "ALBRK", "ANSGR", "TURSG", "ISMEN", "AGHOL", "DOHOL"}

def borc_nakit_olculer(ham, mcap_tl, mcap_usd):
    """Banka disi / holding disi: FD/FAVOK, net borc/FAVOK, FD/Satis, FAVOK ve net kar marji, FCF verimi, kar kalitesi.
    Akis kalemleri YTD -> TTM; bakiye kalemleri son donem. FD = piyasa degeri + net borc + azinlik.
    UYARI: finansal borc kira (TFRS16) borclarini icerir; FAVOK TFRS16 sonrasi (kira gideri amortismanda). Tutarlidir ama
    'kira oncesi FAVOK' karsilastirmasi icin yanlis olur. FCF = isletme nakit akisi + sabit sermaye yatirimi."""
    out = {}
    for borsa, mc in (("TRY", mcap_tl), ("USD", mcap_usd)):
        def ser(k): return seri(ham, borsa, k)
        fa, am, st, ni = ser("3DF"), ser("4B") or ser("4CAB"), ser("3C"), ser("3Z")
        ocf, capex = ser("4C"), ser("4CAI")
        if not fa or not mc: continue
        q = max(fa)
        def t(k):
            y, p = q
            if p == 12: return k.get(q)
            a, b, c2 = k.get(q), k.get((y - 1, 12)), k.get((y - 1, p))
            return None if None in (a, b, c2) else a + b - c2
        def stok(kod): return ser(kod).get(q)
        fav = None if t(fa) is None or t(am) is None else t(fa) + t(am)
        borc = sum(stok(k) or 0.0 for k in ("2AA", "2BA", "2AAG", "2BB"))
        nakit = (stok("1AA") or 0.0) + (stok("1AB") or 0.0)
        oz_top, oz_ana = stok("2N"), stok("2O")
        azn = (oz_top - oz_ana) if (oz_top is not None and oz_ana is not None) else 0.0
        netborc = borc - nakit
        fd = mc + netborc + azn
        satis, nk, o, cx = t(st), t(ni), t(ocf), t(capex)
        sfx = "tl" if borsa == "TRY" else "usd"
        out[f"fd_favok_{sfx}"] = None if not fav or fav <= 0 or fd <= 0 else round(fd / fav, 1)
        if borsa == "USD":
            out["net_borc_favok"] = None if not fav or fav <= 0 else round(netborc / fav, 1)
            out["fd_satis"] = None if not satis or satis <= 0 or fd <= 0 else round(fd / satis, 2)
            out["favok_marji"] = None if not fav or not satis or satis <= 0 else round(100 * fav / satis, 1)
            out["net_kar_marji"] = None if nk is None or not satis or satis <= 0 else round(100 * nk / satis, 1)
            out["fcf_verimi"] = None if o is None or cx is None or mc <= 0 else round(100 * (o + cx) / mc, 1)
            out["nakit_kar_orani"] = None if o is None or not nk or nk <= 0 else round(o / nk, 2)
            out["bilanco_donemi"] = f"{q[0]}/{q[1]:02d}"
    return out

def banka_olculer(ham):
    """Banka sablonu (TRY): oranlar para biriminden bagimsiz. NPL ve SYR bu servisten GELMEZ (takipteki kredi kalemi 0 doner);
    risk maliyeti = karsilik gideri / ortalama krediler, ozkaynak/aktif SYR icin yalniz kaba vekildir."""
    k = lambda kod: seri(ham, "TRY", kod)
    z, kr, mev, nfg, uc, gel, kars, gid, ni = k("1Z"), k("1AFA"), k("2A"), k("3C"), k("3CA"), k("3CE"), k("3CF"), k("3CG"), k("3Z")
    if not nfg or not z: return None
    q = max(nfg)
    def t(s_):
        y, p = q
        if p == 12: return s_.get(q)
        a, b, c2 = s_.get(q), s_.get((y - 1, 12)), s_.get((y - 1, p))
        return None if None in (a, b, c2) else a + b - c2
    def ort(s_):
        a, b = s_.get(q), s_.get((q[0] - 1, q[1]))
        return (a + b) / 2 if (a is not None and b is not None) else s_.get(q)
    o = {}
    nim = t(nfg); za = ort(z); kra = ort(kr)
    o["nim_vekil"] = None if nim is None or not za else round(100 * nim / za, 2)
    o["risk_maliyeti"] = None if t(kars) is None or not kra else round(100 * t(kars) / kra, 2)
    o["ucret_payi"] = None if t(uc) is None or not t(gel) else round(100 * t(uc) / t(gel), 1)
    o["maliyet_gelir"] = None if t(gid) is None or not t(gel) else round(100 * t(gid) / t(gel), 1)
    o["kredi_mevduat"] = None if not kr.get(q) or not mev.get(q) else round(100 * kr[q] / mev[q], 1)
    oz = seri(ham, "TRY", "2O").get(q)
    o["ozkaynak_aktif"] = None if not oz or not z.get(q) else round(100 * oz / z[q], 1)
    o["roa"] = None if t(ni) is None or not za else round(100 * t(ni) / za, 2)
    o["bilanco_donemi"] = f"{q[0]}/{q[1]:02d}"
    return o

def temettu_cek():
    """Son 12 ay hisse basi brut temettu toplami (TL). Alinamazsa None; sessizce 0 sayilmaz."""
    out = {}
    try:
        import yfinance as yf
    except Exception:
        return out
    bitis = datetime.now(timezone.utc).date(); bas = bitis - timedelta(days=365)
    for s in SEMBOLLER:
        try:
            d = yf.Ticker(f"{s}.IS").dividends
            if d is None: continue
            tops = 0.0
            for t, v in d.items():
                if bas <= t.date() <= bitis: tops += float(v)
            out[s] = tops if tops > 0 else None   # 0 = Yahoo'da kayit yok; 'temettu yok' diye YAZILMAZ
        except Exception as ex:
            print("temettu hata", s, ex, file=sys.stderr)
    return out

def test_verisi():
    """SCHUMPETER-benzeri test modu: sentetik fiyat/kur ve ham veri."""
    import random
    random.seed(1)
    g = date(2021, 1, 4); fiy, kur = {}, {}; p, k = 10.0, 7.5
    while g <= date(2026, 10, 13):
        if g.weekday() < 5:
            p *= 1 + random.gauss(0.0008, 0.02); k *= 1 + 0.0007; fiy[g] = p; kur[g] = k
        g += timedelta(days=1)
    return fiy, kur

def sentetik_ham(carpan_usd=1.0):
    ham = {}
    for b, kur in (("TRY", 1.0), ("USD", 1 / 30.0)):
        kar, oz, sermaye = {}, {}, {}
        for y in range(2020, 2027):
            for p in (3, 6, 9, 12):
                if (y, p) > (2026, 6): continue
                kar[f"{y}/{p:02d}"] = str(1e9 * (y - 2019) * (p / 12) * kur)
                oz[f"{y}/{p:02d}"] = str(1e10 * (y - 2019) * kur)
                sermaye[f"{y}/{p:02d}"] = "1000000000"
        ham[b] = {"grup": "TEST", "kalemler": {"3Z": {"ad": "k", "v": kar}, "2O": {"ad": "o", "v": oz}, "2OA": {"ad": "s", "v": sermaye}}}
    return ham

def main():
    test = os.environ.get("TEMEL_TEST") == "1"
    if test:
        fy, kur = test_verisi(); fiyatlar = {s: fy for s in SEMBOLLER[:3]}
        hamlar = {s: sentetik_ham() for s in SEMBOLLER[:3]}
    else:
        fiyatlar, kur = fiyatlari_cek()
        hamlar = {}
        for s in SEMBOLLER:
            yol = f"{CIKTI}/ham_{s}.json"
            if os.path.exists(yol): hamlar[s] = json.load(open(yol, encoding="utf-8"))
    temettu = {} if test else temettu_cek()
    sonuc, atlanan = {}, []
    for s in SEMBOLLER:
        if s not in hamlar or s not in fiyatlar:
            atlanan.append(f"{s}: " + ("ham yok" if s not in hamlar else "fiyat yok")); continue
        r = gunluk_oran(fiyatlar[s], kur, hamlar[s], s)
        if not r: atlanan.append(f"{s}: sermaye kalemi yok"); continue
        tg, res, bilgi = r
        ist = {k: istat(v) for k, v in res.items()}
        ist2 = {k: istat([x for g, x in zip(tg, v) if g >= TMS29_BAS]) for k, v in res.items()}
        ok_kar, ok_oz = kalite(bilgi)
        ek = ek_olcular(res, bilgi, fiyatlar[s][max(fiyatlar[s])], temettu.get(s) if temettu else None)
        if s in BANKALAR:
            try: ek["banka"] = banka_olculer(hamlar[s])
            except Exception as ex: ek["banka"] = {"hata": str(ex)[:100]}
        if s not in BORC_ATLA:
            try:
                fson = fiyatlar[s][max(fiyatlar[s])]; kson = kur[max(kur)] if kur else None
                mc_tl = fson * bilgi["adet"]; mc_usd = (mc_tl / kson) if kson else None
                ek["borc_nakit"] = borc_nakit_olculer(hamlar[s], mc_tl, mc_usd)
            except Exception as ex:
                ek["borc_nakit"] = {"hata": str(ex)[:100]}
        yillik = {}
        for yil in range(2021, tg[-1].year + 1):
            idx = [i for i, g in enumerate(tg) if g.year == yil]
            if not idx: continue
            i = idx[-1]
            yillik[str(yil) if yil < tg[-1].year else f"{yil} (güncel)"] = {k: (round(v[i], 2) if v[i] is not None else None) for k, v in res.items() if k in ("fk_tl", "fk_usd", "pddd_tl", "pddd_usd")}
        banka = s in BANKALAR
        def dip(k): return ist.get(k) and ist[k]["yuzdelik"] <= DIP_YUZDELIK
        dip_pd = bool(dip("pddd_tl") and dip("pddd_usd"))
        dip_fk = bool(dip("fk_tl") and dip("fk_usd"))
        def dip2(k): return ist2.get(k) and ist2[k]["yuzdelik"] <= DIP_YUZDELIK
        dip_pd2 = bool(dip2("pddd_tl") and dip2("pddd_usd"))
        dip_fk2 = bool(dip2("fk_tl") and dip2("fk_usd"))
        aday = dip_pd and (banka or dip_fk)
        aday2 = dip_pd2 and (banka or dip_fk2)
        sonuc[s] = {"banka": banka, "son_tarih": str(tg[-1]) if tg else None, "ek_olculer": ek, "yillik": yillik, "istatistik": ist, "istatistik_tms29": ist2, "dip_pddd_tms29": dip_pd2, "dip_fk_tms29": dip_fk2, "aday_tms29": aday2,
                    "kalite_kar_usd": ok_kar, "kalite_ozkaynak_usd": ok_oz,
                    "dip_pddd": dip_pd, "dip_fk": dip_fk, "aday": aday,
                    "aday_kaliteli": bool(aday and ok_kar is not False and ok_oz is not False),
                    "son_bilanco": (bilgi["tl"][-1]["donem"] if bilgi["tl"] else None)}
    kayit = {"olusturma_utc": datetime.now(timezone.utc).isoformat(), "mod": "TEST" if test else "GERCEK",
             "dip_yuzdelik_esigi": DIP_YUZDELIK, "atlanan": atlanan, "semboller": sonuc}
    json.dump(kayit, open(("data/temel_carpan_bist100.json" if _EVREN == "BIST100" else "data/temel_carpan.json") if not test else "/tmp/temel_carpan_test.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    md = rapor(kayit)
    open(("temel_carpan_bist100.md" if _EVREN == "BIST100" else "temel_carpan.md") if not test else "/tmp/temel_carpan_test.md", "w", encoding="utf-8").write(md)
    print(md[:3000])

def sat(s, d, k):
    x = d["istatistik"].get(k)
    return f"{x['son']} (%{x['yuzdelik']:.0f}, z {x['z']})" if x else "-"

def rapor(kayit):
    S = kayit["semboller"]
    L = ["# Temel çarpan gözlemi (SALT ÖLÇÜM)", "",
         f"Üretim: {kayit['olusturma_utc'][:16]} UTC · mod {kayit['mod']} · dip eşiği: kendi 2021 sonrası dağılımında alt %{kayit['dip_yuzdelik_esigi']:.0f}",
         "Pine'a dokunmaz, alarm üretmez. **Tavsiye değildir**, aday taramasıdır. Yüzdelik: hissenin kendi tarihine göre guncel deger kaç % dilimde (düşük = tarihinin ucuz tarafı).",
         "TL çarpanları TMS 29 nedeniyle dönemler arası karışık birimdedir; USD çarpanları daha kararlıdır. Döngüsel hisselerde düşük F/K zirve kârı olabilir.", ""]
    ad = [(s, d) for s, d in S.items() if d["aday"]]
    L += ["## Dip adayları (PD/DD TL ve USD alt dilimde; banka dışında F/K de)", "",
          "| Hisse | PD/DD TL | PD/DD USD | F/K TL | F/K USD | Kâr trendi (USD) | Özkaynak trendi (USD) | Kaliteli |", "|---|---|---|---|---|---|---|---|"]
    for s, d in sorted(ad, key=lambda x: x[1]["istatistik"]["pddd_usd"]["yuzdelik"]):
        L.append(f"| {s} | {sat(s,d,'pddd_tl')} | {sat(s,d,'pddd_usd')} | {sat(s,d,'fk_tl')} | {sat(s,d,'fk_usd')} | "
                 f"{d['kalite_kar_usd']} | {d['kalite_ozkaynak_usd']} | {'EVET' if d['aday_kaliteli'] else 'HAYIR'} |")
    if not ad: L.append("| (aday yok) | | | | | | | |")
    ad2 = [(s, d) for s, d in S.items() if d.get("aday_tms29")]
    L += ["", "## Dip adayları, yalnız TMS 29 sonrası pencere (04.2024+)", "",
          "Özkaynak 2024 öncesi enflasyon düzeltmesizdi, bu yüzden 2021-23 PD/DD yapay yüksek olabilir ve bugünkü değer olduğundan 'ucuz' görünür. Bu pencere o yanlılığı azaltır.", "",
          "| Hisse | PD/DD USD (2024+) | F/K USD (2024+) | Kâr trendi | Özkaynak trendi |", "|---|---|---|---|---|"]
    for s, d in sorted(ad2, key=lambda x: x[1]["istatistik_tms29"]["pddd_usd"]["yuzdelik"]):
        t = d["istatistik_tms29"]; fk = t.get("fk_usd")
        L.append(f"| {s} | {t['pddd_usd']['son']} (%{t['pddd_usd']['yuzdelik']:.0f}, z {t['pddd_usd']['z']}) | "
                 f"{(str(fk['son']) + ' (%' + format(fk['yuzdelik'], '.0f') + ')') if fk else '-'} | {d['kalite_kar_usd']} | {d['kalite_ozkaynak_usd']} |")
    if not ad2: L.append("| (aday yok) | | | | |")
    def t2(d, k):
        x = (d.get("istatistik_tms29") or {}).get(k)
        return f"%{x['yuzdelik']:.0f}" if x else "-"
    L += ["", "## Tüm evren", "", "| Hisse | PD/DD TL | PD/DD USD | F/K TL | F/K USD | PD/DD USD yüzdelik 2024+ | F/K USD yüzdelik 2024+ | Son bilanço | Dip PD | Dip PD 2024+ |", "|---|---|---|---|---|---|---|---|---|---|"]
    for s, d in sorted(S.items(), key=lambda x: (x[1]["istatistik"].get("pddd_usd") or {"yuzdelik": 999})["yuzdelik"]):
        L.append(f"| {s} | {sat(s,d,'pddd_tl')} | {sat(s,d,'pddd_usd')} | {sat(s,d,'fk_tl')} | {sat(s,d,'fk_usd')} | {t2(d,'pddd_usd')} | {t2(d,'fk_usd')} | {d['son_bilanco']} | {'x' if d['dip_pddd'] else ''} | {'x' if d.get('dip_pddd_tms29') else ''} |")
    L += ["", "## Açıklayıcı ek ölçüler (aday kriterine GİRMEZ)", "",
          "ROE: son 12 ay USD net kâr / ortalama USD özkaynak. PD/DD÷ROE: düşük = kârlılığa göre ucuz. Normalize F/K: USD piyasa değeri / son 3 yıl ortalama USD kâr. "
          f"Kazanç getirisi farkı: 100/F/K(TL) eksi politika faizi ({POLITIKA_FAIZI:g}%). Temettü verimi: son 12 ay brüt temettü / fiyat (Yahoo; '-' = kayıt yok, temettü dağıtılmadı demek DEĞİL). "
          "2024 öncesi özkaynak düzeltmesiz olduğu için ROE yalnız GÜNCEL dönemde yorumlanmalı.", "",
          "| Hisse | ROE USD % | PD/DD÷ROE | Norm. F/K USD | Kazanç get. % | Kazanç get. − faiz | Temettü verimi % |", "|---|---|---|---|---|---|---|"]
    for s, d in sorted(S.items(), key=lambda x: ((x[1].get("ek_olculer") or {}).get("pddd_roe") is None, (x[1].get("ek_olculer") or {}).get("pddd_roe") or 0)):
        e = d.get("ek_olculer") or {}
        def g(k):
            v = e.get(k); return "-" if v is None else v
        nf = g("norm_fk_usd"); nf = nf if e.get("norm_fk_yil_sayisi", 0) == 3 or nf == "-" else f"{nf}*"
        L.append(f"| {s} | {g('roe_usd')} | {g('pddd_roe')} | {nf} | {g('kazanc_getirisi')} | {g('kazanc_getirisi_eksi_faiz')} | {g('temettu_verimi')} |")
    L += ["", "## Borç ve nakit akışı ölçüleri (açıklayıcı; banka ve finans kolu konsolide holding hariç)", "",
          "FD = piyasa değeri + net borç + azınlık. Net borç = finansal borç (kira dahil) − (nakit + kısa vadeli finansal yatırım). FAVÖK = faaliyet kârı + amortisman (TFRS 16 sonrası). "
          "FCF verimi = (işletme nakit akışı + sabit sermaye yatırımı) / piyasa değeri. Nakit/kâr = işletme nakit akışı / net kâr (kâr kalitesi; <1 zayıf). Son 12 ay.", "",
          "| Hisse | FD/FAVÖK USD | Net borç/FAVÖK | FD/Satış | FAVÖK marjı % | Net kâr marjı % | FCF verimi % | Nakit/kâr | Bilanço |", "|---|---|---|---|---|---|---|---|---|"]
    for s, d in sorted(S.items(), key=lambda x: (((x[1].get("ek_olculer") or {}).get("borc_nakit") or {}).get("fd_favok_usd") is None, ((x[1].get("ek_olculer") or {}).get("borc_nakit") or {}).get("fd_favok_usd") or 0)):
        b = ((d.get("ek_olculer") or {}).get("borc_nakit")) or {}
        if not b or "hata" in b: continue
        def g(k):
            v = b.get(k); return "-" if v is None else v
        L.append(f"| {s} | {g('fd_favok_usd')} | {g('net_borc_favok')} | {g('fd_satis')} | {g('favok_marji')} | {g('net_kar_marji')} | {g('fcf_verimi')} | {g('nakit_kar_orani')} | {g('bilanco_donemi')} |")
    L += ["", "## Banka ölçüleri (açıklayıcı)", "",
          "Kaynak: banka şablonu (UFRS), son 12 ay. NIM vekili = net faiz geliri / ortalama aktif. Risk maliyeti = kredi ve diğer alacak değer düşüş karşılığı / ortalama krediler. "
          "Maliyet/gelir = diğer faaliyet giderleri / faaliyet gelirleri (personel dahil olmayabilir, banka arası yaklaşık karşılaştırma). **Takipteki kredi oranı ve sermaye yeterlilik oranı bu servisten gelmez** (BDDK bülteni/KAP gerekir); özkaynak/aktif yalnız kaba vekildir.", "",
          "| Banka | NIM vekili % | Risk maliyeti % | Ücret payı % | Maliyet/gelir % | Kredi/mevduat % | Özkaynak/aktif % | ROA % | Bilanço |", "|---|---|---|---|---|---|---|---|---|"]
    for s, d in sorted(S.items()):
        b = (d.get("ek_olculer") or {}).get("banka")
        if not b or "hata" in b: continue
        def g(k):
            v = b.get(k); return "-" if v is None else v
        L.append(f"| {s} | {g('nim_vekil')} | {g('risk_maliyeti')} | {g('ucret_payi')} | {g('maliyet_gelir')} | {g('kredi_mevduat')} | {g('ozkaynak_aktif')} | {g('roa')} | {g('bilanco_donemi')} |")
    if kayit["atlanan"]: L += ["", "Atlanan: " + "; ".join(kayit["atlanan"])]
    L += ["", "Hücre biçimi: değer (kendi tarihinde yüzdelik dilim, log z-skoru)."]
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    main()
