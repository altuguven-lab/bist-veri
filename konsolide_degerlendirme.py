"""
KONSOLIDE DEGERLENDIRME RAPORU (08.08.2026) - Faz V0
Bugun kurulan TUM veri katmanlarini (panel, sinyal dogrulama, yabanci
akis, analist gorusu, portfoy, RSI gozlem) SEMBOL BAZINDA TEK bir
tabloda birlestirir - Katman 1-6 mimarisinin gorsel karsiligi.

KIRMIZI CIZGI: bu, bir "AL/SAT tavsiyesi" URETMEZ - yalniz HANGI
kaynaklarin MEVCUT oldugunu ve YONUNU gosterir, YORUMLAMAYI insana
birakir. "Konsensus" sutunu bile SAYISAL bir SAYAC (kac kaynak
pozitif/negatif), OTOMATIK bir KARAR DEGIL.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime

CIKTI_JSON = "data/konsolide_degerlendirme.json"
CIKTI_MD = "data/konsolide_degerlendirme.md"


def _oku(yol, varsayilan=None):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return varsayilan if varsayilan is not None else {}


def en_son_panel(panel_veri, sembol):
    kayitlar = [k for k in panel_veri.get("okumalar", []) if k["sembol"] == sembol]
    if not kayitlar:
        return None
    return max(kayitlar, key=lambda k: k["tarih"])


def en_son_yabanci(yabanci_veri, sembol):
    kayitlar = [k for k in yabanci_veri.get("kayitlar", []) if k["sembol"] == sembol]
    if not kayitlar:
        return None
    return max(kayitlar, key=lambda k: k["tarih"])


def en_son_analist(arastirma_veri, sembol):
    kayitlar = [k for k in arastirma_veri.get("kayitlar", []) if k["sembol"] == sembol]
    if not kayitlar:
        return None
    return max(kayitlar, key=lambda k: k["tarih"])


def portfoy_durumu(portfoy_veri, sembol):
    for p in portfoy_veri.get("acik_pozisyonlar", []):
        if p["sembol"] == sembol:
            return p
    return None


def _portfoy_detay(p, guncel):
    detay = {"giris_fiyat": p["giris_fiyat"], "stop_seviye": p.get("stop_seviye"),
             "etiket": p.get("sinyal_etiketi"), "guncel_fiyat": guncel, "kar_zarar_pct": None}
    if guncel is not None and p["giris_fiyat"]:
        detay["kar_zarar_pct"] = round((guncel / p["giris_fiyat"] - 1) * 100, 2)
    return detay


def rsi_gozlem_durumu(rsi_veri, sembol):
    if sembol in rsi_veri.get("acik_pozisyonlar", {}):
        return ("ACIK", rsi_veri["acik_pozisyonlar"][sembol])
    kapananlar = [k for k in rsi_veri.get("kapanan_pozisyonlar", []) if k["sembol"] == sembol]
    if kapananlar:
        return ("KAPANDI", max(kapananlar, key=lambda k: k["cikis_tarih"]))
    return (None, None)


def sinyal_arsiv_ozet(sinyal_veri, sembol):
    kayitlar = [k for k in sinyal_veri.get("kayitlar", []) if k["sembol"] == sembol]
    dogrulanan = [k for k in kayitlar if k["dogrulama_durumu"] == "DOGRULANDI"]
    return {"toplam": len(kayitlar), "dogrulanan": len(dogrulanan)}


def main():
    evren = _oku("config/universe.yml", {}).get("symbols")
    if not evren:
        import yaml
        with open("config/universe.yml", encoding="utf-8") as f:
            evren = yaml.safe_load(f)["symbols"]

    panel = _oku("data/panel_okuma_arsivi.json", {"okumalar": []})
    yabanci = _oku("data/yabanci_takas_takip.json", {"kayitlar": []})
    arastirma = _oku("data/arastirma_hedef_fiyat.json", {"kayitlar": []})
    portfoy = _oku("data/portfoy.json", {"acik_pozisyonlar": []})
    fiyatlar_ham = _oku("data/bist_quotes.json", {"veriler": []})
    guncel_fiyat = {v["sembol"]: v["son_fiyat"] for v in fiyatlar_ham.get("veriler", [])}
    rsi_gozlem = _oku("data/rsi_gozlem_defteri.json", {"acik_pozisyonlar": {}, "kapanan_pozisyonlar": []})
    sinyal_arsiv = _oku("data/sinyal_arsiv.json", {"kayitlar": []})
    hedef_getiri = _oku("data/hedef_fiyat_getiri_analizi.json", {"sonuclar": []})
    hedef_getiri_map = {s["sembol"]: s for s in hedef_getiri.get("sonuclar", [])}

    satirlar = []
    for sembol in evren:
        p = en_son_panel(panel, sembol)
        y = en_son_yabanci(yabanci, sembol)
        a = en_son_analist(arastirma, sembol)
        pf_poz = portfoy_durumu(portfoy, sembol)
        rsi_durum, rsi_detay = rsi_gozlem_durumu(rsi_gozlem, sembol)
        sinyal_oz = sinyal_arsiv_ozet(sinyal_arsiv, sembol)

        pozitif_sayaci, negatif_sayaci = 0, 0
        if p and p.get("pf") is not None:
            if p["pf"] >= 1.0: pozitif_sayaci += 1
            else: negatif_sayaci += 1
        if y:
            if y["yon"] == "ARTIS": pozitif_sayaci += 1
            elif y["yon"] == "AZALIS": negatif_sayaci += 1
        if a:
            if a.get("yon") == "YUKARI": pozitif_sayaci += 1
            elif a.get("yon") == "ASAGI": negatif_sayaci += 1

        satir = {
            "sembol": sembol,
            "panel": {"tarih": p["tarih"], "n": p["n"], "wr_pct": p["wr_pct"], "pf": p["pf"], "dd": p["dd"]} if p else None,
            "yabanci_akisi": {"tarih": y["tarih"], "yon": y["yon"], "puan_degisimi": y["puan_degisimi"]} if y else None,
            "analist_gorusu": {"tarih": a["tarih"], "yon": a.get("yon"), "kurum": a.get("kurum")} if a else None,
            "portfoy": _portfoy_detay(pf_poz, guncel_fiyat.get(sembol)) if pf_poz else None,
            "rsi_gozlem": {"durum": rsi_durum, "detay": rsi_detay} if rsi_durum else None,
            "sinyal_arsivi": sinyal_oz,
            "hedef_fiyat_getirisi": hedef_getiri_map.get(sembol),
            "kaynak_konsensusu": {"pozitif": pozitif_sayaci, "negatif": negatif_sayaci},
        }
        satirlar.append(satir)

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "not": ("Bu rapor bir AL/SAT tavsiyesi URETMEZ - yalniz mevcut veri "
                "katmanlarini (panel/yabanci-akisi/analist/portfoy/RSI-gozlem/"
                "sinyal-arsivi) SEMBOL bazinda bir araya getirir. "
                "'kaynak_konsensusu' SAYISAL bir sayac, otomatik karar DEGIL."),
        "sembol_sayisi": len(satirlar),
        "semboller": satirlar,
    }
    atomik_json_yaz(CIKTI_JSON, rapor)

    md = ["# Konsolide Degerlendirme Raporu",
          f"Olusturma: {rapor['olusturma_utc']}", "",
          "Bu, bir AL/SAT tavsiyesi degildir - mevcut veri katmanlarini "
          "bir araya getirir, yorumlamayi insana birakir.", "",
          "| Sembol | Panel(N/WR/PF/DD) | Yabanci Akis | Analist | Beklenen Getiri% | Portfoy | RSI Gozlem | Sinyal Ars.(top/dogr) | Konsensus(+/-) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s in satirlar:
        p = s["panel"]
        if p:
            n_g = p['n'] if p['n'] is not None else '-'
            wr_g = f"{p['wr_pct']}%" if p['wr_pct'] is not None else '-'
            dd_g = p['dd'] if p['dd'] is not None else '-'
            panel_str = f"{n_g}/{wr_g}/{p['pf']}/{dd_g}"
        else:
            panel_str = "-"
        y = s["yabanci_akisi"]
        yabanci_str = f"{y['yon']} ({y['puan_degisimi']:+.1f})" if y else "-"
        a = s["analist_gorusu"]
        analist_str = a["yon"] if a else "-"
        hg = s["hedef_fiyat_getirisi"]
        hedef_getiri_str = f"{hg['beklenen_getiri_pct']:+.1f}% ({hg['son_revizyon_yonu']})" if hg else "-"
        pf = s["portfoy"]
        if pf:
            kz = pf["kar_zarar_pct"]
            kz_str = f" ({kz:+.1f}%)" if kz is not None else ""
            portfoy_str = f"{pf['etiket']}@{pf['giris_fiyat']}{kz_str}"
        else:
            portfoy_str = "-"
        rg = s["rsi_gozlem"]
        rsi_str = rg["durum"] if rg else "-"
        sa = s["sinyal_arsivi"]
        sinyal_str = f"{sa['toplam']}/{sa['dogrulanan']}"
        kk = s["kaynak_konsensusu"]
        konsensus_str = f"{kk['pozitif']}/{kk['negatif']}"
        md.append(f"| {s['sembol']} | {panel_str} | {yabanci_str} | {analist_str} | "
                   f"{hedef_getiri_str} | {portfoy_str} | {rsi_str} | {sinyal_str} | {konsensus_str} |")

    with open(CIKTI_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print(f"Yazildi: {CIKTI_JSON}, {CIKTI_MD}")
    print(f"{len(satirlar)} sembol islendi")


if __name__ == "__main__":
    main()
