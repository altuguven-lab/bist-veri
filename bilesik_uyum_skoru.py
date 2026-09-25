"""
BILESIK UYUM SKORU - HISSE BAZINDA TARAMA (25.09.2026)
=========================================================
Bugunku oturumda dogrulanan bulgulari (backtest DEGIL, BUGUNKU ANLIK
GORUNTUYE uygulanan bir TARAYICI) birlestirip takip edilen evreni
puanlar. Sadece DOGRULANMIS, kod degisikligi onerilmeyen ama gercek
istatistiksel destegi olan bulgular kullaniliyor:

1. 60-GUNLUK GETIRI PERCENTILE (dip vs kovalama testi, formasyon
   penceresi taramasi - 60 gunde mean-reversion T+10'da net kazandi,
   sembol tutarliligi %66,7). DUSUK percentile (dip) = OLUMLU.

2. SEKTOR GUCU (sektor momentumu testi - ZAYIF sektor T+10'da HER IKI
   rejimde de kazandi, genel/yapisal bir bulgu). ZAYIF sektor = OLUMLU.

3. 52-HAFTA ZIRVEYE UZAKLIK (rejim-kosullu test - guclu etki ozellikle
   RISK-OFF'ta, su anki rejimde). UZAK = OLUMLU (rejime gore agirlik
   degisir - RISK-OFF'ta bu sinyal cok daha guclu agirliklandirilir).

Sistem GUNCEL rejimi (RISK-ON/RISK-OFF) kendisi tespit edip agirliklari
ona gore ayarliyor.

KIRMIZI CIZGI: SALT OLCUM/TARAMA. Pine'a dokunmuyor, alarm uretmiyor.
DURUSTLUK NOTU: GUNLUK BAR yaklasikligi. Bu bir BACKTEST DEGIL - bugunku
anlik goruntuye gecmiste dogrulanmis orguntuleri uygulayan bir tarayici.
Kompozit skor KENDI ICINDE yeni bir hipotez - AYRI olarak ileri-getiri
testine tabi TUTULMADI (bu, dogal bir sonraki adim olabilir).
Sektor kapsam sinirlamasi onceki testlerle AYNI (9/11 sektor, 21 hisse) -
sektor disi semboller icin yalniz 1. ve 3. bilesen kullanilir.

Cikti: data/backtest/bilesik_uyum_skoru_sonuc.json
"""
import json
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import SEMBOLLER, veri_cek, gostergeler, ENDEKS

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
}
SEMBOL_SEKTOR = {s: sek for sek, uyeler in SEKTORLER.items() for s in uyeler}
FORMASYON_GUN_SEKTOR = 20
PENCERE_52H = 252


