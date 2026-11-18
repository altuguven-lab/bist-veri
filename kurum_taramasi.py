#!/usr/bin/env python3
"""
KURUM TARAMASI (18.11.2026) - SALT VERI TOPLAMA VE ISARETLEME, TAVSIYE DEGILDIR.

Neden: 18.11 brifinginde "Takasbank, TSPB, BIST'te yeni olagandisi duyuru gorulmedi" yazildi; kaynaklar
aslinda acilmamisti. Sonradan bakildiginda Takasbank'in 12.11 VIOP risk parametresi guncellemesi ve
16.11 Pazartesi yayimlanan SPK bulteni 2026/81 atlanmisti. kurum_kumesi.py yalniz >= 5 hisselik kumeleri
yakaladigi icin tekil kurum bildirimleri (SPK bulteni, Takasbank duyurusu) hic listelenmiyordu.

Ilke: brifing "baktim, yok" diyebilmek icin bu dosyadaki ERISIM KAYDINA dayanir. Erisilemeyen ya da
bayat kalan kaynak "yok" sayilmaz; "kontrol edilemedi" olarak raporlanir.

Kaynaklar:
  A) KAP arsivi (data/arsiv/kap/YYYY/MM/DD.json.gz, veri_arsivi.py): SPK, BIST, Takasbank, MKK, KAP,
     portfoy yonetim sirketleri ve tasfiye/tedbir/kayyum iceren TUM bildirimler (kume esigi yok).
  B) Kurumlarin kendi sayfalari (robots.txt'e uyar, adres tahmini yapmaz):
     SPK bulten listesi (+ en son bultenin PDF metninden karar turleri), Takasbank duyurulari,
     TSPB duyurulari, BIST duyurulari.
  C) Izleme listesi (config/kurum_izleme.yml): sirket adlari, konular, hisse kodlari -> KAP arsivinde arar.
  D) Takvim (data/takvim.json): bu ve gelecek haftanin olaylari; kaynagi/teyidi olmayanlar ayrica listelenir.

Cikti: data/kurum_taramasi.json, data/kurum_taramasi.md
"""
import datetime as dt
import glob
import gzip
import html
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser

TR = dt.timezone(dt.timedelta(hours=3))
CIKTI_JSON = "data/kurum_taramasi.json"
CIKTI_MD = "data/kurum_taramasi.md"
PENCERE_GUN = 7
MIN_ARALIK_SAAT = float(os.environ.get("KURUM_MIN_ARALIK_SAAT", "3"))   # siteleri yormamak icin
UA_AD = "bist-veri-arastirma"
UA = {"User-Agent": f"Mozilla/5.0 (compatible; {UA_AD}/1.0; kisisel arastirma)",
      "Accept-Language": "tr-TR,tr;q=0.9", "Accept-Encoding": "gzip, deflate"}

AYLAR = {"ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5, "haziran": 6,
         "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11,
         "kasim": 11, "aralık": 12, "aralik": 12}
TARIH_RE = re.compile(
    r"(\d{1,2})[./](\d{1,2})[./](\d{4})"                                       # 17.11.2026
    r"|(\d{4})-(\d{2})-(\d{2})"                                                # 2026-11-17
    r"|(\d{1,2})\s+(ocak|şubat|subat|mart|nisan|mayıs|mayis|haziran|temmuz|ağustos|agustos|eylül|eylul"
    r"|ekim|kasım|kasim|aralık|aralik)\s+(\d{4})", re.I)

KRITIK = re.compile(r"temerr|tedbir|işlem yasa|islem yasa|işlem iptal|islem iptal|sırası kapat|sirasi kapat"
                    r"|tasfiye|kayyum|kayyım|tmsf|suç duyuru|suc duyuru|idari para|izin iptal|faaliyet izni"
                    r"|risk parametre|teminat|devre kesici kural|olağanüstü|olaganustu|brüt takas|brut takas"
                    r"|kredili işlem|kredili islem|açığa satış|aciga satis", re.I)
KURUM_KAP = re.compile(r"SERMAYE PİYASASI KURULU|BORSA İSTANBUL A\.Ş|TAKAS VE SAKLAMA|MERKEZİ KAYIT|"
                       r"KAMUYU AYDINLATMA|SERMAYE PİYASASI ARACI KURULUŞLARI|TÜRKİYE SERMAYE PİYASALARI", re.I)
