"""GDM giris ekrani: alttaki logo (FLUGEL) + kullanici resmi (F monogram). Cinzel, beyaz/gumus. (sistem-bakim)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
T = os.path.dirname(os.path.abspath(__file__))
F = os.path.expanduser("~/sistem-bakim/acilis-flugel/Cinzel.ttf")
# 1) logo: FLUGEL, genis harf araligi, hafif parilti
font = ImageFont.truetype(F, 120); font.set_variation_by_axes([500])
harfler, aralik = "FLUGEL", 46
gen = sum(font.getlength(h) for h in harfler) + aralik * (len(harfler) - 1)
W, H = int(gen) + 80, 200
im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 40
for h in harfler:
    d.text((x, 30), h, font=font, fill=(244, 245, 250, 255)); x += font.getlength(h) + aralik
g = im.filter(ImageFilter.GaussianBlur(10)); g.putalpha(g.getchannel("A").point(lambda a: int(a * .45)))
logo = Image.alpha_composite(g, im)
logo.resize((W // 2, H // 2), Image.LANCZOS).save(f"{T}/flugel-gdm-logo.png")
# 2) kullanici resmi: koyu daire icinde F
S = 512
av = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(av)
for i in range(S // 2, 0, -1):   # yumusak radyal gecis
    t = i / (S / 2); c = int(18 + 34 * (1 - t))
    d.ellipse([S/2 - i, S/2 - i, S/2 + i, S/2 + i], fill=(c, c + 2, c + 8, 255))
d.ellipse([10, 10, S - 10, S - 10], outline=(220, 224, 236, 90), width=4)
f2 = ImageFont.truetype(F, 300); f2.set_variation_by_axes([600])
b = d.textbbox((0, 0), "F", font=f2)
d.text(((S - (b[2] - b[0])) / 2 - b[0], (S - (b[3] - b[1])) / 2 - b[1]), "F", font=f2, fill=(246, 247, 252, 255))
av.save(f"{T}/flugel-avatar.png")
print("ok", logo.size)
