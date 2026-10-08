#!/usr/bin/env python3
"""Günlük açığa satış verisini toplar + short squeeze adayı taraması.

Kaynak (birincil): İş Yatırım Araştırma "Günlük Açığa Satış Bilgileri" PDF'i — URL deseni sabit:
  https://arastirma.isyatirim.com.tr/wp-content/uploads/YYYY/MM/Aciga_Satis_Raporu_DDMMYY.pdf
Tablo: Kod, Açığa Satış Hacmi (mn TL), Toplam İşlem Hacmi (mn TL), Açığa Satış Adet (bin),
       Açığa Satış AOF, 1.Destek, 2.Destek, 1.Direnç, 2.Direnç.
Eksik günler otomatik tamamlanır (ilk çalıştırmada son ~60 günü geriye doldurur).
Yedek: data/aciga_satis_inbox/*.html|*.txt (elle bırakılan tablo; Foreks/İnfo biçimi).
Çıktı: data/aciga_satis_gunluk.json, data/aciga_satis_squeeze.json, aciga_satis_squeeze.md
Not: tavsiye değil; aday listesi kendi panelinde teyit edilir. Hata durumunda exit 0 (workflow'u bozmaz).
"""
import json, os, re, sys, glob, shutil, statistics, subprocess, tempfile, time, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta, date

DATA = os.environ.get("AS_DATA_DIR", "data")
GECMIS = os.path.join(DATA, "aciga_satis_gunluk.json")
INBOX = os.path.join(DATA, "aciga_satis_inbox")
SQZ_JSON = os.path.join(DATA, "aciga_satis_squeeze.json")
SQZ_MD = os.environ.get("AS_MD", "aciga_satis_squeeze.md")
PDF_URL = "https://arastirma.isyatirim.com.tr/wp-content/uploads/%d/%02d/Aciga_Satis_Raporu_%02d%02d%02d.pdf"
GERI_GUN = 60          # ilk çalıştırmada geriye doldurma
SON_GUN_KONTROL = 7    # sonraki çalıştırmalarda eksik gün kontrolü
MAX_GUN = 250
UA = {"User-Agent": "Mozilla/5.0 (compatible; bist-veri/1.0)"}
KOD = re.compile(r"^[A-Z][A-Z0-9]{2,5}$")
# Kaynak PDF'te 21.09.2026 öncesi oranlar ~2 kat yüksek (medyan ~%22 -> ~%9): ölçüm tanımı değişmiş görünüyor.
# Seriler homojen olmadığı için z/trend yalnızca bu tarihten itibaren hesaplanır.
REJIM_BASLANGIC = os.environ.get("AS_REJIM", "2026-09-21")


def duzelt(v):
    """Kaynak birim tutarsızlıklarını giderir (idempotent). Kopya döner."""
    v = dict(v)
    a, t = v.get("as_hacmi_mn"), v.get("islem_hacmi_mn")
    if a and t and t < a:            # bazı günlerde toplam hacim milyar TL cinsinden ('1,177')
        t = t * 1000
        v["islem_hacmi_mn"] = t
    if a and t: v["as_oran_pct"] = round(a / t * 100, 2)
    ao, d1 = v.get("as_ort"), v.get("destek1")
    if ao and d1 and ao / d1 > 100:  # AOF çoğu günde x1000 ölçekli ('369.865,00' = 369,865 TL)
        v["as_ort"] = ao / 1000
    return v


def tr_sayi(s):
    """Türkçe biçim: nokta binlik, virgül ondalık. '1.847' -> 1847, '369.865,00' -> 369865.0"""
    s = (s or "").strip().replace("%", "").replace("\xa0", "")
    if not s or s in ("-", "--"): return None
    s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return None


def satirlari_ayikla(metin):
    """9 belirteçli satırlar: kod + 8 sayı (ana tablo). Aynı kod tekrar ederse ilk görülen kalır."""
    sonuc = {}
    for ln in metin.splitlines():
        p = ln.split()
        if len(p) != 9 or not KOD.match(p[0]): continue
        v = [tr_sayi(x) for x in p[1:]]
        if any(x is None for x in v): continue
        asv, tv, adet, aof, d1, d2, r1, r2 = v
        if tv <= 0 or p[0] in sonuc: continue
        sonuc[p[0]] = {"as_hacmi_mn": asv, "islem_hacmi_mn": tv, "as_oran_pct": round(asv / tv * 100, 2),
                       "as_adet_bin": adet, "as_ort": aof, "destek1": d1, "destek2": d2,
                       "direnc1": r1, "direnc2": r2, "kapanis": None, "degisim_pct": None}
    return sonuc


