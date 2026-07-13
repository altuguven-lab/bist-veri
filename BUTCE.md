# KAYNAK BUTCE TABLOSU (G3.5) - Madde 6
Tarih: 10.07.2026 | Her yamada guncellenir.

| Kaynak | V151 | V195 | Limit | Durum |
|---|---|---|---|---|
| request.security cagri noktasi | 16 | 20 | - | - |
| unique request baglami | ~16 (tek sembol) | 37 (kod yorumu 299/458) | 40 | V195 %92 - YENI BAGLAM YASAK, tuple genisletme serbest |
| alertcondition | 18 | 0 | - | OK |
| plot ailesi | 38 | (tablo agirlikli) | 64 | G1 icin +5 plot -> 43/64 OK (fizibilite ONAYLI) |
| ust-duzey satir (heuristik) | 1401 | ~970 | ~? (1401 derleniyor) | izlemede |
| max_bars_back | 150 | 100 | - | optimize edilmis (kalici) |
| max_labels/lines | 100/100 | - | 500 | OK |

## Kritik notlar
1. V195 baglam butcesi 37/40: gelecek her ozellik TUPLE GENISLETME ile
   (dChg ornegindeki gibi) yapilmali; yeni request.security KIRMIZI CIZGI.
2. G1 (alarm zenginlestirme) fizibilitesi bu tabloyla teyitli: +5 gizli
   plot 43/64'e tasir, guvenli.
3. dynamic_requests=true (V195) - baglam muhasebesinde dinamik cagrilarin
   sayimi TradingView tarafinda degisebilir; buyuk ekleme oncesi test sart.
4. PLACEHOLDER PENCERESI (13.07 dersi): TradingView alarm mesajlari yalnizca
   ILK 20 plotu (plot_0..19) degistirir. Ilk 6 indeks (RG + 5 tasiyici)
   webhook icin REZERVEDIR; gorunur plot eklemeleri daima tasiyicilardan
   SONRA yapilir. Yeni tasiyici ihtiyacinda indeks kontrolu ZORUNLU.

