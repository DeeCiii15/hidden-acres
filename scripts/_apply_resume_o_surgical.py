"""Surgical resume-o edits on sharp resume-j: widen ballroom hall, nudge groom north."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(r"C:\dev\hidden-acres")
MAPS = ROOT / "public" / "maps"
BASE_PATH = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-j.png"
LIVE_PATH = MAPS / "hidden-acres-grounds-illustrated.png"
OUT_RESUME_O = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-o.png"
PRE_OVERWRITE = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-o-pre-live.png"
QA = MAPS / "_qa-crops-resume-o"

BALL_BOX = (400, 940, 610, 1400)
BALL_SCALE_X = 1.16
BALL_CENTER_X = 502
BALL_END_FADE = 64
HALL_CORE = (438, 1005, 568, 1360)

GROOM_BOX = (372, 860, 478, 1005)
GROOM_SHIFT = 18
GROOM_CORE = (380, 872, 468, 988)

rng = np.random.default_rng(42)


def is_building_rgb(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    green = (g > r + 12) & (g > b + 8) & (g > 55)
    warm = (r > 90) & (r < 210) & (r > g + 10) & (r > b + 15) & (g < 170) & (b < 140)
    lum = (r.astype(np.int32) + g + b) / 3.0
    mx = np.maximum(np.maximum(r, g), b).astype(np.float32)
    mn = np.minimum(np.minimum(r, g), b).astype(np.float32)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0.0)
    wall = (
        (lum > 150)
        & (sat < 0.35)
        & (r > 140)
        & (g > 130)
        & (b > 100)
        & ~((g > r + 5) & (g > b + 5))
    )
    eave = (lum < 95) & (lum > 25) & (r >= g - 5) & (g < 110) & ~((g > r + 8) & (g > b + 5))
    return ((warm | wall | eave) & ~green).astype(np.uint8)


def soft_rect_alpha(
    h: int, w: int, rect: tuple[int, int, int, int], feather: float, end_fade: int = 0
) -> np.ndarray:
    x0, y0, x1, y1 = rect
    m = np.zeros((h, w), np.float32)
    m[max(0, y0) : min(h, y1), max(0, x0) : min(w, x1)] = 1.0
    k = max(3, int(feather * 2) | 1)
    m = cv2.GaussianBlur(m, (k, k), feather)
    m = np.clip(m * 1.25, 0, 1)
    if end_fade > 0:
        fade = np.ones(h, dtype=np.float32)
        for i in range(end_fade):
            t = (i + 1) / end_fade
            fade[i] = t * t * t
            fade[h - 1 - i] = t * t * t
        m *= fade[:, None]
    return m


def widen_ballroom(work: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x0, y0, x1, y1 = BALL_BOX
    crop = work[y0:y1, x0:x1].copy()
    h, w = crop.shape[:2]

    hx0, hy0, hx1, hy1 = HALL_CORE
    rect = (hx0 - x0 - 10, hy0 - y0, hx1 - x0 + 10, hy1 - y0)
    geo = soft_rect_alpha(h, w, rect, feather=9, end_fade=BALL_END_FADE)

    bld = is_building_rgb(crop).astype(np.float32)
    bld = cv2.dilate(bld, np.ones((9, 9), np.uint8), iterations=1)
    bld = cv2.GaussianBlur(bld, (0, 0), 2.0)
    # Hard mid-body paste so widen sticks; geo dominates
    alpha = np.clip(geo * np.maximum(bld, 0.85), 0, 1)

    # Protect Groom's Quarters footprint after north nudge — do not smear it
    gx0, gy0, gx1, gy1 = GROOM_BOX
    gy0, gy1 = gy0 - GROOM_SHIFT, gy1 - GROOM_SHIFT
    px0, py0 = max(0, gx0 - x0 - 8), max(0, gy0 - y0 - 8)
    px1, py1 = min(w, gx1 - x0 + 8), min(h, gy1 - y0 + 8)
    if px1 > px0 and py1 > py0:
        protect = np.zeros((h, w), np.float32)
        protect[py0:py1, px0:px1] = 1.0
        protect = cv2.GaussianBlur(protect, (0, 0), 4.0)
        alpha *= 1.0 - np.clip(protect, 0, 1)

    new_w = int(round(w * BALL_SCALE_X))
    scaled = cv2.resize(crop, (new_w, h), interpolation=cv2.INTER_LANCZOS4)
    alpha_s = np.clip(cv2.resize(alpha, (new_w, h), interpolation=cv2.INTER_LINEAR), 0, 1)

    paste_x0 = int(round(BALL_CENTER_X - new_w / 2))
    paste_y0 = y0
    H, W = work.shape[:2]
    paste_x1, paste_y1 = paste_x0 + new_w, paste_y0 + h

    sx0 = max(0, -paste_x0)
    sy0 = max(0, -paste_y0)
    sx1 = new_w - max(0, paste_x1 - W)
    sy1 = h - max(0, paste_y1 - H)
    dx0, dy0 = max(0, paste_x0), max(0, paste_y0)

    out = work.copy()
    wrote = np.zeros((H, W), dtype=bool)
    patch = scaled[sy0:sy1, sx0:sx1].astype(np.float32)
    a = alpha_s[sy0:sy1, sx0:sx1]
    dest = out[dy0 : dy0 + (sy1 - sy0), dx0 : dx0 + (sx1 - sx0)].astype(np.float32)
    blended = dest * (1.0 - a[..., None]) + patch * a[..., None]
    out[dy0 : dy0 + (sy1 - sy0), dx0 : dx0 + (sx1 - sx0)] = np.clip(blended, 0, 255).astype(np.uint8)
    wrote[dy0 : dy0 + (sy1 - sy0), dx0 : dx0 + (sx1 - sx0)] |= a > 1e-4
    return out, wrote


def soft_rect_mask_u8(h: int, w: int, feather: int = 10) -> np.ndarray:
    m = np.zeros((h, w), np.float32)
    f = max(1, feather)
    m[f : h - f, f : w - f] = 1.0
    m = cv2.GaussianBlur(m, (0, 0), feather * 0.85)
    return np.clip(m, 0, 1)


def clone_fill_box(dst: np.ndarray, box: tuple[int, int, int, int], feather: int = 16) -> None:
    """Fill box by blending nearby left/right samples (refine5-style)."""
    H, W = dst.shape[:2]
    x0, y0, x1, y1 = box
    sw, sh = x1 - x0, y1 - y0
    if sw <= 0 or sh <= 0:
        return
    sx0 = max(0, x0 - sw - 20)
    sy0 = max(0, y0 - 8)
    sample = dst[sy0 : sy0 + sh, sx0 : sx0 + sw]
    sx1 = min(W - sw, x1 + 12)
    sample2 = dst[sy0 : sy0 + sh, sx1 : sx1 + sw]
    if sample.shape[:2] != (sh, sw):
        sample = cv2.resize(sample, (sw, sh), interpolation=cv2.INTER_LINEAR)
    if sample2.shape[:2] != (sh, sw):
        sample2 = cv2.resize(sample2, (sw, sh), interpolation=cv2.INTER_LINEAR)
    blended = (0.55 * sample.astype(np.float32) + 0.45 * sample2.astype(np.float32))
    blended = cv2.GaussianBlur(np.clip(blended, 0, 255).astype(np.uint8), (0, 0), 1.1)
    alpha = soft_rect_mask_u8(sh, sw, feather=feather)
    dest = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = np.clip(
        dest * (1 - alpha[..., None]) + blended.astype(np.float32) * alpha[..., None],
        0,
        255,
    ).astype(np.uint8)


def move_groom_north(work: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Subtle north nudge: hard-shift building pixels; clone-fill only vacated south strip."""
    x0, y0, x1, y1 = GROOM_BOX
    shift = GROOM_SHIFT
    H, W = work.shape[:2]
    wrote = np.zeros((H, W), dtype=bool)
    ny0 = y0 - shift
    if ny0 < 0:
        return work, wrote

    crop = work[y0:y1, x0:x1].copy()
    hh, ww = crop.shape[:2]
    r, g, b = (crop[..., i].astype(np.int16) for i in range(3))
    lum = (r.astype(np.int32) + g + b) / 3.0
    roof = (r > 90) & (r < 200) & (r > g + 10) & (r > b + 18) & (g < 160) & (b < 135)
    wall = (r > 115) & (g > 100) & (b > 75) & (lum > 110) & (r < 215) & ~((g > r + 8) & (g > b + 5))
    steps = (
        (lum > 120)
        & (lum < 200)
        & (np.abs(r.astype(np.int16) - g) < 28)
        & (np.abs(g.astype(np.int16) - b) < 32)
    )
    bush = (g > r + 5) & (g > b + 3) & (g > 55) & (g < 170) & (r < 145)
    pin = (g > 35) & (g < 115) & (r < 75) & (b < 75) & (g > r + 12) & (g > b + 8)

    gx0, gy0, gx1, gy1 = GROOM_CORE
    env = np.zeros((hh, ww), np.uint8)
    env[
        max(0, gy0 - y0 - 4) : min(hh, gy1 - y0 + 22),
        max(0, gx0 - x0 - 4) : min(ww, gx1 - x0 + 4),
    ] = 1
    env = cv2.dilate(env, np.ones((9, 9), np.uint8), iterations=1)

    hard = ((roof | wall | steps | pin) & (env > 0)).astype(np.uint8)
    near = cv2.dilate(hard, np.ones((7, 7), np.uint8), iterations=1)
    plant = (bush & (near > 0) & (env > 0)).astype(np.uint8)
    alpha_u8 = np.maximum(hard, plant)
    alpha_u8 = cv2.dilate(alpha_u8, np.ones((3, 3), np.uint8), iterations=1)
    alpha = cv2.GaussianBlur(alpha_u8.astype(np.float32), (0, 0), 1.2)
    alpha = np.where(hard > 0, np.maximum(alpha, 0.92), alpha)
    alpha = np.clip(alpha, 0, 1)

    out = work.copy()

    # Vacated = old alpha footprint; fill ONLY those pixels (before paste) via left/right clone
    old_mask = np.zeros((H, W), np.uint8)
    old_mask[y0:y1, x0:x1] = (alpha > 0.28).astype(np.uint8) * 255
    old_mask[:, :345] = 0
    old_mask[:, 500:] = 0
    ys, xs = np.where(old_mask > 0)
    if len(ys):
        by0, by1 = int(ys.min()), int(ys.max()) + 1
        bx0, bx1 = int(xs.min()), int(xs.max()) + 1
        clone_fill_box(out, (bx0, by0, bx1, by1), feather=12)
        # Restore non-mask pixels inside the box (clone_fill is soft-rect; keep outside alpha)
        keep = work[by0:by1, bx0:bx1]
        local = old_mask[by0:by1, bx0:bx1].astype(np.float32) / 255.0
        local = cv2.GaussianBlur(local, (0, 0), 1.5)
        filled = out[by0:by1, bx0:bx1].astype(np.float32)
        out[by0:by1, bx0:bx1] = np.clip(
            keep.astype(np.float32) * (1 - local[..., None]) + filled * local[..., None],
            0,
            255,
        ).astype(np.uint8)

    # Paste sharp building north
    dest = out[ny0 : ny0 + hh, x0:x1].astype(np.float32)
    out[ny0 : ny0 + hh, x0:x1] = np.clip(
        dest * (1 - alpha[..., None]) + crop.astype(np.float32) * alpha[..., None],
        0,
        255,
    ).astype(np.uint8)

    region = np.zeros((H, W), dtype=bool)
    region[max(0, ny0 - 2) : min(H, y1 + 2), max(0, x0 - 2) : min(W, x1 + 2)] = True
    diff = np.any(np.abs(out.astype(np.int16) - work.astype(np.int16)) > 1, axis=-1) & region
    wrote |= diff
    result = work.copy()
    result[wrote] = out[wrote]
    return result, wrote


