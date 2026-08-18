# İP-7 ÖN KAYIT BELGESİ
## "19 Mart 2025 sonrası BIST davranışı farklı" hipotezi

**Tarih:** 17.08.2026 | **Statü:** Aşama 2 koşulmadan ÖNCE kilitlenmiştir
**Onay:** B1–B6 (17.08.2026)
**Etiket:** ÖLÇÜM — Pine'a dokunmaz, kuluçka sayacını yakmaz

> Bu belge, veri görülmeden yazılmıştır. Aşama 2 sonuçları geldikten
> sonra bu dosyada yapılacak **hiçbir değişiklik geçerli değildir**;
> revizyon gerekirse yeni bir ön kayıt açılır ve ikisi birlikte
> raporlanır.

---

## 0. ÖNCEDEN BİLDİKLERİMİN BEYANI

Körleme, bilmediğimi iddia etmek değil, bildiğimi kayda geçirmektir.
Bu ön kaydı yazarken şunları **zaten biliyorum**:

1. 5 yıllık (2021-2026) toplu ölçümde XU100 gece payı %85,1; gece
   ortalaması %+0,2407/gün, gündüz %−0,0420/gün.
2. Aynı ölçümde gap kovaları ters U şekli veriyor; uç kovalar negatif.
3. Dünün kazananları ertesi gün endekse göre 0,383 puan önde.

**Bilmediklerim** — ve bu testin konusu olan şeyler:

- Bu büyüklüklerin **zaman içindeki seyri**. Yukarıdakilerin hepsi
  dönem toplamı; hiçbirinin günlük serisine bakmadım.
- 19 Mart 2025 civarında herhangi bir kırılma olup olmadığı.
- EM emsallerinde ne olduğu.

Yani ön kayıt, seviyeler hakkında bilgiliyken **kırılmalar hakkında
kör** yazılmıştır. Aşama 1 çıktısı bu körlüğü korumak üzere
tasarlanmıştır (§4).

---

## 1. ESTIMAND'LAR — üç ayrı iddia, asla birleştirilmez

| | İddia | Test edilen |
|---|---|---|
| **E1 — ÖLÇEK** | Volatilite seviyesi yükseldi | GJR-GARCH koşullu sigma serisinde kırılma |
| **E2 — YAPI** | Davranış kalıbı değişti | Koşullu volatiliteye standardize edilmiş getirilerde kırılma |
| **E3 — KOMPOZİSYON** | Değişim yabancı payı en çok düşen hisselerde en güçlü | **BLOKE** — hisse bazlı takas verisi yok (B2) |

E3, takas fizibilite kapısı açılana kadar planlanmaz. Bu belge E1 ve
E2 içindir.

---

## 2. SERİLER — dört tanesi, önceden sabit

| Kod | Seri | Neden |
|---|---|---|
| **S1** | XU100 gece getirisi (kapanış→açılış), günlük | Sistemin fiilen dayandığı büyüklük |
| **S2** | XU100 gündüz getirisi (açılış→kapanış), günlük | S1'in tamamlayıcısı; ayrı test edilir |
| **S3** | XU100 koşullu volatilite (GJR-GARCH(1,1), Student-t) | E1'in doğrudan ölçüsü |
| **S4** | Günlük kesitsel korelasyon: corr(gece_i, gündüz_i), 30 sembol | Gap ters dönüş yoğunluğunun günlük skaleri |

Sonradan seri eklenmez. S4'ün seçilme gerekçesi: H2'nin mekanizmasını
tek bir günlük sayıya indirger, dolayısıyla kırılma testine uygundur.

---

## 3. ZAMAN YAPISI — sabit tarihler, kayan pencere yok

Önceki koşularda `period="5y"` kullanmak iki koşuda 1257 ve 1249 gün
verdi. Tekrarlanabilirlik için burada **sabit tarih** kullanılır.

