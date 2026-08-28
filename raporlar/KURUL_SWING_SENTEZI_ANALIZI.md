# KURUL ANALİZİ — 1-2 GÜNLÜK SWING SENTEZİ
17.08.2026 | Girdi: Kurul_Sentezi__BIST_1-2_Günlük_Swing_Kriterleri.md
Kuluçka v2 günü 9/42 (bitiş 19.09.2026)

---

## 0. GENEL HÜKÜM

Sentez **iyi bir belge** — özellikle kendi sınırını doğru çiziyor:
"bu bir araştırma şartnamesi, kanıtlanmış bir kâr formülü değil".
Bu kurul o hükmü onaylıyor ve **tek bir cümlesine tam destek veriyor:**

> Önerilen ilk adım, yeni bir kod yazmadan önce, gece ve gündüz
> getirilerini ayrıştırmak.

Geri kalan her şey — iki motor, ATR stop, zaman çıkışı, gap vetosu,
R/R hedefleri — bu ölçüm yapılmadan **parametre tartışmasıdır.** Ve
bugün öğrendiğimiz şey tam olarak şu: ölçüm aygıtı bozukken parametre
tartışmak, gürültüyü kanaate çevirir.

Bu yüzden kurul, sentezin 18 maddesini tek tek tartışmak yerine
**ölçüm betiğini üretti** (`gece_gunduz_ayristirma.py`, §4).

---

## 1. SENTEZİN GÖRMEDİĞİ ÜÇ ŞEY — bizim kendi sistemimizden

İki modelin de bilemeyeceği, yalnız bizim altyapımızdan görülen
kısıtlar var. Üçü de tasarımı doğrudan değiştiriyor.

### 1.1 Kapanışa yakın giriş bizim borumuzla MÜMKÜN DEĞİL

Sentezin en büyük ayrışması "17:40-17:55'te sinyal, 18:01-18:05
kapanış seansında giriş" ile "ertesi sabah teyit" arasında.

Bizim GUNLUK_OZET alarmlarımız **15:11 UTC = 18:11 TSİ**'de düşüyor —
kapanış seansı bittikten sonra. Yani Claude Opus 5'in önerdiği kapanış
seansı girişi mevcut alarm zamanlamasıyla **uygulanamaz**; sinyal
elimize geldiğinde pencere kapanmış oluyor.

Bu, tartışmayı çözmez ama şartını netleştirir: kapanış girişi isteniyorsa
önce **ayrı bir erken alarm penceresi** kurulmalı (17:40 civarı) — ve
bu, kuluçka boyunca yasak olan bir alarm seti değişikliğidir (C.4).
Dolayısıyla 19.09'a kadar tek uygulanabilir seçenek **ertesi sabah
teyitli giriş**tir. GPT-5.6 Sol'un önerisi, mimari tercih olduğu için
değil, borunun şekli yüzünden kazanıyor.

### 1.2 Yeni bir script, kuluçkanın ölçtüğü şeyi kirletir

Sentez yeni bir Pine dosyasından bahsediyor ve haklı olarak "bu V162'yi
değiştirmiyor" diyor. Ama bizim protokolümüzde iki dolaylı temas var:

