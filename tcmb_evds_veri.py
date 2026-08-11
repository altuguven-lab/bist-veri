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

EVDS_TEMEL_URL = "https://evds2.tcmb.gov.tr/service/evds/series={seri}&startDate={baslangic}&endDate={bitis}&type=json&key={anahtar}"

USD_TRY_SERI = "TP.DK.USD.A.YTL"


def tarih_evds_format(tarih):
    return tarih.strftime("%d-%m-%Y")


def evds_veri_cek(seri, baslangic, bitis, anahtar):
    url = EVDS_TEMEL_URL.format(seri=seri, baslangic=tarih_evds_format(baslangic),
                                  bitis=tarih_evds_format(bitis), anahtar=anahtar)
    istek = urllib.request.Request(url, headers={"User-Agent": "bist-veri-arastirma-botu"})
    with urllib.request.urlopen(istek, timeout=20) as yanit:
        ham = yanit.read().decode("utf-8")
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
