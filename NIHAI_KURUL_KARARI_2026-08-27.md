GECERLI
# NİHAİ KURUL KARARI — PINE SÜRÜM SENTEZİ
27.08.2026, üçüncü ve son tur | Önceki iki analizin (HTF_FIXED,
GERCEKLIK_ALARM_3) birleştirilmiş sonucu

---

## KARAR TABLOSU

| # | Madde | Kaynak | Sınıf | Karar |
|---|---|---|---|---|
| 1 | Radar bridge NA-güvenliği | HTF_FIXED | ALTYAPI | ✅ UYGULANDI (V162_ALTYAPI_YAMA.txt) |
| 2 | Panel blocker genişletmesi (HTF/AGE/SECLEAD) | HTF_FIXED | ALTYAPI | ✅ UYGULANDI (aynı dosya) |
| 3 | BİST tavan/taban farkındalığı | GERCEKLIK_ALARM_3 | ALTYAPI | 🟢 ŞİMDİ EKLENEBİLİR — aşağıda |
| 4 | Shadow paralel puanlama motoru | GERCEKLIK_ALARM_3 | ALTYAPI ama... | 🟡 ARŞİVLEME OLMADAN DEĞERSİZ — ayrı karar |
| 5 | HTF EMA hesaplama düzeltmesi | HTF_FIXED | MANTIK (C.4) | 🔴 19.09 SONRASI, gölge-koşuyla |
| 6 | sectorBridge/dirAlign NA-güvenliği | HTF_FIXED | MANTIK (C.4, lot boyutu) | 🔴 19.09 SONRASI |
| 7 | 16 alarmın silinmesi | HTF_FIXED | — | ❌ ASLA |
| 8 | P3_SKOR_AL/STOP_KIRILDI mesaj şeması fakirleşmesi | HER İKİSİ | — | ❌ ASLA |
| 9 | v112/N-WR-PF-DD sıfırlanması | Mevcut kod (üçünde de var) | Bilinen sınırlama | 📝 BELGELE, düzeltme projesi AÇMA (M7 zaten kapatıyor) |

---

## MADDE 3 — BİST limit farkındalığı: ŞİMDİ EKLEME GEREKÇESİ

Doğrulandı: `isLimitZoneBist`/`bistRealismGate`/`gapRisk` hiçbir
`alertcondition`'a ya da `_finalDecision`'a girmiyor — sadece panel
rengine besleniyor. Bu, radar-bridge düzeltmesiyle **aynı sınıf**:
ALTYAPI, C.4 dışı, sinyal davranışını değiştirmiyor.

Teknik risk kontrolü: yeni bir `request.security()` çağrısı ekliyor
(günlük kapanış için) — mevcut 13 çağrıya 1 daha eklenir, Pine'ın 40
sınırına göre bolca yer var, endişe değil.

**Değeri somut:** şu an bir alarm geldiğinde "bu fiyattan gerçekten
işlem yapılabilir mi" sorusuna körüz. Bu, panelde görünür hale gelir.

**Öneri: bu maddeyi V162_ALTYAPI_YAMA.txt'nin üzerine, aynı titizlikle
(tam mesaj şeması + 21 alarm korunarak) ekleyip yeni bir teslim
yapayım.**

---

## MADDE 4 — Shadow motor: neden ayrı bir karar

Teknik olarak aynı ALTYAPI sınıfında (doğrulandı, hiçbir alarma
girmiyor). Ama BİST limitinden farklı olarak, **şu haliyle hiçbir
pratik değeri yok** — üretmesi gereken bilgi (V162 ile bağımsız model
ne sıklıkla aynı fikirde) sadece panelde görünüp kayboluyor, hiçbir
yerde birikmiyor.

Değerli olması için `sinyal_arsiv_gunluk.py` benzeri bir arşivleme
mekanizması gerekir — bu, BİST limitinden daha büyük bir iş (yeni
alan, yeni ölçüm mantığı, muhtemelen `hafta_denetim.py`'ye yeni bir
madde). **Bunu şimdi mi açalım, yoksa "değerli ama şu an düşük
öncelik" diye kayda geçip ileride mi ele alalım?**

Benim eğilimim: düşük öncelik. Bugün zaten M7 ile P3_SKOR_AL'in
kendisini dışarıdan ölçüyoruz — shadow motorun sunduğu "iç tutarlılık
kontrolü" değerli ama M7'nin sunduğu "gerçek piyasa sonucu" kadar
acil değil.

---

## MADDE 9 — v112 sıfırlanması: neden düzeltme projesi AÇMIYORUZ

`portfolioPosition` işaretli her sembolde N/WR/PF/DD paneli sıfır
kalacak — bunu düzeltmek (statik kutu yerine tarihli bir mekanizma)
gerçek bir mühendislik işi, ve üç dosyanın hiçbiri bunu çözmüyor.

Ama M7 (`sinyal_arsiv_gunluk.py` + `hafta_denetim.py`, dışarıdan,
gerçek fiyatla) zaten bu ölçümü sağlıyor — panelin sıfır göstermesi
bir bilgi kaybı değil, **aynı bilginin başka bir yerden zaten geldiği**
bir durum. Düzeltme projesi açmak, zaten çözülmüş bir sorunu ikinci
kez çözmek olur. `RISK_KURALLARI.md`'ye tek satırlık bir not
("portfolioPosition işaretli sembollerde panelin N/WR/PF/DD alanı
güvenilir değildir, gerçek performans M7'den okunur") yeterli.

---

## SIRADAKİ ADIM

Onaylarsan şimdi:
1. `V162_ALTYAPI_YAMA.txt`'ye BİST limit farkındalığını ekleyip
   yeniden teslim edeyim (madde 3)
2. `RISK_KURALLARI.md`'ye v112 notunu ekleyeyim (madde 9)
3. Shadow motor (madde 4) ve 19.09-sonrası listesi (madde 5-6)
   olduğu gibi kalsın, aksiyon gerekmiyor

Sonra sektörel analiz sonuçlarına geçelim.
