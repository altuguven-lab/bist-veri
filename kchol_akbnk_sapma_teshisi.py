"""
KCHOL_AKBNK_SAPMA_TESHISI (10.08.2026) - Faz V0
pine_python_capraz_dogrulama.py'de KCHOL/AKBNK'nin (2000'e kadar giden,
EN UZUN gecmisli iki sembol) diger sembollerden COK DAHA BUYUK sapma
gostermesi uzerine - hipotez: DUZELTILMEMIS sermaye artirimi/bolunme
(split) verisi, YAPAY fiyat cokuslerine yol acip sahte stop-tetikleme/
DD yaratiyor olabilir.

BU SCRIPT: (1) yfinance'in KAYITLI split gecmisini yazdirir, (2) fiyat
serisinde TEK GUNLUK asiri (>%25) sicramalari (YUKARI ya da ASAGI)
TARAR - bunlar DUZELTILMEMIS split/bolunme olaylarinin IZI olabilir.

KIRMIZI CIZGI: SALT TESHIS, Pine'a hic dokunmuyor.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import yfinance as yf

ESIK_YUZDE = 25.0


def main():
    sonuclar = {}
    for sembol in ["KCHOL", "AKBNK", "TTKOM"]:
        ticker = yf.Ticker(f"{sembol}.IS")
        try:
            df = ticker.history(period="max", interval="1d")
        except Exception as e:
            print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
            continue

        try:
            splits = ticker.splits
            split_listesi = [{"tarih": str(t.date()), "oran": float(v)} for t, v in splits.items()]
        except Exception as e:
            split_listesi = []
            print(f"UYARI: {sembol} split verisi cekilemedi -> {e}", file=sys.stderr)

        supheli_sicramalar = []
        kapanis = df["Close"]
        for i in range(1, len(df)):
            onceki = float(kapanis.iloc[i-1])
            simdi = float(kapanis.iloc[i])
            if onceki <= 0:
                continue
            degisim_pct = (simdi / onceki - 1) * 100
            if abs(degisim_pct) >= ESIK_YUZDE:
                supheli_sicramalar.append({"tarih": str(df.index[i].date()),
                                             "onceki_kapanis": round(onceki, 2),
                                             "yeni_kapanis": round(simdi, 2),
                                             "degisim_pct": round(degisim_pct, 1)})

        sonuclar[sembol] = {
            "veri_baslangic": str(df.index[0].date()), "veri_bitis": str(df.index[-1].date()),
            "kayitli_split_sayisi": len(split_listesi), "split_listesi": split_listesi,
            "supheli_sicrama_sayisi": len(supheli_sicramalar),
            "supheli_sicramalar": supheli_sicramalar,
        }
        print(f"\n{sembol}: {len(split_listesi)} kayitli split, {len(supheli_sicramalar)} supheli sicrama (>%{ESIK_YUZDE})")
        for s in split_listesi[:10]:
            print(f"   SPLIT: {s['tarih']} oran={s['oran']}")
        for s in supheli_sicramalar[:10]:
            print(f"   SICRAMA: {s['tarih']} {s['onceki_kapanis']}->{s['yeni_kapanis']} (%{s['degisim_pct']:+.1f})")

    rapor = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("KCHOL/AKBNK'nin pine_python_capraz_dogrulama.py'de gosterdigi "
                "buyuk sapmanin (PF/DD) KAYNAGINI arastirir - hipotez: "
                "duzeltilmemis split/bolunme verisi YAPAY fiyat cokusleri "
                "yaratip sahte stop-tetiklemeleri/DD olusturuyor olabilir. "
                "TTKOM referans olarak eklendi (makul cikan sembol)."),
        "esik_yuzde": ESIK_YUZDE,
        "semboller": sonuclar,
    }
    atomik_json_yaz("data/backtest/kchol_akbnk_sapma_teshisi_sonuc.json", rapor)
    print(f"\nYazildi: data/backtest/kchol_akbnk_sapma_teshisi_sonuc.json")


if __name__ == "__main__":
    main()
