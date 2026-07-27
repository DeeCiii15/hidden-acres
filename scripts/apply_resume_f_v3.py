"""Resume-f v3: spatial clone-stamp grass + coherent road patches.

Fixes v2 issues: roof/courtyard contamination, noisy random-pixel fills,
hard road edges.
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
    return cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))


def erode(mask: np.ndarray, k: int) -> np.ndarray:
    return cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))


def soft_alpha(mask: np.ndarray, blur: int = 17) -> np.ndarray:
    if blur % 2 == 0:
        blur += 1
    return np.clip(cv2.GaussianBlur(mask.astype(np.float32), (blur, blur), 0) / 255.0, 0, 1)


def roadish(bgr: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(bgr.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    return ((lum > 125) & (lum < 220) & (r > b + 8) & (r >= g - 10) & (g > b - 8)).astype(np.uint8)


def grassish(bgr: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(bgr.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    return ((g > r + 4) & (g > b) & (lum > 55) & (lum < 190)).astype(np.uint8)


def water(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return (hsv[:, :, 0] >= 90) & (hsv[:, :, 0] <= 130) & (hsv[:, :, 1] > 50) & (hsv[:, :, 2] < 165)


def _keep_large_components(mask: np.ndarray, min_area: int) -> np.ndarray:
    raw = (mask > 0).astype(np.uint8) * 255
    n, labels, stats, _ = cv2.connectedComponentsWithStats(raw, 8)
    out = np.zeros_like(raw)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            # Prefer compact building-like blobs (not long road strokes)
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            if w < 1 or h < 1:
                continue
            fill = area / float(w * h)
            if fill < 0.12 and max(w, h) > 120:
                continue
            out[labels == i] = 255
    return out


def structure_protect(bgr: np.ndarray) -> np.ndarray:
    """Buildings / roofs / courtyard — tight mask so roads stay editable."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    bch, gch, rch = cv2.split(bgr.astype(np.float32))
    hh, ww = bgr.shape[:2]

    # Terracotta / brown shingles (ballroom etc.) — tighter sat/value
    roof = (
        ((h <= 15) | (h >= 172))
        & (s > 55)
        & (v > 55)
        & (v < 170)
        & (rch > gch + 8)
        & (rch > bch + 15)
    )
    roof_m = _keep_large_components(roof.astype(np.uint8) * 255, 180)

    # Grey chapel/inn roofs
    grey = (
        (s < 45)
        & (v > 70)
        & (v < 145)
        & (np.abs(rch - gch) < 18)
        & (np.abs(gch - bch) < 22)
        & (rch > 70)
    )
    # Restrict grey to upper half where Inn/Chapel live + filter CCs
    grey_m = np.zeros((hh, ww), np.uint8)
    grey_m[: int(hh * 0.55)] = grey[: int(hh * 0.55)].astype(np.uint8) * 255
    grey_m = _keep_large_components(grey_m, 250)

    # Courtyard stone — bbox only
    stone = np.zeros((hh, ww), np.uint8)
    y0, y1 = int(hh * 0.52), int(hh * 0.68)
    x0, x1 = int(ww * 0.38), int(ww * 0.62)
    roi = bgr[y0:y1, x0:x1]
    hsv_r = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    st = (hsv_r[:, :, 2] > 145) & (hsv_r[:, :, 1] < 75)
    stone[y0:y1, x0:x1] = st.astype(np.uint8) * 255
    stone = _keep_large_components(stone, 120)

    prot = cv2.bitwise_or(roof_m, grey_m)
    prot = cv2.bitwise_or(prot, stone)
    prot = dilate(prot, 3)
    return prot


def skeletonize(mask: np.ndarray) -> np.ndarray:
    img = (mask > 0).astype(np.uint8) * 255
    skel = np.zeros_like(img)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        opened = cv2.morphologyEx(img, cv2.MORPH_OPEN, element)
        temp = cv2.subtract(img, opened)
        eroded = cv2.erode(img, element)
        skel = cv2.bitwise_or(skel, temp)
        img = eroded.copy()
        if cv2.countNonZero(img) == 0:
            break
    return skel


def build_red_erase(clean: np.ndarray, red: np.ndarray, protect: np.ndarray) -> np.ndarray:
    near = dilate(red, 26)
    # Only road pixels near red + modest stroke dilation
    core = ((roadish(clean) > 0) & (near > 0)).astype(np.uint8) * 255
    core = cv2.bitwise_or(core, dilate(red, 11))
    core = dilate(core, 7)
    core[water(clean)] = 0
    core[protect > 0] = 0
    return core


