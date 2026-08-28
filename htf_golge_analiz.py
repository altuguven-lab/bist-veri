"""
htf_golge_analiz.py — HTF EMA duzeltmesinin GOLGE OLCUMU

AMAC: 27.08.2026 kurul karari geregi, HTF EMA hesaplama hatasinin
duzeltilmis halini CANLI ALARMLARA HIC DOKUNMADAN, ayri bir olcum
katmaninda dogrulamak. Pine'in kendi alertcondition/finalDecision
mantigina bu betik HICBIR SEKILDE MUDAHALE ETMEZ - salt okunur bir
arka-plan analizi.

C.5 ON KAYIT (veri gorulmeden yontem kilitlendi, 27.08.2026):
  Soru: htfAlign'in DOGRU hesaplanan hali (1s/4s barlarinin kendi
  baglaminda EMA) ile ESKI (15dk barlarinda tekrarlanmis 1s/4s
  kapanisi uzerinden EMA) hali arasinda ne siklikta fark cikiyor,
  ve bu fark P3_SKOR_AL sinyallerinin ileri getirisiyle iliskili mi?

  Yontem:
  - HTF1=1s, HTF2=4s (V162 kaynagindaki gercek degerler, input.timeframe)
  - ESKI: 1s kapanisi 15dk barlarda TEKRARLANIR (onceki TAMAMLANMIS
    1s barinin kapanisi, o saat icindeki her 15dk barinda AYNI),
    EMA21/EMA50 bu TEKRARLANMIS seri uzerinde hesaplanir.
  - YENI: EMA21/EMA50 DOGRUDAN 1s barlarin kendi serisinde hesaplanir,
    sonra deger 15dk'ya tasinir (yine tekrarli ama EMA'nin KENDISI
    doguru hesaplanmis).
  - htfBull = close > ema50 and ema21 > ema50 (1s icin), htf2Bull =
    close > ema50 (4s icin, tek EMA), htfAlign = htfBull+htf2Bull (0-2)
  - Karsilastirma: sinyal_arsiv.json'daki DOGRULANMIS P3_SKOR_AL
    kayitlarinin HER BIRI icin, sinyal anindaki htfAlign_eski vs
    htfAlign_yeni hesaplanir. FARKLI cikanlar isaretlenir.
  - Hukum: farkli-htfAlign alt kumesinde goreli T+3 getirisi (zaten
    sinyal_arsiv'de var) ile AYNI-htfAlign alt kumesi karsilastirilir.
    Ayrisirsa (farkli kumenin performansi farkliysa), duzeltmenin
    canli etkisi olacagina dair KANIT olur - simdiden HUKUM VERILMEZ,
    n kucukse "n YETERSIZ" diye raporlanir.

  Red kriteri: iki grup arasinda goreli anlam farki yoksa ya da n<10
  ise "KANIT YETERSIZ" - duzeltmenin canli etkisi belirsiz kalir,
  bu BASARISIZLIK degildir, dogru sonuc budur.

  27.08 EK ON KAYIT (ilk kosumun SONUCUNU gordukten sonra eklendi -
  bu yuzden ilk kosum icin kesin kanit degil, ikinci kosumdan itibaren
  ON KAYITLI sayilir): "farkli" grubu YONE gore ikiye bolunur:
    - YENI > ESKI: duzeltme HTF onayini GUCLENDIRIYOR (sinyal zaten
      gecerdi, ama daha guclu onayla)
    - YENI < ESKI: duzeltme HTF onayini ZAYIFLATIYOR (sinyal
      duzeltilmis sistemde pAzamiHtf esigini GECEMEYEBILIRDI - bu
      grubun performansi, duzeltmenin "kotu sinyalleri eliyor mu"
      sorusuna dogrudan cevap verir)
  Her alt grup n<10 ise ayri ayri "n YETERSIZ" raporlanir.

CANLI SISTEME ETKI: SIFIR. Bu betik hicbir alertcondition, hicbir
Pine dosyasi, hicbir islem/portfoy dosyasi YAZMAZ - sadece OKUR
(sinyal_arsiv.json) ve kendi cikti dosyasina (htf_golge_sonuc.json)
YAZAR.
"""
import datetime
import json
import statistics
import sys

import yfinance as yf

from json_atomik_yaz import atomik_json_yaz

ARSIV_YOL = "data/sinyal_arsiv.json"
CIKTI_YOL = "data/htf_golge_sonuc.json"
EMA_BURN_IN_SAAT = 150  # EMA50'nin stabilize olmasi icin gereken minimum 1s bar sayisi


