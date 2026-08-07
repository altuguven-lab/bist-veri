"""
TEMEL MODUL TESTLERI (07.08.2026) - Faz V0
BIST-ROS paketinden benimsenen fikir: kalici, tests/ altinda tekrar
calistirilabilir testler. Kapsam BILINCLI DAR - yalniz EN COK
yeniden kullanilan ucuncu parca (json_atomik_yaz, konfig_yukle,
piyasa_takvimi). Bugunku (06-07.08) konusma icinde manuel calistirilan
testlerin KALICI hale getirilmis hali - ayni senaryolar.

Calistirma: pytest tests/test_temel_moduller.py -v   (repo kokunde)
"""
import datetime
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from json_atomik_yaz import atomik_json_yaz
from konfig_yukle import sembol_evreni_yukle, tatil_gunleri_yukle, KonfigHatasi
from piyasa_takvimi import tatil_gunleri_yukle as pt_tatil_gunleri_yukle, bugun_tatil_mi


# ---- json_atomik_yaz.py ----

def test_atomik_yazma_normal(tmp_path):
    yol = tmp_path / "veri" / "test.json"
    atomik_json_yaz(str(yol), {"a": 1, "b": [1, 2, 3]})
    assert yol.exists()
    with open(yol) as f:
        assert json.load(f) == {"a": 1, "b": [1, 2, 3]}


def test_atomik_yazma_gecici_dosya_temizlenir(tmp_path):
    yol = tmp_path / "veri" / "test.json"
    atomik_json_yaz(str(yol), {"x": 1})
    kalanlar = [f for f in os.listdir(yol.parent) if f.startswith(".") and f.endswith(".tmp")]
    assert kalanlar == []


def test_atomik_yazma_uzerine_yazma(tmp_path):
    yol = tmp_path / "veri" / "test.json"
    atomik_json_yaz(str(yol), {"a": 1})
    atomik_json_yaz(str(yol), {"c": 99})
    with open(yol) as f:
        assert json.load(f) == {"c": 99}


def test_atomik_yazma_hata_orijinali_korur(tmp_path):
    yol = tmp_path / "veri" / "test.json"
    atomik_json_yaz(str(yol), {"a": 1})
    onceki_icerik = yol.read_text()

    class Serilestirilemez:
        pass

    try:
        atomik_json_yaz(str(yol), {"x": Serilestirilemez()})
        assert False, "TypeError beklenirdi"
    except TypeError:
        pass
    assert yol.read_text() == onceki_icerik
    kalanlar = [f for f in os.listdir(yol.parent) if f.startswith(".") and f.endswith(".tmp")]
    assert kalanlar == []


# ---- konfig_yukle.py ----

def _universe_yaz(tmp_path, icerik):
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "universe.yml").write_text(icerik)


def test_sembol_evreni_yukle_gecerli(tmp_path):
    _universe_yaz(tmp_path, """
schema_version: "1.0"
provider_suffix: ".IS"
symbols:
  - AKBNK
  - KCHOL
fallback_symbols:
  AKBNK: KOZAA
""")
    semboller, sonek, yedekler = sembol_evreni_yukle(str(tmp_path / "config" / "universe.yml"))
    assert semboller == ("AKBNK", "KCHOL")
    assert sonek == ".IS"
    assert yedekler == {"AKBNK": "KOZAA"}


def test_sembol_evreni_yukle_tekrar_eden_sembol_reddedilir(tmp_path):
    _universe_yaz(tmp_path, """
symbols:
  - AKBNK
  - AKBNK
""")
    try:
        sembol_evreni_yukle(str(tmp_path / "config" / "universe.yml"))
        assert False, "KonfigHatasi beklenirdi"
    except KonfigHatasi:
        pass


def test_sembol_evreni_yukle_eksik_dosya(tmp_path):
    try:
        sembol_evreni_yukle(str(tmp_path / "config" / "olmayan.yml"))
        assert False, "KonfigHatasi beklenirdi"
    except KonfigHatasi:
        pass


def test_tatil_gunleri_yukle_konfig(tmp_path):
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "market_calendar.yml").write_text("""
full_day_holidays:
  - date: "2026-01-01"
    name: Yilbasi
  - date: "2026-03-20"
    name: Ramazan Bayrami
""")
    tatiller = tatil_gunleri_yukle(str(tmp_path / "config" / "market_calendar.yml"))
    assert tatiller == {datetime.date(2026, 1, 1), datetime.date(2026, 3, 20)}


# ---- piyasa_takvimi.py ----

def test_piyasa_takvimi_bilinen_tatiller(tmp_path):
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "market_calendar.yml").write_text("""
full_day_holidays:
  - date: "2026-01-01"
    name: Yilbasi
""")
    tatiller = pt_tatil_gunleri_yukle(str(tmp_path / "config" / "market_calendar.yml"))
    assert bugun_tatil_mi(datetime.date(2026, 1, 1), tatiller) is True


def test_piyasa_takvimi_normal_is_gunu(tmp_path):
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "market_calendar.yml").write_text("""
full_day_holidays:
  - date: "2026-01-01"
    name: Yilbasi
""")
    tatiller = pt_tatil_gunleri_yukle(str(tmp_path / "config" / "market_calendar.yml"))
    # 2026-08-06 Persembe, ne tatil listesinde ne hafta sonu
    assert bugun_tatil_mi(datetime.date(2026, 8, 6), tatiller) is False


def test_piyasa_takvimi_hafta_sonu(tmp_path):
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "config" / "market_calendar.yml").write_text("full_day_holidays: []")
    tatiller = pt_tatil_gunleri_yukle(str(tmp_path / "config" / "market_calendar.yml"))
    # 2026-08-08 Cumartesi - listede olmasa bile tatil sayilmali
    assert bugun_tatil_mi(datetime.date(2026, 8, 8), tatiller) is True
