"""
SCHUMPETER GOZLEM KATMANI (11.10.2026) - SALT OLCUM
=====================================================================
Schumpeter'in iki mekanizmasini OLCULEBILIR gozlem degiskenine cevirir:
  H1  YIGILMA (swarming): bir sektorde guc tek hisseden uyelerin cogunluguna
      yayildiginda sektorun sonraki 5/10 gun XU100'e goreli getirisi
      kosulsuz ortalamadan farkli mi?
  H2  YENILIK YOGUNLUGU: KAP'ta sektor basina "yatirim/sozlesme/ihracat/
      kapasite" turu bildirim yogunlugu artinca sonraki 10/20 gun goreli
      getiri farkli mi? (KAP verisi yalniz 45 gun saklandigi icin bu betik
      KENDI defterini tutar; degerlendirme n>=30 olay birikince baslar.)
H3 (rant erimesi) ve H4 (kredi dalgasi) ILERIDE; bu betikte YOK.

KIRMIZI CIZGI (Kulucka / IP-3): bu betik Pine'a DOKUNMAZ, ALARM URETMEZ,
hicbir sinyal mantigina baglanmaz. Cikti yalniz data/schumpeter_gozlem.* ve
hafta denetimine okunacak bir tablodur. Olcum kodu dondurmadan muaftir.

ON KAYIT: SCHUMPETER_ON_KAYIT.md. Esikler/tanimlar ORADAKILERLE AYNIDIR;
buradaki sabitler sonuca bakildiktan sonra DEGISTIRILEMEZ (degisirse
ON_KAYIT_SURUMU artar ve onceki sonuclar "eski tanim" diye etiketlenir).

DURUSTLUK NOTU:
  - Gecmis (ON_KAYIT_TARIHI oncesi) olaylar KESIFSELDIR; yalniz sonrasi
    TEYIT niteligindedir. Verdikt yalniz teyit olaylariyla verilir.
  - Olay sayisi n<30 ise verdikt "ORNEK YETERSIZ"dir. "Kenar yok" (anlamsiz)
    ile "zarar var" iki ayri iddiadir; burasi ikisini de iddia etmez.
  - 5 sektorle (>=3 uyeli) sinirli; sonuclar BIST'in tamamina genellenmez.
  - Duzeltilmis alfa = 0.05/4 = 0.0125 (dort hipotezlik aile, H3/H4 ayrildi).
"""
import datetime
import json
import math
import os
import re
import sys

import numpy as np
import pandas as pd

ON_KAYIT_SURUMU = 2   # v2 (12.10.2026): taban SEKTOR BAZINDA (v1: tum sektorler ortak taban)
ON_KAYIT_TARIHI = "2026-10-11"
ALFA = 0.0125
MIN_OLAY = 30
CIKTI_JSON = "data/schumpeter_gozlem.json"
CIKTI_MD = "schumpeter_gozlem.md"
KAP_DOSYA = "data/kap_bildirimleri.json"
KAP_DEFTER = "data/schumpeter_kap_defter.json"
VIOP_DOSYA = "data/viop_hisse_gunluk.json"
BASLANGIC = "2025-09-01"
ENDEKS = "XU100.IS"
YEDEK = {"TRMET": "KOZAA", "TRALT": "KOZAL"}

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
H1_SEKTORLER = ["BANKACILIK", "HAVACILIK", "SINAI", "ENERJI", "OTOMOTIV"]

# H1 tanimlari (ON KAYIT)
RS_PENCERE = 5          # goreli getiri penceresi (gun)
YAYILMA_UST = 2 / 3     # onset: breadth >= bu
YAYILMA_ALT = 1 / 3     # ve 5 gun once breadth <= bu
ILERI = (5, 10)
OLAY_ARASI_MIN = 10     # ayni sektorde iki olay arasi min gun (ust uste binmeyi onler)

# H2 tanimlari (ON KAYIT)
H2_ANAHTAR = [r"sözleşme", r"sozlesme", r"yatırım(?!c)", r"yatirim(?!c)", r"kapasite", r"sipariş",
              r"siparis", r"ihracat", r"tesis", r"proje", r"mutabakat zaptı",
              r"ortak girişim", r"satın alma", r"satin alma", r"ihale ilanı",
              r"ihale sonucu", r"ihale sonuç", r"\byeni "]
