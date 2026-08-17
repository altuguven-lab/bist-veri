# İP-6 ÖNERİSİ — ARACI KURUM AKIŞ KATMANI (AKD / TAKAS)
17.08.2026 | Etiket: ÖLÇÜM PROJESİ | Pine'a dokunmaz, kuluçka sayacını yakmaz

---

## 0. ÖNCE PREMİSİ DÜZELTELİM — "BofA yönü belirliyor" ifadesi yanlış kurulmuş

BofA'nın Türkiye'deki yapısı Bank of America Yatırım Bank A.Ş.
BIST'te **Türk bireysel yatırımcıya hizmet vermiyor**; Londra, New York
veya Tokyo'daki bir fon BIST'te işlem yapmak istediğinde ihtiyaç duyduğu
yerel aracı olarak çalışıyor. 2023 yıllık ortalama pay piyasası payı
yaklaşık %7 — yabancı kurumlar arasında birinci.

Yani **BofA bir oyuncu değil, bir boru.** "BofA aldı" cümlesinin gerçek
karşılığı "BofA üzerinden geçen bir ya da birkaç yabancı fon aldı"dır.
Ve o fonların kimliği, sayısı, motivasyonu (aktif görüş mü, endeks
yeniden dengelemesi mi, ETF sepeti mi, müşteri itfası mı) veriden
görünmez.

Bu ayrım kozmetik değil, projenin temelidir: bir boruya niyet atfedersen
kurduğun her model yanlış değişkeni modeller. Küçük yatırımcının
"BofA bir anda sattı" rahatsızlığının çoğu, tek bir global kararın
yürütme algoritmasıyla dakikalara bölünmesidir — bu ne manipülasyondur
ne de öngörülebilir bir niyettir.

---

## 1. VERİNİN NE OLDUĞU VE NE OLMADIĞI

Piyasada iki ayrı veri sürekli birbirine karıştırılıyor:

| | AKD (Aracı Kurum Dağılımı) | Takas dağılımı |
|---|---|---|
| Ne gösterir | Emrin hangi üye üzerinden geçtiği | Payın hangi kurumun saklamasında durduğu |
| Zamanlama | Seans içi / seans sonu | T+2 |
| Kirlilik kaynağı | Aynı fonun birden çok hesabı | **Virman** — alım-satım olmadan da değişir |

Kritik uyarılar:

1. **Takas değişimi ≠ alım-satım.** Kurumlar arası virman, portföy
   düzenlemesi ve hesap hareketleri de takası değiştirir. Bu tek başına,
   naif "takas arttı = topluyorlar" okumasını çürütür.
2. **Yayınlanan "BofA net" rakamları genellikle ilk 10 alım − ilk 10
   satım farkıdır**, seansın gerçek neti değil. Haber sitelerindeki
   "659 milyon TL net" tipi başlıklar bu kısmi farktır.
3. **Maliyet engeli:** BIST takas verilerini 1 Ocak 2025'ten itibaren
   ücretli veri yayın lisansına bağladı. Faz 0'ın ilk işi, TradeMaster
   ve mevcut TradingView Plus aboneliğinin bu veriyi zaten kapsayıp
   kapsamadığını tespit etmek olmalı — kapsamıyorsa proje bir maliyet
   kararına dönüşür.

---

## 2. LİTERATÜR NE DİYOR — halk teorisinin aleyhine

Aracı kurum bazlı BIST verisiyle yapılmış çalışmalar, "yabancı bilir"
sezgisini desteklemiyor:

- **Yabancıların bilgi üstünlüğü genel değil.** Broker düzeyinde
  yerli/yabancı ayrımıyla yapılan bir çalışma, yabancı yatırımcıların
  anlamlı fiyat etkisini örneklemdeki firmaların ancak **%7'sinde**
  buluyor ve genel bir bilgi avantajı bulunmadığı sonucuna varıyor.
  (Political turmoil and the impact of foreign orders on equity prices,
  J. Int. Financial Markets)
- **Sürü davranışı literatürü karışık.** CSAD tabanlı BIST çalışmaları
  çelişkili sonuç veriyor; state-space yöntemli çalışmalar sürüyü daha
  tutarlı buluyor. Tekrar eden bir bulgu var: **sürü davranışı düşen
  piyasada belirginleşiyor** — bu, sizin İP-1'de belgelenmiş "olay öncesi
  testere" ve "V dönüş tuzağı" zaaflarınızla aynı rejimi işaret ediyor.
- **Kurumsal katılım çöküş riskini artırıyor.** BIST'te 2005-2023
  verisiyle yapılan bir çalışma, kurumsal yatırımcı payı arttıkça gelecek
  çöküş riskinin arttığını buluyor ve bunu izleme değil **kısa vadecilik**
  teorisiyle açıklıyor. Aynı yönde: yüksek likidite + yüksek yabancı
  kurumsal pay birlikte çöküş olasılığını yükseltiyor.
- **Yatırımcı tipleri arasında yayılım var ama yön yerliden yabancıya
  değil, tersine.** Risk iştahı bağlantısı çalışmaları, yabancı ve
  profesyonel yatırımcıdan yerli yatırımcıya doğru baskın etki buluyor.

**Bu literatürün özeti şudur:** aracı kurum akışı bir **alfa kaynağı**
değil, bir **rejim ve kırılganlık göstergesi** olarak daha savunulabilir.
Yani "BofA aldı, ben de alayım" değil; "akış yoğunlaşmış ve tek yönlü,
bu ortamda stop mesafem ve pozisyon boyutum farklı olmalı".

