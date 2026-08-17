# İCRA RAPORU — 17.08.2026
## Teşhis düzeltmeleri, kanıtlar, yama şartnamesi

Sabahki denetimden sonra depo ağacına erişildi. **Üç teşhisim değişti,
biri de sıra değiştirdi.** Aşağıdakiler kanıta bağlanmıştır.

---

## 1. SIRA DEĞİŞTİ: TAVHL stopu YAKLAŞMIYOR — 10 GÜN ÖNCE KIRILDI

`data/sinyal_arsiv.json` kaydı:

| Tarih | Sembol | Sinyal | Fiyat |
|---|---|---|---|
| 2026-08-06 | TAVHL | STOP_KIRILDI | 274.75 |
| 2026-08-07 | TAVHL | STOP_KIRILDI | 274.50 |

Stop 275.00. Sistem **iki gün üst üste** stop kırılımı bildirmiş.
Pozisyon 17.08 itibarıyla hâlâ AÇIK.

RISK_KURALLARI Bölüm 3: stop kırılırsa aynı gün kapatılır, "toparlar"
beklenmez. Bölüm 8.6: kırılan stop TAŞINAMAZ, aynı gün kapanış hükmü
istisnasız uygulanır — ve bu madde geriye yürürlü af değildir.

Sabah "stopa %0.64 mesafede, izle" dedim. **Yanlıştı**: mesafe değil,
10 günlük bir açık ihlal. Bu, günün 1 numaralı maddesidir ve bir yazılım
işi değil, bir icra kararıdır: ya pozisyon kapatılır, ya ihlal tutanağa
işlenip gerekçesi yazılır. Üçüncü seçenek yok.

Not: aynı arşivde 12.08'de TAVHL P3_SKOR_AL (278.25) var — yani sistem
çıkardığı pozisyona 5 gün sonra yeniden giriş sinyali üretmiş. Bu, İP-1'in
"V dönüş tuzağı" zaafının canlı örneği (M5 metriği).

---

## 2. GUNLUK_OZET KAYIPLARI — kök neden bulundu, veri KURTARILDI

Sabah "%25 kayıp" dedim. Kayıplar **kaybolmuyor**: Pipedream ana dosyaya
yazamadığında (sha yarışı) kaydı `data/inbox/` altına tekil dosya olarak
düşürüyor. Orada 19 dosya birikmiş, hiçbir şey onları geri taşımıyor.

`inbox_birlestir.py` yazıldı ve gerçek veriyle test edildi:

- **18 kayıt kurtarıldı** (1 dosya reddedildi, §5)
- Kapsama: 12.08 → 27, 13.08 → 26, 14.08 → 27 sembol
  (önce 22 / 24 / 22 idi)
- İdempotent: ikinci koşu hiçbir şey yazmıyor, doğrulandı
- inbox dosyaları SİLİNMİYOR (geri dönüşü olmayan karar ayrı alınır)

**Düzeltme:** "ENJSA'nın alarmı yok" teşhisim de yanlıştı — ENJSA
11.08'de sinyal üretmiş, inbox'a düşmüş. Alarm var, kanal kaybediyor.

