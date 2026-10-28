"""
ALARM KARNESI v1 (27.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Komite doc'u "Seytanin Avukati: sistem denetimi (27.10)" Oncelik A1-A2 (+A3, A4, A5'in ucuz kismi).

Soru: TradingView alarmlarinin HER turu (izleme sinifi dahil) sonraki gunlerde dogru yonu gosterdi mi?

Girdi : data/arsiv/tv_alerts_YYYY_MM.json (tumu) + data/tv_alerts_latest.json
        Fiyat: yfinance gunluk (auto_adjust=False -> fiyat bazli, XU100 fiyat endeksiyle tutarli)
               + ma610_tarama.bolunme_duzelt (Yahoo'nun duzeltmedigi bedelsizler)
Cikti : data/alarm_karne.json, data/alarm_karne.md, data/alarm_karne_olaylar.csv

YONTEM (veri gorulmeden yazildi = on kayit; degisiklik CHANGELOG'a islenir):
  Taban fiyat : alarmin yerel (TR) tarihine denk gelen ya da sonraki ILK islem gununun KAPANISI.
                Alarm fiyati degil: kapanista islem yapilabilir, endeks icin de ayni an kullanilir.
                Alarm fiyati ile kapanis arasindaki fark "giris_kaymasi_pct" olarak ayrica raporlanir.
  28.10 EKI   : "af_net_T" = ALARM FIYATINDAN giris (canlida gerceklesecek dolum). Yalniz seans ici alarmlarda
                (alarm gunu = taban gunu) alarm fiyati kullanilir, digerlerinde kapanis. Endeks getirisi yine
                kapanistan olculur (alarm anindaki endeks seviyesi yok) - yaklasiktir. Hukum kurallari DEGISMEDI;
                hukum hala net_T (kapanis bazli) ile verilir, af_net_T yalniz raporlanir.
  Ufuk        : T+1, T+3, T+5, T+10 islem gunu kapanisi.
  Goreli      : hisse getirisi - XU100 getirisi (ayni pencere), ve
                hisse getirisi - SEKTOR SEPETI (evrendeki ayni sektor hisselerinin esit agirlikli
                ortalamasi, hissenin kendisi haric; sektorde tek hisse varsa yok).
  Yon         : YON tablosu. yon_T = yon-ayarli BRUT goreli (YUKARI: goreli, ASAGI: -goreli).
                net_T = yon_T - MALIYET_PCT (YUKARI turlerde; gidis-donus komisyon+kayma).
                ASAGI turlerde (cikis/risk-off) net = yon_T (kacinilan goreli getiri; maliyet yok).
                TERS hukmu BRUT yon_T ile verilir (yon yanlis mi?), KALITELI hukmu NET ile (maliyeti asiyor mu?).
  Tekillestirme: ayni sembol + ayni tur + ayni taban gunu = 1 olay (ilk alarm).
                Ayni sembolde ayni gun P4 -> P3 zinciri turler arasinda ayrica "zincir_orani" ile raporlanir.
  Istatistik  : KUMELENMIS standart hata. Kume = taban gunu (T+1, T+3) / ISO hafta (T+5, T+10;
                pencereler ust uste bindigi icin daha tutucu). Ayrica kume-blok bootstrap %95 GA.
                Kriz gunlerinde ayni gun 10-15 hisse birlikte alarm verdigi icin naif t sisiktir;
                naif t yalniz karsilastirma icin yazilir.
  Coklu test  : Benjamini-Hochberg, q = 0.10, tum (tur x {T+3, T+5}) testleri birlikte.
  Rejim       : KRIZ_ONCESI tarihinden once / sonra, ve alarmdaki 'rejim' alanina gore kirilim.
  HUKUM (tur basina, net T+3 ve net T+5 uzerinden):
     YETERSIZ_ORNEK : olay sayisi < MIN_N
     TERS           : T+3 ya da T+5 BRUT yon ortalamasi < 0, kumelenmis t < -1.96 ve BH-anlamli
     KALITELI       : T+3 ve T+5 net ortalama > 0, en az birinde kumelenmis t > 1.96 ve BH-anlamli,
                      ve ornegi >= REJIM_MIN_N olan her rejimde T+3 net ortalama > 0
     ADAY           : T+3 ve T+5 net ortalama > 0 ama anlamli degil (ya da rejimlerde isaret tutarsiz)
     KENAR_YOK      : digerleri
  "KENAR_YOK" ile "TERS" farkli iddialardir: birincisi zarar kaniti degildir.
Veri butunlugu (A4): gunluk alarm ve GUNLUK_OZET sayisi (eksik gun tespiti), alan bosluk oranlari,
  eventId tekrarlari, tanimsiz sinyal adlari, schemaVersion dagilimi, carrierLagBars.
Fiyat capraz kontrolu (A5, ucuz kisim): alarm fiyati o gunun Yahoo [dusuk, yuksek] araliginin
  %1 disindaysa "fiyat_uyusmazligi" (bedelsiz/veri hatasi ya da yanlis sembol isareti).
Sinirlar: tek fiyat kaynagi Yahoo; seans ici giris modellenmez; evren 31 sembol; sonuclar gecmis
  davranistir, yon tahmini degildir.
"""
import os, json, glob, math, random, datetime, statistics
from collections import Counter, defaultdict

