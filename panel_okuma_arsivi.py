"""
PANEL_OKUMA_ARSIVI (08.08.2026) - Faz V0
V151/V16x'in grafik-uzeri N/WR/PF/DD panelinin (f_v112Validation
ciktisi) ELLE okunan degerlerini zaman icinde KALICI olarak kaydeder.
arastirma_hedef_fiyat.py ile AYNI disiplin (kayit_ekle, tekrar onleme/
upsert, atomik yazma).

NEDEN GEREKLI: bu panel KUMULATIF (07.07'den beri biriken TUM
islemler) - kod duzeltmelerinin (P3_SKOR_AL esigi, POZ_AZALT mantigi,
v112n plot/atama, PF=0 hatasi) etkisini GORMEK icin, "duzeltme
ONCESI" bir BASLANGIC NOKTASI (baseline) sarttir - AKSI HALDE
karsilastirma YAPILAMAZ (bugun tam da bu sorunu yasadik, 05.08
verisi ilk basta KAYBOLMUS gorunuyordu).

Veri KAYNAGI: TradingView grafiginden ELLE okunup, buraya YAPILANDIRILMIS
olarak girilir - otomatik degil.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime

DOSYA = "data/panel_okuma_arsivi.json"


def _oku():
    try:
        with open(DOSYA, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"okumalar": []}


def okuma_ekle(tarih, sembol, n, wr_pct, pf, dd, pine_surumu, not_metni=""):
    """Tekrar onleme: (tarih, sembol) ciftiyle - ayni gun ayni sembol
    icin ikinci kez cagrilirsa GUNCELLENIR (upsert)."""
    veri = _oku()
    for k in veri["okumalar"]:
        if (k["tarih"], k["sembol"]) == (tarih, sembol):
            k.update({"n": n, "wr_pct": wr_pct, "pf": pf, "dd": dd,
                       "pine_surumu": pine_surumu, "not_metni": not_metni,
                       "son_guncelleme_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()})
            atomik_json_yaz(DOSYA, veri)
            return k
    kayit = {
        "tarih": tarih, "sembol": sembol, "n": n, "wr_pct": wr_pct,
        "pf": pf, "dd": dd, "pine_surumu": pine_surumu, "not_metni": not_metni,
        "eklenme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    veri["okumalar"].append(kayit)
    atomik_json_yaz(DOSYA, veri)
    return kayit


if __name__ == "__main__":
    # 05.08 BASELINE (v112n/P3/POZ_AZALT duzeltmelerinden ONCE, V157)
    # - kullanicinin 08.08'de PAYLASTIGI, gecmis bir oturumdan alinti
    baseline_veriler = [
        ("ASTOR", 2.0), ("EREGL", 1.9), ("ASELS", 1.7),
        ("KCHOL", 1.5), ("TRALT", 1.5), ("PETKM", 1.5), ("AKBNK", 1.5),
        ("TAVHL", 1.4), ("TUPRS", 1.4), ("HALKB", 1.4), ("PGSUS", 1.4),
        ("YKBNK", 1.2), ("BIMAS", 1.2), ("FROTO", 1.2),
        ("VAKBN", 1.1), ("SISE", 1.1), ("TRMET", 1.1), ("ENKAI", 1.1),
        ("OTKAR", 1.1), ("TOASO", 1.1),
        ("GARAN", 1.0), ("MGROS", 1.0), ("SAHOL", 1.0), ("ULKER", 1.0), ("DMLKT", 1.0),
        ("ALARK", 0.9), ("AEFES", 0.9),
        ("ENJSA", 0.8),
        ("TTKOM", 0.7),
    ]
    for sembol, pf in baseline_veriler:
        okuma_ekle("2026-08-05", sembol, n=None, wr_pct=None, pf=pf, dd=None,
                   pine_surumu="V157 (v112n/P3/POZ_AZALT duzeltmeleri ONCESI)",
                   not_metni="Yalniz PF biliniyor (siralama tablosundan) - N/WR/DD kaydedilmedi.")

    # 05.08 - N/WR/PF/DD TAM detayli olan 14 sembol (ayni gunden, farkli mesaj)
    tam_detayli_05 = [
        ("SAHOL", 176, 34, 1.0, 12.8), ("SISE", 108, 33, 1.1, 137.7),
        ("TRMET", 279, 38, 1.1, 23.3), ("FROTO", 142, 38, 1.2, 12.7),
        ("ULKER", 168, 33, 1.0, 46.2), ("TTKOM", 189, 26, 0.7, 48.8),
        ("ENJSA", 218, 38, 0.8, 35.6), ("ENKAI", 149, 36, 1.1, 16.8),
        ("DMLKT", 32, 16, 1.0, 5.0), ("PGSUS", 109, 38, 1.4, 13.7),
        ("ALARK", 179, 29, 0.9, 28.6), ("OTKAR", 163, 37, 1.1, 19.4),
        ("AEFES", 225, 38, 0.9, 39.0), ("TOASO", 187, 30, 1.1, 19.9),
    ]
    for sembol, n, wr, pf, dd in tam_detayli_05:
        okuma_ekle("2026-08-05", sembol, n=n, wr_pct=wr, pf=pf, dd=dd,
                   pine_surumu="V157 (v112n/P3/POZ_AZALT duzeltmeleri ONCESI)",
                   not_metni="Tam N/WR/PF/DD detayi mevcut.")

    # 08.08 YENI OKUMA (v112n/P3/POZ_AZALT/PF=0 duzeltmeleri SONRASI, V162)
    yeni_veriler = [
        ("THYAO", 24, 17, 0.5, 10.3),
        ("KCHOL", 150, 40, 1.4, 15.5),
        ("AKBNK", 80, 39, 1.5, 14.0),
    ]
    for sembol, n, wr, pf, dd in yeni_veriler:
        okuma_ekle("2026-08-08", sembol, n=n, wr_pct=wr, pf=pf, dd=dd,
                   pine_surumu="V162 (v112n+P3_esik+POZ_AZALT+PF=0 duzeltmeleri SONRASI)",
                   not_metni="Kullanici tarafindan grafikten okunup dogrulandi.")

    print("Kayitlar eklendi.")
