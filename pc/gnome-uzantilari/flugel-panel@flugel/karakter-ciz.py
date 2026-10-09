#!/usr/bin/env python3
"""Re:Zero ekibi chibi cizimleri v3 (ozgun SVG, sistem-bakim)
Tarz: Re:Zero Break Time / Isekai Quartet chibi'leri (Studio Puyukai, chibi tasarim Minoru Takehara) gibi:
buyuk kafa, yuzun alt yarisinda iri gozler, minik agiz, yumusak hatlar, duz renk + kalin temiz dis cizgi.
Karakter ayrintilari resmi gorunus tariflerine gore (Re:Zero Wiki, Otapedia).
Calistir: python3 karakter-ciz.py -> ekip/<ad>-acik.svg, ekip/<ad>-kapali.svg"""
import os

CIKTI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ekip")
C = "#1B1724"                 # dis cizgi
TEN, TEN_G = "#FFEEE4", "#F2C9B8"
GX = (23.6, 40.4)             # goz merkezleri
GY = 38.4

# id: (ad, sac, sac golge, iris ust, iris alt)
EKIP = {
    "emilia":    ("Emilia",    "#EFEAF8", "#C6BAE4", "#5E3AB8", "#B48EF4"),
    "subaru":    ("Subaru",    "#26252D", "#73728A", "#3A2A22", "#7A5A44"),
    "beatrice":  ("Beatrice",  "#F6E7AE", "#D8BE6E", "#2F63D0", "#8DB6FF"),
    "rem":       ("Rem",       "#86B9F0", "#5287CB", "#3C78D2", "#A6D0FF"),
    "ram":       ("Ram",       "#F6B3CC", "#CF7C9E", "#C2365E", "#F69AB4"),
    "julius":    ("Julius",    "#A88BDA", "#7056A8", "#B9860F", "#F4D466"),
    "anastasia": ("Anastasia", "#C9B4EC", "#9C84CC", "#22918F", "#79DCD3"),
    "meili":     ("Meili",     "#4F78CC", "#2E4F96", "#5D7820", "#AFC45E"),
    "shaula":    ("Shaula",    "#2F2520", "#7B6353", "#1F7F49", "#66D592"),
}


def defs(i, u, a):
    return (f'<defs><linearGradient id="i{i}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{u}"/><stop offset="1" stop-color="{a}"/></linearGradient></defs>')


def goz(i, acik, kucuk=False, kelebek=False, akrep=False, ortu=None):
    """Chibi goz. ortu: 'sol'/'sag' -> o goz kakulle kismen ortulu (izleyiciye gore)."""
    s = ""
    for k, x in enumerate(GX):
        if not acik:
            s += f'<path d="M{x-5.2} {GY} Q{x} {GY+3.6} {x+5.2} {GY}" stroke="{C}" stroke-width="2" fill="none" stroke-linecap="round"/>'
            continue
        s += f'<ellipse cx="{x}" cy="{GY}" rx="5" ry="6.3" fill="#FFFFFF" stroke="{C}" stroke-width="0.6"/>'
        ir = 3.1 if kucuk else 4.6
        s += f'<ellipse cx="{x}" cy="{GY + (0.8 if kucuk else 0.4)}" rx="{ir}" ry="{ir*1.25:.1f}" fill="url(#i{i})"/>'
        s += f'<ellipse cx="{x}" cy="{GY + 1}" rx="{ir*0.42:.1f}" ry="{ir*0.6:.1f}" fill="{C}" opacity="0.8"/>'
        if kelebek:   # Beatrice: kelebek bicimli gozbebegi
            s += (f'<path d="M{x-2.6} {GY-0.6} Q{x-1} {GY+0.8} {x} {GY+1.2} Q{x+1} {GY+0.8} {x+2.6} {GY-0.6} '
                  f'Q{x+2} {GY+2.8} {x} {GY+2} Q{x-2} {GY+2.8} {x-2.6} {GY-0.6} Z" fill="#FFFFFF" opacity="0.92"/>')
        if akrep:     # Shaula: gozbebegi cevresinde uc kirmizi nokta
            for dx, dy in ((-2.1, -1), (2.1, -1), (0, 2.6)):
                s += f'<circle cx="{x+dx}" cy="{GY+1+dy}" r="0.6" fill="#E8283E"/>'
        s += f'<ellipse cx="{x+1.7}" cy="{GY-2.4}" rx="1.7" ry="1.9" fill="#FFFFFF"/><circle cx="{x-1.6}" cy="{GY+3}" r="0.75" fill="#FFFFFF" opacity="0.9"/>'
        s += f'<path d="M{x-5.6} {GY-3.4} Q{x} {GY-8.6} {x+5.6} {GY-3.4}" stroke="{C}" stroke-width="2" fill="none" stroke-linecap="round"/>'
        if kucuk:     # Subaru'nun keskin bakisi
            yon = 1 if k == 0 else -1
            s += f'<path d="M{x-5*yon} {GY-7.2} L{x+4.6*yon} {GY-5.8}" stroke="{C}" stroke-width="1.5" stroke-linecap="round"/>'
    return s


