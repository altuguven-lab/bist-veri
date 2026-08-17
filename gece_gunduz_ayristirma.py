"""
GECE / GUNDUZ GETIRI AYRISTIRMASI + GAP OLCUMU (17.08.2026)
SALT OLCUM - hicbir sinyal uretmez, hicbir dosyaya karar yazmaz.

GEREKCE: "1-2 gunluk swing" kurul sentezi, yeni bir Pine yazmadan ONCE
yapilmasi gereken tek adimi soyluyor: gece (kapanis->acilis) ve gunduz
(acilis->kapanis) getirilerini ayristirmak. Sentezdeki iki buyuk
anlasmazlik da (girisin kapanisa yakin mi ertesi sabah mi verilecegi,
gap veto esiginin 0.3 mu 0.75 ATR mi olacagi) bu olcum yapilmadan
cozulemez - ikisi de ABD verisinden turetilmis, BIST'e transferi
dogrulanmamis rakamlar.

Bu betik o iki soruyu KENDI 30 sembollu evrenimizde olcer.

--- OLCUM DISIPLINI (17.08 kurul dersleri buraya gomulu) --------------
1. PIYASA-GORELI: her sembol icin XU100'e gore asiri getiri de yazilir.
2. GUN-AGIRLIKLI: ayni gunun 30 sembolu bagimsiz gozlem DEGILDIR.
   Evren ozetleri once gun ici ortalanir, sonra gunler ortalanir.
3. ISLEM GUNU: pencereler seri uzerinde bar sayarak kurulur.
4. KONTROL GRUBU: gap kovalari karsilastirmali okunur, tek kova
   tek basina yorumlanmaz.
5. ON KAYITLI RED: asagidaki H0'lar reddedilemezse swing projesi
   ACILMAZ. Sonuc "ilginc" diye kurtarilmaz.

--- ON KAYITLI HIPOTEZLER --------------------------------------------
H1 (giris zamanlamasi): 1-2 gunluk getirinin buyuk kismi GECE olusur.
    RED KRITERI: gece payi %40'in altindaysa, "kapanisa yakin giris"
    savunmasi duser ve ertesi sabah teyitli giris tercih edilir.
H2 (gap vetosu): pozitif gap buyudukce ayni gunun GUNDUZ getirisi
    duser (ters donus).
    RED KRITERI: kovalar arasi monoton bir dususe yoksa gap vetosu
    icin ampirik dayanak yok demektir - esik ABD verisinden
    ithal EDILMEZ, veto maddesi dusurulur.
H3 (kisa ufuk donus): dun en cok yukselenler bugun geride kalir.
    RED KRITERI: ust ve alt desil arasindaki ertesi gun GORELI
    getiri farki isaret degistiriyorsa ya da |fark| < %0.20 ise,
    DONUS motoru icin dayanak yok demektir.

KULLANIM:
    python gece_gunduz_ayristirma.py            # 5 yil, tum evren
    python gece_gunduz_ayristirma.py 2y         # kisa pencere
Cikti: data/denetim/gece_gunduz_olcum.json + stdout ozeti.
NOT: yfinance gerektirir - Actions runner'inda kosar.
"""
from json_atomik_yaz import atomik_json_yaz
import datetime
import statistics
import sys

import yfinance as yf

CIKTI = "data/denetim/gece_gunduz_olcum.json"
ENDEKS = "XU100.IS"
VARSAYILAN_DONEM = "5y"
ATR_PENCERE = 14

# 30 sembollu evren (07.07.2026 guncellemesi)
EVREN = [
    "AKBNK", "GARAN", "YKBNK", "ISCTR", "VAKBN", "HALKB",
    "KCHOL", "SAHOL", "ALARK", "ENKAI",
    "THYAO", "PGSUS", "TAVHL",
    "ASELS", "OTKAR", "ASTOR", "ENJSA",
    "TUPRS", "PETKM", "EREGL", "TRMET", "SISE",
    "TOASO", "FROTO", "TTKOM",
    "BIMAS", "MGROS", "ULKER", "AEFES", "EKGYO",
]

