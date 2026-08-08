"""
SINYAL DOGRULAMA TESTI (08.08.2026) - Faz V0
Kurul karari: "Alarmlarimiz sonrasi fiyat hareketi sinyali dogruluyor
mu yaniltiyor mu?" sorusuna DOGRUDAN, kendi GERCEK sinyal gecmisimizle
cevap arar. HER sinyal icin, sinyal ANINDAN T+1/T+2/T+3 gun SONRAKI
GERCEK fiyata gore getiri hesaplanir.

DURUST SINIRLAMA: tv_alerts_latest.json yalniz SON ~4 gunu tutuyor -
bu, T+10/T+20 icin YETERSIZ (yalniz T+1/T+2/T+3 icin YETERLI zaman
gecmis). Orneklem KUCUK (41 gercek trade sinyali) - bu, KESIN bir
sonuc DEGIL, ILK bir olcum. Arsiv buyudukce tekrarlanmali.

YONLU TUTARLILIK MANTIGI:
  AL sinyalleri (P3_SKOR_AL, P2_DIP_DONUS): fiyat YUKSELMELI (basari
    = pozitif getiri).
  RISK-OFF sinyalleri (POZ_AZALT, STOP_KIRILDI, ACIL_CIK): fiyat
    DUSMEYE DEVAM ETMELI ya da EN AZINDAN toparlanmamali (basari =
    negatif/notr getiri - COKISI HAKLI CIKARMASI). Eger fiyat GUCLU
    YUKSELIRSE, bu sinyal MUHTEMELEN ERKEN/YANLIS bir cikisti.

SALT OLCUM - Pine'a hic dokunmuyor.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, sys
import yfinance as yf

GIRIS_YOL = "data/tv_alerts_latest.json"
CIKTI = "data/backtest/sinyal_dogrulama_sonuc.json"

AL_SINYALLERI = {"P3_SKOR_AL", "P2_DIP_DONUS", "P1_AL"}
RISK_OFF_SINYALLERI = {"POZ_AZALT", "STOP_KIRILDI", "ACIL_CIK"}
TAKIP_GUNLERI = [1, 2, 3]


def _en_yakin_kapanis(seri, hedef_tarih, sonraki_mi):
    if sonraki_mi:
        adaylar = [(t, c) for t, c in seri if t >= hedef_tarih]
        return min(adaylar, key=lambda x: x[0])[1] if adaylar else None
    else:
        adaylar = [(t, c) for t, c in seri if t <= hedef_tarih]
        return max(adaylar, key=lambda x: x[0])[1] if adaylar else None


def main():
    veri = json.load(open(GIRIS_YOL, encoding="utf-8"))
    sinyaller = [s for s in veri["sinyal_gecmisi"]
                 if s["sinyal"] in (AL_SINYALLERI | RISK_OFF_SINYALLERI)]
    print(f"{len(sinyaller)} gercek trade sinyali bulundu")

    fiyat_serileri = {}
    sonuclar = []
    for s in sinyaller:
        sembol = s["sembol"]
        if sembol not in fiyat_serileri:
            try:
                df = yf.Ticker(f"{sembol}.IS").history(period="1mo", interval="1d")
                fiyat_serileri[sembol] = [(idx.date(), float(v)) for idx, v in df["Close"].items()]
            except Exception as e:
                print(f"UYARI: {sembol} veri cekilemedi -> {e}", file=sys.stderr)
                fiyat_serileri[sembol] = []
        seri = fiyat_serileri[sembol]
        if not seri:
            continue

        sinyal_tarih = datetime.datetime.fromisoformat(
            s["zaman_utc"].replace("Z", "+00:00")).date()
        sinyal_fiyat = float(s["fiyat"])
        kayit = {"sembol": sembol, "sinyal": s["sinyal"], "tarih": str(sinyal_tarih),
                  "sinyal_fiyat": sinyal_fiyat,
                  "yon_beklentisi": "YUKARI" if s["sinyal"] in AL_SINYALLERI else "ASAGI_VEYA_NOTR"}
        for gun in TAKIP_GUNLERI:
            hedef = sinyal_tarih + datetime.timedelta(days=gun)
            t_fiyat = _en_yakin_kapanis(seri, hedef, sonraki_mi=True)
            if t_fiyat and sinyal_fiyat > 0:
                kayit[f"getiri_t{gun}_pct"] = round((t_fiyat / sinyal_fiyat - 1) * 100, 3)
            else:
                kayit[f"getiri_t{gun}_pct"] = None
        sonuclar.append(kayit)

    # tip bazinda ozet - AL sinyalleri icin pozitif getiri = DOGRULANDI,
    # RISK-OFF sinyalleri icin negatif/notr getiri = DOGRULANDI
    tip_ozet = {}
    for tip in (AL_SINYALLERI | RISK_OFF_SINYALLERI):
        alt = [k for k in sonuclar if k["sinyal"] == tip]
        if not alt:
            continue
        for gun in TAKIP_GUNLERI:
            degerler = [k[f"getiri_t{gun}_pct"] for k in alt if k[f"getiri_t{gun}_pct"] is not None]
            if not degerler:
                continue
            ort = sum(degerler) / len(degerler)
            if tip in AL_SINYALLERI:
                dogrulanan = sum(1 for d in degerler if d > 0)
            else:
                dogrulanan = sum(1 for d in degerler if d <= 0)
            tip_ozet.setdefault(tip, {})[f"t{gun}"] = {
                "n": len(degerler), "ort_getiri_pct": round(ort, 3),
                "dogrulanan_sayisi": dogrulanan,
                "dogrulanan_pct": round(100 * dogrulanan / len(degerler), 1),
            }

    sonuc_json = {
        "kesif_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("SINIRLAMA: sinyal arsivi yalniz ~4 gun geriye gidiyor, "
                "orneklem KUCUK (41 sinyal) - bu KESIN bir sonuc DEGIL, "
                "ILK olcum. AL sinyalleri icin basari=pozitif getiri, "
                "RISK-OFF sinyalleri icin basari=negatif/notr getiri "
                "(cikisi haklı cikarmasi)."),
        "toplam_sinyal": len(sonuclar),
        "tip_ozet": tip_ozet,
        "sinyal_detaylari": sonuclar,
    }
    atomik_json_yaz(CIKTI, sonuc_json)
    print(f"\nYazildi: {CIKTI}")
    for tip, gunler in tip_ozet.items():
        print(f"\n{tip}:")
        for gun, v in gunler.items():
            print(f"  {gun}: n={v['n']}, ort getiri=%{v['ort_getiri_pct']}, "
                  f"dogrulanan=%{v['dogrulanan_pct']}")


if __name__ == "__main__":
    main()
