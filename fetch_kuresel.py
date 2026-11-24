"""
KURESEL GOSTERGE (27.07.2026, ALTYAPI) - fetch_asya.py'nin genisletilmis
hali. Gunde UC kez farkli saatte cagrilir, HER SEFERINDE dosyayi
OKUYUP-BIRLESTIRIR (bir onceki kontrolun verisini kaybetmez):

  09:35 TSI - ASYA (kapanmis): dun kapanis vs onceki kapanis (gun-oncesi)
  11:15 TSI - AVRUPA (yeni acilmis): BUGUNKU ilk bar vs son bar (kendi
              acilisina gore, 5dk barlarla)
  16:40 TSI - AMERIKA (yeni acilmis): ayni yontem, ABD icin

Asya icin "onceki kapanis" anlamli (kendi seansi bitti); Avrupa/ABD
icin "onceki kapanis" YANLIS olur (BIST'in tum gunu boyunca hareket
etmis olabilirler) - o yuzden ikisi FARKLI hesap yontemi kullanir.
"""
import json, datetime, sys, os, math
import yfinance as yf

ASYA_ENDEKSLER = [
    ("Nikkei 225",      "^N225",     "Japonya"),
    ("Kospi",            "^KS11",    "G.Kore"),
    ("Sanghay Bilesik",  "000001.SS","Cin"),
    ("Hang Seng",        "^HSI",     "H.Kong"),
]
AVRUPA_ENDEKSLER = [
    ("DAX",    "^GDAXI", "Almanya"),
    ("CAC 40", "^FCHI",  "Fransa"),
    ("FTSE 100", "^FTSE", "Ingiltere"),
]
AMERIKA_ENDEKSLER = [
    ("S&P 500", "^GSPC", "ABD"),
    ("Dow Jones", "^DJI", "ABD"),
    ("Nasdaq",  "^IXIC", "ABD"),
]
DOSYA = "data/kuresel_gosterge.json"

BORSA_TZ = {"^N225": "Asia/Tokyo", "^KS11": "Asia/Seoul", "000001.SS": "Asia/Shanghai", "^HSI": "Asia/Hong_Kong",
            "^GDAXI": "Europe/Berlin", "^FCHI": "Europe/Paris", "^FTSE": "Europe/London",
            "^GSPC": "America/New_York", "^DJI": "America/New_York", "^IXIC": "America/New_York"}


def _yerel_bugun(kod):
    from zoneinfo import ZoneInfo
    return datetime.datetime.now(ZoneInfo(BORSA_TZ.get(kod, "UTC"))).date()


def _bar_tarihi(ix, kod):
    """Bar zaman damgasinin BORSANIN yerel takvimindeki tarihi."""
    from zoneinfo import ZoneInfo
    try:
        return ix.tz_convert(ZoneInfo(BORSA_TZ.get(kod, "UTC"))).date() if ix.tzinfo else ix.date()
    except Exception:
        return ix.date()


def kapanmis_hesap(kod):
    """Asya tipi: onceki iki GUNLUK kapanisi kiyaslar (kendi seansi bitmis).
    04.08: NaN barlar "hata" olarak isaretlenir.
    24.11 (paket58, aksam denetimi 23.11): borsa tatilse (23.11 Tokyo) son bar BUGUN degildir; deger yine
    verilir ama seans_tarihi ve 'bugun_degil' uyarisi eklenir (brifing Cuma verisini bugunku sanmasin)."""
    df = yf.Ticker(kod).history(period="7d")
    satirlar = [(ix, float(c)) for ix, c in zip(df.index, df["Close"]) if not math.isnan(float(c))]
    if len(satirlar) < 2:
        return None, "yetersiz veri (NaN bar/tatil)", {}
    (ix_s, son), (ix_o, onceki) = satirlar[-1], satirlar[-2]
    st = _bar_tarihi(ix_s, kod)
    ek = {"seans_tarihi": str(st), "onceki_seans_tarihi": str(_bar_tarihi(ix_o, kod))}
    if st < _yerel_bugun(kod):
        ek["uyari"] = f"bugun_degil: son kapanis {st.strftime('%d.%m')} (tatil ya da veri gecikmesi)"
    return round((son / onceki - 1) * 100, 2), None, ek


