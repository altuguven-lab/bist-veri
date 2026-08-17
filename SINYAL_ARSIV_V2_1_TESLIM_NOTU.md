# sinyal_arsiv_gunluk.py v2.1 — TESLİM NOTU
17.08.2026 | Kurul kararı: seçenek (1) — düzelt ve tüm arşivi yeniden doğrula
Etiket: ALTYAPI (salt ölçüm) | Pine'a dokunmuyor, kuluçka sayacını yakmıyor

Dosya: `sinyal_arsiv_gunluk_v2_1.py` → depoda `sinyal_arsiv_gunluk.py` yerine konur.
(v2 taslağı geçersiz — bu sürüm onu kapsıyor.)

---

## 1. DÜZELTME

`T+N` artık **seri üzerinde bar sayarak** bulunuyor, takvim günü ekleyerek değil.

Kontrollü seriyle doğrulandı (03-14.08, kapanış = gün numarası):

| Sinyal günü | T+1 | T+2 | T+3 |
|---|---|---|---|
| Cuma 07.08 | Pzt 10 | Sal 11 | Çar 12 |
| Perşembe 06.08 | Cum 07 | Pzt 10 | Sal 11 |
| Pazartesi 10.08 | Sal 11 | Çar 12 | Per 13 |

Eski davranışta Cuma sinyalinin üç penceresi de Pazartesi kapanışına düşüyordu.

Aynı düzeltme piyasa endeksine de uygulandı — sinyal ve referans **aynı
pencereden** okunuyor, yoksa göreli getiri kendi içinde tutarsız olurdu.

---

## 2. MİGRASYON MEKANİZMASI

`OLCUM_SURUMU = 2` sabiti eklendi. Her kayıt `olcum_surumu` alanı taşıyor;
bu sayıdan küçükse (ya da alan yoksa) kayıt yeniden hesaplanıyor.

Bu, tek seferlik bir betik değil — kalıcı bir taşıma yolu. Ölçüm mantığı
bir daha değişirse sabit artırılır, arşiv kendini bir sonraki koşuda taşır.

Ek olarak `_donem_sec()`: yeniden doğrulama tüm arşivi taradığı için
fiyat dönemi artık sabit değil, en eski kaydı kapsayacak şekilde
seçiliyor (3mo → 6mo → 1y → 2y → 5y → max). Sabit `2mo` ile arşiv
büyüdükçe eski kayıtlar sessizce ölçüsüz kalırdı.

---

## 3. TEST SONUÇLARI (gerçek arşiv, sahte fiyat kaynağı)

```
Fiyat donemi: 3mo (arsivin en eskisi: 2026-08-04)
Piyasa referansi: XU100.IS
21 sinyal bu kosumda dogrulandi (T+3 islem gunu gecmis)
53 eski kayit islem-gunu penceresiyle YENIDEN hesaplandi (olcum surumu 2)
Arsiv: 97 toplam, 74 dogrulanmis
```

| Kontrol | Sonuç |
|---|---|
| T+1=T+2=T+3 çakışması | **10 → 0** |
| `olcum_surumu = 2` taşınan kayıt | 74/74 |
| İkinci koşu (idempotens) | 0 yeni, 0 taşıma |
| Karışık arşiv uyarısı | tetiklenmedi |

Doğrulanmış kayıt 53'ten 74'e çıktı: eski takvim-günü mantığı, T+3'ü
hafta sonuna denk gelen bazı kayıtları gereksiz yere `BEKLIYOR`da
tutuyormuş.

**Not:** testteki getiri yüzdeleri anlamsız (sahte fiyat serisi ~100'den
başlıyor, sinyal fiyatları gerçek). Test edilen şey **pencere mantığı ve
migrasyon**, getiri değerleri değil. Gerçek rakamlar ilk canlı koşuda çıkar.

---

## 4. KORUNAN DAVRANIŞLAR

- Fiyat serisi çekilemezse kayda **dokunulmuyor** — eski hali korunuyor,
  yarım hesaplanmış kayıt oluşmuyor.
- Böyle kayıtlar kalırsa arşive `_uyari` alanı yazılıyor (karışık arşiv
  sessizce oluşmasın diye).
- `tip_ozet` (sinyal-ağırlıklı) aynen duruyor; `tip_ozet_goreli` ve
  `gun_ozet` onun yanına eklendi.
- `dogrulama_durumu` yeniden adlandırılmadı (`hafta_denetim.py` okuyor);
  anlamı `_alan_aciklamalari` bloğunda yazılı.

---

## 5. İLK CANLI KOŞUDA BAKILACAKLAR

1. `piyasa_referansi` → `XU100.IS` mi, `YOK` mu? Yahoo'nun endeksi
   verdiğini burada doğrulayamadım. `YOK` gelirse göreli alanlar
   yazılmaz (mutlak ölçüm devam eder) ve endeks kaynağı ayrıca çözülür.
2. `53 eski kayit ... YENIDEN hesaplandi` satırı gerçek veride de
   görülmeli — görülmezse migrasyon çalışmamıştır.
3. `_uyari` alanı **oluşmamalı**. Oluşursa hangi sembollerin serisi
   çekilemediğine bakılır.
4. Yeni gün-ağırlıklı rakamlar eski raporlardakiyle **tutmayacak** —
   bu beklenen sonuçtur, kurul kararı buydu.

---

## 6. SIRADAKİ

- `haber_teshis.yml` + üç teşhis koşusu (KAP, GN:AKBNK, tümü) — bekliyor
- P3_SKOR_AL mesaj şablonu + Düzenle→Kaydet turu — bekliyor
- `inbox_birlestir.py` koşum sırasına yerleştirme — bekliyor
- TAVHL stop yenilemesi + İHLAL-2 tutanağı — bekliyor