H2_DISLA = ["iptal", "alacak", "geri alım", "geri alim", "trafik", "bağımsız yönetim",
            "bagimsiz yonetim", "rekabet kurulu", "mahkeme", "basında yer alan",
            "basinda yer alan", "finans başkanı", "cfo", "eurobond", "rıza talebi", "ruhsat", "yatırımcılarımız"]
H2_PENCERE = 20
H2_ESIK = 2             # son 20 gunde >= 2 yenilik olayi
H2_ILERI = (10, 20)


# ---------------------------------------------------------------- yardimcilar
def tstat(x):
    x = np.asarray([v for v in x if v is not None and not np.isnan(v)], dtype=float)
    n = len(x)
    if n < 2:
        return n, None, None, None
    sd = x.std(ddof=1)
    if sd == 0:
        return n, float(x.mean()), None, None
    t = x.mean() / (sd / math.sqrt(n))
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))   # normal yaklasim (n>=30 icin makul)
    return n, float(x.mean()), float(t), float(p)


def verdikt(n, p):
    if n < MIN_OLAY or p is None:
        return "ORNEK YETERSIZ"
    return "ANLAMLI" if p < ALFA else "KENAR YOK (anlamsiz)"


def json_yaz(yol, veri):
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, yol)


# ---------------------------------------------------------------- veri
def fiyatlari_cek():
    """Doner: kapanis DataFrame (sutunlar: semboller + 'XU100')."""
    if os.environ.get("SCHUMPETER_TEST") == "1":
        rng = np.random.default_rng(7)
        gunler = pd.bdate_range("2025-09-01", "2026-10-09")
        cols = list(SEKTOR) + ["XU100"]
        getiri = rng.normal(0.0008, 0.015, (len(gunler), len(cols)))
        return pd.DataFrame(100 * np.exp(np.cumsum(getiri, axis=0)), index=gunler, columns=cols)
    import yfinance as yf
    seri = {}
    for s in list(SEKTOR) + ["XU100"]:
        adaylar = [ENDEKS] if s == "XU100" else [s + ".IS"] + ([YEDEK[s] + ".IS"] if s in YEDEK else [])
        for tk in adaylar:
            try:
                df = yf.download(tk, start=BASLANGIC, interval="1d", auto_adjust=True, progress=False)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                if df is not None and not df.empty:
                    seri[s] = df["Close"].dropna()
                    break
            except Exception as e:
                print(f"UYARI {tk}: {e}", file=sys.stderr)
    fiyat = pd.DataFrame(seri).sort_index()
    fiyat.index = pd.to_datetime(fiyat.index).tz_localize(None)
    return fiyat


