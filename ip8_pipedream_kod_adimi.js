// IP-8 PIPEDREAM CODE ADIMI - v1 (14.09.2026)
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
    const PATH = "data/ip8_sinyal_latest.json";
    const MAX_KAYIT = 500; // ~1.5+ yil gunluk gecmis (V162'nin 100'unden
                            // daha yuksek - IP-8 gunde 1 kayit ekliyor,
                            // V162 gunde onlarca)
    const MAX_DENEME = 8;

    const bekle = (ms) => new Promise((r) => setTimeout(r, ms));

    const body = steps.trigger.event.body || {};

    // 15.09 EKLENTI (denetim maddesi 4): eskiden sadece "tip" kontrol
    // ediliyordu - yarim/eksik gelen bir payload (orn. sektorler dizisi
    // 11 yerine 1 hisse) sessizce GitHub'a yazilabiliyordu. Artik tam
    // sema dogrulamasi VAR - herhangi biri basarisiz olursa yazma islemi
    // hic baslamiyor, hata firlatilip Pipedream'in kendi hata bildirimi
    // (varsa) devreye girsin diye.
    if (body.tip !== "IP8_GUNLUK_SEKTOR_OZET") {
      return { atlandi: true, sebep: "beklenmeyen payload tipi", alinan: body.tip };
    }
    // 15.09 EKLENTI (denetim - webhook guvenligi): webhook adresi tek
    // basina gizli anahtar gibi dusunulmemeli - adresi ogrenen herkes
    // sahte payload gonderebilir. Artik Pine'dan gelen "webhookKey" alani,
    // Pipedream'in KENDI ortam degiskenine (IP8_WEBHOOK_KEY) kiyaslaniyor.
    // KURULUM: Pipedream'de bu workflow'un "Environment Variables"
    // ayarina IP8_WEBHOOK_KEY=<Pine'daki ile AYNI deger> ekleyin. Bos/
    // tanimsizsa kontrol devre disi kalir (geriye donuk uyumluluk icin) -
    // ama uretimde MUTLAKA doldurulmali.
    const beklenenAnahtar = process.env.IP8_WEBHOOK_KEY;
    if (beklenenAnahtar && body.webhookKey !== beklenenAnahtar) {
      throw new Error("Yetkisiz istek: webhookKey uyusmuyor");
    }

    if (body.versiyon !== "0.4-P2") {
      throw new Error(`Beklenmeyen sema surumu: ${body.versiyon} (beklenen: 0.4-P2)`);
    }
    if (!Array.isArray(body.sektorler) || body.sektorler.length !== 11) {
      throw new Error(`Eksik sektor payloadi: ${Array.isArray(body.sektorler) ? body.sektorler.length : 0}/11 sektor geldi`);
    }
    if (!body.tarih || !/^\d{4}-\d{2}-\d{2}$/.test(body.tarih)) {
      throw new Error(`Gecersiz tarih formati: ${body.tarih}`);
    }

    // 15.09 EKLENTI (denetim maddesi 3): TEST payload'lari (Colab/manuel
    // test istekleri gibi) ARTIK ayri isaretleniyor ve gunluk_gecmis'e
    // KARISMIYOR - Python tarafinin (tarih,sektor) tekillik kontrolu,
    // gercek bir gunun kaydini "zaten var" diye atlamasin diye.
    const testMi = body.test === true || (body.sektorler || []).some(
      (s) => s.evre === "TEST" || s.aksiyon === "TEST" || s.lider === "TESTHISSE"
    );
    if (testMi) {
      return { atlandi: true, sebep: "test payload'i - gunluk_gecmis'e eklenmedi", tarih: body.tarih };
    }

    const yeniKayit = {
      alinma_zamani_utc: new Date().toISOString(),
      tarih: String(body.tarih ?? "?"),
      versiyon: String(body.versiyon ?? "?"),
      rejim: String(body.rejim ?? "?"),
      breadthYumusatilmamis: body.breadthYumusatilmamis ?? null,
      xuKapanis: body.xuKapanis ?? null,
      xuGunlukGetiri: body.xuGunlukGetiri ?? null,
      isinmaTamamMi: body.isinmaTamamMi ?? null,
      kesitselKapsam: body.kesitselKapsam ?? null,
      universeVersion: body.universeVersion ?? null,
      stateAgeDays: body.stateAgeDays ?? null,
      sektorler: Array.isArray(body.sektorler) ? body.sektorler : [],
    };
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
        const arsivYol = `data/arsiv/ip8_sinyal_${dosyaAy.replace("-", "_")}.json`;
        let arsivSha;
        try { arsivSha = (await dosyaOku(arsivYol)).sha; } catch (e) { /* yeni dosya */ }
        try {
          await dosyaYaz(arsivYol,
            { ay: dosyaAy, gun_sayisi: gecmis.length, gunler: gecmis },
            `IP8 sinyal arsivi ${dosyaAy}`, arsivSha);
          gecmis = [];
        } catch (e) { /* arsiv yazilamadiysa gecmisi KORU */ }
      }

      // TEKRAR-KAYIT KORUMASI: ayni TARIH icin ikinci kez eklenmesin
      // (yeniGun sadece gunde 1 kez tetiklendigi icin normalde tekrar
      // gelmez, ama retry/yeniden-calisma ihtimaline karsi guvenlik agi)
      const zatenVar = gecmis.some((k) => k.tarih === yeniKayit.tarih);
      if (!zatenVar) {
        gecmis.unshift(yeniKayit);
      } else {
        // ayni tarih tekrar geldiyse (orn. script gun icinde yeniden
        // derlendi), ESKI kaydi YENI ile DEGISTIR - en guncel veri kalsin
        gecmis = gecmis.filter((k) => k.tarih !== yeniKayit.tarih);
        gecmis.unshift(yeniKayit);
      }
      gecmis.sort((a, b) => String(b.tarih).localeCompare(String(a.tarih)));
      gecmis = gecmis.slice(0, MAX_KAYIT);

      const dosya = {
        son_guncelleme_utc: new Date().toISOString(),
        kaynak: "IP-8 Sektor Rotasyon Motoru (TradingView alert() -> Pipedream)",
        kayit_sayisi: gecmis.length,
        son_kayit: gecmis[0] ?? yeniKayit,
        gunluk_gecmis: gecmis,
      };

      try {
        await dosyaYaz(PATH, dosya, `IP8 gunluk sektor ozet: ${yeniKayit.tarih}`, sha);
        return dosya; // basarili
      } catch (e) {
        sonHata = e;
        const taban = 300 * deneme;
        await bekle(taban + Math.floor(Math.random() * taban * 2));
      }
    }

    // SON CARE: kaydi ASLA kaybetme - benzersiz inbox dosyasina yaz
    const kimlik = `${yeniKayit.tarih}_${Math.floor(Math.random() * 1e6)}`;
    const inboxYol = `data/inbox/ip8_${kimlik}.json`;
    try {
      await dosyaYaz(inboxYol, yeniKayit, `IP8 INBOX (yaris kaybi): ${yeniKayit.tarih}`);
      return { inbox: inboxYol, not: "ana dosya yazilamadi, inbox'a birakildi", sonHata: String(sonHata) };
    } catch (e2) {
      throw sonHata;
    }
  },
});
