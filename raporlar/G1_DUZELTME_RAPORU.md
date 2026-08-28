# G1 DUZELTME RAPORU (Ters Muhendislik, 2. Tur) - 13.07.2026
Taban: canli uretim dosyasi (22 kayit) + V151/Pipedream kaynak okumasi.

## BULGULAR (kanitli)
B-1 [HATA] Plot placeholder limiti: TradingView alarm mesajlarinda yalnizca
    ILK 20 plot (plot_0..plot_19) degistirilir. G1 plotlari 38-42. sirada
    kaldi; TradingView basliklari indekse cevirdi ({{plot_38}}) ama deger
    basamadi - kayitlara ham metin dustu. KOK NEDEN: fizibilite kontrolunde
    yalniz 64 toplam limiti dogrulandi, 20'lik placeholder penceresi
    dogrulanmadi (BUTCE.md eksigi).
B-2 [BULGU] sinyal_gecmisi zaman-sirali DEGIL: es zamanli 7 GUNLUK_OZET,
    isleme-bitis sirasiyla dizilmis (PETKM 05.271 -> THYAO 06.539 ->
    DMLKT 05.729...). Tuketici tarafinda karisiklik riski.
B-3 [OLUMLU KANIT] Retry mekanizmasi gercek es-zamanli patlamada dogrulandi:
    3.5 saniyede 7 webhook, SIFIR kayip (sinyal_sayisi 22 tutarli).
B-4 [NOT] Eski format kayitlarin bir kismi skor alanlarini hic tasimiyor
    (bos degil, YOK) - tum tuketiciler eksik-anahtar toleransli olmali.

## KARARLAR
D-1 Tasiyici plot cozumu: 5 `var float` tasiyici dosyanin EN BASINDA
    (RG'den hemen sonra) tanimlanir ve plot edilir -> indeks 1-5, limit ici.
    Degerler hesap tamamlaninca atanir (`:=`). BILINEN SINIR: placeholder,
    plot cagri noktasindaki degeri bastigi icin alanlar BIR BAR gecikmeli
    olur (sinyali DOGURAN barin degerleri) - analiz icin esdeger, belgelendi.
D-2 Pipedream: gecmis her yazimda zaman_utc'ye gore (yeniden) siralanir -
    tek satir, davranis-notr netlik.
D-3 BUTCE.md'ye yeni KIRMIZI CIZGI: "Ilk 20 plot indeksi webhook tasiyicilari
    icin rezervedir; gorunur plot eklemeleri tasiyicilardan SONRA yapilir."
D-4 Birikime B10: alert() mimarisine gecis (dinamik mesaj = placeholder
    limitlerinden kalici kurtulus + sembol basina TEK alarm). Kulucka
    sonrasi degerlendirilir - alarm filosunu kokten sadelestirir ama
    katman filtrelemesinin script'e tasinmasini gerektirir.

## KULLANICI TARAFI (tek tur)
Pine yapistir-kaydet sonrasi HER alarmda: Duzenle -> Mesaj kutusunu
TAMAMEN bosalt -> kosul listesinden sinyali yeniden sec (mesaj yeni
varsayilana doner) -> Kaydet. (Eski alarmlar {{plot_38}} metnini sakladigi
icin bosaltmadan kaydetmek YETMEZ.)

## KABUL
Yarin seans icindeki ilk kayitta skor/kgs/stop/rejim/relvol alanlari SAYI
tasimali; GUNLUK_OZET setinde rejim alani 0/1/2 gelmeli (M4 baslar).

