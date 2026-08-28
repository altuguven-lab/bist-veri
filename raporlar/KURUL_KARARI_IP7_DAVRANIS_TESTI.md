GECERLI
# KURUL KARARI — "19 MART 2025 SONRASI BIST DAVRANIŞI" TEST PROTOKOLÜ
17.08.2026 | Girdi: kurul sentezi + iki üye protokolü (GPT-5.6 Sol, Claude Opus 5)
Etiket: ÖLÇÜM | Pine'a dokunmaz, kuluçka sayacını yakmaz

---

## 0. HÜKÜM

Protokol **standart olarak kabul**, **yazıldığı haliyle uygulanabilir değil**.

Belge, bu masaya gelmiş en disiplinli test tasarımı. Üçlü ayrım
(ölçek/yapı/kompozisyon), 1 Eylül 2025 EBDKS kural değişikliğinin ayrı
kırılma olarak zorunlu tutulması, "yabancı payı"nın karantinaya alınması
ve "yetersiz güç → belirsiz, H0 lehine değil" kuralı — dördü de doğru ve
bizim ölçüm kültürümüze doğrudan eklenmeli.

Ama protokol bir araştırma ekibi ve lisanslı veri varsayıyor. Bizde ikisi
de yok. Kurul, kapsamı fizibiliteye göre daraltıyor ve **İP-7** olarak
tanımlıyor.

---

## 1. FİZİBİLİTE HARİTASI — ne yapabiliriz, ne yapamayız

Araç envanteri fiilen kontrol edildi (kurulu ve çalışır):

| Protokol adımı | Durum | Not |
|---|---|---|
| Adım 3 — Kırılma tespiti | **YAPILABİLİR** | `ruptures` 1.1.10 (PELT/BinSeg) kurulu |
| Adım 3 — Kırılma tarihi %95 GA'sı | **KISMEN** | `ruptures` GA vermiyor; bootstrap ile kendimiz üretmeliyiz. K1 bu GA'ya bağlı — atlanamaz |
| Adım 4 — GJR-GARCH / E-GARCH | **YAPILABİLİR** | `arch` 8.0.0 kurulu, LR bootstrap dahil |
| Adım 4 — MS-GARCH (2 rejim) | **YAPILAMAZ** | Python'da yok. `statsmodels` yalnız MS-AR/MS-regresyon veriyor. Claude'un rejim-yapışkanlığı bulgusu (5,5→37 gün) **tekrarlanamaz**, ancak alıntılanabilir |
| Adım 5 — Yapı metrikleri | **YAPILABİLİR** | Varyans oranı, Ljung-Box Q², gap doldurma — hepsi elde |
| **Adım 6 — Kesit doz-tepki DiD** | **BLOKE** | Hisse bazında 18.03.2025'te dondurulmuş yabancı payı gerekiyor. Bu takas verisi ve BIST onu 01.01.2025'ten beri ücretli lisansa bağladı |
| Adım 7 — EM emsal plasebo | **YAPILABİLİR** | Endeksler yfinance'ten çekilebilir |
| Adım 7 — Faktör arındırma | **YAPILABİLİR** | USD/TRY, VIX, MSCI EM erişilebilir; CDS zor |
| Adım 8 — Holm/FDR, MDE | **YAPILABİLİR** | `scipy` yeterli |

### En büyük tek blokaj ve şaşırtıcı sonucu

Claude Opus 5'in **ana test** ilan ettiği kesit doz-tepki DiD, hisse
bazında yabancı payı verisi olmadan kurulamaz. Ve bu, İP-6'nın (aracı
kurum akış katmanı) Faz 0 fizibilite sorusunun **aynısı**.

Yani iki ayrı projenin en kritik adımı tek bir soruya bağlı:
**TradeMaster ve TradingView aboneliklerimizde hisse bazında takas /
yabancı payı verisi var mı?**

