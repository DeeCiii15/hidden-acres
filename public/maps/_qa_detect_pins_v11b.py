from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape

# Approximate centers of pin BODIES (not tips) from visual layout
approx = {
    "the-inn": (0.665, 0.055),
    "the-chapel": (0.425, 0.345),
    "ceremony-pond": (0.315, 0.525),
    "grooms-quarters": (0.495, 0.595),
    "rusted-silo": (0.635, 0.565),
    "courtyard-pavilion": (0.605, 0.670),
    "the-ballroom": (0.535, 0.755),
    "bridal-suite-salon": (0.710, 0.735),
}

out_dir = Path(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v11")
out_dir.mkdir(exist_ok=True)

results = []
for name, (fx, fy) in approx.items():
    cx, cy = int(fx * w), int(fy * h)
    half = 55
    x0, x1 = max(0, cx - half), min(w, cx + half)
    y0, y1 = max(0, cy - half), min(h, cy + half + 25)
    patch = a[y0:y1, x0:x1]
    pr, pg, pb = patch[:, :, 0], patch[:, :, 1], patch[:, :, 2]

    # Olive / forest pin fill (looser)
    pin = (
        (pg > 50)
        & (pg < 140)
        & (pg >= pr - 5)
        & (pg > pb + 8)
        & (pr < 120)
        & (pb < 90)
        & ((pg - pr) + (pg - pb) > 25)
    )

    # Prefer blobs that contain bright white text
    white = (pr > 185) & (pg > 185) & (pb > 185)

    # Connected components on pin mask
    visited = np.zeros(pin.shape, dtype=bool)
    best = None
    ys_all, xs_all = np.where(pin)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    ph, pw = pin.shape
    for sy, sx in zip(ys_all, xs_all):
        if visited[sy, sx]:
            continue
        stack = [(int(sy), int(sx))]
        visited[sy, sx] = True
        pts = []
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for dy, dx in dirs:
                ny, nx = y + dy, x + dx
                if 0 <= ny < ph and 0 <= nx < pw and (not visited[ny, nx]) and pin[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((ny, nx))
        area = len(pts)
        if area < 80 or area > 5000:
            continue
        ys = np.array([p[0] for p in pts])
        xs = np.array([p[1] for p in pts])
        y_min, y_max = int(ys.min()), int(ys.max())
        x_min, x_max = int(xs.min()), int(xs.max())
        height = y_max - y_min + 1
        width = x_max - x_min + 1
        if height < 12 or width < 10:
            continue
        # white text inside bbox
        wfrac = white[y_min : y_max + 1, x_min : x_max + 1].mean()
        # score: prefer taller teardrop with white text near search center
        cy_c = (y_min + y_max) / 2
        cx_c = (x_min + x_max) / 2
        dist = ((cx_c - (cx - x0)) ** 2 + (cy_c - (cy - y0)) ** 2) ** 0.5
        score = wfrac * 1000 + area * 0.05 - dist * 2
        if height < width * 0.55:
            score -= 50
        cand = dict(
            area=area,
            wfrac=float(wfrac),
            tip_local=(float(xs[ys >= y_max - max(1, int(height * 0.1))].mean()), float(y_max)),
            bbox=(x_min, y_min, x_max, y_max),
            score=score,
            wh=(width, height),
        )
        if best is None or cand["score"] > best["score"]:
            best = cand

    crop = im.crop((x0, y0, x1, y1)).copy()
    draw = ImageDraw.Draw(crop)
    if best:
        tx, ty = best["tip_local"]
        ax, ay = x0 + tx, y0 + ty
        pct = (ax / w * 100, ay / h * 100)
        draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], outline=(255, 0, 0), width=2)
        draw.line([tx - 8, ty, tx + 8, ty], fill=(255, 255, 0))
        draw.line([tx, ty - 8, tx, ty + 8], fill=(255, 255, 0))
        bx0, by0, bx1, by1 = best["bbox"]
        draw.rectangle([bx0, by0, bx1, by1], outline=(0, 255, 255), width=1)
        results.append((name, pct[0], pct[1], best))
        print(
            f"{name}: tip%=({pct[0]:.2f},{pct[1]:.2f}) px=({ax:.1f},{ay:.1f}) "
            f"area={best['area']} white={best['wfrac']:.3f} size={best['wh']}"
        )
    else:
        print(f"{name}: NO PIN FOUND near ({cx},{cy})")
        results.append((name, None, None, None))
    crop.save(out_dir / f"{name}.png")

# overview with crosses
ov = im.copy()
draw = ImageDraw.Draw(ov)
for name, px, py, best in results:
    if px is None:
        continue
    x, y = px / 100 * w, py / 100 * h
    draw.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 0, 0), width=2)
    draw.text((x + 6, y - 10), name.split("-")[0][:6], fill=(255, 255, 0))
ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v11-pin-tips.png")
print("wrote overview + crops")