| Pencere | Tarih | Kullanım |
|---|---|---|
| Uzun bağlam | 01.01.2018 – 16.08.2026 | Tüm tahmin |
| **Sansür** | **19.03.2025 – 04.04.2025** | Tahminden ÇIKARILIR (devre kesici + Yahoo kapanış tanımı riski) |
| Sonrası-1 | 07.04.2025 – 29.08.2025 | Kukla değişken (ayrı test EDİLMEZ — güç yetersiz) |
| Sonrası-2 | 01.09.2025 – bugün | Kukla değişken (EBDKS rejimi) |
| Saklı pencere | 17.02.2026 – bugün | Hiçbir parametre seçiminde kullanılmaz; yalnız teyit |

**Sonrası-1'in ayrı test edilmemesi bilinçlidir.** ~100 işlem günüyle
%80 güçte ancak 0,29–0,36 sigmalık bir kayma görülebilir; daha küçük
gerçek bir etki sistematik olarak "belirsiz"e düşerdi. Bunun yerine
1 Eylül rejim farkı tek modelde kukla değişkenle taşınır.

---

## 4. İKİ AŞAMALI KOŞU — körlemenin mekanizması

**Aşama 1 (`--asama 1`)** yalnız şunları basar: veri künyesi, gözlem
sayıları, seri betimleyici istatistikleri, ve **MDE tablosu**.
Kırılma sonucu, kırılma tarihi, GARCH karşılaştırması, plasebo
sonucu — hiçbiri basılmaz ve dosyaya yazılmaz.

**Bu belge Aşama 1'den sonra, Aşama 2'den önce commit'lenir.**

**Aşama 2 (`--asama 2`)** tam sonucu üretir.

Amaç: sonucu görüp eşik ayarlamayı mekanik olarak imkânsız kılmak.
Bugün sabah tam bu hatayı yaptım — "08.08 sonrası performans kötüleşti"
dedim, gün-ağırlıklama düzeltmesi iddiayı tersine çevirdi. Körleme o
sırayı tersine çeviren tek şey.

---

## 5. KARAR KURALLARI — şimdi kilitlenir

Kırılma tespiti: `ruptures` PELT, `model="l2"`, ceza **BIC kuralıyla**
belirlenir (`pen = 2·σ̂²·log n`) — gözle seçilmez.
Kırılma tarihi %95 güven aralığı: hareketli blok bootstrap, blok
uzunluğu 21 gün, 1.000 tekrar.

| Koşul | Eşik |
|---|---|
| **K1 — Tarih** | Birincil kırılmanın %95 GA'sı (a) 19.03.2025'i içeriyor, **(b)** genişliği ≤166 gün, **(c)** 01.09.2025'i (EBDKS) içermiyor |
| **K2 — Büyüklük** | Kayma, öncesi dönemin 250 günlük kayan dağılımının 99. yüzdeliğini aşıyor |
| **K3 — Yapı ≠ ölçek** | Etki, standardize getirilerde (S1/S3, S2/S3) de korunuyor |
| **K4 — Dayanıklılık** | Faktör-arındırılmış artıklarda korunuyor **ve** EM emsallerinin hiçbirinde aynı pencerede kırılma yok |
| **K5 — Mekanizma** | **BLOKE** — takas kapısına bağlı |

Faktörler: USD/TRY, VIX, EEM (MSCI EM vekili). CDS kapsam dışı (veri).
EM emsalleri: erişilebilen endeksler kullanılır; **hangilerinin veri
verdiği rapora yazılır**, veri vermeyen emsal sessizce düşürülmez.

**K1'in (b) ve (c) şartları, sentetik pozitif kontrolden öğrenilerek —
gerçek veri görülmeden, körleme bozulmadan — eklenmiştir.** İlk yazımda
K1 yalnız "GA 19 Mart'ı içeriyor mu" diye soruyordu; kontrol serisinde
koşullu volatilite 5,5 yıl genişliğinde bir GA üretti ve 19 Mart'ı
"içerdiği" için K1'i geçti. Yani kural belirsizliği ödüllendiriyordu.
166 gün eşiği keyfi değil: 19.03.2025 ile 01.09.2025 arasındaki mesafe.
Bundan geniş bir GA, siyasi şoku kural değişikliğinden ayıramaz ve
sonuç **BELİRSİZ** olarak etiketlenir — "desteklendi" değil.

