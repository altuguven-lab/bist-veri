GECERLI
# C3 — TEK KAYNAK: config/universe.yml
20.08.2026 | Etiket: ALTYAPI | Sinyal mantığı değişmiyor, kuluçkayı etkilemiyor

---

## Bulgu: dosya zaten vardı, kimse okumuyordu

`config/universe.yml` depoda hazır duruyordu — doğru şema, 30 sembol,
hatta yararlı bir `fallback_symbols: {TRMET: KOZAA}` eşlemesi bile
içeriyordu. Ama `fetch_bist.py` ve `fetch_news.py` kendi
`BIST_SEMBOLLER` listelerini taşımaya devam ediyordu. Dosya var, bağlı
değildi — inceleme raporunun "elle senkronize edilen kopyalar" dediği
hâlin tam örneği.

**`config/universe.yml`'in kendisine dokunulmadı.** Sadece iki betik
ona bağlandı.

---

## Değişiklikler

**Yeni: `universe.py`.** Tek işi `config/universe.yml`'i okumak.
Kritik davranış: dosya eksik veya bozuksa **sessizce eski sabit
listeye düşmez** — hata verip durur. Sessiz düşme, "universe.yml'i
güncelleyip betiği güncellemeyi unutma" hatasını başka bir kılığa
sokardı.

**`fetch_bist.py`:** `BIST_SEMBOLLER` ve `ESKI_KOD_YEDEK` artık
`yukle_evren()`'den geliyor. Aşağı akış kodu (`for sembol in
BIST_SEMBOLLER`, `ESKI_KOD_YEDEK[sembol]`) hiç değişmedi — yalnız
kaynağı değişti.

**`fetch_news.py`:** Aynı şekilde `BIST_SEMBOLLER` `yukle_evren()`'den
geliyor. `fallback_symbols` burada kullanılmıyor (Google News sorgusu
Yahoo'ya özgü geçiş kodu ayrımına ihtiyaç duymuyor). Dosyanın başındaki
"iki dosya birlikte güncellenmeli" yorumu da güncellendi — artık doğru
değildi.

**`requirements.txt`:** `PyYAML==6.0.2` eklendi.

**`haber_update.yml`:** `pip install feedparser` → `pip install
feedparser PyYAML==6.0.2`. Tek satır.

---

## Test edildi

- İki betik de gerçek `config/universe.yml`'den 30/30 sembolü doğru
  sırayla yüklüyor
- `fetch_bist.py`: `ESKI_KOD_YEDEK == {'TRMET': 'KOZAA'}` doğrulandı
- Dosya kaldırılınca: `FileNotFoundError` — sessiz düşme yok,
  beklenen davranış
- Her iki betiğin sözdizimi `ast.parse` ile doğrulandı

---

## Commit sırası (önemli)

1. `universe.py` (yeni dosya)
2. `requirements.txt`
3. `.github/workflows/haber_update.yml`
4. `fetch_bist.py`, `fetch_news.py`

`config/universe.yml` zaten depoda — dokunmuyorsun.

3 ve 4'ü aynı anda commit etmek de olur; sıra asıl 1-2'nin 4'ten önce
gelmesinde önemli, yoksa bir sonraki `update.yml` / `haber_update.yml`
koşusu `ModuleNotFoundError: yaml` ile çöker.

---

## Doğrulama

İlk `update.yml` koşusunda log'da şunu görmelisin:

```
30 sembol yuklendi: AKBNK, YKBNK, ...
```

(bunu görmek istersen `python universe.py`'yi geçici bir adım olarak
ekleyebilirsin, ama zorunlu değil — asıl kanıt `bist_quotes.json`'da
yine 30/30 sembolün gelmesi.)

Bundan sonra evren değişikliği (sembol ekleme/çıkarma, TRALT gibi bir
sembolü resmen evrene almak) **tek dosyada** yapılır:
`config/universe.yml`.
