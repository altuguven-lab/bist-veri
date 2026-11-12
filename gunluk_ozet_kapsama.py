#!/usr/bin/env python3
"""
GUNLUK OZET KAPSAMA DENETIMI (11.11.2026, Denetim 1.3) - SALT IZLEME, TAVSIYE DEGILDIR.
Soru: Bugun evrendeki her hisse icin GUNLUK_OZET alarmi geldi mi ve hepsi ayni Pine surumunde mi?
Neden: 05.11 (25/32), 06.11 (2/32), 09.11 (23/32) eksikleri hicbir otomatik uyari uretmedi; GUNLUK_OZET
  o gunun "alarm hatti calisiyor" kanitidir ve karnenin butunluk olcusudur.
Girdi : config/universe.yml (beklenen hisseler), data/tv_alerts_latest.json, data/inbox/ (yedek kutu)
Cikti : data/gunluk_ozet_kapsama.json (gun gun kayit, brifing bunu okur)
Eksik hisse ya da surum disi alarm varsa GitHub Issue acar (etiket: saglik). Ayni gun ayni baslik tekrar acilmaz.
18:20 TR'den once, hafta sonu ya da tatilde calisirsa SON TAMAMLANMIS islem gununu denetler (gec kalan tetikler icin).
tv_alerts_latest.json kayan pencere oldugundan (son ~280 kayit) denetim en gec ertesi sabah yapilmalidir.
"""
import collections, datetime as dt, glob, json, os, sys, urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "altuguven-lab/bist-veri")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
CIKTI = "data/gunluk_ozet_kapsama.json"
TR = dt.timezone(dt.timedelta(hours=3))
EN_ERKEN = dt.time(18, 20)        # GUNLUK_OZET 18:11-18:13 TR'de gelir
SAKLA_GUN = 250


def evren():
    out = []
    bolum = None
    for l in open("config/universe.yml", encoding="utf-8"):
        if l and not l[0].isspace() and l.strip().endswith(":"):
            bolum = l.strip()[:-1]
        elif bolum == "symbols" and l.strip().startswith("- "):
            out.append(l.strip()[2:].split("#")[0].strip())
    return out


def tatil_mi(gun):
    try:
        from piyasa_takvimi import tatil_gunleri_yukle
        return gun in set(tatil_gunleri_yukle())
    except Exception:
        return False


def tr_gun(zaman_utc):
    return dt.datetime.fromisoformat(str(zaman_utc).replace("Z", "+00:00")).astimezone(TR).date()


def issue_ac(baslik, govde):
    if not TOKEN:
        print("(token yok, issue acilmadi)", baslik)
        return
    def api(yol, veri=None):
        req = urllib.request.Request("https://api.github.com" + yol, method="POST" if veri else "GET",
                                     data=json.dumps(veri).encode() if veri else None,
                                     headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
                                              "Content-Type": "application/json", "User-Agent": "gunluk-ozet-kapsama"})
        return json.load(urllib.request.urlopen(req, timeout=30))
    try:
        acik = api(f"/repos/{REPO}/issues?state=open&labels=saglik&per_page=50")
        if any(i.get("title") == baslik for i in acik):
            print("Atlandi (ayni baslik acik):", baslik)
            return
        api(f"/repos/{REPO}/issues", {"title": baslik, "body": govde, "labels": ["saglik"]})
        print("ISSUE ACILDI:", baslik)
    except Exception as e:
        print("ISSUE ACILAMADI:", baslik, e)


