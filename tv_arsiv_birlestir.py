"""TV SINYAL ARSIV BIRLESTIRME (26.10.2026) - SALT VERI KORUMA, Pine'a ve sinyal mantigina dokunmaz.
Sorun: Pipedream data/tv_alerts_latest.json'da yalniz son MAX_SINYAL (100) sinyali tutuyor; aylik arsiv
       yalniz AY DONUMUNDE o anki son 100 sinyali yaziyordu. Temmuz-Ekim'de sinyallerin cogu ham kayittan
       dustu (git gecmisinden yeniden kuruldu: Tem 197, Agu 852, Eyl 488, Eki 1034 sinyal).
Cozum: Bu betik her calistiginda latest'teki sinyalleri kendi ayinin arsivine (data/arsiv/tv_alerts_YYYY_MM.json)
       tekil (eventId, yoksa zaman|sembol|sinyal) olarak ekler. Gunde en az bir kez calismali.
"""
import json, os, glob
from datetime import datetime, timezone

LATEST = "data/tv_alerts_latest.json"


def anahtar(s):
    e = s.get("eventId")
    return e if e and e != "?" else f"{s.get('zaman_utc')}|{s.get('sembol')}|{s.get('sinyal')}"


def main():
    latest = json.load(open(LATEST, encoding="utf-8"))
    yeni = latest.get("sinyal_gecmisi") or []
    aylar = {}
    for s in yeni:
        z = s.get("zaman_utc") or ""
        if len(z) >= 7:
            aylar.setdefault(z[:7], []).append(s)
    os.makedirs("data/arsiv", exist_ok=True)
    for ay, liste in sorted(aylar.items()):
        yol = f"data/arsiv/tv_alerts_{ay.replace('-', '_')}.json"
        if os.path.exists(yol):
            a = json.load(open(yol, encoding="utf-8"))
        else:
            a = {"ay": ay, "sinyaller": []}
        mevcut = {anahtar(s): s for s in a.get("sinyaller", [])}
        once = len(mevcut)
        for s in liste:
            mevcut.setdefault(anahtar(s), s)
        sirali = sorted(mevcut.values(), key=lambda s: s.get("zaman_utc", ""))
        a.update({"ay": ay, "sinyal_sayisi": len(sirali), "sinyaller": sirali,
                  "son_birlestirme_utc": datetime.now(timezone.utc).isoformat()})
        json.dump(a, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{ay}: {once} -> {len(sirali)} (+{len(sirali) - once})")


if __name__ == "__main__":
    main()
