from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# Mint/cream pin label text
label = (
    (r > 145)
    & (g > 165)
    & (b > 140)
    & (g >= r)
    & (g > b)
    & ((r + g + b) > 470)
    & ((r + g + b) < 700)
)

visited = np.zeros((h, w), dtype=bool)
dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
ys_all, xs_all = np.where(label)
clusters = []
for y0, x0 in zip(ys_all, xs_all):
    if visited[y0, x0]:
        continue
    stack = [(int(y0), int(x0))]
    visited[y0, x0] = True
    pts_x, pts_y = [], []
    while stack:
        y, x = stack.pop()
        pts_x.append(x)
        pts_y.append(y)
        for dy, dx in dirs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and label[ny, nx]:
                visited[ny, nx] = True
                stack.append((ny, nx))
    area = len(pts_x)
    if area < 12 or area > 500:
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    bw, bh = x_max - x_min + 1, y_max - y_min + 1
    if bw < 10 or bh < 5 or bw > 85 or bh > 55:
        continue
    cx = float(xs.mean())
    cy = float(ys.mean())
    clusters.append(
        dict(
            cx=cx,
            cy=cy,
            area=area,
            bbox=(x_min, y_min, x_max, y_max),
            wh=(bw, bh),
        )
    )

print(f"label clusters raw={len(clusters)}")

# Olive pin body for tip finding
olive = (
    (g > 40)
    & (g < 130)
    & (g >= r - 5)
    & (g > b + 8)
    & (r < 115)
    & (b < 90)
    & ((g - r) + (g - b) > 22)
)

results = []
for c in clusters:
    cx, cy = c["cx"], c["cy"]
    x_min, y_min, x_max, y_max = c["bbox"]
    # Search downward from label for teardrop tip: olive pixels tapering
    sx0, sx1 = max(0, int(cx) - 18), min(w, int(cx) + 19)
    sy0, sy1 = max(0, y_min - 5), min(h, y_max + 95)
    sub = olive[sy0:sy1, sx0:sx1]
    if sub.sum() < 40:
        continue
    # Also require substantial olive around the label (pin body)
    around = olive[max(0, y_min - 8) : min(h, y_max + 8), max(0, x_min - 8) : min(w, x_max + 8)]
    if around.mean() < 0.12:
        continue
    sy, sx = np.where(sub)
    y_abs = sy + sy0
    x_abs = sx + sx0
    # Tip = bottom-most olive near center column
    y_tip = int(y_abs.max())
    near_bottom = y_abs >= (y_tip - 3)
    # weight by proximity to cx
    weights = 1.0 / (1.0 + np.abs(x_abs[near_bottom] - cx) * 0.35)
    tip_x = float(np.average(x_abs[near_bottom], weights=weights))
    tip_y = float(y_tip)
    # Pin height sanity: tip should be meaningfully below label
    if tip_y - cy < 12:
        continue
    if tip_y - cy > 95:
        continue
    results.append(
        dict(
            tip=(tip_x, tip_y),
            tip_pct=(tip_x / w * 100, tip_y / h * 100),
            label_c=(cx, cy),
            area=c["area"],
            bbox=c["bbox"],
            wh=c["wh"],
            olive_below=int(sub.sum()),
        )
    )

# Dedup
results.sort(key=lambda c: c["tip_pct"][1])
kept = []
for c in results:
    dup = False
    for i, k in enumerate(kept):
        if abs(c["tip"][0] - k["tip"][0]) < 20 and abs(c["tip"][1] - k["tip"][1]) < 22:
            dup = True
            if c["area"] > k["area"]:
                kept[i] = c
            break
    if not dup:
        kept.append(c)

print(f"pins kept={len(kept)}")
for i, c in enumerate(kept):
    print(
        f"{i}: tip%=({c['tip_pct'][0]:5.2f},{c['tip_pct'][1]:5.2f}) "
        f"label=({c['label_c'][0]:.0f},{c['label_c'][1]:.0f}) "
        f"area={c['area']} wh={c['wh']} olive={c['olive_below']}"
    )

ov = im.copy()
draw = ImageDraw.Draw(ov)
for i, c in enumerate(kept):
    x, y = c["tip"]
    draw.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 0), width=2)
    draw.line([x - 12, y, x + 12, y], fill=(255, 255, 0), width=1)
    draw.line([x, y - 12, x, y + 12], fill=(255, 255, 0), width=1)
    draw.rectangle(c["bbox"], outline=(0, 255, 255))
    draw.text((x + 7, y - 10), str(i), fill=(255, 0, 255))
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v11-label-tips.png")
print("wrote _qa-v11-label-tips.png")

# Also write named assignment guess by position
names_by_order = []
guesses = [
    ("the-inn", 0.66, 0.08),
    ("the-chapel", 0.42, 0.36),
    ("ceremony-pond", 0.32, 0.55),
    ("rusted-silo", 0.63, 0.59),
    ("grooms-quarters", 0.49, 0.62),
    ("courtyard-pavilion", 0.60, 0.69),
    ("bridal-suite-salon", 0.71, 0.75),
    ("the-ballroom", 0.53, 0.78),
]
print("\nNearest assignment:")
used = set()
for name, fx, fy in guesses:
    best_i, best_d = None, 1e9
    for i, c in enumerate(kept):
        if i in used:
            continue
        d = (c["tip_pct"][0] - fx * 100) ** 2 + (c["tip_pct"][1] - fy * 100) ** 2
        if d < best_d:
            best_d, best_i = d, i
    if best_i is None:
        print(name, "NONE")
        continue
    used.add(best_i)
    c = kept[best_i]
    print(
        f"  {name}: tip%=({c['tip_pct'][0]:.2f},{c['tip_pct'][1]:.2f}) "
        f"from cluster {best_i} dist2={best_d:.1f}"
    )
