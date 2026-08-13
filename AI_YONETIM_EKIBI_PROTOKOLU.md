# AI YÖNETİM EKİBİ PROTOKOLÜ

**Durum:** Yürürlükte
**Kapsam:** Claude bellek katmanı, NotebookLM MCP bağlantısı (4 notebook), komite süreci
**Amaç:** Token verimliliği ve hatırlama doğruluğunu korumak için üç katman arasında net yönlendirme kuralı tanımlamak. Bu protokol yeni bir teknik yapı kurmaz — mevcut üç parça arasındaki ad-hoc karar sürecini yazılı hale getirir.

---

## 1. Katmanlar ve Rolleri

| Katman | Bileşen | Ne İçin Var |
|---|---|---|
| A | Claude bellek dosyaları (`/areas`, `/topics`, `/profile`) | Süreç bilgisi, karar geçmişi, eşik takibi, kısa-orta vadeli bağlam |
| B | Claude geçmiş sohbet arama (`conversation_search` / `recent_chats`) | Belirli bir geçmiş konuşmanın veya kararın tam metnine erişim |
| C | NotebookLM (NB-BIST-30, NB-MAKRO, NB-SİSTEM, Deep Research) | Çok-kaynaklı, atıf gerektiren, büyük belge kümesi üzerinden sentez/doğrulama |
| D | Doğrudan repo/dosya erişimi (Claude Code, `bist-veri` pipeline) | Kod değişikliği, veri pipeline hata ayıklama — RAG değil |
| E | Komite süreci (örn. Kurumsal Radar Adaptasyon Komite Raporu formatı) | Mimariye dokunan öneriler için resmi karar kaydı |

---

## 2. Yönlendirme Kuralı (Routing)

Bir soru/görev geldiğinde önce şu sırayla değerlendirilir:

1. **Kod veya pipeline değişikliği mi?** → Katman D. RAG'e gitmez.
2. **"Bu kararı neden almıştık / hangi eşik neydi" tipi tek-dosyalık geçmiş bilgi mi?** → Katman A. Tek dosya okunur, NotebookLM'e gidilmez.
3. **Belirli bir geçmiş konuşmanın tam içeriği mi isteniyor?** → Katman B.
4. **Çoklu kurum/fon/sembol arasında mutabakat, sentez veya atıflı doğrulama mı gerekiyor** (ör. 30 sembol × 6 kurum × ~40 fon)? → Katman C, ilgili notebook.
5. **Mimariye dokunan, geri dönüşü zor bir öneri mi** (V151/V195 sinyal mantığına etki, yeni katman ekleme)? → Katman E. Önce komite raporu, sonra uygulama.

**Sızma kontrolü:** Katman A dosyaları büyük/çok-kaynaklı sorgu sonuçlarıyla şişirilmez — bu tip içerik Katman C'nin sorumluluğundadır. Katman C'ye basit, tek-dosyalık sorular yönlendirilmez — gereksiz gecikme ve atıf yükü yaratır.

---

## 3. Notebook Ayrımı (Katman C içi)

| Notebook | Kapsam |
|---|---|
| NB-BIST-30 | Kurumsal mutabakat, model portföy, fon sahipliği sorguları |
| NB-MAKRO | Makro senaryo, KAP açıklama sentezi |
| NB-SİSTEM | V151/V195 sistem dokümantasyonu, Kuluçka Protokolü referansları |
| Deep Research | Tek seferlik derin araştırma, protokole dahil edilmemiş konular |

Bir sorgu birden fazla notebook'u ilgilendiriyorsa, önce en dar kapsamlı notebook'tan başlanır; sonuç yetersizse bir üst notebook'a geçilir.

---

## 4. Token Verimliliği Kuralları

- **Katman A/B öncelik kuralı:** Cevap tek dosyada veya tek geçmiş konuşmada varsa, Katman C'ye hiç gidilmez.
- **API otomasyonu kurulursa** (komite rollerinin ayrı ajanlar olarak çalıştırılması gibi): sabit sistem promptu (bu protokol, Kuluçka kuralları, çalışma tarzı sözleşmesi) `cache_control` ile önbelleğe alınır; her turda yeniden gönderilmez.
- **NotebookLM sorguları** dar ve spesifik tutulur — geniş/açık uçlu sorular yerine notebook bazında hedefli soru sorulur, atıf takibi kolaylaşır ve gereksiz genişletilmiş getirme (retrieval) önlenir.
- **Bellek dosyaları** düzenli aralıklarla gözden geçirilir; eskiyen/çakışan girdiler konsolide edilir, tekrar eden günlük kayıtlar özetlenir.

---

## 5. Değişiklik ve Onay

Bu protokolün kendisinde değişiklik (yeni katman ekleme, yönlendirme sırasının değiştirilmesi) Katman E sürecinden geçer — yani resmi bir komite notu gerektirir, doğrudan uygulanmaz.

---

*Bu belge, mevcut Kuluçka Protokolü ve çalışma tarzı sözleşmesiyle çelişmez; onları tamamlar.*
