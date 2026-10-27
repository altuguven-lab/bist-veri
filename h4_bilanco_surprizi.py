"""
H4 BILANCO SURPRIZI SONRASI SEYIR (27.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Tanimlar ve gecme kriterleri: ON_KAYIT_H4.md (bu betikten ONCE commit edilir). Bu betik parametre secmez.
Girdi : data/temel/ham_*.json (Is Yatirim ceyreklik tablolar), config/bist100_uyeler.txt, config/kapsam_disi.txt
Cikti : data/h4/sonuc.json, data/h4/sonuc.md, data/h4/donemler.csv, data/h4/deneme_kaydi.json
"""
import os, json, glob, math, datetime
from collections import defaultdict

import numpy as np
import pandas as pd

from h_testleri import fiyat_cek, panel_kur, sektor_sepeti, sha256

ON_KAYIT = "ON_KAYIT_H4.md"
CIKTI = "data/h4"
MALIYET = 0.25
T_ESIK = 2.23
GECIKME = {3: 60, 6: 70, 9: 60, 12: 80}
TUTMA = 40
TUTMA_EK = (10, 20, 60)
MIN_SIRKET = 30
IS_ARALIK = ((2021, 3), (2023, 6))
OOS_ARALIK = ((2023, 9), (2026, 3))

# Yaklasik sektor eslemesi (19 grup). Esleme on kayda dahildir; sonuc gorulduktan sonra degistirilmez.
SEKTOR100 = {}
for s, uyeler in {
    "Banka": "AKBNK YKBNK GARAN ISCTR VAKBN HALKB TSKB ALBRK",
    "FinansDiger": "TURSG ANSGR ANHYT ISMEN",
    "Holding": "KCHOL SAHOL ALARK DOHOL AGHOL GLYHO TKFEN ECZYT BRYAT BINHO",
    "Ulastirma": "THYAO PGSUS TAVHL CLEBI TUREX GRSEL RYSAS",
    "Otomotiv": "TOASO FROTO OTKAR DOAS TTRAK KARSN EGEEN",
    "Metal": "EREGL KRDMD ISDMR BRSAN KCAER TCKRC",
    "Madencilik": "TRMET TRALT ALTNY",
    "Enerji": "ENJSA AKSEN ODAS ZOREN ENERY GWIND CANTE ASTOR YEOTK CWENE AHGAZ ENTRA KONTR TRENJ AKFYE",
    "Kimya": "TUPRS PETKM SASA AKSA GUBRF HEKTS AYGAZ KORDS SISE EGGUB",
    "Cimento": "BTCIM CIMSA OYAKC AKCNS LMKDC",
    "Insaat": "ENKAI GLRMK",
    "GYO": "EKGYO SNGYO TRGYO RGYAS",
    "Perakende": "BIMAS MGROS SOKM MAVI",
    "Gida": "ULKER AEFES CCOLA TABGD TUKAS OBAMS",
    "Telekom": "TTKOM TCELL",
    "Dayanikli": "ARCLK VESTL",
    "Saglik": "ECILC MPARK",
    "Spor": "FENER TSPOR",
    "Savunma": "ASELS KATMR",
}.items():
    for k in uyeler.split():
        SEKTOR100[k] = s


def liste_oku(yol):
    if not os.path.exists(yol):
        return []
    out = []
    for s in open(yol, encoding="utf-8"):
        s = s.split("#")[0].strip().upper()
        if s and s not in out:
            out.append(s)
    return out


def kalem(ham, borsa, kod):
    k = ((ham.get(borsa) or {}).get("kalemler") or {}).get(kod) or {}
    out = {}
    for ky, v in (k.get("v") or {}).items():
        try:
            y, p = ky.split("/")
            out[(int(y), int(p))] = float(v)
        except (ValueError, TypeError):
            pass
    return out