Kalan gerçek boşluklar (kurtarma sonrası): 12.08 ALARK/ENJSA/HALKB/KCHOL,
13.08 AEFES/BIMAS/ENJSA/ENKAI/YKBNK, 14.08 ENJSA/EREGL/ISCTR/ULKER.
Yani ~4-5/gün hâlâ hiç ulaşmıyor ve ENJSA 3/3 gün kayıp — ENJSA'da ayrı
bir sorun var (Pipedream Event History'den bakılmalı).

**Çalışma sırası zorunlu:** `inbox_birlestir.py` → `sinyal_arsiv_gunluk.py`
→ `hafta_denetim.py`. İkisi de tv_alerts_latest.json okuyor; birleştirme
sonra koşarsa hiçbir işe yaramaz.

---

## 3. P3_SKOR_AL: eşik düzeltmesi büyük olasılıkla CANLIDA DEĞİL

Sabahki "doğrulanamıyor" teşhisi güçlendi. Üç bağımsız kanıt:

**Kanıt A — otomasyon zaten iki haftadır söylüyor.**
`hafta_denetim.py` başlığı: W32 "skor alanı bozuk: 31", W33 "skor alanı
bozuk: 23". Sayı, o haftaki P3_SKOR_AL sayısıyla birebir aynı. Betik
sorunu buluyor, kimse okumuyor.

**Kanıt B — eşik yükseldi ama sinyal sayısı arttı.**
`data/sinyal_arsiv.json` (97 kayıt, 04-14.08):

| Dönem | Günlük P3_SKOR_AL | T+1 ort. | T+3 ort. |
|---|---|---|---|
| 04-07.08 (eşik 30) | 6,5/gün | %+0,25 | %+0,79 |
| 10-14.08 (eşik 40?) | 11,2/gün | %-0,81 | %-1,45 |

Eşik %33 sıkılaştırıldı, sinyal frekansı **%72 arttı**. Bu, piyasa
yönünden bağımsız bir gözlemdir — dönemler arası getiri farkı piyasayla
açıklanabilir, frekans artışı açıklanamaz.

**Kanıt C — kapanış skorlarıyla çapraz kontrol.**
13.08'de P3_SKOR_AL alan 14 sembolün 9'unun aynı gün kapanış skoru 40'ın
altında (TTKOM 13,1 / SAHOL 16,2 / KCHOL 16,9 / TOASO 18,3). Tek başına
kanıt değil (skor gün içinde düşebilir), ama A ve B ile aynı yöne bakıyor.

**En olası açıklama:** V157 Pine'da güncellendi ama TradingView'de
P3_SKOR_AL alarmları Düzenle→Kaydet turundan geçirilmedi. TradingView
alarmı, yeniden kaydedilene kadar ESKİ derlenmiş sürümü çalıştırır.
13-14.07'de aynı tuzağa düşülmüştü (plot_38 vakası).

**Yan bulgu:** W32'de POZ_AZALT 7, STOP_KIRILDI 5, ACIL_CIK 1 varken
W33'te bu üç sınıftan **sıfır** kayıt var. OR→AND düzeltmesi risk-off
tarafını tamamen susturmuş olabilir. Sistem şu anda yalnız AL üretiyor,
hiç çıkış üretmiyor — bir kuluçka ölçümü için tehlikeli bir asimetri.

---

## 4. YAMA ŞARTNAMESİ — P3_SKOR_AL mesaj alanları

**Etiket: ALTYAPI + doğrulama. Yeni plot GEREKMEZ.**

`IP4_EK1_P3_SKOR.md` bütçesi "1 alertcondition, plot yok" diyordu; bu
kısıt korunuyor. Çünkü `skor`, `kgs`, `rejim`, `stop` taşıyıcı plotları
GUNLUK_OZET / P3_RADAR / P2_ADAY için **zaten mevcut ve ilk 20 içinde**
(bu üç sinyal tipi alanları dolduruyor). Yapılacak tek şey, P3_SKOR_AL'in
alertcondition mesaj dizesine mevcut placeholder'ları eklemek.

Hedef biçim (GUNLUK_OZET'le birebir aynı alan seti):

```
{"zaman_utc":"{{timenow}}","sembol":"{{ticker}}","sinyal":"P3_SKOR_AL",
 "interval":"{{interval}}","fiyat":"{{close}}",
 "skor":"{{plot(\"Skor\")}}","kgs":"{{plot(\"KGS\")}}",
 "stop":"{{plot(\"Stop\")}}","rejim":"{{plot(\"Rejim\")}}",
 "relvol":"{{plot(\"RelVol\")}}","v112n":"{{plot(\"v112n\")}}",
 "v112wr":"{{plot(\"v112wr\")}}"}
```

Plot başlıkları V157 kaynağındaki gerçek `title=` değerlerinden
kopyalanmalı — bu blok mevcut GUNLUK_OZET mesajından birebir alınırsa
isim hatası riski sıfırlanır.

**Zorunlu ikinci adım:** yama sonrası TradingView'de P3_SKOR_AL
alarmlarının hepsi Düzenle→Kaydet turundan geçirilir. Bu tur zaten §3'ün
asıl testidir: tur sonrası sinyal frekansı 11/gün'den düşerse eşik
gerçekten canlıya alınmamıştı; düşmezse eşiğin kendisi yetersiz demektir.
Her iki sonuç da bilgi üretir.

**Kuluçka uyumu:** alarm SETİ değişmiyor (yeni/silinen alarm yok), yalnız
mesaj İÇERİĞİ zenginleşiyor — Karar Otorite Haritası'nda bu ALTYAPI.
Sayaç yanmaz.

---

## 5. KÜÇÜK AMA GERÇEK BULGULAR

- **DMLKT:** `data/inbox/2026-07-30...DMLKT.json` — evren dışı bir
  semboldan alarm, üstelik eski `{"sinyaller":[...]}` biçiminde.
  Temmuz'daki THYAO-348.50 hayalet alarmının kardeşi. TradingView'de
  aranıp silinmeli. Birleştirme betiği bunu zaten reddediyor (doğru
  davranış), ama kaynağı kapatılmalı.
- **TRALT:** kurtarma sonrası da tek "evren dışı alarm veren" sembol.
  K3 kararı hâlâ bekliyor.
- **`hafta_denetim.py` kuluçka sayacı yanlış:** W33 raporu "Kuluçka günü
  39/42" diyor — 07.07 başlangıcından sayıyor. Protokol 08.08'de
  sıfırlandı, doğrusu **9/42**. Betikteki başlangıç tarihi güncellenmeli
  (RISK_KURALLARI'ndaki 18.08 → 19.09 düzeltmesiyle aynı aile).
- **Arşiv alan adı tuzağı:** `dogrulama_durumu: "DOGRULANDI"` = "ölçüm
  tamamlandı" demek, "sinyal haklı çıktı" demek DEĞİL. Yön isabeti
  `tip_ozet.*.dogrulanan_pct` alanında. İleride bu iki kavram
  karıştırılırsa rapor sessizce yanlış çıkar; alan adı
  `olcum_durumu` olarak yeniden adlandırılmalı (birikime).
- **W31 denetim dosyası yok:** W29, W30, W32, W33 var. Bir haftanın
  otomatik denetimi hiç koşmamış ya da commit edilmemiş.
- **M3 sıfır çünkü kayıt eksik:** islem_gunlugu.json'da tek kayıt var
  (21.07 ASTOR alım, MANUEL_ALIM). 11.08 ASTOR satışı yok. M3
  "%0,0 KALDI" raporluyor — bu bir sistem başarısızlığı değil, kayıt
  boşluğu. Hüküm gününde bu haliyle M3 anlamsız olur.

---

## 6. ŞİMDİ NE YAPILACAK

**Karar bekleyen (senin):**
1. TAVHL — kapat mı, ihlal tutanağı + gerekçe mi? (§1)
2. islem_gunlugu.json'a ASTOR satışı + net tutar teyidi (§5)
3. Konsantrasyon ihlali (sabahki rapor §4) — küçültme planı mı, revize
   takvim commit'i mi?

**Onayınla hemen üretebileceğim (kod hazır ya da küçük):**
4. `inbox_birlestir.py` commit + `update.yml`/`hafta_denetim.yml`
   içinde doğru sıraya yerleştirme — **kod hazır, test edildi**
5. `hafta_denetim.py` kuluçka başlangıç tarihi düzeltmesi (tek satır)
6. RISK_KURALLARI 18.08 → 19.09; SURUM_NOTLARI'ye 08.08 kaydı

**Senin TradingView'de yapman gerekenler:**
7. P3_SKOR_AL mesaj şablonu (§4) + tüm P3_SKOR_AL alarmlarında
   Düzenle→Kaydet turu
8. DMLKT hayalet alarmını bul ve sil
9. ENJSA alarmını Pipedream Event History'den kontrol et (3/3 gün kayıp)