def spatial_clone_fill(
    base: np.ndarray,
    erase: np.ndarray,
    src: np.ndarray,
    protect: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Fill erase by copying nearby grass patches with spatial coherence + feather."""
    h, w = base.shape[:2]
    out = base.copy()
    avoid = dilate(erase, 2)
    b, g, r = cv2.split(src.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    donor_ok = (
        (grassish(src) > 0)
        & (roadish(src) == 0)
        & (avoid == 0)
        & (protect == 0)
        & ~water(src)
        & (lum > 80)
        & (lum < 175)
    )

    n, labels, stats, _ = cv2.connectedComponentsWithStats(erase, 8)
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < 15:
            continue
        x0 = int(stats[i, cv2.CC_STAT_LEFT])
        y0 = int(stats[i, cv2.CC_STAT_TOP])
        bw = int(stats[i, cv2.CC_STAT_WIDTH])
        bh = int(stats[i, cv2.CC_STAT_HEIGHT])
        pad = max(80, int(max(bw, bh) * 1.5))
        rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
        rx1, ry1 = min(w, x0 + bw + pad), min(h, y0 + bh + pad)

        blob = (labels == i).astype(np.uint8) * 255
        # Candidate donor offsets: try shifts that land in grass
        offsets = []
        for dy, dx in [
            (-bh - 10, 0),
            (bh + 10, 0),
            (0, -bw - 10),
            (0, bw + 10),
            (-bh // 2, bw + 8),
            (bh // 2, -bw - 8),
            (-20, 30),
            (20, -30),
            (-40, -20),
            (35, 25),
        ]:
            offsets.append((dy, dx))
        # random extras
        for _ in range(12):
            offsets.append((int(rng.integers(-pad, pad)), int(rng.integers(-pad, pad))))

        best_score = -1.0
        best = None
        for dy, dx in offsets:
            # Score: how many erase pixels map to donor_ok
            ys, xs = np.where(blob > 0)
            ty = ys + dy
            tx = xs + dx
            valid = (ty >= 0) & (ty < h) & (tx >= 0) & (tx < w)
            if valid.sum() < area * 0.5:
                continue
            score = float(donor_ok[ty[valid], tx[valid]].mean())
            if score > best_score:
                best_score = score
                best = (dy, dx)
        if best is None or best_score < 0.15:
            # fallback: NS inpaint only this blob (less smear than Telea for small)
            local = out[ry0:ry1, rx0:rx1].copy()
            local_m = blob[ry0:ry1, rx0:rx1]
            local = cv2.inpaint(local, local_m, 5, cv2.INPAINT_NS)
            a = soft_alpha(local_m, 11)[..., None]
            roi = out[ry0:ry1, rx0:rx1].astype(np.float32)
            out[ry0:ry1, rx0:rx1] = np.clip(roi * (1 - a) + local.astype(np.float32) * a, 0, 255).astype(
                np.uint8
            )
            continue

        dy, dx = best
        # Build fill via shift
        fill = np.zeros_like(out)
        ys, xs = np.where(blob > 0)
        ty = np.clip(ys + dy, 0, h - 1)
        tx = np.clip(xs + dx, 0, w - 1)
        # Where donor bad, search local alternative
        good = donor_ok[ty, tx]
        fill[ys, xs] = src[ty, tx]
        bad_ys, bad_xs = ys[~good], xs[~good]
        if len(bad_xs) > 0:
            # sample from ring grass
            ring = dilate(blob, 40)
            ring = cv2.bitwise_and(ring, cv2.bitwise_not(blob))
            ring = (ring > 0) & donor_ok
            rys, rxs = np.where(ring)
            if len(rxs) > 20:
                picks = rng.integers(0, len(rxs), size=len(bad_xs))
                fill[bad_ys, bad_xs] = src[rys[picks], rxs[picks]]
            else:
                fill[bad_ys, bad_xs] = src[ty[~good], tx[~good]]

        # Multi-pass micro jitter for less clone-repeat look
        jitter = fill.copy()
        for jdy, jdx in ((3, 5), (-4, 2), (2, -6)):
            shifted = np.roll(np.roll(fill, jdy, axis=0), jdx, axis=1)
            mix = 0.18
            jitter = (
                jitter.astype(np.float32) * (1 - mix) + shifted.astype(np.float32) * mix
            ).astype(np.uint8)

        a = soft_alpha(blob, 15)
        # Stronger in core
        a = np.maximum(a, soft_alpha(erode(blob, 3), 5) * 0.98)
        a[protect > 0] = 0
        bf = out.astype(np.float32)
        ff = jitter.astype(np.float32)
        # Add tiny high-freq noise from donor neighborhood to break seams
        noise = rng.normal(0, 1.8, ff.shape).astype(np.float32)
        ff = np.clip(ff + noise * a[..., None], 0, 255)
        out = np.clip(bf * (1 - a[..., None]) + ff * a[..., None], 0, 255).astype(np.uint8)

    return out


def extract_road_atlas(clean: np.ndarray, avoid: np.ndarray) -> np.ndarray:
    h, w = clean.shape[:2]
    rm = roadish(clean).astype(bool)
    rm[avoid > 0] = False
    yy, xx = np.mgrid[0:h, 0:w]
    zone = (yy > int(h * 0.55)) & (yy < int(h * 0.80)) & (xx > int(w * 0.34)) & (xx < int(w * 0.62))
    cand = rm & zone
    if cand.sum() < 400:
        cand = rm
    ys, xs = np.where(cand)
    cy, cx = int(np.median(ys)), int(np.median(xs))
    y0, y1 = max(0, cy - 56), min(h, cy + 56)
    x0, x1 = max(0, cx - 56), min(w, cx + 56)
    patch = clean[y0:y1, x0:x1].copy()
    local = roadish(patch)
    if local.sum() > 80:
        miss = (local == 0).astype(np.uint8) * 255
        patch = cv2.inpaint(patch, miss, 4, cv2.INPAINT_NS)
    return patch


def paint_roads(
    work: np.ndarray,
    blue: np.ndarray,
    atlas: np.ndarray,
    protect: np.ndarray,
    erase: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    h, w = work.shape[:2]
    blue_bin = cv2.morphologyEx(
        (blue > 0).astype(np.uint8) * 255,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
    )
    sk = skeletonize(blue_bin)
    if cv2.countNonZero(sk) < 80:
        sk = blue_bin
    # Match existing road width (~34-38px diameter)
    body = dilate(sk, 17)
    body = cv2.bitwise_or(body, dilate(blue_bin, 9))
    body[protect > 0] = 0
    body[erase > 0] = 0
    body[water(work)] = 0

    dist = cv2.distanceTransform((body > 0).astype(np.uint8), cv2.DIST_L2, 5)
    alpha = np.zeros((h, w), np.float32)
    inside = body > 0
    if inside.any():
        dmax = max(float(dist[inside].max()), 1.0)
        t = dist / dmax
        # Keep center solid; feather outer 35%
        alpha[inside] = np.clip((t - 0.12) / 0.88, 0, 1)[inside] ** 0.7
    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)
    alpha = np.clip(alpha, 0, 1)
    alpha[protect > 0] = 0
    alpha[erase > 0] = 0
    alpha[water(work)] = 0

    ah, aw = atlas.shape[:2]
    yy, xx = np.indices((h, w))
    # Two offset layers for less tiling
    dirt1 = atlas[yy % ah, xx % aw].astype(np.float32)
    dirt2 = atlas[(yy + ah // 3) % ah, (xx + aw // 2) % aw].astype(np.float32)
    dirt = 0.55 * dirt1 + 0.45 * dirt2
    dirt += rng.normal(0, 3.0, dirt.shape)
    # Slight center brightening like gravel highlight
    dirt = dirt + (alpha * 6.0)[..., None]
    dirt = np.clip(dirt, 0, 255)

    # Edge darkening
    edge = np.clip(alpha * (1 - alpha) * 3.8, 0, 1)
    dirt = dirt * (1.0 - 0.14 * edge[..., None])

    out = work.astype(np.float32)
    a = alpha[..., None]
    # Forest: more opaque so canopy doesn't speck through
    forest_dark = grassish(work).astype(bool) & (
        cv2.cvtColor(work, cv2.COLOR_BGR2HSV)[:, :, 2] < 100
    )
    a_use = a.copy()
    boost = (forest_dark & (alpha > 0.2))
    a_use[boost] = np.maximum(a_use[boost], 0.92)

    out = out * (1 - a_use * 0.96) + dirt * (a_use * 0.96)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out, body


def main() -> None:
    QA.mkdir(exist_ok=True)
    clean = cv2.imread(str(CLEAN))
    markup = cv2.imread(str(MARKUP))
    assert clean is not None and markup is not None
    if markup.shape[:2] != clean.shape[:2]:
        markup = cv2.resize(markup, (clean.shape[1], clean.shape[0]), interpolation=cv2.INTER_AREA)

    if BAD_E.exists() and not BAD_E_ASIDE.exists():
        shutil.copy2(BAD_E, BAD_E_ASIDE)

    blue = vivid_blue_mask(markup)
    red = vivid_red_mask(markup)
    protect = structure_protect(clean)
    print(f"blue={cv2.countNonZero(blue)} red={cv2.countNonZero(red)} protect={cv2.countNonZero(protect)}")

    rng = np.random.default_rng(42)
    erase = build_red_erase(clean, red, protect)
    print(f"erase={cv2.countNonZero(erase)}")

    work = spatial_clone_fill(clean, erase, clean, protect, rng)

    # Ghost pass
    soft_e = soft_alpha(erase, 9)
    ghost = (soft_e > 0.5) & (roadish(work) > 0) & (protect == 0) & ~water(work)
    if ghost.any():
        gmask = dilate(ghost.astype(np.uint8) * 255, 5)
        gmask[protect > 0] = 0
        print(f"ghost={cv2.countNonZero(gmask)}")
        work = spatial_clone_fill(work, gmask, clean, protect, np.random.default_rng(9))

    atlas = extract_road_atlas(clean, dilate(blue, 8))
    work, blue_body = paint_roads(work, blue, atlas, protect, erase, rng)

    # Weak blue fill-in
    weak = (blue_body > 0) & (roadish(work) == 0) & (protect == 0) & ~water(work)
    if weak.any():
        print(f"weak={int(weak.sum())}")
        # boost alpha paint again on weak only
        boost_mask = dilate(weak.astype(np.uint8) * 255, 5)
        # temporarily treat boost as blue
        work, _ = paint_roads(work, boost_mask, atlas, protect, erase, np.random.default_rng(3))

    # Scrub ink
    near = dilate(cv2.bitwise_or(blue, red), 22)
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    hh, ss, vv = cv2.split(hsv)
    ink = (
        ((hh >= 95) & (hh <= 135) & (ss > 110) & (vv > 70))
        | (((hh <= 10) | (hh >= 170)) & (ss > 110) & (vv > 70))
    ) & (near > 0) & (protect == 0)
    if ink.any():
        im = dilate(ink.astype(np.uint8) * 255, 3)
        work = spatial_clone_fill(work, im, clean, protect, np.random.default_rng(1))

    cv2.imwrite(str(OUT_LIVE), work)
    cv2.imwrite(str(OUT_BACKUP), work)
    print(f"wrote {OUT_BACKUP.name}")

    qb = cv2.bitwise_and(vivid_blue_mask(work), near)
    qr = cv2.bitwise_and(vivid_red_mask(work), near)
    print(f"QA ink blue={cv2.countNonZero(qb)} red={cv2.countNonZero(qr)}")
    print(
        "roadish erase",
        int(((roadish(work) > 0) & (erase > 0)).sum()),
        "roadish blue",
        int(((roadish(work) > 0) & (blue_body > 0)).sum()),
        "/",
        int((blue_body > 0).sum()),
    )
    edit = cv2.bitwise_or(dilate(blue_body, 2), dilate(erase, 2))
    outside = (edit == 0) & (protect == 0)
    diff = cv2.absdiff(clean, work).mean(axis=2)
    print("outside mean absdiff", float(diff[outside].mean()))
    # roof check
    roi = (slice(1000, 1280), slice(350, 750))
    print("roof roi mean diff", float(diff[roi].mean()))

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
        cv2.imwrite(str(QA / f"v3-{name}.png"), grid)
    cv2.imwrite(str(QA / "v3-full.png"), work)
    hot = (diff > 25).astype(np.uint8) * 255
    ov = work.copy()
    ov[hot > 0] = (0, 0, 255)
    cv2.imwrite(str(QA / "v3-hotdiff.png"), ov)


if __name__ == "__main__":
    main()
