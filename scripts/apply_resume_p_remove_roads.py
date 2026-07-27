"""Resume-p: remove two roads from sharp resume-j via coherent offset clone.

1) Chapel south / pond-north tree-grid gap road
2) Inn fork east spur toward east wood-line main road

Hard-replace stroke interiors with nearby non-road terrain (multi-offset),
feather only the fringe. Outside masks the image stays pixel-identical to j.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(r"C:\dev\hidden-acres")
MAPS = ROOT / "public" / "maps"
LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
RESUME_J = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-j.png"
BASE_P = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-p-base.png"
OUT_P = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-p.png"
QA = MAPS / "_qa-resume-p"

CHAPEL_DEST = [
    (330, 479),
    (345, 483),
    (360, 490),
    (375, 494),
    (390, 498),
    (405, 503),
    (420, 508),
    (435, 512),
    (448, 514),
]
INN_DEST = [
    (772, 229),
    (790, 230),
    (808, 228),
    (825, 223),
    (842, 214),
    (856, 200),
    (866, 184),
    (874, 168),
    (880, 152),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def densify(pts: list[tuple[int, int]], step: float = 0.7) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        dist = max(1.0, float(np.hypot(x1 - x0, y1 - y0)))
        n = max(1, int(dist / step))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    out.append((float(pts[-1][0]), float(pts[-1][1])))
    return out


def stroke_mask(h: int, w: int, pts: list[tuple[int, int]], radii: list[int]) -> np.ndarray:
    m = np.zeros((h, w), np.float32)
    dens = densify(pts, 0.65)
    max_r = max(radii)
    yy, xx = np.ogrid[-max_r : max_r + 1, -max_r : max_r + 1]
    for x, y in dens:
        ix, iy = int(round(x)), int(round(y))
        for rad in radii:
            disk = ((xx * xx + yy * yy) <= rad * rad).astype(np.float32)
            dist = np.sqrt(xx * xx + yy * yy)
            fall = np.clip(1.0 - (dist / max(rad, 1)) * 0.3, 0.7, 1.0)
            stamp = disk * fall
            y0, y1 = iy - max_r, iy + max_r + 1
            x0, x1 = ix - max_r, ix + max_r + 1
            if y0 < 0 or x0 < 0 or y1 > h or x1 > w:
                continue
            m[y0:y1, x0:x1] = np.maximum(m[y0:y1, x0:x1], stamp)
    return m


def blur01(m: np.ndarray, radius: float) -> np.ndarray:
    u8 = (np.clip(m, 0, 1) * 255).astype(np.uint8)
    return np.array(Image.fromarray(u8).filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255.0


def build_protect(base: np.ndarray) -> np.ndarray:
    h, w = base.shape[:2]
    r, g, b = (base[..., i].astype(np.int16) for i in range(3))
    tree = (g > r + 14) & (g > b + 10) & (g > 65)
    tree_core = cv2.erode(tree.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
    protect = np.zeros((h, w), np.float32)
    protect[380:465, 355:490] = 1.0
    protect[90:235, 540:690] = 1.0
    protect[:, 960:] = 1.0
    protect[:, :318] = 1.0
    for x in range(318, 334):
        protect[:, x] = np.maximum(protect[:, x], 1.0 - (x - 318) / 16.0)
    return np.maximum(protect, tree_core)


def is_roadish(img: np.ndarray) -> np.ndarray:
    r, g, b = (img[..., i] for i in range(3))
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return (lum > 130) & (r > b + 12) & (r >= g - 10) & ((r - g) < 55) & (b < 145)


def multi_offset_replace(work: np.ndarray, alpha: np.ndarray, offsets: list[tuple[int, int, float]]) -> np.ndarray:
    road = is_roadish(work)
    acc = np.zeros_like(work)
    wsum = np.zeros(alpha.shape, np.float32)
    for dx, dy, wt in offsets:
        src = np.roll(np.roll(work, dy, axis=0), dx, axis=1)
        src_rd = np.roll(np.roll(road.astype(np.float32), dy, axis=0), dx, axis=1)
        ok = (src_rd < 0.5).astype(np.float32) * wt
        acc += src * ok[..., None]
        wsum += ok
    wsum = np.maximum(wsum, 1e-3)
    filled = acc / wsum[..., None]
    hard = np.clip((alpha - 0.12) / 0.25, 0, 1)
    hard = np.clip(hard * 1.25, 0, 1)
    return work * (1.0 - hard[..., None]) + filled * hard[..., None]


def main() -> None:
    QA.mkdir(exist_ok=True)

    if sha256(LIVE) != sha256(RESUME_J):
        shutil.copy2(RESUME_J, LIVE)
        print("restored live from resume-j")
    else:
        print("live matches resume-j")

    shutil.copy2(LIVE, BASE_P)
    base = np.array(Image.open(BASE_P).convert("RGB"), dtype=np.float32)
    h, w = base.shape[:2]
    protect = build_protect(base)

    chapel_m = stroke_mask(h, w, CHAPEL_DEST, [12, 16, 19])
    inn_m = stroke_mask(h, w, INN_DEST, [11, 15, 18])
    # Keep fork bulb intact — only east spur
    inn_m[:, :765] = 0
    for x in range(765, 780):
        inn_m[:, x] *= (x - 765) / 15.0
    chapel_m *= 1.0 - protect
    inn_m *= 1.0 - protect
    chapel_m = blur01(chapel_m, 1.8)
    inn_m = blur01(inn_m, 1.8)

    work = base.copy()
    work = multi_offset_replace(
        work,
        chapel_m,
        [(12, -28, 1.2), (28, -14, 1.0), (40, 6, 0.8), (18, 26, 0.7), (-10, 24, 0.5), (50, -4, 0.6)],
    )
    grass = inn_m.copy()
    grass[:, 820:] *= 0.15
    woods = inn_m.copy()
    woods[:, :805] *= 0.12
    work = multi_offset_replace(
        work,
        grass,
        [(-48, 32, 1.2), (-58, 18, 1.0), (-35, 45, 0.85), (10, 42, 0.5), (-42, 55, 0.6), (-25, 20, 0.5)],
    )
    work = multi_offset_replace(
        work,
        woods,
        [(38, -24, 1.2), (48, -10, 1.0), (28, -42, 0.95), (55, 8, 0.5), (20, -50, 0.75), (42, -35, 0.7)],
    )
    work = work * (1.0 - protect[..., None]) + base * protect[..., None]

    union = np.maximum(chapel_m, inn_m)
    hard = np.clip((union - 0.1) / 0.25, 0, 1) * (1.0 - protect)
    hard = np.clip(hard * 1.2, 0, 1)
    out = base * (1.0 - hard[..., None]) + work * hard[..., None]
    out_u8 = np.clip(out, 0, 255).astype(np.uint8)
    base_u8 = np.clip(base, 0, 255).astype(np.uint8)
    out_u8 = np.where((hard < 0.01)[..., None], base_u8, out_u8)

    # Residual bright-tan cleanup
    r, g, b = (out_u8[..., i].astype(np.float32) for i in range(3))
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    still = (
        (lum > 145)
        & (r > b + 16)
        & (r >= g - 5)
        & ((r - g) < 50)
        & (hard > 0.25)
        & (protect < 0.4)
    )
    print("residual tan px", int(still.sum()))
    if still.sum() > 8:
        tmp = out_u8.astype(np.float32)
        for dx, dy in [(20, -26), (35, 8), (-40, 28), (45, -15), (-30, 40), (30, -40), (0, -30), (25, 20)]:
            src = np.roll(np.roll(base, dy, axis=0), dx, axis=1)
            src_l = 0.299 * src[..., 0] + 0.587 * src[..., 1] + 0.114 * src[..., 2]
            ok = (src_l < 140) | (src[..., 1] > src[..., 0] + 3)
            sel = still & ok
            tmp[sel] = src[sel]
            # refresh still
            tr, tg, tb = (tmp[..., i] for i in range(3))
            tl = 0.299 * tr + 0.587 * tg + 0.114 * tb
            still = (tl > 145) & (tr > tb + 16) & (tr >= tg - 5) & ((tr - tg) < 50) & (hard > 0.25) & (protect < 0.4)
        tmp = tmp * (1.0 - protect[..., None]) + base * protect[..., None]
        out_u8 = np.where((hard > 0.2)[..., None], np.clip(tmp, 0, 255).astype(np.uint8), out_u8)
        print("residual tan px after", int(still.sum()))

    Image.fromarray(out_u8).save(LIVE, optimize=True)
    shutil.copy2(LIVE, OUT_P)

    vis = base_u8.copy()
    a = hard[..., None]
    vis = (vis * (1 - a * 0.5) + np.array([255, 40, 40], dtype=np.float32) * (a * 0.5)).astype(np.uint8)
    Image.fromarray(vis).crop((250, 420, 520, 560)).save(QA / "mask_chapel.png")
    Image.fromarray(vis).crop((700, 120, 950, 300)).save(QA / "mask_inn.png")
    for tag, box in (("chapel", (250, 420, 520, 560)), ("inn", (700, 120, 950, 300))):
        Image.fromarray(base_u8).crop(box).save(QA / f"before_{tag}.png")
        Image.fromarray(out_u8).crop(box).save(QA / f"after_{tag}.png")
        x0, y0, x1, y1 = box
        Image.fromarray(np.concatenate([base_u8[y0:y1, x0:x1], out_u8[y0:y1, x0:x1]], axis=1)).save(
            QA / f"side_{tag}.png"
        )

    diff = np.abs(out_u8.astype(np.int16) - base_u8.astype(np.int16)).sum(axis=2)
    print("max diff outside", int(diff[hard < 0.01].max()))
    print("changed px", int((diff > 0).sum()))
    print("sha", sha256(LIVE))
    print("wrote", LIVE.name, OUT_P.name)


if __name__ == "__main__":
    main()