def _ema_seri(degerler, periyot):
    """Basit EMA - liste halinde degerler uzerinde, ilk deger baz alinir."""
    if not degerler:
        return []
    k = 2.0 / (periyot + 1)
    sonuc = [degerler[0]]
    for v in degerler[1:]:
        sonuc.append(v * k + sonuc[-1] * (1 - k))
    return sonuc


def _saatlik_veri_cek(ticker, baslangic, bitis):
    """1 saatlik OHLC ceker. yfinance 1h icin ~730 gun geriye izin verir."""
    df = yf.Ticker(ticker).history(
        start=baslangic, end=bitis, interval="1h", auto_adjust=False
    )
    if df.empty:
        return None
    return df


def _dortsaatlik_turet(saatlik_df):
    """Yahoo Finance'te DOGAL '4 saat' araligi YOK (yalniz 1m/5m/15m/30m/
    60m/1d/1wk/1mo/3mo). 4s bari, 1s barlarindan kendimiz turetiyoruz -
    BIST seans baslangici 10:00 TSI oldugu icin 4'lu gruplama seans
    baslangicina hizalanir (00:00 UTC degil), yoksa gruplar gercek 4s
    mumlarla ORTUSMEZ."""
    if saatlik_df is None or saatlik_df.empty:
        return None
    df = saatlik_df.resample("4h", origin="start_day", offset="7h").agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    )
    df = df.dropna(subset=["Close"])
    return df


