"""
KURUM KUMESI DEDEKTORU (05.11.2026) - SALT VERI ISARETLEME, TAVSIYE DEGILDIR.
Amac: Sirket disi bir kurumun (Takasbank, BIST, MKK, KAP/SPK, emeklilik sirketleri vb.) ayni gun
cok sayida hisse icin yaptigi bildirimleri yakalamak. 04.11.2026'da 25 hisselik Takasbank
"Temerrut Islemi" kumesi (tasfiye fonlarinin 20 paket satisi) brifingde gozden kacti; bu betik onu onler.
Girdi : data/arsiv/kap/YYYY/MM/DD.json.gz (veri_arsivi.py haber kipi), data/endeks_uyelik/donemsel.json
Cikti : data/kurum_kumesi.json, data/kurum_kumesi.md
Kural (ONEMLI): ayni (kurum, konu) icin ayni gun >= 5 farkli hisse VE asagidakilerden biri:
  a) KRITIK konu (temerrut, tedbir, islem yasagi, islem iptali, sira kapatma, toptan, tasfiye, fonlara iliskin),
  b) NADIR: bu (kurum, konu) son 365 gunde gunlerin <= %5'inde kume olusturmus,
  c) BUYUK: kume buyuklugu, ayni (kurum, konu)nun gecmis kume buyuklugunun 95. yuzdeliginin >= 2 kati (gecmis >= 20 kume).
"""
import os, re, json, gzip, glob, datetime, collections
import numpy as np

ESIK_HISSE = 5
NADIR_ORAN = 0.05
BUYUK_KAT = 2.0
GOSTER_GUN = 14
KRITIK = re.compile(r"temerr|tedbir|işlem yasa|islem yasa|işlem iptal|islem iptal|sırası kapat|sirasi kapat|toptan|tasfiye|fonlara ilişkin|fonlara iliskin", re.I)


def kumeler(yol):
    k = collections.defaultdict(set)
    for x in json.load(gzip.open(yol))["bildirimler"]:
        if x.get("stockCodes"):                          # sirketin kendi bildirimi -> kapsam disi
            continue
        for s in (x.get("relatedStocks") or "").replace(" ", "").split(","):
            if s:
                k[(x.get("kapTitle", "").strip(), x.get("subject", "").strip())].add(s)
    return {key: v for key, v in k.items() if len(v) >= ESIK_HISSE}


def bist100():
    try:
        u = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))["uyelik"]
        bugun = datetime.date.today().isoformat()
        return set(u[max(k for k in u if k[:4].isdigit() and k <= bugun)]["XU100"])
    except Exception:
        return set()


def main():
    dosyalar = sorted(glob.glob("data/arsiv/kap/*/*/*.json.gz"))
    tarih = lambda f: f.split("kap/")[1][:10].replace("/", "-")
    son = [f for f in dosyalar if tarih(f) >= (datetime.date.today() - datetime.timedelta(days=GOSTER_GUN)).isoformat()]
    xu = bist100()
    out = []
    for f in son:
        g = tarih(f)
        gecmis = [h for h in dosyalar if (datetime.date.fromisoformat(g) - datetime.timedelta(days=365)).isoformat() <= tarih(h) < g]
        if not gecmis:
            continue
        hist = collections.defaultdict(list)
        for h in gecmis:
            for key, v in kumeler(h).items():
                hist[key].append(len(v))
        for key, v in kumeler(f).items():
            n, h = len(v), hist.get(key, [])
            oran = len(h) / len(gecmis)
            p95 = float(np.percentile(h, 95)) if len(h) >= 20 else None
            neden = []
            if KRITIK.search(key[1]):
                neden.append("KRITIK_KONU")
            if oran <= NADIR_ORAN:
                neden.append(f"NADIR (son 1 yilda gunlerin %{oran * 100:.1f}'inde)")
            if p95 and n >= BUYUK_KAT * p95:
                neden.append(f"BUYUK ({n} hisse, gecmis p95 {p95:.0f})")
            if neden:
                out.append({"tarih": g, "seviye": "ONEMLI", "kurum": key[0], "konu": key[1], "hisse_sayisi": n,
                            "bist100_icinde": len(v & xu), "nedenler": neden, "hisseler": sorted(v)})
    out.sort(key=lambda r: (r["tarih"], r["bist100_icinde"], r["hisse_sayisi"]), reverse=True)
    sonuc = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "pencere_gun": GOSTER_GUN,
             "kural": {"esik_hisse": ESIK_HISSE, "nadir_oran": NADIR_ORAN, "buyuk_kat": BUYUK_KAT},
             "not": "Salt isaretleme; tavsiye degildir. Brifing bu dosyayi okuyarak baslar.", "kumeler": out}
    os.makedirs("data", exist_ok=True)
    json.dump(sonuc, open("data/kurum_kumesi.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# Kurum kumesi dedektoru", "", f"Uretim {sonuc['uretim_utc'][:16]} UTC, son {GOSTER_GUN} gun. Salt isaretleme; tavsiye degildir.", "",
         "| Tarih | Kurum | Konu | Hisse | BIST100 | Neden | Ornek hisseler |", "|---|---|---|---|---|---|---|"]
    for r in out:
        L.append(f"| {r['tarih']} | {r['kurum'][:40]} | {r['konu'][:50]} | {r['hisse_sayisi']} | {r['bist100_icinde']} | {'; '.join(r['nedenler'])} | {', '.join(r['hisseler'][:8])} |")
    open("data/kurum_kumesi.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
