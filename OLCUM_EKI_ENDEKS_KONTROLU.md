# ÖLÇÜM EKİ — ENDEKS KONTROLÜ SONUCU
17.08.2026 | `gece_gunduz_ayristirma.py 5y` (H1_KONTROL_endeks ile)

---

## 1. ARTEFAKT ŞÜPHESİ ELENDİ

| | Gece | Gündüz | Gece payı |
|---|---|---|---|
| 30 sembollü evren (düzeltmeli seri) | %+0,2796 | %−0,0445 | %86,3 |
| **XU100 (düzeltme YOK)** | **%+0,2407** | **%−0,0420** | **%85,1** |

Endeks fiyat serisinde temettü/bedelsiz düzeltmesi yok ve **aynı deseni
gösteriyor.** Temettü düzeltmesinin açıklayabileceği kısım en fazla
0,039 puan — yani bulgunun %14'ü. Geri kalan %86'sı gerçek.

**H1 doğrulandı.** Bu bir veri artefaktı değil, BIST'in gerçek
mikroyapısı: son beş yılda getirinin tamamı gece penceresinde oluştu,
seans içi ortalama negatifti.

Bileşik etkiyle (XU100, 1249 gün):

| | Günlük | 5 yılda |
|---|---|---|
| Sadece gece tutan | %+0,2407 | **×20,1** |
| 24 saat tutan (al-tut) | %+0,1987 | ×11,9 |
| Sadece gündüz tutan | %−0,0420 | **×0,59** |

Son satır çarpıcı: beş yıl boyunca her sabah açılışta alıp her akşam
kapanışta satan biri, nominal olarak parasının %41'ini kaybederdi —
endeks 12 katına çıkarken.

---

## 2. AMA BU BİR STRATEJİ DEĞİL — maliyet aritmetiği

"Öyleyse kapanışta al, açılışta sat" refleksine karşı hesap:

Gece-only tutmanın al-tut'a göre kazandırdığı, kaçınılan gündüz
sürüklenmesidir: **günde %+0,042.** Yıllık brüt %+10,5.

Ama bu, **yılda 250 tam işlem turu** demek:

| Tur başına maliyet | Yıllık net |
|---|---|
| %0,02 | %+5,5 |
| %0,03 | %+3,0 |
| **%0,05** | **%−2,0** |
| %0,10 | %−14,5 |

**Başabaş noktası tur başına %0,042.** Komisyon + BSMV + açılış
seansındaki spread'in bu rakamın altında kalması bireysel yatırımcı
için gerçekçi değil.

Ayrıca hepsi **nominal TL.** Beş yılda ×11,9 (yıllık ~%64 nominal),
aynı dönemin enflasyonuyla büyük ölçüde örtüşüyor. Yani gece primi
büyük ihtimalle alfa değil — TL'nin küresel saatlerde değer kaybetmesinin
açılışta fiyata girmesi. Bunu yakalamanın yolu işlem yapmak değil,
zaten yatırımda olmak.

---

## 3. O ZAMAN BU ÖLÇÜM NE İŞE YARIYOR — üç somut sonuç

**a) V162 teşhisi kesinleşti.** Gün içi akıştan 1-2 günlük getiri
beklemek, beklenen değeri negatif olan pencerede sinyal aramaktır.
Bu, kurum önerileriyle çelişmenin en olası açıklaması ve artık
ölçülmüş bir gözlem.

**b) Tasarım kuralı doğdu:** hiçbir strateji sistematik olarak
"sadece seans içi" pozisyon taşımamalı. Zaman-bazlı zorunlu çıkışın
**kapanışta** olması (sentezin önerdiği gibi) doğru; ama girişin de
kapanışa yakın olması gerektiği artık bir tercih değil, ölçülmüş bir
gereklilik — ve mevcut alarm borumuz (18:11 TSİ) buna izin vermiyor.
**19.09 sonrası birikimin en üst maddesi bu olmalı.**

**c) Aranacak edge yer değiştirdi.** Zamansal edge (gece) maliyet
yiyor ve zaten al-tut ile geliyor. Geriye **kesitsel** edge kalıyor:
H3'ün bulduğu desil farkı %0,383/gün. 1-2 günlük tutuşla bu ~125 tur/yıl
demek, yani maliyet baskısı gece-only'nin yarısı.

Ama bu rakamı hedef sanmayalım — üst sınırdır, tahmin değil: aynı
veride ölçüldü, desil uçları haber ve tavan-taban hareketlerini
içeriyor, ve "üst desilde olmak" ile "üst desili önceden seçmek" aynı
şey değil. Gerçek soru şu: **dünkü getiriden başka hiçbir bilgi
kullanmadan** elde edilen bu farkın ne kadarı, gerçek bir seçim
kuralıyla korunabilir?

---

## 4. SIRADAKİ

1. **2y koşusu** — beş yıllık pencere 2021-2023 enflasyonist melt-up'ı
   içeriyor ve §2'deki "gece primi = TL sürüklenmesi" hipotezi tam da
   bunu söylüyor. İki pencere ayrışırsa hipotez güçlenir.
2. **H3'ün dayanıklılık testi** — desil farkı yıl yıl ayrıştırılmalı;
   tek bir rejimden geliyorsa DEVAM motoru da düşer.
3. **Maliyet parametresi ölçülmeli** — TradeMaster'daki gerçek komisyon
   + BSMV + tipik açılış spread'i. §2'deki tablo bu sayı olmadan
   varsayım tablosu.

---

## Küçük not: koşular arası tekrarlanabilirlik

İki 5y koşusu 1257 ve 1249 gün verdi, gece payı %86,5 ve %86,3.
Fark önemsiz ama sıfır değil — `period="5y"` kayan bir pencere.
İleride kıyaslanacak koşularda sabit tarih aralığı kullanmak, ölçümü
tekrarlanabilir kılar. Şimdilik sonucu etkilemiyor.
