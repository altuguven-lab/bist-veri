# V162.1 KAPSAMLI DEĞERLENDİRME VE KOTA-NÖTR PAKET
15.10.2026 | Girdi: V162.1_BIST_IRE_FOCUS_24.txt (3779 satır, 255.871 karakter), repo (15.10 11:30), önceki kurul raporu
Gözlem ve sistem mühendisliği değerlendirmesidir, yatırım tavsiyesi değildir.

## 0. Kota kararı ve yorumu
"TradingView kotalarında başabaşız" ifadesini şöyle yorumladım: yeni plot, yeni `alertcondition`, yeni `request.security` ve ek token/karakter **eklenmeyecek**. Bu yüzden önceki raporun Paket 1 ve Paket 2 önerilerini yeniden tasarladım. Kaynağı okuyunca asıl sonuç şu çıktı: **istediğimiz yeni alanların hiçbiri Pine'a girmek zorunda değil.** Seans dilimi (`zaman` zaten geliyor), gap kovası (günlük OHLC'den) ve kategori sunucu tarafında hesaplanıyor. Pine'da yalnızca kota **açan** bir temizlik yapıyorum.

## 1. Kod denetimi: doğrulanmış bulgular

| # | Bulgu | Kanıt | Sonuç |
|---|---|---|---|
| K1 | **BIST limit/gap kapısı ölü kod.** 27.08 kararında "panelde görünür" denmişti. | `bistRealismGate` yalnızca tanımlanıyor (satır 1171), hiçbir yerde okunmuyor. `gapPct`, `gapRisk`, `isLimitZoneBist`, `htfUsable` aynı kaderde. Ek olarak `gapPct` günün açılışını değil **15dk barın açılışını** önceki kapanışla kıyaslıyor; yani wired olsaydı da yanlış ölçerdi. | Kapı fiilen hiç çalışmadı. Çıkarıyorum (1 `request.security` geri kazanılır). Gap bilgisini sunucu tarafında üretiyoruz. |
| K2 | **121 ölü tanım** (120 değişken, 2 fonksiyon). | Her biri tüm kodda tam bir kez geçiyor (kendi tanımı), yan etkisiz, `input`/`plot`/`label`/`alert` içermiyor, zincirleme (cascade) hesaplandı. | 15.734 karakter (%6,2) ve 272 satır geri kazanılır. Üst düzey ifade sayısı 1460 → 1339. |
| K3 | **P3Ozet hiç arşivlenmiyor.** | `sinyal_arsiv.json` kayıtlarında `p3ozet` alanı yok; `sinyal_arsiv_gunluk.py` yalnız skor/kgs/rejim/relvol kopyalıyor. | 04.09'dan beri webhook'ta olan entryScore, htf, B3 yarı-boyut bitleri **hiç analiz edilemedi**. Düzeltildi (aşağıda). |
| K4 | **A1 kararı (23.07) uygulanmamış gibi.** "DEFENSIVE (banka/savunma) hariç" denmişti. | `isDefensive = not isMomentum and not isHeavy and _atrPct < 1.0 and _rsSmooth < 1.5`: sektöre değil **düşük volatiliteye** bağlı. Son 100 alarmın 100'ünde `dna=0`. Arşivde P3_SKOR_AL'in 229 kaydından 45'i banka. | Niyet (bankalar hariç) kodda yok. Ama veri bunu düzeltmeyi desteklemiyor, bkz. 2. bölüm. Mantık değişikliği yapmıyorum. |
| K5 | `pSkorTaban` sorusu kapandı. | Son 100 alarmın tamamında skor tabanı 32. | Grafik başına farklı input riski yok. |
| K6 | HTF hizası zayıf alarmlarda yaygın. | Son 100 alarmın %64'ünde `htf=0` (GUNLUK_OZET dahil), P3_SKOR_AL `htf≥1` istiyor ama P3_RADAR/P4_HAZIRLIK istemiyor. | Gözlem; HTF EMA düzeltmesi için gölge ölçüm n=215'te anlamlı fark vermedi, dokunmuyorum. |

