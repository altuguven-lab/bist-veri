"""
KAP FINANSAL RAPOR TARIHLERI TOPLAYICI (27.10.2026) - SALT VERI TOPLAMA. H4b testinin girdisi.
Her bilanco sezonu icin (ceyrek sonu +1 .. +90 gun) KAP bildirim sorgusunu GUN GUN calistirir,
konusu "Finansal Rapor" olan bildirimlerin yayin zamanini sembol bazinda kaydeder.
Kaldigi yerden devam eder: islenen gunler dosyada tutulur; her calismada en fazla MAX_GUN gun sorgulanir.
Cikti: data/kap_finansal_rapor_tarihleri.json
  kayitlar: [{sembol, donem "YYYY/PP", yayin_utc, yayin_yerel, disclosureIndex, ozet, gec}]
  Donem atamasi: bildirim, hangi ceyregin sezon penceresine dustuyse o ceyrege atanir; ayni sembol+donem
  icin EN ERKEN bildirim tutulur (sonraki duzeltme/yeniden gonderimler 'sonraki' sayaciyla saklanir).
"""
import os, json, time, urllib.request
from datetime import date, datetime, timedelta, timezone
from collections import Counter

KAP_URL = "https://www.kap.org.tr/tr/api/disclosure/members/byCriteria"
KAP_HEADERS = {"Content-Type": "application/json", "Referer": "https://www.kap.org.tr/tr/bildirim-sorgu",
               "User-Agent": "bist-veri/1.0 (kisisel arastirma amacli)"}
DOSYA = "data/kap_finansal_rapor_tarihleri.json"
KONU_ANAHTAR = "Finansal Rapor"
ILK_DONEM = (2021, 3)
SEZON_GUN = 90
MAX_GUN = int(os.environ.get("MAX_GUN", "450"))
BEKLE = float(os.environ.get("BEKLE_SN", "0.8"))
TR = timedelta(hours=3)


def evren():
    out = []
    for s in open("config/bist100_uyeler.txt", encoding="utf-8"):
        s = s.split("#")[0].strip().upper()
        if s and s not in out:
            out.append(s)
    return out


def donemler(bugun):
    y, p = ILK_DONEM
    while True:
        son = date(y, p, 1)
        son = (son.replace(day=28) + timedelta(days=4))
        son = son - timedelta(days=son.day)
        if son >= bugun:
            return
        yield (y, p), son
        p += 3
        if p > 12:
            y, p = y + 1, 3


def sorgu(gun):
    govde = json.dumps({"fromDate": gun.isoformat(), "toDate": gun.isoformat(),
                        "mkkMemberOidList": [], "subjectList": []}).encode("utf-8")
    req = urllib.request.Request(KAP_URL, data=govde, headers=KAP_HEADERS, method="POST")
    for deneme in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            hata = e
            time.sleep(3 * (deneme + 1))
    raise hata


def main():
    bugun = date.today()
    d = json.load(open(DOSYA, encoding="utf-8")) if os.path.exists(DOSYA) else {"islenen_gunler": [], "kayitlar": [], "konu_sayaci": {}}
    islenen = set(d["islenen_gunler"])
    kayit = {(k["sembol"], k["donem"]): k for k in d["kayitlar"]}
    konu = Counter(d.get("konu_sayaci", {}))
    gun_sayi = dict(d.get("gun_bildirim_sayisi", {}))   # tavan (sayfa siniri) tespiti icin
    ev = evren()
    plan = []
    for (y, p), son in donemler(bugun):
        for i in range(1, SEZON_GUN + 1):
            g = son + timedelta(days=i)
            if g >= bugun:
                break
            if g.weekday() < 5 and g.isoformat() not in islenen:
                plan.append(((y, p), g))
    yapilan, hata = 0, []
    for (y, p), g in plan[:MAX_GUN]:
        try:
            ham = sorgu(g)
        except Exception as e:
            hata.append(f"{g}: {str(e)[:80]}")
            continue
        gun_sayi[g.isoformat()] = len(ham or [])
        for b in ham or []:
            s = b.get("subject") or ""
            konu[s] += 1
            if KONU_ANAHTAR not in s:
                continue
            alan = " ".join(str(b.get(k) or "") for k in ("relatedStocks", "stockCodes"))
            try:
                yerel = datetime.strptime(b.get("publishDate", ""), "%d.%m.%Y %H:%M:%S")
            except ValueError:
                continue
            for sem in ev:
                if sem not in alan.replace(",", " ").split():
                    continue
                a = (sem, f"{y}/{p:02d}")
                yeni = {"sembol": sem, "donem": a[1], "yayin_yerel": yerel.isoformat(),
                        "yayin_utc": (yerel - TR).replace(tzinfo=timezone.utc).isoformat(),
                        "disclosureIndex": b.get("disclosureIndex"), "ozet": b.get("summary"), "gec": bool(b.get("isLate")),
                        "sonraki": 0}
                if a not in kayit:
                    kayit[a] = yeni
                elif yeni["yayin_yerel"] < kayit[a]["yayin_yerel"]:
                    yeni["sonraki"] = kayit[a].get("sonraki", 0) + 1
                    kayit[a] = yeni
                else:
                    kayit[a]["sonraki"] = kayit[a].get("sonraki", 0) + 1
        islenen.add(g.isoformat())
        yapilan += 1
        if yapilan % 25 == 0:
            d.update({"islenen_gunler": sorted(islenen), "kayitlar": list(kayit.values()), "konu_sayaci": dict(konu)})
            json.dump(d, open(DOSYA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        time.sleep(BEKLE)
    kalan = len(plan) - yapilan
    d.update({"islenen_gunler": sorted(islenen), "kayitlar": sorted(kayit.values(), key=lambda k: (k["donem"], k["sembol"])),
              "konu_sayaci": dict(konu.most_common(40)), "guncelleme_utc": datetime.now(timezone.utc).isoformat(),
              "kalan_gun": kalan, "son_hatalar": hata[-20:], "tamamlandi": kalan == 0,
              "gun_bildirim_sayisi": gun_sayi,
              "tavan_suphesi": sorted(g for g, n in gun_sayi.items() if n and n == max(gun_sayi.values()) and list(gun_sayi.values()).count(n) > 2)})
    os.makedirs("data", exist_ok=True)
    json.dump(d, open(DOSYA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    say = Counter(k["donem"] for k in kayit.values())
    print(f"{yapilan} gun sorgulandi, {kalan} gun kaldi, {len(hata)} hata. Donem basina kayit: {dict(sorted(say.items()))}")
    print("En sik konular:", konu.most_common(8))


if __name__ == "__main__":
    main()