def yuz(agiz="gulus"):
    a = {
        "gulus": '<path d="M30 47.4 Q32 49.2 34 47.4" stroke="#A9506A" stroke-width="1.3" fill="none" stroke-linecap="round"/>',
        "duz":   '<path d="M30.2 47.8 Q32 48.6 33.8 47.6" stroke="#8A4A55" stroke-width="1.3" fill="none" stroke-linecap="round"/>',
        "acik":  '<path d="M29.4 46.8 Q32 51.2 34.6 46.8 Z" fill="#9C3346" stroke="#7A2436" stroke-width="0.7"/>',
        "kedi":  '<path d="M29.6 47.2 Q30.8 48.8 32 47.4 Q33.2 48.8 34.4 47.2" stroke="#A9506A" stroke-width="1.2" fill="none" stroke-linecap="round"/>',
    }[agiz]
    return (f'<ellipse cx="32" cy="36" rx="19" ry="17" fill="{TEN}" stroke="{C}" stroke-width="1"/>'
            f'<ellipse cx="19.4" cy="45" rx="3.2" ry="1.7" fill="#FF97B0" opacity="0.5"/>'
            f'<ellipse cx="44.6" cy="45" rx="3.2" ry="1.7" fill="#FF97B0" opacity="0.5"/>' + a)


O = f'stroke="{C}" stroke-width="1" stroke-linejoin="round"'
PARLA = '<path d="M20 16 Q30 11 42 14" stroke="#FFFFFF" stroke-width="1.8" fill="none" opacity="0.45" stroke-linecap="round"/>'


def govde(renk, yaka=""):
    return f'<path d="M17 64 Q18 54.6 32 53 Q46 54.6 47 64 Z" fill="{renk}" {O}/>{yaka}'


# ---------------- karakterler ----------------
def emilia(acik):
    c, g = EKIP["emilia"][1:3]
    arka = (f'<path d="M9 31 Q6 50 14 63 L24 63 Q17 48 19 34 Z" fill="{c}" {O}/>'
            f'<path d="M55 31 Q58 50 50 63 L40 63 Q47 48 45 34 Z" fill="{c}" {O}/>')
    kulak = f'<path d="M13.4 38 L5 31 L14.6 34.4 Z" fill="{TEN}" {O}/><path d="M50.6 38 L59 31 L49.4 34.4 Z" fill="{TEN}" {O}/>'
    kiyafet = govde("#FFFFFF", f'<path d="M25 54 L32 61 L39 54" fill="#8B62D6" {O}/><circle cx="32" cy="58" r="1.5" fill="#D6C2FF"/>')
    on = (f'<path d="M13 33 Q13 11 32 10 Q51 11 51 33 Q46 23 40 25 Q37 19 32 26 Q27 19 24 25 Q18 23 13 33 Z" fill="{c}" {O}/>'
          f'<path d="M22 25 L24.6 31 M32 24.6 L32 31 M42 25 L39.4 31" stroke="{g}" stroke-width="1.1" stroke-linecap="round"/>{PARLA}')
    # beyaz cicek + mor kurdele
    cicek = ('<g transform="translate(15 17) scale(1.3)" stroke="#9D85D6" stroke-width="0.6">'
             + "".join(f'<ellipse cx="{x}" cy="{y}" rx="2.9" ry="2.5" fill="#fff" transform="rotate({r} {x} {y})"/>'
                       for x, y, r in ((0, -3.6, 0), (3.4, -1.1, 72), (2.1, 3, 144), (-2.1, 3, 216), (-3.4, -1.1, 288)))
             + '<circle cx="0" cy="0" r="1.6" fill="#F2C94C" stroke="none"/></g>'
             f'<path d="M17 24 L13.4 30 M18.6 24 L19.8 30.6" stroke="#8B62D6" stroke-width="1.6" stroke-linecap="round"/>')
    return arka + kiyafet + kulak + yuz() + on + goz("emilia", acik) + cicek


