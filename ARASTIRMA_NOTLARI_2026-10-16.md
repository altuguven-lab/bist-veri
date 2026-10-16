# ARAŞTIRMA NOTLARI — 16.10.2026 (sonraki araştırmalar için kayıt)
Gözlem ve sistem kontrolüdür, yatırım tavsiyesi değildir. Kaynak: Altuğ + Claude oturumu, 15–16.10.2026. Etiketler: [DOĞRULANDI] / [KEŞİF] / [DOĞRULANMADI].

## 1. Pine sürüm durumu
- V162.2: ölü kod temizliği (request.security 14→13). AKBNK ve ASELS panelleri, pozisyon kutusu ve VIOP sembolü hizalanınca birebir aynı [DOĞRULANDI]. İlk farkın nedeni eski `KCHOL1!` sembolüydü.
- V162.3: yalnız görüntü değişikliği (SHPF/PF "N/A", PORT K1..K4, pozisyon %, MODEL/MALIYET YOK). Karar mantığı ve alarm/plot/security sayıları değişmedi (22/24/16).
- V162.3S: V162.3 + `f_tickerSectorIndex` (hisse bazlı sektör endeksi: ASTOR→XMESY, ASELS→XUTEK, SISE→XTAST, TRMET→XMADN, BIMAS/MGROS/SOKM→XPTIC, TUPRS/PETKM→XKMYA, ALARK→XHOLD, ULKER/AEFES→XGIDA). **Kararı değiştirir** (rsSector/KGS/entryScore). Ayrı gösterge olarak ~1 hafta karşılaştırılacak (ASTOR, ASELS, TUPRS, BIMAS). XPTIC'in TradingView'da varlığı [DOĞRULANMADI] (`BIST:XPTIC`); SOKM→XPTIC eşlemesi Claude eklemesidir, repo onaylı haritasında yok.
- Dosyalar: `pine_adaylar/`.

## 2. Önceden kayıtlı kurallar / hipotezler
- Ölü sinyal kuralı: n≥250, T+3 ort.<0, t<−1,96 → TERS SİNYAL. ACIL_CIK/POZ_AZALT için n≥40 ve t≥+1,96. H-A (sektör kırılımı, P3_SKOR_AL) keşif düzeyinde.
- **H-R (yeni, keşif):** P3 alarm başarısı XU100'ün 200g ortalamasının altında/üstünde farklı mı? Her hücrede n≥100 ve |t|>1,96 olmadan mantık değişmez.
- Pozisyon kapısı (`_v112Open`) kararı, bastırılan alarm sayacı çıkana kadar bekliyor.

## 3. Kendi arşivimizden gözlem (keşif)
- 17.09 öncesi n=266: göreli T+3 −%0,18. 17.09 sonrası n=122: göreli −%0,83, mutlak −%2,10, piyasa −%1,27.
- t≈−2,7 üst üste binen pencereler yüzünden şişkin; kanıt değil, hipotez üretir.

## 4. Piyasa bağlamı (Fintables / Ali Cenk Gözen grafikleri)
- BIST 100 TL 12.118,29 vs 200g ort. 13.615,62; USD cinsi 245,32 vs 297,26.
- Zirveden düşüş: TL −%19,9, USD −%27,8; 2026 düşüşü −%21,1 (zirve 11.05.2026, geçici dip 30.09.2026), 107 seans.
- 100g altında 22 seans, 200g altında 19 seans. Tamamlanan 6 dönem: düşüş −%15,3…−%31,8; toparlanma 77–489 seans; dip sonrası hacim 4/6 dönemde arttı.
- Dashboard "Piyasa bağlamı" kartları: `data/baglam_durum.json`, `data/baglam_donem.json`. Yorum: bağlam bilgisidir, sinyal değildir.

## 5. 16.10.2026 brifing özeti (10:13)
- Kospi −%7,57 (5.554, devre kesici), Nikkei −%4,90 (64.426): ABD Eylül TÜFE %3,7 (beklenti %3,6), Fed faiz artışı endişesi. Avrupa yükseliş, ABD gün içi toparladı.
- BIST 100 14.10 kapanış: 12.133,79 (BloombergHT) vs 12.118,29 (Fintables) — **fark çözülmedi**; 15.10 kapanışı bulunamadı.
- USDTRY 49,39; altın ~4.084 $/ons; Brent ~105,85.
- Takvim: PPK 22.10, FOMC 28.10, Akbank 3Ç26 27.10.
- TR TÜFE Eylül: aylık %1,84, yıllık %29,73 (Kasım 2021'den beri ilk kez %30 altı).
- SPK fon krizi (17.09'dan beri): 7 portföy yönetim şirketi, ~130 fon.
- 15.10 alarmlar: GARAN P2_ADAY/P3_RADAR, EKGYO P3_RADAR, ASTOR ACIL_CIK, ISCTR P2_DIP_DONUS.
- Jeopolitik güncel sürücü [DOĞRULANMADI]. AKBNK pozisyon −%12,5 (portföy dosyası bayat).

## 6. Sistem kontrolleri
- SQZ push yarışı düzeltildi (5 denemeli `git pull --rebase`), SQZ geçti.
- Risk ve Sağlık kırmızı. FIYAT/HABER (#7/#8, 31.08'den beri): GitHub schedule atlıyor → harici tetikleyici (Pipedream `repository_dispatch`) gerekli.
- Seans Kapanışı: `sinyal_arsiv_gunluk.py` pazartesi hatası (28.09, 05.10, 12.10); run 38317079687 logu alınamadı, neden bilinmiyor.
- Pipedream 685 çağrı / eşik 2.500. `portfoy.json` 26.08'den beri bayat.

## 7. Açık işler
1. Fiyat/Haber harici tetikleyici. 2. Pazartesi hatası logu. 3. Sektör haritası ve pozisyon kapısı kararları. 4. H-R testi, bastırılan alarm sayacı. 5. PPK 22.10 sonrası POLITIKA_FAIZI; Akbank 27.10. 6. `portfoy.json` güncelle. 7. P3_KAPANIS_GOLGE Python gölge ölçümü. 8. Banka takipteki alacak/SYR kaynaklarını doğrula.
