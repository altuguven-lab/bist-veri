"""
PIYASA_TAKVIMI (06.08.2026) - BIST-ROS paketinden benimsenen ikinci parca
config/market_calendar.yml'i okuyup "bu tarih BIST tatili mi" sorusuna
cevap verir. Henuz HICBIR script'e BAGLANMADI (izole, test edilmis bir
parca) - kurulun "parca parca, once izole test" disipliniyle uyumlu.

BILINEN SINIRLAMA: yalniz TAM GUN tatilleri destekler, yarim-gun
(arife) ayrimi YOK - config/market_calendar.yml'deki not'a bakiniz.
"""
import datetime
import yaml


def tatil_gunleri_yukle(yol="config/market_calendar.yml"):
    """YAML'daki tum tam-gun tatillerini bir set olarak dondurur."""
    with open(yol, encoding="utf-8") as f:
        veri = yaml.safe_load(f)
    return {datetime.date.fromisoformat(h["date"]) for h in veri.get("full_day_holidays", [])}


def bugun_tatil_mi(tarih, tatil_seti):
    """tarih: datetime.date. Hafta sonu VEYA tam-gun resmi tatil ise True."""
    if tarih.weekday() >= 5:  # 5=Cumartesi, 6=Pazar
        return True
    return tarih in tatil_seti
