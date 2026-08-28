GECERLI
# TARİH YAMASI + TETİKLEME LİSTESİ
17.08.2026 | Etiket: ALTYAPI/BELGE — Pine'a dokunmuyor

---

## 1. YAMA — dört yerde eski tarih vardı

### a) `hafta_denetim.py` → `hafta_denetim_YAMALI.py`

`KULUCKA_BASI` hâlâ **07.07.2026**'ydı. Bu yalnız sayaç hatası değildi:
sabit beş yerde kullanılıyor — sinyal filtresi, fiyat serisi başlangıcı,
seri filtresi, gün sayacı ve rapor metni. Yani **metrikler eski mantıkla
üretilmiş 07.07–07.08 sinyallerini de içeriyordu.** M1/M2 karışık dönem
ölçüyordu; W33'teki "39/42" bunun yalnız görünen yüzüydü.

Yapılan:
- `KULUCKA_BASI = 2026-08-08` (sayaç sıfırlama tarihi)
- `KALIBRASYON_BASI = 2026-07-07` — 07.07–07.08 arası artık açıkça
  "kalibrasyon dönemi", metriklere girmiyor ama rapor bunu **yazıyor**
- Rapor başlığındaki `/42` ve metindeki `07.07'den beri` artık
  sabitlerden türetiliyor, elle yazılmıyor. Çürümenin sebebi tam olarak
  hardcoded tarihti.

### b) `gunluk_gozlem_cetveli.py` → `..._YAMALI.py`

İki yerde "18.08.2026'ya kadar" → **19.09.2026**. Bu betik
`gunluk_gozlem_cetveli.json`'daki `kulucka_notu` alanını üretiyor;
JSON'u elle düzeltmek işe yaramazdı, bir sonraki koşuda geri gelirdi.

### c) `RISK_KURALLARI.md` — elle düzeltilecek

Bölüm başlığındaki `KULUÇKA MODU (18.08.2026'ya kadar)` →
`KULUÇKA MODU (19.09.2026'ya kadar)`.

### d) `SURUM_NOTLARI.md` — elle eklenecek

Dosya 13.07'de kesiliyor. 08.08 sayaç sıfırlaması ve V157 düzeltmesi
(P3_SKOR_AL 30→40, POZ_AZALT OR→AND) işlenmemiş. Protokol bunların
"gerekçesiyle SURUM_NOTLARI'ye işlenmesini" şart koşuyor.

---

## 2. YAMA SIRASINDA ÇIKAN TUTARSIZLIK — protokolde bir gün hatası var

`KULUCKA_PROTOKOLU.md` hem **"42 gün"** hem **"19.09.2026"** diyor.
Ama 08.08 + 42 gün = **18.09**. Bir günlük fark var.

Bunu sessizce seçmedim. Betikte otoriter kabul edilen **bitiş tarihi**
(hüküm günü takvimde sabit); gün sayısı ondan türetiliyor:

```
KULUCKA_BITIS = 2026-09-19
KULUCKA_GUN_SAYISI = 43        # turetildi, elle yazilmadi
17.08 sayaci = 10/43
```

Yani W33'te söylediğim "doğrusu 9/42" da tam doğru değilmiş —
protokolün kendi bitiş tarihine göre **10/43**. Tutarsızlığın protokol
metninde de kapatılması gerekiyor: ya bitiş 18.09'a çekilir ya "42 gün"
ifadesi 43 yapılır. Kurul kararı senin.

---

## 3. ELLE TETİKLEYECEKLERİN — sırayla

Otomatik koşanlar (dokunma): `sinyal_arsiv_gunluk.yml` ve
`hafta_denetim.yml` zaten 15:45 UTC cron'unda; yamalı sürümleri
commit'lersen bu akşamki koşuda kendiliğinden devreye girer.

**Elle tetiklenecek dört iş:**

| # | Workflow | Girdi | Ne için |
|---|---|---|---|
| 1 | **Haber Kanalı Teşhisi** | `kaynak` boş | Yamalı betik artık `gurultu_kalip_dagilimi` yazıyor — hangi gürültü kalıbının %67'yi elediğini görmek için. `fetch_news.py` düzeltmesi buna bağlı |
| 2 | **IP-7 Kırılma Testi** | `asama: 1` | Künye + MDE. Kırılma sonucu **basmaz** |
| 3 | *(commit)* | — | `ON_KAYIT_IP7.md` depoya girer — aşama 2'nin ön şartı |
| 4 | **IP-7 Kırılma Testi** | `asama: 2` | Tam sonuç. Ön kayıt commit'i yoksa workflow kendini durdurur |
| 5 | **Gece Gündüz Ölçümü** | `donem: 5y` | Sansür yaması sonrası tekrar — B3 |
| 6 | **Gece Gündüz Ölçümü** | `donem: 2y` | Rejim duyarlılığı: gece primi 2021-23 melt-up'a mı ait |

**Sıra önemli olan tek yer 2→3→4.** Diğerleri paralel koşabilir.

**İsteğe bağlı ama faydalı:** `Sinyal Dogrulama Arsivi` workflow'unu
elle bir kez tetiklemek — v2.1 migrasyonunun (işlem günü penceresi +
piyasa referansı) gerçek veride çalıştığını akşamı beklemeden görürsün.
Bakılacaklar: `piyasa_referansi` alanı `XU100.IS` mi `YOK` mu, "eski
kayıt yeniden hesaplandı" satırı, ve `_uyari` alanının **oluşmaması**.

---

## 4. SENDE KALAN İKİ İŞ (workflow değil)

- **TradingView:** P3_SKOR_AL alarmlarına GUNLUK_OZET mesaj şablonu +
  Düzenle→Kaydet turu; DMLKT hayalet alarmını sil; ENJSA alarmını
  kontrol et.
- **TAVHL:** stop yenilemesi + İHLAL-2 tutanağı. Sabahtan beri açık,
  ve konsantrasyon ihlali kararı da bekliyor.
