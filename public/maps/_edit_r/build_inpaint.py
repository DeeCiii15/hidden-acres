import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(r"C:\Dev\hidden-acres\public\maps")
EDIT = ROOT / "_edit_r"
R_BASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r-base.png"
LIVE = ROOT / "hidden-acres-grounds-illustrated.png"
RESUME_R = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r.png"
R2 = EDIT / "cluster-fix-r2-resized.png"

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
x0, y0, x1, y1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]
H, W = 1024, 682

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


def paste_feather(work, patch, bx0, by0, feather=22):
    h, w = patch.shape[:2]
    m = feather_ellipse_mask(h, w, feather)[..., None]
    roi = work[by0 : by0 + h, bx0 : bx0 + w].astype(np.float32)
    work[by0 : by0 + h, bx0 : bx0 + w] = np.clip(roi * (1 - m) + patch.astype(np.float32) * m, 0, 255).astype(np.uint8)


def unsharp_region(arr, bx0, by0, bx1, by1, amount=0.25, sigma=1.0):
    roi = arr[by0:by1, bx0:bx1]
    blur = cv2.GaussianBlur(roi, (0, 0), sigma)
    arr[by0:by1, bx0:bx1] = np.clip(roi.astype(np.float32) + amount * (roi.astype(np.float32) - blur.astype(np.float32)), 0, 255).astype(np.uint8)


def save_mask(name, mask_u8):
    p = EDIT / f"inpaint-mask-{name}.png"
    cv2.imwrite(str(p), mask_u8)
    return p


def run_inpaint(work_bgr, combined_mask, radius=4):
    return cv2.inpaint(work_bgr, combined_mask, radius, cv2.INPAINT_TELEA)


def bridal_roof_score(work_rgb, zone):
    zx0, zy0, zx1, zy1 = zone
    roi = work_rgb[zy0:zy1, zx0:zx1].astype(np.float32)
    # roof-ish: darker brown/red vs green lawn; high saturation + mid-low green
    hsv = cv2.cvtColor(roi.astype(np.uint8), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    roof_like = ((s > 45) & (v < 200) & (h < 35)).astype(np.float32)
    return float(roof_like.mean())


# --- 1) start r-base ---
work = load_rgb(R_BASE).copy()
r_base_bytes = R_BASE.stat().st_size
notes.append(f"Started from r-base ({r_base_bytes} bytes)")

# --- 2) paste r2 ---
r2 = load_rgb(R2)
if r2.shape[1] != x1 - x0 or r2.shape[0] != y1 - y0:
    r2 = np.asarray(Image.fromarray(r2).resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS))
paste_feather(work, r2, x0, y0, feather=22)
save_rgb(work, EDIT / "work-r2-only.png")
notes.append("Feather-pasted r2 cluster (22px elliptical feather)")

# --- 3) masks ---
masks = {}

# A) pond fork spur - small irregular polygon (tan tongue into pond)
pond = np.zeros((H, W), np.uint8)
pond_poly = np.array([
    [118, 478], [165, 472], [188, 492], [175, 528], [142, 538], [108, 520], [105, 495]
], np.int32)
cv2.fillPoly(pond, [pond_poly], 255)
masks["pond-fork"] = pond

# B) south ballroom ghost - trapezoid south of main roof
ballroom = np.zeros((H, W), np.uint8)
ballroom_poly = np.array([
    [278, 848], [358, 842], [365, 898], [285, 905]
], np.int32)
cv2.fillPoly(ballroom, [ballroom_poly], 255)
masks["south-ballroom-ghost"] = ballroom

# C) bridal south mass
bridal = np.zeros((H, W), np.uint8)
bridal_rect = (420, 655, 510, 780)  # x0,y0,x1,y1
cv2.rectangle(bridal, (bridal_rect[0], bridal_rect[1]), (bridal_rect[2], bridal_rect[3]), 255, -1)
# taper north edge to avoid cross-wing
for y in range(bridal_rect[1], bridal_rect[3]):
    if y < 665:
        fade = int(255 * max(0, (y - 655) / 10.0))
        bridal[y, bridal_rect[0]:bridal_rect[2]] = np.minimum(bridal[y, bridal_rect[0]:bridal_rect[2]], fade)
masks["bridal-south"] = bridal

# D) ghost pins / dark arcs north of courtyard
ghosts = np.zeros((H, W), np.uint8)
cv2.ellipse(ghosts, (340, 502), (38, 18), 0, 0, 360, 255, -1)
cv2.ellipse(ghosts, (365, 512), (22, 12), -15, 0, 360, 255, -1)
cv2.circle(ghosts, (455, 595), 14, 255, -1)  # possible doubled pin near bridal approach
masks["courtyard-ghosts"] = ghosts

for name, m in masks.items():
    save_mask(name.replace("_", "-"), m)

