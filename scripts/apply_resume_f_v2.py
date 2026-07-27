"""Apply resume-c blue/red markup with clean-texture cloning (no Telea smears).

Base: unmarked assets resume-c (pixel-exact outside edit zones).
RED: sample grass pixels from nearby clean lawn → textured fill.
BLUE: sample road pixels from clean gravel atlas → stamp along skeleton
      with soft distance-based alpha (and optional gen2 guidance for coverage).
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


def collect_pixels(img: np.ndarray, mask: np.ndarray, max_n: int = 8000) -> np.ndarray:
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return np.zeros((0, 3), np.uint8)
    if len(xs) > max_n:
        idx = np.linspace(0, len(xs) - 1, max_n).astype(int)
        ys, xs = ys[idx], xs[idx]
    return img[ys, xs]


def fill_mask_from_pixels(
    img: np.ndarray,
    alpha: np.ndarray,
    palette: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """Per-pixel textured fill using random samples from palette (preserves grain)."""
    if palette.shape[0] < 10:
        return img
    out = img.astype(np.float32)
    ys, xs = np.where(alpha > 0.02)
    n = len(xs)
    if n == 0:
        return img
    # batch sample
    picks = rng.integers(0, palette.shape[0], size=n)
    pix = palette[picks].astype(np.float32)
    pix += rng.normal(0, 2.2, pix.shape).astype(np.float32)
    pix = np.clip(pix, 0, 255)
    a = alpha[ys, xs][:, None]
    out[ys, xs] = out[ys, xs] * (1 - a) + pix * a
    return np.clip(out, 0, 255).astype(np.uint8)


def build_red_erase_mask(clean: np.ndarray, red: np.ndarray) -> np.ndarray:
    """Widen red strokes to cover road under them (roadish ∩ dilated red)."""
    # Core: road pixels near red stroke
    near = dilate(red, 28)
    core = ((roadish(clean) > 0) & (near > 0)).astype(np.uint8) * 255
    # Also include dilated red itself so ink footprint clears
    core = cv2.bitwise_or(core, dilate(red, 15))
    # Grow slightly to cover soft road edges
    core = dilate(core, 9)
    core[water(clean)] = 0
    # Soften binary
    return core


def build_blue_body(blue: np.ndarray, width: int = 18) -> tuple[np.ndarray, np.ndarray]:
    blue_bin = cv2.morphologyEx(
        (blue > 0).astype(np.uint8) * 255,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
    )
    sk = skeletonize(blue_bin)
    if cv2.countNonZero(sk) < 80:
        sk = blue_bin
    body = dilate(sk, width)
    body = cv2.bitwise_or(body, dilate(blue_bin, max(9, width // 2)))
    dist = cv2.distanceTransform((body > 0).astype(np.uint8), cv2.DIST_L2, 5)
    alpha = np.zeros(body.shape, np.float32)
    inside = body > 0
    if inside.any():
        dmax = max(float(dist[inside].max()), 1.0)
        t = dist / dmax
        # Opaque center, soft outer ~25% of radius
        alpha[inside] = np.clip((t - 0.05) / 0.95, 0, 1)[inside]
        alpha = np.power(alpha, 0.55)
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
    return body, np.clip(alpha, 0, 1)


def sample_road_palette(clean: np.ndarray, avoid: np.ndarray) -> np.ndarray:
    h, w = clean.shape[:2]
    rm = roadish(clean).astype(bool)
    rm[avoid > 0] = False
    yy, xx = np.mgrid[0:h, 0:w]
    # Prefer approach road south of courtyard / parking connector
    zone = (yy > int(h * 0.52)) & (yy < int(h * 0.82)) & (xx > int(w * 0.32)) & (xx < int(w * 0.65))
    cand = rm & zone
    if cand.sum() < 500:
        cand = rm
    return collect_pixels(clean, cand.astype(np.uint8) * 255, 12000)


def sample_grass_palette_near(
    clean: np.ndarray,
    erase: np.ndarray,
    rng: np.random.Generator,
) -> dict[int, np.ndarray]:
    """Per connected component, gather nearby grass palette."""
    h, w = clean.shape[:2]
    avoid = dilate(erase, 3)
    grass = (grassish(clean) > 0) & (avoid == 0) & (roadish(clean) == 0) & ~water(clean)
    # Prefer brighter lawn (not deep forest)
    b, g, r = cv2.split(clean.astype(np.float32))
    lum = 0.114 * b + 0.587 * g + 0.299 * r
    lawn = grass & (lum > 85)

    n, labels, stats, _ = cv2.connectedComponentsWithStats(erase, 8)
    palettes: dict[int, np.ndarray] = {}
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 20:
            continue
        x0 = stats[i, cv2.CC_STAT_LEFT]
        y0 = stats[i, cv2.CC_STAT_TOP]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]
        pad = max(60, int(max(bw, bh) * 1.2))
        rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
        rx1, ry1 = min(w, x0 + bw + pad), min(h, y0 + bh + pad)
        local = np.zeros((h, w), np.uint8)
        local[ry0:ry1, rx0:rx1] = lawn[ry0:ry1, rx0:rx1].astype(np.uint8) * 255
        # Prefer ring around blob
        blob = (labels == i).astype(np.uint8) * 255
        ring = dilate(blob, pad // 2)
        ring = cv2.bitwise_and(ring, cv2.bitwise_not(blob))
        cand = cv2.bitwise_and(local, ring)
        if cv2.countNonZero(cand) < 200:
            cand = local
        pal = collect_pixels(clean, cand, 6000)
        if pal.shape[0] < 50:
            # global lawn fallback
            pal = collect_pixels(clean, lawn.astype(np.uint8) * 255, 6000)
        palettes[i] = pal
        _ = rng  # silence
    return palettes, labels, n


def erase_roads_textured(clean: np.ndarray, erase: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    alpha = soft_alpha(erase, 13)
    # Sharper core
    core = soft_alpha(erase, 5)
    alpha = np.maximum(alpha * 0.85, core * 0.98)

    palettes, labels, n = sample_grass_palette_near(clean, erase, rng)
    out = clean.copy()
    for i in range(1, n):
        if i not in palettes:
            continue
        comp = (labels == i).astype(np.uint8) * 255
        a = alpha * (cv2.GaussianBlur(comp, (9, 9), 0).astype(np.float32) / 255.0)
        out = fill_mask_from_pixels(out, a, palettes[i], rng)

    # Any remaining roadish in erase → second pass with global lawn
    still = (soft_alpha(erase, 9) > 0.5) & (roadish(out) > 0) & ~water(out)
    if still.any():
        b, g, r = cv2.split(clean.astype(np.float32))
        lum = 0.114 * b + 0.587 * g + 0.299 * r
        lawn = (grassish(clean) > 0) & (roadish(clean) == 0) & (lum > 85) & ~water(clean)
        lawn[dilate(erase, 2) > 0] = False
        pal = collect_pixels(clean, lawn.astype(np.uint8) * 255, 8000)
        a2 = soft_alpha(still.astype(np.uint8) * 255, 9)
        out = fill_mask_from_pixels(out, a2, pal, rng)
    return out


def paint_roads_textured(
    work: np.ndarray,
    blue: np.ndarray,
    palette: np.ndarray,
    protect: np.ndarray,
    rng: np.random.Generator,
    width: int = 17,
) -> np.ndarray:
    body, alpha = build_blue_body(blue, width=width)
    alpha = alpha.copy()
    alpha[protect > 0] = 0
    alpha[water(work)] = 0

    # Edge darkening baked into palette mix
    out = fill_mask_from_pixels(work, alpha * 0.97, palette, rng)

    # Darken lip slightly for gravel edge
    edge = np.clip(alpha * (1.0 - alpha) * 4.0, 0, 1)
    if edge.any():
        darkened = out.astype(np.float32) * 0.90
        a = edge[..., None]
        out = np.clip(out.astype(np.float32) * (1 - a * 0.55) + darkened * (a * 0.55), 0, 255).astype(
            np.uint8
        )
    return out, body, alpha


def main() -> None:
    QA.mkdir(exist_ok=True)
    clean = cv2.imread(str(CLEAN))
    markup = cv2.imread(str(MARKUP))
    assert clean is not None and markup is not None
    h, w = clean.shape[:2]
    if markup.shape[:2] != (h, w):
        markup = cv2.resize(markup, (w, h), interpolation=cv2.INTER_AREA)

    if BAD_E.exists() and not BAD_E_ASIDE.exists():
        shutil.copy2(BAD_E, BAD_E_ASIDE)
        print(f"aside {BAD_E_ASIDE.name}")

    blue = vivid_blue_mask(markup)
    red = vivid_red_mask(markup)
    print(f"blue={cv2.countNonZero(blue)} red={cv2.countNonZero(red)}")

    rng = np.random.default_rng(42)

    # 1) RED erase with textured grass from clean
    erase = build_red_erase_mask(clean, red)
    print(f"erase px={cv2.countNonZero(erase)}")
    work = erase_roads_textured(clean, erase, rng)

    # 2) BLUE paint with road pixel palette from clean
    road_pal = sample_road_palette(clean, dilate(blue, 10))
    print(f"road palette n={road_pal.shape[0]}")
    work, blue_body, blue_alpha = paint_roads_textured(
        work, blue, road_pal, erase, rng, width=17
    )

    # Optional: where gen2 has strong road and we are still weak, boost with clean palette
    # (do not paste gen2 pixels — they drift). Just widen paint.
    weak = (blue_body > 0) & (roadish(work) == 0) & (erase == 0) & ~water(work)
    if weak.any():
        print(f"weak blue follow-up px={int(weak.sum())}")
        a = soft_alpha(dilate(weak.astype(np.uint8) * 255, 5), 9) * 0.95
        a[erase > 0] = 0
        work = fill_mask_from_pixels(work, a, road_pal, rng)

    # 3) Scrub ink leftovers near markup
    near = dilate(cv2.bitwise_or(blue, red), 24)
    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    hh, ss, vv = cv2.split(hsv)
    ink = (
        ((hh >= 95) & (hh <= 135) & (ss > 110) & (vv > 70))
        | (((hh <= 10) | (hh >= 170)) & (ss > 110) & (vv > 70))
    ) & (near > 0)
    if ink.any():
        # Replace ink with local clean/work neighborhood samples
        a = soft_alpha(dilate(ink.astype(np.uint8) * 255, 3), 5)
        # use surrounding non-ink pixels as palette
        ok = ~ink & (near > 0)
        pal = collect_pixels(work, ok.astype(np.uint8) * 255, 4000)
        if pal.shape[0] > 20:
            work = fill_mask_from_pixels(work, a, pal, rng)

    # 4) Final red ghost cleanup
    soft_e = soft_alpha(erase, 11)
    ghost = (soft_e > 0.45) & (roadish(work) > 0) & ~water(work)
    if ghost.any():
        print(f"final ghost px={int(ghost.sum())}")
        b, g, r = cv2.split(clean.astype(np.float32))
        lum = 0.114 * b + 0.587 * g + 0.299 * r
        lawn = (grassish(clean) > 0) & (roadish(clean) == 0) & (lum > 85)
        lawn[dilate(erase, 2) > 0] = False
        pal = collect_pixels(clean, lawn.astype(np.uint8) * 255, 8000)
        work = fill_mask_from_pixels(work, soft_alpha(ghost.astype(np.uint8) * 255, 7), pal, rng)

    cv2.imwrite(str(OUT_LIVE), work)
    cv2.imwrite(str(OUT_BACKUP), work)
    print(f"wrote {OUT_LIVE.name} + {OUT_BACKUP.name}")

    # QA
    qb = vivid_blue_mask(work)
    qr = vivid_red_mask(work)
    qb = cv2.bitwise_and(qb, near)
    qr = cv2.bitwise_and(qr, near)
    print(f"QA ink blue={cv2.countNonZero(qb)} red={cv2.countNonZero(qr)}")
    print(
        "roadish erase",
        int(((roadish(work) > 0) & (erase > 0)).sum()),
        "roadish bluebody",
        int(((roadish(work) > 0) & (blue_body > 0)).sum()),
        "/",
        int((blue_body > 0).sum()),
    )
    edit = cv2.bitwise_or(dilate(blue_body, 3), dilate(erase, 3))
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
        cv2.imwrite(str(QA / f"v2-{name}.png"), grid)
    cv2.imwrite(str(QA / "v2-full.png"), work)
    # debug masks
    dbg = clean.copy()
    dbg[erase > 0] = (40, 40, 200)
    dbg[blue_body > 0] = (200, 160, 40)
    cv2.imwrite(str(QA / "v2-masks.png"), dbg)


if __name__ == "__main__":
    main()