def subaru(acik):
    c, g = EKIP["subaru"][1:3]
    # beyaz ceket, dik yaka, koyu gri omuzlar, turuncu cizgi
    kiyafet = (f'<path d="M17 64 Q18 54.6 32 53 Q46 54.6 47 64 Z" fill="#F4F4F6" {O}/>'
               f'<path d="M17 64 Q17.6 56 25 54 L22 64 Z M47 64 Q46.4 56 39 54 L42 64 Z" fill="#4A4A55"/>'
               f'<path d="M19.4 64 Q20 57.6 24 55.4 M44.6 64 Q44 57.6 40 55.4" stroke="#F08A2C" stroke-width="1.3" fill="none"/>'
               f'<path d="M26.4 52.6 L28 56.4 L32 55.2 L36 56.4 L37.6 52.6" fill="#F4F4F6" {O}/><path d="M32 55.4 V64" stroke="#8A8A96" stroke-width="1.1"/>')
    on = (f'<path d="M13 34 L10.6 21 L17.6 23.4 L18.4 12 L25 18.6 L30 7.6 L34.4 17.4 L41.4 9.6 L42.6 19.4 L50.6 15.4 L48.6 24.4 L53 31 '
          f'Q47 22.6 40.4 24.6 Q36.4 20.4 32 25.6 Q27.4 20.4 23.4 24.6 Q18 23.6 13 34 Z" fill="{c}" stroke="{g}" stroke-width="1.3" stroke-linejoin="round"/>'
          f'<path d="M21.4 15 Q28 11.4 35 12.6" stroke="{g}" stroke-width="1.3" fill="none" opacity="0.85"/>')
    return kiyafet + yuz("duz") + on + goz("subaru", acik, kucuk=True)


def beatrice(acik):
    c, g = EKIP["beatrice"][1:3]
    matkap = ""
    for x, yon in ((8.6, 1), (55.4, -1)):
        for k in range(6):
            matkap += f'<ellipse cx="{x + yon*0.9*(k % 2)}" cy="{29 + k*5.8}" rx="{6.6 - k*0.6:.1f}" ry="3.7" fill="{c}" stroke="{g}" stroke-width="1"/>'
        matkap += f'<path d="M{x-3.2} 63 L{x} 60.4 L{x+3.2} 63 Z" fill="#E86A9C" {O}/>'   # pembe kurdele uclari
    kiyafet = govde("#C9356E", f'<path d="M20 55.4 Q32 61 44 55.4 L43 58.6 Q32 63.4 21 58.6 Z" fill="#FFFFFF" {O}/>'
                               f'<path d="M29.4 54 L32 56.6 L34.6 54 L34.6 58 L32 56.6 L29.4 58 Z" fill="#F07FA8" {O}/>')
    on = (f'<path d="M13 33 Q13 11 32 10 Q51 11 51 33 Q46 22 40 24 Q37 19 32 25 Q27 19 24 24 Q18 22 13 33 Z" fill="{c}" {O}/>'
          f'<path d="M22 24 L24.6 31 M32 24 L32 30.6 M42 24 L39.4 31" stroke="{g}" stroke-width="1.1" stroke-linecap="round"/>{PARLA}')
    tac = (f'<g transform="rotate(14 38 9)"><path d="M31 11.4 L31.8 5.4 L34.6 8.6 L37.2 3.6 L39.8 8.6 L42.6 5.4 L43.4 11.4 Z" '
           f'fill="#F2C94C" {O}/><circle cx="37.2" cy="8.6" r="0.9" fill="#E8508A"/></g>')
    kurdele = f'<path d="M14.8 22 L11 18.4 L11 25.4 Z M14.8 22 L18.6 18.6 L18.4 25.4 Z" fill="#E86A9C" {O}/><circle cx="14.8" cy="22" r="1.4" fill="#C9356E"/>'
    return matkap + kiyafet + yuz("duz") + on + goz("beatrice", acik, kelebek=True) + tac + kurdele


