# Brifing şablonu (18.11.2026; 19.11 güncellemeleri)

**Neden:**
- **18.11:** Açılmamış kaynaklar için "yeni duyuru görmedim" yazıldı.
- **19.11:** Öğle brifinginde depoda hazır duran veri ("BIST öğle seviyesi") ve açılabilecek bir PDF (Takasbank pozisyon limitleri) için "kontrol edilemedi" yazıldı.

Bu şablon iki şeyi önler: kontrol edilmemiş bir şeyin "yok" diye yazılmasını ve denenmemiş bir şeyin "kontrol edilemedi" diye yazılmasını.

## İşaretler

| İşaret | Anlamı | Ne yazılır |
|---|---|---|
| ✅ | Birincil kaynak açıldı: kurumun kendi sayfası, KAP, PDF, tcmb.gov.tr ya da depodaki veri dosyası | Bağlantı ya da dosya adı ve kaynağın kendi tarihi/saati |
| ◐ | İkincil kaynak (haber sitesi) | Sitenin adı. Birincil teyit bekleniyor. |
| ⛔ | Erişim kuralı gereği açılamıyor (robots.txt, site izni, oturum gerekiyor) | Neden yazılır. İkincil kaynak aranır, bulunursa ◐ ile verilir. Bulunamazsa "panelden bakılmalı" yazılır. |
| ✖ | Açılmaya **çalışıldı** ama açılamadı (zaman aşımı, hata, bayat sayfa) | **Neden zorunludur** ("açılamadı: zaman aşımı"). "Açmadım" bir ✖ gerekçesi değildir. |
| 🕒 | Henüz yayımlanmadı | "Henüz yayımlanmadı, beklenen saat ..." (saat `takvim.json`'dan). Bu bir boşluk sayılmaz. |

**Kurallar:**
- Bir maddeye ✖ yazılmadan önce açılması mutlaka denenir.
- Hafızadan tarih, saat ya da sayı yazılmaz.
- Takvim bilgisi `data/takvim.json` (olaylar ve kurallar) ile `data/makro_takvim.json`'dan alınır.
- "Kurala göre" ve "teyitli" olaylar saatiyle yazılır. Diğerleri "teyitsiz" diye yazılır.

## Sıra

1. **Depo verisi** (önce bunlar okunur; web aramasından önce gelir):

   | Dosya | İçerik |
   |---|---|
   | `data/kurum_kumesi.json` | Son 14 günde 5 ve daha fazla hisseyi kapsayan kurum kümeleri |
   | `data/kurum_taramasi.json` / `.md` | Kaynak durum tablosu; Takasbank'ın bütün PDF özetleri; KAP kurum bildirimleri; izleme listesi ve devre kesici sayımı; takvim |
   | `data/endeks_intraday.json` | XU100, XU030, XBANK, XHOLD, XUSIN, USDTRY, EURTRY, Brent, S&P/Nasdaq vadelileri, ABD 10 yıllık, dolar endeksi, altın (15 dk, Yahoo, gecikmeli) |
   | `data/piyasa_gunluk.json` | TL tahvil getirileri TR02Y, TR05Y, TR10Y (günlük, TradingView TVC → köprü; seans sonu son değer). Bugünün tarihi yoksa 🕒 (seans bitmedi) ya da ✖ (alarm/köprü sorunu) |
   | `data/bist_intraday.json` | Evrendeki 32 hissenin 15 dakikalık barları (öğle seviyesi, gün içi seyir) |
   | `data/kuresel_gosterge.json` | Asya, Avrupa ve ABD özeti |
   | `data/makro_takvim.json` | TCMB ve Fed tarihleri (birincil kaynakla teyitli) |
   | `data/makro_akim_reel.json` / `.md` | Yabancıların haftalık hisse ve DİBS net alımı (TCMB EVDS, milyon USD), ex-ante reel faiz, piyasa faiz beklentisi |
   | `data/bist100_tarama.md` | BIST 100 taraması (K1, K2, K3) ve **H10c**: yabancı payı kesintisiz artan 5 hisse (10 gün ufku, GEÇTİ) |
   | `data/analist_hedef/revizyon.md` | Analist hedef revizyon genişliği (en az 21 günlük karşılaştırma; ilk karşılaştırma Aralık'ta) |
   | `data/msci_turkiye.json` | MSCI dondurması (15.10.2026), Haziran 2027 takvimi, izlenecekler |
   | `data/endeks_intraday.json` (ek) | VIX, EEM (gelişen piyasalar ETF'i), TUR (MSCI Türkiye ETF'i, USD) |
   | `data/makro_akim_reel.md` (ek) | TCMB brüt rezervleri (haftalık), TÜFE bazlı reel efektif kur (aylık) |
   | `data/tv_alerts_latest.json`, `data/gunluk_ozet_kapsama.json`, `data/alarm_karne.md` | Alarmlar, kapsama, karne ve H14 |

2. **Kurum taraması:**
   - Kaynak durum tablosu olduğu gibi verilir. OK olmayan kaynak elle açılmaya çalışılır.
   - Takasbank PDF özeti eksikse PDF elle açılır.
   - KAP bildirim eki robots.txt nedeniyle açılamıyorsa ⛔ yazılır. `kap.org.tr/tr/api/BildirimPdf/<id>` adresi denenir; bildirimin kapak bilgisi buradan okunabilir.
   - Bir listede adı geçmek, ilgili şirket hakkında bir hüküm değildir.
3. **Sistem kontrolleri:** Kapsama, köprü ("TV sinyal: CF" commit'leri), başarısız iş akışları, H14, V195 ve IP-8.
4. **Türkiye 5 yıllık CDS (her brifingte):** Güncel değer, tarihi ve kaynağıyla yazılır. Sırası şöyle: (a) kullanıcının panelinden paylaştığı değer ✅ (panel esastır); (b) toplayıcı kurulunca `data/cds_gunluk.json` (kaynağına göre ✅ ya da ◐); (c) o gün tarihli bir haber ◐ (kaynak S&P Global, Bloomberg, LSEG vb. yazılır). Bugüne ait değer bulunamazsa ✖ yazılır ve "son bilinen: değer, tarih, kaynak" verilir. Tarihi belli olmayan sayfalardaki değer kullanılmaz.
5. **Piyasa:** Endeks ve kur için önce `endeks_intraday.json` kullanılır ("Yahoo, gecikmeli" diye belirtilir). Resmi kapanış için borsaistanbul.com ve TCMB esas alınır; haber siteleri ◐.
6. **Makro ve siyasi:** Her veri için ✅ ya da ◐ kullanılır. Henüz açıklanmamış veri için 🕒 ve beklenen saat yazılır.
7. **Savaş ve jeopolitik:** Haberin tarihi yazılır. Bugünden eski haber "son bilinen" diye işaretlenir.
8. **İzlenecekler:** Yalnızca takvimden alınır, saatleriyle.
9. **Teyit edilemeyenler:** Bu başlık her zaman bulunur. Her ✖, ⛔ ve ◐ maddesi burada nedeniyle birlikte tekrar edilir ve her birine aynı gün için bir kontrol saati verilir.
10. Kaynaklar (markdown bağlantı) ve "Gözlem amaçlıdır, tavsiye değildir".

## Haftalık bakım (Cuma)

- `data/takvim.json`: Gelecek haftanın tek seferlik olayları birincil kaynaktan eklenir. Düzenli yayınlar için `kurallar` bölümüne kural yazılır; kuralın kaynağı açılmış olmalıdır.
- `config/kurum_izleme.yml`: Yeni konular eklenir (şirket adı, konu ve kod; kişi adı yazılmaz).
- `data/kurum_taramasi.md`: BAYAT ya da KAYIT_BULUNAMADI kalan kaynak varsa `data/kurum_taramasi_ham/` klasöründeki ham HTML'e bakılarak ayrıştırıcı düzeltilir.
