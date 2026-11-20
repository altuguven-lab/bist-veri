"""
ARASTIRMA AKISI (20.11.2026) - araci kurum ve uluslararasi kurum raporlarinin duzenli takibi. SALT VERI, TAVSIYE DEGILDIR.
Neden: Kurum raporlari (hedef fiyat, tavsiye, strateji, model portfoy, kredi notu) yayimlandiginda piyasa ve
algoritmalar tepki verebilir. Bu betik raporlarin KENDISINI degil, yalnizca yapilandirilmis OLGULARINI toplar:
kurum, sembol, hedef, tavsiye, tarih, baglanti. Depo herkese acik oldugu icin rapor metni kopyalanmaz.

Kaynaklar (config/arastirma_kaynaklari.yml; robots.txt kurallari 20.11'de kontrol edildi):
  1) Is Yatirim arastirma RSS (arastirma.isyatirim.com.tr/feed)             -> birincil (✅)
  2) hedeffiyat.com.tr ana sayfasi (cok kurumlu toplayici; Playwright)       -> toplayici (✅ toplayici, kurum metni degil)
  3) Google News RSS sorgulari: yabanci kurumlar, kredi notu, model portfoy  -> haber (◐)
Okunamayanlar (⛔): Garanti BBVA Yatirim (uye girisi), YKY ve Ziraat PDF'leri (robots), yabanci banka raporlari (musteriye ozel).

Cikti:
  data/arastirma_akisi.json     son 7 gun kayitlari + kaynak durumu
  data/arastirma_akisi.md       brifing ozeti (son 24 saat / 7 gun, evren hisseleri once)
  data/arastirma/arsiv/YYYY-MM.jsonl  tekil kayit arsivi (ileride revizyon ve olay testleri icin)
Revizyon yonu: ayni kurum+sembol icin arsivdeki bir onceki farkli hedefle karsilastirilir (YUKARI/ASAGI/YENI).
"""
import datetime as dt
import glob
import hashlib
import html
import json
import os
import re
import sys
import time
from urllib.parse import quote

import feedparser
import yaml

