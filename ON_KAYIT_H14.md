# ÖN KAYIT: H14 V163 alarmlarının değerlendirmesi (ileriye dönük, plasebolu)

**Kayıt tarihi:** 16.11.2026.
**Uygulayan:** `alarm_karne.py` (plasebo ve H14 haftalık ara bakış bölümleri, 16.11 eki).
**Yalnızca ileriye dönüktür.** Hüküm, bu belge commit edildikten sonra biriken veriyle verilir.

**Neden yazıldı:**
- 16.11'de "kod değişikliğinden sonra alarmlar doğru yön gösteriyor mu?" sorusu soruldu.
- 09–13.11 arasındaki V163 olayları (T+1 için 3–4 gün, T+3 için 1–2 gün) aynı gün rastgele seçilen başka hisselerle karşılaştırıldı. Hiçbir tür plasebodan ayrışmadı (p 0,10–0,93).
- Örnek: SEKTÖR_ROTASYONU T+3 ortalaması +%0,87'den −%2,14'e "döndü", ama aynı günlerin plasebosu da −%1,05'ti. Fark sinyalden değil, o günlerin piyasa hareketinden geliyordu.
- Bu kadar az günle Pine'da eşik değiştirmek, gürültüye göre ayar yapmak olur. Bu belge ne zaman ve hangi ölçüyle karar verileceğini önceden sabitler.

**Görülmüş olan:** 09–13.11 V163 olaylarının T+1 ve T+3 değerleri ve plasebo karşılaştırması (`data/alarm_karne.md`, 16.11). Bu günler V163 verisinin parçasıdır ve resmi bakışlara girer; ancak bu belgedeki eşikler o değerler görüldükten sonra, onlara bakılarak değil, önceden belirlenmiş genel kurallarla seçildi.

**Kural:**
- Bu belge değerlendirme ilk kez çalışmadan önce repoya commit edilir.
- Günlük karne tabloları hüküm değildir. Karar yalnızca haftalık resmi bakışta ve aşağıdaki eşiklerle verilir.
- Hüküm başarısız çıkarsa aynı iddia farklı eşik, ufuk ya da alt grupla yeniden denenmez.
- Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir.

## İddialar

**H14a (ana):** V163 giriş sınıfı alarmları, alarm günü kapanışından T+3 kapanışına, maliyet sonrası XU100'ü geçer **ve** aynı gün rastgele seçilen başka evren hisselerinden daha iyidir.

**H14b (ikincil):** P3_SKOR_AL olayları, aynı dönemdeki P3_HACIM_BEKLE olaylarından (P3 koşulu sağlanmış ama hacim tetiği gelmemiş) T+3'te daha iyidir. Yani hacim tetiği bilgi katar.

**H14c (ikincil, çıkış):** ACIL_CIK, POZ_AZALT ve IC_STOP birlikte, alarmdan sonra T+3'te XU100'ün altında kalan hisseleri plasebodan daha iyi seçer.

## Veri ve tanımlar

Tanımlar alarm karnesiyle **aynıdır**. Kaynak `data/alarm_karne_olaylar.csv`.

