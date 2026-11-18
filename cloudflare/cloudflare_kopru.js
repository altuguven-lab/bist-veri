// CLOUDFLARE KOPRUSU - v1 (16.11.2026) - TradingView V163 alarmlari -> GitHub (bist-veri)
// Pipedream'in yerini alir. Neden: ucretsiz planda es zamanlilik ve uyanma gecikmesi ayari yok;
// ayni bara dusen alarmlarin bir kismi Pipedream'e hic ulasmiyordu (12-16.11: TOASO, TRALT, ASELS, SAHOL).
//
// TASARIM (iki ayri is):
//  1) KABUL (fetch): istek gelir gelmez dogrulanir, her sinyal Cloudflare KV'ye kendi anahtariyla
//     yazilir ve hemen 200 doner. Ayni bara 30 alarm dusse de hicbiri digerini beklemez.
//     Anahtar = eventId (sembol|interval|sinyal|barTime): ayni alarm iki kez gelse tek kayit kalir.
//  2) AKTARMA (scheduled, seans saatlerinde 2 dakikada bir): KV'deki kayitlari okur, depodaki
//     data/tv_alerts_latest.json'da olmayanlari ekler ve TEK commit atar. Depoya tek yazan bu oldugu
//     icin carpisma yok. Yazilamazsa kayitlar KV'de kalir (2 gun), sonraki calismada yeniden denenir.
//  3) BILDIRIM (istege bagli): karar sinyalleri (giris / cikis / stop) Telegram'a tek satir okunabilir
//     mesaj olarak gider; nihai KARAR alani her mesajda gosterilir (16.11 Baskan karari).
//     Bilgi sinyalleri (P4, P3_RADAR, SEKTOR_ROTASYONU, P3_HACIM_BEKLE, TASIMA, GUNLUK_OZET) gonderilmez.
//  4) GECIS (istege bagli): PIPEDREAM_URL tanimliysa her istek Pipedream'e de iletilir; gecis haftasi
//     iki hat birlikte yazar, depo eventId ile tekillestirir. Bir hafta sonra bu degisken silinir.
//
// GEREKEN AYARLAR (Cloudflare > Worker > Settings):
//   KV baglantisi  : OLAYLAR  (bir KV namespace)
//   Gizli (Secret) : GITHUB_TOKEN  (fine-grained, yalniz altuguven-lab/bist-veri, Contents: Read and write)
//   Gizli          : WEBHOOK_KEY   (uzun rastgele metin; TradingView adresinde ?k= olarak kullanilir)
//   Istege bagli   : TELEGRAM_TOKEN, TELEGRAM_CHAT, PIPEDREAM_URL
//   Cron Triggers  : "*/2 6-15 * * 1-5" ve "30 20 * * 1-5"  (UTC)
// Bu dosyanin aynisi repoda cloudflare_kopru.js olarak yedeklenir. ANAHTARLAR KODDA YOKTUR.

const OWNER = "altuguven-lab";
const REPO = "bist-veri";
const PATH = "data/tv_alerts_latest.json";
const MAX_SINYAL = 400;
const KV_TTL_SN = 2 * 24 * 3600;
const BILGI = new Set(["P4_HAZIRLIK", "P3_RADAR", "SEKTOR_ROTASYONU", "P3_HACIM_BEKLE", "TASIMA", "GUNLUK_OZET"]);
const ETIKET = {
  STOP_KIRILDI: "STOP KIRILDI", ACIL_CIK: "ACIL CIK", POZ_AZALT: "POZ AZALT", IC_STOP: "IC STOP",
  KAR_KORU: "KAR KORU", P1_KALITELI_AL: "P1 KALITELI AL", P1_AL: "P1 AL", P2_ERKEN_AL: "P2 ERKEN AL",
  P2_DIP_DONUS: "P2 DIP DONUS", P2_DESTEK_DONUS: "P2 DESTEK DONUS", P2_ADAY: "P2 ADAY",
  P3_SKOR_AL: "P3 SKOR AL", EKLEME_ADAYI: "EKLEME ADAYI",
};
const CIKIS = new Set(["STOP_KIRILDI", "ACIL_CIK", "POZ_AZALT", "IC_STOP", "KAR_KORU"]);

// ---------- yardimcilar ----------
const s = (x) => String(x ?? "?");
const b64 = (metin) => {
  const bayt = new TextEncoder().encode(metin);
  let ikili = "";
  for (let i = 0; i < bayt.length; i += 0x8000) ikili += String.fromCharCode(...bayt.subarray(i, i + 0x8000));
  return btoa(ikili);
};
const b64coz = (veri) => {
  const ikili = atob(veri.replace(/\n/g, ""));
  return new TextDecoder().decode(Uint8Array.from(ikili, (c) => c.charCodeAt(0)));
};
const bekle = (ms) => new Promise((r) => setTimeout(r, ms));

