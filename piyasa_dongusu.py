"""
PIYASA DONGUSU GOSTERGESI (04.11.2026) - SALT BETIMLEME, TEST/HUKUM DEGIL, TAVSIYE DEGILDIR.
Haftalik brifing icin BIST 100'un dongu konumu:
  1) Zirveden uzaklik (TL, USD, reel TL), zirveden bu yana seans, 100/200 gunluk ortalamaya uzaklik,
     ortalama altinda kesintisiz seri.
  2) Gecmis dususler ve toparlanma sureleri (tum XU100 gecmisi): zirve -> dip -> eski zirveye donus,
     dip sonrasi 200 gunluk ortalama ustunde 5. kapanis.
  3) Buffett rasyosu (piyasa degeri / GSYH): piyasa degeri arsivdeki endeks agirlik dosyasindan
     (XUTUM: toplam pay sayisi x fiyat), XUTUM degisimiyle bugune tasinir; GSYH EVDS'den son 4 ceyrek.
     Kendi serimiz bugunden itibaren biriktirilir (data/piyasa_dongusu/buffett_seri.json).
Girdi : yfinance (XU100.IS, XUTUM.IS, TRY=X yedek), EVDS (TP.DK.USD.A.YTL, TP.TUKFIY2025.GENEL,
        TP.GSYIH20.BY.B1GQ; anahtar TCMB_EVDS_API_KEY), data/arsiv/endeks_agirlik/*.csv.gz
Cikti : data/piyasa_dongusu/sonuc.json, sonuc.md, buffett_seri.json
"""
import os, re, io, csv, glob, gzip, json, datetime
import numpy as np
import pandas as pd

CIKTI = "data/piyasa_dongusu"
ESIK = {"TL": 0.15, "USD": 0.25, "REEL_TL": 0.20}   # dongu sayilacak asgari zirveden kayip
DIS_BUFFETT = {"ortalama_pct": 25.4, "aralik": "1993-2025", "kaynak": "Dunya Bankasi / WFE (paylasilan infografik)"}
HATA = []


# ------------------------------------------------------------------ veri
def yf_seri(kod, start="1990-01-01"):
    import yfinance as yf
    df = yf.Ticker(kod).history(start=start, interval="1d", auto_adjust=False)
    s = df["Close"].dropna()
    s = s[s > 0]
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    # 2020 "iki sifir atma" gibi olcek kirilmalari: tek gunde 20 kattan buyuk sicrama varsa oncesi olceklenir
    r = s / s.shift(1)
    for t in list(r.index[(r > 20) | (r < 0.05)]):
        f = float(s[t] / s.shift(1)[t])
        s[s.index < t] = s[s.index < t] * f
    return s


def evds(kod, bas="1995-01-01"):
    anahtar = os.environ.get("TCMB_EVDS_API_KEY")
    if not anahtar:
        return None
    from tcmb_evds_veri import evds_veri_cek
    alan, out = kod.replace(".", "_"), {}
    y0, y1 = int(bas[:4]), datetime.date.today().year
    adim = 1 if "DK.USD" in kod else 10
    y = y0
    while y <= y1:
        b, e = datetime.date(y, 1, 1), datetime.date(min(y + adim - 1, y1), 12, 31)
        try:
            for k in (evds_veri_cek(kod, b, e, anahtar).get("items") or []):
                v, t = k.get(alan), str(k.get("Tarih", ""))
                try:
                    v = float(v)
                except (TypeError, ValueError):
                    continue
                if re.match(r"^\d{2}-\d{2}-\d{4}$", t):
                    d = pd.to_datetime(t, format="%d-%m-%Y")
                elif re.match(r"^\d{4}-Q\d$", t):
                    d = pd.Period(t.replace("-", ""), freq="Q").end_time.normalize()
                elif re.match(r"^\d{4}-\d{1,2}$", t):
                    d = pd.Period(t, freq="M").end_time.normalize()
                else:
                    continue
                out[d] = v
        except Exception as ex:
            HATA.append(f"evds {kod} {y}: {str(ex)[:80]}")
        y += adim
    return pd.Series(out).sort_index() if out else None


