"""
DEGERLEME TARAMASI v2 (26.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Soru: BIST 100 hisselerinde piyasa fiyati ile tahmini deger arasindaki fark.
"Gercek deger" tek bir rakam degildir; uc bagimsiz yontemle tahmin edilir, medyani alinir:
  Y1 Kendi tarihsel F/K (USD, 2021+ medyan):  ima = fiyat x (F/K medyan / F/K son)      [yalniz kar > 0]
  Y2 Kendi tarihsel PD/DD (USD, 2021+ medyan): ima = fiyat x (PD/DD medyan / PD/DD son)
  Y3 Karliliga gore makul PD/DD (Gordon, g=0): makul PD/DD = ROE(USD) / Ozkaynak maliyeti
                                               ima = fiyat x (makul PD/DD / PD/DD son)   [yalniz ROE > 0]
     Ozkaynak maliyeti (USD) = ABD 10y + Turkiye 5y CDS + hisse risk primi (ortam degiskenleriyle).
Ek gorus (degere katilmaz, yan sutun): Yahoo analist konsensus hedefi (targetMeanPrice, analist sayisi)
  ve repodaki son araci kurum hedefi (data/arastirma_hedef_fiyat.json).
Girdi : data/temel_carpan_bist100.json (EVREN=BIST100 temel_carpan_gozlem.py), yfinance anlik fiyat
Cikti : data/deger_tarama.json, data/deger_tarama.csv
v2 (26.10): (1) Y1/Y2 medyanlari TMS 29 donemi (2024+) istatistiklerinden alinir; 2021+ medyan, enflasyon muhasebesi
    oncesi dusuk ozkaynak nedeniyle PD/DD medyanini sisiriyordu. (2) Zarar eden (ROE<=0) hisse degerlenmez.
    (3) En az iki yontem gerekir. (4) 2024 sonrasi duzeltilmemis bedelsizi olan hisse (data/direnc_tarama.json
    bolunme_olaylari) "veri supheli" olarak disarida birakilir. (5) guven = orta yalniz yontem dagilimi <= %100.
Sinirlar: TMS 29 enflasyon muhasebesi; dongusel hisselerde zirve/dip kar; holding ve GYO'da NAD daha anlamli;
          tarihsel medyan "adil" degil, yalniz hissenin kendi gecmisine gore goreli konumdur.
"""
import json, os, statistics, datetime
import pandas as pd
import yfinance as yf

RF = float(os.environ.get("RF_USD", "4.97"))     # ABD 10y, 23.10.2026
CDS = float(os.environ.get("CDS_TR", "2.58"))    # Turkiye 5y CDS (puan/100), 23.10.2026
ERP = float(os.environ.get("ERP", "5.0"))        # hisse risk primi
KE = (RF + CDS + ERP) / 100.0
GIRDI = os.environ.get("CARPAN", "data/temel_carpan_bist100.json")


def fiyat_ve_hedef(kod):
    t = yf.Ticker(kod + ".IS")
    p, hedef, n, oneri = None, None, None, None
    try:
        p = float(t.fast_info["last_price"])
    except Exception:
        try:
            h = t.history(period="5d")["Close"].dropna()
            p = float(h.iloc[-1])
        except Exception:
            pass
    try:
        inf = t.info or {}
        hedef = inf.get("targetMeanPrice")
        n = inf.get("numberOfAnalystOpinions")
        oneri = inf.get("recommendationKey")
    except Exception:
        pass
    return p, hedef, n, oneri


def repo_hedef():
    yol = "data/arastirma_hedef_fiyat.json"
    if not os.path.exists(yol):
        return {}
    son = {}
    for k in json.load(open(yol, encoding="utf-8")).get("kayitlar", []):
        if k.get("yeni_hedef") and (k["sembol"] not in son or k["tarih"] >= son[k["sembol"]]["tarih"]):
            son[k["sembol"]] = k
    return son


