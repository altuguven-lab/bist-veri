#!/usr/bin/env python3
"""
MAKRO AKIM VE REEL FAIZ (19.11.2026) - SALT OLCUM, TAVSIYE DEGILDIR.

Neden: 19.11 kurum raporu karsilastirmasinda (JPMorgan, BofA, BlackRock) iki eksik bulundu:
  (1) yabancinin PIYASA TOPLAMI hisse/DIBS akimi (bizde yalniz hisse bazli yabanci payi vardi),
  (2) reel faiz ve enflasyon beklentisi serisi (deger_tarama'da risk primi ve faiz sabit giriliyordu).

Kaynak: TCMB EVDS (birincil). Anahtar TCMB_EVDS_API_KEY (GitHub Secret), istek basliginda gonderilir.
Seriler (19.11'de EVDS'de dogrulandi):
  TP.MKNETHAR.M7  Yurt disi yerlesikler, hisse senedi NET HAREKET (haftalik, Cuma, milyon USD, fiyat/kur etkisinden arindirilmis)
  TP.MKNETHAR.M8  Yurt disi yerlesikler, DIBS (kesin alim) NET HAREKET (haftalik, milyon USD)
  TP.MKNETHAR.M1  Yurt disi yerlesikler, hisse senedi STOK (haftalik, milyon USD, piyasa degeriyle)
  TP.BEK.S01.E.U  Piyasa Katilimcilari Anketi: 12 ay sonrasi yillik TUFE beklentisi (aylik, %)
  TP.BEK.S01.I.U  Piyasa Katilimcilari Anketi: gelecek yil sonu TUFE beklentisi (aylik, %)
  TP.PKAUO.S04.D.U Piyasa Katilimcilari Anketi: 12 ay sonrasi politika faizi beklentisi (aylik, %)
  TP.APIFON4      TCMB agirlikli ortalama fonlama maliyeti (is gunu, %) - reel faiz hesabinin ESAS serisi
  TP.BISTTLREF.ORAN BIST TLREF gecelik referans faiz (is gunu, %)
  TP.AB.TOPLAM    TCMB brut uluslararasi rezervleri, toplam (haftalik, Cuma, milyon USD) - 19.11 eki
  TP.RK.T1.Y      TUFE bazli reel efektif doviz kuru (2025=100, aylik; artis = TL reel degerlenme) - 19.11 eki
  TP.BISPOLFAIZ.TUR Politika faizi (BIS karsilastirma serisi, aylik; GECIKMELI - 19.11'de son gozlem Agustos %37,
                  fonlama maliyeti ise %36 idi; yalniz kiyas icin tutulur)
Turetilen (betimleyici, sinyal DEGIL): ex-ante reel faiz = politika faizi - 12 ay sonrasi TUFE beklentisi;
  piyasanin ima ettigi faiz degisimi = 12 ay sonrasi politika faizi beklentisi - bugunku politika faizi.
Cikti: data/makro_akim_reel.json, data/makro_akim_reel.md
Bir seri gelmezse digerleri yazilir; hicbiri gelmezse mevcut dosya korunur.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/series={seri}&startDate={bas}&endDate={bit}&type=json"
SERILER = {
    "yabanci_hisse_net_mn_usd": ("TP.MKNETHAR.M7", "haftalik"),
    "yabanci_dibs_net_mn_usd": ("TP.MKNETHAR.M8", "haftalik"),
    "yabanci_hisse_stok_mn_usd": ("TP.MKNETHAR.M1", "haftalik"),
    "tufe_beklenti_12ay_pct": ("TP.BEK.S01.E.U", "aylik"),
    "tufe_beklenti_gelecek_yil_sonu_pct": ("TP.BEK.S01.I.U", "aylik"),
    "politika_faizi_beklenti_12ay_pct": ("TP.PKAUO.S04.D.U", "aylik"),
    "fonlama_maliyeti_pct": ("TP.APIFON4", "isgunu"),
    "tlref_pct": ("TP.BISTTLREF.ORAN", "isgunu"),
    "politika_faizi_bis_pct": ("TP.BISPOLFAIZ.TUR", "aylik"),
    # 19.11 (paket38): TCMB brut rezervleri (haftalik, Cuma; Persembe yayimlanir) ve reel efektif kur
    "tcmb_brut_rezerv_mn_usd": ("TP.AB.TOPLAM", "haftalik"),
    "reel_efektif_kur_tufe": ("TP.RK.T1.Y", "aylik"),
}
# 20.11.2026 eki - reel kesim, anket ve dis pozisyon gostergeleri (kodlar EVDS'te dogrulandi; hepsi TCMB birincil)
GOSTERGELER = {
    "reel_kesim_guven_MA": ("TP.GY1.N2.MA", "aylik", "Reel Kesim Guven Endeksi (MA)"),
    "rkge_toplam_siparis_MA": ("TP.GY2.N2.MA", "aylik", "RKGE: toplam siparis, mevcut (MA)"),
    "rkge_ihracat_siparis_3ay_MA": ("TP.GY7.N2.MA", "aylik", "RKGE: ihracat siparisi, gelecek 3 ay (MA)"),
    "rkge_yatirim_harcamasi_MA": ("TP.GY8.N2.MA", "aylik", "RKGE: sabit sermaye yatirim harcamasi (MA)"),
    "rkge_genel_gidisat_MA": ("TP.GY9.N2.MA", "aylik", "RKGE: genel gidisat (MA)"),
    "kko_imalat_MA": ("TP.KKO.MA", "aylik", "Imalat sanayi kapasite kullanim orani (MA, %)"),
    "tuketici_guven": ("TP.TG2.Y01", "aylik", "Tuketici guven endeksi"),
    "oncu_gosterge_12ay_degisim": ("TP.CLI2.A03", "aylik", "Bilesik oncu gostergeler, 12 aylik % degisim"),
    "enf_bek_12ay_reel_sektor": ("TP.ENFBEK.IYA12ENF", "aylik", "Reel sektor 12 ay sonrasi enflasyon beklentisi (%)"),
    "enf_bek_12ay_hanehalki": ("TP.ENFBEK.HBA12ENF", "aylik", "Hanehalki 12 ay sonrasi enflasyon beklentisi (%)"),
    "uyp_net_mn_usd": ("TP.UYPUCAY.K1", "ucaylik", "Uluslararasi yatirim pozisyonu, net (milyon USD)"),
    "uyp_yabanci_hisse_yukumluluk_mn_usd": ("TP.UYPUCAY.K45", "ucaylik", "UYP: yurt disina hisse senedi yukumlulugu (milyon USD)"),
    "kredi_standartlari_isletme_gecen3ay": ("TP.BKEA.S001", "ucaylik", "Banka kredileri egilim: isletme kredi standartlari, gecen 3 ay (net %)"),
    "kredi_talebi_isletme_gecen3ay": ("TP.BKEA.S024", "ucaylik", "Banka kredileri egilim: isletme kredi talebi, gecen 3 ay (net %)"),
    "kredi_standartlari_isletme_gelecek3ay": ("TP.BKEA.S042", "ucaylik", "Banka kredileri egilim: isletme kredi standartlari beklentisi, gelecek 3 ay (net %)"),
}
CIKTI = "data/makro_akim_reel.json"


def cek(seri, bas, bit, anahtar):
    url = URL.format(seri=seri, bas=bas.strftime("%d-%m-%Y"), bit=bit.strftime("%d-%m-%Y"))
    istek = urllib.request.Request(url, headers={"User-Agent": "bist-veri-arastirma-botu",
                                                 "Accept": "application/json", "key": anahtar})
    with urllib.request.urlopen(istek, timeout=30) as y:
        ham = y.read().decode("utf-8", errors="replace")
    if not ham.strip():
        raise ValueError("EVDS bos yanit")
    alan = seri.replace(".", "_")
    out = []
    for k in json.loads(ham).get("items", []):
        v = k.get(alan, k.get(seri))
        if v in (None, "", "null"):
            continue
        out.append({"tarih": k.get("Tarih"), "deger": round(float(v), 4)})
    return out


def toplam(seri, n):
    return round(sum(x["deger"] for x in seri[-n:]), 1) if len(seri) >= 1 else None


def ardisik(seri):
    """Son haftadan geriye ayni isaretli kac hafta (giris +, cikis -)."""
    if not seri:
        return 0
    isaret = 1 if seri[-1]["deger"] > 0 else -1
    n = 0
    for x in reversed(seri):
        if (x["deger"] > 0) == (isaret > 0) and x["deger"] != 0:
            n += 1
        else:
            break
    return n * isaret


def main():
    anahtar = os.environ.get("TCMB_EVDS_API_KEY")
    if not anahtar:
        print("HATA: TCMB_EVDS_API_KEY yok", file=sys.stderr)
        return 1
    bugun = dt.date.today()
    veri, hatalar = {}, {}
    for ad, (kod, frekans) in SERILER.items():
        # is gunu serilerinde 2 yil yeter (istek basina gozlem siniri); haftalik/aylik 2020'den
        bas = bugun - dt.timedelta(days=730) if frekans == "isgunu" else dt.date(2020, 9, 1)
        try:
            veri[ad] = cek(kod, bas, bugun, anahtar)
            print(f"{ad}: {len(veri[ad])} gozlem, son {veri[ad][-1] if veri[ad] else '-'}")
        except Exception as e:
            hatalar[ad] = str(e)[:200]
            print(f"UYARI: {ad} ({kod}) cekilemedi: {e}", file=sys.stderr)
    gosterge = {}
    for ad, (kod, frekans, etiket) in GOSTERGELER.items():
        try:
            g = cek(kod, dt.date(2020, 1, 1), bugun, anahtar)
            veri[ad] = g
            if g:
                son, onc = g[-1], (g[-2] if len(g) >= 2 else None)
                gosterge[ad] = {"etiket": etiket, "kod": kod, "frekans": frekans, "son": son, "onceki": onc,
                                "degisim": round(son["deger"] - onc["deger"], 2) if onc else None,
                                "yon": ("artti" if onc and son["deger"] > onc["deger"] else "azaldi" if onc and son["deger"] < onc["deger"] else "ayni")}
        except Exception as e:
            hatalar[ad] = str(e)[:200]
            print(f"UYARI: {ad} ({kod}) cekilemedi: {e}", file=sys.stderr)
    if not veri:
        print("HATA: hicbir seri gelmedi, mevcut dosya korundu", file=sys.stderr)
        return 1

    ozet = {}
    h = veri.get("yabanci_hisse_net_mn_usd", [])
    if h:
        yil = str(bugun.year)
        ozet["yabanci_hisse"] = {
            "son_hafta": h[-1], "son_4_hafta_toplam": toplam(h, 4), "son_13_hafta_toplam": toplam(h, 13),
            "yilbasindan_toplam": round(sum(x["deger"] for x in h if yil in x["tarih"]), 1),
            "ardisik_hafta": ardisik(h),
            "not": "Pozitif = yurt disi yerlesikler net ALICI (milyon USD, fiyat/kur etkisinden arindirilmis net hareket)."}
    d = veri.get("yabanci_dibs_net_mn_usd", [])
    if d:
        ozet["yabanci_dibs"] = {"son_hafta": d[-1], "son_4_hafta_toplam": toplam(d, 4),
                                "son_13_hafta_toplam": toplam(d, 13), "ardisik_hafta": ardisik(d)}
    s = veri.get("yabanci_hisse_stok_mn_usd", [])
    if s:
        ozet["yabanci_hisse_stok"] = {"son": s[-1], "13_hafta_once": s[-14] if len(s) >= 14 else None}
    pf, bk = veri.get("fonlama_maliyeti_pct", []), veri.get("tufe_beklenti_12ay_pct", [])
    if pf and bk:
        ozet["reel_faiz"] = {
            "politika_faizi": pf[-1], "tufe_beklenti_12ay": bk[-1],
            "ex_ante_reel_faiz_pct": round(pf[-1]["deger"] - bk[-1]["deger"], 2),
            "tlref": (veri.get("tlref_pct") or [None])[-1],
            "bis_politika_faizi": (veri.get("politika_faizi_bis_pct") or [None])[-1],
            "not": "TCMB agirlikli ortalama fonlama maliyeti - 12 ay sonrasi TUFE beklentisi (Piyasa Katilimcilari "
                   "Anketi). Basit fark; bilesik (Fisher) duzeltme yok. Serilerin son gozlem tarihleri farklidir."}
    pb = veri.get("politika_faizi_beklenti_12ay_pct", [])
    if pb and pf:
        ozet["piyasa_faiz_beklentisi"] = {"12ay_sonra_politika_faizi": pb[-1],
                                          "ima_edilen_degisim_puan": round(pb[-1]["deger"] - pf[-1]["deger"], 2)}

    r = veri.get("tcmb_brut_rezerv_mn_usd", [])
    if r:
        ozet["tcmb_rezerv"] = {"son": r[-1], "haftalik_degisim": round(r[-1]["deger"] - r[-2]["deger"], 1) if len(r) > 1 else None,
                               "4_hafta_degisim": round(r[-1]["deger"] - r[-5]["deger"], 1) if len(r) > 4 else None}
    rk = veri.get("reel_efektif_kur_tufe", [])
    if rk:
        ozet["reel_efektif_kur"] = {"son": rk[-1], "12_ay_once": rk[-13] if len(rk) > 12 else None,
                                    "not": "2025=100; artis TL'nin reel degerlenmesi."}
    ozet["gostergeler"] = gosterge
    tum_kod = {**{a: (k, f) for a, (k, f) in SERILER.items()}, **{a: (k, f) for a, (k, f, _) in GOSTERGELER.items()}}
    out = {"uretim_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "kaynak": "TCMB EVDS (birincil)",
           "seriler": {ad: {"kod": tum_kod[ad][0], "frekans": tum_kod[ad][1], "gozlem": v[-160:]} for ad, v in veri.items()},
           "ozet": ozet, "hatalar": hatalar,
           "not": "Salt olcum, tavsiye degildir. Akimlarin getiri ongorusu test edilmedi; tahmin olarak kullanmadan "
                  "once on kayit gerekir."}
    tmp = CIKTI + ".tmp"
    json.dump(out, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, CIKTI)

    # baslikta uretim saati yok: veri degismedikce md degismez, is akisi bos commit atmaz
    son_tarihler = ", ".join(f"{a}: {v[-1]['tarih']}" for a, v in veri.items() if v)
    L = ["# Makro akim ve reel faiz", "", f"Kaynak: TCMB EVDS. Son gozlemler - {son_tarihler}.",
         "Salt olcum, tavsiye degildir.", ""]
    yh = ozet.get("yabanci_hisse")
    if yh:
        L += ["## Yurt disi yerlesikler - hisse senedi (net, milyon USD)", "",
              f"- Son hafta ({yh['son_hafta']['tarih']}): {yh['son_hafta']['deger']}",
              f"- Son 4 hafta: {yh['son_4_hafta_toplam']} | son 13 hafta: {yh['son_13_hafta_toplam']} | yilbasindan: {yh['yilbasindan_toplam']}",
              f"- Ardisik: {abs(yh['ardisik_hafta'])} hafta {'giris' if yh['ardisik_hafta'] > 0 else 'cikis'}", ""]
        L += ["| Hafta | Hisse net | DIBS net |", "|---|---|---|"]
        dd = {x["tarih"]: x["deger"] for x in d}
        for x in h[-8:]:
            L.append(f"| {x['tarih']} | {x['deger']} | {dd.get(x['tarih'], '-')} |")
        L.append("")
    rf = ozet.get("reel_faiz")
    if rf:
        L += ["## Reel faiz", "",
              f"- TCMB agirlikli ortalama fonlama maliyeti: %{rf['politika_faizi']['deger']} ({rf['politika_faizi']['tarih']})",
              f"- BIST TLREF: %{rf['tlref']['deger']} ({rf['tlref']['tarih']})" if rf.get('tlref') else "- BIST TLREF: -",
              f"- 12 ay sonrasi TUFE beklentisi: %{rf['tufe_beklenti_12ay']['deger']} ({rf['tufe_beklenti_12ay']['tarih']})",
              f"- Ex-ante reel faiz: **{rf['ex_ante_reel_faiz_pct']} puan**"]
        pfb = ozet.get("piyasa_faiz_beklentisi")
        if pfb:
            L.append(f"- 12 ay sonrasi politika faizi beklentisi: %{pfb['12ay_sonra_politika_faizi']['deger']} "
                     f"(ima edilen degisim {pfb['ima_edilen_degisim_puan']} puan)")
        L.append("")
    tr_ = ozet.get("tcmb_rezerv")
    if tr_:
        L += ["## TCMB brut rezervleri (milyon USD)", "",
              f"- {tr_['son']['tarih']}: {round(tr_['son']['deger'])} | haftalik degisim {tr_['haftalik_degisim']} | 4 hafta {tr_['4_hafta_degisim']}", ""]
    rk_ = ozet.get("reel_efektif_kur")
    if rk_:
        L += ["## Reel efektif kur (TUFE bazli, 2025=100)", "",
              f"- {rk_['son']['tarih']}: {rk_['son']['deger']}" + (f" | 12 ay once ({rk_['12_ay_once']['tarih']}): {rk_['12_ay_once']['deger']}" if rk_.get('12_ay_once') else ""), ""]
    if gosterge:
        L += ["## Reel kesim, anket ve dis pozisyon gostergeleri", "", "| Gosterge | Son | Onceki | Degisim |", "|---|---|---|---|"]
        for ad, g in gosterge.items():
            onc = f"{g['onceki']['deger']} ({g['onceki']['tarih']})" if g.get("onceki") else "-"
            L.append(f"| {g['etiket']} | {g['son']['deger']} ({g['son']['tarih']}) | {onc} | {g['degisim'] if g['degisim'] is not None else '-'} |")
        L += ["", "Guven endeksleri 100 esigine gore okunur (100 ustu iyimser); kredi egilim serileri net yuzdedir (pozitif = sikilasma/artis). UYP'deki ceyreklik degisimin buyuk kismi degerleme "
              "(kur/fiyat) etkisi olabilir; akim ile karistirilmamali.", ""]
    if hatalar:
        L += ["## Cekilemeyen seriler", ""] + [f"- {k}: {v}" for k, v in hatalar.items()] + [""]
    L.append("Gozlem amaclidir, tavsiye degildir.")
    open("data/makro_akim_reel.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
