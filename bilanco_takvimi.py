"""
BILANCO TAKVIMI (18.08.2026) - SALT OKUMA, brifing girdisi

SORUN: Bu haftanin en buyuk dort fiyat hareketinin dordu de bilanco ya
da KAP kaynakliydi (MGROS %-9.2, BIMAS %+6.2, ASTOR %+9.9, ASTOR TEIAS
sozlesmesi) ve brifing hicbirini gormedi. Sebep: haber kanali bozuk
(KAP ham 100 / suzulen 0) ve "portfoy sembollerine haber yok" satiri
dunya hakkinda bilgi degil, boru hattinin ariza raporuydu.

COZUM: Bilanco tarihleri DETERMINISTIK. Arama sorgusuyla degil,
takvim dosyasiyla tasinir. Bu betik data/bilanco_takvimi.json'u okur
ve brifinge hazir iki sey uretir:
  1. Pencere: bugun/yarin aciklama bekleyenler, dun aciklayanlar
  2. RISK BAYRAGI: acik pozisyonlardan hangisi bilanco penceresinde

Ikincisi asil onemli olan. MGROS bir gunde %9.2 gosterdi; bilanco gunu
stop mesafesi ve pozisyon boyutu ayni olamaz. IP-1'de "olay oncesi
testere" zaafi zaten belgelenmisti - bu, o zaafin eksik girdisi.

KIRMIZI CIZGI: Pine'a dokunmaz, sinyal uretmez, karar dosyasina
yazmaz. Tek ciktisi data/denetim/bilanco_uyari.json ve stdout.

ONEMLI KURAL: takvim dosyasi TAHMIN TASIMAZ. Bilinmeyen tarih null
kalir ve bu betik onu "BILINMIYOR" olarak raporlar. Uydurulmus bir
tarih, tarihi olmamasindan daha kotudur - risk katmanini yanlis yone
kilitler ve yanlis guven verir.
"""
from json_atomik_yaz import atomik_json_yaz
import datetime
import json
import sys

TAKVIM_YOL = "data/bilanco_takvimi.json"
PORTFOY_YOL = "data/portfoy.json"
CIKTI = "data/denetim/bilanco_uyari.json"

ONCE_GUN = 2   # kac gun onceden uyar
SONRA_GUN = 1  # kac gun sonrasina kadar "dun acikladi" say


def _tarih(s):
    return datetime.date.fromisoformat(s) if s else None


def _aktif_donem(takvim, bugun):
    """Bugune en yakin, henuz kapanmamis donem. Son tarihi gecmis
    donemler de raporlanir (gecikmis aciklama olabilir)."""
    adaylar = []
    for ad, d in takvim["donemler"].items():
        sk = _tarih(d.get("son_tarih_konsolide"))
        if sk is None or (bugun - sk).days <= 30:
            adaylar.append((ad, d))
    return adaylar


