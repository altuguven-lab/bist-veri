"""
RSI vs XU100 BENCHMARK KIYASLAMASI (07.08.2026) - Faz V0
Kritik soru: RSI asiri-satim stratejisi GERCEK bir alpha mi uretiyor,
yoksa son 5 yilda BIST zaten GENEL OLARAK yukseldigi icin mi her sey
pozitif cikiyor? Bu script, HER RSI islemi icin, AYNI giris->cikis
tarih araliginda XU100'un (basit al-tut) ne kazandiracagini hesaplayip,
ISLEM-BAZLI, birebir eslesen bir kiyaslama yapar (apples-to-apples -
farkli donemlerin karistirilmasi riski yok).

SALT OLCUM - rsi_asiri_satim_swing_sonuc.json'daki (orijinal, tarihli)
276 islemi okur, XU100 GERCEK gunluk verisiyle kiyaslar.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime
import yfinance as yf

GIRIS_YOL = "data/backtest/rsi_asiri_satim_swing_sonuc.json"
CIKTI = "data/backtest/rsi_vs_xu100_kiyas_sonuc.json"
XU100_TICKER = "XU100.IS"


def xu100_serisi_cek():
    df = yf.Ticker(XU100_TICKER).history(period="5y", interval="1d")
    if df.empty:
        raise RuntimeError(f"{XU100_TICKER} icin veri cekilemedi")
    return [(idx.date(), float(v)) for idx, v in df["Close"].items()]


def en_yakin_kapanis(seri, hedef_tarih, sonraki_mi):
    """hedef_tarih'e ESIT ya da (sonraki_mi=True ise) SONRAKI, (False
    ise) ONCEKI en yakin islem gununun kapanisini bulur - tatil/hafta
    sonu tarihleri XU100 serisinde olmayabilir."""
    if sonraki_mi:
        adaylar = [(t, c) for t, c in seri if t >= hedef_tarih]
        return min(adaylar, key=lambda x: x[0])[1] if adaylar else None
    else:
        adaylar = [(t, c) for t, c in seri if t <= hedef_tarih]
        return max(adaylar, key=lambda x: x[0])[1] if adaylar else None


def main():
    rsi_veri = json.load(open(GIRIS_YOL, encoding="utf-8"))
    islemler = rsi_veri["islem_detaylari"]
    xu100 = xu100_serisi_cek()
    print(f"XU100 veri noktasi sayisi: {len(xu100)}")

    eslesmeler = []
    for t in islemler:
        giris_tarih = datetime.date.fromisoformat(t["giris_tarih"])
        cikis_tarih = datetime.date.fromisoformat(t["cikis_tarih"])
        xu_giris = en_yakin_kapanis(xu100, giris_tarih, sonraki_mi=True)
        xu_cikis = en_yakin_kapanis(xu100, cikis_tarih, sonraki_mi=False)
        if xu_giris is None or xu_cikis is None or xu_giris <= 0:
            continue
        xu100_getiri_pct = round((xu_cikis / xu_giris - 1) * 100, 3)
        eslesmeler.append({
            "sembol": t["sembol"], "giris_tarih": t["giris_tarih"], "cikis_tarih": t["cikis_tarih"],
            "rsi_net_getiri_pct": t["net_getiri_pct"],
            "xu100_ayni_donem_getiri_pct": xu100_getiri_pct,
            "fark_pct": round(t["net_getiri_pct"] - xu100_getiri_pct, 3),
        })

    if not eslesmeler:
        print("HATA: hic eslesme uretilemedi")
        return

    rsi_ort = sum(e["rsi_net_getiri_pct"] for e in eslesmeler) / len(eslesmeler)
    xu100_ort = sum(e["xu100_ayni_donem_getiri_pct"] for e in eslesmeler) / len(eslesmeler)
    fark_ort = sum(e["fark_pct"] for e in eslesmeler) / len(eslesmeler)
    rsi_ustun_sayisi = sum(1 for e in eslesmeler if e["fark_pct"] > 0)

    sonuc = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Faz V0 - RSI stratejisi vs XU100 basit al-tut, ISLEM-BAZLI "
                "eslestirilmis (her RSI isleminin giris->cikis araliginda "
                "XU100 ne kazandirirdi). SALT OLCUM."),
        "eslesen_islem_sayisi": len(eslesmeler),
        "rsi_ortalama_getiri_pct": round(rsi_ort, 3),
        "xu100_ayni_donemler_ortalama_getiri_pct": round(xu100_ort, 3),
        "ortalama_fark_pct": round(fark_ort, 3),
        "rsi_ustun_oldugu_islem_sayisi": rsi_ustun_sayisi,
        "rsi_ustun_oldugu_yuzde": round(100 * rsi_ustun_sayisi / len(eslesmeler), 1),
        "detaylar": eslesmeler,
    }
    atomik_json_yaz(CIKTI, sonuc)
    print(f"\nYazildi: {CIKTI}")
    print(f"RSI ortalama: %{rsi_ort:.3f} | XU100 (ayni donemler) ortalama: %{xu100_ort:.3f}")
    print(f"Ortalama fark (RSI - XU100): %{fark_ort:.3f}")
    print(f"RSI, islemlerin %{sonuc['rsi_ustun_oldugu_yuzde']}'inde XU100'u gecti")


if __name__ == "__main__":
    main()
