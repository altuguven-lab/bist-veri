"""KAP BILDIRIM PDF OZETLERI - 26.11.2026 (paket60). SALT VERI, TAVSIYE DEGILDIR.

Neden: Brifing gorevlerinin calistigi ortam kap.org.tr PDF'lerine erisemiyor (ag gecidi 403). Bu yuzden
her brifingte "KAP BildirimPdf ✖" yaziliyor ve ornegin FROTO hak kullaniminin turu bilinemiyordu.
GitHub Actions acik internette calisir: PDF'ler burada indirilir, kisa bir ozet ve yapilandirilmis alanlar
data/kap_pdf_ozet.json'a yazilir; brifing ozeti depodan (✅) okur.

Kapsam (gunde birkac on bildirim, en fazla AZAMI_PDF):
  - BIST 100 sirketlerinin (config/bist100_uyeler.txt) ONEMLI konulu kendi bildirimleri (ONEMLI_SIRKET).
  - Kurum bildirimleri (Borsa Istanbul, KAP, MKK, SPK) icinde ONEMLI_KURUM konulari.
  Rutin bildirimler (pay geri alim, faiz iceren arac, piyasa yapicilik, genel bilgi formu, varant, devre kesici)
  alinmaz; bunlarin KAP ozet satiri zaten arsivde var.

Kurallar:
  - robots.txt'e uyulur (kurum_taramasi.izinli). Izin yoksa PDF indirilmez, durum "ROBOTS_IZIN_YOK" yazilir,
    brifing bunu ⛔ olarak verir. Erisim korumasi asilmaz.
  - Kisi adi saklanmaz: SPK tedbir / islem yasagi gibi kisi iceren konularda METIN saklanmaz, yalniz gecen borsa
    kodlari ve karar sozcukleri sayilir. Diger metinlerde "Ad SOYAD" kalibi [kisi] ile maskelenir.
  - Metnin tamami degil, "Aciklamalar" bolumunden en fazla OZET_KARAKTER karakter saklanir (depo herkese acik).
"""
import datetime as dt
import glob
import gzip
import io
import json
import os
import re
import sys
import time

import kurum_taramasi as kt   # izinli(), getir(), UA: ayni robots ve istek kurallari

CIKTI = "data/kap_pdf_ozet.json"
CIKTI_MD = "data/kap_pdf_ozet.md"
KAP_ARSIV = "data/arsiv/kap"
PDF_URL = "https://www.kap.org.tr/tr/api/BildirimPdf/{}"
AZAMI_PDF = 40          # tek calismada en fazla indirilecek yeni PDF
OZET_KARAKTER = 600
SAKLA_GUN = 10
GERI_GUN = 2            # bugun + onceki 2 takvim gunu taranir

ONEMLI_SIRKET = r"Özel Durum Açıklaması|Kredi Derecelendirme|Kar Payı|Ortaklık Aleyhine Dava|Yeni İş İlişkisi|" \
                r"İhale Süreci|Finansal Duran Varlık|Sermaye Artırım|Hak Kullanım|Geleceğe Dönük|Esas Sözleşme|" \
                r"Birleşme|Bölünme|Pay Satın Alma|Pay Satış|Önemli Nitelikteki İşlem|Maddi Duran Varlık|" \
                r"Ödenmeyen|Temerrüt|Konkordato|İflas|Tasfiye|Kayyum|Kayyım|Borsada İşlem Görmeye"
ONEMLI_KURUM = r"Hak Kullanımı|Pazar Değişikliği|İşlem Sırası|Alım Satım Sistemi Duyurusu|Fiili Dolaşım|" \
               r"Borsa İstanbul A\.Ş\. Duyurusu|Kamuyu Aydınlatma Platformu Duyurusu|Merkezi Kayıt Kuruluşu A\.Ş\. Duyurusu|" \
               r"Tedbir Kararı|İşlem Yasağı|Kayyum|Kayyım|Tasfiye|Volatilite|Devre Kesici Kural|Brüt Takas|Kredili İşlem|Açığa Satış"
