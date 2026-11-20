"""
TCMB YAYIN VE TAKVIM TAKIBI (20.11.2026) - SALT VERI, TAVSIYE DEGILDIR.
Neden: TCMB'nin anket ve istatistik yayinlari (Reel Kesim Guven Endeksi, KKO, Iktisadi Yonelim, Yatirim Egilimi,
UYP, Piyasa Katilimcilari Anketi vb.) brifinglerde "teyitsiz takvim" olarak kaliyordu; EVDS'te olmayan raporlar
(Yatirim Egilimi gibi) hic izlenmiyordu. robots.txt yalniz */search+results yolunu yasaklar (20.11 kontrol).

Kaynaklar (birincil):
  1) TCMB RSS: Veriler, Yayinlar, Basin Duyurulari, PPK Kararlari, Baskanin Konusmalari
  2) TCMB Veri Yayimlama Takvimi (appg.tcmb.gov.tr/igmvytsfe-dis; JavaScript uygulamasi -> Playwright, sayfanin kendi
     veri adresleri kaydedilir; ilk calisma kesif niteligindedir)
Cikti: data/tcmb_yayin.json, data/tcmb_yayin.md, data/tcmb_yayin_ham/ (takvim sayfasi ve ag kayitlari)
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request

import feedparser

TABAN = "https://www.tcmb.gov.tr"
RSS = {
    "Veriler": TABAN + "/wps/wcm/connect/TR/TCMB+TR/Bottom+Menu/Diger/RSS/Veriler",
    "Yayinlar": TABAN + "/wps/wcm/connect/TR/TCMB+TR/Bottom+Menu/Diger/RSS/Yayinlar",
    "Basin Duyurulari": TABAN + "/wps/wcm/connect/TR/TCMB+TR/Bottom+Menu/Diger/RSS/Basin+Duyurulari",
    "PPK Kararlari": TABAN + "/wps/wcm/connect/TR/TCMB+TR/Bottom+Menu/Diger/RSS/PPK+Kararlari",
    "Baskanin Konusmalari": TABAN + "/wps/wcm/connect/TR/TCMB+TR/Bottom+Menu/Diger/RSS/Baskanin+Konusmalari",
}
TAKVIM_URL = "https://appg.tcmb.gov.tr/igmvytsfe-dis/tr"
UA = "Mozilla/5.0 (bist-veri arastirma botu; gunde birkac kez)"
AY = {"oca": 1, "şub": 2, "sub": 2, "mar": 3, "nis": 4, "may": 5, "haz": 6, "tem": 7, "ağu": 8, "agu": 8, "eyl": 9,
      "eki": 10, "kas": 11, "ara": 12, "jan": 1, "feb": 2, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10,
      "nov": 11, "dec": 12}


def temiz(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def tarih_coz(s):
    """'5 Kas 2026 17:00:00' | 'Thu, 05 Nov 2026 17:00:00 +0300' | '2026-11-20' | '20.11.2026' -> (YYYY-MM-DD, HH:MM)"""
    s = s or ""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}", (f"{m.group(4)}:{m.group(5)}" if m.group(4) else None)
    m = re.search(r"(\d{1,2})[./](\d{1,2})[./](\d{4})(?:\s+(\d{1,2}):(\d{2}))?", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}", (f"{int(m.group(4)):02d}:{m.group(5)}" if m.group(4) else None)
    m = re.search(r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]{3})[A-Za-zÇĞİÖŞÜçğıöşü]*\.?\s+(\d{4})(?:\s+(\d{1,2}):(\d{2}))?", s)
    if m and m.group(2).lower() in AY:
        return f"{m.group(3)}-{AY[m.group(2).lower()]:02d}-{int(m.group(1)):02d}", (f"{int(m.group(4)):02d}:{m.group(5)}" if m.group(4) else None)
    return None, None


def getir(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml,text/xml,*/*"})
    with urllib.request.urlopen(r, timeout=40) as y:
        return y.read().decode("utf-8", errors="replace")


def rss_oku(ad, url):
    ham = getir(url)
    f = feedparser.parse(ham)
    out = []
    if f.entries:
        for e in f.entries[:40]:
            t, s = tarih_coz(getattr(e, "published", "") or getattr(e, "updated", ""))
            link = getattr(e, "link", "") or ""
            out.append({"akis": ad, "baslik": temiz(getattr(e, "title", ""))[:200], "tarih": t, "saat": s,
                        "link": link if link.startswith("http") else TABAN + link})
        if sum(1 for o in out if o["tarih"]) * 2 >= len(out) and all(o["link"] != TABAN for o in out):
            return out, "rss"
        out = []
    # yedek: duz metin/bozuk XML -> baslik (CDATA), baglanti (/wps/...), tarih ("5 Kas 2026 17:00:00")
    for m in re.finditer(r"<!\[CDATA\[(.*?)\]\]>(.{0,600}?)(/wps/wcm/connect/[^\s<\"']+)(.{0,200}?)(\d{1,2}\s+\w{3}\s+\d{4}\s+\d{1,2}:\d{2})", ham, re.S):
        t, s = tarih_coz(m.group(5))
        out.append({"akis": ad, "baslik": temiz(m.group(1))[:200], "tarih": t, "saat": s, "link": TABAN + m.group(3)})
    return out, "metin-yedek"


def takvim_oku():
    from playwright.sync_api import sync_playwright
    os.makedirs("data/tcmb_yayin_ham", exist_ok=True)
    ag = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        s = b.new_page(locale="tr-TR", user_agent=UA)

        def yanit(r):
            try:
                if "json" in (r.headers.get("content-type") or "") and len(ag) < 30:
                    ag.append({"url": r.url, "durum": r.status, "govde": r.text()[:200000]})
            except Exception as e:
                print("UYARI: yanit okunamadi", r.url, e, file=sys.stderr)
        s.on("response", yanit)
        s.goto(TAKVIM_URL, wait_until="networkidle", timeout=90000)
        s.wait_for_timeout(3000)
        metin = s.evaluate("() => document.body.innerText")
        open("data/tcmb_yayin_ham/takvim.html", "w", encoding="utf-8").write(s.content())
        b.close()
    json.dump([{k: v for k, v in a.items() if k != "govde"} | {"ornek": a["govde"][:3000]} for a in ag],
              open("data/tcmb_yayin_ham/ag.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    olay = []

    def yuru(x):
        if isinstance(x, dict):
            metinler = [v for v in x.values() if isinstance(v, str)]
            tarih = next((tarih_coz(v) for v in metinler if tarih_coz(v)[0]), (None, None))
            ad = max((v for v in metinler if len(v) > 8 and not tarih_coz(v)[0] and not v.startswith("http")), key=len, default=None)
            if tarih[0] and ad:
                olay.append({"tarih": tarih[0], "saat": tarih[1], "ad": temiz(ad)[:160], "kaynak": "takvim-json"})
            for v in x.values():
                yuru(v)
        elif isinstance(x, list):
            for v in x:
                yuru(v)
    for a in ag:
        try:
            yuru(json.loads(a["govde"]))
        except Exception:
            pass
    if not olay:   # yedek: sayfa metni satirlari "20.11.2026 10:00 Reel Kesim Guven Endeksi"
        for sat in metin.splitlines():
            t, s = tarih_coz(sat)
            ad = temiz(re.sub(r"\d{1,2}[./]\d{1,2}[./]\d{4}|\d{1,2}:\d{2}", "", sat))
            if t and len(ad) > 8:
                olay.append({"tarih": t, "saat": s, "ad": ad[:160], "kaynak": "takvim-metin"})
    tek, gor = [], set()
    for o in sorted(olay, key=lambda o: (o["tarih"], o["saat"] or "")):
        k = (o["tarih"], o["saat"], o["ad"].lower())
        if k not in gor:
            gor.add(k)
            tek.append(o)
    return tek


def main():
    simdi = dt.datetime.now(dt.timezone.utc)
    bugun = (simdi + dt.timedelta(hours=3)).date()
    durum, yayin = {}, []
    for ad, url in RSS.items():
        try:
            r, yontem = rss_oku(ad, url)
            durum[ad] = {"durum": "OK" if r else "BOS", "adet": len(r), "yontem": yontem}
            yayin += r
        except Exception as e:
            durum[ad] = {"durum": "ERISILEMEDI", "hata": str(e)[:200]}
            print(f"UYARI: {ad}: {e}", file=sys.stderr)
    takvim = []
    try:
        takvim = takvim_oku()
        durum["Veri Yayimlama Takvimi"] = {"durum": "OK" if takvim else "AYRISTIRILAMADI", "adet": len(takvim)}
    except Exception as e:
        durum["Veri Yayimlama Takvimi"] = {"durum": "ERISILEMEDI", "hata": str(e)[:200]}
        print("UYARI: takvim:", e, file=sys.stderr)
    if not yayin and not takvim:
        print("HATA: hicbir kaynak veri vermedi; mevcut dosya korundu", file=sys.stderr)
        return 1
    yedi = (bugun - dt.timedelta(days=7)).isoformat()
    ileri = (bugun + dt.timedelta(days=14)).isoformat()
    son = sorted([y for y in yayin if (y.get("tarih") or "") >= yedi], key=lambda y: (y["tarih"], y["saat"] or ""), reverse=True)
    gelecek = [o for o in takvim if bugun.isoformat() <= o["tarih"] <= ileri]
    out = {"uretim_utc": simdi.isoformat(), "kaynak_durumu": durum, "son_7_gun_yayinlar": son,
           "gelecek_14_gun_takvim": gelecek, "takvim_tum": takvim[-400:],
           "not": "TCMB birincil kaynak. Takvim ayristirmasi ilk calismada kesif niteligindedir. Salt veri, tavsiye degildir."}
    json.dump(out, open("data/tcmb_yayin.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# TCMB yayınları ve veri takvimi", "", "Kaynak: tcmb.gov.tr (birincil ✅). Salt veri, tavsiye değildir.", "",
         "| Kaynak | Durum | Adet |", "|---|---|---|"] + \
        [f"| {a} | {v['durum']} | {v.get('adet', v.get('hata', ''))} |" for a, v in durum.items()] + \
        ["", "## Son 7 gün yayımlananlar", ""] + \
        ([f"- {y['tarih']} {y['saat'] or ''} [{y['akis']}] [{y['baslik']}]({y['link']})" for y in son[:40]] or ["- (yok)"]) + \
        ["", "## Önümüzdeki 14 gün (Veri Yayımlama Takvimi)", ""] + \
        ([f"- {o['tarih']} {o['saat'] or ''} {o['ad']}" for o in gelecek[:60]] or ["- (ayrıştırılamadı ya da kayıt yok; data/tcmb_yayin_ham/ incelenmeli)"]) + \
        ["", "Gözlem amaçlıdır, tavsiye değildir."]
    open("data/tcmb_yayin.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"Tamam: {len(yayin)} yayin, {len(takvim)} takvim olayi; durum {durum}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
