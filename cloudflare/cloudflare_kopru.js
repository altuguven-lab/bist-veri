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
//   Cron Triggers  : "*/2 5-17 * * MON-FRI", "*/10 6-7 * * SAT" ve "30 20 * * MON-FRI"  (UTC; 23.11 paket55)
// Bu dosyanin aynisi repoda cloudflare_kopru.js olarak yedeklenir. ANAHTARLAR KODDA YOKTUR.

const OWNER = "altuguven-lab";
const REPO = "bist-veri";
const PATH = "data/tv_alerts_latest.json";
// 19.11 (paket40): gunluk piyasa kaydi (TradingView TVC tahvil getirileri vb.) V163 sinyal dosyasindan AYRI dosyaya
const PIYASA_PATH = "data/piyasa_gunluk.json";
const PIYASA_ALANLAR = new Set(["TR02Y", "TR05Y", "TR10Y"]);
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
  if (body.kanal === "PIYASA_GUNLUK") return piyasaKabul(body, env);   // V163 akisina hic dokunmaz
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

// ---------- 1b) GUNLUK PIYASA KAYDI (paket40) ----------
// Mesaj: {"kanal":"PIYASA_GUNLUK","kaynak":"TradingView TVC","tarih":"YYYY-MM-DD","TR02Y":..,"TR05Y":..,"TR10Y":..}
// Yalniz PIYASA_ALANLAR'daki sayisal alanlar alinir; ayni gun ikinci mesaj ilkinin uzerine yazar.
export function piyasaKaydi(body, simdi = new Date().toISOString()) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(body.tarih || ""))) return null;
  const degerler = {};
  for (const [k, v] of Object.entries(body)) {
    if (PIYASA_ALANLAR.has(k) && typeof v === "number" && Number.isFinite(v)) degerler[k] = v;
  }
  if (!Object.keys(degerler).length) return null;
  return { tarih: body.tarih, zaman_utc: simdi, kaynak: s(body.kaynak), degerler };
}

async function piyasaKabul(body, env) {
  const k = piyasaKaydi(body);
  if (!k) return new Response("piyasa: gecersiz ya da bos", { status: 200 });
  await env.OLAYLAR.put(`pg:${k.tarih}`, "1", { expirationTtl: KV_TTL_SN, metadata: k });
  return new Response(`piyasa kaydedildi: ${k.tarih}`, { status: 200 });
}

