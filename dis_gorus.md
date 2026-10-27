# V162 Alarm Sistemi: Dış Görüş (27.10.2026)
Sistem tasarımı değerlendirmesidir, yatırım tavsiyesi değildir. Kaynaklar: `data/alarm_karne_olaylar.csv` (953 olay) üzerinde kendi hesaplarım; t değerleri gün kümelenmiş (T+1/3) veya hafta kümelenmiş (T+5/10). Ayrıca aşağıda adı geçen repo dosyaları.

## 1. Teşhis
**Sorun "bilgi yok" değil, işaretin ve ufkun ters olması.** Sistem kısa vadeli göreli güç kovalıyor. Oysa BIST30'da 1-5 günlük hisseye özgü hareket tersine dönme eğiliminde.
- Alış türleri, aynı sembol aynı gün tekilleştirilince (n≈646), XU100'e göre sıfır çıkıyor (T+3 −0,14, t −0,8). **Sektörüne göre** ise tutarlı biçimde negatif: T+1 −0,20 (t −3,0), T+3 −0,29 (t −2,5), T+5 −0,36 (t −2,2).
- Çıkış türlerinde (POZ_AZALT/ACIL_CIK/STOP, n≈60) sinyalden sonra hisse sektörünü geçiyor: T+3 **+2,45** (t 2,9). Yani sistem gücü alıp zayıflığı satıyor, iki yönde de dönüşün yanlış tarafında kalıyor.
- Skor sıralama yapmıyor. Türlerin içinde skor ile T+3 arasındaki Spearman korelasyonu −0,08 ile +0,10 arasında, hiçbiri anlamlı değil. Türlerin içinde skor üçte birlik dilimlere ayrılıp havuzlanınca en yüksek dilim en kötüsü: sektöre göre T+3 −0,92 (t −3,2). Orta dilim −0,03. KGS dilimleri de aynı resmi veriyor. relvol>1,5 ise −0,75 (t −2,0).
- Aynı DNA 10 yıllık günlük testte de var: Supertrend+ADX genel net −%1,34, "güçlü momentum" grubu −%2,37 (`supertrend_adx_swing_momentum_10y_sonuc.json`).
- **XU100'e göre görünen T+10 artısı sinyalden değil, sektör bileşiminden geliyor.** Bankalarda T+10 +3,91, banka dışında −0,20.

**Ölçüm sorunları:**
- Bağımsız gözlem sayısı küçük. Alış olaylarının 583/646'sı günde 8'den fazla alarmın çıktığı günlere düşüyor. Toplamda 62 gün ve 16 hafta var. P3_SKOR_AL'in 269 olayı 39 güne, POZ_AZALT'ın 32 olayı 5 haftaya sığıyor.
- Karne kapanıştan ölçüyor, oysa canlıda alarm fiyatından girilir. İlk 30 dakikadaki alarmlarda kapanış, alarm fiyatının ortalama %0,56 altında. Bu kayma SEKTOR_ROTASYONU'nda −0,30, P3_RADAR'da −0,20. Yani canlı sonuç karnede görünenden daha kötü.
- Veri bütünlüğü sorunlu. 07-17.09 krizinin tam ortasında 9 gün tamamen boş. 138 olayda rejim alanı "?" ve bu olayların ortalaması −1,10. P1'de THYAO iki gün üst üste 348,5 gibi bayat fiyat geliyor; kayma ortalaması −%8,4.
- 17.09 yamaları örneklemin ortasında devreye girdi. P3_SKOR_AL net T+3 yamadan önce −0,86, sonra −0,81, yani değişmedi.

**Zaman dilimi:** Getirinin %69,7'si gece oluşuyor. Gündüz ortalaması −%0,086/gün ve >+0,75 gap sonrası gündüz −0,53 (`denetim/gece_gunduz_olcum.json`, 2 yıl). 15 dakikalık seans içi giriş, beklenen getirinin negatif olduğu pencerede yapılıyor.

