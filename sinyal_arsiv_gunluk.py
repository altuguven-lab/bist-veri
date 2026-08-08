"""
SINYAL DOGRULAMA ARSIVI - GUNLUK (08.08.2026) - Faz V0
sinyal_dogrulama.py'nin (tek seferlik kesif) KALICI, GUNLUK versiyonu.
tv_alerts_latest.json yalniz ~4 gun tutuyor - bu script HER GUN, o
gunku YENI sinyalleri KALICI bir arsive (data/sinyal_arsiv.json) ekler,
ve YETERLI zaman gecmis (T+3) ESKI sinyaller icin GERCEK fiyat
hareketiyle dogrulama yapar. Zamanla arsiv buyudukce, istatistiksel
guc artar - dorduncu-gun penceresi sinirini asar.

KIRMIZI CIZGI: Pine'a hic dokunmuyor, hicbir gercek islem/uyari
uretmiyor - SALT OLCUM, gunluk calisan bir arastirma gunlugu.

Calisma mantigi (her gun):
  1. tv_alerts_latest.json'daki BUGUNUN yeni trade sinyallerini
     arsive EKLE (tekrar onleme: sembol+sinyal+zaman ile).
  2. Arsivdeki, GIRISTEN BU YANA en az 3 GUN gecmis ama HENUZ
     dogrulanmamis sinyaller icin GERCEK T+1/T+2/T+3 fiyatini
     yfinance'ten cekip dogrula, sonucu KALICI olarak isle.
  3. Tip-bazinda GUNCEL ozet istatistikleri yeniden hesapla.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import yfinance as yf

GIRIS_YOL = "data/tv_alerts_latest.json"
ARSIV_YOL = "data/sinyal_arsiv.json"

AL_SINYALLERI = {"P3_SKOR_AL", "P2_DIP_DONUS", "P1_AL", "P1_KALITELI_AL", "P2_ERKEN_AL"}
RISK_OFF_SINYALLERI = {"POZ_AZALT", "STOP_KIRILDI", "ACIL_CIK"}
TAKIP_GUNLERI = [1, 2, 3]
DOGRULAMA_ICIN_GEREKEN_GUN = 3  # T+3 gecmeden dogrulama YAPILMAZ


def _oku_arsiv():
    try:
        with open(ARSIV_YOL, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"kayitlar": [], "tip_ozet": {}}


def _en_yakin_kapanis(seri, hedef_tarih, sonraki_mi=True):
    if sonraki_mi:
        adaylar = [(t, c) for t, c in seri if t >= hedef_tarih]
        return min(adaylar, key=lambda x: x[0])[1] if adaylar else None
    adaylar = [(t, c) for t, c in seri if t <= hedef_tarih]
    return max(adaylar, key=lambda x: x[0])[1] if adaylar else None


def main():
    arsiv = _oku_arsiv()
    mevcut_anahtarlar = {(k["sembol"], k["sinyal"], k["tarih"]) for k in arsiv["kayitlar"]}

    veri = json.load(open(GIRIS_YOL, encoding="utf-8"))
    yeni_sayisi = 0
    for s in veri["sinyal_gecmisi"]:
        if s["sinyal"] not in (AL_SINYALLERI | RISK_OFF_SINYALLERI):
            continue
        sinyal_tarih = datetime.datetime.fromisoformat(
            s["zaman_utc"].replace("Z", "+00:00")).date()
        anahtar = (s["sembol"], s["sinyal"], str(sinyal_tarih))
        if anahtar in mevcut_anahtarlar:
            continue
        arsiv["kayitlar"].append({
            "sembol": s["sembol"], "sinyal": s["sinyal"], "tarih": str(sinyal_tarih),
            "sinyal_fiyat": float(s["fiyat"]),
            "yon_beklentisi": "YUKARI" if s["sinyal"] in AL_SINYALLERI else "ASAGI_VEYA_NOTR",
            "dogrulama_durumu": "BEKLIYOR",
        })
        mevcut_anahtarlar.add(anahtar)
        yeni_sayisi += 1
    print(f"{yeni_sayisi} yeni sinyal arsive eklendi")

    bugun = datetime.datetime.now(datetime.timezone.utc).date()
    fiyat_serileri = {}
    dogrulanan_sayisi = 0
    for kayit in arsiv["kayitlar"]:
        if kayit["dogrulama_durumu"] != "BEKLIYOR":
            continue
        sinyal_tarih = datetime.date.fromisoformat(kayit["tarih"])
        if (bugun - sinyal_tarih).days < DOGRULAMA_ICIN_GEREKEN_GUN:
            continue  # henuz T+3 gecmedi

        sembol = kayit["sembol"]
        if sembol not in fiyat_serileri:
            try:
                df = yf.Ticker(f"{sembol}.IS").history(period="2mo", interval="1d")
                fiyat_serileri[sembol] = [(idx.date(), float(v)) for idx, v in df["Close"].items()]
            except Exception as e:
                print(f"UYARI: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
                fiyat_serileri[sembol] = []
        seri = fiyat_serileri[sembol]
        if not seri:
            continue

        for gun in TAKIP_GUNLERI:
            hedef = sinyal_tarih + datetime.timedelta(days=gun)
            t_fiyat = _en_yakin_kapanis(seri, hedef, sonraki_mi=True)
            if t_fiyat and kayit["sinyal_fiyat"] > 0:
                kayit[f"getiri_t{gun}_pct"] = round((t_fiyat / kayit["sinyal_fiyat"] - 1) * 100, 3)
        if all(f"getiri_t{g}_pct" in kayit for g in TAKIP_GUNLERI):
            kayit["dogrulama_durumu"] = "DOGRULANDI"
            dogrulanan_sayisi += 1
    print(f"{dogrulanan_sayisi} sinyal bu kosumda dogrulandi (T+3 gecmis)")

    tip_ozet = {}
    for tip in (AL_SINYALLERI | RISK_OFF_SINYALLERI):
        alt = [k for k in arsiv["kayitlar"]
               if k["sinyal"] == tip and k["dogrulama_durumu"] == "DOGRULANDI"]
        if not alt:
            continue
        for gun in TAKIP_GUNLERI:
            degerler = [k[f"getiri_t{gun}_pct"] for k in alt if f"getiri_t{gun}_pct" in k]
            if not degerler:
                continue
            ort = sum(degerler) / len(degerler)
            if tip in AL_SINYALLERI:
                dogrulanan = sum(1 for d in degerler if d > 0)
            else:
                dogrulanan = sum(1 for d in degerler if d <= 0)
            tip_ozet.setdefault(tip, {})[f"t{gun}"] = {
                "n": len(degerler), "ort_getiri_pct": round(ort, 3),
                "dogrulanan_pct": round(100 * dogrulanan / len(degerler), 1),
            }

    arsiv["tip_ozet"] = tip_ozet
    arsiv["son_guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    arsiv["toplam_kayit"] = len(arsiv["kayitlar"])
    arsiv["dogrulanmis_kayit"] = sum(1 for k in arsiv["kayitlar"] if k["dogrulama_durumu"] == "DOGRULANDI")
    atomik_json_yaz(ARSIV_YOL, arsiv)
    print(f"\nArsiv: {arsiv['toplam_kayit']} toplam, {arsiv['dogrulanmis_kayit']} dogrulanmis")
    for tip, gunler in tip_ozet.items():
        t1 = gunler.get("t1", {})
        if t1:
            print(f"  {tip}: n={t1['n']}, T+1 ort=%{t1['ort_getiri_pct']}, dogrulanan=%{t1['dogrulanan_pct']}")


if __name__ == "__main__":
    main()