def main():
    c = json.load(open(GIRDI, encoding="utf-8"))
    # carpanlar ("son") carpan uretim anindaki fiyatla hesaplanir; ima = fiyat x medyan/son formulu ancak ayni
    # anin fiyatiyla tutarlidir. Bu yuzden betik carpan hesabindan hemen sonra (ayni is akisinda) calistirilmali.
    yas_saat = None
    try:
        t0 = datetime.datetime.fromisoformat(c["olusturma_utc"])
        yas_saat = round((datetime.datetime.now(datetime.timezone.utc) - t0).total_seconds() / 3600, 1)
    except Exception:
        pass
    rh = repo_hedef()
    kd = set()
    if os.path.exists("config/kapsam_disi.txt"):
        kd = {l.split("#")[0].strip().upper() for l in open("config/kapsam_disi.txt", encoding="utf-8") if l.split("#")[0].strip()}
    satir, atlanan = [], list(c.get("atlanan", []))
    bolunme = {}
    if os.path.exists("data/direnc_tarama.json"):
        for x in json.load(open("data/direnc_tarama.json", encoding="utf-8")).get("satirlar", []):
            bolunme[x["kod"]] = [e for e in x.get("bolunme_olaylari", []) if str(e[0]) >= "2024-01-01"]
    for kod, v in c["semboller"].items():
        ist = v.get("istatistik_tms29") or v.get("istatistik") or {}
        fk, pd_ = ist.get("fk_usd"), ist.get("pddd_usd")
        roe = (v.get("ek_olculer") or {}).get("roe_usd")
        p, hedef, n, oneri = fiyat_ve_hedef(kod)
        if not p or not pd_:
            atlanan.append(f"{kod}: fiyat veya PD/DD yok")
            continue
        if bolunme.get(kod):
            atlanan.append(f"{kod}: veri supheli (duzeltilmemis bedelsiz {bolunme[kod][0][0]})")
            continue
        if roe is None or roe <= 0:
            atlanan.append(f"{kod}: zarar (ROE {roe}), degerlenmedi")
            continue
        imalar = {}
        if fk and fk.get("son") and fk["son"] > 0 and fk.get("medyan") and fk["medyan"] > 0:
            imalar["Y1_fk"] = p * fk["medyan"] / fk["son"]
        if pd_.get("son") and pd_["son"] > 0 and pd_.get("medyan"):
            imalar["Y2_pddd"] = p * pd_["medyan"] / pd_["son"]
        if roe is not None and roe > 0 and pd_.get("son"):
            imalar["Y3_roe"] = p * (roe / 100.0 / KE) / pd_["son"]
        if len(imalar) < 2:
            atlanan.append(f"{kod}: ikiden az yontem")
            continue
        deger = statistics.median(imalar.values())
        r = {"kod": kod, "fiyat": round(p, 2), "tahmini_deger": round(deger, 2),
             "potansiyel_pct": round((deger / p - 1) * 100, 1),
             "yontem_sayisi": len(imalar), "yontem_dagilimi_pct": round((max(imalar.values()) - min(imalar.values())) / p * 100, 1),
             "guven": ("orta" if (max(imalar.values()) - min(imalar.values())) / p <= 1.0 else "dusuk"),
             **{k: round(x, 2) for k, x in imalar.items()},
             "fk_usd": fk and fk.get("son"), "fk_usd_medyan": fk and fk.get("medyan"),
             "pddd_usd": pd_.get("son"), "pddd_usd_medyan": pd_.get("medyan"), "pddd_yuzdelik": pd_.get("yuzdelik"),
             "roe_usd": roe, "makul_pddd": round(roe / 100.0 / KE, 2) if roe and roe > 0 else None,
             "yahoo_hedef": hedef, "yahoo_analist": n, "yahoo_oneri": oneri,
             "yahoo_potansiyel_pct": round((hedef / p - 1) * 100, 1) if hedef else None,
             "repo_hedef": (rh.get(kod) or {}).get("yeni_hedef"), "repo_hedef_kurum": (rh.get(kod) or {}).get("kurum"),
             "repo_hedef_tarih": (rh.get(kod) or {}).get("tarih"),
             "banka": v.get("banka"), "kapsam_disi": kod in kd, "son_bilanco": v.get("son_bilanco")}
        satir.append(r)
    satir.sort(key=lambda r: -r["potansiyel_pct"])
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "ozkaynak_maliyeti_usd_pct": round(KE * 100, 2), "parametreler": {"RF_USD": RF, "CDS_TR": CDS, "ERP": ERP},
           "carpan_kaynagi": GIRDI, "carpan_uretim_utc": c.get("olusturma_utc"), "carpan_yasi_saat": yas_saat,
           "uyari_bayat_carpan": bool(yas_saat and yas_saat > 6),
           "not": "Salt olcum, tavsiye degildir. Tahmini deger = uc yontemin medyani. yontem_dagilimi_pct yuksekse belirsizlik yuksektir.",
           "atlanan": atlanan, "satirlar": satir}
    json.dump(out, open("data/deger_tarama.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pd.DataFrame(satir).to_csv("data/deger_tarama.csv", index=False)
    print(f"Ozkaynak maliyeti {KE*100:.2f}% | {len(satir)} hisse, {len(atlanan)} atlandi")
    for r in satir[:15]:
        print(r["kod"], r["fiyat"], r["tahmini_deger"], r["potansiyel_pct"], r["yontem_sayisi"], r.get("yahoo_potansiyel_pct"))


if __name__ == "__main__":
    main()
