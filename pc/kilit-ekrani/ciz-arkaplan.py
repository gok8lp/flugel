#!/usr/bin/env python3
"""FLUGEL kilit ekrani arka plani (Re:Zero): Augria kum tepelerinde gece, Pleiades Gozetleme Kulesi,
Flugel'in Buyuk Agaci ve Pleiades yildiz kumesi. Siyah-gri, ay isigi tonlari. Calistir: python3 ciz-arkaplan.py"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import math, random, os
W, H = 3840, 2400
OUT = os.path.expanduser("~/.local/share/backgrounds/flugel-kilit.png")
R = random.Random(1907)

def katman():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def yumusat(img, r):
    return img.filter(ImageFilter.GaussianBlur(r))

# 1) gokyuzu: yukari neredeyse siyah, ufuga dogru gumus-gri
gok = Image.new("RGB", (W, H)); d = ImageDraw.Draw(gok)
for y in range(H):
    t = (y / H) ** 1.6
    c = (int(6 + 30 * t), int(7 + 31 * t), int(11 + 36 * t))
    d.line([(0, y), (W, y)], fill=c)
gok = gok.convert("RGBA")

# 2) samanyolu: capraz, bulanik gurultu bandi
bant = katman(); db = ImageDraw.Draw(bant)
for _ in range(9000):
    t = R.random(); x = -200 + t * (W + 400); y = 1500 - t * 1350 + R.gauss(0, 170)
    r = R.uniform(8, 60); a = R.randint(2, 9)
    db.ellipse([x - r, y - r, x + r, y + r], fill=(215, 220, 235, a))
gok = Image.alpha_composite(gok, yumusat(bant, 40))

# 3) yildizlar
yz = katman(); dy = ImageDraw.Draw(yz)
for _ in range(2600):
    x, y = R.uniform(0, W), R.uniform(0, H * 0.78) ** 1.0
    b = int(255 * R.random() ** 2.2); r = R.choice([1, 1, 1, 1.5, 2])
    dy.ellipse([x - r, y - r, x + r, y + r], fill=(235, 238, 248, b))
parlak = katman(); dp = ImageDraw.Draw(parlak)
for _ in range(60):
    x, y = R.uniform(0, W), R.uniform(0, H * 0.6); r = R.uniform(2.5, 4)
    dp.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))
gok = Image.alpha_composite(gok, yz)
gok = Image.alpha_composite(gok, yumusat(parlak, 6)); gok = Image.alpha_composite(gok, parlak)

# 4) Pleiades kumesi (Yedi Kardes) — pirilti haclari ile
def pirilti(dr, x, y, boy, a=255):
    for ux, uy in ((1, 0), (0, 1)):
        for k in range(boy, 0, -2):
            al = int(a * (1 - k / boy) ** 1.5)
            dr.line([(x - ux * k, y - uy * k), (x + ux * k, y + uy * k)], fill=(240, 244, 255, al), width=2)
    dr.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255, a))
pl = katman(); dpl = ImageDraw.Draw(pl)
for (x, y, s) in [(1880, 250, 70), (1955, 220, 52), (2000, 292, 60), (1915, 330, 44), (2052, 238, 40), (1840, 315, 36), (1965, 372, 34)]:
    pirilti(dpl, x, y, s)
gok = Image.alpha_composite(gok, yumusat(pl, 10)); gok = Image.alpha_composite(gok, pl)

# 5) ay (kulenin arkasinda)
MX, MY, MR = 2930, 760, 300
hale = katman(); dh = ImageDraw.Draw(hale)
for i in range(14, 0, -1):
    r = MR + i * 55; dh.ellipse([MX - r, MY - r, MX + r, MY + r], fill=(200, 205, 220, int(5 + 3 * (14 - i))))
gok = Image.alpha_composite(gok, yumusat(hale, 50))
ay = katman(); da = ImageDraw.Draw(ay)
da.ellipse([MX - MR, MY - MR, MX + MR, MY + MR], fill=(226, 228, 234, 255))
lek = katman(); dl = ImageDraw.Draw(lek)
for _ in range(38):
    a = R.uniform(0, 2 * math.pi); q = MR * math.sqrt(R.random()) * 0.92; r = R.uniform(14, 70)
    x, y = MX + q * math.cos(a), MY + q * math.sin(a)
    dl.ellipse([x - r, y - r, x + r, y + r], fill=(150, 154, 166, R.randint(25, 70)))
lek = yumusat(lek, 9)
maske = Image.new("L", (W, H), 0); ImageDraw.Draw(maske).ellipse([MX - MR, MY - MR, MX + MR, MY + MR], fill=255)
ay = Image.alpha_composite(ay, Image.composite(lek, katman(), maske))
golge = katman(); ImageDraw.Draw(golge).ellipse([MX - MR - 120, MY - MR + 40, MX + MR - 120, MY + MR + 40], fill=(20, 22, 30, 120))
ay = Image.alpha_composite(ay, Image.composite(yumusat(golge, 40), katman(), maske))
gok = Image.alpha_composite(gok, ay)

# kum tepesi egrisi
def tepe(x, taban, genlik, faz, dalga):
    return taban + genlik * math.sin(x / dalga + faz) + genlik * 0.35 * math.sin(x / (dalga * 0.37) + faz * 1.7)

def tepe_ciz(taban, genlik, faz, dalga, renk, kenar):
    k = katman(); dk = ImageDraw.Draw(k)
    noktalar = [(x, tepe(x, taban, genlik, faz, dalga)) for x in range(0, W + 9, 8)]
    dk.polygon(noktalar + [(W, H), (0, H)], fill=renk)
    dk.line(noktalar, fill=kenar, width=3)
    return k

# 6) arka tepeler
gok = Image.alpha_composite(gok, tepe_ciz(1790, 70, 0.4, 610, (30, 32, 40, 255), (120, 124, 138, 90)))

# 7) Pleiades Gozetleme Kulesi (sag, ayin onunde)
KX = 2990; KT = tepe(KX, 1950, 60, 2.1, 520) + 20
ku = katman(); dk = ImageDraw.Draw(ku); KR = (12, 13, 18, 255)
y = KT
katlar = [(420, 250), (350, 300), (290, 280), (236, 240), (190, 200), (150, 160), (116, 120)]
pencere = []
for i, (w, h) in enumerate(katlar):
    ust = y - h; uw = w * 0.86
    dk.polygon([(KX - w / 2, y), (KX - uw / 2, ust), (KX + uw / 2, ust), (KX + w / 2, y)], fill=KR)
    dk.rectangle([KX - uw / 2 - 12, ust - 10, KX + uw / 2 + 12, ust + 4], fill=KR)
    n = 3 if i < 2 else (2 if i < 5 else 1)
    for j in range(n):
        px = KX + (j - (n - 1) / 2) * (uw / (n + 0.6)); py = y - h * 0.62
        pencere.append((px, py, max(6, w * 0.03), h * 0.26))
    y = ust
dk.polygon([(KX - 50, y), (KX, y - 210), (KX + 50, y)], fill=KR)
dk.ellipse([KX - 22, y - 262, KX + 22, y - 218], fill=KR)
dk.line([(KX, y - 262), (KX, y - 330)], fill=KR, width=6)
isik = katman(); di = ImageDraw.Draw(isik)
for (px, py, pw, ph) in pencere:
    di.rectangle([px - pw, py, px + pw, py + ph], fill=(225, 228, 236, 70))
    di.ellipse([px - pw, py - pw, px + pw, py + pw], fill=(225, 228, 236, 70))
ku = Image.alpha_composite(ku, Image.composite(isik, katman(), ku.getchannel("A")))
# ay tarafinda ince kenar isigi
kenar = ImageChops.subtract(ku.getchannel("A"), ku.getchannel("A").transform((W, H), Image.AFFINE, (1, 0, -5, 0, 1, 0)))
kk = Image.new("RGBA", (W, H), (180, 186, 200, 0)); kk.putalpha(kenar.point(lambda a: a // 3))
gok = Image.alpha_composite(gok, yumusat(ku, 3)); gok = Image.alpha_composite(gok, ku); gok = Image.alpha_composite(gok, kk)

# 8) orta tepeler
gok = Image.alpha_composite(gok, tepe_ciz(1980, 60, 2.1, 520, (18, 19, 25, 255), (150, 154, 168, 110)))

# 9) Flugel'in Buyuk Agaci (sol)
ag = katman(); dg = ImageDraw.Draw(ag); AR = (8, 8, 12, 255)
yaprak = []
def dal(x, y, aci, boy, kalin, derin):
    x2 = x + boy * math.cos(aci); y2 = y - boy * math.sin(aci)
    dg.line([(x, y), (x2, y2)], fill=AR, width=max(2, int(kalin)))
    dg.ellipse([x2 - kalin / 2, y2 - kalin / 2, x2 + kalin / 2, y2 + kalin / 2], fill=AR)
    if derin == 0 or boy < 18:
        yaprak.append((x2, y2)); return
    for _ in range(2 if derin > 5 else R.choice([2, 3])):
        yay = R.uniform(0.28, 0.62) * R.choice([-1, 1])
        dal(x2, y2, aci + yay + (math.pi / 2 - aci) * 0.12, boy * R.uniform(0.66, 0.8), kalin * 0.66, derin - 1)
AX = 760; AY = tepe(AX, 1980, 60, 2.1, 520) + 30
# govde + kokler
dg.polygon([(AX - 120, AY + 40), (AX - 62, AY - 420), (AX + 62, AY - 420), (AX + 140, AY + 40)], fill=AR)
for s in (-1, 1):
    for k in range(3):
        dg.line([(AX + s * 40, AY - 20), (AX + s * (180 + k * 110), AY + 40 + k * 22)], fill=AR, width=34 - k * 9)
for a, b in [(1.95, 1.0), (1.2, 1.0), (1.6, 1.08), (2.45, 0.85), (0.72, 0.85)]:
    dal(AX + (a - 1.6) * 50, AY - 400, a, 235 * b, 62, 8)
# yapraklar: dal uclarinda yogun kumeler
for (x, y) in yaprak:
    for _ in range(6):
        r = R.uniform(34, 80); ox, oy = R.gauss(0, 30), R.gauss(0, 24)
        dg.ellipse([x + ox - r, y + oy - r * 0.8, x + ox + r, y + oy + r * 0.8], fill=AR)
# ay isigi: agacin sag ust kenarlari
ka = ag.getchannel("A")
kenar = ImageChops.subtract(ka, ka.transform((W, H), Image.AFFINE, (1, 0, -6, 0, 1, 5)))
ki = Image.new("RGBA", (W, H), (160, 166, 182, 0)); ki.putalpha(yumusat(kenar.convert("RGBA"), 1).getchannel("R").point(lambda a: a // 4) if False else kenar.point(lambda a: a // 4))
# agaca suzulen isik parcaciklari (Flugel'in buyusu)
pc = katman(); dpc = ImageDraw.Draw(pc)
for _ in range(140):
    x = R.gauss(AX, 420); y = R.gauss(AY - 760, 300); r = R.uniform(1.5, 4)
    dpc.ellipse([x - r, y - r, x + r, y + r], fill=(235, 238, 250, R.randint(90, 230)))
gok = Image.alpha_composite(gok, yumusat(ag, 2)); gok = Image.alpha_composite(gok, ag)
gok = Image.alpha_composite(gok, yumusat(pc, 5)); gok = Image.alpha_composite(gok, pc)

# 10) on tepe + kum serpintisi
gok = Image.alpha_composite(gok, tepe_ciz(2200, 55, 4.0, 700, (9, 9, 12, 255), (120, 124, 138, 70)))
kum = katman(); dku = ImageDraw.Draw(kum)
for _ in range(1800):
    x = R.uniform(0, W); y = R.uniform(1750, H); dku.point((x, y), fill=(200, 204, 215, R.randint(20, 80)))
gok = Image.alpha_composite(gok, kum)

# 11) vinyet + ortada saat icin hafif karartma + gren
vin = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vin)
for i in range(40):
    t = i / 40; dv.ellipse([-W * 0.25 + t * W * 0.3, -H * 0.25 + t * H * 0.3, W * 1.25 - t * W * 0.3, H * 1.25 - t * H * 0.3], fill=int(255 * t))
vin = yumusat(vin, 120)
siyah = Image.new("RGBA", (W, H), (0, 0, 0, 255))
gok = Image.composite(gok, Image.blend(gok, siyah, 0.55), vin)
orta = Image.new("L", (W, H), 0); ImageDraw.Draw(orta).ellipse([W * 0.32, H * 0.22, W * 0.68, H * 0.62], fill=70)
gok = Image.composite(siyah, gok, yumusat(orta, 220))
gren = Image.effect_noise((W, H), 18).convert("RGBA"); gren.putalpha(14)
gok = Image.alpha_composite(gok, gren)
gok.convert("RGB").save(OUT, optimize=True)
gok.convert("RGB").resize((960, 600), Image.LANCZOS).save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "onizleme.png"))
print("kaydedildi:", OUT)
