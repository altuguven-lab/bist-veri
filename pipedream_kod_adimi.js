// PIPEDREAM CODE ADIMI - v4 (06.10.2026)
// v3'ten fark (05.10 15:11:01 GMT "TIMEOUT" hatasi + 02.10 eksik 8 sembol):
//  KOK NEDEN (KANITLI): GitHub ayni branch'e gelen commit'leri SIRAYLA
//  isliyor (02.10 patlamasinda ~1.1 sn/commit, 26 commit +34 sn'de bitti).
//  30+ eszamanli webhook = en az ~35 sn'lik kuyruk. Pipedream adim
//  zaman asimi (varsayilan 30 sn) dolunca yurutme SESSIZCE OLUR: ne ana
//  dosya ne inbox yazilir, TradingView ise "basariyla iletildi" gorur
//  (Pipedream 200'u hemen doner). v2/v3'un rastgele gecikme + retry
//  yapisi kuyrugu kisaltamaz, sadece toplam sureyi uzatir - v3 bunu
//  KOTULESTIRMISTI (en kotu durum ~40 sn).
//  DUZELTME:
//   a) GUNLUK_OZET icin SEMBOL-SIRALI zaman dilimi (rastgele degil):
//      her sembol kendi ~1.4 sn'lik diliminde yazar -> carpisma yok,
//      kuyruk olusmaz. Diger sinyaller icin kisa rastgele gecikme.
//   b) Tum yurutme SURE BUTCESINE bagli (ZAMAN_ASIMI_MS): ana yazma
//      butceyi asmadan birakilir, inbox'a HER ZAMAN sure ayrilir.
//   c) Her HTTP cagrisina 8 sn timeout - tek takili cagri butceyi yemez.
//  *** ZORUNLU AYAR: Pipedream workflow > Settings > Execution Controls >
//  Timeout en az 120 sn olmali (ZAMAN_ASIMI_MS=110000 buna gore). Bu
//  ayar 30 sn kalirsa dilim mantigi SON sembolleri yine oldurur. ***
// ---- v3 notlari (asagida, bilgi icin) ----
// PIPEDREAM CODE ADIMI - v3 (01.10.2026)
// v2'den fark (01.11 PM 409 HATASI KOK NEDEN DUZELTMESI):
//  5. GUNLUK_OZET anindaki 30-sembollu patlamada ("suru kirici"
//     penceresi yetersiz kaliyordu) sure 0-2500ms -> 0-6000ms'ye
//     cikarildi; 30 es zamanli istek daha genis bir pencereye
//     yayilir, ana yazmanin ilk denemede basarili olma ihtimali artar.
//  6. KOK NEDEN: son care (inbox) yazmasi TEK denemeydi. GitHub
//     Contents API, AYNI BRANCH'E farkli dosya yollarina yapilan
//     es zamanli PUT'larda bile (her PUT ref HEAD'i uzerine yeni
//     commit actigindan) 409 verebiliyor. 30'luk patlamada 8 ana
//     deneme TUKENIP de inbox'un TEK denemesi de bu ikinci dalgaya
//     denk gelirse, sinyal GERCEKTEN KAYBOLUYOR ve atilan hata
//     e-postasi aslinda ana yazmanin EN SON hatasiydi (throw sonHata).
//     Duzeltme: inbox yazmasina da 3 denemelik kisa jitter'li
//     retry eklendi - sha gondermedigi icin (yeni dosya) cakisma
//     ihtimali zaten dusuk, birkac deneme pratikte yeterli.
// v2'nin orijinal notlari (hala gecerli):
//  1. Ilk okumadan ONCE rastgele gecikme (suru kirici):
//     es zamanli event ayni milisaniyede okumaya girmesin.
//  2. Deneme sayisi 3 -> 8; bekleme deterministik degil RASTGELE
//     (jitter'li ustel): kaybedenler senkronize geri donup yeniden
//     carpismasin.
//  3. Tum denemeler biterse throw YOK: son care olarak sinyal
//     data/inbox/ altina kendi benzersiz dosyasina yazilir
//     (cakismasi onceden imkansiz saniliyordu - v3'te bu da retry'landi)
//     - event asla kaybolmaz. Brifing/denetim inbox'i da okur;
//     bos kalmasi beklenir.
//  4. Tekrar-kayit korumasi: yazma basarili olup yanit kaybolduysa
//     retry ayni sinyali ikinci kez eklemesin diye 60sn penceresinde
//     ayni sembol+sinyal+fiyat varsa eklenmez.
// Sinyal isleme mantigi, ay donumu arsivi, sayac ve G1 alanlari AYNEN.
// Bu kodun aynisi repoda pipedream_kod_adimi.js olarak YEDEKLENIR.
import { axios } from "@pipedream/platform";

