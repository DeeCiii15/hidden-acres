from PIL import Image, ImageDraw
import numpy as np
from collections import deque

im = Image.open(
    r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated-v-map-accuracy-v9.png"
).convert("RGB")
a = np.asarray(im).astype(float)
h, w, _ = a.shape

# Region covering courtyard+bridal from court-bridal crop
y0, y1 = int(h * 0.65), int(h * 0.85)
x0, x1 = int(w * 0.60), int(w * 0.97)
reg = a[y0:y1, x0:x1]
r, g, b = reg[:, :, 0], reg[:, :, 1], reg[:, :, 2]

# Pin body: muted dark green (not lime canopy)
pin = (
    (g > 50)
    & (g < 130)
    & (r > 20)
    & (r < 95)
    & (b < 90)
    & (g > r + 20)
    & (g > b + 15)
    & ((g - r) > 25)
)

visited = np.zeros(pin.shape, dtype=bool)
comps = []
ys, xs = np.where(pin)
for y, x in zip(ys, xs):
    if visited[y, x]:
        continue
    q = deque([(int(y), int(x))])
    visited[y, x] = True
    px, py = [], []
    while q:
        cy, cx = q.popleft()
        px.append(cx)
        py.append(cy)
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = cy + dy, cx + dx
            if (
                0 <= ny < pin.shape[0]
                and 0 <= nx < pin.shape[1]
                and not visited[ny, nx]
                and pin[ny, nx]
            ):
                visited[ny, nx] = True
                q.append((ny, nx))
    area = len(px)
    if area < 400:
        continue
    xsA = np.array(px)
    ysA = np.array(py)
    height = ysA.max() - ysA.min() + 1
    width = xsA.max() - xsA.min() + 1
    if height < 20 or width < 15:
        continue
    tipx = x0 + float(xsA[ysA >= ysA.max() - max(2, height // 10)].mean())
    tipy = y0 + float(ysA.max())
    # white text ratio
    sub = reg[ysA.min() : ysA.max() + 1, xsA.min() : xsA.max() + 1]
    white = float(
        ((sub[:, :, 0] > 170) & (sub[:, :, 1] > 170) & (sub[:, :, 2] > 170)).mean()
    )
    comps.append(
        {
            "area": area,
            "tx": tipx / w * 100,
            "ty": tipy / h * 100,
            "px": tipx,
            "py": tipy,
            "white": white,
            "wh": (int(width), int(height)),
            "bbox": (
                int(x0 + xsA.min()),
                int(y0 + ysA.min()),
                int(x0 + xsA.max()),
                int(y0 + ysA.max()),
            ),
        }
    )

comps.sort(key=lambda c: c["tx"])
print(f"comps in court+bridal region: {len(comps)}")
for c in comps:
    print(
        f"  area={c['area']:5d} tip%=({c['tx']:5.1f},{c['ty']:5.1f}) "
        f"white={c['white']:.3f} size={c['wh']} bbox={c['bbox']}"
    )

ov = im.crop((x0, y0, x1, y1)).copy()
draw = ImageDraw.Draw(ov)
for c in comps:
    lx, ly = c["px"] - x0, c["py"] - y0
    draw.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], outline=(255, 0, 0), width=3)
    draw.text((lx + 8, ly - 10), f"{c['tx']:.0f},{c['ty']:.0f}", fill=(255, 255, 0))
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v9-court-bridal-marked.png")
print("saved marked")