def hizmetci(ad, acik, ortu_sag_izleyici):
    """Rem ve Ram birbirinin aynasi: Rem kakulu sag gozunu (izleyicinin solu), Ram sol gozunu (izleyicinin sagi) orter."""
    c, g = EKIP[ad][1:3]
    kiyafet = govde("#23243A", f'<path d="M25 53.6 L32 60.4 L39 53.6" fill="#FFFFFF" {O}/><circle cx="32" cy="57" r="1.3" fill="#C8507D"/>')
    yan = (f'<path d="M12.4 42 Q11 24 18 17 L20 36 Z" fill="{c}" {O}/><path d="M51.6 42 Q53 24 46 17 L44 36 Z" fill="{c}" {O}/>')
    kapak = f'<path d="M13 30 Q13 10.6 32 10 Q51 10.6 51 30 Q47 21 41 22 Q36 20 32 23 Q28 20 23 22 Q17 21 13 30 Z" fill="{c}" {O}/>'
    if ortu_sag_izleyici:   # Ram: izleyicinin sagindaki gozu orten kakul
        kakul = f'<path d="M30 20 Q44 21 49.6 38 Q46 34 43.4 31.4 Q40 34.4 35.4 33.6 Q37 27 30 20 Z" fill="{c}" {O}/>'
        sus_x = 20.6
    else:                   # Rem: izleyicinin solundaki gozu orten kakul
        kakul = f'<path d="M34 20 Q20 21 14.4 38 Q18 34 20.6 31.4 Q24 34.4 28.6 33.6 Q27 27 34 20 Z" fill="{c}" {O}/>'
        sus_x = 43.4
    basortu = (f'<path d="M17 16 Q32 5 47 16 L45 19.6 Q32 10.6 19 19.6 Z" fill="#FFFFFF" {O}/>'
               f'<path d="M22 14.4 L24.6 16.6 M28.6 11.8 L30.4 14.4 M35 11.8 L36 14.6 M41.4 14 L42.4 16.6" stroke="#B4B4C6" stroke-width="0.8"/>')
    # cicek bicimli kurdele (Rem: sol yani = izleyicinin sagi, Ram: sag yani = izleyicinin solu)
    cicek = (f'<g transform="translate({sus_x} 22.6)">'
             + "".join(f'<ellipse cx="{x}" cy="{y}" rx="2" ry="1.6" fill="#FFFFFF" stroke="{C}" stroke-width="0.6" transform="rotate({r} {x} {y})"/>'
                       for x, y, r in ((0, -2.4, 0), (2.3, -0.7, 72), (1.4, 2, 144), (-1.4, 2, 216), (-2.3, -0.7, 288)))
             + '<circle cx="0" cy="0" r="1.1" fill="#C8507D"/></g>')
    return yan + kiyafet + yuz() + goz(ad, acik) + kapak + kakul + basortu + cicek


def rem(acik):
    return hizmetci("rem", acik, False)


def ram(acik):
    return hizmetci("ram", acik, True)