Bu, KMS için verdiğimiz hükmün aynısı: **doğrulama katmanı, giriş
üreteci değil.**

---

## 3. NE İNŞA EDİLMELİ — dört aday gösterge

KMS zaten "kim sahiplendiğini **söylüyor**"u ölçüyor (model portföy +
fon raporları). AKD/takas ise "kim gerçekten **hareket ettirdi**"yi
ölçer. İkisi aynı projenin iki yarısı — İP-6, KMS'nin kardeşi olarak
kurulmalı, ayrı bir proje olarak değil.

| # | Gösterge | Tanım | Neyi ölçer |
|---|---|---|---|
| G1 | **Akış yoğunlaşması** | AKD net alışın ilk 3 kurumda toplanma oranı (HHI benzeri) | Tek elden baskı — toksisite vekili |
| G2 | **Yabancı kanal neti** | Yabancı sınıflı üyelerin (BofA dahil) net adedi, ln ölçekli | Küresel para yönü |
| G3 | **Süreklilik** | Aynı yönlü net akışın üst üste kaç seans sürdüğü | Tek günlük gürültüyü eler |
| G4 | **Çelişki bayrağı** | KMS pozitif ↔ G2 negatif (ya da tersi) | **En değerli olan bu** |

G4'ün gerekçesi: model portföyler "topluyoruz" derken kanal dağıtıyorsa,
ikisinden biri yanlıştır ve bu çelişki tek başına bir bilgidir. Tek tek
G1-G3'ten daha az taklit edilebilir ve literatürün "yabancı bilgi
üstünlüğü genel değil" bulgusuyla tutarlı: değerli olan seviye değil,
**uyumsuzluk**.

---

## 4. ÖLÇÜM ŞARTNAMESİ — bugünkü derslerin hepsi buraya yazılıyor

Bugün ölçüm aygıtımızda dört hata bulduk. İP-6, o hatalar **tasarımına
gömülü olmadan** başlamayacak:

1. **Piyasa-göreli ölçüm zorunlu.** Getiri değil, XU100'e göre aşırı
   getiri. (v2.1'de zaten kuruldu, aynı altyapı kullanılır.)
2. **Gün-ağırlıklı okuma zorunlu.** Aynı gün 30 sembolde akış görmek
   n=30 değil n=1'dir. Sinyal-ağırlıklı ortalama rapora yazılmaz.
3. **İşlem günü penceresi.** T+N bar sayarak. (v2.1'de kuruldu.)
4. **Kontrol grubu zorunlu.** "Akış alan semboller" ile "almayanlar"
   aynı gün karşılaştırılır. 13.08 kesitinde bunu yapınca sinyalin
   değeri 1,27 puan değişmişti — kontrolsüz ölçüm yanıltır.
5. **Ön kayıtlı red kriteri.** İP-4'ün D1 kapısı gibi: 8 hafta sonunda
   G4'ün T+5 göreli getiri ayrışması istatistiksel olarak sıfırdan
   ayrılamıyorsa **proje kapatılır**, göstergeler kurtarılmaya
   çalışılmaz.

Ayrıca bir tuzak: takas verisi T+2 gecikmeli. G2/G3'ü "bugünkü karar"
girdisi sanmak, geriye dönük testte gerçekte sahip olmadığın bilgiyi
kullanmaktır. Her ölçümde veri **erişilebilir olduğu tarihle**
etiketlenmeli, üretildiği tarihle değil.

---

## 5. FAZLANDIRMA

**Faz 0 — Fizibilite (bu hafta, kod yok).**
TradeMaster ve TradingView aboneliklerinde AKD/takas verisi var mı,
hangi granülerlikte, indirilebilir mi? Yoksa lisans maliyeti nedir?
Cevap "yok ve pahalı" ise proje burada durur — bu da bir sonuçtur.

**Faz 1 — Kayıt (2 hafta).** Sadece toplama. 30 sembol için günlük AKD
özeti + haftalık takas anlık görüntüsü, `data/kurumsal/akis/` altına.
Hiçbir skor hesaplanmaz, hiçbir karar etkilenmez.

**Faz 2 — Ölçüm (6-8 hafta).** G1-G4 hesaplanır, §4 disipliniyle
ölçülür, haftalık rapora **salt okunur bağlam** olarak eklenir.

**Faz 3 — Karar.** Ön kayıtlı kriter geçilirse KMS ile birleşik bir
doğrulama katmanı; geçilmezse kapatma ve gerekçe yazımı.

---

## 6. AÇIK SÖYLENMESİ GEREKEN

Bu projenin en olası sonucu, İP-4'ün sonucudur: **kapanma.** Literatür
"yabancı akışı genel bir bilgi avantajı taşımıyor" diyor, veri T+2
gecikmeli ve virmanla kirli, yayınlanan rakamlar kısmi.

Buna rağmen kurmaya değer, çünkü G4 (çelişki bayrağı) literatürde
doğrudan test edilmemiş bir kesişimi kullanıyor ve zaten kurulmakta
olan KMS altyapısının üzerine biniyor — marjinal maliyeti düşük.

Ama bir şeyi baştan kabul etmek gerekiyor: bu katman **gün içi yönü
önceden söylemeyecek.** Veri seans sonrası yayımlanıyor. En iyi ihtimalle
"bu tapede pozisyon açma / stopu genişletme" diyen bir risk katmanı olur.
Kimse gün içi BofA hareketini önceden göremez — görebildiğini söyleyen
veri satıyordur.
