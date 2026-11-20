"""
BIST RESMI VERI (20.11.2026) - borsaistanbul.com ana sayfasi, gercek tarayici (Playwright) ile. SALT VERI, TAVSIYE DEGILDIR.
Neden: Brifinglerde "BIST 100 resmi kapanis ✖" kaliyordu. Ana sayfadaki piyasa tablosu JavaScript ile doluyor;
duz HTML okuyucular bos tablo goruyor. robots.txt: "User-agent: * / Allow: /" (20.11'de kontrol edildi).
Nezaket: is gununde bir kez (18:20 TR), tek sayfa.
Cikti:
  data/bist_resmi.json           son okuma: sayfadaki endeks satirlari (son deger, gunluk %, hacim) + durum
  data/bist_resmi_gecmis.json    gun -> {XU100: son, ...}  (yalniz durum OK ise eklenir)
  data/bist_resmi_ham/sayfa.html islenmis sayfa (ayristirici bozulursa buna bakilir)
  data/bist_resmi_ham/ag.json    sayfanin cagirdigi JSON adresleri (ileride dogrudan, tarayicisiz okuma icin)
Durumlar: OK / AYRISTIRILAMADI (tablo bos ya da beklenen satir yok) / ERISILEMEDI.
Not: Sitenin gosterdigi deger gecikmeli olabilir; sayfada zaman bilgisi bulunursa "sayfa_zamani" alanina yazilir.
"""
import datetime as dt
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

URL = "https://www.borsaistanbul.com/"
HEDEF = {  # sayfadaki TAM endeks adi -> kisa ad (kismi eslesme yok: "BIST BANKA DISI LIKIT 10" XBANK degildir)
    "BIST 100": "XU100", "BIST 30": "XU030", "BIST 50": "XU050", "BIST 500": "XU500",
    "BIST BANKA": "XBANK", "BIST SINAI": "XUSIN", "BIST SINAİ": "XUSIN", "BIST HOLDING VE YATIRIM": "XHOLD",
    "BIST TUM": "XUTUM", "BIST TÜM": "XUTUM", "BIST TUM-100": "XTUMY", "BIST KATILIM 100": "XK100",
    "BIST LIKIT BANKA": "XLBNK", "BIST BANKA DISI LIKIT 10": "XBLSM",
}
JS_TABLOLAR = """() => {
  const out = [];
  document.querySelectorAll('table').forEach(t => {
    const bas = [...t.querySelectorAll('thead th, thead td')].map(x => x.innerText.trim());
    const satir = [...t.querySelectorAll('tbody tr')].map(tr => [...tr.querySelectorAll('th,td')].map(x => x.innerText.trim()));
    out.push({bas, satir});
  });
  // tablo olmayan kart/liste yapilari icin yedek: rakam iceren kisa metin bloklari
  const kart = [...document.querySelectorAll('[class*=index], [class*=endeks], [class*=market], [class*=piyasa]')]
      .map(x => x.innerText.trim()).filter(s => s && s.length < 300 && /\\d/.test(s)).slice(0, 80);
  return {tablolar: out, kartlar: kart, saat: document.body.innerText.match(/\\d{2}[.:]\\d{2}(?:[.:]\\d{2})?\\s*(?:itibar|güncel|son güncelleme)[^\\n]{0,40}/i)?.[0] || null};
}"""


def sayi(s):
    """'11.408,19' / '-0,60%' / '%-0,60' / '₺ 1.234.567' -> float"""
    if s is None:
        return None
    t = re.sub(r"[^\d,.\-+]", "", str(s).replace("−", "-"))
    if not re.search(r"\d", t):
        return None
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif t.count(".") > 1:
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def sutun(bas, *anahtar):
    for i, b in enumerate(bas):
        bl = b.lower()
        if any(a in bl for a in anahtar):
            return i
    return None


