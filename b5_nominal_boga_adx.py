"""
B5 FAZ V0: NOMINAL BOGA REJIM - ADX DIRENC TESTI (17.09.2026)
================================================================
KULUCKA SONRASI BIRIKIM B5: "Nominal boga rejim yamasi" (İP-2 K5).
Test plani: "ADX/genislik kosullu OFF-direnci; İP-2 tekrar kosumu
2021-22 kiyasi".

BULUNAN KOD (V162_1_yama.txt satir 1027):
  marketRiskOn = xu100Close > xu100Ema50
TEK KOSUL - fiyat gecici olarak EMA50 altina sarkarsa (2021-22 gibi
enflasyonist/oynak bir yukseliste sik olur), sistem RISK-OFF'a
geciyor, _p3RejimUygun uzerinden TUM P3 sinyalleri kapaniyor.

ONERI: marketRiskOn = xu100Close > xu100Ema50 OR xu100Adx >= esik
(ADX guclu trend gosteriyorsa, EMA50 alti gecici sarkmaya ragmen
RISK-ON'da KAL).

V0 KISITI (durustluk notu): yalniz ADX direnci test edildi. GENISLIK
(breadth - evrendeki hisselerin kaci kendi ortalamasinin ustunde)
BURADA YOK - tek-sembol Pine gostergesi 30 sembolun HEPSI icin ayri
request.security gerektirir, bu V0'in kapsami disinda. Sadece XU100'un
KENDI ADX'i kullanildi.

TEST: 2021-2022 XU100 gunluk verisinde, "mevcut kural RISK-OFF derdi
ama ADX>=esik oldugu icin B5 ONERISI RISK-ON'da tutardi" gunlerinin
ileri getirisi ("KURTARILAN" grup) ile "ikisi de RISK-OFF" gunlerinin
ileri getirisi ("GERCEK OFF" grubu) karsilastirilir. KURTARILAN grup
belirgin pozitifse (boga devam ediyor demektir), B5 destekli olur.

KIRMIZI CIZGI: SALT OLCUM. Pine'a dokunmuyor.

Cikti: data/backtest/b5_nominal_boga_adx_sonuc.json
"""
import json
import sys
import datetime

import numpy as np
import pandas as pd

from kgs_gunluk_port import veri_cek, ENDEKS

ADX_LEN = 14
ADX_ESIK_LISTESI = [20, 25, 30]  # birden fazla esik denenip en anlamlisi gorulsun
DONEM_BAS, DONEM_SON = "2021-01-01", "2022-12-31"
ILERI_GUNLER = [3, 10, 20]  # 20 eklendi - rejim/trend sorusu daha uzun ufuk da ister


def adx_hesapla(df, n=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    up = high.diff()
    down = -low.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di) * 100
    adx = dx.ewm(alpha=1 / n, adjust=False).mean()
    return adx


def ileri_getiri(close, n):
    return (close.shift(-n) / close - 1) * 100


def islem_ozet(getiriler):
    g = [x for x in getiriler if not np.isnan(x)]
    if not g:
        return {"gun_sayisi": 0, "isabet_pct": None, "ort_getiri_pct": None}
    return {
        "gun_sayisi": len(g),
        "isabet_pct": round(100 * float(np.mean([x > 0 for x in g])), 1),
        "ort_getiri_pct": round(float(np.mean(g)), 3),
    }


def main():
    d = veri_cek(ENDEKS, start="2018-01-01")
    if d is None:
        print("HATA: XU100 verisi cekilemedi", file=sys.stderr)
        return

    d = d.copy()
    d["ema50"] = d["Close"].ewm(span=50, adjust=False).mean()
    d["adx"] = adx_hesapla(d, ADX_LEN)
    d["riskOn_eski"] = d["Close"] > d["ema50"]

    donem_mask = (d.index >= DONEM_BAS) & (d.index <= DONEM_SON)

    sonuclar = {}
    for esik in ADX_ESIK_LISTESI:
        riskOn_yeni = d["riskOn_eski"] | (d["adx"] >= esik)
        kurtarilan_mask = (~d["riskOn_eski"]) & (d["adx"] >= esik) & donem_mask
        gercekOff_mask = (~d["riskOn_eski"]) & (d["adx"] < esik) & donem_mask

        kurtarilan = {}
        gercekOff = {}
        for n in ILERI_GUNLER:
            g = ileri_getiri(d["Close"], n)
            kurtarilan[f"t{n}"] = islem_ozet(g[kurtarilan_mask].dropna().tolist())
            gercekOff[f"t{n}"] = islem_ozet(g[gercekOff_mask].dropna().tolist())

        sonuclar[f"adx_esik_{esik}"] = {
            "kurtarilan_gun_sayisi": int(kurtarilan_mask.sum()),
            "gercek_off_gun_sayisi": int(gercekOff_mask.sum()),
            "kurtarilan": kurtarilan,
            "gercek_off": gercekOff,
        }
        print(f"ADX>={esik}: kurtarilan={int(kurtarilan_mask.sum())} gun, "
              f"gercek_off={int(gercekOff_mask.sum())} gun, "
              f"kurtarilan T+10 isabet={kurtarilan['t10']['isabet_pct']}, "
              f"gercek_off T+10 isabet={gercekOff['t10']['isabet_pct']}")

    # 2021-2022 tum donem ozeti (RISK-OFF gun sayisi eski vs yeni kural)
    donem_riskOff_eski = int((~d.loc[donem_mask, "riskOn_eski"]).sum())
    donem_gun_toplam = int(donem_mask.sum())

    rapor = {
        "calisma": "B5 Faz V0 - Nominal Boga Rejim ADX Direnc Testi",
        "uretim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "durustluk_notu": (
            "Yalniz ADX direnci test edildi, GENISLIK (breadth) V0 kapsami "
            "disinda - 30 sembolun hepsi icin ayri request.security gerektirir. "
            "TEK BASINA hicbir kod degisikligine GEREKCE OLAMAZ - B5'in ilk "
            "kesif adimidir."
        ),
        "donem": f"{DONEM_BAS} - {DONEM_SON}",
        "donem_toplam_gun": donem_gun_toplam,
        "donem_riskOff_gun_eski_kural": donem_riskOff_eski,
        "donem_riskOff_oran_eski_kural_pct": round(100 * donem_riskOff_eski / donem_gun_toplam, 1),
        "adx_esik_bazli": sonuclar,
    }

    import os
    os.makedirs("data/backtest", exist_ok=True)
    with open("data/backtest/b5_nominal_boga_adx_sonuc.json", "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print("\nTamamlandi -> data/backtest/b5_nominal_boga_adx_sonuc.json")


if __name__ == "__main__":
    main()
