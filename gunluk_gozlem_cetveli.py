"""
GUNLUK GOZLEM CETVELI (09.08.2026) - Faz V0
Sabah rutini: VIOP acilis gostergesi + kuresel/sektorel baglam +
konsolide_degerlendirme.py'nin TUM katmanlarini (panel/yabanci-akis/
analist/hedef-getiri/portfoy/RSI-gozlem/sinyal-arsivi) TEK bir GUNLUK
tabloda birlestirir.

KIRMIZI CIZGI (Kulucka Protokolu ile UYUM): VIOP verisinden YENI bir
"sinyal" (SQZ vb.) TURETILMEZ - viop_analiz.json'un kendi notu acik:
"18.08.2026'ya kadar SQZ/sinyal hesaplanmaz". Burada VIOP'tan yalniz
TANIMLAYICI bir GOZLEM (futures'in spot'a gore baz/prim yuzdesi)
okunabilir hale getirilir - bu bir SINYAL DEGIL, HAM VERININ
OKUNMASIDIR (konsolide_degerlendirme.py'deki diger katmanlarla ayni
kategori).

DURUST SINIRLAMA: VIOP verisi YALNIZCA 5 sembolde var (AKBNK/YKBNK/
KCHOL/TAVHL/ASTOR - portfoy pozisyonlarimiz), 30 sembolluk evrenin
GERI KALANINDA VIOP sutunu BOS kalir.

Bu, bir "GUNLUK TAHMIN" (AL/SAT tavsiyesi) DEGILDIR - mevcut verinin
konsolide GORUNUMUDUR, yorumlama VE karar insana aittir.
"""
from json_atomik_yaz import atomik_json_yaz
import json, datetime


def _oku(yol, varsayilan=None):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return varsayilan if varsayilan is not None else {}


def viop_baz_bul(viop_veri, sembol):
    veri = viop_veri.get("semboller", {}).get(sembol)
    if not veri:
        return None
    futures = [s for s in veri.get("sozlesmeler", []) if s["sozlesme_turu"] == "FUTURES"]
    if not futures:
        return None
    en_yakin = min(futures, key=lambda s: s["vade_tarihi"])
    return {"spot_fiyat": en_yakin["spot_fiyat"], "futures_fiyat": en_yakin["uzlasma_fiyati"],
            "baz_yuzde": en_yakin["baz_yuzde_ham"], "vade_tarihi": en_yakin["vade_tarihi"]}


def main():
    konsolide = _oku("data/konsolide_degerlendirme.json", {"semboller": []})
    viop = _oku("data/viop_analiz.json", {"semboller": {}})
    kuresel = _oku("data/kuresel_gosterge.json", {})
    sektor = _oku("data/sektor_gosterge.json", {})

    kuresel_ozet = []
    for bolge in ("asya", "avrupa", "amerika"):
        if bolge in kuresel:
            b = kuresel[bolge]
            kuresel_ozet.append(f"{bolge}: {b.get('ozet_yon', '-')} ({b.get('ozet_ortalama_yuzde', '-')}%)")

    satirlar = []
    for s in konsolide.get("semboller", []):
        sembol = s["sembol"]
        v = viop_baz_bul(viop, sembol)
        satir = dict(s)
        satir["viop_baz"] = v
        satirlar.append(satir)
    viop_kapsam_sayisi = sum(1 for s in satirlar if s["viop_baz"])

    rapor = {
        "olusturma_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "viop_bulten_gunu": viop.get("bulten_gunu"),
        "kulucka_notu": ("VIOP'tan YENI sinyal TURETILMEDI - Kulucka Protokolu "
                          "18.08.2026'ya kadar SQZ/sinyal hesaplanmasini yasakliyor. "
                          "Burada yalniz HAM baz/prim yuzdesi okunabilir hale getirildi."),
        "kuresel_baglam": kuresel_ozet,
        "not": ("Bu bir 'AL/SAT tavsiyesi' ya da kesin bir tahmin DEGILDIR - "
                "mevcut verinin GUNLUK konsolide gorunumudur. VIOP sutunu "
                "yalniz VIOP kontrati OLAN sembollerde dolu (asagidaki "
                "viop_kapsam_sayisi'na bakiniz) - kalanlarinda VIOP piyasasi "
                "yok/veri yok."),
        "sembol_sayisi": len(satirlar),
        "viop_kapsam_sayisi": viop_kapsam_sayisi,
        "semboller": satirlar,
    }
    atomik_json_yaz("data/gunluk_gozlem_cetveli.json", rapor)

    md = ["# Gunluk Gozlem Cetveli",
          f"Olusturma: {rapor['olusturma_utc']}",
          f"VIOP bulten gunu: {rapor['viop_bulten_gunu']}", ""]
    if kuresel_ozet:
        md.append("**Kuresel baglam:** " + " | ".join(kuresel_ozet))
        md.append("")
    md.append(f"Bu bir AL/SAT tavsiyesi degildir - mevcut verinin konsolide "
               f"gorunumudur. VIOP sutunu {viop_kapsam_sayisi}/{len(satirlar)} "
               f"semboldeki GERCEK VIOP kontratina gore dolu.")
    md.append("")
    md.append("| Sembol | VIOP Baz% | Panel(N/WR/PF/DD) | Yabanci Akis | Analist | Beklenen Getiri% | Portfoy | RSI Gozlem | Sinyal Ars. | Konsensus |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for s in satirlar:
        v = s["viop_baz"]
        viop_str = f"{v['baz_yuzde']:+.2f}%" if v else "-"
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
        md.append(f"| {s['sembol']} | {viop_str} | {panel_str} | {yabanci_str} | "
                   f"{analist_str} | {hedef_getiri_str} | {portfoy_str} | {rsi_str} | "
                   f"{sinyal_str} | {konsensus_str} |")

    with open("data/gunluk_gozlem_cetveli.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print(f"Yazildi: data/gunluk_gozlem_cetveli.json, data/gunluk_gozlem_cetveli.md")
    print(f"{len(satirlar)} sembol, {sum(1 for s in satirlar if s['viop_baz'])} sembolde VIOP verisi var")


if __name__ == "__main__":
    main()
