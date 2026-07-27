"""Apply blue/red road markup on resume-c → clean illustrated map (v2).

BLUE = paint/extend tan dirt roads
RED  = remove roads → surrounding terrain
"""
from __future__ import annotations

import shutil
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public" / "maps"

MARKED = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-c.png"
MARKUP_COPY = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-c-markup.png"
CLEAN_REF = Path(
    r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets"
    r"\hidden-acres-grounds-illustrated-v-map-resume-c.png"
)
OUT_LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
OUT_BACKUP = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-e.png"


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
    # Drop tiny flecks (roof noise)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(raw, 8)
    out = np.zeros_like(raw)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 80:
            out[labels == i] = 255
    return out


def dilate(mask: np.ndarray, k: int) -> np.ndarray:
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    return cv2.dilate(mask, ker, iterations=1)


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


def sample_road_patch(bgr: np.ndarray, avoid: np.ndarray) -> np.ndarray:
    """Extract a rectangular road texture atlas from known good road area."""
    h, w = bgr.shape[:2]
    rm = roadish_mask(bgr)
    rm[avoid > 0] = 0
    # Prefer central approach road (south of courtyard)
    yy, xx = np.mgrid[0:h, 0:w]
    zone = (yy > int(h * 0.55)) & (yy < int(h * 0.78)) & (xx > int(w * 0.35)) & (xx < int(w * 0.62))
    cand = (rm > 0) & zone
    if cand.sum() < 400:
        cand = rm > 0
    ys, xs = np.where(cand)
    if len(xs) < 50:
        # synthetic
        patch = np.zeros((64, 64, 3), np.uint8)
        patch[:] = (110, 145, 165)
        noise = np.random.default_rng(3).integers(-12, 12, patch.shape, dtype=np.int16)
        return np.clip(patch.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    cy, cx = int(np.median(ys)), int(np.median(xs))
    y0, y1 = max(0, cy - 40), min(h, cy + 40)
    x0, x1 = max(0, cx - 40), min(w, cx + 40)
    patch = bgr[y0:y1, x0:x1].copy()
    # Inpaint non-road in patch so tiling is clean
    local = roadish_mask(patch)
    if local.sum() > 100:
        miss = (local == 0).astype(np.uint8) * 255
        patch = cv2.inpaint(patch, miss, 5, cv2.INPAINT_TELEA)
    return patch


def stamp_texture(shape_hw: tuple[int, int], atlas: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    h, w = shape_hw
    ah, aw = atlas.shape[:2]
    yy, xx = np.indices((h, w))
    # jittered tile
    ty = (yy + int(rng.integers(0, max(ah - 1, 1)))) % max(ah, 1)
    tx = (xx + int(rng.integers(0, max(aw - 1, 1)))) % max(aw, 1)
    base = atlas[ty, tx].astype(np.float32)
    base += rng.normal(0, 3.5, base.shape).astype(np.float32)
    return np.clip(base, 0, 255)


def local_terrain_fill(bgr: np.ndarray, erase: np.ndarray) -> np.ndarray:
    """Replace erase zone with nearby grass/forest (Telea + local clone)."""
    # Telea first
    base = cv2.inpaint(bgr, erase, 9, cv2.INPAINT_TELEA)

    h, w = bgr.shape[:2]
    soft = cv2.GaussianBlur(erase, (51, 51), 0).astype(np.float32) / 255.0

    # Build fill by sampling outward ring around erase
    avoid = dilate(erase, 3)
    grass = grassish_mask(bgr)
    forest = forestish_mask(bgr)
    terrain = ((grass > 0) | (forest > 0)) & (avoid == 0) & (roadish_mask(bgr) == 0)

    # Distance-weighted: for each erase pixel, we'll use global median of nearby terrain via blur trick
    # Create masked image where non-terrain is 0, blur, renormalize
    terr_img = bgr.astype(np.float32).copy()
    terr_img[terrain == 0] = 0
    weight = terrain.astype(np.float32)
    # Large blur to spread terrain colors
    blur_img = cv2.GaussianBlur(terr_img, (0, 0), 28)
    blur_w = cv2.GaussianBlur(weight, (0, 0), 28)[..., None]
    spread = blur_img / np.maximum(blur_w, 1e-3)

    # Where blur weight is too low, fall back to telea
    low = (blur_w[..., 0] < 0.05) & (soft > 0.2)
    spread[low] = base[low].astype(np.float32)

    # Add subtle texture noise so fill isn't flat
    rng = np.random.default_rng(11)
    spread = spread + rng.normal(0, 4.0, spread.shape)

    out = bgr.astype(np.float32)
    a = soft[..., None]
    out = out * (1 - a) + np.clip(spread, 0, 255) * a

    # Force remaining roadish pixels inside erase to terrain
    still = (soft > 0.4) & (roadish_mask(np.clip(out, 0, 255).astype(np.uint8)) > 0)
    out[still] = spread[still]

    return np.clip(out, 0, 255).astype(np.uint8)


def paint_roads_along_blue(
    work: np.ndarray,
    blue: np.ndarray,
    clean_ref: np.ndarray | None,
    red_zone: np.ndarray,
) -> np.ndarray:
    h, w = work.shape[:2]
    rng = np.random.default_rng(42)

    blue_bin = (blue > 0).astype(np.uint8) * 255
    blue_bin = cv2.morphologyEx(
        blue_bin, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    )

    skel = skeletonize(blue_bin)
    # Road body: dilate skeleton for consistent width; also include dilated stroke
    body = dilate(skel if cv2.countNonZero(skel) > 80 else blue_bin, 21)
    body = cv2.bitwise_or(body, dilate(blue_bin, 11))

    # Soft alpha from distance to skeleton (crisp center, soft edge)
    inv = (body == 0).astype(np.uint8) * 255
    dist = cv2.distanceTransform(cv2.bitwise_not(inv), cv2.DIST_L2, 5)
    # Normalize within body
    alpha = np.zeros((h, w), np.float32)
    inside = body > 0
    if inside.any():
        dmax = max(float(dist[inside].max()), 1.0)
        # Full opacity near centerline, feather toward edge
        t = np.zeros_like(dist, dtype=np.float32)
        t[inside] = dist[inside] / dmax
        feather = np.clip((t - 0.12) / 0.88, 0, 1) ** 0.7
        alpha[inside] = feather[inside]
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
    alpha = np.clip(alpha * 1.05, 0, 1)

    # Restore clean under blue where clean already has road (remove ink only)
    out = work.astype(np.float32)
    if clean_ref is not None and clean_ref.shape == work.shape:
        existing = roadish_mask(clean_ref) > 0
        ink = dilate(blue_bin, 5) > 0
        restore = ink & existing & (red_zone == 0)
        rs = cv2.GaussianBlur(restore.astype(np.uint8) * 255, (5, 5), 0).astype(np.float32) / 255.0
        for c in range(3):
            out[:, :, c] = out[:, :, c] * (1 - rs) + clean_ref[:, :, c] * rs
        # Reduce painting where restored
        alpha = alpha * (1.0 - rs * 0.9)

    avoid = dilate(blue_bin, 8)
    atlas = sample_road_patch(np.clip(out, 0, 255).astype(np.uint8), avoid)
    dirt = stamp_texture((h, w), atlas, rng)

    # Darken edges slightly
    edge = alpha * (1.0 - alpha) * 4.0
    edge = np.clip(edge, 0, 1)
    dirt_edge = dirt * 0.86

    # Protect water & dark roofs
    hsv = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    water = (hsv[:, :, 0] >= 90) & (hsv[:, :, 0] <= 130) & (hsv[:, :, 1] > 55) & (hsv[:, :, 2] < 165)
    dark = hsv[:, :, 2] < 50
    alpha[water | dark] = 0
    alpha[red_zone > 0] = 0

    # Stronger opacity through forest so trees don't speck through
    forest = forestish_mask(np.clip(out, 0, 255).astype(np.uint8)) > 0
    alpha_use = alpha.copy()
    alpha_use[forest & (alpha > 0.15)] = np.maximum(alpha_use[forest & (alpha > 0.15)], 0.92)

    painted = dirt * (1 - edge[..., None]) + dirt_edge * edge[..., None]
    a = alpha_use[..., None]
    # Near-opaque paint
    out = out * (1 - a * 0.98) + painted * (a * 0.98)

    return np.clip(out, 0, 255).astype(np.uint8)


def scrub_ink(work: np.ndarray, near: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    blue = (h >= 95) & (h <= 135) & (s > 110) & (v > 70)
    red = ((h <= 10) | (h >= 170)) & (s > 110) & (v > 70)
    ink = ((blue | red) & (near > 0)).astype(np.uint8) * 255
    if cv2.countNonZero(ink) == 0:
        return work
    return cv2.inpaint(work, dilate(ink, 4), 4, cv2.INPAINT_TELEA)


def main() -> None:
    if (not MARKUP_COPY.exists()) or (
        MARKED.exists() and MARKUP_COPY.stat().st_mtime < MARKED.stat().st_mtime - 1
    ):
        # Only overwrite markup copy if marked is newer AND markup doesn't already
        # look like the marked file. Prefer never clobbering an older markup backup
        # once user edits resume-c again — here we keep existing markup if present.
        if not MARKUP_COPY.exists():
            shutil.copy2(MARKED, MARKUP_COPY)
            print(f"copied markup -> {MARKUP_COPY}")
        else:
            print(f"keeping existing markup copy {MARKUP_COPY}")
    else:
        if not MARKUP_COPY.exists():
            shutil.copy2(MARKED, MARKUP_COPY)
        print(f"markup copy: {MARKUP_COPY}")

    # Always ensure markup exists from marked if missing
    if not MARKUP_COPY.exists():
        shutil.copy2(MARKED, MARKUP_COPY)

    src_path = MARKUP_COPY if MARKUP_COPY.exists() else MARKED
    marked = cv2.imread(str(src_path))
    assert marked is not None
    h, w = marked.shape[:2]
    print(f"size {w}x{h} from {src_path.name}")

    clean = None
    if CLEAN_REF.exists():
        clean = cv2.imread(str(CLEAN_REF))
        if clean is not None and clean.shape[:2] != (h, w):
            clean = cv2.resize(clean, (w, h), interpolation=cv2.INTER_AREA)
        print("clean_ref ok")

    blue = vivid_blue_mask(marked)
    red = vivid_red_mask(marked)
    blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    print(f"blue={cv2.countNonZero(blue)} red={cv2.countNonZero(red)}")

    dbg = marked.copy()
    dbg[blue > 0] = (255, 180, 0)
    dbg[red > 0] = (0, 0, 255)
    cv2.imwrite(str(MAPS / "_debug-resume-e-masks.png"), dbg)

    ink = cv2.bitwise_or(blue, red)

    # 1) Strip ink using clean ref
    work = marked.copy()
    thin = dilate(ink, 4)
    if clean is not None:
        soft = cv2.GaussianBlur(thin, (5, 5), 0).astype(np.float32) / 255.0
        wf = work.astype(np.float32)
        cf = clean.astype(np.float32)
        for c in range(3):
            wf[:, :, c] = wf[:, :, c] * (1 - soft) + cf[:, :, c] * soft
        work = np.clip(wf, 0, 255).astype(np.uint8)
    else:
        work = cv2.inpaint(work, thin, 4, cv2.INPAINT_TELEA)

    # 2) RED erase — widen to full road under stroke
    red_zone = dilate(red, 31)
    red_zone = (cv2.GaussianBlur(red_zone, (17, 17), 0) > 35).astype(np.uint8) * 255
    # Protect water
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    water = (hsv[:, :, 0] >= 90) & (hsv[:, :, 0] <= 130) & (hsv[:, :, 1] > 50) & (hsv[:, :, 2] < 160)
    red_zone[water] = 0
    work = local_terrain_fill(work, red_zone)

    # 3) BLUE paint
    work = paint_roads_along_blue(work, blue, clean, red_zone)

    # 4) Scrub leftover ink near markup
    near = dilate(ink, 30)
    work = scrub_ink(work, near)

    # 5) Second pass: any remaining roadish ghosts in red zone → terrain again
    soft_red = cv2.GaussianBlur(red_zone, (21, 21), 0).astype(np.float32) / 255.0
    ghost = (soft_red > 0.35) & (roadish_mask(work) > 0)
    if ghost.any():
        gmask = dilate(ghost.astype(np.uint8) * 255, 7)
        work = local_terrain_fill(work, gmask)

    # 6) Ensure blue corridors look road-like (boost thin spots)
    sk = skeletonize(blue)
    blue_body = dilate(sk if cv2.countNonZero(sk) > 80 else blue, 17)
    blue_body = cv2.bitwise_and(blue_body, cv2.bitwise_not(red_zone))
    weak = (blue_body > 0) & (roadish_mask(work) == 0)
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    water = (hsv[:, :, 0] >= 90) & (hsv[:, :, 0] <= 130) & (hsv[:, :, 1] > 55)
    weak = weak & ~water
    if weak.any():
        atlas = sample_road_patch(work, dilate(blue, 8))
        dirt = stamp_texture((h, w), atlas, np.random.default_rng(99))
        wm = cv2.GaussianBlur(weak.astype(np.uint8) * 255, (7, 7), 0).astype(np.float32) / 255.0
        wf = work.astype(np.float32)
        a = np.clip(wm * 1.1, 0, 1)[..., None]
        wf = wf * (1 - a * 0.97) + dirt * (a * 0.97)
        work = np.clip(wf, 0, 255).astype(np.uint8)

    cv2.imwrite(str(OUT_LIVE), work)
    cv2.imwrite(str(OUT_BACKUP), work)
    print(f"wrote {OUT_LIVE}")
    print(f"wrote {OUT_BACKUP}")

    qb = vivid_blue_mask(work)
    qr = vivid_red_mask(work)
    qb = cv2.bitwise_and(qb, near)
    qr = cv2.bitwise_and(qr, near)
    print(f"QA leftover blue={cv2.countNonZero(qb)} red={cv2.countNonZero(qr)}")
    print(
        "roadish redzone",
        int(((roadish_mask(work) > 0) & (red_zone > 0)).sum()),
        "roadish bluezone",
        int(((roadish_mask(work) > 0) & (blue_body > 0)).sum()),
        "blue_body",
        int((blue_body > 0).sum()),
    )


if __name__ == "__main__":
    main()