# ---------------------------------------------------------------- H1
def h1_hesapla(fiyat):
    eksik = [s for s in SEKTOR if s not in fiyat.columns]
    if "XU100" not in fiyat.columns:
        return {"hata": "XU100 verisi yok"}
    getiri_ileri = {h: fiyat.shift(-h) / fiyat - 1 for h in ILERI}
    rs_geri = fiyat.pct_change(RS_PENCERE).sub(fiyat["XU100"].pct_change(RS_PENCERE), axis=0)
    sonuc = {"eksik_semboller": eksik, "sektorler": {}, "guncel": {}}
    fazla = {h: {"kesif": [], "teyit": []} for h in ILERI}    # olay getirisi - AYNI SEKTORUN tabani
    ham = {h: {"kesif": [], "teyit": []} for h in ILERI}
    taban_havuz = {h: [] for h in ILERI}
    for sek in H1_SEKTORLER:
        uyeler = [s for s in SEKTOR if SEKTOR[s] == sek and s in fiyat.columns]
        if len(uyeler) < 3:
            continue
        breadth = (rs_geri[uyeler] > 0).mean(axis=1)
        ort_rs = rs_geri[uyeler].mean(axis=1)
        gelecek = {h: getiri_ileri[h][uyeler].sub(getiri_ileri[h]["XU100"], axis=0).mean(axis=1) for h in ILERI}
        taban = {h: gelecek[h].dropna() for h in ILERI}
        son_olay = None
        olay_gunleri = []
        gun_listesi = list(breadth.index)
        for i, g in enumerate(gun_listesi):
            if i < RS_PENCERE + 1 or pd.isna(breadth.iloc[i]) or pd.isna(breadth.iloc[i - RS_PENCERE]):
                continue
            if breadth.iloc[i] >= YAYILMA_UST - 1e-9 and breadth.iloc[i - RS_PENCERE] <= YAYILMA_ALT + 1e-9 and ort_rs.iloc[i] > 0:
                if son_olay is None or i - son_olay >= OLAY_ARASI_MIN:
                    olay_gunleri.append(g)
                    son_olay = i
        satir = {"uye_sayisi": len(uyeler), "olay_sayisi": len(olay_gunleri), "olaylar": [str(d.date()) for d in olay_gunleri[-5:]]}
        for h in ILERI:
            sek_taban = float(taban[h].mean()) if len(taban[h]) else 0.0
            for ad, secici in (("kesif", lambda g: str(g.date()) < ON_KAYIT_TARIHI), ("teyit", lambda g: str(g.date()) >= ON_KAYIT_TARIHI)):
                for g in olay_gunleri:
                    if not secici(g):
                        continue
                    v = gelecek[h].get(g)
                    if v is None or pd.isna(v):
                        continue
                    ham[h][ad].append(float(v))
                    fazla[h][ad].append(float(v) - sek_taban)   # sektor-ozgu taban
            taban_havuz[h] += list(taban[h].values)
            satir[f"taban_ort_t{h}_pct"] = round(sek_taban * 100, 3) if len(taban[h]) else None
        sonuc["sektorler"][sek] = satir
        # guncel durum
        son = gun_listesi[-1]
        b_simdi, b_once = breadth.iloc[-1], breadth.iloc[-1 - RS_PENCERE]
        durum = "YAYILIYOR" if (b_simdi >= YAYILMA_UST - 1e-9 and b_once <= YAYILMA_ALT + 1e-9) else (
            "GUCLU-YAYILMIS" if b_simdi >= YAYILMA_UST - 1e-9 else (
                "DAGILIYOR" if b_simdi <= YAYILMA_ALT + 1e-9 and b_once > YAYILMA_ALT else "NORMAL"))
        sonuc["guncel"][sek] = {"tarih": str(son.date()), "breadth_simdi": round(float(b_simdi), 2),
                                "breadth_5g_once": round(float(b_once), 2),
                                "sektor_rs5_pct": round(float(ort_rs.iloc[-1]) * 100, 2), "durum": durum,
                                "uyeler": uyeler}
    sonuc["test"] = {}
    for h in ILERI:
        taban_ort = float(np.mean(taban_havuz[h])) if taban_havuz[h] else 0.0   # yalniz bilgi icin (havuz)
        for ad in ("kesif", "teyit"):
            n, ort, t, p = tstat(fazla[h][ad])
            sonuc["test"][f"t{h}_{ad}"] = {
                "n_olay": n, "olay_ort_pct": round(float(np.mean(ham[h][ad])) * 100, 3) if n else None,
                "taban_ort_pct": round(taban_ort * 100, 3),
                "fark_ort_pct": round(ort * 100, 3) if ort is not None else None,
                "t": round(t, 2) if t is not None else None, "p": round(p, 4) if p is not None else None,
                "verdikt": verdikt(n, p) if ad == "teyit" else "KESIFSEL (verdikt yok)"}
    return sonuc


# ---------------------------------------------------------------- H2
def yenilik_mi(ozet):
    s = (ozet or "").lower()
    if any(k in s for k in H2_DISLA):
        return False
    return any(re.search(k, s) for k in H2_ANAHTAR)


def kap_defteri_guncelle():
    defter = {"kayitlar": {}}
    if os.path.exists(KAP_DEFTER):
        with open(KAP_DEFTER, encoding="utf-8") as f:
            defter = json.load(f)
    yeni = 0
    if os.path.exists(KAP_DOSYA):
        with open(KAP_DOSYA, encoding="utf-8") as f:
            kap = json.load(f)
        for b in kap.get("bildirimler", []):
            if not str(b.get("tur", "")).startswith("Özel Durum"):
                continue
            anahtar = str(b["disclosureIndex"])
            if anahtar in defter["kayitlar"]:
                continue
            defter["kayitlar"][anahtar] = {
                "tarih": str(b["tarih_utc"])[:10], "sembol": b["sembol"],
                "sektor": SEKTOR.get(b["sembol"], "?"), "ozet": b.get("ozet", "")[:140],
                "yenilik": yenilik_mi(b.get("ozet", ""))}
            yeni += 1
    json_yaz(KAP_DEFTER, defter)
    return defter, yeni


