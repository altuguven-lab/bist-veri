"""
BIST ENDEKS DONEMSEL DEGISIKLIKLERI - KAP UZERINDEN (30.10.2026). SALT VERI TOPLAMA, test degil. robots.txt'e uyar.
Neden: Internet Archive'da endeks agirlik dosyasinin yalniz 2024-25'ten ~8 kopyasi var (gecmis icin yetersiz).
Borsa Istanbul pay endeksi donemsel degisikliklerini KAP'ta da duyurur (or. "BIST Stock Indices Periodic Review").
Adimlar:
  1) Bilinen bir Borsa Istanbul endeks bildirimi sayfasindan (KAP 1666347) BIST'in KAP uye kimligini (mkkMemberOid) bulur.
  2) byCriteria ile o uyenin 2015'ten bugune tum bildirimlerini 90 gunluk dilimlerle listeler (~50 istek).
  3) Konu/ozetinde endeks gecenleri secer; her birinin sayfasini ve sayfada ACIKCA baglanan eklerini indirir
     (dosya basina 5 MB, calisma basina MAX_EK). Ayristirici, ek bicimi gorulduktan sonra yazilacak.
Kaldigi yerden devam eder. Cikti: data/endeks_kap/ (liste.json, sayfa_*.html, ekler/)
"""
import os, re, json, time, html, datetime, urllib.request, urllib.parse, urllib.robotparser

CIKTI = "data/endeks_kap"
KOK = "https://www.kap.org.tr"
UA_AD = "bist-veri"
UA = {"User-Agent": f"{UA_AD}/1.0 (kisisel arastirma amacli)", "Accept-Language": "tr-TR,tr;q=0.9"}
API = KOK + "/tr/api/disclosure/members/byCriteria"
TOHUM = [1666347]                         # bilinen BIST endeks bildirimi
BAS = datetime.date(2015, 1, 1)
BEKLE = float(os.environ.get("BEKLE_SN", "2.5"))
MAX_EK = int(os.environ.get("MAX_EK", "150"))
AZAMI = 5 * 1024 * 1024
ENDEKS_RE = re.compile(r"endeks|index|indices", re.I)
_rp = urllib.robotparser.RobotFileParser()


def robots():
    try:
        with urllib.request.urlopen(urllib.request.Request(KOK + "/robots.txt", headers=UA), timeout=20) as r:
            _rp.parse(r.read().decode("utf-8", errors="replace").splitlines())
    except Exception:
        _rp.parse([])


def getir(url, govde=None):
    if govde is None and not (_rp.can_fetch(UA_AD, url) and _rp.can_fetch("*", url)):
        raise PermissionError("robots_yasak")
    h = dict(UA, **({"Content-Type": "application/json", "Referer": KOK + "/tr/bildirim-sorgu"} if govde else {}))
    son = None
    for d in range(3):
        try:
            req = urllib.request.Request(url, data=govde, headers=h, method="POST" if govde else "GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                v = r.read(AZAMI + 1)
                tur = r.headers.get("Content-Type", "")
                ad = r.headers.get("Content-Disposition", "")
            if len(v) > AZAMI:
                raise ValueError("cok_buyuk")
            return v, tur, ad
        except (PermissionError, ValueError):
            raise
        except Exception as e:
            son = e
            time.sleep((45 if "429" in str(e) else 4) * (d + 1))
    raise son


def oid_bul(ozet):
    for idx in TOHUM:
        s = getir(f"{KOK}/tr/Bildirim/{idx}")[0].decode("utf-8", errors="replace")
        open(f"{CIKTI}/tohum_{idx}.html", "w", encoding="utf-8").write(s)
        adaylar = re.findall(r'mkkMemberOid\\?"\s*:\s*\\?"([0-9a-f]{32})', s)
        ozet["tohum_oid_adaylari"] = sorted(set(adaylar))
        if adaylar:
            return adaylar[0]
    return None


def listele(oid, d):
    gun = datetime.date.fromisoformat(d["son_tarama"]) if d.get("son_tarama") else BAS
    bugun = datetime.date.today()
    while gun <= bugun:
        bit = min(gun + datetime.timedelta(days=89), bugun)
        g = json.dumps({"fromDate": gun.isoformat(), "toDate": bit.isoformat(), "mkkMemberOidList": [oid],
                        "subjectList": []}).encode("utf-8")
        try:
            for b in json.loads(getir(API, g)[0].decode("utf-8")):
                idx = b.get("disclosureIndex")
                if idx and str(idx) not in d["tum"]:
                    d["tum"][str(idx)] = {k: b.get(k) for k in ("publishDate", "subject", "summary", "kapTitle", "attachmentCount", "relatedStocks")}
        except Exception as e:
            d["hatalar"].append(f"liste {gun}: {str(e)[:80]}")
            break
        d["son_tarama"] = (bit - datetime.timedelta(days=7)).isoformat()   # 1 hafta ortusme
        gun = bit + datetime.timedelta(days=1)
        time.sleep(BEKLE)


def ekleri_indir(d):
    sayac = 0
    secili = {i: b for i, b in d["tum"].items() if ENDEKS_RE.search(f"{b.get('subject')} {b.get('summary')}")}
    d["secili_sayisi"] = len(secili)
    for idx, b in sorted(secili.items(), key=lambda x: int(x[0])):
        if idx in d["indirilen"] or sayac >= MAX_EK:
            continue
        try:
            s = getir(f"{KOK}/tr/Bildirim/{idx}")[0].decode("utf-8", errors="replace")
            open(f"{CIKTI}/sayfa_{idx}.html", "w", encoding="utf-8").write(s)
            ekler = []
            for u in sorted(set(re.findall(r'(?:href=\\?"|\\?")(/tr/api/file/download/[^"\\]+|/tr/api/BildirimPdf/[^"\\]+)', s))):
                try:
                    v, tur, ad = getir(KOK + u)
                    m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', ad)
                    dosya = f"{idx}_" + re.sub(r"[^A-Za-z0-9._-]", "_", urllib.parse.unquote(m.group(1)) if m else os.path.basename(u))[:90]
                    open(f"{CIKTI}/ekler/{dosya}", "wb").write(v)
                    ekler.append({"url": u, "dosya": dosya, "tur": tur, "boyut": len(v)})
                except Exception as e:
                    ekler.append({"url": u, "hata": str(e)[:80]})
                time.sleep(BEKLE)
            d["indirilen"][idx] = ekler
        except Exception as e:
            d["hatalar"].append(f"sayfa {idx}: {str(e)[:80]}")
        sayac += 1
        time.sleep(BEKLE)


def main():
    os.makedirs(f"{CIKTI}/ekler", exist_ok=True)
    yol = f"{CIKTI}/liste.json"
    d = json.load(open(yol, encoding="utf-8")) if os.path.exists(yol) else {"tum": {}, "indirilen": {}}
    d["hatalar"] = []
    robots()
    try:
        oid = d.get("oid") or oid_bul(d)
        d["oid"] = oid
        if oid:
            listele(oid, d)
            ekleri_indir(d)
        else:
            d["hatalar"].append("oid bulunamadi - tohum sayfasina bakilacak")
    finally:
        d["guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        d["kalan"] = max(0, d.get("secili_sayisi", 0) - len(d["indirilen"]))
        json.dump(d, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"oid {d.get('oid')}, bildirim {len(d['tum'])}, endeks {d.get('secili_sayisi')}, indirilen {len(d['indirilen'])}, "
          f"kalan {d['kalan']}, hata {len(d['hatalar'])} {d['hatalar'][:3]}")


if __name__ == "__main__":
    main()
