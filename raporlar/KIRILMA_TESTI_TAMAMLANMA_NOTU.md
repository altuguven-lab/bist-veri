GECERLI
# kirilma_testi.py — TAMAMLANDI
17.08.2026 | Ön kayıt: ON_KAYIT_IP7.md | Etiket: ÖLÇÜM

Önceki teslimde betiğin kendi kapanış uyarısı şunu diyordu:
"K2/K3 ve faktör arındırma bu sürümde YOK". O boşluk kapandı — ve
onunla birlikte, sabah tüzüğe yazdığımız specification curve kuralının
kendi betiğimizde bulunmaması çelişkisi de.

---

## 1. EKLENENLER

| Kriter | Uygulama |
|---|---|
| **K2 — Büyüklük** | Kayma, öncesi dönemin 250 günlük kayan ortalama sapmalarının 99. yüzdeliğini aşıyor mu. Eşik serinin kendi tarihsel oynaklığından türer, dışarıdan verilmez |
| **K3 — Yapı ≠ ölçek** | S1 ve S2, GJR-GARCH koşullu volatilitesine bölünüp kırılma yeniden aranır. Kayboluyorsa bulgu "ölçek değişimi" olarak yeniden etiketlenir |
| **K4a — Faktör arındırma** | USD/TRY, VIX, EEM'e regres edilip artıklarda kırılma yeniden aranır |
| **K4b — EM plasebosu** | Zaten vardı |
| **Holm-FWER** | Seriler arası çoklu test düzeltmesi, birincil eşik %5 |
| **C.7 — Specification curve** | 5 ceza çarpanı × 3 min_boyut = 15 spesifikasyon, hepsi tek sıralı listede; kaçının 19 Mart ±60 gün penceresine düştüğü raporlanır |

Faktör verisi gelmeyen kaynak **sessizce düşürülmüyor**, "VERİ YOK"
olarak rapora yazılıyor — ön kayıt §5'in kuralı.

---

## 2. İKİ KONTROL DE KOŞULDU

**Negatif kontrol** (kırılma gömülmemiş sentetik seri): S1, S2, S4'te
kırılma yok; K3 düştü, K4a düştü, spec curve 0/15. **Betik olmayan bir
kırılmayı uydurmadı.**

**Pozitif kontrol** (19.03.2025'e seviye kayması gömülü):

| Kontrol | Sonuç |
|---|---|
| S1 kırılma | 2025-04-25, GA 2025-02-13..2025-06-13 → **K1 EVET** |
| S1 kayma | +0,531 (K2 eşiği 99p = 0,096) → **K2 EVET** |
| K3 (S1n standardize) | kırılma 2025-04-25, GA 19 Mart'ı kapsıyor → **KORUNUYOR** |
| K4a (faktör artıkları) | kırılma 2025-04-25 → **KORUNUYOR** |
| K4b (EM emsalleri) | **TEMİZ** |
| Holm | S1 ham p ≈ 0 → düzeltilmiş de anlamlı |
| Spec curve | **12/15 spesifikasyon** 19 Mart penceresinde |
| S2 (kayma gömülmemişti) | kırılma yok — doğru |

Yani batarya, gerçek bir kırılmayı beş ayrı kriterden geçirebiliyor ve
olmayanı reddediyor.

**S3'ün davranışı da doğru:** koşullu volatilite serisinde kırılma
2022-07-19'da bulundu, GA 19 Mart'ı içermiyor → K1 "hayır". Sentetik
veride volatilite kayması gömülmemişti; test onu 19 Mart'a atfetmedi.
Spec curve de 0/15 dedi. Sahte pozitif üretmiyor.

---

## 3. BU KONTROLLERİN ANLAMI VE SINIRI

Kontroller **betiğin doğru çalıştığını** gösteriyor, BIST hakkında
hiçbir şey söylemiyor. Sentetik veri benim yazdığım varsayımları
taşıyor: sabit varyans, bağımsız getiriler, temiz seviye kayması.
Gerçek seride bunların üçü de yok.

Özellikle bir konuda dürüst olmak gerek: pozitif kontrolde kırılma
19 Mart'a gömülmüşken tahmin **25 Nisan** çıktı — 25 işlem günü sonra.
Nokta tahmini kaymaya meyilli; K1'in güven aralığına bağlanmasının
sebebi tam olarak bu. Gerçek veride de nokta tahminine değil, GA'ya
bakılacak.

---

## 4. KOŞUM SIRASI — değişmedi

1. `--asama 1` → künye + gözlem + MDE (kırılma sonucu **basmaz**)
2. `ON_KAYIT_IP7.md` commit'lenir
3. `--asama 2` → tam sonuç

`ip7_kirilma_testi.yml`, aşama 2'den önce ön kayıt dosyasının depoda
olup olmadığını kontrol edip yoksa iş akışını durduruyor. Körleme kuralı
belge değil, mekanizma.

Bootstrap 1.000 tekrar × 4 seri + K3 + K4a; runner'da birkaç dakika
sürer. Testlerde 100 tekrarla koşuldu, sonuç yapısı aynı.

---

## 5. AÇIK KALANLAR

- **K5 (mekanizma)** takas kapısına bağlı — bu test hiçbir koşulda
  kompozisyon iddiasını doğrulayamaz. Rapor bunu açıkça yazıyor.
- **20 sahte tarih plasebosu** henüz yok; EM emsal plasebosu var.
  Ön kayıt §5 ikisini de istiyor. Bir sonraki ekte.
- **Sonrası-1 / Sonrası-2 kukla değişkeni** modele girmiş değil;
  şu an EBDKS ayrımı yalnız K1'in "GA 01 Eylül'ü içermemeli" şartıyla
  dolaylı taşınıyor. Yeterli değil, tamamlanmalı.

Bunlar ön kayıtta yazılı olduğu için "unutuldu" olamaz — eksik olarak
kayıtta duruyorlar.
