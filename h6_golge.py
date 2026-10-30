"""
H6 GOLGE IZLEME (30.10.2026) - SALT OLCUM, Pine'a dokunmaz. TAVSIYE DEGILDIR.
Kurallar: ON_KAYIT_H6_GOLGE.md (+ ON_KAYIT_H6.md). Listeler olusum ayinin son islem gunu kapanisiyla
dondurulur, bir daha degismez.
Cikti : data/h6/golge.json (kalici kayit), data/h6/golge.md
"""
import os, json, math, datetime
import numpy as np
import pandas as pd

from h_testleri import panel_kur, sha256
from h4_bilanco_surprizi import liste_oku
from h6_faktor_siralama import (temel_tablo, faktor_tablosu, siralar, ay_sonlari, MALIYET, DILIM, MIN_SIRALI, MIN_FAKTOR)

ON_KAYIT = "ON_KAYIT_H6_GOLGE.md"
YOL = "data/h6/golge.json"
ILK_AY = "2026-10"
HUKUM_AYLARI = [f"{y}-{m:02d}" for y, m in [(2026, 10), (2026, 11), (2026, 12)] + [(2027, k) for k in range(1, 10)]]


def aylar_sonu(idx):
    return [pd.Timestamp(t) for t in ay_sonlari(idx)]


def sec(sk, ust=True):
    sk = sk.dropna()
    if len(sk) < MIN_SIRALI:
        return None
    n = max(5, int(math.floor(DILIM * len(sk))))
    return list((sk.nlargest(n) if ust else sk.nsmallest(n)).index)