def h2_hesapla(defter, fiyat):
    kayit = list(defter["kayitlar"].values())
    yenilik = [k for k in kayit if k["yenilik"] and k["sektor"] != "?"]
    bugun = pd.Timestamp(datetime.date.today())
    pencere_bas = bugun - pd.Timedelta(days=H2_PENCERE)
    sayac = {}
    for k in yenilik:
        if pd.Timestamp(k["tarih"]) >= pencere_bas:
            sayac[k["sektor"]] = sayac.get(k["sektor"], 0) + 1
    ilk = min((k["tarih"] for k in kayit), default=None)
    sonuc = {"defter_kayit": len(kayit), "yenilik_kayit": len(yenilik), "defter_ilk_tarih": ilk,
             "son20g_sektor_sayac": dict(sorted(sayac.items(), key=lambda x: -x[1])),
             "esik_ustu_sektorler": [s for s, c in sayac.items() if c >= H2_ESIK],
             "son_yenilik_olaylari": sorted(yenilik, key=lambda k: k["tarih"])[-8:]}
    # olay-calismasi: sektor 'esik ustu' oldugu GUNLERDEN sonra goreli getiri (defter yeterince uzayinca)
    sonuc["test"] = {}
    if fiyat is None or "XU100" not in fiyat.columns:
        sonuc["test"]["not"] = "fiyat verisi yok"
        return sonuc
    gunler = fiyat.index
    fazla = {h: [] for h in H2_ILERI}   # olay getirisi - AYNI SEKTORUN tabani (v2)
    sektorler = sorted({k["sektor"] for k in yenilik})
    for sek in sektorler:
        uyeler = [s for s in SEKTOR if SEKTOR[s] == sek and s in fiyat.columns]
        if not uyeler:
            continue
        tarihler = sorted(pd.Timestamp(k["tarih"]) for k in yenilik if k["sektor"] == sek)
        son_i = None
        sek_taban = {h: [] for h in H2_ILERI}
        sek_olay = {h: [] for h in H2_ILERI}
        for i, g in enumerate(gunler):
            sayi = sum(1 for t in tarihler if g - pd.Timedelta(days=H2_PENCERE) < t <= g)
            for h in H2_ILERI:
                if i + h < len(gunler):
                    gel = (fiyat[uyeler].iloc[i + h] / fiyat[uyeler].iloc[i] - 1).mean() - (fiyat["XU100"].iloc[i + h] / fiyat["XU100"].iloc[i] - 1)
                    sek_taban[h].append(gel)
                    if sayi >= H2_ESIK and str(g.date()) >= (ilk or "9999") and (son_i is None or i - son_i >= H2_PENCERE):
                        sek_olay[h].append(gel)
            if sayi >= H2_ESIK and (son_i is None or i - son_i >= H2_PENCERE):
                son_i = i
        for h in H2_ILERI:
            tb = float(np.mean(sek_taban[h])) if sek_taban[h] else 0.0
            fazla[h] += [v - tb for v in sek_olay[h]]
    for h in H2_ILERI:
        n, ort, t, p = tstat(fazla[h])
        sonuc["test"][f"t{h}"] = {"n_olay": n, "fark_ort_pct": round(ort * 100, 3) if ort is not None else None,
                                  "t": round(t, 2) if t is not None else None, "p": round(p, 4) if p is not None else None,
                                  "verdikt": verdikt(n, p),
                                  "not": "defter KAP'in 45 gunluk penceresinden biriktigi icin tum olaylar ileriye donuktur (teyit)"}
    return sonuc


# ---------------------------------------------------------------- VIOP teyidi (betimleyici)
def viop_teyit(h1):
    if not os.path.exists(VIOP_DOSYA):
        return None
    with open(VIOP_DOSYA, encoding="utf-8") as f:
        g = json.load(f).get("gunler", {})
    if not g:
        return None
    son = sorted(g)[-1]
    gun = g[son]
    cikti = {"tarih": son, "sektorler": {}}
    for sek, bilgi in h1.get("guncel", {}).items():
        yeni_long = yeni_short = n = 0
        for s in bilgi["uyeler"]:
            v = gun.get(s)
            if not v:
                continue
            n += 1
            fd, od = v.get("fiyat_degisim_pct"), v.get("oi_degisim_pct")
            if fd is None or od is None:
                continue
            if fd > 0 and od > 0:
                yeni_long += 1
            elif fd < 0 and od > 0:
                yeni_short += 1
        cikti["sektorler"][sek] = {"viop_uye": n, "yeni_long": yeni_long, "yeni_short": yeni_short}
    return cikti


