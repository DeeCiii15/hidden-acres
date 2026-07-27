from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

mask = (
    (g > 45)
    & (g < 180)
    & (g > r + 20)
    & (g > b + 15)
    & (r < 120)
    & (b < 120)
).astype(np.uint8)

visited = np.zeros((h, w), dtype=bool)
comps = []
dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
ys_all, xs_all = np.where(mask > 0)
for y0, x0 in zip(ys_all, xs_all):
    if visited[y0, x0]:
        continue
    stack = [(int(y0), int(x0))]
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
    if area < 200 or area > 8000:
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    y_max = int(ys.max())
    y_min = int(ys.min())
    x_min = int(xs.min())
    x_max = int(xs.max())
    height = y_max - y_min + 1
    width = x_max - x_min + 1
    if height < 15 or width < 12:
        continue
    if height < width * 0.6 or height > width * 3.2:
        continue
    region = a[y_min : y_max + 1, x_min : x_max + 1]
    rr, gg, bb = region[:, :, 0], region[:, :, 1], region[:, :, 2]
    white = ((rr > 175) & (gg > 175) & (bb > 175)).mean()
    if white < 0.015:
        continue
    bottom = ys >= (y_max - max(2, int(height * 0.12)))
    tip_x = float(xs[bottom].mean())
    tip_y = float(y_max)
    comps.append(
        {
            "area": area,
            "tx": tip_x / w * 100,
            "ty": tip_y / h * 100,
            "px": tip_x,
            "py": tip_y,
            "white": float(white),
            "bbox": (x_min, y_min, x_max, y_max),
            "wh": (width, height),
        }
    )

comps.sort(key=lambda c: (c["ty"], c["tx"]))
print(f"{w}x{h} pin-like={len(comps)}")
for i, c in enumerate(comps):
    print(
        f"{i}: area={c['area']:5d} tip%=({c['tx']:5.2f},{c['ty']:5.2f}) "
        f"white={c['white']:.3f} size={c['wh']} bbox={c['bbox']}"
    )

ov = im.copy()
draw = ImageDraw.Draw(ov)
for i, c in enumerate(comps):
    x, y = c["px"], c["py"]
    draw.ellipse([x - 6, y - 6, x + 6, y + 6], outline=(255, 0, 0), width=2)
    draw.line([x - 10, y, x + 10, y], fill=(255, 255, 0), width=1)
    draw.line([x, y - 10, x, y + 10], fill=(255, 255, 0), width=1)
    draw.text((x + 8, y - 12), str(i), fill=(255, 255, 0))
out = Path(r"C:\Dev\hidden-acres\public\maps\_qa-v11-pin-tips.png")
ov.save(out)
print("wrote", out)