def julius(acik):
    c, g = EKIP["julius"][1:3]
    # beyaz palto, kirmizi kollar ve seritler, yakali pelerin
    kiyafet = (f'<path d="M14 64 Q15 54 26 52.6 L32 56 L38 52.6 Q49 54 50 64 Z" fill="#FFFFFF" {O}/>'
               f'<path d="M14 64 Q14.6 57.6 19.4 55 L20.6 64 Z M50 64 Q49.4 57.6 44.6 55 L43.4 64 Z" fill="#C3283A"/>'
               f'<path d="M26 52.6 L32 56 L38 52.6" stroke="#C3283A" stroke-width="1.4" fill="none"/>'
               f'<path d="M32 56 V64" stroke="#C3283A" stroke-width="1.2"/><circle cx="32" cy="59" r="1.4" fill="#E3BC4E"/>')
    on = (f'<path d="M13 33 Q13 11 32 10 Q51 11 51 33 Q47 22 37 22 Q30 21 24 25 Q18 25 13 33 Z" fill="{c}" {O}/>{PARLA}')
    # yuzun onune kivrilarak dusen tek tutam (izleyicinin solundaki gozun disina dogru)
    tutam = (f'<path d="M35 21 Q25 26 19.6 37.4" stroke="{C}" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
             f'<path d="M35 21 Q25 26 19.6 37.4" stroke="{c}" stroke-width="2.1" fill="none" stroke-linecap="round"/>')
    return kiyafet + yuz("duz") + on + goz("julius", acik) + tutam


def anastasia(acik):
    c, g = EKIP["anastasia"][1:3]
    arka = (f'<path d="M10 31 Q4 42 10 50 Q5 56 12 63 L23 63 Q17 48 19 34 Z" fill="{c}" {O}/>'
            f'<path d="M54 31 Q60 42 54 50 Q59 56 52 63 L41 63 Q47 48 45 34 Z" fill="{c}" {O}/>')
    kiyafet = govde("#FFFFFF")
    atki = (f'<path d="M13 54 Q32 63.4 51 54 Q51.4 61 32 64 Q12.6 61 13 54 Z" fill="#FFFFFF" {O}/>'      # Echidna (tilki atki)
            f'<path d="M46 53 L52.4 46 L53 54.4 Z" fill="#FFFFFF" {O}/><path d="M49 51.4 L51.6 48.6" stroke="#F2B8C6" stroke-width="0.9"/>'
            f'<circle cx="49" cy="55" r="0.9" fill="{C}"/>')
    on = (f'<path d="M13 33 Q13 11 32 10 Q51 11 51 33 Q46 22 40 24 Q37 19 32 25 Q27 19 24 24 Q18 22 13 33 Z" fill="{c}" {O}/>'
          f'<path d="M22 24 L24.6 31 M42 24 L39.4 31" stroke="{g}" stroke-width="1.1" stroke-linecap="round"/>')
    # beyaz kabarik sapka: bulut kenarli yuvarlak bere
    sapka = (f'<path d="M14 18 Q10 14 14 11 Q14 5 21 6 Q24 1.6 30 3.6 Q35 0.6 40 3.6 Q46 2.4 48 7.6 Q54 9.4 51.4 14.4 Q53.6 18 49.6 19.2 '
             f'Q32 13.4 14 18 Z" fill="#FFFFFF" {O}/>'
             f'<path d="M20 10.4 Q22.4 8.6 25 10 M30 7.4 Q32.6 5.8 35 7.4 M39.6 9 Q42 7.6 44.4 9.4" stroke="#D6D0E0" stroke-width="0.9" fill="none" stroke-linecap="round"/>')
    yildiz = f'<path d="M45 22 L46.2 24.6 L49 24.8 L46.8 26.6 L47.6 29.4 L45 27.8 L42.4 29.4 L43.2 26.6 L41 24.8 L43.8 24.6 Z" fill="#F2C94C" {O}/>'
    return arka + kiyafet + atki + yuz() + on + goz("anastasia", acik) + sapka + yildiz


