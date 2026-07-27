import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(r"C:\Dev\hidden-acres\public\maps")
EDIT = ROOT / "_edit_r"
LIVE = ROOT / "hidden-acres-grounds-illustrated.png"
RESUME_R = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r.png"
R_BASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r-base.png"
WORK_R2 = EDIT / "work-r2-only.png"

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
bx0, by0, bx1, by1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]

BALLROOM_ROI = (270, 840, 370, 910)
BALLROOM_CUT_Y = 858
BALLROOM_X = (275, 365)
POND_ROI = (100, 470, 210, 545)
GROOM = (200, 520, 280, 620)


def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB"))


def save_rgb(a, p):
    Image.fromarray(a).save(p, optimize=True)


def roof_pct(rgb, reg):
    x0, y0, x1, y1 = reg
    roi = rgb[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    roof = ((h <= 25) | ((h >= 160) & (h <= 180))) & (s > 40) & (v >= 60) & (v <= 200)
    return float(roof.mean() * 100)


def tan_pct(rgb, reg):
    x0, y0, x1, y1 = reg
    roi = rgb[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    tan = (h >= 10) & (h <= 40) & (s >= 20) & (s <= 120) & (v >= 120) & (v <= 220)
    rgbf = roi.astype(np.float32)
    rg_high = (rgbf[..., 0] + rgbf[..., 1]) / 2.0
    b_rel = rg_high - rgbf[..., 2]
    tan |= (b_rel > 15) & (v >= 110) & (s >= 15)
    return float(tan.mean() * 100)


def feather_alpha(h, w, feather):
    a = np.ones((h, w), np.float32)
    f = max(1, int(feather))
    for i in range(min(f, h // 2, w // 2)):
        t = (i + 1) / f
        a[i, :] *= t
        a[-1 - i, :] *= t
        a[:, i] *= t
        a[:, -1 - i] *= t
    return a


# Start from live
shutil.copy2(LIVE, EDIT / "work-pass2.png")
work = load_rgb(EDIT / "work-pass2.png").copy()
work_r2 = load_rgb(WORK_R2)

ball_before = roof_pct(work, BALLROOM_ROI)
pond_tan_before = tan_pct(work, POND_ROI)
print("=== BEFORE ===")
print(f"  ballroom roof% {BALLROOM_ROI}: {ball_before:.2f}")
print(f"  pond tan% {POND_ROI}: {pond_tan_before:.2f}")

# 1) Ballroom south grass below y=858
y_cut = BALLROOM_CUT_Y
x0, x1 = BALLROOM_X
for y in range(y_cut, 921):
    y0, y1 = y, y + 1
    band_h = 1
    band_w = x1 - x0
    gl = work[y0:y1, 210:260]
    gr = work[y0:y1, 380:430]
    if gl.size == 0 or gr.size == 0:
        continue
    gl = cv2.resize(gl, (band_w // 2, band_h), interpolation=cv2.INTER_LINEAR)
    gr = cv2.resize(gr, (band_w - band_w // 2, band_h), interpolation=cv2.INTER_LINEAR)
    grass = np.concatenate([gl, gr], axis=1)
    alpha = 1.0
    if y == y_cut:
        alpha = 0.85
    work[y0:y1, x0:x1] = (
        work[y0:y1, x0:x1].astype(np.float32) * (1 - alpha) + grass.astype(np.float32) * alpha
    ).astype(np.uint8)
# horizontal feather band at cut
cut_band = work[y_cut - 3 : y_cut + 8, x0:x1].astype(np.float32)
grass_cut = work[y_cut : y_cut + 1, x0:x1].astype(np.float32)
for i in range(cut_band.shape[0]):
    t = i / max(cut_band.shape[0] - 1, 1)
    if y_cut - 3 + i < y_cut:
        continue
    work[y_cut - 3 + i, x0:x1] = np.clip(
        work[y_cut - 3 + i, x0:x1].astype(np.float32) * (1 - t) + grass_cut[0] * t,
        0,
        255,
    ).astype(np.uint8)

ball_after = roof_pct(work, BALLROOM_ROI)
print(f"  ballroom after roof%: {ball_after:.2f}")

# 2) Pond spur mask
px0, py0, px1, py1 = POND_ROI
pond_roi = work[py0:py1, px0:px1].copy()
hsv = cv2.cvtColor(pond_roi, cv2.COLOR_RGB2HSV)
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
tan = ((h >= 10) & (h <= 40) & (s >= 20) & (s <= 120) & (v >= 120) & (v <= 220)).astype(np.uint8) * 255
rgbf = pond_roi.astype(np.float32)
b_rel = (rgbf[..., 0] + rgbf[..., 1]) / 2.0 - rgbf[..., 2]
tan2 = ((b_rel > 15) & (v >= 110) & (s >= 15)).astype(np.uint8) * 255
tan = cv2.bitwise_or(tan, tan2)
tan = cv2.morphologyEx(tan, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

num, labels, stats, centroids = cv2.connectedComponentsWithStats(tan, connectivity=8)
spur = np.zeros_like(tan)
for i in range(1, num):
    x, y, w, h, area = stats[i]
    cx, cy = centroids[i]
    # leftward / upper-left toward pond (smaller x in region)
    if area < 25 or area > 2500:
        continue
    if cx < (px1 - px0) * 0.55:
        spur[labels == i] = 255

if spur.sum() < 300:
    spur = np.zeros((py1 - py0, px1 - px0), np.uint8)
    poly = np.array([[130 - px0, 500 - py0], [155 - px0, 490 - py0], [170 - px0, 510 - py0], [145 - px0, 530 - py0], [120 - px0, 520 - py0]], np.int32)
    cv2.fillPoly(spur, [poly], 255)

full_spur = np.zeros(work.shape[:2], np.uint8)
full_spur[py0:py1, px0:px1] = spur
cv2.imwrite(str(EDIT / "mask-pond-spur.png"), full_spur)

grass_src = work[530:570, 170:220]
gh, gw = py1 - py0, px1 - px0
grass = cv2.resize(grass_src, (gw, gh), interpolation=cv2.INTER_LANCZOS4)
m = cv2.GaussianBlur(spur.astype(np.float32) / 255.0, (11, 11), 4)[..., None]
work[py0:py1, px0:px1] = np.clip(
    work[py0:py1, px0:px1].astype(np.float32) * (1 - m) + grass.astype(np.float32) * m,
    0,
    255,
).astype(np.uint8)

pond_tan_after = tan_pct(work, POND_ROI)
print(f"  pond tan% after: {pond_tan_before:.2f} -> {pond_tan_after:.2f}")

# 3) Pin ghosts optional telea
pin_mask = np.zeros(work.shape[:2], np.uint8)
for cx, cy, r in [(452, 592, 16), (470, 608, 14), (488, 578, 12)]:
    x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
    roi = work[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    g = ((hh >= 45) & (hh <= 95) & (ss > 100) & (vv > 140)).astype(np.uint8) * 255
    if g.sum() > 250:
        pin_mask[y0:y1, x0:x1] = cv2.max(pin_mask[y0:y1, x0:x1], g)

pin_note = "skipped"
if pin_mask.sum() > 400:
    wb = cv2.cvtColor(work, cv2.COLOR_RGB2BGR)
    wb = cv2.inpaint(wb, pin_mask, 3, cv2.INPAINT_TELEA)
    work = cv2.cvtColor(wb, cv2.COLOR_BGR2RGB)
    cv2.imwrite(str(EDIT / "mask-pin-ghosts-pass2.png"), pin_mask)
    pin_note = f"telea inpaint pixels={int((pin_mask>0).sum())}"
print(f"  pin ghosts: {pin_note}")

# 4) Groom verify / restore
gx0, gy0, gx1, gy1 = GROOM
groom_diff = np.abs(work[gy0:gy1, gx0:gx1].astype(np.int16) - work_r2[gy0:gy1, gx0:gx1].astype(np.int16)).mean()
print(f"  groom mean abs diff vs work-r2-only: {groom_diff:.3f}")
if groom_diff > 2.0:
    work[gy0:gy1, gx0:gx1] = work_r2[gy0:gy1, gx0:gx1]
    print("  groom restored from work-r2-only")
else:
    print("  groom OK (no restore)")

# cluster unsharp mild
roi = work[by0:by1, bx0:bx1]
blur = cv2.GaussianBlur(roi, (0, 0), 1.0)
work[by0:by1, bx0:bx1] = np.clip(roi.astype(np.float32) + 0.2 * (roi.astype(np.float32) - blur.astype(np.float32)), 0, 255).astype(np.uint8)

# ship
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

print("\n=== AFTER METRICS ===")
print(f"  ballroom roof%: {roof_pct(work, BALLROOM_ROI):.2f}")
print(f"  pond tan%: {tan_pct(work, POND_ROI):.2f}")
print(f"  groom mean abs diff vs work-r2-only: {np.abs(work[gy0:gy1, gx0:gx1].astype(np.int16)-work_r2[gy0:gy1, gx0:gx1].astype(np.int16)).mean():.3f}")
print("\n=== FILES ===")
for p in [EDIT / "work-pass2.png", final_full, final_cluster, LIVE, RESUME_R, EDIT / "qa-before-after.png", R_BASE]:
    print(f"  {p.name}: {p.stat().st_size} bytes")
print(f"  live==resume-r: {LIVE.stat().st_size == RESUME_R.stat().st_size}")