Çoklu test: 4 seri × 2 test → Holm-FWER %5 birincil, BH-FDR %10 ikincil.

### Sonuç etiketleri — üçü de meşru

- **DESTEKLENDİ:** K1+K2+K3+K4 hepsi geçti
- **KISMEN:** K1+K2 geçti, K3 düştü → "ölçek değişti" olarak yeniden
  etiketlenir, "davranış değişti" DENMEZ
- **BELİRSİZ:** güç <%80 veya GA geniş → **H0 lehine sayılmaz**,
  öyle raporlanmaz

Kırılma başka bir tarihte bulunursa: genel rejim değişikliği
desteklenebilir ama **19 Mart nedenselliği desteklenmez.**

---

## 6. ÖNCEDEN KABUL EDİLEN SINIRLAR

Bunlar sonuçtan sonra keşfedilmiş mazeret olmasın diye şimdi yazılıyor:

1. **20 Mart 2025 ara PPK** (gecelik %46, repo ihalelerine ara) olaydan
   1 gün sonra. Parasal şok ile siyasi şok ekonometrik olarak
   ayrıştırılamayabilir. Test "19 Mart'ta bir şey oldu" diyebilir,
   "İmamoğlu olayı nedeniyle" diyemez. Bu bir kimlik problemidir ve
   hiçbir istatistikle çözülmez.
2. **MS-GARCH yok.** Python'da mevcut değil. Claude Opus 5'in
   rejim-yapışkanlığı bulgusu (Kasım 2021 sonrası 5,5→37 gün)
   **doğrulanmamış literatür alıntısıdır**, bizim bulgumuz gibi
   kullanılmaz (B5).
3. **Kompozisyon iddiası test edilmiyor.** Bu testin "değişmedi"
   demesi, yabancı payı mekanizmasının olmadığı anlamına gelmez.
4. **Beklenen çıktı** (B6): E1'de net cevap, E2'de büyük olasılıkla
   belirsizlik. Belirsizlik çıkarsa bu bir başarısızlık değil, güç
   sınırının dürüst raporudur.
5. Yahoo verisi ikincil kaynaktır; sansür penceresi bu riski azaltır
   ama sıfırlamaz.

---

## 7. V162'YE BAĞLANTI

Hiçbir bulgu otomatik kod değişikliği doğurmaz. Doğrulanan her alt
hipotez, ilgili parametreyi yalnızca **"DAVRANIŞ DEĞİŞİKLİĞİ ÖNERİSİ —
TEST EDİLMEMİŞ"** etiketiyle listeler. Uygulama sırası: K koşulları →
ekonomik anlamlılık (maliyet sonrası) → tek parametre, yönü teoriyle
uyumlu → walk-forward + DSR/PBO → saklı pencerede sınama → paralel
canlı izleme → ancak sonra kod. Herhangi bir adımda başarısızlık:
değişiklik yapılmaz, bulgu belgelenir.

Ve kuluçka: 19.09.2026'ya kadar hiçbir Pine değişikliği yapılmaz,
bulgu ne olursa olsun.

---

## 8. LABORATUVAR KURALLARI (B4) — tüzük ekine

Bu iki kural İP-7'ye özel değildir; **tüm İP çalışmalarına** uygulanır:

> **C.6 — Veri körleme.** Ölçüm kodu ve karar eşikleri, sonuç
> görülmeden yazılır ve commit'lenir. Ön kayıt commit'i olmayan
> hiçbir İP bulgusu "kanıt" sayılmaz.
>
> **C.7 — Specification curve.** Duyarlılık analizleri seçilerek
> değil, tümü tek sıralı eğride raporlanır. Tek bir spesifikasyonun
> geçmesi bulgu değildir.
