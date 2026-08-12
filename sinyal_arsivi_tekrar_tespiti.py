"""
SINYAL_ARSIVI_TEKRAR_TESPITI (11.08.2026) - Faz V0
Perplexity_V162_degerlendirme.txt'nin uyardigi sorun DOGRULANDI:
sinyal_arsiv.json'daki 54 kayittan 18'i (%33) AYNI (sembol,sinyal)
icin 1-2 GUN ARALIKLA TEKRARLANMIS (orn. TRALT P3_SKOR_AL 4 GUN UST
USTE). Bu, istatistiksel BAGIMSIZLIK varsayimini CIGNIYOR - AYNI
fiyat hareketi BIRDEN FAZLA KEZ olculuyor OLABILIR.

BU SCRIPT: MEVCUT arsivi SILMEZ/DEGISTIRMEZ (ham veri KORUNUR) -
SADECE her kaydi "ILK_GORULEN" (bir onceki 3 gun icinde AYNI sembol+
sinyal YOK) ya da "TEKRAR_ADAYI" (3 gun icinde AYNI sembol+sinyal
VAR) diye ETIKETLER. Bu, GERIYE DONUK, SEFFAF bir ISARETLEME -
ISTATISTIKLERI biz NASIL YORUMLAYACAGIMIZA rehberlik eder, VERIYI
SILMEZ.

KIRMIZI CIZGI: SALT OLCUM/ETIKETLEME, Pine'a hic dokunmuyor,
Kulucka Protokolu'nu ETKILEMEZ.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime
from collections import defaultdict

TEKRAR_PENCERE_GUN = 3


def main():
    with open("data/sinyal_arsiv.json", encoding="utf-8") as f:
        arsiv = json.load(f)

    kayitlar = arsiv["kayitlar"]
    gruplar = defaultdict(list)
    for i, k in enumerate(kayitlar):
        gruplar[(k["sembol"], k["sinyal"])].append((i, datetime.date.fromisoformat(k["tarih"])))

    etiketler = {}
    for (sembol, sinyal), liste in gruplar.items():
        liste_sirali = sorted(liste, key=lambda x: x[1])
        son_gorulen_tarih = None
        for idx, tarih in liste_sirali:
            if son_gorulen_tarih is not None and (tarih - son_gorulen_tarih).days <= TEKRAR_PENCERE_GUN:
                etiketler[idx] = "TEKRAR_ADAYI"
            else:
                etiketler[idx] = "ILK_GORULEN"
            son_gorulen_tarih = tarih

    zenginlestirilmis = []
    tekrar_sayisi = 0
    for i, k in enumerate(kayitlar):
        yeni = dict(k)
        yeni["tekrar_durumu"] = etiketler.get(i, "ILK_GORULEN")
        if yeni["tekrar_durumu"] == "TEKRAR_ADAYI":
            tekrar_sayisi += 1
        zenginlestirilmis.append(yeni)

    ilk_gorulen = [k for k in zenginlestirilmis if k["tekrar_durumu"] == "ILK_GORULEN"]
    dogrulanan_tum = sum(1 for k in kayitlar if k.get("dogrulama_durumu") == "DOGRULANDI")
    dogrulanan_ilk = sum(1 for k in ilk_gorulen if k.get("dogrulama_durumu") == "DOGRULANDI")

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Perplexity_V162_degerlendirme.txt'nin uyardigi 'ayni sinyal "
                "arka arkaya tekrarlaniyorsa istatistikler yapay sekilde "
                "carpitilir' sorununu ISARETLER - VERIYI SILMEZ/DEGISTIRMEZ, "
                "yalniz her kaydi ILK_GORULEN/TEKRAR_ADAYI diye ETIKETLER. "
                f"Tekrar penceresi: {TEKRAR_PENCERE_GUN} gun."),
        "tekrar_penceresi_gun": TEKRAR_PENCERE_GUN,
        "toplam_kayit": len(kayitlar),
        "tekrar_adayi_sayisi": tekrar_sayisi,
        "ilk_gorulen_sayisi": len(ilk_gorulen),
        "karsilastirma": {
            "tum_kayitlarda_dogrulama_orani_pct": round(100 * dogrulanan_tum / len(kayitlar), 1) if kayitlar else None,
            "yalniz_ilk_gorulende_dogrulama_orani_pct": round(100 * dogrulanan_ilk / len(ilk_gorulen), 1) if ilk_gorulen else None,
        },
        "kayitlar": zenginlestirilmis,
    }
    atomik_json_yaz("data/sinyal_arsiv_tekrar_tespiti.json", rapor)
    print(f"Yazildi: data/sinyal_arsiv_tekrar_tespiti.json")
    print(f"Toplam {len(kayitlar)} kayit, {tekrar_sayisi} TEKRAR_ADAYI, {len(ilk_gorulen)} ILK_GORULEN")
    print(f"TUM kayitlarda dogrulama orani: %{rapor['karsilastirma']['tum_kayitlarda_dogrulama_orani_pct']}")
    print(f"YALNIZ ilk-gorulende dogrulama orani: %{rapor['karsilastirma']['yalniz_ilk_gorulende_dogrulama_orani_pct']}")


if __name__ == "__main__":
    main()
