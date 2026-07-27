from PIL import Image, ImageDraw
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
w, h = im.size

cands = [
    ("d1", 49.5, 62.4),
    ("d2", 49.2, 62.6),
    ("d3", 49.8, 62.5),
    ("d4", 49.0, 62.3),
    ("d5", 50.0, 62.5),
    ("d6", 49.4, 62.2),
]

out_dir = Path(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v11-final")
for name, xp, yp in cands:
    tx, ty = xp / 100 * w, yp / 100 * h
    box = (int(tx - 50), int(ty - 70), int(tx + 50), int(ty + 40))
    crop = im.crop(box).copy()
    d = ImageDraw.Draw(crop)
    lx, ly = tx - box[0], ty - box[1]
    d.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], outline=(255, 0, 0), width=2)
    d.line([lx - 10, ly, lx + 10, ly], fill=(255, 255, 0))
    d.line([lx, ly - 10, lx, ly + 10], fill=(255, 255, 0))
    crop = crop.resize((crop.width * 2, crop.height * 2), Image.NEAREST)
    crop.save(out_dir / f"grooms-{name}.png")
    print(name, xp, yp)
