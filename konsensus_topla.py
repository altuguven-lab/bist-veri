"""
ANALIST KONSENSUSU ILERIYE DONUK TOPLAYICI (30.10.2026) - SALT VERI TOPLAMA, test degil.
Neden: BIST icin ucretsiz ve erisimi serbest GECMIS analist hedef/tavsiye verisi bulunamadi (Halk Yatirim arsivi
robots.txt ile otomatik erisime kapali). Revizyon testi icin veri bugunden itibaren biriktirilir.
Kaynak: yfinance Ticker.info (Yahoo): targetMeanPrice, targetHigh/LowPrice, numberOfAnalystOpinions,
recommendationMean, recommendationKey, forwardEps, trailingEps.
Her is gunu BIST100 (kapsam disi haric) icin bir anlik goruntu alinir; ayni gun tekrar calisirsa uzerine yazar.
Cikti: data/konsensus/YYYY-MM.json  ({gun: {sembol: {...}}})
"""
import os, json, datetime, time

ALANLAR = ["targetMeanPrice", "targetMedianPrice", "targetHighPrice", "targetLowPrice", "numberOfAnalystOpinions",
           "recommendationMean", "recommendationKey", "forwardEps", "trailingEps", "currentPrice"]


def liste_oku(yol):
    if not os.path.exists(yol):
        return []
    out = []
    for s in open(yol, encoding="utf-8"):
        s = s.split("#")[0].strip().upper()
        if s and s not in out:
            out.append(s)
    return out


def main():
    import yfinance as yf
    kd = set(liste_oku("config/kapsam_disi.txt"))
    semboller = [k for k in liste_oku("config/bist100_uyeler.txt") if k not in kd]
    gun = datetime.date.today().isoformat()
    yol = f"data/konsensus/{gun[:7]}.json"
    os.makedirs("data/konsensus", exist_ok=True)
    veri = json.load(open(yol, encoding="utf-8")) if os.path.exists(yol) else {}
    anlik, hata = {}, []
    for k in semboller:
        try:
            info = yf.Ticker(k + ".IS").info or {}
            kayit = {a: info.get(a) for a in ALANLAR if info.get(a) is not None}
            if kayit:
                anlik[k] = kayit
        except Exception as e:
            hata.append(f"{k}: {str(e)[:60]}")
        time.sleep(0.3)
    veri[gun] = anlik
    json.dump(veri, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    hedefli = sum(1 for v in anlik.values() if v.get("targetMeanPrice"))
    print(f"{gun}: {len(anlik)} sembol, hedef fiyati olan {hedefli}, hata {len(hata)}")


if __name__ == "__main__":
    main()
