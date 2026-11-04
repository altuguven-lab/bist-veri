# ÖN KAYIT: H12 Yüksek hacimli P4_HAZIRLIK alarmları, ileriye dönük test

**Kayıt tarihi:** 04.11.2026.
**Uygulayan betik:** `h12_p4_hacimli.py`.
**Yalnızca ileriye dönüktür.** Kayıt tarihinden önceki alarmlar hükme girmez.

**Neden yazıldı:**
- 04.11 alarm karnesinde, kriz sonrası dönemde P4_HAZIRLIK alarmlarının net T+3 ortalaması +%0,70 (80 olay, t 1,37). Bu, alarm türleri arasında en iyi sonuç.
- Bu alarmların hacimli olanları (relvol ≥ 1) +%1,49 (29 olay) verdi.
- Ancak bu alt grup **sonuç görüldükten sonra** seçildi. Bu yüzden geçmiş veri kanıt sayılmaz; yalnızca kayıttan sonra gelen alarmlarla sınanır.

**Görülmüş olan:** Yukarıdaki geçmiş karne değerleri. Kayıttan sonraki hiçbir olay görülmedi.

**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Ara raporlar hüküm değildir. Hüküm yalnızca bitiş şartı sağlandığında bir kez verilir ve `data/h12/deneme_kaydi.json` dosyasına eklenir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz. Kurul kararı gereği P4_HAZIRLIK "BİLGİ" sınıfındadır; bu test geçse bile sınıf değişikliği ayrı bir kurul kararı gerektirir.

## İddia

**H12:** relvol ≥ 1,0 olan P4_HAZIRLIK alarmları, alarm günü kapanışından 3 işlem günü sonraki kapanışa kadar, maliyet sonrası XU100'ü geçer.

## Veri ve tanımlar

Tanımlar alarm karnesiyle **aynıdır**. Kaynak, `alarm_karne.py`'nin her gün ürettiği `data/alarm_karne_olaylar.csv` dosyasıdır.

| Konu | Tanım |
|---|---|
| Olay | `sinyal == "P4_HAZIRLIK"`. `zaman_utc` ≥ **2026-11-05T00:00:00Z**. `schemaVersion` v162.x ya da v163.x; alarm mantığı iki sürümde aynıdır. Aynı sembol ve aynı gün için tek olay sayılır (karnedeki tekilleştirme). |
| Hacim | `relvol`, webhook'un taşıdığı değerdir (plot taşıyıcısı, bir bar gecikmeli). **Ana grup:** relvol ≥ 1,0. **Karşılaştırma grubu:** relvol < 1,0. |
| Getiri | `net_T3`: alarm günü kapanışından T+3 kapanışına, XU100'e göre fark, gidiş-dönüş %0,25 maliyet düşülmüş. |
| Ek ölçü (hüküm vermez) | `sek_rel_T3` (sektör sepetine göre) ve `net_T5`. |
| İstatistik | Gün kümelenmiş t (`alarm_karne.kumelenmis`; aynı gündeki olaylar tek küme). |

## Bitiş şartı

Ana grupta T+3 getirisi hesaplanmış **en az 100 olay** birikince ya da **30.04.2027** tarihinde (hangisi önce gelirse) hüküm bir kez verilir. Bu tarihte 100 olaya ulaşılmamışsa ve 40'tan az olay varsa hüküm **VERI_YETERSIZ** olur.

## Plasebo (hükmün parçası)

Her ana grup olayı için **aynı sembol**, alarm gününden **63 işlem günü önceki** gün taban alınarak aynı tanımla bir "net T+3" hesaplanır. Fiyatlar `alarm_karne.fiyat_cek` ile alınır.

Bu plasebo, alarmın zamanlamasını ölçer: etki bu hisselerin kalıcı bir özelliğinden mi geliyor, yoksa alarmın zamanlamasından mı?

## Hüküm

**GEÇTİ şartlarının hepsi sağlanmalıdır:**
1. Ana grup ortalaması > 0 ve gün kümelenmiş t > 2,0.
2. Plasebo ortalaması için |t| < 2,0.
3. Ana grup ortalaması > plasebo ortalaması.

**Diğer hükümler:**
- Şart 1 sağlanıp şart 2 sağlanmazsa: **SUPHELI**. Etki zamanlamadan değil, hisse seçiminden geliyor.
- İşaret doğru ve 1,65 < t ≤ 2,0 ise: **ZAYIF**.
- Aksi hâlde: **KENAR_YOK**.

**Ek bilgi (hüküm vermez):** Karşılaştırma grubu (relvol < 1), ana grup ile karşılaştırma grubu farkı, sektöre göre sonuç, T+5, ay bazında ortalamalar ve en büyük 5 olay katkısı.

## Sınırlılıklar

- Alarm günü kapanışından giriş varsayılır. Alarm gün içinde gelir; gerçek giriş fiyatı farklı olabilir. Bu fark karnede "giriş kayması" olarak ayrıca izleniyor.
- 30 sembollük izleme evreni ve tek bir piyasa dönemi söz konusu. Fon krizi sonrası toparlanma özel bir dönem olabilir.
