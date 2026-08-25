"""
KAP BİLDİRİM ÇEKİCİSİ (25.08.2026) — ÜRETİM

Google News proxy'si üzerinden KAP'a erişmenin çalışmadığı kanıtlandı
(site:kap.org.tr when:7d sorgusu 10 yıl önceki sonuçları döndürüyordu —
bkz. KONTROL_2026-08-24.md). Bu betik KAP'ın kendi JSON uç noktasını
doğrudan kullanır (kap_bildirim_prototip.py'nin üretim sürümü).

DOĞRULAMA (25.08): 11-13.08 penceresi sorgulandığında MGROS'un 699 mn
TL zarar açıklaması (11.08 22:46, "Özel Durum Açıklaması (Genel)")
gerçekten bulundu — ertesi günkü %-9,2 fiyat tepkisinden ÖNCE,
sistemin kendi zaman damgasından yakalanabilirdi.

TASARIM:
- Ayrı dosya (data/kap_bildirimleri.json) — haber_akisi.json'un
  puanlama/eleme mantığına karışmıyor, whitelist zaten temiz
- TÜR FİLTRESİ: yalnız DEGERLI_TURLER (KAP_TUR_SINIFLANDIRMA_2026-08-
  25.md'den, 72 kayıtlık örneğin ~%25'i). Finansal Rapor BİLEREK
  DIŞARIDA - bilanço takvimiyle çakışma riski
- PENCERE 2 GÜN (bugün dahil) - cron zamanlaması/gecikme ihtimaline
  karşı güvenlik payı, disclosureIndex ile dedupe edilip birleştirilir
- BİRİKİMLİ: yeni kayıtlar mevcut dosyaya eklenir (üzerine yazılmaz),
  45 günden eski kayıtlar budanır - dosya sınırsız büyümez
- SUNUCU TARAFI subjectList KULLANILMAZ (25.08 testinde muhtemelen OID
  bekleyip metni reddettiği görüldü, 292→0). İstemci tarafı tek yol

KIRMIZI ÇİZGİ: KAP'a erişilemezse SESSİZCE eski dosyayla devam etmez -
hata verip durur. Bu tek kaynaklı bir çağrı (fetch_bist.py'deki gibi
30 ayrı sembol sorgusu değil) - kısmi başarı diye bir şey yok, ya
tüm pencere gelir ya hiç gelmez.
"""
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone

from json_atomik_yaz import atomik_json_yaz
from universe import yukle_evren

KAP_URL = "https://www.kap.org.tr/tr/api/disclosure/members/byCriteria"
KAP_HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://www.kap.org.tr/tr/bildirim-sorgu",
    "User-Agent": "bist-veri/1.0 (kisisel arastirma amacli)",
}

DEGERLI_TURLER = [
    "Özel Durum Açıklaması (Genel)",
    "Pay Bazında Devre Kesici Bildirimi",
    "Kredi Derecelendirmesi",
    "Geleceğe Dönük Değerlendirmeler",
]

PENCERE_GUN = 2      # bugun dahil, kac gun geriye bakilir (cron guvenlik payi)
SAKLAMA_GUN = 45      # dosyada bu gunden eski kayit birikmez
DOSYA = "data/kap_bildirimleri.json"

TR_UTC_FARKI = timedelta(hours=3)  # Turkiye 2016'dan beri sabit UTC+3, DST yok


