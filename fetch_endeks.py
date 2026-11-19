"""
FETCH_ENDEKS (19.11.2026) - SALT VERI, TAVSIYE DEGILDIR.

Neden: 19.11 ogle brifinginde "BIST 100 ogle seviyesi: kaynak bulunamadi" yazildi. Depoda 32 hissenin
15dk barlari vardi (data/bist_intraday.json) ama endeks ve kur yoktu. Bu betik endeksleri, kuru ve
birkac kuresel gostergeyi ayni 15dk duzeninde ceker; brifing bu dosyadan "depo verisi" olarak okur.

Kaynak: Yahoo Finance (yfinance) - birkac dakika gecikmeli, ANLIK DEGIL. Brifingde "veri akisi (Yahoo,
gecikmeli)" diye yazilir; resmi kapanis icin borsaistanbul.com / TCMB esastir.

Cikti: data/endeks_intraday.json  {guncelleme_zamani_utc, kaynak, gostergeler: {AD: {kod, son, onceki_kapanis,
        degisim_yuzde, gun_yuksek, gun_dusuk, bar_zamani, seri:[{t,k}] }}}
Bos sonuc korumasi: hicbir gosterge cekilemezse mevcut dosya ezilmez.
fetch_bist.py'den AYRI tutuldu: bist_quotes.json'i okuyan betikler (karne, saglik vb.) etkilenmesin.
"""
import datetime
import sys

import yfinance as yf

from json_atomik_yaz import atomik_json_yaz

GOSTERGELER = {
    # ad: (yahoo kodu, yedek kod)
    "XU100": ("XU100.IS", None),
    "XU030": ("XU030.IS", None),
    "XBANK": ("XBANK.IS", None),
    "XHOLD": ("XHOLD.IS", None),
    "XUSIN": ("XUSIN.IS", None),
    "USDTRY": ("USDTRY=X", "TRY=X"),
    "EURTRY": ("EURTRY=X", None),
    "BRENT": ("BZ=F", None),
    "SP500_VADELI": ("ES=F", None),
    "NASDAQ_VADELI": ("NQ=F", None),
    "ABD_10Y": ("^TNX", None),
    "DOLAR_ENDEKSI": ("DX-Y.NYB", None),
    "ONS_ALTIN": ("GC=F", None),
}


def cek(ad, kod, yedek):
    for k in [kod] + ([yedek] if yedek else []):
        try:
            t = yf.Ticker(k)
            h = t.history(period="1d", interval="15m")
            g = t.history(period="5d", interval="1d")
            if h.empty and g.empty:
                continue
            kaynak = h if not h.empty else g
            son = float(kaynak["Close"].iloc[-1])
            onceki = None
            if len(g) >= 2:
                # gunluk serinin son satiri bugun ise bir onceki kapanis, degilse son satir
                bugun = datetime.datetime.utcnow().date()
                son_gun = g.index[-1].date()
                onceki = float(g["Close"].iloc[-2] if son_gun >= bugun else g["Close"].iloc[-1])
            return {
                "kod": k,
                "son": round(son, 4),
                "onceki_kapanis": round(onceki, 4) if onceki else None,
                "degisim_yuzde": round((son / onceki - 1) * 100, 2) if onceki else None,
                "gun_yuksek": round(float(kaynak["High"].max()), 4),
                "gun_dusuk": round(float(kaynak["Low"].min()), 4),
                "bar_zamani": str(kaynak.index[-1]),
                "kaynak_tip": "15m" if not h.empty else "gunluk-yedek",
                "seri": [{"t": str(ix), "k": round(float(r["Close"]), 4)} for ix, r in h.iterrows()] if not h.empty else [],
            }
        except Exception as e:
            print(f"UYARI: {ad} ({k}) cekilemedi: {e}", file=sys.stderr)
    return None


def main():
    sonuc = {}
    for ad, (kod, yedek) in GOSTERGELER.items():
        v = cek(ad, kod, yedek)
        if v:
            sonuc[ad] = v
        else:
            print(f"UYARI: {ad} bos", file=sys.stderr)
    if not sonuc:
        print("HATA: hicbir gosterge cekilemedi - mevcut dosya korundu.", file=sys.stderr)
        sys.exit(1)
    atomik_json_yaz("data/endeks_intraday.json", {
        "guncelleme_zamani_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "kaynak": "Yahoo Finance (yfinance) - birkac dakika gecikmeli, ANLIK DEGIL. Resmi kapanis icin borsaistanbul.com/TCMB esastir.",
        "eksik": [a for a in GOSTERGELER if a not in sonuc],
        "gostergeler": sonuc,
    })
    print(f"Tamamlandi: {len(sonuc)}/{len(GOSTERGELER)} gosterge. Eksik: {[a for a in GOSTERGELER if a not in sonuc]}")


if __name__ == "__main__":
    main()
