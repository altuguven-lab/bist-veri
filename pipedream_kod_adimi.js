// PIPEDREAM CODE ADIMI - v2 (15.07.2026)
// v1'den fark (KAPANIS PATLAMASI DUZELTMESI - yalniz yaris yonetimi):
//  1. Ilk okumadan ONCE rastgele 0-2500ms gecikme (suru kirici):
//     14 es zamanli event ayni milisaniyede okumaya girmesin.
//  2. Deneme sayisi 3 -> 8; bekleme deterministik degil RASTGELE
//     (jitter'li ustel): kaybedenler senkronize geri donup yeniden
//     carpismasin.
//  3. Tum denemeler biterse throw YOK: son care olarak sinyal
//     data/inbox/ altina kendi benzersiz dosyasina yazilir
//     (cakismasi imkansiz) - event asla kaybolmaz. Brifing/denetim
//     inbox'i da okur; bos kalmasi beklenir.
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
    const MAX_DENEME = 8;

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
        headers,
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
        headers, data,
      });
    };

    // (1) SURU KIRICI: es zamanli patlamada okumalari dagit
    await bekle(Math.floor(Math.random() * 2500));

    let sonHata = null;
    for (let deneme = 1; deneme <= MAX_DENEME; deneme++) {
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
        const taban = 300 * deneme;
        await bekle(taban + Math.floor(Math.random() * taban * 2));
      }
    }

    // (3) SON CARE: event'i ASLA kaybetme - benzersiz inbox dosyasina yaz
    const kimlik = `${yeniSinyal.zaman_utc.replace(/[:.]/g, "-")}_${yeniSinyal.sembol}_${Math.floor(Math.random() * 1e6)}`;
    const inboxYol = `data/inbox/${kimlik}.json`;
    try {
      await dosyaYaz(inboxYol, yeniSinyal,
        `INBOX (yaris kaybi): ${yeniSinyal.sembol} ${yeniSinyal.sinyal}`);
      return { inbox: inboxYol, not: "ana dosya yazilamadi, inbox'a birakildi", sonHata: String(sonHata) };
    } catch (e2) {
      throw sonHata; // inbox bile yazilamadiysa gercek ariza - failed gorunsun
    }
  },
});

