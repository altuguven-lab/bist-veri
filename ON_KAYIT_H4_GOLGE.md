ÖN KAYIT: H4 ileriye dönük gölge izleme
Kayıt tarihi: 27.10.2026. H4 deneme 1 sonucu (ZAYIF) görüldükten sonra, ama gölge dönemin hiçbir sonucu görülmeden.
Uygulayan betik: `h4_golge.py`
Bağlı olduğu kayıt: `ON_KAYIT_H4.md` (SHA-256 `0b119af5…`). Bu belge o kaydın kurallarını değiştirmez, yalnızca ileriye uygular.
Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.
Amaç
H4, örneklem dışında artı ama yetersiz güçte çıktı (ZAYIF). Tarihsel veriye ek deneme yapılırsa aşırı uyum riski doğar. Bu yüzden kanıt yalnızca henüz yaşanmamış çeyreklerde, kurallar değiştirilmeden biriktirilir.
Kurallar
Sinyal, sıralama, zamanlama, portföy, sektör sepeti, maliyet: `ON_KAYIT_H4.md` ile birebir aynı (`h4_bilanco_surprizi.py` fonksiyonları).
İlk gölge çeyreği: 2026/09 (3. çeyrek 2026). Kurala göre giriş 30.11.2026.
Liste dondurma:
Giriş günü geldiğinde o çeyreğin İYİ ve KÖTÜ listeleri, S değerleriyle birlikte `data/h4/golge.json` dosyasına yazılır ve bir daha değiştirilmez.
Giriş gününde 30'dan az şirketin verisi varsa dondurma, 30'a ulaşılan ilk çalışmaya ertelenir. Bu durumda giriş fiyatı yine kural günü kapanışıdır ve gecikme kayda geçer.
Giriş gününden önceki çalışmalarda yalnızca "ön liste" yayımlanır; hükme girmez.
Performans: Dondurulmuş listeler için sektöre göre net getiri 10, 20, 40 ve 60 işlem gününde ölçülür. Birincil ölçü 40 gündür.
Veri tazeliği: Mali tablolar her çalışmada İş Yatırım'dan yeniden çekilir (BIST100).
Hüküm (ilk 4 gölge çeyreği: 2026/09, 2026/12, 2027/03, 2027/06)
Dördünün de 40 günlük sonucu oluştuğunda hüküm verilir. 2027/06 için bu, yaklaşık Kasım 2027'dir.
H4 GÖLGE GEÇTİ:
4 çeyreğin İYİ sektöre göre net ortalaması > 0,
en az 3 çeyrekte > 0,
İYİ − KÖTÜ brüt fark ortalaması > 0.
KÖTÜ KURALI TEYİT: 4 çeyreğin KÖTÜ sektöre göre net ortalaması < 0 ve en az 3 çeyrekte < 0. Bağımsız raporlanır; "kötü bilanço sonrası 40 gün alım yok" kuralının dayanağı olur.
ELENDİ: İYİ ortalaması ≤ 0.
ZAYIF: Diğer durumlar.
Ara izleme: Hüküm gününe kadar her çeyreğin sonucu raporlanır, ama hiçbir ara sonuç kuralı ya da hükmü değiştirmez. Erken durdurma yalnızca bir durumda vardır: ilk iki çeyreğin ikisinde de İYİ − KÖTÜ farkı −5 puandan kötü çıkarsa izleme Başkan kararıyla sonlandırılabilir.
Bilinen sınırlar
4 çeyrek küçük bir örneklemdir. Gölge hükmü tek başına değil, H4'ün tarihsel sonucuyla birlikte okunur.
İş Yatırım verisi, dondurma anındaki hâliyle kullanılır.
