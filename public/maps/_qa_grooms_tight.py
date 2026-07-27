from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# Tight pin fill (darker olive, exclude bright grass/trees a bit)
pin = (
    (g > 40) & (g < 110) & (r < 95) & (b < 85)
    & (g > r + 10) & (g > b + 10)
    & ((g - r) + (g - b) > 30)
)

# Groom label center from earlier
cx, cy = 0.471 * w, 0.621 * h

# Only search a small teardrop envelope under label, max ~45px down
pts = []
for y in range(int(cy - 5), int(cy + 48)):
    t = max(0, (y - cy) / 45.0)
    max_r = 20 * (1.0 - t * 0.92)
    if max_r < 1:
        break
    for x in range(int(cx - max_r), int(cx + max_r) + 1):
        if 0 <= x < w and pin[y, x]:
            pts.append((x, y))

print("pts", len(pts))
xs = np.array([p[0] for p in pts])
ys = np.array([p[1] for p in pts])
# tip = bottom-most, prefer center
tip_y = int(ys.max())
bottom = ys >= tip_y - 1
tip_x = float(np.median(xs[bottom]))
# walk up for narrow tip
for row in range(tip_y, tip_y - 8, -1):
    rowx = xs[ys == row]
    if len(rowx) == 0:
        continue
    tip_x = float(np.median(rowx))
    tip_y = row
    if len(rowx) <= 3:
        break

print(f"tip % ({tip_x/w*100:.2f}, {tip_y/h*100:.2f}) px=({tip_x:.1f},{tip_y})")

# Also compute tip as label_x + geometric offset using mean delta from good pins
# good deltas: inn 4.1, chapel 4.2, silo 3.6, court 3.7, ball 3.8, bridal 3.7, pond 55.9-52.6=3.3
mean_dy = 3.8
geo = (47.1, 62.1 + mean_dy)
print(f"geo % {geo}")

# Render both
for name, xp, yp in [("tight", tip_x/w*100, tip_y/h*100), ("geo", geo[0], geo[1]), ("blend", 47.5, 65.5)]:
    tx, ty = xp/100*w, yp/100*h
    half = 55
    box = (int(tx-half), int(ty-half-15), int(tx+half), int(ty+half))
    crop = im.crop(box).copy()
    d = ImageDraw.Draw(crop)
    lx, ly = tx - box[0], ty - box[1]
    d.ellipse([lx-4, ly-4, lx+4, ly+4], outline=(255,0,0), width=2)
    d.line([lx-10, ly, lx+10, ly], fill=(255,255,0))
    d.line([lx, ly-10, lx, ly+10], fill=(255,255,0))
    crop = crop.resize((crop.width*2, crop.height*2), Image.NEAREST)
    out = Path(rf"C:\Dev\hidden-acres\public\maps\_qa-crops-v11-final\grooms-{name}.png")
    crop.save(out)
    print("wrote", name, round(xp,1), round(yp,1))