## 2. Yeni empirik bulgu (keşif, ön kayıtsız, çoklu karşılaştırma riski var)
P3_SKOR_AL, XU100'e göre T+3, arşivdeki 223 doğrulanmış kayıt:

| Grup | n | Ort. | t | Pozitif |
|---|---|---|---|---|
| Banka (6) | 43 | %+0,01 | 0,03 | %44 |
| Holding (KCHOL, SAHOL) | 27 | %0,00 | −0,01 | %48 |
| Diğer 22 sembol | 153 | **%−0,95** | **−2,25** | %38 |

Zarar bankalardan/holdinglerden değil, diğer sektörlerden geliyor. Bu bir **hipotez (H-A)**; sektör kırılımı veri görüldükten sonra seçildi. Kayıt altına alıyorum, n büyüyünce yeniden test edilecek. İki sonuç çıkıyor: (i) bankaları P3'ten çıkarmak (A1'in niyeti) skoru düzeltmez; (ii) "diğer" grupta sinyalin kendisi sorunlu görünüyor. Aynı kırılımda P3_RADAR bankalarda zayıf (n=26, −0,89, t=−2,7), yani sonuç tür bazında da tutarlı değil.

Ayrıca bir ders: ACIL_CIK 26.08'de n=6 ile **t=−2,53 (doğru yönde, anlamlı)** idi; bugün n=17 ile **t=+1,11 (yanlış yönde)**. P3_RADAR n=5, t=6,5 → n=55, %45,5. Erken "anlamlı" sonuçlar ortalamaya döndü. Bu yüzden **ACIL_CIK/POZ_AZALT anlamını değiştirmedim.** Yeni kanıt (n=17, t=1,11 / n=7, t=1,31) anlamlı değil, "kenar yok" demeye yeter, "ters çalışıyor" demeye yetmez. Panel metinleri ve mantık aynen kalıyor; kural bölüm 4'te.

## 3. Teslim edilen paket (hepsi davranış-nötr)

| Dosya | Ne yapar | Kota etkisi |
|---|---|---|
| `V162.2_BIST_IRE_FOCUS_ADAY.txt` | V162.1'den yalnızca ölü kodu çıkarır (+1 yorum satırı). Alarm sayısı, mesaj şeması, plot sayısı, karar mantığı aynı. CRLF korundu. | karakter −15.734 (kod: 223.862 → 208.128), `request.security` 14 → 13, `ta.*` 90 → 89, alertcondition 22, plot 161/plotshape 11 değişmedi |
| `olu_kod_analiz.py` + `rapor_olu_kod.txt` | Çıkarılan 121 tanımın satır aralıklarıyla listesi; yeniden üretilebilir. | – |
| `sinyal_arsiv_gunluk.py` | `p3ozet` çözümü (entry, htf, dna, yarı-boyut, skor tabanı) ve `seans_fazi` (ACILIS / SABAH / OGLE / KAPANISA_YAKIN, Istanbul saati) arşiv kaydına eklenir. Ölçüm kodu, kuluçka dışı. | Pine'a dokunmaz |
| `hafta_denetim.py` | M7 çıktısına `olu_sinyal_kurali` ekler (bölüm 4). Bugünkü arşivle çalıştırıldı: P3_SKOR_AL BEKLEMEDE (223/250), P3_RADAR (77/250), P2_ADAY (40/250). | Pine'a dokunmaz |

**Doğrulama ve sınır:** Aday dosyada kalan referans taraması (çıkarılan adlar 0 kez geçiyor), parantez/köşeli/süslü denge, plot/alert/security sayımları ve satır farkı (yalnız 272 silinen + 1 yorum eklenen) kontrol edildi. **TradingView'de derlenmedi.** Statik kontrol derleme garantisi değildir; aşağıdaki test adımı şart.

