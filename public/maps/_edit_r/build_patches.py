import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(r"C:\Dev\hidden-acres\public\maps")
EDIT = ROOT / "_edit_r"
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")
R_BASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r-base.png"
LIVE = ROOT / "hidden-acres-grounds-illustrated.png"
RESUME_R = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r.png"

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
bx0, by0, bx1, by1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]
W, H = 682, 1024

PATCH_FILES = {
    "pond": ASSETS / "patch-pond-lawn.png",
    "ballroom": ASSETS / "patch-ballroom-south-clean.png",
    "bridal": ASSETS / "patch-bridal-north-only.png",
}

placements = []
notes = []


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB"))


def save_rgb(a, p):
    Image.fromarray(a).save(p, optimize=True)


def feather_ellipse_mask(h, w, feather=22.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rx, ry = max(w / 2.0 - 2, 1), max(h / 2.0 - 2, 1)
    norm = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    mask = np.clip(1.15 - norm, 0, 1)
    k = int(max(3, feather * 2 + 1)) | 1
    mask = cv2.GaussianBlur(mask, (k, k), feather / 2.5)
    return np.clip(mask, 0, 1)


def edge_feather_alpha(h, w, feather):
    a = np.ones((h, w), np.float32)
    f = int(max(1, feather))
    for i in range(min(f, h // 2, w // 2)):
        t = (i + 1) / f
        a[i, :] *= t
        a[-1 - i, :] *= t
        a[:, i] *= t
        a[:, -1 - i] *= t
    return a


def paste_roi(work, patch_roi, x0, y0, feather=22, alpha=None):
    h, w = patch_roi.shape[:2]
    if alpha is None:
        alpha = feather_ellipse_mask(h, w, feather)
    else:
        alpha = np.clip(alpha, 0, 1)
        k = int(max(3, feather * 2 + 1)) | 1
        alpha = cv2.GaussianBlur(alpha, (k, k), feather / 3.0)
    m = alpha[..., None]
    roi = work[y0 : y0 + h, x0 : x0 + w].astype(np.float32)
    work[y0 : y0 + h, x0 : x0 + w] = np.clip(roi * (1 - m) + patch_roi.astype(np.float32) * m, 0, 255).astype(np.uint8)
    placements.append({"x": x0, "y": y0, "w": w, "h": h, "feather": feather})


def scale_patch_to_map(patch_rgb):
    if patch_rgb.shape[1] == W and patch_rgb.shape[0] == H:
        return patch_rgb
    return np.asarray(Image.fromarray(patch_rgb).resize((W, H), Image.Resampling.LANCZOS))


def stamp_from_work(work, src_xyxy, dst_xyxy, feather=22, strength=0.7):
    sx0, sy0, sx1, sy1 = src_xyxy
    dx0, dy0, dx1, dy1 = dst_xyxy
    src = work[sy0:sy1, sx0:sx1]
    dh, dw = dy1 - dy0, dx1 - dx0
    tex = cv2.resize(src, (dw, dh), interpolation=cv2.INTER_LANCZOS4)
    alpha = edge_feather_alpha(dh, dw, feather) * strength
    paste_roi(work, tex, dx0, dy0, feather=feather, alpha=alpha)


# --- base work-patches ---
work_r2 = EDIT / "work-r2-only.png"
if work_r2.exists():
    work = load_rgb(work_r2)
    notes.append("Base: work-r2-only.png")
else:
    work = load_rgb(R_BASE)
    r2 = load_rgb(EDIT / "cluster-fix-r2-resized.png")
    paste_roi(work, r2, bx0, by0, feather=22)
    save_rgb(work, work_r2)
    notes.append("Recreated work-r2-only from r-base + r2")

work_start = EDIT / "work-patches.png"
shutil.copy2(work_r2 if work_r2.exists() else work_start, work_start)
work = load_rgb(work_start).copy()
notes.append("Starting point saved as work-patches.png")

# copy patch assets
local_patches = {}
for key, src in PATCH_FILES.items():
    dst = EDIT / src.name
    shutil.copy2(src, dst)
    local_patches[key] = load_rgb(dst)
    notes.append(f"Copied {src.name}")

# scale patches to full map
pond_map = scale_patch_to_map(local_patches["pond"])
ball_map = scale_patch_to_map(local_patches["ballroom"])
bridal_map = scale_patch_to_map(local_patches["bridal"])

# A) pond lawn x=90-230 y=450-560
px0, py0, px1, py1 = 90, 450, 230, 560
pond_roi = pond_map[py0:py1, px0:px1]
paste_roi(work, pond_roi, px0, py0, feather=25)
notes.append("A pond lawn patch blended (avoid x>250 groom)")

# B) ballroom south tip only y=810-930 x=250-390
bx0z, by0z, bx1z, by1z = 250, 810, 390, 930
ball_roi = ball_map[by0z:by1z, bx0z:bx1z]
paste_roi(work, ball_roi, bx0z, by0z, feather=28)
notes.append("B ballroom south clean (~120px tip band)")

# C) bridal north-only with east-heavy mask x=350-540 y=480-720
cx0, cy0, cx1, cy1 = 350, 480, 540, 720
bridal_roi = bridal_map[cy0:cy1, cx0:cx1]
h, w = bridal_roi.shape[:2]
alpha = np.zeros((h, w), np.float32)
for yi in range(h):
    y_full = cy0 + yi
    for xi in range(w):
        x_full = cx0 + xi
        ax = np.clip((x_full - 395) / 125.0, 0.0, 1.0)
        if x_full < 380:
            ax = 0.0
        ay = 1.0
        if y_full < 635:
            ay = 0.25
        elif y_full < 655:
            ay = 0.45
        elif y_full > 660:
            ay = 0.95
        alpha[yi, xi] = ax * ay
paste_roi(work, bridal_roi, cx0, cy0, feather=24, alpha=alpha)
notes.append("C bridal patch with east-heavy mask (weak west/groom side)")

# bridal south trees: stamp canopy from east woods
stamp_from_work(work, (520, 680, 560, 780), (420, 660, 510, 780), feather=26, strength=0.72)
notes.append("C2 tree canopy stamp over bridal-south x420-510 y660-780 from sample x520-560")

# mild cluster unsharp
roi = work[by0:by1, bx0:bx1]
blur = cv2.GaussianBlur(roi, (0, 0), 1.0)
work[by0:by1, bx0:bx1] = np.clip(roi.astype(np.float32) + 0.22 * (roi.astype(np.float32) - blur.astype(np.float32)), 0, 255).astype(np.uint8)

# outputs
final_full = EDIT / "final-full.png"
final_cluster = EDIT / "final-cluster.png"
save_rgb(work, final_full)
save_rgb(work[by0:by1, bx0:bx1], final_cluster)
shutil.copy2(final_full, LIVE)
shutil.copy2(final_full, RESUME_R)

rbase = load_rgb(R_BASE)
qa = np.zeros((by1 - by0, (bx1 - bx0) * 2, 3), np.uint8)
qa[:, : bx1 - bx0] = rbase[by0:by1, bx0:bx1]
qa[:, bx1 - bx0 :] = work[by0:by1, bx0:bx1]
save_rgb(qa, EDIT / "qa-before-after.png")

print("=== PATCH REBUILD (r2-only base, no inpaint) ===")
for n in notes:
    print(f"  - {n}")
print()
print("Patch placements (x,y,w,h,feather):")
labels = ["pond", "ballroom-south", "bridal-east-weighted"]
for i, p in enumerate(placements[:3]):
    print(f"  {labels[i]}: x={p['x']} y={p['y']} w={p['w']} h={p['h']} feather={p['feather']}")
print("  tree-stamp bridal-south: dst x=420 y=660 w=90 h=120 src x=520-560 y=680-780")
print()
for name, p in [
    ("work-patches", EDIT / "work-patches.png"),
    ("final-full", final_full),
    ("final-cluster", final_cluster),
    ("live", LIVE),
    ("resume-r", RESUME_R),
    ("qa-before-after", EDIT / "qa-before-after.png"),
    ("r-base", R_BASE),
]:
    print(f"  {name}: {p.stat().st_size} bytes")
print(f"live==resume-r: {LIVE.stat().st_size == RESUME_R.stat().st_size}")
print(f"r-base unchanged bytes: {R_BASE.stat().st_size}")

