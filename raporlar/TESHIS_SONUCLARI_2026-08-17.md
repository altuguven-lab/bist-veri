GECERLI (tarihsel anlık görüntü — 17.08 durumu)
# TEŞHİS SONUÇLARI + İKİ İŞ ŞARTNAMESİ
17.08.2026 | Teşhis koşusu: 07:13 UTC, 41 kaynak

---

## 1. KAP ÇÖZÜLDÜ — VE BENİM "KANITLANAN HATA"M ANA SEBEP DEĞİLMİŞ

**KAP: 25/25 kayıt `YAYIN_YASI` ile elenmiş.** Başka hiçbir neden yok.
Yani sabahki iki adaydan birincisi doğru çıktı: Google News `site:`
sorgularını alaka sırasıyla döndürüyor, incelenen ilk 25 kaydın tamamı
7 günden eski. BloombergHT de aynı: 20/20 yayın yaşı.

Ama GN sembol sorgularında tablo beklediğimden farklı:

| Eleme nedeni | Adet | Elenenlerin payı |
|---|---|---|
| **GURULTU_KALIBI** | **474** | **%67** |
| YAYIN_YASI | 211 | %30 |
| DUSUK_PUAN | 18 | **%3** |

Sabah "şirket adı puanlayıcıya eklenmemiş" hatasını ana sebep gibi
sundum. **Değilmiş.** Kod tutarsızlığı gerçek — `SIRKET_ADLARI` yalnız
sorgu kurmada kullanılıyor — ama elenenlerin sadece %3'ünü açıklıyor.
Asıl katil gürültü kalıpları: elenenlerin üçte ikisi.

Bunu düzeltmeden yamayı uygulasaydık, %3'lük bir sorunu çözüp %67'lik
sorunu görmemiş olacaktık. Ölçmenin sebebi tam olarak buydu.

Sıfır geçiren sembol sayısı 11/30: AKBNK, YKBNK, ISCTR, KCHOL, ASELS,
FROTO, AEFES, OTKAR, PETKM, TRMET, ENJSA.

---

## 2. `when:` KANITI — DÜZELTME KENDİ KODUMUZDA DURUYOR

Yayın yaşı elemesi ile sorgudaki `when:` operatörü arasında birebir
ilişki var:

| Kaynak | Sorguda `when:` | Bakılan | Geçen | Yaş elemesi |
|---|---|---|---|---|
| Makro-Fed | `when:3d` | 25 | **25** | 0 |
| Makro-TUIK | `when:5d` | 25 | **23** | 0 |
| Reuters | `when:7d` | 13 | **13** | 0 |
| Makro-Asya | yok | 25 | 2 | **23** |
| KAP | yok | 25 | **0** | **25** |
| BloombergHT | (doğrudan RSS) | 20 | **0** | **20** |

`when:` taşıyan üç sorgu %92-100 geçiyor, taşımayanlar yaş filtresine
kırılıyor. Çözüm icat etmeye gerek yok — Reuters satırında zaten var,
sadece diğer sorgulara taşınmamış.

**Öneri A:** `google_news_rss()` içine varsayılan `when:7d` eklensin
(zaten `MAX_YAYIN_YASI_GUN = 7` ile aynı sayı — iki yerde ayrı ayrı
tutulmasın, tek sabitten türesin).

BloombergHT ayrı vaka: doğrudan RSS veriyor ama 20/20 eski. Yayın akışı
gerçekten durmuş olabilir; ayrıca bakılmalı.

---

## 3. GÜRÜLTÜ KALIPLARI — ÖNCE HANGİSİ ELİYOR, SONRA YAMA

Özet koşumu kalıp adını tutmuyordu; `haber_teshis.py`'yi yamaladım,
artık `gurultu_kalip_dagilimi` alanı da yazıyor. Ofline doğrulandı:

```
GURULTU_KALIBI[hisse yorumlari]  :: AKBNK Hisse Yorumlari 2026
GURULTU_KALIBI[hisse senedi -]   :: Akbank hisse senedi - analiz
GURULTU_KALIBI[ne zaman]         :: Garanti temettu ne zaman odenecek
DUSUK_PUAN[1<2]                  :: Akbank ikinci ceyrek bilanco
```

Şüphem: `"ne zaman"` ve `"hisse senedi -"` fazla geniş. "Temettü ne
zaman ödenecek" gerçek bir yatırımcı sorusu; "hisse senedi -" ise
Google News'in `Başlık - Yayıncı` biçimiyle çakışıyor olabilir —
öyleyse başlığında "hisse senedi" geçen **her** haberi eliyor.