GURULTU = re.compile(r"Devre Kesici Bildirimi|Günlük Bülten|Pay Alım Satım Bildirimi|Hak Kullanımı|"
                     r"Borçlanma Araçlarının / Kira|Varantların veya Sertifikaların|İtfa/Kupon|"
                     r"Şirket Genel Bilgi Formu|Nakit Ödeme", re.I)
PORTFOY = re.compile(r"PORTFÖY YÖNETİMİ|PORTFOY YONETIMI|GİRİŞİM SERMAYESİ PORTFÖY", re.I)

# Kaynak -> sayfadaki en son kaydin yasi bu kadar gunu asarsa BAYAT (sayfa degismis/donmus olabilir)
BAYAT_GUN = {"spk_bulten": 10, "takasbank": 21, "tspb": 45, "bist": 21}


# ---------------------------------------------------------------- yardimcilar
def simdi():
    return dt.datetime.now(TR)


def tarih_coz(s):
    m = TARIH_RE.search(s or "")
    if not m:
        return None
    try:
        if m.group(1):
            return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        if m.group(4):
            return dt.date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
        return dt.date(int(m.group(9)), AYLAR[m.group(8).lower()], int(m.group(7)))
    except (ValueError, KeyError):
        return None


AY_KISA = {"oca": 1, "şub": 2, "sub": 2, "mar": 3, "nis": 4, "may": 5, "haz": 6, "tem": 7, "ağu": 8, "agu": 8,
           "eyl": 9, "eki": 10, "kas": 11, "ara": 12}


def gun_ay_kutulari(sayfa_html, bugun):
    """Takasbank listesi tarihi yilsiz iki kutuda verir: <div class="day">17</div><div class="month">Kas</div>.
    Bunlar 17.11.YYYY bicimine cevrilir; ay bugunden ilerideyse onceki yil kabul edilir."""
    def cevir(m):
        ay = AY_KISA.get(m.group(2).strip().lower()[:3])
        if not ay:
            return m.group(0)
        yil = bugun.year - (1 if ay > bugun.month else 0)
        return f" {int(m.group(1)):02d}.{ay:02d}.{yil} "
    return re.sub(r'<div class="day">\s*(\d{1,2})\s*</div>\s*<div class="month">\s*([^<]{3,10})</div>',
                  cevir, sayfa_html, flags=re.I)


def metin(s):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S | re.I)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", t)).split())


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
            rp.parse([])            # robots.txt okunamazsa kisit yok sayilir (standart davranis)
        _robots[kok] = rp
    return _robots[kok].can_fetch(UA_AD, url) and _robots[kok].can_fetch("*", url)


def getir(url, zaman=30, azami=8 * 1024 * 1024):
    if not izinli(url):
        raise PermissionError("robots.txt izin vermiyor")
    son = None
    for deneme in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=zaman) as r:
                ham = r.read(azami)
                kod = (r.headers.get("Content-Encoding") or "").lower()
            # 18.11: borsaistanbul.com istenmedigi halde gzip donduruyor; acilmazsa sayfa bozuk okunuyordu
            if "gzip" in kod or ham[:2] == b"\x1f\x8b":
                ham = gzip.decompress(ham)
            elif "deflate" in kod:
                import zlib
                try:
                    ham = zlib.decompress(ham)
                except zlib.error:
                    ham = zlib.decompress(ham, -zlib.MAX_WBITS)
            return ham
        except PermissionError:
            raise
        except Exception as e:
            son = e
            time.sleep(3)
    raise son