def canli_hesap(kod):
    """Avrupa/ABD tipi: BUGUNKU ilk 5dk bar vs en son bar (kendi acilisina gore).
    24.11 (paket58): period="1d" Yahoo'da acilisin ilk dakikalarinda bos/NaN donuyordu (23-24.11 Avrupa).
    Artik 5 gunluk 5dk seri cekilir, YALNIZ borsanin yerel takvimine gore bugunun barlari kullanilir.
    Bugun bar yoksa (seans acilmamis/tatil) deger uretilmez, son seansin tarihi yazilir."""
    df = yf.Ticker(kod).history(period="5d", interval="5m")
    satirlar = [(ix, float(c)) for ix, c in zip(df.index, df["Close"]) if not math.isnan(float(c))]
    if not satirlar:
        return None, "veri yok (Yahoo bos dondu)", {}
    bugun = _yerel_bugun(kod)
    bugunku = [c for ix, c in satirlar if _bar_tarihi(ix, kod) == bugun]
    son_tarih = _bar_tarihi(satirlar[-1][0], kod)
    if len(bugunku) < 2:
        return None, f"bugun bar yok/yetersiz ({len(bugunku)}); son seans {son_tarih.strftime('%d.%m')} - seans acilmamis olabilir", \
            {"seans_tarihi": str(son_tarih)}
    ek = {"seans_tarihi": str(bugun), "bar_sayisi": len(bugunku),
          "son_bar_utc": satirlar[-1][0].tz_convert("UTC").strftime("%H:%M") if satirlar[-1][0].tzinfo else None}
    return round((bugunku[-1] / bugunku[0] - 1) * 100, 2), None, ek


def bolum_isle(liste, hesap_fn):
    sonuc = []
    for isim, kod, bolge in liste:
        try:
            degisim, hata, ek = hesap_fn(kod)
            kayit = {"isim": isim, "kod": kod, "bolge": bolge, **ek}
            if hata:
                kayit["hata"] = hata
            else:
                kayit["degisim_yuzde"] = degisim
            sonuc.append(kayit)
        except Exception as e:
            sonuc.append({"isim": isim, "kod": kod, "bolge": bolge, "hata": str(e)})
            print(f"UYARI: {isim} ({kod}) cekilemedi: {e}", file=sys.stderr)
    return sonuc

def ozet(liste):
    gecerli = [s["degisim_yuzde"] for s in liste if "degisim_yuzde" in s]
    if not gecerli:
        return None, None
    ort = sum(gecerli) / len(gecerli)
    yon = "RISK-ON" if ort > 0.3 else ("RISK-OFF" if ort < -0.3 else "NOTR")
    return yon, round(ort, 2)

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("asya", "avrupa", "amerika"):
        print("Kullanim: python fetch_kuresel.py [asya|avrupa|amerika]", file=sys.stderr)
        sys.exit(1)
    bolum = sys.argv[1]

    mevcut = {}
    if os.path.exists(DOSYA):
        try:
            with open(DOSYA, encoding="utf-8") as f:
                mevcut = json.load(f)
        except Exception:
            mevcut = {}

    if bolum == "asya":
        liste = bolum_isle(ASYA_ENDEKSLER, kapanmis_hesap)
    elif bolum == "avrupa":
        liste = bolum_isle(AVRUPA_ENDEKSLER, canli_hesap)
    else:
        liste = bolum_isle(AMERIKA_ENDEKSLER, canli_hesap)

    yon, ort = ozet(liste)
    tarihler = sorted({x.get("seans_tarihi") for x in liste if x.get("seans_tarihi") and "degisim_yuzde" in x})
    mevcut[bolum] = {
        "guncelleme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "seans_tarihleri": tarihler,
        "uyari": "bolumdeki bazi endeksler bugunun seansi degil" if any("uyari" in x for x in liste) else None,
        "endeksler": liste,
        "ozet_yon": yon,
        "ozet_ortalama_yuzde": ort,
    }
    # gunluk kok: her sabah asya kosarken ESKI GUNUN avrupa/amerika verisini temizle.
    # 23.11 (paket55, akşam denetimi 20.11): GitHub zamanlayicisi asya kosusunu ~9 saat geciktirip
    # aksam calistirdiginda AYNI GUNUN avrupa/amerika verisi de siliniyordu. Artik yalniz kaydin
    # UTC tarihi bugunden eskiyse silinir.
    if bolum == "asya":
        bugun = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        for k in ("avrupa", "amerika"):
            z = (mevcut.get(k) or {}).get("guncelleme_zamani_utc") or ""
            if z[:10] < bugun:
                mevcut.pop(k, None)

    os.makedirs("data", exist_ok=True)
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=2)
    print(f"[{bolum}] yazildi: {len([x for x in liste if 'degisim_yuzde' in x])}/{len(liste)} basarili, yon: {yon}")

if __name__ == "__main__":
    main()