def roof_mask(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (r > 100) & (r < 195) & (r > g + 14) & (r > b + 22) & (g < 150) & (b < 125)


def largest_run(row, x_lo, x_hi, contain_x=505, gap=4):
    xs = np.where(row[x_lo:x_hi])[0] + x_lo
    if len(xs) == 0:
        return None
    segs, s, prev = [], int(xs[0]), int(xs[0])
    for x in xs[1:]:
        x = int(x)
        if x - prev <= gap:
            prev = x
        else:
            segs.append((s, prev))
            s = prev = x
    segs.append((s, prev))
    core = [t for t in segs if t[0] <= contain_x <= t[1]]
    pick = max(core or segs, key=lambda t: t[1] - t[0])
    return pick[0], pick[1], pick[1] - pick[0] + 1


def ballroom_widths(rgb: np.ndarray, label: str, x_lo: int = 440, x_hi: int = 575) -> list[tuple]:
    """Largest roof run containing ridge x~505 (hall body, not courtyard blobs)."""
    roof = roof_mask(rgb)
    scan_ys = [1040, 1080, 1120, 1240, 1280, 1320]
    rows = []
    print(f"\n=== Ballroom hall roof run ({label}) ===")
    print(f"{'y':>6} {'x0':>6} {'x1':>6} {'width':>6}")
    for y in scan_ys:
        pick = largest_run(roof[y], x_lo, x_hi, contain_x=505, gap=4)
        if pick is None:
            rows.append((y, None, None, None))
            print(f"{y:6d} n/a")
            continue
        lo, hi, ww = pick
        rows.append((y, lo, hi, ww))
        print(f"{y:6d} {lo:6d} {hi:6d} {ww:6d}")
    return rows


def groom_centroid(rgb: np.ndarray) -> tuple[float, float, int]:
    roof = roof_mask(rgb)
    ys, xs = np.where(roof[845:985, 378:462])
    if len(ys) == 0:
        return float("nan"), float("nan"), 0
    return float(xs.mean() + 378), float(ys.mean() + 845), int(len(ys))


def forest_laplacian(rgb: np.ndarray) -> float:
    gray = cv2.cvtColor(rgb[50:200, 50:200], cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def side_by_side(a: np.ndarray, b: np.ndarray, box: tuple[int, int, int, int], path: Path) -> None:
    x0, y0, x1, y1 = box
    ca, cb = a[y0:y1, x0:x1], b[y0:y1, x0:x1]
    gap = np.full((ca.shape[0], 8, 3), 240, dtype=np.uint8)
    Image.fromarray(np.concatenate([ca, gap, cb], axis=1)).save(path)


def main() -> None:
    assert BASE_PATH.exists(), BASE_PATH
    base = np.array(Image.open(BASE_PATH).convert("RGB"))
    assert base.shape[:2] == (1536, 1024), base.shape

    if LIVE_PATH.exists():
        Image.open(LIVE_PATH).convert("RGB").save(PRE_OVERWRITE, quality=95)
        print(f"saved pre-live backup -> {PRE_OVERWRITE}")

    # Groom first (protects cottage), then widen ballroom with groom footprint masked out
    work, wrote_g = move_groom_north(base.copy())
    work, wrote_b = widen_ballroom(work)
    wrote = wrote_b | wrote_g

    out = base.copy()
    out[wrote] = work[wrote]
    work = out

    rj = ballroom_widths(base, "resume-j", x_lo=440, x_hi=575)
    ro = ballroom_widths(work, "resume-o", x_lo=430, x_hi=595)
    wsj = [r[3] for r in rj if r[3] is not None]
    wso = [r[3] for r in ro if r[3] is not None]
    avg_j, avg_o = float(np.mean(wsj)), float(np.mean(wso))
    print(f"\nAVG roof span j={avg_j:.1f}  o={avg_o:.1f}  delta={avg_o - avg_j:+.1f}px")

    cxj, cyj, nj = groom_centroid(base)
    cxo, cyo, no = groom_centroid(work)
    print(f"\n=== Groom roof centroid ===")
    print(f"j: cx={cxj:.1f} cy={cyj:.1f} n={nj}")
    print(f"o: cx={cxo:.1f} cy={cyo:.1f} n={no}")
    print(f"dcy(o-j)={cyo - cyj:+.1f}  north_by={max(0.0, cyj - cyo):.1f}px")

    lap_j = forest_laplacian(base)
    lap_o = forest_laplacian(work)
    print(f"\nForest laplacian j={lap_j:.2f} o={lap_o:.2f} match={abs(lap_j - lap_o) < 1e-9}")

    outside = ~wrote
    diff_out = (
        int(np.abs(base.astype(np.int16) - work.astype(np.int16))[outside].max()) if outside.any() else 0
    )
    print(f"Max absdiff outside edit mask: {diff_out} (want 0)")
    print(f"Edit mask pixels: {int(wrote.sum())}")

    Image.fromarray(work).save(OUT_RESUME_O, quality=95)
    Image.fromarray(work).save(LIVE_PATH, quality=95)
    print(f"\nsaved {OUT_RESUME_O}")
    print(f"saved {LIVE_PATH}")

    QA.mkdir(parents=True, exist_ok=True)
    Image.fromarray(work[960:1400, 390:620]).save(QA / "o-ballroom.png")
    Image.fromarray(work[840:1020, 350:510]).save(QA / "o-groom.png")
    Image.fromarray(work[820:1420, 300:700]).save(QA / "o-cluster.png")
    side_by_side(base, work, (390, 960, 620, 1400), QA / "cmp-ballroom.png")
    side_by_side(base, work, (350, 840, 510, 1020), QA / "cmp-groom.png")
    print(f"QA crops -> {QA}")

    print("\n========== VERDICT ==========")
    print(f"Ballroom wider? {'YES' if avg_o > avg_j + 12 else 'NO'} (delta {avg_o - avg_j:+.1f})")
    print(f"Groom north? {'YES' if (cyj - cyo) >= 7 else 'NO'} (north_by {cyj - cyo:.1f})")
    print(f"Forest sharp match? {'YES' if abs(lap_j - lap_o) < 1e-9 else 'NO'}")


if __name__ == "__main__":
    main()
