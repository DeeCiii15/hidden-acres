from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# Mint label
label = (r > 140) & (g > 155) & (b > 130) & (g >= r - 5) & ((r + g + b) > 450)
lab = label.copy()
for dy in (-1, 0, 1):
    for dx in (-1, 0, 1):
        if dy == 0 and dx == 0:
            continue
        shifted = np.zeros_like(label)
        ys = slice(max(0, dy), h + min(0, dy))
        xs = slice(max(0, dx), w + min(0, dx))
        ys2 = slice(max(0, -dy), h + min(0, -dy))
        xs2 = slice(max(0, -dx), w + min(0, -dx))
        shifted[ys, xs] = label[ys2, xs2]
        lab |= shifted

# Pin body: darker olive/forest green (exclude bright grass)
pin_body = (
    (g > 35)
    & (g < 125)
    & (r < 110)
    & (b < 95)
    & (g > r + 5)
    & (g > b + 5)
    & ((g - r) + (g - b) > 25)
)

# Find label components
visited = np.zeros((h, w), dtype=bool)
dirs8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
comps = []
ys_all, xs_all = np.where(lab)
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
        for dy, dx in dirs8:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and lab[ny, nx]:
                visited[ny, nx] = True
                stack.append((ny, nx))
    area = len(pts_x)
    if area < 25 or area > 2500:
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    bw, bh = x_max - x_min + 1, y_max - y_min + 1
    if bw < 10 or bh < 5 or bw > 90 or bh > 60:
        continue
    if int(label[y_min : y_max + 1, x_min : x_max + 1].sum()) < 8:
        continue
    comps.append(dict(cx=float(xs.mean()), cy=float(ys.mean()), bbox=(x_min, y_min, x_max, y_max), area=area, wh=(bw, bh)))

# Merge nearby label fragments into one pin label (Inn has 2 lines)
merged = []
comps.sort(key=lambda c: (c["cy"], c["cx"]))
used = [False] * len(comps)
for i, c in enumerate(comps):
    if used[i]:
        continue
    group = [c]
    used[i] = True
    changed = True
    while changed:
        changed = False
        for j, d in enumerate(comps):
            if used[j]:
                continue
            if any(abs(d["cx"] - g["cx"]) < 28 and abs(d["cy"] - g["cy"]) < 22 for g in group):
                group.append(d)
                used[j] = True
                changed = True
    xs = [g["cx"] for g in group]
    ys = [g["cy"] for g in group]
    bboxes = [g["bbox"] for g in group]
    x_min = min(b[0] for b in bboxes)
    y_min = min(b[1] for b in bboxes)
    x_max = max(b[2] for b in bboxes)
    y_max = max(b[3] for b in bboxes)
    merged.append(
        dict(
            cx=float(np.mean(xs)),
            cy=float(np.mean(ys)),
            bbox=(x_min, y_min, x_max, y_max),
            area=sum(g["area"] for g in group),
        )
    )

print(f"merged labels: {len(merged)}")
for i, c in enumerate(merged):
    print(f"  {i}: c%=({c['cx']/w*100:.1f},{c['cy']/h*100:.1f}) bbox={c['bbox']} area={c['area']}")

# From each label, flood pin_body with tapering width constraint
results = []
for c in merged:
    cx, cy = c["cx"], c["cy"]
    x_min, y_min, x_max, y_max = c["bbox"]
    # seed: pin body pixels adjacent to label bbox
    seeds = []
    for y in range(max(0, y_min - 6), min(h, y_max + 8)):
        for x in range(max(0, x_min - 10), min(w, x_max + 10)):
            if pin_body[y, x]:
                seeds.append((y, x))
    if len(seeds) < 15:
        continue
    # flood with max radius from center that shrinks below label
    max_r_top = max(18, (x_max - x_min) / 2 + 14)
    visited2 = np.zeros((h, w), dtype=bool)
    stack = []
    for y, x in seeds:
        if not visited2[y, x]:
            visited2[y, x] = True
            stack.append((y, x))
    pts_x, pts_y = [], []
    while stack:
        y, x = stack.pop()
        # envelope
        if y <= y_max + 2:
            max_r = max_r_top
        else:
            # taper linearly to tip over ~55px
            t = (y - (y_max + 2)) / 55.0
            if t > 1.2:
                continue
            max_r = max_r_top * max(0.08, 1.0 - t * 0.95)
        if abs(x - cx) > max_r:
            continue
        pts_x.append(x)
        pts_y.append(y)
        for dy, dx in dirs8:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (not visited2[ny, nx]) and pin_body[ny, nx]:
                visited2[ny, nx] = True
                stack.append((ny, nx))
    if len(pts_x) < 80:
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    tip_y = int(ys.max())
    bottom = ys >= tip_y - 1
    tip_x = float(xs[bottom].mean())
    # refine: among bottom 3 rows, take median x of narrowest row
    for row in range(tip_y, max(tip_y - 4, int(ys.min())), -1):
        row_xs = xs[ys == row]
        if len(row_xs) > 0:
            tip_x = float(np.median(row_xs))
            tip_y = row
            if len(row_xs) <= 4:
                break
    tip_pct = (tip_x / w * 100, tip_y / h * 100)
    results.append(
        dict(
            tip=(tip_x, tip_y),
            tip_pct=tip_pct,
            label_c=(cx, cy),
            label_pct=(cx / w * 100, cy / h * 100),
            n=len(pts_x),
            bbox=c["bbox"],
        )
    )

results.sort(key=lambda c: c["tip_pct"][1])
print(f"\npins: {len(results)}")
for i, c in enumerate(results):
    print(
        f"{i}: tip%=({c['tip_pct'][0]:5.2f},{c['tip_pct'][1]:5.2f}) "
        f"label%=({c['label_pct'][0]:5.1f},{c['label_pct'][1]:5.1f}) n={c['n']}"
    )

ov = im.copy()
draw = ImageDraw.Draw(ov)
for i, c in enumerate(results):
    x, y = c["tip"]
    draw.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 0), width=2)
    draw.line([x - 12, y, x + 12, y], fill=(255, 255, 0))
    draw.line([x, y - 12, x, y + 12], fill=(255, 255, 0))
    draw.rectangle(c["bbox"], outline=(0, 255, 255))
    draw.text((x + 6, y - 10), str(i), fill=(255, 0, 255))
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v11-taper-tips.png")

# Also seed search windows for missing silo/ballroom by approx
extra_seeds = {
    "rusted-silo": (0.635, 0.555),
    "the-ballroom": (0.535, 0.745),
    "courtyard-pavilion": (0.605, 0.675),
}
print("\nWindow search for missing:")
for name, (fx, fy) in extra_seeds.items():
    cx, cy = int(fx * w), int(fy * h)
    # find mint in window
    x0, x1 = max(0, cx - 45), min(w, cx + 45)
    y0, y1 = max(0, cy - 40), min(h, cy + 35)
    sub = label[y0:y1, x0:x1]
    print(f"  {name} mint_px={int(sub.sum())} window=({x0},{y0})-({x1},{y1})")
    if sub.any():
        sy, sx = np.where(sub)
        print(f"    mint centroid % ({(sx.mean()+x0)/w*100:.1f},{(sy.mean()+y0)/h*100:.1f})")
