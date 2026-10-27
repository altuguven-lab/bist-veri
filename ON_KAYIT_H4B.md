# ÖN KAYIT: H4b bilanço sürprizi, gerçek KAP açıklama tarihiyle

**Kayıt tarihi:** 27.10.2026. H4 deneme 1 sonucu (ZAYIF) görüldükten sonra, H4b'nin hiçbir sonucu görülmeden.
**Uygulayan betik:** `h4b_kap_tarihli.py`
**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h4b/deneme_kaydi.json` dosyasına eklenir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## Neden ayrı bir test

H4'te bütün şirketler aynı gün, yasal son tarihlerden sonra giriyordu. Bu iki şeyi kaçırıyordu:
- Erken açıklayan şirketlerdeki ilk sürüklenmeyi.
- Çeyrek başına tek gözlem birimi (11 örneklem dışı çeyrek) yüzünden gücü.

H4b her şirkete kendi KAP açıklamasının ertesi günü girer ve **takvim zamanlı portföy** ile ölçer: her gün, aktif bütün pozisyonların ortalaması.

**Dürüstlük notu:** H4'ün sonucu görüldükten sonra tasarlandı. Aynı sinyal, aynı veri, aynı dönemler üzerinde ikinci bir denemedir. Bu yüzden eşik H4'ten yüksek tutuldu (aşağıda K2) ve sonuç, H4 gölge izlemesinin yerini tutmaz.

## Veri

| Konu | Tanım |
|---|---|
| Açıklama tarihi | `data/kap_finansal_rapor_tarihleri.json`. KAP'ta konusu "Finansal Rapor" olan, şirketin o çeyrek sezonundaki **ilk** bildirimi. |
| Kapsam şartı | S değeri hesaplanabilen şirket-çeyreklerin en az %80'inde KAP tarihi bulunmalı. Yoksa test çalışmaz, sonuç `VERI_YETERSIZ` olur. Toplayıcı tamamlanmadıysa da `VERI_YETERSIZ`. |
| Sinyal S, evren, mali veri, fiyat, sektör sepeti, maliyet | `ON_KAYIT_H4.md` ile aynı. |

## Sınıflandırma (ileriye bakmadan)

- Sınıflandırma, açıklama anında bilinen bilgiyle yapılmalı. O çeyreğin üçte bir sınırları sezon bitmeden bilinemez. Bu yüzden **bir önceki çeyreğin** tüm S dağılımının %33 ve %67 yüzdelikleri kullanılır.
- **İYİ:** S ≥ önceki çeyreğin %67'lik yüzdeliği.
- **KÖTÜ:** S ≤ önceki çeyreğin %33'lük yüzdeliği.
- Önceki çeyrekte 30'dan az şirket varsa o çeyreğin olayları dışarıda kalır.

## Giriş ve tutma

- **Giriş:** Açıklamanın yerel tarihinden **sonraki** ilk işlem gününün kapanışı. Seans içi ya da akşam açıklaması fark etmez; her zaman ertesi gün kapanışı.
- **Tutma:** 40 işlem günü.
- **Günlük katkı:** hisse günlük getirisi − sektör sepeti günlük getirisi.
- **Maliyet:** pozisyon başına %0,25, tutma süresine eşit bölünür (günlük 0,25/40).

## Birincil test

- **Seri:** İYİ pozisyonların takvim zamanlı günlük ortalama sektöre göre net getirisi. Pozisyon olmayan günler seriye girmez.
- **Ölçek:** günlük ortalama × 40 = "40 günlük pozisyon başına eşdeğer".
- **t istatistiği:** 20 gecikmeli Newey-West.
- **Dönemler** (pozisyonun giriş tarihine göre):
  - IS: 01.04.2021–31.10.2023.
  - OOS: 01.11.2023–31.07.2026.
  - 01.08.2026 sonrası "taze" olarak ayrı raporlanır.

## Geçme kriterleri (beşi birden)

- **K1.** OOS 40 günlük eşdeğer ortalama > 0.
- **K2.** OOS t > 2,58. H4'ün sonucu görülmüş ikinci deneme olduğu için %1 düzeyi.
- **K3.** OOS çeyrek sezonlarının en az %60'ında, o sezonun İYİ pozisyonlarının 40 günlük ortalaması > 0.
- **K4.** Tek bir sektör çıkarıldığında her durumda OOS ortalama > 0 kalır.
- **K5.** IS ortalama > 0.

**Etiketler:**
- GEÇTİ: beşi birden.
- ZAYIF: K1 ve K5 tutuyor, diğerlerinden en az biri tutmuyor.
- ELENDİ: geri kalan her durum.
- VERI_YETERSIZ: kapsam şartı sağlanmadı.

## Raporlanan ama hüküm vermeyenler

- KÖTÜ pozisyonların takvim zamanlı serisi ("kötü bilanço sonrası uzak dur" adayı).
- İYİ − KÖTÜ günlük fark serisi.
- 10 ve 20 günlük tutma.
- Bankalar hariç sürüm.
- Açıklama saatine göre kırılım: seans içi (10:00–18:10) ve seans dışı.
- Kapsam: çeyrek başına KAP tarihi bulunan şirket oranı, ortalama açıklama gecikmesi (gün).

## Bilinen sınırlar

`ON_KAYIT_H4.md`'deki beş sınırın hepsi geçerli. Ek olarak:
- KAP sorgusu günlük sonuç sınırına takılırsa bazı bildirimler eksik kalabilir. Toplayıcı tavan şüphesini raporlar.
- Önceki çeyreğin eşikleri, mevsimsellik nedeniyle (örneğin 4. çeyrekten 1. çeyreğe geçişte) sınıf oranlarını üçte birden saptırabilir. Oranlar raporlanır.