def baglanti_kayitlari(sayfa_html, taban_url, filtre=None, bugun=None, baslik_tarihi_once=False, yon="oto"):
    """Sayfadaki <a> baglantilarini yayim tarihiyle birlikte dondurur.
    Her baglanti icin yalniz KENDI bolumune bakilir: onceki aday baglantinin bitisinden bu baglantiya kadar
    ("once" bolumu) ve bu baglantidan bir sonraki aday baglantiya kadar ("sonra" bolumu), en fazla 800 karakter.
    yon: "once"  -> tarih baglantidan once yazilir (Takasbank: tarih kutusu, kategori, baslik);
         "sonra" -> tarih baglantidan ve ozetten sonra, bir sonraki kayittan once yazilir (TSPB);
         "oto"   -> bitisik tarihe gore sayfa basina karar verilir (bilinmeyen sayfalar).
    Basliktaki tarih etkinlik tarihi olabilecegi icin yalniz baslik_tarihi_once=True ise (SPK: "Yayimlanma: ...")
    ya da baska tarih bulunamazsa kullanilir. Yarindan ileri tarih yayim tarihi sayilmaz."""
    bulunan = []
    for m in re.finditer(r"<a\b[^>]*href\s*=\s*[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", sayfa_html, flags=re.S | re.I):
        href, ic = m.group(1).strip(), metin(m.group(2))
        if len(ic) < 6 or href.startswith(("javascript:", "mailto:")):
            continue
        url = urllib.parse.urljoin(taban_url, href)
        if filtre and not filtre(url, ic):
            continue
        bulunan.append((m.start(), m.end(), url, ic))
    adaylar = []
    for i, (bas, son, url, ic) in enumerate(bulunan):
        onceki_son = bulunan[i - 1][1] if i else max(0, bas - 800)
        sonraki_bas = bulunan[i + 1][0] if i + 1 < len(bulunan) else son + 800
        once = metin(sayfa_html[max(onceki_son, bas - 800):bas])
        sonra = metin(sayfa_html[son:min(sonraki_bas, son + 800)])
        mo = list(TARIH_RE.finditer(once))
        ms = list(TARIH_RE.finditer(sonra))
        # baglanti metnindeki SON tarih: kart bicimli sayfalarda (TSPB) baglanti tum karti kapsar; ozetteki
        # etkinlik tarihi once, kartin altindaki yayim tarihi en sonda gelir
        ic_tarihler = list(TARIH_RE.finditer(ic))
        adaylar.append({"url": url, "ic": ic, "baslik": tarih_coz(ic_tarihler[-1].group(0)) if ic_tarihler else None,
                        "once": (len(once) - mo[-1].end(), tarih_coz(mo[-1].group(0))) if mo else None,
                        "sonra_ilk": (ms[0].start(), tarih_coz(ms[0].group(0))) if ms else None,
                        "sonra_son": (0, tarih_coz(ms[-1].group(0))) if ms else None})
    if yon == "oto":
        once_say = sum(1 for a in adaylar if a["once"] and a["once"][0] <= 5)
        sonra_say = sum(1 for a in adaylar if a["sonra_ilk"] and a["sonra_ilk"][0] <= 5)
        sira = ("once", "sonra_ilk") if once_say > sonra_say else ("sonra_ilk", "once")
    elif yon == "once":
        sira = ("once",)
    else:
        sira = ("sonra_son",)
    kayitlar, gorulen = [], set()
    yarin = (bugun or simdi().date()) + dt.timedelta(days=1)
    for a in adaylar:
        t_baslik = a["baslik"] if a["baslik"] and a["baslik"] <= yarin else None
        t = t_baslik if baslik_tarihi_once else None
        if not t:
            for taraf in sira:
                aday = a[taraf]
                if aday and aday[1] and aday[1] <= yarin:
                    t = aday[1]
                    break
        t = t or t_baslik
        if not t or (a["url"], a["ic"]) in gorulen:
            continue
        gorulen.add((a["url"], a["ic"]))
        kayitlar.append({"tarih": t.isoformat(), "baslik": a["ic"][:220], "url": a["url"]})
    kayitlar.sort(key=lambda x: x["tarih"], reverse=True)
    return kayitlar


def kaynak_sonucu(ad, url, kayitlar, bugun, hata=None, ek=None):
    son = kayitlar[0]["tarih"] if kayitlar else None
    if hata:
        durum = "ERISILEMEDI"
    elif not kayitlar:
        durum = "KAYIT_BULUNAMADI"         # sayfa geldi ama tarihli kayit cozulemedi (yapi degismis olabilir)
    elif (bugun - dt.date.fromisoformat(son)).days > BAYAT_GUN.get(ad, 21):
        durum = "BAYAT"
    else:
        durum = "OK"
    sinir = (bugun - dt.timedelta(days=PENCERE_GUN)).isoformat()
    r = {"kaynak": ad, "url": url, "durum": durum, "hata": str(hata)[:200] if hata else None,
         "en_son_kayit": son, "kontrol_tr": simdi().strftime("%Y-%m-%d %H:%M"),
         "son_7_gun": [k for k in kayitlar if k["tarih"] >= sinir][:30]}
    if ek:
        r.update(ek)
    return r