export function kayitlariKur(body, simdi = new Date().toISOString()) {
  const sablon = {
    zaman_utc: simdi, sembol: s(body.symbol), interval: s(body.interval), fiyat: s(body.price),
    skor: s(body.skor), kgs: s(body.kgs), stop: s(body.stop), rejim: s(body.rejim), relvol: s(body.relvol),
    v112n: s(body.v112n), v112wr: s(body.v112wr), p3ozet: s(body.p3ozet), pozsebep: s(body.pozsebep),
    schemaVersion: s(body.schemaVersion), carrierLagBars: s(body.carrierLagBars),
    skor0: s(body.skor0), kgs0: s(body.kgs0), relvol0: s(body.relvol0), manuel_poz: s(body.manuel_poz),
    poz_kaynak: s(body.poz_kaynak), karar: s(body.karar), faktor: s(body.faktor), kopru: "cloudflare-v1",
  };
  const adlar = body.signals
    ? String(body.signals).split(",").map((x) => x.trim()).filter(Boolean)
    : [s(body.signal)];
  return adlar.map((ad) => ({
    ...sablon, sinyal: ad,
    eventId: body.signals ? `${sablon.sembol}|${sablon.interval}|${ad}|${s(body.barTime)}` : s(body.eventId),
  }));
}

export function bildirimMetni(k) {
  const ad = ETIKET[k.sinyal];
  if (!ad || BILGI.has(k.sinyal)) return null;
  const tur = CIKIS.has(k.sinyal) ? "CIKIS/RISK" : "GIRIS";
  const karar = k.karar && k.karar !== "?" ? k.karar : "bilinmiyor";
  const celiski = (tur === "GIRIS" && karar === "PAS GEC") || (tur === "CIKIS/RISK" && /AL$/.test(karar))
    ? " (sinyal ile karar celisiyor)" : "";
  const saat = new Date(k.zaman_utc).toLocaleTimeString("tr-TR", { timeZone: "Europe/Istanbul", hour: "2-digit", minute: "2-digit" });
  return `${tur} | ${ad} | ${k.sembol} ${k.interval}dk ${saat}\nFiyat ${k.fiyat} | Stop ${k.stop}\n` +
         `Karar: ${karar}${celiski} | Skor ${k.skor0 !== "?" ? k.skor0 : k.skor} | KGS ${k.kgs0 !== "?" ? k.kgs0 : k.kgs}\n` +
         `Gozlem amaclidir, tavsiye degildir.`;
}

// ---------- GitHub ----------
function gh(env) {
  const headers = {
    Authorization: `Bearer ${env.GITHUB_TOKEN}`, Accept: "application/vnd.github+json",
    "User-Agent": "bist-veri-cloudflare", "Content-Type": "application/json",
  };
  const url = (yol) => `https://api.github.com/repos/${OWNER}/${REPO}/contents/${yol}`;
  return {
    async oku(yol) {
      const r = await fetch(`${url(yol)}?ref=main`, { headers });
      if (r.status === 404) return null;
      if (!r.ok) throw new Error(`GitHub okuma ${r.status}`);
      const j = await r.json();
      return { sha: j.sha, icerik: JSON.parse(b64coz(j.content)) };
    },
    async yaz(yol, veri, mesaj, sha) {
      const govde = { message: mesaj, content: b64(JSON.stringify(veri, null, 2)), branch: "main" };
      if (sha) govde.sha = sha;
      const r = await fetch(url(yol), { method: "PUT", headers, body: JSON.stringify(govde) });
      if (!r.ok) throw new Error(`GitHub yazma ${r.status}`);
    },
  };
}

// ---------- 1) KABUL ----------
async function kabul(request, env, ctx) {
  const u = new URL(request.url);
  if (request.method !== "POST") return new Response("bist-veri kopru v1", { status: 200 });
  if (env.WEBHOOK_KEY && u.searchParams.get("k") !== env.WEBHOOK_KEY) return new Response("yetkisiz", { status: 401 });
  const ham = await request.text();
  let body;
  try { body = JSON.parse(ham); } catch (e) { return new Response("gecersiz JSON", { status: 400 }); }
  if (!body.schemaVersion) return new Response("schemaVersion yok - yazilmadi", { status: 200 });
  const kayitlar = kayitlariKur(body);
  // ayni alarm ikinci kez gelirse (TradingView yeniden denemesi) bildirim tekrar gitmesin
  const yeniMi = await Promise.all(kayitlar.map(async (k) => (await env.OLAYLAR.get(`ev:${k.eventId}`)) === null));
  await Promise.all(kayitlar.map((k) => env.OLAYLAR.put(`ev:${k.eventId}`, "1",
    { expirationTtl: KV_TTL_SN, metadata: k })));
  const arka = [];
  if (env.TELEGRAM_TOKEN && env.TELEGRAM_CHAT) {
    for (const k of kayitlar.filter((_, i) => yeniMi[i])) {
      const metin = bildirimMetni(k);
      if (metin) arka.push(fetch(`https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/sendMessage`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: env.TELEGRAM_CHAT, text: metin }),
      }).catch(() => null));
    }
  }
  if (env.PIPEDREAM_URL) {
    arka.push(fetch(env.PIPEDREAM_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: ham }).catch(() => null));
  }
  if (arka.length) ctx.waitUntil(Promise.all(arka));
  return new Response(`kaydedildi: ${kayitlar.length}`, { status: 200 });
}

