"""
HAFTA KAPANISI DENETIMI (K1) - Kulucka metrik betigi - v1.2
v1.1 (14.07): parmak izi tarih kilidi (<=13.07); GERCEK_TEST oneki
standardi; O2 kullanilabilirlik metrikleri bolumu eklendi.
v1.2 (16.07): KACAN FIRSAT bolumu (EREGL vakasi) - giris sinyalsiz
+3%/T+3 hareketler ve POZ_AZALT-sonrasi-ralli (erken savunma) vakalari.
Amac: hukum gununde "disiplinin onledigi zarar" (M1) ile "disiplinin
kacirdigi kar" YAN YANA okunsun; tek basina karar gerekcesi DEGILDIR.
Kaynak: KULUCKA_PROTOKOLU.md M1-M6 | Tuzuk: KOMITE_TUZUGU.md
Calistirma: python hafta_denetim.py   (repo kokunde)
Cikti: data/denetim/hafta_<yil>-W<hafta>.md + .json

YONTEM NOTLARI (K5 karari dahil):
- Sinyal fiyati webhook {{close}} degeridir: sinyal barinin GERCEK
  kapanisi, gecikmesiz. M1/M2 bu fiyatla hesaplanir -> kayma yok.
- GUNLUK_OZET icindeki skor/kgs/rejim degerleri TASARIM GEREGI bir bar
  gecikmelidir (G1 tasiyici plot mimarisi). M4 ve skor bazli kirilimlar
  bu gecikmeyle hesaplanir ve bu dosyada boyle raporlanir.
- Test kayitlari OTOMATIK dislanir: THYAO fiyat=348.50 parmak izi,
  sinyal adinda TEST gecenler. Placeholder bozuk alanlar ({{...}} / ?)
  sinyali gecersiz kilmaz; yalnizca skor bazli metriklerden duser.
- T+N = sinyal gununden sonraki N. ISLEM GUNU (sembolun kendi gunluk
  serisinden). Henuz T+3 dolmamis sinyaller "beklemede" sayilir ve
  orana KATILMAZ.
- Fiyat kaynagi: yfinance (<SEMBOL>.IS). Erisilemezse M1/M2 "HESAPLANAMADI"
  olarak isaretlenir; betik asla sessizce eksik veriyle oran basmaz.
"""

import json
import os
import glob
import datetime
import statistics

KULUCKA_BASI = datetime.date(2026, 7, 7)
TEST_FIYAT_PARMAK_IZI = ("THYAO", 348.50)
# v1.2 (23.07) DUZELTME: tarih kilidi KALDIRILDI. Kanit: TradingView'de
# silinmemis, sabit fiyatli bir test alarmi bu parmak izini 07-22 Temmuz
# arasinda 6 kez tekrar uretti (tarih kilidi varken 22.07 kaydi denetimden
# KACIYORDU - M2 istatistigini kirletme riski). 14.07'de ASELS'in gercek
# kapanisinin bir kez 348.50 basmasi ihtimali kabul edilebilir bir bedel;
# THYAO'nun ayni kurusta alti kez "AL" basmasindan cok daha az zararli.
TRADE_SINYALLERI_M1 = ("ACIL_CIK",)
TRADE_SINYALLERI_M2_ONEK = ("P1",)          # P1_AL, P1_KALITELI_AL, P1Q...
YENIDEN_GIRIS_ONEK = ("P1", "P2")           # M5 icin
M1_ESIK, M2_ESIK, M3_ESIK, M3_RAGMEN_AZAMI = 0.60, 0.55, 0.80, 2
KACAN_ESIK = 0.03           # T -> T+3 getiri esigi (kacan firsat tanimi)
GIRIS_ONEK = ("P1", "P2")   # "giris sinyali" sayilanlar


