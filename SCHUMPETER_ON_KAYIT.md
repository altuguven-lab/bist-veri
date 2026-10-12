# SCHUMPETER GÖZLEM KATMANI — ÖN KAYIT (sürüm 1)

Tarih: 11.10.2026 · Karar mercii: Başkan (Altuğ) · Hazırlayan: Claude
Kod: `schumpeter_gozlem.py` · Workflow: `schumpeter_gozlem.yml` · Çıktı: `data/schumpeter_gozlem.json`, `schumpeter_gozlem.md`, `data/schumpeter_kap_defter.json`

## Kuluçka (İP-3) uyumu

- Bu katman SALT ÖLÇÜMDÜR. V151/V195 sinyal mantığına, Pine'a ve alarmlara DOKUNMAZ; hiçbir sinyalle birleştirilmez. Ölçüm/boru hattı kodu dondurmadan muaftır (Dönem 3 maddesi).
- Sonuçların herhangi bir sinyal kuralına dönüşmesi ayrı bir Başkan kararı ve ayrı bir ön kayıt gerektirir; bu belge bunu yetkilendirmez.

## Teorik dayanak (kısa)

Schumpeter: yenilik kümeler hâlinde gelir (yığılma), kredi bu dalgayı finanse eder, rekabet rantı eritir ve "yaratıcı yıkım" eskiyi eler. Bu belge yalnız bu fikirlerin BIST'te ölçülebilir iki vekilini sınar. Teori tanımlayıcıdır; sonuç "kenar yok" çıkarsa çürüyen teori değil, bu veri ve bu pencerede bu vekildir.

## H1 — Yığılma (sektör içi yayılma)

- Evren: ≥3 üyeli sektörler — BANKACILIK (6), HAVACILIK (3), SINAI (3), ENERJI (4), OTOMOTIV (3). Diğer sektörler dışarıda.
- RS5(hisse, t) = 5 günlük hisse getirisi − 5 günlük XU100 getirisi.
- breadth(sektör, t) = RS5 > 0 olan üye oranı.
- **Olay (yayılma başlangıcı):** breadth(t) ≥ 2/3 VE breadth(t−5) ≤ 1/3 VE sektör ortalama RS5 > 0. Aynı sektörde iki olay arası en az 10 işlem günü.
- **Sonuç ölçümü:** olaydan sonraki 5 ve 10 işlem günü için sektörün (eşit ağırlık) XU100'e göreli getirisi.
- **Karşılaştırma tabanı:** aynı ölçümün tüm günlerdeki ortalaması (kâğıt üstü olay olmayan günler dahil).
- **İstatistik:** (olay ortalaması − taban) üzerinde tek örneklem t, normal yaklaşık p (çift yönlü).
- Betimleyici ek (teste girmez): son VİOP gününde sektörde yeni long (fiyat↑, APS↑) / yeni short (fiyat↓, APS↑) sayısı.

## H2 — Yenilik yoğunluğu (KAP)

- Kaynak: `data/kap_bildirimleri.json` içindeki "Özel Durum" türü kayıtlar; KAP 45 gün sakladığı için kayıtlar `data/schumpeter_kap_defter.json` defterine eklenir (tekrarsız, disclosureIndex ile).
- **Yenilik sayılma kuralı (anahtar kelime, küçük harf):** sözleşme, yatırım (yatırımcı hariç), kapasite, sipariş, ihracat, tesis, proje, mutabakat zaptı, ortak girişim, satın alma, ihale ilanı/sonucu, "yeni ". **Dışlama:** iptal, alacak, geri alım, trafik, bağımsız yönetim, rekabet kurulu, mahkeme, basında yer alan, finans başkanı/CFO, eurobond, rıza talebi, ruhsat, yatırımcılarımız.
- Sektör yenilik yoğunluğu = son 20 takvim gününde yenilik olayı sayısı. **Olay:** sayı ≥ 2 olduğu gün (aynı sektörde en az 20 işlem günü arayla).
- **Sonuç:** olaydan sonraki 10 ve 20 işlem günü sektör göreli getirisi, taban: aynı sektörün tüm günleri.
- **Bilinen zayıflık:** anahtar kelime sınıflandırıcı kabadır (GYO sektörü tek hisse EKGYO'nun ihale/sözleşme bildirimleriyle şişer). Sınıflandırıcı sonuçlara bakıldıktan sonra DEĞİŞTİRİLEMEZ.

## Ortak kurallar

- **Teyit olayı:** ön kayıt tarihinden (11.10.2026) sonraki olay. Önceki olaylar KEŞİFSELDİR, verdikt taşımaz.
- **Alfa:** 0,05 / 4 = **0,0125** (dört hipotezlik aile: H1–H4; H3/H4 henüz kodlanmadı, alfa payı ayrıldı).
- **Minimum örnek:** teyit olayı ≥ 30 olmadan verdikt "ÖRNEK YETERSİZ".
- **Verdikt:** p < 0,0125 → ANLAMLI; aksi → KENAR YOK (anlamsız). "Kenar yok" ≠ "zarar var".
- **Değişiklik kuralı:** tanım/eşik/anahtar listesi değişirse `ON_KAYIT_SURUMU` artar; önceki sonuçlar "eski tanım" diye etiketlenir ve yeni sürümün teyit sayacı sıfırdan başlar.
- **Örnek büyüklüğü beklentisi:** H1 sektör başına haftada en fazla birkaç olay üretir; 30 teyit olayı aylar alabilir. H2 defter yeni olduğundan 30 olay için çok daha uzun sürer. Bu normaldir; erken yorum yapılmaz.

## Durdurma ve yayma kuralları

- 26 hafta sonunda (≈ 11.04.2027) her iki hipotez hâlâ ÖRNEK YETERSİZ ise katman sonlandırılır veya sürüm 2 ile yeniden tanımlanır.
- Herhangi bir sonucun sinyal kuralına dönüşmesi için: (a) teyit olayı ≥ 30, (b) p < 0,0125, (c) etki işlem maliyeti sonrası pozitif, (d) Başkan kararı + ayrı ön kayıt.

## Açık iş

- H3 (kâr sürprizi sonrası rant erimesi) ve H4 (kredi ivmesi → banka göreli performansı) için ayrı ön kayıt, veri kaynakları netleşince yazılacaktır (H4 için TCMB/BDDK haftalık kredi serisi gerekir).
