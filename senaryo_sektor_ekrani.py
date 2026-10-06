"""
SENARYO x SEKTOR EKRANI (06.10.2026)
=====================================================================
Soru (Baskan, 06.10.2026): "Fon krizi cozumlenmeye basliyor + TCMB bu ay
faiz indirimine basliyor + Kasim'da Iran savasi anlasma yoluna giriyor"
senaryosunda en guclu 3 sektor ve bu sektorlerdeki en guclu hisseler?

BU BETIK NE YAPAR (SALT OLCUM - Pine'a dokunmaz, alarm uretmez):
  A) 30 sembol + sektor endeksleri + XU100 icin yfinance gunluk veriden
     OLCULEBILIR seyleri hesaplar: 1/3/6 ay getiri, XU100'e goreli getiri,
     52 hafta zirveye uzaklik, 50/200 gun ort. durumu, 20 gun ort. gunluk
     TL hacim (likidite/dusuk-float bayragi), FON KRIZI ONCESI (16.09.2026)
     kapanisina gore getiri ve o tarihten beri dip->bugun toparlanma.
  B) yfinance .info'dan degerleme alanlarini (F/K, ileri F/K, PD/DD,
     piyasa degeri, temettu verimi) DENER - gelmezse None yazar.
  C) data/dusuk_teyit_gozlem.json defterinden sistemin son gunluk
     skor/kgs/rejim okumasini ekler (varsa).
  D) Senaryo duyarliligi: SENARYO_DUYARLILIK sabitindeki (ASAGIDA, ELLE
     DUZENLENEBILIR) -2..+2 puanlarini ayak agirliklariyla toplar.
Cikti: data/senaryo_ekrani/senaryo_sektor_ekrani.json + .md

DURUSTLUK NOTU (okumadan once):
  - SENARYO_DUYARLILIK puanlari OLCUM DEGILDIR; yapisal/nitel yargidir
    (makro_hassasiyet_haritasi.json mantigiyla, yon: faiz indirimi,
    petrol dusus, risk istahi). Betik bu puanlari DOGRULAMAZ. Siz farkli
    dusunuyorsaniz sabiti degistirin, ekran yeniden hesaplanir.
  - Betik tek bir "kazanan skoru" URETMEZ: duyarlilik (varsayim) ile
    olculen momentum/toparlanma (veri) YAN YANA gosterilir, ayri sutunlar.
    Sirayi birlestirmek bir yargi kararidir, hesap degil.
  - Gecmis momentum gelecegi garanti etmez; faiz indirimi beklentisi
    banka endeksine zaten kismen yansimis olabilir (momentum bunu
    gosterir ama "fiyatlandi mi" sorusunu CEVAPLAMAZ).
  - yfinance .info alanlari guvenilmez/bos olabilir; degerleme sutunlari
    YALNIZCA ipucudur. Banka/holding icin F/K tek basina anlamsizdir.
  - Sistemin skor/kgs/rejim degerleri kulucka doneminde "hukumsuz"
    kapanmistir (05.10.2026); kanit degil baglamdir.
  - Bu bir AL/SAT tavsiyesi degildir.
"""
import json
import os
import sys
import time
import datetime

import numpy as np
import pandas as pd

CIKTI_KLASOR = "data/senaryo_ekrani"
DEFTER_YOL = "data/dusuk_teyit_gozlem.json"
BASLANGIC = "2025-09-01"
KRIZ_ONCESI_TARIH = "2026-09-16"   # SPK fon tasfiyesi 17.09.2026'da basladi
GUN = {"1a": 21, "3a": 63, "6a": 126}

