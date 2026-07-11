// PIPEDREAM CODE ADIMI - FINAL (retry + aylik sayac + ay donumu arsivi)
// Bu dosya repodaki YEDEKTIR; canli kopya Pipedream'de calisir.
// Her Pipedream degisikliginde bu dosya da ayni icerikle commit'lenir.
import { axios } from "@pipedream/platform";

export default defineComponent({
  props: {
    github: { type: "app", app: "github" },
  },
  async run({ steps, $ }) {
    const OWNER = "altuguven-lab";
    const REPO = "bist-veri";
    const PATH = "data/tv_alerts_latest.json";
    const MAX_SINYAL = 100; // aylik arsiv tam kapsasin diye 30 -> 100

    const body = steps.trigger.event.body || {};
    const yeniSinyal = {
      zaman_utc: new Date().toISOString(),
      sembol: String(body.symbol ?? "?"),
      sinyal: String(body.signal ?? "?"),
      interval: String(body.interval ?? "?"),
      fiyat: String(body.price ?? "?"),
      // G1 alanlari (eski format alarmlar "?" gonderir - geriye uyumlu)
      skor: String(body.skor ?? "?"),
      kgs: String(body.kgs ?? "?"),
      stop: String(body.stop ?? "?"),
      rejim: String(body.rejim ?? "?"),   // 2=ON, 1=notr, 0=RISK-OFF
      relvol: String(body.relvol ?? "?"),
    };
    const buAy = yeniSinyal.zaman_utc.slice(0, 7); // "2026-07"

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

    let sonHata = null;
    for (let deneme = 1; deneme <= 3; deneme++) {
      // 1) Guncel dosyayi oku
      let sha, gecmis = [], sayac = { ay: buAy, adet: 0 }, dosyaAy = buAy;
      try {
        const m = await dosyaOku(PATH);
        sha = m.sha;
        if (Array.isArray(m.icerik.sinyal_gecmisi)) gecmis = m.icerik.sinyal_gecmisi;
        if (m.icerik.ay_sayac) sayac = m.icerik.ay_sayac;
        if (m.icerik.son_sinyal?.zaman_utc) dosyaAy = m.icerik.son_sinyal.zaman_utc.slice(0, 7);
      } catch (e) { /* dosya yok/eski format -> sifirdan */ }

      // 2) AY DONUMU: onceki ayin gecmisini arsive tasi, tamponu bosalt
      if (dosyaAy !== buAy && gecmis.length > 0) {
        const arsivYol = `data/arsiv/tv_alerts_${dosyaAy.replace("-", "_")}.json`;
        let arsivSha;
        try { arsivSha = (await dosyaOku(arsivYol)).sha; } catch (e) { /* yeni dosya */ }
        try {
          await dosyaYaz(arsivYol,
            { ay: dosyaAy, sinyal_sayisi: gecmis.length, sinyaller: gecmis },
            `Sinyal arsivi ${dosyaAy}`, arsivSha);
          gecmis = [];
        } catch (e) { /* arsiv yazilamadiysa gecmisi KORU, veri kaybetme */ }
      }
      if (sayac.ay !== buAy) sayac = { ay: buAy, adet: 0 };

      // 3) Yeni sinyali ekle, sayaci ilerlet
      gecmis.unshift(yeniSinyal);
      gecmis = gecmis.slice(0, MAX_SINYAL);
      sayac.adet += 1;

      const dosya = {
        son_guncelleme_utc: yeniSinyal.zaman_utc,
        kaynak: "TradingView Webhook (Pipedream uzerinden)",
        sinyal_sayisi: gecmis.length,
        ay_sayac: sayac,
        son_sinyal: yeniSinyal,
        sinyal_gecmisi: gecmis,
      };

      // 4) Yaz - sha cakismasinda taze okuma ile tekrar dene
      try {
        await dosyaYaz(PATH, dosya, `TV sinyal: ${yeniSinyal.sembol} ${yeniSinyal.sinyal}`, sha);
        return dosya;
      } catch (e) {
        sonHata = e;
        await new Promise((r) => setTimeout(r, 400 * deneme));
      }
    }
    throw sonHata;
  },
});

