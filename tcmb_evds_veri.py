"""
TCMB_EVDS_VERI (10.08.2026) - Faz V0
Merkez Bankasi'nin resmi EVDS (Elektronik Veri Dagitim Sistemi) API'sinden
USD/TRY kurunu ceker. Kullanicinin 10.08 arastirmasi uzerine kuruldu -
makro_hassasiyet_haritasi.json'daki "USD_TRY_KURU" gibi faktorleri
GERCEK veriyle DOLDURMAK icin ilk adim.

API ANAHTARI: kod icinde HICBIR ZAMAN acik yazilmaz - ortam degiskeni
(TCMB_EVDS_API_KEY, GitHub Secret) olarak okunur.

KIRMIZI CIZGI: SALT VERI CEKME, Pine'a hic dokunmuyor, hicbir sinyal/
karar URETMEZ.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime, os, sys
import urllib.request
import urllib.error

# 10.08 DUZELTME: EVDS GUVENLIK GUNCELLEMESI - key artik URL parametresi
# DEGIL, HTTP HEADER olarak gonderilmeli (iki bagimsiz kaynaktan
# dogrulandi - TCMB bu degisikligi resmi olarak duyurmus).
EVDS_TEMEL_URL = "https://evds2.tcmb.gov.tr/service/evds/series={seri}&startDate={baslangic}&endDate={bitis}&type=json"

USD_TRY_SERI = "TP.DK.USD.A.YTL"


def tarih_evds_format(tarih):
    return tarih.strftime("%d-%m-%Y")


def evds_veri_cek(seri, baslangic, bitis, anahtar):
    url = EVDS_TEMEL_URL.format(seri=seri, baslangic=tarih_evds_format(baslangic),
                                  bitis=tarih_evds_format(bitis))
    print(f"TESHIS: istek URL'i -> {url}", file=sys.stderr)
    print(f"TESHIS: anahtar uzunlugu -> {len(anahtar)} karakter (HEADER'da gonderiliyor)", file=sys.stderr)

    # 10.08 DUZELTME: key artik HEADER'da - EVDS'nin guvenlik
    # guncellemesi geregi (URL'de gonderilirse SESSIZCE bos yanit
    # donuyor - onceki denemede HTTP 200/0-bayt olarak GOZLEMLENDI).
    istek = urllib.request.Request(url, headers={
        "User-Agent": "bist-veri-arastirma-botu",
        "Accept": "application/json",
        "key": anahtar,
    })
    with urllib.request.urlopen(istek, timeout=20) as yanit:
        durum_kodu = yanit.status if hasattr(yanit, "status") else yanit.getcode()
        ham_bytes = yanit.read()
    print(f"TESHIS: HTTP durum kodu -> {durum_kodu}", file=sys.stderr)
    print(f"TESHIS: yanit uzunlugu -> {len(ham_bytes)} bayt", file=sys.stderr)
    ham = ham_bytes.decode("utf-8", errors="replace")
    print(f"TESHIS: yanitin ilk 300 karakteri -> {ham[:300]!r}", file=sys.stderr)
    if not ham.strip():
        raise ValueError(f"EVDS BOS yanit dondurdu (HTTP {durum_kodu}) - "
                          f"anahtar GECERSIZ olabilir ya da baska bir sorun var.")
    return json.loads(ham)


def main():
    anahtar = os.environ.get("TCMB_EVDS_API_KEY")
    if not anahtar:
        print("HATA: TCMB_EVDS_API_KEY ortam degiskeni bulunamadi - "
              "GitHub Secret olarak eklendi mi kontrol edin.", file=sys.stderr)
        sys.exit(1)

    bugun = datetime.date.today()
    baslangic = bugun - datetime.timedelta(days=30)

    try:
        veri = evds_veri_cek(USD_TRY_SERI, baslangic, bugun, anahtar)
    except urllib.error.HTTPError as e:
        print(f"HATA: EVDS API HTTP hatasi -> {e.code} {e.reason}", file=sys.stderr)
        print("Olasi nedenler: API anahtari eksik/yanlis kopyalanmis, "
              "ya da seri kodu gecersiz.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"HATA: EVDS veri cekilemedi -> {e}", file=sys.stderr)
        sys.exit(1)

    kayitlar = veri.get("items", [])
    print(f"{len(kayitlar)} gunluk USD/TRY kaydi cekildi")
    if not kayitlar:
        print("UYARI: kayit listesi bos - seri kodu/tarih araligi kontrol edilmeli", file=sys.stderr)

    # 10.08 NOT: EVDS'nin JSON alan adi formati (nokta mi alt cizgi mi)
    # KESIN dogrulanamadi (gercek API cagrisi bu ortamda YAPILAMADI) -
    # HER IKI olasi formati da dener, ikisi de basarisizsa HAM kaydi
    # gosterir ki format sorunu GORULEBILSIN.
    alt_cizgili = USD_TRY_SERI.replace(".", "_")
    for k in kayitlar[-5:]:
        deger = k.get(USD_TRY_SERI, k.get(alt_cizgili))
        if deger is None:
            print(f"  {k.get('Tarih')}: DEGER BULUNAMADI - ham kayit: {k}")
        else:
            print(f"  {k.get('Tarih')}: {deger}")

    rapor = {
        "cekim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kaynak": "TCMB EVDS - resmi Merkez Bankasi veri sistemi",
        "seri_kodu": USD_TRY_SERI,
        "baslangic_tarihi": str(baslangic), "bitis_tarihi": str(bugun),
        "kayitlar": kayitlar,
    }
    atomik_json_yaz("data/tcmb_evds_veri.json", rapor)
    print(f"\nYazildi: data/tcmb_evds_veri.json")


if __name__ == "__main__":
    main()
