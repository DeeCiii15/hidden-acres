from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated-v-map-accuracy-v9.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
mask = (
    (g > 60)
    & (g > r * 1.3)
    & (g > b * 1.2)
    & (r < 120)
    & (b < 120)
    & ((g - r) > 28)
).astype(np.uint8)

visited = np.zeros_like(mask, dtype=bool)
comps = []
dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
ys_all, xs_all = np.where(mask > 0)
for y0, x0 in zip(ys_all, xs_all):
    if visited[y0, x0]:
        continue
    stack = [(y0, x0)]
    visited[y0, x0] = True
    pts_x = []
    pts_y = []
    while stack:
        y, x = stack.pop()
        pts_x.append(x)
        pts_y.append(y)
        for dy, dx in dirs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and mask[ny, nx]:
                visited[ny, nx] = True
                stack.append((ny, nx))
    area = len(pts_x)
    if area < 120 or area > 20000:
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    y_max = int(ys.max())
    y_min = int(ys.min())
    height = y_max - y_min + 1
    if height < 12:
        continue
    width = int(xs.max() - xs.min() + 1)
    if height < width * 0.6:
        continue
    bottom = ys >= (y_max - max(2, int(height * 0.1)))
    tip_x = float(xs[bottom].mean())
    tip_y = float(y_max)
    comps.append(
        {
            "area": area,
            "tx": tip_x / w * 100,
            "ty": tip_y / h * 100,
            "px": tip_x,
            "py": tip_y,
            "bbox": (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())),
        }
    )

comps.sort(key=lambda c: c["ty"])
print(f"{w}x{h} pins={len(comps)}")
for i, c in enumerate(comps):
    print(
        f"{i}: area={c['area']:5d} tip%=({c['tx']:5.1f},{c['ty']:5.1f}) bbox={c['bbox']}"
    )

ov = im.copy()
draw = ImageDraw.Draw(ov)
for c in comps:
    x, y = c["px"], c["py"]
    draw.ellipse([x - 6, y - 6, x + 6, y + 6], outline=(255, 0, 0), width=3)
    draw.line([x - 10, y, x + 10, y], fill=(255, 255, 0), width=2)
    draw.line([x, y - 10, x, y + 10], fill=(255, 255, 0), width=2)
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v9-pin-tips.png")
print("wrote pin tip overlay")
