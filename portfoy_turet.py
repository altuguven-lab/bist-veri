"""
PORTFOY TURETME (19.08.2026) - C2 karari

DEGISIKLIK: portfoy.json artik ELLE DUZENLENMEZ. islem_gunlugu.json
degismez ana kayittir; portfoy durumu ondan TURETILIR.

GEREKCE (mimari inceleme, 19.08): portfoy.json ve islem_gunlugu.json
iki ayri ELLE guncellenen gerceklik olusturuyordu. Sonuc: ASTOR satisi
portfoyde vardi, gunlukte YOKTU - ve M3 (sinyal-uyum) hukum metrigi
matematiksel olarak calissa bile ekonomik anlam tasimiyordu.

--- BU BETIGIN EN ONEMLI OZELLIGI: SESSIZCE CALISMAZ ---------------
Mutabakat tutmuyorsa PORTFOY URETMEZ, hata verir ve durur. Yanlis bir
portfoy uretmektense hic uretmemek dogrudur - yanlis portfoy, risk
hesaplarina ve hukum metriklerine sessizce sizar.

Ilk kosuda 261.783 TL'lik bir acik cikti (bkz. islem_gunlugu.json
_acik_mutabakat blogu). Bu acik kapanmadan betik calismayacak. Zaten
C2'nin degeri de bu: defteri tek gerceklik yapmak, mutabakati ZORLAR.

KULLANIM:
    python portfoy_turet.py            # turet + dogrula, yazmaz
    python portfoy_turet.py --yaz      # data/portfoy.json'a yaz
"""
from json_atomik_yaz import atomik_json_yaz
import argparse
import datetime
import json
import sys

GUNLUK_YOL = "data/islem_gunlugu.json"
PORTFOY_YOL = "data/portfoy.json"

# Nakit/pozisyon etkileyen olaylar; digerleri yalniz meta veri
FINANSAL_TIPLER = {"ACILIS_BAKIYESI", "ALIS", "SATIS", "TEMETTU",
                   "NAKIT_HAREKETI"}


