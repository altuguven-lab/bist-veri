# ÖN KAYIT: H16 V163 alarm dengesi piyasanın yönünü önceden gösteriyor mu? (ileriye dönük, plasebolu)

**Kayıt tarihi:** 23.11.2026.
**Uygulayacak kod:** `h16_alarm_rejim.py` (ilk resmi bakıştan önce, en geç 30.12.2026'da depoya girer; bu belge koddan ÖNCE commit edilir).
**Yalnızca ileriye dönüktür.** Veri penceresi **24.11.2026** (dahil) ile başlar. Bu tarihten önceki V163 günleri (09–20.11) görülmüştür ve teste girmez.
Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir.

## Neden yazıldı

- 21.11 haftalık kurulda "alarm sistemi hisse seçmiyor, bir rejim (piyasa yönü) göstergesi olabilir" notu düşüldü.
- Dayanak: H14a'da giriş alarmlarının T+3 sonucu (−%0,74) ile aynı günlerin rastgele hisse plasebosu (−%0,50) birbirine çok yakın. Alarmların getirisi büyük ölçüde o günlerin piyasa hareketini taşıyor.
- Bu gözlem hisse seçimi hakkında bir şey söylemez. Ama alarmların **toplamının** (o gün kaç hissede yukarı, kaç hissede aşağı alarm çıktığı) ertesi günlerin piyasa yönü hakkında bilgi taşıyıp taşımadığı ayrı bir sorudur. H16 yalnızca bunu sorar.
- Fikir görülmüş veriden (09–20.11) doğdu. Bu yüzden o veri teste girmez; test tamamen yeni günlerle yapılır.

## Görülmüş olan

- 09–20.11 V163 olayları ve alarm karnesi tabloları (`data/alarm_karne.md`, 21.11).
- Bu belgedeki tanımlar o günlerin H16 sinyaline bakılarak **seçilmedi**. Sinyal o dönem için hesaplanmadı. Yalnızca tür dağılımı görüldü: giriş sınıfı alarmlar az (günde ortalama 3–4), bu yüzden ana sinyal tür sınıfı yerine alarm **yönü** ve hisse **genişliği** üzerine kuruldu.

## Kural

- Bu belge değerlendirme kodu yazılmadan ve ilk resmi bakıştan önce depoya commit edilir.
- Hüküm başarısız çıkarsa aynı iddia farklı ufuk, eşik, gecikme ya da alt grupla **yeniden denenmez**.
- Ara tablolar hüküm değildir. Karar yalnızca aşağıdaki resmi bakışlarda ve eşiklerle verilir.
- Pine'daki sinyal tanımları değişirse (yeni `schemaVersion` ile eşik ya da ağırlık değişikliği) seri o günde bölünür. Değişiklik sonrası günler ayrı seri olarak raporlanır ve bu hükme girmez. Yalnızca alarm iletimi ya da hata düzeltmesi içeren sürümler seriyi bölmez; hangi sürümün hangi sınıfa girdiği hüküm notunda yazılır.

## İddialar

**H16a (ana):** Gün *d*'deki alarm genişlik dengesi *S_d*, gün *d*'nin piyasa getirisi kontrol edildikten sonra, BIST 100'ün *d* kapanışından *d+1* kapanışına getirisini açıklar.

**H16b (ikincil):** Aynı *S_d*, BIST 100'ün *d* kapanışından *d+3* kapanışına getirisini açıklar.

**H16c (ikincil, dar sinyal):** Yalnızca giriş ve çıkış sınıfı alarmlardan kurulan dar denge *D_d*, H16a ile aynı biçimde *d+1* getirisini açıklar.

Yön önceden sabitlenmez. Test **iki yönlüdür**:
- Pozitif katsayı: alarm dengesi momentum göstergesi gibi çalışıyor.
- Negatif katsayı: ters (karşıt) gösterge gibi çalışıyor.

İkisi de bilgi kabul edilir; hüküm notunda yönüyle birlikte yazılır.

## Veri ve tanımlar

| Konu | Tanım |
|---|---|
| Olay | `data/alarm_karne_olaylar.csv` satırları. `schemaVersion` "v163" ile başlar, `taban_gun` ≥ **2026-11-24**. Aynı sembol, tür ve gün için tek olay (karnenin tekilleştirme kuralı). `GUNLUK_OZET` ve `STOP_KIRILDI` hariç tutulur; STOP_KIRILDI kullanıcının grafik ayarına bağlı olduğu için sistem sinyali sayılmaz. |
| Yön | Karnedeki `yon` alanı (YUKARI / ASAGI). |
| Evren | Günlük özetin beklediği evren (`data/gunluk_ozet_kapsama.json` → `beklenen`, şu an 32). |
| *Y_d*, *A_d* | Gün *d*'de en az bir YUKARI (*Y*) ya da en az bir ASAGI (*A*) yönlü alarm üreten **farklı hisse** sayısı. |
| *S_d* (ana sinyal) | (*Y_d* − *A_d*) / evren. −1 ile +1 arasında. |
| *D_d* (dar sinyal) | (*G_d* − *C_d*) / (*G_d* + *C_d*). *G*: giriş sınıfı hisse sayısı (P1_KALITELI_AL, P1_AL, P2_ERKEN_AL, P2_DIP_DONUS, P2_DESTEK_DONUS, P2_ADAY, P3_SKOR_AL, EKLEME_ADAYI). *C*: çıkış sınıfı hisse sayısı (ACIL_CIK, POZ_AZALT, IC_STOP). *G + C* = 0 ise o gün H16c'den çıkar. |
| Getiri | BIST 100 kapanışından kapanışa log getiri. *r_d*: *d−1* → *d*. *R1_d*: *d* → *d+1*. *R3_d*: *d* → *d+3*. |
| Fiyat kaynağı | `data/bist_resmi_gecmis.json` (borsaistanbul.com, kesinleşmiş kapanış). Kayıt yoksa Yahoo XU100.IS kapanışı kullanılır ve o gün raporda işaretlenir. |
| İşlem günü | `config/market_calendar.yml`. Yarım günler dahil, tam tatiller hariç. |
| Kapsam dışı gün | Köprü arızası: günlük özet kapsaması < %80 (32 hissede 26'dan az). Gün dışarıda kalır, sayısı raporlanır. Sinyal gün içi alarmlardan kurulduğu için eksik gün sinyali sistematik olarak bozar. |

## İstatistik

- **Model:** *R1_d* = a + b·*S_d* + c·*r_d* + hata. H16b'de bağımlı değişken *R3_d*; H16c'de *S_d* yerine *D_d*.
- **Kontrol değişkeni (*r_d*):** Alarmlar o günün piyasa hareketini izler. Bu kontrol olmadan, piyasanın kendi günlük ataleti sinyalin bilgisi gibi görünebilir.
- **Test istatistiği:** *b*'nin t değeri. H16b'de *R3* ufukları üst üste bindiği için standart hata Newey-West (gecikme 3) ile hesaplanır.
- **Plasebo:** Sinyal serisinin (*S_d* ya da *D_d*) 5 günlük bloklar halinde karıştırılması. *r_d* ve getiriler yerinde kalır. 10.000 simülasyon, tohum **20261123**. Blok karıştırma sinyalin kendi otokorelasyonunu korur, getiriyle bağını koparır.
- **p:** Plasebo |t| değerinin gerçek |t| değerine eşit ya da büyük çıkma oranı (iki yönlü).
- **Ek rapor (karar kuralına girmez):**
  - Ham Spearman korelasyonu (*S_d*, *R1_d*).
  - *S_d* üçte birlik dilimlerine göre ortalama *R1*.
  - İsabet: *S_d* işareti ile *R1* işaretinin uyuşma oranı.
  - Kapsam dışı gün sayısı.

## Takvim: resmi bakışlar

- **Resmi bakış:** Her ayın son işlem günü kapanışından sonraki ilk çalışma. İlki 31.12.2026 (yaklaşık 26 gün; yalnızca durum raporu, karar verilmez). Sonuç `data/h16/bakis.json` dosyasına eklenir ve sonradan değiştirilmez.
- **İlk karar mümkün bakış:** Geçerli gün sayısı ≥ **40** (yaklaşık Ocak 2027 sonu).
- **Son bakış:** **30.04.2027** (H14 ile aynı). Yaklaşık 100 geçerli gün.

## Karar kuralları

| Karar | Koşul (her resmi bakışta, iddia başına) | Sonuç |
|---|---|---|
| ERKEN_GEÇTİ | ≥ 40 gün **ve** plasebo p < **0,002** | Olumlu hüküm (yönüyle). Test kapanır. |
| DEVAM | Diğer durumlar | Bir sonraki ay yeniden bakılır. |
| Son hüküm (30.04.2027) | ≥ 60 gün: plasebo p < 0,05 ise GEÇTİ, değilse KALDI. < 60 gün: VERİ YETERSİZ. | — |

- Erken eşik, ayda bir bakmanın getirdiği yanlış pozitif riskini karşılamak için tek seferlik testten çok daha sıkı seçildi.
- Erken "durdurma" kuralı yoktur. Sıfır etki de bir sonuçtur ve son bakışta KALDI olarak yazılır.
- Her iddia ayrı karar verir. H16b ve H16c ana iddiayı kurtarmak için kullanılmaz. H16a KALDI iken H16b ya da H16c GEÇTİ çıkarsa, sonuç "ikincil, tek başına bağlayıcı değil" diye yazılır.

## Sonuç ne işe yarar (önceden yazılmıştır)

- **H16a GEÇTİ:**
  - Alarm dengesi brifinglerde ve haftalık kurulda bir **piyasa rejimi göstergesi** olarak, yönüyle birlikte kullanılabilir.
  - Pine'a dokunulmaz.
  - Göstergenin kullanım biçimi ayrı bir kurul kararıyla belirlenir; bu belge kullanım kuralı koymaz.
- **H16a KALDI ya da VERİ YETERSİZ:**
  - Alarm toplamı yön bilgisi taşımaz.
  - Kurulun "rejim göstergesi" notu kapatılır.
  - Alarmlar yalnızca risk ve disiplin aracı olarak kalır (27.10 yönü).

## Bilinen zayıflıklar

- **Az gözlem:** Günlük tek gözlem. 30.04.2027'ye kadar yaklaşık 100 gün. Küçük etkiler (ör. korelasyon 0,1) bu sürede yakalanamaz. Test yalnızca orta büyüklükte bir etkiyi görebilir.
- **Tek rejim riski:** Pencere tek bir piyasa rejiminde geçerse sonuç başka rejimlere taşınamaz. Hüküm notunda pencerenin XU100 toplam getirisi ve oynaklığı yazılır.
- **Kayıp alarmlar:** Cloudflare köprüsüyle azaldı. Kapsama < %80 kuralı kalan riski sınırlar.
- **Evren küçük ve sabit:** 32 hisse. Evren değişirse (hisse eklenir ya da çıkarılırsa) *S_d* paydası değişir. Değişiklik tarihi raporda yazılır, seri bölünmez.
- **Gün içi zamanlama:** Alarmlar gün içinde tetiklenir, getiri kapanıştan başlar. Bu yüzden ileriye bakma (look-ahead) yoktur. Ama sinyal kapanışa yakın alarmlarla birlikte hesaplandığı için pratikte yalnızca kapanıştan sonra bilinir.