def pdf_metin(veri):
    if shutil.which("pdftotext"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(veri); f.flush()
            return subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True, timeout=60).stdout
    try:
        import io; from pypdf import PdfReader
        return "\n".join((pg.extract_text() or "") for pg in PdfReader(io.BytesIO(veri)).pages)
    except Exception as e:
        print("  pdf okunamadı (pdftotext/pypdf yok):", e); return ""


def al(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def yukle():
    if os.path.exists(GECMIS):
        with open(GECMIS, encoding="utf-8") as f: return json.load(f)
    return {"gunler": {}}


def kaydet(obj, yol):
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, yol)


def hedef_gunler(gecmis, bugun=None):
    bugun = bugun or datetime.now(timezone(timedelta(hours=3))).date()
    mevcut = set(gecmis["gunler"])
    geri = GERI_GUN if len(mevcut) < 10 else SON_GUN_KONTROL
    out = []
    for i in range(0, geri + 1):
        d = bugun - timedelta(days=i)
        if d.weekday() < 5 and d.isoformat() not in mevcut: out.append(d)
    return out


def pdf_cek(gecmis, bugun=None):
    yeni = 0; sayac_404 = 0
    for d in hedef_gunler(gecmis, bugun):
        url = PDF_URL % (d.year, d.month, d.day, d.month, d.year % 100)
        try:
            veri = al(url)
        except urllib.error.HTTPError as e:
            if e.code != 404: print(f"  {d}: HTTP {e.code}")
            else: sayac_404 += 1
            time.sleep(0.3); continue
        except Exception as e:
            print(f"  {d}: {e}"); time.sleep(0.3); continue
        t = satirlari_ayikla(pdf_metin(veri))
        if len(t) >= 15:
            gecmis["gunler"][d.isoformat()] = t; yeni += 1; print(f"  {d}: {len(t)} hisse")
        else:
            print(f"  {d}: PDF alındı ({len(veri)} bayt) ama tablo ayıklanamadı ({len(t)} satır)")
        time.sleep(0.5)
    print(f"  (404: {sayac_404} gün — tatil/yayımlanmamış olabilir)")
    return yeni


def inbox_oku(gecmis):
    """Elle bırakılan Foreks/İnfo tablosu: kod, işlem hacmi, AS hacmi, oran, adet(mn), oran2, min, max, kapanış, ort, değ."""
    n = 0
    for yol in sorted(glob.glob(os.path.join(INBOX, "*"))):
        m = re.search(r"(20\d\d)-(\d\d)-(\d\d)", os.path.basename(yol))
        if not m or "-".join(m.groups()) in gecmis["gunler"]: continue
        iso = "-".join(m.groups())
        with open(yol, encoding="utf-8", errors="replace") as f: txt = re.sub(r"<[^>]+>", " ", f.read())
        t = {}
        for ln in txt.splitlines():
            p = ln.split()
            if len(p) < 11 or not KOD.match(p[0]): continue
            v = [tr_sayi(x) for x in p[1:11]]
            if sum(x is not None for x in v) < 8: continue
            t[p[0]] = {"islem_hacmi_mn": v[0], "as_hacmi_mn": v[1], "as_oran_pct": v[2], "as_ort": v[8],
                       "kapanis": v[7], "degisim_pct": v[9]}
        if t: gecmis["gunler"][iso] = t; n += 1; print(f"  inbox {iso}: {len(t)} satır")
    return n