import pandas as pd

MALIYET_PCT = float(os.environ.get("MALIYET_PCT", "0.25"))
KRIZ = os.environ.get("KRIZ_ONCESI", "2026-09-15")
MIN_N = int(os.environ.get("MIN_N", "30"))
REJIM_MIN_N = int(os.environ.get("REJIM_MIN_N", "10"))
BH_Q = float(os.environ.get("BH_Q", "0.10"))
BOOT_B = int(os.environ.get("BOOT_B", "2000"))
UFUK = (1, 3, 5, 10)
TEST_UFUK = (3, 5)
TR_SAAT = datetime.timedelta(hours=3)

# Yon beklentisi. SEKTOR_ROTASYONU ve P4_HAZIRLIK icin YUKARI bir VARSAYIMDIR (izleme sinifi,
# AL oncusu kabul edildi); Baskan farkli tanimlarsa yalniz bu tablo degisir.
YON = {
    "P1_KALITELI_AL": "YUKARI", "P1_AL": "YUKARI", "P2_ADAY": "YUKARI", "P2_DIP_DONUS": "YUKARI",
    "P2_ERKEN_AL": "YUKARI", "P3_SKOR_AL": "YUKARI", "P3_RADAR": "YUKARI", "P4_HAZIRLIK": "YUKARI",
    "SEKTOR_ROTASYONU": "YUKARI", "CORE_AL": "YUKARI",
    "ACIL_CIK": "ASAGI", "POZ_AZALT": "ASAGI", "STOP_KIRILDI": "ASAGI", "IC_STOP": "ASAGI",
    "CORE_CIKIS": "ASAGI",
}
# CHANGELOG_V162 alarm oncelik tablosu (P2_ADAY orada "Islem"; sinyal_arsiv_gunluk.py'de IZLEME -
# celiski raporda belirtilir).
SINIF = {
    "STOP_KIRILDI": "KRITIK", "IC_STOP": "KRITIK", "ACIL_CIK": "KRITIK", "POZ_AZALT": "KRITIK",
    "CORE_AL": "ISLEM", "CORE_CIKIS": "ISLEM", "P1_KALITELI_AL": "ISLEM", "P2_ADAY": "ISLEM",
    "P3_SKOR_AL": "ISLEM", "P2_DIP_DONUS": "ISLEM",
    "P3_RADAR": "IZLEME", "P4_HAZIRLIK": "IZLEME", "SEKTOR_ROTASYONU": "IZLEME",
}
HARIC = {"GUNLUK_OZET"}
HARIC_ONEK = ("GERCEK_TEST",)   # kanal test alarmlari
# 28.10 EKI: Pipedream "Test" dugmesiyle yeniden gonderilen eski ornek olay. schemaVersion/eventId
# tasimiyor, fiyati hep 348.50; Pine alarmi degil. (sembol, sinyal, fiyat) imzasiyla disarida tutulur.
TEST_IMZALARI = {("THYAO", "P1_KALITELI_AL", "348.50")}


def haric_mi(tur):
    return bos(tur) or tur in HARIC or str(tur).startswith(HARIC_ONEK)