| Konu | Tanım |
|---|---|
| Olay | `schemaVersion` "v163" ile başlayan, `taban_gun` ≥ **2026-11-09** olan kayıtlar. Aynı sembol, tür ve gün için tek olay (karnenin kuralı). |
| Giriş sınıfı (H14a) | P1_KALITELI_AL, P1_AL, P2_ERKEN_AL, P2_DIP_DONUS, P2_DESTEK_DONUS, P2_ADAY, P3_SKOR_AL (karnedeki `GIRIS_TURLERI`'nin YUKARI yönlü olanları). |
| Getiri | `net_T3`: XU100'e göre fark, gidiş-dönüş %0,25 maliyet düşülmüş. H14b ve H14c'de yön düzeltilmiş brüt `yon_T3`. |
| Plasebo | Her olay için aynı `taban_gun`'de, evrenden rastgele seçilen **başka** bir hissenin aynı yön ve ufuktaki göreli getirisi. Hükümde 10.000 simülasyon (karnenin günlük tablosunda 2.000), tohum 20261116 (`alarm_karne.plasebo`). p = plasebo ortalamasının gerçeğe eşit ya da daha iyi çıkma oranı. |
| İstatistik | Gün kümelenmiş t (`alarm_karne.kumelenmis`). |
| Sürüm bölmesi | Değerlendirme süresince Pine'da yalnızca hata düzeltmesi yapılabilir. Her düzeltme yeni `schemaVersion` alır; hüküm tablosu sürüm başına ayrıca gösterilir. Eşik ya da ağırlık değişikliği bu türlerin değerlendirmesini sıfırlar ve yeni bir ön kayıt gerektirir. |

## Takvim: haftalık resmi bakış (grup-ardışık tasarım)

16.11'de Başkan'ın talebiyle uzun bekleme yerine **haftalık kontrol** seçildi. Sık bakmak, şans eseri iyi ya da kötü görünen bir haftada yanlış karar verme riskini artırır; bu yüzden erken karar eşikleri tek seferlik bir testten **daha sıkıdır**.

- **Resmi bakış:** Her hafta bir kez, Cuma ya da Cumartesi karne çalışmasında. Sonuç `data/h14/ara_bakis.json` dosyasına eklenir ve sonradan değiştirilmez. Günlük karne tablosu bilgi içindir, karar vermez.
- **İlk karar mümkün olan bakış:** Veri en az **10 farklı işlem gününe** yayıldığında (V163 başlangıcından yaklaşık iki hafta sonra; T+3 için ilk resmi karar en erken 27–28.11 haftası).
- **Son bakış:** 30.04.2027. O güne kadar erken karar çıkmazsa son bakışta aşağıdaki "son hüküm" kuralı uygulanır.

## Karar kuralları

| Karar | Koşul (her resmi bakışta) | Sonuç |
|---|---|---|
| ERKEN_GEÇTİ | ≥ 10 gün, ortalama > 0, gün kümelenmiş t > 2,6 **ve** plasebo p < 0,01 | Grup için olumlu hüküm; test kapanır |
| ERKEN_DURDUR | ≥ 10 gün, ortalama < 0, gün kümelenmiş t < −2,6 **ve** plasebo p > 0,99 (rastgele seçimden belirgin kötü) | Olumsuz hüküm; ilgili Pine bileşeni düzeltme listesine girer |
| DEVAM | diğer durumlar | Bir sonraki hafta yeniden bakılır |

- **Son hüküm (30.04.2027, erken karar çıkmadıysa):** ortalama > 0, t > 1,96 ve plasebo p < 0,05 ise GEÇTİ; aksi halde KALDI. 20 günden azsa VERİ YETERSİZ.
- **H14a:** giriş grubu, `net_T3` ortalaması ve t; plasebo karşılaştırması brüt yön getirisiyle (`yon_T3`) yapılır, çünkü plasebo hissesine maliyet uygulanmaz.
- **H14b:** P3_SKOR_AL ile P3_HACIM_BEKLE arasındaki `yon_T3` farkı; yalnızca ikisinin de görüldüğü günler, gün içi etiket permütasyonu ile p. Aynı eşikler (p < 0,01 erken, p < 0,05 son).
- **H14c:** çıkış grubu (ACIL_CIK, POZ_AZALT, IC_STOP), `yon_T3`; aynı eşikler.
- Her iddia ayrı karar verir. Uygulayan kod: `alarm_karne.h14_ara_bakis` ve `h14_resmi_kayit`.

## Hızlı düzeltme kuralı

Hızlı hareket etmek ile gürültüye göre ayar yapmak arasındaki çizgi şöyle çekilir:

- **Hemen düzeltilir (beklemez):** kodun yanlış çalıştığı durumlar. Sinyalin yanlış barda tetiklenmesi, alanların boş ya da hatalı gelmesi, alarm kayıpları, yön tanımı hataları. Her düzeltme yeni `schemaVersion` alır; ölçüm sürüm başına ayrıca gösterilir.
- **ERKEN_DURDUR kararından sonra düzeltilir:** bir grubun rastgele seçimden belirgin kötü çıktığı durumlar. Düzeltme yeni bir ön kayıtla birlikte yapılır.
- **Düzeltilmez:** tek bir haftanın iyi ya da kötü görünmesi. Eşik ve ağırlık değişikliği ancak bir karar sonrasında yapılır.

## Bilinen zayıflıklar

- **Kayıp alarmlar:** Webhook zaman aşımları (12–16.11'de günde 1–2 kayıt) veri setinden düşüyor. Kayıplar aynı bara çok alarm düşen yoğun anlara yığılıyorsa bu rastgele değildir. Kayıp sayısı `data/gunluk_ozet_kapsama.json` ile izlenir ve hüküm notunda yazılır.
- **Evren küçük:** 32 hisse; plasebo havuzu aynı evrenden. Sinyal "evrendeki ortalama hisseden iyi mi" sorusunu cevaplar, "piyasadan iyi mi" sorusunu net_T3 cevaplar.
- **Olaylar bağımsız değil:** Aynı hissede art arda gelen sinyaller var; gün kümelemesi bunu kısmen düzeltir.