Kurul kararı: bu soru artık iki projenin ortak kapısı. Cevap gelmeden
ne İP-6 Faz 1 başlar ne İP-7 Adım 6 planlanır. Tek soru, iki proje.

---

## 2. PROTOKOLÜN KENDİ İÇİNDE BİR GERİLİM VAR — güç hesabı

Ne sentez ne iki üye protokolü, pencere bölme kararının güç maliyetini
sayıyla göstermiyor. Kurul hesapladı (%80 güç, sigma birimi):

| Pencere | α=0,05 | α=0,01 |
|---|---|---|
| Sonrası tamamı (~340 gün) | 0,176 | 0,215 |
| **Sonrası-1 tek başına (~100 gün)** | **0,294** | **0,358** |
| Sonrası-2 tek başına (~240 gün) | 0,201 | 0,246 |

K4 koşulu, etkinin **Sonrası-1'de zaten mevcut** olmasını şart koşuyor —
yani 1 Eylül kural değişikliğinden önce. Ama Sonrası-1 sadece ~100 işlem
günü. K2 mertebesindeki büyük bir etki (99. yüzdelik ≈ 2,3 sigma) orada
görülür; **0,2–0,3 sigmalık gerçek ama ölçülü bir etki görülemez.**

Sonuç: protokol, gerçek-ama-orta büyüklükte bir davranış değişikliğini
K4'te sistematik olarak "belirsiz"e düşürecek biçimde kurulmuş. Bu bir
hata değil — muhafazakârlık — ama **beklenen çıktının ne olduğunu
baştan bilmek gerekir**: ölçek sorusunda net cevap, yapı ve mekanizma
sorusunda büyük olasılıkla "belirsiz". Buna hazır olmayan bir ekip,
belirsizliği sessizce H0'a çevirir. Protokolün kendi kuralı bunu
yasaklıyor; kurul altını çiziyor.

---

## 3. PROTOKOL BİZİ VURDU — Yahoo uyarısı kendi ölçümümüze işliyor

Claude Opus 5'in benzersiz uyarısı: devre kesici günlerinde Yahoo tipi
ikincil kaynakların kapanış fiyatı tanımı resmi bültenden farklı olabilir.

Bu bugün yaptığımız gece/gündüz ölçümünü doğrudan ilgilendiriyor: 5
yıllık pencere 19-25 Mart 2025'i içeriyor ve o günlerde devre kesici
tetiklendi. Ölçümümüz `yfinance` ile yapıldı.

Etki muhtemelen küçük (1249 günde birkaç gün), ama **kontrol edilmeden
küçük olduğu varsayılamaz** — üstelik gap ölçümümüzün (H2) en uç kovası
tam olarak bu tür günlerden besleniyor. `>+0,75 ATR` kovasında 621 gözlem
var ve devre kesici günleri buraya orantısız katkı yapar.

**Aksiyon:** 19.03–04.04.2025 penceresi sansürlenerek gece/gündüz ölçümü
tekrarlansın. Sonuç değişmiyorsa bulgular güçlenir; değişiyorsa H2'nin
uç kovası yeniden okunmalı. Tek satırlık bir tarih filtresi.

---

## 4. İP-7 KAPSAMI — kurulun onayladığı hâli

**Test istatistiği seçimi (kurulun asıl katkısı).** Protokol "BIST
davranışı değişti mi" diye soruyor. Bu soru bizim için fazla geniş.
Bizim sormamız gereken daha dar ve daha yararlı soru şu:

> Sistemimizin fiilen dayandığı büyüklükler 19 Mart'tan sonra değişti mi?

Bugün ölçtüğümüz **gece payı** tam olarak böyle bir büyüklük: günlük,
skaler, endeks kontrollü, ve V162'nin neden gün içi akıştan 1-2 günlük
getiri üretemediğini açıklayan şey. Kırılma testi için ideal seri.