## 2. Kurtarılabilir mi?
Bir **mimari** olarak hayır: 10 alarm türü, 4 pozisyon kaynağı, 80 bin token ve 64 plot sınırında, her yamanın bir başka "ölü kod"u ortaya çıkardığı bir yapı (CL006, CL015, CL017). Bir **altyapı** olarak evet.
- **Korunacaklar:** webhook→Pipedream→GitHub hattı, eventId/schemaVersion, `alarm_karne.py` (kümelenmiş t, BH düzeltmesi, ön kayıt), `f_bistRound`/tick yuvarlama, `barstate.isconfirmed` disiplini, portföye bağlı GERÇEK STOP alarmı, RISK_KURALLARI'ndaki risk tabanlı boyutlama.
- **Bırakılacaklar:**
  - P3_SKOR_AL, P3_RADAR, P4_HAZIRLIK, P2_ADAY ve SEKTOR_ROTASYONU'nun işlem sinyali olarak kullanımı.
  - KGS/entryScore'un giriş sıralaması olarak kullanımı.
  - Kelly, regimeHistMult ve ardışık kayıp çarpanlarıyla boyutlama (gölge veriyle kirlenmiş).
  - ACIL_CIK/POZ_AZALT'ın çıkış tetiği olarak kullanımı.
  - P2_DIP_DONUS fikir olarak doğru yönde ama n=21. Kriz öncesi 8 günde +4,53, sonrası −1,05. Yalnız gölgede kalsın.

## 3. Pine ve alarm değişiklikleri (öncelik sırasıyla)
1. **V162'yi dondurun, araştırma kaydına alın.** Telefon bildirimi kapansın, kod değişmesin. Neden: hiçbir tür eşiği geçmiyor ve örneklem ortasında yama yapmak ölçümü bozuyor. Doğrulama: aynı karne 60 işlem günü daha değişmeden üretilir.
2. **Tek hipotezli, yalın yeni Pine.** Günlük bağlam kullanır, 3 alarmla sınırlıdır (GİRİŞ, ZAMAN_ÇIKIŞ, FELAKET_STOP). Kontrol, son sürekli işlem barında (17:45) bir kez yapılır; giriş kapanış seansından olur. Dayanak: gece/gündüz ölçümü ve kayma bulgusu. Doğrulama: aynı sinyal hem alarm fiyatından hem kapanıştan ölçülür.
3. **Seans filtreleri.** İlk 15 dakikalık barda (açılış seansı baskısı + gap) ve 18:00 sonrası kapanış seansı barlarında sinyal üretilmesin. Şu an 6 alarm 10:00'dan önce, 35 alarm 18:00'den sonra gelmiş. Piyasa geneli devre kesici günlerinde de sinyal üretilmesin. Doğrulama: alarm saati dağılımı.
4. **Çıkış tahmine değil mekaniğe dayansın:** sabit süre (T+5) + geniş felaket stopu. Dayanak: çıkış sinyalleri sektöre göre +2,45 ters çalışıyor.
5. **Alarm yükü (payload):** sinyal anı fiyatı, gap kovası, seans fazı, sektör-artık getiri, tedbir/VBTS bayrağı. Kurulun 1. paketi bu yeni script'e uygulanır.
6. **Kesitsel sıralamayı Python'a taşıyın.** 31 sembolü sektöre göre sıralamak Pine'ın işi değil (`request.security` sınırları var). Pine yalnız görüntüleme ve tetik için kalsın. TradingView'daki BIST verinizin gerçek zamanlı mı yoksa 15 dakika gecikmeli mi olduğunu teyit edin. Gecikmeliyse kapanışa yakın sinyal bayat olur.

## 4. Geliştirme sırası ve ilk hipotezler
Akış: fikir → günlük veriyle Python'da ön kayıtlı test → 60 işlem günü gölge alarm → yarım boyutla canlı.
- Örneklem içi dönem 2016-2022, örneklem dışı 2023-06.2026.
- Ortak geçme şartı: örneklem dışında, **sektöre göre** ve %0,25 maliyet sonrası ortalama > 0. Hafta kümelenmiş t > 2,0. Yılların ≥%60'ında aynı işaret. Bir sektör çıkarılınca işaret değişmemeli. Deneme sayısı kayda geçmeli.
- Gölge aşamasında kalma kriteri: ortalama < 0 ve t < −1.

**H1 — Kısa vadeli dönüş:** 5 günlük sektör-artık getirisi en düşük %20'lik dilimdeki hisseler kapanışta alınır, 5 gün tutulur. Dayanak: alış ve çıkış sinyallerinin ayna görüntüsü, en yüksek skor diliminin en kötü olması, RSI dönüş testi. Uyarı: RSI dönüş testi XU100'ü işlemlerin yalnız %43,8'inde geçiyor. `toparlanma_testi` T+20'de neredeyse etki bulmadı (b −0,022, R² 0,001).

**H2 — Giriş zamanlaması:** Aynı sinyaller seans içi alarm fiyatından ve kapanış seansından eşleştirilerek karşılaştırılır. Geçme: kapanış girişi, maliyet farkını aşan bir üstünlük sağlamalı. Dayanak: gece payı %69,7 ve gap kovaları.

