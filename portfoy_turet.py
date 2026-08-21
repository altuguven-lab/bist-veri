"""
PORTFOY TURETME (19.08.2026) - C2 karari

DEGISIKLIK: portfoy.json artik ELLE DUZENLENMEZ. islem_gunlugu.json
degismez ana kayittir; portfoy durumu ondan TURETILIR.

GEREKCE (mimari inceleme, 19.08): portfoy.json ve islem_gunlugu.json
iki ayri ELLE guncellenen gerceklik olusturuyordu. Sonuc: ASTOR satisi
portfoyde vardi, gunlukte YOKTU - ve M3 (sinyal-uyum) hukum metrigi
matematiksel olarak calissa bile ekonomik anlam tasimiyordu.

--- NAKIT TURETILMEZ, RAPORLANIR (v3, 19.08) -----------------------
Nakit gunluk para piyasasi fonlarinda degerleniyor: getiri isliyor.
Islemlerden turetilen bir nakit rakami gercek bakiyeden SUREKLI
sapardi. Bu yuzden nakdin tek otoritesi NAKIT_MUTABAKAT olaylaridir.

Ama betik islemlerden beklenen nakit degisimini de hesaplar ve
raporlanan bakiyeyle KARSILASTIRIR. Aradaki fark = fon getirisi +
(varsa) KAYDA GECMEMIS ISLEM. Bu fark her kosuda yazilir; anormal
buyurse kayitsiz bir islem var demektir. Yani mutabakat kapisi
kaldirilmadi, DOGRU YERE tasindi.

NOT: getiri_tabani muhasebe kimligi DEGILDIR. Pozisyon maliyeti +
nakit toplamiyla ortusmesi beklenmez; brifingdeki yuzde onun uzerinden
hesaplanir.

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
# Fon getirisi disinda aciklanamayan nakit farki bu esigi asarsa uyar.
# Gunluk para piyasasi fonu icin makul ust sinir (yillik ~%50 -> aylik
# ~%4); bunun uzeri fon getirisiyle aciklanamaz.
NAKIT_FARK_UYARI_ORANI = 0.05

# v4: nakit akisi ISLEM tarihine gore degil TAKAS tarihine gore islenir.
# ASTOR ornegi: emir 12.08, bedel 14.08'de hesaba gecti. 13.08 tarihli bir
# NAKIT_MUTABAKAT o bedeli HENUZ ICERMEZ. Islem tarihiyle eslestirmek,
# arada kalan her mutabakatta sahte "kayitsiz islem" uyarisi uretirdi.
# takas_tarihi yoksa islem tarihi kullanilir ve uyari listesine yazilir.


def _uygula(olaylar):
    """Olaylari SIRAYLA katlayarak durum uretir. Saf fonksiyon.

    islem_nakit_akisi: yalniz ALIS/SATIS'tan gelen nakit hareketi.
    raporlanan_nakit: son NAKIT_MUTABAKAT. Ikisi AYRI tutulur."""
    islem_nakit_akisi = 0.0
    raporlanan_nakit = None
    raporlanan_tarih = None
    mutabakatlar = []   # (tarih, raporlanan, o tarihe kadar TAKASLANMIS akis)
    nakit_takvimi = []  # (takas_tarihi, tutar) - sirali degil, toplanirken suzulur
    takas_tarihi_eksik = []
    pozisyon = {}
    kapanan = []
    stoplar = {}
    uyarilar = []

    for o in sorted(olaylar, key=lambda x: x["tarih_utc"]):
        tip = o["tip"]

        if tip == "ACILIS_BAKIYESI":
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
            islem_nakit_akisi -= tutar
            tt = o.get("takas_tarihi")
            if not tt:
                takas_tarihi_eksik.append(o["olay_id"])
                tt = o["tarih_utc"][:10]
            nakit_takvimi.append((tt, -tutar))
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
            islem_nakit_akisi += o["adet"] * o["fiyat"]
            tt = o.get("takas_tarihi")
            if not tt:
                takas_tarihi_eksik.append(o["olay_id"])
                tt = o["tarih_utc"][:10]
            nakit_takvimi.append((tt, o["adet"] * o["fiyat"]))
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

        elif tip == "NAKIT_MUTABAKAT":
            raporlanan_nakit = o["raporlanan_nakit_tl"]
            raporlanan_tarih = o["tarih_utc"]
            # Bu tarihe kadar TAKASI GERCEKLESMIS akisi topla
            gun = o["tarih_utc"][:10]
            takas_akisi = sum(
                t for d, t in nakit_takvimi if d <= gun)
            mutabakatlar.append((o["tarih_utc"], raporlanan_nakit,
                                 takas_akisi))

        elif tip == "TEMETTU":
            pass  # bilgi kaydi - nakit NAKIT_MUTABAKAT'tan gelir

        elif tip == "STOP_GUNCELLEME":
            stoplar[o["sembol"]] = o["yeni_stop"]

        else:
            uyarilar.append(f"{o['olay_id']}: bilinmeyen olay tipi '{tip}'")

    if takas_tarihi_eksik:
        uyarilar.append("takas_tarihi eksik (islem tarihi kullanildi): "
                        + ", ".join(takas_tarihi_eksik))
    return (islem_nakit_akisi, raporlanan_nakit, raporlanan_tarih,
            mutabakatlar, pozisyon, kapanan, stoplar, uyarilar)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaz", action="store_true",
                    help="data/portfoy.json'a yaz (varsayilan: yalniz goster)")
    args = ap.parse_args()

    with open(GUNLUK_YOL, encoding="utf-8") as f:
        gunluk = json.load(f)

    olaylar = gunluk.get("olaylar", [])
    if not olaylar:
        print("HATA: olay yok", file=sys.stderr)
        sys.exit(1)

    (islem_akisi, nakit, nakit_tarih, mutabakatlar, pozisyon, kapanan,
     stoplar, uyarilar) = _uygula(olaylar)

    # --- KAPI: raporlanan nakit var mi ------------------------------
    if nakit is None:
        print("DURDURULDU — hic NAKIT_MUTABAKAT olayi yok.", file=sys.stderr)
        print("Nakit turetilmez, raporlanir. En az bir NAKIT_MUTABAKAT "
              "olayi gerekli.", file=sys.stderr)
        sys.exit(2)

    # 19.08 DUZELTME: mutlak karsilastirma YANLISTI. Acilis bakiyesi
    # nakit tasimadigi icin islem akisi sifirdan basliyor; raporlanan
    # bakiyeyle kiyaslayinca acilis nakdi "aciklanmayan fark" gibi
    # gorunuyordu (+600.000, %97). Dogrusu IKI MUTABAKAT ARASINDAKI
    # degisimi kiyaslamak: raporlanan delta vs o araliktaki islem akisi.
    # Fark = fon getirisi + (varsa) kayda gecmemis islem.
    fark = fark_orani = None
    nakit_uyari = False
    if len(mutabakatlar) >= 2:
        (t0, n0, a0), (t1, n1, a1) = mutabakatlar[-2], mutabakatlar[-1]
        fark = (n1 - n0) - (a1 - a0)
        fark_orani = abs(fark) / n0 if n0 else 0.0
        nakit_uyari = fark_orani > NAKIT_FARK_UYARI_ORANI

    eksik_stop = [s for s in pozisyon if s not in stoplar]
    if eksik_stop:
        uyarilar.append("stop seviyesi olmayan acik pozisyon: "
                        + ", ".join(sorted(eksik_stop)))

    cikti = {
        "_turetildi": True,
        "getiri_tabani_tl": (gunluk.get("_getiri_tabani") or {}).get("tutar_tl"),
        "_getiri_tabani_notu": "GETIRI OLCUM TABANI - muhasebe kimligi degil",
        "nakit_kaynak": {
            "raporlanan_tarih": nakit_tarih,
            "mutabakat_sayisi": len(mutabakatlar),
            "aciklanmayan_fark_tl": round(fark, 2) if fark is not None else None,
            "aciklanmayan_fark_orani": (round(fark_orani, 4)
                                        if fark_orani is not None else None),
            "not": ("fark = son iki mutabakat arasindaki raporlanan degisim "
                    "eksi ayni araliktaki islem akisi = fon getirisi + "
                    "(varsa) kayda gecmemis islem"),
        },
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

    yas = ""
    if nakit_tarih:
        try:
            t = datetime.datetime.fromisoformat(nakit_tarih.replace("Z", "+00:00"))
            g = (datetime.datetime.now(datetime.timezone.utc) - t).days
            yas = f" (raporlandi {nakit_tarih[:10]}, {g} gun once)"
        except Exception:
            pass
    print(f"Nakit: {cikti['nakit_tl']:,.2f} TL{yas}")
    if fark is None:
        print(f"  nakit kontrolu: YAPILAMADI — {len(mutabakatlar)} mutabakat "
              "var, en az 2 gerekli")
        print("  (tek mutabakatla fon getirisi ile kayitsiz islem ayrilamaz)")
    else:
        print(f"  son iki mutabakat arasi aciklanmayan fark: "
              f"{fark:+,.2f} TL (%{fark_orani*100:.1f})")
    if nakit_uyari:
        print(f"  >>> UYARI: fark %{NAKIT_FARK_UYARI_ORANI*100:.0f} esigini "
              "asiyor. Fon getirisiyle aciklanamaz - kayda gecmemis islem "
              "olabilir.")
    print(f"Acik pozisyon: {len(cikti['acik_pozisyonlar'])} | "
          f"kapanan: {len(kapanan)}")
    for p in cikti["acik_pozisyonlar"]:
        st = f"{p['stop_seviye']}" if p["stop_seviye"] else "STOP YOK"
        print(f"  {p['sembol']:7} {p['adet']:6} @ {p['giris_fiyat']:9.4f}  "
              f"stop {st}")
    if nakit_uyari:
        uyarilar.append(
            f"aciklanmayan nakit farki {fark:+,.2f} TL "
            f"(%{fark_orani*100:.1f}) — esik asildi")
    elif fark is None:
        uyarilar.append("nakit kontrolu yapilamadi — ikinci bir "
                        "NAKIT_MUTABAKAT olayi gerekli")
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