# Gap kovalari (ATR biriminde). Sentezdeki iki rakip esik
# (0.3-0.5 ve 0.75) AYNI tabloda gorunsun diye boyle bolundu.
GAP_KOVALARI = [
    ("<= -0.75", -99.0, -0.75),
    ("-0.75..-0.30", -0.75, -0.30),
    ("-0.30..+0.30", -0.30, 0.30),
    ("+0.30..+0.50", 0.30, 0.50),
    ("+0.50..+0.75", 0.50, 0.75),
    ("> +0.75", 0.75, 99.0),
]


def _gunluk_cek(ticker, donem):
    try:
        df = yf.Ticker(ticker).history(period=donem, interval="1d")
    except Exception as e:
        print(f"UYARI: {ticker} cekilemedi -> {e}", file=sys.stderr)
        return []
    satirlar = []
    for idx, r in df.iterrows():
        try:
            satirlar.append({
                "tarih": idx.date(),
                "acilis": float(r["Open"]), "yuksek": float(r["High"]),
                "dusuk": float(r["Low"]), "kapanis": float(r["Close"]),
            })
        except (TypeError, ValueError):
            continue
    return sorted(satirlar, key=lambda x: x["tarih"])


def _atr_serisi(barlar, pencere=ATR_PENCERE):
    """Wilder TR'nin basit hareketli ortalamasi. Bar i icin ATR,
    i'den ONCEKI pencere kadar bardan hesaplanir - bugunun barini
    kullanmaz (look-ahead yok)."""
    tr = [None]
    for i in range(1, len(barlar)):
        o, y = barlar[i], barlar[i - 1]
        tr.append(max(o["yuksek"] - o["dusuk"],
                      abs(o["yuksek"] - y["kapanis"]),
                      abs(o["dusuk"] - y["kapanis"])))
    atr = [None] * len(barlar)
    for i in range(pencere + 1, len(barlar)):
        dilim = tr[i - pencere:i]
        if all(v is not None for v in dilim):
            atr[i] = sum(dilim) / pencere
    return atr


def _gunluk_kayitlar(barlar):
    """Her bar icin gece/gunduz/toplam getiri ve ATR-normalize gap."""
    atr = _atr_serisi(barlar)
    kayitlar = []
    for i in range(1, len(barlar)):
        b, onceki = barlar[i], barlar[i - 1]
        if onceki["kapanis"] <= 0 or b["acilis"] <= 0:
            continue
        gece = (b["acilis"] / onceki["kapanis"] - 1) * 100
        gunduz = (b["kapanis"] / b["acilis"] - 1) * 100
        toplam = (b["kapanis"] / onceki["kapanis"] - 1) * 100
        gap_atr = None
        if atr[i] and atr[i] > 0:
            gap_atr = (b["acilis"] - onceki["kapanis"]) / atr[i]
        kayitlar.append({"tarih": b["tarih"], "gece": gece,
                         "gunduz": gunduz, "toplam": toplam,
                         "gap_atr": gap_atr})
    return kayitlar


def _gun_agirlikli(gun_sozluk):
    """gun -> [deger] sozlugunden gun-agirlikli ortalama."""
    if not gun_sozluk:
        return None, 0
    gun_ort = [statistics.mean(v) for v in gun_sozluk.values()]
    return statistics.mean(gun_ort), len(gun_ort)


