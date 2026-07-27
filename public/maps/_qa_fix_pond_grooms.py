from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

pin_body = (
    (g > 35) & (g < 125) & (r < 110) & (b < 95)
    & (g > r + 5) & (g > b + 5) & ((g - r) + (g - b) > 25)
)
# Gold/cream pin outline (thin rim)
rim = (
    (r > 150) & (g > 145) & (b > 90)
    & (r < 230) & (g < 220)
    & (np.abs(r.astype(float) - g) < 35)
    & (r > b + 15)
)
label = (r > 140) & (g > 155) & (b > 130) & (g >= r - 5) & ((r + g + b) > 450)

# Confirmed good tips from visual QA + fixed pond/grooms
# For most: flood tip was verified. Pond/grooms: use rim-constrained tip.
coords = {
    "the-inn": (67.4, 8.3),
    "the-chapel": (42.3, 36.4),
    "rusted-silo": (63.5, 60.0),
    "courtyard-pavilion": (60.4, 70.3),
    "the-ballroom": (54.0, 78.7),
    "bridal-suite-salon": (70.9, 76.7),
}

def tip_from_label(lxp, lyp, max_drop_px=55, max_r0=22):
    cx, cy = lxp / 100 * w, lyp / 100 * h
    # collect pin_body under label with strong taper; stop if no pin pixels in row
    tip_x, tip_y = cx, cy
    last_good = None
    for y in range(int(cy), min(h, int(cy) + max_drop_px)):
        t = (y - cy) / max_drop_px
        max_r = max_r0 * max(0.05, 1.0 - t * 0.98)
        xs = []
        for x in range(max(0, int(cx - max_r)), min(w, int(cx + max_r) + 1)):
            if pin_body[y, x] and abs(x - cx) <= max_r:
                xs.append(x)
        if not xs:
            # allow 2 empty rows then stop
            if last_good is not None and y - last_good[1] > 2:
                break
            continue
        tip_x = float(np.median(xs))
        tip_y = float(y)
        last_good = (tip_x, tip_y)
        # if very narrow, this is the tip
        if len(xs) <= 2 and y > cy + 20:
            break
    return tip_x / w * 100, tip_y / h * 100

# Fix pond and grooms with tighter search
pond = tip_from_label(32.9, 52.6, max_drop_px=48, max_r0=20)
grooms = tip_from_label(47.1, 62.1, max_drop_px=48, max_r0=18)
print(f"pond refined: ({pond[0]:.2f},{pond[1]:.2f})")
print(f"grooms refined: ({grooms[0]:.2f},{grooms[1]:.2f})")

coords["ceremony-pond"] = (round(pond[0], 1), round(pond[1], 1))
coords["grooms-quarters"] = (round(grooms[0], 1), round(grooms[1], 1))

# Also try rim-based: bottom-most rim pixel under label for these two
def tip_from_rim(lxp, lyp):
    cx, cy = lxp / 100 * w, lyp / 100 * h
    best = None
    for y in range(int(cy), min(h, int(cy) + 55)):
        t = (y - cy) / 55
        max_r = 20 * max(0.05, 1 - t * 0.95)
        xs = [x for x in range(max(0, int(cx - max_r)), min(w, int(cx + max_r) + 1)) if rim[y, x]]
        if xs:
            best = (float(np.median(xs)), float(y))
    return (best[0] / w * 100, best[1] / h * 100) if best else None

print("pond rim", tip_from_rim(32.9, 52.6))
print("grooms rim", tip_from_rim(47.1, 62.1))

out_dir = Path(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v11-final")
ov = im.copy()
draw = ImageDraw.Draw(ov)
for name, (xp, yp) in coords.items():
    tip_x, tip_y = xp / 100 * w, yp / 100 * h
    half = 60
    cx0, cy0 = int(tip_x), int(tip_y)
    box = (max(0, cx0 - half), max(0, cy0 - half - 20), min(w, cx0 + half), min(h, cy0 + half))
    crop = im.crop(box).copy()
    cd = ImageDraw.Draw(crop)
    lx, ly = tip_x - box[0], tip_y - box[1]
    cd.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], outline=(255, 0, 0), width=2)
    cd.line([lx - 10, ly, lx + 10, ly], fill=(255, 255, 0))
    cd.line([lx, ly - 10, lx, ly + 10], fill=(255, 255, 0))
    crop.save(out_dir / f"{name}.png")
    draw.ellipse([tip_x - 5, tip_y - 5, tip_x + 5, tip_y + 5], outline=(255, 0, 0), width=2)
    print(f"{name}: ({xp}, {yp})")

ov.save(r"C:\Dev\hidden-acres\public\maps\_qa-v11-final-tips.png")
print("done", coords)