def ayristir(veri):
    sonuc = {}
    for t in veri.get("tablolar", []):
        bas = t.get("bas") or []
        i_son = sutun(bas, "son değer", "son deger")
        if i_son is None:   # piyasa degeri vb. baska tablolar
            continue
        i_yuz = sutun(bas, "%", "değişim", "degisim", "bugün", "bugun")
        i_hac = sutun(bas, "hacim", "hacm")
        for sat in t.get("satir", []):
            if not sat:
                continue
            ad_metin = sat[0]
            kisa = HEDEF.get(ad_metin.strip())
            if kisa and kisa not in sonuc:
                son = sayi(sat[i_son]) if i_son < len(sat) else None
                sonuc[kisa] = {"ad": ad_metin, "son": son,
                               "degisim_yuzde": sayi(sat[i_yuz]) if i_yuz is not None and i_yuz < len(sat) else None,
                               "hacim_tl": sayi(sat[i_hac]) if i_hac is not None and i_hac < len(sat) else None,
                               "ham_satir": sat, "basliklar": bas}
    return sonuc


def json_ayristir(govde):
    """bist-indexes.php?op=getBistIndices yaniti: data[{trName, lastValue, todayPercentage, ...}]"""
    sonuc, tum = {}, {}
    for x in (json.loads(govde).get("data") or []):
        ad = (x.get("trName") or "").strip()
        kayit = {"ad": ad, "son": x.get("lastValue"), "degisim_yuzde": x.get("todayPercentage"),
                 "haftalik_yuzde": x.get("weeklyPercentage"), "aylik_yuzde": x.get("monthlyPercentage"),
                 "yilbasindan_yuzde": x.get("sinceJanuaryPercentage"), "yillik_yuzde": x.get("yearlyPercentage"),
                 "hacim_tl": x.get("tradingValue")}
        tum[ad] = kayit
        kisa = HEDEF.get(ad)
        if kisa and kisa not in sonuc:
            sonuc[kisa] = kayit
    return sonuc, tum


def islem_gunu_mu(g):
    if g.weekday() >= 5:
        return False
    try:
        import yaml
        tat = {str(x["date"]) for x in (yaml.safe_load(open("config/market_calendar.yml", encoding="utf-8")) or {}).get("full_day_holidays", [])}
    except Exception:
        tat = set()
    return g.isoformat() not in tat


def veri_tarihi(tr):
    """Okunan degerin ait oldugu islem gunu ve seans durumu (20.11 duzeltmesi: seans oncesi okuma dunun kapanisidir)."""
    g = tr.date()
    if not islem_gunu_mu(g):
        durum = "tatil_ya_da_hafta_sonu"
    elif (tr.hour, tr.minute) < (10, 0):
        durum = "seans_oncesi"
    elif (tr.hour, tr.minute) < (18, 10):
        return g.isoformat(), "seans_ici"
    else:
        return g.isoformat(), "kapanis_sonrasi"
    g -= dt.timedelta(days=1)
    while not islem_gunu_mu(g):
        g -= dt.timedelta(days=1)
    return g.isoformat(), durum


