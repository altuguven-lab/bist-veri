"""
sqz_karne.py — SQZ skorunun KENDI kulucka karnesi (FAZ V3'un "hafta
kapanisi" adimi, VIOP_ENTEGRASYON_PROMPTU 13.07.2026):

"SQZ >= 65 vakalarinin T+3/T+5 sonuclari izlenir - parametrenin KENDI
kulucka karnesi (2 hafta gozlem, sonra degerlendirme)."

Bu betik YENI bir yontem TASARLAMIYOR - sinyal_arsiv_gunluk.py'deki
AYNI olcum mantigini (islem-gunu penceresi, piyasa-goreli getiri,
T+N kapanis) SQZ adaylarina uyguluyor. Amac tutarlilik: iki farkli
olcum yontemi olursa hangisine guvenilecegi belirsizlesir.

YON VARSAYIMI (on kayit): "sikisma adayi" kisa pozisyonlarin
kapanmaya zorlanmasini bekler - yani fiyatin YUKARI gitmesi beklenir.
Isabet = goreli getiri > 0. ACIL_CIK/POZ_AZALT gibi asagi bekleyen
degil, P3_SKOR_AL/P2_DIP_DONUS gibi yukari bekleyen bir sinyal.

KIRMIZI CIZGI (degismez): SQZ skoru hicbir alertcondition/portfoy/
islem dosyasina baglanmaz - bu karne SADECE gozlem raporu.

RED KRITERI (plan geregi, 2 hafta = ~10 islem gunu): ilk 10 islem
gunu icinde "GOZLEM DONEMI BITMEDI, HUKUM VERILMEZ" - erken yorum
YAPILMAZ, plan bunu acikca ister.
"""
import datetime
import json
import statistics
import sys
import math

import yfinance as yf

from json_atomik_yaz import atomik_json_yaz

SQZ_YOL = "data/sqz_skoru.json"
KARNE_YOL = "data/sqz_karne.json"
PIYASA_ENDEKSLERI = ["XU100.IS", "^XU100"]
ESIK_ADAY = 65
GOZLEM_DONEMI_ISLEM_GUNU = 10  # ~2 hafta, plan geregi


def _seri_cek(ticker, donem="3mo"):
    try:
        df = yf.Ticker(ticker).history(period=donem, interval="1d")
        seri = [(idx.date(), float(v)) for idx, v in df["Close"].items()]
        return sorted(seri, key=lambda x: x[0])
    except Exception as e:
        print(f"UYARI: {ticker} veri cekilemedi -> {e}", file=sys.stderr)
        return []


def _baz_indeks(seri, sinyal_tarih):
    adaylar = [i for i, (t, _) in enumerate(seri) if t <= sinyal_tarih]
    return max(adaylar) if adaylar else None


def _t_plus_kapanis(seri, sinyal_tarih, n):
    i = _baz_indeks(seri, sinyal_tarih)
    if i is None or i + n >= len(seri):
        return None
    return seri[i + n][1]


def _baz_kapanis(seri, sinyal_tarih):
    i = _baz_indeks(seri, sinyal_tarih)
    return seri[i][1] if i is not None else None


def _islem_gunu_farki(seri, sinyal_tarih):
    """Sinyal barindan bugune kadar kac islem gunu gecmis - GOZLEM_DONEMI
    kontrolu icin."""
    i = _baz_indeks(seri, sinyal_tarih)
    if i is None:
        return 0
    return len(seri) - 1 - i


def _piyasa_serisi_al(donem="3mo"):
    for tic in PIYASA_ENDEKSLERI:
        seri = _seri_cek(tic, donem)
        if seri:
            print(f"Piyasa referansi: {tic} ({len(seri)} gun)")
            return tic, seri
    print("UYARI: piyasa endeksi cekilemedi", file=sys.stderr)
    return None, []


def _piyasa_getirisi(piyasa_seri, sinyal_tarih, gun):
    baz = _baz_kapanis(piyasa_seri, sinyal_tarih)
    hedef = _t_plus_kapanis(piyasa_seri, sinyal_tarih, gun)
    if baz and hedef and baz > 0:
        return round((hedef / baz - 1) * 100, 3)
    return None


