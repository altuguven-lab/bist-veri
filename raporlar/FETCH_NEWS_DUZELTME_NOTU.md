KISMEN GECERLI (bkz. sonraki bulgu — beklenen faydayı sağlamadı, KAP ile çözüldü)
# fetch_news.py — when:7d DÜZELTMESİ
20.08.2026 | Etiket: ALTYAPI (sinyal mantığı değişmiyor) | Kuluçkayı etkilemiyor

---

## Değişiklik

`google_news_rss()` artık sorguda `when:` yoksa kendisi ekliyor:

```python
def google_news_rss(sorgu):
    if "when:" not in sorgu:
        sorgu = f"{sorgu} when:{MAX_YAYIN_YASI_GUN}d"
    return (...)
```

`MAX_YAYIN_YASI_GUN` sabiti fonksiyonun hemen üstüne taşındı — önceden
dosyanın sonunda ikinci kez tanımlıydı, şimdi tek yerde.

**Etkilenen:** KAP, TCMB, Foreks, Makro-Asya, Makro-Jeopolitik ve otuz
sembolün tamamı için üretilen `GN:` sorguları — hiçbirinde `when:` yoktu.

**Etkilenmeyen:** Reuters (`when:7d`), Dunya (`when:7d`), Makro-Fed
(`when:3d`), Makro-TUIK (`when:5d`) — zaten vardı, kendi seçtikleri
pencereye dokunulmadı. BloombergHT ve AA Ekonomi doğrudan RSS, Google
News sorgusu değiller — `when:` onlara uygulanmaz.

Doğrulandı: her sorguda tam bir `when:` (çiftlenme yok), 41 kaynağın
tamamı hatasız inşa ediliyor.

---

## Gerekçe

17-18.08 ölçümü (`haber_teshis.py`): sorguda `when:` olan kaynaklar
%92-100 geçiyor, olmayanlar yaş filtresine kırılıyor — KAP 0/25,
30 sembolün 11-14'ü GN sorgusunda sıfır.

Google News `site:` ve genel sorguları **alaka sırasıyla** döndürüyor,
tarih sırasıyla değil. İlk 25 kayıt yıllar öncesinden gelebiliyor ve
`MAX_YAYIN_YASI_GUN=7` filtresine tamamı takılıyor. `when:Nd` bunu
kaynakta çözüyor — Google'dan zaten son N günün sonuçlarını istiyor.

---

## Dokunulmayan: gürültü kalıbı

Elenenlerin %95'i `"günlük teknik analiz"` kalıbından geliyordu (457/483).
Bunu **daraltmadım** — örnek başlıkları görmeden. Bu konteynerin ağ
erişimi Google News'e kapalı; `haber_teshis.py GN:AKBNK` ayrıntılı
modunu koşturmak workflow tetiklemesi gerektiriyor, bende o yetki yok.

Önerim: bu düzeltme commit'lendikten sonra `Haber Kanalı Teşhisi`
workflow'unu `kaynak: GN:AKBNK` ile bir kez tetikle. Sonuç
`data/denetim/haber_teshis.json`'a örnek başlıklarla düşecek, ben
oradan kalıbı hangi kelimelerin taşıdığını görüp ancak o zaman
daraltma öneririm.

---

## Doğrulama

Commit sonrası `haber_update.yml`'in bir sonraki koşusunda:
1. `kaynak_detay.KAP.suzulen` — 0'dan yukarı çıkmalı
2. GN sembol sorgularının sıfır verenlerinin sayısı — 11-14'ten
   düşmeli
3. Portföy sembollerine (AKBNK/KCHOL/TAVHL/YKBNK) doğrudan haber
   sayısı — şu an 0-1 civarında, artması beklenir