export async function piyasaAktar(env, simdi = new Date()) {
  let imlec, bekleyen = [];
  do {
    const l = await env.OLAYLAR.list({ prefix: "pg:", cursor: imlec });
    for (const k of l.keys) if (k.metadata) bekleyen.push(k.metadata);
    imlec = l.list_complete ? undefined : l.cursor;
  } while (imlec);
  if (!bekleyen.length) return { durum: "bos" };
  const G = gh(env);
  let sonHata;
  for (let deneme = 1; deneme <= 5; deneme++) {
    try {
      const m = await G.oku(PIYASA_PATH);
      const d = m?.icerik && typeof m.icerik === "object" ? m.icerik : {};
      const seriler = d.seriler || {};
      for (const k of bekleyen) {
        for (const [ad, v] of Object.entries(k.degerler)) {
          seriler[ad] = seriler[ad] || {};
          seriler[ad][k.tarih] = v;
        }
      }
      for (const ad of Object.keys(seriler)) {             // tarih sirali, en fazla ~3 yil
        seriler[ad] = Object.fromEntries(Object.entries(seriler[ad]).sort().slice(-800));
      }
      const son = bekleyen.map((k) => k.tarih).sort().pop();
      const dosya = {
        son_guncelleme_utc: simdi.toISOString(),
        kaynak: "TradingView TVC (kullanicinin aboneligi), Pine alarmi -> Cloudflare kopru",
        not: "Gunluk kapanis getirileri (%). Salt olcum, tavsiye degildir.",
        son_tarih: son, seriler,
      };
      await G.yaz(PIYASA_PATH, dosya, `Piyasa gunluk: CF ${son}`, m?.sha);
      await Promise.all(bekleyen.map((k) => env.OLAYLAR.delete(`pg:${k.tarih}`).catch(() => null)));
      return { durum: "yazildi", gun: bekleyen.length };
    } catch (e) {
      sonHata = e;
      await bekle(500 * deneme + Math.floor(Math.random() * 500 * deneme));
    }
  }
  throw sonHata;
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

// ------------------------------------------------------------------ ZAMANLI TETIK (20.11.2026)
// Neden: GitHub'in gunduz `schedule:` tetikleri bu depoda ~9 saat gecikiyor (kuresel_gosterge 06:40 UTC -> 16:01,
// makro_akim_reel 13:15 -> 21:36). Kopru zaten seans saatlerinde 2 dakikada bir calisiyor; belirli UTC dakikalarinda
// GitHub'a repository_dispatch gonderir. Ayni GITHUB_TOKEN (Contents: Read and write) yeterlidir.
// Anahtar: "SS:DD" UTC; deger: repository_dispatch event_type listesi. */2 tetigi yalniz CIFT dakikalarda calisir.
// 23.11 (paket55): GitHub'in kendi zamanlayicisi 6-9 saat geciktigi icin sabah brifingine (09:40 TR) ve
// aksam kapanisina bagli tum isler buradan tetiklenir. Anahtarlar UTC "SS:DD"; hafta ici 05-17 UTC arasi
// CIFT dakikalar (cron "*/2 5-17 * * MON-FRI"), Cumartesi 10'un katlari (cron "*/10 6-7 * * SAT").
// Ayni dakikaya en fazla 3 is konur (depoya es zamanli push carpismasini azaltmak icin).
export const ZAMANLI = {
  "05:00": ["kap_bildirim_tetikle"],                                        // 08:00 TR
  "05:20": ["kuresel_asya", "arastirma_tetikle", "tcmb_yayin_tetikle"],   // 08:20 TR, sabah brifinginden once
  "05:30": ["bilanco_tetikle"],                                             // 08:30 TR
  "06:00": ["sabah_veri_tetikle"],                                          // 09:00 TR (sektor + VIOP)
  "06:04": ["risk_saglik_tetikle"],                                         // 09:04 TR, seans oncesi
  "06:10": ["h6_golge_tetikle"],                                            // 09:10 TR
  "06:16": ["aciga_satis_tetikle"],                                         // 09:16 TR, onceki gun yakalama
  "06:20": ["gunluk_gozlem_tetikle", "kopru_sessizlik_tetikle"],            // 09:20 TR
  "06:24": ["viop_hisse_tetikle"],                                          // 09:24 TR, onceki gun yakalama
  "07:00": ["tcmb_evds_tetikle"],                                           // 10:00 TR
  "07:20": ["tcmb_yayin_tetikle", "yabanci_oran_tetikle"],                  // 10:20 TR, TCMB 10:00 yayinlari
  "08:16": ["kuresel_avrupa"],                                              // 11:16 TR
  "09:50": ["arastirma_tetikle"],                                           // 12:50 TR, ogle brifinginden once
  "10:18": ["tv_arsiv_tetikle"],                                            // 13:18 TR
  "11:36": ["risk_saglik_tetikle"],                                         // 14:36 TR
  "11:50": ["tcmb_yayin_tetikle"],                                          // 14:50 TR, TCMB 14:30 yayinlari
  "13:16": ["makro_tetikle"],                                               // 16:16 TR, EVDS
  "13:40": ["kuresel_amerika"],                                             // 16:40 TR, ABD acilisi sonrasi
  "14:20": ["tcmb_yayin_tetikle"],                                          // 17:20 TR
  "15:20": ["bist_resmi_tetikle", "seans_kapanisi_tetikle"],                // 18:20 TR, kapanis sonrasi (ilk okuma)
  "15:26": ["dusuk_teyit_tetikle"],                                         // 18:26 TR
  "15:30": ["kopru_sessizlik_tetikle"],                                     // 18:30 TR
  "15:44": ["risk_saglik_tetikle"],                                         // 18:44 TR, ertesi gunun gun-basi referansi
  "15:50": ["arastirma_tetikle"],                                           // 18:50 TR
  "16:18": ["tv_arsiv_tetikle"],                                            // 19:18 TR
  "16:20": ["veri_arsivi_tetikle"],                                         // 19:20 TR
  "16:30": ["bist_resmi_tetikle", "ip8_arsiv_tetikle"],                     // 19:30 TR, kesinlesmis kapanis
  "16:32": ["sqz_tetikle"],                                                 // 19:32 TR
  "16:34": ["viop_hisse_tetikle"],                                          // 19:34 TR
  "16:40": ["alarm_karne_tetikle"],                                         // 19:40 TR
  "16:42": ["aciga_satis_tetikle"],                                         // 19:42 TR
  "16:50": ["kopru_sessizlik_tetikle"],                                     // 19:50 TR
  "17:10": ["h5_filtre_tetikle"],                                           // 20:10 TR
  "17:30": ["konsensus_tetikle"],                                           // 20:30 TR
};
// Yalniz Cuma (hafta ici tablosuna EK)
export const ZAMANLI_CUMA = {
  "15:22": ["hafta_kapanisi_tetikle"],                                      // 18:22 TR
  "17:32": ["schumpeter_tetikle"],                                          // 20:32 TR
};
// Cumartesi (Cuma verisinin Yahoo gecikmesiyle tamamlanmasi)
export const ZAMANLI_CMT = {
  "06:20": ["aciga_satis_tetikle", "kopru_sessizlik_tetikle"],              // 09:20 TR
  "06:40": ["viop_hisse_tetikle"],                                          // 09:40 TR
  "07:20": ["veri_arsivi_tetikle"],                                         // 10:20 TR
  "07:40": ["alarm_karne_tetikle"],                                         // 10:40 TR
  "07:50": ["piyasa_dongusu_tetikle"],                                      // 10:50 TR
};

export function zamanliOlaylar(zamanMs) {
  const d = new Date(zamanMs);
  const g = d.getUTCDay();                       // 0 Pazar ... 6 Cumartesi
  const anahtar = `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}`;
  if (g === 0) return [];
  if (g === 6) return ZAMANLI_CMT[anahtar] || [];
  return [...(ZAMANLI[anahtar] || []), ...(g === 5 ? (ZAMANLI_CUMA[anahtar] || []) : [])];
}

export async function zamanliTetik(env, zamanMs) {
  const olaylar = zamanliOlaylar(zamanMs);
  const sonuc = [];
  for (const tur of olaylar) {
    const r = await fetch(`https://api.github.com/repos/${OWNER}/${REPO}/dispatches`, {
      method: "POST",
      headers: { Authorization: `Bearer ${env.GITHUB_TOKEN}`, Accept: "application/vnd.github+json",
                 "User-Agent": "bist-veri-cloudflare", "Content-Type": "application/json" },
      body: JSON.stringify({ event_type: tur, client_payload: { kaynak: "cloudflare-zamanli", utc: new Date(zamanMs).toISOString() } }),
    });
    sonuc.push(`${tur}:${r.status}`);   // 204 = kabul
    if (r.status !== 204) console.log(`zamanli tetik hata ${tur} ${r.status}`);
  }
  if (sonuc.length) console.log("zamanli tetik", sonuc.join(" "));
  return sonuc;
}

export default {
  fetch: (request, env, ctx) => kabul(request, env, ctx),
  // iki aktarma birbirinden bagimsiz: biri hata verirse digeri yine calisir
  // aktarmalar ve zamanli tetik birbirinden bagimsiz: biri hata verirse digerleri yine calisir
  scheduled: (event, env, ctx) => ctx.waitUntil(Promise.allSettled([
    aktar(env), piyasaAktar(env), zamanliTetik(env, event.scheduledTime)])),
};