CFG = "config/arastirma_kaynaklari.yml"
IS_RSS = "https://arastirma.isyatirim.com.tr/feed/"
HF_URL = "https://hedeffiyat.com.tr/"
ARSIV = "data/arastirma/arsiv"
UA = "Mozilla/5.0 (bist-veri arastirma botu; gunde birkac kez)"
AYLAR = {"ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5, "haziran": 6, "temmuz": 7,
         "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12}
TAVSIYE = [r"Endeks Üstü Getiri", r"Endekse Paralel Getiri", r"Endeks Altı Getiri", r"Endeksin Üzerinde",
           r"Endeksin Altında", r"Endekse Paralel", r"Endeks Üstü", r"Endeks Altı", r"Güçlü Al", r"\bAL\b", r"\bTUT\b",
           r"\bSAT\b", r"Overweight", r"Underweight", r"Equal-?weight", r"Outperform", r"Underperform", r"\bBuy\b",
           r"\bHold\b", r"\bSell\b", r"Neutral", r"Nötr", r"Kapsama Dışı", r"Gözden Geçiriliyor"]
TURKIYE = r"Türkiye|Turkiye|Türk|Turk|Turkey|Turkish|BIST|Borsa İstanbul|Borsa Istanbul|borsada|\bTL\b|lira|Hazine|TCMB"
SIRKET_ADLARI = {  # haber basliginda kod yerine sirket adi gecebilir (takip seti)
    "Akbank": "AKBNK", "Garanti": "GARAN", "Yapı Kredi": "YKBNK", "Yapi Kredi": "YKBNK", "İş Bankası": "ISCTR", "İşbank": "ISCTR",
    "Sabancı": "SAHOL", "Koç Holding": "KCHOL", "Türk Hava Yolları": "THYAO", "THY": "THYAO", "TAV Havalimanları": "TAVHL",
    "Ereğli": "EREGL", "Erdemir": "EREGL", "Aselsan": "ASELS", "Astor": "ASTOR", "Migros": "MGROS", "BİM": "BIMAS",
    "Tüpraş": "TUPRS", "Tofaş": "TOASO", "Ford Otosan": "FROTO", "Otokar": "OTKAR", "Pegasus": "PGSUS", "Enerjisa": "ENJSA",
    "Ülker": "ULKER", "Anadolu Efes": "AEFES", "Enka": "ENKAI", "Emlak Konut": "EKGYO", "Şişecam": "SISE",
    "Türk Telekom": "TTKOM", "Turkcell": "TCELL", "Petkim": "PETKM", "Alarko": "ALARK", "Halkbank": "HALKB",
    "VakıfBank": "VAKBN", "Vakıfbank": "VAKBN", "Türkiye Sigorta": "TURSG"}
TAKAS = r"takas|alım satım verileri|alım yaptığı|satış yaptı|en fazla alım|müşterilerinin alım|milyon TL.lik alım|aracı kurum dağılımı"
SAYI = r"(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)"


def sayi(s):
    if s is None:
        return None
    t = str(s).strip()
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def evren():
    kod = set()
    for yol in ("config/bist100_uyeler.txt",):
        if os.path.exists(yol):
            kod |= {l.strip() for l in open(yol, encoding="utf-8") if l.strip() and not l.startswith("#")}
    if os.path.exists("config/universe.yml"):
        u = yaml.safe_load(open("config/universe.yml", encoding="utf-8")) or {}
        kod |= set(u.get("symbols") or [])
    takip = set((yaml.safe_load(open("config/universe.yml", encoding="utf-8")) or {}).get("symbols") or []) \
        if os.path.exists("config/universe.yml") else set()
    return kod, takip


def kurum_bul(metin, cfg):
    for grup in ("yerli", "yabanci", "kredi_notu"):
        for k in cfg.get(grup) or []:
            if re.search(k["desen"], metin, re.I if grup != "yabanci" else 0):
                return k["ad"], grup, k.get("kademe")
    return None, None, None


def kod_bul(metin, kodlar):
    return sorted({m for m in re.findall(r"\b[A-Z][A-Z0-9]{3,5}\b", metin) if m in kodlar})


def tavsiye_bul(metin):
    for d in TAVSIYE:
        m = re.search(d, metin, re.I if len(d) > 8 else 0)
        if m:
            return m.group(0).strip()
    return None


def tarih_bul(metin):
    m = re.search(r"\b(\d{1,2})[./](\d{1,2})[./](20\d{2})\b", metin)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(20\d{2})\b", metin)
    if m and m.group(2).lower() in AYLAR:
        return f"{m.group(3)}-{AYLAR[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return None


def tip_bul(baslik):
    b = baslik.lower()
    for k, v in (("hedef fiyat", "hedef_fiyat"), ("model portföy", "model_portfoy"), ("model portfoy", "model_portfoy"),
                 ("strateji", "strateji"), ("kredi not", "kredi_notu"), ("rating", "kredi_notu"), ("bilanço", "bilanco"),
                 ("kapsama", "kapsama"), ("upgrade", "tavsiye_degisikligi"), ("downgrade", "tavsiye_degisikligi"),
                 ("yükselt", "tavsiye_degisikligi"), ("düşür", "tavsiye_degisikligi")):
        if k in b:
            return v
    return "diger"


def temiz(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


# ------------------------------------------------------------------ kaynak 1: Is Yatirim RSS
def is_yatirim(kodlar, cfg):
    f = feedparser.parse(IS_RSS, agent=UA)
    if f.bozo and not f.entries:
        raise RuntimeError(str(getattr(f, "bozo_exception", "bos")))
    out = []
    for e in f.entries[:40]:
        baslik = temiz(getattr(e, "title", ""))
        icerik = temiz((getattr(e, "content", None) or [{}])[0].get("value", "") or getattr(e, "summary", ""))
        pp = getattr(e, "published_parsed", None)
        tarih = dt.date(*pp[:3]).isoformat() if pp else None
        kod = kod_bul(baslik, kodlar) or kod_bul(icerik[:400], kodlar)
        hedef, kurum_onceki = None, None
        m2 = re.search(r"hedef fiyat\w*[^0-9]{0,80}?" + SAYI + r"\s*(?:TL|₺)\s*['’]?\s*(?:den|dan|ten|tan)\s+" + SAYI + r"\s*(?:TL|₺)",
                       icerik, re.I)
        m = re.search(r"hedef fiyat\w*[^0-9]{0,80}?" + SAYI + r"\s*(?:TL|₺)", icerik, re.I)
        if m2:   # "hedef fiyatimizi 520,00 TL'den 560,50 TL'ye" -> yeni hedef ikinci sayi
            kurum_onceki, hedef = sayi(m2.group(1)), sayi(m2.group(2))
        elif m:
            hedef = sayi(m.group(1))
        out.append({"kaynak": "İş Yatırım RSS", "teyit": "birincil", "kurum": "İş Yatırım", "kademe": "A",
                    "grup": "yerli", "tarih": tarih, "tip": tip_bul(baslik), "baslik": baslik[:160],
                    "semboller": kod, "hedef_tl": hedef if len(kod) == 1 else None,
                    "tavsiye": tavsiye_bul(icerik[:1500]) if len(kod) == 1 else None,
                    "kurumun_belirttigi_onceki_hedef": kurum_onceki if len(kod) == 1 else None,
                    "kategoriler": [t.get("term") for t in getattr(e, "tags", [])][:6], "link": getattr(e, "link", "")})
    return out


# ------------------------------------------------------------------ kaynak 2: hedeffiyat.com.tr
JS_KART = r"""() => {
  const ok = el => { const t = el.innerText || ''; return t.length > 8 && t.length < 400 && /₺|TL/.test(t) && /\b[A-Z][A-Z0-9]{3,5}\b/.test(t); };
  const hepsi = [...document.querySelectorAll('tr, li, article, div, a')].filter(ok);
  const en_kucuk = hepsi.filter(el => ![...el.querySelectorAll('tr, li, article, div, a')].some(c => c !== el && ok(c)));
  const g = new Set(); const out = [];
  for (const el of en_kucuk) { const t = el.innerText.replace(/\s+/g, ' ').trim(); if (!g.has(t)) { g.add(t); out.push({t, href: el.closest('a') ? el.closest('a').href : (el.querySelector('a') ? el.querySelector('a').href : null)}); } }
  return out.slice(0, 200);
}"""


JS_SENETBOX = r"""() => [...document.querySelectorAll('.senetbox')].map(b => {
  const q = sel => b.querySelector(sel);
  const aciklama = [...b.querySelectorAll('a[title]')].map(a => a.title).find(t => /hedef fiyat/i.test(t)) || null;
  return {id: b.id || null, kurum: q('a.kurumLogo') ? q('a.kurumLogo').title : null,
          kod: q('.senetbox-title strong') ? q('.senetbox-title strong').innerText.trim() : null,
          hedef: q('.hedeffiyat span') ? q('.hedeffiyat span').innerText.trim() : null,
          potansiyel: q('.potansiyelgetiri span') ? q('.potansiyelgetiri span').innerText.trim() : null,
          aciklama, tarih: q('.senettarih') ? q('.senettarih').innerText.trim() : null,
          href: b.getAttribute('data-href') ? new URL(b.getAttribute('data-href'), location.href).href : null};
})"""


def hedeffiyat(kodlar, cfg):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        s = b.new_page(locale="tr-TR", user_agent=UA)
        s.goto(HF_URL, wait_until="networkidle", timeout=90000)
        try:   # "Bu Hafta Paylasilan" sekmesi (tek ek istek): kacirilan gunleri de yakalar
            s.evaluate("() => { const b = document.querySelector('#pills-buhafta-tab'); if (b) b.click(); }")
            s.wait_for_timeout(4000)
        except Exception as e:
            print("UYARI: Bu Hafta sekmesi acilamadi:", e, file=sys.stderr)
        kutular = s.evaluate(JS_SENETBOX)
        kartlar = [] if kutular else s.evaluate(JS_KART)
        os.makedirs("data/arastirma/ham", exist_ok=True)
        open("data/arastirma/ham/hedeffiyat.html", "w", encoding="utf-8").write(s.content())
        b.close()
    if kutular:
        return senetbox_ayristir(kutular, kodlar, cfg)
    return hedeffiyat_ayristir(kartlar, kodlar, cfg)


def fiyat(t):
    t = re.sub(r"[^\d.,]", "", t or "")
    if not t:
        return None
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif t.count(".") == 1 and len(t.split(".")[1]) <= 2:
        pass
    else:
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def senetbox_ayristir(kutular, kodlar, cfg):
    out, gor = [], set()
    for k in kutular:
        if not k.get("kod") or not k.get("hedef") or (k.get("id") and k["id"] in gor):
            continue
        gor.add(k.get("id"))
        acik = k.get("aciklama") or ""
        kurum_ad = (k.get("kurum") or "").strip()
        kurum, grup, kademe = kurum_bul(kurum_ad, cfg)
        onceki = re.search(SAYI + r"\s*(?:TL|₺)\s*['’]?\s*(?:den|dan|ten|tan)\s+" + SAYI + r"\s*(?:TL|₺)", acik)
        yon = ("YUKARI" if re.search(r"yükselt|artır", acik, re.I) else "ASAGI" if re.search(r"düşür|indir", acik, re.I)
               else "AYNI" if re.search(r"korudu|sabit", acik, re.I) else "BASLATTI" if re.search(r"başlat|kapsam", acik, re.I) else None)
        if onceki and fiyat(k["hedef"]):   # sayilar varsa yon onlardan (metinde tavsiye yukseltmesi karisabilir)
            o_, y_ = sayi(onceki.group(1)), fiyat(k["hedef"])
            yon = "YUKARI" if y_ > o_ else "ASAGI" if y_ < o_ else "AYNI"
        tv = re.search(r"tavsiye(?:sini|si)?\s+(.+?)\s+(?:olarak|'?(?:y|ı|i|u|ü)e)", acik, re.I)
        out.append({"kaynak": "hedeffiyat.com.tr", "teyit": "toplayici", "kurum": kurum or kurum_ad or "(bilinmiyor)",
                    "kademe": kademe, "grup": grup or "yerli", "tarih": tarih_bul(k.get("tarih") or ""), "tip": "hedef_fiyat",
                    "baslik": acik[:200] or f"{kurum_ad} {k['kod']} {k['hedef']}", "semboller": [k["kod"]],
                    "hedef_tl": fiyat(k["hedef"]),
                    "tavsiye": (tv.group(1).strip() if tv else None) or tavsiye_bul(acik),
                    "kurumun_belirttigi_onceki_hedef": sayi(onceki.group(1)) if onceki else None,
                    "kurumun_belirttigi_yon": yon, "potansiyel": k.get("potansiyel"), "link": k.get("href")})
    return out


def hedeffiyat_ayristir(kartlar, kodlar, cfg):
    out = []
    for k in kartlar:
        t = k["t"]
        kod = kod_bul(t, kodlar)
        kurum, grup, kademe = kurum_bul(t, cfg)
        m = re.search(SAYI + r"\s*(?:₺|TL)", t)
        if len(kod) != 1 or not m:
            continue
        out.append({"kaynak": "hedeffiyat.com.tr", "teyit": "toplayici", "kurum": kurum or "(kurum ayristirilamadi)",
                    "kademe": kademe, "grup": grup or "yerli", "tarih": tarih_bul(t), "tip": "hedef_fiyat",
                    "baslik": t[:160], "semboller": kod, "hedef_tl": sayi(m.group(1)), "tavsiye": tavsiye_bul(t),
                    "link": k.get("href")})
    return out


# ------------------------------------------------------------------ kaynak 3: haber (◐)
def haber(kodlar, cfg):
    out, gor = [], set()
    simdi = dt.datetime.now(dt.timezone.utc)
    for q in cfg.get("haber_sorgulari") or []:
        time.sleep(0.8)
        url = "https://news.google.com/rss/search?q=" + quote(q + " when:7d") + "&hl=tr&gl=TR&ceid=TR:tr"
        f = feedparser.parse(url, agent=UA)
        for e in f.entries[:15]:
            baslik = temiz(getattr(e, "title", ""))
            anahtar = re.sub(r"\W+", "", baslik.lower())[:80]
            if not baslik or anahtar in gor:
                continue
            pp = getattr(e, "published_parsed", None)
            if pp and (simdi - dt.datetime(*pp[:6], tzinfo=dt.timezone.utc)).days > 7:
                continue
            kurum, grup, kademe = kurum_bul(baslik, cfg)
            ilgili = kurum or re.search(r"hedef fiyat|model portf|kredi not|upgrade|downgrade|tavsiye", baslik, re.I)
            govde = re.sub(r"\s+-\s+[^-]{2,40}$", "", baslik)   # " - Investing.com Türkiye" gibi kaynak eki eslesmeye girmez
            semb = sorted(set(kod_bul(govde, kodlar)) | {v for k_, v in SIRKET_ADLARI.items() if re.search(r"\b" + re.escape(k_), govde)})
            turkiye = semb or re.search(TURKIYE, govde, re.I)
            if not ilgili or not turkiye:   # yabanci hisse haberleri (CRH, Dell vb.) elenir
                continue
            gor.add(anahtar)
            out.append({"kaynak": "Google News", "teyit": "ikincil", "kurum": kurum, "kademe": kademe, "grup": grup,
                        "tarih": dt.date(*pp[:3]).isoformat() if pp else None,
                        "tip": "takas" if re.search(TAKAS, baslik, re.I) else tip_bul(baslik),
                        "baslik": baslik[:200], "semboller": semb, "hedef_tl": None,
                        "tavsiye": None, "link": getattr(e, "link", ""), "sorgu": q})
    return out


# ------------------------------------------------------------------ arsiv ve revizyon
def anahtar(k):
    h = "|".join(str(k.get(x)) for x in ("kaynak", "kurum", "semboller", "hedef_tl", "tarih", "baslik"))
    return hashlib.sha1(h.encode()).hexdigest()[:16]


def arsiv_oku():
    """20.11 ilk calismanin hatali kayitlari (kurumsuz toplayici kartlari, Turkiye disi haberler) okumada elenir."""
    kayit = []
    for yol in sorted(glob.glob(f"{ARSIV}/*.jsonl"))[-6:]:
        for l in open(yol, encoding="utf-8"):
            if not l.strip():
                continue
            g = json.loads(l)
            if g.get("kurum") == "(kurum ayristirilamadi)":
                continue
            if g.get("kaynak") == "Google News":
                govde = re.sub(r"\s+-\s+[^-]{2,40}$", "", g.get("baslik") or "")
                if not (g.get("semboller") and "sorgu" in g and re.search(r"\b[A-Z]{4,6}\b", govde)) and not re.search(TURKIYE, govde, re.I) \
                        and not any(re.search(r"\b" + re.escape(k), govde) for k in SIRKET_ADLARI):
                    continue
            kayit.append(g)
    return kayit


def revizyon(k, gecmis):
    if not k.get("hedef_tl") or len(k.get("semboller") or []) != 1 or not k.get("kurum"):
        return None
    onceki = [g for g in gecmis if g.get("kurum") == k["kurum"] and g.get("semboller") == k["semboller"]
              and g.get("hedef_tl") and g.get("anahtar") != k.get("anahtar") and (g.get("tarih") or "") <= (k.get("tarih") or "9")]
    if not onceki:
        return {"yon": "YENI_KAYIT", "onceki_hedef": None}
    o = sorted(onceki, key=lambda g: (g.get("tarih") or "", g.get("ilk_gorulme") or ""))[-1]
    if o["hedef_tl"] == k["hedef_tl"]:
        return {"yon": "AYNI", "onceki_hedef": o["hedef_tl"]}
    return {"yon": "YUKARI" if k["hedef_tl"] > o["hedef_tl"] else "ASAGI", "onceki_hedef": o["hedef_tl"],
            "degisim_yuzde": round((k["hedef_tl"] / o["hedef_tl"] - 1) * 100, 1), "onceki_tarih": o.get("tarih")}


def main():
    cfg = yaml.safe_load(open(CFG, encoding="utf-8"))
    kodlar, takip = evren()
    simdi = dt.datetime.now(dt.timezone.utc)
    durum, kayit = {}, []
    for ad, fn in (("is_yatirim_rss", is_yatirim), ("hedeffiyat", hedeffiyat), ("haber", haber)):
        try:
            r = fn(kodlar, cfg)
            durum[ad] = {"durum": "OK" if r else "BOS", "adet": len(r)}
            kayit += r
        except Exception as e:
            durum[ad] = {"durum": "ERISILEMEDI", "hata": str(e)[:200]}
            print(f"UYARI: {ad}: {e}", file=sys.stderr)
    if not kayit:
        print("HATA: hicbir kaynak kayit vermedi; mevcut dosyalar korundu", file=sys.stderr)
        json.dump({"uretim_utc": simdi.isoformat(), "kaynak_durumu": durum}, open("data/arastirma_akisi_durum.json", "w"), indent=1)
        return 1
    gecmis = arsiv_oku()
    bilinen = {g["anahtar"] for g in gecmis}
    os.makedirs(ARSIV, exist_ok=True)
    yeni = 0
    with open(f"{ARSIV}/{simdi:%Y-%m}.jsonl", "a", encoding="utf-8") as f:
        for k in kayit:
            k["anahtar"] = anahtar(k)
            k["ilk_gorulme"] = simdi.isoformat(timespec="minutes")
            k["takip_setinde"] = bool(set(k.get("semboller") or []) & takip)
            if k["anahtar"] not in bilinen:
                k["revizyon"] = revizyon(k, gecmis)
                f.write(json.dumps(k, ensure_ascii=False) + "\n")
                gecmis.append(k)
                bilinen.add(k["anahtar"])
                yeni += 1
    son7 = (simdi - dt.timedelta(days=7)).date().isoformat()
    son1 = (simdi - dt.timedelta(days=1)).date().isoformat()
    pencere = [g for g in gecmis if (g.get("tarih") or g["ilk_gorulme"][:10]) >= son7]
    pencere.sort(key=lambda g: (g.get("tarih") or "", g["ilk_gorulme"]), reverse=True)
    out = {"uretim_utc": simdi.isoformat(), "kaynak_durumu": durum, "yeni_kayit": yeni, "kayitlar_7gun": pencere,
           "not": "Yalniz yapilandirilmis olgular; rapor metni kopyalanmaz. teyit: birincil (kurumun kendi yayini), "
                  "toplayici (hedeffiyat.com.tr), ikincil (haber). Salt veri, tavsiye degildir."}
    json.dump(out, open("data/arastirma_akisi.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    tek, gor_b = [], set()
    for g in pencere:
        if g["kaynak"] == "Google News":
            n = re.sub(r"\W+", "", re.sub(r"\s+-\s+[^-]{2,40}$", "", g["baslik"]).lower())[:70]
            if n in gor_b:
                continue
            gor_b.add(n)
            if re.search(TAKAS, g["baslik"], re.I):
                g = dict(g, tip="takas")
        tek.append(g)
    pencere = tek
    isaret = {"birincil": "✅", "toplayici": "✅ (toplayıcı)", "ikincil": "◐"}
    L = ["# Araştırma akışı", "", "Salt veri, tavsiye değildir. Rapor metni kopyalanmaz; yalnız kurum, sembol, hedef, tavsiye, tarih.", "",
         "## Kaynak durumu", "", "| Kaynak | Durum | Adet |", "|---|---|---|"]
    L += [f"| {a} | {v['durum']} | {v.get('adet', v.get('hata', ''))} |" for a, v in durum.items()]
    L += ["| Garanti BBVA Yatırım raporları | ⛔ üye girişi | - |", "| YKY / Ziraat PDF | ⛔ robots.txt | - |",
          "| Yabancı banka raporları | ⛔ müşteriye özel; yalnız haber ◐ | - |", ""]
    hf, gor = [], set()   # kurum+sembol basina en yeni kayit
    for g in pencere:
        if g.get("hedef_tl") and g.get("semboller") and (g.get("kurum"), tuple(g["semboller"])) not in gor:
            gor.add((g.get("kurum"), tuple(g["semboller"])))
            hf.append(g)
    for baslik, sec in (("Takip setinde hedef/tavsiye (son 7 gün)", [g for g in hf if g.get("takip_setinde")]),
                        ("Diğer BIST100 hedef/tavsiye (son 7 gün)", [g for g in hf if not g.get("takip_setinde")][:30])):
        L += [f"## {baslik}", "", "| Tarih | Sembol | Kurum (kademe) | Hedef TL | Tavsiye | Revizyon | Kaynak |", "|---|---|---|---|---|---|---|"]
        for g in sec:
            r = g.get("revizyon") or {}
            if g.get("kurumun_belirttigi_onceki_hedef") and g.get("hedef_tl"):
                o = g["kurumun_belirttigi_onceki_hedef"]
                r = {"yon": "YUKARI" if g["hedef_tl"] > o else "ASAGI" if g["hedef_tl"] < o else "AYNI", "onceki_hedef": o,
                     "degisim_yuzde": round((g["hedef_tl"] / o - 1) * 100, 1)}
            elif g.get("kurumun_belirttigi_yon") in ("AYNI", "BASLATTI"):
                r = {"yon": g["kurumun_belirttigi_yon"]}
            rv = r.get("yon", "-") + (f" ({r['onceki_hedef']} → {r.get('degisim_yuzde')}%)" if r.get("onceki_hedef") and r.get("yon") in ("YUKARI", "ASAGI") else "")
            L.append(f"| {g.get('tarih') or '?'} | {','.join(g['semboller'])} | {g.get('kurum')} ({g.get('kademe') or '-'}) | "
                     f"{g['hedef_tl']} | {g.get('tavsiye') or '-'} | {rv} | {isaret.get(g['teyit'])} |")
        L.append("")
    L += ["## İş Yatırım yayınları (son 24 saat, birincil)", ""]
    L += [f"- {g.get('tarih')} [{g['baslik']}]({g['link']}) ({g['tip']})" for g in pencere
          if g["kaynak"] == "İş Yatırım RSS" and (g.get("tarih") or "") >= son1][:20] or ["- (yok)"]
    L += ["", "## Yabancı kurum ve kredi notu haberleri (son 7 gün, ◐)", ""]
    L += [f"- {g.get('tarih')} **{g.get('kurum') or '-'}**: [{g['baslik']}]({g['link']})" for g in pencere
          if g["kaynak"] == "Google News" and g.get("grup") in ("yabanci", "kredi_notu") and g.get("tip") != "takas"][:25] or ["- (yok)"]
    L += ["", "## Yabancı aracı kurum takas haberleri (son 7 gün, ◐; araştırma değil, işlem akışı)", ""]
    L += [f"- {g.get('tarih')} {g.get('kurum') or ''}: [{g['baslik']}]({g['link']})" for g in pencere
          if g["kaynak"] == "Google News" and g.get("tip") == "takas"][:8] or ["- (yok)"]
    L += ["", "## Diğer kurum haberleri (son 7 gün, ◐)", ""]
    L += [f"- {g.get('tarih')} {g.get('kurum') or ''}: [{g['baslik']}]({g['link']})" for g in pencere
          if g["kaynak"] == "Google News" and g.get("grup") not in ("yabanci", "kredi_notu") and g.get("tip") != "takas"][:15] or ["- (yok)"]
    L += ["", "Revizyon yönü yalnız bu arşivdeki önceki kayıtla karşılaştırmadır; arşiv 20.11.2026'da başladı.",
          "Gözlem amaçlıdır, tavsiye değildir."]
    open("data/arastirma_akisi.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"Tamam: {len(kayit)} kayit, {yeni} yeni; durum {durum}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
