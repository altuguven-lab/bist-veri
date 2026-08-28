# DALGA 2 — TAM TESLİM
20.08.2026 | C3 + atomik yazım yaygınlaştırma + mükerrer temizlik

---

## Bir hata yaptım, düzelttim — kayda geçsin

`fetch_bist.py` ve `fetch_news.py`'yi iki ayrı adımda yamaladım (önce
`universe.yml` bağlantısı, sonra atomik yazım) ve ikisini birleştirirken
yanlış bir `cp` komutu C3'ün temiz çıktısının üzerine atomik-yazım-only
sürümü yazdı — universe bağlantısı sessizce kayboldu. Kendi doğrulama
adımım (`assert 'from universe' in s`) bunu hemen yakaladı ve iki
dosyayı da **orijinal depo kaynağından** yeniden, iki yamayı tek geçişte
uygulayarak ürettim. Şu anki teslim ikisini de doğrulanmış halde taşıyor.

Bunu saklamıyorum çünkü tam olarak bu yüzden "birleştirmeden önce
doğrula" diye bir adım var — ve işe yaradı.

---

## 1. C3 + atomik yazım — birleşik, test edilmiş

`fetch_bist.py` ve `fetch_news.py` artık:
- `config/universe.yml`'den evreni okuyor (C3)
- `atomik_json_yaz()` ile yazıyor (mimari inceleme bulgu 3)

**Uçtan uca test edildi** (pandas tabanlı sahte `yfinance` ile):
`fetch_bist.py` gerçek `config/universe.yml`'den 30/30 sembolü çekti,
`data/bist_quotes.json` ve `data/bist_intraday.json`'ı atomik yazımla
üretti. `fetch_news.py`'nin evren yükleme kısmı da aynı şekilde
doğrulandı; ağa bağlı kısmı bu ortamda koşulamadı ama statik olarak
`atomik_json_yaz(DOSYA, cikti)` çağrısının tek ve doğru yerde olduğu
teyit edildi.

`portfoy_risk_kontrol.py` tek başına atomik yazıma geçirildi (evren
kullanmıyor), sözdizimi doğrulandı.

---

## 2. Mükerrer dosyalar — ayrı belgede (MUKERRER_TEMIZLIK_2026-08-20.md)

İki çift kanıtlandı ve silinebilir (`sinyal_arsiv_gunluk_v2.py`,
`# SENIOR_ENGINEER_AGENT.md`). İki çift (supertrend/momentum, aynı
SHA'lı workflow'lar) GitHub API kotası dolu olduğu için doğrulanamadı —
kanıtsız silme talimatı verilmedi.

---

## COMMIT SIRASI (bu dosyaların hepsi için, tek sıra)

1. `universe.py` (yeni)
2. `requirements.txt` (PyYAML eklendi)
3. `.github/workflows/haber_update.yml` (PyYAML eklendi)
4. `fetch_bist.py`, `fetch_news.py`, `portfoy_risk_kontrol.py`
5. `git rm sinyal_arsiv_gunluk_v2.py`
6. `git rm "# SENIOR_ENGINEER_AGENT.md"`

`config/universe.yml`'e dokunulmuyor — zaten depoda doğru haliyle var.

1-3, 4'ten önce gelmezse bir sonraki workflow koşusu
`ModuleNotFoundError: yaml` ile çöker.

---

## Doğrulama

İlk `update.yml` ve `haber_update.yml` koşularında:
- `data/bist_quotes.json` yine 30/30 sembol içermeli
- `data/haber_akisi.json` üretilmeli, hata vermemeli
- Her iki dosyanın da yazılma anında geçici `.tmp` dosyası kalmamalı
  (repo'da görünmemeli — `atomik_json_yaz` bunu garanti ediyor)

Evren değişikliği (sembol ekleme/çıkarma) bundan sonra **tek dosyada**
yapılır: `config/universe.yml`.

---

## Kalan Dalga 2/3 maddeleri

- Mükerrer çiftlerin doğrulanamayan ikisi (Altuğ'un GitHub arayüzünden
  bakması gerekiyor)
- Rapor durum etiketleri + `raporlar/` klasörü (Dalga 3)
- README'yi gerçek cron'larla eşitleme (Dalga 3)
- `pSkorTaban` okuması — 30 grafikte tek tek bakılacak, kod işi değil
