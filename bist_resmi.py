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
HEDEF = {  # sayfadaki satir adi (regex) -> kisa ad
    r"\bBIST\s*100\b|\bXU100\b": "XU100",
    r"\bBIST\s*30\b|\bXU030\b": "XU030",
    r"\bBIST\s*BANKA|\bXBANK\b": "XBANK",
    r"\bBIST\s*S[İI]NA[İI]|\bXUSIN\b": "XUSIN",
    r"\bBIST\s*HOLD|\bXHOLD\b": "XHOLD",
    r"\bBIST\s*TÜM\b|\bXUTUM\b": "XUTUM",
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
        i_son = sutun(bas, "son değer", "son deger", "son", "değer", "kapanış", "kapanis")
        i_yuz = sutun(bas, "%", "değişim", "degisim", "bugün", "bugun")
        i_hac = sutun(bas, "hacim", "hacm")
        for sat in t.get("satir", []):
            if not sat:
                continue
            ad_metin = sat[0]
            for desen, kisa in HEDEF.items():
                if kisa in sonuc or not re.search(desen, ad_metin, re.I):
                    continue
                if re.search(r"\b100\b", ad_metin) and kisa == "XU030":
                    continue
                son = sayi(sat[i_son]) if i_son is not None and i_son < len(sat) else None
                if son is None:  # basliklar eslesmediyse satirdaki ilk sayi
                    son = next((sayi(x) for x in sat[1:] if sayi(x) is not None), None)
                sonuc[kisa] = {"ad": ad_metin, "son": son,
                               "degisim_yuzde": sayi(sat[i_yuz]) if i_yuz is not None and i_yuz < len(sat) else None,
                               "hacim_tl": sayi(sat[i_hac]) if i_hac is not None and i_hac < len(sat) else None,
                               "ham_satir": sat, "basliklar": bas}
    return sonuc


def main():
    simdi = dt.datetime.now(dt.timezone.utc)
    os.makedirs("data/bist_resmi_ham", exist_ok=True)
    ag, veri, durum, hata = [], {}, "ERISILEMEDI", None
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            sayfa = b.new_page(locale="tr-TR", user_agent="Mozilla/5.0 (X11; Linux x86_64) bist-veri-arastirma-botu (gunde bir kez)")

            def yanit(r):
                try:
                    if "json" in (r.headers.get("content-type") or "") and len(ag) < 40:
                        govde = r.text()
                        ag.append({"url": r.url, "durum": r.status, "boyut": len(govde), "ornek": govde[:1500]})
                except Exception:
                    pass
            sayfa.on("response", yanit)
            sayfa.goto(URL, wait_until="networkidle", timeout=90000)
            try:  # piyasa tablosu dolana kadar bekle (rakam iceren bir hucre)
                sayfa.wait_for_function("""() => [...document.querySelectorAll('table tbody td')]
                    .some(td => /\\d{1,3}(\\.\\d{3})*,\\d{2}/.test(td.innerText))""", timeout=30000)
            except Exception:
                pass
            veri = sayfa.evaluate(JS_TABLOLAR)
            open("data/bist_resmi_ham/sayfa.html", "w", encoding="utf-8").write(sayfa.content())
            b.close()
    except Exception as e:
        hata = str(e)[:300]
        print("HATA:", hata, file=sys.stderr)
    json.dump(ag, open("data/bist_resmi_ham/ag.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    endeks = ayristir(veri) if veri else {}
    if veri:
        durum = "OK" if endeks.get("XU100", {}).get("son") else "AYRISTIRILAMADI"
    tr = simdi + dt.timedelta(hours=3)
    out = {"uretim_utc": simdi.isoformat(), "uretim_tr": tr.strftime("%Y-%m-%d %H:%M"), "kaynak": URL,
           "durum": durum, "hata": hata, "sayfa_zamani": veri.get("saat") if veri else None,
           "endeksler": endeks, "tablo_sayisi": len(veri.get("tablolar", [])) if veri else 0,
           "kartlar_ornek": (veri.get("kartlar") or [])[:20] if veri else [],
           "not": "borsaistanbul.com ana sayfasindaki tablo; site verisi gecikmeli olabilir. Salt veri, tavsiye degildir."}
    json.dump(out, open("data/bist_resmi.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if durum == "OK" and tr.hour >= 18:  # yalniz seans sonrasi okuma "gun sonu" sayilir
        yol = "data/bist_resmi_gecmis.json"
        g = json.load(open(yol, encoding="utf-8")) if os.path.exists(yol) else {}
        g[tr.strftime("%Y-%m-%d")] = {k: {"son": v["son"], "degisim_yuzde": v["degisim_yuzde"]} for k, v in endeks.items()}
        json.dump(dict(sorted(g.items())[-800:]), open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"durum {durum}; endeksler {list(endeks)}; json adresleri {len(ag)}")
    return 0 if durum != "ERISILEMEDI" else 1


if __name__ == "__main__":
    sys.exit(main())
