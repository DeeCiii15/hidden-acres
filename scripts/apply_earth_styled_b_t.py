"""Opaque capital-T wings + bridal join + groom north on earth-styled-b-base."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public" / "maps"
LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
BASE = MAPS / "hidden-acres-grounds-illustrated-v-map-earth-styled-b-base.png"
OUT_B = MAPS / "hidden-acres-grounds-illustrated-v-map-earth-styled-b.png"
QA = MAPS / "_qa-crops-earth-b"

# Stem edges from tip survey (longest terra run ~480–564 at y=1035)
STEM_L, STEM_R = 472, 556
WY0, WY1 = 996, 1052
WEST_TIP = 450  # east of groom east face (~444) — visible lawn gap
EAST_TIP = 625
GROOM_SHIFT = 20


def ch(rgb: np.ndarray):
    return rgb[..., 0].astype(np.int16), rgb[..., 1].astype(np.int16), rgb[..., 2].astype(np.int16)


def is_pin(rgb: np.ndarray) -> np.ndarray:
    r, g, b = ch(rgb)
    return (g > 45) & (g < 155) & (r < 95) & (b < 95) & (g > r + 14) & (g > b + 10)


def is_terra(rgb: np.ndarray) -> np.ndarray:
    r, g, b = ch(rgb)
    return (
        (r > 95)
        & (r < 215)
        & (g > 40)
        & (g < 165)
        & (b > 20)
        & (b < 125)
        & (r > g + 16)
        & (r > b + 28)
    )


def grey_roof(rgb: np.ndarray) -> np.ndarray:
    r, g, b = ch(rgb)
    lum = (r.astype(np.int32) + g + b) // 3
    chroma = np.maximum(np.maximum(np.abs(r - g), np.abs(g - b)), np.abs(r - b))
    return (lum > 70) & (lum < 150) & (chroma < 32) & ~((g > r + 8) & (g > b + 6))


def move_groom(work: np.ndarray) -> np.ndarray:
    gr = grey_roof(work)
    zone = np.zeros(work.shape[:2], np.uint8)
    zone[900:1030, 360:440] = gr[900:1030, 360:440].astype(np.uint8)
    zone = cv2.morphologyEx(zone, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(zone, 8)
    cid = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    roof_cc = (lab == cid).astype(np.uint8)
    dil = cv2.dilate(roof_cc, np.ones((19, 15), np.uint8), iterations=1)
    r, g, b = ch(work)
    lum = (r.astype(np.int32) + g + b) // 3
    wall = (
        (r > 60)
        & (r < 175)
        & (g > 40)
        & (g < 135)
        & (b > 22)
        & (b < 105)
        & (r > b + 10)
        & ~((g > r + 10) & (g > b + 8))
    )
    steps = (lum > 105) & (lum < 215) & (np.abs(r - g) < 40) & (r > 90)
    pond = (b > 85) & (b > r + 12) & (g > r - 5)
    bush = (g > r + 3) & (g > b + 2) & (g > 48) & (g < 180) & (r < 155)
    hard = ((roof_cc > 0) | ((wall | steps | is_pin(work)) & (dil > 0))) & ~pond
    near = cv2.dilate(hard.astype(np.uint8), np.ones((7, 7), np.uint8), iterations=1)
    plant = bush & (near > 0) & ~pond
    alpha = cv2.GaussianBlur((hard | plant).astype(np.float32), (0, 0), 0.9)
    alpha = np.clip(alpha, 0, 1)
    alpha = np.where(hard, np.maximum(alpha, 0.96), alpha)
    alpha[:, :355] = 0
    alpha[:, 448:] = 0
    alpha[:885] = 0
    alpha[1040:] = 0

    ys, xs = np.where(alpha > 0.3)
    y0, y1 = max(0, int(ys.min()) - 3), min(work.shape[0], int(ys.max()) + 4)
    x0, x1 = max(0, int(xs.min()) - 3), min(work.shape[1], int(xs.max()) + 4)
    crop = work[y0:y1, x0:x1].copy()
    a = alpha[y0:y1, x0:x1]
    ny0 = y0 - GROOM_SHIFT

    vac = np.zeros(work.shape[:2], np.uint8)
    vac[y0:y1, x0:x1] = (a > 0.35).astype(np.uint8) * 255
    nc = np.zeros_like(vac)
    nc[ny0 : ny0 + (y1 - y0), x0:x1] = (a > 0.35).astype(np.uint8) * 255
    only = cv2.subtract(vac, nc)
    if only.any():
        inp = cv2.inpaint(work, only, 5, cv2.INPAINT_TELEA)
        lawn = work[1080:1160, 300:380].astype(np.float32)
        lh, lw = lawn.shape[:2]
        yy, xx = np.where(only > 0)
        for y, x in zip(yy, xx):
            lp = lawn[(y * 3) % lh, (x * 5) % lw]
            inp[y, x] = (0.4 * inp[y, x].astype(np.float32) + 0.6 * lp).astype(np.uint8)
        work = inp

    dest = work[ny0 : ny0 + (y1 - y0), x0:x1].astype(np.float32)
    work[ny0 : ny0 + (y1 - y0), x0:x1] = np.clip(
        dest * (1 - a[..., None]) + crop.astype(np.float32) * a[..., None], 0, 255
    ).astype(np.uint8)
    print(f"groom y {y0}-{y1} -> {ny0}-{ny0 + y1 - y0} x {x0}-{x1}")
    return work


def roof_src(work: np.ndarray) -> np.ndarray:
    src = work[1200:1280, 465:525].copy()
    pin = is_pin(src)
    if pin.any():
        roof = is_terra(src)
        med = np.median(src[roof], axis=0) if roof.any() else np.array([145.0, 98.0, 58.0])
        src = src.copy()
        src[pin] = med
    return src


def paint_solid_wing(
    out: np.ndarray,
    src: np.ndarray,
    x0: int,
    x1: int,
    y0: int,
    y1: int,
    *,
    connect_bridal: bool = False,
    fade_west_tip: bool = False,
) -> None:
    H, W = out.shape[:2]
    x0, x1 = max(0, x0), min(W, x1)
    y0, y1 = max(0, y0), min(H, y1)
    ww, hh = x1 - x0, y1 - y0
    grain = cv2.resize(src, (ww, hh), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    mid = src[src.shape[0] // 3 : 2 * src.shape[0] // 3]
    slab = np.zeros((hh, ww, 3), np.float32)
    for x in range(ww):
        col = mid[:, x % mid.shape[1]]
        slab[:, x] = cv2.resize(col[:, None, :], (1, hh), interpolation=cv2.INTER_LINEAR)[:, 0, :]
    slab = 0.5 * slab + 0.5 * grain
    cy = hh // 2
    slab[cy - 1 : cy + 2] *= 0.86
    slab[-5:] *= 0.78
    slab[:3] *= 0.88

    yy = np.linspace(-1, 1, hh, dtype=np.float32)
    profile = np.clip(1.05 - np.abs(yy) * 0.92, 0, 1).astype(np.float32)
    alpha = np.repeat(profile[:, None], ww, axis=1)
    tip = np.ones(ww, np.float32)
    if fade_west_tip:
        tip[:5] = np.linspace(0.25, 1.0, 5)
        tip[-3:] = np.linspace(1.0, 0.75, 3)
    else:
        tip[:3] = np.linspace(0.6, 1.0, 3)
        tip[-4:] = np.linspace(1.0, 0.55, 4)
    alpha *= tip[None, :]
    alpha = np.clip(cv2.GaussianBlur(alpha * 1.75, (0, 0), 0.4), 0, 1)

    dest = out[y0:y1, x0:x1]
    a = alpha.copy()
    a[is_pin(dest)] = 0.0
    dr, dg, db = ch(dest)
    court = (dr > 165) & (dg > 150) & (db > 105) & (np.abs(dr.astype(int) - dg) < 35)
    a[court] *= 0.12
    if connect_bridal:
        gr = grey_roof(dest)
        a[gr] = np.maximum(a[gr], 0.88)
    else:
        a[grey_roof(dest)] *= 0.04

    # Force near-opaque on lawn / path
    lawnish = ~is_terra(dest) & ~grey_roof(dest) & ~court & ~is_pin(dest)
    a[lawnish] = np.maximum(a[lawnish], (profile[:, None] * tip[None, :])[lawnish] * 0.98)

    # Keep west tip clear of groom (east face ~444)
    if fade_west_tip:
        for lx in range(ww):
            if x0 + lx < 448:
                a[:, lx] = 0.0

    out[y0:y1, x0:x1] = np.clip(
        dest.astype(np.float32) * (1 - a[..., None]) + slab * a[..., None], 0, 255
    ).astype(np.uint8)
    print(f"wing ({x0},{y0})-({x1},{y1}) a_mean={a.mean():.2f} a_max={a.max():.2f}")


def main() -> None:
    base = np.array(Image.open(BASE).convert("RGB"))
    work = base.copy()
    work = move_groom(work)
    src = roof_src(work)

    paint_solid_wing(work, src, WEST_TIP, STEM_L + 4, WY0, WY1, fade_west_tip=True)
    paint_solid_wing(work, src, STEM_R - 4, EAST_TIP, WY0, WY1, connect_bridal=True)
    paint_solid_wing(work, src, STEM_L - 2, STEM_R + 2, WY0 + 1, WY1 - 1)

    # Enforce lawn gap between west wing tip and groom east face
    gap = np.zeros(work.shape[:2], np.float32)
    gap[WY0:WY1, 440:450] = 1.0
    gap = cv2.GaussianBlur(gap, (0, 0), 1.2)
    lawn = base[1080:1160, 300:380].astype(np.float32)
    lh, lw = lawn.shape[:2]
    ys, xs = np.where(gap > 0.05)
    fill = work.copy().astype(np.float32)
    for y, x in zip(ys, xs):
        # Prefer original base lawn/path in this strip
        fill[y, x] = 0.35 * work[y, x].astype(np.float32) + 0.65 * base[y, x].astype(np.float32)
        # If still too terra, force lawn tile
        pr, pg, pb = fill[y, x]
        if pr > pg + 16 and pr > pb + 28:
            fill[y, x] = lawn[(y * 3) % lh, (x * 5) % lw]
    a = gap[..., None]
    work = np.clip(work.astype(np.float32) * (1 - a) + fill * a, 0, 255).astype(np.uint8)

    final = Image.fromarray(work)
    final.save(LIVE)
    final.save(OUT_B)
    QA.mkdir(exist_ok=True)
    final.crop((280, 860, 720, 1160)).save(QA / "after-cluster.png")
    final.crop((400, 980, 650, 1100)).save(QA / "after-t.png")
    final.crop((320, 850, 470, 1040)).save(QA / "after-groom.png")
    final.crop((480, 900, 700, 1080)).save(QA / "after-bridal-join.png")
    Image.open(BASE).crop((400, 980, 650, 1100)).save(QA / "before-t.png")

    d = np.abs(work.astype(np.int16) - base.astype(np.int16)).max(axis=-1)
    vis = base[860:1120, 300:700].copy()
    m = d[860:1120, 300:700] > 12
    vis[m] = np.clip(vis[m].astype(int) * 0.3 + np.array([255, 0, 255]), 0, 255)
    Image.fromarray(vis.astype(np.uint8)).save(QA / "diff-cluster.png")
    print(f"changed={(d > 2).sum()}")
    print("done")


if __name__ == "__main__":
    main()
