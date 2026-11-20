# Komite notu: Ajan katmanı önerisi (20.11.2026)

**Durum:** Öneri. `AI_YONETIM_EKIBI_PROTOKOLU.md` §5 gereği protokole yeni katman eklemek komite kararı ister. 21.11 haftalık kurulunun gündemine alınır.
**Karar sahibi:** Altuğ. Bu not tavsiye değildir; seçenekleri ve maliyetlerini sıralar.

## 1. Sorun

Bugünkü yapıda aynı Claude oturumu veriyi okuyor, analiz ediyor, sonucu yazıyor ve kendi işini kontrol ediyor. Son iki haftanın hataları bu yapıdan çıktı:
- 18.11 brifinginde açılmamış kaynaklar için "duyuru yok" yazıldı.
- 19.11 öğle brifinginde depoda hazır olan veri için "kontrol edilemedi" yazıldı.
- H10c doğrulanmış olmasına rağmen taramalara alınmadı.

Hepsi "işini kendi notlayan" tek ajan hatasıdır. Amaç daha çok ajan değil, **görev ayrılığıdır**: üreten ile denetleyen ayrı olsun.

## 2. Mevcut ajanlar (zaten çalışıyor)

| Tür | Örnek | Rol |
|---|---|---|
| Belirlenimci ajanlar (GitHub Actions) | Veri topla, kurum taraması, endeks, EVDS, BIST resmi, risk raporu, sağlık kontrolü | Veri toplar, kural uygular. Yorum yapmaz. |
| Zamanlanmış Claude oturumları | Sabah brifingi, 13:12 öğle, akşam kontrolü, haftalık kurul (Cmt 11:37) | Her biri ayrı, temiz bir oturum: kendi sabit görev metniyle çalışan bir analist. |
| Bağlantılar (MCP) | TCMB EVDS | Birincil veriye doğrudan erişim |
| Köprü | Cloudflare `bist-kopru` | TradingView alarmlarını depoya taşır |

## 3. Önerilen yeni roller

| # | Rol | Nasıl çalışır | Ne zaman | Yetkisi |
|---|---|---|---|---|
| A1 | **Teyit Denetçisi** | İşi üretmemiş, ayrı bir ajan. Yalnız çıktıyı ve kaynak listesini görür. Her ✅ için kaynağı yeniden açar, her "yok" için gerçekten bakılmış mı diye kontrol eder. | Haftalık kurul raporu; her test hükmü (GEÇTİ/ELENDİ/UYUMLU); risk raporu | Okur, işaretler. Düzeltme yazmaz, "uyuşmazlık listesi" verir. |
| A2 | **Kod Gözden Geçiricisi** | Her paket teslim edilmeden önce ayrı bir ajan kodu okur: veri sızıntısı (look-ahead), boş sonuç koruması, gizli anahtar, commit döngüsü. | Her paket (paket44 ve sonrası) | Okur, bulgu listesi verir. |
| A3 | **Araştırma Kütüphanecisi** | NotebookLM bağlantınız (NB-BIST-30, NB-MAKRO, NB-SİSTEM) bu çalışma alanına bağlanırsa, çok kaynaklı ve atıflı sorular ona gider. | Komite ve derin analiz | Okur. |
| A4 | **Tarayıcı ajanı** | JavaScript ile dolan ya da oturum gerektiren sayfaları okur (TradeMaster panel ekranı dahil, yalnız okuma). | İstek üzerine | **Asla emir vermez, form göndermez.** Aracı kurum hesabında yalnız ekran okuma. |

**Bağımsızlık sınırı (açıkça):** A1 ve A2 de Claude'dur, yani aynı modelin farklı bir oturumu. Kör noktalar ortak olabilir. Bu nedenle insan denetimi (sizin panel teyidiniz) kaldırılmaz, ajan denetimi ona eklenir. Gerçek bağımsızlık kaynağı ajanlar değil, depodaki ön kayıtlı testler ve dış kütüphanelerdir (örnek: 19.11 alphalens çapraz kontrolü).

