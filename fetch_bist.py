"""
BIST verisini Yahoo Finance uzerinden ceker ve data/bist_quotes.json dosyasina yazar.
GitHub Actions tarafindan periyodik olarak calistirilir (bkz. .github/workflows/update.yml).

NOT: Yahoo Finance BIST verisi genelde birkac dakika gecikmelidir, gercek anlik
(tick-by-tick) veri DEGILDIR. Gercek anlik veri icin lisansli bir veri saglayicisi
(Matriks, Foreks, araci kurum API'si) gerekir.
"""

import yfinance as yf
import json
import datetime
import sys

# V195 CTRL KURUMSAL'daki 30 sembol listesiyle birebir ayni - istersen
# kendi listeni buraya uyarlayabilirsin. Yahoo Finance'de BIST hisseleri
# ".IS" sonekiyle yazilir (orn. AKBNK -> AKBNK.IS).
# EVREN REV. 07.07.2026: SASA->OTKAR, KOZAL->TRMET, DOAS->ENJSA
BIST_SEMBOLLER = [
    "AKBNK", "YKBNK", "GARAN", "ISCTR", "SAHOL", "KCHOL", "THYAO", "TAVHL",
    "EREGL", "ASELS", "ASTOR", "MGROS", "BIMAS", "TUPRS", "TOASO", "FROTO",
    "ENKAI", "TTKOM", "AEFES", "PGSUS", "HALKB", "VAKBN", "OTKAR", "PETKM",
    "SISE", "EKGYO", "TRMET", "ALARK", "ENJSA", "ULKER",
]

# Kod/unvan degisikligi gecis donemi: birincil kod bos donerse denenecek
# eski kod (Yahoo bazen veriyi eski ticker altinda tutmaya devam eder).
ESKI_KOD_YEDEK = {
    "TRMET": "KOZAA",  # TR Anadolu Metal = eski Koza Anadolu Metal
}


def fetch_one(sembol):
    """Tek bir sembolun son fiyat/hacim verisini ceker. Hata olursa None doner
    (script tamamini durdurmaz, tek sembolu atlar)."""
    denenecekler = [sembol] + ([ESKI_KOD_YEDEK[sembol]] if sembol in ESKI_KOD_YEDEK else [])
    for kod in denenecekler:
        ticker_id = f"{kod}.IS"
        try:
            t = yf.Ticker(ticker_id)
            hist = t.history(period="1d", interval="15m")
            if hist.empty:
                print(f"UYARI: {sembol} icin {ticker_id} bos donuyor", file=sys.stderr)
                continue
            son = hist.iloc[-1]
            seri = [
                {"t": str(ix), "a": round(float(r["Open"]), 4), "y": round(float(r["High"]), 4),
                 "d": round(float(r["Low"]), 4), "k": round(float(r["Close"]), 4), "h": int(r["Volume"])}
                for ix, r in hist.iterrows()
            ]
            return {
                "_gun_ici_seri": seri,
                "sembol": sembol,
                "son_fiyat": round(float(son["Close"]), 4),
                "acilis": round(float(son["Open"]), 4),
                "yuksek": round(float(son["High"]), 4),
                "dusuk": round(float(son["Low"]), 4),
                "hacim": int(son["Volume"]),
                "bar_zamani": str(hist.index[-1]),
                "veri_kodu": kod,
            }
        except Exception as e:
            print(f"HATA: {sembol} ({ticker_id}) cekilemedi -> {e}", file=sys.stderr)
    return None


def main():
    sonuclar = []
    gun_ici = {}
    for sembol in BIST_SEMBOLLER:
        veri = fetch_one(sembol)
        if veri is not None:
            gun_ici[sembol] = veri.pop("_gun_ici_seri", [])
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

    # Gun ici 15dk serisi (Claude'un gun ici analizi icin; her kosumda yeniden yazilir)
    with open("data/bist_intraday.json", "w", encoding="utf-8") as f:
        json.dump({
            "guncelleme_zamani_utc": cikti["guncelleme_zamani_utc"],
            "aciklama": "Bugunun 15dk barlari. a=acilis y=yuksek d=dusuk k=kapanis h=hacim",
            "seriler": gun_ici,
        }, f, ensure_ascii=False, indent=2)

    print(f"Tamamlandi: {len(sonuclar)}/{len(BIST_SEMBOLLER)} sembol basariyla cekildi.")


if __name__ == "__main__":
    main()
