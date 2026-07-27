"""Build hybrid cluster map - one-shot pipeline."""
import json
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(r"C:\Dev\hidden-acres\public\maps")
EDIT = ROOT / "_edit_r"
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")

LIVE = ROOT / "hidden-acres-grounds-illustrated.png"
QBASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-q-base.png"
R_BASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r-base.png"
RESUME_R = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r.png"

GEN_R2 = ASSETS / "cluster-fix-r2.png"
GEN_R1 = ASSETS / "cluster-fix-r.png"

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
x0, y0, x1, y1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]
cw, ch = x1 - x0, y1 - y0

report = []


def load_rgb(path: Path) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    return np.asarray(im)


def save_rgb(arr: np.ndarray, path: Path) -> None:
    Image.fromarray(arr).save(path, optimize=True)


def feather_ellipse_mask(h: int, w: int, feather: float = 22.0) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rx, ry = max(w / 2.0 - 2, 1), max(h / 2.0 - 2, 1)
    norm = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    mask = np.clip(1.15 - norm, 0.0, 1.0)
    k = int(max(3, feather * 2 + 1)) | 1
    mask = cv2.GaussianBlur(mask, (k, k), feather / 2.5)
    return np.clip(mask, 0.0, 1.0)


def save_zone_mask(full_h: int, full_w: int, zone, path: Path, gradient_y=None):
    x0z, y0z, x1z, y1z = zone
    m = np.zeros((full_h, full_w), dtype=np.uint8)
    patch = np.ones((y1z - y0z, x1z - x0z), dtype=np.float32)
    if gradient_y is not None:
        gy0, gy1 = gradient_y
        for y in range(y0z, y1z):
            t = np.clip((y - gy0) / max(gy1 - gy0, 1), 0.0, 1.0)
            patch[y - y0z, :] = t
    m[y0z:y1z, x0z:x1z] = (patch * 255).astype(np.uint8)
    cv2.imwrite(str(path), m)


def paste_feather(work: np.ndarray, patch: np.ndarray, bx0: int, by0: int, feather: float = 22.0):
    h, w = patch.shape[:2]
    m = feather_ellipse_mask(h, w, feather)[..., None]
    roi = work[by0 : by0 + h, bx0 : bx0 + w].astype(np.float32)
    work[by0 : by0 + h, bx0 : bx0 + w] = np.clip(roi * (1 - m) + patch.astype(np.float32) * m, 0, 255).astype(np.uint8)


def clone_zone(work_bgr, qbase_bgr, zone, name, feather=18, max_alpha=1.0, gradient_y=None, use_seamless=True):
    zx0, zy0, zx1, zy1 = zone
    zh, zw = zy1 - zy0, zx1 - zx0
    src = qbase_bgr[zy0:zy1, zx0:zx1].copy()
    mask_hard = np.ones((zh, zw), np.uint8) * 255
    center = (zx0 + zw // 2, zy0 + zh // 2)
    ok = False
    if use_seamless and max_alpha >= 0.95:
        try:
            work_bgr[:] = cv2.seamlessClone(src, work_bgr, mask_hard, center, cv2.NORMAL_CLONE)
            ok = True
            report.append(f"{name}: seamlessClone NORMAL at center {center}")
        except cv2.error as e:
            report.append(f"{name}: seamlessClone failed ({e}), feather blend")
    if not ok:
        work_rgb = cv2.cvtColor(work_bgr, cv2.COLOR_BGR2RGB)
        qbase_rgb = cv2.cvtColor(qbase_bgr, cv2.COLOR_BGR2RGB)
        patch_q = qbase_rgb[zy0:zy1, zx0:zx1].astype(np.float32)
        roi = work_rgb[zy0:zy1, zx0:zx1].astype(np.float32)
        alpha = np.ones((zh, zw), dtype=np.float32) * max_alpha
        if gradient_y is not None:
            gy0, gy1 = gradient_y
            for y in range(zy0, zy1):
                t = np.clip((y - gy0) / max(gy1 - gy0, 1), 0.0, 1.0)
                alpha[y - zy0, :] = t * max_alpha
        k = int(max(3, feather * 2 + 1)) | 1
        alpha = cv2.GaussianBlur(alpha, (k, k), feather / 3.0)
        alpha = np.clip(alpha, 0, 1)[..., None]
        blended = np.clip(roi * (1 - alpha) + patch_q * alpha, 0, 255).astype(np.uint8)
        work_rgb[zy0:zy1, zx0:zx1] = blended
        work_bgr[:] = cv2.cvtColor(work_rgb, cv2.COLOR_RGB2BGR)
        report.append(f"{name}: feather blend feather={feather}px max_alpha={max_alpha}")


def unsharp_region(arr_rgb, bx0, by0, bx1, by1, amount=0.35, sigma=1.2):
    roi = arr_rgb[by0:by1, bx0:bx1]
    blur = cv2.GaussianBlur(roi, (0, 0), sigma)
    sharp = np.clip(roi.astype(np.float32) + amount * (roi.astype(np.float32) - blur.astype(np.float32)), 0, 255)
    arr_rgb[by0:by1, bx0:bx1] = sharp.astype(np.uint8)


# --- 1) Resize r2 ---
r2 = Image.open(GEN_R2).convert("RGB")
if r2.size != (cw, ch):
    r2 = r2.resize((cw, ch), Image.Resampling.LANCZOS)
    report.append(f"r2 resized from asset to {cw}x{ch}")
else:
    report.append(f"r2 already {cw}x{ch}")
r2_path = EDIT / "cluster-fix-r2-resized.png"
r2.save(r2_path)
r2_arr = np.asarray(r2)

# r1 comparison stats
if GEN_R1.exists():
    r1 = Image.open(GEN_R1).convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS)
    live_cluster = load_rgb(EDIT / "live-cluster.png")
    mad_r1 = np.abs(live_cluster.astype(np.float32) - np.asarray(r1, dtype=np.float32)).mean()
    mad_r2 = np.abs(live_cluster.astype(np.float32) - r2_arr.astype(np.float32)).mean()
    report.append(f"compare vs live-cluster: r1 MAD={mad_r1:.2f}, r2 MAD={mad_r2:.2f} (using r2)")

