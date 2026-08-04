"""
KESIF: BIST sektor endeksleri yfinance destekliyor mu? (04.08.2026)
Varsayimla ilerlemek yerine birkac olasi sembol formatini dener,
hangisi (varsa) gercek veri dondurdugunu raporlar. Sonuc, vekil
(proxy) hesaplama mi yoksa dogrudan endeks cekimi mi kuracagimizi
belirleyecek.
"""
import json, datetime, sys
import yfinance as yf

# Test edilecek endeksler ve olasi sembol varyasyonlari
ENDEKSLER = {
    "XBANK (Banka)": ["XBANK.IS", "^XBANK", "XBANK", "XBANK.IST"],
    "XHOLD (Holding)": ["XHOLD.IS", "^XHOLD", "XHOLD"],
    "XULAS (Ulastirma)": ["XULAS.IS", "^XULAS", "XULAS"],
    "XUSIN (Sinai)": ["XUSIN.IS", "^XUSIN", "XUSIN"],
    "XU100 (referans - bilinen calisir)": ["XU100.IS", "^XU100"],
}

CIKTI = "data/kesif/kesif_sektor_endeks.json"


def dene(kod):
    try:
        df = yf.Ticker(kod).history(period="5d")
        if len(df) >= 1:
            son = float(df["Close"].iloc[-1])
            return {"basarili": True, "satir_sayisi": len(df), "son_kapanis": son}
        return {"basarili": False, "hata": "0 satir donduruldu"}
    except Exception as e:
        return {"basarili": False, "hata": str(e)}


def main():
    sonuc = {"kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "sonuclar": {}}
    for isim, adaylar in ENDEKSLER.items():
        sonuc["sonuclar"][isim] = {}
        for kod in adaylar:
            r = dene(kod)
            sonuc["sonuclar"][isim][kod] = r
            durum = "BASARILI" if r["basarili"] else f"basarisiz ({r.get('hata','?')[:60]})"
            print(f"{isim} | {kod} -> {durum}")

    import os
    os.makedirs("data/kesif", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"\nYazildi: {CIKTI}")


if __name__ == "__main__":
    main()
