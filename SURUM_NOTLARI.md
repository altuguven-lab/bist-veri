SURUM NOTLARI
Kural: Pine, Pipedream veya script katmaninda her degisiklik buraya bir satir
olarak islenir. "Alarm" sutunu, TradingView alarmlarinin Duzenle->Kaydet
turuyla yeniden baglanmasi gerekip gerekmedigini soyler (MANTIK degisikligi =
EVET, kozmetik = HAYIR).
Tarih	Katman	Degisiklik	Alarm
06.07.2026	Pipedream	Kopru kuruldu (webhook -> GitHub tek-sinyal yazimi)	-
07.07.2026	Pipedream	Biriktirme modu: son 30 sinyal, uzerine yazma kalkti	-
07.07.2026	V151	18 alertcondition mesaji sinyal-bazli JSON sablonuna gecti	EVET (yapildi)
07.07.2026	V151	Saat-ayarli hacim tabani (_todSlotVol): U-egrisi duzeltmesi	EVET
07.07.2026	V151	Bar-ici hacim projeksiyonu (_barFrac): canli VOL okumasi	EVET
07.07.2026	V195	Evren takasi: SASA/KOZAL/DOAS -> OTKAR/TRMET/ENJSA + fundTier	-
07.07.2026	V195	Lider hucresi: WR yerine liderin gunluk % degisimi (WR tooltip'e)	-
08.07.2026	fetch_bist	Evren takasi + TRMET/KOZAA gecis yedegi	-
08.07.2026	fetch_news	Kanal 3 kuruldu; ayni gun kalibrasyon (yayin-tarihi filtresi, gurultu kaliplari, baslik tekrari onleme)	-
08.07.2026	Pipedream	Cakisma-retry (sha yarisi korumasi)	-
08.07.2026	Workflows	update/haber yml: git pull --rebase sigortasi + git add duzeltmesi	-
08.07.2026	V151	Baslik hucresine gunluk % (renkli) - kozmetik	HAYIR
08.07.2026	V195	Makro panel tiny->small + parlak etiketler - kozmetik	HAYIR
08.07.2026	Pipedream	FINAL: retry + aylik sayac + ay donumu arsivi (MAX 100)	-
08.07.2026	Yeni	saglik_kontrol.py/yml (dead man's switch), bist_intraday.json, kaynak_sagligi alani	-
08.07.2026	Belgeler	RISK_KURALLARI.md, FELAKET_RUNBOOK.md, portfoy.json, islem_gunlugu.json sablonlari	-
> Bekleyen: 08.07 aksami alarm Duzenle->Kaydet turu (07.07 hacim yamalari icin).
10.07 | fetch_news | G2 kalibrasyonu: kaynak tavanı 5 + kalıp/alan filtreleri | -
10.07 | Denetim | G3 raporları + G4 birikim (S1 çifte-eşik bulgusu B1'e kanıtla işlendi) | -
12.07 | V151+Pipedream | G1 alarm zenginleştirme (5 gizli plot, 9 alanlı webhook) — kozmetik/operasyonel, sinyal mantığı değişmedi | EVET (yapıldı)
11.07 | V151+Pipedream | G1 tamamlandı ve uçtan uca doğrulandı | EVET (yapıldı)
13.07 | V151+Pipedream | G1 düzeltme: taşıyıcı plotlar (indeks 1-5) + kronolojik sıralama | EVET (mesaj tazeleme turu
28.08 | TradingView | Altuğ'un deneme amaçlı kurduğu 5dk P3_SKOR_AL alarmı (ASELS, KCHOL, SAHOL, THYAO) silindi. Silinmeden önce sinyal_arsiv.json'a 6 kayıt düşmüştü (interval="5"): THYAO 28.08 12:10 UTC, SAHOL 28.08 11:20, KCHOL 28.08 07:10, ASELS 28.08 07:05, ASELS 27.08 08:00, THYAO 26.08 08:50. sinyal_dogrulama.py ve hafta_denetim.py interval alanına bakmıyor - bu 6 kayıt normal 15dk P3_SKOR_AL örneklemine (M7 dahil) karışmış olabilir. C.5 (veri körleme) gereği bu kayıtlar SİLİNMEDİ, sadece işaretlendi; M7/M2 tekrar koşulursa dahil/hariç tutulması bilinçli karar verilmeli. | HAYIR (deneme alarmıydı, resmi 19-alarm setine hiç girmedi, Pine kodu değişmedi)
