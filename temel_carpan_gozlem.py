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
YEDEK = {"TRMET": "KOZAA", "TRALT": "KOZAL"}
GECIKME = {3: 60, 6: 70, 9: 60, 12: 70}
DIP_YUZDELIK = 20.0
MIN_GUN = 250
CIKTI = "data/temel"
BAS = date(2021, 1, 1)

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
    sonuc, atlanan = {}, []
    for s in SEMBOLLER:
        if s not in hamlar or s not in fiyatlar:
            atlanan.append(f"{s}: " + ("ham yok" if s not in hamlar else "fiyat yok")); continue
        r = gunluk_oran(fiyatlar[s], kur, hamlar[s], s)
        if not r: atlanan.append(f"{s}: sermaye kalemi yok"); continue
        tg, res, bilgi = r
        ist = {k: istat(v) for k, v in res.items()}
        ok_kar, ok_oz = kalite(bilgi)
        banka = s in BANKALAR
        def dip(k): return ist.get(k) and ist[k]["yuzdelik"] <= DIP_YUZDELIK
        dip_pd = bool(dip("pddd_tl") and dip("pddd_usd"))
        dip_fk = bool(dip("fk_tl") and dip("fk_usd"))
        aday = dip_pd and (banka or dip_fk)
        sonuc[s] = {"banka": banka, "son_tarih": str(tg[-1]) if tg else None, "istatistik": ist,
                    "kalite_kar_usd": ok_kar, "kalite_ozkaynak_usd": ok_oz,
                    "dip_pddd": dip_pd, "dip_fk": dip_fk, "aday": aday,
                    "aday_kaliteli": bool(aday and ok_kar is not False and ok_oz is not False),
                    "son_bilanco": (bilgi["tl"][-1]["donem"] if bilgi["tl"] else None)}
    kayit = {"olusturma_utc": datetime.now(timezone.utc).isoformat(), "mod": "TEST" if test else "GERCEK",
             "dip_yuzdelik_esigi": DIP_YUZDELIK, "atlanan": atlanan, "semboller": sonuc}
    json.dump(kayit, open("data/temel_carpan.json" if not test else "/tmp/temel_carpan_test.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    md = rapor(kayit)
    open("temel_carpan.md" if not test else "/tmp/temel_carpan_test.md", "w", encoding="utf-8").write(md)
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
    L += ["", "## Tüm evren", "", "| Hisse | PD/DD TL | PD/DD USD | F/K TL | F/K USD | Son bilanço | Dip PD | Dip F/K |", "|---|---|---|---|---|---|---|---|"]
    for s, d in sorted(S.items(), key=lambda x: (x[1]["istatistik"].get("pddd_usd") or {"yuzdelik": 999})["yuzdelik"]):
        L.append(f"| {s} | {sat(s,d,'pddd_tl')} | {sat(s,d,'pddd_usd')} | {sat(s,d,'fk_tl')} | {sat(s,d,'fk_usd')} | {d['son_bilanco']} | {'x' if d['dip_pddd'] else ''} | {'x' if d['dip_fk'] else ''} |")
    if kayit["atlanan"]: L += ["", "Atlanan: " + "; ".join(kayit["atlanan"])]
    L += ["", "Hücre biçimi: değer (kendi tarihinde yüzdelik dilim, log z-skoru)."]
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    main()
