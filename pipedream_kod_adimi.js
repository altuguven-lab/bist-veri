// PIPEDREAM "Run Node.js code" ADIMI - bu kodu Pipedream workflow'unda
// HTTP trigger'dan SONRAKI adima yapistir. Cikti, bir sonraki GitHub
// adiminda dosya icerigi olarak kullanilacak.

export default defineComponent({
  async run({ steps, $ }) {
    const rawBody = steps.trigger.event.body;
    let parsed;

    // TradingView'in alert mesaji JSON formatindaysa (onerilen), onu ayristir.
    // Degilse (duz metin), ham_mesaj alanina oldugu gibi koy.
    try {
      parsed = typeof rawBody === "string" ? JSON.parse(rawBody) : rawBody;
    } catch (e) {
      parsed = { ham_mesaj: String(rawBody) };
    }

    const sonuc = {
      son_guncelleme_utc: new Date().toISOString(),
      kaynak: "TradingView Webhook (Pipedream uzerinden)",
      sembol: parsed.symbol || parsed.sembol || null,
      sinyal: parsed.signal || parsed.sinyal || null,
      interval: parsed.interval || null,
      fiyat: parsed.price || parsed.fiyat || null,
      ham_mesaj: parsed.ham_mesaj || rawBody,
    };

    // Bu adimin ciktisi (JSON string), bir sonraki "GitHub: Create or Update
    // File" adiminda dosya icerigi olarak kullanilacak (steps.kod_adi.$return_value).
    return JSON.stringify(sonuc, null, 2);
  },
});
