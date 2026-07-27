"""Precise ballroom body width: resume-j vs resume-o-gen."""
from PIL import Image
import numpy as np
from pathlib import Path

J = np.array(Image.open("public/maps/hidden-acres-grounds-illustrated-v-map-resume-j.png").convert("RGB"))
G = np.array(Image.open("public/maps/hidden-acres-grounds-illustrated-v-map-resume-o-gen.png").convert("RGB"))
OUT = Path("public/maps/_qa-crops-resume-o")
OUT.mkdir(parents=True, exist_ok=True)
print(f"images {J.shape[0]}x{J.shape[1]}")


def is_building(rgb):
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    green = (g > r + 12) & (g > b + 8) & (g > 55)
    warm = (r > 90) & (r < 210) & (r > g + 10) & (r > b + 15) & (g < 170) & (b < 140)
    lum = (r.astype(np.int32) + g + b) / 3.0
    mx = np.maximum(np.maximum(r, g), b).astype(np.float32)
    mn = np.minimum(np.minimum(r, g), b).astype(np.float32)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0.0)
    wall = (lum > 150) & (sat < 0.35) & (r > 140) & (g > 130) & (b > 100) & ~((g > r + 5) & (g > b + 5))
    eave = (lum < 95) & (lum > 25) & (r >= g - 5) & (g < 110) & ~((g > r + 8) & (g > b + 5))
    return (warm | wall | eave) & ~green


SCAN_YS = [1050, 1100, 1150, 1200, 1250, 1300]
# Main ballroom body (west mass through east face); stop before east courtyard cluster ~497+
X_LO, X_HI = 200, 490
GAP_TOL = 12


def measure(rgb, label):
    m = is_building(rgb)
    rows = []
    print(f"\n=== {label} ===")
    print(f"{'y':>6} {'x0':>6} {'x1':>6} {'width':>6}")
    for y in SCAN_YS:
        xs = np.where(m[y, X_LO:X_HI])[0] + X_LO
        if len(xs) == 0:
            rows.append((y, None, None, None))
            print(f"{y:6d} n/a")
            continue
        # merge micro-gaps, then take largest run overlapping core
        segs, s, prev = [], int(xs[0]), int(xs[0])
        for x in xs[1:]:
            x = int(x)
            if x - prev <= GAP_TOL:
                prev = x
            else:
                segs.append((s, prev))
                s = prev = x
        segs.append((s, prev))
        core = [t for t in segs if t[0] <= 450 and t[1] >= 280]
        pick = max(core or segs, key=lambda t: t[1] - t[0])
        x0, x1 = pick
        w = x1 - x0 + 1
        rows.append((y, x0, x1, w))
        print(f"{y:6d} {x0:6d} {x1:6d} {w:6d}")
    return rows, m


rj, mj = measure(J, "resume-j")
rg, mg = measure(G, "resume-o-gen")

print("\n=== Comparison ===")
print(f"{'y':>6} {'j_x0':>6} {'j_x1':>6} {'j_w':>5} {'g_x0':>6} {'g_x1':>6} {'g_w':>5} {'dw':>5} {'dL':>4} {'dR':>4}")
wsj, wsg = [], []
for (y, a0, a1, aw), (_, b0, b1, bw) in zip(rj, rg):
    wsj.append(aw); wsg.append(bw)
    print(f"{y:6d} {a0:6d} {a1:6d} {aw:5d} {b0:6d} {b1:6d} {bw:5d} {bw-aw:+5d} {b0-a0:+4d} {b1-a1:+4d}")

avg_j, avg_g = float(np.mean(wsj)), float(np.mean(wsg))
med_j, med_g = float(np.median(wsj)), float(np.median(wsg))
print(f"\nAVG  j={avg_j:.1f}  gen={avg_g:.1f}  delta(gen-j)={avg_g-avg_j:+.1f}px")
print(f"MED  j={med_j:.1f}  gen={med_g:.1f}  delta(gen-j)={med_g-med_j:+.1f}px")

# Groom
def groom_cy(rgb):
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    roof = (r > 95) & (r < 200) & (r > g + 12) & (r > b + 20) & (g < 155) & (b < 130)
    ys, xs = np.where(roof[780:1040, 280:560])
    return float(xs.mean() + 280), float(ys.mean() + 780), len(ys)

cxj, cyj, nj = groom_cy(J)
cxg, cyg, ng = groom_cy(G)
dcy = cyg - cyj
print(f"\n=== Groom roof centroid ===")
print(f"j:   cx={cxj:.1f} cy={cyj:.1f} n={nj}")
print(f"gen: cx={cxg:.1f} cy={cyg:.1f} n={ng}")
print(f"dcy(gen-j)={dcy:+.1f}  north_by={max(0,-dcy):.1f}px")

# Diffs
def save_diff(a, b, box, path):
    x0, y0, x1, y1 = box
    pa, pb = a[y0:y1, x0:x1].astype(np.float32), b[y0:y1, x0:x1].astype(np.float32)
    ad = np.abs(pa - pb)
    mean, mx = float(ad.mean()), ad.max(-1)
    pct = float((mx > 25).mean() * 100)
    heat = np.clip(mx * 4, 0, 255).astype(np.uint8)
    heat_rgb = np.stack([heat, (heat * 0.4).astype(np.uint8), ((255 - heat) // 3).astype(np.uint8)], -1)
    out = np.clip((pa * 0.35).astype(np.int16) + heat_rgb.astype(np.int16), 0, 255).astype(np.uint8)
    Image.fromarray(out).save(path)
    return mean, pct

mb, pb = save_diff(J, G, (200, 1000, 490, 1340), OUT / "diff-ballroom.png")
mgr, pgr = save_diff(J, G, (280, 780, 560, 1040), OUT / "diff-groom.png")
print(f"\n=== Absdiff ===")
print(f"ballroom: mean={mb:.2f} pct>25={pb:.2f}% -> {OUT/'diff-ballroom.png'}")
print(f"groom:    mean={mgr:.2f} pct>25={pgr:.2f}% -> {OUT/'diff-groom.png'}")

# overlays
for name, rgb, rows, mask in (("j", J, rj, mj), ("gen", G, rg, mg)):
    y0, y1, x0, x1 = 1000, 1340, 200, 490
    crop = rgb[y0:y1, x0:x1].astype(np.float32).copy()
    mm = mask[y0:y1, x0:x1]
    crop[mm, 0] = np.clip(crop[mm, 0] * 0.4 + 220, 0, 255)
    crop[mm, 1] *= 0.35; crop[mm, 2] *= 0.35
    for y, xa, xb, w in rows:
        yy = y - y0
        if w is None or not (0 <= yy < crop.shape[0]):
            continue
        crop[yy, :] = [0, 255, 255]
        for xx in (xa - x0, xb - x0):
            if 0 <= xx < crop.shape[1]:
                crop[max(0, yy - 5):min(crop.shape[0], yy + 6), xx] = [255, 0, 255]
    Image.fromarray(crop.astype(np.uint8)).save(OUT / f"mask-ballroom-{name}.png")

print("\n========== VERDICT ==========")
print(f"Ballroom wider on gen? {'YES' if avg_g > avg_j + 0.5 else 'NO'}")
print(f"Average width delta (gen - j): {avg_g - avg_j:+.1f} px")
print(f"Groom north on gen by: {max(0, -dcy):.1f} px")
