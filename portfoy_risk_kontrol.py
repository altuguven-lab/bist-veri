"""
PORTFOY RISK ESIGI KONTROLU (03.08.2026, ALTYAPI)
Anayasa Bolum 3'un gunluk -%3 / haftalik -%5 frenlerini otomatik
izler. Simdiye kadar bu frenler yalniz ELLE hesaplaniyordu (Claude
"kontrol et" dedikce) - ekran basinda olunmayan gunlerde hicbir
otomatik uyari gitmiyordu (tipki stop-kirilma sorununda oldugu gibi).

MEKANIZMA: saglik_kontrol.py'nin kanitlanmis "GitHub Issue ac -> GitHub
otomatik e-posta gonderir" desenini yeniden kullanir - yeni bir bildirim
altyapisi icat etmez.

REFERANS DEGERLER: data/portfoy_risk_takip.json'da saklanir:
  - gun_basi_deger: bugunun ilk kosumunda kaydedilen ozkaynak (gun
    icinde SABIT kalir, bir dahaki gun basinda guncellenir)
  - hafta_basi_deger: bu haftanin Pazartesi ilk kosumunda kaydedilen
    ozkaynak (hafta icinde SABIT kalir)
Boylece "gunluk -%3" ve "haftalik -%5" gercekten o gunun/haftanin
BASINDAKI degere gore olculur, on cagriya gore degil.
"""
import json, datetime, os, sys, urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")

PORTFOY_YOL = "data/portfoy.json"
FIYAT_YOL = "data/bist_quotes.json"
TAKIP_YOL = "data/portfoy_risk_takip.json"

GUNLUK_ESIK_YUZDE = -3.0
HAFTALIK_ESIK_YUZDE = -5.0


def _oku(yol):
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def guncel_ozkaynak(portfoy, fiyatlar):
    fiyat_map = {v["sembol"]: v["son_fiyat"] for v in fiyatlar.get("veriler", [])}
    toplam = portfoy.get("nakit_tl", 0.0)
    eksik_fiyat = []
    for p in portfoy.get("acik_pozisyonlar", []):
        f = fiyat_map.get(p["sembol"])
        if f is None:
            eksik_fiyat.append(p["sembol"])
            continue
        toplam += p["adet"] * f
    return toplam, eksik_fiyat


def github_api(yol, method="GET", veri=None):
    """saglik_kontrol.py'den birebir alindi - ayni kanitlanmis mekanizma."""
    if not TOKEN:
        return None
    req = urllib.request.Request(
        f"https://api.github.com{yol}",
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "bist-risk-esigi",
        },
        data=json.dumps(veri).encode() if veri else None,
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except Exception as e:
        print(f"UYARI: GitHub API {yol} -> {e}", file=sys.stderr)
        return None


def acik_issue_var_mi(baslik_on_eki):
    sonuc = github_api(f"/repos/{REPO}/issues?state=open&labels=risk-esigi&per_page=50")
    if not sonuc:
        return False
    return any(i.get("title", "").startswith(baslik_on_eki) for i in sonuc)


def github_issue_ac_veya_guncelle(baslik, govde, etiket):
    on_ek = baslik.split(" - ")[0]
    if acik_issue_var_mi(on_ek):
        print(f"Atlandi (acik issue var): {baslik}")
        return
    r = github_api(f"/repos/{REPO}/issues", "POST",
                   {"title": baslik, "body": govde, "labels": [etiket]})
    print(f"ISSUE ACILDI: {baslik}" if r else f"ISSUE ACILAMADI: {baslik}")


def main():
    portfoy = _oku(PORTFOY_YOL)
    fiyatlar = _oku(FIYAT_YOL)
    if not portfoy or not fiyatlar:
        print("UYARI: portfoy.json veya bist_quotes.json okunamadi", file=sys.stderr)
        sys.exit(0)  # veri yoksa sessizce cik, yanlis alarm verme

    guncel, eksik = guncel_ozkaynak(portfoy, fiyatlar)
    if eksik:
        print(f"UYARI: fiyati eksik semboller: {eksik}", file=sys.stderr)

    bugun = datetime.date.today()
    bu_hafta = bugun.isocalendar()[:2]  # (yil, hafta_no)

    takip = _oku(TAKIP_YOL) or {}

    # GUN BASI referansi: bugun ilk kez kosuyorsak kaydet
    if takip.get("gun_tarihi") != str(bugun):
        takip["gun_tarihi"] = str(bugun)
        takip["gun_basi_deger"] = guncel

    # HAFTA BASI referansi: bu hafta ilk kez kosuyorsak kaydet
    if takip.get("hafta_no") != list(bu_hafta):
        takip["hafta_no"] = list(bu_hafta)
        takip["hafta_basi_deger"] = guncel

    gun_basi = takip.get("gun_basi_deger", guncel)
    hafta_basi = takip.get("hafta_basi_deger", guncel)

    gunluk_degisim = (guncel / gun_basi - 1) * 100 if gun_basi else 0.0
    haftalik_degisim = (guncel / hafta_basi - 1) * 100 if hafta_basi else 0.0

    print(f"guncel ozkaynak: {guncel:,.0f} TL")
    print(f"gunluk degisim: %{gunluk_degisim:.2f} (esik %{GUNLUK_ESIK_YUZDE})")
    print(f"haftalik degisim: %{haftalik_degisim:.2f} (esik %{HAFTALIK_ESIK_YUZDE})")

    takip["son_kontrol_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    takip["son_ozkaynak"] = guncel
    takip["son_gunluk_degisim_yuzde"] = round(gunluk_degisim, 2)
    takip["son_haftalik_degisim_yuzde"] = round(haftalik_degisim, 2)

    ihlal_mesajlari = []
    if gunluk_degisim <= GUNLUK_ESIK_YUZDE:
        ihlal_mesajlari.append(
            f"GUNLUK FREN ASILDI: ozkaynak bugun %{gunluk_degisim:.2f} "
            f"degisti (esik %{GUNLUK_ESIK_YUZDE}). Gun basi: {gun_basi:,.0f} TL "
            f"-> simdi: {guncel:,.0f} TL.")
    if haftalik_degisim <= HAFTALIK_ESIK_YUZDE:
        ihlal_mesajlari.append(
            f"HAFTALIK FREN ASILDI: ozkaynak bu hafta %{haftalik_degisim:.2f} "
            f"degisti (esik %{HAFTALIK_ESIK_YUZDE}). Hafta basi: {hafta_basi:,.0f} TL "
            f"-> simdi: {guncel:,.0f} TL.")

    if ihlal_mesajlari:
        govde = "\n\n".join(ihlal_mesajlari) + (
            "\n\nAnayasa Bolum 3 geregi: ACIL_CIK tepkisi ertesi bar "
            "kapanisinda degerlendirilmeli. Bu otomatik bir uyaridir, "
            "islem karari degildir.")
        github_issue_ac_veya_guncelle(
            "🔴 PORTFOY RISK ESIGI ASILDI", govde, "risk-esigi")

    os.makedirs("data", exist_ok=True)
    with open(TAKIP_YOL, "w", encoding="utf-8") as f:
        json.dump(takip, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