def main():
    kd = set(liste_oku("config/kapsam_disi.txt"))
    evren = [k for k in liste_oku("config/bist100_uyeler.txt") if os.path.exists(f"data/temel/ham_{k}.json") and k not in kd]
    C, _, _, hata = panel_kur(evren, {})
    C = C[C.index >= pd.Timestamp("2024-06-01")]
    R = C.pct_change()
    temel = {k: temel_tablo(k) for k in C.columns}
    kayit = json.load(open(YOL, encoding="utf-8")) if os.path.exists(YOL) else {"aylar": {}}
    bugun = pd.Timestamp(os.environ.get("H6_BUGUN") or datetime.date.today())   # H6_BUGUN yalniz yerel test
    son_veri = C.index[-1]
    ay_sonu = [t for t in aylar_sonu(C.index) if t.strftime("%Y-%m") >= ILK_AY]
    # ayin son islem gunu: ancak takvim ayi bittiyse kesin (veri o gunden sonra da devam ediyorsa ya da ay bittiyse)
    for t in ay_sonu:
        a = t.strftime("%Y-%m")
        ay_bitti = (t + pd.offsets.MonthEnd(0)) < bugun.normalize() or son_veri > t
        if a in kayit["aylar"] or not ay_bitti:
            continue
        i0 = C.index.get_loc(t)
        r = siralar(faktor_tablosu(C, R, temel, i0))
        bil = r.mean(axis=1).where(r.notna().sum(axis=1) >= MIN_FAKTOR)
        g1, g2, g3 = sec(bil), sec(r["F5_bilanco_surprizi"]), sec(r["F5_bilanco_surprizi"], ust=False)
        if not g1:
            continue
        kayit["aylar"][a] = {"olusum": str(t.date()), "dondurma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                             "sirali": int(bil.notna().sum()), "evren": list(bil.dropna().index),
                             "G1": g1, "G2": g2, "G3": g3, "skor_G1": {k: round(float(bil[k]), 3) for k in g1}}
    # performans
    ay_sirasi = sorted(kayit["aylar"])
    onceki = {}
    for a in ay_sirasi:
        k = kayit["aylar"][a]
        t0 = pd.Timestamp(k["olusum"])
        sonraki = [t for t in aylar_sonu(C.index) if t > t0]
        if not sonraki or t0 not in C.index:
            k["performans"] = None
            continue
        t1 = sonraki[0]
        if t1 == C.index[-1] and (t1 + pd.offsets.MonthEnd(0)) >= bugun.normalize() and son_veri == t1:
            k["performans"] = None            # sonraki ay bitmedi
            continue
        getiri = C.loc[t1] / C.loc[t0] - 1
        ew = float(getiri[k["evren"]].dropna().mean()) * 100
        perf = {"bitis": str(t1.date()), "evren_ort": round(ew, 3)}
        for g in ("G1", "G2", "G3"):
            liste = k.get(g) or []
            r_ = getiri[liste].dropna()
            if r_.empty:
                continue
            brut = float(r_.mean()) * 100
            eski = set(onceki.get(g) or [])
            devir = 1.0 if not eski else len(set(liste) - eski) / len(liste)
            mal = 0.0 if g == "G3" else MALIYET * devir
            perf[g] = {"brut": round(brut, 3), "net_ew": round(brut - mal - ew, 3), "devir": round(devir, 2)}
        k["performans"] = perf
        onceki = {g: k.get(g) for g in ("G1", "G2", "G3")}
    # hukum
    p = [kayit["aylar"].get(a, {}).get("performans") for a in HUKUM_AYLARI]
    if all(p):
        out = {}
        for g in ("G1", "G2"):
            v = [x[g]["net_ew"] for x in p]
            out[g] = "ELENDI" if np.mean(v) <= 0 else ("GECTI" if sum(x > 0 for x in v) >= 7 else "ZAYIF")
        v3 = [x["G3"]["net_ew"] for x in p]
        out["G3_kotu_kurali"] = "TEYIT" if np.mean(v3) < 0 and sum(x < 0 for x in v3) >= 7 else "TEYIT_YOK"
        kayit["hukum"] = {"durum": "VERILDI", **out}
    else:
        kayit["hukum"] = {"durum": "BEKLIYOR", "tamamlanan_ay": sum(1 for x in p if x)}
    kayit.update({"guncelleme_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "on_kayit_sha256": sha256(ON_KAYIT), "fiyat_hatalari": hata})
    os.makedirs("data/h6", exist_ok=True)
    json.dump(kayit, open(YOL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# H6 Golge Izleme", "", f"Guncelleme {kayit['guncelleme_utc'][:16]} UTC | on kayit `{(kayit['on_kayit_sha256'] or '-')[:16]}`",
         "", "Salt olcum, tavsiye degildir. G1 bilesik ust %20, G2 bilanco surprizi ust %20, G3 bilanco surprizi alt %20.",
         "Degerler: evren esit agirlikli ortalamasina gore aylik net (G3'te maliyet yok).", "",
         f"## Hukum: {kayit['hukum']}", "", "| Olusum | Bitis | G1 net | G2 net | G3 net | Evren ort |", "|---|---|---|---|---|---|"]
    for a in ay_sirasi:
        pf = kayit["aylar"][a].get("performans")
        if not pf:
            L.append(f"| {kayit['aylar'][a]['olusum']} | (bekliyor) | - | - | - | - |")
        else:
            L.append(f"| {kayit['aylar'][a]['olusum']} | {pf['bitis']} | {pf.get('G1',{}).get('net_ew')} | {pf.get('G2',{}).get('net_ew')} | "
                     f"{pf.get('G3',{}).get('net_ew')} | {pf['evren_ort']} |")
    if ay_sirasi:
        s = kayit["aylar"][ay_sirasi[-1]]
        L += ["", f"## Son dondurulan liste ({s['olusum']})", f"- G1 bilesik: {', '.join(s['G1'])}",
              f"- G2 bilanco surprizi ust: {', '.join(s.get('G2') or [])}", f"- G3 bilanco surprizi alt: {', '.join(s.get('G3') or [])}"]
    open("data/h6/golge.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("H6 golge:", kayit["hukum"], "| aylar:", ay_sirasi)


if __name__ == "__main__":
    main()
