from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
w, h = im.size

# Crop around grooms area
cx, cy = int(0.49 * w), int(0.635 * h)
half = 80
box = (cx - half, cy - half, cx + half, cy + half)
crop = im.crop(box).copy()
draw = ImageDraw.Draw(crop)

candidates = [
    ("A", 47.1, 65.8),
    ("B", 48.0, 65.0),
    ("C", 49.0, 64.5),
    ("D", 49.5, 64.0),
    ("E", 50.0, 63.5),
    ("F", 47.5, 64.8),
    ("G", 48.5, 65.5),
    ("H", 46.5, 65.2),
]

colors = {
    "A": (255, 0, 0),
    "B": (255, 128, 0),
    "C": (255, 255, 0),
    "D": (0, 255, 0),
    "E": (0, 255, 255),
    "F": (0, 128, 255),
    "G": (255, 0, 255),
    "H": (255, 255, 255),
}

for name, xp, yp in candidates:
    x = xp / 100 * w - box[0]
    y = yp / 100 * h - box[1]
    col = colors[name]
    draw.ellipse([x - 3, y - 3, x + 3, y + 3], outline=col, width=2)
    draw.text((x + 5, y - 8), name, fill=col)

crop = crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST)
out = Path(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v11-final\grooms-candidates.png")
crop.save(out)
print("wrote", out, "box", box)
