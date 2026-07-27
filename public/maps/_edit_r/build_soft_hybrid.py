import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(r"C:\Dev\hidden-acres\public\maps")
EDIT = ROOT / "_edit_r"
QA = EDIT / "qa_zones"
QA.mkdir(parents=True, exist_ok=True)
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")

R_BASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r-base.png"
LIVE = ROOT / "hidden-acres-grounds-illustrated.png"
RESUME_R = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r.png"
WORK_R2 = EDIT / "work-r2-only.png"

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
bx0, by0, bx1, by1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]
GROOM = (200, 510, 290, 630)

PATCH_ASSETS = {
    "woods": ASSETS / "patch-woods-fill.png",
    "ballroom": ASSETS / "patch-ballroom-tip-clean.png",
    "pond": ASSETS / "patch-pond-lawn.png",
}

ZONES = {
    "pond": (95, 455, 220, 545),
    "ballroom": (255, 820, 385, 920),
    "bridal_south": (415, 655, 510, 785),
}

placements = []


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB"))


def save_rgb(a, p):
    Image.fromarray(a).save(p, optimize=True)


def scale_to_map(patch):
    if patch.shape[1] == 682 and patch.shape[0] == 1024:
        return patch
    return np.asarray(Image.fromarray(patch).resize((682, 1024), Image.Resampling.LANCZOS))


def elliptical_alpha(h, w, feather, y_bias=None):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rx, ry = max(w / 2.0 - 1, 1), max(h / 2.0 - 1, 1)
    norm = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    a = np.clip(1.2 - norm, 0, 1)
    if y_bias is not None:
        y0, y1 = y_bias
        for yi in range(h):
            yf = y0 + yi
            if yf < y1:
                t = np.clip((yf - (y1 - 25)) / 25.0, 0, 1)
                a[yi, :] *= t
    k = int(max(3, feather * 2 + 1)) | 1
    a = cv2.GaussianBlur(a, (k, k), feather / 2.8)
    return np.clip(a, 0, 1)


def soft_paste(work, patch_map, zone, feather, y_cut_protect=None, x_max=None):
    x0, y0, x1, y1 = zone
    roi_patch = patch_map[y0:y1, x0:x1].copy()
    h, w = roi_patch.shape[:2]
    alpha = elliptical_alpha(h, w, feather, y_bias=y_cut_protect)
    if x_max is not None:
        for xi in range(w):
            xf = x0 + xi
            if xf > x_max:
                alpha[:, xi] = 0
    m = alpha[..., None]
    roi = work[y0:y1, x0:x1].astype(np.float32)
    work[y0:y1, x0:x1] = np.clip(roi * (1 - m) + roi_patch.astype(np.float32) * m, 0, 255).astype(np.uint8)
    placements.append({"zone": zone, "feather": feather, "x": x0, "y": y0, "w": w, "h": h})


def tree_soft_layer(work, work_r2, dst, src, feather=28, strength=0.45):
    dx0, dy0, dx1, dy1 = dst
    sx0, sy0, sx1, sy1 = src
    tex = cv2.resize(work[sy0:sy1, sx0:sx1], (dx1 - dx0, dy1 - dy0), interpolation=cv2.INTER_LANCZOS4)
    h, w = tex.shape[:2]
    alpha = elliptical_alpha(h, w, feather) * strength
    for yi in range(h):
        if dy0 + yi < 640:
            alpha[yi, :] *= 0.0
    m = alpha[..., None]
    roi = work[dy0:dy1, dx0:dx1].astype(np.float32)
    work[dy0:dy1, dx0:dx1] = np.clip(roi * (1 - m) + tex.astype(np.float32) * m, 0, 255).astype(np.uint8)


patches = {}
for k, src in PATCH_ASSETS.items():
    dst = EDIT / src.name
    shutil.copy2(src, dst)
    patches[k] = scale_to_map(load_rgb(dst))

work_r2 = load_rgb(WORK_R2)
work = work_r2.copy()

soft_paste(work, patches["pond"], ZONES["pond"], feather=32, x_max=240)
soft_paste(work, patches["ballroom"], ZONES["ballroom"], feather=38, y_cut_protect=(833, 858))
soft_paste(work, patches["woods"], ZONES["bridal_south"], feather=34, y_cut_protect=(635, 655))
tree_soft_layer(work, work_r2, (420, 660, 510, 785), (545, 650, 600, 780), feather=30, strength=0.38)

gx0, gy0, gx1, gy1 = GROOM
work[gy0:gy1, gx0:gx1] = work_r2[gy0:gy1, gx0:gx1]

roi = work[by0:by1, bx0:bx1]
blur = cv2.GaussianBlur(roi, (0, 0), 1.0)
work[by0:by1, bx0:bx1] = np.clip(roi.astype(np.float32) + 0.18 * (roi.astype(np.float32) - blur.astype(np.float32)), 0, 255).astype(np.uint8)
work[gy0:gy1, gx0:gx1] = work_r2[gy0:gy1, gx0:gx1]

groom_diff = float(np.abs(work[gy0:gy1, gx0:gx1].astype(np.int16) - work_r2[gy0:gy1, gx0:gx1].astype(np.int16)).mean())

final_full = EDIT / "final-full.png"
final_cluster = EDIT / "final-cluster.png"
save_rgb(work, final_full)
save_rgb(work[by0:by1, bx0:bx1], final_cluster)
shutil.copy2(final_full, LIVE)
shutil.copy2(final_full, RESUME_R)

base_img = Image.open(R_BASE).convert("RGB")
live_img = Image.open(LIVE).convert("RGB")
qa_zones = {
    "pond_fork": (90, 450, 240, 560),
    "groom_west": (180, 500, 340, 640),
    "bridal_east": (380, 520, 540, 780),
    "ballroom_south": (250, 780, 400, 930),
}
for name, (zx0, zy0, zx1, zy1) in qa_zones.items():
    b = base_img.crop((zx0, zy0, zx1, zy1))
    l = live_img.crop((zx0, zy0, zx1, zy1))
    b.save(QA / f"{name}_base.png", optimize=True)
    l.save(QA / f"{name}_live.png", optimize=True)
    w, h = b.size
    cmp = Image.new("RGB", (w * 2, h))
    cmp.paste(b, (0, 0))
    cmp.paste(l, (w, 0))
    cmp.save(QA / f"{name}_compare.png", optimize=True)

print("=== SOFT HYBRID SHIP ===")
print("Base: work-r2-only.png only")
print()
print("Placements:")
for i, p in enumerate(placements):
    labels = ["pond-lawn", "ballroom-tip-clean", "woods-fill"]
    print(f"  {labels[i]}: x={p['x']} y={p['y']} w={p['w']} h={p['h']} feather={p['feather']}")
print("  tree secondary: dst 420,660-510,785 src 545-600 x 650-780 feather~30")
print()
print(f"groom mean abs diff vs work-r2-only: {groom_diff:.4f}")
print()
for label, p in [
    ("final-full", final_full),
    ("final-cluster", final_cluster),
    ("live", LIVE),
    ("resume-r", RESUME_R),
    ("r-base", R_BASE),
]:
    print(f"  {label}: {p.stat().st_size} bytes")
print(f"  live==resume-r: {LIVE.stat().st_size == RESUME_R.stat().st_size}")
print(f"  QA compares updated: {', '.join(k + '_compare.png' for k in qa_zones)}")
