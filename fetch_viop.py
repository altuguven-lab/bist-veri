"""
FAZ V1 - fetch_viop.py (04.08.2026)
VIOP ENTEGRASYON PROMPTU'nun V0 (kesif) fazi tamamlandi, bu V1'in ilk
hali: gunluk VIOP bultenini TAM (satir limitsiz) okur, yalniz bizim
ELDE TUTULAN sembollerin (DAYANAK VARLIK = "{SEMBOL}.E") satirlarini
filtreler, spot fiyatla (bist_quotes.json) HAM baz farkini hesaplar.

KIRMIZI CIZGI (VIOP ENTEGRASYON PROMPTU): 18.08.2026'ya kadar hicbir
skor/sinyal (SQZ, kadran_puani) hesaplanmaz - bu betik yalniz HAM veri
tasir. Yorumlama/z-skor Faz V2'nin isi, burada YOK.
"""
import json, datetime, os, sys, urllib.request, io
import pandas as pd

TABAN_URL = "https://www.borsaistanbul.com/viopdata/"
CIKTI = "data/viop_analiz.json"
KODLAMALAR = ["windows-1254", "utf-8", "iso-8859-9"]
AYRACLAR = [";", ","]

# Portfoy.json'dan otomatik degil, bilinclii sabit liste (5 pozisyon +
# ASTOR ilk kesifte SSF'si dogrulanmisti) - portfoy degisirse burasi
# elle guncellenir, sessiz kaymayi onlemek icin.
TAKIP_EDILEN = ["AKBNK", "YKBNK", "KCHOL", "TAVHL", "ASTOR"]


def indir(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (bist-veri fetch_viop)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def csv_oku_tam(ham_bayt):
    """Tur 4 kesfindeki ayni kodlama/ayrac tespiti - ama nrows LIMITSIZ."""
    for kod in KODLAMALAR:
        for ayrac in AYRACLAR:
            try:
                df = pd.read_csv(io.BytesIO(ham_bayt), encoding=kod, sep=ayrac,
                                  on_bad_lines="skip", engine="python")
                if df.shape[1] >= 2:
                    return df, kod, ayrac
            except Exception:
                continue
    return None, None, None


def gunluk_bulten_bul(bugun, azami_geri=6):
    """Bugunden geriye dogru en son yayinlanmis bulteni bulur."""
    for geri in range(azami_geri):
        gun = bugun - datetime.timedelta(days=geri)
        if gun.weekday() >= 5:
            continue
        url = TABAN_URL + f"viop_{gun.strftime('%Y%m%d')}.csv"
        try:
            ham = indir(url)
            if len(ham) < 200:
                continue
            df, kod, ayrac = csv_oku_tam(ham)
            if df is not None:
                return df, gun, url
        except Exception as e:
            print(f"denendi, basarisiz: {gun} -> {e}", file=sys.stderr)
    return None, None, None


def spot_fiyatlari_oku():
    try:
        with open("data/bist_quotes.json", encoding="utf-8") as f:
            q = json.load(f)
        return {v["sembol"]: v["son_fiyat"] for v in q.get("veriler", [])}
    except Exception as e:
        print(f"UYARI: spot fiyat okunamadi: {e}", file=sys.stderr)
        return {}


def main():
    bugun = datetime.date.today()
    df, kullanilan_gun, url = gunluk_bulten_bul(bugun)
    if df is None:
        print("HATA: hicbir gun icin bulten bulunamadi", file=sys.stderr)
        # veri yoksa sessizce cik - yanlis/eksik dosya yazma
        sys.exit(0)

    spot = spot_fiyatlari_oku()
    sonuc = {
        "guncelleme_zamani_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "bulten_gunu": str(kullanilan_gun),
        "kaynak_url": url,
        "kirmizi_cizgi_notu": ("18.08.2026'ya kadar SQZ/sinyal hesaplanmaz - "
                               "bu dosya yalniz ham VIOP verisi tasir."),
        "semboller": {},
    }

    for sem in TAKIP_EDILEN:
        eslesen = df[df.get("DAYANAK VARLIK", pd.Series(dtype=str)).astype(str)
                     .str.upper() == f"{sem}.E"]
        sozlesmeler = []
        for _, satir in eslesen.iterrows():
            try:
                ham_deger = str(satir.get("UZLASMA FIYATI", "")).strip()
                # BIST dosyalari bazen virgullu (67,74) bazen noktali (67.74)
                # ondalik kullanabiliyor - ikisini de kabul et.
                if "," in ham_deger and "." not in ham_deger:
                    ham_deger = ham_deger.replace(",", ".")
                uzlasma = float(ham_deger)
            except (TypeError, ValueError):
                uzlasma = None
            kayit = {
                "sozlesme_kodu": str(satir.get("SOZLESME KODU", "")),
                "vade_tarihi": str(satir.get("VADE TARIHI", "")),
                "uzlasma_fiyati": uzlasma,
                "uzlasma_degisim_yuzde": satir.get("UZLASMA FIYATI DEGISIMI (%)"),
                "islem_hacmi": satir.get("ISLEM HACMI"),
                "acik_pozisyon": satir.get("ACIK POZISYON"),
                "acik_pozisyon_degisim": satir.get("ACIK POZISYON DEGISIMI"),
            }
            if uzlasma and sem in spot:
                kayit["spot_fiyat"] = spot[sem]
                kayit["baz_ham"] = round(uzlasma - spot[sem], 4)
                kayit["baz_yuzde_ham"] = round((uzlasma / spot[sem] - 1) * 100, 3)
            sozlesmeler.append(kayit)
        # yakin vadeye gore sirala
        sozlesmeler.sort(key=lambda x: x["vade_tarihi"] or "9999")
        sonuc["semboller"][sem] = {
            "sozlesme_sayisi": len(sozlesmeler),
            "sozlesmeler": sozlesmeler,
        }
        print(f"{sem}: {len(sozlesmeler)} sozlesme bulundu")

    os.makedirs("data", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2)
    print(f"Yazildi: {CIKTI} (bulten gunu: {kullanilan_gun})")


if __name__ == "__main__":
    main()
