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

v2 (17.07.2026, K6): (a) kaynak_sagligi artik HAM cekim adedini sayar
(0 = gercekten olu); suzulen adet "kaynak_detay"da. (b) Kaynak basina
YEDEKLI URL listesi - ilk dolu donen kazanir (Reuters/Dunya kirilganligi).
(c) GN istekleri arasi 0.6s gecikme + tarayici User-Agent (hiz siniri).
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
import time
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
    # Birincil / resmi (dogrudan RSS adresleri guvenilir degil/engelli cikti;
    # Google News uzerinden site filtresiyle cekilir - 09.07.2026 revizyonu)
    ("KAP",          google_news_rss("site:kap.org.tr"), 3),
    ("TCMB",         google_news_rss("TCMB faiz OR duyuru"), 3),
    ("Reuters",      [google_news_rss("Reuters Turkiye ekonomi when:7d"),
                      google_news_rss("site:reuters.com turkey")], 2),
    ("BloombergHT",  "https://www.bloomberght.com/rss", 2),
    ("AA Ekonomi",   "https://www.aa.com.tr/tr/rss/default?cat=ekonomi", 2),
    # Yerli finans
    ("Dunya",        ["https://www.dunya.com/rss",
                      "https://www.dunya.com/rss?dunya",
                      google_news_rss("dunya.com ekonomi when:7d")], 1),
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
                     "viop yorum", "vİop yorum", "opsiyonu fiz",
                     "ne zaman", "toplanti tarihi", "toplantı tarihi",
                     "hisse senedi -", "hisse yorumları", "hisse yorumlari",
                     "varant"]
# Alaka disi/SEO kaynak alan adlari - linki bu alanlari iceren kayit alinmaz
SPAM_ALANLAR = ["mshale.com"]
KAYNAK_TAVANI = 5  # tek kosumda ayni kaynaktan dosyaya girebilecek azami kayit
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


def kaynak_cek(isim, url_veya_liste, taban):
    """Tek kaynagi ceker. v2: url listesi verilirse sirayla dener, ilk
    HAM kayit getiren kazanir. Donus: (suzulen_kayitlar, ham_adet, hata)."""
    urller = url_veya_liste if isinstance(url_veya_liste, list) else [url_veya_liste]
    hata = None
    for url in urller:
        try:
            time.sleep(0.6)  # GN hiz siniri nezaketi
            feed = feedparser.parse(url, agent="Mozilla/5.0 (bist-veri haber botu)")
            if feed.bozo and not feed.entries:
                hata = str(getattr(feed, "bozo_exception", "bos"))
                continue
            if not feed.entries:
                hata = "0 kayit"
                continue
        except Exception as e:
            hata = str(e)
            continue
        ham_adet = len(feed.entries)
        kayitlar = []
        simdi_ts = datetime.datetime.now(datetime.timezone.utc)
        for e in feed.entries[:25]:
            baslik = temizle(getattr(e, "title", ""))
            link = getattr(e, "link", "")
            if not baslik or not link:
                continue
            if any(k in baslik.lower() for k in GURULTU_KALIPLARI):
                continue
            if any(a in link.lower() for a in SPAM_ALANLAR):
                continue
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
                "ilgili_semboller": semboller,
            })
        return kayitlar, ham_adet, None
    print(f"UYARI: {isim} tum URL'lerde basarisiz ({hata})", file=sys.stderr)
    return [], 0, hata


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
    kaynak_sagligi, kaynak_detay = {}, {}
    for isim, url, taban in KAYNAKLAR:
        kaynak_kayitlari, ham_adet, hata = kaynak_cek(isim, url, taban)
        kaynak_sagligi[isim] = ham_adet
        kaynak_detay[isim] = {"ham": ham_adet, "suzulen": len(kaynak_kayitlari),
                              "hata": hata}
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
        "kaynak_detay": kaynak_detay,
        "toplam_haber": len(hepsi),
        "haberler": hepsi,
    }
    os.makedirs("data", exist_ok=True)
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    print(f"Tamamlandi: {len(yeniler)} yeni haber, dosyada {len(hepsi)} kayit.")


if __name__ == "__main__":
    main()