KISI_ICEREN = r"Tedbir Kararı|İşlem Yasağı|Pay Alım Satım|Yönetim Kurulu|Görev Değişikliği|Atama|Genel Müdür|İstifa|" \
              r"Dava|12-\(4\)|Kamuyu Aydınlatma Platformu Duyurusu|Merkezi Kayıt Kuruluşu A\.Ş\. Duyurusu"
# 26.11 (bagimsiz inceleme): ad maskeleme her kalibi yakalamiyor. Bu yuzden METIN yalniz kisi icermesi beklenmeyen
# konularda saklanir (beyaz liste); digerlerinde yalniz yapilandirilmis alanlar ve kodlar tutulur.
METIN_GUVENLI = r"Hak Kullanım|Kredi Derecelendirme|Kar Payı|Yeni İş İlişkisi|İhale Süreci|Finansal Duran Varlık|" \
                r"Maddi Duran Varlık|Sermaye Artırım|Pazar Değişikliği|İşlem Sırası|Fiili Dolaşım|Volatilite|" \
                r"Birleşme|Bölünme|Borsada İşlem Görmeye"
AZAMI_SAYFA = 3          # uzun belgelerde yalniz ilk sayfalar ayristirilir
AZAMI_DENEME = 3         # basarisiz bir bildirim en fazla bu kadar yeniden denenir
ARDISIK_HATA_SINIR = 5   # art arda bu kadar hata -> calisma durur (site geneli engel olabilir)

KARAR_SOZCUKLERI = {"tedbir": r"tedbir", "islem_yasagi": r"işlem yasağı", "kayyum": r"kayyum|kayyım|TMSF",
                    "tasfiye": r"tasfiye", "suc_duyurusu": r"suç duyurusu", "temerrut": r"temerrüt|ödenmey",
                    "konkordato": r"konkordato", "iflas": r"iflas"}


def simdi_tr():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))


def evren():
    try:
        return {l.strip() for l in open("config/bist100_uyeler.txt", encoding="utf-8")
                if l.strip() and not l.startswith("#")}
    except OSError:
        return set()


def kodlar_of(b):
    """Sirket bildiriminde stockCodes, kurum bildiriminde relatedStocks dolu olur."""
    ham = ",".join(x for x in (b.get("stockCodes"), b.get("relatedStocks")) if x)
    return list(dict.fromkeys(k.strip() for k in ham.split(",") if k.strip()))


def arsiv_bildirimleri(bugun):
    out = []
    for g in range(GERI_GUN, -1, -1):
        gun = bugun - dt.timedelta(days=g)
        yol = f"{KAP_ARSIV}/{gun:%Y/%m/%d}.json.gz"
        if os.path.exists(yol):
            try:
                out += json.load(gzip.open(yol)).get("bildirimler", [])
            except Exception as e:
                print(f"UYARI: {yol}: {e}", file=sys.stderr)
    return out


def sec(bildirimler, uy):
    """(oncelik, bildirim, tur) listesi. Oncelik: kurum > BIST100 sirket."""
    secilen = []
    for b in bildirimler:
        konu = b.get("subject") or ""
        tam = f"{konu} {b.get('summary') or ''}"        # kurum bildiriminde asil konu ozet satirinda (ör. "Hak Kullanımı")
        kod = kodlar_of(b)
        if not b.get("stockCodes") or b.get("kapTitle", "").startswith(("BORSA İSTANBUL", "KAMUYU AYDINLATMA", "MERKEZİ KAYIT",
                                                         "SERMAYE PİYASASI KURULU")):
            # piyasa geneli (kodsuz) ya da BIST 100 sirketini ilgilendiren kurum bildirimleri; devre kesici ve
            # islem iptali bildirimleri rutin (KAP ozet satiri yeterli)
            if re.search(ONEMLI_KURUM, tam, re.I) and (not kod or set(kod) & uy) \
                    and not re.search(r"Devre Kesici Bildirimi|VİOP İşlem İptal|^İşlem İptali", konu, re.I):
                secilen.append((0, b, "kurum"))
        elif set(kod) & uy and re.search(ONEMLI_SIRKET, konu, re.I):
            secilen.append((1, b, "sirket"))
    secilen.sort(key=lambda x: (x[0], -(x[1].get("disclosureIndex") or 0)))
    return secilen