# ------------------------------------------------------------------ olculer
def durum(s):
    s = s.dropna()
    tepe = s.cummax()
    dd = s / tepe - 1
    i_tepe = s[: s.index[-1]].idxmax()
    sma100, sma200 = s.rolling(100).mean(), s.rolling(200).mean()
    def seri_alti(sma):
        alt = (s < sma).values[::-1]
        n = 0
        for a in alt:
            if not a:
                break
            n += 1
        return n
    return {"son_tarih": str(s.index[-1].date()), "son": round(float(s.iloc[-1]), 2),
            "zirve": round(float(s[i_tepe]), 2), "zirve_tarih": str(i_tepe.date()),
            "zirveden_uzaklik_pct": round(float(dd.iloc[-1]) * 100, 1),
            "zirveden_bu_yana_seans": int((s.index > i_tepe).sum()),
            "sma100_uzaklik_pct": round(float(s.iloc[-1] / sma100.iloc[-1] - 1) * 100, 1) if np.isfinite(sma100.iloc[-1]) else None,
            "sma200_uzaklik_pct": round(float(s.iloc[-1] / sma200.iloc[-1] - 1) * 100, 1) if np.isfinite(sma200.iloc[-1]) else None,
            "sma100_alti_seri_seans": seri_alti(sma100), "sma200_alti_seri_seans": seri_alti(sma200)}


def donguler(s, esik):
    s = s.dropna()
    sma200 = s.rolling(200).mean()
    v, idx = s.values, s.index
    out, i, n = [], 0, len(v)
    tepe_i = 0
    while i < n:
        if v[i] >= v[tepe_i]:
            tepe_i = i
        elif v[i] / v[tepe_i] - 1 <= -esik:
            # dongu basladi: dip ve donus ara
            j, dip_i = i, i
            while j < n and v[j] < v[tepe_i]:
                if v[j] < v[dip_i]:
                    dip_i = j
                j += 1
            donus_i = j if j < n else None
            say, bes = 0, None
            for k in range(dip_i + 1, n):                       # ust uste 5 kapanis
                if np.isfinite(sma200.iloc[k]) and v[k] > sma200.iloc[k]:
                    say += 1
                    if say == 5:
                        bes = str(idx[k].date())
                        break
                else:
                    say = 0
            out.append({"zirve": str(idx[tepe_i].date()), "dip": str(idx[dip_i].date()),
                        "kayip_pct": round((v[dip_i] / v[tepe_i] - 1) * 100, 1),
                        "zirveden_dibe_seans": dip_i - tepe_i,
                        "eski_zirveye_donus": str(idx[donus_i].date()) if donus_i is not None else None,
                        "dipten_donus_seans": (donus_i - dip_i) if donus_i is not None else None,
                        "toplam_seans": (donus_i - tepe_i) if donus_i is not None else n - 1 - tepe_i,
                        "dip_sonrasi_sma200_5_kapanis": bes, "devam_ediyor": donus_i is None})
            if donus_i is None:
                break
            i, tepe_i = donus_i, donus_i
            continue
        i += 1
    return out


def ozet_istatistik(dl):
    tam = [d for d in dl if not d["devam_ediyor"]]
    if not tam:
        return None
    f = lambda a: [d[a] for d in tam]
    return {"dongu_sayisi": len(tam), "kayip_medyan_pct": round(float(np.median(f("kayip_pct"))), 1),
            "kayip_en_derin_pct": float(min(f("kayip_pct"))),
            "dipten_donus_medyan_seans": int(np.median(f("dipten_donus_seans"))),
            "dipten_donus_aralik_seans": [int(min(f("dipten_donus_seans"))), int(max(f("dipten_donus_seans")))],
            "toplam_medyan_seans": int(np.median(f("toplam_seans")))}


