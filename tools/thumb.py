"""Thumbnail-style cover frame: python3 thumb.py image.jpg "LINEA 1|LINEA 2" out.png [badge]"""
import sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1080, 1920
img, text, out = sys.argv[1], sys.argv[2], sys.argv[3]
badge = sys.argv[4] if len(sys.argv) > 4 else "GTA 6"
FONT = glob.glob("/usr/share/fonts/truetype/google-fonts/ofl/anton/*.ttf")[0]
im = Image.open(img).convert("RGB")
s = H / im.height; im = im.resize((int(im.width * s), H))
x = (im.width - W) // 2; im = im.crop((x, 0, x + W, H))
im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.35)).enhance(1.15)
# dark gradients top and bottom for legibility
grad = Image.new("L", (1, H))
for y in range(H):
    t = y / H
    a = 210 if t < 0.0 else int(230 * max(0, 1 - t / 0.42)) if t < 0.42 else int(200 * max(0, (t - 0.72) / 0.28))
    grad.putpixel((0, y), a)
im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, grad.resize((W, H)))
d = ImageDraw.Draw(im)
lines = text.upper().split("|")
y = 230
colors = [(255, 255, 255), (255, 214, 0), (255, 255, 255)]
for i, ln in enumerate(lines):
    size = 190
    while True:
        f = ImageFont.truetype(FONT, size)
        w = d.textlength(ln, font=f)
        if w <= W - 100 or size < 80: break
        size -= 6
    d.text(((W - w) / 2, y), ln, font=f, fill=colors[i % 3], stroke_width=12, stroke_fill=(0, 0, 0))
    y += int(size * 1.12)
# badge
bf = ImageFont.truetype(FONT, 78)
bw = d.textlength(badge, font=bf) + 70
d.rounded_rectangle(((W - bw) / 2, 90, (W + bw) / 2, 200), 24, fill=(230, 30, 90))
d.text(((W - bw) / 2 + 35, 100), badge, font=bf, fill=(255, 255, 255))
im.save(out); print(out)
