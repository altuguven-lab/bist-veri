# M3 / ŞEMA KOPUKLUĞU DÜZELTMESİ
24.08.2026 | Etiket: ALTYAPI | Pine'a dokunmuyor, kuluçka sayacını yakmıyor

---

## Üç dosya, tek kök neden

C2 (işlem günlüğü reformu, 20.08) defterin **doğruluğunu** çözdü ama
onu **okuyan** iki yeri güncellemeyi atladım. Bu, `saglik_kontrol.yml`
tarafından benden üç gün önce (21.08, Issue #5) otomatik yakalanmıştı;
ben dün fark ettim.

### 1. `hafta_denetim.py` — `m3()`

`d.get("islemler", [])` okuyordu, v4 defter `"olaylar"` kullanıyor.
Artık `olaylar`'ı okuyup yalnız `tip in ("ALIS", "SATIS")` olanları
sayıyor — `ACILIS_BAKIYESI`, `NAKIT_MUTABAKAT`, `STOP_GUNCELLEME` gibi
işlem olmayan kayıtlar M3'e karışmıyor.

**Gerçek veriyle test edildi:** artık "VERİ YOK" demiyor, 2 işlem
buluyor (`MANUEL_ALIM` ve etiketsiz), `sinyalli_oran: 0.0` dönüyor —
bu doğru: iki işlemin de sistemin ürettiği bir sinyale bağlı olduğu
işaretlenmemiş. Sahte bir "geçti" üretmiyor, gerçek durumu yansıtıyor.

### 2. `saglik_kontrol.py` — şema doğrulayıcı

Aynı sebep, aynı düzeltme: `("islemler", list)` → `("olaylar", list)`.

**Gerçek dosyalarla test edildi:** şema kontrolünü izole çalıştırdım,
**sıfır arıza** döndü. Issue #5'in kapanması gereken koşul artık
sağlanıyor — bir sonraki `saglik_kontrol.yml` koşusunda kendiliğinden
kapanmalı (ya da elle kapatılabilir).

### 3. `portfoy_turet.py` — alan adı geri düzeltmesi

Bunu ararken üçüncü bir kopukluk buldum: `RISK_KURALLARI.md` Bölüm 7
"Denetim ve veri sözleşmesi" `portfoy.json`'da `baslangic_sermaye_tl`
adını **denetim sözleşmesi** olarak sabitliyor, `saglik_kontrol.py` da
onu bu adla arıyor. Ben 19-20.08'de bu alanı `getiri_tabani_tl` olarak
yeniden adlandırmıştım — anlamı doğru gerekçeyle (muhasebe kimliği
değil, getiri ölçüm tabanı) ama isim governance belgesindeki
sözleşmeyi bozuyordu.

**Düzeltme yönü:** governance belgesine dokunmak yerine, çıktı alan
adını sözleşmeye geri uydurdum. Kaynak veri (`islem_gunlugu.json`'daki
`_getiri_tabani` bloğu) değişmedi — sadece `portfoy_turet.py`'nin
**ürettiği** `portfoy.json`'daki anahtar adı `baslangic_sermaye_tl`'ye
döndü. Anlam açıklaması (`_baslangic_sermaye_notu`) korundu, hâlâ
"muhasebe kimliği değildir" diyor — isim eskisi, uyarı duruyor.

**Gerçek veriyle test edildi:** `--yaz` ile çalıştırıp üretilen
`portfoy.json`'u `saglik_kontrol.py`'nin şema kuralına karşı test
ettim — üç alan da (`acik_pozisyonlar`, `baslangic_sermaye_tl`,
`nakit_tl`) doğru tipte mevcut, sıfır arıza.

---

## Bu arada `portfoy.json` gerçekten yazıldı

Test sürecinde `portfoy_turet.py --yaz`'ı gerçek `islem_gunlugu.json`
ile çalıştırdım. Üretilen dosya:

- 4 açık pozisyon (AKBNK, KCHOL, TAVHL, YKBNK) — **stop seviyesi yok**,
  bu beklenen ve raporda uyarı olarak çıkıyor (henüz `STOP_GUNCELLEME`
  olayı girilmedi)
- Nakit 618.750 TL, 11 gün önce raporlanmış
- Nakit kontrolü hâlâ "YAPILAMADI" — tek `NAKIT_MUTABAKAT` var, en az
  iki gerekiyor (18-19.08'de belgelediğimiz tasarım, değişmedi)

Bu benim test ortamımdaki çıktı, depoya commit'lenmedi. Sen
`--yaz`'ı gerçek depoda çalıştırdığında aynı sonucu alacaksın — ve
o an stop seviyelerinin eksikliği ile nakit kontrolünün eksikliği
gerçek uyarılar olarak görünecek. İkisi de bilinen, açık maddeler.

---

## Sıra

1. Üç dosyayı commit'le (`hafta_denetim.py`, `saglik_kontrol.py`,
   `portfoy_turet.py`)
2. `portfoy_turet.py --yaz`'ı gerçek depoda çalıştır — `portfoy.json`
   ilk kez v4 defterden türetilmiş olarak yazılacak
3. Bir sonraki `hafta_denetim.yml` koşusunda M3'ün gerçek bir sayı
   döndürdüğünü doğrula (artık "VERİ YOK" demeyecek)
4. Issue #5'in bir sonraki `saglik_kontrol.yml` koşusunda kapanıp
   kapanmadığını kontrol et
