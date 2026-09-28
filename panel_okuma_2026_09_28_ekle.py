"""
PANEL OKUMASI EKLE - 28.09.2026 (V162.1c)
Kullanicinin TradingView grafiginden 28.09 09:07'de (acilis oncesi, Cuma
kapanis verisiyle) ELLE okudugu N/WR/PF/DD degerlerini panel_okuma_arsivi'ne
ekler. panel_okuma_arsivi.okuma_ekle (tarih,sembol) ciftiyle UPSERT yapar -
ayni gun iki kez calistirilirsa CIFT KAYIT olusmaz.

ONEMLI NOT (kodla dogrulandi, f_v112Validation): panel, KUMULATIF bir kayit
DEGIL - var-tabanli sayaclar grafigin YUKLU gecmisi uzerinde her yuklemede
bastan yeniden hesaplanir, baslangic-tarihi kapisi yok. N zamanla DUSEBILIR
(pencere kayar / kod degisir). Bu yuzden onceki okumalarla farklar "kod
duzeltmesinin etkisi" olarak DOGRUDAN yorumlanmamali.
"""
from panel_okuma_arsivi import okuma_ekle

PINE = "V162.1c (P0 stop/fill + B1-B6 + golge karar; SHWR/SHPF golge panel, 21-23.09 surumu)"
NOT = ("Kullanici tarafindan grafikten okundu (28.09 09:07, Cuma kapanis verisi). "
       "Golge (SH) panel; N kumulatif DEGIL, yuklu grafik gecmisi uzerinden yeniden hesaplaniyor.")

OKUMALAR = [  # (sembol, N, WR%, PF, DD)
    ("AKBNK", 72, 35, 1.3, 17.6),
    ("YKBNK", 63, 37, 0.8, 25.5),
    ("KCHOL", 143, 38, 1.3, 16.1),
    ("BIMAS", 238, 32, 1.2, 19.6),
    ("ASELS", 257, 39, 1.9, 11.2),
    ("ASTOR", 206, 43, 2.2, 9.3),
    ("THYAO", 27, 22, 0.5, 10.8),
]

if __name__ == "__main__":
    for sembol, n, wr, pf, dd in OKUMALAR:
        okuma_ekle("2026-09-28", sembol, n=n, wr_pct=wr, pf=pf, dd=dd,
                   pine_surumu=PINE, not_metni=NOT)
    print(f"{len(OKUMALAR)} okuma eklendi (2026-09-28).")