# ---------------------------------------------------------------- B) kurum sayfalari
HAM_KLASOR = "data/kurum_taramasi_ham"


def kaydet_ham(ad, s):
    """Ayristirici ayari icin sayfanin ham HTML'i saklanir (her calismada uzerine yazilir, en fazla 1,5 MB).
    Sayfa yapisi degisirse ya da KAYIT_BULUNAMADI cikarsa bu dosyaya bakilarak duzeltilir."""
    try:
        os.makedirs(HAM_KLASOR, exist_ok=True)
        open(f"{HAM_KLASOR}/{ad}.html", "w", encoding="utf-8").write(s[:1_500_000])
    except Exception as e:
        print("ham sayfa yazilamadi:", ad, e, file=sys.stderr)
def spk_bulten(bugun):
    url = f"https://spk.gov.tr/spk-bultenleri/{bugun.year}-yili-spk-bultenleri"
    try:
        s = getir(url).decode("utf-8", errors="replace")
        kaydet_ham("spk_bulten", s)
        kay = baglanti_kayitlari(s, url, lambda u, t: re.search(r"\d{4}\s*/\s*\d+", t) or u.lower().endswith(".pdf"),
                                 bugun=bugun, baslik_tarihi_once=True)
        # ayni bultene giden birden cok baglantidan numarali olani tut
        tek = {}
        for k in kay:
            no = re.search(r"(\d{4})\s*/\s*(\d+)", k["baslik"]) or re.search(r"(\d{4})-(\d+)\.pdf", k["url"])
            if no:
                anahtar = f"{no.group(1)}/{int(no.group(2))}"
                k["bulten_no"] = anahtar
                tek.setdefault(anahtar, k)
        kay = sorted(tek.values(), key=lambda x: (x["tarih"], int(x["bulten_no"].split("/")[1])), reverse=True)
        ek = {}
        if kay:
            ek["son_bulten_ozet"] = spk_pdf_ozet(kay[0])
        return kaynak_sonucu("spk_bulten", url, kay, bugun, ek=ek)
    except Exception as e:
        return kaynak_sonucu("spk_bulten", url, [], bugun, hata=e)


KARAR_TURLERI = [("islem_yasagi", r"işlem yasağı|islem yasagi"), ("tedbir", r"tedbir"),
                 ("suc_duyurusu", r"suç duyurusu|suc duyurusu"), ("idari_para_cezasi", r"idari para ceza"),
                 ("izin_iptali", r"izin(?:inin)? iptal|faaliyet izn"), ("tasfiye", r"tasfiye"),
                 ("ilke_karari", r"ilke karar"), ("halka_arz_onayi", r"halka arz|satışa ilişkin|ihraç belgesi"),
                 ("kayyum_tmsf", r"kayyum|kayyım|TMSF")]


def spk_pdf_ozet(kayit):
    """En son bultenin PDF'ini indirip karar turlerini ve gecen borsa kodlarini cikarir (ayrinti yerine sayim)."""
    url = kayit["url"]
    if not url.lower().endswith(".pdf"):
        return {"durum": "PDF_BAGLANTISI_YOK"}
    try:
        from pypdf import PdfReader
        ham = getir(url, zaman=60)
        yazi = " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(ham)).pages)
        yazi = " ".join(yazi.split())
        turler = {ad: len(re.findall(desen, yazi, flags=re.I)) for ad, desen in KARAR_TURLERI}
        kodlar = sorted(set(re.findall(r"\(([A-ZÇĞİÖŞÜ0-9]{4,6})\)", yazi)) |
                        set(re.findall(r"\b([A-Z]{4,5})\.E\b", yazi)))
        return {"durum": "OK", "bulten_no": kayit.get("bulten_no"), "sayfa_karakter": len(yazi),
                "karar_turleri": {k: v for k, v in turler.items() if v},
                "gecen_kodlar": kodlar[:60],
                "not": "Sayimlar metinde gecen ifadelerdir; karar ayrintisi icin PDF okunmalidir. "
                       "Bultende adi gecmek ilgili sirket hakkinda hukum degildir."}
    except Exception as e:
        return {"durum": "PDF_OKUNAMADI", "hata": str(e)[:200]}