def sinyaller(semboller, borsa="TRY"):
    """{(y,p): {kod: S}}"""
    out = defaultdict(dict)
    for kod in semboller:
        yol = f"data/temel/ham_{kod}.json"
        if not os.path.exists(yol):
            continue
        ham = json.load(open(yol, encoding="utf-8"))
        kar, oz = kalem(ham, borsa, "3Z"), kalem(ham, borsa, "2O")
        for (y, p), k in kar.items():
            k0, o0 = kar.get((y - 1, p)), oz.get((y - 1, p))
            if k0 is None or o0 is None or o0 <= 0:
                continue
            out[(y, p)][kod] = (k - k0) / o0
    return out


def bilgi_tarihi(y, p):
    son = pd.Timestamp(year=y, month=p, day=1) + pd.offsets.MonthEnd(0)
    return son + pd.Timedelta(days=GECIKME[p])


def donem_araliginda(yp, aralik):
    return aralik[0] <= yp <= aralik[1]


def portfoyler(S, C, xu, sektor_map, banka_haric=False, haric_sektor=None):
    """Donem basina satir: IYI/KOTU/fark, birincil ve ek ufuklar."""
    gunler = C.index
    satir = []
    tum_ufuk = sorted({TUTMA, *TUTMA_EK})
    akran = {h: sektor_sepeti(C.shift(-h) / C - 1, sektor_map) for h in tum_ufuk}
    ileri = {h: C.shift(-h) / C - 1 for h in tum_ufuk}
    xu_ileri = {h: (xu.shift(-h) / xu - 1) for h in tum_ufuk}
    for (y, p) in sorted(S):
        bt = bilgi_tarihi(y, p)
        poz = gunler.searchsorted(bt)
        if poz >= len(gunler):
            continue
        t0 = gunler[poz]
        sk = {k: v for k, v in S[(y, p)].items() if k in C.columns and pd.notna(C.at[t0, k])
              and not (banka_haric and sektor_map.get(k) == "Banka")
              and not (haric_sektor and sektor_map.get(k) == haric_sektor)}
        if len(sk) < MIN_SIRKET:
            continue
        sira = sorted(sk, key=lambda k: sk[k])
        n3 = len(sira) // 3
        kotu, iyi = sira[:n3], sira[-n3:]
        r = {"donem": f"{y}/{p:02d}", "y": y, "p": p, "giris": str(t0.date()), "sirket": len(sk), "uctebir": n3}
        for h in tum_ufuk:
            if poz + h >= len(gunler):
                continue
            f, a = ileri[h].loc[t0], akran[h].loc[t0]
            def ort(ks, ref):
                v = [(f[k] - ref[k]) if ref is not None else f[k] for k in ks if pd.notna(f[k]) and (ref is None or pd.notna(ref[k]))]
                return float(np.mean(v)) * 100 if v else None
            iyi_sek, kotu_sek = ort(iyi, a), ort(kotu, a)
            iyi_brut, kotu_brut = ort(iyi, None), ort(kotu, None)
            xr = float(xu_ileri[h].loc[t0]) * 100 if pd.notna(xu_ileri[h].loc[t0]) else None
            r[f"iyi_sek_net_{h}"] = None if iyi_sek is None else iyi_sek - MALIYET
            r[f"kotu_sek_net_{h}"] = None if kotu_sek is None else kotu_sek - MALIYET
            r[f"fark_brut_{h}"] = None if iyi_brut is None or kotu_brut is None else iyi_brut - kotu_brut
            r[f"iyi_xu_net_{h}"] = None if iyi_brut is None or xr is None else iyi_brut - xr - MALIYET
        satir.append(r)
    return pd.DataFrame(satir)


def ozet(df, alan, aralik):
    if df.empty or alan not in df:
        return {"n": 0}
    x = df[[donem_araliginda((a, b), aralik) for a, b in zip(df["y"], df["p"])]][alan].dropna()
    n = len(x)
    if n < 3:
        return {"n": n}
    sd = float(x.std(ddof=1))
    return {"n": n, "ort": round(float(x.mean()), 3), "t": round(float(x.mean()) / (sd / math.sqrt(n)), 2) if sd > 0 else None,
            "pozitif_pct": round(100 * float((x > 0).mean()), 1)}


