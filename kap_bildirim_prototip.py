"""
KAP BİLDİRİM PROTOTİPİ (24.08.2026) — SALT DENEME, ÜRETİME BAĞLI DEĞİL

Amaç: Google News proxy'si üzerinden KAP'a erişmenin çalışmadığını
kanıtladık (dünkü ölçüm: site:kap.org.tr when:7d sorgusu 10 yıl önceki
sonuçları döndürüyordu). Bu betik, KAP'ın kendi web sitesinin arka
planındaki JSON uç noktasını doğrudan kullanır.

KAYNAK: caganco/trailingedge deposu (github.com), KAP_ENDPOINT_NOTES.md
— topluluk tarafından belgelenmiş, resmi olmayan ama kimlik doğrulama
ve CAPTCHA gerektirmeyen bir uç nokta. Veri zaten yasal olarak kamuya
açık (KAP'in kuruluş amacı bu). robots.txt HTTP 666 dönüyor (özel WAF
reddi, standart "yasak" sinyali değil) — bu notta belirtiliyor,
kararı etkilemek için değil, şeffaflık için.

BU BETİK NE YAPMAZ:
- Hiçbir dosyaya yazmaz (yalnız konsola basar)
- fetch_news.py'ye bağlı değil, ona dokunmaz
- PDF indirmiyor / açmıyor (KAP_ENDPOINT_NOTES.md §3.2-3.3) — yalnız
  liste uç noktasını (§3.1) kullanıyor, bizim ihtiyacımız (başlık +
  tarih + ilgili sembol) için yeterli
- Bu ortamdan test EDİLEMEDİ — kap.org.tr bu sandbox'ın izin verilen
  ağ listesinde yok. Altuğ'un GitHub Actions'ta ya da yerel makinede
  çalıştırıp çıktıyı göndermesi gerekiyor.

ÇALIŞTIRMA:
    python kap_bildirim_prototip.py           # son 1 gün
    python kap_bildirim_prototip.py --gun 3   # son 3 gün
"""
import argparse
import json
import sys
import time
import urllib.request
from datetime import date, timedelta

try:
    from universe import yukle_evren
    EVREN, _ = yukle_evren()
except Exception as e:
    print(f"UYARI: universe.py okunamadi ({e}) — evren filtresi "
          "uygulanmayacak, TUM bildirimler gosterilecek.", file=sys.stderr)
    EVREN = None

KAP_URL = "https://www.kap.org.tr/tr/api/disclosure/members/byCriteria"
KAP_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://www.kap.org.tr/tr/bildirim-sorgu",
    "User-Agent": "bist-veri-arastirma/0.1 (kisisel arastirma amacli)",
}
# KAP_ENDPOINT_NOTES.md §4: onerilen 2 istek/sn, biz tek istekte
# kaliyoruz (gunluk pencere), rate limit sorunu beklenmiyor.


def kap_bildirimlerini_cek(from_date, to_date):
    """POST /tr/api/disclosure/members/byCriteria. Ham liste doner."""
    govde = json.dumps({
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat(),
        "mkkMemberOidList": [],
        "subjectList": [],
    }).encode("utf-8")
    istek = urllib.request.Request(
        KAP_URL, data=govde, headers=KAP_HEADERS, method="POST")
    with urllib.request.urlopen(istek, timeout=15) as yanit:
        return json.loads(yanit.read().decode("utf-8"))


def evren_filtresi(bildirimler):
    """relatedStocks/stockCodes alanlarindan EVREN'deki sembolleri iceren
    bildirimleri suzer. Evren yuklenemezse suzme yapilmaz (yukarida
    uyarildi)."""
    if EVREN is None:
        return bildirimler
    sonuc = []
    for b in bildirimler:
        alanlar = " ".join(str(b.get(k) or "")
                           for k in ("relatedStocks", "stockCodes"))
        if any(sembol in alanlar for sembol in EVREN):
            sonuc.append(b)
    return sonuc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gun", type=int, default=1,
                    help="Kac gunluk pencere (varsayilan: 1)")
    args = ap.parse_args()

    bugun = date.today()
    baslangic = bugun - timedelta(days=args.gun)

    print(f"KAP sorgusu: {baslangic} -> {bugun}")
    try:
        ham = kap_bildirimlerini_cek(baslangic, bugun)
    except Exception as e:
        print(f"HATA: KAP'a erisilemedi -> {type(e).__name__}: {e}",
              file=sys.stderr)
        print("Bu ortamdan (GitHub Actions / yerel makine) calistirildiginda "
              "farkli sonuc verebilir - sandbox'ta kap.org.tr'ye ag "
              "erisimi yok.", file=sys.stderr)
        sys.exit(1)

    print(f"Toplam bildirim (tum sirketler): {len(ham)}")
    if len(ham) >= 2000:
        print("UYARI: yanit 2000 sinirina dayanmis olabilir - pencereyi "
              "daralt (KAP_ENDPOINT_NOTES.md §8)", file=sys.stderr)

    suzulen = evren_filtresi(ham)
    print(f"Evrenimizdeki sembollere ait bildirim: {len(suzulen)}")
    print()

    for b in sorted(suzulen, key=lambda x: x.get("publishDate", "")):
        print(f"  {b.get('publishDate','?'):20} "
              f"{(b.get('relatedStocks') or b.get('stockCodes') or '?'):10} "
              f"{b.get('subject','?')}")


if __name__ == "__main__":
    main()
