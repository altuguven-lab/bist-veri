"""
SINYAL DOGRULAMA ARSIVI - GUNLUK (08.08.2026) - Faz V0
v2 (17.08.2026): PIYASA REFERANSI + GUN-AGIRLIKLI OZET
v2.1 (17.08.2026): ISLEM GUNU PENCERESI + TUM ARSIVIN YENIDEN DOGRULANMASI

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

(C) TAKVIM GUNU PENCERESI (v2.1 duzeltmesi). v1/v2 T+N'i TAKVIM
    gunu sayiyordu. Cuma gelen bir sinyalde T+1 Cumartesi'ye,
    T+2 Pazar'a, T+3 Pazartesi'ye dusuyor; ucunun de "ilk sonraki
    seans"i AYNI Pazartesi kapanisi oluyordu. Dogrulanmis 53 kaydin
    10'u (%19, hepsi Cuma sinyali) bu durumdaydi: T+1=T+2=T+3, yani
    Cuma sinyalleri icin T+3 diye bir olcum fiilen YOKTU ve kayitlar
    sahte bir istikrar gosteriyordu. M1/M2 hukum metrikleri T+3
    uzerinden tanimli oldugu icin bu, hukmun beste birini yanlis
    pencereden okuyordu.
    v2.1 T+N'i SERIDEKI BAR sayarak bulur (islem gunu). Kurul karari
    (17.08): duzeltme geriye donuk uygulanir, TUM arsiv yeniden
    dogrulanir - arsiv kendi icinde tutarli olur, 08.08 oncesi
    raporlarla sayilar TUTMAZ (kulucka zaten 08.08'de sifirlandi,
    eski raporlarla uyumun degeri dusuk goruldu).

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

# 26.08.2026 EKLENDI - ON KAYIT (C.5): erken uyari sinyalleri artik
# arsivleniyor. Bunlar dogrudan AL/RISK_OFF degil - "yaklasiyor" uyarisi.
# ONCEDEN sonuca bakilmadan iki soru + yontem KILITLENIYOR:
#   (1) DONUSUM: N islem gunu icinde ayni sembol icin gercek bir
#       AL_SINYALLERI kaydi geliyor mu? DONUSUM_PENCERE_GUN=5 (sabit,
#       kurul karari 26.08, sonradan degistirilmez).
#   (2) KENDI BASINA ONGORU: donusum olmasa bile, radar'in kendisi
#       fiyat hareketini haber veriyor mu? (ayni forward-return
#       mekanizmasi AL_SINYALLERI ile PAYLASILIR, ayri kod yazilmadi.)
IZLEME_SINYALLERI = {"P3_RADAR", "P2_ADAY"}
DONUSUM_PENCERE_GUN = 5

# Piyasa referansi. Sirayla denenir, ilk dolu donen kullanilir.
# BULUNAMAZSA: goreli alanlar YAZILMAZ - yerine vekil UYDURULMAZ.
# (Sinyal sembollerinin ortalamasi vekil OLAMAZ: onlar zaten secilmis
#  ornekler, yani referans degil olculen seyin kendisi.)
PIYASA_ENDEKSLERI = ["XU100.IS", "XU030.IS"]

# Olcum surumu. Kaydin `olcum_surumu` alani bundan kucukse (ya da
# yoksa) kayit YENIDEN hesaplanir. Olcum mantigi her degistiginde
# bu sayi artar ve arsiv kendini bir sonraki kosuda tasir.
OLCUM_SURUMU = 2

ALAN_ACIKLAMALARI = {
    "dogrulama_durumu": "OLCUM tamamlandi mi (DOGRULANDI/BEKLIYOR) - "
                        "sinyalin HAKLI cikip cikmadigi DEGIL. Yon isabeti "
                        "tip_ozet.*.dogrulanan_pct alanindadir.",
    "getiri_tN_pct": "Sinyal fiyatindan T+N kapanisina MUTLAK getiri.",
    "piyasa_tN_pct": "AYNI pencerede piyasa endeksinin getirisi.",
    "getiri_rel_tN_pct": "getiri_tN_pct - piyasa_tN_pct. ASIL BAKILACAK ALAN.",
    "gun_ozet": "Gun-agirlikli okuma: ayni gunun sinyalleri once kendi "
                "aralarinda ortalanir, sonra gunler ortalanir. n = GUN sayisi.",
    "olcum_surumu": "Kaydi ureten olcum mantiginin surumu. 2 = islem gunu "
                    "penceresi (v2.1). Surum atlayinca kayit yeniden hesaplanir.",
    "kategori": "IZLEME ise erken uyari sinyali (P3_RADAR/P2_ADAY) - "
               "dogrudan AL/RISK_OFF degil. Yoksa AL_SINYALLERI/"
               "RISK_OFF_SINYALLERI turunden.",
    "donusum_durumu": "Yalniz IZLEME kayitlarinda: DONUSTU/DONUSMEDI/BEKLIYOR. "
                      f"Pencere {DONUSUM_PENCERE_GUN} islem gunu (C.5 on kayit, "
                      "26.08, degistirilmez).",
    "donusum_gun": "DONUSTU ise, kac islem gunu sonra gercek sinyale donustu.",
    "donusturen_sinyal": "DONUSTU ise, hangi AL_SINYALLERI turune donustu.",
}


def _oku_arsiv():
    try:
        with open(ARSIV_YOL, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"kayitlar": [], "tip_ozet": {}}


def _donem_sec(en_eski_tarih):
    """Arsivin en eski kaydini kapsayacak en kisa yfinance donemi.
    Yeniden dogrulama TUM arsivi tarar - sabit '2mo' arsiv buyudukce
    eski kayitlari sessizce olcusuz birakirdi."""
    if en_eski_tarih is None:
        return "3mo"
    gun = (datetime.date.today() - en_eski_tarih).days + 10  # pay
    for sinir, donem in ((60, "3mo"), (150, "6mo"), (330, "1y"),
                         (700, "2y"), (1800, "5y")):
        if gun <= sinir:
            return donem
    return "max"


def _seri_cek(ticker, donem="3mo"):
    try:
        df = yf.Ticker(ticker).history(period=donem, interval="1d")
        seri = [(idx.date(), float(v)) for idx, v in df["Close"].items()]
        return sorted(seri, key=lambda x: x[0])
    except Exception as e:
        print(f"UYARI: {ticker} veri cekilemedi -> {e}", file=sys.stderr)
        return []


def _baz_indeks(seri, sinyal_tarih):
    """Sinyal gununun (yoksa ondan onceki en yakin seansin) bar indeksi.
    T+N bu indeksten ILERI SAYILARAK bulunur - takvim gunu degil."""
    adaylar = [i for i, (t, _) in enumerate(seri) if t <= sinyal_tarih]
    return max(adaylar) if adaylar else None


def _t_plus_kapanis(seri, sinyal_tarih, n):
    """Sinyal barindan N ISLEM GUNU sonraki kapanis. Seri o kadar
    ilerlemediyse None - kayit BEKLIYOR'da kalir."""
    i = _baz_indeks(seri, sinyal_tarih)
    if i is None or i + n >= len(seri):
        return None
    return seri[i + n][1]


