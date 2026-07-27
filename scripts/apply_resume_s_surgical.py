"""Surgical resume-s edits on locked s-base (682x1024).

ONLY:
1) Widen ballroom N–S stem a little (X-scale stem body only)
2) Capital-T wings at extreme north tip (clone roof tiles)
3) Translate Groom's Quarters slightly north; fill vacated south with lawn

Rest of map stays pixel-identical to s-base.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public" / "maps"
BASE = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-s-base.png"
LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
OUT = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-s.png"
QA = MAPS / "_qa-crops-resume-s"

STEM_CX = 368
# Stem body BELOW the T crossbar
STEM_BOX = (310, 692, 430, 760)  # x0,y0,x1,y1 — widen zone
STEM_SCALE_X = 1.16  # a little wider

# Capital-T crossbar at extreme north tip only (short) — sit on tip, minimal courtyard spill
WING_Y0, WING_Y1 = 642, 672
WING_LEN_W = 24  # small west wing — narrow gap beside groom
WING_LEN_E = 40  # east has more clearance
WING_OVERLAP = 6  # overlap onto stem for seam

# Groom translate
GROOM_BOX = (215, 520, 335, 685)
GROOM_SHIFT = 32
LAWN_SAMPLE = (255, 695, 325, 745)  # grass south of groom — NOT pond

rng = np.random.default_rng(61)


def is_roof(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (r > 95) & (r < 195) & (r > g + 12) & (r > b + 20) & (g < 150) & (b < 125)


def is_pin(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (g > 50) & (g < 145) & (r < 80) & (b < 80) & (g > r + 18) & (g > b + 12)


def soft_rect(h: int, w: int, feather: float = 4.0) -> np.ndarray:
    m = np.ones((h, w), np.float32)
    f = max(1, int(feather))
    for i in range(f):
        t = (i + 1) / (f + 1)
        m[i, :] *= t
        m[h - 1 - i, :] *= t
        m[:, i] *= t
        m[:, w - 1 - i] *= t
    return cv2.GaussianBlur(m, (0, 0), feather * 0.35)


def tile_patch(src: np.ndarray, hh: int, ww: int, mirror_x: bool = False) -> np.ndarray:
    patch = src[:, ::-1].copy() if mirror_x else src.copy()
    sh, sw = patch.shape[:2]
    out = np.zeros((hh, ww, 3), np.uint8)
    for y in range(0, hh, sh):
        for x in range(0, ww, sw):
            y2, x2 = min(hh, y + sh), min(ww, x + sw)
            out[y:y2, x:x2] = patch[: y2 - y, : x2 - x]
    return out


def fill_with_lawn(dst: np.ndarray, mask: np.ndarray, lawn: np.ndarray, base: np.ndarray) -> None:
    """Fill mask using nearby base lawn pixels (prefer local neighbors), light feather."""
    H, W = dst.shape[:2]
    ys, xs = np.where(mask > 0.25)
    if len(ys) == 0:
        return
    br, bg, bb = (base[..., i].astype(np.int16) for i in range(3))
    grass = (bg > br + 6) & (bg > bb + 4) & (bg > 55) & (bg < 200)
    # exclude building-ish from donor
    warm = (br > 95) & (br < 200) & (br > bg + 10) & (br > bb + 18)
    donor = grass & ~warm & (mask < 0.15)

    fill = dst.copy().astype(np.float32)
    lh, lw = lawn.shape[:2]
    for y, x in zip(ys, xs):
        found = False
        for rad in (6, 12, 20, 32):
            y0, y1 = max(0, y - rad), min(H, y + rad + 1)
            x0, x1 = max(0, x - rad), min(W, x + rad + 1)
            local = donor[y0:y1, x0:x1]
            if not local.any():
                continue
            ly, lx = np.where(local)
            # prefer south/east donors (lawn below vacated south strip)
            scores = (ly + y0 - y) * 1.5 + np.abs(lx + x0 - x)
            # prefer positive dy (south)
            prefer = np.where(ly + y0 >= y, scores - 8, scores)
            k = int(np.argmin(prefer))
            fill[y, x] = base[ly[k] + y0, lx[k] + x0].astype(np.float32)
            found = True
            break
        if not found:
            ty = int((y * 3 + 17) % max(lh - 1, 1))
            tx = int((x * 5 + 29) % max(lw - 1, 1))
            fill[y, x] = lawn[ty, tx].astype(np.float32)

    a = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.35)
    a = np.clip(a, 0, 1)
    # lightly texture-blend fill
    fill_u8 = np.clip(fill, 0, 255).astype(np.uint8)
    fill_u8 = cv2.GaussianBlur(fill_u8, (0, 0), 0.55)
    dst[:] = np.clip(
        dst.astype(np.float32) * (1 - a[..., None]) + fill_u8.astype(np.float32) * a[..., None],
        0,
        255,
    ).astype(np.uint8)


def groom_alpha(crop: np.ndarray) -> np.ndarray:
    r, g, b = (crop[..., i].astype(np.int16) for i in range(3))
    lum = (r.astype(np.int32) + g + b) / 3.0
    roof = is_roof(crop)
    wall = (r > 115) & (g > 100) & (b > 75) & (lum > 110) & (r < 215) & ~((g > r + 8) & (g > b + 5))
    steps = (lum > 115) & (lum < 205) & (np.abs(r - g) < 30) & (np.abs(g - b) < 35) & (r > 100)
    bush = (g > r + 5) & (g > b + 3) & (g > 55) & (g < 175) & (r < 150)
    pin = is_pin(crop)
    hard = (roof | wall | steps | pin).astype(np.uint8)
    # keep bushes that touch the building
    near = cv2.dilate(hard, np.ones((9, 9), np.uint8), iterations=1)
    plant = (bush & (near > 0)).astype(np.uint8)
    a = np.maximum(hard, plant)
    a = cv2.dilate(a, np.ones((3, 3), np.uint8), iterations=1)
    # tighten: drop far-left pond pixels
    a[:, :8] = 0
    alpha = cv2.GaussianBlur(a.astype(np.float32), (0, 0), 1.0)
    alpha = np.where(hard > 0, np.maximum(alpha, 0.95), alpha)
    return np.clip(alpha, 0, 1)


def move_groom_north(work: np.ndarray, lawn: np.ndarray, base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x0, y0, x1, y1 = GROOM_BOX
    shift = GROOM_SHIFT
    H, W = work.shape[:2]
    wrote = np.zeros((H, W), dtype=bool)
    ny0 = y0 - shift
    if ny0 < 0:
        return work, wrote

    crop = work[y0:y1, x0:x1].copy()
    alpha = groom_alpha(crop)
    hh, ww = crop.shape[:2]

    out = work.copy()

    # Only fill vacated pixels (old footprint not covered by new paste)
    old = np.zeros((H, W), np.float32)
    old[y0:y1, x0:x1] = alpha
    new_cover = np.zeros((H, W), np.float32)
    new_cover[ny0 : ny0 + hh, x0:x1] = alpha
    vacated = np.clip(old - new_cover, 0, 1)
    vacated[:, 336:] = 0
    vacated[:, :205] = 0
    fill_with_lawn(out, vacated, lawn, base)

    # Paste identical building pixels north (hard where alpha high)
    dest = out[ny0 : ny0 + hh, x0:x1].astype(np.float32)
    out[ny0 : ny0 + hh, x0:x1] = np.clip(
        dest * (1 - alpha[..., None]) + crop.astype(np.float32) * alpha[..., None], 0, 255
    ).astype(np.uint8)

    zone = np.zeros((H, W), dtype=bool)
    zone[ny0 - 2 : y1 + 2, x0 - 2 : x1 + 2] = True
    zone[:, 340:] = False
    diff = np.any(np.abs(out.astype(np.int16) - work.astype(np.int16)) > 1, axis=-1) & zone
    wrote |= diff
    result = work.copy()
    result[wrote] = out[wrote]
    return result, wrote


def stem_edges_at(rgb: np.ndarray, y: int) -> tuple[int, int] | None:
    roof = is_roof(rgb)
    xs = np.where(roof[y, 300:450])[0] + 300
    if len(xs) < 10:
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
    if pick[1] - pick[0] < 40:
        return None
    return pick[0], pick[1]


def widen_stem(work: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """X-scale the stem body only (below T), soft-composite building pixels."""
    x0, y0, x1, y1 = STEM_BOX
    crop = work[y0:y1, x0:x1].copy()
    h, w = crop.shape[:2]
    bld = is_roof(crop) | (groom_alpha(crop) > 0.5)  # reuse buildingish via alpha-ish
    # better building mask for stem
    r, g, b = (crop[..., i].astype(np.int16) for i in range(3))
    green = (g > r + 12) & (g > b + 8) & (g > 55)
    warm = (r > 90) & (r < 210) & (r > g + 8) & (r > b + 15) & (g < 170)
    lum = (r.astype(np.int32) + g + b) / 3.0
    wall = (lum > 130) & (r > 130) & (g > 120) & (b > 90) & ~((g > r + 5) & (g > b + 5))
    bld = ((is_roof(crop) | warm | wall) & ~green).astype(np.float32)
    bld = cv2.dilate(bld, np.ones((5, 5), np.uint8), iterations=1)
    bld = cv2.GaussianBlur(bld, (0, 0), 1.5)

    # geo: central hall band with soft sides + end fade at north (toward T) and south
    geo = np.zeros((h, w), np.float32)
    # hall core relative
    hx0, hx1 = 18, w - 18
    geo[:, hx0:hx1] = 1.0
    geo = cv2.GaussianBlur(geo, (0, 0), 5.0)
    # fade top 12 rows so T zone stays clean
    for i in range(12):
        geo[i, :] *= (i / 12.0) ** 1.5
    for i in range(10):
        geo[h - 1 - i, :] *= (i / 10.0) ** 1.2
    alpha = np.clip(geo * np.maximum(bld, 0.75), 0, 1)

    new_w = int(round(w * STEM_SCALE_X))
    scaled = cv2.resize(crop, (new_w, h), interpolation=cv2.INTER_LANCZOS4)
    alpha_s = cv2.resize(alpha, (new_w, h), interpolation=cv2.INTER_LINEAR)
    alpha_s = np.clip(alpha_s, 0, 1)

    paste_x0 = int(round(STEM_CX - new_w / 2))
    H, W = work.shape[:2]
    out = work.copy()
    wrote = np.zeros((H, W), dtype=bool)

    # protect groom / bridal — keep west of stem free for wings/widen edge only
    protect = np.zeros((H, W), dtype=bool)
    protect[480:660, 200:300] = True  # groom core only (not wing corridor)
    protect[540:700, 455:560] = True

    for yy in range(h):
        for xx in range(new_w):
            a = float(alpha_s[yy, xx])
            if a < 0.05:
                continue
            dx = paste_x0 + xx
            dy = y0 + yy
            if dx < 0 or dx >= W or dy < 0 or dy >= H:
                continue
            if protect[dy, dx]:
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


def add_t_wings(work: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Paint short E/W roof wings at north tip — capital T crossbar."""
    H, W = work.shape[:2]
    out = work.copy()
    wrote = np.zeros((H, W), dtype=bool)

    # Roof tile source from mid-stem (clean shingles) — resize, don't tile-stamp
    src = work[708:748, 345:395].copy()
    if is_roof(src).mean() < 0.3:
        src = work[712:752, 348:398].copy()

    # Stem edges just below tip
    edges = stem_edges_at(out, 700) or stem_edges_at(out, 710)
    if edges is None:
        stem_l, stem_r = 320, 416
    else:
        stem_l, stem_r = edges

    wing_h = WING_Y1 - WING_Y0
    specs = [
        # west wing — small
        (stem_l - WING_LEN_W, WING_Y0, stem_l + WING_OVERLAP, WING_Y1, True),
        # east wing
        (stem_r - WING_OVERLAP, WING_Y0, stem_r + WING_LEN_E, WING_Y1, False),
    ]

    # Do NOT protect the west-wing corridor; groom already moved north
    protect = np.zeros((H, W), dtype=bool)
    protect[480:630, 200:310] = True  # remaining groom body north of tip
    protect[540:700, 460:560] = True  # bridal
    protect[555:615, 385:435] = True  # fountain

    for wx0, wy0, wx1, wy1, mirror in specs:
        wx0, wx1 = max(0, wx0), min(W, wx1)
        wy0, wy1 = max(0, wy0), min(H, wy1)
        ww, hh = wx1 - wx0, wy1 - wy0
        if ww < 6 or hh < 6:
            continue

        # Lanczos-resized roof patch (continuous shingles, not stamped tiles)
        patch = src[:, ::-1].copy() if mirror else src.copy()
        tiled = cv2.resize(patch, (ww, hh), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        if mirror:
            tiled[:, :3] *= 0.80
            tiled[:2, :] *= 0.90
        else:
            tiled[:, -3:] *= 0.80
            tiled[:2, :] *= 0.90

        # Firm crossbar alpha — capital T must read clearly
        alpha = soft_rect(hh, ww, feather=2.0)
        alpha = np.clip(alpha * 1.25, 0, 1)
        if mirror:
            fade = np.linspace(0.7, 1.0, ww, dtype=np.float32)
        else:
            fade = np.linspace(1.0, 0.65, ww, dtype=np.float32)
        alpha = alpha * fade[None, :]

        dest = out[wy0:wy1, wx0:wx1]
        dr, dg, db = (dest[..., i].astype(np.int16) for i in range(3))
        # Prefer painting onto lawn/path; reduce on foreign roofs (bridal/groom)
        foreign_roof = is_roof(dest)
        # keep stem-join columns paintable even if already roof
        join = WING_OVERLAP + 3
        if mirror:
            foreign_roof[:, ww - join :] = False
        else:
            foreign_roof[:, :join] = False
        # if it's groom-ish far west, skip
        court = (dr > 155) & (dg > 145) & (db > 115) & (np.abs(dr.astype(int) - dg) < 30)
        alpha = alpha.copy()
        alpha[foreign_roof] *= 0.20
        alpha[court] *= 0.35  # keep wings mostly off courtyard paving
        prot = protect[wy0:wy1, wx0:wx1]
        alpha[prot] = 0.0
        alpha = np.clip(alpha, 0, 1)

        blended = dest.astype(np.float32) * (1 - alpha[..., None]) + tiled * alpha[..., None]
        out[wy0:wy1, wx0:wx1] = np.clip(blended, 0, 255).astype(np.uint8)
        wrote[wy0:wy1, wx0:wx1] |= alpha > 0.15

    # Ensure stem north tip still has roof continuity under crossbar
    for y in range(WING_Y0 + 6, WING_Y1 - 4):
        e = stem_edges_at(work, min(H - 1, y + 50))
        if e is None:
            continue
        for x in range(e[0], e[1] + 1):
            if protect[y, x]:
                continue
            if not is_roof(out[y : y + 1, x : x + 1])[0, 0]:
                out[y, x] = work[min(H - 1, y + 55), np.clip(x, e[0], e[1])]
                wrote[y, x] = True

    result = work.copy()
    result[wrote] = out[wrote]
    return result, wrote


def roof_run(rgb: np.ndarray, y: int) -> tuple[int, int, int] | None:
    e = stem_edges_at(rgb, y)
    if e is None:
        return None
    return e[0], e[1], e[1] - e[0] + 1


def groom_centroid(rgb: np.ndarray) -> tuple[float, float, int]:
    roof = is_roof(rgb)
    # after shift, search expanded band
    ys, xs = np.where(roof[490:690, 220:340])
    if len(ys) == 0:
        return float("nan"), float("nan"), 0
    return float(xs.mean() + 220), float(ys.mean() + 490), int(len(ys))


def wing_frac(rgb: np.ndarray, box: tuple[int, int, int, int]) -> float:
    x0, y0, x1, y1 = box
    return float(is_roof(rgb)[y0:y1, x0:x1].mean())


def main() -> None:
    assert BASE.exists(), BASE
    base = np.array(Image.open(BASE).convert("RGB"))
    assert base.shape[:2] == (1024, 682), base.shape

    lx0, ly0, lx1, ly1 = LAWN_SAMPLE
    lawn = base[ly0:ly1, lx0:lx1].copy()
    # keep only grassy-ish pixels in sample (replace non-grass with median grass)
    lr, lg, lb = (lawn[..., i].astype(np.int16) for i in range(3))
    grass = (lg > lr + 6) & (lg > lb + 4) & (lg > 55)
    if grass.any():
        med = np.median(lawn[grass], axis=0)
        lawn = lawn.copy()
        lawn[~grass] = med.astype(np.uint8)

    # 1) Groom north
    work, wrote_g = move_groom_north(base.copy(), lawn, base)

    # 2) Widen stem body
    work, wrote_w = widen_stem(work)

    # 3) T wings
    work, wrote_t = add_t_wings(work)

    wrote = wrote_g | wrote_w | wrote_t
    out = base.copy()
    out[wrote] = work[wrote]

    print("=== Stem widths (body) ===")
    for y in (700, 720, 740):
        print(f"y={y} base={roof_run(base, y)} after={roof_run(out, y)}")

    print("\n=== Tip / wings ===")
    # measure tip span including wings
    for y in (650, 660, 670, 680):
        print(f"y={y} base={roof_run(base, y)} after={roof_run(out, y)}")

    lb = (STEM_BOX[0] - WING_LEN_W, WING_Y0, STEM_BOX[0], WING_Y1)
    # use measured stem edges for wing boxes
    e700 = stem_edges_at(out, 700) or (320, 416)
    lbox = (e700[0] - WING_LEN_W, WING_Y0, e700[0], WING_Y1)
    rbox = (e700[1], WING_Y0, e700[1] + WING_LEN_E, WING_Y1)
    print(f"L-wing {lbox}: {wing_frac(base, lbox):.3f} -> {wing_frac(out, lbox):.3f}")
    print(f"R-wing {rbox}: {wing_frac(base, rbox):.3f} -> {wing_frac(out, rbox):.3f}")

    cxb, cyb, nb = groom_centroid(base)
    cxa, cya, na = groom_centroid(out)
    print(f"\nGroom: cy {cyb:.1f}->{cya:.1f} north_by={cyb-cya:.1f} n={nb}->{na}")

    outside = ~wrote
    max_out = int(np.abs(base.astype(np.int16) - out.astype(np.int16))[outside].max()) if outside.any() else 0
    print(f"Max absdiff outside edit mask: {max_out}")
    print(f"Edit mask pixels: {int(wrote.sum())}")

    def lap(rgb):
        gray = cv2.cvtColor(rgb[40:160, 40:160], cv2.COLOR_RGB2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())

    print(f"Forest lap equal: {lap(base) == lap(out)}")

    Image.fromarray(out).save(OUT)
    Image.fromarray(out).save(LIVE)
    print(f"saved {OUT.name} + {LIVE.name}")

    QA.mkdir(parents=True, exist_ok=True)

    def sbs(box, name):
        x0, y0, x1, y1 = box
        ca, cb = base[y0:y1, x0:x1], out[y0:y1, x0:x1]
        gap = np.full((ca.shape[0], 6, 3), 240, np.uint8)
        Image.fromarray(np.concatenate([ca, gap, cb], 1)).save(QA / name)

    Image.fromarray(out[540:780, 250:470]).save(QA / "s-ballroom.png")
    Image.fromarray(out[490:700, 195:355]).save(QA / "s-groom.png")
    Image.fromarray(out[560:720, 280:460]).save(QA / "s-north-tip.png")
    sbs((250, 540, 470, 780), "cmp-ballroom.png")
    sbs((195, 490, 355, 700), "cmp-groom.png")
    sbs((280, 560, 460, 720), "cmp-north-tip.png")
    Image.fromarray((wrote.astype(np.uint8) * 255)).save(QA / "edit-mask.png")

    wb = [roof_run(base, y)[2] for y in (700, 720, 740) if roof_run(base, y)]
    wa = [roof_run(out, y)[2] for y in (700, 720, 740) if roof_run(out, y)]
    lg = wing_frac(out, lbox) - wing_frac(base, lbox)
    rg = wing_frac(out, rbox) - wing_frac(base, rbox)
    print("\n========== VERDICT ==========")
    print(f"Wider? {'YES' if np.mean(wa) > np.mean(wb) + 5 else 'NO'} ({np.mean(wb):.1f}->{np.mean(wa):.1f})")
    print(f"T wings? {'YES' if lg > 0.15 and rg > 0.15 else 'NO'} L={lg:+.3f} R={rg:+.3f}")
    print(f"Groom north? {'YES' if (cyb - cya) >= 10 else 'NO'} ({cyb - cya:.1f}px)")
    print(f"Exterior identical? {'YES' if max_out == 0 else 'NO'}")


if __name__ == "__main__":
    main()
