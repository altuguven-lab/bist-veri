"""
KAP FINANSAL RAPOR TARIHLERI TOPLAYICI v2 (29.10.2026) - SALT VERI TOPLAMA. H4b testinin girdisi.

v2 DUZELTMESI (29.10, H4b HIC CALISMADAN once): v1 her bildirimi dustugu "sezon penceresine" gore
ceyrege atiyordu. 2023 yillik raporlari (ilk TMS 29 bilancolari) icin yasal sure uzatildigindan yaklasik
40 sirketin yillik raporu Nisan-Haziran 2024'e dustu ve v1 bunlari 2024/03'un aciklama tarihi sandi
(2024/03'te 'sonraki' sayaci 39; diger donemlerde 16-19). Bu, H4b'de 1. ceyrek rakamlari aciklanmadan
pozisyona girmek, yani ileriye bakma yanliligi demekti.
v2.1 (30.10): KAP bildiriminin kendi 'period' ve 'year' alanlari bulundu; ceyrek atamasi artik dogrudan
bunlarla yapiliyor (pencere kurali yalniz bu alanlar bossa yedek). Konu eslesmesi TAM yapiliyor; "Finansal
Rapor Ek Sure Taleplerine Iliskin SPK Degerlendirmesi" gibi notlar rapor sayilmiyor. Toplanmis veri
korunur (yeniden toplama gerekmez).
v2: (1) her gun SUREKLI sorgulanir (2021-01-01'den bugune), (2) sembol basina TUM "Finansal Rapor"
bildirimleri saklanir, (3) ceyrek atamasi pencere tabanlidir ve yillik raporlarin sure uzatmasini
ayirt eder (ayrinti: ata() aciklamasi). Atanamayan bildirimler 'atanmamis' olarak sayilir.
Kaldigi yerden devam eder; her calismada en fazla MAX_GUN gun sorgulanir.
Cikti: data/kap_finansal_rapor_tarihleri.json
  kayitlar (H4b'nin okudugu): [{sembol, donem "YYYY/PP", yayin_yerel, yayin_utc, disclosureIndex, gec, ayni_ceyrek_ek}]
  bildirimler: {sembol: [[yayin_yerel, disclosureIndex, gec], ...]}  (ham, tumu)
"""
import os, json, time, urllib.request
from datetime import date, datetime, timedelta, timezone
from collections import Counter

KAP_URL = "https://www.kap.org.tr/tr/api/disclosure/members/byCriteria"
KAP_HEADERS = {"Content-Type": "application/json", "Referer": "https://www.kap.org.tr/tr/bildirim-sorgu",
               "User-Agent": "bist-veri/1.0 (kisisel arastirma amacli)"}
DOSYA = "data/kap_finansal_rapor_tarihleri.json"
SURUM = 2
KONU_ANAHTAR = "Finansal Rapor"            # konu TAM olarak bu olmali (30.10)
SORGU_BAS = date(2021, 1, 1)
ATAMA_ILK = (2020, 12)          # 2020 yillik raporu da atanir ki 2021/03'e yanlis dusmesin
ATAMA_AZAMI_GUN = 160
ATAMA_ASGARI_GUN = 15          # ceyrek sonundan 15 gun icinde gelen bildirim o ceyregin raporu sayilmaz
                               # (onceki donemin duzeltmesi/ek raporu olma ihtimali yuksek)
MAX_GUN = int(os.environ.get("MAX_GUN", "450"))
BEKLE = float(os.environ.get("BEKLE_SN", "2.0"))   # 0.8 sn KAP'ta HTTP 429 uretti
ARDISIK_HATA_DUR = 3
TR = timedelta(hours=3)


def evren():
    out = []
    for s in open("config/bist100_uyeler.txt", encoding="utf-8"):
        s = s.split("#")[0].strip().upper()
        if s and s not in out:
            out.append(s)
    return out


