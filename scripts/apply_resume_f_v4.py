"""Resume-f v4: multi-scale grass erase + gen road composite on clean base.

- Outside markup: exact clean pixels
- RED: NS low-freq + high-freq detail from nearby clean lawn (no Telea smear look)
- BLUE: prefer gen2 road pixels (painterly) with soft mask; atlas fallback gaps
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
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            fill = area / float(max(w * h, 1))
            if fill < 0.12 and max(w, h) > 120:
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


def multi_scale_grass_fill(
    base: np.ndarray,
    erase: np.ndarray,
    src: np.ndarray,
    protect: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Low-freq NS inpaint + high-freq detail from shifted nearby lawn."""
    h, w = base.shape[:2]
    erase = erase.copy()
    erase[protect > 0] = 0
    if cv2.countNonZero(erase) == 0:
        return base

    # 1) Low-frequency structure via NS
    low = cv2.inpaint(base, erase, 6, cv2.INPAINT_NS)

    # 2) Build donor HF detail field from clean grass (exclude erase)
    avoid = dilate(erase, 2)
    b, g, r = cv2.split(src.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    donor = (
        (grassish(src) > 0)
        & (roadish(src) == 0)
        & (avoid == 0)
        & (protect == 0)
        & ~water(src)
        & (lum > 80)
        & (lum < 175)
    )

    src_f = src.astype(np.float32)
    blur = cv2.GaussianBlur(src_f, (0, 0), 2.2)
    detail = src_f - blur

    # Spread donor detail into erase via offset copy (per component)
    detail_fill = np.zeros_like(src_f)
    weight = np.zeros((h, w), np.float32)

    n, labels, stats, _ = cv2.connectedComponentsWithStats(erase, 8)
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < 12:
            continue
        blob = labels == i
        bw = int(stats[i, cv2.CC_STAT_WIDTH])
        bh = int(stats[i, cv2.CC_STAT_HEIGHT])
        ys, xs = np.where(blob)
        best = None
        best_score = -1.0
        candidates = [
            (-bh - 8, 0),
            (bh + 8, 0),
            (0, -bw - 8),
            (0, bw + 8),
            (-bh // 2, bw + 6),
            (bh // 2, -bw - 6),
            (-25, 18),
            (22, -20),
            (-15, -28),
            (30, 12),
        ]
        for _ in range(10):
            candidates.append((int(rng.integers(-70, 70)), int(rng.integers(-70, 70))))
        for dy, dx in candidates:
            ty = ys + dy
            tx = xs + dx
            valid = (ty >= 0) & (ty < h) & (tx >= 0) & (tx < w)
            if valid.mean() < 0.6:
                continue
            score = float(donor[ty[valid], tx[valid]].mean())
            if score > best_score:
                best_score = score
                best = (dy, dx)
        if best is None:
            continue
        dy, dx = best
        ty = np.clip(ys + dy, 0, h - 1)
        tx = np.clip(xs + dx, 0, w - 1)
        detail_fill[ys, xs] = detail[ty, tx]
        weight[ys, xs] = 1.0
        # If donor weak, mix random lawn detail
        if best_score < 0.35:
            rys, rxs = np.where(donor)
            if len(rxs) > 50:
                picks = rng.integers(0, len(rxs), size=len(xs))
                detail_fill[ys, xs] = (
                    0.4 * detail_fill[ys, xs] + 0.6 * detail[rys[picks], rxs[picks]]
                )

    # Also blur-spread detail from ring into erase as secondary
    ring = dilate(erase, 35)
    ring = cv2.bitwise_and(ring, cv2.bitwise_not(erase))
    ring_m = (ring > 0) & donor
    det_masked = detail.copy()
    det_masked[~ring_m] = 0
    w_ring = ring_m.astype(np.float32)
    spread_d = cv2.GaussianBlur(det_masked, (0, 0), 12)
    spread_w = cv2.GaussianBlur(w_ring, (0, 0), 12)[..., None]
    spread = spread_d / np.maximum(spread_w, 1e-3)

    a = soft_alpha(erase, 13)
    a[protect > 0] = 0
    # Compose: low freq from NS + HF detail
    hf = detail_fill
    # where weight low, use spread
    use_spread = (weight < 0.5) & (erase > 0)
    hf[use_spread] = spread[use_spread]
    # slight extra noise for grit
    hf = hf + rng.normal(0, 1.2, hf.shape).astype(np.float32)

    out = base.astype(np.float32)
    filled = np.clip(low.astype(np.float32) + hf * 0.95, 0, 255)
    out = out * (1 - a[..., None]) + filled * a[..., None]

    # Kill remaining roadish ghosts with another NS+detail pass on ghosts only
    ghost = (a > 0.45) & (roadish(np.clip(out, 0, 255).astype(np.uint8)) > 0) & (protect == 0)
    if ghost.any():
        gm = dilate(ghost.astype(np.uint8) * 255, 5)
        gm[protect > 0] = 0
        low2 = cv2.inpaint(np.clip(out, 0, 255).astype(np.uint8), gm, 5, cv2.INPAINT_NS)
        a2 = soft_alpha(gm, 9)
        # random lawn detail
        rys, rxs = np.where(donor)
        ys, xs = np.where(gm > 0)
        extra = np.zeros_like(out)
        if len(rxs) > 50 and len(xs) > 0:
            picks = rng.integers(0, len(rxs), size=len(xs))
            extra[ys, xs] = detail[rys[picks], rxs[picks]]
        filled2 = np.clip(low2.astype(np.float32) + extra * 0.9, 0, 255)
        out = out * (1 - a2[..., None]) + filled2 * a2[..., None]

    return np.clip(out, 0, 255).astype(np.uint8)


def blue_body_alpha(blue: np.ndarray, protect: np.ndarray, erase: np.ndarray, work: np.ndarray):
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
        alpha[inside] = np.clip((t - 0.1) / 0.9, 0, 1)[inside] ** 0.65
    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)
    alpha = np.clip(alpha, 0, 1)
    alpha[protect > 0] = 0
    alpha[erase > 0] = 0
    return body, alpha


def pick_best_gen(gen1: np.ndarray, gen2: np.ndarray, clean: np.ndarray, body: np.ndarray) -> np.ndarray:
    """Per-pixel choose gen that looks more road-like in blue body."""
    r1 = roadish(gen1).astype(np.float32)
    r2 = roadish(gen2).astype(np.float32)
    # Prefer higher roadish; slight preference to gen2
    use2 = r2 + 0.05 >= r1
    out = gen1.copy()
    out[use2] = gen2[use2]
    # Where neither roadish, still prefer gen2 (may have softer gravel)
    neither = (r1 < 0.5) & (r2 < 0.5) & (body > 0)
    out[neither] = gen2[neither]
    return out


def atlas_paint(work, alpha, atlas, rng):
    h, w = work.shape[:2]
    ah, aw = atlas.shape[:2]
    yy, xx = np.indices((h, w))
    dirt = 0.55 * atlas[yy % ah, xx % aw].astype(np.float32) + 0.45 * atlas[
        (yy + ah // 3) % ah, (xx + aw // 2) % aw
    ].astype(np.float32)
    dirt += rng.normal(0, 3.0, dirt.shape)
    edge = np.clip(alpha * (1 - alpha) * 3.8, 0, 1)
    dirt = dirt * (1.0 - 0.12 * edge[..., None])
    dirt = np.clip(dirt, 0, 255)
    a = alpha[..., None]
    out = work.astype(np.float32) * (1 - a * 0.95) + dirt * (a * 0.95)
    return np.clip(out, 0, 255).astype(np.uint8)


def extract_atlas(clean, avoid):
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


def main() -> None:
    QA.mkdir(exist_ok=True)
    clean = cv2.imread(str(CLEAN))
    markup = cv2.imread(str(MARKUP))
    gen1 = cv2.imread(str(GEN1))
    gen2 = cv2.imread(str(GEN2))
    assert clean is not None and markup is not None
    h, w = clean.shape[:2]
    for name, im in [("markup", markup), ("gen1", gen1), ("gen2", gen2)]:
        if im is None:
            continue
        if im.shape[:2] != (h, w):
            resized = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
            if name == "markup":
                markup = resized
            elif name == "gen1":
                gen1 = resized
            else:
                gen2 = resized

    if BAD_E.exists() and not BAD_E_ASIDE.exists():
        shutil.copy2(BAD_E, BAD_E_ASIDE)

    blue = vivid_blue_mask(markup)
    red = vivid_red_mask(markup)
    protect = structure_protect(clean)
    erase = build_red_erase(clean, red, protect)
    print(f"blue={cv2.countNonZero(blue)} red={cv2.countNonZero(red)} erase={cv2.countNonZero(erase)}")

    rng = np.random.default_rng(42)
    work = multi_scale_grass_fill(clean, erase, clean, protect, rng)

    body, alpha = blue_body_alpha(blue, protect, erase, work)

    if gen1 is not None and gen2 is not None:
        gen = pick_best_gen(gen1, gen2, clean, body)
        # Take gen where it looks road-like OR where clean isn't already road
        gen_r = roadish(gen).astype(bool)
        take = (body > 0) & (protect == 0) & (erase == 0) & ~water(work)
        # Strength: higher when gen roadish
        strength = alpha.copy()
        strength[take & gen_r] = np.maximum(strength[take & gen_r], 0.88)
        strength[take & ~gen_r] *= 0.55
        strength[~take] = 0
        # Forest boost
        hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
        forest = (hsv[:, :, 2] < 105) & (grassish(work) > 0)
        strength[forest & take] = np.maximum(strength[forest & take], 0.9)

        wf = work.astype(np.float32)
        gf = gen.astype(np.float32)
        work = np.clip(wf * (1 - strength[..., None]) + gf * strength[..., None], 0, 255).astype(
            np.uint8
        )

    # Atlas fill remaining gaps
    weak = (body > 0) & (roadish(work) == 0) & (protect == 0) & (erase == 0) & ~water(work)
    if weak.any():
        print(f"atlas weak={int(weak.sum())}")
        atlas = extract_atlas(clean, dilate(blue, 8))
        wa = soft_alpha(dilate(weak.astype(np.uint8) * 255, 5), 9) * 0.92
        wa[protect > 0] = 0
        wa[erase > 0] = 0
        work = atlas_paint(work, wa, atlas, rng)

    # Ink scrub via grass fill
    near = dilate(cv2.bitwise_or(blue, red), 22)
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    hh, ss, vv = cv2.split(hsv)
    ink = (
        ((hh >= 95) & (hh <= 135) & (ss > 110) & (vv > 70))
        | (((hh <= 10) | (hh >= 170)) & (ss > 110) & (vv > 70))
    ) & (near > 0) & (protect == 0)
    if ink.any():
        work = multi_scale_grass_fill(
            work, dilate(ink.astype(np.uint8) * 255, 3), clean, protect, np.random.default_rng(2)
        )

    # Final red ghosts
    soft_e = soft_alpha(erase, 9)
    ghost = (soft_e > 0.5) & (roadish(work) > 0) & (protect == 0)
    if ghost.any():
        print(f"final ghost={int(ghost.sum())}")
        work = multi_scale_grass_fill(
            work, dilate(ghost.astype(np.uint8) * 255, 5), clean, protect, np.random.default_rng(7)
        )

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
        int(((roadish(work) > 0) & (body > 0)).sum()),
        "/",
        int((body > 0).sum()),
    )
    edit = cv2.bitwise_or(dilate(body, 2), dilate(erase, 2))
    outside = edit == 0
    diff = cv2.absdiff(clean, work).mean(axis=2)
    print("outside mean absdiff", float(diff[outside].mean()))
    print("roof roi mean diff", float(diff[1000:1280, 350:750].mean()))

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
        cv2.imwrite(str(QA / f"v4-{name}.png"), grid)
    cv2.imwrite(str(QA / "v4-full.png"), work)
    # triptych clean|v4|markup
    def sm(im):
        return cv2.resize(im, (420, 630))

    cv2.imwrite(str(QA / "v4-triptych.png"), np.hstack([sm(clean), sm(markup), sm(work)]))


if __name__ == "__main__":
    main()
