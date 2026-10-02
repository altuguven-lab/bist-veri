"""
DUSUK TEYIT x YUKSEK HAREKET GOZLEM DEFTERI (02.10.2026)
=============================================================
Gerekce (kurul karari, 02.10.2026 - ASTOR ve OTKAR vakalari): Son
gunlerde iki sembol (ASTOR 01.10, OTKAR 01-02.10) gun icinde %8-10
araliginda guclu fiyat hareketi yasadi, ama sistem hicbir AL turu
sinyal uretmedi - ASTOR'da soguma penceresi + dusuk relVol cakismasi,
OTKAR'da dogrudan skor tabaninin (pSkorTaban=32) altinda kalma
yuzunden. Soru: bu BIR TESADUF mu, yoksa mevcut rejimde (fon
sorusturmasi sonrasi, ince/dusuk katilimli sert tepkiler) sistemin
skor/relVol esikleri YAPISAL OLARAK para mi kacirtiyor?

BU BETIK NE YAPAR: Pine'a veya alarm mantigina DOKUNMADAN, GUNLUK_OZET
kayitlarindan (her sembol icin GUNUN TEK ve GUVENILIR kapanis
okumasi) KENDI KALICI gunluk kapanis defterini olusturur ve HER
GUN icin:
  1. Bir onceki GUNLUK_OZET'e gore fiyat degisimini (%) hesaplar.
  2. Degisim ESIK'i (varsayilan %5) asip asmadigina, O GUN herhangi
     bir AL_SINYALLERI turu gelip gelmedigine, relVol ve skorun
     Pine'daki GERCEK giris esiklerinin (pTetikHacim=1.2,
     pSkorTaban=32) altinda kalip kalmadigina bakar.
  3. Esik asildiysa VE AL sinyali gelmediyse VE (relVol dusuk VEYA
     skor dusuk) ise -> "gozlem_kayitlari"na DUSUK_TEYIT_YUKSEK_HAREKET
     olarak kalici isler.
  4. Her kosuda, ONCEKI gozlem kayitlarinin ileri getirisini (T+1,
     T+3 GUNLUK_OZET kapanisina gore) KENDI DEFTERINDEN doldurur -
     DISARIDAN VERI CEKMEZ, bu yuzden yfinance/ag baglantisi GEREKMEZ,
     SADECE tv_alerts_latest.json okunur.

KIRMIZI CIZGI: SALT OLCUM/GOZLEM. Pine'a dokunmaz, hicbir alarm
uretmez, mevcut dosyalari degistirmez - yalniz data/dusuk_teyit_
gozlem.json'u YAZAR.

DURUSTLUK NOTU:
  - GUNLUK_OZET gunde BIR kez (session.islastbar_regular) geldigi icin
    "gunluk degisim" GERCEKTEN kapanistan kapanisa degisimdir - gun
    ICI (intraday) zirveyi KACIRABILIR (ASTOR vakasinda oldugu gibi,
    gun ici %17x relVol ama kapanista 0.49 gibi). Bu YUZDEN flag
    esigini ASAGIDA tutuyoruz (%5) - gun ici daha da buyuk
    hareketlerin kapanista sonmus olabilecegini biliyoruz.
  - relVol/skor degerleri webhook alaninda GELMEZSE (eski sema
    surumleri, "?" degeri) o kayit ATLANIR, varsayilan DEGER
    UYDURULMAZ.
  - Defter, tv_alerts_latest.json'un GECMISINE (ring buffer, pratikte
    ~birkac hafta) bagimlidir - cok eski GUNLUK_OZET'ler zaten
    dusmus olabilir, bu durumda o sembolun "onceki gun" karsilastirmasi
    o gun icin atlanir (kayit BOZULMAZ, sadece o gun icin degisim
    hesaplanamaz).
  - Bu bir ALARM uretmez, bir OLCUM GUNLUGUDUR. Haftalik/aylik
    birikince (hafta_denetim.py benzeri) ayri bir ozet raporu ile
    "bu esikler bu rejimde degistirilmeli mi" sorusu CEVAPLANABILIR -
    simdiden HUKUM VERILMEZ.

Cikti: data/dusuk_teyit_gozlem.json
"""
import json
import datetime
import os