def ceyrek_sonu(y, p):
    s = date(y, p, 1).replace(day=28) + timedelta(days=4)
    return s - timedelta(days=s.day)


def ceyrekler(bugun):
    y, p = ATAMA_ILK
    while ceyrek_sonu(y, p) < bugun:
        yield (y, p)
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
            time.sleep((45 if "429" in str(e) else 3) * (deneme + 1))
    raise hata


def kap_donemi(metin):
    """KAP 'Finansal Rapor' bildiriminin kendi alanlari: 'period | year' (or. '3 | 2021' = 3. ceyrek 2021).
    Donus: (yil, ay) ya da None."""
    try:
        parca = [x.strip() for x in str(metin).split("|")]
        per, yil = int(parca[-2]), int(parca[-1])
        if per in (1, 2, 3, 4) and 2000 < yil < 2100:
            return yil, per * 3
    except (ValueError, IndexError):
        pass
    return None


def ata(bildirimler, bugun):
    """Ceyrek atamasi. Donus: (kayitlar, atanmamis_sayisi).
    30.10 v2.1: KAP her finansal rapor bildiriminde donemi (period 1-4) ve yili (year) veriyor. Atama
    BUNA gore yapilir: sembol + (yil, ceyrek) icin en erken bildirim. Sure uzatmalari ve gecikmeler
    otomatik olarak dogru ceyrege duser. Donem alani bos olan bildirimler (gorulmedi) eski pencere
    kuralina (ceyrek sonu +15..+100 gun) gore atanir ve 'pencere' olarak isaretlenir."""
    kayit, atanmamis = {}, 0
    for sem, lst in bildirimler.items():
        donemsiz = []
        for x in sorted(lst):
            yerel, idx, gec = x[0], x[1], x[2]
            metin = x[3] if len(x) > 3 else ""
            dp = kap_donemi(metin)
            if dp is None:
                if "Finansal Rapor" in str(metin):          # v2 ilk calismadan kalan SPK ek sure notlari
                    continue
                donemsiz.append(x)
                continue
            a = (sem, dp)
            if a in kayit:
                kayit[a]["ayni_ceyrek_ek"] += 1
                continue
            ytl = datetime.fromisoformat(yerel)
            kayit[a] = {"sembol": sem, "donem": f"{dp[0]}/{dp[1]:02d}", "yayin_yerel": yerel,
                        "yayin_utc": (ytl - TR).replace(tzinfo=timezone.utc).isoformat(),
                        "disclosureIndex": idx, "gec": gec, "ayni_ceyrek_ek": 0, "atama": "kap_donem"}
        for x in donemsiz:
            gun = date.fromisoformat(x[0][:10])
            bulundu = False
            for (y, p) in ceyrekler(bugun):
                son = ceyrek_sonu(y, p)
                if son + timedelta(days=ATAMA_ASGARI_GUN) < gun <= son + timedelta(days=100):
                    a = (sem, (y, p))
                    if a not in kayit:
                        ytl = datetime.fromisoformat(x[0])
                        kayit[a] = {"sembol": sem, "donem": f"{y}/{p:02d}", "yayin_yerel": x[0],
                                    "yayin_utc": (ytl - TR).replace(tzinfo=timezone.utc).isoformat(),
                                    "disclosureIndex": x[1], "gec": x[2], "ayni_ceyrek_ek": 0, "atama": "pencere"}
                        bulundu = True
                    break
            atanmamis += 0 if bulundu else 1
    return sorted(kayit.values(), key=lambda k: (k["donem"], k["sembol"])), atanmamis


