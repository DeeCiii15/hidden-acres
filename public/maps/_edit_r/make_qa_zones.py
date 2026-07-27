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

R_BASE = ROOT / "hidden-acres-grounds-illustrated-v-map-resume-r-base.png"
LIVE = ROOT / "hidden-acres-grounds-illustrated.png"
R5_SRC = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets\cluster-fix-r5.png")

bbox = json.loads((EDIT / "bbox.json").read_text(encoding="utf-8"))
x0, y0, x1, y1 = bbox["x0"], bbox["y0"], bbox["x1"], bbox["y1"]
cw, ch = x1 - x0, y1 - y0


def load_rgb(p):
    return Image.open(p).convert("RGB")


def feather_ellipse(h, w, feather=20.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    rx, ry = max(w / 2.0 - 2, 1), max(h / 2.0 - 2, 1)
    norm = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    mask = np.clip(1.15 - norm, 0, 1)
    k = int(max(3, feather * 2 + 1)) | 1
    mask = cv2.GaussianBlur(mask, (k, k), feather / 2.5)
    return np.clip(mask, 0, 1)


def paste_feather(base_img, patch_img, bx0, by0, feather=20):
    base = np.asarray(base_img, dtype=np.float32)
    patch = np.asarray(patch_img, dtype=np.float32)
    h, w = patch.shape[:2]
    m = feather_ellipse(h, w, feather)[..., None]
    roi = base[by0 : by0 + h, bx0 : bx0 + w]
    base[by0 : by0 + h, bx0 : bx0 + w] = np.clip(roi * (1 - m) + patch * m, 0, 255)
    return Image.fromarray(base.astype(np.uint8))


shutil.copy2(R5_SRC, EDIT / "cluster-fix-r5.png")
r5 = load_rgb(EDIT / "cluster-fix-r5.png").resize((cw, ch), Image.Resampling.LANCZOS)
r5.save(EDIT / "cluster-fix-r5-resized.png")
candidate = paste_feather(load_rgb(R_BASE), r5, x0, y0, feather=20)
candidate_path = EDIT / "candidate-r5-full.png"
candidate.save(candidate_path)
candidate.save(EDIT / "candidate-r5-full-alt.png")

sources = {"base": load_rgb(R_BASE), "live": load_rgb(LIVE), "r5": candidate}

zones = {
    "pond_fork": (90, 450, 240, 560),
    "groom_west": (180, 500, 340, 640),
    "bridal_east": (380, 520, 540, 780),
    "ballroom_south": (250, 780, 400, 930),
    "courtyard_center": (280, 520, 450, 680),
}

for zname, (zx0, zy0, zx1, zy1) in zones.items():
    prefix = "courtyard" if zname == "courtyard_center" else zname
    for key, img in sources.items():
        out = QA / f"{prefix}_{key}.png"
        img.crop((zx0, zy0, zx1, zy1)).save(out, optimize=True)
    b = sources["base"].crop((zx0, zy0, zx1, zy1))
    l = sources["live"].crop((zx0, zy0, zx1, zy1))
    w, h = b.size
    cmp = Image.new("RGB", (w * 2, h))
    cmp.paste(b, (0, 0))
    cmp.paste(l, (w, 0))
    cmp.save(QA / f"{prefix}_compare.png", optimize=True)

print("=== QA ZONE CROPS ===")
print(f"candidate-r5-full: {candidate_path} ({candidate_path.stat().st_size} bytes)")
print(f"alternate: {EDIT / 'candidate-r5-full-alt.png'}")
print(f"qa dir: {QA}")
print()
for p in sorted(QA.glob("*.png")):
    im = Image.open(p)
    print(f"  {p.name}  {im.size[0]}x{im.size[1]}  {p.stat().st_size} bytes")
print()
print("Total qa_zones png:", len(list(QA.glob("*.png"))))
print("Live unchanged bytes:", LIVE.stat().st_size)
