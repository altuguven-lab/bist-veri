"""
KAYNAK KESFI 2 (30.10.2026) - SALT VERI TOPLAMA, test degil. robots.txt KURALINA UYAR. Uye girisi gerektiren
icerige dokunulmaz, adres tahmini yapilmaz: yalniz sayfalarda ACIKCA verilen baglantilar izlenir.
A) Yabanci orani: ayristirilamayan 2022-23 raporlarindan 4 ornek + ayrisan 2 ornek indirilir; metin ve sayfadaki
   tum PDF baglantilari kaydedilir (gunluk "Yabanci Oranlari Tablosu" PDF'ine acik baglanti var mi?).
B) Endeks uyelik: Internet Archive CDX'te borsaistanbul.com/files/ ve /data/ altindaki endeks/agirlik dosyalari
   onek (prefix) sorgusuyla listelenir (ilk denemede tam adres sorgusu 0 sonuc verdi).
Cikti: data/kaynak_kesif2/ozet.json ve ornek dosyalar
"""
import os, re, json, time, html, datetime, urllib.request, urllib.parse, urllib.robotparser

CIKTI = "data/kaynak_kesif2"
UA_AD = "bist-veri-arastirma"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; {UA_AD}/1.0; kisisel arastirma)", "Accept-Language": "tr-TR,tr;q=0.9"}
_robots = {}


def izinli(url):
    p = urllib.parse.urlparse(url)
    kok = f"{p.scheme}://{p.netloc}"
    if kok not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            with urllib.request.urlopen(urllib.request.Request(kok + "/robots.txt", headers=UA), timeout=20) as r:
                rp.parse(r.read().decode("utf-8", errors="replace").splitlines())
        except Exception:
            rp.parse([])
        _robots[kok] = rp
    return _robots[kok].can_fetch(UA_AD, url) and _robots[kok].can_fetch("*", url)


def getir(url, zaman=60):
    if not izinli(url):
        raise PermissionError("robots_yasak")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=zaman) as r:
        return r.read(6 * 1024 * 1024)


def metin(s):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)).split())


def yabanci_ornekleri(ozet):
    d = json.load(open("data/yabanci_oran_arsiv.json", encoding="utf-8"))
    ays = [k["url"] for k in d["kayitlar"] if not k.get("ayristi")]
    ays_ok = [k["url"] for k in d["kayitlar"] if k.get("ayristi")]
    secim = [ays[0], ays[len(ays) // 3], ays[2 * len(ays) // 3], ays[-1], ays_ok[0], ays_ok[-1]]
    out = []
    for i, u in enumerate(secim):
        try:
            s = getir(u).decode("utf-8", errors="replace")
            open(f"{CIKTI}/yabanci_ornek_{i}.html", "w", encoding="utf-8").write(s)
            t = metin(s)
            j = t.lower().find("yabancı")
            pdf = sorted(set(urllib.parse.urljoin(u, html.unescape(x)) for x in re.findall(r'href="([^"]+\.pdf[^"]*)"', s, flags=re.I)))
            out.append({"url": u, "ayristi_mi": u in ays_ok, "metin_parcasi": t[max(0, j - 200): j + 1500], "pdf_baglantilari": pdf})
        except Exception as e:
            out.append({"url": u, "hata": str(e)[:120]})
        time.sleep(1.5)
    ozet["yabanci_ornekleri"] = out


def cdx_onek(ozet):
    sonuc = {}
    for onek in ["borsaistanbul.com/files/", "borsaistanbul.com/data/", "borsaistanbul.com/datum/",
                 "www.borsaistanbul.com/files/", "www.borsaistanbul.com/data/"]:
        q = urllib.parse.urlencode({"url": onek, "matchType": "prefix", "output": "json", "fl": "original,timestamp,statuscode,digest",
                                    "filter": "statuscode:200", "collapse": "digest", "limit": "20000"})
        try:
            satir = json.loads(getir(f"https://web.archive.org/cdx/search/cdx?{q}", zaman=180).decode("utf-8") or "[]")
            kayit = [dict(zip(satir[0], s)) for s in satir[1:]] if satir else []
            ilgili = [k for k in kayit if re.search(r"endeks|agirlik|index|weight|xu0|xu100|bist", k["original"], flags=re.I)]
            adlar = {}
            for k in ilgili:
                ad = k["original"].split("?")[0].lower()
                adlar.setdefault(ad, []).append(k["timestamp"])
            sonuc[onek] = {"toplam": len(kayit), "ilgili": len(ilgili),
                           "dosyalar": {a: {"adet": len(t), "ilk": min(t), "son": max(t)} for a, t in sorted(adlar.items())}}
        except Exception as e:
            sonuc[onek] = {"hata": str(e)[:150]}
        time.sleep(3)
    ozet["cdx_onek"] = sonuc


def main():
    os.makedirs(CIKTI, exist_ok=True)
    ozet = {"zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for adim in (yabanci_ornekleri, cdx_onek):
        try:
            adim(ozet)
        except Exception as e:
            ozet[adim.__name__ + "_hata"] = str(e)[:200]
    json.dump(ozet, open(f"{CIKTI}/ozet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for o in ozet.get("yabanci_ornekleri", []):
        print(o["url"][-28:], o.get("ayristi_mi"), len(o.get("pdf_baglantilari", [])), o.get("hata", ""))
    for k, v in ozet.get("cdx_onek", {}).items():
        print(k, v.get("toplam"), v.get("ilgili"), v.get("hata", ""))


if __name__ == "__main__":
    main()
