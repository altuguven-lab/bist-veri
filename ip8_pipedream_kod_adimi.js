// IP-8 + V195 PIPEDREAM CODE ADIMI - v2 (12.11.2026; v1: 14.09.2026)
// v2: ayni is akisi V195_GUNLUK_RADAR ve IP-8 degisim olaylarini da yazar (asagida 'v2' notuna bakin).
// V162'nin pipedream_kod_adimi.js'sindeki KANITLANMIS desene (suru kirici
// gecikme, jitter'li ustel retry, ay donumu arsivi, inbox son-care) DAYANIR
// - ama IP-8'in FARKLI semasina (gunde BIR kez, 11-sektorlu ic-ice JSON)
// uyarlanmistir. V162'nin dosyasina (data/tv_alerts_latest.json) DOKUNMAZ,
// AYRI bir dosyaya (data/ip8_sinyal_latest.json) yazar.
//
// IP-8 gunde sadece 1 kez ates aldigi icin (V162'nin ayni anda 21 alarm
// turunden herhangi biri, gun icinde defalarca ates alabilmesinin aksine),
// carpisma riski cok daha dusuk - yine de ayni guvenlik agini (retry+inbox)
// koruyoruz, bedeli ucuz.
import { axios } from "@pipedream/platform";

export default defineComponent({
  props: {
    github: { type: "app", app: "github" },
  },
  async run({ steps, $ }) {
    const OWNER = "altuguven-lab";
    const REPO = "bist-veri";
    const MAX_KAYIT = 500; // ~1.5+ yil gunluk gecmis (V162'nin 100'unden
                            // daha yuksek - IP-8 gunde 1 kayit ekliyor,
                            // V162 gunde onlarca)
    const MAX_DENEME = 8;

    const bekle = (ms) => new Promise((r) => setTimeout(r, ms));

    // v2 (12.11.2026, Denetim 2.6/2.7): TEK is akisi artik UC kayit turunu tasir:
    //   IP8_GUNLUK_SEKTOR_OZET          -> data/ip8_sinyal_latest.json   (degismedi)
    //   V195_GUNLUK_RADAR               -> data/v195_radar_latest.json   (YENI)
    //   IP8_REJIM_DEGISTI / IP8_EN_GUCLU_SEKTOR_DEGISTI -> data/ip8_olaylar_latest.json (YENI)
    // Taninmayan tip ve duz metin (alertcondition mesajlari) eskisi gibi sessizce atlanir.
    let body = steps.trigger.event.body || {};
    if (typeof body === "string") {
      try { body = JSON.parse(body); }
      catch (e) { return { atlandi: true, sebep: "duz metin / gecersiz JSON", ilk80: body.slice(0, 80) }; }
    }
    const TIPLER = ["IP8_GUNLUK_SEKTOR_OZET", "V195_GUNLUK_RADAR", "IP8_REJIM_DEGISTI", "IP8_EN_GUCLU_SEKTOR_DEGISTI"];
    if (!TIPLER.includes(body.tip)) {
      return { atlandi: true, sebep: "beklenmeyen payload tipi", alinan: body.tip };
    }
    // 15.09 (denetim - webhook guvenligi): IP8_WEBHOOK_KEY tanimliysa mesajdaki webhookKey ile kiyaslanir.
    const beklenenAnahtar = process.env.IP8_WEBHOOK_KEY;
    if (beklenenAnahtar && body.webhookKey !== beklenenAnahtar) {
      throw new Error("Yetkisiz istek: webhookKey uyusmuyor");
    }
    if (typeof body.tarih !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(body.tarih)) {
      throw new Error(`Gecersiz tarih formati: ${body.tarih}`);
    }
    const alinma = new Date().toISOString();
    let PATH, etiket, arsivOnEk, kaynak, yeniKayit, anahtar;

    if (body.tip === "IP8_GUNLUK_SEKTOR_OZET") {
      // tam sema dogrulamasi (15.09 denetim maddesi 4): eksik payload yazilmaz, hata firlatilir
      if (body.versiyon !== "0.4-P2") {
        throw new Error(`Beklenmeyen sema surumu: ${body.versiyon} (beklenen: 0.4-P2)`);
      }
      if (!Array.isArray(body.sektorler) || body.sektorler.length !== 11) {
        throw new Error(`Eksik sektor payloadi: ${Array.isArray(body.sektorler) ? body.sektorler.length : 0}/11 sektor geldi`);
      }
      const testMi = body.test === true || body.sektorler.some(
        (s) => s.evre === "TEST" || s.aksiyon === "TEST" || s.lider === "TESTHISSE"
      );
      if (testMi) {
        return { atlandi: true, sebep: "test payload'i - gunluk_gecmis'e eklenmedi", tarih: body.tarih };
      }
      PATH = "data/ip8_sinyal_latest.json";
      etiket = "IP8 gunluk sektor ozet";
      arsivOnEk = "ip8_sinyal";
      kaynak = "IP-8 Sektor Rotasyon Motoru (TradingView alert() -> Pipedream)";
      anahtar = (k) => k.tarih;
      yeniKayit = {
        alinma_zamani_utc: alinma,
        tarih: body.tarih,
        versiyon: String(body.versiyon ?? "?"),
        rejim: String(body.rejim ?? "?"),
        breadthYumusatilmamis: body.breadthYumusatilmamis ?? null,
        xuKapanis: body.xuKapanis ?? null,
        xuGunlukGetiri: body.xuGunlukGetiri ?? null,
        isinmaTamamMi: body.isinmaTamamMi ?? null,
        kesitselKapsam: body.kesitselKapsam ?? null,
        universeVersion: body.universeVersion ?? null,
        stateAgeDays: body.stateAgeDays ?? null,
        sektorler: body.sektorler,
      };
    } else if (body.tip === "V195_GUNLUK_RADAR") {
      if (!Array.isArray(body.radar) || body.radar.length !== 30) {
        throw new Error(`Eksik radar payloadi: ${Array.isArray(body.radar) ? body.radar.length : 0}/30 sembol geldi`);
      }
      if (body.test === true) {
        return { atlandi: true, sebep: "test payload'i", tarih: body.tarih };
      }
      PATH = "data/v195_radar_latest.json";
      etiket = "V195 gunluk radar";
      arsivOnEk = "v195_radar";
      kaynak = "V195 CTRL KURUMSAL gunluk radar kaydi (TradingView alert() -> Pipedream)";
      anahtar = (k) => k.tarih;
      const { webhookKey, tip, ...gerisi } = body;
      yeniKayit = { alinma_zamani_utc: alinma, ...gerisi };
    } else {
      PATH = "data/ip8_olaylar_latest.json";
      etiket = "IP8 olay " + body.tip.replace("IP8_", "");
      arsivOnEk = "ip8_olaylar";
      kaynak = "IP-8 rejim ve en guclu sektor degisim olaylari (TradingView alert() -> Pipedream)";
      anahtar = (k) => `${k.tarih}|${k.tip}`;
      yeniKayit = { alinma_zamani_utc: alinma, tarih: body.tarih, tip: body.tip,
                    eski: body.eski ?? null, yeni: body.yeni ?? null, breadth: body.breadth ?? null };
    }
    const buAy = yeniKayit.tarih.slice(0, 7); // "2026-09"

    const headers = {
      Authorization: `Bearer ${this.github.$auth.oauth_access_token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "bist-veri-pipedream-ip8",
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

    // SURU KIRICI: (IP-8'de tek payload oldugu icin risk dusuk ama ucuz,
    // V162 ile ayni pencerede tetiklenirse GitHub API rate-limit'e yardimci)
    await bekle(Math.floor(Math.random() * 1500));

    let sonHata = null;
    for (let deneme = 1; deneme <= MAX_DENEME; deneme++) {
      let sha, gecmis = [], dosyaAy = buAy;
      try {
        const m = await dosyaOku(PATH);
        sha = m.sha;
        if (Array.isArray(m.icerik.gunluk_gecmis)) gecmis = m.icerik.gunluk_gecmis;
        if (m.icerik.son_kayit?.tarih) dosyaAy = m.icerik.son_kayit.tarih.slice(0, 7);
      } catch (e) { /* dosya yok/eski format -> sifirdan */ }

      // AY DONUMU: V162 ile ayni mantik - ay degisince eski gecmisi
      // ayri bir arsiv dosyasina tasi
      if (dosyaAy !== buAy && gecmis.length > 0) {
        const arsivYol = `data/arsiv/${arsivOnEk}_${dosyaAy.replace("-", "_")}.json`;
        let arsivSha;
        try { arsivSha = (await dosyaOku(arsivYol)).sha; } catch (e) { /* yeni dosya */ }
        try {
          await dosyaYaz(arsivYol,
            { ay: dosyaAy, gun_sayisi: gecmis.length, gunler: gecmis },
            `${etiket} arsivi ${dosyaAy}`, arsivSha);
          gecmis = [];
        } catch (e) { /* arsiv yazilamadiysa gecmisi KORU */ }
      }

      // TEKRAR-KAYIT KORUMASI: ayni TARIH icin ikinci kez eklenmesin
      // (yeniGun sadece gunde 1 kez tetiklendigi icin normalde tekrar
      // gelmez, ama retry/yeniden-calisma ihtimaline karsi guvenlik agi)
      gecmis = gecmis.filter((k) => anahtar(k) !== anahtar(yeniKayit));   // ayni gun/olay -> yenisi kazanir
      gecmis.unshift(yeniKayit);
      gecmis.sort((x, y) => String(anahtar(y)).localeCompare(String(anahtar(x))));
      gecmis = gecmis.slice(0, MAX_KAYIT);

      const dosya = {
        son_guncelleme_utc: new Date().toISOString(),
        kaynak,
        kayit_sayisi: gecmis.length,
        son_kayit: gecmis[0] ?? yeniKayit,
        gunluk_gecmis: gecmis,
      };

      try {
        await dosyaYaz(PATH, dosya, `${etiket}: ${yeniKayit.tarih}`, sha);
        return dosya; // basarili
      } catch (e) {
        sonHata = e;
        const taban = 300 * deneme;
        await bekle(taban + Math.floor(Math.random() * taban * 2));
      }
    }

    // SON CARE: kaydi ASLA kaybetme - benzersiz inbox dosyasina yaz
    const kimlik = `${yeniKayit.tarih}_${Math.floor(Math.random() * 1e6)}`;
    const inboxYol = `data/inbox/${arsivOnEk}_${kimlik}.json`;
    try {
      await dosyaYaz(inboxYol, yeniKayit, `${etiket} INBOX (yaris kaybi): ${yeniKayit.tarih}`);
      return { inbox: inboxYol, not: "ana dosya yazilamadi, inbox'a birakildi", sonHata: String(sonHata) };
    } catch (e2) {
      throw sonHata;
    }
  },
});
