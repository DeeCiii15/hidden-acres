from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# Bright white-ish label text on pins
white = (r > 200) & (g > 200) & (b > 200) & ((r + g + b) > 620)

# Find white clusters that could be pin labels
visited = np.zeros((h, w), dtype=bool)
dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
ys_all, xs_all = np.where(white)
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
            if 0 <= ny < h and 0 <= nx < w and (not visited[ny, nx]) and white[ny, nx]:
                visited[ny, nx] = True
                stack.append((ny, nx))
    area = len(pts_x)
    if area < 8 or area > 400:
        continue
    xs = np.array(pts_x)
    ys = np.array(pts_y)
    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    bw, bh = x_max - x_min + 1, y_max - y_min + 1
    if bw < 8 or bh < 4 or bw > 70 or bh > 45:
        continue
    # Look for olive pin color below/around this white text
    pad = 8
    xa0, xa1 = max(0, x_min - pad), min(w, x_max + pad)
    ya0, ya1 = max(0, y_min - pad), min(h, y_max + int(bh * 2.5) + 20)
    region = a[ya0:ya1, xa0:xa1]
    rr, gg, bb = region[:, :, 0], region[:, :, 1], region[:, :, 2]
    olive = (
        (gg > 45)
        & (gg < 145)
        & (gg >= rr - 8)
        & (gg > bb + 5)
        & (rr < 125)
        & (bb < 95)
        & ((gg - rr) + (gg - bb) > 20)
    )
    olive_frac = olive.mean()
    if olive_frac < 0.08:
        continue
    # tip = bottom-most olive pixel in a column near white center
    cx = int(xs.mean())
    # search columns around center
    tip_candidates = []
    for dx in range(-8, 9):
        col = cx + dx
        if col < 0 or col >= w:
            continue
        # from white bottom downward ~ 80px
        y_start = y_max
        y_end = min(h, y_max + 80)
        col_slice = olive[:, col - xa0] if 0 <= col - xa0 < olive.shape[1] else None
        # use full image olive for tip
    # Build local olive mask relative to full image
    full_olive = (
        (g > 45)
        & (g < 145)
        & (g >= r - 8)
        & (g > b + 5)
        & (r < 125)
        & (b < 95)
        & ((g - r) + (g - b) > 20)
    )
    tip_y = None
    tip_x = cx
    search_x0, search_x1 = max(0, cx - 12), min(w, cx + 13)
    search_y0, search_y1 = y_min, min(h, y_max + 90)
    sub = full_olive[search_y0:search_y1, search_x0:search_x1]
    if not sub.any():
        continue
    # bottom-most olive in this window, near horizontal center of white
    sy, sx = np.where(sub)
    # prefer pixels near cx
    weights = 1.0 / (1.0 + np.abs((sx + search_x0) - cx))
    # take bottom 15% by y
    y_abs = sy + search_y0
    y_cut = np.percentile(y_abs, 88)
    bottom = y_abs >= y_cut
    if not bottom.any():
        continue
    tip_x = float(((sx[bottom] + search_x0) * weights[bottom]).sum() / weights[bottom].sum())
    tip_y = float(y_abs[bottom].max())
    clusters.append(
        dict(
            white_c=(float(xs.mean()), float(ys.mean())),
            tip=(tip_x, tip_y),
            tip_pct=(tip_x / w * 100, tip_y / h * 100),
            area=area,
            olive=float(olive_frac),
            bbox=(x_min, y_min, x_max, y_max),
        )
    )

# Deduplicate nearby clusters
clusters.sort(key=lambda c: c["tip_pct"][1])
kept = []
for c in clusters:
    if any(abs(c["tip"][0] - k["tip"][0]) < 18 and abs(c["tip"][1] - k["tip"][1]) < 18 for k in kept):
        # keep higher olive
        for i, k in enumerate(kept):
            if abs(c["tip"][0] - k["tip"][0]) < 18 and abs(c["tip"][1] - k["tip"][1]) < 18:
                if c["olive"] > k["olive"]:
                    kept[i] = c
                break
        continue
    kept.append(c)

print(f"white-anchored pins: {len(kept)}")
for i, c in enumerate(kept):
    print(
        f"{i}: tip%=({c['tip_pct'][0]:5.2f},{c['tip_pct'][1]:5.2f}) "
        f"white_c={c['white_c']} area={c['area']} olive={c['olive']:.3f}"
    )

ov = im.copy()
draw = ImageDraw.Draw(ov)
for i, c in enumerate(kept):
    x, y = c["tip"]
    draw.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 0), width=2)
    draw.line([x - 10, y, x + 10, y], fill=(255, 255, 0))
    draw.line([x, y - 10, x, y + 10], fill=(255, 255, 0))
    wx, wy = c["white_c"]
    draw.rectangle([c["bbox"][0], c["bbox"][1], c["bbox"][2], c["bbox"][3]], outline=(0, 255, 255))
    draw.text((x + 6, y - 8), str(i), fill=(255, 0, 255))
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v11-white-tips.png")
print("wrote _qa-v11-white-tips.png")
