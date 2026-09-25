"""
BILESIK UYUM SKORU v3 - SEKTOR KAPSAMI GENISLETILMIS (25.09.2026)
====================================================================
v2 + Demir-Celik sektoru (EREGL+KRDMD, kullanici talebi: "genisletelim").
KRDMD SEMBOLLER disinda, yalniz sektor-gucu YARDIMCISI. Elektrik
Ekipmani (6 uye beklenen, yalniz ASTOR biliniyor) BILEREK eklenmedi -
eksik uyelikle yanlis sektor gucu vermek eklemek yerine EKSIK
birakmaktan kotu olurdu. PGSUS/SISE/EKGYO/TRMET/AEFES/ALARK icin
sektor/KGS hala hesaplanamiyor.
============================================================
Onceki surumun (bilesik_uyum_skoru.py) DUZELTILMIS hali. Kullanicinin
kendi gozlemi dogruydu: 60-gunluk getiri ve 52-hafta zirve yakinligi
BAGIMSIZ degildi - ikisi de "son donem gucu"nun farkli olculeriydi,
en dusuk 5 skor pratikte "en cok yukselen 5" ile ayniydi.

DEGISIKLIKLER:
1. 60-gunluk getiri bileseni KALDIRILDI - yalniz 52-hafta zirve
   yakinligi kullaniliyor (rejim-kosullu testte DAHA GUCLU kanit
   bulunan, dolayisiyla TERCIH EDILEN olcu).
2. YENI: KGS KALITE KONTROLU eklendi - kgs_gunluk_port.py'nin ZATEN
   var olan KGS hesabi kullanilarak. MANTIK: fiyat zayifligi (dip)
   ARANAN sey, ama KGS'nin de (trend/hacim/kurumsal saglik) COK
   dusuk OLMAMASI gerekir - aksi halde bu "saglikli bir duzeltme"
   degil, "gercekten bozulan bir hisse" olabilir. KGS ORTA-YUKSEK +
   fiyat zirveden uzak = "saglikli dip". KGS DUSUK + fiyat zirveden
   uzak = "riskli, dikkatli ol" (ayri bir uyari bayragi olarak
   isaretleniyor, skoru DUSURMUYOR ama GORUNUR kiliniyor).
3. Sektor gucu bileseni KORUNDU (genuinely bagimsiz, cross-sectional).

KIRMIZI CIZGI: SALT OLCUM/TARAMA. Pine'a dokunmuyor, alarm uretmiyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi. Bu bir BACKTEST DEGIL. KGS
esigi (40) sezgisel secildi, ayrica optimize EDILMEDI - "cok dusuk KGS"
icin kaba bir uyari cizgisi.

Cikti: data/backtest/bilesik_uyum_skoru_v3_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler, kgs_hesapla, ENDEKS

SEKTORLER = {
    "Banka": ["AKBNK", "GARAN", "ISCTR", "YKBNK", "HALKB", "VAKBN"],
    "Holding": ["KCHOL", "SAHOL", "ENKAI"],
    "Savunma": ["ASELS", "OTKAR"],
    "Rafineri": ["TUPRS", "PETKM"],
    "EnerjiUretim": ["ENJSA", "AKSEN"],
    "Otomotiv": ["FROTO", "TOASO"],
    "Telekom": ["TCELL", "TTKOM"],
    "Ulastirma": ["THYAO", "TAVHL"],
    "Tuketim": ["BIMAS", "MGROS", "ULKER"],
    "DemirCelik": ["EREGL", "KRDMD"],
}
SEMBOL_SEKTOR = {s: sek for sek, uyeler in SEKTORLER.items() for s in uyeler}
FORMASYON_GUN_SEKTOR = 20
PENCERE_52H = 252
KGS_DUSUK_UYARI_ESIGI = 40


def main():
    xu = veri_cek(ENDEKS, start="2018-06-01")
    xu_ema60 = xu["Close"].ewm(span=60, adjust=False).mean()
    xu_ret20 = xu["Close"].pct_change(FORMASYON_GUN_SEKTOR) * 100
    guncel_rejim = "RISK_ON" if float(xu["Close"].iloc[-1]) > float(xu_ema60.iloc[-1]) else "RISK_OFF"
    agirlik_52h = 0.65 if guncel_rejim == "RISK_OFF" else 0.40
    agirlik_sektor = 1.0 - agirlik_52h

    # 25.09 GENISLETME (kullanici talebi): ham artik SEMBOLLER + TUM
    # sektor uyelerinin BIRLESIMI - boylece KRDMD gibi SEMBOLLER'de
    # olmayan ama sektor gucu hesabi icin gereken yardimci semboller de
    # cekiliyor. Nihai CIKTI (sonuclar) yine yalniz SEMBOLLER ile
    # SINIRLI - KRDMD kullaniciya puanli olarak gosterilmiyor, yalniz
    # EREGL'in sektor gucunu dogru hesaplamaya yariyor.
    tum_cekilecek = sorted(set(SEMBOLLER) | set(s for uyeler in SEKTORLER.values() for s in uyeler))
    ham = {}
    for s in tum_cekilecek:
        d = veri_cek(f"{s}.IS", start="2018-06-01")
        if d is not None and len(d) > 300:
            ham[s] = gostergeler(d)

    # sektor gucu (bugun)
    rel_ret = {s: (df["Close"].pct_change(FORMASYON_GUN_SEKTOR) * 100) - xu_ret20.reindex(df.index).ffill()
               for s, df in ham.items() if s in SEMBOL_SEKTOR}
    sektor_guc_bugun = {}
    for sek, uyeler in SEKTORLER.items():
        degerler = [rel_ret[s].iloc[-1] for s in uyeler if s in rel_ret and not pd.isna(rel_ret[s].iloc[-1])]
        if degerler:
            sektor_guc_bugun[sek] = float(np.mean(degerler))
    sektor_sira = sorted(sektor_guc_bugun, key=lambda k: sektor_guc_bugun[k])
    sektor_percentile = {sek: 100 * i / max(len(sektor_sira) - 1, 1) for i, sek in enumerate(sektor_sira)}

    # KGS icin sektor-getiri serisi gerekiyor (kgs_hesapla imzasi) - ayni
    # sektor eslemesini kullanip her sembol icin kendi sektorunun GUNLUK
    # (rolling degil, basit) getiri serisini turetiyoruz
    sektor_gunluk_getiri = {}
    for sek, uyeler in SEKTORLER.items():
        seriler = [ham[s]["Close"].pct_change() for s in uyeler if s in ham]
        if seriler:
            sektor_gunluk_getiri[sek] = pd.concat(seriler, axis=1).mean(axis=1) * 100
    idx_roc_gunluk = xu["Close"].pct_change() * 100

    sonuclar = []
    for s, df in ham.items():
        if s not in SEMBOLLER:
            continue  # yalniz sektor-gucu yardimcisi (orn. KRDMD), kullaniciya puanli gosterilmiyor
        close_bugun = float(df["Close"].iloc[-1])

        # 1) 52-hafta zirveye uzaklik
        zirve_252 = df["High"].rolling(PENCERE_52H, min_periods=200).max()
        yakinlik_bugun = float(close_bugun / zirve_252.iloc[-1]) if not pd.isna(zirve_252.iloc[-1]) else None
        uzaklik_pct = round((1 - yakinlik_bugun) * 100, 2) if yakinlik_bugun is not None else None

        # 2) sektor gucu percentile
        sek = SEMBOL_SEKTOR.get(s)
        sektor_pct = sektor_percentile.get(sek) if sek else None

        # 3) KGS kalite kontrolu
        kgs_bugun = None
        if sek and sek in sektor_gunluk_getiri:
            sec_roc = sektor_gunluk_getiri[sek].reindex(df.index)
            sec_strong = (sec_roc > idx_roc_gunluk.reindex(df.index) + 0.5).fillna(False)
            try:
                kgs_df = kgs_hesapla(df, idx_roc_gunluk, sec_roc, sec_strong)
                kgs_bugun = float(kgs_df["kgs"].iloc[-1]) if not pd.isna(kgs_df["kgs"].iloc[-1]) else None
            except Exception:
                kgs_bugun = None

        puan_52h = min(uzaklik_pct * 3, 100) if uzaklik_pct is not None else None
        puan_sektor = (100 - sektor_pct) if sektor_pct is not None else None

        bilesenler = []
        if puan_52h is not None:
            bilesenler.append((puan_52h, agirlik_52h))
        if puan_sektor is not None:
            bilesenler.append((puan_sektor, agirlik_sektor))
        toplam_agirlik = sum(a for p, a in bilesenler)
        bilesik_skor = round(sum(p * a for p, a in bilesenler) / toplam_agirlik, 1) if toplam_agirlik > 0 else None

        kgs_uyari = (kgs_bugun is not None and kgs_bugun < KGS_DUSUK_UYARI_ESIGI)

        sonuclar.append({
            "sembol": s, "sektor": sek, "guncel_fiyat": round(close_bugun, 2),
            "zirve52h_uzaklik_pct": uzaklik_pct,
            "sektor_guc_percentile": round(sektor_pct, 1) if sektor_pct is not None else None,
            "kgs_bugun": round(kgs_bugun, 1) if kgs_bugun is not None else None,
            "bilesik_uyum_skoru": bilesik_skor,
            "KGS_DUSUK_UYARI": kgs_uyari,
        })

    sonuclar.sort(key=lambda x: -(x["bilesik_uyum_skoru"] or -1))

    rapor = {
        "calisma": "Bilesik Uyum Skoru v3 - KGS Kalite Kontrollu",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "guncel_rejim": guncel_rejim,
        "kullanilan_agirliklar": {"zirve52h_uzakligi": agirlik_52h, "sektor_zayifligi": round(agirlik_sektor, 2)},
        "v2den_degisiklik": (
            "Demir-Celik sektoru eklendi (EREGL+KRDMD) - kullanici "
            "talebiyle sektor kapsami genisletildi. KRDMD SEMBOLLER "
            "disinda oldugu icin yalniz sektor-gucu YARDIMCISI olarak "
            "cekildi, kendisi PUANLI olarak listelenmiyor."
        ),
        "kapsam_durumu": (
            "9/11 sektor -> simdi 10/11 (Demir-Celik eklendi). Elektrik "
            "Ekipmani sektoru (6 uye beklenen, yalniz ASTOR guvenle "
            "biliniyor) HALA EKSIK - yanlis/eksik uyelikle sektor "
            "ortalamasi bozulmasin diye eklenmedi. PGSUS, SISE, EKGYO, "
            "TRMET, AEFES, ALARK icin sektor/KGS HALA hesaplanamiyor - "
            "bu isimlerin GERCEK sektor uyeligi bu oturumda guvenle "
            "dogrulanamadi."
        ),
        "durustluk_notu": (
            "Bu BIR BACKTEST DEGIL - tarama. KGS esigi (40) sezgisel, "
            "ayrica optimize edilmedi. Kompozit skorun kendisi ileri-"
            "getiri testine AYRICA tabi tutulmadi."
        ),
        "siralama_en_yuksek_uyumdan": sonuclar,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/bilesik_uyum_skoru_v3_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"Guncel rejim: {guncel_rejim} (agirliklar: 52h={agirlik_52h}, sektor={agirlik_sektor:.2f})")
    print("\nEn yuksek uyum skorlu 10 sembol:")
    for r in sonuclar[:10]:
        uyari = " ⚠KGS DUSUK" if r["KGS_DUSUK_UYARI"] else ""
        print(f"  {r['sembol']:8s} skor={r['bilesik_uyum_skoru']:>5} sektor={str(r['sektor']):14s} "
              f"52h_uzaklik={r['zirve52h_uzaklik_pct']:>6} KGS={r['kgs_bugun']}{uyari}")
    print("\nTamamlandi -> data/backtest/bilesik_uyum_skoru_v3_sonuc.json")


if __name__ == "__main__":
    main()