# ---------------------------------------------------------------- rapor
def md_yaz(h1, h2, viop):
    s = ["# Schumpeter gözlem katmanı (SALT ÖLÇÜM)", "",
         f"Önkayıt sürümü {ON_KAYIT_SURUMU} · önkayıt tarihi {ON_KAYIT_TARIHI} · α={ALFA} · min olay {MIN_OLAY}",
         "Pine'a dokunmaz, alarm üretmez. Tavsiye değildir.", "",
         "## H1 — Yığılma (sektör içi yayılma)", "",
         "| Sektör | Breadth şimdi | 5g önce | Sektör RS5 % | Durum | VİOP yeni long/short |", "|---|---|---|---|---|---|"]
    for sek, b in h1.get("guncel", {}).items():
        v = (viop or {}).get("sektorler", {}).get(sek)
        vt = f"{v['yeni_long']}/{v['yeni_short']} ({v['viop_uye']} üye)" if v else "-"
        s.append(f"| {sek} | {b['breadth_simdi']} | {b['breadth_5g_once']} | {b['sektor_rs5_pct']} | {b['durum']} | {vt} |")
    s += ["", "Olay çalışması (yayılma başlangıcı sonrası sektörün XU100'e göreli getirisi − koşulsuz ortalama):", "",
          "| Test | n | Olay ort % | Taban % | Fark % | t | p | Verdikt |", "|---|---|---|---|---|---|---|---|"]
    for ad, t in h1.get("test", {}).items():
        s.append(f"| H1 {ad} | {t['n_olay']} | {t['olay_ort_pct']} | {t['taban_ort_pct']} | {t['fark_ort_pct']} | {t['t']} | {t['p']} | {t['verdikt']} |")
    s += ["", "## H2 — Yenilik yoğunluğu (KAP)", "",
          f"Defter: {h2['defter_kayit']} Özel Durum kaydı, bunun {h2['yenilik_kayit']}'i yenilik türü · ilk kayıt {h2['defter_ilk_tarih']}",
          f"Son {H2_PENCERE} gün sektör sayacı: {h2['son20g_sektor_sayac']}",
          f"Eşik üstü (>= {H2_ESIK}): {h2['esik_ustu_sektorler'] or '-'}", ""]
    for ad, t in h2.get("test", {}).items():
        if isinstance(t, dict):
            s.append(f"- H2 {ad}: n={t['n_olay']}, fark={t['fark_ort_pct']}%, t={t['t']}, p={t['p']} → **{t['verdikt']}**")
    s += ["", "Son yenilik olayları:"]
    for k in h2["son_yenilik_olaylari"]:
        s.append(f"- {k['tarih']} {k['sembol']} ({k['sektor']}): {k['ozet']}")
    s += ["", "---", "H3 (rant erimesi) ve H4 (kredi dalgası) bu sürümde yok.",
          "Keşifsel (önkayıt öncesi) sonuçlar verdikt taşımaz; yalnız teyit olayları değerlendirilir."]
    return "\n".join(s) + "\n"


def main():
    fiyat = fiyatlari_cek()
    if fiyat is None or fiyat.empty:
        print("HATA: fiyat verisi alinamadi")
        return 1
    h1 = h1_hesapla(fiyat)
    defter, yeni = kap_defteri_guncelle()
    h2 = h2_hesapla(defter, fiyat)
    viop = viop_teyit(h1)
    json_yaz(CIKTI_JSON, {"olusturma_utc": datetime.datetime.utcnow().isoformat() + "Z",
                          "on_kayit_surumu": ON_KAYIT_SURUMU, "on_kayit_tarihi": ON_KAYIT_TARIHI,
                          "h1": h1, "h2": h2, "viop_teyit": viop, "kap_yeni_kayit": yeni})
    with open(CIKTI_MD, "w", encoding="utf-8") as f:
        f.write(md_yaz(h1, h2, viop))
    print(f"Tamam: H1 sektor {len(h1.get('guncel', {}))}, KAP defteri +{yeni} (toplam {h2['defter_kayit']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