def genel_sayfa(ad, url, bugun, filtre=None, yon="oto"):
    try:
        s = getir(url).decode("utf-8", errors="replace")
        kaydet_ham(ad, s)
        s = gun_ay_kutulari(s, bugun)
        return kaynak_sonucu(ad, url, baglanti_kayitlari(s, url, filtre, bugun=bugun, yon=yon), bugun)
    except Exception as e:
        return kaynak_sonucu(ad, url, [], bugun, hata=e)


def takasbank_pdf_ozet(sonuc):
    """Takasbank 'risk parametre' / 'teminat' duyurularinin PDF'inden piyasa ve yururluk bilgisini cikarir."""
    for k in sonuc.get("son_7_gun", []):
        if not re.search(r"risk parametre|teminat|marj", k["baslik"], re.I) or not k["url"].lower().endswith(".pdf"):
            continue
        try:
            from pypdf import PdfReader
            yazi = " ".join(" ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(getir(k["url"], 60))).pages).split())
            # 18.11: sayfa basligi/adres blogu degil, metnin kendisi: "guncellen", "gecerli", "itibar" gecen cumleler
            cumleler = [c.strip() for c in re.split(r"(?<=[.;:])\s+", yazi)
                        if re.search(r"güncellen|guncellen|geçerli ol|gecerli ol|itibar|yürürlü|yururlu", c, re.I)]
            tarihler = sorted({tarih_coz(m.group(0)).isoformat() for m in TARIH_RE.finditer(yazi)
                               if tarih_coz(m.group(0))})
            # degisen parametreler PDF ekinde "DEGISEN RISK PARAMETRELERI" basligindan sonra gelir
            # buyuk harfli ek basligi aranir (buyuk/kucuk harf duyarli); govdedeki "degisen risk parametreleri"
            # ifadesi eslesmesin. Bulunamazsa son eslesme kullanilir.
            m_deg = re.search(r"DEĞİŞEN R[İI]SK PARAMETRELER[İI](.{0,260})", yazi) or \
                (list(re.finditer(r"değişen risk parametreleri(.{0,260})", yazi, re.I)) or [None])[-1]
            degisen = [m_deg.group(1).strip()] if m_deg else []
            yururluk = [c for c in cumleler if re.search(r"itibar|geçerli ol|gecerli ol", c, re.I)]
            k["pdf_ozet"] = {"degisen_bolum": degisen, "yururluk": [c[:300] for c in yururluk[:2]],
                             "metindeki_tarihler": tarihler[-6:],
                             "ilgili_cumleler": [c[:300] for c in cumleler[:5]],
                             "not": "Otomatik cikarim; ayrinti ve degerler icin PDF okunmalidir."}
        except Exception as e:
            k["pdf_ozet"] = {"hata": str(e)[:200]}


# ---------------------------------------------------------------- A) ve C) KAP arsivi
def kap_bildirimleri(bugun, gun=PENCERE_GUN):
    out = []
    for i in range(gun + 1):
        g = bugun - dt.timedelta(days=i)
        yol = f"data/arsiv/kap/{g:%Y/%m/%d}.json.gz"
        if not os.path.exists(yol):
            continue
        try:
            for x in json.load(gzip.open(yol)).get("bildirimler", []):
                x["_gun"] = g.isoformat()
                out.append(x)
        except Exception as e:
            print("KAP arsivi okunamadi:", yol, e, file=sys.stderr)
    return out


def kap_ozet(x):
    return {"gun": x["_gun"], "zaman": x.get("publishDate"), "kurum": (x.get("kapTitle") or "").strip(),
            "konu": (x.get("subject") or "").strip(), "ozet": (x.get("summary") or "").strip()[:200],
            "kod": x.get("stockCodes") or "", "ilgili": (x.get("relatedStocks") or "")[:200],
            "kritik": bool(KRITIK.search(" ".join([x.get("subject") or "", x.get("summary") or ""]))),
            "url": f"https://www.kap.org.tr/tr/Bildirim/{x.get('disclosureIndex')}"}


def kap_bolumu(bildirimler, bugun):
    kurum, portfoy, kritik_diger = [], [], []
    gurultu_say = {}
    for x in bildirimler:
        baslik = x.get("kapTitle") or ""
        konu = x.get("subject") or ""
        if KURUM_KAP.search(baslik):
            if GURULTU.search(konu):
                gurultu_say[konu] = gurultu_say.get(konu, 0) + 1
                continue
            kurum.append(kap_ozet(x))
        elif PORTFOY.search(baslik):
            if not GURULTU.search(konu):
                portfoy.append(kap_ozet(x))
        elif KRITIK.search(konu + " " + (x.get("summary") or "")) and re.search(
                r"tasfiye|kayyum|kayyım|tmsf|tedbir|işlem yasa|islem yasa|suç duyuru", konu + " " + (x.get("summary") or ""), re.I):
            kritik_diger.append(kap_ozet(x))
    son_gun = max((x["_gun"] for x in bildirimler), default=None)
    return {"arsiv_son_gun": son_gun,
            "arsiv_durum": "OK" if son_gun and (bugun - dt.date.fromisoformat(son_gun)).days <= 3 else "BAYAT_YA_DA_YOK",
            "kurum_bildirimleri": sorted(kurum, key=lambda k: k["zaman"] or "", reverse=True),
            "portfoy_sirketleri": sorted(portfoy, key=lambda k: k["zaman"] or "", reverse=True)[:40],
            "tasfiye_tedbir_diger": sorted(kritik_diger, key=lambda k: k["zaman"] or "", reverse=True)[:40],
            "rutin_sayim": dict(sorted(gurultu_say.items(), key=lambda kv: -kv[1]))}


def izleme_yukle(yol="config/kurum_izleme.yml"):
    terimler, kodlar = [], []
    if not os.path.exists(yol):
        return terimler, kodlar
    try:
        import yaml
        d = yaml.safe_load(open(yol, encoding="utf-8")) or {}
        for k in d.get("terimler", []) or []:
            terimler.append(k if isinstance(k, dict) else {"terim": str(k)})
        kodlar = [str(k).strip().upper() for k in (d.get("kodlar") or []) if str(k).strip()]
    except Exception as e:
        print("izleme listesi okunamadi:", e, file=sys.stderr)
    return terimler, kodlar


def tr_kucuk(s):
    return (s or "").replace("I", "ı").replace("İ", "i").lower()


def izleme_bolumu(bildirimler):
    terimler, kodlar = izleme_yukle()
    eslesme, devre_kesici = [], {}
    for x in bildirimler:
        if "Devre Kesici Bildirimi" in (x.get("subject") or ""):
            # pay bazli devre kesici: tek tek listelenmez, izlenen kod icin gun bazinda sayilir
            for k in set((x.get("relatedStocks") or x.get("stockCodes") or "").replace(" ", "").split(",")) & set(kodlar):
                devre_kesici.setdefault(k, {}).setdefault(x["_gun"], 0)
                devre_kesici[k][x["_gun"]] += 1
            continue
        alan = tr_kucuk(" ".join([x.get("kapTitle") or "", x.get("subject") or "", x.get("summary") or ""]))
        ilgili = set((x.get("stockCodes") or "").replace(" ", "").split(",")) | \
                 set((x.get("relatedStocks") or "").replace(" ", "").split(","))
        bulunan = [t["terim"] for t in terimler if tr_kucuk(t["terim"]) in alan]
        bulunan += [k for k in kodlar if k in ilgili]
        if bulunan:
            o = kap_ozet(x)
            o["eslesen"] = bulunan
            eslesme.append(o)
    return {"terim_sayisi": len(terimler), "kod_sayisi": len(kodlar),
            "eslesmeler": sorted(eslesme, key=lambda k: k["zaman"] or "", reverse=True)[:60],
            "devre_kesici_sayim": {k: dict(sorted(v.items())) for k, v in sorted(devre_kesici.items())},
            "not": "Eslesme yalniz KAP arsivinde gecen ifadedir; ilgili sirket hakkinda hukum degildir."}


# ---------------------------------------------------------------- D) takvim
def takvim_bolumu(bugun):
    yol = "data/takvim.json"
    if not os.path.exists(yol):
        return {"durum": "DOSYA_YOK", "olaylar": [], "teyitsiz": []}
    try:
        d = json.load(open(yol, encoding="utf-8"))
    except Exception as e:
        return {"durum": f"OKUNAMADI: {e}", "olaylar": [], "teyitsiz": []}
    bas, son = bugun - dt.timedelta(days=1), bugun + dt.timedelta(days=14)
    olaylar = [o for o in d.get("olaylar", []) if bas.isoformat() <= o.get("tarih", "") <= son.isoformat()]
    olaylar.sort(key=lambda o: (o["tarih"], o.get("saat_tr") or ""))
    teyitsiz = [o for o in olaylar if o.get("teyit") != "birincil" or not o.get("kaynak")]
    gelecek_hafta_bos = not any(o["tarih"] > (bugun + dt.timedelta(days=7)).isoformat() for o in d.get("olaylar", []))
    return {"durum": "OK", "dosya_guncelleme": d.get("guncelleme"), "olaylar": olaylar, "teyitsiz": teyitsiz,
            "uyari": "Gelecek haftanin takvimi girilmemis" if gelecek_hafta_bos else None}


# ---------------------------------------------------------------- rapor
def md_yaz(r):
    L = [f"# Kurum taramasi - {r['uretim_tr']}", "",
         "Salt veri toplama; tavsiye degildir. **ERISILEMEDI / BAYAT / KAYIT_BULUNAMADI** olan kaynak icin "
         "brifing \"yok\" demez, \"kontrol edilemedi\" der.", "", "## Kaynak durumu", "",
         "| Kaynak | Durum | En son kayit | Son 7 gun |", "|---|---|---|---|"]
    for k in r["kaynaklar"]:
        L.append(f"| [{k['kaynak']}]({k['url']}) | **{k['durum']}** | {k['en_son_kayit'] or '-'} | {len(k['son_7_gun'])} |")
    kap = r["kap"]
    L.append(f"| KAP arsivi | **{kap['arsiv_durum']}** | {kap['arsiv_son_gun'] or '-'} | {len(kap['kurum_bildirimleri'])} kurum bildirimi |")
    for k in r["kaynaklar"]:
        if not k["son_7_gun"]:
            continue
        L += ["", f"## {k['kaynak']} (son 7 gun)", ""]
        for x in k["son_7_gun"][:15]:
            L.append(f"- {x['tarih']} [{x['baslik']}]({x['url']})")
            po = x.get("pdf_ozet") or {}
            if po.get("degisen_bolum") or po.get("yururluk"):
                L.append(f"  - PDF degisen: {(po.get('degisen_bolum') or ['?'])[0][:200]}")
                L.append(f"  - PDF yururluk: {(po.get('yururluk') or ['?'])[0][:220]}")
            elif po.get("hata"):
                L.append(f"  - PDF okunamadi: {po['hata'][:120]}")
        oz = k.get("son_bulten_ozet")
        if oz and oz.get("durum") == "OK":
            L.append(f"- Son bulten {oz.get('bulten_no')}: karar turleri {oz['karar_turleri'] or '-'}; "
                     f"gecen kodlar {', '.join(oz['gecen_kodlar']) or '-'}")
    L += ["", "## KAP: kurum bildirimleri (SPK, BIST, Takasbank, MKK, KAP)", ""]
    for x in kap["kurum_bildirimleri"][:40]:
        L.append(f"- {'**[KRITIK]** ' if x['kritik'] else ''}{x['zaman']} {x['kurum'][:30]} - "
                 f"[{x['konu']}]({x['url']}) {x['ozet'][:90]}")
    if kap["tasfiye_tedbir_diger"]:
        L += ["", "## KAP: tasfiye / tedbir / kayyum gecen diger bildirimler", ""]
        for x in kap["tasfiye_tedbir_diger"][:20]:
            L.append(f"- {x['zaman']} {x['kurum'][:35]} - [{x['konu']}]({x['url']}) {x['ozet'][:80]}")
    if r["izleme"]["eslesmeler"]:
        L += ["", "## Izleme listesi eslesmeleri", ""]
        for x in r["izleme"]["eslesmeler"][:20]:
            L.append(f"- {x['zaman']} {x['kurum'][:35]} - [{x['konu']}]({x['url']}) eslesen: {', '.join(x['eslesen'])}")
    if r["izleme"].get("devre_kesici_sayim"):
        L += ["", "## Izlenen kodlarda pay bazli devre kesici (gun: adet)", ""]
        for k, v in r["izleme"]["devre_kesici_sayim"].items():
            L.append(f"- {k}: " + ", ".join(f"{g[5:]}: {n}" for g, n in v.items()))
    t = r["takvim"]
    L += ["", "## Takvim (bugun-1 .. +14 gun)", ""]
    for o in t.get("olaylar", []):
        isaret = "teyitli" if o.get("teyit") == "birincil" and o.get("kaynak") else "TEYITSIZ"
        L.append(f"- {o['tarih']} {o.get('saat_tr') or 'saat ?'} {o['olay']} ({isaret})")
    if t.get("uyari"):
        L.append(f"- UYARI: {t['uyari']}")
    L += ["", "## Kontrol edilemeyenler", ""]
    for x in r["kontrol_edilemeyenler"] or ["(yok)"]:
        L.append(f"- {x}")
    L += ["", "Gozlem amaclidir, tavsiye degildir."]
    open(CIKTI_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    zorla = "--zorla" in sys.argv
    if os.path.exists(CIKTI_JSON) and not zorla:
        try:
            once = dt.datetime.fromisoformat(json.load(open(CIKTI_JSON, encoding="utf-8"))["uretim_utc"])
            if (dt.datetime.now(dt.timezone.utc) - once).total_seconds() < MIN_ARALIK_SAAT * 3600:
                print(f"Son tarama {MIN_ARALIK_SAAT} saatten yeni; atlandi (--zorla ile calisir).")
                return 0
        except Exception:
            pass
    bugun = simdi().date()
    kaynaklar = [spk_bulten(bugun)]
    tk = genel_sayfa("takasbank", "https://www.takasbank.com.tr/tr/duyurular", bugun,
                     lambda u, t: "Takasbank_Announcement" in u or "/duyuru-detay/" in u.lower(), yon="once")
    takasbank_pdf_ozet(tk)
    kaynaklar.append(tk)
    kaynaklar.append(genel_sayfa("tspb", "https://www.tspb.org.tr/duyurular/", bugun,
                                 lambda u, t: "/bilgi/" in u.lower() or "/duyuru" in u.lower(), yon="sonra"))
    kaynaklar.append(genel_sayfa("bist", "https://www.borsaistanbul.com/duyurular", bugun,
                                 lambda u, t: "/duyuru" in u.lower() or u.lower().endswith(".pdf")))
    bildirimler = kap_bildirimleri(bugun)
    kap = kap_bolumu(bildirimler, bugun)
    izleme = izleme_bolumu(bildirimler)
    takvim = takvim_bolumu(bugun)

    edilemeyen = [f"{k['kaynak']}: {k['durum']}" + (f" ({k['hata']})" if k["hata"] else "")
                  + (f", en son kayit {k['en_son_kayit']}" if k["durum"] == "BAYAT" else "")
                  for k in kaynaklar if k["durum"] != "OK"]
    oz = kaynaklar[0].get("son_bulten_ozet") or {}
    if kaynaklar[0]["durum"] == "OK" and oz.get("durum") != "OK":
        edilemeyen.append(f"spk_bulten: son bultenin PDF'i okunamadi ({oz.get('durum')})")
    if kap["arsiv_durum"] != "OK":
        edilemeyen.append(f"KAP arsivi: {kap['arsiv_durum']} (son gun {kap['arsiv_son_gun']})")
    edilemeyen += [f"takvim: {o['tarih']} {o['olay']} - birincil kaynakla teyit edilmedi" for o in takvim.get("teyitsiz", [])]
    if takvim.get("uyari"):
        edilemeyen.append(f"takvim: {takvim['uyari']}")
    if takvim.get("durum") != "OK":
        edilemeyen.append(f"takvim: {takvim.get('durum')}")

    r = {"uretim_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "uretim_tr": simdi().strftime("%Y-%m-%d %H:%M"),
         "pencere_gun": PENCERE_GUN,
         "not": "Salt veri toplama; tavsiye degildir. Brifing bu dosyayi kurum_kumesi.json ile birlikte okur. "
                "Durumu OK olmayan kaynak icin 'yok' denmez.",
         "kaynaklar": kaynaklar, "kap": kap, "izleme": izleme, "takvim": takvim,
         "kontrol_edilemeyenler": edilemeyen}
    os.makedirs("data", exist_ok=True)
    tmp = CIKTI_JSON + ".tmp"
    json.dump(r, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, CIKTI_JSON)
    md_yaz(r)
    print(json.dumps({"kaynaklar": {k["kaynak"]: k["durum"] for k in kaynaklar}, "kap": kap["arsiv_durum"],
                      "kurum_bildirimi": len(kap["kurum_bildirimleri"]), "izleme_eslesme": len(izleme["eslesmeler"]),
                      "kontrol_edilemeyen": len(edilemeyen)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