def pdf_metin(ham):
    yazilar = []
    try:
        from pypdf import PdfReader
        yazilar.append(" ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(ham)).pages[:AZAMI_SAYFA]))
    except Exception as e:
        print(f"pypdf: {e}", file=sys.stderr)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(ham)) as pdf:
            yazilar.append(" ".join((p.extract_text() or "") for p in pdf.pages[:AZAMI_SAYFA]))
    except Exception as e:
        print(f"pdfplumber: {e}", file=sys.stderr)
    return max((" ".join(y.split()) for y in yazilar), key=len, default="")


KISI_DESEN = re.compile(r"\b(?:Sayın\s+|Sn\.\s*)?[A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?\s+[A-ZÇĞİÖŞÜ]{2,}\b"
                        r"(?!\s*(?:A\.Ş|AŞ|LTD|A\.S))")


SIRKET_SOZCUK = r"A\.Ş|AŞ|SANAY|TİCARET|TICARET|HOLD|BANKA|YATIRIM|ENERJ|GAYRİMENKUL|GYO|OTOMOT|SİGORTA|SIGORTA|" \
                r"FAKTOR|FİNANS|FINANS|ELEKTR|MADEN|İNŞAAT|INSAAT|TEKNOLOJ|PORTFÖY|KATILIM|BİST|BIST|KAP|SPK|MKK|TCMB|" \
                r"TÜRKİYE|TURKIYE|ULUSLARARASI|GRUP|LİMİTED|LTD|ŞİRKET|SIRKET|ORTAKLI|FON|ENDEKS|BORSA|PAZAR|TL|USD|EUR"
BUYUK_AD = re.compile(r"\b([A-ZÇĞİÖŞÜ]{3,}(?:\s+[A-ZÇĞİÖŞÜ]{2,}){1,2})\b")


def maskele(t):
    t = KISI_DESEN.sub("[kişi]", t)
    t = re.sub(r"\b(?:Sayın|Sn\.)\s+[A-ZÇĞİÖŞÜ][\wçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][\wçğıöşü]+){0,2}", "[kişi]", t)
    # 26.11 (bagimsiz inceleme): tamami buyuk harf ad-soyad ("AHMET YILMAZ") ve "[kişi] YILMAZ" artiklari.
    # Sirket/kurum sozcugu iceren buyuk harfli diziler (FORD OTOMOTİV SANAYİ, BORSA İSTANBUL) maskelenmez.
    t = BUYUK_AD.sub(lambda m: m.group(0) if re.search(SIRKET_SOZCUK, m.group(0)) else "[kişi]", t)
    t = re.sub(r"\[kişi\](?:\s+(?:\[kişi\]|[A-ZÇĞİÖŞÜ]{2,}\b))+", "[kişi]", t)
    # "[kişi]" onundeki baslik harfli ad parcalari ("Ayşe [kişi]") da maskelenir (fazla maskeleme kabul)
    return re.sub(r"(?:\b[A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+){1,3}\[kişi\]", "[kişi]", t)


def aciklama_bolumu(yazi):
    m = re.search(r"Açıklamalar\s*:?", yazi, re.I) or re.search(r"Özet Bilgi\s*:?", yazi, re.I)
    parca = yazi[m.end():] if m else yazi
    parca = re.split(r"Yukarıdaki açıklamalarımızın|Sorumluluk Beyanı|İlgili Şirketler|Ek Açıklamalar\s*$", parca)[0]
    return parca.strip()