SEKTOR = {
    "AKBNK": "Banka", "YKBNK": "Banka", "GARAN": "Banka", "ISCTR": "Banka", "HALKB": "Banka", "VAKBN": "Banka",
    "KCHOL": "Holding", "SAHOL": "Holding", "ALARK": "Holding",
    "THYAO": "Ulastirma", "PGSUS": "Ulastirma", "TAVHL": "Ulastirma",
    "TOASO": "Otomotiv", "FROTO": "Otomotiv", "OTKAR": "Otomotiv",
    "EREGL": "Sanayi", "SISE": "Sanayi", "ASELS": "Sanayi", "TUPRS": "Sanayi",
    "ENJSA": "Enerji", "PETKM": "Enerji", "ASTOR": "Enerji",
    "BIMAS": "Perakende", "MGROS": "Perakende", "ULKER": "Perakende",
    "TRMET": "Madencilik", "TRALT": "Madencilik",
    "TTKOM": "Iletisim", "AEFES": "Icecek", "ENKAI": "Insaat", "EKGYO": "GYO",
}
ALANLAR = ["fiyat", "skor", "kgs", "stop", "rejim", "relvol", "v112n", "v112wr", "p3ozet", "pozsebep",
           "schemaVersion", "eventId", "carrierLagBars"]


