from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

mask = (
    (g > 40)
    & (g < 160)
    & (g > r + 12)
    & (g > b + 12)
    & (r < 130)
    & (b < 120)
)
label = (r > 150) & (g > 160) & (b > 140) & ((r + g + b) > 470)

# Seeds near known label centers for v9 composition
seeds = {
    "the-inn": (56.0, 4.5),
    "the-chapel": (43.0, 29.0),
    "ceremony-pond": (33.0, 48.0),
    "grooms-quarters": (48.0, 56.0),
    "rusted-silo": (62.0, 54.0),
    "courtyard-pavilion": (60.0, 64.0),
    "the-ballroom": (54.0, 72.0),
    "bridal-suite-salon": (70.0, 70.0),
}

print(f"map {w}x{h}")
dirs8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
final = {}
ov = im.copy()
draw = ImageDraw.Draw(ov)

for name, (lxp, lyp) in seeds.items():
    cx, cy = lxp / 100 * w, lyp / 100 * h
    x0, x1 = max(0, int(cx) - 50), min(w, int(cx) + 50)
    y0, y1 = max(0, int(cy) - 40), min(h, int(cy) + 40)
    sub = label[y0:y1, x0:x1]
    if sub.any():
        sy, sx = np.where(sub)
        d = (sx + x0 - cx) ** 2 + (sy + y0 - cy) ** 2
        keep = d < 40**2
        sx, sy = sx[keep], sy[keep]
        if len(sx) == 0:
            sy, sx = np.where(sub)
        cx = float(sx.mean() + x0)
        cy = float(sy.mean() + y0)
        x_min, x_max = int(sx.min() + x0), int(sx.max() + x0)
        y_min, y_max = int(sy.min() + y0), int(sy.max() + y0)
    else:
        x_min, x_max = int(cx - 15), int(cx + 15)
        y_min, y_max = int(cy - 10), int(cy + 10)
        print(f"  {name}: no label near seed")

    max_r_top = max(22, (x_max - x_min) / 2 + 18)
    seeds_px = []
    for y in range(max(0, y_min - 8), min(h, y_max + 14)):
        for x in range(max(0, x_min - 16), min(w, x_max + 16)):
            if mask[y, x]:
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
        if y <= y_max + 3:
            max_r = max_r_top
        else:
            t = (y - (y_max + 3)) / 70.0
            if t > 1.2:
                continue
            max_r = max_r_top * max(0.05, 1.0 - t * 0.95)
        if abs(x - cx) > max_r:
            continue
        pts_x.append(x)
        pts_y.append(y)
        for dy, dx in dirs8:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and mask[ny, nx]:
                visited[ny, nx] = True
                stack.append((ny, nx))
    if len(pts_x) < 40:
        print(f"{name}: FAIL n={len(pts_x)} label%=({cx/w*100:.1f},{cy/h*100:.1f})")
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    tip_y = int(ys.max())
    tip_x = float(np.median(xs[ys >= tip_y - 1]))
    for row in range(tip_y, tip_y - 8, -1):
        row_xs = xs[ys == row]
        if len(row_xs) == 0:
            continue
        tip_x = float(np.median(row_xs))
        tip_y = row
        if len(row_xs) <= 4:
            break
    xp, yp = tip_x / w * 100, tip_y / h * 100
    final[name] = (round(xp, 1), round(yp, 1))
    print(
        f"{name}: tip%=({xp:.2f},{yp:.2f}) n={len(pts_x)} "
        f"label%=({cx/w*100:.1f},{cy/h*100:.1f})"
    )
    draw.ellipse([tip_x - 6, tip_y - 6, tip_x + 6, tip_y + 6], outline=(255, 0, 0), width=3)
    draw.line([tip_x - 14, tip_y, tip_x + 14, tip_y], fill=(255, 255, 0))
    draw.line([tip_x, tip_y - 14, tip_x, tip_y + 14], fill=(255, 255, 0))
    draw.text((tip_x + 8, tip_y - 12), name.split("-")[0][:6], fill=(255, 0, 255))

    half = 70
    cx0, cy0 = int(tip_x), int(tip_y)
    crop_box = (
        max(0, cx0 - half),
        max(0, cy0 - half - 25),
        min(w, cx0 + half),
        min(h, cy0 + half),
    )
    crop = im.crop(crop_box).copy()
    cd = ImageDraw.Draw(crop)
    lx, ly = tip_x - crop_box[0], tip_y - crop_box[1]
    cd.ellipse([lx - 5, ly - 5, lx + 5, ly + 5], outline=(255, 0, 0), width=2)
    out_dir = Path(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v9-restored")
    out_dir.mkdir(exist_ok=True)
    crop.save(out_dir / f"{name}.png")

ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v9-restored-tips.png")
print("\nFINAL:")
for k, v in final.items():
    print(f"  {k}: {v}")
