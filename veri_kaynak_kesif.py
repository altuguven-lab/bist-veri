"""
VERI KAYNAGI KESFI (30.10.2026) - SALT VERI TOPLAMA, test degil. robots.txt KURALINA UYAR.
Amac: Analist hedef/tavsiye gecmisi ve hisse bazinda yabanci payi gecmisi icin aday kaynaklarin bicimini gormek.
Her kaynakta once robots.txt okunur; izin verilmeyen adres INDIRILMEZ, "robots_yasak" olarak kaydedilir.
Cikti: data/kaynak_kesif/ (ham HTML ornekleri) ve data/kaynak_kesif/ozet.json
"""
import os, re, json, time, html, datetime, urllib.request, urllib.parse, urllib.robotparser

CIKTI = "data/kaynak_kesif"
UA_AD = "bist-veri-arastirma"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; {UA_AD}/1.0; kisisel arastirma)", "Accept-Language": "tr-TR,tr;q=0.9"}
BEKLE = 1.5

ADAYLAR = {
    "isyatirim_yabanci": [
        "https://arastirma.isyatirim.com.tr/category/gunluk-raporlar/gunluk-yabanci-oranlari/",
        "https://arastirma.isyatirim.com.tr/category/gunluk-raporlar/gunluk-yabanci-oranlari/page/65/",
        "https://arastirma.isyatirim.com.tr/category/gunluk-raporlar/gunluk-yabanci-oranlari/page/130/",
        "https://arastirma.isyatirim.com.tr/2026/10/28/gunluk-yabanci-oranlari-28-10-2026/",
    ],
    "halkyatirim_analist": [
        "https://www.halkyatirim.com.tr/",
        "https://www.halkyatirim.com.tr/arastirma",
    ],
    "hedeffiyat_com_tr": [
        "https://hedeffiyat.com.tr/",
    ],
    "getborsa_analist": [
        "https://www.getborsa.com/arastirma/analist-beklentileri/index.html",
    ],
    "isyatirim_hedef_fiyat": [
        "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx",
    ],
}

_robots = {}


def izinli(url):
    p = urllib.parse.urlparse(url)
    kok = f"{p.scheme}://{p.netloc}"
    if kok not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(kok + "/robots.txt", headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                rp.parse(r.read().decode("utf-8", errors="replace").splitlines())
        except Exception:
            rp.parse([])          # robots.txt yoksa ya da okunamazsa: kisitlama yok kabul edilir
        _robots[kok] = rp
    return _robots[kok].can_fetch(UA_AD, url) and _robots[kok].can_fetch("*", url)


def getir(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read(4 * 1024 * 1024).decode("utf-8", errors="replace"), r.headers.get("Content-Type", "")


def ozetle(sayfa, url):
    linkler = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', sayfa, flags=re.S | re.I):
        u = urllib.parse.urljoin(url, html.unescape(m.group(1)))
        t = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(2))).split())
        if re.search(r"\.(pdf|xlsx?|csv)(\?|$)|analist|hedef|yabanc|beklenti|takas", u + " " + t, flags=re.I):
            linkler.append({"url": u, "metin": t[:120]})
    tablolar = len(re.findall(r"<table", sayfa, flags=re.I))
    satirlar = len(re.findall(r"<tr", sayfa, flags=re.I))
    m = re.search(r"<title>(.*?)</title>", sayfa, flags=re.S | re.I)
    return {"baslik": " ".join(html.unescape(m.group(1)).split()) if m else "", "tablo": tablolar, "satir": satirlar,
            "ilgili_linkler": linkler[:200], "uzunluk": len(sayfa)}


def main():
    os.makedirs(CIKTI, exist_ok=True)
    ozet = {"zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "kaynaklar": {}}
    for ad, urller in ADAYLAR.items():
        kayitlar = []
        for i, url in enumerate(urller):
            if not izinli(url):
                kayitlar.append({"url": url, "durum": "robots_yasak"})
                continue
            try:
                s, tur = getir(url)
                dosya = f"{ad}_{i}.html"
                open(f"{CIKTI}/{dosya}", "w", encoding="utf-8").write(s)
                kayitlar.append({"url": url, "durum": "ok", "dosya": dosya, "tur": tur, **ozetle(s, url)})
            except Exception as e:
                kayitlar.append({"url": url, "durum": "hata", "hata": str(e)[:120]})
            time.sleep(BEKLE)
        ozet["kaynaklar"][ad] = kayitlar
    json.dump(ozet, open(f"{CIKTI}/ozet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for ad, k in ozet["kaynaklar"].items():
        print(ad, [x["durum"] for x in k])


if __name__ == "__main__":
    main()