def main():
    try:
        with open(TAKVIM_YOL, encoding="utf-8") as f:
            takvim = json.load(f)
    except Exception as e:
        print(f"HATA: takvim okunamadi -> {e}", file=sys.stderr)
        return

    try:
        with open(PORTFOY_YOL, encoding="utf-8") as f:
            acik = {p["sembol"] for p in json.load(f)["acik_pozisyonlar"]}
    except Exception:
        acik = set()
        print("UYARI: portfoy okunamadi - risk bayragi uretilmeyecek",
              file=sys.stderr)

    bugun = datetime.datetime.now(datetime.timezone.utc).date()
    semboller = takvim["semboller"]

    bekleyen, aciklayan, bilinmeyen, risk = [], [], [], []

    for sembol, kayit in semboller.items():
        tarihler = {k: _tarih(v) for k, v in kayit.items()
                    if k.endswith("_aciklama")}
        gecerli = {k: t for k, t in tarihler.items() if t is not None}

        kaynak = kayit.get("kaynak", "BILINMIYOR")

        if not gecerli:
            bilinmeyen.append({"sembol": sembol, "kaynak": kaynak})
            if sembol in acik:
                risk.append({"sembol": sembol, "durum": "TARIH BILINMIYOR",
                             "kaynak": kaynak,
                             "not": "acik pozisyon, bilanco tarihi yok"})
            continue

        for alan, t in gecerli.items():
            fark = (t - bugun).days
            donem = alan.replace("_aciklama", "")
            if 0 <= fark <= ONCE_GUN:
                bekleyen.append({"sembol": sembol, "donem": donem,
                                 "tarih": str(t), "gun_kaldi": fark,
                                 "kaynak": kaynak,
                                 "acik_pozisyon": sembol in acik})
                if sembol in acik:
                    risk.append({
                        "sembol": sembol, "durum": "BILANCO PENCERESI",
                        "tarih": str(t), "gun_kaldi": fark,
                        "kaynak": kaynak,
                        "not": "stop mesafesi ve pozisyon boyutu gozden "
                               "gecirilmeli (MGROS 12.08: bir gunde %-9.2)"
                               + (" | TARIH SADECE DERLEME - sirket revize "
                                  "edebilir" if kaynak == "DERLEME_BEKLENTI"
                                  else ""),
                    })
            elif -SONRA_GUN <= fark < 0:
                aciklayan.append({"sembol": sembol, "donem": donem,
                                  "tarih": str(t), "kaynak": kaynak,
                                  "not": kayit.get("not", ""),
                                  "acik_pozisyon": sembol in acik})

    # Donem son tarihleri (evren geneli uyari)
    donem_uyari = []
    for ad, d in _aktif_donem(takvim, bugun):
        for alan in ("son_tarih_konsolide_olmayan", "son_tarih_konsolide"):
            t = _tarih(d.get(alan))
            if t and 0 <= (t - bugun).days <= 5:
                donem_uyari.append({"donem": ad, "tur": alan,
                                    "tarih": str(t),
                                    "gun_kaldi": (t - bugun).days})

    sonuc = {
        "zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "bugun": str(bugun),
        "bekleyen": sorted(bekleyen, key=lambda x: x["gun_kaldi"]),
        "aciklayan": aciklayan,
        "donem_son_tarih_uyarisi": donem_uyari,
        "risk_bayragi": risk,
        "tarihi_bilinmeyen": sorted(bilinmeyen, key=lambda x: x["sembol"]),
        "celiskiler": takvim.get("_celiskiler", []),
        "kapsama": {
            "toplam_sembol": len(semboller),
            "tarihi_olan": len(semboller) - len(bilinmeyen),
            "kapsama_pct": round(
                100 * (len(semboller) - len(bilinmeyen)) / len(semboller), 1),
            "celiskili": sum(1 for x in bilinmeyen
                             if x["kaynak"] == "CELISKILI"),
        },
    }
    atomik_json_yaz(CIKTI, sonuc)

    print(f"BILANCO TAKVIMI — {bugun}")
    print(f"Kapsama: {sonuc['kapsama']['tarihi_olan']}/"
          f"{sonuc['kapsama']['toplam_sembol']} sembolde tarih var "
          f"(%{sonuc['kapsama']['kapsama_pct']})")

    if donem_uyari:
        print("\nDONEM SON TARIHI YAKLASIYOR")
        for u in donem_uyari:
            print(f"  {u['donem']} {u['tur']}: {u['tarih']} "
                  f"({u['gun_kaldi']} gun)")

    if bekleyen:
        print("\nBILANCO BEKLEYENLER")
        for b in bekleyen:
            poz = " [ACIK POZISYON]" if b["acik_pozisyon"] else ""
            print(f"  {b['sembol']:7} {b['donem']} {b['tarih']} "
                  f"({b['gun_kaldi']} gun) [{b['kaynak']}]{poz}")
    else:
        print("\nBilanco bekleyen yok (bilinen tarihler icinde)")

    if aciklayan:
        print("\nDUN/BUGUN ACIKLAYANLAR")
        for a in aciklayan:
            print(f"  {a['sembol']:7} {a['donem']} {a['tarih']}"
                  f"{'  ' + a['not'] if a['not'] else ''}")

    if risk:
        print("\n*** RISK BAYRAGI — ACIK POZISYONLAR ***")
        for r in risk:
            print(f"  {r['sembol']:7} {r['durum']} — {r['not']}")

    if sonuc["kapsama"]["kapsama_pct"] < 50:
        print(f"\nUYARI: sembollerin %"
              f"{100 - sonuc['kapsama']['kapsama_pct']:.0f}'inde tarih YOK. "
              "Bu betigin sessizligi 'bilanco yok' ANLAMINA GELMEZ.")
        print("Tarihi bilinmeyenler: " + ", ".join(
            f"{x['sembol']}({x['kaynak']})"
            for x in sonuc["tarihi_bilinmeyen"]))

    if sonuc["celiskiler"]:
        print("\nCOZULMEMIS CELISKILER")
        for c in sonuc["celiskiler"]:
            print(f"  {c['konu']}: {' vs '.join(c['degerler'])}")


if __name__ == "__main__":
    main()
