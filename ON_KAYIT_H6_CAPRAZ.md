# ÖN KAYIT: H6/F5 bağımsız çapraz kontrol (alphalens)

**Kayıt tarihi:** 19.11.2026, betik çalışmadan önce.
**Uygulayan betik:** `h6_capraz_alphalens.py`
**Niteliği:** Bu yeni bir test değildir. 30.10.2026'daki H6 bulgusunun (F5 bilanço sürprizi, OOS üst %20 net +1,18 puan/ay, t 2,37, BH anlamlı; üst−alt brüt +3,32, t 3,97) **portföy ve istatistik katmanının** bağımsız bir kütüphaneyle yeniden hesaplanmasıdır. H6'nın parametreleri değişmez. Tek seferlik çalışır; sonuç ne olursa olsun tekrarlanmaz.

Salt ölçümdür. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## Ne bağımsız, ne değil

- **Bağımsız:** Dilimleme (quintile), dilim getirileri, evren ortalamasından arındırma, bilgi katsayısı (IC). Bunları alphalens-reloaded (sürümü sonuca yazılır) hesaplar.
- **Ortak (bağımsız değil):** Fiyat paneli (`h_testleri.panel_kur`) ve F5 değerleri (`h6_faktor_siralama.faktor_tablosu`). Bu yüzden veri ya da faktör tanımındaki bir hata bu kontrolle yakalanmaz. Sonuç "hesaplama katmanı doğru" anlamına gelir, "F5 gerçek" anlamına gelmez.
- Aynı çalışmada H6'nın kendi `portfoy_serisi` de aynı panelle yeniden hesaplanır. Böylece iki hesap, Ekim'deki yerine **aynı veri** üzerinde kıyaslanır.

## Yöntem

- Her ayın son işlem günü F5 değeri; bir sonraki ay sonuna kadar getiri (H6 ile aynı tutma).
- alphalens: `quantiles=5`, `periods=(1,)` (aylık kapanış serisi üzerinde 1 dönem). Evren ortalamasından arındırılmış (demeaned) brüt getiri.
- Dönemler H6 ile aynı: IS 2021-04..2023-12, OOS 2024-01..2026-06.
- İstatistik: aylık seri üzerinde ortalama ve 2 gecikmeli Newey-West t.
- **Plasebo:** Her ay F5 değerleri hisseler arasında rastgele karıştırılır (200 tekrar, tohum 20261119). Gerçek OOS Q5−Q1 yayılımının plasebo dağılımındaki yüzdeliği raporlanır.

## Uyum kriterleri (dördü birden)

- **U1.** alphalens OOS Q5−Q1 aylık yayılım > 0 ve t > 2,0.
- **U2.** alphalens OOS Q5 arındırılmış brüt ortalaması ile H6'nın aynı panelde yeniden hesaplanan OOS üst %20 brüt−evren ortalaması arasındaki fark mutlak olarak ≤ 0,50 puan. (Dilim sınırları farklıdır: alphalens eşit beşli, H6 en az 5 hisse; küçük fark beklenir.)
- **U3.** alphalens OOS ortalama Spearman IC > 0.
- **U4.** Gerçek OOS Q5−Q1 yayılımı, plasebo dağılımının %95'ini aşar.

**Etiketler:**
- **UYUMLU:** Dördü birden.
- **KISMI:** U1 ve U3 tutuyor, diğerlerinden biri tutmuyor.
- **UYUMSUZ:** Geri kalan her durum. Bu durumda `bist100_tarama`'daki F5 tabanlı K1 etiketi komite incelemesine kadar "doğrulanmadı" notuyla gösterilir.

## Bilinen sınırlar

H6 ile aynıdır: hayatta kalma yanlılığı, nokta-zaman verisi değil, TMS 29, yaklaşık piyasa değeri, temettü hariç. Fiyatlar yfinance'ten yeniden çekildiği için Ekim'deki sayılarla birebir aynı çıkmayabilir. Kıyas, aynı çalışmadaki H6 yeniden hesabıyla yapılır.
