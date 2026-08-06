"""
KONFIG_YUKLE (06.08.2026) - BIST-ROS paketinden benimsenen ucuncu parca
Kaynak: src/bist_ros/config/loader.py - dogrulama mantigi (tip kontrolu,
tekrar-sembol kontrolu, YAML hata yonetimi) AYNEN korundu, yalniz bizim
DUZ-DOSYA script kuralimiza (paket degil) uyarlandi.

Henuz HICBIR canli script'e baglanmadi - fetch_bist_v2_kesif.py'de
IZOLE test edilecek.
"""
import datetime
import yaml


class KonfigHatasi(ValueError):
    pass


def sembol_evreni_yukle(yol="config/universe.yml"):
    """Doner: (semboller_tuple, saglayici_soneki, yedek_kodlar_dict)."""
    try:
        with open(yol, encoding="utf-8") as f:
            ham = yaml.safe_load(f)
    except FileNotFoundError:
        raise KonfigHatasi(f"Konfig dosyasi bulunamadi: {yol}")
    except yaml.YAMLError as e:
        raise KonfigHatasi(f"Gecersiz YAML ({yol}): {e}")

    semboller = ham.get("symbols")
    if not isinstance(semboller, list) or not semboller:
        raise KonfigHatasi("universe.symbols bos olamaz")
    normalize = tuple(str(s).strip().upper() for s in semboller)
    if len(set(normalize)) != len(normalize):
        raise KonfigHatasi("universe.symbols icinde tekrar eden sembol var")

    yedekler = {str(k).strip().upper(): str(v).strip().upper()
                for k, v in (ham.get("fallback_symbols") or {}).items()}
    bilinmeyen = set(yedekler) - set(normalize)
    if bilinmeyen:
        raise KonfigHatasi(f"fallback_symbols evren disi anahtar iceriyor: {sorted(bilinmeyen)}")

    return normalize, str(ham.get("provider_suffix", ".IS")), yedekler


def tatil_gunleri_yukle(yol="config/market_calendar.yml"):
    """Tum tam-gun tatillerini bir set (datetime.date) olarak dondurur."""
    try:
        with open(yol, encoding="utf-8") as f:
            ham = yaml.safe_load(f)
    except FileNotFoundError:
        raise KonfigHatasi(f"Konfig dosyasi bulunamadi: {yol}")
    return {datetime.date.fromisoformat(h["date"]) for h in ham.get("full_day_holidays", [])}
