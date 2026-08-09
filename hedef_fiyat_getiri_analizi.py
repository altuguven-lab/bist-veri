"""
HEDEF_FIYAT_GETIRI_ANALIZI (08.08.2026) - Faz V0
Kurul karari: bir "AL/SAT skoru" URETMEZ - yalniz SEFFAF bir hesaplama:
"eger en son analist hedef fiyati GERCEKLESIRSE, guncel fiyattan ne
kadar getiri olur" sorusuna DUZ MATEMATIKSEL cevap verir. Vade bilgisi
VARSA (kisa/orta) AYRI gosterilir, YOKSA "BILINMIYOR" ile birlikte
gosterilir - vade etiketi olmayan eski kayitlar icin TAHMIN YURUTULMEZ.

KIRMIZI CIZGI: SALT HESAPLAMA/GOSTERIM - yorumlama VE karar insana
aittir. "Beklenen getiri %" bir TAVSIYE DEGIL, hedef fiyatin KENDI
matematigidir.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime


def main():
    arastirma = json.load(open("data/arastirma_hedef_fiyat.json", encoding="utf-8"))
    fiyatlar = json.load(open("data/bist_quotes.json", encoding="utf-8"))
    guncel_fiyat = {v["sembol"]: v["son_fiyat"] for v in fiyatlar.get("veriler", [])}

    # 08.08 DUZELTME: yalniz GERCEK hedef fiyat kayitlarini isle -
    # "KAR_RAKAMI"/"MARJ_REHBERI" gibi FARKLI olcekteki sayilar
    # (orn. KCHOL'un milyar-TL kar rakami) HEDEF FIYAT sanilip
    # anlamsiz "getiri" (-%90) URETMESIN diye FILTRELENIR. Eski
    # kayitlarda 'kayit_tipi' YOKSA (henuz etiketlenmemis gecmis
    # veri), GERIYE UYUMLULUK icin varsayilan HEDEF_FIYAT sayilir.
    en_son_kayit = {}
    for k in arastirma["kayitlar"]:
        if k.get("kayit_tipi", "HEDEF_FIYAT") != "HEDEF_FIYAT":
            continue
        sembol = k["sembol"]
        if sembol not in en_son_kayit or k["tarih"] > en_son_kayit[sembol]["tarih"]:
            en_son_kayit[sembol] = k

    sonuclar = []
    for sembol, kayit in en_son_kayit.items():
        guncel = guncel_fiyat.get(sembol)
        if guncel is None or guncel <= 0:
            continue
        hedef = kayit["yeni_hedef"]
        beklenen_getiri_pct = round((hedef / guncel - 1) * 100, 2)
        sonuclar.append({
            "sembol": sembol, "guncel_fiyat": guncel, "hedef_fiyat": hedef,
            "hedef_tarihi": kayit["tarih"], "kurum": kayit["kurum"],
            "vade": kayit.get("vade", "BILINMIYOR"),
            "son_revizyon_yonu": kayit["yon"],  # 08.08 EKI: TAM BAGLAM icin -
            # yuksek "beklenen getiri" ile "son revizyon ASAGIYDI" AYNI ANDA
            # olabilir (hedef dusurulmus ama hala guncel fiyatin ustunde) -
            # bu ikisi CELISMEZ ama BIRLIKTE gosterilmezse YANILTICI olabilir.
            "beklenen_getiri_pct": beklenen_getiri_pct,
        })

    sonuclar.sort(key=lambda s: -s["beklenen_getiri_pct"])

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Bu, bir AL/SAT tavsiyesi DEGILDIR - yalniz 'eger en son "
                "analist hedefi gerceklesirse guncel fiyattan ne getiri "
                "olur' sorusuna DUZ MATEMATIKSEL cevaptir. Vade bilgisi "
                "olmayan (BILINMIYOR) kayitlar icin ufuk TAHMIN EDILMEZ."),
        "sembol_sayisi": len(sonuclar),
        "sonuclar": sonuclar,
    }
    atomik_json_yaz("data/hedef_fiyat_getiri_analizi.json", rapor)
    print(f"Yazildi: data/hedef_fiyat_getiri_analizi.json ({len(sonuclar)} sembol)")
    for s in sonuclar[:5]:
        print(f"  {s['sembol']}: beklenen getiri %{s['beklenen_getiri_pct']} "
              f"(son revizyon: {s['son_revizyon_yonu']}, vade: {s['vade']}, "
              f"kaynak: {s['kurum']}, {s['hedef_tarihi']})")


if __name__ == "__main__":
    main()
