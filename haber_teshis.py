"""
HABER KANALI TESHISI (17.08.2026) - SALT OLCUM

SORUN (17.08 brifingi): kaynak_detay'da KAP ham=100 / suzulen=0 / hata=yok.
Genisletilmis bakista tablo daha kotu: GN sembol sorgularinin tamami
2.885 ham kayittan 48 kayit uretiyor (%2) ve 30 sembolun 10'u SIFIR
veriyor - portfoydeki AKBNK, KCHOL, YKBNK dahil.

fetch_news.py bir kaydi dort ayri yerde eleyebilir ama HANGISININ
eledigini hicbir yere yazmiyor: kaynak_detay yalniz "kac tane girdi"
diyor, "neden girmedi" demiyor. Bu betik o bosluk icindir.

NE YAPAR: fetch_news.py'nin KENDI sabitlerini ve KENDI puanla()
fonksiyonunu ice aktarir (kopyalamaz - kopya sessizce ayrisir),
kaynaklari ceker ve her elenen kayit icin eleme NEDENINI sayar.

NE YAPMAZ: data/haber_akisi.json'a dokunmaz, hicbir sinyal uretmez,
fetch_news.py'yi degistirmez. Ciktisi data/denetim/haber_teshis.json
ve stdout.

KULLANIM:
    python haber_teshis.py              # tum kaynaklar, ozet
    python haber_teshis.py KAP          # tek kaynak, basliklariyla
    python haber_teshis.py GN:AKBNK     # tek kaynak, basliklariyla

NOT: Google News'e erisim gerektirir - Actions runner'inda kosar,
kisitli ortamlarda kosmaz.
"""
from json_atomik_yaz import atomik_json_yaz
import datetime
import sys
import time

import feedparser

import fetch_news as fn

CIKTI = "data/denetim/haber_teshis.json"
ORNEK_SAYISI = 6  # tek kaynak modunda gosterilecek ornek baslik adedi


def _eleme_nedeni(giris, taban, simdi):
    """Bir RSS girdisinin fetch_news.py tarafindan neden elendigini
    doner. Sira, fetch_news.kaynak_cek() icindeki sirayla BIREBIR
    ayni olmalidir - degisirse bu betik de guncellenir."""
    baslik = fn.temizle(getattr(giris, "title", ""))
    link = getattr(giris, "link", "")

    if not baslik or not link:
        return "BASLIK_VEYA_LINK_YOK", baslik, None

    if any(k in baslik.lower() for k in fn.GURULTU_KALIPLARI):
        kalip = next(k for k in fn.GURULTU_KALIPLARI if k in baslik.lower())
        return f"GURULTU_KALIBI[{kalip}]", baslik, None

    if any(a in link.lower() for a in fn.SPAM_ALANLAR):
        return "SPAM_ALAN", baslik, None

    pp = (getattr(giris, "published_parsed", None)
          or getattr(giris, "updated_parsed", None))
    if pp is not None:
        yayin = datetime.datetime(*pp[:6], tzinfo=datetime.timezone.utc)
        yas = (simdi - yayin).days
        if yas > fn.MAX_YAYIN_YASI_GUN:
            return f"YAYIN_YASI[{yas}g]", baslik, None

    puan, semboller = fn.puanla(baslik, taban)
    if puan < fn.MIN_PUAN:
        return f"DUSUK_PUAN[{puan}<{fn.MIN_PUAN}]", baslik, puan

    return "GECTI", baslik, puan


def kaynak_teshis(isim, url_veya_liste, taban, ayrintili=False):
    urller = (url_veya_liste if isinstance(url_veya_liste, list)
              else [url_veya_liste])
    simdi = datetime.datetime.now(datetime.timezone.utc)

    for url in urller:
        time.sleep(0.6)
        try:
            feed = feedparser.parse(
                url, agent="Mozilla/5.0 (bist-veri haber botu)")
        except Exception as e:
            return {"isim": isim, "hata": str(e)}
        if not feed.entries:
            continue

        ham = len(feed.entries)
        # fetch_news.py yalniz ILK 25 girdiye bakar - teshis de oyle
        # bakmali, yoksa gercekte islenmeyen kayitlari sayariz.
        incelenen = feed.entries[:25]

        nedenler, kalip_sayaci, ornekler = {}, {}, []
        for g in incelenen:
            neden, baslik, puan = _eleme_nedeni(g, taban, simdi)
            kok = neden.split("[")[0]
            nedenler[kok] = nedenler.get(kok, 0) + 1
            # 17.08 eki: hangi GURULTU kalibinin eledigini ozet modunda da
            # bilmek gerekiyor - duzeltme dogrudan buna baglaniyor.
            if kok == "GURULTU_KALIBI":
                kalip = neden[neden.index("[") + 1:-1]
                kalip_sayaci[kalip] = kalip_sayaci.get(kalip, 0) + 1
            if ayrintili and len(ornekler) < ORNEK_SAYISI:
                ornekler.append({"neden": neden, "puan": puan,
                                 "baslik": baslik[:110]})

        return {
            "isim": isim, "taban": taban, "url": url,
            "ham": ham, "incelenen": len(incelenen),
            "gecen": nedenler.get("GECTI", 0),
            "eleme_nedenleri": {k: v for k, v in sorted(
                nedenler.items(), key=lambda x: -x[1]) if k != "GECTI"},
            "gurultu_kalip_dagilimi": dict(sorted(
                kalip_sayaci.items(), key=lambda x: -x[1])),
            "ornekler": ornekler,
        }

    return {"isim": isim, "taban": taban, "ham": 0,
            "hata": "tum URL'ler bos dondu"}


def main():
    hedef = sys.argv[1] if len(sys.argv) > 1 else None
    kaynaklar = [k for k in fn.KAYNAKLAR if hedef is None or k[0] == hedef]

    if not kaynaklar:
        print(f"'{hedef}' adli kaynak yok. Mevcut kaynaklar:")
        print("  " + ", ".join(k[0] for k in fn.KAYNAKLAR))
        return

    ayrintili = hedef is not None
    sonuclar = []
    print(f"{'KAYNAK':18}{'HAM':>5}{'BAKILAN':>9}{'GECEN':>7}  BASLICA ELEME NEDENI")
    for isim, url, taban in kaynaklar:
        s = kaynak_teshis(isim, url, taban, ayrintili)
        sonuclar.append(s)
        if s.get("hata") and "ham" not in s:
            print(f"{isim:18}{'HATA':>5}  {s['hata'][:50]}")
            continue
        nd = s.get("eleme_nedenleri") or {}
        basat = max(nd.items(), key=lambda x: x[1]) if nd else ("-", 0)
        print(f"{isim:18}{s['ham']:5}{s['incelenen']:9}{s['gecen']:7}  "
              f"{basat[0]} ({basat[1]})")
        if ayrintili:
            for o in s["ornekler"]:
                print(f"    [{o['neden']:24}] {o['baslik']}")

    atomik_json_yaz(CIKTI, {
        "zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "min_puan": fn.MIN_PUAN,
        "max_yayin_yasi_gun": fn.MAX_YAYIN_YASI_GUN,
        "kaynaklar": sonuclar,
    })
    print(f"\nYazildi: {CIKTI}")


if __name__ == "__main__":
    main()