SEKTOR = {
    "AKBNK": "BANKACILIK", "YKBNK": "BANKACILIK", "GARAN": "BANKACILIK",
    "ISCTR": "BANKACILIK", "HALKB": "BANKACILIK", "VAKBN": "BANKACILIK",
    "KCHOL": "HOLDING", "SAHOL": "HOLDING",
    "BIMAS": "PERAKENDE", "MGROS": "PERAKENDE",
    "ASELS": "SAVUNMA",
    "THYAO": "HAVACILIK", "PGSUS": "HAVACILIK", "TAVHL": "HAVACILIK",
    "TTKOM": "ILETISIM",
    "EREGL": "SINAI", "SISE": "SINAI", "TRMET": "SINAI",
    "TUPRS": "ENERJI", "PETKM": "ENERJI", "ASTOR": "ENERJI", "ENJSA": "ENERJI",
    "ENKAI": "INSAAT",
    "EKGYO": "GYO",
    "FROTO": "OTOMOTIV", "TOASO": "OTOMOTIV", "OTKAR": "OTOMOTIV",
    "AEFES": "GENEL", "ALARK": "GENEL", "ULKER": "GENEL",
}
SEKTOR_ENDEKS = {
    "BANKACILIK": "XBANK.IS", "HOLDING": "XHOLD.IS", "PERAKENDE": "XGIDA.IS",
    "SAVUNMA": "XUSIN.IS", "HAVACILIK": "XULAS.IS", "ILETISIM": "XILTM.IS",
    "SINAI": "XMANA.IS", "ENERJI": "XELKT.IS", "INSAAT": "XINSA.IS",
    "GYO": "XGMYO.IS", "OTOMOTIV": "XMESY.IS",
}
ENDEKS = "XU100.IS"

# ---------------------------------------------------------------------------
# ELLE DUZENLENEBILIR VARSAYIMLAR (OLCUM DEGIL - bkz. durustluk notu)
# Ayaklar: (fon_krizi_cozumu, faiz_indirimi, iran_anlasmasi_petrol_dusus)
# Puan: -2 (guclu olumsuz) .. +2 (guclu olumlu)
AYAK_AGIRLIK = (1.0, 1.0, 1.0)
SEKTOR_DUYARLILIK = {
    "BANKACILIK": (2, 2, 1),   # guven + faiz indirimi + TL risk primi dususu
    "HOLDING":    (2, 1, 0),   # NAV iskontosu/risk istahi; TUPRS iştiraki barista negatif
    "HAVACILIK":  (1, 0, 2),   # yakit + rota/jeopolitik risk dususu
    "GYO":        (1, 2, 0),   # borclanma maliyeti, konut talebi
    "INSAAT":     (1, 1, 1),   # faiz + Ortadogu proje portfoyu
    "OTOMOTIV":   (1, 1, 0),   # tasit kredisi (ihracat tarafi ayri duyarli)
    "PERAKENDE":  (1, 1, 0),   # tuketim/kredi
    "SINAI":      (0, 0, 1),   # enerji maliyeti dususu (EREGL/SISE)
    "ILETISIM":   (0, 0, 0),
    "ENERJI":     (0, 0, 0),   # hisse bazinda ASAGIDA
    "SAVUNMA":    (0, 0, -1),  # jeopolitik prim cozulmesi
    "GENEL":      (0, 0, 0),   # hisse bazinda ASAGIDA
}
HISSE_DUYARLILIK_ISTISNA = {
    "TUPRS": (0, 0, -2),   # rafineri marji savas primiyle sismis, barista normallesir
    "PETKM": (0, 0, 0),    # girdi maliyeti dusuyor ama urun fiyati da dusuyor: belirsiz
    "ASTOR": (0, 0, -1),   # jeopolitik/enerji altyapisi temasi
    "ENJSA": (0, 1, 0),    # sermaye yogun, borclanma maliyeti
    "ALARK": (0, 1, 0),
    "ULKER": (0, 1, 0),
    "AEFES": (0, 0, 0),
}
# ---------------------------------------------------------------------------


