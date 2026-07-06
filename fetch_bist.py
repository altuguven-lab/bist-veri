"""
BIST verisini Yahoo Finance uzerinden ceker ve data/bist_quotes.json dosyasina yazar.
GitHub Actions tarafindan periyodik olarak calistirilir (bkz. .github/workflows/update.yml).

NOT: Yahoo Finance BIST verisi genelde birkac dakika gecikmelidir, gercek anlik
(tick-by-tick) veri DEGILDIR. Gercek anlik veri icin lisansli bir veri saglayicisi
(Matriks, Foreks, aracı kurum API'si) gerekir.
"""
import yfinance as yf
import json
import datetime
import sys

# V195 CTRL KURUMSAL'daki 30 sembol listesiyle birebir ayni - istersen
# kendi listeni buraya uyarlayabilirsin. Yahoo Finance'de BIST hisseleri
# ".IS" sonekiyle yazilir (orn. AKBNK -> AKBNK.IS).
BIST_SEMBOLLER = [
    "AKBNK", "YKBNK", "GARAN", "ISCTR", "SAHOL", "KCHOL", "THYAO", "TAVHL",
    "EREGL", "ASELS", "ASTOR", "MGROS", "BIMAS", "TUPRS", "TOASO", "FROTO",
    "ENKAI", "TTKOM", "AEFES", "PGSUS", "HALKB", "VAKBN", "SASA", "PETKM",
    "SISE", "EKGYO", "KOZAL", "ALARK", "DOAS", "ULKER",
]

def fetch_one(sembol):
    """Tek bir sembolun son fiyat/hacim verisini ceker. Hata olursa None doner
    (script tamamini durdurmaz, tek sembolu atlar)."""
    ticker_id = f"{sembol}.IS"
    try:
        t = yf.Ticker(ticker_id)
        hist = t.history(period="1d", interval="15m")
        if hist.empty:
            print(f"UYARI: {sembol} icin veri bos donuyor", file=sys.stderr)
            return None
        son = hist.iloc[-1]
        return {
            "sembol": sembol,
            "son_fiyat": round(float(son["Close"]), 4),
            "acilis": round(float(son["Open"]), 4),
            "yuksek": round(float(son["High"]), 4),
            "dusuk": round(float(son["Low"]), 4),
            "hacim": int(son["Volume"]),
            "bar_zamani": str(hist.index[-1]),
        }
    except Exception as e:
        print(f"HATA: {sembol} cekilemedi -> {e}", file=sys.stderr)
        return None


def main():
    sonuclar = []
    for sembol in BIST_SEMBOLLER:
        veri = fetch_one(sembol)
        if veri is not None:
            sonuclar.append(veri)

    cikti = {
        "guncelleme_zamani_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "kaynak": "Yahoo Finance (yfinance) - birkac dakika gecikmeli, ANLIK DEGIL",
        "toplam_sembol": len(BIST_SEMBOLLER),
        "basarili_cekim": len(sonuclar),
        "veriler": sonuclar,
    }

    with open("data/bist_quotes.json", "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    print(f"Tamamlandi: {len(sonuclar)}/{len(BIST_SEMBOLLER)} sembol basariyla cekildi.")


if __name__ == "__main__":
    main()
