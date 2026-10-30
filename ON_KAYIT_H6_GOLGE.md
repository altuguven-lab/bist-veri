# ÖN KAYIT: H6 ileriye dönük gölge izleme

**Kayıt tarihi:** 30.10.2026. H6 deneme 1 sonucu (ZAYIF) görüldükten sonra, ama gölge dönemin hiçbir sonucu görülmeden.
**Uygulayan betik:** `h6_golge.py`
**Bağlı olduğu kayıt:** `ON_KAYIT_H6.md` (SHA-256 `c1fb12c2…`). Bu belge o kaydın tanımlarını değiştirmez, yalnızca ileriye uygular.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## Neden

H6 bileşik portföyü örneklem dışında her yıl ve her sektör çıkarma durumunda artıydı (aylık +0,69 puan), ama 30 ay istatistiksel kanıt için yetmedi. Tek faktörler arasında yalnızca bilanço sürprizi (F5) çoklu test sonrası anlamlı çıktı. Bu sonuç görüldükten sonra tarihsel veride yeni deneme yapmak aşırı uyum olur. Kanıt yalnızca **henüz yaşanmamış aylarda** biriktirilir.

## İzlenen portföyler

Tanımların hepsi `ON_KAYIT_H6.md` ve `h6_faktor_siralama.py` ile aynı.

| Kod | Portföy | Ölçü |
|---|---|---|
| G1 | Bileşik skor üst %20 | Evren eşit ağırlıklı ortalamasına göre aylık net (maliyet × devir) |
| G2 | Yalnızca F5 (bilanço sürprizi) üst %20 | Aynı |
| G3 | Yalnızca F5 alt %20 | Aynı. "Kötü bilanço sonrası uzak dur" adayı; maliyet düşülmez, beklenen işaret eksi |

## Kurallar

- **Oluşum:** Her ayın son işlem günü kapanışında. İlk gölge ayı **Ekim 2026**: oluşum 30.10.2026, ölçüm 30.11.2026'ya kadar.
- **Dondurma:** Bir ayın listeleri, o ayın son işlem günü kapanışı veride göründükten sonraki ilk çalışmada `data/h6/golge.json` dosyasına yazılır ve bir daha değiştirilmez. Liste hesaplanırken yalnızca oluşum gününe kadar bilinir olan veri kullanılır.
- **Ölçüm:** Dondurulmuş listenin getirisi, oluşum günü kapanışından sonraki ayın son işlem günü kapanışına kadar.
- **Veri:** Fiyat yfinance'ten. Mali tablolar repodaki `data/temel` dosyalarından; bunları her salı H4 Gölge İzleme tazeliyor.

## Hüküm (ilk 12 gölge ayı: Ekim 2026 – Eylül 2027 oluşumları)

Son ayın getirisi Ekim 2027 sonunda oluşur; hüküm ondan sonraki ilk çalışmada verilir.

- **G1 ve G2, ayrı ayrı:**
  - GÖLGE GEÇTİ: 12 ayın ortalaması > 0 ve en az 7 ay > 0.
  - ELENDİ: ortalama ≤ 0.
  - ZAYIF: diğer durumlar.
- **G3 KÖTÜ KURALI TEYİT:** Ortalama < 0 ve en az 7 ay < 0.
- **Ara izleme:** Her ayın sonucu raporlanır; hiçbir ara sonuç kuralı ya da hükmü değiştirmez.

**GEÇTİ'nin anlamı:** O portföyün listesi karar destek aracı olarak kullanılmaya aday olur. Pine'da hissenin sıralamadaki yeri gösterilir. Gerçek pozisyon kararı yine Başkan'ındır.

## Bilinen sınırlar

- 12 ay küçük bir örneklemdir. Gölge hükmü tek başına değil, H6'nın tarihsel sonucuyla birlikte okunur.
- `ON_KAYIT_H6.md`'deki altı sınırın hepsi geçerli.