export default defineComponent({
  props: {
    github: { type: "app", app: "github" },
  },
  async run({ steps, $ }) {
    const OWNER = "altuguven-lab";
    const REPO = "bist-veri";
    const PATH = "data/tv_alerts_latest.json";
    const MAX_SINYAL = 100;
    const MAX_DENEME = 12;
    const BASLANGIC = Date.now();
    const ZAMAN_ASIMI_MS = 110000;  // Pipedream Timeout (>=120 sn) - 10 sn pay
    const ANA_BUTCE_MS = 75000;     // ana dosya denemeleri bu sureyi asmaz
    const INBOX_BITIS_MS = ZAMAN_ASIMI_MS - 8000;
    const HTTP_TIMEOUT_MS = 8000;
    const SEMBOL_SIRASI = ["AKBNK","YKBNK","GARAN","ISCTR","HALKB","VAKBN","KCHOL","SAHOL",
      "BIMAS","MGROS","ASELS","THYAO","PGSUS","TAVHL","TTKOM","EREGL","SISE","TRMET","TUPRS",
      "PETKM","ASTOR","ENJSA","ENKAI","EKGYO","FROTO","TOASO","OTKAR","AEFES","ALARK","ULKER","TRALT"];
    const DILIM_MS = 1400;
    const gecen = () => Date.now() - BASLANGIC;

    const bekle = (ms) => new Promise((r) => setTimeout(r, ms));

    const body = steps.trigger.event.body || {};
    const yeniSinyal = {
      zaman_utc: new Date().toISOString(),
      sembol: String(body.symbol ?? "?"),
      sinyal: String(body.signal ?? "?"),
      interval: String(body.interval ?? "?"),
      fiyat: String(body.price ?? "?"),
      skor: String(body.skor ?? "?"),
      kgs: String(body.kgs ?? "?"),
      stop: String(body.stop ?? "?"),
      rejim: String(body.rejim ?? "?"),
      relvol: String(body.relvol ?? "?"),
      // 04.08 EKI: sadece GUNLUK_OZET tasir - V151'in kendi _v112Total/_v112Wr
      // sayacini disari aktarir (kurul: "gercek sistem tarihte kac kez
      // giris verdi" sorusunu zamanla izlemek icin). Diger 17 alarmda
      // bu alanlar "?" gelir - mesaj sablonlarina eklenmedi, bilincli.
      v112n: String(body.v112n ?? "?"),
      v112wr: String(body.v112wr ?? "?"),
      // 21.09 EKI (kurul onayli, genel sistem kontrolunde bulundu): Pine
      // tarafi 17.09'dan beri bu alanlari GONDERIYORDU ama bu kod onlari
      // TANIMIYORDU, sessizce dusuyordu - ozellikle p3ozet, entryScore
      // tanisi icin (bkz. CHANGELOG_V162.md [CL029]) ZORUNLU, bir haftalik
      // veri birikimi bu alan olmadan BOS kalacakti.
      p3ozet: String(body.p3ozet ?? "?"),
      pozsebep: String(body.pozsebep ?? "?"),
      schemaVersion: String(body.schemaVersion ?? "?"),
      eventId: String(body.eventId ?? "?"),
      carrierLagBars: String(body.carrierLagBars ?? "?"),
    };
    const buAy = yeniSinyal.zaman_utc.slice(0, 7);

    const headers = {
      Authorization: `Bearer ${this.github.$auth.oauth_access_token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "bist-veri-pipedream",
    };

    const dosyaOku = async (yol) => {
      const r = await axios($, {
        url: `https://api.github.com/repos/${OWNER}/${REPO}/contents/${yol}?ref=main`,
        headers, timeout: HTTP_TIMEOUT_MS,
      });
      return { sha: r.sha, icerik: JSON.parse(Buffer.from(r.content, "base64").toString("utf8")) };
    };
    const dosyaYaz = async (yol, veri, mesaj, sha) => {
      const data = {
        message: mesaj,
        content: Buffer.from(JSON.stringify(veri, null, 2)).toString("base64"),
        branch: "main",
      };
      if (sha) data.sha = sha;
      await axios($, {
        method: "PUT",
        url: `https://api.github.com/repos/${OWNER}/${REPO}/contents/${yol}`,
        headers, data, timeout: HTTP_TIMEOUT_MS,
      });
    };

    // (1) v4: GUNLUK_OZET icin SEMBOL-SIRALI dilim (kuyruk olusmasin);
    // digerleri icin kisa rastgele gecikme.
    if (yeniSinyal.sinyal === "GUNLUK_OZET") {
      const idx = SEMBOL_SIRASI.indexOf(yeniSinyal.sembol);
      const dilim = idx >= 0 ? idx : SEMBOL_SIRASI.length;
      await bekle(dilim * DILIM_MS + Math.floor(Math.random() * 400));
    } else {
      await bekle(Math.floor(Math.random() * 2500));
    }

    let sonHata = null;
    for (let deneme = 1; deneme <= MAX_DENEME && gecen() < ANA_BUTCE_MS; deneme++) {
      let sha, gecmis = [], sayac = { ay: buAy, adet: 0 }, dosyaAy = buAy;
      try {
        const m = await dosyaOku(PATH);
        sha = m.sha;
        if (Array.isArray(m.icerik.sinyal_gecmisi)) gecmis = m.icerik.sinyal_gecmisi;
        if (m.icerik.ay_sayac) sayac = m.icerik.ay_sayac;
        if (m.icerik.son_sinyal?.zaman_utc) dosyaAy = m.icerik.son_sinyal.zaman_utc.slice(0, 7);
      } catch (e) { /* dosya yok/eski format -> sifirdan */ }

      // AY DONUMU (degismedi)
      if (dosyaAy !== buAy && gecmis.length > 0) {
        const arsivYol = `data/arsiv/tv_alerts_${dosyaAy.replace("-", "_")}.json`;
        let arsivSha;
        try { arsivSha = (await dosyaOku(arsivYol)).sha; } catch (e) { /* yeni dosya */ }
        try {
          await dosyaYaz(arsivYol,
            { ay: dosyaAy, sinyal_sayisi: gecmis.length, sinyaller: gecmis },
            `Sinyal arsivi ${dosyaAy}`, arsivSha);
          gecmis = [];
        } catch (e) { /* arsiv yazilamadiysa gecmisi KORU */ }
      }
      if (sayac.ay !== buAy) sayac = { ay: buAy, adet: 0 };

      // (4) TEKRAR-KAYIT KORUMASI: onceki denemede yazma aslinda
      // basarili olduysa ayni sinyali ikinci kez ekleme.
      const suSaniye = Date.parse(yeniSinyal.zaman_utc);
      const zatenVar = gecmis.some((s) =>
        s.sembol === yeniSinyal.sembol && s.sinyal === yeniSinyal.sinyal &&
        s.fiyat === yeniSinyal.fiyat &&
        Math.abs(Date.parse(s.zaman_utc) - suSaniye) < 60000);
      if (!zatenVar) {
        gecmis.unshift(yeniSinyal);
        sayac.adet += 1;
      }
      gecmis.sort((a, b) => String(b.zaman_utc).localeCompare(String(a.zaman_utc)));
      gecmis = gecmis.slice(0, MAX_SINYAL);

      const dosya = {
        son_guncelleme_utc: new Date().toISOString(),
        kaynak: "TradingView Webhook (Pipedream uzerinden)",
        sinyal_sayisi: gecmis.length,
        ay_sayac: sayac,
        son_sinyal: gecmis[0] ?? yeniSinyal,
        sinyal_gecmisi: gecmis,
      };

      try {
        await dosyaYaz(PATH, dosya, `TV sinyal: ${yeniSinyal.sembol} ${yeniSinyal.sinyal}`, sha);
        return dosya; // basarili
      } catch (e) {
        sonHata = e;
        // (2) JITTER'LI USTEL BEKLEME: 300-900, 600-1800, 900-2700ms...
        const taban = Math.min(300 * deneme, 2000);
        await bekle(taban + Math.floor(Math.random() * taban * 2));
      }
    }

    // (3) SON CARE: event'i ASLA kaybetme - benzersiz inbox dosyasina yaz
    // v3: inbox yazmasi da artik 3 denemelik jitter'li retry iceriyor.
    // Eskiden tek denemeydi; 30'luk patlamada ana dosyanin 8 denemesi
    // TUKENDIGI anda (en yogun saniyeler) inbox'in TEK denemesi de
    // es zamanli baska bir inbox-dosyasi commit'iyle cakisabiliyordu
    // (GitHub ayni branch'teki es zamanli PUT'larda farkli yollarda
    // bile 409 verebiliyor) - bu da sinyalin GERCEKTEN kaybolmasina
    // ve atilan hatanin kullaniciya e-posta olarak dusmesine yol aciyordu.
    const kimlik = `${yeniSinyal.zaman_utc.replace(/[:.]/g, "-")}_${yeniSinyal.sembol}_${Math.floor(Math.random() * 1e6)}`;
    const inboxYol = `data/inbox/${kimlik}.json`;
    const INBOX_DENEME = 8;
    let inboxHata = null;
    for (let d2 = 1; d2 <= INBOX_DENEME && (d2 === 1 || gecen() < INBOX_BITIS_MS); d2++) {
      try {
        await dosyaYaz(inboxYol, yeniSinyal,
          `INBOX (yaris kaybi): ${yeniSinyal.sembol} ${yeniSinyal.sinyal}`);
        return { inbox: inboxYol, not: "ana dosya yazilamadi, inbox'a birakildi", sonHata: String(sonHata) };
      } catch (e2) {
        inboxHata = e2;
        const taban2 = Math.min(400 * d2, 1500);
        await bekle(taban2 + Math.floor(Math.random() * taban2));
      }
    }
    throw sonHata; // inbox 3 denemede de yazilamadiysa gercek ariza - failed gorunsun
  },
});
