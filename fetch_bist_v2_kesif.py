"""
FETCH_BIST_V2_KESIF (06.08.2026) - Faz V0
BIST-ROS paketindeki fetch_bist.py fikrinin (merkezi config'den sembol
okuma + atomik yazma + bos-sonuc korumasi) IZOLE testi.

KIRMIZI CIZGI: update.yml'e (canli cron) HIC DOKUNMUYOR. Mevcut
data/bist_quotes.json'a HIC DOKUNMUYOR - AYRI bir dosyaya
(data/bist_quotes_v2_deneme.json) yazar. Katı sema dogrulamasi
("additionalProperties: False") KULLANILMIYOR - kurul bunu riskli
buldu (bkz. REJIM_KALIBRASYON_PROMPTU.md Bolum 7).

Amac: "config/universe.yml'den sembol okumak, gercekte calisiyor mu"
sorusuna GERCEK yfinance veriyle cevap vermek - canli sistemi hic
riske atmadan.
"""
import datetime
import json
import sys

import yfinance as yf

from konfig_yukle import sembol_evreni_yukle, tatil_gunleri_yukle
from json_atomik_yaz import atomik_json_yaz

CIKTI = "data/bist_quotes_v2_deneme.json"


def fetch_one(sembol, sonek, yedekler):
    denenecekler = [sembol] + ([yedekler[sembol]] if sembol in yedekler else [])
    for kod in denenecekler:
        ticker_id = f"{kod}{sonek}"
        try:
            t = yf.Ticker(ticker_id)
            hist, kaynak_tip = None, "15m"
            try:
                h15 = t.history(period="1d", interval="15m")
                if not h15.empty:
                    hist = h15
            except Exception as e:
                print(f"UYARI: {sembol} 15m ucu hata verdi ({e}), gunluge dusuluyor",
                      file=sys.stderr)
            if hist is None:
                hg = t.history(period="5d", interval="1d")
                if hg.empty:
                    print(f"UYARI: {sembol} icin {ticker_id} iki ucta da bos", file=sys.stderr)
                    continue
                hist, kaynak_tip = hg, "gunluk-yedek"
            son = hist.iloc[-1]
            return {
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
    semboller, sonek, yedekler = sembol_evreni_yukle()
    tatiller = tatil_gunleri_yukle()
    bugun = datetime.datetime.now(datetime.timezone.utc).date()
    if bugun in tatiller:
        print(f"BIST tatili ({bugun}) - kesif atlandi.")
        return

    sonuclar = []
    for sembol in semboller:
        veri = fetch_one(sembol, sonek, yedekler)
        if veri is not None:
            sonuclar.append(veri)

    if not sonuclar:
        print("HATA: 0 sembol cekildi - kesif dosyasi yazilmadi.", file=sys.stderr)
        sys.exit(1)

    cikti = {
        "schema_version": "kesif-v2",
        "guncelleme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": "IZOLE KESIF - canli data/bist_quotes.json'dan BAGIMSIZ, karsilastirma icin.",
        "toplam_sembol": len(semboller),
        "basarili_cekim": len(sonuclar),
        "veriler": sonuclar,
    }
    atomik_json_yaz(CIKTI, cikti)
    print(f"Tamamlandi: {len(sonuclar)}/{len(semboller)} sembol basariyla cekildi -> {CIKTI}")


if __name__ == "__main__":
    main()