def main():
    bugun = date.today()
    d = json.load(open(DOSYA, encoding="utf-8")) if os.path.exists(DOSYA) else {}
    if d.get("surum") != SURUM:          # v1 dosyasi: bildirimlerin tamami saklanmamisti -> bastan topla
        d = {"surum": SURUM, "islenen_gunler": [], "bildirimler": {}, "konu_sayaci": {},
             "gun_bildirim_sayisi": {}, "not": "v2: v1 verisi donem atama hatasi nedeniyle bastan toplaniyor (29.10.2026)."}
    islenen = set(d["islenen_gunler"])
    bild = {k: [tuple(x) for x in v] for k, v in d.get("bildirimler", {}).items()}
    gorulen = {(k, x[1]) for k, v in bild.items() for x in v}
    konu = Counter(d.get("konu_sayaci", {}))
    gun_sayi = dict(d.get("gun_bildirim_sayisi", {}))
    ev = evren()
    plan, g = [], SORGU_BAS
    while g < bugun:
        if g.weekday() < 5 and g.isoformat() not in islenen:
            plan.append(g)
        g += timedelta(days=1)
    yapilan, hata, ardisik = 0, [], 0

    def kaydet(son=False):
        kayitlar, atanmamis = ata(bild, bugun)
        kalan = len(plan) - yapilan
        d.update({"islenen_gunler": sorted(islenen), "bildirimler": {k: sorted(v) for k, v in bild.items()},
                  "kayitlar": kayitlar, "atanmamis_bildirim": atanmamis, "konu_sayaci": dict(konu.most_common(40)),
                  "gun_bildirim_sayisi": gun_sayi, "guncelleme_utc": datetime.now(timezone.utc).isoformat(),
                  "kalan_gun": kalan, "son_hatalar": hata[-20:], "tamamlandi": kalan == 0,
                  "tavan_suphesi": sorted(x for x, n in gun_sayi.items()
                                          if n and n == max(gun_sayi.values()) and list(gun_sayi.values()).count(n) > 2)})
        os.makedirs("data", exist_ok=True)
        json.dump(d, open(DOSYA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        return kayitlar, kalan

    for g in plan[:MAX_GUN]:
        try:
            ham = sorgu(g)
            ardisik = 0
        except Exception as e:
            hata.append(f"{g}: {str(e)[:80]}")
            ardisik += 1
            if ardisik >= ARDISIK_HATA_DUR:
                hata.append("ust uste hata - calisma durduruldu, sonraki calismada devam edecek")
                break
            continue
        gun_sayi[g.isoformat()] = len(ham or [])
        for b in ham or []:
            s = b.get("subject") or ""
            konu[s] += 1
            if s.strip() != KONU_ANAHTAR:       # 30.10: "Finansal Rapor Ek Sure ... SPK Degerlendirmesi" gibi notlar disarida
                continue
            alan = " ".join(str(b.get(k) or "") for k in ("relatedStocks", "stockCodes")).replace(",", " ").split()
            try:
                yerel = datetime.strptime(b.get("publishDate", ""), "%d.%m.%Y %H:%M:%S").isoformat()
            except ValueError:
                continue
            for sem in ev:
                if sem in alan and (sem, b.get("disclosureIndex")) not in gorulen:
                    metin = " | ".join(str(b.get(k)) for k in ("summary", "period", "year") if b.get(k))
                    bild.setdefault(sem, []).append((yerel, b.get("disclosureIndex"), bool(b.get("isLate")), metin))
                    if "ornek_finansal_rapor" not in d:
                        d["ornek_finansal_rapor"] = b      # alan yapisini gormek icin (donem bilgisi var mi?)
                    gorulen.add((sem, b.get("disclosureIndex")))
        islenen.add(g.isoformat())
        yapilan += 1
        if yapilan % 50 == 0:
            kaydet()
        time.sleep(BEKLE)
    kayitlar, kalan = kaydet(son=True)
    say = Counter(k["donem"] for k in kayitlar)
    print(f"{yapilan} gun sorgulandi, {kalan} gun kaldi, {len(hata)} hata, atanmamis bildirim {d['atanmamis_bildirim']}.")
    print("Donem basina kayit:", dict(sorted(say.items())))


if __name__ == "__main__":
    main()