# ----------------------------------------------------------- veri okuma
def _json_oku(yol):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def sinyalleri_topla():
    """tv_alerts_latest + varsa aylik arsivler; (zaman,sembol,sinyal) tekillestirir."""
    kayitlar, gorulen = [], set()
    yollar = ["data/tv_alerts_latest.json"]
    for desen in ("data/tv_alerts_2*.json", "data/arsiv/tv_alerts*.json",
                  "data/arsiv/*.json"):
        yollar += sorted(glob.glob(desen))
    for yol in yollar:
        d = _json_oku(yol)
        if not d:
            continue
        for s in d.get("sinyal_gecmisi", []):
            anahtar = (s.get("zaman_utc"), s.get("sembol"), s.get("sinyal"))
            if anahtar in gorulen:
                continue
            gorulen.add(anahtar)
            kayitlar.append(s)
    return kayitlar


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def zenginlestir(kayitlar):
    """Her kayda: tarih, test_mi, skor_gecerli_mi bayraklari."""
    temiz = []
    for s in kayitlar:
        try:
            t = datetime.datetime.fromisoformat(
                str(s["zaman_utc"]).replace("Z", "+00:00"))
        except Exception:
            continue
        fiyat = _f(s.get("fiyat"))
        test_mi = (
            (s.get("sembol"), fiyat) == TEST_FIYAT_PARMAK_IZI  # tarih sartsiz
            or "TEST" in str(s.get("sinyal", "")).upper()
        )
        bozuk = any("{{" in str(s.get(k, "")) or str(s.get(k, "")).strip() == "?"
                    for k in ("skor", "kgs", "rejim"))
        temiz.append({**s, "_t": t, "_tarih": t.date(), "_fiyat": fiyat,
                      "_test": test_mi, "_skor_ok": not bozuk})
    # kulucka penceresi + testler disari
    return [s for s in temiz
            if s["_tarih"] >= KULUCKA_BASI and not s["_test"]]


# ----------------------------------------------------------- fiyat servisi
class FiyatServisi:
    """Sembol basina gunluk kapanis serisi (yfinance). Yoksa None doner."""

    def __init__(self):
        self.seriler, self.aktif, self.hata = {}, True, None
        try:
            import yfinance  # noqa
        except Exception as e:
            self.aktif, self.hata = False, f"yfinance yok: {e}"

    def seri(self, sembol):
        if not self.aktif:
            return None
        if sembol in self.seriler:
            return self.seriler[sembol]
        try:
            import yfinance as yf
            df = yf.Ticker(f"{sembol}.IS").history(
                start=str(KULUCKA_BASI - datetime.timedelta(days=7)),
                auto_adjust=False)
            kapanis = [(idx.date(), float(v))
                       for idx, v in df["Close"].items()] if len(df) else []
        except Exception as e:
            self.hata = f"{sembol}: {e}"
            kapanis = []
        self.seriler[sembol] = kapanis or None
        return self.seriler[sembol]

    def t_arti_n_kapanis(self, sembol, sinyal_tarihi, n):
        """Sinyal gununden sonraki n. islem gununun kapanisi; yoksa None."""
        seri = self.seri(sembol)
        if not seri:
            return None
        sonrakiler = [(t, c) for t, c in seri if t > sinyal_tarihi]
        return sonrakiler[n - 1][1] if len(sonrakiler) >= n else None


# ----------------------------------------------------------- metrikler
def m1_m2(sinyaller, fs):
    def oranla(adaylar, hit_kosulu):
        hit = miss = beklemede = hesapsiz = 0
        detay = []
        for s in adaylar:
            if s["_fiyat"] is None:
                hesapsiz += 1
                continue
            kapanis = fs.t_arti_n_kapanis(s["sembol"], s["_tarih"], 3)
            if kapanis is None:
                # seri var ama T+3 dolmamis mi, seri mi yok?
                if fs.seri(s["sembol"]):
                    beklemede += 1
                else:
                    hesapsiz += 1
                continue
            ok = hit_kosulu(kapanis, s["_fiyat"])
            hit, miss = hit + ok, miss + (not ok)
            detay.append((str(s["_tarih"]), s["sembol"], s["sinyal"],
                          s["_fiyat"], round(kapanis, 2), "HIT" if ok else "MISS"))
        toplam = hit + miss
        oran = hit / toplam if toplam else None
        return {"hit": hit, "miss": miss, "beklemede": beklemede,
                "hesaplanamadi": hesapsiz, "oran": oran, "detay": detay}

    acil = [s for s in sinyaller if s.get("sinyal") in TRADE_SINYALLERI_M1]
    p1 = [s for s in sinyaller
          if str(s.get("sinyal", "")).startswith(TRADE_SINYALLERI_M2_ONEK)]
    return (oranla(acil, lambda kap, ref: kap < ref),
            oranla(p1, lambda kap, ref: kap > ref))


