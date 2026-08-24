# MÜKERRER DOSYA TEMİZLİĞİ
20.08.2026 | Etiket: ALTYAPI | Dalga 2, madde 5

---

## Kanıtlanan iki çift — silinebilir

GitHub API'nin kimlik doğrulamasız kotası şu an dolu, tam ağaç
taraması yapamadım. Ama iki çifti doğrudan `diff` ile karşılaştırdım
ve ikisi de **bit bit aynı:**

**1. `sinyal_arsiv_gunluk_v2.py`**

Canonical `sinyal_arsiv_gunluk.py` (18.08'de v2.1 olarak commit'lendi)
ile birebir aynı — 363 satır, `diff -q` fark bulmuyor. Bu dosya v2.1
teslim edilirken geride kalmış bir ara taslak. Kod bu şekilde
`import sinyal_arsiv_gunluk_v2` diye çağrılmıyor (kontrol ettim,
hiçbir workflow ona referans vermiyor) — güvenle silinebilir.

```
git rm sinyal_arsiv_gunluk_v2.py
```

**2. `SENIOR_ENGINEER_AGENT.md` — iki kopya**

`# SENIOR_ENGINEER_AGENT.md` (dosya adında `#` işareti var — muhtemelen
bir düzenleyicinin kaza sonucu oluşturduğu dosya) ve
`SENIOR_ENGINEER_AGENT.md`, ikisi de 4.863 bayt, içerik birebir aynı.

`#`'li olan sil, normal adı olan kalsın:

```
git rm "# SENIOR_ENGINEER_AGENT.md"
```

---

## Doğrulayamadığım iki çift — silme talimatı VERMİYORUM

İncelemede geçen iki iddiayı **kanıtlamadan** silme talimatı vermek,
yanlış dosyayı silmekten daha kötü bir hata olurdu:

- `supertrend_adx_swing_backtest.py` ile "başka bir momentum dosyası"
  birebir aynı iddiası — hangi dosya olduğu belirtilmemiş, ben de
  bulamadım (API kotası kapalı).
- "İki ayrı workflow aynı SHA'ya sahip" iddiası — hangi ikisi
  belirtilmemiş.

**Öneri:** GitHub arayüzünden `Code` sekmesinde dosya adına göre arama
yaparak (`supertrend`, `momentum`) iki dosyayı bulup `diff` bak. Eğer
gerçekten birebir aynıysa hangisinin daha az yerde referans aldığını
(`grep -rn "supertrend_adx_swing_backtest\|<diger_ad>" .`) kontrol edip
öyle sil. Workflow çifti için Actions sekmesindeki "Run workflow"
geçmişini karşılaştırmak yeterli olur — hangisi daha güncel çalışmışsa
o kalır.

Bu ikisini onaylanmadan silmemek, "smallest safe change" ilkesiyle
tutarlı: kanıtsız silme, kanıtsız yazmadan farksız bir risk.

---

## Sıra

Bu dosya Dalga 2'nin geri kalanına engel değil — `requirements.txt`
ve atomik yazım genişletmesi bağımsız işler, paralel ilerleyebilir.
