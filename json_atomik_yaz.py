"""
JSON_ATOMIK_YAZ (06.08.2026) - BIST-ROS paketinden benimsenen ilk parca
Kaynak: ChatGPT'nin hazirladigi src/bist_ros/core/json_store.py -
incelendi, test edildi, bizim script yapimiza (paket degil, duz .py
dosyalari) uyarlandi.

SORUN: mevcut script'lerimizin cogu `json.dump(veri, open(yol, "w"))`
deseniyle DOGRUDAN hedef dosyaya yaziyor - eger Actions runner'i tam
yazma sirasinda kesintiye ugrarsa (timeout, iptal, cokme), YARIM/BOZUK
bir JSON dosyasi kalabilir, bir sonraki okuma (brifing, saglik_kontrol,
golge_kalibrasyon vb.) bunu ACAMAZ.

COZUM: once GECICI bir dosyaya yaz, diske ZORLA yazdir (fsync), sonra
ATOMIK olarak (os.replace - isletim sistemi duzeyinde tek adim) hedef
dosyanin USTUNE koy. Kesinti ne zaman olursa olsun, hedef dosya ya
ESKI (saglam) hali ya da YENI (tam) haliyle kalir - ASLA yarim kalmaz.
"""
import json
import os
import tempfile
from pathlib import Path


def atomik_json_yaz(yol, veri, girinti=2):
    """json.dump(veri, open(yol,'w')) yerine bunu kullan - ayni imza,
    yalniz kesintiye karsi guvenli. yol: str ya da Path."""
    hedef = Path(yol)
    hedef.parent.mkdir(parents=True, exist_ok=True)
    tanitici, gecici_ad = tempfile.mkstemp(
        prefix=f".{hedef.name}.", suffix=".tmp", dir=hedef.parent)
    gecici = Path(gecici_ad)
    try:
        with os.fdopen(tanitici, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=girinti)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(gecici, hedef)
    except Exception:
        gecici.unlink(missing_ok=True)
        raise
