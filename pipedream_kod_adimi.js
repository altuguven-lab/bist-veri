import { axios } from "@pipedream/platform";

export default defineComponent({
  props: {
    github: { type: "app", app: "github" },
  },
  async run({ steps, $ }) {
    const OWNER = "altuguven-lab";
    const REPO = "bist-veri";
    const PATH = "data/tv_alerts_latest.json";
    const MAX_SINYAL = 30;

    // TradingView'den gelen govde
    const body = steps.trigger.event.body || {};
    const yeniSinyal = {
      zaman_utc: new Date().toISOString(),
      sembol: String(body.symbol ?? "?"),
      sinyal: String(body.signal ?? "?"),
      interval: String(body.interval ?? "?"),
      fiyat: String(body.price ?? "?"),
    };

    const headers = {
      Authorization: `Bearer ${this.github.$auth.oauth_access_token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "bist-veri-pipedream",
    };

    // Dosyayi oku, sinyali ekle, yaz. Sha cakismasinda (es zamanli sinyal)
    // dosyayi TAZE halinden yeniden okuyup tekrar dener - sinyal kaybolmaz.
    let sonHata = null;
    for (let deneme = 1; deneme <= 3; deneme++) {
      // 1) Guncel dosyayi oku (sha + gecmis)
      let sha;
      let gecmis = [];
      try {
        const mevcut = await axios($, {
          url: `https://api.github.com/repos/${OWNER}/${REPO}/contents/${PATH}?ref=main`,
          headers,
        });
        sha = mevcut.sha;
        const icerik = JSON.parse(
          Buffer.from(mevcut.content, "base64").toString("utf8")
        );
        if (Array.isArray(icerik.sinyal_gecmisi)) {
          gecmis = icerik.sinyal_gecmisi;
        }
      } catch (e) {
        // Dosya yoksa veya eski formattaysa sifirdan basla
      }

      // 2) Yeni sinyal en basa, son MAX_SINYAL kadari kalir
      gecmis.unshift(yeniSinyal);
      gecmis = gecmis.slice(0, MAX_SINYAL);

      const dosya = {
        son_guncelleme_utc: yeniSinyal.zaman_utc,
        kaynak: "TradingView Webhook (Pipedream uzerinden)",
        sinyal_sayisi: gecmis.length,
        son_sinyal: yeniSinyal,
        sinyal_gecmisi: gecmis,
      };

      // 3) Yaz - cakisirsa dongu basa doner ve TAZE sha/gecmisle tekrar dener
      try {
        await axios($, {
          method: "PUT",
          url: `https://api.github.com/repos/${OWNER}/${REPO}/contents/${PATH}`,
          headers,
          data: {
            message: `TV sinyal: ${yeniSinyal.sembol} ${yeniSinyal.sinyal}`,
            content: Buffer.from(JSON.stringify(dosya, null, 2)).toString("base64"),
            sha,
            branch: "main",
          },
        });
        return dosya; // basarili
      } catch (e) {
        sonHata = e;
        await new Promise((r) => setTimeout(r, 400 * deneme)); // kisa bekleme
      }
    }
    throw sonHata; // 3 denemede de yazilamadi
  },
});