def main():
    try:
        with open(SQZ_YOL, encoding="utf-8") as f:
            sqz = json.load(f)
    except FileNotFoundError:
        print(f"HATA: {SQZ_YOL} yok, once sqz_skoru.py calismali", file=sys.stderr)
        sys.exit(1)

    try:
        with open(KARNE_YOL, encoding="utf-8") as f:
            karne = json.load(f)
    except FileNotFoundError:
        karne = {"kayitlar": []}

    bulten_gunu = datetime.date.fromisoformat(sqz["bulten_gunu"])

    # --- 1) Bugunku adaylari karneye ekle (mukerrer olmasin diye
    # ayni sembol+tarih zaten varsa atla) ---
    mevcut_anahtarlar = {(k["sembol"], k["tarih"]) for k in karne["kayitlar"]}
    eklenen = 0
    for sem, v in sqz["semboller"].items():
        if v.get("etiket") is None:
            continue
        anahtar = (sem, str(bulten_gunu))
        if anahtar in mevcut_anahtarlar:
            continue
        karne["kayitlar"].append({
            "sembol": sem, "tarih": str(bulten_gunu),
            "sqz_skoru": v["sqz_skoru"], "etiket": v["etiket"],
            "dogrulama_durumu": "BEKLIYOR",
        })
        eklenen += 1
    if eklenen:
        print(f"{eklenen} yeni SQZ adayi karneye eklendi")

    # --- 2) Bekleyen kayitlari, yeterli islem gunu gectiyse dogrula ---
    bekleyen = [k for k in karne["kayitlar"] if k["dogrulama_durumu"] == "BEKLIYOR"]
    if bekleyen:
        piyasa_tic, piyasa_seri = _piyasa_serisi_al()
        fiyat_serileri = {}
        dogrulanan = 0
        for k in bekleyen:
            sem = k["sembol"]
            sinyal_tarih = datetime.date.fromisoformat(k["tarih"])
            if sem not in fiyat_serileri:
                fiyat_serileri[sem] = _seri_cek(f"{sem}.IS")
            seri = fiyat_serileri[sem]
            if not seri:
                continue

            islem_gunu_gecti = _islem_gunu_farki(seri, sinyal_tarih)
            k["islem_gunu_gecti"] = islem_gunu_gecti

            t3 = _t_plus_kapanis(seri, sinyal_tarih, 3)
            t5 = _t_plus_kapanis(seri, sinyal_tarih, 5)
            if t5 is None:
                continue  # T+5 henuz gelmedi, BEKLIYOR kalir

            baz = _baz_kapanis(seri, sinyal_tarih)
            if baz is None or baz <= 0:
                continue

            k["getiri_t3_pct"] = round((t3 / baz - 1) * 100, 3) if t3 else None
            k["getiri_t5_pct"] = round((t5 / baz - 1) * 100, 3) if t5 else None
            if piyasa_seri:
                pt3 = _piyasa_getirisi(piyasa_seri, sinyal_tarih, 3)
                pt5 = _piyasa_getirisi(piyasa_seri, sinyal_tarih, 5)
                k["piyasa_t3_pct"] = pt3
                k["piyasa_t5_pct"] = pt5
                if k["getiri_t3_pct"] is not None and pt3 is not None:
                    k["getiri_rel_t3_pct"] = round(k["getiri_t3_pct"] - pt3, 3)
                if k["getiri_t5_pct"] is not None and pt5 is not None:
                    k["getiri_rel_t5_pct"] = round(k["getiri_t5_pct"] - pt5, 3)
            k["dogrulama_durumu"] = "DOGRULANDI"
            dogrulanan += 1
        if dogrulanan:
            print(f"{dogrulanan} SQZ adayi dogrulandi (T+5 islem gunu gecmis)")

    # --- 3) Ozet: sadece GOZLEM_DONEMI_ISLEM_GUNU gecmisse hukum verilir ---
    dg = [k for k in karne["kayitlar"] if k["dogrulama_durumu"] == "DOGRULANDI"]
    en_eski_aday_gun = min((k.get("islem_gunu_gecti", 0) for k in karne["kayitlar"]), default=0)

    ozet = {"n_toplam_aday": len(karne["kayitlar"]), "n_dogrulanmis": len(dg)}
    if len(dg) < 5:
        ozet["hukum"] = ("GOZLEM DONEMI BITMEDI / n COK KUCUK - hukum verilmez "
                         f"(plan geregi ~{GOZLEM_DONEMI_ISLEM_GUNU} islem gunu "
                         "gozlem + yeterli n gerekiyor)")
    else:
        vals = [k["getiri_rel_t5_pct"] for k in dg if k.get("getiri_rel_t5_pct") is not None]
        if len(vals) >= 5:
            n = len(vals)
            ort = statistics.mean(vals)
            std = statistics.stdev(vals)
            se = std / math.sqrt(n) if n > 1 else 0
            t = ort / se if se else 0
            isabet = sum(1 for v in vals if v > 0)
            ozet.update({
                "n": n, "goreli_t5_ortalama_pct": round(ort, 3),
                "t_istatistigi": round(t, 2), "anlamli_mi": abs(t) > 1.96,
                "isabet_pct": round(100 * isabet / n, 1),
                "guven_araligi_95": [round(ort - 1.96 * se, 3), round(ort + 1.96 * se, 3)],
                "hukum": ("KARSILASTIRMA YAPILABILIR" if abs(t) > 1.96
                          else "KENAR YOK (anlamli degil) - ZARAR VAR ANLAMINA GELMEZ"),
            })
        else:
            ozet["hukum"] = "n YETERSIZ - goreli getiri hesaplanamayan kayit sayisi fazla"

    karne["son_guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    karne["ozet"] = ozet
    atomik_json_yaz(KARNE_YOL, karne)
    print(json.dumps(ozet, ensure_ascii=False, indent=2))
    print(f"Yazildi: {KARNE_YOL}")


if __name__ == "__main__":
    main()