def alanlar(yazi):
    """Hak kullanimi, kar payi, derecelendirme gibi yapilandirilmis alanlar (yalniz bulunanlar)."""
    a = {}
    for ad, desen in (("bedelsiz_oran_yuzde", r"bedelsiz[^%]{0,80}%\s*([\d.,]+)|%\s*([\d.,]+)[^.]{0,40}bedelsiz"),
                      ("bedelli_oran_yuzde", r"bedelli[^%]{0,80}%\s*([\d.,]+)|%\s*([\d.,]+)[^.]{0,40}bedelli"),
                      ("brut_kar_payi_tl", r"brüt[^0-9]{0,40}([\d.,]+)\s*TL"),
                      ("baz_fiyat_tl", r"(?:düzeltilmiş|teorik)\s+(?:baz\s+)?fiyat[^0-9]{0,40}([\d.,]+)"),
                      ("hak_kullanim_tarihi", r"hak kullanım(?:ı)?\s+(?:başlangıç\s+)?tarihi[^0-9]{0,20}(\d{2}[./]\d{2}[./]\d{4})"),
                      ("derecelendirme_notu", r"\b((?:AAA|AA|A|BBB|BB|B|CCC)[+-]?\s*\((?:tr|TR|Trk|tur|TUR)\))")):
        m = re.search(desen, yazi, re.I)
        if m:
            a[ad] = next(g for g in m.groups() if g)
    if re.search(r"bedelsiz", yazi, re.I):
        a["tur"] = "bedelsiz_sermaye_artirimi"
    elif re.search(r"bedelli", yazi, re.I):
        a["tur"] = "bedelli_sermaye_artirimi"
    elif re.search(r"kar payı|kâr payı|temettü", yazi, re.I):
        a["tur"] = "kar_payi"
    elif re.search(r"bölünme|birleşme", yazi, re.I):
        a["tur"] = "birlesme_bolunme"
    return a


def ozetle(b, tur, ham):
    yazi = pdf_metin(ham)
    konu = b.get("subject") or ""
    kod = kodlar_of(b)
    r = {"id": b.get("disclosureIndex"), "zaman": b.get("publishDate"), "kurum": b.get("kapTitle"),
         "kodlar": kod, "konu": konu, "kap_ozet": b.get("summary"), "tur": tur,
         "url": f"https://www.kap.org.tr/tr/Bildirim/{b.get('disclosureIndex')}", "metin_karakter": len(yazi)}
    if len(yazi) < 40:
        r["durum"] = "METIN_CIKARILAMADI"      # goruntu PDF ya da bos yanit
        return r
    r["durum"] = "OK"
    tam = f"{konu} {b.get('summary') or ''}"
    if re.search(KISI_ICEREN, tam, re.I):
        # kisi adi iceren konular: metin saklanmaz
        r["gecen_kodlar"] = sorted(set(re.findall(r"\b([A-ZÇĞİÖŞÜ]{4,6})\b", yazi)) & (evren() | set(kod)))[:40]
        r["karar_sozcukleri"] = {k: len(re.findall(d, yazi, re.I)) for k, d in KARAR_SOZCUKLERI.items()
                                 if re.search(d, yazi, re.I)}
        r["not"] = "Kisi bilgisi icerebilecegi icin metin saklanmadi; yalniz kod ve karar sozcugu sayimi."
        return r
    ac = aciklama_bolumu(yazi)
    # Coklu kodlu bildirimde (ör. 4 sirketli Hak Kullanimi) bulunan oran/tutar hangi koda ait bilinemez -> alan yok
    if len(kod) == 1:
        r["alanlar"] = alanlar(ac)
    else:
        r["alanlar_not"] = "Birden fazla kod: oran/tutar alanlari koda baglanamadigi icin cikarilmadi; ozet metne bakin."
    if re.search(METIN_GUVENLI, tam, re.I):
        m = maskele(ac)
        r["ozet"] = m[:OZET_KARAKTER] + ("…" if len(m) > OZET_KARAKTER else "")
    else:
        r["not"] = "Bu konu turunde kisi bilgisi olabilecegi icin metin saklanmadi; esas metin icin url."
    return r


