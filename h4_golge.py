"""
H4 GOLGE IZLEME (27.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H4_GOLGE.md (+ ON_KAYIT_H4.md). Listeler giris gunu dondurulur, bir daha degismez.
Girdi : data/temel/ham_*.json (is akisinda once BIST100 icin tazelenir), fiyat (yfinance)
Cikti : data/h4/golge.json (kalici kayit), data/h4/golge.md
"""
import os, json, datetime
import numpy as np
import pandas as pd

from h_testleri import panel_kur, fiyat_cek, sektor_sepeti, sha256
from h4_bilanco_surprizi import sinyaller, bilgi_tarihi, liste_oku, SEKTOR100, MALIYET, MIN_SIRKET

ON_KAYIT = "ON_KAYIT_H4_GOLGE.md"
YOL = "data/h4/golge.json"
BASLANGIC = (2026, 9)
HUKUM_CEYREKLERI = [(2026, 9), (2026, 12), (2027, 3), (2027, 6)]
UFUK = (10, 20, 40, 60)
BIRINCIL = 40


def ceyrek_listesi(bugun):
    y, p = BASLANGIC
    out = []
    while bilgi_tarihi(y, p) - pd.Timedelta(days=60) <= bugun:   # donem sonu gectiyse listeye al
        out.append((y, p))
        p += 3
        if p > 12:
            y, p = y + 1, 3
    return out


def anahtar(y, p):
    return f"{y}/{p:02d}"


def ilk_islem_gunu(t, gunler):
    i = gunler.searchsorted(t)
    return gunler[i] if i < len(gunler) else None


def performans(kayit, C, sektor_map):
    gunler = C.index
    t0 = pd.Timestamp(kayit["giris"])
    if t0 not in gunler:
        return {}
    i0 = gunler.get_loc(t0)
    out = {}
    for h in UFUK:
        if i0 + h >= len(gunler):
            continue
        f = C.iloc[i0 + h] / C.iloc[i0] - 1
        akran = sektor_sepeti(pd.DataFrame([f.values], columns=C.columns), sektor_map).iloc[0]
        def ort(ks, sek):
            v = [(f[k] - akran[k]) if sek else f[k] for k in ks if k in f and pd.notna(f[k]) and (not sek or pd.notna(akran[k]))]
            return float(np.mean(v)) * 100 if v else None
        iyi_s, kotu_s, iyi_b, kotu_b = ort(kayit["iyi"], True), ort(kayit["kotu"], True), ort(kayit["iyi"], False), ort(kayit["kotu"], False)
        out[str(h)] = {"bitis": str(gunler[i0 + h].date()),
                       "iyi_sek_net": None if iyi_s is None else round(iyi_s - MALIYET, 3),
                       "kotu_sek_net": None if kotu_s is None else round(kotu_s - MALIYET, 3),
                       "fark_brut": None if iyi_b is None or kotu_b is None else round(iyi_b - kotu_b, 3)}
    return out


def hukum(kayitlar):
    p = [kayitlar.get(anahtar(*c), {}).get("performans", {}).get(str(BIRINCIL)) for c in HUKUM_CEYREKLERI]
    if not all(p):
        return {"durum": "BEKLIYOR", "tamamlanan": sum(1 for x in p if x)}
    iyi = [x["iyi_sek_net"] for x in p]
    kotu = [x["kotu_sek_net"] for x in p]
    fark = [x["fark_brut"] for x in p]
    if np.mean(iyi) <= 0:
        e = "ELENDI"
    elif sum(v > 0 for v in iyi) >= 3 and np.mean(fark) > 0:
        e = "GECTI"
    else:
        e = "ZAYIF"
    kotu_kural = "TEYIT" if np.mean(kotu) < 0 and sum(v < 0 for v in kotu) >= 3 else "TEYIT_YOK"
    return {"durum": e, "kotu_kurali": kotu_kural, "iyi": iyi, "kotu": kotu, "fark": fark}


