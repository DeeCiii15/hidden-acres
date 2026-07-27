from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

pin_body = (
    (g > 35)
    & (g < 125)
    & (r < 110)
    & (b < 95)
    & (g > r + 5)
    & (g > b + 5)
    & ((g - r) + (g - b) > 25)
)
label = (r > 140) & (g > 155) & (b > 130) & (g >= r - 5) & ((r + g + b) > 450)
dirs8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

# Hand-confirmed label centers (from detection + window search)
seeds = {
    "the-inn": (67.7, 4.3),
    "the-chapel": (42.8, 32.0),
    "ceremony-pond": (32.7, 52.7),
    "rusted-silo": (63.0, 56.4),
    "grooms-quarters": (47.1, 61.6),
    "courtyard-pavilion": (60.5, 66.6),
    "the-ballroom": (54.0, 74.9),
    "bridal-suite-salon": (71.5, 73.0),
}

out_dir = Path(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v11-final")
out_dir.mkdir(exist_ok=True)

final = {}
ov = im.copy()
draw = ImageDraw.Draw(ov)

for name, (lxp, lyp) in seeds.items():
    cx, cy = lxp / 100 * w, lyp / 100 * h
    # find mint bbox near seed
    x0, x1 = max(0, int(cx) - 35), min(w, int(cx) + 35)
    y0, y1 = max(0, int(cy) - 25), min(h, int(cy) + 25)
    sub = label[y0:y1, x0:x1]
    if sub.any():
        sy, sx = np.where(sub)
        # use only mint near seed
        d = (sx + x0 - cx) ** 2 + (sy + y0 - cy) ** 2
        keep = d < 28 ** 2
        sx, sy = sx[keep], sy[keep]
        if len(sx) == 0:
            sy, sx = np.where(sub)
        x_min, x_max = int(sx.min() + x0), int(sx.max() + x0)
        y_min, y_max = int(sy.min() + y0), int(sy.max() + y0)
        cx = float(sx.mean() + x0)
        cy = float(sy.mean() + y0)
    else:
        x_min, x_max = int(cx - 12), int(cx + 12)
        y_min, y_max = int(cy - 8), int(cy + 8)

    max_r_top = max(18, (x_max - x_min) / 2 + 14)
    seeds_px = []
    for y in range(max(0, y_min - 6), min(h, y_max + 10)):
        for x in range(max(0, x_min - 12), min(w, x_max + 12)):
            if pin_body[y, x]:
                seeds_px.append((y, x))

    visited = np.zeros((h, w), dtype=bool)
    stack = []
    for y, x in seeds_px:
        if not visited[y, x]:
            visited[y, x] = True
            stack.append((y, x))
    pts_x, pts_y = [], []
    while stack:
        y, x = stack.pop()
        if y <= y_max + 2:
            max_r = max_r_top
        else:
            t = (y - (y_max + 2)) / 58.0
            if t > 1.15:
                continue
            max_r = max_r_top * max(0.06, 1.0 - t * 0.96)
        if abs(x - cx) > max_r:
            continue
        pts_x.append(x)
        pts_y.append(y)
        for dy, dx in dirs8:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and pin_body[ny, nx]:
                visited[ny, nx] = True
                stack.append((ny, nx))

    if len(pts_x) < 50:
        print(f"{name}: FAIL n={len(pts_x)}")
        continue

    xs = np.array(pts_x)
    ys = np.array(pts_y)
    tip_y = int(ys.max())
    tip_x = float(np.median(xs[ys >= tip_y - 1]))
    # walk up a few rows for the actual pointy tip (narrowest bottom)
    for row in range(tip_y, tip_y - 6, -1):
        row_xs = xs[ys == row]
        if len(row_xs) == 0:
            continue
        tip_x = float(np.median(row_xs))
        tip_y = row
        if len(row_xs) <= 3:
            break

    xp, yp = tip_x / w * 100, tip_y / h * 100
    final[name] = (round(xp, 1), round(yp, 1))
    print(f"{name}: tip%=({xp:.2f},{yp:.2f}) px=({tip_x:.1f},{tip_y}) n={len(pts_x)} label%=({cx/w*100:.1f},{cy/h*100:.1f})")

    # crop
    half = 60
    cx0, cy0 = int(tip_x), int(tip_y)
    crop_box = (max(0, cx0 - half), max(0, cy0 - half - 20), min(w, cx0 + half), min(h, cy0 + half))
    crop = im.crop(crop_box).copy()
    cd = ImageDraw.Draw(crop)
    lx, ly = tip_x - crop_box[0], tip_y - crop_box[1]
    cd.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], outline=(255, 0, 0), width=2)
    cd.line([lx - 10, ly, lx + 10, ly], fill=(255, 255, 0))
    cd.line([lx, ly - 10, lx, ly + 10], fill=(255, 255, 0))
    crop.save(out_dir / f"{name}.png")

    draw.ellipse([tip_x - 5, tip_y - 5, tip_x + 5, tip_y + 5], outline=(255, 0, 0), width=2)
    draw.line([tip_x - 12, tip_y, tip_x + 12, tip_y], fill=(255, 255, 0))
    draw.line([tip_x, tip_y - 12, tip_x, tip_y + 12], fill=(255, 255, 0))
    draw.text((tip_x + 6, tip_y - 10), name.split("-")[0][:5], fill=(255, 0, 255))

ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v11-final-tips.png")
print("\nFINAL:")
for k, v in final.items():
    print(f"  {k}: {v}")
