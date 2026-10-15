"""V162.1 -> olu (okunmayan) ust-duzey tanimlari bulur ve (istenirse) cikarir.
Davranis-notr: yalniz hicbir yerde OKUNMAYAN, yan etkisiz atamalar.
Kullanim: python olu_kod_analiz.py GIRDI.txt [--yaz CIKTI.txt] [--kapi-sil]
"""
import re, sys, collections

YAN_ETKI = re.compile(r'\b(label|line|box|table|polyline|linefill|chart|strategy|alert)\.|\bplot\w*\(|alertcondition\(|\binput\.|\bvar\b|\bvarip\b')
SEC = re.compile(r'request\.')

def yorumsuz(l):
    # // yorumunu at (string icindeki // yok varsayimi: Pine kaynaginda URL yok; dogrulandi)
    return re.sub(r'//.*', '', l)

def bul(satirlar, kapi_sil):
    kod = [yorumsuz(l) for l in satirlar]
    silinen = []   # (ad, bas, son)
    while True:
        metin = '\n'.join(kod)
        sayac = collections.Counter(re.findall(r'[A-Za-z_]\w*', metin))
        yeni = []
        i = 0
        while i < len(kod):
            l = kod[i]
            mf = re.match(r'^([A-Za-z_]\w*)\([^)]*\)\s*=>\s*$', l) or re.match(r'^([A-Za-z_]\w*)\([^)]*\)\s*=>', l)
            if mf and sayac[mf.group(1)] == 1:
                j = i + 1
                while j < len(kod) and (kod[j].startswith(' ') or kod[j].startswith('\t')):
                    j += 1
                govde = '\n'.join(kod[i:j])
                if not YAN_ETKI.search(govde.replace('var ', 'v_')) or True:
                    # fonksiyon govdesindeki var/ta durumu cagrilmadikca calismaz -> guvenle silinir
                    yeni.append((mf.group(1) + '()', i, j))
                i = j
                continue
            m = re.match(r'^([A-Za-z_]\w*)\s*(=|:=)(?!=)', l)
            if m and sayac[m.group(1)] == 1 and not (satirlar[i].startswith('//')):
                j = i + 1
                while j < len(kod) and kod[j].startswith(' ') and kod[j].strip():
                    j += 1
                govde = '\n'.join(kod[i:j])
                ok = not YAN_ETKI.search(govde)
                if SEC.search(govde) and not kapi_sil:
                    ok = False
                if ok and m.group(2) == '=':
                    yeni.append((m.group(1), i, j))
                i = j
                continue
            i += 1
        if not yeni:
            break
        for ad, b, s in yeni:
            for k in range(b, s):
                kod[k] = ''
            silinen.append((ad, b, s))
    return silinen

def main():
    g = sys.argv[1]
    kapi = '--kapi-sil' in sys.argv
    with open(g, encoding='utf-8', newline='') as f:
        ham = f.read()
    satirlar = ham.split('\n')
    silinen = bul(satirlar, kapi)
    toplam = sum(len('\n'.join(satirlar[b:s])) + 1 for _, b, s in silinen)
    print(f"{len(silinen)} tanim, {toplam} karakter, {sum(s-b for _,b,s in silinen)} satir")
    for ad, b, s in sorted(silinen, key=lambda x: x[1]):
        print(f"  {b+1:5d}-{s:5d}  {ad}")
    if '--yaz' in sys.argv:
        cikti = sys.argv[sys.argv.index('--yaz') + 1]
        sil = set()
        for _, b, s in silinen:
            sil.update(range(b, s))
        yeni = [l for k, l in enumerate(satirlar) if k not in sil]
        with open(cikti, 'w', encoding='utf-8', newline='') as f:
            f.write('\n'.join(yeni))
        print('yazildi', cikti, len(yeni), 'satir')

main()
