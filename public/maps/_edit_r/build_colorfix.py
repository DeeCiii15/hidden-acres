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

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
bx0, by0, bx1, by1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]

REGIONS = {
    "bridal_south": (420, 660, 510, 780),
    "ballroom_south_ghost": (270, 840, 370, 910),
    "pond_fork": (110, 480, 200, 540),
    "groom_west_check": (200, 520, 280, 620),
}


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB"))


def save_rgb(a, p):
    Image.fromarray(a).save(p, optimize=True)


def region_slice(rgb, reg):
    x0, y0, x1, y1 = reg
    return rgb[y0:y1, x0:x1], (x0, y0, x1, y1)


def roof_green_stats(rgb, reg):
    roi, _ = region_slice(rgb, reg)
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    roof = ((h <= 25) | ((h >= 160) & (h <= 180))) & (s > 40) & (v >= 60) & (v <= 200)
    green = (h >= 35) & (h <= 85) & (s > 35) & (v >= 40)
    return float(roof.mean() * 100), float(green.mean() * 100)


def roof_mask_in_region(rgb, reg, dilate=3):
    roi, (x0, y0, x1, y1) = region_slice(rgb, reg)
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = (((h <= 25) | ((h >= 160) & (h <= 180))) & (s > 40) & (v >= 60) & (v <= 200)).astype(np.uint8) * 255
    if dilate:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate * 2 + 1, dilate * 2 + 1))
        m = cv2.dilate(m, k, 1)
    full = np.zeros(rgb.shape[:2], np.uint8)
    full[y0:y1, x0:x1] = m
    return full


def tan_spur_mask(rgb, reg):
    roi, (x0, y0, x1, y1) = region_slice(rgb, reg)
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    tan = ((h >= 8) & (h <= 35) & (s >= 25) & (s <= 120) & (v >= 90) & (v <= 220)).astype(np.uint8) * 255
    ww = tan.shape[1]
    west = np.zeros_like(tan)
    west[:, : int(ww * 0.7)] = 255
    tan = cv2.bitwise_and(tan, west)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    tan = cv2.morphologyEx(tan, cv2.MORPH_OPEN, k)
    tan = cv2.dilate(tan, k, 1)
    full = np.zeros(rgb.shape[:2], np.uint8)
    full[y0:y1, x0:x1] = tan
    return full


def ballroom_faint_mask(rgb, reg):
    x0, y0, x1, y1 = reg
    roi = rgb[y0:y1, x0:x1]
    h, w = roi.shape[:2]
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    hh, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    roof = (((hh <= 25) | ((hh >= 160) & (hh <= 180))) & (s > 35) & (v >= 50) & (v <= 210)).astype(np.float32)
    yy = np.linspace(0, 1, h)[:, None]
    south = np.clip((yy - 0.4) / 0.6, 0, 1)
    faint = (1.0 - (v.astype(np.float32) / 255.0))
    score = roof * south * (0.5 + 0.5 * faint)
    m = (score > 0.42).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
    full = np.zeros(rgb.shape[:2], np.uint8)
    full[y0:y1, x0:x1] = m
    full[:845, :] = 0
    return full


def feather_blend_masked(work, src_patch, dst_xyxy, mask_full, feather=16):
    x0, y0, x1, y1 = dst_xyxy
    dh, dw = y1 - y0, x1 - x0
    if src_patch.shape[0] != dh or src_patch.shape[1] != dw:
        src_patch = cv2.resize(src_patch, (dw, dh), interpolation=cv2.INTER_LANCZOS4)
    m = mask_full[y0:y1, x0:x1].astype(np.float32) / 255.0
    k = int(max(3, feather * 2 + 1)) | 1
    m = cv2.GaussianBlur(m, (k, k), feather / 3.0)
    m = np.clip(m, 0, 1)[..., None]
    roi = work[y0:y1, x0:x1].astype(np.float32)
    work[y0:y1, x0:x1] = np.clip(roi * (1 - m) + src_patch.astype(np.float32) * m, 0, 255).astype(np.uint8)


def paste_feather_r2_if_missing():
    j = json.loads((EDIT / "bbox.json").read_text())
    x0, y0, x1, y1 = j["x0"], j["y0"], j["x1"], j["y1"]
    work = load_rgb(R_BASE).copy()
    r2 = load_rgb(EDIT / "cluster-fix-r2-resized.png")
    h, w = r2.shape[:2]
    fm = cv2.GaussianBlur(
        feather_ellipse(w, h, 22)[..., None].astype(np.float32), (45, 45), 9
    )
    roi = work[y0 : y0 + h, x0 : x0 + w].astype(np.float32)
    work[y0 : y0 + h, x0 : x0 + w] = np.clip(roi * (1 - fm) + r2.astype(np.float32) * fm, 0, 255).astype(np.uint8)
    save_rgb(work, EDIT / "work-r2-only.png")


