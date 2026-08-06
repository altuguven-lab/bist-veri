"""
ANLATI-TEKNIK CAPRAZ REFERANS (06.08.2026) - Faz V0
Kurul karari: gun-ici (15dk) sentetik backtest yerine, P1/P2'nin
GERCEK tarihsel sinyal gecmisini (tv_alerts_latest.json + arsiv)
arastirma_hedef_fiyat.json'daki anlati gucuyle CAPRAZ REFERANSLAR.
Arastirma raporunun onerisiyle uyumlu: PEAD/analist-revizyon etkisi
haftalar surer, bu yuzden T+3'e ek olarak T+10/T+20 de olculuyor.

SALT OLCUM - Pine'a hic dokunmuyor, hicbir yeni Pine script'i
gerektirmiyor (kurulun onerdigi mimari: sentez Python/GitHub
katmaninda, Pine yalniz teknik tetikleyiciyi uretmeye devam eder).

Yontem:
  - hafta_denetim.py'nin GUVENILIR, TEST EDILMIS bilesenleri
    (sinyalleri_topla, zenginlestir, FiyatServisi, TEST_FIYAT_PARMAK_IZI
    disla) AYNEN yeniden kullanilir - sifirdan yazip yeni hata riski
    almamak icin.
  - Her GERCEK trade sinyali (P1/P2/ACIL_CIK/P3_SKOR_AL onekli,
    GUNLUK_OZET DEGIL) icin, sinyal ONCESI (90 gun penceresinde) o
    sembolun en son arastirma_hedef_fiyat.json revizyonuna bakilir:
    YUKARI -> GUCLU_ANLATI, ASAGI -> ZAYIF_ANLATI, kayit yoksa
    BILINMIYOR.
  - T+3/T+10/T+20 getirileri hesaplanip GUCLU/ZAYIF/BILINMIYOR
    gruplarinda karsilastirilir.
"""
import json, os, glob, datetime

KULUCKA_BASI = datetime.date(2026, 7, 7)
TEST_FIYAT_PARMAK_IZI = ("THYAO", 348.50)
GIRIS_ONEK = ("P1", "P2", "ACIL_CIK", "P3_SKOR_AL")
ANLATI_PENCERE_GUN = 90  # arastirmadaki PEAD/revizyon etki suresiyle uyumlu
UFUKLAR = (3, 10, 20)
CIKTI = "data/denetim/anlati_teknik_capraz_referans.json"


def _json_oku(yol):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def sinyalleri_topla():
    kayitlar, gorulen = [], set()
    yollar = ["data/tv_alerts_latest.json"]
    for desen in ("data/tv_alerts_2*.json", "data/arsiv/tv_alerts*.json", "data/arsiv/*.json"):
        yollar += sorted(glob.glob(desen))
    for yol in yollar:
        d = _json_oku(yol)
        if not d:
            continue
        for s in d.get("sinyal_gecmisi", []) or d.get("sinyaller", []):
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
    temiz = []
    for s in kayitlar:
        try:
            t = datetime.datetime.fromisoformat(str(s["zaman_utc"]).replace("Z", "+00:00"))
        except Exception:
            continue
        fiyat = _f(s.get("fiyat"))
        test_mi = ((s.get("sembol"), fiyat) == TEST_FIYAT_PARMAK_IZI
                   or "TEST" in str(s.get("sinyal", "")).upper())
        temiz.append({**s, "_t": t, "_tarih": t.date(), "_fiyat": fiyat, "_test": test_mi})
    return [s for s in temiz if s["_tarih"] >= KULUCKA_BASI and not s["_test"]]


class FiyatServisi:
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
                start=str(KULUCKA_BASI - datetime.timedelta(days=7)), auto_adjust=False)
            kapanis = [(idx.date(), float(v)) for idx, v in df["Close"].items()] if len(df) else []
        except Exception as e:
            self.hata = f"{sembol}: {e}"
            kapanis = []
        self.seriler[sembol] = kapanis or None
        return self.seriler[sembol]

    def t_arti_n_kapanis(self, sembol, sinyal_tarihi, n):
        seri = self.seri(sembol)
        if not seri:
            return None
        sonrakiler = [(t, c) for t, c in seri if t > sinyal_tarihi]
        return sonrakiler[n - 1][1] if len(sonrakiler) >= n else None