**Alarmları yeniden kurmak gerekmiyor:** Alarm içeriğini (mesaj, p3ozet, plotlar) değiştirmedik; yani sil-yeniden-kur turu ve alarm kotası harcanmıyor. Yeni sürüm yalnızca grafik/panel tarafında geçerli. (Alarmın kaydedildiği script anlık görüntüsüne bağlı kalması davranışı bu yüzden zararsız.)

## 4. Ön kayıtlı kurallar (bugün kilitlendi)
1. **Ölü sinyal kuralı:** P3_SKOR_AL, P3_RADAR veya P2_ADAY için n ≥ 250 ve XU100'e göre T+3 ortalaması negatif ve t < −1,96 ise tür "TERS SINYAL" ilan edilir; alarm silinmez (ASLA kuralı), kategori kalıcı olarak IZLEME'ye düşer. Bugün: hiçbiri tetiklenmedi, P3_SKOR_AL 223/250.
2. **H-A (keşif):** P3_SKOR_AL'in zararı bankaların/holdinglerin dışında yoğunlaşıyor. Karar için n ≥ 100 "diğer" yeni kayıt (17.09 sonrası dahil) ve aynı sınama yeniden koşulur; o zamana kadar mantık değişmez.
3. **ACIL_CIK/POZ_AZALT:** n ≥ 40 ve t ≥ +1,96 (ters yönde anlamlı) olmadan anlam değişikliği yapılmaz.
4. Spesifikasyon sayısı artırılmaz; yeni fikir ancak eski bir sinyal ailesini kapatırsa girer.

## 5. Uygulama sırası
1. **Python dosyalarını** repoya yükleyin (`sinyal_arsiv_gunluk.py`, `hafta_denetim.py`). Bir sonraki hafta kapanışında yeni alanlar görünür.
2. **Pine adayını** TradingView'de yeni bir indikatör olarak yapıştırıp derleyin; aynı üç sembolde (örn. AKBNK, KCHOL, ASELS) eski ve yeni sürümün panelini yan yana karşılaştırın. Fark görürseniz bana hangi hücre olduğunu söyleyin, tanımı geri koyarım.
3. Derleme ve panel eşit çıkarsa eski sürümün yerine koyun. Alarmlara dokunmayın.
4. Bu temizlikle açılan bütçe (≈ 15,7 bin karakter, 1 security) sonraki gerçek özellikler için rezerv: örneğin B1 karşı-olgusal biti ya da düzeltilmiş gün-açılış gap'i. Şimdi eklemedim; ihtiyaç kanıtlanınca.

## 6. Önceki rapordan neyi değiştirdim
- `seansFaz`, `gapKova`, `kategori` Pine'dan çıktı, sunucu tarafında üretiliyor (kota nötr).
- `P3_KAPANIS_GOLGE` yeni alarm olmaz (alarm kotası). Kapanış gölge ölçümü GUNLUK_OZET kayıtları + günlük veriyle Python'da yapılır; bir sonraki iş.
- B3 karşı-olgusal biti zaten p3ozet'te (yarı-boyut); B1 karşı-olgusalı 8 kapının yeniden hesabını gerektirir (token), ertelendi.
- ACIL_CIK/POZ_AZALT yeniden tanımı onay verilmiş olsa da kanıt eşiğine bağlandı (bölüm 2 ve 4).

## 7. Açık sınırlar
- Çıkarılan 121 tanımın tamamı statik analizle "okunmayan" bulundu; bir tanesi bile yanlış sınıflanmışsa derleme hatası "Undeclared identifier" olarak hemen görünür (sessiz davranış değişikliği oluşmaz).
- Sektör kırılımı (bölüm 2) post-hoc; n ve çoklu karşılaştırma uyarısıyla okuyun.
- 17.09 sonrası P3_SKOR_AL/P3_RADAR rakamları (n=23/56) ön kayıtlı değil, T+3 pencereleri çakışıyor.