def skorla(gecmis):
    veri = {g: {k: duzelt(v) for k, v in t.items()} for g, t in gecmis["gunler"].items() if g >= REJIM_BASLANGIC}
    gun = sorted(veri)
    if not gun: return None
    son = gun[-1]; rows = []
    for kod, s in veri[son].items():
        ser = [(g, veri[g][kod]) for g in gun if kod in veri[g] and veri[g][kod].get("as_oran_pct") is not None]
        o = [x[1]["as_oran_pct"] for x in ser]; bugun = s["as_oran_pct"]
        z = trend = None
        if len(o) >= 10:
            gecm = o[:-1][-60:]; sd = statistics.pstdev(gecm)
            z = (bugun - statistics.mean(gecm)) / sd if sd > 0 else 0.0
            trend = statistics.mean(o[-3:]) - statistics.mean(o[-10:])
        aof = [x[1].get("as_ort") for x in ser]
        aof_5g = None
        if len(aof) >= 6 and aof[-1] and aof[-6]: aof_5g = (aof[-1] / aof[-6] - 1) * 100
        d1 = s.get("direnc1"); aof_son = s.get("as_ort")
        dirence_yakin = bool(d1 and aof_son and aof_son >= d1 * 0.99)
        k = {"yuksek_oran": z is not None and z >= 1.5,
             "oran_artiyor": trend is not None and trend > 0.5,
             "short_ort_5g_yukari": aof_5g is not None and aof_5g > 3.0,
             "dirence_yakin": dirence_yakin}
        rows.append({"kod": kod, "oran_pct": bugun, "as_hacmi_mn": s.get("as_hacmi_mn"),
                     "z_oran": None if z is None else round(z, 2),
                     "trend_3g_10g": None if trend is None else round(trend, 2),
                     "short_ort_5g_pct": None if aof_5g is None else round(aof_5g, 2),
                     "gecmis_gun": len(o), "kosullar": k, "skor": sum(k.values())})
    rows.sort(key=lambda r: (-r["skor"], -(r["z_oran"] if r["z_oran"] is not None else -9), -r["oran_pct"]))
    # piyasa geneli: listelenen hisselerde toplam AS hacmi / toplam işlem hacmi
    piyasa = []
    for g in gun[-30:]:
        a = sum(v.get("as_hacmi_mn") or 0 for v in veri[g].values())
        t = sum(v.get("islem_hacmi_mn") or 0 for v in veri[g].values())
        if t > 0: piyasa.append((g, round(a / t * 100, 2)))
    return {"tarih": son, "gun_sayisi": len(gun), "rejim_baslangic": REJIM_BASLANGIC, "adaylar": rows, "liste_toplam_oran_son30": piyasa,
            "uyari": "Geçmiş < 10 gün ise z/trend yok. Liste tavsiye değil, aday taramasıdır."}


def rapor(r):
    f = lambda v: "–" if v is None else f"{v:.2f}"
    L = [f"# Açığa satış / short squeeze taraması — {r['tarih']}", "", f"Geçmiş: {r['gun_sayisi']} gün ({r['rejim_baslangic']} sonrası; öncesinde kaynak oranları ~2 kat yüksek, homojen değil). {r['uyari']}", ""]
    if r["liste_toplam_oran_son30"]:
        L.append("**Listelenen hisselerde toplam açığa satış / işlem hacmi % (son günler):** " +
                 ", ".join(f"{g[5:]}: {v:.2f}" for g, v in r["liste_toplam_oran_son30"][-15:]))
    L += ["", "| Hisse | Pay % | z | Trend (3g−10g) | Short ort. 5g % | AS hacmi mn | Skor |", "|---|---|---|---|---|---|---|"]
    for x in r["adaylar"][:15]:
        L.append(f"| {x['kod']} | {x['oran_pct']:.2f} | {f(x['z_oran'])} | {f(x['trend_3g_10g'])} | {f(x['short_ort_5g_pct'])} | {x['as_hacmi_mn']:.0f} | {x['skor']}/4 |")
    L += ["", "Skor koşulları: pay z≥1,5 · 3g ort. − 10g ort. > 0,5 puan · short ortalama fiyatı 5 günde >%3 yukarıda (shortçular zararda, vekil) · short ort. fiyatı 1. dirence ≥%99 yakın."]
    return "\n".join(L) + "\n"


def main():
    os.makedirs(DATA, exist_ok=True); os.makedirs(INBOX, exist_ok=True)
    gecmis = yukle()
    try: yeni = pdf_cek(gecmis)
    except Exception as e: print("PDF çekme hatası:", e); yeni = 0
    yeni += inbox_oku(gecmis)
    for g in sorted(gecmis["gunler"])[:-MAX_GUN]: del gecmis["gunler"][g]
    gecmis["guncelleme_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    kaydet(gecmis, GECMIS)
    r = skorla(gecmis)
    if r:
        kaydet(r, SQZ_JSON)
        with open(SQZ_MD, "w", encoding="utf-8") as f: f.write(rapor(r))
    print(f"Yeni gün: {yeni}; toplam gün: {len(gecmis['gunler'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