**H3 — Sert düşüş sonrası T+10:** ≤−%8 gün sonrası, 448 olay. T+10 +%2,64, koşulsuz taban +%1,81, ancak bu rakamlar **nominal**. Önce XU100'e göre yeniden hesaplanmalı. Fark +0,8 puanın altına düşerse hipotez elenir.

## 5. BIST'e özgü uyarılar (bu sistemin hatalarını açıklayanlar ✱ ile işaretli)
- ✱ **Açılış/kapanış seansı:** İlk bar, açılış seansı fiyatı ve gap'i taşır. relvol ve EMA kesişimleri burada yanlış tetiklenir. İlk 30 dakikadaki alarmlarda kayma −0,56, T+3 −0,53.
- ✱ **Faktör yoğunlaşması:** 31 sembolün 9'u banka/holding, yabancı akışı, CDS ve TCMB kararlarıyla birlikte hareket ediyor. Alarmlar makro günlerde kümeleniyor. "Bağımsız 269 olay" diye bir şey yok.
- ✱ **TL nominal sürüklenme:** Repodaki "%55 isabet" bulgularının çoğu ham TL getirisi. Kurulun aktardığı koşulsuz taban zaten %53,1 / +0,53. Göreli ölçüm şart.
- ✱ **Kıyas endeksi:** BIST30 evreni XU100 ile kıyaslanıyor. XU030 veya evrenin eşit ağırlıklı ortalaması, ayrıca sektör sepeti esas alınmalı.
- **Devre kesici/VBTS:** Durma ve tek fiyat dönemlerinde 15 dakikalık barlar bozulur. Kriz döneminde XU100 bir günde %9,88 hareket etti. Bu günler sinyal dışında tutulmalı.
- **Temettü:** Karne düzeltilmemiş fiyat kullanıyor (`auto_adjust=False`). Hak kullanım günü düşüşleri, temettü ödeyen hisselerde alış sinyallerini cezalandırır. Etkisi küçük ama sıfır değil, kontrol edilmeli.
- **Takas T+2 ve açığa satış:** Aşağı yönlü sinyaller bireysel yatırımcı için yalnızca elde tutulan pozisyonu korur. Bunları "isabet" diye saymak yanıltır.

## 6. Kurul (15.10) hakkında
**Katıldıklarım:** üç katmanlı hedef, kapanış gölgesi, gap vetosu, skoru yeniden ağırlıklandırmamak, yeni gösterge eklememek, ACIL_CIK'ın çıkış anlamını kaldırmak.

**Katılmadıklarım:**
- "Niyet verisi yok" teşhisi eksik. Veride bilgi var ama işareti ters. Bunu gösteren sektöre göre ölçüme hiç bakılmamış.
- "Küçük-orta ölçekte kenar ara" önerisi, süreç oturmadan maliyet, VBTS ve manipülasyon riskini artırır.
- "16 alarm asla silinmez" kuralı sorunun kendisi. Paket 1'i V162'ye değil yeni script'e uygulayın.
- Ölü sinyal kuralı (n≥250) olay sayıyor, küme saymıyor. Hafta sayısı üzerinden tanımlanmalı.

**Kaçırdıkları:** sektör bileşimi etkisi (bankalar), kapanış tabanlı ölçümle canlıda gerçekleşecek dolum arasındaki fark, krizin ortasındaki 9 boş gün. Gece payı için verdikleri %86-87, okuduğum 2 yıllık dosyadaki %69,7 ile uyuşmuyor. Muhtemelen 5 yıllık başka bir ölçüm, kaynağı teyit edilmeli.

## 7. Yapmayın
- Bu 953 olay üzerinde V162 eşiklerini ayarlamayın. Aşırı uyum olur.
- Sinyalleri canlıda ters çevirmeyin (POZ_AZALT'ta almak gibi). Bulgu örneklem içi ve 5 haftalık.
- V162'ye yeni tür, skor bileşeni veya gösterge eklemeyin.
- Ham TL isabetini ve 60 günlük 15 dakikalık yfinance testlerini (ORB/VWAP/MACD) kanıt saymayın.
- Pine panelindeki WR/PF/Kelly değerlerini boyutlamada kullanmayın.
- Ölçerken yama yapmayın. Örneklem sayısını olay değil gün/hafta olarak raporlayın.
- Aynı anda birden fazla hipotezi canlıya almayın.
