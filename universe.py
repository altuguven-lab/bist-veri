"""
EVREN YUKLEYICI (20.08.2026) - C3

SORUN (mimari inceleme, 19.08): sembol evreni ucayrı yerde elle
senkronize ediliyordu: fetch_bist.py, fetch_news.py, ve
config/universe.yml (VAR ama HICBIR SEY OKUMUYORDU). TRALT, DMLKT,
ENJSA ve TRMET/KOZAA sorunlarinin hepsi bu ayriliktan cikti - biri
guncellenip digeri unutuldugunda sessizce tutarsizlik olustu.

COZUM: config/universe.yml TEK OTORITE. Bu modul onu okur; fetch_bist.py
ve fetch_news.py artik kendi BIST_SEMBOLLER listelerini TASIMAZ, buradan
alir.

KIRMIZI CIZGI: dosya eksik/bozuksa SESSIZCE eski sabit listeye DUSMEZ -
hata verir ve durur. Sessiz dusme, universe.yml'i guncelleyip script'i
guncellemeyi unutma hatasini bir baska sekle tasirdi.
"""
import sys

try:
    import yaml
except ImportError:
    print("HATA: PyYAML kurulu degil. requirements.txt'e eklendi mi? "
          "(pip install pyyaml)", file=sys.stderr)
    raise

YOL = "config/universe.yml"


def yukle_evren(yol=YOL):
    """(sembol_listesi, fallback_sozlugu) doner.

    fallback_sozlugu: {SEMBOL: eski_kod} - Yahoo'da birincil kod bos
    donerse denenecek eski ticker (kod/unvan degisikligi gecis donemi).
    fetch_news.py gibi Yahoo kullanmayan cagiranlar bu sozlugu yok
    sayabilir.
    """
    try:
        with open(yol, encoding="utf-8") as f:
            d = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"HATA: {yol} yok. Evrenin tek otoritesi bu dosyadir, "
              "sessizce baska bir listeye dusulmez.", file=sys.stderr)
        raise
    except yaml.YAMLError as e:
        print(f"HATA: {yol} gecersiz YAML -> {e}", file=sys.stderr)
        raise

    semboller = d.get("symbols")
    if not semboller or not isinstance(semboller, list):
        raise ValueError(f"{yol}: 'symbols' listesi bos veya eksik")

    fallback = d.get("fallback_symbols") or {}
    return list(semboller), dict(fallback)


if __name__ == "__main__":
    # Elle dogrulama: python universe.py
    semboller, fallback = yukle_evren()
    print(f"{len(semboller)} sembol yuklendi: {', '.join(semboller)}")
    if fallback:
        print(f"fallback: {fallback}")