def _baz_kapanis(seri, sinyal_tarih):
    i = _baz_indeks(seri, sinyal_tarih)
    return seri[i][1] if i is not None else None


def _piyasa_serisi_al(donem="3mo"):
    """Ilk dolu donen endeksi kullanir. Hicbiri gelmezse (None, []) doner
    ve goreli olcum o kosuda YAPILMAZ - sessizce vekil kullanilmaz."""
    for tic in PIYASA_ENDEKSLERI:
        seri = _seri_cek(tic, donem)
        if seri:
            print(f"Piyasa referansi: {tic} ({len(seri)} gun)")
            return tic, seri
    print("UYARI: piyasa endeksi cekilemedi - goreli alanlar bu kosuda "
          "YAZILMAYACAK (mutlak olcum devam eder)", file=sys.stderr)
    return None, []


def _piyasa_getirisi(piyasa_seri, sinyal_tarih, gun):
    """Sinyal gunu kapanisindan T+gun (ISLEM GUNU) kapanisina endeks
    getirisi."""
    baz = _baz_kapanis(piyasa_seri, sinyal_tarih)
    hedef = _t_plus_kapanis(piyasa_seri, sinyal_tarih, gun)
    if baz and hedef and baz > 0:
        return round((hedef / baz - 1) * 100, 3)
    return None


def _goreli_yaz(kayit, piyasa_seri, uzerine_yaz=False):
    """Kayda piyasa ve goreli getiri alanlarini ekler. uzerine_yaz=False
    ise mevcut degere dokunmaz (gunluk kosum); True ise yeniden hesaplar
    (surum tasima). Eksik mutlak getiri varsa o gun atlanir."""
    if not piyasa_seri:
        return False
    sinyal_tarih = datetime.date.fromisoformat(kayit["tarih"])
    yazildi = False
    for gun in TAKIP_GUNLERI:
        mutlak = kayit.get(f"getiri_t{gun}_pct")
        if mutlak is None:
            continue
        if f"getiri_rel_t{gun}_pct" in kayit and not uzerine_yaz:
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