def main():
    donem = sys.argv[1] if len(sys.argv) > 1 else VARSAYILAN_DONEM
    print(f"Donem: {donem} | evren: {len(EVREN)} sembol")

    endeks = {k["tarih"]: k for k in
              _gunluk_kayitlar(_gunluk_cek(ENDEKS, donem))}
    if not endeks:
        print("HATA: endeks serisi yok - goreli olcum yapilamaz, "
              "cikiliyor.", file=sys.stderr)
        return
    print(f"Endeks ({ENDEKS}): {len(endeks)} gun")

    sembol_ozet, gece_gun, gunduz_gun, rel_gece_gun = {}, {}, {}, {}
    gap_kova_gunler = {ad: {} for ad, _, _ in GAP_KOVALARI}
    onceki_getiri_kayit = []  # H3 icin (dun toplam, bugun goreli toplam)

    for sembol in EVREN:
        barlar = _gunluk_cek(f"{sembol}.IS", donem)
        kayitlar = _gunluk_kayitlar(barlar)
        if len(kayitlar) < 60:
            print(f"  {sembol}: yetersiz veri ({len(kayitlar)}), atlandi")
            continue

        g = [k["gece"] for k in kayitlar]
        d = [k["gunduz"] for k in kayitlar]
        t = [k["toplam"] for k in kayitlar]
        top_gece, top_gunduz = sum(g), sum(d)
        pay = (abs(top_gece) / (abs(top_gece) + abs(top_gunduz)) * 100
               if (top_gece or top_gunduz) else None)
        sembol_ozet[sembol] = {
            "gun": len(kayitlar),
            "gece_toplam_pct": round(top_gece, 2),
            "gunduz_toplam_pct": round(top_gunduz, 2),
            "toplam_pct": round(sum(t), 2),
            "gece_payi_pct": round(pay, 1) if pay is not None else None,
            "gece_ort_pct": round(statistics.mean(g), 4),
            "gunduz_ort_pct": round(statistics.mean(d), 4),
        }

        for i, k in enumerate(kayitlar):
            e = endeks.get(k["tarih"])
            gece_gun.setdefault(k["tarih"], []).append(k["gece"])
            gunduz_gun.setdefault(k["tarih"], []).append(k["gunduz"])
            if e:
                rel_gece_gun.setdefault(k["tarih"], []).append(
                    k["gece"] - e["gece"])
            # H2: gap kovasi -> AYNI GUNUN gunduz getirisi (goreli)
            if k["gap_atr"] is not None and e:
                for ad, alt, ust in GAP_KOVALARI:
                    if alt < k["gap_atr"] <= ust:
                        gap_kova_gunler[ad].setdefault(
                            k["tarih"], []).append(k["gunduz"] - e["gunduz"])
                        break
            # H3: dunun toplami -> bugunun goreli toplami
            if i > 0 and e:
                onceki_getiri_kayit.append(
                    (k["tarih"], kayitlar[i - 1]["toplam"],
                     k["toplam"] - e["toplam"]))

    if not sembol_ozet:
        print("HATA: hicbir sembolde yeterli veri yok.", file=sys.stderr)
        return

    # --- H1-KONTROL: endeksin KENDI ayrismasi --------------------------
    # 17.08 ekle: sembol serilerinde temettu/bedelsiz duzeltmesi var,
    # endeks fiyat serisinde yok. Endeks de ayni deseni gosteriyorsa
    # bulgu duzeltme artefakti DEGILDIR; gostermiyorsa buyuk kismi
    # artefakt suphesi altindadir. Kontrol olmadan H1 yorumlanamaz.
    e_gece = {t: [k["gece"]] for t, k in endeks.items()}
    e_gunduz = {t: [k["gunduz"]] for t, k in endeks.items()}
    eg, _ = _gun_agirlikli(e_gece)
    ed, _ = _gun_agirlikli(e_gunduz)
    e_toplam = abs(eg) + abs(ed)
    e_pay = (abs(eg) / e_toplam * 100) if e_toplam else None

    # --- H1: gece payi -------------------------------------------------
    gece_ort, n_gun = _gun_agirlikli(gece_gun)
    gunduz_ort, _ = _gun_agirlikli(gunduz_gun)
    toplam_mutlak = abs(gece_ort) + abs(gunduz_ort)
    gece_payi = (abs(gece_ort) / toplam_mutlak * 100) if toplam_mutlak else None
    h1_red = gece_payi is not None and gece_payi < 40

    # --- H2: gap kovalari ----------------------------------------------
    gap_tablo = {}
    for ad, _, _ in GAP_KOVALARI:
        ort, ng = _gun_agirlikli(gap_kova_gunler[ad])
        gozlem = sum(len(v) for v in gap_kova_gunler[ad].values())
        gap_tablo[ad] = {"gun": ng, "gozlem": gozlem,
                         "gunduz_goreli_ort_pct":
                             round(ort, 4) if ort is not None else None}
    poz_kovalar = ["-0.30..+0.30", "+0.30..+0.50",
                   "+0.50..+0.75", "> +0.75"]
    diziler = [gap_tablo[k]["gunduz_goreli_ort_pct"] for k in poz_kovalar]
    h2_red = any(v is None for v in diziler) or not all(
        diziler[i] >= diziler[i + 1] for i in range(len(diziler) - 1))

    # --- H3: kisa ufuk donus -------------------------------------------
    h3_red, h3_fark = True, None
    if len(onceki_getiri_kayit) > 500:
        sirali = sorted(onceki_getiri_kayit, key=lambda x: x[1])
        k = max(1, len(sirali) // 10)
        alt_gun, ust_gun = {}, {}
        for tarih, _, rel in sirali[:k]:
            alt_gun.setdefault(tarih, []).append(rel)
        for tarih, _, rel in sirali[-k:]:
            ust_gun.setdefault(tarih, []).append(rel)
        alt_ort, _ = _gun_agirlikli(alt_gun)
        ust_ort, _ = _gun_agirlikli(ust_gun)
        if alt_ort is not None and ust_ort is not None:
            h3_fark = alt_ort - ust_ort  # donus varsa POZITIF
            h3_red = h3_fark <= 0.20

    sonuc = {
        "zaman_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "donem": donem, "endeks": ENDEKS,
        "sembol_sayisi": len(sembol_ozet), "gun_sayisi": n_gun,
        "H1_gece_payi": {
            "gece_gun_agirlikli_ort_pct": round(gece_ort, 4),
            "gunduz_gun_agirlikli_ort_pct": round(gunduz_ort, 4),
            "gece_payi_pct": round(gece_payi, 1) if gece_payi else None,
            "RED": h1_red,
        },
        "H1_KONTROL_endeks": {
            "gece_ort_pct": round(eg, 4),
            "gunduz_ort_pct": round(ed, 4),
            "gece_payi_pct": round(e_pay, 1) if e_pay else None,
            "not": "Endeks fiyat serisinde temettu/bedelsiz duzeltmesi "
                   "yoktur. Sembol sonucuyla ayni yondeyse H1 artefakt "
                   "degildir.",
        },
        "H2_gap_veto": {"kovalar": gap_tablo, "RED": h2_red},
        "H3_kisa_ufuk_donus": {
            "alt_ust_desil_farki_pct":
                round(h3_fark, 4) if h3_fark is not None else None,
            "RED": h3_red,
        },
        "sembol_ozet": sembol_ozet,
    }
    atomik_json_yaz(CIKTI, sonuc)

    print("\n=== H1: GECE / GUNDUZ AYRISMASI (gun-agirlikli) ===")
    print(f"  gece   ort %{gece_ort:+.4f}")
    print(f"  gunduz ort %{gunduz_ort:+.4f}")
    print(f"  gece payi %{gece_payi:.1f}  -> H1 {'RED' if h1_red else 'AYAKTA'}")
    print(f"  KONTROL {ENDEKS}: gece %{eg:+.4f} | gunduz %{ed:+.4f} | "
          f"gece payi %{e_pay:.1f}" if e_pay else "  KONTROL: hesaplanamadi")
    print("    (endekste duzeltme yok - ayni yondeyse artefakt degil)")
    print("\n=== H2: GAP KOVASI -> AYNI GUN GORELI GUNDUZ GETIRISI ===")
    print(f"  {'KOVA':16}{'GUN':>6}{'GOZLEM':>8}{'GUNDUZ GORELI':>15}")
    for ad, _, _ in GAP_KOVALARI:
        v = gap_tablo[ad]
        d = v["gunduz_goreli_ort_pct"]
        print(f"  {ad:16}{v['gun']:6}{v['gozlem']:8}"
              f"{('%%%+.3f' % d) if d is not None else '-':>15}")
    print(f"  -> H2 {'RED' if h2_red else 'AYAKTA'} "
          f"(monoton dusus {'yok' if h2_red else 'var'})")
    print("\n=== H3: KISA UFUK DONUS ===")
    print(f"  alt desil - ust desil ertesi gun goreli farki: "
          f"{('%%%+.3f' % h3_fark) if h3_fark is not None else '-'}")
    print(f"  -> H3 {'RED' if h3_red else 'AYAKTA'}")
    print(f"\nYazildi: {CIKTI}")
    print("\nUYARI: bu bir OLCUMDUR, strateji degildir. Uc hipotezin "
          "hepsi RED gelirse swing projesi ACILMAZ.")


if __name__ == "__main__":
    main()
