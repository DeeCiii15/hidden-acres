"""Resume-f final: Poisson grass clone for red + opaque roads for blue.

Forest blue paths use clean road atlas (fully opaque). Open-field blue uses
GenerateImage composite. Red uses seamlessClone of nearby lawn patches.
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
GEN1 = ASSETS / "hidden-acres-grounds-illustrated-v-map-resume-f-gen.png"
GEN2 = ASSETS / "hidden-acres-grounds-illustrated-v-map-resume-f-gen2.png"
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
            ww = stats[i, cv2.CC_STAT_WIDTH]
            hh = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            fill = area / float(max(ww * hh, 1))
            if fill < 0.12 and max(ww, hh) > 120:
                continue
            out[labels == i] = 255
    return out


def structure_protect(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    bch, gch, rch = cv2.split(bgr.astype(np.float32))
    hh, ww = bgr.shape[:2]
    roof = (
        ((h <= 15) | (h >= 172))
        & (s > 55)
        & (v > 55)
        & (v < 170)
        & (rch > gch + 8)
        & (rch > bch + 15)
    )
    roof_m = _keep_large_components(roof.astype(np.uint8) * 255, 180)
    grey = (
        (s < 45)
        & (v > 70)
        & (v < 145)
        & (np.abs(rch - gch) < 18)
        & (np.abs(gch - bch) < 22)
        & (rch > 70)
    )
    grey_m = np.zeros((hh, ww), np.uint8)
    grey_m[: int(hh * 0.55)] = grey[: int(hh * 0.55)].astype(np.uint8) * 255
    grey_m = _keep_large_components(grey_m, 250)
    stone = np.zeros((hh, ww), np.uint8)
    y0, y1 = int(hh * 0.52), int(hh * 0.68)
    x0, x1 = int(ww * 0.38), int(ww * 0.62)
    hsv_r = cv2.cvtColor(bgr[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    st = (hsv_r[:, :, 2] > 145) & (hsv_r[:, :, 1] < 75)
    stone[y0:y1, x0:x1] = st.astype(np.uint8) * 255
    stone = _keep_large_components(stone, 120)
    return dilate(cv2.bitwise_or(cv2.bitwise_or(roof_m, grey_m), stone), 3)


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
    core = ((roadish(clean) > 0) & (near > 0)).astype(np.uint8) * 255
    core = cv2.bitwise_or(core, dilate(red, 11))
    core = dilate(core, 7)
    core[water(clean)] = 0
    core[protect > 0] = 0
    return core


def find_lawn_patch(
    src: np.ndarray,
    avoid: np.ndarray,
    protect: np.ndarray,
    bw: int,
    bh: int,
    prefer_xy: tuple[int, int],
    rng: np.random.Generator,
) -> np.ndarray | None:
    """Return a bw x bh lawn patch from src, or None."""
    h, w = src.shape[:2]
    b, g, r = cv2.split(src.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    lawn = (
        (grassish(src) > 0)
        & (roadish(src) == 0)
        & (avoid == 0)
        & (protect == 0)
        & ~water(src)
        & (lum > 85)
        & (lum < 170)
    )
    # integral for fast window scoring
    integ = cv2.integral(lawn.astype(np.float32))
    best = None
    best_score = -1.0
    px, py = prefer_xy
    trials = []
    for dy in range(-180, 181, 12):
        for dx in range(-180, 181, 12):
            trials.append((py + dy, px + dx))
    for _ in range(40):
        trials.append((int(rng.integers(0, h)), int(rng.integers(0, w))))
    for cy, cx in trials:
        y0 = cy - bh // 2
        x0 = cx - bw // 2
        if y0 < 0 or x0 < 0 or y0 + bh >= h or x0 + bw >= w:
            continue
        # sum via integral
        s = (
            integ[y0 + bh, x0 + bw]
            - integ[y0, x0 + bw]
            - integ[y0 + bh, x0]
            + integ[y0, x0]
        )
        score = float(s) / float(bw * bh)
        # prefer nearby
        dist = abs(cy - py) + abs(cx - px)
        score -= dist * 0.0004
        if score > best_score:
            best_score = score
            best = (y0, x0)
    if best is None or best_score < 0.35:
        return None
    y0, x0 = best
    return src[y0 : y0 + bh, x0 : x0 + bw].copy()


def poisson_grass_fill(
    base: np.ndarray,
    erase: np.ndarray,
    src: np.ndarray,
    protect: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    h, w = base.shape[:2]
    out = base.copy()
    erase = erase.copy()
    erase[protect > 0] = 0
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(erase, 8)
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < 20:
            continue
        x0 = int(stats[i, cv2.CC_STAT_LEFT])
        y0 = int(stats[i, cv2.CC_STAT_TOP])
        bw = int(stats[i, cv2.CC_STAT_WIDTH])
        bh = int(stats[i, cv2.CC_STAT_HEIGHT])
        # pad patch a bit larger than bbox
        pw, ph = bw + 16, bh + 16
        cx = int(centroids[i][0])
        cy = int(centroids[i][1])
        avoid = dilate(erase, 3)
        patch = find_lawn_patch(src, avoid, protect, pw, ph, (cx, cy), rng)
        blob = (labels == i).astype(np.uint8) * 255
        if patch is None:
            # fallback pixel sample
            b, g, r = cv2.split(src.astype(np.float32))
            lum = 0.114 * b + 0.587 * g + 0.299 * r
            lawn = (
                (grassish(src) > 0)
                & (roadish(src) == 0)
                & (avoid == 0)
                & (protect == 0)
                & (lum > 85)
            )
            ys, xs = np.where(lawn)
            bys, bxs = np.where(blob > 0)
            if len(xs) < 30 or len(bxs) == 0:
                continue
            picks = rng.integers(0, len(xs), size=len(bxs))
            a = soft_alpha(blob, 11)
            tmp = out.astype(np.float32)
            pix = src[ys[picks], xs[picks]].astype(np.float32)
            pix += rng.normal(0, 2.0, pix.shape)
            aa = a[bys, bxs][:, None]
            tmp[bys, bxs] = tmp[bys, bxs] * (1 - aa) + np.clip(pix, 0, 255) * aa
            out = np.clip(tmp, 0, 255).astype(np.uint8)
            continue

        # Place patch into a canvas aligned to blob bbox center
        src_canvas = out.copy()
        # center patch on centroid
        py0 = max(0, cy - ph // 2)
        px0 = max(0, cx - pw // 2)
        py1 = min(h, py0 + ph)
        px1 = min(w, px0 + pw)
        ph2, pw2 = py1 - py0, px1 - px0
        src_canvas[py0:py1, px0:px1] = patch[:ph2, :pw2]

        mask = blob.copy()
        # shrink slightly so clone edges land inside
        mask = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        if cv2.countNonZero(mask) < 10:
            mask = blob
        # ensure center inside mask
        if mask[cy, cx] == 0:
            # move to mask centroid
            m = cv2.moments(mask)
            if m["m00"] > 0:
                cx = int(m["m10"] / m["m00"])
                cy = int(m["m01"] / m["m00"])
        try:
            cloned = cv2.seamlessClone(src_canvas, out, mask, (cx, cy), cv2.NORMAL_CLONE)
            a = soft_alpha(blob, 13)
            a[protect > 0] = 0
            out = np.clip(
                out.astype(np.float32) * (1 - a[..., None])
                + cloned.astype(np.float32) * a[..., None],
                0,
                255,
            ).astype(np.uint8)
        except cv2.error:
            # alpha blend patch directly
            a = soft_alpha(blob, 13)
            a[protect > 0] = 0
            out = np.clip(
                out.astype(np.float32) * (1 - a[..., None])
                + src_canvas.astype(np.float32) * a[..., None],
                0,
                255,
            ).astype(np.uint8)
    return out


def extract_atlas(clean: np.ndarray, avoid: np.ndarray) -> np.ndarray:
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
    patch = clean[max(0, cy - 56) : min(h, cy + 56), max(0, cx - 56) : min(w, cx + 56)].copy()
    local = roadish(patch)
    if local.sum() > 80:
        patch = cv2.inpaint(patch, (local == 0).astype(np.uint8) * 255, 4, cv2.INPAINT_NS)
    return patch


def blue_body_alpha(blue, protect, erase, work):
    blue_bin = cv2.morphologyEx(
        (blue > 0).astype(np.uint8) * 255,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
    )
    sk = skeletonize(blue_bin)
    if cv2.countNonZero(sk) < 80:
        sk = blue_bin
    body = dilate(sk, 17)
    body = cv2.bitwise_or(body, dilate(blue_bin, 9))
    body[protect > 0] = 0
    body[erase > 0] = 0
    body[water(work)] = 0
    dist = cv2.distanceTransform((body > 0).astype(np.uint8), cv2.DIST_L2, 5)
    alpha = np.zeros(body.shape, np.float32)
    inside = body > 0
    if inside.any():
        dmax = max(float(dist[inside].max()), 1.0)
        t = dist / dmax
        alpha[inside] = np.clip((t - 0.08) / 0.92, 0, 1)[inside] ** 0.6
    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)
    return body, np.clip(alpha, 0, 1)


def opaque_atlas_roads(work, body, alpha, atlas, rng):
    h, w = work.shape[:2]
    ah, aw = atlas.shape[:2]
    yy, xx = np.indices((h, w))
    dirt = 0.5 * atlas[yy % ah, xx % aw].astype(np.float32) + 0.5 * atlas[
        (yy + 17) % ah, (xx + 29) % aw
    ].astype(np.float32)
    blur = cv2.GaussianBlur(dirt, (0, 0), 1.5)
    detail = dirt - blur
    dirt = dirt + detail * 0.8 + rng.normal(0, 2.5, dirt.shape)
    edge = np.clip(alpha * (1 - alpha) * 4.0, 0, 1)
    dirt = dirt * (1.0 - 0.14 * edge[..., None])
    dirt = np.clip(dirt, 0, 255)
    a = alpha[..., None]
    # nearly opaque
    out = work.astype(np.float32) * (1 - a * 0.98) + dirt * (a * 0.98)
    return np.clip(out, 0, 255).astype(np.uint8)


def main() -> None:
    QA.mkdir(exist_ok=True)
    clean = cv2.imread(str(CLEAN))
    markup = cv2.imread(str(MARKUP))
    gen1 = cv2.imread(str(GEN1))
    gen2 = cv2.imread(str(GEN2))
    assert clean is not None and markup is not None
    h, w = clean.shape[:2]
    if markup.shape[:2] != (h, w):
        markup = cv2.resize(markup, (w, h), interpolation=cv2.INTER_AREA)
    if gen1 is not None and gen1.shape[:2] != (h, w):
        gen1 = cv2.resize(gen1, (w, h), interpolation=cv2.INTER_AREA)
    if gen2 is not None and gen2.shape[:2] != (h, w):
        gen2 = cv2.resize(gen2, (w, h), interpolation=cv2.INTER_AREA)

    if BAD_E.exists() and not BAD_E_ASIDE.exists():
        shutil.copy2(BAD_E, BAD_E_ASIDE)

    blue = vivid_blue_mask(markup)
    red = vivid_red_mask(markup)
    protect = structure_protect(clean)
    erase = build_red_erase(clean, red, protect)
    print(f"erase={cv2.countNonZero(erase)} protect={cv2.countNonZero(protect)}")

    rng = np.random.default_rng(42)
    work = poisson_grass_fill(clean, erase, clean, protect, rng)

    # ghost pass
    soft_e = soft_alpha(erase, 9)
    ghost = (soft_e > 0.45) & (roadish(work) > 0) & (protect == 0)
    if ghost.any():
        print(f"ghost={int(ghost.sum())}")
        work = poisson_grass_fill(
            work, dilate(ghost.astype(np.uint8) * 255, 5), clean, protect, np.random.default_rng(7)
        )

    body, alpha = blue_body_alpha(blue, protect, erase, work)
    atlas = extract_atlas(clean, dilate(blue, 8))

    # Forest vs open: forest = dark green canopy
    hsv = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)
    forest = (hsv[:, :, 2] < 110) & (grassish(clean) > 0)
    open_field = ~forest & ~water(clean)

    # 1) Opaque atlas everywhere on blue (base layer)
    work = opaque_atlas_roads(work, body, alpha, atlas, rng)

    # 2) In open field, blend gen roads on top for painterly look
    if gen1 is not None and gen2 is not None:
        r1 = roadish(gen1).astype(np.float32)
        r2 = roadish(gen2).astype(np.float32)
        gen = gen1.copy()
        gen[r2 >= r1] = gen2[r2 >= r1]
        take = (body > 0) & open_field & (protect == 0) & (erase == 0) & (roadish(gen) > 0)
        strength = alpha.copy()
        strength[~take] = 0
        strength[take] = np.clip(strength[take] * 0.75, 0, 0.85)
        work = np.clip(
            work.astype(np.float32) * (1 - strength[..., None])
            + gen.astype(np.float32) * strength[..., None],
            0,
            255,
        ).astype(np.uint8)

    # Reinforce forest blue opacity (trees must not show through)
    forest_blue = (body > 0) & forest & (protect == 0)
    if forest_blue.any():
        fa = soft_alpha(forest_blue.astype(np.uint8) * 255, 7) * alpha
        fa = np.clip(fa * 1.1, 0, 1)
        work = opaque_atlas_roads(work, body, fa, atlas, np.random.default_rng(3))

    # Final red ghosts
    soft_e = soft_alpha(erase, 9)
    ghost = (soft_e > 0.4) & (roadish(work) > 0) & (protect == 0)
    if ghost.any():
        print(f"ghost2={int(ghost.sum())}")
        work = poisson_grass_fill(
            work, dilate(ghost.astype(np.uint8) * 255, 5), clean, protect, np.random.default_rng(11)
        )

    # Ink scrub
    near = dilate(cv2.bitwise_or(blue, red), 22)
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    hh, ss, vv = cv2.split(hsv)
    ink = (
        ((hh >= 95) & (hh <= 135) & (ss > 110) & (vv > 70))
        | (((hh <= 10) | (hh >= 170)) & (ss > 110) & (vv > 70))
    ) & (near > 0) & (protect == 0)
    if ink.any():
        work = poisson_grass_fill(
            work, dilate(ink.astype(np.uint8) * 255, 3), clean, protect, np.random.default_rng(2)
        )

    cv2.imwrite(str(OUT_LIVE), work)
    cv2.imwrite(str(OUT_BACKUP), work)
    print(f"wrote {OUT_BACKUP.name}")

    print(
        "roadish erase",
        int(((roadish(work) > 0) & (erase > 0)).sum()),
        "roadish blue",
        int(((roadish(work) > 0) & (body > 0)).sum()),
        "/",
        int((body > 0).sum()),
    )
    qb = cv2.bitwise_and(vivid_blue_mask(work), near)
    qr = cv2.bitwise_and(vivid_red_mask(work), near)
    print("ink", cv2.countNonZero(qb), cv2.countNonZero(qr))
    diff = cv2.absdiff(clean, work).mean(axis=2)
    edit = cv2.bitwise_or(dilate(body, 2), dilate(erase, 2))
    print("outside", float(diff[edit == 0].mean()), "roof", float(diff[1000:1280, 350:750].mean()))

    for name, box in {
        "court": (700, 950, 400, 650),
        "park": (920, 1100, 250, 480),
        "pond": (220, 520, 40, 360),
        "far": (40, 420, 780, 1020),
        "mid": (320, 560, 280, 560),
        "north": (60, 280, 250, 900),
    }.items():
        y0, y1, x0, x1 = box
        cv2.imwrite(str(QA / f"final-zoom-{name}.png"), work[y0:y1, x0:x1])
        cv2.imwrite(
            str(QA / f"final-cmp-{name}.png"),
            np.hstack([clean[y0:y1, x0:x1], markup[y0:y1, x0:x1], work[y0:y1, x0:x1]]),
        )
    cv2.imwrite(str(QA / "final-full.png"), work)
    sm = lambda im: cv2.resize(im, (420, 630))
    cv2.imwrite(str(QA / "final-triptych.png"), np.hstack([sm(clean), sm(markup), sm(work)]))


if __name__ == "__main__":
    main()