# ---------------------------------------------------------------- yardimcilar
def f(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def bos(x):
    return x is None or str(x).strip() in ("", "?", "nan", "None")


def kumelenmis(vals, kume):
    """Ortalama, kumelenmis SE (CR1, G/(G-1) duzeltmesi), t, naif t, kume sayisi."""
    n = len(vals)
    if n < 2:
        return None
    m = sum(vals) / n
    top = defaultdict(float)
    for v, g in zip(vals, kume):
        top[g] += v - m
    G = len(top)
    naif_se = statistics.stdev(vals) / math.sqrt(n)
    if G < 2:
        return {"ort": m, "se": None, "t": None, "naif_t": m / naif_se if naif_se else None, "G": G}
    se = math.sqrt(sum(s * s for s in top.values()) * G / (G - 1)) / n
    return {"ort": m, "se": se, "t": (m / se) if se else None,
            "naif_t": (m / naif_se) if naif_se else None, "G": G}


def bootstrap_ga(vals, kume, B=BOOT_B, tohum=20261027):
    gruplar = defaultdict(list)
    for v, g in zip(vals, kume):
        gruplar[g].append(v)
    anahtar = list(gruplar)
    if len(anahtar) < 5:
        return None
    rnd = random.Random(tohum)
    ortlar = []
    for _ in range(B):
        s = c = 0.0
        for _ in anahtar:
            gv = gruplar[rnd.choice(anahtar)]
            s += sum(gv)
            c += len(gv)
        ortlar.append(s / c)
    ortlar.sort()
    return [round(ortlar[int(0.025 * B)], 3), round(ortlar[int(0.975 * B) - 1], 3)]


def p_iki_yonlu(t):
    return None if t is None else math.erfc(abs(t) / math.sqrt(2))


def bh(pler, q=BH_Q):
    """pler: {anahtar: p}. Donus: {anahtar: anlamli_mi}."""
    gecerli = sorted([(p, k) for k, p in pler.items() if p is not None])
    m = len(gecerli)
    esik_k = 0
    for i, (p, _) in enumerate(gecerli, 1):
        if p <= q * i / m:
            esik_k = i
    anlamli = {k: False for k in pler}
    for i, (_, k) in enumerate(gecerli, 1):
        if i <= esik_k:
            anlamli[k] = True
    return anlamli


# ---------------------------------------------------------------- veri
def alarmlari_oku():
    ham, kaynak = [], Counter()
    for yol in sorted(glob.glob("data/arsiv/tv_alerts_*.json")):
        for s in json.load(open(yol, encoding="utf-8")).get("sinyaller", []):
            ham.append(s)
            kaynak[os.path.basename(yol)] += 1
    if os.path.exists("data/tv_alerts_latest.json"):
        for s in json.load(open("data/tv_alerts_latest.json", encoding="utf-8")).get("sinyal_gecmisi", []):
            ham.append(s)
            kaynak["tv_alerts_latest.json"] += 1
    gorulen, tekil, tekrar = set(), [], 0
    for s in ham:
        k = s.get("eventId") if not bos(s.get("eventId")) else None
        k = k or f'{s.get("sembol")}|{s.get("sinyal")}|{s.get("zaman_utc")}'
        if k in gorulen:
            tekrar += 1
            continue
        gorulen.add(k)
        tekil.append(s)
    for s in tekil:
        t = datetime.datetime.fromisoformat(s["zaman_utc"].replace("Z", "+00:00"))
        s["_t_utc"] = t
        s["_gun"] = (t + TR_SAAT).date()
    tekil.sort(key=lambda s: s["_t_utc"])
    return tekil, dict(kaynak), tekrar


def fiyat_cek(kod, bas):
    """DataFrame[Close, High, Low], index = gun (naive). kod: 'AKBNK' ya da 'XU100'."""
    import yfinance as yf
    from ma610_tarama import bolunme_duzelt
    df = yf.Ticker(kod + ".IS").history(start=str(bas), interval="1d", auto_adjust=False)
    df = df[df["Close"] > 0].dropna(subset=["Close"])
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    ham = df["Close"].copy()
    duz, olay = bolunme_duzelt(ham)
    if kod == "XU100" and float(ham.pct_change().abs().max()) <= 0.25:
        duz, olay = ham, []
    carpan = duz / ham
    return pd.DataFrame({"Close": duz, "High": df["High"] * carpan, "Low": df["Low"] * carpan,
                         "HamClose": ham, "HamHigh": df["High"], "HamLow": df["Low"]}), olay


# ---------------------------------------------------------------- olcum
def olaylari_kur(alarmlar, fiyatlar, xu):
    gunler = list(xu.index)
    gun_poz = {g: i for i, g in enumerate(gunler)}
    kriz = pd.Timestamp(KRIZ)

    def taban_poz(gun):
        g = pd.Timestamp(gun)
        for i in range(len(gunler)):
            if gunler[i] >= g:
                return i
        return None

    # sektor sepeti icin hizli erisim
    sektor_uyeleri = defaultdict(list)
    for k, s in SEKTOR.items():
        if k in fiyatlar:
            sektor_uyeleri[s].append(k)

    def getiri(df, g0, g1):
        try:
            a, b = df.at[g0, "Close"], df.at[g1, "Close"]
        except KeyError:
            return None
        return (b / a - 1) * 100 if a and b else None

    olaylar, gorulen, uyusmazlik = [], set(), []
    for s in alarmlar:
        tur, kod = s.get("sinyal"), s.get("sembol")
        if haric_mi(tur) or kod not in fiyatlar or (kod, tur, str(s.get("fiyat"))) in TEST_IMZALARI:
            continue
        p0 = taban_poz(s["_gun"])
        if p0 is None:
            continue
        g0 = gunler[p0]
        anahtar = (kod, tur, g0)
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar)
        df = fiyatlar[kod]
        if g0 not in df.index:
            continue
        yon = YON.get(tur, "BELIRSIZ")
        r = {"sembol": kod, "sinyal": tur, "sinif": SINIF.get(tur, "TANIMSIZ"), "yon": yon,
             "zaman_utc": s["zaman_utc"], "taban_gun": str(g0.date()),
             "rejim_alani": s.get("rejim"), "donem": "KRIZ_SONRASI" if g0 > kriz else "KRIZ_ONCESI",
             "relvol": f(s.get("relvol")), "skor": f(s.get("skor")), "kgs": f(s.get("kgs"))}
        afiyat = f(s.get("fiyat"))
        kapanis = float(df.at[g0, "Close"])
        if afiyat:
            r["alarm_fiyat"] = afiyat
            # alarm gunu kapanisina gore giris kaymasi (ham fiyatla kiyas: duzeltme carpani disarida)
            ham_kap = float(df.at[g0, "HamClose"])
            r["giris_kaymasi_pct"] = round((ham_kap / afiyat - 1) * 100, 3)
            # A5: alarm gunu ise (seans ici) fiyat [dusuk, yuksek] icinde olmali
            if pd.Timestamp(s["_gun"]) == g0:
                lo, hi = float(df.at[g0, "HamLow"]), float(df.at[g0, "HamHigh"])
                if afiyat < lo * 0.99 or afiyat > hi * 1.01:
                    uyusmazlik.append({"sembol": kod, "sinyal": tur, "gun": str(g0.date()),
                                       "alarm_fiyat": afiyat, "yahoo_dusuk": round(lo, 4), "yahoo_yuksek": round(hi, 4)})
                    r["fiyat_uyusmazligi"] = True
        r["iso_hafta"] = "%d-W%02d" % g0.isocalendar()[:2]
        seans_ici = bool(afiyat) and pd.Timestamp(s["_gun"]) == g0 and not r.get("fiyat_uyusmazligi")
        giris_duz = afiyat * (kapanis / float(df.at[g0, "HamClose"])) if seans_ici else kapanis
        peers = [k for k in sektor_uyeleri.get(SEKTOR.get(kod), []) if k != kod]
        for h in UFUK:
            if p0 + h >= len(gunler):
                r[f"T{h}"] = None
                continue
            g1 = gunler[p0 + h]
            ri = getiri(df, g0, g1)
            rx = getiri(xu, g0, g1)
            r[f"T{h}"] = None if ri is None else round(ri, 3)
            rel = None if ri is None or rx is None else ri - rx
            r[f"rel_T{h}"] = None if rel is None else round(rel, 3)
            ps = [getiri(fiyatlar[k], g0, g1) for k in peers]
            ps = [x for x in ps if x is not None]
            r[f"sek_rel_T{h}"] = round(ri - sum(ps) / len(ps), 3) if ri is not None and ps else None
            try:
                ri_af = (float(df.at[g1, "Close"]) / giris_duz - 1) * 100
            except KeyError:
                ri_af = None
            if ri_af is None or rx is None or yon == "BELIRSIZ":
                r[f"af_net_T{h}"] = None
            else:
                r[f"af_net_T{h}"] = round(ri_af - rx - MALIYET_PCT, 3) if yon == "YUKARI" else round(-(ri_af - rx), 3)
            if rel is None or yon == "BELIRSIZ":
                r[f"yon_T{h}"] = r[f"net_T{h}"] = None
            elif yon == "YUKARI":
                r[f"yon_T{h}"] = round(rel, 3)
                r[f"net_T{h}"] = round(rel - MALIYET_PCT, 3)
            else:
                r[f"yon_T{h}"] = r[f"net_T{h}"] = round(-rel, 3)
        olaylar.append(r)
    return olaylar, uyusmazlik