**Faz A — kırılma testi (bir hafta içinde yapılabilir)**
- Seri 1: XU100 günlük gece payı
- Seri 2: XU100 koşullu volatilite (GJR-GARCH)
- Seri 3: evren geneli gün içi ters dönüş katsayısı
- `ruptures` ile çoklu kırılma + bootstrap ile tarih GA'sı
- Ön kayıtlı: GA 19 Mart'ı kapsamıyorsa "19 Mart'a atıf" reddedilir

**Faz B — ölçek/yapı ayrımı**
- Aynı metrikler koşullu volatiliteye standardize edilmiş getirilerde
- Etki kayboluyorsa bulgu "volatilite arttı" olarak yeniden etiketlenir

**Faz C — plasebo**
- EM emsalleri + 20 sahte tarih
- Emsallerde de aynı kırılma varsa hipotez çürütülmüş sayılır

**Faz D — mekanizma:** BLOKE. §1'deki takas kapısına bağlı.

**Kapsam dışı bırakılanlar ve gerekçesi:** MS-GARCH (araç yok, alıntı
ile yetinilir), CDS faktörü (veri zor), hisse bazlı DiD (veri bloke),
Sonrası-1'in tek başına ayrı testi (güç yetersiz — §2; bunun yerine
Sonrası-1/Sonrası-2 farkı tek modelde kukla değişkenle taşınır).

---

## 5. İKİ LABORATUVAR KURALI — hemen yürürlüğe

GPT-5.6 Sol'un iki benzersiz katkısı, tasarım tercihi değil **disiplin
aracı** ve bugün ikisine de ihtiyacımız olduğu kanıtlandı:

**Kural 1 — Veri körleme.** Metrik kodu, gerçek tarihler maskeliyken
yazılıp kilitlenir; ancak sonra gerçek tarihlerle koşulur. Bugün sabah
"08.08 sonrası performans kötüleşti" derken tam olarak bunun tersini
yaptım: sonucu gördüm, sonra gerekçe kurdum. Gün-ağırlıklama düzeltmesi
o iddiayı tersine çevirdi. Körleme bu hatayı mekanik olarak imkânsız
kılar.

**Kural 2 — Specification curve.** Tüm duyarlılık modelleri tek bir
sıralı eğride raporlanır, seçilmiş olanlar tek tek değil. H2'de bugün
"pozitif kovalarda monotonluk" testi geçti ama tam şekil ters U çıktı —
tek bir spesifikasyona bakmanın maliyeti buydu.

Bu iki kural İP-7'ye özel değil; **tüm İP çalışmalarına** uygulanır ve
KOMITE_TUZUGU ekine yazılmalıdır.

---

## 6. ONAY BEKLEYEN KARARLAR

- **B1** Protokol standart olarak kabul; İP-7 kapsamı §4'teki hâliyle
  açılır (Faz A-B-C; Faz D takas kapısına bağlı).
- **B2** Takas/yabancı payı fizibilite sorusu, İP-6 ve İP-7'nin ortak
  kapısı ilan edilir; cevap gelmeden ikisinin de mekanizma fazı
  başlamaz.
- **B3** Gece/gündüz ölçümü, 19.03–04.04.2025 sansürüyle tekrarlanır
  (§3).
- **B4** Veri körleme ve specification curve, tüm İP çalışmaları için
  zorunlu laboratuvar kuralı olarak tüzük ekine geçer.
- **B5** MS-GARCH kapsam dışı; Claude'un rejim-yapışkanlığı bulgusu
  (Kasım 2021 sonrası 5,5→37 gün) **doğrulanmamış literatür alıntısı**
  olarak kaydedilir, kendi bulgumuz gibi kullanılmaz.
- **B6** İP-7 beklenen çıktısı baştan yazılır: ölçekte net cevap,
  yapı ve mekanizmada büyük olasılıkla belirsizlik. "Belirsiz" sonucu
  hiçbir koşulda "değişmedi" diye raporlanmaz.

Onay gelirse `kirilma_testi.py` şartnamesini ve ön kayıt belgesini
üretirim — veri görülmeden, körleme kuralına uygun sırayla.
