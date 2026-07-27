import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(r"C:\Dev\hidden-acres\public\maps")
EDIT = ROOT / "_edit_r"
QA = EDIT / "qa_zones"
LIVE = ROOT / "hidden-acres-grounds-illustrated.png"
RESUME_R = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r.png"
R_BASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r-base.png"
WORK_R2 = EDIT / "work-r2-only.png"

PATCH = EDIT / "patch-ballroom-tip-clean.png"
if not PATCH.exists():
    PATCH = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets\patch-ballroom-tip-clean.png")
    shutil.copy2(PATCH, EDIT / PATCH.name)

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
bx0, by0, bx1, by1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]
GROOM = (200, 510, 290, 630)
ZONE = (265, 850, 380, 920)
Y_PROTECT = 845


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB"))


def save_rgb(a, p):
    Image.fromarray(a).save(p, optimize=True)


def elliptical_alpha(h, w, feather, y_full_start, y_protect=845):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rx, ry = max(w / 2.0 - 1, 1), max(h / 2.0 - 1, 1)
    norm = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    a = np.clip(1.25 - norm, 0, 1)
    for yi in range(h):
        yf = y_full_start + yi
        if yf < y_protect + 5:
            t = np.clip((yf - (y_protect - 8)) / 13.0, 0, 1)
            a[yi, :] *= t
    k = int(max(3, feather * 2 + 1)) | 1
    a = cv2.GaussianBlur(a, (k, k), feather / 2.5)
    return np.clip(a, 0, 1)


shutil.copy2(LIVE, EDIT / "work-ballroom-pass.png")
work = load_rgb(LIVE).copy()
work_r2 = load_rgb(WORK_R2)

x0, y0, x1, y1 = ZONE
h, w = y1 - y0, x1 - x0

# grass fill from sides at same y band
gl = work[870:910, 200:250]
gr = work[870:910, 390:440]
gl_r = cv2.resize(gl, (w // 2, h), interpolation=cv2.INTER_LANCZOS4)
gr_r = cv2.resize(gr, (w - w // 2, h), interpolation=cv2.INTER_LANCZOS4)
grass = np.concatenate([gl_r, gr_r], axis=1)

# optional patch blend underneath grass for alignment
patch_map = load_rgb(PATCH)
if patch_map.shape[1] != 682:
    patch_map = np.asarray(Image.fromarray(patch_map).resize((682, 1024), Image.Resampling.LANCZOS))
patch_roi = patch_map[y0:y1, x0:x1]
mix = cv2.addWeighted(grass.astype(np.float32), 0.65, patch_roi.astype(np.float32), 0.35, 0)

alpha = elliptical_alpha(h, w, feather=42, y_full_start=y0, y_protect=Y_PROTECT)
m = alpha[..., None]
roi = work[y0:y1, x0:x1].astype(np.float32)
work[y0:y1, x0:x1] = np.clip(roi * (1 - m) + mix * m, 0, 255).astype(np.uint8)

# restore groom
gx0, gy0, gx1, gy1 = GROOM
work[gy0:gy1, gx0:gx1] = work_r2[gy0:gy1, gx0:gx1]

groom_diff = float(np.abs(work[gy0:gy1, gx0:gx1].astype(np.int16) - work_r2[gy0:gy1, gx0:gx1].astype(np.int16)).mean())

final_full = EDIT / "final-full.png"
final_cluster = EDIT / "final-cluster.png"
save_rgb(work, final_full)
save_rgb(work[by0:by1, bx0:bx1], final_cluster)
shutil.copy2(final_full, LIVE)
shutil.copy2(final_full, RESUME_R)

# qa ballroom only
zx0, zy0, zx1, zy1 = 250, 780, 400, 930
base_img = Image.open(R_BASE).convert("RGB")
live_img = Image.open(LIVE).convert("RGB")
base_img.crop((zx0, zy0, zx1, zy1)).save(QA / "ballroom_south_base.png", optimize=True)
live_img.crop((zx0, zy0, zx1, zy1)).save(QA / "ballroom_south_live.png", optimize=True)
b = base_img.crop((zx0, zy0, zx1, zy1))
l = live_img.crop((zx0, zy0, zx1, zy1))
bw, bh = b.size
cmp = Image.new("RGB", (bw * 2, bh))
cmp.paste(b, (0, 0))
cmp.paste(l, (bw, 0))
cmp.save(QA / "ballroom_south_compare.png", optimize=True)

print("=== BALLROOM SOUTH PASS ===")
print(f"Zone: x={x0}-{x1} y={y0}-{y1} feather=42px elliptical")
print(f"Fill: 65% side grass (200-250|390-440 @ y870-910) + 35% tip-clean patch")
print(f"Protected roof above y~{Y_PROTECT}")
print(f"groom mean abs diff vs work-r2-only: {groom_diff:.4f}")
for label, p in [("work", EDIT/"work-ballroom-pass.png"), ("final-full", final_full), ("final-cluster", final_cluster), ("live", LIVE), ("resume-r", RESUME_R), ("r-base", R_BASE)]:
    print(f"  {label}: {p.stat().st_size} bytes")
print(f"  QA refreshed: ballroom_south_live.png, ballroom_south_compare.png")


