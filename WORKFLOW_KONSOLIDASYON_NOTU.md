# Workflow Konsolidasyonu ve Harici Tetikleyici (28.08.2026)

## Neden

28.08 sabahi fiyat (`bist_quotes.json`) ve haber (`haber_akisi.json`)
kanallari seans icinde saatlerce (sirasiyla ~18 ve ~7 saat) guncellenmedi.
`saglik_kontrol.py` bunu dogru tespit etti; workflow'lar devre disi
degildi, kod da hata vermiyordu — Actions calisma gecmisi incelendiginde
(`Haber Akisi Guncelle` #532-#538) zamanli tetiklemeler arasindaki
gecikme **94 dakikadan baslayip 10 saate kadar buyuyen** bir orkuntu
gosterdi. Bu, GitHub'in kendi belgeledigi bir davranis: bir depoda
zamanli (`schedule:`) is yuku yuksekse, tetiklemeler sessizce
ertelenip atlanabiliyor.

Depo taranınca **24 ayri workflow dosyasinin** `schedule:` ile
tetiklendigi ve bircogunun **ayni dakikada** cakistigi goruldu:

| Saat (UTC) | Cakisan workflow'lar |
|---|---|
| 06:35 hafta ici | fetch_sektor, fetch_viop, kuresel_asya, portfoy_risk, saglik_kontrol (**5'li**) |
| 07:00 Pazartesi | geri_donus_adaylari, tcmb_evds_veri |
| 07:15 Pazartesi | kazanc_surprizi_reversal, makro_guncel_durum |
| 11:35 hafta ici | portfoy_risk, saglik_kontrol |
| 15:30 Cuma | rsi_gozlem, retro_firsat |
| 15:45 Cuma | sinyal_arsiv_gunluk, hafta_denetim |

Bunun ustune `update.yml` (gunde 18 kez) ve `haber_update.yml` (gunde
24 kez) en yuksek frekansli iki workflow — toplam zamanli tetikleme
hacminin buyuk kismini bunlar olusturuyor.

## Yapilan degisiklik (iki yonlu)

**1) Konsolidasyon** — cakisan/ilgili workflow'lar tek dosyada
birlestirildi, GitHub'a giden ayri `schedule:` kaydi sayisi **24 -> 12**'ye
dustu (bkz. `SIL_BU_DOSYALARI.txt`). Onemli detay: bazi workflow'lar
arasinda kod yorumlarinda ACIKCA belirtilmis GERCEK veri bagimliligi
vardi (ör. "kazanc_surprizi_reversal, geri_donus_adaylari'dan 15dk
sonra, onun ciktisini okumak icin") — bunlar eskiden sadece wall-clock
(saat farki) ile saglaniyordu, ki tam da bunun guvenilmez oldugu
kanitlandi. Yeni dosyalarda bu siralar `needs:` ile GERCEKTEN garanti
edildi (bir adim, onceki adimin commit'i dahil bitmeden baslamiyor):

- `pazartesi_paketi.yml`: geri_donus_adaylari -> kazanc_surprizi_reversal -> kazanc_reversal_izleme
- `hafta_kapanisi.yml`: retro_firsat -> hafta_denetim
- `makro_guncel_durum.yml`: artik `workflow_run` ile tcmb_evds_veri.yml'nin BITISINE bagli (saate degil, olaya bagli), ve sadece Pazartesi calisiyor
- `kuresel_gosterge.yml`: ayni script (fetch_kuresel.py), 3 bolge, tek dosya, `github.event.schedule` ile hangi bolgenin calisacagi seciliyor
- `sabah_veri_paketi.yml`, `risk_ve_saglik_paketi.yml`, `seans_kapanisi.yml`: aralarinda stated bagimlilik olmayan islerin PARALEL birlestirilmesi (tek kaynak hatasinda cokmeme ilkesi korundu — her biri ayri job)

**2) Harici tetikleyici** — en kritik ve en sik ihtiyac duyulan iki
kanal (`update.yml`, `haber_update.yml`) artik GitHub'in `schedule:`
tetikleyicisini HIC kullanmiyor; `repository_dispatch` event'ine
gecti. Bu event GitHub'in "olabilirse calistiririm" zamanlayicisindan
GECMIYOR — API cagrisi geldigi anda calisiyor. Saat garantisi icin dis
bir servisin bu API'yi cagirmasi gerekiyor (asagida).

## Harici tetikleyici kurulumu (elle yapilmasi gereken tek adim)

Bu adimi ben yapamam — GitHub kimlik bilgisi (PAT) olusturmak guvenlik
acisindan sadece sizin yapabileceginiz bir islem.

1. **Token olustur**: GitHub -> sag ustte profil -> Settings ->
   Developer settings -> Personal access tokens -> Fine-grained tokens
   -> "Generate new token". Repository access: sadece `bist-veri`.
   Permissions: **Contents: Read and write**, **Actions: Read and write**.
   Token'i bir yere guvenli kaydedin (bir daha gosterilmiyor).

2. **Ucretsiz bir dis cron servisi secin** (ör. cron-job.org, ucretsiz
   hesap yeterli — dakika hassasiyetinde, GitHub'in ic zamanlayicisindan
   bagimsiz calisir).

3. Her biri icin bir "cronjob" tanimlayin, HTTP POST:
   - URL: `https://api.github.com/repos/altuguven-lab/bist-veri/dispatches`
   - Header: `Authorization: Bearer <TOKEN>`
   - Header: `Accept: application/vnd.github+json`
   - Header: `Content-Type: application/json`
   - Body (fiyat kanali icin, 07:04-15:34 arasi 30dk'da bir, hafta ici):
     `{"event_type": "bist_veri_tetikle"}`
   - Body (haber kanali icin, saatte bir, her gun):
     `{"event_type": "haber_tetikle"}`

4. cron-job.org'da zamanlama dogrudan cron ifadesiyle girilebiliyor —
   fiyat icin `4,34 7-15 * * 1-5`, haber icin `13 * * * *` (ayni saatler,
   sadece tetikleyen taraf artik GitHub degil).

Bu kurulumdan sonra `update.yml` ve `haber_update.yml`'de "Run workflow"
butonuyla elle de tetikleyebilirsiniz (workflow_dispatch hala acik) —
dis servis kurulana kadar GEÇICI olarak elle/mevcut sekilde
calistirmaya devam edebilirsiniz, hicbir veri kaybi olmaz.

## Uygulama sirasi

1. Bu klasordeki `.github/workflows/*.yml` dosyalarini depoya kopyalayin
   (ayni isimdeki `makro_guncel_durum.yml`, `update.yml`,
   `haber_update.yml` UZERINE YAZILACAK — kalanlar yeni dosya).
2. `SIL_BU_DOSYALARI.txt`'deki 15 dosyayi silin.
3. Commit + push edin.
4. Yukaridaki harici tetikleyici adimini tamamlayin (ideal olarak ayni
   gun) — o adim bitene kadar fiyat/haber kanali sadece elle
   (`workflow_dispatch`) veya (kurmazsaniz) hic tetiklenmez, bu yuzden
   1-3 tamamlaninca 4'u ERTELEMEYIN.
5. Ertesi gun Actions sekmesinden yeni paket workflow'larinin (ozellikle
   `Sabah Veri Paketi`, `Risk ve Saglik Paketi`) beklenen saatte
   calistigini dogrulayin.

## Kapsam disi / dokunulmayan

Bu degisiklik SADECE workflow zamanlama/dagitim altyapisi — hicbir
Python script'inin ic mantigi, hicbir Pine/sinyal kurali degismedi.
Kulucka Protokolu'nun donma maddesi sinyal mantigini kapsiyor, bu
degisiklik onun disinda.
