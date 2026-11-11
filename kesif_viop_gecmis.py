#!/usr/bin/env python3
"""
KESIF - VIOP BULTEN GECMISI (11.11.2026, Asama 2). Tek seferlik, elle tetiklenir. Veri yazmaz, yalniz rapor.
Soru: borsaistanbul.com/viopdata/viop_YYYYMMDD.csv arsivi ne kadar geriye gidiyor, bicim degismis mi?
Yontem: once robots.txt (/viopdata/ yasakliysa HIC istek atilmaz). Sonra bugunden GERIYE her ceyregin
5'inden ornek (tatil icin 3 is gunu), art arda 3 ceyrek bos gelince durur ve siniri ay ay daraltir.
Her istek aninda loglanir, sonuc her ornekten sonra yazilir (iptalde kismi sonuc kalir). 14 dk ic butce. Her ornek icin: HTTP durum,
boyut, kolon sayisi/listesi, satir, TARIH, ve XU030/USDTRY/endeks opsiyonu satirlarinin varligi.
Cikti: data/kesif/kesif_viop_gecmis.json + .md
"""
import csv, datetime as dt, io, json, os, time, urllib.request, urllib.robotparser

BASE = "https://www.borsaistanbul.com"
URL = BASE + "/viopdata/viop_{t}.csv"
UA = "Mozilla/5.0 (bist-veri kesif_viop_gecmis)"
BEKLE = 1.5
ZAMAN_ASIMI = 12


def log(m):
    print(m, flush=True)


def getir(url):
    t = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=ZAMAN_ASIMI)
        return r.status, r.read(), time.time() - t
    except Exception as e:
        return getattr(e, "code", type(e).__name__), b"", time.time() - t


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


ZAMAN_BUTCESI = 14 * 60
BOS_DUR = 3          # art arda bu kadar ceyrek bos -> geri taramayi durdur


def main():
    t0 = time.time()
    os.makedirs("data/kesif", exist_ok=True)
    rp = urllib.robotparser.RobotFileParser()
    durum, robots, sn = getir(BASE + "/robots.txt")
    log(f"robots.txt HTTP {durum}, {len(robots)} bayt, {sn:.1f} sn")
    rp.parse(robots.decode("latin-1", "ignore").splitlines())
    izin = rp.can_fetch(UA, URL.format(t="20200102"))
    out = {"zaman_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "robots_durum": durum, "robots_viopdata_izinli": izin, "ornekler": []}
    if not izin:
        out["sonuc"] = "robots.txt /viopdata/ yolunu yasakliyor - istek atilmadi, geri doldurma YAPILMAZ."
        yaz(out)
        return

    def dene(g0):
        """g0'dan itibaren en cok 3 is gunu dener; basarili kayit veya None."""
        g, deneme = g0, 0
        while deneme < 3:
            if time.time() - t0 > ZAMAN_BUTCESI:
                out["zaman_asimi"] = True
                return None
            if g.weekday() < 5:
                deneme += 1
                d, ham, sn = getir(URL.format(t=f"{g:%Y%m%d}"))
                k = {"gun": g.isoformat(), "http": d, "bayt": len(ham), "sure_sn": round(sn, 1)}
                if d == 200 and len(ham) > 1000:
                    try:
                        k.update(incele(ham))
                    except Exception as e:
                        k["ayristirma_hatasi"] = f"{type(e).__name__}: {e}"
                out["ornekler"].append(k)
                log(f"{k['gun']} HTTP {d} {len(ham)} bayt {sn:.1f} sn kolon {k.get('kolon_sayisi', '-')} satir {k.get('satir', '-')}")
                yaz(out)
                time.sleep(BEKLE)
                if k.get("satir"):
                    return k
            g += dt.timedelta(days=1)
        return None

    # 1) bugunden geriye ceyrek ceyrek
    bugun = dt.date.today()
    y, a = bugun.year, ((bugun.month - 1) // 3) * 3 + 1
    son_basarili, ilk_bos, bos = None, None, 0
    while y >= 2010 and not out.get("zaman_asimi"):
        k = dene(dt.date(y, a, 5))
        if k:
            son_basarili, bos, ilk_bos = dt.date.fromisoformat(k["gun"]), 0, None
        else:
            bos += 1
            ilk_bos = ilk_bos or dt.date(y, a, 5)
            if bos >= BOS_DUR:
                break
        a -= 3
        if a < 1:
            a, y = 10, y - 1
    # 2) sinir: ilk bos ceyrek ile son basarili arasinda ay ay
    if son_basarili and ilk_bos and not out.get("zaman_asimi"):
        g = dt.date(ilk_bos.year, ilk_bos.month, 1)
        while g < son_basarili and not out.get("zaman_asimi"):
            g = (g.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
            if g < son_basarili and dene(g.replace(day=5)):
                break
    ok = [o for o in out["ornekler"] if o.get("satir")]
    out["en_eski_basarili"] = min((o["gun"] for o in ok), default=None)
    out["kolon_bicimleri"] = sorted({o["kolon_sayisi"] for o in ok if o.get("kolon_sayisi")})
    out["xu030_ilk"] = min((o["gun"] for o in ok if o.get("xu030_vadeli")), default=None)
    out["usdtry_ilk"] = min((o["gun"] for o in ok if o.get("usdtry")), default=None)
    out["opsiyon_ilk"] = min((o["gun"] for o in ok if o.get("endeks_opsiyon")), default=None)
    out["toplam_sure_sn"] = round(time.time() - t0)
    yaz(out)
    log(f"bitti: en eski {out['en_eski_basarili']}, {len(out['ornekler'])} istek, {out['toplam_sure_sn']} sn")


def yaz(out):
    json.dump(out, open("data/kesif/kesif_viop_gecmis.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# VİOP bülten geçmişi keşfi", "", f"Zaman {out['zaman_utc']} · robots.txt HTTP {out['robots_durum']} · /viopdata/ izinli: **{out['robots_viopdata_izinli']}**"
         + (" · **ZAMAN AŞIMI (kısmi sonuç)**" if out.get("zaman_asimi") else ""), ""]
    if "sonuc" in out:
        L.append(out["sonuc"])
    else:
        if "en_eski_basarili" in out:
            L += [f"En eski başarılı gün: **{out['en_eski_basarili']}** · kolon biçimleri: {out['kolon_bicimleri']} · XU030 vadeli ilk: {out['xu030_ilk']} · "
                  f"USD/TRY ilk: {out['usdtry_ilk']} · endeks opsiyon ilk: {out['opsiyon_ilk']} · süre {out['toplam_sure_sn']} sn", ""]
        L += ["| Gün | HTTP | Bayt | Süre sn | Kolon | Satır | XU030 | USD | Ops |", "|---|---|---|---|---|---|---|---|---|"]
        for o in out["ornekler"]:
            L.append(f"| {o['gun']} | {o['http']} | {o['bayt']} | {o['sure_sn']} | {o.get('kolon_sayisi', '')} | {o.get('satir', '')} | "
                     f"{o.get('xu030_vadeli', '')} | {o.get('usdtry', '')} | {o.get('endeks_opsiyon', '')} |")
    open("data/kesif/kesif_viop_gecmis.md", "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
