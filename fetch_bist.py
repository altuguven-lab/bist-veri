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

# v3 (16.07.2026 ogleden sonra): 15dk intraday ucu bosalirsa GUNLUK uca
# dusen yedek mod eklendi (16.07 vakasi: ayni ortamda gunluk uc calisirken
# 15m ucu 0/30 dondu - kirilan yfinance degil Yahoo intraday ucuydu).
# Kayitlarda "kaynak_tip": "15m" | "gunluk-yedek" alani eklendi.
# v2 (16.07.2026): (a) BIST tatil gunlerinde cekim yapilmaz (bos veri
# uretmemek icin), (b) BOS SONUC KORUMASI - hic sembol cekilemezse mevcut
# dosyalarin UZERINE YAZILMAZ (15.07 vakasi: tatil kosusu 0/30 donup
# Pazartesi kapanis setini sildi). Liste saglik_kontrol.py ile es tutulur.
TATIL_GUNLERI = {
    "2026-07-15",  # Demokrasi ve Milli Birlik Gunu
    "2026-08-30",  # Zafer Bayrami
    "2026-10-29",  # Cumhuriyet Bayrami
    "2027-01-01",  # Yilbasi
}

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
    """Tek sembolun verisini ceker. v3: once 15dk gun ici denenir; Yahoo
    intraday ucu bos/ariza donerse GUNLUK uca duser (son fiyat + gun OHLC
    gunlukten gelir, 15dk serisi o kosuda bos kalir). Hata olursa None doner
    (script tamamini durdurmaz, tek sembolu atlar)."""
    denenecekler = [sembol] + ([ESKI_KOD_YEDEK[sembol]] if sembol in ESKI_KOD_YEDEK else [])
    for kod in denenecekler:
        ticker_id = f"{kod}.IS"
        try:
            t = yf.Ticker(ticker_id)
            # 1) Tercih: 15dk gun ici
            hist, kaynak_tip = None, "15m"
            try:
                h15 = t.history(period="1d", interval="15m")
                if not h15.empty:
                    hist = h15
            except Exception as e:
                print(f"UYARI: {sembol} 15m ucu hata verdi ({e}), gunluge dusuluyor",
                      file=sys.stderr)
            # 2) Yedek: gunluk uc (son 5 gun, en taze satir)
            if hist is None:
                hg = t.history(period="5d", interval="1d")
                if hg.empty:
                    print(f"UYARI: {sembol} icin {ticker_id} iki ucta da bos",
                          file=sys.stderr)
                    continue
                hist, kaynak_tip = hg, "gunluk-yedek"
            son = hist.iloc[-1]
            seri = []
            if kaynak_tip == "15m":
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
                "kaynak_tip": kaynak_tip,
            }
        except Exception as e:
            print(f"HATA: {sembol} ({ticker_id}) cekilemedi -> {e}", file=sys.stderr)
    return None


def main():
    bugun = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    if bugun in TATIL_GUNLERI:
        print(f"BIST tatili ({bugun}) - cekim atlandi, dosyalara dokunulmadi.")
        return

    sonuclar = []
    gun_ici = {}
    for sembol in BIST_SEMBOLLER:
        veri = fetch_one(sembol)
        if veri is not None:
            gun_ici[sembol] = veri.pop("_gun_ici_seri", [])
            sonuclar.append(veri)

    if not sonuclar:
        # BOS SONUC KORUMASI: son saglam veri setini ezme, kosuyu kirmizi bitir
        # (saglik_kontrol seans icinde bayatlamayi zaten yakalar).
        print("HATA: 0 sembol cekildi - mevcut dosyalar KORUNDU, yazilmadi.",
              file=sys.stderr)
        sys.exit(1)

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
