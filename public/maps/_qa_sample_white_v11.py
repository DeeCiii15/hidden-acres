from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)
h, w, _ = a.shape
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# Sample brightness near known pin labels
samples = {
    "inn": (470, 55),
    "chapel": (300, 340),
    "pond": (222, 530),
    "silo": (448, 565),
    "ball": (378, 760),
    "bridal": (500, 725),
    "court": (425, 675),
    "grooms": (348, 600),
}
for name, (x, y) in samples.items():
    patch = a[y-8:y+8, x-20:x+20]
    # brightest pixels
    lum = patch.mean(axis=2)
    flat = patch.reshape(-1, 3)
    idxs = np.argsort(lum.ravel())[-5:]
    print(name, "brightest", flat[idxs].astype(int).tolist(), "mean", flat.mean(0).astype(int).tolist())

# Lower white threshold
for thr in [160, 170, 180, 190, 200]:
    m = (r > thr) & (g > thr) & (b > thr)
    print(f"white>{thr}: {int(m.sum())}")

# Gold/cream pin border: high L, similar RGB, not pure white
border = (r > 170) & (g > 155) & (b > 100) & (r < 245) & (np.abs(r - g) < 40) & (r > b + 20)
print("border-ish", int(border.sum()))