def anlati_gecmisi_yukle():
    """sembol -> [(tarih, yon), ...] artan sirali."""
    veri = _json_oku("data/arastirma_hedef_fiyat.json") or {}
    gecmis = {}
    for k in veri.get("kayitlar", []):
        try:
            t = datetime.date.fromisoformat(k["tarih"])
        except (KeyError, ValueError):
            continue
        gecmis.setdefault(k["sembol"], []).append((t, k["yon"]))
    for sembol in gecmis:
        gecmis[sembol].sort(key=lambda x: x[0])
    return gecmis


def anlati_durumu(gecmis, sembol, sinyal_tarihi):
    """Sinyal ONCESI, ANLATI_PENCERE_GUN icindeki en son revizyon yonu."""
    kayitlar = gecmis.get(sembol, [])
    esik = sinyal_tarihi - datetime.timedelta(days=ANLATI_PENCERE_GUN)
    uygunlar = [(t, y) for t, y in kayitlar if esik <= t <= sinyal_tarihi]
    if not uygunlar:
        return "BILINMIYOR"
    son_yon = uygunlar[-1][1]
    if son_yon == "YUKARI":
        return "GUCLU_ANLATI"
    elif son_yon == "ASAGI":
        return "ZAYIF_ANLATI"
    return "BILINMIYOR"


def main():
    ham = sinyalleri_topla()
    sinyaller = zenginlestir(ham)
    girisler = [s for s in sinyaller
                if any(str(s.get("sinyal", "")).startswith(onek) for onek in GIRIS_ONEK)]
    print(f"Toplam giris-tipi sinyal: {len(girisler)}")

    anlati_gecmis = anlati_gecmisi_yukle()
    fs = FiyatServisi()

    detaylar = []
    for s in girisler:
        if s["_fiyat"] is None:
            continue
        durum = anlati_durumu(anlati_gecmis, s["sembol"], s["_tarih"])
        kayit = {"sembol": s["sembol"], "sinyal": s["sinyal"], "tarih": str(s["_tarih"]),
                  "fiyat": s["_fiyat"], "anlati_durumu": durum}
        for n in UFUKLAR:
            kapanis = fs.t_arti_n_kapanis(s["sembol"], s["_tarih"], n)
            kayit[f"t{n}_getiri_pct"] = (round((kapanis / s["_fiyat"] - 1) * 100, 2)
                                          if kapanis is not None else None)
        detaylar.append(kayit)

    # grup bazli ozet - her ufuk icin ayri
    grup_ozet = {}
    for durum in ("GUCLU_ANLATI", "ZAYIF_ANLATI", "BILINMIYOR"):
        grup = [d for d in detaylar if d["anlati_durumu"] == durum]
        grup_ozet[durum] = {"toplam_sinyal": len(grup)}
        for n in UFUKLAR:
            hesaplanan = [d[f"t{n}_getiri_pct"] for d in grup if d[f"t{n}_getiri_pct"] is not None]
            if not hesaplanan:
                continue
            pozitif = [x for x in hesaplanan if x > 0]
            grup_ozet[durum][f"t{n}"] = {
                "hesaplanan_sayisi": len(hesaplanan),
                "isabet_pct": round(100 * len(pozitif) / len(hesaplanan), 1),
                "ort_getiri_pct": round(sum(hesaplanan) / len(hesaplanan), 3),
            }

    sonuc = {
        "olusturma_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 - P1/P2 gercek sinyal gecmisi x anlati gucu capraz "
                "referansi. SALT OLCUM. FiyatServisi hatasi: " + str(fs.hata if not fs.aktif else "yok")),
        "anlati_pencere_gun": ANLATI_PENCERE_GUN, "ufuklar": list(UFUKLAR),
        "grup_ozet": grup_ozet, "detaylar": detaylar,
    }
    os.makedirs("data/denetim", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"\nYazildi: {CIKTI}")
    for durum, v in grup_ozet.items():
        print(f"{durum}: {v['toplam_sinyal']} sinyal", {k: v[k] for k in v if k.startswith("t")})


if __name__ == "__main__":
    main()
