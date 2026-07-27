from PIL import Image
import numpy as np
from pathlib import Path

src = Path(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im)
h, w, _ = a.shape
print("size", w, h)

# Sample around expected pin areas (approx from visual)
seeds = {
    "inn": (0.66, 0.08),
    "chapel": (0.42, 0.36),
    "pond": (0.32, 0.54),
    "grooms": (0.49, 0.61),
    "silo": (0.63, 0.58),
    "court": (0.60, 0.68),
    "ballroom": (0.53, 0.77),
    "bridal": (0.70, 0.74),
}

for name, (fx, fy) in seeds.items():
    cx, cy = int(fx * w), int(fy * h)
    # search neighborhood for darkest green-ish pixels
    y0, y1 = max(0, cy - 40), min(h, cy + 40)
    x0, x1 = max(0, cx - 40), min(w, cx + 40)
    patch = a[y0:y1, x0:x1].astype(np.float32)
    r, g, b = patch[:,:,0], patch[:,:,1], patch[:,:,2]
    score = g - r - b + (g > r) * 20 + (g > b) * 20
    # find green-dominant
    green = (g > r + 10) & (g > b + 5) & (g > 40) & (r < 140)
    print(f"\n{name} around ({cx},{cy}) green_px={int(green.sum())}")
    if green.any():
        ys, xs = np.where(green)
        # pick a few samples
        idxs = np.linspace(0, len(xs)-1, min(5, len(xs))).astype(int)
        for i in idxs:
            yy, xx = ys[i], xs[i]
            print("  rgb", patch[yy, xx].astype(int), "abs", (x0+xx, y0+yy))
        # also find bottom-most green in this patch
        bot_i = ys.argmax()
        print("  bottom green rgb", patch[ys[bot_i], xs[bot_i]].astype(int), "abs", (x0+xs[bot_i], y0+ys[bot_i]), f"% ({(x0+xs[bot_i])/w*100:.1f},{(y0+ys[bot_i])/h*100:.1f})")

# global green histogram for pin-like dark green
r,g,b = a[:,:,0].astype(np.float32), a[:,:,1].astype(np.float32), a[:,:,2].astype(np.float32)
for thr in [10,15,20,25,30]:
    m = (g > r + thr) & (g > b + thr) & (g > 40) & (g < 160) & (r < 130) & (b < 130)
    print(f"thr={thr} count={int(m.sum())}")
