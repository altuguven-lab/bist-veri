# Brifing şablonu (18.11.2026)

**Neden:** 18.11 sabah brifinginde açılmamış kaynaklar için "yeni duyuru görmedim" yazıldı. Sonradan Takasbank'ın 12.11 VİOP risk parametresi güncellemesi ile 16.11 tarihli SPK bülteni 2026/81'in atlandığı görüldü. Bu şablon, kontrol edilmemiş bir şeyin "yok" diye yazılmasını önler.

## Teyit işaretleri

Brifingteki her bilgi satırı şu işaretlerden birini taşır:

| İşaret | Anlamı | Ne yazılır |
|---|---|---|
| ✅ | Birincil kaynak açıldı (kurumun kendi sayfası, KAP, PDF) | Bağlantı ve kaynağın kendi tarihi |
| ◐ | İkincil kaynak (haber sitesi) | Sitenin adı; "birincil teyit bekliyor" |
| ✖ | Bakılmadı, açılamadı ya da kaynak bayat | "Kontrol edilemedi". **"Yok" ya da "görmedim" yazılmaz.** |

Hafızadan tarih, saat ya da sayı yazılmaz. Takvimdeki olaylar `data/takvim.json`'dan alınır. Orada `teyit` alanı "birincil" olmayan olay "saat/tarih teyitsiz" diye yazılır.

## Sıra

1. **Kurum kümesi:** `data/kurum_kumesi.json`. Son 14 günde 5 ve daha fazla hisseyi kapsayan kurum kümeleri.
2. **Kurum taraması:** `data/kurum_taramasi.json` / `.md`.
   - Kaynak durum tablosu olduğu gibi verilir: SPK bülteni, Takasbank, TSPB, BIST, KAP arşivi.
   - Durumu OK olmayan kaynak için ✖ kullanılır ve brifingi hazırlayan o kaynağı elle açmayı dener. Açarsa ✅ ve bağlantı verilir.
   - SPK'nın son bülteni: numarası, tarihi, karar türleri. Bültende adı geçmek, ilgili şirket hakkında bir hüküm değildir.
   - KAP kurum bildirimleri arasında [KRİTİK] olanlar, izleme listesi eşleşmeleri ve izlenen kodlardaki devre kesici sayımı.
3. **Sistem kontrolleri:**
   - Kapsama (`gunluk_ozet_kapsama.json`)
   - Köprü (Cloudflare logu ve "TV sinyal: CF" commit'leri)
   - Karne ve H14
   - V195 ve IP-8
   - Sağlık sorunları (açık Issue'lar)
4. **Makro ve siyasi:** Her veri için ✅ ya da ◐. Sonucu açıklanmamış ya da bulunamamış veri ✖ olarak yazılır.
5. **Savaş ve jeopolitik:** Haberin tarihi yazılır. Bugünden eski haber "son bilinen" diye işaretlenir.
6. **Bugün izlenecekler:** Yalnızca takvimden.
7. **Teyit edilemeyenler** (bu başlık her zaman bulunur, boş olsa da yazılır):
   - Her ✖ ve ◐ satırı burada tekrar listelenir.
   - Her birine aynı gün bir kontrol saati verilir. Sonuç o saatte ayrı mesajla bildirilir.
8. Kaynaklar (markdown bağlantı) ve "Gözlem amaçlıdır, tavsiye değildir".

## Haftalık bakım (Cuma)

- `data/takvim.json`: Gelecek haftanın olayları birincil kaynaktan eklenir (Fed, TCMB, TÜİK, SPK, MSCI).
- `config/kurum_izleme.yml`: Yeni soruşturma, tasfiye ya da tedbir konuları eklenir. Yalnızca şirket adı, konu ve kod yazılır, kişi adı yazılmaz.
- `data/kurum_taramasi.md`: BAYAT ya da KAYIT_BULUNAMADI kalan kaynak varsa sayfa adresi yeniden bulunur. Adres tahmin edilmez; kurumun ana sayfasındaki bağlantı izlenir.