def buffett(xutum, yedek):
    dosyalar = sorted(glob.glob("data/arsiv/endeks_agirlik/*.csv.gz"))
    if not dosyalar:
        return {"hata": "agirlik arsivi yok"}
    r = list(csv.reader(io.StringIO(gzip.open(dosyalar[-1]).read().decode("utf-8-sig", errors="replace")), delimiter=";"))
    tarih, pd_tl, gor = None, 0.0, set()
    for x in r[1:]:
        if len(x) > 13 and x[1].strip() == "XUTUM" and "SONRASI" in x[6].upper() and x[9] not in gor:
            try:
                pd_tl += float(x[11]) * float(x[13])
                gor.add(x[9])
                tarih = x[0].strip()
            except ValueError:
                pass
    if not gor:
        return {"hata": "XUTUM satiri yok"}
    t0 = pd.to_datetime(tarih, format="%d/%m/%Y")
    tasiyici = "XUTUM"
    x0 = xutum[xutum.index <= t0] if xutum is not None else pd.Series(dtype=float)
    if x0.empty or (xutum.index[-1] - t0).days < 0:
        xutum, tasiyici = yedek, "XU100 (XUTUM serisi yetersiz, yaklasik)"
        x0 = xutum[xutum.index <= t0]
        HATA.append("Buffett tasimasi XU100 ile")
    tasima = float(xutum.iloc[-1] / x0.iloc[-1])
    pd_bugun = pd_tl * tasima
    g = evds("TP.GSYIH20.BY.B1GQ", "2023-01-01")
    if g is None or len(g) < 4:
        return {"piyasa_degeri_trilyon_tl": round(pd_bugun / 1e12, 2), "hata": "GSYH alinamadi (EVDS anahtari?)"}
    gsyh = float(g.iloc[-4:].sum()) * 1000                     # bin TL -> TL
    oran = pd_bugun / gsyh * 100
    return {"oran_pct": round(oran, 1), "piyasa_degeri_trilyon_tl": round(pd_bugun / 1e12, 2),
            "piyasa_degeri_kaynak": f"endeks agirlik dosyasi {tarih} (XUTUM {len(gor)} pay), {tasiyici} ile {str(xutum.index[-1].date())}'e tasindi (x{tasima:.3f})",
            "gsyh_son4ceyrek_trilyon_tl": round(gsyh / 1e12, 2), "gsyh_son_ceyrek": str(g.index[-1].date()),
            "dis_kaynak_karsilastirma": DIS_BUFFETT,
            "dis_ortalamaya_gore_pct": round((oran / DIS_BUFFETT["ortalama_pct"] - 1) * 100, 1),
            "not": "Dis kaynak ortalamasi farkli tanimla hesaplanmis olabilir; kendi serimiz bugunden itibaren birikir."}


# ------------------------------------------------------------------ genislik (hisse bazinda)
def uyeler_bugun():
    try:
        u = json.load(open("data/endeks_uyelik/donemsel.json", encoding="utf-8"))["uyelik"]
        bugun = datetime.date.today().isoformat()
        anahtar = max(k for k in u if k[:4].isdigit() and k <= bugun)
        return sorted(u[anahtar]["XU100"]), anahtar
    except Exception as ex:
        HATA.append(f"uyelik: {str(ex)[:60]}")
        return None, None


def genislik_panel(kodlar):
    import yfinance as yf
    df = yf.download([k + ".IS" for k in kodlar], period="3y", interval="1d", auto_adjust=False,
                     progress=False, threads=True, group_by="column")["Close"]
    df.columns = [c.replace(".IS", "") for c in df.columns]
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    return df.dropna(how="all")