def _tarih_cevir(kap_tarih):
    """'26.05.2026 09:10:35' -> ISO UTC string. Bicim beklenenden
    farkliysa None doner (kayit atlanir, betik COKMEZ)."""
    try:
        yerel = datetime.strptime(kap_tarih, "%d.%m.%Y %H:%M:%S")
        return (yerel - TR_UTC_FARKI).replace(tzinfo=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return None


def kap_bildirimlerini_cek(from_date, to_date):
    govde = json.dumps({
        "fromDate": from_date.isoformat(),
        "toDate": to_date.isoformat(),
        "mkkMemberOidList": [],
        "subjectList": [],
    }).encode("utf-8")
    istek = urllib.request.Request(
        KAP_URL, data=govde, headers=KAP_HEADERS, method="POST")
    with urllib.request.urlopen(istek, timeout=20) as yanit:
        return json.loads(yanit.read().decode("utf-8"))


def _sembol_bul(bildirim, evren):
    """relatedStocks/stockCodes icinde EVREN'den ilk eslesen sembolu
    doner. Coklu sembollu bildirimlerde (orn. 'TRALT, TRMET') hepsini
    ayri ayri liste olarak doner."""
    alanlar = " ".join(str(bildirim.get(k) or "")
                       for k in ("relatedStocks", "stockCodes"))
    return [s for s in evren if s in alanlar]


def isle(ham, evren):
    """Ham KAP kayitlarini tur+evren filtresinden gecirir, her
    sembol icin AYRI kayit uretir (coklu-sembollu bildirim = birden
    fazla cikti kaydi, brifing/risk katmani sembol bazinda okuyacagi
    icin)."""
    sonuc = []
    for b in ham:
        if b.get("subject") not in DEGERLI_TURLER:
            continue
        semboller = _sembol_bul(b, evren)
        if not semboller:
            continue
        tarih_utc = _tarih_cevir(b.get("publishDate", ""))
        for sembol in semboller:
            sonuc.append({
                "disclosureIndex": b.get("disclosureIndex"),
                "tarih_utc": tarih_utc,
                "sembol": sembol,
                "tur": b.get("subject"),
                "ozet": b.get("summary"),
                "gec_bildirim": bool(b.get("isLate")),
            })
    return sonuc


def birlestir_ve_budama(eski_kayitlar, yeni_kayitlar):
    """disclosureIndex+sembol ile dedupe eder (coklu-sembollu bildirim
    her sembol icin ayri kayit oldugundan ikisi birlikte anahtar),
    SAKLAMA_GUN'den eski kayitlari budar."""
    birlesik = {}
    for k in eski_kayitlar + yeni_kayitlar:
        anahtar = (k.get("disclosureIndex"), k.get("sembol"))
        birlesik[anahtar] = k  # yeni veri eskinin uzerine yazar (guncel)

    sinir = (datetime.now(timezone.utc) - timedelta(days=SAKLAMA_GUN)).isoformat()
    kalan = [k for k in birlesik.values()
             if k.get("tarih_utc") and k["tarih_utc"] >= sinir]
    kalan.sort(key=lambda k: k.get("tarih_utc") or "")
    return kalan


def main():
    try:
        evren, _ = yukle_evren()
    except Exception as e:
        print(f"HATA: universe.py okunamadi -> {e}", file=sys.stderr)
        sys.exit(1)

    bugun = date.today()
    baslangic = bugun - timedelta(days=PENCERE_GUN - 1)

    try:
        ham = kap_bildirimlerini_cek(baslangic, bugun)
    except Exception as e:
        print(f"HATA: KAP'a erisilemedi -> {type(e).__name__}: {e}",
              file=sys.stderr)
        print("Sessizce eski dosyayla devam ETMIYORUZ - tek kaynakli "
              "cagri, kismi basari yok.", file=sys.stderr)
        sys.exit(1)

    yeni = isle(ham, evren)

    try:
        with open(DOSYA, encoding="utf-8") as f:
            eski_kayitlar = json.load(f).get("bildirimler", [])
    except FileNotFoundError:
        eski_kayitlar = []
    except json.JSONDecodeError as e:
        print(f"UYARI: {DOSYA} bozuk, sifirdan baslaniyor -> {e}",
              file=sys.stderr)
        eski_kayitlar = []

    birlesik = birlestir_ve_budama(eski_kayitlar, yeni)

    cikti = {
        "guncelleme_zamani_utc": datetime.now(timezone.utc).isoformat(),
        "aciklama": ("KAP'tan DOGRUDAN cekilen, evrenimizdeki sembollere "
                    "ait ozel-durum tipi bildirimler. Google News uzerinden "
                    "DEGIL - KAP'in kendi JSON ucnoktasindan."),
        "tur_beyaz_listesi": DEGERLI_TURLER,
        "saklama_gun": SAKLAMA_GUN,
        "son_pencere": {"baslangic": baslangic.isoformat(),
                        "bitis": bugun.isoformat(),
                        "ham_kayit": len(ham), "yeni_kayit": len(yeni)},
        "bildirimler": birlesik,
    }
    atomik_json_yaz(DOSYA, cikti)

    print(f"KAP: {len(ham)} ham -> {len(yeni)} yeni (tur+evren filtreli) "
          f"-> dosyada toplam {len(birlesik)} kayit")


if __name__ == "__main__":
    main()
