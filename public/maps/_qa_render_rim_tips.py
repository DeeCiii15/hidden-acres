from PIL import Image, ImageDraw
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
w, h = im.size

# Visually verified tips + rim-based fixes for pond/grooms
coords = {
    "the-inn": (67.4, 8.3),
    "the-chapel": (42.3, 36.4),
    "ceremony-pond": (33.6, 55.9),  # rim tip
    "rusted-silo": (63.5, 60.0),
    "grooms-quarters": (48.8, 64.3),  # rim tip
    "courtyard-pavilion": (60.4, 70.3),
    "the-ballroom": (54.0, 78.7),
    "bridal-suite-salon": (70.9, 76.7),
}

out_dir = Path(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v11-final")
for name, (xp, yp) in coords.items():
    tip_x, tip_y = xp / 100 * w, yp / 100 * h
    half = 60
    cx0, cy0 = int(tip_x), int(tip_y)
    box = (max(0, cx0 - half), max(0, cy0 - half - 20), min(w, cx0 + half), min(h, cy0 + half))
    crop = im.crop(box).copy()
    cd = ImageDraw.Draw(crop)
    lx, ly = tip_x - box[0], tip_y - box[1]
    cd.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], outline=(255, 0, 0), width=2)
    cd.line([lx - 10, ly, lx + 10, ly], fill=(255, 255, 0))
    cd.line([lx, ly - 10, lx, ly + 10], fill=(255, 255, 0))
    crop.save(out_dir / f"{name}.png")
    print(name, xp, yp)
