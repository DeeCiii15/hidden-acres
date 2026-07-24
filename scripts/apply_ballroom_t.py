"""Widen Ballroom stem a little; expand north tip into a capital-T crossbar.

Uses real Ballroom roof pixels (X-scale tip band + stem body). Outside the
edit mask the map is pixel-identical to the source.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public" / "maps"
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")

SRC = (
    ASSETS
    / "c__Users_livingt_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-4190aa79-eb92-4f3e-937e-a90fea20e0d6.png"
)
OUT_SMALL = MAPS / "hidden-acres-grounds-illustrated-v-map-ballroom-t.png"
OUT_LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
OUT_ASSET = ASSETS / "hidden-acres-grounds-illustrated-ballroom-t.png"
QA = MAPS / "_qa-crops-ballroom-t"

STEM_CX = 368

# Stem body (below T) — slight widen
STEM_BOX = (305, 705, 435, 870)
STEM_SCALE_X = 1.13

# Tip band that becomes the T crossbar (against courtyard)
TIP_BOX = (300, 638, 440, 705)
TIP_SCALE_X = 2.18  # capital-T bar: clear left/right wings


def is_roof(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (r > 95) & (r < 200) & (r > g + 10) & (r > b + 18) & (g < 155) & (b < 130)


def is_building(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    green = (g > r + 12) & (g > b + 8) & (g > 55)
    warm = (r > 90) & (r < 215) & (r > g + 8) & (r > b + 14) & (g < 175)
    lum = (r.astype(np.int32) + g + b) / 3.0
    wall = (
        (lum > 125)
        & (r > 125)
        & (g > 115)
        & (b > 85)
        & ~((g > r + 5) & (g > b + 5))
    )
    eave = (lum < 100) & (lum > 28) & (r >= g - 6) & (g < 115) & ~((g > r + 8) & (g > b + 5))
    return ((is_roof(rgb) | warm | wall | eave) & ~green).astype(np.uint8)


def soft_geo(h: int, w: int, x_pad: int, y_fade_top: int, y_fade_bot: int) -> np.ndarray:
    geo = np.zeros((h, w), np.float32)
    geo[:, x_pad : w - x_pad] = 1.0
    geo = cv2.GaussianBlur(geo, (0, 0), 4.5)
    for i in range(max(1, y_fade_top)):
        geo[i, :] *= (i / y_fade_top) ** 1.3
    for i in range(max(1, y_fade_bot)):
        geo[h - 1 - i, :] *= (i / y_fade_bot) ** 1.15
    return geo


def protect_mask(H: int, W: int) -> np.ndarray:
    protect = np.zeros((H, W), dtype=bool)
    protect[500:635, 200:295] = True  # groom body (leave wing corridor)
    protect[555:700, 495:575] = True  # bridal core only (east of wing tip)
    protect[555:615, 385:435] = True  # fountain
    return protect


def xscale_band(
    work: np.ndarray,
    box: tuple[int, int, int, int],
    scale_x: float,
    center_x: int,
    *,
    x_pad: int,
    y_fade_top: int,
    y_fade_bot: int,
    bld_floor: float,
) -> tuple[np.ndarray, np.ndarray]:
    x0, y0, x1, y1 = box
    crop = work[y0:y1, x0:x1].copy()
    h, w = crop.shape[:2]
    bld = is_building(crop).astype(np.float32)
    bld = cv2.dilate(bld, np.ones((5, 5), np.uint8), iterations=1)
    bld = cv2.GaussianBlur(bld, (0, 0), 1.3)

    geo = soft_geo(h, w, x_pad=x_pad, y_fade_top=y_fade_top, y_fade_bot=y_fade_bot)
    alpha = np.clip(geo * np.maximum(bld, bld_floor), 0, 1)

    new_w = int(round(w * scale_x))
    scaled = cv2.resize(crop, (new_w, h), interpolation=cv2.INTER_LANCZOS4)
    alpha_s = np.clip(cv2.resize(alpha, (new_w, h), interpolation=cv2.INTER_LINEAR), 0, 1)

    paste_x0 = int(round(center_x - new_w / 2))
    H, W = work.shape[:2]
    protect = protect_mask(H, W)
    out = work.copy()
    wrote = np.zeros((H, W), dtype=bool)

    for yy in range(h):
        for xx in range(new_w):
            a = float(alpha_s[yy, xx])
            if a < 0.05:
                continue
            dx = paste_x0 + xx
            dy = y0 + yy
            if dx < 0 or dx >= W or dy < 0 or dy >= H or protect[dy, dx]:
                continue
            out[dy, dx] = np.clip(
                (1 - a) * out[dy, dx].astype(np.float32) + a * scaled[yy, xx].astype(np.float32),
                0,
                255,
            ).astype(np.uint8)
            wrote[dy, dx] = True

    result = work.copy()
    result[wrote] = out[wrote]
    return result, wrote


def stem_edges_at(rgb: np.ndarray, y: int) -> tuple[int, int] | None:
    roof = is_roof(rgb)
    xs = np.where(roof[y, 290:460])[0] + 290
    if len(xs) < 12:
        return None
    segs, s, prev = [], int(xs[0]), int(xs[0])
    for x in xs[1:]:
        x = int(x)
        if x - prev <= 3:
            prev = x
        else:
            segs.append((s, prev))
            s = prev = x
    segs.append((s, prev))
    core = [t for t in segs if t[0] <= STEM_CX <= t[1]]
    pick = max(core or segs, key=lambda t: t[1] - t[0])
    if pick[1] - pick[0] < 36:
        return None
    return pick[0], pick[1]


def roof_run(rgb: np.ndarray, y: int) -> tuple[int, int, int] | None:
    e = stem_edges_at(rgb, y)
    if e is None:
        return None
    return e[0], e[1], e[1] - e[0] + 1


def main() -> None:
    assert SRC.exists(), SRC
    base = np.array(Image.open(SRC).convert("RGB"))
    assert base.shape[:2] == (1024, 682), base.shape

    # 1) Capital-T crossbar from tip band
    work, wrote_t = xscale_band(
        base.copy(),
        TIP_BOX,
        TIP_SCALE_X,
        STEM_CX,
        x_pad=10,
        y_fade_top=6,
        y_fade_bot=8,
        bld_floor=0.82,
    )
    # 2) Slightly wider stem body
    work, wrote_s = xscale_band(
        work,
        STEM_BOX,
        STEM_SCALE_X,
        STEM_CX,
        x_pad=14,
        y_fade_top=12,
        y_fade_bot=10,
        bld_floor=0.78,
    )
    wrote = wrote_t | wrote_s
    out = base.copy()
    out[wrote] = work[wrote]

    print("=== Tip (T bar) ===")
    for y in (650, 665, 680, 695):
        print(f"y={y} base={roof_run(base, y)} after={roof_run(out, y)}")
    print("=== Stem ===")
    for y in (720, 760, 800):
        print(f"y={y} base={roof_run(base, y)} after={roof_run(out, y)}")

    outside = ~wrote
    max_out = (
        int(np.abs(base.astype(np.int16) - out.astype(np.int16))[outside].max())
        if outside.any()
        else 0
    )
    print(f"\nEdit pixels: {int(wrote.sum())}")
    print(f"Max absdiff outside edit mask: {max_out}")

    Image.fromarray(out).save(OUT_SMALL)
    Image.fromarray(out).save(OUT_ASSET)
    live = Image.fromarray(out).resize((1024, 1536), Image.Resampling.LANCZOS)
    live.save(OUT_LIVE)
    print(f"saved {OUT_SMALL.name}, {OUT_ASSET.name}, {OUT_LIVE.name}")

    QA.mkdir(parents=True, exist_ok=True)

    def sbs(box, name):
        x0, y0, x1, y1 = box
        ca, cb = base[y0:y1, x0:x1], out[y0:y1, x0:x1]
        gap = np.full((ca.shape[0], 6, 3), 240, np.uint8)
        Image.fromarray(np.concatenate([ca, gap, cb], 1)).save(QA / name)

    Image.fromarray(out[540:880, 240:500]).save(QA / "ballroom.png")
    Image.fromarray(out[560:720, 250:480]).save(QA / "north-tip.png")
    sbs((240, 540, 500, 880), "cmp-ballroom.png")
    sbs((250, 560, 480, 720), "cmp-north-tip.png")
    Image.fromarray((wrote.astype(np.uint8) * 255)).save(QA / "edit-mask.png")

    # Silhouette for QA
    y0, y1, x0, x1 = 620, 900, 250, 500
    sil = np.full((y1 - y0, x1 - x0, 3), (28, 55, 36), np.uint8)
    sil[is_roof(out[y0:y1, x0:x1])] = (176, 92, 52)
    Image.fromarray(sil).save(QA / "silhouette.png")
    Image.fromarray(sil).save(ASSETS / "_silhouette-ballroom-t.png")
    Image.fromarray(out[560:720, 250:480]).save(ASSETS / "_qa-tip-final.png")
    sbs((250, 560, 480, 720), "cmp-north-tip.png")
    Image.open(QA / "cmp-north-tip.png").save(ASSETS / "_qa-cmp-tip-final.png")

    tb = [roof_run(base, y)[2] for y in (650, 665, 680) if roof_run(base, y)]
    ta = [roof_run(out, y)[2] for y in (650, 665, 680) if roof_run(out, y)]
    sb = [roof_run(base, y)[2] for y in (720,) if roof_run(base, y)]
    sa = [roof_run(out, y)[2] for y in (720,) if roof_run(out, y)]
    print("\n========== VERDICT ==========")
    print(
        f"T bar wider? {'YES' if np.mean(ta) > np.mean(tb) + 25 else 'NO'} "
        f"({np.mean(tb):.1f}->{np.mean(ta):.1f})"
    )
    print(
        f"Stem wider? {'YES' if np.mean(sa) > np.mean(sb) + 4 else 'NO'} "
        f"({np.mean(sb):.1f}->{np.mean(sa):.1f})"
    )
    print(f"Exterior identical? {'YES' if max_out == 0 else 'NO'}")


if __name__ == "__main__":
    main()