def ozetle(alt, alan, h):
    kume_alan = "taban_gun" if h <= 3 else "iso_hafta"
    pairs = [(o[alan], o[kume_alan]) for o in alt if o.get(alan) is not None]
    if len(pairs) < 2:
        return {"n": len(pairs)}
    vals, kume = [p[0] for p in pairs], [p[1] for p in pairs]
    k = kumelenmis(vals, kume)
    out = {"n": len(vals), "kume": k["G"], "ort": round(k["ort"], 3),
           "t_kume": None if k["t"] is None else round(k["t"], 2),
           "t_naif": None if k["naif_t"] is None else round(k["naif_t"], 2),
           "p": None if k["t"] is None else round(p_iki_yonlu(k["t"]), 4),
           "isabet_pct": round(100 * sum(v > 0 for v in vals) / len(vals), 1),
           "ga95_bootstrap": bootstrap_ga(vals, kume)}
    return out


def karne(olaylar):
    turler = sorted({o["sinyal"] for o in olaylar})
    sonuc = {}
    for tur in turler:
        alt = [o for o in olaylar if o["sinyal"] == tur]
        r = {"sinif": alt[0]["sinif"], "yon": alt[0]["yon"], "olay": len(alt),
             "sembol_sayisi": len({o["sembol"] for o in alt}),
             "ilk": min(o["taban_gun"] for o in alt), "son": max(o["taban_gun"] for o in alt)}
        for h in UFUK:
            r[f"mutlak_T{h}"] = ozetle(alt, f"T{h}", h)
            r[f"rel_T{h}"] = ozetle(alt, f"rel_T{h}", h)
            r[f"sek_rel_T{h}"] = ozetle(alt, f"sek_rel_T{h}", h)
            r[f"yon_T{h}"] = ozetle(alt, f"yon_T{h}", h)
            r[f"net_T{h}"] = ozetle(alt, f"net_T{h}", h)
            r[f"af_net_T{h}"] = ozetle(alt, f"af_net_T{h}", h)
        r["rejim_donem"] = {d: {f"net_T{h}": ozetle([o for o in alt if o["donem"] == d], f"net_T{h}", h) for h in TEST_UFUK}
                            for d in ("KRIZ_ONCESI", "KRIZ_SONRASI")}
        r["rejim_alani"] = {str(ra): ozetle([o for o in alt if str(o["rejim_alani"]) == str(ra)], "net_T3", 3)
                            for ra in sorted({str(o["rejim_alani"]) for o in alt})}
        hacimli = [o for o in alt if o.get("relvol") is not None and o["relvol"] >= 1]
        hacimsiz = [o for o in alt if o.get("relvol") is not None and o["relvol"] < 1]
        r["hacim_kirilimi"] = {"relvol>=1": ozetle(hacimli, "net_T3", 3), "relvol<1": ozetle(hacimsiz, "net_T3", 3)}
        kay = [o["giris_kaymasi_pct"] for o in alt if o.get("giris_kaymasi_pct") is not None]
        r["giris_kaymasi_ort_pct"] = round(sum(kay) / len(kay), 3) if kay else None
        sonuc[tur] = r

    # zincir: ayni sembol + ayni gun birden fazla tur
    gun_sembol = defaultdict(set)
    for o in olaylar:
        gun_sembol[(o["sembol"], o["taban_gun"])].add(o["sinyal"])
    for tur, r in sonuc.items():
        alt = [o for o in olaylar if o["sinyal"] == tur]
        r["zincir_orani_pct"] = round(100 * sum(len(gun_sembol[(o["sembol"], o["taban_gun"])]) > 1 for o in alt) / len(alt), 1)

    # coklu test + hukum
    p_net, p_yon = {}, {}
    for tur, r in sonuc.items():
        if r["yon"] == "BELIRSIZ":
            continue
        for h in TEST_UFUK:
            p_net[(tur, h)] = r[f"net_T{h}"].get("p")
            p_yon[(tur, h)] = r[f"yon_T{h}"].get("p")
    anl_net, anl_yon = bh(p_net), bh(p_yon)
    for tur, r in sonuc.items():
        r["bh_anlamli"] = {f"net_T{h}": anl_net.get((tur, h), False) for h in TEST_UFUK}
        r["bh_anlamli"].update({f"yon_T{h}": anl_yon.get((tur, h), False) for h in TEST_UFUK})
        r["hukum"], r["hukum_gerekce"] = hukum(r, anl_net, anl_yon, tur)
    return sonuc


