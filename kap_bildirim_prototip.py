"""
KAP BİLDİRİM PROTOTİPİ v2 (25.08.2026) — SALT DENEME, ÜRETİME BAĞLI DEĞİL

v1'den fark: iki şeyi TEK koşuda test ediyor.

1) SUNUCU TARAFI subjectList filtresi gerçekten çalışıyor mu?
   KAP_ENDPOINT_NOTES.md şöyle diyor: "subjectList: ... list of subject
   OID strings" — yani OID bekliyor olabilir, düz TÜRKÇE METİN değil.
   Elimizde OID yok, yalnız gözlemlediğimiz metin değerleri var
   ("Özel Durum Açıklaması (Genel)" vb.). Bu betik metni doğrudan
   deneyip API'nin onu tanıyıp tanımadığını AYNI PENCERE için iki ayrı
   istekle (filtresiz vs filtreli) kıyaslayarak ölçer. Sayılar
   birbirine yakınsa/aynıysa → sunucu metni yok sayıyor, OID gerekiyor.
   İkinci sayı belirgin küçükse → metin filtresi ÇALIŞIYOR.

2) İSTEMCİ TARAFI beyaz liste — 25.08'de 72 kayıtlık örnekten
   çıkardığımız dört tür (KAP_TUR_SINIFLANDIRMA_2026-08-25.md). Sunucu
   filtresi çalışmasa bile bu HER ZAMAN devreye girer — üretim için
   güvenilir yol budur, sunucu filtresi yalnız "daha az veri çeksek mi"
   sorusuna cevap.

BU BETİK NE YAPMAZ: hiçbir dosyaya yazmaz, fetch_news.py'ye dokunmaz.
"""
import argparse
import json
import sys
import urllib.request
from datetime import date, timedelta

try:
    from universe import yukle_evren
    EVREN, _ = yukle_evren()
except Exception as e:
    print(f"UYARI: universe.py okunamadi ({e}) — evren filtresi yok.",
          file=sys.stderr)
    EVREN = None

KAP_URL = "https://www.kap.org.tr/tr/api/disclosure/members/byCriteria"
KAP_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://www.kap.org.tr/tr/bildirim-sorgu",
    "User-Agent": "bist-veri-arastirma/0.2 (kisisel arastirma amacli)",
}

# 25.08 sınıflandırmasından (72 kayıtlık örnek, ~%25'i bu dört tür).
# Finansal Rapor BİLEREK DIŞARIDA — bilanço takvimiyle çakışma riski.
DEGERLI_TURLER = [
    "Özel Durum Açıklaması (Genel)",
    "Pay Bazında Devre Kesici Bildirimi",
    "Kredi Derecelendirmesi",
    "Geleceğe Dönük Değerlendirmeler",
]


def kap_bildirimlerini_cek(from_date, to_date, subject_list=None):
    govde = json.dumps({
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat(),
        "mkkMemberOidList": [],
        "subjectList": subject_list or [],
    }).encode("utf-8")
    istek = urllib.request.Request(
        KAP_URL, data=govde, headers=KAP_HEADERS, method="POST")
    with urllib.request.urlopen(istek, timeout=15) as yanit:
        return json.loads(yanit.read().decode("utf-8"))


def evren_filtresi(bildirimler):
    if EVREN is None:
        return bildirimler
    sonuc = []
    for b in bildirimler:
        alanlar = " ".join(str(b.get(k) or "")
                           for k in ("relatedStocks", "stockCodes"))
        if any(sembol in alanlar for sembol in EVREN):
            sonuc.append(b)
    return sonuc


def tur_beyaz_listesi(bildirimler):
    return [b for b in bildirimler if b.get("subject") in DEGERLI_TURLER]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gun", type=int, default=1,
                    help="Kac gunluk pencere (varsayilan: 1, en fazla 3)")
    args = ap.parse_args()
    if args.gun > 3:
        print("UYARI: --gun 3'u asiyor, 2000 tavanina carpma riski "
              "(25.08 bulgusu). 3'e sabitleniyor.", file=sys.stderr)
        args.gun = 3

    bugun = date.today()
    baslangic = bugun - timedelta(days=args.gun)
    print(f"KAP sorgusu: {baslangic} -> {bugun}\n")

    # --- ADIM 1: filtresiz (baseline) ---
    try:
        ham = kap_bildirimlerini_cek(baslangic, bugun, subject_list=[])
    except Exception as e:
        print(f"HATA: KAP'a erisilemedi -> {type(e).__name__}: {e}",
              file=sys.stderr)
        sys.exit(1)
    print(f"[1] FİLTRESİZ istek — toplam bildirim: {len(ham)}")
    if len(ham) >= 2000:
        print("    UYARI: 2000 tavanina carpmis olabilir", file=sys.stderr)

    # --- ADIM 2: sunucu tarafi subjectList denemesi ---
    try:
        sunucu_filtreli = kap_bildirimlerini_cek(
            baslangic, bugun, subject_list=DEGERLI_TURLER)
    except Exception as e:
        print(f"HATA: sunucu-filtreli istek basarisiz -> {e}",
              file=sys.stderr)
        sunucu_filtreli = None

    if sunucu_filtreli is not None:
        print(f"[2] SUNUCU-FİLTRELİ istek (subjectList=4 tur metni) — "
              f"toplam bildirim: {len(sunucu_filtreli)}")
        if len(sunucu_filtreli) == len(ham):
            print("    SONUÇ: sayılar AYNI — sunucu metni muhtemelen YOK "
                  "SAYDI (OID bekliyor olabilir). İstemci tarafı beyaz "
                  "liste her durumda gerekli.")
        elif len(sunucu_filtreli) < len(ham):
            print(f"    SONUÇ: sayı düştü ({len(ham)} → "
                  f"{len(sunucu_filtreli)}) — sunucu filtresi ÇALIŞIYOR "
                  "gibi görünüyor. Yine de aşağıdaki istemci-taraflı "
                  "sonuçla karşılaştır.")
        else:
            print("    SONUÇ: sayı ARTTI — beklenmeyen davranış, "
                  "yoruma dikkatli yaklaş.")
    print()

    # --- ADIM 3: istemci tarafi beyaz liste + evren filtresi (guvenilir yol) ---
    tur_suzulen = tur_beyaz_listesi(ham)
    nihai = evren_filtresi(tur_suzulen)
    print(f"[3] İSTEMCİ TARAFI (her zaman uygulanır): "
          f"{len(ham)} → tür beyaz listesi → {len(tur_suzulen)} "
          f"→ evren filtresi → {len(nihai)}\n")

    for b in sorted(nihai, key=lambda x: x.get("publishDate", "")):
        print(f"  {b.get('publishDate','?'):20} "
              f"{(b.get('relatedStocks') or b.get('stockCodes') or '?'):10} "
              f"{b.get('subject','?')}")


if __name__ == "__main__":
    main()
