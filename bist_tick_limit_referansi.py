"""
BIST_TICK_LIMIT_REFERANSI (11.08.2026) - Faz V0
Perplexity_V162_degerlendirme.txt Bolum 7.2-7.4'ten (BIST'in resmi
fiyat adimi/limit tablosuna dayali) - SALT MATEMATIK, Pine'a hic
DOKUNMUYOR. Mevcut sinyal_arsiv.json kayitlarini GERIYE DONUK olarak
"tavan/taban bolgesinde miydi" diye ZENGINLESTIRIR.

DURUST VARSAYIM: 30 sembollük evrenimizin TAMAMININ Yildiz Pazar'da
(%20 limit) islem gordugu VARSAYILIYOR - BIST-30 kapsamindaki BUYUK,
likit hisseler icin bu MAKUL bir varsayim (arastirma: Yildiz Pazar
"BIST 100/50/30 endekslerinin ANA HAVUZUNU" olusturuyor), ama HER
30 sembol icin TEK TEK DOGRULANMADI - KESIN degil.

KIRMIZI CIZGI: SALT OLCUM/ZENGINLESTIRME, Pine'a hic dokunmuyor,
hicbir sinyal/karar URETMEZ. Kulucka Protokolu'nu ETKILEMEZ.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import yfinance as yf

YILDIZ_PAZAR_LIMIT_PCT = 20.0
LIMIT_TOLERANS_PCT = 1.0


def bist_tick(fiyat):
    if fiyat < 20.0:
        return 0.01
    elif fiyat < 50.0:
        return 0.02
    elif fiyat < 100.0:
        return 0.05
    elif fiyat < 250.0:
        return 0.10
    elif fiyat < 500.0:
        return 0.25
    elif fiyat < 1000.0:
        return 0.50
    elif fiyat < 2500.0:
        return 1.00
    else:
        return 2.50


def yuvarla_asagi(fiyat, tick):
    import math
    return math.floor(fiyat / tick) * tick if tick > 0 else fiyat


def yuvarla_yukari(fiyat, tick):
    import math
    return math.ceil(fiyat / tick) * tick if tick > 0 else fiyat


def limit_bandi_hesapla(onceki_kapanis, limit_pct=YILDIZ_PAZAR_LIMIT_PCT):
    ham_ust = onceki_kapanis * (1 + limit_pct / 100)
    ham_alt = onceki_kapanis * (1 - limit_pct / 100)
    ust_tick = bist_tick(ham_ust)
    alt_tick = bist_tick(ham_alt)
    return {
        "ust_limit": round(yuvarla_asagi(ham_ust, ust_tick), 2),
        "alt_limit": round(yuvarla_yukari(ham_alt, alt_tick), 2),
    }


def onceki_gun_kapanisi_bul(sembol, tarih_str):
    tarih = datetime.date.fromisoformat(tarih_str)
    try:
        df = yf.Ticker(f"{sembol}.IS").history(
            start=(tarih - datetime.timedelta(days=10)).isoformat(),
            end=(tarih + datetime.timedelta(days=1)).isoformat(),
            interval="1d")
    except Exception as e:
        print(f"HATA: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
        return None
    if df.empty:
        return None
    onceki_barlar = df[df.index.date < tarih]
    if onceki_barlar.empty:
        return None
    return float(onceki_barlar["Close"].iloc[-1])


def main():
    with open("data/sinyal_arsiv.json", encoding="utf-8") as f:
        arsiv = json.load(f)

    zenginlestirilmis = []
    limit_bolgesi_sayisi = 0
    veri_eksik_sayisi = 0

    onbellek = {}
    for kayit in arsiv["kayitlar"]:
        anahtar = (kayit["sembol"], kayit["tarih"])
        if anahtar not in onbellek:
            onbellek[anahtar] = onceki_gun_kapanisi_bul(kayit["sembol"], kayit["tarih"])
        onceki_kapanis = onbellek[anahtar]

        yeni_kayit = dict(kayit)
        if onceki_kapanis is None:
            yeni_kayit["bist_limit_kontrolu"] = "VERI_YOK"
            veri_eksik_sayisi += 1
        else:
            bant = limit_bandi_hesapla(onceki_kapanis)
            fiyat = kayit["sinyal_fiyat"]
            ust_tolerans = bant["ust_limit"] * (1 - LIMIT_TOLERANS_PCT / 100)
            alt_tolerans = bant["alt_limit"] * (1 + LIMIT_TOLERANS_PCT / 100)
            if fiyat >= ust_tolerans:
                yeni_kayit["bist_limit_kontrolu"] = "TAVAN_BOLGESI"
                limit_bolgesi_sayisi += 1
            elif fiyat <= alt_tolerans:
                yeni_kayit["bist_limit_kontrolu"] = "TABAN_BOLGESI"
                limit_bolgesi_sayisi += 1
            else:
                yeni_kayit["bist_limit_kontrolu"] = "NORMAL"
            yeni_kayit["bist_limit_detay"] = {
                "onceki_kapanis": onceki_kapanis, "ust_limit": bant["ust_limit"],
                "alt_limit": bant["alt_limit"], "varsayim": "YILDIZ_PAZAR_%20",
            }
        zenginlestirilmis.append(yeni_kayit)

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("sinyal_arsiv.json kayitlarinin GERIYE DONUK BIST tavan/"
                "taban limit kontrolu - Perplexity_V162_degerlendirme.txt "
                "Bolum 7'den. VARSAYIM: TUM semboller Yildiz Pazar'da "
                "(%20 limit) - HER sembol icin TEK TEK DOGRULANMADI. "
                "SALT OLCUM, Pine'a dokunmuyor, Kulucka Protokolu'nu "
                "ETKILEMEZ."),
        "limit_bolgesinde_sinyal_sayisi": limit_bolgesi_sayisi,
        "veri_eksik_sayisi": veri_eksik_sayisi,
        "toplam_kayit": len(zenginlestirilmis),
        "kayitlar": zenginlestirilmis,
    }
    atomik_json_yaz("data/sinyal_arsiv_bist_limit_kontrolu.json", rapor)
    print(f"Yazildi: data/sinyal_arsiv_bist_limit_kontrolu.json")
    print(f"Limit bolgesinde (tavan/taban) sinyal sayisi: {limit_bolgesi_sayisi}/{len(zenginlestirilmis)}")
    print(f"Veri eksik: {veri_eksik_sayisi}")
    for k in zenginlestirilmis:
        if k.get("bist_limit_kontrolu") in ("TAVAN_BOLGESI", "TABAN_BOLGESI"):
            print(f"  {k['sembol']} {k['sinyal']} {k['tarih']}: {k['bist_limit_kontrolu']} "
                  f"(fiyat={k['sinyal_fiyat']}, limit_detay={k['bist_limit_detay']})")


if __name__ == "__main__":
    main()