GIRIS_YOL = "data/tv_alerts_latest.json"
CIKTI_YOL = "data/dusuk_teyit_gozlem.json"

AL_SINYALLERI = {"P3_SKOR_AL", "P2_DIP_DONUS", "P1_AL", "P1_KALITELI_AL",
                  "P2_ERKEN_AL", "CORE_AL"}

GUNLUK_DEGISIM_ESIGI_PCT = 5.0   # bu veya daha fazla |degisim| -> "yuksek hareket"
RELVOL_ESIGI = 1.2               # Pine pTetikHacim ile AYNI
SKOR_ESIGI = 32.0                # Pine pSkorTaban ile AYNI
ILERI_TAKIP_GUN = [1, 3]         # GUNLUK_OZET bazinda ileri takip (islem gunu)


def _sayi(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _oku_defter():
    if os.path.exists(CIKTI_YOL):
        with open(CIKTI_YOL, encoding="utf-8") as f:
            return json.load(f)
    return {
        "aciklama": ("Dusuk teyit x yuksek hareket gozlem defteri - SALT OLCUM. "
                     "Pine'a dokunmaz, alarm uretmez. bkz. dosyanin basindaki "
                     "docstring (betigin kendisinde)."),
        "esikler": {
            "gunluk_degisim_esigi_pct": GUNLUK_DEGISIM_ESIGI_PCT,
            "relvol_esigi": RELVOL_ESIGI,
            "skor_esigi": SKOR_ESIGI,
        },
        "gunluk_kapanis_defteri": {},   # sembol -> [{"tarih":..,"fiyat":..,"relvol":..,"skor":..,"kgs":..,"rejim":..}]
        "gozlem_kayitlari": [],         # her biri bir DUSUK_TEYIT_YUKSEK_HAREKET olayi
    }


def main():
    defter = _oku_defter()
    with open(GIRIS_YOL, encoding="utf-8") as f:
        veri = json.load(f)

    gecmis = veri.get("sinyal_gecmisi", [])

    # --- (A) O GUN herhangi bir AL sinyali geldi mi? (sembol,tarih) -> bool
    al_geldi = {}
    for s in gecmis:
        if s.get("sinyal") in AL_SINYALLERI:
            tarih = s["zaman_utc"][:10]
            al_geldi[(s["sembol"], tarih)] = True

    # --- (B) GUNLUK_OZET kayitlarini sembol+tarih bazinda tekille
    ozet_kayitlari = {}
    for s in gecmis:
        if s.get("sinyal") != "GUNLUK_OZET":
            continue
        tarih = s["zaman_utc"][:10]
        anahtar = (s["sembol"], tarih)
        # ayni gun icinde birden fazla GUNLUK_OZET varsa (tekrar/retry) EN SONUNCUYU al
        mevcut = ozet_kayitlari.get(anahtar)
        if mevcut is None or s["zaman_utc"] > mevcut["zaman_utc"]:
            ozet_kayitlari[anahtar] = s

    defter.setdefault("gunluk_kapanis_defteri", {})
    defter.setdefault("gozlem_kayitlari", [])
    mevcut_gozlem_anahtarlari = {(g["sembol"], g["tarih"]) for g in defter["gozlem_kayitlari"]}

    yeni_gozlem = 0
    for (sembol, tarih), s in sorted(ozet_kayitlari.items(), key=lambda kv: kv[0][1]):
        fiyat = _sayi(s.get("fiyat"))
        if fiyat is None:
            continue
        gunluk_liste = defter["gunluk_kapanis_defteri"].setdefault(sembol, [])
        if any(k["tarih"] == tarih for k in gunluk_liste):
            onceki_girdi = None
        else:
            onceki_girdi = gunluk_liste[-1] if gunluk_liste else None
            gunluk_liste.append({
                "tarih": tarih, "fiyat": fiyat,
                "relvol": _sayi(s.get("relvol")),
                "skor": _sayi(s.get("skor")),
                "kgs": _sayi(s.get("kgs")),
                "rejim": _sayi(s.get("rejim")),
            })
            gunluk_liste.sort(key=lambda k: k["tarih"])

        if onceki_girdi is None or (sembol, tarih) in mevcut_gozlem_anahtarlari:
            continue

        onceki_fiyat = onceki_girdi["fiyat"]
        if not onceki_fiyat:
            continue
        degisim_pct = round((fiyat / onceki_fiyat - 1) * 100, 3)

        relvol = _sayi(s.get("relvol"))
        skor = _sayi(s.get("skor"))
        al_mi_geldi = al_geldi.get((sembol, tarih), False)

        dusuk_hacim = relvol is not None and relvol < RELVOL_ESIGI
        dusuk_skor = skor is not None and skor < SKOR_ESIGI

        if (abs(degisim_pct) >= GUNLUK_DEGISIM_ESIGI_PCT
                and not al_mi_geldi
                and (dusuk_hacim or dusuk_skor)):
            defter["gozlem_kayitlari"].append({
                "sembol": sembol, "tarih": tarih,
                "gunluk_degisim_pct": degisim_pct,
                "onceki_gun_fiyat": onceki_fiyat, "fiyat": fiyat,
                "relvol": relvol, "skor": skor, "kgs": _sayi(s.get("kgs")),
                "rejim": _sayi(s.get("rejim")),
                "dusuk_hacim_mi": dusuk_hacim, "dusuk_skor_mu": dusuk_skor,
                "o_gun_al_sinyali_geldi_mi": al_mi_geldi,
                "not": "GUNLUK_OZET kapanistan-kapanisa olcum - gun ICI zirve "
                       "daha yuksek/dusuk olabilir, bkz. durustluk notu.",
            })
            mevcut_gozlem_anahtarlari.add((sembol, tarih))
            yeni_gozlem += 1

    # --- (C) Eski gozlem kayitlarinin ileri getirisini KENDI defterinden doldur
    dolduruldu = 0
    for g in defter["gozlem_kayitlari"]:
        sembol = g["sembol"]
        gunluk_liste = defter["gunluk_kapanis_defteri"].get(sembol, [])
        tarihler = [k["tarih"] for k in gunluk_liste]
        if g["tarih"] not in tarihler:
            continue
        idx = tarihler.index(g["tarih"])
        for n in ILERI_TAKIP_GUN:
            alan = f"ileri_getiri_t{n}_pct"
            if alan in g:
                continue
            if idx + n < len(gunluk_liste):
                hedef_fiyat = gunluk_liste[idx + n]["fiyat"]
                g[alan] = round((hedef_fiyat / g["fiyat"] - 1) * 100, 3)
                dolduruldu += 1

    defter["son_calisma_utc"] = datetime.datetime.utcnow().isoformat() + "Z"
    defter["toplam_gozlem_kaydi"] = len(defter["gozlem_kayitlari"])

    os.makedirs(os.path.dirname(CIKTI_YOL), exist_ok=True)
    with open(CIKTI_YOL, "w", encoding="utf-8") as f:
        json.dump(defter, f, ensure_ascii=False, indent=2)

    print(f"{yeni_gozlem} yeni gozlem kaydi eklendi, {dolduruldu} ileri-getiri "
          f"alani dolduruldu. Toplam gozlem kaydi: {len(defter['gozlem_kayitlari'])}")
    for g in defter["gozlem_kayitlari"][-yeni_gozlem:] if yeni_gozlem else []:
        print(f"  + {g['tarih']} {g['sembol']:7} degisim={g['gunluk_degisim_pct']:+.1f}% "
              f"relvol={g['relvol']} skor={g['skor']} "
              f"(hacim_dusuk={g['dusuk_hacim_mi']}, skor_dusuk={g['dusuk_skor_mu']})")


if __name__ == "__main__":
    main()
