"""Hybrid resume-f: composite GenerateImage road edits onto clean base.

Keeps clean resume-c pixel-exact outside markup zones.
Inside blue/red dilated zones, prefer gen (painterly roads / grass fills),
with multi-scale patch clone fallback for red where gen still looks roadish.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public" / "maps"
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")

CLEAN = ASSETS / "hidden-acres-grounds-illustrated-v-map-resume-c.png"
MARKUP = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-c-markup.png"
GEN = ASSETS / "hidden-acres-grounds-illustrated-v-map-resume-f-gen.png"
OUT_LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
OUT_BACKUP = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-f.png"
BAD_E = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-e.png"
BAD_E_ASIDE = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-e-blurry-aside.png"
QA = MAPS / "_qa-resume-f"


def vivid_blue_mask(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    m = (h >= 95) & (h <= 135) & (s >= 80) & (v >= 70)
    b, g, r = cv2.split(bgr)
    m2 = (b.astype(np.int16) > 140) & (r.astype(np.int16) < 110) & (
        b.astype(np.int16) > r.astype(np.int16) + 40
    )
    return ((m | m2) & (s >= 70)).astype(np.uint8) * 255


def vivid_red_mask(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    m = ((h <= 12) | (h >= 165)) & (s >= 90) & (v >= 70)
    b, g, r = cv2.split(bgr)
    m2 = (
        (r.astype(np.int16) > 150)
        & (g.astype(np.int16) < 110)
        & (b.astype(np.int16) < 110)
        & (r.astype(np.int16) > g.astype(np.int16) + 50)
    )
    raw = ((m | m2) & (s >= 85)).astype(np.uint8) * 255
    n, labels, stats, _ = cv2.connectedComponentsWithStats(raw, 8)
    out = np.zeros_like(raw)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 80:
            out[labels == i] = 255
    return out


def dilate(mask: np.ndarray, k: int) -> np.ndarray:
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    return cv2.dilate(mask, ker, iterations=1)


def roadish_mask(bgr: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(bgr.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    return ((lum > 130) & (lum < 215) & (r > b + 10) & (r >= g - 8) & (g > b - 5)).astype(np.uint8)


def grassish_mask(bgr: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(bgr.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    return ((g > r + 5) & (g > b) & (lum > 50) & (lum < 185)).astype(np.uint8)


def forestish_mask(bgr: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(bgr.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    return ((g > r) & (g > b) & (lum < 110) & (lum > 25)).astype(np.uint8)


def water_mask(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return (
        (hsv[:, :, 0] >= 90)
        & (hsv[:, :, 0] <= 130)
        & (hsv[:, :, 1] > 50)
        & (hsv[:, :, 2] < 165)
    )


def soft_alpha(mask: np.ndarray, blur: int = 21) -> np.ndarray:
    if blur % 2 == 0:
        blur += 1
    a = cv2.GaussianBlur(mask.astype(np.float32), (blur, blur), 0) / 255.0
    return np.clip(a, 0, 1)


def multi_scale_patch_fill(
    base: np.ndarray,
    erase: np.ndarray,
    src: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Fill erase mask by copying multi-scale patches from nearby grass/forest in src."""
    h, w = base.shape[:2]
    out = base.copy()
    avoid = dilate(erase, 5)
    terrain = ((grassish_mask(src) > 0) | (forestish_mask(src) > 0)) & (avoid == 0)
    terrain &= roadish_mask(src) == 0
    terrain &= ~water_mask(src)

    ys, xs = np.where(erase > 0)
    if len(xs) == 0:
        return out

    # Connected components — fill each blob independently
    n, labels, stats, _ = cv2.connectedComponentsWithStats(erase, 8)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 20:
            continue
        x0 = stats[i, cv2.CC_STAT_LEFT]
        y0 = stats[i, cv2.CC_STAT_TOP]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]
        pad = max(40, int(max(bw, bh) * 0.8))
        rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
        rx1, ry1 = min(w, x0 + bw + pad), min(h, y0 + bh + pad)

        region_mask = (labels[ry0:ry1, rx0:rx1] == i).astype(np.uint8) * 255
        search = terrain[ry0:ry1, rx0:rx1]
        # Expand search ring around blob
        ring = dilate(region_mask, max(15, pad // 2))
        ring = cv2.bitwise_and(ring, cv2.bitwise_not(region_mask))
        cand = (search > 0) & (ring > 0)
        if cand.sum() < 80:
            cand = search > 0
        if cand.sum() < 40:
            # fall back: NS inpaint on this blob only
            local = out[ry0:ry1, rx0:rx1].copy()
            local = cv2.inpaint(local, region_mask, 7, cv2.INPAINT_NS)
            out[ry0:ry1, rx0:rx1] = local
            continue

        cy, cx = np.where(cand)
        # Build fill canvas by stamping random patches
        fill = out[ry0:ry1, rx0:rx1].astype(np.float32)
        alpha_acc = np.zeros((ry1 - ry0, rx1 - rx0), np.float32)
        blob_ys, blob_xs = np.where(region_mask > 0)

        # Patch sizes at multiple scales
        for psize in (48, 32, 20, 12):
            half = psize // 2
            # stride sampling over blob
            step = max(psize // 3, 4)
            pts = list(zip(blob_ys[::step], blob_xs[::step]))
            if not pts:
                continue
            for by, bx in pts:
                # pick donor
                for _ in range(8):
                    j = int(rng.integers(0, len(cy)))
                    dy, dx = int(cy[j]), int(cx[j])
                    # donor patch in local coords
                    sy0, sy1 = dy - half, dy + half
                    sx0, sx1 = dx - half, dx + half
                    if sy0 < 0 or sx0 < 0 or sy1 > (ry1 - ry0) or sx1 > (rx1 - rx0):
                        continue
                    donor = src[ry0 + sy0 : ry0 + sy1, rx0 + sx0 : rx0 + sx1]
                    if donor.shape[0] != psize or donor.shape[1] != psize:
                        continue
                    # destination patch centered on blob point
                    ty0, ty1 = by - half, by + half
                    tx0, tx1 = bx - half, bx + half
                    if ty0 < 0 or tx0 < 0 or ty1 > (ry1 - ry0) or tx1 > (rx1 - rx0):
                        continue
                    # weight: only inside erase + soft falloff
                    yy, xx = np.mgrid[ty0:ty1, tx0:tx1]
                    dist = np.sqrt((yy - by) ** 2 + (xx - bx) ** 2)
                    wgt = np.clip(1.0 - dist / (half + 1e-3), 0, 1) ** 1.2
                    wgt *= (region_mask[ty0:ty1, tx0:tx1] > 0).astype(np.float32)
                    # Prefer donor that is terrain-like
                    if roadish_mask(donor).mean() > 0.35:
                        continue
                    for c in range(3):
                        prev = fill[ty0:ty1, tx0:tx1, c]
                        fill[ty0:ty1, tx0:tx1, c] = prev * (1 - wgt) + donor[:, :, c] * wgt
                    alpha_acc[ty0:ty1, tx0:tx1] = np.maximum(
                        alpha_acc[ty0:ty1, tx0:tx1], wgt
                    )
                    break

        # Any remaining holes: NS inpaint
        holes = (region_mask > 0) & (alpha_acc < 0.25)
        local_u8 = np.clip(fill, 0, 255).astype(np.uint8)
        if holes.any():
            hmask = holes.astype(np.uint8) * 255
            local_u8 = cv2.inpaint(local_u8, hmask, 5, cv2.INPAINT_NS)

        # Soft blend into out
        soft = soft_alpha(region_mask, 15)[..., None]
        base_roi = out[ry0:ry1, rx0:rx1].astype(np.float32)
        blended = base_roi * (1 - soft) + local_u8.astype(np.float32) * soft
        out[ry0:ry1, rx0:rx1] = np.clip(blended, 0, 255).astype(np.uint8)

    return out


def sample_road_atlas(bgr: np.ndarray, avoid: np.ndarray) -> np.ndarray:
    h, w = bgr.shape[:2]
    rm = roadish_mask(bgr).copy()
    rm[avoid > 0] = 0
    yy, xx = np.mgrid[0:h, 0:w]
    zone = (yy > int(h * 0.55)) & (yy < int(h * 0.78)) & (xx > int(w * 0.35)) & (xx < int(w * 0.62))
    cand = (rm > 0) & zone
    if cand.sum() < 400:
        cand = rm > 0
    ys, xs = np.where(cand)
    if len(xs) < 50:
        patch = np.full((64, 64, 3), (110, 145, 165), np.uint8)
        noise = np.random.default_rng(3).integers(-12, 12, patch.shape, dtype=np.int16)
        return np.clip(patch.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    cy, cx = int(np.median(ys)), int(np.median(xs))
    y0, y1 = max(0, cy - 48), min(h, cy + 48)
    x0, x1 = max(0, cx - 48), min(w, cx + 48)
    patch = bgr[y0:y1, x0:x1].copy()
    local = roadish_mask(patch)
    if local.sum() > 100:
        miss = (local == 0).astype(np.uint8) * 255
        patch = cv2.inpaint(patch, miss, 5, cv2.INPAINT_NS)
    return patch


def stamp_roads_poisson(
    base: np.ndarray,
    blue: np.ndarray,
    atlas: np.ndarray,
    protect: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Paint road along blue skeleton using tiled atlas + seamlessClone chunks."""
    h, w = base.shape[:2]
    blue_bin = cv2.morphologyEx(
        (blue > 0).astype(np.uint8) * 255,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
    )
    # Width matching existing roads ~18-24px half-width
    body = dilate(blue_bin, 19)
    body = cv2.bitwise_or(body, dilate(blue_bin, 11))
    body[protect > 0] = 0
    body[water_mask(base)] = 0

    # Build full-frame dirt texture from atlas
    ah, aw = atlas.shape[:2]
    yy, xx = np.indices((h, w))
    dirt = atlas[(yy + 7) % ah, (xx + 13) % aw].astype(np.float32)
    dirt += rng.normal(0, 4.0, dirt.shape)
    dirt = np.clip(dirt, 0, 255).astype(np.uint8)

    # Soft alpha from distance transform
    dist = cv2.distanceTransform((body > 0).astype(np.uint8), cv2.DIST_L2, 5)
    alpha = np.zeros((h, w), np.float32)
    inside = body > 0
    if inside.any():
        dmax = max(float(dist[inside].max()), 1.0)
        t = dist / dmax
        alpha[inside] = np.clip((t - 0.08) / 0.92, 0, 1)[inside] ** 0.65
    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)
    alpha = np.clip(alpha, 0, 1)
    alpha[protect > 0] = 0
    alpha[water_mask(base)] = 0

    # Slightly darken edges for gravel lip
    edge = np.clip(alpha * (1 - alpha) * 3.5, 0, 1)
    painted = dirt.astype(np.float32)
    painted = painted * (1 - 0.12 * edge[..., None])

    out = base.astype(np.float32)
    a = alpha[..., None]
    out = out * (1 - a * 0.96) + painted * (a * 0.96)
    out = np.clip(out, 0, 255).astype(np.uint8)

    # Poisson refine in chunks along blue for seamless edges
    ys, xs = np.where(blue_bin > 0)
    if len(xs) == 0:
        return out

    step = 56
    half = 40
    # subsample points
    idx = np.arange(0, len(xs), max(1, len(xs) // 120))
    for i in idx:
        cy, cx = int(ys[i]), int(xs[i])
        y0, y1 = max(0, cy - half), min(h, cy + half)
        x0, x1 = max(0, cx - half), min(w, cx + half)
        roi_mask = (alpha[y0:y1, x0:x1] > 0.35).astype(np.uint8) * 255
        if cv2.countNonZero(roi_mask) < 40:
            continue
        # Source = painted dirt in ROI; destination = current out
        src = painted[y0:y1, x0:x1].astype(np.uint8)
        # Center of mask
        m = cv2.moments(roi_mask)
        if m["m00"] < 1:
            continue
        mx = int(m["m10"] / m["m00"])
        my = int(m["m01"] / m["m00"])
        center = (x0 + mx, y0 + my)
        try:
            # Expand mask slightly for clone
            cm = dilate(roi_mask, 5)
            # Build full-size source canvas
            src_full = out.copy()
            src_full[y0:y1, x0:x1] = src
            mask_full = np.zeros((h, w), np.uint8)
            mask_full[y0:y1, x0:x1] = cm
            # Only clone if center interior
            if mask_full[center[1], center[0]] == 0:
                continue
            cloned = cv2.seamlessClone(src_full, out, mask_full, center, cv2.NORMAL_CLONE)
            # Blend clone only near this chunk
            local_a = soft_alpha(mask_full, 11)
            bf = out.astype(np.float32)
            cf = cloned.astype(np.float32)
            la = local_a[..., None] * 0.85
            out = np.clip(bf * (1 - la) + cf * la, 0, 255).astype(np.uint8)
        except cv2.error:
            continue

    return out


def main() -> None:
    QA.mkdir(exist_ok=True)
    clean = cv2.imread(str(CLEAN))
    markup = cv2.imread(str(MARKUP))
    gen = cv2.imread(str(GEN))
    assert clean is not None and markup is not None and gen is not None
    h, w = clean.shape[:2]
    if gen.shape[:2] != (h, w):
        gen = cv2.resize(gen, (w, h), interpolation=cv2.INTER_AREA)
    if markup.shape[:2] != (h, w):
        markup = cv2.resize(markup, (w, h), interpolation=cv2.INTER_AREA)

    # Aside bad resume-e
    if BAD_E.exists() and not BAD_E_ASIDE.exists():
        shutil.copy2(BAD_E, BAD_E_ASIDE)
        print(f"aside blurry e -> {BAD_E_ASIDE.name}")

    blue = vivid_blue_mask(markup)
    red = vivid_red_mask(markup)
    print(f"blue={cv2.countNonZero(blue)} red={cv2.countNonZero(red)}")

    # Widen zones to cover road width under strokes
    blue_zone = dilate(blue, 23)
    red_zone = dilate(red, 33)
    red_zone = (cv2.GaussianBlur(red_zone, (17, 17), 0) > 30).astype(np.uint8) * 255
    red_zone[water_mask(clean)] = 0

    # Where blue overlays red, blue wins for painting after red fill
    blue_only = cv2.bitwise_and(blue_zone, cv2.bitwise_not(red_zone))

    work = clean.copy()
    rng = np.random.default_rng(42)

    # --- RED: prefer gen grass if gen is less roadish; else patch fill from clean ---
    gen_tan = roadish_mask(gen).astype(np.float32)
    clean_tan = roadish_mask(clean).astype(np.float32)
    # Use gen in red where gen reduced roadishness
    use_gen_red = (red_zone > 0) & (gen_tan < clean_tan + 0.1)
    # Also where gen is grassier
    gen_grass = grassish_mask(gen).astype(bool)
    use_gen_red = use_gen_red | ((red_zone > 0) & gen_grass & (clean_tan > 0))

    a_red_gen = soft_alpha((use_gen_red.astype(np.uint8) * 255), 19)
    # Gate to red_zone soft
    a_red = soft_alpha(red_zone, 23) * a_red_gen
    wf = work.astype(np.float32)
    gf = gen.astype(np.float32)
    work = np.clip(wf * (1 - a_red[..., None]) + gf * a_red[..., None], 0, 255).astype(np.uint8)

    # Remaining roadish ghosts in red → multi-scale patch fill from CLEAN terrain
    soft_red = soft_alpha(red_zone, 17)
    ghost = (soft_red > 0.4) & (roadish_mask(work) > 0)
    ghost &= ~water_mask(work)
    if ghost.any():
        gmask = dilate(ghost.astype(np.uint8) * 255, 9)
        gmask = cv2.bitwise_and(gmask, dilate(red_zone, 5))
        print(f"patch-fill ghost px={cv2.countNonZero(gmask)}")
        work = multi_scale_patch_fill(work, gmask, clean, rng)

    # --- BLUE: composite gen roads where gen is roadish; stamp elsewhere ---
    gen_road = (roadish_mask(gen) > 0) & (blue_only > 0)
    # Also take gen where blue zone and gen is tan-ish even if mask weak
    hsv_g = cv2.cvtColor(gen, cv2.COLOR_BGR2HSV)
    tanish = (
        (hsv_g[:, :, 0] >= 8)
        & (hsv_g[:, :, 0] <= 40)
        & (hsv_g[:, :, 1] < 130)
        & (hsv_g[:, :, 2] > 120)
    )
    take_gen_blue = ((gen_road | (tanish & (blue_only > 0))) & (red_zone == 0)).astype(np.uint8) * 255
    a_blue = soft_alpha(take_gen_blue, 15) * soft_alpha(blue_only, 17)
    # Stronger in forest so tree speck doesn't show
    forest = forestish_mask(clean) > 0
    a_blue = a_blue.copy()
    a_blue[forest & (a_blue > 0.2)] = np.maximum(a_blue[forest & (a_blue > 0.2)], 0.9)

    wf = work.astype(np.float32)
    work = np.clip(wf * (1 - a_blue[..., None] * 0.95) + gf * (a_blue[..., None] * 0.95), 0, 255).astype(
        np.uint8
    )

    # Gaps: blue corridor still not roadish → atlas stamp + poisson
    weak = (blue_only > 0) & (roadish_mask(work) == 0) & (red_zone == 0) & ~water_mask(work)
    if weak.any():
        print(f"stamp weak blue px={int(weak.sum())}")
        atlas = sample_road_atlas(clean, dilate(blue, 8))
        weak_mask = dilate(weak.astype(np.uint8) * 255, 7)
        # paint only weak corridors
        stamped = stamp_roads_poisson(work, weak_mask, atlas, red_zone, rng)
        wa = soft_alpha(weak_mask, 13)
        wf = work.astype(np.float32)
        sf = stamped.astype(np.float32)
        work = np.clip(wf * (1 - wa[..., None] * 0.9) + sf * (wa[..., None] * 0.9), 0, 255).astype(
            np.uint8
        )

    # Scrub residual vivid ink near markup
    near = dilate(cv2.bitwise_or(blue, red), 28)
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    hch, sch, vch = cv2.split(hsv)
    ink = (
        ((hch >= 95) & (hch <= 135) & (sch > 110) & (vch > 70))
        | (((hch <= 10) | (hch >= 170)) & (sch > 110) & (vch > 70))
    ) & (near > 0)
    if ink.any():
        work = cv2.inpaint(work, dilate(ink.astype(np.uint8) * 255, 3), 4, cv2.INPAINT_NS)

    # Final red ghost pass
    soft_red = soft_alpha(red_zone, 15)
    ghost2 = (soft_red > 0.45) & (roadish_mask(work) > 0) & ~water_mask(work)
    if ghost2.any():
        g2 = dilate(ghost2.astype(np.uint8) * 255, 7)
        work = multi_scale_patch_fill(work, g2, clean, np.random.default_rng(7))

    cv2.imwrite(str(OUT_LIVE), work)
    cv2.imwrite(str(OUT_BACKUP), work)
    print(f"wrote {OUT_LIVE}")
    print(f"wrote {OUT_BACKUP}")

    # QA metrics
    qb = vivid_blue_mask(work)
    qr = vivid_red_mask(work)
    qb = cv2.bitwise_and(qb, near)
    qr = cv2.bitwise_and(qr, near)
    blue_body = blue_only
    print(f"QA leftover blue={cv2.countNonZero(qb)} red={cv2.countNonZero(qr)}")
    print(
        "roadish redzone",
        int(((roadish_mask(work) > 0) & (red_zone > 0)).sum()),
        "roadish bluezone",
        int(((roadish_mask(work) > 0) & (blue_body > 0)).sum()),
        "blue_body",
        int((blue_body > 0).sum()),
    )
    # Outside edit zones should match clean exactly-ish
    edit = cv2.bitwise_or(dilate(blue_zone, 5), dilate(red_zone, 5))
    outside = edit == 0
    diff = cv2.absdiff(clean, work).mean(axis=2)
    print("outside mean absdiff", float(diff[outside].mean()))

    crops = {
        "pond-west": (220, 520, 40, 360),
        "north-field": (60, 280, 250, 900),
        "courtyard-n": (680, 980, 380, 720),
        "far-right": (40, 420, 780, 1020),
        "parking-w": (900, 1120, 220, 520),
        "mid-cottage": (320, 560, 280, 560),
    }
    for name, (y0, y1, x0, x1) in crops.items():
        grid = np.hstack([clean[y0:y1, x0:x1], markup[y0:y1, x0:x1], work[y0:y1, x0:x1]])
        cv2.imwrite(str(QA / f"hyb-{name}.png"), grid)
    cv2.imwrite(str(QA / "hyb-full.png"), work)


if __name__ == "__main__":
    main()