## 4. İş akışı

```
Veri (Actions, EVDS, köprü)  →  Depo (tek doğruluk kaynağı)
        ↓
Analist (zamanlanmış oturum: brifing / kurul)  →  taslak çıktı + kaynak listesi
        ↓
Teyit Denetçisi (A1, ayrı ajan)  →  uyuşmazlık listesi
        ↓
Analist uyuşmazlıkları düzeltir ya da "Teyit edilemeyenler"e taşır
        ↓
Altuğ (panel teyidi + karar)  →  karar kaydı (komite)
```

Kod tarafında: Claude paketi yazar → A2 gözden geçirir → bulgular düzeltilir → paket teslim → Altuğ commit eder → GitHub run sonucu kontrol edilir.

## 5. Kurallar

1. Hiçbir ajan push etmez, işlem yapmaz, emir vermez, gizli anahtar görmez.
2. Denetçi ajan, işi üreten ajanın gerekçesini görmez; yalnız çıktıyı ve kaynakları görür (kendi kendini notlama olmasın).
3. Denetçi bulgusu sonucu otomatik değiştirmez; analist düzeltir ya da gerekçesiyle reddeder, bu not çıktıya eklenir.
4. Brifinglerde denetçi kullanılmaz (hız ve maliyet). Brifing kalitesi `BRIFING_SABLONU.md` işaretleri ve "Teyit edilemeyenler" bölümüyle korunur.
5. Her yeni ajan önce 4 hafta deneme: yakaladığı gerçek hata sayısı ve yanlış alarm sayısı kurulda raporlanır; değer üretmeyen rol kaldırılır.

## 6. Maliyet ve risk

| Rol | Maliyet | Risk |
|---|---|---|
| A1 | Her kullanımda ikinci bir oturum kadar | Aynı model körlüğü; yanlış güven hissi |
| A2 | Paket başına bir okuma | Düşük |
| A3 | NotebookLM sunucunuz açık olmalı (Zenbook, Tailscale) | Sunucu kapalıyken erişim yok; çalışma bu duruma dayanmamalı |
| A4 | Tarayıcı oturumu | Aracı kurum ekranında yanlış tıklama riski → yalnız okuma kuralı |

## 7. Kurulum için gerekenler

| Rol | Sizden | Benden |
|---|---|---|
| A1 | Bu notun onayı | Kurul görev metnine "rapor yayımlanmadan önce bağımsız denetçi" adımı |
| A2 | Onay | Her pakette gözden geçirme notu (`PAKET_INCELEME.md`) |
| A3 | claude.ai → Bağlayıcılar: NotebookLM sunucunuzu özel bağlayıcı olarak eklemek (adres + kimlik doğrulama sizde kalır) | Yönlendirme kurallarını protokole yazmak |
| A4 | Masaüstü uygulamasında bu sohbeti bilgisayarınıza bağlamak | Okuma kurallarını protokole yazmak |
| — | Depo bağlayıcısı (`bist-veri`) claude.ai'da "yeniden bağlan" durumunda görünüyor; yeniden bağlanırsa zamanlanmış oturumlar depoyu doğrudan okuyabilir | — |

## 8. Ücretli veri bağlayıcıları (ayrı karar)

Kayıtta finansal veri pazaryerleri var (örnek: viaNexus, Financial Datasets). Türkiye CDS'i ya da BIST verisi sunup sunmadıkları **teyit edilmedi**. CDS için ücretli kaynak kararı bekliyor; bu bağlayıcılar o kararda aday olarak incelenebilir.

## 9. Önerilen karar

- A1 ve A2: 4 haftalık deneme ile başlat (hemen kurulabilir, sizden ek kurulum istemez).
- A3: NotebookLM bağlayıcısı eklenirse başlat.
- A4: İhtiyaç olduğunda, yalnız okuma kuralıyla.

Gözlem amaçlıdır, tavsiye değildir.