def veri_cek(ticker):
    import yfinance as yf
    try:
        df = yf.download(ticker, start=BASLANGIC, interval="1d",
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        return df if not df.empty else None
    except Exception as e:
        print(f"UYARI: {ticker} -> {e}", file=sys.stderr)
        return None


def bilgi_cek(ticker):
    """yfinance .info degerleme alanlari - gelmezse None."""
    import yfinance as yf
    alanlar = {"fk": "trailingPE", "ileri_fk": "forwardPE", "pd_dd": "priceToBook",
               "piyasa_degeri": "marketCap", "temettu_verimi": "dividendYield"}
    cikti = {k: None for k in alanlar}
    try:
        info = yf.Ticker(ticker).info or {}
        for k, a in alanlar.items():
            v = info.get(a)
            if isinstance(v, (int, float)) and np.isfinite(v):
                cikti[k] = float(v)
    except Exception as e:
        print(f"UYARI(info): {ticker} -> {e}", file=sys.stderr)
    return cikti


def getiri(close, n):
    if len(close) <= n:
        return None
    return float(close.iloc[-1] / close.iloc[-1 - n] - 1) * 100


def metrikler(df, xu_getiri):
    c = df["Close"].astype(float)
    m = {"son_fiyat": float(c.iloc[-1]), "son_tarih": str(c.index[-1].date())}
    for ad, n in GUN.items():
        g = getiri(c, n)
        m[f"getiri_{ad}_pct"] = None if g is None else round(g, 2)
        xg = xu_getiri.get(ad)
        m[f"goreli_{ad}_pct"] = None if (g is None or xg is None) else round(g - xg, 2)
    son252 = c.iloc[-252:]
    m["zirveden_uzaklik_pct"] = round(float(c.iloc[-1] / son252.max() - 1) * 100, 2)
    ma50 = c.rolling(50).mean().iloc[-1] if len(c) >= 50 else np.nan
    ma200 = c.rolling(200).mean().iloc[-1] if len(c) >= 200 else np.nan
    m["ustunde_ma50"] = None if np.isnan(ma50) else bool(c.iloc[-1] > ma50)
    m["ma50_ustunde_ma200"] = None if (np.isnan(ma50) or np.isnan(ma200)) else bool(ma50 > ma200)
    # fon krizi oncesi (<= 16.09.2026) referansi
    onc = c[c.index <= pd.Timestamp(KRIZ_ONCESI_TARIH)]
    if len(onc) > 0:
        base = float(onc.iloc[-1])
        m["kriz_oncesi_fiyat"] = round(base, 3)
        m["kriz_oncesine_gore_pct"] = round((float(c.iloc[-1]) / base - 1) * 100, 2)
        sonra = c[c.index > pd.Timestamp(KRIZ_ONCESI_TARIH)]
        if len(sonra) > 0:
            dip = float(sonra.min())
            m["kriz_sonrasi_dip_pct"] = round((dip / base - 1) * 100, 2)
            m["dipten_toparlanma_pct"] = round((float(c.iloc[-1]) / dip - 1) * 100, 2)
    if "Volume" in df.columns:
        tl_hacim = (df["Close"] * df["Volume"]).iloc[-20:].mean()
        m["ort_gunluk_hacim_tl_20g_milyon"] = round(float(tl_hacim) / 1e6, 1)
    return m


def sistem_okumasi():
    if not os.path.exists(DEFTER_YOL):
        return {}
    try:
        d = json.load(open(DEFTER_YOL, encoding="utf-8"))
    except Exception:
        return {}
    cikti = {}
    for s, liste in d.get("gunluk_kapanis_defteri", {}).items():
        if liste:
            k = liste[-1]
            cikti[s] = {"sistem_skor": k.get("skor"), "sistem_kgs": k.get("kgs"),
                        "sistem_rejim": k.get("rejim"), "sistem_tarih": k.get("tarih")}
    return cikti


def duyarlilik(sembol):
    p = HISSE_DUYARLILIK_ISTISNA.get(sembol) or SEKTOR_DUYARLILIK[SEKTOR[sembol]]
    return round(sum(a * b for a, b in zip(AYAK_AGIRLIK, p)), 2), p


def medyan(liste):
    v = [x for x in liste if x is not None]
    return round(float(np.median(v)), 2) if v else None


def main():
    os.makedirs(CIKTI_KLASOR, exist_ok=True)
    xu = veri_cek(ENDEKS)
    if xu is None:
        print("HATA: XU100 verisi alinamadi"); sys.exit(1)
    xu_c = xu["Close"].astype(float)
    xu_getiri = {ad: getiri(xu_c, n) for ad, n in GUN.items()}
    xu_ozet = {"son": round(float(xu_c.iloc[-1]), 2), "son_tarih": str(xu_c.index[-1].date())}
    for ad, g in xu_getiri.items():
        xu_ozet[f"getiri_{ad}_pct"] = None if g is None else round(g, 2)
    onc = xu_c[xu_c.index <= pd.Timestamp(KRIZ_ONCESI_TARIH)]
    if len(onc):
        xu_ozet["kriz_oncesine_gore_pct"] = round((float(xu_c.iloc[-1]) / float(onc.iloc[-1]) - 1) * 100, 2)

    sistem = sistem_okumasi()
    hisseler, eksik = [], []
    for s in SEKTOR:
        df = veri_cek(f"{s}.IS")
        if df is None or len(df) < 70:
            eksik.append(s); continue
        m = metrikler(df, xu_getiri)
        m.update(bilgi_cek(f"{s}.IS")); time.sleep(0.4)
        puan, ayaklar = duyarlilik(s)
        m.update({"sembol": s, "sektor": SEKTOR[s], "senaryo_duyarlilik": puan,
                  "duyarlilik_ayaklari": list(ayaklar)})
        m.update(sistem.get(s, {}))
        hisseler.append(m)

    sektorler = []
    for sek in sorted(set(SEKTOR.values())):
        uyeler = [h for h in hisseler if h["sektor"] == sek]
        if not uyeler:
            continue
        ind = veri_cek(SEKTOR_ENDEKS[sek]) if sek in SEKTOR_ENDEKS else None
        ind_3a = None if ind is None else getiri(ind["Close"].astype(float), GUN["3a"])
        sektorler.append({
            "sektor": sek, "uye_sayisi": len(uyeler),
            "sektor_duyarlilik_ort": round(float(np.mean([h["senaryo_duyarlilik"] for h in uyeler])), 2),
            "medyan_goreli_1a_pct": medyan([h.get("goreli_1a_pct") for h in uyeler]),
            "medyan_goreli_3a_pct": medyan([h.get("goreli_3a_pct") for h in uyeler]),
            "medyan_kriz_oncesine_gore_pct": medyan([h.get("kriz_oncesine_gore_pct") for h in uyeler]),
            "medyan_dipten_toparlanma_pct": medyan([h.get("dipten_toparlanma_pct") for h in uyeler]),
            "sektor_endeksi_3a_pct": None if ind_3a is None else round(ind_3a, 2),
            "uyeler": [h["sembol"] for h in uyeler],
        })
    sektorler.sort(key=lambda r: (-r["sektor_duyarlilik_ort"],
                                  -(r["medyan_goreli_3a_pct"] if r["medyan_goreli_3a_pct"] is not None else -999)))
    hisseler.sort(key=lambda h: (-h["senaryo_duyarlilik"], -(h.get("goreli_3a_pct") if h.get("goreli_3a_pct") is not None else -999)))

    sonuc = {
        "olusturma_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "senaryo": "fon krizi cozumu + TCMB faiz indirimi (Ekim) + Iran anlasmasi (Kasim, petrol dususu)",
        "kriz_oncesi_referans_tarih": KRIZ_ONCESI_TARIH,
        "ayak_agirliklari": list(AYAK_AGIRLIK),
        "xu100": xu_ozet, "sektorler": sektorler, "hisseler": hisseler,
        "veri_alinamayan_semboller": eksik,
        "durustluk_notu": "SENARYO_DUYARLILIK elle yazilmis nitel varsayimdir, olcum degildir; "
                          "momentum/toparlanma/degerleme ayri sutundur ve tek skora INDIRGENMEZ. "
                          "AL/SAT tavsiyesi degildir. Bkz. betik docstring.",
    }
    with open(f"{CIKTI_KLASOR}/senaryo_sektor_ekrani.json", "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)

    def f(v, n=1):
        return "-" if v is None else f"{v:.{n}f}"

    L = ["# Senaryo x Sektor Ekrani", f"Olusturma: {sonuc['olusturma_utc']}",
         f"Senaryo: {sonuc['senaryo']}", "",
         "> Duyarlilik puani ELLE YAZILMIS varsayimdir (olcum degil); momentum/toparlanma/degerleme "
         "veridir ve ayri sutundur. AL/SAT tavsiyesi degildir.", "",
         f"XU100: son {xu_ozet['son']} ({xu_ozet['son_tarih']}) | 1a {f(xu_ozet.get('getiri_1a_pct'))}% | "
         f"3a {f(xu_ozet.get('getiri_3a_pct'))}% | kriz oncesine gore {f(xu_ozet.get('kriz_oncesine_gore_pct'))}%", "",
         "## Sektorler (duyarliliga gore, esitlikte 3a goreli getiri)",
         "| Sektor | Duyarlilik | Med. goreli 1a% | Med. goreli 3a% | Kriz oncesine gore% | Dipten toparlanma% | Sektor endeksi 3a% |",
         "|---|---|---|---|---|---|---|"]
    for r in sektorler:
        L.append(f"| {r['sektor']} | {r['sektor_duyarlilik_ort']:+.1f} | {f(r['medyan_goreli_1a_pct'])} | "
                 f"{f(r['medyan_goreli_3a_pct'])} | {f(r['medyan_kriz_oncesine_gore_pct'])} | "
                 f"{f(r['medyan_dipten_toparlanma_pct'])} | {f(r['sektor_endeksi_3a_pct'])} |")
    L += ["", "## Hisseler",
          "| Sektor | Hisse | Duyarlilik | 1a% | 3a% | Goreli 3a% | Zirveden% | >MA50 | MA50>MA200 | Kriz oncesine% | Hacim 20g (mn TL) | F/K | PD/DD | Sistem skor/kgs/rejim |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for h in hisseler:
        sis = "-" if h.get("sistem_skor") is None else f"{f(h.get('sistem_skor'))}/{f(h.get('sistem_kgs'),0)}/{f(h.get('sistem_rejim'),0)} ({h.get('sistem_tarih')})"
        L.append(f"| {h['sektor']} | {h['sembol']} | {h['senaryo_duyarlilik']:+.1f} | {f(h.get('getiri_1a_pct'))} | "
                 f"{f(h.get('getiri_3a_pct'))} | {f(h.get('goreli_3a_pct'))} | {f(h.get('zirveden_uzaklik_pct'))} | "
                 f"{h.get('ustunde_ma50')} | {h.get('ma50_ustunde_ma200')} | {f(h.get('kriz_oncesine_gore_pct'))} | "
                 f"{f(h.get('ort_gunluk_hacim_tl_20g_milyon'),0)} | {f(h.get('fk'))} | {f(h.get('pd_dd'),2)} | {sis} |")
    if eksik:
        L += ["", f"Veri alinamayan: {', '.join(eksik)}"]
    with open(f"{CIKTI_KLASOR}/senaryo_sektor_ekrani.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("Tamam. Sektor siralamasi (duyarlilik, med. goreli 3a):")
    for r in sektorler[:5]:
        print(f"  {r['sektor']:11} {r['sektor_duyarlilik_ort']:+.1f}  goreli3a={r['medyan_goreli_3a_pct']}")


if __name__ == "__main__":
    main()
