#!/usr/bin/env python3
"""Günlük açığa satış verisini toplar + short squeeze adayı taraması.

Kaynak: Foreks "ANALİZ- Açığa Satış İşlem Hacmi (İnfo Yatırım)" haberi (herkese açık HTML tablo).
Keşif: foreks.com/haberler/?page=1..N listesinde slug taranır. Bulunamazsa
data/aciga_satis_inbox/*.html|*.txt|*.csv dosyaları (elle bırakılan tablo) okunur.
Çıktı: data/aciga_satis_gunluk.json (geçmiş), data/aciga_satis_squeeze.json, aciga_satis_squeeze.md
Not: bu bir yatırım tavsiyesi değil; aday listesi kullanıcının kendi panelinde teyit edilir.
"""
import json, os, re, sys, glob, statistics, time, urllib.request
from html.parser import HTMLParser
from datetime import datetime, timezone

DATA = os.environ.get("AS_DATA_DIR", "data")
GECMIS = os.path.join(DATA, "aciga_satis_gunluk.json")
INBOX = os.path.join(DATA, "aciga_satis_inbox")
SQZ_JSON = os.path.join(DATA, "aciga_satis_squeeze.json")
SQZ_MD = os.environ.get("AS_MD", "aciga_satis_squeeze.md")
LISTE = "https://www.foreks.com/haberler/?page=%d"
SAYFA_SAYISI = 10
SLUG = re.compile(r'href="([^"]*aciga-satis-islem-hacmi-info-yatirim-(\d\d)-(\d\d)-(\d\d)[^"]*)"', re.I)
MAX_GUN = 250
UA = {"User-Agent": "Mozilla/5.0 (compatible; bist-veri/1.0)"}
ALANLAR = ["kod", "islem_hacmi_mn", "as_hacmi_mn", "as_oran_pct", "as_adet_mn", "islem_adet_oran",
           "as_min", "as_max", "kapanis", "as_ort", "degisim_pct"]


def sayi(s):
    s = (s or "").strip().replace("%", "").replace("\xa0", "").replace(" ", "")
    if not s or s in ("-", "--"):
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


class Tablo(HTMLParser):
    def __init__(self):
        super().__init__(); self.satirlar = []; self._h = None; self._r = None
    def handle_starttag(self, t, a):
        if t == "tr": self._r = []
        elif t in ("td", "th") and self._r is not None: self._h = ""
    def handle_data(self, d):
        if self._h is not None: self._h += d
    def handle_endtag(self, t):
        if t in ("td", "th") and self._h is not None and self._r is not None:
            self._r.append(self._h.strip()); self._h = None
        elif t == "tr" and self._r is not None:
            if self._r: self.satirlar.append(self._r)
            self._r = None


def metin_satirlari(txt):
    """HTML tablo yoksa: boşluk/;/tab ayrık düz metin satırları."""
    out = []
    for ln in txt.splitlines():
        p = [x for x in re.split(r"[;\t]|\s{2,}", ln.strip()) if x != ""]
        if len(p) < 3: p = ln.split()
        if len(p) >= 9: out.append(p)
    return out


def tablo_ayikla(icerik):
    t = Tablo(); t.feed(icerik)
    satirlar = t.satirlar if t.satirlar else metin_satirlari(icerik)
    sonuc = {}
    for r in satirlar:
        if len(r) < 9: continue
        kod = r[0].strip().upper()
        if not re.fullmatch(r"[A-Z0-9 ]{3,9}", kod) or kod in ("KOD",):
            continue
        v = [sayi(x) for x in r[1:1 + 10]]
        if sum(x is not None for x in v) < 6: continue
        v += [None] * (10 - len(v))
        kayit = dict(zip(ALANLAR[1:], v)); sonuc[kod] = kayit
    return sonuc


def al(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def kesfet():
    """{tarih_iso: url} — listede görünen açığa satış haberleri."""
    bulunan = {}
    for n in range(1, SAYFA_SAYISI + 1):
        try:
            h = al(LISTE % n)
        except Exception as e:
            print(f"  liste {n}: {e}"); continue
        print(f"  liste {n}: {len(h)} bayt, 'aciga' geçen: {h.lower().count('aciga')}")
        for url, g, a, y in SLUG.findall(h):
            iso = f"20{y}-{a}-{g}"
            if url.startswith("/"): url = "https://www.foreks.com" + url
            bulunan.setdefault(iso, url)
        time.sleep(0.5)
    return bulunan


def yukle():
    if os.path.exists(GECMIS):
        with open(GECMIS, encoding="utf-8") as f: return json.load(f)
    return {"gunler": {}}


def kaydet(obj, yol):
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, yol)


def inbox_oku(gecmis):
    n = 0
    for yol in sorted(glob.glob(os.path.join(INBOX, "*"))):
        ad = os.path.basename(yol)
        m = re.search(r"(20\d\d)-(\d\d)-(\d\d)", ad) or re.search(r"(\d\d)[-_.](\d\d)[-_.](20\d\d)", ad)
        if not m: continue
        iso = "-".join(m.groups()) if len(m.group(1)) == 4 else f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        if iso in gecmis["gunler"]: continue
        with open(yol, encoding="utf-8", errors="replace") as f: t = tablo_ayikla(f.read())
        if t: gecmis["gunler"][iso] = t; n += 1; print(f"  inbox {ad}: {len(t)} satır")
    return n