def m3(islem_dosyasi):
    d = _json_oku(islem_dosyasi)
    if d is None:
        return {"durum": "DOSYA OKUNAMADI"}
    islemler = [i for i in d.get("islemler", [])]
    if not islemler:
        return {"durum": "VERI YOK (henuz islem kaydi girilmemis)",
                "toplam": 0}
    say = {}
    for i in islemler:
        e = str(i.get("sinyal_etiketi", "ETIKETSIZ")).upper()
        say[e] = say.get(e, 0) + 1
    toplam = len(islemler)
    sinyalli = say.get("SINYALLI", 0)
    return {"toplam": toplam, "kirilim": say,
            "sinyalli_oran": sinyalli / toplam,
            "ragmen": say.get("SINYALE_RAGMEN", 0),
            "gecer_mi": sinyalli / toplam > M3_ESIK
                        and say.get("SINYALE_RAGMEN", 0) <= M3_RAGMEN_AZAMI}


def m4_rejim_flip(sinyaller):
    """GUNLUK_OZET rejim degeri degisim sayisi (bir bar gecikmeli veri)."""
    ozet = [s for s in sinyaller
            if s.get("sinyal") == "GUNLUK_OZET" and s["_skor_ok"]]
    ozet.sort(key=lambda s: s["_t"])
    flip, seri = {}, {}
    for s in ozet:
        sem, rejim = s["sembol"], str(s.get("rejim"))
        if sem in seri and seri[sem] != rejim:
            flip[sem] = flip.get(sem, 0) + 1
        seri[sem] = rejim
    return {"sembol_flip": flip, "gozlem": len(ozet),
            "not": "veri yalnizca gecerli GUNLUK_OZET kayitlarindan; "
                   "seri kisa ise anlamsizdir"}


def m5_yeniden_giris(sinyaller):
    cikislar = [s for s in sinyaller if s.get("sinyal") in TRADE_SINYALLERI_M1]
    gecikmeler = []
    for c in cikislar:
        adaylar = [s for s in sinyaller
                   if s["sembol"] == c["sembol"] and s["_t"] > c["_t"]
                   and str(s.get("sinyal", "")).startswith(YENIDEN_GIRIS_ONEK)]
        if adaylar:
            ilk = min(adaylar, key=lambda s: s["_t"])
            gecikmeler.append((c["sembol"], str(c["_tarih"]),
                               (ilk["_tarih"] - c["_tarih"]).days))
    return {"vakalar": gecikmeler,
            "medyan_gun": statistics.median([g[2] for g in gecikmeler])
            if gecikmeler else None,
            "not": "takvim gunu bazli; seans bazina fiyat serisi girince gecilecek"}


def m6_haber_kesisim(sinyaller, fs):
    h = _json_oku("data/haber_akisi.json") or {}
    haberler = h.get("haberler", [])
    gun_sembol = set()
    for hb in haberler:
        semboller = hb.get("ilgili_semboller") or hb.get("semboller") or []
        tarih = str(hb.get("zaman") or hb.get("tarih") or "")[:10]
        for sem in semboller:
            gun_sembol.add((tarih, sem))
    trade = [s for s in sinyaller
             if s.get("sinyal") in TRADE_SINYALLERI_M1
             or str(s.get("sinyal", "")).startswith(TRADE_SINYALLERI_M2_ONEK)]
    haberli = [s for s in trade if any(
        (str(s["_tarih"] + datetime.timedelta(days=d)), s["sembol"]) in gun_sembol
        for d in (-1, 0, 1))]
    return {"trade_sinyal": len(trade), "haberli": len(haberli),
            "not": "haber_akisi son ~77 kaydi tutar; tarihsel eslesme "
                   "sinirlidir - arsivlenmis haber olmadan M6 kismi kalir"}


def o2_kullanilabilirlik(sinyaller):
    """Icra Trader'in haftalik raporu icin ham metrikler (tuzuk A.6)."""
    trade = [s for s in sinyaller if s.get("sinyal") != "GUNLUK_OZET"]
    gunler, tip, saat, sembol = {}, {}, {}, {}
    for s in trade:
        gunler.setdefault(str(s["_tarih"]), 0)
        gunler[str(s["_tarih"])] += 1
        tip[s["sinyal"]] = tip.get(s["sinyal"], 0) + 1
        saat[s["_t"].hour] = saat.get(s["_t"].hour, 0) + 1
        sembol[s["sembol"]] = sembol.get(s["sembol"], 0) + 1
    gun_ort = (sum(gunler.values()) / len(gunler)) if gunler else 0
    yogun_saat = max(saat, key=saat.get) if saat else None
    return {"islem_sinyali_toplam": len(trade),
            "gun_ortalama": round(gun_ort, 1),
            "en_yogun_gun": max(gunler.values()) if gunler else 0,
            "tip_dagilimi": dict(sorted(tip.items(), key=lambda x: -x[1])),
            "yogun_saat_utc": yogun_saat,
            "sembol_dagilimi": dict(sorted(sembol.items(), key=lambda x: -x[1]))}