def main():
    simdi = dt.datetime.now(dt.timezone.utc)
    os.makedirs("data/bist_resmi_ham", exist_ok=True)
    ag, veri, durum, hata, endeks_json = [], {}, "ERISILEMEDI", None, None
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            sayfa = b.new_page(locale="tr-TR", user_agent="Mozilla/5.0 (X11; Linux x86_64) bist-veri-arastirma-botu (gunde bir kez)")

            def yanit(r):
                try:
                    if "getBistIndices" in r.url and r.status == 200:
                        nonlocal endeks_json
                        endeks_json = r.text()
                    if "json" in (r.headers.get("content-type") or "") and len(ag) < 40:
                        govde = r.text()
                        ag.append({"url": r.url, "durum": r.status, "boyut": len(govde), "ornek": govde[:1500]})
                except Exception as e:
                    print("UYARI: yanit okunamadi", r.url, e, file=sys.stderr)
            sayfa.on("response", yanit)
            sayfa.goto(URL, wait_until="networkidle", timeout=90000)
            try:  # piyasa tablosu dolana kadar bekle (rakam iceren bir hucre)
                sayfa.wait_for_function("""() => [...document.querySelectorAll('table tbody td')]
                    .some(td => /\\d{1,3}(\\.\\d{3})*,\\d{2}/.test(td.innerText))""", timeout=30000)
            except Exception:
                pass
            veri = sayfa.evaluate(JS_TABLOLAR)
            if not endeks_json:  # dinleyici yaniti yakalayamadiysa sayfanin kendi adresini sayfa icinden bir kez iste
                try:
                    endeks_json = sayfa.evaluate("""async () => { const r = await fetch('/bist-indexes.php?op=getBistIndices',
                        {headers: {'X-Requested-With': 'XMLHttpRequest'}}); return r.ok ? await r.text() : null; }""")
                except Exception as e:
                    print("UYARI: getBistIndices sayfa icinden alinamadi:", e, file=sys.stderr)
            open("data/bist_resmi_ham/sayfa.html", "w", encoding="utf-8").write(sayfa.content())
            b.close()
    except Exception as e:
        hata = str(e)[:300]
        print("HATA:", hata, file=sys.stderr)
    json.dump(ag, open("data/bist_resmi_ham/ag.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    endeks, tum, yontem = {}, {}, None
    if endeks_json:
        try:
            endeks, tum = json_ayristir(endeks_json)
            yontem = "getBistIndices JSON (sayfanin kendi veri adresi)"
        except Exception as e:
            print("UYARI: JSON ayristirilamadi:", e, file=sys.stderr)
    if not endeks.get("XU100") and veri:
        endeks, yontem = ayristir(veri), "tablo (yedek)"
    if veri or endeks_json:
        durum = "OK" if endeks.get("XU100", {}).get("son") else "AYRISTIRILAMADI"
    tr = simdi + dt.timedelta(hours=3)
    vt, seans = veri_tarihi(tr)
    out = {"uretim_utc": simdi.isoformat(), "uretim_tr": tr.strftime("%Y-%m-%d %H:%M"),
           "veri_tarihi": vt, "seans_durumu": seans,
           "okuma_notu": ("Deger " + vt + " kapanisidir (bugunun degil)." if seans in ("seans_oncesi", "tatil_ya_da_hafta_sonu")
                          else "Seans ici okuma: gecikmeli olabilir, kapanis degildir." if seans == "seans_ici" else "Gun sonu degeri."), "kaynak": URL,
           "durum": durum, "hata": hata, "sayfa_zamani": veri.get("saat") if veri else None,
           "yontem": yontem, "endeksler": endeks, "tum_endeksler": tum,
           "seans_oncesi_not": "09:55 oncesi okumada 'Bugun %' 0 olur ve son deger bir onceki gunun kapanisidir." if tr.hour < 10 else None,
           "tablo_sayisi": len(veri.get("tablolar", [])) if veri else 0,
           "kartlar_ornek": (veri.get("kartlar") or [])[:20] if veri else [],
           "not": "borsaistanbul.com ana sayfasindaki tablo; site verisi gecikmeli olabilir. Salt veri, tavsiye degildir."}
    json.dump(out, open("data/bist_resmi.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if durum == "OK" and seans != "seans_ici":
        # kapanis sonrasi: bugunun gun sonu. Seans oncesi/tatil: onceki islem gunu eksikse kapanisla doldurulur.
        yol = "data/bist_resmi_gecmis.json"
        g = json.load(open(yol, encoding="utf-8")) if os.path.exists(yol) else {}
        if seans == "kapanis_sonrasi" or vt not in g:
            g[vt] = {k: {"son": v["son"], "degisim_yuzde": v["degisim_yuzde"] if seans == "kapanis_sonrasi" else None,
                         "hacim_tl": v.get("hacim_tl"), "kaynak_okuma": seans} for k, v in endeks.items()}
            json.dump(dict(sorted(g.items())[-800:]), open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"durum {durum}; endeksler {list(endeks)}; json adresleri {len(ag)}")
    return 0 if durum != "ERISILEMEDI" else 1


if __name__ == "__main__":
    sys.exit(main())