def hukum(r, anl, anl_yon, tur):
    if r["yon"] == "BELIRSIZ":
        return "YON_TANIMSIZ", "YON tablosunda yok"
    n3 = r["net_T3"].get("n", 0)
    if n3 < MIN_N:
        return "YETERSIZ_ORNEK", f"olay {n3} < {MIN_N}"
    o3, o5 = r["net_T3"].get("ort"), r["net_T5"].get("ort")
    t3, t5 = r["net_T3"].get("t_kume"), r["net_T5"].get("t_kume")
    for h in TEST_UFUK:
        o, t = r[f"yon_T{h}"].get("ort"), r[f"yon_T{h}"].get("t_kume")
        if o is not None and o < 0 and t is not None and t < -1.96 and anl_yon.get((tur, h)):
            return "TERS", f"brut yon T+{h} {o} (t_kume {t}, BH anlamli) - yon yanlis"
    if o3 is None or o5 is None:
        return "YETERSIZ_ORNEK", "T+5 henuz olusmadi"
    if o3 > 0 and o5 > 0:
        anlamli = any(t is not None and t > 1.96 and anl.get((tur, h)) for h, t in ((3, t3), (5, t5)))
        rejim_ok = all((v["net_T3"].get("ort") or 0) > 0 for v in r["rejim_donem"].values()
                       if v["net_T3"].get("n", 0) >= REJIM_MIN_N)
        if anlamli and rejim_ok:
            return "KALITELI", f"net T+3 {o3}, T+5 {o5}; anlamli ve rejimlerde tutarli"
        return "ADAY", f"net T+3 {o3}, T+5 {o5}; " + ("anlamli degil" if not anlamli else "rejimlerde isaret tutarsiz")
    return "KENAR_YOK", f"net T+3 {o3} (t_kume {t3}), T+5 {o5} (t_kume {t5})"


def butunluk(alarmlar, islem_gunleri):
    ilk = min(s["_gun"] for s in alarmlar)
    son = max(s["_gun"] for s in alarmlar)
    gunluk = Counter(s["_gun"] for s in alarmlar if not haric_mi(s.get("sinyal")))
    ozet = Counter(s["_gun"] for s in alarmlar if s.get("sinyal") == "GUNLUK_OZET")
    # son gun tamamlanmamis olabilir (seans ici calisma) -> butunluk kontrolune girmez
    gunler = [g.date() for g in islem_gunleri if ilk <= g.date() < son]
    sayilar = [gunluk.get(g, 0) for g in gunler]
    med = statistics.median(sayilar) if sayilar else 0
    oz_med = statistics.median([ozet.get(g, 0) for g in gunler]) if gunler else 0
    eksik = [{"gun": str(g), "alarm": gunluk.get(g, 0), "gunluk_ozet": ozet.get(g, 0)}
             for g in gunler if gunluk.get(g, 0) < 0.5 * med or (oz_med and ozet.get(g, 0) < 0.8 * oz_med)]
    turler = Counter(s.get("sinyal") for s in alarmlar)
    return {
        "aralik": [str(ilk), str(son)], "islem_gunu": len(gunler),
        "gunluk_alarm_medyan": med, "gunluk_ozet_medyan": oz_med,
        "supheli_eksik_gunler": eksik,
        "alan_bosluk_orani_pct": {a: round(100 * sum(bos(s.get(a)) for s in alarmlar) / len(alarmlar), 1) for a in ALANLAR},
        "tanimsiz_sinyal_adlari": {k: v for k, v in turler.items() if k not in YON and k not in HARIC},
        "son_30_gunde_supheli": sum(1 for x in eksik if x["gun"] >= str(son - datetime.timedelta(days=30))),
        "schemaVersion": dict(Counter(s.get("schemaVersion", "?") for s in alarmlar)),
        "carrierLagBars": dict(Counter(str(s.get("carrierLagBars", "?")) for s in alarmlar)),
    }