def main():
    # H4_BUGUN yalniz yerel test icindir; is akisinda tanimli degildir.
    bugun = pd.Timestamp(os.environ.get("H4_BUGUN") or datetime.date.today())
    kayit = json.load(open(YOL, encoding="utf-8")) if os.path.exists(YOL) else {"ceyrekler": {}}
    kd = set(liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in liste_oku("config/bist100_uyeler.txt") if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    C, _, _, hata = panel_kur(evren, {})
    C = C[C.index >= pd.Timestamp("2026-06-01")]
    gunler = C.index
    S_tum = sinyaller(list(C.columns))
    sektor_map = dict(SEKTOR100)
    on_liste = {}
    for (y, p) in ceyrek_listesi(bugun):
        a = anahtar(y, p)
        bt = bilgi_tarihi(y, p)
        S = {k: v for k, v in S_tum.get((y, p), {}).items() if k in C.columns}
        mevcut = kayit["ceyrekler"].get(a)
        if mevcut and mevcut.get("durum") == "DONDURULDU":
            continue
        giris = ilk_islem_gunu(bt, gunler)
        sira = sorted(S, key=lambda k: S[k])
        n3 = len(sira) // 3
        if giris is not None and bugun >= giris and len(S) >= MIN_SIRKET:
            kayit["ceyrekler"][a] = {"durum": "DONDURULDU", "bilgi_tarihi": str(bt.date()), "giris": str(giris.date()),
                                     "dondurma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                     "gec_dondurma_gun": int((bugun - giris).days), "sirket": len(S),
                                     "iyi": sira[-n3:][::-1], "kotu": sira[:n3],
                                     "S": {k: round(S[k], 5) for k in sira}}
        else:
            on_liste[a] = {"durum": "ON_LISTE", "bilgi_tarihi": str(bt.date()), "aciklayan_sirket": len(S),
                           "iyi_simdilik": sira[-n3:][::-1] if n3 else [], "kotu_simdilik": sira[:n3] if n3 else []}
    for a, k in kayit["ceyrekler"].items():
        if k.get("durum") == "DONDURULDU":
            k["performans"] = performans(k, C, sektor_map)
    kayit["hukum"] = hukum(kayit["ceyrekler"])
    kayit["on_listeler"] = on_liste
    kayit["guncelleme_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    kayit["on_kayit_sha256"] = sha256(ON_KAYIT)
    kayit["fiyat_hatalari"] = hata
    os.makedirs("data/h4", exist_ok=True)
    json.dump(kayit, open(YOL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    L = ["# H4 Golge Izleme", "", f"Guncelleme {kayit['guncelleme_utc'][:16]} UTC | on kayit `{(kayit['on_kayit_sha256'] or '-')[:16]}`",
         "", "Salt olcum, tavsiye degildir. Listeler giris gunu dondurulur.", "",
         f"## Hukum: {kayit['hukum'].get('durum')}" + (f" | KOTU kurali: {kayit['hukum'].get('kotu_kurali')}" if kayit['hukum'].get('kotu_kurali') else ""), "",
         "## Dondurulmus ceyrekler", "", "| Ceyrek | Giris | Sirket | Ufuk | IYI sek net | KOTU sek net | Fark brut |", "|---|---|---|---|---|---|---|"]
    for a, k in sorted(kayit["ceyrekler"].items()):
        perf = k.get("performans") or {}
        if not perf:
            L.append(f"| {a} | {k['giris']} | {k['sirket']} | - | - | - | - |")
        for h, v in sorted(perf.items(), key=lambda x: int(x[0])):
            L.append(f"| {a} | {k['giris']} | {k['sirket']} | {h} | {v['iyi_sek_net']} | {v['kotu_sek_net']} | {v['fark_brut']} |")
    for a, k in sorted(kayit["ceyrekler"].items()):
        L += ["", f"### {a} listeleri (donduruldu {k['dondurma_utc'][:10]})", f"- IYI: {', '.join(k['iyi'])}", f"- KOTU: {', '.join(k['kotu'])}"]
    for a, k in sorted(on_liste.items()):
        L += ["", f"### {a} on liste (kesin degil; bilgi tarihi {k['bilgi_tarihi']}, aciklayan {k['aciklayan_sirket']} sirket)",
              f"- IYI simdilik: {', '.join(k['iyi_simdilik']) or '-'}", f"- KOTU simdilik: {', '.join(k['kotu_simdilik']) or '-'}"]
    open("data/h4/golge.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("Golge:", kayit["hukum"], "| on liste:", {a: k["aciklayan_sirket"] for a, k in on_liste.items()})


if __name__ == "__main__":
    main()
