"""
SINYAL DOGRULAMA ARSIVI - GUNLUK (08.08.2026) - Faz V0
v2 (17.08.2026): PIYASA REFERANSI + GUN-AGIRLIKLI OZET

tv_alerts_latest.json yalniz ~4 gun tutuyor - bu script HER GUN, o
gunku YENI sinyalleri KALICI bir arsive (data/sinyal_arsiv.json) ekler,
ve YETERLI zaman gecmis (T+3) ESKI sinyaller icin GERCEK fiyat
hareketiyle dogrulama yapar.

KIRMIZI CIZGI: Pine'a hic dokunmuyor, hicbir gercek islem/uyari
uretmiyor - SALT OLCUM, gunluk calisan bir arastirma gunlugu.

--- v2 GEREKCESI (17.08 kurul degerlendirmesi) ---------------------
v1 iki yapisal olcum hatasi tasiyordu:

(A) MUTLAK GETIRI. Bir AL sinyalinin degeri "fiyat yukseldi mi"
    degil, "ayni gun hicbir sey yapmamaya gore ne kazandirdi"dir.
    Dusen piyasada her AL sinyali kotu, yukselen piyasada her AL
    sinyali iyi gorunuyordu. v2 her sinyal icin AYNI pencerede
    piyasa endeksinin getirisini de olcer ve FARKI yazar.

(B) SAHTE ORNEKLEM. Ayni gunun sinyalleri ayni piyasa gununu
    yasar - bagimsiz gozlem degillerdir. 04-11.08 verisinde
    varyansin buyuk kismi GUNLER arasiydi (gun ortalamalarinin
    std'si %2.04, tum sinyallerin std'si %3.92). Sinyal basina
    agirliklandirma "08.08 sonrasi kotulesti" derken, gun basina
    agirliklandirma sonucu TERSINE ceviriyordu. v2 iki okumayi da
    yan yana yazar; hangisine bakilacagini okuyan bilir.

Ayrica: sinyal kaydina varsa `skor` alani da islenir. P3_SKOR_AL
alarm mesaji duzeltilince (17.08 yama sartnamesi) "yuksek skorlu
sinyaller daha mi iyi" sorusu - esik tartismasinin TEK anlamli
testi - bu alan sayesinde sorulabilir hale gelir.

GERIYE DONUK: v1 doneminde dogrulanmis kayitlarda piyasa alanlari
yoktur; v2 bunlari ilk kosuda TAMAMLAR (endeks serisi tek indirme).
Mevcut alanlarin hicbiri degistirilmez veya silinmez.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, statistics, sys
import yfinance as yf

GIRIS_YOL = "data/tv_alerts_latest.json"
ARSIV_YOL = "data/sinyal_arsiv.json"

AL_SINYALLERI = {"P3_SKOR_AL", "P2_DIP_DONUS", "P1_AL", "P1_KALITELI_AL", "P2_ERKEN_AL"}
RISK_OFF_SINYALLERI = {"POZ_AZALT", "STOP_KIRILDI", "ACIL_CIK"}
TAKIP_GUNLERI = [1, 2, 3]
DOGRULAMA_ICIN_GEREKEN_GUN = 3  # T+3 gecmeden dogrulama YAPILMAZ

# Piyasa referansi. Sirayla denenir, ilk dolu donen kullanilir.
# BULUNAMAZSA: goreli alanlar YAZILMAZ - yerine vekil UYDURULMAZ.
# (Sinyal sembollerinin ortalamasi vekil OLAMAZ: onlar zaten secilmis
#  ornekler, yani referans degil olculen seyin kendisi.)
PIYASA_ENDEKSLERI = ["XU100.IS", "XU030.IS"]

ALAN_ACIKLAMALARI = {
    "dogrulama_durumu": "OLCUM tamamlandi mi (DOGRULANDI/BEKLIYOR) - "
                        "sinyalin HAKLI cikip cikmadigi DEGIL. Yon isabeti "
                        "tip_ozet.*.dogrulanan_pct alanindadir.",
    "getiri_tN_pct": "Sinyal fiyatindan T+N kapanisina MUTLAK getiri.",
    "piyasa_tN_pct": "AYNI pencerede piyasa endeksinin getirisi.",
    "getiri_rel_tN_pct": "getiri_tN_pct - piyasa_tN_pct. ASIL BAKILACAK ALAN.",
    "gun_ozet": "Gun-agirlikli okuma: ayni gunun sinyalleri once kendi "
                "aralarinda ortalanir, sonra gunler ortalanir. n = GUN sayisi.",
}


def _oku_arsiv():
    try:
        with open(ARSIV_YOL, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"kayitlar": [], "tip_ozet": {}}


def _seri_cek(ticker, donem="2mo"):
    try:
        df = yf.Ticker(ticker).history(period=donem, interval="1d")
        return [(idx.date(), float(v)) for idx, v in df["Close"].items()]
    except Exception as e:
        print(f"UYARI: {ticker} veri cekilemedi -> {e}", file=sys.stderr)
        return []


def _en_yakin_kapanis(seri, hedef_tarih, sonraki_mi=True):
    if sonraki_mi:
        adaylar = [(t, c) for t, c in seri if t >= hedef_tarih]
        return min(adaylar, key=lambda x: x[0])[1] if adaylar else None
    adaylar = [(t, c) for t, c in seri if t <= hedef_tarih]
    return max(adaylar, key=lambda x: x[0])[1] if adaylar else None


def _piyasa_serisi_al():
    """Ilk dolu donen endeksi kullanir. Hicbiri gelmezse (None, []) doner
    ve goreli olcum o kosuda YAPILMAZ - sessizce vekil kullanilmaz."""
    for tic in PIYASA_ENDEKSLERI:
        seri = _seri_cek(tic)
        if seri:
            print(f"Piyasa referansi: {tic} ({len(seri)} gun)")
            return tic, seri
    print("UYARI: piyasa endeksi cekilemedi - goreli alanlar bu kosuda "
          "YAZILMAYACAK (mutlak olcum devam eder)", file=sys.stderr)
    return None, []


def _piyasa_getirisi(piyasa_seri, sinyal_tarih, gun):
    """Sinyal gunu kapanisindan T+gun kapanisina endeks getirisi."""
    baz = _en_yakin_kapanis(piyasa_seri, sinyal_tarih, sonraki_mi=False)
    hedef = _en_yakin_kapanis(piyasa_seri, sinyal_tarih + datetime.timedelta(days=gun),
                              sonraki_mi=True)
    if baz and hedef and baz > 0:
        return round((hedef / baz - 1) * 100, 3)
    return None


def _goreli_yaz(kayit, piyasa_seri):
    """Kayda piyasa ve goreli getiri alanlarini ekler. Zaten varsa
    dokunmaz. Eksik mutlak getiri varsa o gun atlanir."""
    if not piyasa_seri:
        return False
    sinyal_tarih = datetime.date.fromisoformat(kayit["tarih"])
    yazildi = False
    for gun in TAKIP_GUNLERI:
        mutlak = kayit.get(f"getiri_t{gun}_pct")
        if mutlak is None or f"getiri_rel_t{gun}_pct" in kayit:
            continue
        piyasa = _piyasa_getirisi(piyasa_seri, sinyal_tarih, gun)
        if piyasa is None:
            continue
        kayit[f"piyasa_t{gun}_pct"] = piyasa
        kayit[f"getiri_rel_t{gun}_pct"] = round(mutlak - piyasa, 3)
        yazildi = True
    return yazildi


def _sayi_mi(deger):
    try:
        float(deger)
        return True
    except (TypeError, ValueError):
        return False


def _ozet_hesapla(alt, alan_kalibi, tip):
    """Bir sinyal tipi icin hem sinyal-agirlikli hem GUN-agirlikli
    ozet uretir. alan_kalibi: 'getiri_t{}_pct' ya da 'getiri_rel_t{}_pct'."""
    sonuc = {}
    for gun in TAKIP_GUNLERI:
        alan = alan_kalibi.format(gun)
        degerler = [(k["tarih"], k[alan]) for k in alt if alan in k]
        if not degerler:
            continue
        ham = [d for _, d in degerler]

        # Gun-agirlikli: once gun ici ortalama, sonra gunler arasi
        gunluk = {}
        for tarih, d in degerler:
            gunluk.setdefault(tarih, []).append(d)
        gun_ortalamalari = [statistics.mean(v) for v in gunluk.values()]

        if tip in AL_SINYALLERI:
            dogrulanan = sum(1 for d in ham if d > 0)
        else:
            dogrulanan = sum(1 for d in ham if d <= 0)

        sonuc[f"t{gun}"] = {
            "n": len(ham),
            "ort_getiri_pct": round(statistics.mean(ham), 3),
            "dogrulanan_pct": round(100 * dogrulanan / len(ham), 1),
            "gun_ozet": {
                "n_gun": len(gun_ortalamalari),
                "gun_ort_pct": round(statistics.mean(gun_ortalamalari), 3),
                "gun_std_pct": round(statistics.pstdev(gun_ortalamalari), 3)
                if len(gun_ortalamalari) > 1 else None,
            },
        }
    return sonuc


def main():
    arsiv = _oku_arsiv()
    mevcut_anahtarlar = {(k["sembol"], k["sinyal"], k["tarih"]) for k in arsiv["kayitlar"]}

    veri = json.load(open(GIRIS_YOL, encoding="utf-8"))
    yeni_sayisi = 0
    for s in veri["sinyal_gecmisi"]:
        if s["sinyal"] not in (AL_SINYALLERI | RISK_OFF_SINYALLERI):
            continue
        sinyal_tarih = datetime.datetime.fromisoformat(
            s["zaman_utc"].replace("Z", "+00:00")).date()
        anahtar = (s["sembol"], s["sinyal"], str(sinyal_tarih))
        if anahtar in mevcut_anahtarlar:
            continue
        kayit = {
            "sembol": s["sembol"], "sinyal": s["sinyal"], "tarih": str(sinyal_tarih),
            "sinyal_fiyat": float(s["fiyat"]),
            "yon_beklentisi": "YUKARI" if s["sinyal"] in AL_SINYALLERI else "ASAGI_VEYA_NOTR",
            "dogrulama_durumu": "BEKLIYOR",
        }
        # v2: alarm mesajinda skor/kgs/rejim varsa sakla - esik testinin
        # girdisi budur. P3_SKOR_AL'de su an "?" geliyor (17.08 bulgusu);
        # mesaj sablonu duzeltilince kendiliginden dolmaya baslar.
        for alan in ("skor", "kgs", "rejim"):
            if _sayi_mi(s.get(alan)):
                kayit[alan] = float(s[alan])
        arsiv["kayitlar"].append(kayit)
        mevcut_anahtarlar.add(anahtar)
        yeni_sayisi += 1
    print(f"{yeni_sayisi} yeni sinyal arsive eklendi")

    piyasa_ticker, piyasa_seri = _piyasa_serisi_al()

    bugun = datetime.datetime.now(datetime.timezone.utc).date()
    fiyat_serileri = {}
    dogrulanan_sayisi = 0
    for kayit in arsiv["kayitlar"]:
        if kayit["dogrulama_durumu"] != "BEKLIYOR":
            continue
        sinyal_tarih = datetime.date.fromisoformat(kayit["tarih"])
        if (bugun - sinyal_tarih).days < DOGRULAMA_ICIN_GEREKEN_GUN:
            continue  # henuz T+3 gecmedi

        sembol = kayit["sembol"]
        if sembol not in fiyat_serileri:
            fiyat_serileri[sembol] = _seri_cek(f"{sembol}.IS")
        seri = fiyat_serileri[sembol]
        if not seri:
            continue

        for gun in TAKIP_GUNLERI:
            hedef = sinyal_tarih + datetime.timedelta(days=gun)
            t_fiyat = _en_yakin_kapanis(seri, hedef, sonraki_mi=True)
            if t_fiyat and kayit["sinyal_fiyat"] > 0:
                kayit[f"getiri_t{gun}_pct"] = round((t_fiyat / kayit["sinyal_fiyat"] - 1) * 100, 3)
        _goreli_yaz(kayit, piyasa_seri)
        if all(f"getiri_t{g}_pct" in kayit for g in TAKIP_GUNLERI):
            kayit["dogrulama_durumu"] = "DOGRULANDI"
            dogrulanan_sayisi += 1
    print(f"{dogrulanan_sayisi} sinyal bu kosumda dogrulandi (T+3 gecmis)")

    # v2 GERIYE DONUK TAMAMLAMA: v1 doneminde dogrulanmis kayitlarda
    # piyasa alanlari yok - endeks serisi zaten elde, tamamlanir.
    tamamlanan = sum(1 for k in arsiv["kayitlar"]
                     if k["dogrulama_durumu"] == "DOGRULANDI"
                     and _goreli_yaz(k, piyasa_seri))
    if tamamlanan:
        print(f"{tamamlanan} eski kayda piyasa referansi geriye donuk eklendi")

    tip_ozet, tip_ozet_rel = {}, {}
    for tip in (AL_SINYALLERI | RISK_OFF_SINYALLERI):
        alt = [k for k in arsiv["kayitlar"]
               if k["sinyal"] == tip and k["dogrulama_durumu"] == "DOGRULANDI"]
        if not alt:
            continue
        mutlak = _ozet_hesapla(alt, "getiri_t{}_pct", tip)
        if mutlak:
            tip_ozet[tip] = mutlak
        goreli = _ozet_hesapla(alt, "getiri_rel_t{}_pct", tip)
        if goreli:
            tip_ozet_rel[tip] = goreli

    arsiv["tip_ozet"] = tip_ozet
    arsiv["tip_ozet_goreli"] = tip_ozet_rel
    arsiv["piyasa_referansi"] = piyasa_ticker or "YOK"
    arsiv["_alan_aciklamalari"] = ALAN_ACIKLAMALARI
    arsiv["son_guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    arsiv["toplam_kayit"] = len(arsiv["kayitlar"])
    arsiv["dogrulanmis_kayit"] = sum(1 for k in arsiv["kayitlar"]
                                     if k["dogrulama_durumu"] == "DOGRULANDI")
    atomik_json_yaz(ARSIV_YOL, arsiv)

    print(f"\nArsiv: {arsiv['toplam_kayit']} toplam, "
          f"{arsiv['dogrulanmis_kayit']} dogrulanmis | "
          f"piyasa referansi: {arsiv['piyasa_referansi']}")
    print(f"{'TIP':16}{'n':>4}{'gun':>5}  {'MUTLAK T+1':>12}  {'GORELI T+1':>12}")
    for tip in sorted(set(tip_ozet) | set(tip_ozet_rel)):
        m = tip_ozet.get(tip, {}).get("t1")
        g = tip_ozet_rel.get(tip, {}).get("t1")
        if not m:
            continue
        gs = f"%{g['gun_ozet']['gun_ort_pct']:+.2f}" if g else "-"
        print(f"{tip:16}{m['n']:4}{m['gun_ozet']['n_gun']:5}  "
              f"%{m['gun_ozet']['gun_ort_pct']:+11.2f}  {gs:>12}")
    print("\nNOT: tablodaki degerler GUN-agirliklidir (ayni gunun sinyalleri "
          "bagimsiz gozlem degildir). Sinyal-agirlikli degerler dosyadaki "
          "ort_getiri_pct alanindadir.")


if __name__ == "__main__":
    main()
