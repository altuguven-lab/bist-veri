"""
YABANCI ORANI OLAY ARSIVI (30.10.2026) - SALT VERI TOPLAMA, test degil. robots.txt KURALINA UYAR.
Kaynak: Is Yatirim "Gunluk Yabanci Oranlari" raporlarinin HERKESE ACIK kismi (uye girisi gerektiren icerige
dokunulmaz): gunluk yabanci orani en cok artan 3 ve en cok azalan 3 hisse, ve orani en uzun suredir artan 5 hisse.
Adimlar: kategori sayfalari 1..N -> rapor adresleri; her rapor sayfasi -> acik metin ayristirilir.
Kaldigi yerden devam eder (islenen adresler saklanir); her calismada en fazla MAX_RAPOR rapor.
Cikti: data/yabanci_oran_arsiv.json
  kayitlar: [{tarih, yayin_utc, artan: [[sembol, deger]], azalan: [[sembol, deger]], surekli_artan: [[sembol, gun]], url}]
"""
import os, re, json, time, html, datetime, urllib.request, urllib.parse, urllib.robotparser

DOSYA = "data/yabanci_oran_arsiv.json"
KATEGORI = "https://arastirma.isyatirim.com.tr/category/gunluk-raporlar/gunluk-yabanci-oranlari/"
UA_AD = "bist-veri-arastirma"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; {UA_AD}/1.0; kisisel arastirma)", "Accept-Language": "tr-TR,tr;q=0.9"}
BEKLE = float(os.environ.get("BEKLE_SN", "1.5"))
MAX_RAPOR = int(os.environ.get("MAX_RAPOR", "450"))   # 30.10: 800 rapor 60 dk sinirini asti

_rp = urllib.robotparser.RobotFileParser()


def robots_hazirla():
    try:
        req = urllib.request.Request("https://arastirma.isyatirim.com.tr/robots.txt", headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            _rp.parse(r.read().decode("utf-8", errors="replace").splitlines())
    except Exception:
        _rp.parse([])


def getir(url):
    if not (_rp.can_fetch(UA_AD, url) and _rp.can_fetch("*", url)):
        raise PermissionError("robots_yasak")
    for deneme in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", errors="replace")
        except PermissionError:
            raise
        except Exception as e:
            son = e
            time.sleep(4 * (deneme + 1))
    raise son


def cift(metin, ikinci_tip=float):
    out = []
    for kod, deger in re.findall(r"([A-ZÇĞİÖŞÜ0-9]{3,6})\s*:\s*(-?\d+(?:,\d+)?)", metin):
        try:
            out.append([kod, ikinci_tip(deger.replace(",", "."))])
        except ValueError:
            pass
    return out


def ayristir(sayfa):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", sayfa, flags=re.S)
    t = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)).split())
    m = re.search(r"en çok artan hisseler;(.*?)azalan hisseler ise;(.*?)olarak görüntülenmektedir", t)
    s = re.search(r"sürekli artan hisselerden \d+ tanesi;(.*?)(?:yabancı oranları sürekli|Üye ve Müşterilere)", t)
    yayin = re.search(r'"datePublished":"([^"]+)"', sayfa)
    return {"artan": cift(m.group(1)) if m else [], "azalan": cift(m.group(2)) if m else [],
            "surekli_artan": [[k, int(v)] for k, v in re.findall(r"([A-ZÇĞİÖŞÜ0-9]{3,6})\s*:\s*(\d+)\s*gün", s.group(1))] if s else [],
            "yayin_utc": yayin.group(1) if yayin else None, "ayristi": bool(m)}


def main():
    robots_hazirla()
    d = json.load(open(DOSYA, encoding="utf-8")) if os.path.exists(DOSYA) else {"kayitlar": [], "islenen": [], "rapor_adresleri": []}
    islenen = set(d["islenen"])
    adresler = list(dict.fromkeys(d.get("rapor_adresleri", [])))
    hata = []
    # kategori sayfalari: ilk calismada hepsi, sonra yalniz ilk 3 sayfa (yeni raporlar)
    son_sayfa = 3 if d.get("kategori_tamam") else 200
    for n in range(1, son_sayfa + 1):
        url = KATEGORI if n == 1 else f"{KATEGORI}page/{n}/"
        try:
            s = getir(url)
        except Exception as e:
            if "404" in str(e):
                break
            hata.append(f"kategori {n}: {str(e)[:60]}")
            continue
        yeni = re.findall(r'href="(https://arastirma\.isyatirim\.com\.tr/\d{4}/\d{2}/\d{2}/gunluk-yabanci-oranlari-[^"/]+/)"', s)
        if not yeni:
            break
        for u in yeni:
            if u not in adresler:
                adresler.append(u)
        time.sleep(BEKLE)
    else:
        pass
    d["kategori_tamam"] = True
    sayac = 0
    for u in adresler:
        if u in islenen or sayac >= MAX_RAPOR:
            continue
        try:
            a = ayristir(getir(u))
            tarih = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", u)
            d["kayitlar"].append({"tarih": "-".join(tarih.groups()) if tarih else None, "url": u, **a})
            islenen.add(u)
        except Exception as e:
            hata.append(f"{u[-30:]}: {str(e)[:60]}")
        sayac += 1
        if sayac % 25 == 0:
            d.update({"islenen": sorted(islenen), "rapor_adresleri": adresler})
            json.dump(d, open(DOSYA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        time.sleep(BEKLE)
    d["kayitlar"].sort(key=lambda k: k.get("tarih") or "")
    d.update({"islenen": sorted(islenen), "rapor_adresleri": adresler, "guncelleme_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "kalan": len([u for u in adresler if u not in islenen]), "son_hatalar": hata[-20:],
              "ayrismayan": sum(1 for k in d["kayitlar"] if not k.get("ayristi"))})
    os.makedirs("data", exist_ok=True)
    json.dump(d, open(DOSYA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"adres {len(adresler)}, kayit {len(d['kayitlar'])}, kalan {d['kalan']}, ayrismayan {d['ayrismayan']}, hata {len(hata)}")


if __name__ == "__main__":
    main()