def main():
    xu = veri_cek(ENDEKS, start="2018-06-01")
    xu_ema60 = xu["Close"].ewm(span=60, adjust=False).mean()
    xu_ret20 = xu["Close"].pct_change(FORMASYON_GUN_SEKTOR) * 100
    guncel_rejim = "RISK_ON" if float(xu["Close"].iloc[-1]) > float(xu_ema60.iloc[-1]) else "RISK_OFF"
    # RISK-OFF'ta 52h-zirve sinyali COK daha guclu dogrulanmisti - agirlik ona gore
    agirlik_52h = 0.45 if guncel_rejim == "RISK_OFF" else 0.20
    agirlik_60g = 0.35
    agirlik_sektor = 1.0 - agirlik_52h - agirlik_60g  # sektor kapsami olanlar icin

    ham = {}
    for s in SEMBOLLER:
        d = veri_cek(f"{s}.IS", start="2018-06-01")
        if d is not None and len(d) > 300:
            ham[s] = gostergeler(d)

    # sektor gucu (yalniz kapsanan semboller icin)
    rel_ret = {s: (df["Close"].pct_change(FORMASYON_GUN_SEKTOR) * 100) - xu_ret20.reindex(df.index).ffill()
               for s, df in ham.items() if s in SEMBOL_SEKTOR}
    sektor_guc_bugun = {}
    for sek, uyeler in SEKTORLER.items():
        degerler = [rel_ret[s].iloc[-1] for s in uyeler if s in rel_ret and not pd.isna(rel_ret[s].iloc[-1])]
        if degerler:
            sektor_guc_bugun[sek] = float(np.mean(degerler))
    sektor_sira = sorted(sektor_guc_bugun, key=lambda k: sektor_guc_bugun[k])  # en zayiftan en gucluye
    sektor_percentile = {sek: 100 * i / max(len(sektor_sira) - 1, 1) for i, sek in enumerate(sektor_sira)}  # 0=en zayif

    sonuclar = []
    for s, df in ham.items():
        close_bugun = float(df["Close"].iloc[-1])

        # 1) 60-gunluk getiri percentile (kendi 7-yillik tarihine gore)
        ret60_serisi = df["Close"].pct_change(60) * 100
        ret60_bugun = float(ret60_serisi.iloc[-1]) if not pd.isna(ret60_serisi.iloc[-1]) else None
        ret60_percentile = float((ret60_serisi.dropna() < ret60_bugun).mean() * 100) if ret60_bugun is not None else None

        # 2) sektor gucu percentile (0=en zayif sektor=olumlu, 100=en guclu)
        sek = SEMBOL_SEKTOR.get(s)
        sektor_pct = sektor_percentile.get(sek) if sek else None

        # 3) 52-hafta zirveye uzaklik
        zirve_252 = df["High"].rolling(PENCERE_52H, min_periods=200).max()
        yakinlik_bugun = float(close_bugun / zirve_252.iloc[-1]) if not pd.isna(zirve_252.iloc[-1]) else None
        uzaklik_pct = round((1 - yakinlik_bugun) * 100, 2) if yakinlik_bugun is not None else None

        # bilesik skor: her bilesen icin DUSUK deger (dip/zayif sektor/zirveden uzak) = YUKSEK puan
        puan_60g = (100 - ret60_percentile) if ret60_percentile is not None else None
        puan_sektor = (100 - sektor_pct) if sektor_pct is not None else None
        puan_52h = min(uzaklik_pct * 3, 100) if uzaklik_pct is not None else None  # %33+ uzaklik = tavan puan

        bilesenler = [(puan_60g, agirlik_60g)]
        if puan_sektor is not None:
            bilesenler.append((puan_sektor, agirlik_sektor))
        if puan_52h is not None:
            bilesenler.append((puan_52h, agirlik_52h))
        toplam_agirlik = sum(a for p, a in bilesenler if p is not None)
        bilesik_skor = round(sum(p * a for p, a in bilesenler if p is not None) / toplam_agirlik, 1) if toplam_agirlik > 0 else None

        sonuclar.append({
            "sembol": s, "sektor": sek, "guncel_fiyat": round(close_bugun, 2),
            "ret60g_pct": round(ret60_bugun, 2) if ret60_bugun is not None else None,
            "ret60g_percentile": round(ret60_percentile, 1) if ret60_percentile is not None else None,
            "sektor_guc_percentile": round(sektor_pct, 1) if sektor_pct is not None else None,
            "zirve52h_uzaklik_pct": uzaklik_pct,
            "bilesik_uyum_skoru": bilesik_skor,
        })

    sonuclar.sort(key=lambda x: -(x["bilesik_uyum_skoru"] or -1))

    rapor = {
        "calisma": "Bilesik Uyum Skoru - Hisse Bazinda Tarama",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "guncel_rejim": guncel_rejim,
        "kullanilan_agirliklar": {"60gun_dip": agirlik_60g, "sektor_zayifligi": round(agirlik_sektor, 2), "zirve52h_uzakligi": agirlik_52h},
        "durustluk_notu": (
            "Bu BIR BACKTEST DEGIL - bugunku anlik goruntuye gecmiste "
            "dogrulanmis orguntuleri uygulayan bir TARAMA. Kompozit skorun "
            "kendisi ileri-getiri testine AYRICA tabi TUTULMADI. Sektor "
            "kapsami 21/30 sembol (9/11 sektor) - kapsam disi semboller "
            "icin sektor bileseni HARIC tutulup agirlik digerlerine "
            "dagitilir."
        ),
        "siralama_en_yuksek_uyumdan": sonuclar,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/bilesik_uyum_skoru_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"Guncel rejim: {guncel_rejim} (agirliklar: 60g={agirlik_60g}, sektor={agirlik_sektor:.2f}, 52h={agirlik_52h})")
    print("\nEn yuksek uyum skorlu 10 sembol:")
    for r in sonuclar[:10]:
        print(f"  {r['sembol']:8s} skor={r['bilesik_uyum_skoru']:>5} sektor={r['sektor'] or '-':14s} "
              f"60g_pct={r['ret60g_percentile']} 52h_uzaklik={r['zirve52h_uzaklik_pct']}")
    print("\nTamamlandi -> data/backtest/bilesik_uyum_skoru_sonuc.json")


if __name__ == "__main__":
    main()