**Yamalanmış `haber_teshis.py` yeniden koşulsun** (bu sefer kalıp
dağılımı gelecek). Rakamı görmeden `GURULTU_KALIPLARI` listesine
dokunmuyorum — sabahki dersi bir kez aldık.

---

## 4. `inbox_birlestir.py` KOŞUM SIRASI — HAZIR

İki workflow `tv_alerts_latest.json` okuyor ve **ikisi de aynı dakikada**
(15:45 UTC) koşuyor: `sinyal_arsiv_gunluk.yml` (hafta içi) ve
`hafta_denetim.yml` (Cuma). Birleştirme ikisinden de önce çalışmalı.

Her iki dosyada da, mevcut `- run: pip install ...` satırından **sonra**,
ana betikten **önce** şu adım eklenir:

```yaml
      # 17.08: Pipedream ana dosyaya yazamadigi kayitlari data/inbox/
      # altina dusuruyor; hicbir sey onlari geri tasimiyordu (12-14.08
      # kapsama 22-24/30). Birlestirme ana betikten ONCE kosmali -
      # ikisi de tv_alerts_latest.json okuyor.
      - name: Inbox kayitlarini birlestir
        run: python inbox_birlestir.py
```

Ve commit adımındaki `git add` satırına dosya eklenir:

- `sinyal_arsiv_gunluk.yml`:
  `git add data/sinyal_arsiv.json` → `git add data/sinyal_arsiv.json data/tv_alerts_latest.json`
- `hafta_denetim.yml`:
  `git add data/denetim/` → `git add data/denetim/ data/tv_alerts_latest.json`

Bu ikinci kısım atlanırsa birleştirme her koşuda çalışır ama sonucu
commit edilmez — kurtarılan kayıtlar bir sonraki checkout'ta kaybolur.

`inbox_birlestir.py` idempotent, o yüzden iki workflow'un aynı gün
koşması sorun değil: ikincisi 0 kayıt ekler.

---

## 5. P3_SKOR_AL MESAJ ŞABLONU — SENDEN BİR ŞEY LAZIM

Bunu tek başıma yazamam, çünkü placeholder'lar Pine'daki `title=`
değerlerine birebir bağlı ve V157 kaynağı depoda yok (Pine dosyaları
depoya girmiyor). Yanlış bir başlık yazarsam alan sessizce boş gelir —
şu anki durumun aynısı, üstelik düzeltildi sanırız.

**Ama Pine'a hiç dokunmadan çözülebilir.** TradingView'de alarm mesajı
alarm penceresinden de düzenlenebilir. Prosedür:

1. Çalışan bir **GUNLUK_OZET** alarmını aç, Mesaj kutusundaki metni
   **olduğu gibi kopyala** (placeholder'lar zaten doğru, çünkü o alarm
   sayısal değer basıyor).
2. Bir **P3_SKOR_AL** alarmını aç, mesaj kutusuna bu metni yapıştır.
3. Yalnız tek bir alanı değiştir: `"sinyal":"GUNLUK_OZET"` →
   `"sinyal":"P3_SKOR_AL"`.
4. Kaydet. Bu kayıt aynı zamanda **Düzenle→Kaydet turudur** — yani eşiğin
   canlıya alınması işini de aynı hamlede halleder.
5. Kalan P3_SKOR_AL alarmları için tekrarla.

Bunu yaparsan iki soru birden kapanır:
- Alan dolmaya başlar → eşik testi mümkün olur (v2.1 arşivi `skor`
  alanını zaten yakalıyor).
- Sinyal frekansı 11/gün'den düşerse eşik gerçekten canlıda değildi;
  düşmezse eşiğin kendisi yetersiz. Her iki sonuç da bilgi.

**Alternatif:** V157 kaynağını yüklersen alertcondition satırını doğrudan
yamalarım ve tam metni veririm. Ama yukarıdaki yol daha hızlı ve Pine'a
hiç dokunmuyor.

---

## 6. SIRA

1. Yamalanmış `haber_teshis.py` commit + tekrar koş → kalıp dağılımı
2. `when:7d` düzeltmesi (§2) — kalıp verisiyle birlikte tek yamada
3. İki workflow'a inbox adımı + `git add` (§4) — hazır, uygula
4. P3_SKOR_AL mesajı (§5) — sende
5. TAVHL stop yenilemesi + İHLAL-2 tutanağı — hâlâ bekliyor