def genislik(P):
    s50, s200 = P.rolling(50, min_periods=50).mean(), P.rolling(200, min_periods=200).mean()
    hi = P.rolling(250, min_periods=200).max()
    lo = P.rolling(250, min_periods=200).min()
    dd = (P / hi - 1) * 100
    def satir(t):
        g = lambda m, s: round(float((P.loc[t] > s.loc[t]).sum() / s.loc[t].notna().sum() * 100), 1) if s.loc[t].notna().sum() else None
        d = dd.loc[t].dropna()
        return {"tarih": str(t.date()), "n": int(d.size), "sma50_ustu_pct": g(P, s50), "sma200_ustu_pct": g(P, s200),
                "zirveden_medyan_pct": round(float(d.median()), 1) if d.size else None,
                "zirveye_5pct_yakin_n": int((d > -5).sum()), "zirveden_40pct_derin_n": int((d < -40).sum()),
                "52h_yeni_zirve_n": int((P.loc[t] >= hi.loc[t]).sum()), "52h_yeni_dip_n": int((P.loc[t] <= lo.loc[t]).sum())}
    gecerli = [t for t in P.index if s200.loc[t].notna().sum() >= 20]
    haftalik = sorted({max(t for t in gecerli if t.isocalendar()[:2] == w.isocalendar()[:2]) for w in gecerli})
    son = dd.iloc[-1].dropna().sort_values()
    return {"son": satir(P.index[-1]), "haftalik": [satir(t) for t in haftalik],
            "en_derin_5": {k: round(float(v), 1) for k, v in son.head(5).items()},
            "zirveye_en_yakin_5": {k: round(float(v), 1) for k, v in son.tail(5)[::-1].items()},
            "not": "Bugunku XU100 uyeleri; endeksten cikmis hisseler yok (hayatta kalma yanliligi). Ham kapanis (temettu/bolunme duzeltmesiz)."}