def _uygula(olaylar):
    """Olaylari SIRAYLA katlayarak durum uretir. Saf fonksiyon."""
    nakit = None
    pozisyon = {}   # sembol -> {adet, maliyet_toplam, etiket}
    kapanan = []
    stoplar = {}
    uyarilar = []

    for o in sorted(olaylar, key=lambda x: x["tarih_utc"]):
        tip = o["tip"]

        if tip == "ACILIS_BAKIYESI":
            if nakit is not None:
                uyarilar.append(f"{o['olay_id']}: ikinci ACILIS_BAKIYESI - "
                                "yalniz bir tane olmali")
            nakit = o.get("acilis_nakit_tl")
            for p in o["pozisyonlar"]:
                pozisyon[p["sembol"]] = {
                    "adet": p["adet"],
                    "maliyet_toplam": p["adet"] * p["fiyat"],
                    "etiket": p.get("etiket", "ACILIS"),
                    "giris_tarih_utc": o["tarih_utc"],
                }

        elif tip == "ALIS":
            s = o["sembol"]
            tutar = o["adet"] * o["fiyat"]
            if nakit is not None:
                nakit -= tutar
            mevcut = pozisyon.get(s)
            if mevcut:
                mevcut["adet"] += o["adet"]
                mevcut["maliyet_toplam"] += tutar
            else:
                pozisyon[s] = {
                    "adet": o["adet"], "maliyet_toplam": tutar,
                    "etiket": o.get("sinyal_etiketi", "?"),
                    "giris_tarih_utc": o["tarih_utc"],
                }

        elif tip == "SATIS":
            s = o["sembol"]
            mevcut = pozisyon.get(s)
            if not mevcut:
                uyarilar.append(f"{o['olay_id']}: {s} satisi var ama acik "
                                "pozisyon YOK - olay sirasi hatali olabilir")
                continue
            if o["adet"] > mevcut["adet"]:
                uyarilar.append(f"{o['olay_id']}: {s} satis adedi "
                                f"({o['adet']}) pozisyondan ({mevcut['adet']}) "
                                "buyuk")
                continue
            oran = o["adet"] / mevcut["adet"]
            cikan_maliyet = mevcut["maliyet_toplam"] * oran
            if nakit is not None:
                nakit += o["adet"] * o["fiyat"]
            mevcut["adet"] -= o["adet"]
            mevcut["maliyet_toplam"] -= cikan_maliyet
            kapanan.append({
                "sembol": s, "adet": o["adet"],
                "giris_ort_fiyat": round(cikan_maliyet / o["adet"], 4),
                "cikis_fiyat": o["fiyat"],
                "cikis_tarih_utc": o["tarih_utc"],
                "realize_pnl_tl": round(o["adet"] * o["fiyat"] - cikan_maliyet, 2),
                "_dogrulama": o.get("_dogrulama", "OK"),
            })
            if mevcut["adet"] == 0:
                del pozisyon[s]

        elif tip == "TEMETTU":
            if nakit is not None:
                nakit += o["tutar_tl"]

        elif tip == "NAKIT_HAREKETI":
            if nakit is not None:
                nakit += o["tutar_tl"]

        elif tip == "STOP_GUNCELLEME":
            stoplar[o["sembol"]] = o["yeni_stop"]

        else:
            uyarilar.append(f"{o['olay_id']}: bilinmeyen olay tipi '{tip}'")

    return nakit, pozisyon, kapanan, stoplar, uyarilar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaz", action="store_true",
                    help="data/portfoy.json'a yaz (varsayilan: yalniz goster)")
    args = ap.parse_args()

    with open(GUNLUK_YOL, encoding="utf-8") as f:
        gunluk = json.load(f)

    # --- KAPI 1: acik mutabakat -------------------------------------
    acik = gunluk.get("_acik_mutabakat")
    if acik and acik.get("durum", "").startswith("COZULMEDI"):
        print("DURDURULDU — MUTABAKAT ACIK", file=sys.stderr)
        print(f"  tutar: {acik.get('tutar_tl'):,.2f} TL", file=sys.stderr)
        print(f"  {acik.get('aciklama')}", file=sys.stderr)
        print("\nAcik kapanmadan portfoy TURETILMEZ. Yanlis bir portfoy, "
              "risk hesaplarina ve hukum metriklerine sessizce sizar.",
              file=sys.stderr)
        sys.exit(2)

    olaylar = gunluk.get("olaylar", [])
    if not olaylar:
        print("HATA: olay yok", file=sys.stderr)
        sys.exit(1)

    nakit, pozisyon, kapanan, stoplar, uyarilar = _uygula(olaylar)

    # --- KAPI 2: acilis nakdi ---------------------------------------
    if nakit is None:
        print("DURDURULDU — acilis_nakit_tl doldurulmamis", file=sys.stderr)
        sys.exit(2)

    eksik_stop = [s for s in pozisyon if s not in stoplar]
    if eksik_stop:
        uyarilar.append("stop seviyesi olmayan acik pozisyon: "
                        + ", ".join(sorted(eksik_stop)))

    cikti = {
        "_turetildi": True,
        "_kaynak": GUNLUK_YOL,
        "_uyari": "BU DOSYA ELLE DUZENLENMEZ. islem_gunlugu.json'a olay ekleyin.",
        "son_guncelleme_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "nakit_tl": round(nakit, 2),
        "acik_pozisyonlar": [
            {"sembol": s, "yon": "LONG", "adet": v["adet"],
             "giris_fiyat": round(v["maliyet_toplam"] / v["adet"], 4),
             "giris_tarih_utc": v["giris_tarih_utc"],
             "sinyal_etiketi": v["etiket"],
             "stop_seviye": stoplar.get(s)}
            for s, v in sorted(pozisyon.items())
        ],
        "kapanan_pozisyonlar": kapanan,
        "_uyarilar": uyarilar,
    }

    print(f"Nakit: {cikti['nakit_tl']:,.2f} TL")
    print(f"Acik pozisyon: {len(cikti['acik_pozisyonlar'])} | "
          f"kapanan: {len(kapanan)}")
    for p in cikti["acik_pozisyonlar"]:
        st = f"{p['stop_seviye']}" if p["stop_seviye"] else "STOP YOK"
        print(f"  {p['sembol']:7} {p['adet']:6} @ {p['giris_fiyat']:9.4f}  "
              f"stop {st}")
    if uyarilar:
        print("\nUYARILAR")
        for u in uyarilar:
            print(f"  - {u}")

    if args.yaz:
        atomik_json_yaz(PORTFOY_YOL, cikti)
        print(f"\nYazildi: {PORTFOY_YOL}")
    else:
        print("\n(--yaz verilmedi, dosya YAZILMADI)")


if __name__ == "__main__":
    main()
