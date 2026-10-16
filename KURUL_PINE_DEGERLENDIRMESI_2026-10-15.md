# KURUL DEĞERLENDİRMESİ — "Gün içi niyet tahmini" ve V162 için Pine yol haritası
15.10.2026 | Kaynak: repo (git pull 15.10 11:30), data/backtest/*, data/denetim/hafta_2026-W41, sinyal_arsiv.json (412 kayıt), raporlar/*, bellek kayıtları
Not: Gözlem ve sistem değerlendirmesidir, yatırım tavsiyesi değildir. Pine kaynağı bu oturumda yüklenmedi; aşağıdaki Pine önerileri CHANGELOG_V162 ve ölçüm dosyalarına dayanır, satır düzeyinde yama için canlı kaynak gerekir.

---

## 1. Soruya doğrudan cevap

Evet, sezginiz doğru: **BIST30'da gün içi alım-satım kararı veren kurumsal oyuncuların ve spekülatörlerin niyetini önceden okuyan bir alarm üretemedik.** Bunun kanıtı tek bir testte değil, birbirinden bağımsız beş ayrı ölçümde aynı yöne bakıyor.

| # | Ölçüm | Sonuç |
|---|---|---|
| 1 | M7 canlı alarm doğruluğu (W41, XU100'e göre T+3) | P3_SKOR_AL n=211: %−0,58, t=−1,84, isabet %41,2. P3_RADAR n=55: %−0,67. P2_ADAY n=26: %−1,77. ACIL_CIK n=17: %+2,66 (çıkış sinyalinden sonra hisse endeksi geçmiş). Hiçbir tür anlamlı pozitif kenar göstermiyor. |
| 2 | Küçük örneklem çöküşü | P3_RADAR n=5, %100, t=6,5 idi; n=55'te %45,5. ACIL_CIK n=6'da %83 idi; n=17'de %47. İlk "güzel" sonuçların hepsi ortalamaya döndü. |
| 3 | Geriye dönük günlük proxy, baz oranla kıyas | P1 proxy (n=4047): T+3 isabet %54,0, ort. +%0,79. Koşulsuz taban (61.738 gözlem): %53,1, +%0,53. Fark ≈ +0,9 puan isabet, +0,26 puan getiri: pratikte sıfır. İki-kapı skor kuralı (B1) %53,0 / +0,53, yani tabanla aynı. |
| 4 | Mikroyapı (gece/gündüz ayrıştırması) | Gece payı %86-87, gündüz ortalaması −%0,04/gün (30 sembolün 25'inde negatif). Sinyalimiz tam da beklenen değeri sıfırın altında olan pencerede (seans içi) giriş üretiyor. |
| 5 | Kısa ufuk kesit testleri | H3: dünün kazananları ertesi gün önde (momentum, dönüş yok). H2: büyük gap her iki yönde de gündüz long için kötü (ters U). Zirveye yakınlık, güçlü sektör momentumu ve "dip" filtresi tabanın altında veya farksız. |

Bu tabloda iki **dürüstlük notu** var:
- Ölçülen şey "sistem kötü" değil, "kenar yok" olmalı. M7'nin kendi okuma kuralı: |t|<1,96 ise "kenar yok" denir, "zarar var" denmez. Ancak P3_SKOR_AL (n=211, t=−1,84) eşiğe yakın ve tutarlı biçimde negatif.
- Kendi hesabım (ön kayıtsız, çakışan T+3 pencereleri ve aynı gün kümelenmesi t'yi şişirir): 17.09 sonrası P3_SKOR_AL n=23, ort. %−1,24, isabet %30; P3_RADAR n=56, %−1,09, t≈−3,2. 17.09'da B1/B3 yamaları devreye girdi. Bu veri "yama zarar verdi" demeye yetmez (n küçük, piyasa rejimi de değişti) ama **"yama iyileştirdi" diyen hiçbir kanıt da yok.**

---

## 2. Neden başaramadık: kök neden analizi

1. **Niyet verisi yok, fiyat türevi var.** Tüm alarmlar fiyat, hacim, EMA, RSI, CVD vekili gibi gecikmeli türevlerden üretiliyor. Fon yöneticisinin emri, AKD/takas, emir defteri yok. İP-6 Faz 0 (takas/AKD) hâlâ lisans engelinde; yabancı payı verisi yalnızca aylık-haftalık ve kısmi.
2. **Ufuk uyumsuzluğu.** Kısa ufukta (T+1) momentum, orta ufukta (T+10) dönüş çalışıyor gibi görünüyor: sert düşüş sonrası T+3 %−0,56 (taban +0,53) ama T+10 %+2,64 (taban +1,81); RISK_OFF'ta dip T+10 isabet %63. Sistem T+3'te ölçülüyor ve "al/çık" mantığı iki ufku karıştırıyor. ACIL_CIK ve POZ_AZALT'ın tersine çalışması buradan geliyor: zayıflık sinyaline satmak, dönüşün hemen öncesine denk geliyor.
3. **Giriş penceresi yanlış.** Alarm 15dk gün içi akıştan çıkıyor; getirinin %87'si gece. Kapanışa yakın giriş ölçülmüş bir gereklilik, mevcut alarm borusu bunu desteklemiyor.
4. **En verimli evreni seçmişiz.** BIST30 en likit ve en çok izlenen havuz. Algoritmik/kurumsal akışın en iyi emildiği yer. Küçük-orta ölçekli hisselerde kenar aramak daha makul, ama kapsam dışı.
5. **Ölçüm altyapısı hâlâ eksik.** M1 "hesaplanamadı" (hit 0/0), M3 %0,0 (veri yokluğu artefaktı), 03-04.09 webhook arızası, 2 kayıtta fiyat sapması (PETKM 20,6 vs 18,81), `skor` alanı bazı kayıtlarda bozuk. Kuluçka "hükümsüz" bitti; yani **bugüne kadar hiçbir sinyal ailesi için temiz ve tam bir karne yok.**
6. **Alarm yoğunluğu.** Haftada 54 işlem sinyali (günde 18, en yoğun gün 52). Bunların büyük kısmı izleme sınıfı (P4_HAZIRLIK 20, P2_ADAY 9, P3_RADAR 9). Bu hacimde insan icracı seçici olamaz, ve her alarm baz oranı geçmek zorunda.
7. **Çoklu test ve serbestlik derecesi.** Repoda 50+ backtest betiği var. Bunların çoğu günlük bar proxy'si, kısa penceresi 60 günlük (ORB/VWAP/MACD), ve her biri "TEK BAŞINA kod değişikliği gerekçesi olamaz" notuyla etiketli. Bu notlar doğru, ama toplamda aranan şeyin sayısı arttıkça tesadüfi bulgu olasılığı da arttı (MinBTL uyarısı bizde zaten ağır).

---

## 3. Kanıtın taşıdığı şeyler (olumlu bulgular, hepsi ön koşullu)

| Bulgu | Güç | Sınır |
|---|---|---|
| Gece primi gerçek mikroyapı (endeks kontrollü, sansürlü, 5 yıl) | Yüksek | Büyük olasılıkla TL'nin nominal sürüklenmesi; işlem stratejisi değil (maliyet sonrası negatif) |
| Gap ters U (H2) | Orta-yüksek (n=443 / 610) | Gündüz getirisi için; T+3 için değil |
| Temiz-uyumlu sektör eşiği: T+3 %57,1 / +0,67 vs baskın tek hisse %51,5 / +0,22 | Orta | Basitleştirilmiş proxy, aynı örneklem içi |
| RSI aşırı-satım dönüşü (276 işlem, +%6,7 net, t=7,7) | Orta | XU100'ü işlemlerin yalnızca %43,8'inde geçiyor, ortalama fark +%1,86; uzun tutma (≤90 gün), nominal sürüklenmeden ayrıştırılmadı |
| Supertrend+ADX: zayıf momentum +%1,43, güçlü momentum −%2,37 (p=0,032) | Orta | Aynı yön RSI testinde de var, ama fark küçük |
| Sert düşüş sonrası T+10 toparlanma (RISK_OFF dip %63) | Orta | Günlük proxy, devre kesici gerçeklerini birebir yakalamıyor |

Ortak desen: **kenar, kısa ufuklu tahminde değil, yapısal olay ve orta ufuklu aşırılık dönüşünde görünüyor.**

---

## 4. Kurulun önerisi: hedefi yeniden tanımlayın

"Kurumların bir sonraki hamlesini tahmin eden alarm" hedefini şimdilik kapatmayı, üç ayrı ve ölçülebilir hedefe bölmeyi öneriyoruz:

- **Katman A. Olay ve risk tespiti (tahmin iddiası yok).** Gap kovası, tavan/taban bölgesi, VBTS/tedbir, KAP, hacim şoku, çıkamayacağı pozisyona girme riski. Başarı ölçüsü "yön doğru muydu" değil "olay gerçekten oldu mu, panel zamanında gösterdi mi".
- **Katman B. Mekanik risk yönetimi.** Stop, zaman çıkışı, pozisyon ve sektör limiti. Burada tahmin yok, disiplin var.
- **Katman C. Orta-uzun ufuk seçimi.** PD/DD ve F/K yüzdelikleri, holding NAD iskontosu, aracı kurum beklentileri, RSI/dip dönüşü. Bugün yaptığımız temel araştırma bu katmanın girdisi. Ufuk haftalar-aylar, gün içi alarm değil.

Gün içi yön alarmları (P3_SKOR_AL, P3_RADAR, P2_ADAY) **gözlem sınıfında** kalır; karar girdisi olmaz, ta ki ön kayıtlı kriter karşılanana kadar.

---

## 5. Pine için somut öneriler (sıralı)

Kısıtlar: (i) "ASLA" listesi korunuyor (16 alarmın silinmesi yok, mesaj şeması geriye gitmiyor); (ii) 17.09'da mantık donması Altuğ kararıyla kaldırıldı ama yamalar ölçülmeden birikmemeli; (iii) alarmın script anlık görüntüsüne bağlı olması nedeniyle yeni alan = sil-yeniden-kur gerektirir, bu yüzden değişiklikleri **tek pakette** yapın.

**Paket 1: ALTYAPI sınıfı, karar mantığına dokunmaz (hemen yapılabilir)**
1. `seansFaz` alanı: açılış (ilk 30dk) / sabah / öğle / son 45dk. Dayanak: gece/gündüz bulgusu. Amaç: M7'yi seans dilimine göre kırabilmek.
2. `gapKova` alanı: H2'nin kovaları (≤−0,75, −0,75..+0,30, +0,30..+0,50, +0,50..+0,75, >+0,75 ATR). Mevcut `bistRealismGate/gapRisk` paneli bu alanı zaten hesaplıyor olmalı; yalnız mesaja taşınır.
3. **Karşı-olgusal bitler** `p3ozet`'e: "B1 çift-kapı olsaydı bu sinyal var mıydı", "kovalama tam veto olsaydı var mıydı". Böylece tek alarm akışından A/B kıyası çıkar, 17.09 yamalarının etkisi sonradan ayrıştırılır. Plot bütçesi (64) ek plot gerektirmez, `p3ozet` kodlama alanı genişler.
4. `kategori` alanı (TICARET / IZLEME / RISK) mesajda: telefon bildirimi ve karne yalnızca TICARET'e; IZLEME günlük özete.

**Paket 2: Gölge modül (yeni alarm türü, ekleme, mevcutlara dokunmaz)**
5. **P3_KAPANIS_GOLGE:** günün son 15dk barında, günlük bağlamla (security günlük) tek karar. Sinyal ancak **kapanışa yakın** ve gap veto'dan geçerse üretilir. Gözlem modunda, hiçbir kaydı etkilemez. Ölçüt: gece primini yakalayan giriş penceresi. Bu, SWING_PINE_SPESIFIKASYONU ve gece/gündüz bulgusunun doğal devamı; "tahmin" iddiası taşımaz, **zamanlama** hipotezidir.
6. **Gap veto** (H2): >+0,75 ATR tam, +0,5..0,75 yarım boyut, ≤−0,75 tam veto. Önce gölge modülde, kanıt gelirse ana akışa.

**Paket 3: Mantık değişikliği, ancak ön kayıtlı kriterle**
7. ACIL_CIK/POZ_AZALT yeniden tanımı: M7'ye göre iki tür de yükselişten önce geliyor (ACIL_CIK +%2,66, POZ_AZALT +%2,73). Önerilen: bu iki tür "savunma sinyali" olarak etiketlenmeye devam eder ama **otomatik azaltma/çıkış anlamı taşımaz**; mekanik çıkış yalnız STOP_KIRILDI ve zaman çıkışı. (Mevcut ölçüm: ACIL_CIK n=17, kullanıcının M1 eşiği %60 altında.) Bu bir mantık değişikliğidir, B1-B3 gibi A/B ile ölçülmeli.
8. Skor ağırlıklarının yeniden kalibrasyonu: **şimdilik yapmayın.** P3_SKOR_AL'de skor kovalarına göre T+3 getirisi monoton değil (skor 0-35: %−0,45; 35-45: %+0,41; ≥45: %−0,70; KGS kovaları da monoton değil). Skor sinyalleri sıralamıyorsa ağırlık oynamak gürültüye uydurmaktır. Önce Spearman(skor, T+3) ve karşı-olgusal bitlerle sorun doğrulanmalı.

**Yapmayın listesi:** yeni göstergeler (MACD/MFI/VWAP/ORB: hepsi maliyet sonrası negatif), 15dk eşik ayarı (n yetersiz), HTF EMA düzeltmesinin zorla ana akışa alınması (gölge n=215'te anlamlı fark yok), yeni skor bileşeni eklemek.

---

## 6. Ön kayıtlı karar kuralları (veri görülmeden, bugün kilitlenmesi önerilen)

- P3_SKOR_AL / P3_RADAR / P2_ADAY için **ölü sinyal kuralı:** n≥250 ve XU100'e göre T+3 ortalaması negatif ve t<−1,96 ise tür "ters sinyal" ilan edilir; alarmı kapatmak yerine (ASLA kuralı) KATEGORİ=IZLEME'ye kalıcı düşürülür. P3_SKOR_AL şu an n=211, t=−1,84.
- Her tür için **baz oran kıyası** zorunlu: aynı gün 30 sembol medyanı ve koşulsuz taban (T+3 %53,1 / +0,53) raporlanır.
- **Seans dilimi ve gap kovası kırılımları** yalnız Paket 1 verisi ≥60 işlem günü birikince açılır; öncesinde spesifikasyon aranmaz.
- Sinyal ailesi sayısı artırılmaz; yeni fikir ancak eskisini kapatırsa girer (serbestlik derecesi bütçesi).

---

## 7. Hemen yapılacak ölçüm düzeltmeleri (Pine'a dokunmaz)

1. M1: hit 0/0 veri bağlantı hatası; sinyal_arsiv.json'daki `getiri_rel_t3_pct` ile hesaplanmalı.
2. M3: islem_gunlugu.json olaylarından üretilmeli ya da metrik resmen kapatılmalı.
3. Fiyat sağlama: PETKM (20,6 vs 18,81) ve ALARK (%7,4) kayıtları incelenmeli.
4. `skor` alanı bozuk kayıtların nedeni.
5. ACIL_CIK isabet tanımı: "yukarı" değil "aşağı veya nötr" beklentisi olduğu için raporlarda %71,4 gibi rakamlar yanlış okunmasın (rel>0 oranı = ters isabet).

---

## 8. Kararınızı bekleyen noktalar

1. Hedefin üç katmana bölünmesi (A olay/risk, B mekanik, C orta-uzun ufuk) onaylanıyor mu?
2. Paket 1 (4 madde, tek sil-yeniden-kur turuyla) ve Paket 2 (gölge) kuluçka sonrası birikim listesine girsin mi?
3. Madde 7 (ACIL_CIK/POZ_AZALT anlamının değişmesi) mantık değişikliği; ayrı onay.
4. Ön kayıtlı ölü sinyal kuralı (bölüm 6) kilitlensin mi?

Sınırlar: Pine kaynağını bu turda okumadım; satır numaralı yama için canlı kaynağı yüklemenizi isterim. Son 17.09 sonrası rakamlar (n=23/56) benim ad hoc hesabım, ön kayıtlı değil.
