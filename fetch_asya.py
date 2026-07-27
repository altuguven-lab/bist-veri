"""
ASYA ONCU GOSTERGE (27.07.2026, ALTYAPI): BIST acilisindan (10:00 TSI)
once, Asya/kuresel endekslerin bir onceki kapanis yuzde degisimini ceker.
Amac: "bugun risk istahı nasil" sorusuna haber yorumlamadan, dogrudan
sayidan cevap - THYAO +%4.25 gibi hareketlerin makro baglamini
brifing/analiz oncesi hazir tutmak icin.

Kapsam BILINCLI DAR tutuldu: yalniz endeks seviyeleri, hicbir V151/
skor/sinyal mantigina dokunmuyor - saf veri toplama.
"""
import json, datetime, sys
import yfinance as yf

ENDEKSLER = [
    ("Nikkei 225",      "^N225",  "Japonya"),
    ("Kospi",           "^KS11",  "G.Kore"),
    ("Sanghay Bilesik", "000001.SS", "Cin"),
    ("Hang Seng",       "^HSI",   "H.Kong"),
    ("S&P 500 Vadeli",  "ES=F",   "ABD"),
    ("Brent Petrol",    "BZ=F",   "Emtia"),
]

def main():
    sonuc = []
    for isim, kod, bolge in ENDEKSLER:
        try:
            df = yf.Ticker(kod).history(period="5d")
            if len(df) < 2:
                sonuc.append({"isim": isim, "kod": kod, "bolge": bolge,
                              "hata": "yetersiz veri"})
                continue
            son = float(df["Close"].iloc[-1])
            onceki = float(df["Close"].iloc[-2])
            degisim = (son / onceki - 1) * 100
            sonuc.append({
                "isim": isim, "kod": kod, "bolge": bolge,
                "kapanis": round(son, 2),
                "degisim_yuzde": round(degisim, 2),
                "tarih": str(df.index[-1].date()),
            })
        except Exception as e:
            sonuc.append({"isim": isim, "kod": kod, "bolge": bolge,
                          "hata": str(e)})
            print(f"UYARI: {isim} ({kod}) cekilemedi: {e}", file=sys.stderr)

    gecerli = [s for s in sonuc if "degisim_yuzde" in s]
    ozet_yon = None
    if gecerli:
        ort = sum(s["degisim_yuzde"] for s in gecerli) / len(gecerli)
        ozet_yon = "RISK-ON" if ort > 0.3 else ("RISK-OFF" if ort < -0.3 else "NOTR")

    dosya = {
        "guncelleme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "endeksler": sonuc,
        "ozet_yon": ozet_yon,
        "ozet_ortalama_yuzde": round(sum(s["degisim_yuzde"] for s in gecerli) / len(gecerli), 2) if gecerli else None,
    }
    with open("data/asya_oncu.json", "w", encoding="utf-8") as f:
        json.dump(dosya, f, ensure_ascii=False, indent=2)
    print(f"Yazildi: {len(gecerli)}/{len(ENDEKSLER)} endeks basarili, yon: {ozet_yon}")

if __name__ == "__main__":
    main()
