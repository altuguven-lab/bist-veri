"""
SAGLIK KONTROLU - Dead man's switch
Uc veri kanalinin canliligini denetler; ariza durumunda GitHub Issue acar
(Issue acilinca GitHub otomatik e-posta bildirimi gonderir).

Denetimler:
1. bist_quotes.json  : seans saatinde 30 dk'dan eskiyse ARIZA
2. haber_akisi.json  : 2 saatten eskiyse ARIZA (7/24 kanal)
3. tv_alerts_latest  : okunabilir/gecerli JSON mu (sinyal yoklugu ariza DEGIL)
4. kaynak_sagligi    : haber kaynagi 0 haber veriyorsa bilgi notu
5. Pipedream sayaci  : aylik cagri adedi esigi asarsa uyari

Ayni baslikta ACIK Issue varsa yenisi ACILMAZ (tekrar onleme).
GitHub Actions icinde GITHUB_TOKEN ve GITHUB_REPOSITORY ortam
degiskenleriyle calisir; yerelde token yoksa sadece rapor basar.
"""

import json
import os
import sys
import datetime
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "altuguven-lab/bist-veri")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

QUOTES_ESIK_DK = 30      # seans icinde fiyat dosyasi azami yasi
HABER_ESIK_SAAT = 2      # haber dosyasi azami yasi
PIPEDREAM_AYLIK_ESIK = 2500  # uyari esigi (ucretsiz plan tamponuyla)

SEANS_BAS, SEANS_SON = 7, 15   # UTC (10:00-18:00 TR)


def simdi_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def oku(yol):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_okuma_hatasi": str(e)}


def yas_dakika(iso_zaman):
    try:
        t = datetime.datetime.fromisoformat(str(iso_zaman).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=datetime.timezone.utc)
        return (simdi_utc() - t).total_seconds() / 60
    except Exception:
        return None


def seans_acik_mi():
    s = simdi_utc()
    return s.weekday() < 5 and SEANS_BAS <= s.hour < SEANS_SON


def github_api(yol, method="GET", veri=None):
    if not TOKEN:
        return None
    req = urllib.request.Request(
        f"https://api.github.com{yol}",
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "bist-saglik",
        },
        data=json.dumps(veri).encode() if veri else None,
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except Exception as e:
        print(f"UYARI: GitHub API {yol} -> {e}", file=sys.stderr)
        return None


def acik_issue_var_mi(baslik_on_eki):
    sonuc = github_api(f"/repos/{REPO}/issues?state=open&labels=saglik&per_page=50")
    if not sonuc:
        return False
    return any(i.get("title", "").startswith(baslik_on_eki) for i in sonuc)


def issue_ac(baslik, govde):
    on_ek = baslik.split(" - ")[0]  # ayni kanal icin tekrar onleme
    if acik_issue_var_mi(on_ek):
        print(f"Atlandi (acik issue var): {baslik}")
        return
    r = github_api(f"/repos/{REPO}/issues", "POST",
                   {"title": baslik, "body": govde, "labels": ["saglik"]})
    print(f"ISSUE ACILDI: {baslik}" if r else f"ISSUE ACILAMADI: {baslik}")


def main():
    arizalar = []
    bilgiler = []
    bugun = simdi_utc().strftime("%Y-%m-%d %H:%M UTC")

    # 1) Fiyat kanali
    q = oku("data/bist_quotes.json")
    if "_okuma_hatasi" in q:
        arizalar.append(("SAGLIK: FIYAT kanali", f"bist_quotes.json okunamadi: {q['_okuma_hatasi']}"))
    elif seans_acik_mi():
        yas = yas_dakika(q.get("guncelleme_zamani_utc"))
        if yas is None or yas > QUOTES_ESIK_DK:
            arizalar.append(("SAGLIK: FIYAT kanali",
                             f"bist_quotes.json seans icinde {yas and round(yas)} dk'dir guncellenmiyor (esik {QUOTES_ESIK_DK} dk)."))
        if q.get("basarili_cekim", 30) < 25:
            bilgiler.append(f"Fiyat: {q.get('basarili_cekim')}/30 sembol cekilebildi - dusuk.")

    # 2) Haber kanali
    h = oku("data/haber_akisi.json")
    if "_okuma_hatasi" in h:
        arizalar.append(("SAGLIK: HABER kanali", f"haber_akisi.json okunamadi: {h['_okuma_hatasi']}"))
    else:
        yas = yas_dakika(h.get("guncelleme_zamani_utc"))
        if yas is None or yas > HABER_ESIK_SAAT * 60:
            arizalar.append(("SAGLIK: HABER kanali",
                             f"haber_akisi.json {yas and round(yas)} dk'dir guncellenmiyor (esik {HABER_ESIK_SAAT} saat)."))
        saglik = h.get("kaynak_sagligi", {})
        oluler = [k for k, v in saglik.items() if v == 0 and not k.startswith("GN:")]
        if oluler:
            bilgiler.append("Sifir haber veren ana kaynaklar: " + ", ".join(oluler))

    # 3) Sinyal kanali (yapisal denetim)
    a = oku("data/tv_alerts_latest.json")
    if "_okuma_hatasi" in a:
        arizalar.append(("SAGLIK: SINYAL kanali", f"tv_alerts_latest.json okunamadi: {a['_okuma_hatasi']}"))
    else:
        sayac = a.get("ay_sayac", {})
        if sayac.get("adet", 0) > PIPEDREAM_AYLIK_ESIK:
            arizalar.append(("SAGLIK: SINYAL kanali (kota)",
                             f"Pipedream aylik cagri {sayac.get('adet')} - esik {PIPEDREAM_AYLIK_ESIK} asildi, plan limitini kontrol et."))

    # Raporla / Issue ac
    print(f"Saglik kontrolu {bugun} | ariza: {len(arizalar)} | bilgi: {len(bilgiler)}")
    for b in bilgiler:
        print("BILGI:", b)
    for baslik, detay in arizalar:
        tam_baslik = f"{baslik} - {simdi_utc().strftime('%d.%m.%Y')}"
        issue_ac(tam_baslik, detay + f"\n\nKontrol zamani: {bugun}\nRunbook: FELAKET_RUNBOOK.md")

    # Ariza varsa job'i kirmizi bitir ki Actions listesinde de gorunsun
    sys.exit(1 if arizalar else 0)


if __name__ == "__main__":
    main()