def hukum(df, k4):
    alan = f"iyi_sek_net_{TUTMA}"
    o, i = ozet(df, alan, OOS_ARALIK), ozet(df, alan, IS_ARALIK)
    k = {"K1_oos_ort_pozitif": (o.get("ort") or -1) > 0,
         "K2_oos_t": (o.get("t") or -99) > T_ESIK,
         "K3_oos_donemlerin_60pct_pozitif": (o.get("pozitif_pct") or 0) >= 60,
         "K4_sektor_cikarma": bool(k4) and all(v is not None and v > 0 for v in k4.values()),
         "K5_is_ort_pozitif": (i.get("ort") or -1) > 0}
    e = "GECTI" if all(k.values()) else ("ZAYIF" if k["K1_oos_ort_pozitif"] and k["K5_is_ort_pozitif"] else "ELENDI")
    return e, k, o, i


def md_yaz(out, df):
    b = out["birincil"]
    L = ["# H4 Bilanco Surprizi Sonrasi Seyir", "",
         f"Uretim {out['uretim_utc'][:16]} UTC | on kayit SHA-256 `{(out['on_kayit_sha256'] or '-')[:16]}` | deneme no {out['deneme_no']} | "
         f"maliyet {MALIYET}% | t esigi {T_ESIK}", "", "Salt olcum, tavsiye degildir. Kurallar ON_KAYIT_H4.md'de.", "",
         "## Hukum", "", "| Metrik | IS ort (t, n) | OOS ort (t, n) | OOS pozitif % | Hukum |", "|---|---|---|---|---|",
         f"| IYI ucte bir, sektore gore net, {TUTMA} gun | {b['IS'].get('ort')} ({b['IS'].get('t')}, {b['IS'].get('n')}) | "
         f"{b['OOS'].get('ort')} ({b['OOS'].get('t')}, {b['OOS'].get('n')}) | {b['OOS'].get('pozitif_pct')} | **{out['hukum']}** |", ""]
    L += [f"- {k}: {'EVET' if v else 'HAYIR'}" for k, v in out["kriterler"].items()]
    L.append(f"- Sektor cikarma OOS: {out['sektor_cikarma_oos']}")
    L += ["", "## Hukum vermeyenler (OOS)", "", "| Metrik | Ufuk | ort | t | n |", "|---|---|---|---|---|"]
    for ad, v in out["ek"].items():
        L.append(f"| {ad} | {v.get('ufuk')} | {v['OOS'].get('ort')} | {v['OOS'].get('t')} | {v['OOS'].get('n')} |")
    L += ["", "## Donem tablosu (birincil ufuk)", "", "| Donem | Giris | Sirket | IYI sek net | KOTU sek net | Fark brut |", "|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        g = lambda c: None if pd.isna(r.get(c)) else round(r.get(c), 2)
        L.append(f"| {r['donem']} | {r['giris']} | {r['sirket']} | {g(f'iyi_sek_net_{TUTMA}')} | {g(f'kotu_sek_net_{TUTMA}')} | {g(f'fark_brut_{TUTMA}')} |")
    L += ["", f"Fiyati cekilemeyen: {out['veri']['hata'] or 'yok'} | sektor eslemesi olmayan: {out['veri']['eslesmeyen'] or 'yok'}",
          "", "Bilinen sinirlar: hayatta kalma yanliligi, nokta-zaman verisi degil, TMS 29 kirilmasi, uzlasi tahmini yok, aciklama tarihleri yaklasik."]
    return "\n".join(L) + "\n"


def main():
    kd = set(liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in liste_oku("config/bist100_uyeler.txt") if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    C, _, _, hata = panel_kur(evren, {})
    C = C[C.index >= pd.Timestamp("2020-06-01")]
    xu = fiyat_cek("XU100")[0]["Close"].reindex(C.index).ffill()
    S = sinyaller(list(C.columns))
    sektor_map = dict(SEKTOR100)

    df = portfoyler(S, C, xu, sektor_map)
    sektorler = sorted({sektor_map[k] for k in C.columns if k in sektor_map})
    k4 = {}
    for s in sektorler:
        d2 = portfoyler(S, C[[k for k in C.columns if sektor_map.get(k) != s]], xu, sektor_map)
        k4[s] = ozet(d2, f"iyi_sek_net_{TUTMA}", OOS_ARALIK).get("ort")
    e, k, o, i = hukum(df, k4)

    ek = {}
    for h in sorted({TUTMA, *TUTMA_EK}):
        ek[f"IYI-KOTU fark brut {h}g"] = {"ufuk": h, "OOS": ozet(df, f"fark_brut_{h}", OOS_ARALIK), "IS": ozet(df, f"fark_brut_{h}", IS_ARALIK)}
        ek[f"KOTU sektore gore net {h}g"] = {"ufuk": h, "OOS": ozet(df, f"kotu_sek_net_{h}", OOS_ARALIK), "IS": ozet(df, f"kotu_sek_net_{h}", IS_ARALIK)}
        ek[f"IYI XU100'e gore net {h}g"] = {"ufuk": h, "OOS": ozet(df, f"iyi_xu_net_{h}", OOS_ARALIK), "IS": ozet(df, f"iyi_xu_net_{h}", IS_ARALIK)}
        if h != TUTMA:
            ek[f"IYI sektore gore net {h}g"] = {"ufuk": h, "OOS": ozet(df, f"iyi_sek_net_{h}", OOS_ARALIK), "IS": ozet(df, f"iyi_sek_net_{h}", IS_ARALIK)}
    dfb = portfoyler(S, C, xu, sektor_map, banka_haric=True)
    ek[f"Bankalar haric IYI sek net {TUTMA}g"] = {"ufuk": TUTMA, "OOS": ozet(dfb, f"iyi_sek_net_{TUTMA}", OOS_ARALIK)}
    dfu = portfoyler(sinyaller(list(C.columns), "USD"), C, xu, sektor_map)
    ek[f"USD tablolar IYI sek net {TUTMA}g"] = {"ufuk": TUTMA, "OOS": ozet(dfu, f"iyi_sek_net_{TUTMA}", OOS_ARALIK)}
    taze = df[[(a, b) > OOS_ARALIK[1] for a, b in zip(df["y"], df["p"])]] if len(df) else df

    os.makedirs(CIKTI, exist_ok=True)
    kayit_yol = f"{CIKTI}/deneme_kaydi.json"
    kayit = json.load(open(kayit_yol, encoding="utf-8")) if os.path.exists(kayit_yol) else {"denemeler": []}
    sha = sha256(ON_KAYIT)
    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "surum": "v1", "on_kayit_sha256": sha,
           "deneme_no": len(kayit["denemeler"]) + 1,
           "parametreler": {"MALIYET": MALIYET, "T_ESIK": T_ESIK, "GECIKME": GECIKME, "TUTMA": TUTMA, "MIN_SIRKET": MIN_SIRKET,
                            "IS": IS_ARALIK, "OOS": OOS_ARALIK},
           "birincil": {"OOS": o, "IS": i}, "hukum": e, "kriterler": k, "sektor_cikarma_oos": k4, "ek": ek,
           "taze_donem": taze.to_dict("records") if len(taze) else [],
           "veri": {"evren": len(evren), "fiyatli": len(C.columns), "hata": hata,
                    "eslesmeyen": [k for k in C.columns if k not in sektor_map],
                    "kapsam_disi_cikarilan": sorted(kd), "donem_sayisi": len(df)}}
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    df.to_csv(f"{CIKTI}/donemler.csv", index=False)
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write(md_yaz(out, df))
    kayit["denemeler"].append({"zaman_utc": out["uretim_utc"], "on_kayit_sha256": sha, "git_sha": os.environ.get("GITHUB_SHA"), "hukum": e})
    json.dump(kayit, open(kayit_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("H4", e, "OOS", o, "IS", i)


if __name__ == "__main__":
    main()