# ---------------------------------------------------------------- rapor
def md_rapor(out):
    L = ["# Alarm Karnesi", "",
         f"Uretim: {out['uretim_utc'][:16]} UTC | maliyet {MALIYET_PCT}% (gidis-donus) | kriz esigi {KRIZ} | "
         f"BH q={BH_Q} | MIN_N={MIN_N}", "",
         "Salt olcum, tavsiye degildir. Net = yon-ayarli XU100-goreli getiri (YUKARI turlerde maliyet dusulu). "
         "t_kume = gun/hafta kumelenmis t; t_naif yalniz karsilastirma icindir.", "",
         "## Tur karnesi (net, XU100'e gore)", "",
         "| Tur | Sinif | Yon | Olay | Brut yon T+3 (t_kume) | Net T+1 | Net T+3 (t_kume / t_naif) | Alarm fiyatindan net T+3 (t_kume) | Net T+5 (t_kume) | Net T+10 | Isabet T+3 | Sektore gore T+3 | Hukum |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    sira = {"KALITELI": 0, "ADAY": 1, "KENAR_YOK": 2, "TERS": 3, "YETERSIZ_ORNEK": 4, "YON_TANIMSIZ": 5}
    for tur, r in sorted(out["turler"].items(), key=lambda kv: (sira.get(kv[1]["hukum"], 9), -kv[1]["olay"])):
        g = lambda k, a="ort": r[k].get(a)
        L.append(f"| {tur} | {r['sinif']} | {r['yon']} | {r['olay']} | {g('yon_T3')} ({g('yon_T3','t_kume')}) | {g('net_T1')} | "
                 f"{g('net_T3')} ({g('net_T3','t_kume')} / {g('net_T3','t_naif')}) | {g('af_net_T3')} ({g('af_net_T3','t_kume')}) | "
                 f"{g('net_T5')} ({g('net_T5','t_kume')}) | "
                 f"{g('net_T10')} | {g('net_T3','isabet_pct')} | {g('sek_rel_T3')} | **{r['hukum']}** |")
    L += ["", "## Rejim kirilimi (net T+3)", "", "| Tur | Kriz oncesi n / ort | Kriz sonrasi n / ort | relvol>=1 n / ort | relvol<1 n / ort | Zincir % |",
          "|---|---|---|---|---|---|"]
    for tur, r in out["turler"].items():
        a, b = r["rejim_donem"]["KRIZ_ONCESI"]["net_T3"], r["rejim_donem"]["KRIZ_SONRASI"]["net_T3"]
        c, d = r["hacim_kirilimi"]["relvol>=1"], r["hacim_kirilimi"]["relvol<1"]
        L.append(f"| {tur} | {a.get('n')} / {a.get('ort')} | {b.get('n')} / {b.get('ort')} | {c.get('n')} / {c.get('ort')} | "
                 f"{d.get('n')} / {d.get('ort')} | {r['zincir_orani_pct']} |")
    v = out["veri_butunlugu"]
    L += ["", "## Veri butunlugu", "",
          f"- Aralik {v['aralik'][0]} - {v['aralik'][1]}, {v['islem_gunu']} islem gunu; gunluk alarm medyani {v['gunluk_alarm_medyan']}, "
          f"GUNLUK_OZET medyani {v['gunluk_ozet_medyan']}.",
          f"- Ham kayit {out['kaynak_ozet']['ham']}, eventId tekrari {out['kaynak_ozet']['tekrar']}, tekil {out['kaynak_ozet']['tekil']}.",
          f"- Supheli eksik gun (alarm < medyanin yarisi ya da GUNLUK_OZET < medyanin %80'i): toplam {len(v['supheli_eksik_gunler'])}, "
          f"son 30 gunde {v['son_30_gunde_supheli']}. En yeni 15 (alarm/ozet): "
          + ", ".join(f"{x['gun']} ({x['alarm']}/{x['gunluk_ozet']})" for x in v["supheli_eksik_gunler"][::-1][:15]),
          "- Tamamen bos alanlar: " + (", ".join(k for k, x in v["alan_bosluk_orani_pct"].items() if x >= 99) or "yok"),
          f"- Tanimsiz sinyal adlari: {v['tanimsiz_sinyal_adlari'] or 'yok'}",
          f"- Fiyat uyusmazligi (alarm fiyati Yahoo gun araliginin %1 disinda): {len(out['fiyat_uyusmazligi'])}",
          f"- Fiyati cekilemeyen: {out['fiyat_hatalari'] or 'yok'}; bedelsiz duzeltmesi: {out['bolunme_olaylari'] or 'yok'}"]
    L += ["", "## Hukum kurallari (on kayit)", "",
          f"KALITELI: net T+3 ve T+5 > 0, en az birinde t_kume > 1.96 ve BH-anlamli, ornegi >= {REJIM_MIN_N} olan her donemde net T+3 > 0. "
          "TERS: BRUT yon T+3 ya da T+5 < 0, t_kume < -1.96 ve BH-anlamli (maliyetten bagimsiz: yon yanlis). ADAY: ikisi de > 0 ama anlamli/tutarli degil. "
          f"KENAR_YOK: digerleri. YETERSIZ_ORNEK: olay < {MIN_N}. KENAR_YOK zarar kaniti degildir."]
    return "\n".join(L) + "\n"


def main():
    alarmlar, kaynak, tekrar = alarmlari_oku()
    semboller = sorted({s["sembol"] for s in alarmlar if s.get("sembol") in SEKTOR})
    bas = min(s["_gun"] for s in alarmlar) - datetime.timedelta(days=10)
    xu, _ = fiyat_cek("XU100", bas)
    fiyatlar, hatalar, bolunme = {}, {}, {}
    for k in semboller:
        try:
            df, olay = fiyat_cek(k, bas)
            if len(df) < 5:
                raise ValueError("az veri")
            fiyatlar[k] = df
            if olay:
                bolunme[k] = olay
        except Exception as e:
            hatalar[k] = str(e)[:120]
    olaylar, uyusmazlik = olaylari_kur(alarmlar, fiyatlar, xu)
    turler = karne(olaylar)
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1",
           "parametreler": {"MALIYET_PCT": MALIYET_PCT, "KRIZ_ONCESI": KRIZ, "MIN_N": MIN_N, "REJIM_MIN_N": REJIM_MIN_N,
                            "BH_Q": BH_Q, "BOOT_B": BOOT_B, "UFUK": UFUK, "YON": YON},
           "kaynak_ozet": {"dosya": kaynak, "ham": sum(kaynak.values()), "tekrar": tekrar, "tekil": len(alarmlar)},
           "xu100_son_gun": str(xu.index[-1].date()),
           "turler": turler, "veri_butunlugu": butunluk(alarmlar, xu.index),
           "fiyat_uyusmazligi": uyusmazlik, "fiyat_hatalari": hatalar, "bolunme_olaylari": bolunme,
           "notlar": ["P2_ADAY CHANGELOG'da ISLEM, sinyal_arsiv_gunluk.py'de IZLEME siniflanmis; burada ISLEM.",
                      "P4_HAZIRLIK ve SEKTOR_ROTASYONU icin yon YUKARI varsayimdir.",
                      "T+5/T+10 kume = ISO hafta (ust uste binen pencereler); yine de tutucu bir yaklasiktir.",
                      "Tek fiyat kaynagi Yahoo; seans ici giris modellenmez (taban = alarm gunu kapanisi)."]}
    os.makedirs("data", exist_ok=True)
    json.dump(out, open("data/alarm_karne.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    open("data/alarm_karne.md", "w", encoding="utf-8").write(md_rapor(out))
    pd.DataFrame(olaylar).to_csv("data/alarm_karne_olaylar.csv", index=False)
    print(f"{len(alarmlar)} tekil alarm, {len(olaylar)} olay, {len(turler)} tur")
    for tur, r in turler.items():
        print(f"{tur:18s} olay {r['olay']:4d}  netT3 {r['net_T3'].get('ort')}  t_kume {r['net_T3'].get('t_kume')}  "
              f"t_naif {r['net_T3'].get('t_naif')}  -> {r['hukum']}")


if __name__ == "__main__":
    main()