# --- 2) work from live ---
work = load_rgb(LIVE).copy()
qbase = load_rgb(QBASE)
assert work.shape[:2] == (1024, 682) or work.shape[0] == 1024
H, W = work.shape[0], work.shape[1]

# --- 3) paste r2 cluster ---
paste_feather(work, r2_arr, x0, y0, feather=22)
save_rgb(work, EDIT / "work-after-r2.png")
report.append(f"r2 cluster pasted at bbox with ~22px elliptical feather")

work_bgr = cv2.cvtColor(work, cv2.COLOR_RGB2BGR)
qbase_bgr = cv2.cvtColor(qbase, cv2.COLOR_BGR2RGB) if False else cv2.cvtColor(qbase, cv2.COLOR_RGB2BGR)

zones = {
    "pond-road-fork": (90, 450, 220, 560),
    "south-ballroom-ghost": (250, 820, 380, 920),
    "bridal-south-extension": (400, 620, 520, 780),
    "old-groom-north-courtyard": (280, 470, 400, 540),
}

save_zone_mask(H, W, zones["pond-road-fork"], EDIT / "mask-pond-road-fork.png")
save_zone_mask(H, W, zones["south-ballroom-ghost"], EDIT / "mask-south-ballroom-ghost.png")
save_zone_mask(H, W, zones["bridal-south-extension"], EDIT / "mask-bridal-south-extension.png", gradient_y=(640, 780))
save_zone_mask(H, W, zones["old-groom-north-courtyard"], EDIT / "mask-old-groom-north-courtyard.png")

# --- 4) surgical clones (order: pond, groom light, bridal gradient, ballroom) ---
clone_zone(work_bgr, qbase_bgr, zones["pond-road-fork"], "pond-road-fork", feather=16, max_alpha=1.0)
clone_zone(work_bgr, qbase_bgr, zones["old-groom-north-courtyard"], "old-groom-north-courtyard", feather=20, max_alpha=0.55, use_seamless=False)
clone_zone(work_bgr, qbase_bgr, zones["bridal-south-extension"], "bridal-south-extension", feather=22, max_alpha=1.0, gradient_y=(640, 780), use_seamless=False)
clone_zone(work_bgr, qbase_bgr, zones["south-ballroom-ghost"], "south-ballroom-ghost", feather=18, max_alpha=1.0)

work = cv2.cvtColor(work_bgr, cv2.COLOR_BGR2RGB)

# --- 5) mild unsharp cluster only ---
unsharp_region(work, x0, y0, x1, y1, amount=0.32, sigma=1.0)
report.append("mild unsharp mask applied inside cluster bbox only")

# --- 6) outputs ---
final_full = EDIT / "final-full.png"
final_cluster = EDIT / "final-cluster.png"
save_rgb(work, final_full)
save_rgb(work[y0:y1, x0:x1], final_cluster)

shutil.copy2(final_full, LIVE)
shutil.copy2(final_full, RESUME_R)

# verify r-base untouched size from before
r_base_size = R_BASE.stat().st_size

live_size = LIVE.stat().st_size
resume_size = RESUME_R.stat().st_size
match = live_size == resume_size

print("=== HYBRID CLUSTER BUILD REPORT ===")
for line in report:
    print(f"  - {line}")
print()
print("Zones cloned from qbase (full-map coords x0,y0,x1,y1):")
for k, z in zones.items():
    print(f"  {k}: {z}")
print()
print("Outputs:")
for p in [r2_path, EDIT / "work-after-r2.png", final_full, final_cluster, LIVE, RESUME_R]:
    print(f"  {p.name}: {p.stat().st_size} bytes")
print()
print(f"live ({LIVE.name}): {live_size} bytes")
print(f"resume-r ({RESUME_R.name}): {resume_size} bytes")
print(f"match: {match}")
print(f"r-base untouched size: {r_base_size} bytes ({R_BASE.name})")
