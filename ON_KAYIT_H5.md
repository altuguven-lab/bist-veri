# ÖN KAYIT: H5 bilanço listesiyle alarm filtresi

**Kayıt tarihi:** 28.10.2026, H5'in hiçbir sonucu görülmeden.
- Alarm karnesi ve H4 sonuçları daha önce görüldü.
- Ama alarmların H4 listelerine göre kırılımına hiç bakılmadı.

**Uygulayan betik:** `h5_alarm_filtre.py`
**Kural:**
- Bu belge betik ilk kez çalışmadan önce repoya commit edilir.
- Betik her çalışmada bu dosyanın SHA-256 parmak izini sonuca yazar.
- Her çalışma `data/h5/deneme_kaydi.json` dosyasına eklenir.

Bu belge salt ölçüm tasarımıdır. Yatırım tavsiyesi değildir. Pine koduna dokunmaz.

## İddia

V162'nin YUKARI yönlü alarmları, o tarihte geçerli bilanço listesinde İYİ üçte birde olan hisselerde, KÖTÜ üçte birde olanlara göre daha iyi sonuç verir. İYİ filtreden geçen alarmlar maliyet sonrası XU100'ü geçer.

**Dayanak:**
- Alarmlar tek başına kenar üretmedi (alarm karnesi).
- Bilanço listesi bilgi taşıyor: H4'te İYİ ile KÖTÜ arasındaki fark 40 günde +4,7, t 5,5.
- Soru: İkisi birleşince, yani filtre olarak kullanılınca, alarm kalitesi artıyor mu?

## Veri

| Konu | Tanım |
|---|---|
| Alarm olayları | `data/alarm_karne_olaylar.csv`. `yon == YUKARI` olan olaylar; karnenin tekilleştirmesi ve getirileri aynen kullanılır. `alarm_karne.TEST_IMZALARI` hariçtir. |
| Bilanço listesi | `h4_bilanco_surprizi.py` fonksiyonlarıyla (aynı S, aynı üçte birler, aynı bilgi tarihi kuralı). |
| Geçerli liste | Çeyrek (y, p) listesi, kendi giriş gününden bir sonraki çeyreğin giriş gününe kadar geçerlidir (giriş günü dahil, sonraki giriş günü hariç). |
| Sınıf | Alarmın taban günü hangi listenin geçerli dönemine düşüyorsa o listeye bakılır: İYİ, KÖTÜ ya da ORTA. Listede olmayan sembol ya da geçerli liste yoksa LİSTE_YOK. |

## Ölçüm

- **Birincil metrik:** Karnedeki `net_T3`, yani XU100'e göre net T+3 getiri (YUKARI türlerde %0,25 maliyet düşülmüş).
- **İkincil (raporlanır):** `net_T5`, `sek_rel_T3`, alarm türüne göre kırılım, aylık kırılım.
- **İstatistik:** Grup ortalaması ve taban günü kümelenmiş t (`alarm_karne.kumelenmis`).
- **Fark testi:** İYİ − KÖTÜ = ortalamalar farkı; SE = √(SE_İYİ² + SE_KÖTÜ²). Gruplar aynı günleri paylaşırsa bu SE tutucu kalır.

## Hüküm

**Ara rapor:** Her çalışmada güncellenir; hüküm vermez.

**Kesin hüküm:** 31.12.2026'ya kadar taban günü oluşan alarmlarla verilir (T+5'in olgunlaşması için 09.01.2027 sonrası ilk çalışmada). Kurallar bu tarihe kadar değişmez.

**Kesin hüküm kriterleri:**
- **YETERSİZ_ÖRNEK:** İYİ ya da KÖTÜ grubunda 30'dan az olay.
- **GEÇTİ:** Üç şartın üçü de sağlanmalı:
  - İYİ grubu net T+3 ortalaması > 0 ve kümelenmiş t > 2,0,
  - İYİ − KÖTÜ farkı > 0 ve t > 2,0,
  - İYİ grubunun net T+5 ortalaması da > 0.
- **ZAYIF:** İYİ − KÖTÜ farkı > 0 ama yukarıdakilerden biri tutmuyor.
- **ELENDİ:** İYİ − KÖTÜ farkı ≤ 0.

**GEÇTİ'nin anlamı:** Pine'da (ya da brifingde) alarm yalnızca İYİ listedeki hisselerde gösterilir, KÖTÜ listedekilerde bastırılır. Bu da önce 60 işlem günü gölgede denenir.

## Bilinen sınırlar

- **Kısa örneklem:** Temmuz 2026'dan bu yana, iki-üç çeyrek listesi. Ara rapor bu yüzden yalnızca yön gösterir.
- **Liste nokta-zaman değil:** İş Yatırım'daki bugünkü rakamlarla kuruluyor.
- **Bağımlılık:** Karne ölçümünün sınırları (kapanış bazlı giriş, tek kaynak Yahoo) aynen geçerli.
- **Ufuk farkı:** Alarm sonuçları T+3/T+5'te, liste etkisi 40–60 günde ölçülmüştü. Ufuklar farklı; filtre kısa ufukta etki göstermeyebilir.