def meili(acik):
    c, g = EKIP["meili"][1:3]
    orgu = f'<path d="M13.6 31 Q9 41 12.4 47" stroke="{C}" stroke-width="7.4" fill="none" stroke-linecap="round"/><path d="M13.6 31 Q9 41 12.4 47" stroke="{c}" stroke-width="5.6" fill="none" stroke-linecap="round"/>'
    for k in range(5):
        orgu += f'<ellipse cx="{12.6 + (k % 2)*0.9}" cy="{45.4 + k*3.8}" rx="3.4" ry="2.5" fill="{c}" stroke="{C}" stroke-width="0.8"/>'
    orgu += '<circle cx="13.4" cy="63.2" r="1.6" fill="#A9CBFF"/>'
    kiyafet = govde("#3E5DAA", f'<path d="M24 54 Q32 59 40 54 L39 56.6 Q32 60.6 25 56.6 Z" fill="#AFD0FF" {O}/>')
    on = (f'<path d="M13 33 Q13 11 32 10 Q51 11 51 33 Q46 23 39 24 Q33 21 27 25 Q20 22 13 33 Z" fill="{c}" {O}/>{PARLA}')
    return kiyafet + yuz() + on + goz("meili", acik) + orgu


def shaula(acik):
    c, g = EKIP["shaula"][1:3]
    arka = (f'<path d="M13 31 Q10 47 15 60 L22 60 Q17 47 19 34 Z" fill="{c}" {O}/><path d="M51 31 Q54 47 49 60 L42 60 Q47 47 45 34 Z" fill="{c}" {O}/>')
    kuyruk = ""   # arkadan yukselip kivrilan akrep kuyrugu orgu + igne
    for x, y, r in ((45, 23, 4.5), (49.6, 18.4, 4.2), (53.4, 13.8, 3.9), (54.6, 8.8, 3.6), (52.4, 4.8, 3.3), (48.2, 3.6, 3)):
        kuyruk += f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.82:.1f}" fill="{c}" stroke="{g}" stroke-width="1"/>'
    kuyruk += f'<path d="M46 2 L39.4 5.6 L45.6 6.4 Z" fill="#C9A24A" {O}/>'
    kiyafet = (f'<path d="M12 64 Q13 52.6 24 51.6 L32 56.6 L40 51.6 Q51 52.6 52 64 Z" fill="#E0762A" {O}/>'
               f'<path d="M20 64 Q21 54.6 32 53.6 Q43 54.6 44 64 Z" fill="#141218" {O}/>'
               f'<path d="M29 54.2 L32 55.6 L35 54.2 L35 57 L32 55.6 L29 57 Z" fill="#E0762A" {O}/>'
               f'<path d="M25 53.2 Q32 58.6 39 53.2" stroke="#D9B45A" stroke-width="0.9" fill="none"/>')
    on = (f'<path d="M13 33 Q13 11 32 10 Q51 11 51 33 Q46 22 40 24 Q37 19 32 25 Q27 19 24 24 Q18 22 13 33 Z" fill="{c}" {O}/>'
          f'<path d="M22 24 L24.6 31 M32 24 L32 30.6 M42 24 L39.4 31" stroke="{g}" stroke-width="1.1" stroke-linecap="round"/>{PARLA}')
    return arka + kuyruk + kiyafet + yuz("acik") + on + goz("shaula", acik, akrep=True)


CIZ = {"emilia": emilia, "subaru": subaru, "beatrice": beatrice, "rem": rem, "ram": ram,
       "julius": julius, "anastasia": anastasia, "meili": meili, "shaula": shaula}


def svg(i, acik):
    ad, _, _, u, a = EKIP[i]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">\n'
            f'<!-- {ad} (Re:Zero) chibi v3 - Break Time tarzindan esinlenen ozgun cizim (sistem-bakim) -->\n'
            f'{defs(i, u, a)}{CIZ[i](acik)}\n</svg>')


if __name__ == "__main__":
    os.makedirs(CIKTI, exist_ok=True)
    for i in EKIP:
        for acik in (True, False):
            open(os.path.join(CIKTI, f"{i}-{'acik' if acik else 'kapali'}.svg"), "w").write(svg(i, acik))
    print("cizildi:", ", ".join(EKIP))
