"""
KAZANC_REVERSAL_IZLEME (10.08.2026) - Faz V0
kazanc_surprizi_reversal.py'nin ("GERI_CEKILME_ADAYI_GUCLU"/
"_TEMKINLI" etiketli) adaylarini KALICI bir arsive ekleyip, YETERLI
zaman gectikten sonra (10 is gunu - ayni PEAD pencere mantigi)
GERCEK fiyat hareketiyle "GERCEKTEN toparlandi mi" diye dogrular.
sinyal_arsiv_gunluk.py ile AYNI disiplin (biriktir + gecikmeli
dogrula + tip-bazinda ozet).

KIRMIZI CIZGI: SALT OLCUM, hicbir gercek islem/uyari uretmez. Bu,
kazanc_surprizi_reversal.py'nin GERCEK ongoru gucunu ZAMAN icinde
degerlendirmemizi saglayan tek yol - ONCEDEN VARSAYMAK yerine.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime
import yfinance as yf

ARSIV_YOL = "data/kazanc_reversal_izleme.json"
IZLEME_GUN_SAYISI = 10


def _oku_arsiv():
    try:
        with open(ARSIV_YOL, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"kayitlar": []}


def _en_yakin_kapanis(seri, hedef_tarih):
    adaylar = [(t, c) for t, c in seri if t >= hedef_tarih]
    return min(adaylar, key=lambda x: x[0])[1] if adaylar else None


def main():
    arsiv = _oku_arsiv()
    mevcut_anahtarlar = {(k["sembol"], k["kar_surprizi_tarihi"]) for k in arsiv["kayitlar"]}

    kaynak = json.load(open("data/kazanc_surprizi_reversal.json", encoding="utf-8"))
    yeni_sayisi = 0
    for s in kaynak.get("sonuclar", []):
        if s["etiket"] not in ("GERI_CEKILME_ADAYI_GUCLU", "GERI_CEKILME_ADAYI_TEMKINLI"):
            continue
        anahtar = (s["sembol"], s["kar_surprizi_tarihi"])
        if anahtar in mevcut_anahtarlar:
            continue
        arsiv["kayitlar"].append({
            "sembol": s["sembol"], "sektor": s["sektor"],
            "kar_surprizi_tarihi": s["kar_surprizi_tarihi"],
            "etiket_tarihi": str(datetime.datetime.now(datetime.timezone.utc).date()),
            "etiket": s["etiket"],
            "isaretlenme_ani_fiyat": s["son_fiyat"],
            "isaretlenme_ani_zirveden_geri_cekilme_pct": s["zirveden_geri_cekilme_pct"],
            "durum": "IZLENIYOR",
        })
        mevcut_anahtarlar.add(anahtar)
        yeni_sayisi += 1
    print(f"{yeni_sayisi} yeni aday arsive eklendi")

    bugun = datetime.datetime.now(datetime.timezone.utc).date()
    fiyat_serileri = {}
    sonuclanan_sayisi = 0
    for kayit in arsiv["kayitlar"]:
        if kayit["durum"] != "IZLENIYOR":
            continue
        etiket_tarih = datetime.date.fromisoformat(kayit["etiket_tarihi"])
        if (bugun - etiket_tarih).days < IZLEME_GUN_SAYISI:
            continue

        sembol = kayit["sembol"]
        if sembol not in fiyat_serileri:
            try:
                df = yf.Ticker(f"{sembol}.IS").history(period="2mo", interval="1d")
                fiyat_serileri[sembol] = [(idx.date(), float(v)) for idx, v in df["Close"].items()]
            except Exception as e:
                print(f"UYARI: {sembol} veri cekilemedi -> {e}")
                fiyat_serileri[sembol] = []
        seri = fiyat_serileri[sembol]
        if not seri:
            continue

        hedef = etiket_tarih + datetime.timedelta(days=IZLEME_GUN_SAYISI)
        sonraki_fiyat = _en_yakin_kapanis(seri, hedef)
        if sonraki_fiyat is None:
            continue

        getiri_pct = round((sonraki_fiyat / kayit["isaretlenme_ani_fiyat"] - 1) * 100, 2)
        kayit["izleme_sonrasi_getiri_pct"] = getiri_pct
        kayit["durum"] = "TOPARLANDI" if getiri_pct > 0 else "TOPARLANMADI"
        sonuclanan_sayisi += 1
    print(f"{sonuclanan_sayisi} aday bu kosumda sonuclandi (10 is gunu gecmis)")

    sonuclanan = [k for k in arsiv["kayitlar"] if k["durum"] in ("TOPARLANDI", "TOPARLANMADI")]
    ozet = {}
    for etiket in ("GERI_CEKILME_ADAYI_GUCLU", "GERI_CEKILME_ADAYI_TEMKINLI"):
        alt = [k for k in sonuclanan if k["etiket"] == etiket]
        if not alt:
            continue
        toparlanan = sum(1 for k in alt if k["durum"] == "TOPARLANDI")
        ort_getiri = sum(k["izleme_sonrasi_getiri_pct"] for k in alt) / len(alt)
        ozet[etiket] = {"n": len(alt), "toparlanan_pct": round(100 * toparlanan / len(alt), 1),
                          "ort_getiri_pct": round(ort_getiri, 2)}

    arsiv["ozet"] = ozet
    arsiv["son_guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    arsiv["toplam_kayit"] = len(arsiv["kayitlar"])
    arsiv["sonuclanan_kayit"] = len(sonuclanan)
    atomik_json_yaz(ARSIV_YOL, arsiv)
    print(f"\nArsiv: {arsiv['toplam_kayit']} toplam, {arsiv['sonuclanan_kayit']} sonuclanmis")
    for etiket, v in ozet.items():
        print(f"  {etiket}: n={v['n']}, toparlanan=%{v['toparlanan_pct']}, ort getiri=%{v['ort_getiri_pct']}")


if __name__ == "__main__":
    main()
