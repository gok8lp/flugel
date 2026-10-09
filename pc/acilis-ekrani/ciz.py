#!/usr/bin/env python3
"""FLÜGEL acilis ekrani gorselleri (Re:Zero'daki bilge Flugel'den esinlenme). Calistir: python3 ciz.py"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, json, os
T = os.path.dirname(os.path.abspath(__file__))
def glow(img, r=10, k=0.55):
    g = img.filter(ImageFilter.GaussianBlur(r)); g.putalpha(g.getchannel("A").point(lambda a: int(a * k)))
    return Image.alpha_composite(g, img)
# 1) FLÜGEL harfleri (Cinzel)
font = ImageFont.truetype(f"{T}/Cinzel.ttf", 230); font.set_variation_by_axes([400])
asc, desc = font.getmetrics(); H = asc + desc + 60
TAKIP = 34; of = []; x = 0
for i, h in enumerate("FLUGEL"):
    w = int(font.getlength(h)) + 60
    im = Image.new("RGBA", (w, H), (0, 0, 0, 0)); ImageDraw.Draw(im).text((30, 30), h, font=font, fill=(255, 255, 255, 255))
    glow(im, 12, 0.5).save(f"{T}/harf{i}.png"); of.append(x); x += int(font.getlength(h)) + TAKIP
G = x - TAKIP
# 2) Pleiades Gozetleme Kulesi
S = 2; KW, KH = 420, 1260
k = Image.new("RGBA", (KW * S, KH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(k); L = 3 * S; B = (255, 255, 255, 255); cx = KW * S / 2
y = KH * S - 10 * S
for i, (w, h) in enumerate([(330, 180), (270, 260), (220, 250), (176, 200), (140, 150)]):
    w *= S; h *= S; ust = y - h; uw = w * 0.86
    d.line([(cx - w / 2, y), (cx - uw / 2, ust)], fill=B, width=L); d.line([(cx + w / 2, y), (cx + uw / 2, ust)], fill=B, width=L)
    d.line([(cx - uw / 2 - 6 * S, ust), (cx + uw / 2 + 6 * S, ust)], fill=B, width=L); d.line([(cx - w / 2, y), (cx + w / 2, y)], fill=B, width=L)
    n = 3 if i < 2 else (2 if i < 4 else 1)
    for j in range(n):
        px = cx + (j - (n - 1) / 2) * (uw / (n + 0.6)); pw = 14 * S; ph = h * 0.32; py = y - h * 0.62
        d.line([(px - pw, py + ph), (px - pw, py)], fill=B, width=L - S); d.line([(px + pw, py + ph), (px + pw, py)], fill=B, width=L - S)
        d.arc([px - pw, py - pw, px + pw, py + pw], 180, 360, fill=B, width=L - S)
    y = ust
d.line([(cx - 30 * S, y), (cx, y - 120 * S), (cx + 30 * S, y)], fill=B, width=L)
d.ellipse([cx - 16 * S, y - 150 * S, cx + 16 * S, y - 118 * S], outline=B, width=L - S)
d.line([(cx, y - 150 * S), (cx, y - 190 * S)], fill=B, width=L - S)
glow(k.resize((KW, KH), Image.LANCZOS), 6, 0.6).save(f"{T}/kule.png")
# 3) Kum tepeleri
DW, DH = 2560, 260
dn = Image.new("RGBA", (DW * S, DH * S), (0, 0, 0, 0)); d = ImageDraw.Draw(dn)
for amp, faz, yy, gen in [(40, 0.0, 90, 3), (28, 1.7, 150, 2), (20, 3.1, 205, 2)]:
    d.line([(xx * S, (yy + amp * math.sin(xx / 420 + faz) + 12 * math.sin(xx / 170 + faz * 2)) * S) for xx in range(0, DW + 1, 8)], fill=B, width=gen * S)
dn.resize((DW, DH), Image.LANCZOS).save(f"{T}/kum.png")
# 4) Yildiz
Y = 48; s = Image.new("RGBA", (Y * S, Y * S), (0, 0, 0, 0)); d = ImageDraw.Draw(s); c = Y * S / 2
d.polygon([(c, 0), (c + 5 * S, c - 5 * S), (Y * S, c), (c + 5 * S, c + 5 * S), (c, Y * S), (c - 5 * S, c + 5 * S), (0, c), (c - 5 * S, c - 5 * S)], fill=B)
glow(s.resize((Y, Y), Image.LANCZOS), 4, 0.8).save(f"{T}/yildiz.png")
Image.new("RGBA", (4, 4), B).save(f"{T}/cizgi.png")
json.dump({"G": G, "H": H, "of": of}, open(f"{T}/olcu.json", "w"))
print("FLUGEL", G, H, of)