- **Alarm bütçesi:** Ağustos'ta Pipedream'e 325 olay geldi ve kapsama
  zaten eksikti (bugün 18 kayıt inbox'tan kurtarıldı). Yeni bir sinyal
  sınıfı bu kanala biner.
- **M3 kirlenmesi:** Hüküm metriği M3 "sinyal-uyum >%80" diyor ve
  `islem_gunlugu.json`'dan hesaplanıyor. Swing sinyaliyle açılan bir
  pozisyon, V151/V195 sinyali olmadığı için denetimde **SINYALE_RAGMEN**
  olarak görünür. Yani swing'de yapılan her işlem, kuluçkanın ölçtüğü
  sistemin karnesini düşürür.

**Hüküm:** swing çalışması 19.09'a kadar **kâğıt üzerinde** kalır.
Ölçüm serbest, alarm ve işlem yasak. Bu bir gecikme değil — İP-4'te
öğrenilen dersin uygulanmasıdır.

### 1.3 VBTS bizim veri hattımızda hiç yok

Sentezin en değerli benzersiz bulgusu VBTS: tedbire giren bir hissede
brüt takas ve tek fiyat kademesi, "2. gün kapanışında zorunlu çıkış"
kuralını fiilen uygulanamaz kılabilir.

Bizim `bist_quotes.json` veya `gunluk_gozlem_cetveli.json`'da **tedbir
durumu diye bir alan yok.** Yani sistem, çıkamayacağı bir pozisyona
girebilir ve bunu göremez.

Acı ironi: tedbir kararları KAP üzerinden duyurulur — ve KAP kanalımızın
bugün 25/25 kayıt elediğini tespit ettik. Yani VBTS körlüğümüz aslında
KAP arızasının bir alt kümesi. **KAP `when:7d` düzeltmesi, swing
projesinden önce gelmeli.**

---

## 2. SENTEZİN AYRIŞMALARI — ölçülebilir olanlar

Sentez üç ayrışmayı "tasarım tercihi" olarak bırakıyor. İkisi tercih
değil, **ölçüm sorusu**:

| Ayrışma | Kurul hükmü |
|---|---|
| Gap eşiği: 0,3-0,5 mi 0,75 ATR mi? | **Ölç.** İki rakip eşik aynı kova tablosunda görünecek şekilde ölçüm kuruldu (§4). ODTÜ tezi endeks düzeyinde ölçmüş; bizim sorumuz 30 sembollü evrende hisse düzeyinde. |
| Gece mi gündüz mü ağır basıyor? | **Ölç.** H1, ön kayıtlı red kriteriyle. |
| Yürütme 15dk mı 60dk mı? | Gerçek tercih — ama §1.1 gereği 19.09'a kadar konu dışı. |
| R/R hedefi 1,5R mi 0,67R mi? | **Türetilecek büyüklük, seçilecek değil.** ATR ve 2 seanslık gerçekleşen hareket mesafesi ölçülünce R/R kendiliğinden çıkar. Şu an ikisi de tahmin. |

### MinBTL uyarısı bizim için de geçerli — ve daha kötü

Sentez V162 için 6 bileşen × 3 eşik = 729 kombinasyon hesaplamış ve
5 yıllık günlük veriyle izin verilen 45 sınırının çok üstünde olduğunu
göstermiş. Doğru ve önemli.

Ama bizim durumumuz daha ağır: `sinyal_arsiv.json`'da **6 işlem günü**
veri var. Bu veriyle hiçbir eşik ayarlanamaz. Sentezin tüm sayısal
önerileri (0,3 ATR, 1,5R, 2. gün çıkışı) bizde **test edilemez** —
edilebilir hale gelmesi için önce §4'teki ölçüm, sonra aylarca veri
gerekir.

---

## 3. KÖK NEDEN TARTIŞMASI — üçüncü bir hipotez

Sentez, İş Yatırım önerileriyle V162'nin çelişmesini iki hipoteze
bağlıyor: kısa-ufuk dönüşü (GPT) ve gece/gündüz ayrışması + evren farkı
(Claude). İkisi de makul.

Kurul **üçüncü bir hipotez** ekliyor ve bunu en olası bulur:
**farklı ufuk, farklı nesne.** Kurum bülteni bir *pozisyon önerisi*
üretir (temel analizle önceden süzülmüş isimde, 1-2 gün tutulacak);
V162 bir *durum tespiti* üretir (şu anda akış güçlü mü). Bunlar
çeliştiğinde biri yanılmıyor olabilir — farklı soruları cevaplıyor
olabilirler.

Bu hipotezin testi ucuz: kurum önerilerinin T+1/T+2 göreli getirisi ile
aynı sembollerdeki V162 skorunun **korelasyonuna** bakmak. Korelasyon
sıfıra yakınsa çelişki bir arıza değil, iki ayrı ölçüm aracının doğal
sonucudur — ve o zaman "ayrı bir swing script'i" doğru cevaptır.
Negatifse gerçek bir çatışma vardır ve önce o çözülmelidir.

Not: bu test için **L99 kademe haritası** zaten elimizde ve KMS
altyapısı kurum önerilerini kaydedecek şekilde tasarlandı. Yani üçüncü
hipotez, KMS Faz 1 verisiyle bedavaya test edilebilir hale gelecek.

---

## 4. ÜRETİLEN ÖLÇÜM — `gece_gunduz_ayristirma.py`

Salt ölçüm. Sinyal üretmez, karar dosyasına yazmaz, Pine'a dokunmaz.
30 sembollü evrende gece (kapanış→açılış) ve gündüz (açılış→kapanış)
getirilerini ayrıştırır, XU100'e göre göreli olarak.

Bugünün dört dersi tasarıma gömülü: piyasa-göreli ölçüm, gün-ağırlıklı
okuma (aynı günün 30 sembolü n=30 değil n=1), işlem günü pencereleri,
ve kontrol grubu (gap kovaları karşılaştırmalı okunur).

**Üç ön kayıtlı hipotez — red kriterleri önceden yazılı:**

| | Hipotez | RED kriteri |
|---|---|---|
| H1 | 1-2 günlük getirinin çoğu gecede oluşur | gece payı <%40 → kapanış girişi savunması düşer |
| H2 | Pozitif gap büyüdükçe aynı günün gündüz getirisi düşer | kovalar arası monoton düşüş yoksa gap vetosu dayanaksız, madde düşer |
| H3 | Dün en çok yükselenler bugün geride kalır | üst/alt desil farkı ≤%0,20 ya da ters işaretli → DÖNÜŞ motoru dayanaksız |

ATR, bugünün barını kullanmadan hesaplanıyor (look-ahead yok).

**Test edildi** — hem pozitif hem negatif kontrolle. Sahte veri üretecine
bilerek bir gap-reversal etkisi gömüldü; H2 monoton düşüşü yakaladı
(+0,70 → −0,75 arası düzgün azalan). Aynı veride seri dönüş etkisi
YOKTU; H3 doğru biçimde RED verdi. Yani betik hem var olanı buluyor
hem olmayanı uydurmuyor.

`yfinance` gerektirdiği için Actions'ta koşar; `haber_teshis.yml`
kalıbıyla elle tetiklenen bir workflow yeterli.

---

## 5. KURULUN SIRALAMASI

1. **KAP `when:7d` düzeltmesi** — VBTS körlüğü buradan geliyor (§1.3)
2. **`gece_gunduz_ayristirma.py` koşusu** — 5 yıl, sonra 2 yıl
   (rejim duyarlılığı için iki pencere)
3. **H1/H2/H3 sonucuna göre karar:** üçü de RED gelirse swing projesi
   açılmaz ve bu bir başarısızlık değil, 300 satır kod ve haftalarca
   emek tasarrufudur
4. **Üçüncü hipotez testi** (§3) — KMS Faz 1 verisi biriktikçe
5. **Pine tarafı** — 19.09 sonrası, ve ancak 2-3 olumlu çıkarsa

Sentezin kendi sözüyle bitirelim: bu bir araştırma şartnamesidir.
Kurul o cümleyi tek değişiklikle onaylıyor — **şartnamenin ilk maddesi
kod değil, ölçümdür.**