def _htf_align_hesapla(saatlik_1s, saatlik_4s, hedef_zaman):
    """hedef_zaman'daki (sinyal ani) htfAlign'i ESKI ve YENI yontemle hesaplar.
    Donen: (htfAlign_eski, htfAlign_yeni) ya da (None, None) veri yetersizse."""
    if saatlik_1s is None or saatlik_4s is None:
        return None, None

    kapaniclar_1s = saatlik_1s["Close"].tolist()
    zamanlar_1s = saatlik_1s.index.tolist()
    kapaniclar_4s = saatlik_4s["Close"].tolist()

    if len(kapaniclar_1s) < EMA_BURN_IN_SAAT or len(kapaniclar_4s) < 40:
        return None, None

    # --- YENI (dogru): EMA dogrudan native 1s/4s serisinde ---
    ema21_yeni = _ema_seri(kapaniclar_1s, 21)
    ema50_yeni = _ema_seri(kapaniclar_1s, 50)
    ema50_4s_yeni = _ema_seri(kapaniclar_4s, 50)

    # --- ESKI (hatali): repeated seri uzerinde EMA. 15dk'da 1s kapanisi
    # AYNI kalir (4 kez tekrar) - bu, EMA'nin ayni degeri 4 kez gormesi
    # anlamina gelir. Bunu simule etmek icin: her 1s kapanisini 4 kez
    # tekrar eden bir seri olusturup EMA'yi O SERIDE hesapliyoruz.
    tekrarli_1s = []
    for v in kapaniclar_1s:
        tekrarli_1s.extend([v, v, v, v])
    ema21_eski_tekrarli = _ema_seri(tekrarli_1s, 21)
    ema50_eski_tekrarli = _ema_seri(tekrarli_1s, 50)
    # Her 1s barinin "eski" EMA degeri, o barin son (4.) tekrarindaki deger
    ema21_eski = ema21_eski_tekrarli[3::4]
    ema50_eski = ema50_eski_tekrarli[3::4]

    tekrarli_4s = []
    for v in kapaniclar_4s:
        tekrarli_4s.extend([v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v])
    ema50_4s_eski_tekrarli = _ema_seri(tekrarli_4s, 50)
    ema50_4s_eski = ema50_4s_eski_tekrarli[15::16]

    # hedef_zaman'dan ONCEKI en son TAMAMLANMIS 1s/4s barini bul (Pine'daki
    # close[1] mantigi - bir onceki tamamlanmis bar)
    idx_1s = None
    for i, t in enumerate(zamanlar_1s):
        if t.to_pydatetime().replace(tzinfo=None) < hedef_zaman:
            idx_1s = i
        else:
            break
    if idx_1s is None or idx_1s < EMA_BURN_IN_SAAT:
        return None, None

    idx_4s = min(idx_1s // 4, len(ema50_4s_yeni) - 1, len(ema50_4s_eski) - 1)
    if idx_4s < 10:
        return None, None

    close_1s = kapaniclar_1s[idx_1s]
    close_4s = kapaniclar_4s[idx_4s]

    htfBull_yeni = close_1s > ema50_yeni[idx_1s] and ema21_yeni[idx_1s] > ema50_yeni[idx_1s]
    htf2Bull_yeni = close_4s > ema50_4s_yeni[idx_4s]
    htfAlign_yeni = (1 if htfBull_yeni else 0) + (1 if htf2Bull_yeni else 0)

    htfBull_eski = close_1s > ema50_eski[idx_1s] and ema21_eski[idx_1s] > ema50_eski[idx_1s]
    htf2Bull_eski = close_4s > ema50_4s_eski[idx_4s]
    htfAlign_eski = (1 if htfBull_eski else 0) + (1 if htf2Bull_eski else 0)

    return htfAlign_eski, htfAlign_yeni


def main():
    try:
        with open(ARSIV_YOL, encoding="utf-8") as f:
            arsiv = json.load(f)
    except FileNotFoundError:
        print(f"HATA: {ARSIV_YOL} yok", file=sys.stderr)
        sys.exit(1)

    kayitlar = [
        k for k in arsiv.get("kayitlar", [])
        if k["sinyal"] == "P3_SKOR_AL" and k["dogrulama_durumu"] == "DOGRULANDI"
    ]
    print(f"{len(kayitlar)} dogrulanmis P3_SKOR_AL kaydi bulundu")

    sembol_verisi = {}
    sonuclar = []
    bugun = datetime.date.today()

    for kayit in kayitlar:
        sembol = kayit["sembol"]
        sinyal_tarihi = datetime.date.fromisoformat(kayit["tarih"])
        hedef_zaman = datetime.datetime.combine(sinyal_tarihi, datetime.time(12, 0))

        if sembol not in sembol_verisi:
            baslangic_1s = (sinyal_tarihi - datetime.timedelta(days=30)).isoformat()
            bitis_1s = (bugun + datetime.timedelta(days=1)).isoformat()
            s1 = _saatlik_veri_cek(f"{sembol}.IS", baslangic_1s, bitis_1s)
            s4 = _dortsaatlik_turet(s1)  # Yahoo'da dogal 4s yok, 1s'ten turetildi
            sembol_verisi[sembol] = (s1, s4)

        s1s, s4s = sembol_verisi[sembol]
        eski, yeni = _htf_align_hesapla(s1s, s4s, hedef_zaman)
        if eski is None:
            continue

        sonuclar.append({
            "sembol": sembol, "tarih": kayit["tarih"],
            "htfAlign_eski": eski, "htfAlign_yeni": yeni,
            "farkli_mi": eski != yeni,
            "getiri_rel_t3_pct": kayit.get("getiri_rel_t3_pct"),
        })

    farkli = [s for s in sonuclar if s["farkli_mi"]]
    ayni = [s for s in sonuclar if not s["farkli_mi"]]
    yon_yukari = [s for s in farkli if s["htfAlign_yeni"] > s["htfAlign_eski"]]
    yon_asagi = [s for s in farkli if s["htfAlign_yeni"] < s["htfAlign_eski"]]
    print(f"{len(sonuclar)} kayit hesaplandi, {len(farkli)} farkli, {len(ayni)} ayni")

    ozet = {"n_toplam": len(sonuclar), "n_farkli": len(farkli), "n_ayni": len(ayni)}
    for grup_ad, grup in [("farkli", farkli), ("ayni", ayni),
                           ("yon_yukari", yon_yukari), ("yon_asagi", yon_asagi)]:
        vals = [s["getiri_rel_t3_pct"] for s in grup if s.get("getiri_rel_t3_pct") is not None]
        if len(vals) >= 2:
            ozet[f"{grup_ad}_ortalama_goreli_t3"] = round(statistics.mean(vals), 3)
            ozet[f"{grup_ad}_n"] = len(vals)
        else:
            ozet[f"{grup_ad}_durum"] = "n YETERSIZ"

    if len(farkli) < 10:
        ozet["hukum"] = "KANIT YETERSIZ - n<10, HTF duzeltmesinin canli etkisi belirsiz"
    else:
        ozet["hukum"] = "KARSILASTIRMA YAPILABILIR - detay icin farkli/ayni gruplarina bak"

    cikti = {
        "son_guncelleme_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "on_kayit": "27.08.2026 - yontem veri gorulmeden kilitlendi, htf_golge_analiz.py docstring",
        "ozet": ozet,
        "kayitlar": sonuclar,
    }
    atomik_json_yaz(CIKTI_YOL, cikti)
    print(f"Yazildi: {CIKTI_YOL}")
    print(json.dumps(ozet, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