def main():
    bugun = simdi_tr().date()
    try:
        eski = json.load(open(CIKTI, encoding="utf-8"))
    except Exception:
        eski = {}
    kayit = {str(k): v for k, v in (eski.get("kayitlar") or {}).items()}
    sinir = (bugun - dt.timedelta(days=SAKLA_GUN)).strftime("%Y-%m-%d")

    def gun_of(v):
        z = v.get("zaman") or ""
        m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", z)
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else "9999"

    kayit = {k: v for k, v in kayit.items() if gun_of(v) >= sinir or (gun_of(v) == "9999" and (v.get("ilk_gorulme") or "9") >= sinir)}

    secilen = sec(arsiv_bildirimleri(bugun), evren())
    robots = None
    indirilen = hata = ardisik = 0
    for _, b, tur in secilen:
        idx = str(b.get("disclosureIndex"))
        onceki = kayit.get(idx) or {}
        if onceki.get("durum") in ("OK", "COK_BUYUK") or onceki.get("deneme", 0) >= AZAMI_DENEME:
            continue
        if indirilen + hata >= AZAMI_PDF or ardisik >= ARDISIK_HATA_SINIR:
            break
        url = PDF_URL.format(idx)
        if robots is None:
            robots = kt.izinli(url)
            if not robots:
                print("KAP robots.txt BildirimPdf adresine izin vermiyor; PDF indirilmeyecek.", file=sys.stderr)
        if not robots:
            break
        temel = {"id": b.get("disclosureIndex"), "zaman": b.get("publishDate"), "kurum": b.get("kapTitle"),
                 "kodlar": kodlar_of(b), "konu": b.get("subject"), "kap_ozet": b.get("summary"), "tur": tur,
                 "url": f"https://www.kap.org.tr/tr/Bildirim/{idx}", "deneme": onceki.get("deneme", 0) + 1,
                 "ilk_gorulme": onceki.get("ilk_gorulme") or simdi_tr().strftime("%Y-%m-%d %H:%M")}
        time.sleep(1)
        try:
            azami = 6 * 1024 * 1024
            ham = kt.getir(url, zaman=40, azami=azami)
            if len(ham) >= azami:
                kayit[idx] = {**temel, "durum": "COK_BUYUK"}
                indirilen += 1
                ardisik = 0
                continue
            if not ham[:5] == b"%PDF-":
                kayit[idx] = {**temel, "durum": "PDF_DEGIL", "ilk_baytlar": ham[:60].decode("latin-1")}
                hata += 1
                ardisik += 1
                continue
            r = ozetle(b, tur, ham)
            kayit[idx] = {**temel, **r}
            indirilen += 1
            ardisik = 0
        except Exception as e:
            kayit[idx] = {**temel, "durum": "ERISILEMEDI", "hata": str(e)[:160]}
            hata += 1
            ardisik += 1

    durum = ("ROBOTS_IZIN_YOK" if robots is False else "SECILEN_YOK" if not secilen
             else "OK" if indirilen or not hata else "HATA")
    out = {"uretim_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "uretim_tr": simdi_tr().strftime("%Y-%m-%d %H:%M"), "durum": durum,
           "secilen": len(secilen), "yeni_indirilen": indirilen, "hata": hata,
           "not": "KAP bildirim PDF'lerinden kisa ozet; kisi adlari maskelenir, kisi iceren konularda metin saklanmaz. "
                  "Salt veri, tavsiye degildir. Esas metin icin url.",
           "kayitlar": dict(sorted(kayit.items(), key=lambda kv: -int(kv[0]) if kv[0].isdigit() else 0))}
    os.makedirs("data", exist_ok=True)
    json.dump(out, open(CIKTI + ".tmp", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(CIKTI + ".tmp", CIKTI)

    L = ["# KAP bildirim PDF özetleri", "", f"Üretim: {out['uretim_tr']} TR · durum {durum} · seçilen {len(secilen)} · "
         f"yeni {indirilen} · hata {hata}", "", "Salt veri, tavsiye değildir. Kişi adları maskelenir.", "",
         "| Zaman | Kod | Konu | Özet / alanlar | Durum |", "|---|---|---|---|---|"]
    for v in list(out["kayitlar"].values())[:60]:
        oz = v.get("alanlar") or {}
        metin = (", ".join(f"{k}={x}" for k, x in oz.items()) + " · " if oz else "") + (v.get("ozet") or v.get("not") or "")
        L.append(f"| {v.get('zaman')} | {','.join(v.get('kodlar') or [])} | [{(v.get('konu') or '')[:50]}]({v.get('url')}) | "
                 f"{metin[:220].replace('|', '/')} | {v.get('durum')} |")
    open(CIKTI_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(json.dumps({k: out[k] for k in ("durum", "secilen", "yeni_indirilen", "hata")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
