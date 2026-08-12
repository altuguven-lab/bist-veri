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
EVDS_TEMEL_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/series={seri}&startDate={baslangic}&endDate={bitis}&type=json"

USD_TRY_SERI = "TP.DK.USD.A.YTL"
# 11.08 EKI: tcmb_faiz_seri_kesif.py ile DOGRULANDI (bkz. o script'in
# ADIM 3 ciktisi) - Turkiye MB politika faizi, BIS karsilastirma
# serisinin ICINDE.
POLITIKA_FAIZ_SERI = "TP.BISPOLFAIZ.TUR"
# EVDS coklu-seri destegi: seriler "-" ile AYRILARAK TEK istekte cekilir
# (resmi belgede dogrulandi: "TP.DK.USD.S-TP.DK.EUR.S" ornegi).
TUM_SERILER = f"{USD_TRY_SERI}-{POLITIKA_FAIZ_SERI}"


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
    # 10.08 EKI: resmi EVDS belgesi ("Web Servis ve API Kullanimi",
    # docId=8) ACIKCA UYARIYOR - "sorgunun surekli GUNCEL veriyi almasi
    # icin bu alana COK UZAK bir tarih yaziniz. Ornegin 01-01-2999."
    # Bu yuzden bitis tarihi olarak BUGUN yerine UZAK bir GELECEK
    # tarih KULLANILIYOR - guncel veriyi GUVENILIR sekilde almak icin.
    bitis_sorgu = datetime.date(2999, 1, 1)

    # 12.08 DUZELTME: coklu-seri istegi (USD/TRY-POLITIKA_FAIZ) BOZUK
    # veri uretiyordu - politika faizi HEP None geliyordu, VE tarih
    # formati GUNLUK yerine AYLIK'a DONUSMUSTU. HIPOTEZ: TP.BISPOLFAIZ.
    # TUR AYLIK bir seri, USD/TRY GUNLUK - EVDS coklu-seri BIRLESTIRMESI
    # bu ikisini DAHA DUSUK (aylik) frekansa INDIRGIYORDU. DUZELTME:
    # HER IKI seri AYRI AYRI cekilir - hem frekans sorunu COZULUR hem
    # bir serinin BASARISIZ olmasi DIGERINI ETKILEMEZ (daha SAGLAM).
    try:
        usd_veri = evds_veri_cek(USD_TRY_SERI, baslangic, bitis_sorgu, anahtar)
        usd_kayitlar = usd_veri.get("items", [])
        print(f"{len(usd_kayitlar)} USD/TRY kaydi cekildi")
    except Exception as e:
        print(f"HATA: USD/TRY cekilemedi -> {e}", file=sys.stderr)
        usd_kayitlar = []

    try:
        faiz_veri = evds_veri_cek(POLITIKA_FAIZ_SERI, baslangic, bitis_sorgu, anahtar)
        faiz_kayitlar = faiz_veri.get("items", [])
        print(f"{len(faiz_kayitlar)} politika faizi kaydi cekildi")
    except Exception as e:
        print(f"HATA: politika faizi cekilemedi -> {e}", file=sys.stderr)
        faiz_kayitlar = []

    if not usd_kayitlar and not faiz_kayitlar:
        print("HATA: HICBIR seri icin veri gelmedi", file=sys.stderr)
        sys.exit(1)

    def alan_bul(kayit, seri):
        alt_cizgili = seri.replace(".", "_")
        return kayit.get(seri, kayit.get(alt_cizgili))

    print("  -- USD/TRY (son 3) --")
    for k in usd_kayitlar[-3:]:
        print(f"     {k.get('Tarih')}: {alan_bul(k, USD_TRY_SERI)}")
    print("  -- Politika Faizi (son 3) --")
    for k in faiz_kayitlar[-3:]:
        print(f"     {k.get('Tarih')}: {alan_bul(k, POLITIKA_FAIZ_SERI)}")

    rapor = {
        "cekim_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kaynak": "TCMB EVDS - resmi Merkez Bankasi veri sistemi",
        "baslangic_tarihi": str(baslangic), "bitis_tarihi_sorgu": str(bitis_sorgu),
        "cekim_tarihi": str(bugun),
        "usd_try_seri_kodu": USD_TRY_SERI, "usd_try_kayitlar": usd_kayitlar,
        "politika_faiz_seri_kodu": POLITIKA_FAIZ_SERI, "politika_faiz_kayitlar": faiz_kayitlar,
        # geriye-uyum: eski "kayitlar" alanini USD/TRY ile DOLDUR (makro_
        # guncel_durum.py hala BU alani okuyor - Faz sonraki adimda
        # o script de GUNCELLENMELI, simdilik BOZULMAMASI icin).
        "kayitlar": usd_kayitlar,
    }
    atomik_json_yaz("data/tcmb_evds_veri.json", rapor)
    print(f"\nYazildi: data/tcmb_evds_veri.json")


if __name__ == "__main__":
    main()
