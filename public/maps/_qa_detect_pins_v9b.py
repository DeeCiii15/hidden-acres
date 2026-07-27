from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated-v-map-accuracy-v9.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# Stronger pin fill: dark green body
mask = (
    (g > 55)
    & (g < 170)
    & (g > r + 25)
    & (g > b + 20)
    & (r < 115)
    & (b < 115)
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
    if area < 800 or area > 12000:
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    y_max = int(ys.max())
    y_min = int(ys.min())
    x_min = int(xs.min())
    x_max = int(xs.max())
    height = y_max - y_min + 1
    width = x_max - x_min + 1
    if height < 25 or width < 20:
        continue
    # teardrop-ish: height roughly similar to width or taller
    if height < width * 0.7 or height > width * 2.8:
        continue
    # white-ish text inside pin?
    region = a[y_min : y_max + 1, x_min : x_max + 1]
    rr, gg, bb = region[:, :, 0], region[:, :, 1], region[:, :, 2]
    white = ((rr > 180) & (gg > 180) & (bb > 180)).mean()
    if white < 0.02:
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
        f"{i}: area={c['area']:5d} tip%=({c['tx']:5.1f},{c['ty']:5.1f}) "
        f"white={c['white']:.3f} size={c['wh']} bbox={c['bbox']}"
    )

# Save annotated with labels
ov = im.copy()
draw = ImageDraw.Draw(ov)
for i, c in enumerate(comps):
    x, y = c["px"], c["py"]
    draw.ellipse([x - 8, y - 8, x + 8, y + 8], outline=(255, 0, 0), width=3)
    draw.text((x + 10, y - 10), str(i), fill=(255, 255, 0))
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v9-pin-tips2.png")

# Also crop bridal/courtyard southeast quadrant for manual look
crop = im.crop((int(w * 0.55), int(h * 0.62), int(w * 0.98), int(h * 0.92)))
crop.save(r"C:\Dev\hidden-acres\public\maps\_qa-v9-se-crop.png")
print("wrote tip2 + se crop")