combined = np.zeros((H, W), np.uint8)
for m in masks.values():
    combined = cv2.max(combined, m)
cv2.imwrite(str(EDIT / "inpaint-mask-combined.png"), combined)
notes.append("Saved inpaint masks + combined")

work_bgr = cv2.cvtColor(work, cv2.COLOR_RGB2BGR)
work_bgr = run_inpaint(work_bgr, combined, radius=4)
work = cv2.cvtColor(work_bgr, cv2.COLOR_BGR2RGB)

# check bridal roof score; expand once if needed
bridal_zone = bridal_rect
score = bridal_roof_score(work, bridal_zone)
notes.append(f"Bridal south roof-like pixel ratio after inpaint: {score:.3f}")
if score > 0.12:
    bridal2 = bridal.copy()
    cv2.rectangle(bridal2, (415, 648), (515, 785), 255, -1)
    for y in range(648, 785):
        if y < 662:
            fade = int(255 * max(0, (y - 648) / 14.0))
            bridal2[y, 415:515] = np.minimum(bridal2[y, 415:515], fade)
    save_mask("bridal-south-expanded", bridal2)
    combined2 = cv2.max(combined, bridal2)
    cv2.imwrite(str(EDIT / "inpaint-mask-combined.png"), combined2)
    work_bgr = cv2.cvtColor(work, cv2.COLOR_RGB2BGR)
    work_bgr = run_inpaint(work_bgr, combined2, radius=5)
    work = cv2.cvtColor(work_bgr, cv2.COLOR_BGR2RGB)
    score2 = bridal_roof_score(work, (415, 648, 515, 785))
    notes.append(f"Expanded bridal mask + re-inpaint; roof-like ratio now {score2:.3f}")

# 4) optional tree texture blend for bridal south forest
bx0, by0, bx1, by1 = 420, 655, 510, 780
sample_x0, sample_x1 = 520, 560
sy0, sy1 = by0, by1
sample = work[sy0:sy1, sample_x0:sample_x1].astype(np.float32)
if sample.size > 0:
    tile = np.tile(sample, (1, max(1, (bx1 - bx0 + sample.shape[1] - 1) // sample.shape[1]), 1))[:, : bx1 - bx0]
    alpha = np.zeros((sy1 - sy0, bx1 - bx0), np.float32)
    alpha[:, :] = 0.35
    for y in range(sy0, sy1):
        t = np.clip((y - 670) / 90.0, 0, 1)
        alpha[y - sy0, :] = 0.15 + 0.35 * t
    alpha = cv2.GaussianBlur(alpha, (21, 21), 8)[..., None]
    roi = work[by0:by1, bx0:bx1].astype(np.float32)
    work[by0:by1, bx0:bx1] = np.clip(roi * (1 - alpha) + tile * alpha, 0, 255).astype(np.uint8)
    notes.append("Soft tree-texture sample from east woods blended into bridal south")

# 5) unsharp cluster
unsharp_region(work, x0, y0, x1, y1, amount=0.25, sigma=1.0)

# 6) outputs
final_full = EDIT / "final-full.png"
final_cluster = EDIT / "final-cluster.png"
save_rgb(work, final_full)
save_rgb(work[y0:y1, x0:x1], final_cluster)
shutil.copy2(final_full, LIVE)
shutil.copy2(final_full, RESUME_R)

# 7) QA before/after cluster
rbase = load_rgb(R_BASE)
before_c = rbase[y0:y1, x0:x1]
after_c = work[y0:y1, x0:x1]
cmp = np.zeros((y1 - y0, (x1 - x0) * 2, 3), np.uint8)
cmp[:, : x1 - x0] = before_c
cmp[:, x1 - x0 :] = after_c
save_rgb(cmp, EDIT / "qa-before-after.png")

print("=== INPAINT REBUILD (no qbase clones) ===")
for n in notes:
    print(f"  - {n}")
print()
print("Inpaint zones (approx):")
print("  A pond fork polygon ~ x100-200 y470-545 (small spur only)")
print("  B south ballroom ghost trapezoid ~ x270-370 y830-910")
print("  C bridal south rect ~ x420-510 y655-780 (tapered below cross-wing)")
print("  D courtyard ghost ellipses ~ x300-420 y480-530 + pin near bridal")
print()
for label, p in [
    ("work-r2-only", EDIT / "work-r2-only.png"),
    ("final-full", final_full),
    ("final-cluster", final_cluster),
    ("live", LIVE),
    ("resume-r", RESUME_R),
    ("qa-before-after", EDIT / "qa-before-after.png"),
    ("r-base (unchanged)", R_BASE),
]:
    print(f"  {label}: {p.stat().st_size} bytes")
print()
print(f"live == resume-r bytes: {LIVE.stat().st_size == RESUME_R.stat().st_size}")
print(f"r-base still {R_BASE.stat().st_size} bytes (unchanged)")
