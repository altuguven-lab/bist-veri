"""
KANAL 3 - HABER AKISI
Turkiye ve dunya finans haberlerini RSS uzerinden ceker, evren + makro
anahtar kelimelerine gore puanlayip filtreler ve data/haber_akisi.json
dosyasina yazar. GitHub Actions tarafindan periyodik calistirilir.

Tasarim ilkeleri (Kanal 1 ile ayni):
- Tek kaynak coker ise script COKMEZ: kaynak atlanir, stderr'e uyari yazilir.
- Dosya son MAX_HABER kaydi tutar (eski kayitlar dusurulur), tekrar eden
  basliklar (ayni link) eklenmez.
- Sembol listesi BIST_SEMBOLLER ile fetch_bist.py'dekiyle birebir aynidir;
  evren degisiminde IKI dosya birlikte guncellenmelidir.

NOT: Reuters/Bloomberg dogrudan RSS vermez; Google News RSS uzerinden
site filtresiyle cekilir (dakikalar mertebesinde gecikme - bar-kapanisli
karar sistemi icin yeterli).
"""

import feedparser
import json
import datetime
import html
import os
import re
import sys
from urllib.parse import quote

# --- EVREN (fetch_bist.py ile birebir ayni tutulmali) --------------------
# EVREN REV. 07.07.2026: SASA->OTKAR, KOZAL->TRMET, DOAS->ENJSA
BIST_SEMBOLLER = [
    "AKBNK", "YKBNK", "GARAN", "ISCTR", "SAHOL", "KCHOL", "THYAO", "TAVHL",
    "EREGL", "ASELS", "ASTOR", "MGROS", "BIMAS", "TUPRS", "TOASO", "FROTO",
    "ENKAI", "TTKOM", "AEFES", "PGSUS", "HALKB", "VAKBN", "OTKAR", "PETKM",
    "SISE", "EKGYO", "TRMET", "ALARK", "ENJSA", "ULKER",
]

# Sembol adi gecmese de haberi onemli kilan makro kelimeler (kucuk harf)
MAKRO_KELIMELER = [
    "tcmb", "merkez bankasi", "merkez bankası", "faiz", "enflasyon", "tufe",
    "fed", "fomc", "ecb", "dolar/tl", "kur korumali", "spk", "bddk",
    "kap bildirimi", "temettu", "temettü", "bedelsiz", "geri alim", "geri alım",
    "nato", "savunma sanayi", "ihale", "tahvil", "cds", "moody", "fitch", "s&p",
    "brent", "petrol", "altin", "altın", "dogalgaz", "doğalgaz",
]

# --- KAYNAKLAR ------------------------------------------------------------
# (isim, url, taban_puan) - taban_puan: kaynagin guvenilirlik/oncelik agirligi
def google_news_rss(sorgu):
    return ("https://news.google.com/rss/search?q=" + quote(sorgu) +
            "&hl=tr&gl=TR&ceid=TR:tr")

KAYNAKLAR = [
    # Birincil / resmi
    ("KAP",          "https://www.kap.org.tr/tr/rss/bildirim", 3),
    ("TCMB",         "https://www.tcmb.gov.tr/wps/wcm/connect/tr/tcmb+tr/main+page+site+area/duyurular/rss", 3),
    # Ajanslar (Google News uzerinden site filtresi)
    ("Reuters",      google_news_rss("site:reuters.com Turkey OR borsa OR lira"), 2),
    ("BloombergHT",  "https://www.bloomberght.com/rss", 2),
    ("AA Ekonomi",   "https://www.aa.com.tr/tr/rss/default?cat=ekonomi", 2),
    # Yerli finans
    ("Dunya",        "https://www.dunya.com/rss?dunya", 1),
    ("Foreks",       google_news_rss("site:foreks.com borsa"), 1),
]

# Evrendeki her sembol icin hedefli Google News sorgusu (dusuk frekansli
# calismada bile sembol haberi kacmasin diye)
for _s in BIST_SEMBOLLER:
    KAYNAKLAR.append((f"GN:{_s}", google_news_rss(f"{_s} hisse"), 1))

DOSYA = "data/haber_akisi.json"
MAX_HABER = 100
MIN_PUAN = 2          # bu esigin altindaki haberler dosyaya yazilmaz
MAX_YAYIN_YASI_GUN = 7  # yayin tarihi bundan eskiyse alinmaz (GN 'alakali' eskileri getirir)
# Sablon/gurultu basliklari (gunluk uretilen kopya icerik) - dosyaya alinmaz
GURULTU_KALIPLARI = ["gunluk teknik analiz", "günlük teknik analiz",
                     "viop yorum", "vİop yorum", "opsiyonu fiz"]