def _donusum_kontrol(radar_kayit, tum_kayitlar, seri):
    """radar_kayit (P3_RADAR/P2_ADAY) DONUSUM_PENCERE_GUN islem gunu
    icinde AYNI sembol icin bir AL_SINYALLERI kaydina DONUSTU mu?
    seri: sembolun fiyat serisi (bar indeksi icin - takvim gunu DEGIL).
    Donen: dict (donustu/donusmedi/henuz belirsiz) ya da None (seri yok)."""
    if not seri:
        return None
    radar_tarih = datetime.date.fromisoformat(radar_kayit["tarih"])
    radar_idx = _baz_indeks(seri, radar_tarih)
    if radar_idx is None:
        return None

    for k in tum_kayitlar:
        if k is radar_kayit or k["sembol"] != radar_kayit["sembol"]:
            continue
        if k["sinyal"] not in AL_SINYALLERI:
            continue
        k_idx = _baz_indeks(seri, datetime.date.fromisoformat(k["tarih"]))
        if k_idx is None:
            continue
        fark = k_idx - radar_idx
        if 0 <= fark <= DONUSUM_PENCERE_GUN:
            return {"donusum_durumu": "DONUSTU", "donusum_gun": fark,
                    "donusturen_sinyal": k["sinyal"], "donusturen_tarih": k["tarih"]}

    bugun_idx = len(seri) - 1
    if bugun_idx - radar_idx >= DONUSUM_PENCERE_GUN:
        return {"donusum_durumu": "DONUSMEDI"}
    return {"donusum_durumu": "BEKLIYOR"}  # pencere henuz kapanmadi


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

        if tip in AL_SINYALLERI or tip in IZLEME_SINYALLERI:
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
        if s["sinyal"] not in (AL_SINYALLERI | RISK_OFF_SINYALLERI | IZLEME_SINYALLERI):
            continue
        sinyal_tarih = datetime.datetime.fromisoformat(
            s["zaman_utc"].replace("Z", "+00:00")).date()
        anahtar = (s["sembol"], s["sinyal"], str(sinyal_tarih))
        if anahtar in mevcut_anahtarlar:
            continue
        izleme_mi = s["sinyal"] in IZLEME_SINYALLERI
        kayit = {
            "sembol": s["sembol"], "sinyal": s["sinyal"], "tarih": str(sinyal_tarih),
            "sinyal_fiyat": float(s["fiyat"]),
            # IZLEME de YUKARI bekler - AL_SINYALLERI'nin ONCUSU, ayni yon.
            "yon_beklentisi": "ASAGI_VEYA_NOTR" if s["sinyal"] in RISK_OFF_SINYALLERI
                              else "YUKARI",
            "dogrulama_durumu": "BEKLIYOR",
        }
        if izleme_mi:
            kayit["kategori"] = "IZLEME"
            kayit["donusum_durumu"] = "BEKLIYOR"
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

    # Yeniden dogrulama TUM arsivi tarar - donem en eski kaydi kapsamali
    tarihler = [datetime.date.fromisoformat(k["tarih"]) for k in arsiv["kayitlar"]]
    donem = _donem_sec(min(tarihler) if tarihler else None)
    print(f"Fiyat donemi: {donem} (arsivin en eskisi: "
          f"{min(tarihler) if tarihler else '-'})")

    piyasa_ticker, piyasa_seri = _piyasa_serisi_al(donem)

    bugun = datetime.datetime.now(datetime.timezone.utc).date()
    fiyat_serileri = {}
    dogrulanan_sayisi = 0
    tasinan_sayisi = 0
    for kayit in arsiv["kayitlar"]:
        eski_surum = kayit.get("olcum_surumu", 1) < OLCUM_SURUMU
        if kayit["dogrulama_durumu"] != "BEKLIYOR" and not eski_surum:
            continue
        sinyal_tarih = datetime.date.fromisoformat(kayit["tarih"])
        if (bugun - sinyal_tarih).days < DOGRULAMA_ICIN_GEREKEN_GUN:
            continue  # T+3 islem gunu icin en az bu kadar takvim gunu sart

        sembol = kayit["sembol"]
        if sembol not in fiyat_serileri:
            fiyat_serileri[sembol] = _seri_cek(f"{sembol}.IS", donem)
        seri = fiyat_serileri[sembol]
        if not seri:
            continue  # seri yoksa kayda DOKUNULMAZ, eski hali korunur

        bulunan = 0
        for gun in TAKIP_GUNLERI:
            t_fiyat = _t_plus_kapanis(seri, sinyal_tarih, gun)
            if t_fiyat and kayit["sinyal_fiyat"] > 0:
                kayit[f"getiri_t{gun}_pct"] = round(
                    (t_fiyat / kayit["sinyal_fiyat"] - 1) * 100, 3)
                bulunan += 1
        _goreli_yaz(kayit, piyasa_seri, uzerine_yaz=eski_surum)

        if bulunan == len(TAKIP_GUNLERI):
            onceden_dogruydu = kayit["dogrulama_durumu"] == "DOGRULANDI"
            kayit["dogrulama_durumu"] = "DOGRULANDI"
            kayit["olcum_surumu"] = OLCUM_SURUMU
            if onceden_dogruydu:
                tasinan_sayisi += 1
            else:
                dogrulanan_sayisi += 1
    print(f"{dogrulanan_sayisi} sinyal bu kosumda dogrulandi (T+3 islem gunu gecmis)")
    if tasinan_sayisi:
        print(f"{tasinan_sayisi} eski kayit islem-gunu penceresiyle YENIDEN "
              f"hesaplandi (olcum surumu {OLCUM_SURUMU})")

    # 26.08 EKLENDI: IZLEME kayitlarinin donusum kontrolu. Forward-return
    # dogrulamasindan BAGIMSIZ - T+3 beklemez, sadece fiyat serisi (bar
    # indeksi icin) gerekir. Sadece BEKLIYOR olanlar tekrar kontrol edilir;
    # DONUSTU/DONUSMEDI nihaidir.
    donusum_kontrol_sayisi = 0
    for kayit in arsiv["kayitlar"]:
        if kayit.get("kategori") != "IZLEME":
            continue
        if kayit.get("donusum_durumu") != "BEKLIYOR":
            continue
        sembol = kayit["sembol"]
        if sembol not in fiyat_serileri:
            fiyat_serileri[sembol] = _seri_cek(f"{sembol}.IS", donem)
        sonuc = _donusum_kontrol(kayit, arsiv["kayitlar"], fiyat_serileri[sembol])
        if sonuc is None:
            continue  # seri yok, dokunma
        kayit.update(sonuc)
        donusum_kontrol_sayisi += 1
    if donusum_kontrol_sayisi:
        print(f"{donusum_kontrol_sayisi} IZLEME kaydi donusum icin kontrol edildi")

    tip_ozet, tip_ozet_rel = {}, {}
    for tip in (AL_SINYALLERI | RISK_OFF_SINYALLERI | IZLEME_SINYALLERI):
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

    # Donusum ozeti - IZLEME turleri icin ayrica.
    izleme_donusum_ozet = {}
    for tip in IZLEME_SINYALLERI:
        alt = [k for k in arsiv["kayitlar"] if k["sinyal"] == tip
               and k.get("donusum_durumu") in ("DONUSTU", "DONUSMEDI")]
        if not alt:
            continue
        donusen = [k for k in alt if k["donusum_durumu"] == "DONUSTU"]
        izleme_donusum_ozet[tip] = {
            "karar_verilmis": len(alt),
            "donusen": len(donusen),
            "donusum_orani_pct": round(100 * len(donusen) / len(alt), 1),
            "ort_donusum_gun": round(statistics.mean(
                [k["donusum_gun"] for k in donusen]), 1) if donusen else None,
        }

    arsiv["tip_ozet"] = tip_ozet
    arsiv["tip_ozet_goreli"] = tip_ozet_rel
    if izleme_donusum_ozet:
        arsiv["izleme_donusum_ozet"] = izleme_donusum_ozet
    arsiv["piyasa_referansi"] = piyasa_ticker or "YOK"
    arsiv["olcum_surumu"] = OLCUM_SURUMU
    surumsuz = sum(1 for k in arsiv["kayitlar"]
                   if k["dogrulama_durumu"] == "DOGRULANDI"
                   and k.get("olcum_surumu", 1) < OLCUM_SURUMU)
    if surumsuz:
        arsiv["_uyari"] = (f"{surumsuz} dogrulanmis kayit hala eski olcum "
                           f"surumunde (fiyat serisi cekilemedi) - karisik arsiv")
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