// ---------- 2) AKTARMA ----------
async function temizle(env, kayitlar) {
  await Promise.all(kayitlar.map((k) => env.OLAYLAR.delete(`ev:${k.eventId}`).catch(() => null)));
}

export async function aktar(env, simdi = new Date()) {
  // KV'deki tum bekleyen kayitlar (metadata icinde tam kayit var; ayrica okuma gerekmez)
  let imlec, bekleyen = [];
  do {
    const l = await env.OLAYLAR.list({ prefix: "ev:", cursor: imlec });
    for (const k of l.keys) if (k.metadata) bekleyen.push(k.metadata);
    imlec = l.list_complete ? undefined : l.cursor;
  } while (imlec);
  if (!bekleyen.length) return { durum: "bos" };
  const G = gh(env);
  let sonHata;
  for (let deneme = 1; deneme <= 5; deneme++) {
    try {
      const m = await G.oku(PATH);
      let gecmis = Array.isArray(m?.icerik?.sinyal_gecmisi) ? m.icerik.sinyal_gecmisi : [];
      let sayac = m?.icerik?.ay_sayac ?? { ay: simdi.toISOString().slice(0, 7), adet: 0 };
      const dosyaAy = (m?.icerik?.son_sinyal?.zaman_utc ?? simdi.toISOString()).slice(0, 7);
      const buAy = simdi.toISOString().slice(0, 7);
      const varolan = new Set(gecmis.map((x) => x.eventId));
      // depoda zaten olanlar ya da arsive gecmis eski ay kayitlari atlanir
      const yeniler = bekleyen.filter((k) => !varolan.has(k.eventId) && k.zaman_utc.slice(0, 7) >= dosyaAy);
      if (!yeniler.length) {
        await temizle(env, bekleyen);
        return { durum: "yeni yok", bekleyen: bekleyen.length };
      }
      if (dosyaAy !== buAy && gecmis.length) {          // ay donumu: eski ayi arsive tasi
        const arsivYol = `data/arsiv/tv_alerts_${dosyaAy.replace("-", "_")}.json`;
        const a = await G.oku(arsivYol);
        const eski = Array.isArray(a?.icerik?.sinyaller) ? a.icerik.sinyaller : [];
        const birlesik = [...new Map([...eski, ...gecmis].map((x) => [x.eventId + x.zaman_utc, x])).values()];
        await G.yaz(arsivYol, { ay: dosyaAy, sinyal_sayisi: birlesik.length, sinyaller: birlesik },
                    `Sinyal arsivi ${dosyaAy}`, a?.sha);
        gecmis = gecmis.filter((x) => x.zaman_utc.slice(0, 7) === buAy);
      }
      if (sayac.ay !== buAy) sayac = { ay: buAy, adet: 0 };
      gecmis.push(...yeniler);
      sayac.adet += yeniler.length;
      gecmis.sort((x, y) => String(y.zaman_utc).localeCompare(String(x.zaman_utc)));
      gecmis = gecmis.slice(0, MAX_SINYAL);
      const semboller = [...new Set(yeniler.map((k) => k.sembol))];
      const dosya = {
        son_guncelleme_utc: simdi.toISOString(), kaynak: "TradingView Webhook (Cloudflare uzerinden)",
        sinyal_sayisi: gecmis.length, ay_sayac: sayac, son_sinyal: gecmis[0], sinyal_gecmisi: gecmis,
      };
      const ozet = semboller.length <= 4 ? semboller.join(",") : `${semboller.length} sembol`;
      await G.yaz(PATH, dosya, `TV sinyal: CF ${yeniler.length} kayit, ${ozet}`, m?.sha);
      await temizle(env, bekleyen);      // depoya gecenler KV'den silinir (TTL yalniz emniyet)
      return { durum: "yazildi", yeni: yeniler.length };
    } catch (e) {
      sonHata = e;
      await bekle(500 * deneme + Math.floor(Math.random() * 500 * deneme));
    }
  }
  throw sonHata;   // kayitlar KV'de duruyor; sonraki calisma yeniden dener
}

export default {
  fetch: (request, env, ctx) => kabul(request, env, ctx),
  scheduled: (event, env, ctx) => ctx.waitUntil(aktar(env)),
};