def feather_ellipse(h, w, feather=22.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rx, ry = max(w / 2.0 - 2, 1), max(h / 2.0 - 2, 1)
    norm = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    mask = np.clip(1.15 - norm, 0, 1)
    k = int(max(3, feather * 2 + 1)) | 1
    return np.clip(cv2.GaussianBlur(mask, (k, k), feather / 2.5), 0, 1)


work_r2 = EDIT / "work-r2-only.png"
if not work_r2.exists():
    paste_feather_r2_if_missing()
shutil.copy2(work_r2, EDIT / "work-colorfix.png")
work = load_rgb(EDIT / "work-colorfix.png").copy()
groom_before = work[520:620, 200:280].copy()

print("=== REGION ANALYSIS (before) ===")
before = {}
for name, reg in REGIONS.items():
    r, g = roof_green_stats(work, reg)
    before[name] = (r, g)
    print(f"  {name}: roof={r:.2f}% green={g:.2f}%")

actions = []

# 1 bridal south
bs = REGIONS["bridal_south"]
if before["bridal_south"][0] > 8.0:
    m = roof_mask_in_region(work, bs, dilate=4)
    m[:640, :] = 0
    m[:, :420] = 0
    m[:, 510:] = 0
    if m.max() > 0:
        cv2.imwrite(str(EDIT / "mask-colorfix-bridal-south-roof.png"), m)
        trees = work[700:780, 530:580].copy()
        feather_blend_masked(work, trees, bs, m, feather=16)
        actions.append("bridal_south: tree feather on dilated roof mask (y>=640)")
    else:
        actions.append("bridal_south: skipped (empty mask)")
else:
    actions.append("bridal_south: skipped (roof below threshold)")

# 2 ballroom ghost
bg = REGIONS["ballroom_south_ghost"]
if before["ballroom_south_ghost"][0] > 5.0:
    m = ballroom_faint_mask(work, bg)
    if m.max() > 0:
        cv2.imwrite(str(EDIT / "mask-colorfix-ballroom-ghost.png"), m)
        x0, y0, x1, y1 = bg
        gh, gw = y1 - y0, x1 - x0
        gl = cv2.resize(work[860:910, 200:250], (gw // 2, gh), interpolation=cv2.INTER_LANCZOS4)
        gr = cv2.resize(work[860:910, 380:430], (gw - gw // 2, gh), interpolation=cv2.INTER_LANCZOS4)
        grass = np.concatenate([gl, gr], axis=1)
        feather_blend_masked(work, grass, bg, m, feather=20)
        actions.append("ballroom_south_ghost: grass feather on faint south mask (y>=845)")
    else:
        actions.append("ballroom_south_ghost: skipped (empty mask)")
else:
    actions.append("ballroom_south_ghost: skipped")

# 3 pond fork
pf = REGIONS["pond_fork"]
tan_pct = 100.0 - before["pond_fork"][1]
if before["pond_fork"][0] > 2.5 or tan_pct > 15:
    m = tan_spur_mask(work, pf)
    if m.max() > 0 and m.sum() > 800:
        cv2.imwrite(str(EDIT / "mask-colorfix-pond-fork.png"), m)
        grass = work[520:560, 160:210].copy()
        feather_blend_masked(work, grass, pf, m, feather=14)
        actions.append("pond_fork: local grass on tan spur mask")
    else:
        actions.append("pond_fork: skipped (mask too small/empty)")
else:
    actions.append("pond_fork: skipped")

# 4 ghost pins - skip (uncertain) conservative
actions.append("ghost pins: skipped (conservative, no inpaint)")

# groom unchanged check
delta = np.abs(work[520:620, 200:280].astype(np.int16) - groom_before.astype(np.int16)).mean()
actions.append(f"groom_west_check mean pixel delta: {delta:.2f} (should be ~0)")

# unsharp cluster
roi = work[by0:by1, bx0:bx1]
blur = cv2.GaussianBlur(roi, (0, 0), 1.0)
work[by0:by1, bx0:bx1] = np.clip(roi.astype(np.float32) + 0.2 * (roi.astype(np.float32) - blur.astype(np.float32)), 0, 255).astype(np.uint8)

print("\n=== REPAIRS ===")
for a in actions:
    print(f"  - {a}")

after_bs = roof_green_stats(work, bs)[0]
after_bg = roof_green_stats(work, bg)[0]
print("\n=== REGION ANALYSIS (after) ===")
for name, reg in REGIONS.items():
    r, g = roof_green_stats(work, reg)
    print(f"  {name}: roof={r:.2f}% green={g:.2f}%")
print("\nRoof % before -> after:")
print(f"  bridal_south: {before['bridal_south'][0]:.2f}% -> {after_bs:.2f}%")
print(f"  ballroom_south_ghost: {before['ballroom_south_ghost'][0]:.2f}% -> {after_bg:.2f}%")

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

print("\n=== FILES ===")
for label, p in [
    ("work-colorfix", EDIT / "work-colorfix.png"),
    ("final-full", final_full),
    ("final-cluster", final_cluster),
    ("live", LIVE),
    ("resume-r", RESUME_R),
    ("qa-before-after", EDIT / "qa-before-after.png"),
]:
    print(f"  {label}: {p.stat().st_size} bytes")
print(f"  r-base: {R_BASE.stat().st_size} bytes (unchanged)")

