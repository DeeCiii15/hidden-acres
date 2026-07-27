from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path
from scipy import ndimage

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# Looser mint text
label = (
    (r > 140)
    & (g > 155)
    & (b > 130)
    & (g >= r - 5)
    & ((r + g + b) > 450)
)
print("label px", int(label.sum()))

# Dilate slightly to connect letter strokes
struct = np.ones((3, 3))
lab2 = ndimage.binary_dilation(label, structure=struct, iterations=1)
labeled, n = ndimage.label(lab2)
print("components", n)

comps = []
for i in range(1, n + 1):
    ys, xs = np.where(labeled == i)
    area = len(xs)
    if area < 20 or area > 2000:
        continue
    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    bw, bh = x_max - x_min + 1, y_max - y_min + 1
    if bw < 12 or bh < 6 or bw > 100 or bh > 70:
        continue
    # Must overlap original label pixels substantially
    orig = label[y_min : y_max + 1, x_min : x_max + 1].sum()
    if orig < 10:
        continue
    comps.append(
        dict(
            i=i,
            area=area,
            orig=int(orig),
            cx=float(xs.mean()),
            cy=float(ys.mean()),
            bbox=(x_min, y_min, x_max, y_max),
            wh=(bw, bh),
        )
    )

print("filtered comps", len(comps))
comps.sort(key=lambda c: (c["cy"], c["cx"]))
for c in comps:
    print(
        f"  area={c['area']:4d} orig={c['orig']:3d} c=({c['cx']:.0f},{c['cy']:.0f}) "
        f"%=({c['cx']/w*100:.1f},{c['cy']/h*100:.1f}) wh={c['wh']}"
    )

# Olive for tip
olive = (
    (g > 40)
    & (g < 135)
    & (g >= r - 5)
    & (g > b + 5)
    & (r < 120)
    & (b < 95)
    & ((g - r) + (g - b) > 18)
)

results = []
for c in comps:
    cx, cy = c["cx"], c["cy"]
    # require olive around label (pin body)
    x_min, y_min, x_max, y_max = c["bbox"]
    around = olive[
        max(0, y_min - 10) : min(h, y_max + 25),
        max(0, x_min - 12) : min(w, x_max + 12),
    ]
    if around.mean() < 0.10:
        continue
    sx0, sx1 = max(0, int(cx) - 16), min(w, int(cx) + 17)
    sy0, sy1 = y_min, min(h, y_max + 90)
    sub = olive[sy0:sy1, sx0:sx1]
    if sub.sum() < 30:
        continue
    sy, sx = np.where(sub)
    y_abs = sy + sy0
    x_abs = sx + sx0
    y_tip = int(y_abs.max())
    near = y_abs >= y_tip - 2
    weights = 1.0 / (1.0 + np.abs(x_abs[near] - cx) * 0.4)
    tip_x = float(np.average(x_abs[near], weights=weights))
    tip_y = float(y_tip)
    if not (15 < tip_y - cy < 100):
        continue
    results.append(
        dict(
            tip=(tip_x, tip_y),
            tip_pct=(tip_x / w * 100, tip_y / h * 100),
            label_c=(cx, cy),
            area=c["area"],
            bbox=c["bbox"],
        )
    )

# dedup
results.sort(key=lambda c: c["tip_pct"][1])
kept = []
for c in results:
    dup = False
    for i, k in enumerate(kept):
        if abs(c["tip"][0] - k["tip"][0]) < 22 and abs(c["tip"][1] - k["tip"][1]) < 24:
            dup = True
            if c["area"] > k["area"]:
                kept[i] = c
            break
    if not dup:
        kept.append(c)

print("\npins", len(kept))
for i, c in enumerate(kept):
    print(f"{i}: tip%=({c['tip_pct'][0]:5.2f},{c['tip_pct'][1]:5.2f}) label=({c['label_c'][0]:.0f},{c['label_c'][1]:.0f})")

ov = im.copy()
draw = ImageDraw.Draw(ov)
for i, c in enumerate(kept):
    x, y = c["tip"]
    draw.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 0), width=2)
    draw.line([x - 12, y, x + 12, y], fill=(255, 255, 0))
    draw.line([x, y - 12, x, y + 12], fill=(255, 255, 0))
    draw.rectangle(c["bbox"], outline=(0, 255, 255))
    draw.text((x + 6, y - 10), str(i), fill=(255, 0, 255))
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v11-label-tips.png")

guesses = [
    ("the-inn", 66.5, 8.0),
    ("the-chapel", 42.0, 37.0),
    ("ceremony-pond", 31.5, 56.0),
    ("rusted-silo", 63.5, 59.0),
    ("grooms-quarters", 49.5, 62.0),
    ("courtyard-pavilion", 60.5, 69.5),
    ("bridal-suite-salon", 71.0, 75.5),
    ("the-ballroom", 53.5, 78.0),
]
print("\nAssignment:")
used = set()
assigned = {}
for name, fx, fy in guesses:
    best_i, best_d = None, 1e9
    for i, c in enumerate(kept):
        if i in used:
            continue
        d = (c["tip_pct"][0] - fx) ** 2 + (c["tip_pct"][1] - fy) ** 2
        if d < best_d:
            best_d, best_i = d, i
    if best_i is None or best_d > 120:
        print(f"  {name}: FAIL best_d={best_d}")
        continue
    used.add(best_i)
    c = kept[best_i]
    assigned[name] = c["tip_pct"]
    print(f"  {name}: ({c['tip_pct'][0]:.2f}, {c['tip_pct'][1]:.2f}) d2={best_d:.1f}")

print("\nTS snippet:")
for name, (x, y) in assigned.items():
    print(f'  {{ spaceSlug: "{name}", x: {x:.1f}, y: {y:.1f}, slot: "..." }},')