# ------------------------------------------------------------------ ana
def main():
    os.makedirs(CIKTI, exist_ok=True)
    xu = yf_seri("XU100.IS")
    usd = evds("TP.DK.USD.A.YTL", "1996-01-01")
    if usd is None or len(usd) < 1000:
        usd = yf_seri("TRY=X", "2000-01-01")
        HATA.append("USD/TRY yfinance yedeginden")
    usd = usd.reindex(xu.index, method="ffill")
    tufe = evds("TP.TUKFIY2025.GENEL", "2005-01-01")
    seriler = {"TL": xu, "USD": (xu / usd).dropna()}
    if tufe is not None and len(tufe) > 24:
        t = tufe.reindex(xu.index, method="ffill").dropna()
        seriler["REEL_TL"] = (xu.reindex(t.index) / t).dropna()
    try:
        xutum = yf_seri("XUTUM.IS")
    except Exception as e:
        xutum = None
        HATA.append(f"XUTUM: {str(e)[:60]}")

    out = {"uretim_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "not": "Betimleyici gosterge; test/hukum degildir, tavsiye degildir. Dipler sonradan belirlenir.",
           "veri_baslangic": {k: str(v.index[0].date()) for k, v in seriler.items()}, "durum": {}, "donguler": {}, "ozet": {}}
    for ad, s in seriler.items():
        out["durum"][ad] = durum(s)
        dl = donguler(s, ESIK[ad])
        out["donguler"][ad] = dl
        out["ozet"][ad] = ozet_istatistik(dl)
    out["buffett"] = buffett(xutum, xu)
    kodlar, uy_tarih = uyeler_bugun()
    try:
        out["genislik"] = genislik(genislik_panel(kodlar)) if kodlar else {"hata": "uyelik yok"}
        out["genislik"]["uyelik_donemi"] = uy_tarih
    except Exception as ex:
        out["genislik"] = {"hata": str(ex)[:120]}
    out["hatalar"] = HATA[-20:]
    json.dump(out, open(f"{CIKTI}/sonuc.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    b = out["buffett"]
    if "oran_pct" in b:
        yol = f"{CIKTI}/buffett_seri.json"
        seri = json.load(open(yol, encoding="utf-8")) if os.path.exists(yol) else {}
        seri[str(xu.index[-1].date())] = {"oran_pct": b["oran_pct"], "pd_trilyon_tl": b["piyasa_degeri_trilyon_tl"], "gsyh_trilyon_tl": b["gsyh_son4ceyrek_trilyon_tl"]}
        json.dump(dict(sorted(seri.items())), open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    L = ["# Piyasa dongusu gostergesi (BIST 100)", "", f"Uretim {out['uretim_utc'][:16]} UTC. Betimleyici; test/hukum ve tavsiye degildir.", "",
         "## Bugunku konum", "", "| Olcu | TL | USD | Reel TL |", "|---|---|---|---|"]
    d = out["durum"]
    g = lambda a, k: d.get(a, {}).get(k)
    for etiket, k in [("Son tarih", "son_tarih"), ("Zirveden uzaklik %", "zirveden_uzaklik_pct"), ("Zirve tarihi", "zirve_tarih"),
                      ("Zirveden bu yana seans", "zirveden_bu_yana_seans"), ("100 g ort. uzaklik %", "sma100_uzaklik_pct"),
                      ("200 g ort. uzaklik %", "sma200_uzaklik_pct"), ("100 g ort. altinda seri (seans)", "sma100_alti_seri_seans"),
                      ("200 g ort. altinda seri (seans)", "sma200_alti_seri_seans")]:
        L.append(f"| {etiket} | {g('TL', k)} | {g('USD', k)} | {g('REEL_TL', k)} |")
    L += ["", "## Buffett rasyosu", ""]
    L += [f"- Oran: **%{b.get('oran_pct')}** (dis kaynak 1993-2025 ortalamasi %{DIS_BUFFETT['ortalama_pct']}; fark %{b.get('dis_ortalamaya_gore_pct')})",
          f"- Piyasa degeri {b.get('piyasa_degeri_trilyon_tl')} trilyon TL / GSYH (son 4 ceyrek, {b.get('gsyh_son_ceyrek')}) {b.get('gsyh_son4ceyrek_trilyon_tl')} trilyon TL",
          f"- {b.get('piyasa_degeri_kaynak', b.get('hata', ''))}"]
    for ad in seriler:
        L += ["", f"## Gecmis donguler - {ad} (esik %{int(ESIK[ad] * 100)}, veri {out['veri_baslangic'][ad]}'den)", "",
              "| Zirve | Dip | Kayip % | Zirve->dip seans | Eski zirveye donus | Dipten donus seans | Toplam seans | Dip sonrasi 200g ust 5. kapanis |",
              "|---|---|---|---|---|---|---|---|"]
        for c in out["donguler"][ad]:
            L.append(f"| {c['zirve']} | {c['dip']} | {c['kayip_pct']} | {c['zirveden_dibe_seans']} | {c['eski_zirveye_donus'] or 'devam ediyor'} | "
                     f"{c['dipten_donus_seans'] if c['dipten_donus_seans'] is not None else '-'} | {c['toplam_seans']} | {c['dip_sonrasi_sma200_5_kapanis'] or '-'} |")
        L.append(f"\nOzet (tamamlanmis donguler): {out['ozet'][ad]}")
    G = out["genislik"]
    L += ["", f"## Genislik - XU100 uyeleri (uyelik donemi {G.get('uyelik_donemi')})", ""]
    if "son" in G:
        L += ["| Hafta sonu | n | 50g ust % | 200g ust % | Zirveden medyan % | Zirveye <%5 | Zirveden -%40 derin | 52h yeni zirve | 52h yeni dip |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in G["haftalik"][-26:]:
            L.append(f"| {r['tarih']} | {r['n']} | {r['sma50_ustu_pct']} | {r['sma200_ustu_pct']} | {r['zirveden_medyan_pct']} | {r['zirveye_5pct_yakin_n']} | {r['zirveden_40pct_derin_n']} | {r['52h_yeni_zirve_n']} | {r['52h_yeni_dip_n']} |")
        L += ["", f"Zirveye en yakin: {G['zirveye_en_yakin_5']} | En derin: {G['en_derin_5']}", "", G["not"]]
    else:
        L.append(f"Hata: {G.get('hata')}")
    L += ["", f"Hatalar: {out['hatalar']}"]
    open(f"{CIKTI}/sonuc.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