def kacan_firsatlar(sinyaller, fs):
    """Disiplinin maliyeti: (a) evrende giris sinyalsiz +KACAN_ESIK/T+3
    hareketler, (b) POZ_AZALT sonrasi T+3'te +KACAN_ESIK ralli (erken
    savunma). Evren = bist_quotes.json'daki semboller."""
    if not fs.aktif:
        return {"durum": "HESAPLANAMADI (fiyat kaynagi yok)"}
    q = _json_oku("data/bist_quotes.json") or {}
    semboller = [v.get("sembol") for v in q.get("veriler", []) if v.get("sembol")]
    if not semboller:
        semboller = sorted({s["sembol"] for s in sinyaller})

    giris_gunleri = {}
    for s in sinyaller:
        if str(s.get("sinyal", "")).startswith(GIRIS_ONEK):
            giris_gunleri.setdefault(s["sembol"], []).append(s["_tarih"])

    kacan = []
    for sem in semboller:
        seri = fs.seri(sem) or []
        seri = [(t, c) for t, c in seri if t >= KULUCKA_BASI]
        en_iyi = None
        for i in range(len(seri) - 3):
            getiri = seri[i + 3][1] / seri[i][1] - 1
            if getiri < KACAN_ESIK:
                continue
            gun = seri[i][0]
            kapsandi = any(abs((g - gun).days) <= 1
                           for g in giris_gunleri.get(sem, []))
            if not kapsandi and (en_iyi is None or getiri > en_iyi[1]):
                en_iyi = (gun, getiri, seri[i][1], seri[i + 3][1])
        if en_iyi:
            kacan.append((sem, str(en_iyi[0]), round(en_iyi[1] * 100, 1),
                          en_iyi[2], en_iyi[3]))
    kacan.sort(key=lambda x: -x[2])

    erken_savunma = []
    for s in sinyaller:
        if s.get("sinyal") != "POZ_AZALT" or s["_fiyat"] is None:
            continue
        t3 = fs.t_arti_n_kapanis(s["sembol"], s["_tarih"], 3)
        if t3 and t3 / s["_fiyat"] - 1 >= KACAN_ESIK:
            erken_savunma.append((s["sembol"], str(s["_tarih"]), s["_fiyat"],
                                  round(t3, 2),
                                  round((t3 / s["_fiyat"] - 1) * 100, 1)))
    return {"kacan": kacan, "erken_savunma": erken_savunma,
            "esik_yuzde": KACAN_ESIK * 100}


# ----------------------------------------------------------- rapor
def esik_satiri(ad, oran, esik, ters=False):
    if oran is None:
        return f"| {ad} | HESAPLANAMADI | {esik:.0%} | - |"
    durum = "GECTI" if oran > esik else "KALDI"
    return f"| {ad} | {oran:.1%} | >{esik:.0%} | {durum} |"


