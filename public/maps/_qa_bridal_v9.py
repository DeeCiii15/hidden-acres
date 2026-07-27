from PIL import Image, ImageDraw
import numpy as np
from collections import deque

im = Image.open(
    r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated-v-map-accuracy-v9.png"
).convert("RGB")
a = np.asarray(im).astype(float)
h, w, _ = a.shape
y0, y1 = int(h * 0.68), int(h * 0.82)
x0, x1 = int(w * 0.78), int(w * 0.98)
reg = a[y0:y1, x0:x1]
r, g, b = reg[:, :, 0], reg[:, :, 1], reg[:, :, 2]
pin = (g > 45) & (g < 140) & (r < 100) & (b < 100) & (g > r + 30) & (g > b + 25)
print("pin frac", float(pin.mean()), "sum", int(pin.sum()))

visited = np.zeros(pin.shape, dtype=bool)
comps = []
ys, xs = np.where(pin)
for y, x in zip(ys, xs):
    if visited[y, x]:
        continue
    q = deque([(int(y), int(x))])
    visited[y, x] = True
    px = []
    py = []
    while q:
        cy, cx = q.popleft()
        px.append(cx)
        py.append(cy)
        for dy, dx in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
        ]:
            ny, nx = cy + dy, cx + dx
            if (
                0 <= ny < pin.shape[0]
                and 0 <= nx < pin.shape[1]
                and (not visited[ny, nx])
                and pin[ny, nx]
            ):
                visited[ny, nx] = True
                q.append((ny, nx))
    area = len(px)
    if area < 200:
        continue
    xsA = np.array(px)
    ysA = np.array(py)
    tipx = x0 + xsA[ysA >= ysA.max() - 3].mean()
    tipy = y0 + ysA.max()
    comps.append(
        (
            area,
            tipx / w * 100,
            tipy / h * 100,
            tipx,
            tipy,
            (x0 + xsA.min(), y0 + ysA.min(), x0 + xsA.max(), y0 + ysA.max()),
        )
    )
comps.sort(key=lambda t: -t[0])
print("bridal-region comps")
for c in comps[:15]:
    print(f"  area={c[0]} tip%=({c[1]:.1f},{c[2]:.1f}) bbox={c[5]}")

crop = im.crop((int(w * 0.55), int(h * 0.62), int(w * 0.98), int(h * 0.92)))
draw = ImageDraw.Draw(crop)
ox, oy = int(w * 0.55), int(h * 0.62)
for c in comps[:8]:
    lx, ly = c[3] - ox, c[4] - oy
    draw.ellipse([lx - 8, ly - 8, lx + 8, ly + 8], outline=(255, 0, 0), width=3)
    draw.text((lx + 10, ly - 8), f"{c[1]:.0f},{c[2]:.0f}", fill=(255, 255, 0))
cx, cy = 70.8 / 100 * w - ox, 71.4 / 100 * h - oy
draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=(0, 255, 255), width=3)
# mark (54.3, 68.5) too
mx, my = 54.3 / 100 * w - ox, 68.5 / 100 * h - oy
draw.ellipse([mx - 8, my - 8, mx + 8, my + 8], outline=(255, 0, 255), width=3)
crop.save(r"C:\Dev\hidden-acres\public\maps\_qa-v9-bridal-tips.png")
print("saved bridal tips")