MAX_KAYIT_YASI_GUN = 3  # 3 gunden eski kayitlar dosyadan dusurulur


def temizle(metin):
    """HTML entity ve etiketlerini temizler."""
    metin = html.unescape(metin or "")
    return re.sub(r"<[^>]+>", "", metin).strip()


def puanla(baslik, taban):
    """Basligi evren sembolleri + makro kelimelere gore puanlar,
    (puan, etiketlenen_semboller) doner."""
    b = baslik.lower()
    semboller = [s for s in BIST_SEMBOLLER if s.lower() in b]
    puan = taban + 2 * len(semboller)
    if any(k in b for k in MAKRO_KELIMELER):
        puan += 2
    return puan, semboller


def kaynak_cek(isim, url, taban):
    """Tek kaynagi ceker; hata durumunda bos liste doner (script surer)."""
    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            print(f"UYARI: {isim} okunamadi ({feed.bozo_exception})", file=sys.stderr)
            return []
        kayitlar = []
        simdi_ts = datetime.datetime.now(datetime.timezone.utc)
        for e in feed.entries[:25]:
            baslik = temizle(getattr(e, "title", ""))
            link = getattr(e, "link", "")
            if not baslik or not link:
                continue
            # Gurultu kalibi iceren basliklar elenir
            if any(k in baslik.lower() for k in GURULTU_KALIPLARI):
                continue
            # Yayin tarihi cok eskiyse elenir (tarih yoksa gecer - resmi kaynaklar icin tolerans)
            pp = getattr(e, "published_parsed", None) or getattr(e, "updated_parsed", None)
            if pp is not None:
                yas = (simdi_ts - datetime.datetime(*pp[:6], tzinfo=datetime.timezone.utc)).days
                if yas > MAX_YAYIN_YASI_GUN:
                    continue
            puan, semboller = puanla(baslik, taban)
            if puan < MIN_PUAN:
                continue
            yayin = ""
            for alan in ("published", "updated"):
                if hasattr(e, alan):
                    yayin = getattr(e, alan)
                    break
            kayitlar.append({
                "zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "yayin_zamani": yayin,
                "kaynak": isim,
                "baslik": baslik,
                "link": link,
                "puan": puan,
                "semboller": semboller,
            })
        return kayitlar
    except Exception as e:
        print(f"HATA: {isim} -> {e}", file=sys.stderr)
        return []


def main():
    # Mevcut dosyayi oku (birikim + tekrar onleme icin)
    eski = []
    if os.path.exists(DOSYA):
        try:
            with open(DOSYA, encoding="utf-8") as f:
                eski = json.load(f).get("haberler", [])
        except Exception:
            pass  # bozuk dosya -> sifirdan basla

    bilinen_linkler = {h["link"] for h in eski}
    bilinen_basliklar = {h["baslik"].lower()[:80] for h in eski}

    yeniler = []
    kaynak_sagligi = {}
    for isim, url, taban in KAYNAKLAR:
        kaynak_kayitlari = kaynak_cek(isim, url, taban)
        kaynak_sagligi[isim] = len(kaynak_kayitlari)
        for kayit in kaynak_kayitlari:
            b_norm = kayit["baslik"].lower()[:80]
            if kayit["link"] not in bilinen_linkler and b_norm not in bilinen_basliklar:
                bilinen_linkler.add(kayit["link"])
                bilinen_basliklar.add(b_norm)
                yeniler.append(kayit)

    # Yeniler basa, eskiler arkaya; yas siniri + adet siniri uygula
    simdi = datetime.datetime.now(datetime.timezone.utc)
    def taze_mi(h):
        try:
            t = datetime.datetime.fromisoformat(h["zaman_utc"].replace("Z", "+00:00"))
            return (simdi - t).days < MAX_KAYIT_YASI_GUN
        except Exception:
            return True
    hepsi = (sorted(yeniler, key=lambda h: -h["puan"]) +
             [h for h in eski if taze_mi(h)])[:MAX_HABER]

    cikti = {
        "guncelleme_zamani_utc": simdi.isoformat(),
        "kaynak_sayisi": len(KAYNAKLAR),
        "yeni_haber": len(yeniler),
        "kaynak_sagligi": kaynak_sagligi,
        "toplam_haber": len(hepsi),
        "haberler": hepsi,
    }
    os.makedirs("data", exist_ok=True)
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    print(f"Tamamlandi: {len(yeniler)} yeni haber, dosyada {len(hepsi)} kayit.")


if __name__ == "__main__":
    main()