def main():
    bugun = datetime.date.today()
    yil, hafta, _ = bugun.isocalendar()
    sinyaller = zenginlestir(sinyalleri_topla())
    fs = FiyatServisi()
    M1, M2 = m1_m2(sinyaller, fs)
    M3 = m3("data/islem_gunlugu.json")
    M4 = m4_rejim_flip(sinyaller)
    M5 = m5_yeniden_giris(sinyaller)
    M6 = m6_haber_kesisim(sinyaller, fs)
    O2 = o2_kullanilabilirlik(sinyaller)
    KF = kacan_firsatlar(sinyaller, fs)

    bozuk = sum(1 for s in sinyaller if not s["_skor_ok"])
    gun = (bugun - KULUCKA_BASI).days + 1

    md = []
    md.append(f"# Hafta Kapanisi Denetimi - {yil}-W{hafta:02d}")
    md.append(f"Kulucka gunu: {gun}/42 | Kayit: {len(sinyaller)} gercek sinyal "
              f"(test dislandi) | skor alani bozuk: {bozuk}")
    if not fs.aktif or fs.hata:
        md.append(f"\n> FIYAT KAYNAGI SORUNU: {fs.hata or 'bilinmiyor'} - "
                  "M1/M2 sonuclarina guvenme, betigi Actions icinde kosur.")
    md.append("\n## Birincil metrikler\n")
    md.append("| Metrik | Deger | Esik | Durum |")
    md.append("|---|---|---|---|")
    md.append(esik_satiri(f"M1 ACIL_CIK isabet (hit {M1['hit']}/"
                          f"{M1['hit']+M1['miss']}, beklemede {M1['beklemede']})",
                          M1["oran"], M1_ESIK))
    md.append(esik_satiri(f"M2 P1 isabet (hit {M2['hit']}/"
                          f"{M2['hit']+M2['miss']}, beklemede {M2['beklemede']})",
                          M2["oran"], M2_ESIK))
    if M3.get("toplam"):
        md.append(f"| M3 sinyal-uyum | {M3['sinyalli_oran']:.1%} "
                  f"(RAGMEN: {M3['ragmen']}) | >80% ve RAGMEN<=2 | "
                  f"{'GECTI' if M3['gecer_mi'] else 'KALDI'} |")
    else:
        md.append(f"| M3 sinyal-uyum | {M3.get('durum','?')} | >80% | - |")
    md.append("\n## Ikincil metrikler (esiksiz, izleme)\n")
    md.append(f"- M4 rejim flip: {M4['sembol_flip'] or 'henuz seri yok'} "
              f"({M4['gozlem']} gecerli gunluk ozet; bir bar gecikmeli veri)")
    md.append(f"- M5 yeniden-giris: medyan {M5['medyan_gun']} gun | "
              f"vakalar: {M5['vakalar'] or 'yok'}")
    md.append(f"- M6 haberli sinyal: {M6['haberli']}/{M6['trade_sinyal']} "
              f"({M6['not']})")
    md.append("\n## Kullanilabilirlik (O2 - Icra Trader raporu girdisi)\n")
    md.append(f"- Islem sinyali: toplam {O2['islem_sinyali_toplam']}, "
              f"gun ort. {O2['gun_ortalama']}, en yogun gun {O2['en_yogun_gun']}")
    md.append(f"- Tip dagilimi: {O2['tip_dagilimi']}")
    md.append(f"- En yogun saat (UTC): {O2['yogun_saat_utc']} | "
              f"Sembol dagilimi: {O2['sembol_dagilimi']}")
    md.append("- Manuel girdi (Icra Trader doldurur): kacan/gec gorulen "
              "alarm sayisi, panelde en cok bloklayan neden")
    md.append("\n## Kacan Firsat (disiplinin maliyeti - tek basina karar gerekcesi DEGIL)\n")
    if KF.get("durum"):
        md.append(f"- {KF['durum']}")
    else:
        md.append(f"- Tanim: T->T+3 >= +{KF['esik_yuzde']:.0f}%, +-1 gun icinde giris sinyali yok")
        for sem, gun, yuzde, p0, p3 in KF["kacan"][:10]:
            md.append(f"- KACAN: {sem} | {gun} | {p0:.2f} -> {p3:.2f} | +{yuzde}%")
        if not KF["kacan"]:
            md.append("- KACAN: yok")
        for sem, gun, p0, p3, yuzde in KF["erken_savunma"]:
            md.append(f"- ERKEN SAVUNMA: {sem} | {gun} POZ_AZALT {p0} -> T+3 {p3} | +{yuzde}%")
        if not KF["erken_savunma"]:
            md.append("- ERKEN SAVUNMA: yok")
        md.append("- Okuma kurali: bu bolum M1 (onlenen zarar) ile YAN YANA okunur; hukum gunu bilancosunun iki sutunu.")
    md.append("\n## M1/M2 vaka dokumu\n")
    for etiket, M in (("M1", M1), ("M2", M2)):
        for satir in M["detay"]:
            md.append(f"- {etiket}: " + " | ".join(map(str, satir)))
        if M["hesaplanamadi"]:
            md.append(f"- {etiket}: {M['hesaplanamadi']} kayit fiyat "
                      "verisi olmadan HESAPLANAMADI olarak birakildi")
    md.append("\n---\nYontem notlari betigin bas yorumundadir; degisiklik = commit.")

    os.makedirs("data/denetim", exist_ok=True)
    kok = f"data/denetim/hafta_{yil}-W{hafta:02d}"
    with open(kok + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(kok + ".json", "w", encoding="utf-8") as f:
        json.dump({"olusturma_utc": datetime.datetime.now(
                       datetime.timezone.utc).isoformat(),
                   "kulucka_gunu": gun,
                   "M1": {k: v for k, v in M1.items() if k != "detay"},
                   "M2": {k: v for k, v in M2.items() if k != "detay"},
                   "M3": M3, "M4": M4, "M5": M5, "M6": M6, "O2": O2, "KF": KF},
                  f, ensure_ascii=False, indent=2)
    print("\n".join(md))
    print(f"\nYAZILDI: {kok}.md / .json")


if __name__ == "__main__":
    main()