def main():
    simdi = dt.datetime.now(TR)
    gun = simdi.date()
    # 12.11 DUZELTME: GitHub 18:30 tetigini saatlerce geciktirebiliyor (11.11'de 02:06'da calisti ve yeni gunu
    # "ERKEN 0/32" diye yazdi). 18:20'den once calisiyorsak ya da bugun islem gunu degilse, denetlenen gun
    # SON TAMAMLANMIS ISLEM GUNUDUR. Boylece gec kalan kosum da dogru gunu degerlendirir.
    if simdi.time() < EN_ERKEN or gun.weekday() >= 5 or tatil_mi(gun):
        gun -= dt.timedelta(days=1)
        while gun.weekday() >= 5 or tatil_mi(gun):
            gun -= dt.timedelta(days=1)
    onceki = (json.load(open(CIKTI, encoding="utf-8")) if os.path.exists(CIKTI) else {"gunler": {}})["gunler"].get(gun.isoformat())
    if onceki and onceki.get("durum") == "TAM":
        print(f"{gun}: zaten TAM kayitli, tekrar denetlenmedi")
        return 0
    beklenen = evren()
    kayitlar = [x for x in json.load(open("data/tv_alerts_latest.json", encoding="utf-8")).get("sinyal_gecmisi", [])
                if x.get("zaman_utc") and tr_gun(x["zaman_utc"]) == gun]
    inbox = []
    for p in glob.glob(f"data/inbox/{gun.isoformat()}T*.json") + glob.glob(f"data/inbox/{(gun - dt.timedelta(days=1)).isoformat()}T2*.json"):
        try:
            j = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        for x in (j.get("sinyaller") or [j]):
            if x.get("zaman_utc") and tr_gun(x["zaman_utc"]) == gun:
                inbox.append(x)
    go = {x["sembol"] for x in kayitlar if x.get("sinyal") == "GUNLUK_OZET"}
    go_inbox = {x["sembol"] for x in inbox if x.get("sinyal") == "GUNLUK_OZET"} - go
    eksik = [s for s in beklenen if s not in go and s not in go_inbox]
    # surum: her hissenin bugunku EN SON kaydinin surumu; cogunluk surumunden farkli olanlar "surum disi"
    son_surum = {}
    for x in sorted(kayitlar + inbox, key=lambda x: x["zaman_utc"]):
        son_surum[x["sembol"]] = x.get("schemaVersion", "?")
    sayim = collections.Counter(son_surum.values())
    ana = sayim.most_common(1)[0][0] if sayim else None
    surum_disi = {s: v for s, v in sorted(son_surum.items()) if v != ana}
    durum = "TAM" if not eksik and not surum_disi else "EKSIK"
    kayit = {"gun": gun.isoformat(), "denetim_tr": simdi.strftime("%d.%m %H:%M"), "durum": durum, "beklenen": len(beklenen),
             "gelen": len(go & set(beklenen)), "yalniz_inbox": sorted(go_inbox), "eksik": eksik,
             "evren_disi_gelen": sorted(go - set(beklenen)), "ana_surum": ana, "surumler": dict(sayim), "surum_disi": surum_disi,
             "gunluk_ozet_disi_kayit": sum(1 for x in kayitlar if x.get("sinyal") != "GUNLUK_OZET")}
    d = json.load(open(CIKTI, encoding="utf-8")) if os.path.exists(CIKTI) else {"gunler": {}}
    d["not"] = "GUNLUK_OZET kapsamasi ve Pine surum birligi; gunde bir satir. Salt izleme."
    d["gunler"][gun.isoformat()] = kayit
    d["gunler"] = {g: k for g, k in d["gunler"].items() if k.get("durum") != "ERKEN"}      # eski surumun bos kayitlari
    d["gunler"] = dict(sorted(d["gunler"].items())[-SAKLA_GUN:])
    json.dump(d, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(kayit, ensure_ascii=False))
    if durum == "EKSIK":
        govde = (f"Denetim {gun} {simdi:%H:%M} TR\n\n"
                 f"- GUNLUK_OZET gelen: {kayit['gelen']}/{len(beklenen)}\n"
                 f"- Eksik hisseler: {', '.join(eksik) or '-'}\n"
                 f"- Yalniz yedek kutuda (inbox) olanlar: {', '.join(sorted(go_inbox)) or '-'}\n"
                 f"- Ana surum: {ana}; surum disi: {surum_disi or '-'}\n\n"
                 "Olasi nedenler: TradingView alarmi durmus/silinmis, webhook kutusu isaretsiz, alarm eski kodla kurulu, "
                 "Pipedream zaman asimi, yarim islem gunu. Kontrol: TradingView alarm listesi ve alarm gunlugu.\n"
                 "Kayit: data/gunluk_ozet_kapsama.json")
        issue_ac(f"KAPSAMA: GUNLUK_OZET {kayit['gelen']}/{len(beklenen)} - {gun:%d.%m.%Y}", govde)
    return 0


if __name__ == "__main__":
    sys.exit(main())