def skorla(gecmis):
    gun = sorted(gecmis["gunler"])
    if not gun: return None
    son = gun[-1]; rows = []
    for kod, s in gecmis["gunler"][son].items():
        if kod.startswith("XU") or kod.startswith("BIST"): continue
        ser = [(g, gecmis["gunler"][g][kod]["as_oran_pct"]) for g in gun
               if kod in gecmis["gunler"][g] and gecmis["gunler"][g][kod].get("as_oran_pct") is not None]
        o = [x[1] for x in ser]; bugun = s.get("as_oran_pct")
        if bugun is None: continue
        z = ort3 = ort10 = trend = None
        if len(o) >= 10:
            gecm = o[:-1][-60:]
            sd = statistics.pstdev(gecm)
            z = (bugun - statistics.mean(gecm)) / sd if sd > 0 else 0.0
            ort3 = statistics.mean(o[-3:]); ort10 = statistics.mean(o[-10:]); trend = ort3 - ort10
        kap, ao, chg = s.get("kapanis"), s.get("as_ort"), s.get("degisim_pct")
        sualtinda = None if not (kap and ao) else (kap / ao - 1) * 100  # short ort. fiyatının üstünde kapanış => zarar
        k = {
            "yuksek_oran": z is not None and z >= 1.5,
            "oran_artiyor": trend is not None and trend > 0.5,
            "short_zararda": sualtinda is not None and sualtinda > 1.0,
            "fiyat_guclu": chg is not None and chg > 1.0,
        }
        skor = sum(k.values())
        rows.append({"kod": kod, "oran_pct": bugun, "z_oran": None if z is None else round(z, 2),
                     "trend_3g_10g": None if trend is None else round(trend, 2),
                     "kapanis_vs_short_ort_pct": None if sualtinda is None else round(sualtinda, 2),
                     "degisim_pct": chg, "as_hacmi_mn": s.get("as_hacmi_mn"), "gecmis_gun": len(o),
                     "kosullar": k, "skor": skor})
    rows.sort(key=lambda r: (-r["skor"], -(r["z_oran"] or -9), -r["oran_pct"]))
    # endeks düzeyi seri
    endeks = {}
    for e in ("BIST100", "BIST 100", "XU100", "BIST50", "BIST 50", "XU050"):
        ser = [(g, gecmis["gunler"][g][e]["as_oran_pct"]) for g in gun if e in gecmis["gunler"][g]]
        if ser: endeks[e] = ser[-20:]
    return {"tarih": son, "gun_sayisi": len(gun), "adaylar": rows, "endeks_oran_son20": endeks,
            "uyari": "Geçmiş < 10 gün ise z/trend hesaplanmaz; bu liste tavsiye değil, aday taramasıdır."}


def rapor(r):
    L = [f"# Açığa satış / short squeeze taraması — {r['tarih']}", "",
         f"Geçmiş: {r['gun_sayisi']} gün. {r['uyari']}", ""]
    for ad, ser in r["endeks_oran_son20"].items():
        L.append(f"**{ad} açığa satış payı (son {len(ser)} gün):** " + ", ".join(f"{v:.2f}" for _, v in ser))
    L += ["", "| Hisse | Pay % | z | Trend (3g−10g) | Kapanış/short ort. % | Değ. % | Skor |", "|---|---|---|---|---|---|---|"]
    f = lambda v: "–" if v is None else f"{v:.2f}"
    for x in r["adaylar"][:15]:
        L.append(f"| {x['kod']} | {x['oran_pct']:.2f} | {f(x['z_oran'])} | {f(x['trend_3g_10g'])} | {f(x['kapanis_vs_short_ort_pct'])} | {f(x['degisim_pct'])} | {x['skor']}/4 |")
    L += ["", "Skor koşulları: pay z≥1,5 · 3g ort. − 10g ort. > 0,5 puan · kapanış, short ort. fiyatının >%1 üstünde · günlük değişim > %1."]
    return "\n".join(L) + "\n"


def main():
    os.makedirs(DATA, exist_ok=True); os.makedirs(INBOX, exist_ok=True)
    gecmis = yukle(); yeni = 0
    try:
        bulunan = kesfet()
    except Exception as e:
        print("keşif hatası:", e); bulunan = {}
    print(f"Listede bulunan gün: {sorted(bulunan)}")
    for iso, url in sorted(bulunan.items()):
        if iso in gecmis["gunler"]: continue
        try:
            t = tablo_ayikla(al(url))
        except Exception as e:
            print(f"  {iso}: {e}"); continue
        if len(t) >= 20:
            gecmis["gunler"][iso] = t; yeni += 1; print(f"  {iso}: {len(t)} satır")
        else:
            print(f"  {iso}: tablo ayıklanamadı ({len(t)} satır)")
    yeni += inbox_oku(gecmis)
    for g in sorted(gecmis["gunler"])[:-MAX_GUN]: del gecmis["gunler"][g]
    gecmis["guncelleme_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    kaydet(gecmis, GECMIS)
    r = skorla(gecmis)
    if r:
        kaydet(r, SQZ_JSON)
        with open(SQZ_MD, "w", encoding="utf-8") as f: f.write(rapor(r))
    print(f"Yeni gün: {yeni}; toplam gün: {len(gecmis['gunler'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
