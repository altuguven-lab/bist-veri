"""
BIST ENDEKS DONEM DUYURULARI - KESIF (30.10.2026). SALT VERI TOPLAMA, test degil.
Amac: Gecmis BIST 30/50/100 uyelik degisikliklerinin kaynagini ve bicimini gormek. Ayristirici bu ciktiya
bakilarak yazilacak (bicim gorulmeden ayristirici yazilmaz).
Adimlar:
  1) BIST Pay Endeksleri sayfasini (sayfa/44) indirir; icindeki /duyuru/ ve dosya baglantilarini cikarir.
  2) Basliginda "Pay Endeksleri" / "endeks" gecen duyurulari indirir; icindeki dosya baglantilarini (pdf, xls, xlsx,
     csv, zip) indirir (dosya basina en fazla 5 MB).
  3) ID_TARAMA=1 ise /tr/duyuru/{id} sayfalarini ID_BAS..ID_BIT araliginda tarar, basliklari kaydeder
     (sayfadaki baglantilar JavaScript ile yukleniyorsa yedek yol).
  4) Guncel agirlik dosyasini (endeks_agirlik_ds_genel.csv) indirir.
Cikti: data/endeks_kesif/ (ham HTML ve dosyalar) ve data/endeks_kesif/ozet.json
"""
import os, re, json, time, html, urllib.request, urllib.parse, datetime

KOK = "https://www.borsaistanbul.com"
CIKTI = "data/endeks_kesif"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
# 30.10 v2: ilk denemede site baglantiyi yanitsiz kapatti. Tam tarayici basliklari, yeniden deneme ve
# alternatif adresler eklendi.
ALTERNATIF_SAYFALAR = [
    "https://www.borsaistanbul.com/tr/sayfa/44/bist-pay-endeksleri",
    "https://borsaistanbul.com/tr/sayfa/44/bist-pay-endeksleri",
    "https://www.borsaistanbul.com/en/indices/index-announcements",
    "https://www.borsaistanbul.com/tr/endeksler/endeks-duyurulari",
]
AZAMI_DOSYA = 5 * 1024 * 1024
BEKLE = float(os.environ.get("BEKLE_SN", "1.0"))


def getir(url, ikili=False):
    son = None
    for deneme in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                veri = r.read(AZAMI_DOSYA + 1)
                tur = r.headers.get("Content-Type", "")
            break
        except Exception as e:
            son = e
            time.sleep(5 * (deneme + 1))
    else:
        raise son
    if len(veri) > AZAMI_DOSYA:
        raise ValueError("dosya cok buyuk")
    return (veri, tur) if ikili else (veri.decode("utf-8", errors="replace"), tur)


def baglantilar(sayfa, taban):
    out = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', sayfa, flags=re.S | re.I):
        href, metin = m.group(1), re.sub(r"<[^>]+>", " ", m.group(2))
        out.append((urllib.parse.urljoin(taban, html.unescape(href)), " ".join(html.unescape(metin).split())))
    return out


def baslik(sayfa):
    m = re.search(r"<title>(.*?)</title>", sayfa, flags=re.S | re.I)
    return " ".join(html.unescape(m.group(1)).split()) if m else ""


def dosya_mi(url):
    return bool(re.search(r"\.(pdf|xlsx?|csv|zip)(\?|$)", url, flags=re.I)) or "/files/" in url


def main():
    os.makedirs(f"{CIKTI}/dosyalar", exist_ok=True)
    ozet = {"zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "duyurular": [], "hatalar": [], "sayfa_baglantilari": []}

    # 1) duyuru listesi sayfalari (alternatifli)
    b = []
    for i, adres in enumerate(ALTERNATIF_SAYFALAR):
        try:
            s, _ = getir(adres)
            open(f"{CIKTI}/liste_{i}.html", "w", encoding="utf-8").write(s)
            bb = baglantilar(s, adres)
            b += bb
            ozet.setdefault("liste_durumu", []).append({"url": adres, "durum": "ok", "uzunluk": len(s), "baglanti": len(bb)})
        except Exception as e:
            ozet.setdefault("liste_durumu", []).append({"url": adres, "durum": "hata", "hata": str(e)[:120]})
    ozet["sayfa_baglantilari"] = [{"url": u, "metin": t} for u, t in b if "/duyuru/" in u or dosya_mi(u)]

    adaylar = {u: t for u, t in b if "/duyuru/" in u}

    # 3) istege bagli ID taramasi
    if os.environ.get("ID_TARAMA") == "1":
        bas, bit = int(os.environ.get("ID_BAS", "1500")), int(os.environ.get("ID_BIT", "7700"))
        tarama = []
        for i in range(bit, bas - 1, -1):
            url = f"{KOK}/tr/duyuru/{i}"
            try:
                s, _ = getir(url)
                t = baslik(s)
                tarama.append({"id": i, "baslik": t})
                if re.search(r"pay endeks|endeks", t, flags=re.I):
                    adaylar[url] = t
            except Exception as e:
                tarama.append({"id": i, "hata": str(e)[:60]})
            time.sleep(BEKLE)
        json.dump(tarama, open(f"{CIKTI}/id_tarama.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    # 2) duyurulari ve eklerini indir
    for url, metin in sorted(adaylar.items()):
        if not re.search(r"pay.endeks|endeks", url + " " + metin, flags=re.I):
            continue
        try:
            s, _ = getir(url)
        except Exception as e:
            ozet["hatalar"].append(f"{url}: {e}")
            continue
        m = re.search(r"/duyuru/(\d+)", url)
        did = m.group(1) if m else str(abs(hash(url)))
        open(f"{CIKTI}/duyuru_{did}.html", "w", encoding="utf-8").write(s)
        tarih = re.search(r"(\d{2}[./]\d{2}[./]\d{4})", s)
        kayit = {"id": did, "url": url, "metin": metin, "baslik": baslik(s), "tarih_ilk_eslesme": tarih.group(1) if tarih else None, "dosyalar": []}
        for fu, ft in baglantilar(s, url):
            if not dosya_mi(fu):
                continue
            ad = f"{did}_" + re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(urllib.parse.urlparse(fu).path))[:80]
            try:
                veri, tur = getir(fu, ikili=True)
                open(f"{CIKTI}/dosyalar/{ad}", "wb").write(veri)
                kayit["dosyalar"].append({"url": fu, "metin": ft, "dosya": ad, "boyut": len(veri), "tur": tur})
            except Exception as e:
                kayit["dosyalar"].append({"url": fu, "metin": ft, "hata": str(e)[:80]})
            time.sleep(BEKLE)
        ozet["duyurular"].append(kayit)
        time.sleep(BEKLE)

    # 4) guncel agirlik dosyasi
    try:
        veri, _ = getir(f"{KOK}/files/endeks_agirlik_ds_genel.csv", ikili=True)
        open(f"{CIKTI}/dosyalar/guncel_endeks_agirlik_ds_genel.csv", "wb").write(veri)
    except Exception as e:
        ozet["hatalar"].append(f"agirlik csv: {e}")

    json.dump(ozet, open(f"{CIKTI}/ozet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"sayfa baglantisi {len(ozet['sayfa_baglantilari'])}, duyuru {len(ozet['duyurular'])}, "
          f"dosya {sum(len(d['dosyalar']) for d in ozet['duyurular'])}, hata {len(ozet['hatalar'])}")


if __name__ == "__main__":
    main()
