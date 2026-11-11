#!/usr/bin/env python3
"""
KESIF - VIOP BULTEN GECMISI (11.11.2026, Asama 2). Tek seferlik, elle tetiklenir. Veri yazmaz, yalniz rapor.
Soru: borsaistanbul.com/viopdata/viop_YYYYMMDD.csv arsivi ne kadar geriye gidiyor, bicim degismis mi?
Yontem: once robots.txt (/viopdata/ yasakliysa HIC istek atilmaz). Sonra 2012-2026 her ceyregin ilk
is gunlerinden ornek (tatil icin 3 gune kadar dener), istekler arasi 1,5 sn. Her ornek icin: HTTP durum,
boyut, kolon sayisi/listesi, satir, TARIH, ve XU030/USDTRY/endeks opsiyonu satirlarinin varligi.
Cikti: data/kesif/kesif_viop_gecmis.json + .md
"""
import csv, datetime as dt, io, json, os, time, urllib.request, urllib.robotparser

BASE = "https://www.borsaistanbul.com"
URL = BASE + "/viopdata/viop_{t}.csv"
UA = "Mozilla/5.0 (bist-veri kesif_viop_gecmis)"
BEKLE = 1.5


def getir(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30)
        return r.status, r.read()
    except Exception as e:
        return getattr(e, "code", type(e).__name__), b""


def incele(ham):
    metin = ham.decode("latin-1")
    ilk = metin.split("\n", 1)[0]
    ayrac = max([";", "\t", ","], key=ilk.count)
    rows = list(csv.reader(io.StringIO(metin, newline=""), delimiter=ayrac))
    h = [x.strip() for x in rows[0]]
    gov = [r for r in rows[1:] if len(r) >= 10 and not r[0].strip().upper().startswith("TRADE")]
    tip = h.index("SOZLESME TIPI") if "SOZLESME TIPI" in h else None
    day = h.index("DAYANAK VARLIK") if "DAYANAK VARLIK" in h else None
    dayanak = {r[day].strip() for r in gov} if day is not None else set()
    tipler = {r[tip].strip() for r in gov} if tip is not None else set()
    return {"ayrac": ayrac, "kolon_sayisi": len(h), "kolonlar": h, "satir": len(gov),
            "ilk_tarih_hucresi": gov[0][0].strip() if gov else None,
            "xu030_vadeli": "D_XU030D" in dayanak and "D_IX_FUT" in tipler,
            "usdtry": any(d.startswith("D_USDTRY") for d in dayanak),
            "endeks_opsiyon": bool({"D_IX_ECO", "D_IX_EPO"} & tipler),
            "acik_pozisyon_kolonu": "ACIK POZISYON" in h}


def main():
    os.makedirs("data/kesif", exist_ok=True)
    rp = urllib.robotparser.RobotFileParser()
    durum, robots = getir(BASE + "/robots.txt")
    rp.parse(robots.decode("latin-1", "ignore").splitlines())
    izin = rp.can_fetch(UA, URL.format(t="20200102"))
    out = {"zaman_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "robots_durum": durum, "robots_viopdata_izinli": izin, "ornekler": []}
    if not izin:
        out["sonuc"] = "robots.txt /viopdata/ yolunu yasakliyor - istek atilmadi, geri doldurma YAPILMAZ."
    else:
        bugun = dt.date.today()
        for yil in range(2012, bugun.year + 1):
            for ay in (1, 4, 7, 10):
                g = dt.date(yil, ay, 5)
                if g > bugun:
                    break
                deneme = 0
                while deneme < 3:
                    if g.weekday() < 5:
                        deneme += 1
                        d, ham = getir(URL.format(t=f"{g:%Y%m%d}"))
                        kayit = {"gun": g.isoformat(), "http": d, "bayt": len(ham)}
                        if d == 200 and len(ham) > 1000:
                            try:
                                kayit.update(incele(ham))
                            except Exception as e:
                                kayit["ayristirma_hatasi"] = f"{type(e).__name__}: {e}"
                            out["ornekler"].append(kayit)
                            print(kayit["gun"], d, len(ham), kayit.get("kolon_sayisi"), kayit.get("satir"))
                            time.sleep(BEKLE)
                            break
                        out["ornekler"].append(kayit)
                        print(kayit["gun"], d, len(ham))
                        time.sleep(BEKLE)
                    g += dt.timedelta(days=1)
        ok = [o for o in out["ornekler"] if o.get("satir")]
        out["en_eski_basarili"] = min((o["gun"] for o in ok), default=None)
        out["kolon_bicimleri"] = sorted({o["kolon_sayisi"] for o in ok})
        out["xu030_ilk"] = min((o["gun"] for o in ok if o.get("xu030_vadeli")), default=None)
        out["usdtry_ilk"] = min((o["gun"] for o in ok if o.get("usdtry")), default=None)
        out["opsiyon_ilk"] = min((o["gun"] for o in ok if o.get("endeks_opsiyon")), default=None)
    json.dump(out, open("data/kesif/kesif_viop_gecmis.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# VİOP bülten geçmişi keşfi", "", f"Zaman {out['zaman_utc']} · robots.txt HTTP {out['robots_durum']} · /viopdata/ izinli: **{out['robots_viopdata_izinli']}**", ""]
    if "sonuc" in out:
        L.append(out["sonuc"])
    else:
        L += [f"En eski başarılı gün: **{out['en_eski_basarili']}** · kolon biçimleri: {out['kolon_bicimleri']} · "
              f"XU030 vadeli ilk: {out['xu030_ilk']} · USD/TRY ilk: {out['usdtry_ilk']} · endeks opsiyon ilk: {out['opsiyon_ilk']}", "",
              "| Gün | HTTP | Bayt | Kolon | Satır | XU030 | USD | Ops |", "|---|---|---|---|---|---|---|---|"]
        for o in out["ornekler"]:
            L.append(f"| {o['gun']} | {o['http']} | {o['bayt']} | {o.get('kolon_sayisi', '')} | {o.get('satir', '')} | "
                     f"{o.get('xu030_vadeli', '')} | {o.get('usdtry', '')} | {o.get('endeks_opsiyon', '')} |")
    open("data/kesif/kesif_viop_gecmis.md", "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
