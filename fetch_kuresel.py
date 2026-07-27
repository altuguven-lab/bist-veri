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
import json, datetime, sys, os
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

def kapanmis_hesap(kod):
    """Asya tipi: onceki iki GUNLUK kapanisi kiyaslar (kendi seansi bitmis)."""
    df = yf.Ticker(kod).history(period="5d")
    if len(df) < 2:
        return None, "yetersiz veri"
    son, onceki = float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    return round((son / onceki - 1) * 100, 2), None

def canli_hesap(kod):
    """Avrupa/ABD tipi: BUGUNKU ilk 5dk bar vs en son bar (kendi acilisina
    gore) - onceki gunun kapanisiyla degil, kendi gun-ici hareketiyle olcer."""
    df = yf.Ticker(kod).history(period="1d", interval="5m")
    if len(df) < 2:
        return None, "henuz veri yok (seans acilmamis olabilir)"
    ilk, son = float(df["Close"].iloc[0]), float(df["Close"].iloc[-1])
    return round((son / ilk - 1) * 100, 2), None

def bolum_isle(liste, hesap_fn):
    sonuc = []
    for isim, kod, bolge in liste:
        try:
            degisim, hata = hesap_fn(kod)
            kayit = {"isim": isim, "kod": kod, "bolge": bolge}
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
    mevcut[bolum] = {
        "guncelleme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "endeksler": liste,
        "ozet_yon": yon,
        "ozet_ortalama_yuzde": ort,
    }
    # gunluk kok: her sabah asya kosarken eski gunun avrupa/amerika verisini temizle
    if bolum == "asya":
        for k in ("avrupa", "amerika"):
            mevcut.pop(k, None)

    os.makedirs("data", exist_ok=True)
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=2)
    print(f"[{bolum}] yazildi: {len([x for x in liste if 'degisim_yuzde' in x])}/{len(liste)} basarili, yon: {yon}")

if __name__ == "__main__":
    main()
