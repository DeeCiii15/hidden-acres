"""Surgical topology edit: resume-b -> resume-d / live (v2).

Fixes from v1: keep vehicle road WEST of pond (never through water),
stronger water mask, cleaner courtyard-center path + silo fork,
small groom north nudge with grass gap.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public/maps"
SRC = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-b.png"
OUT_LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
OUT_D = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-d.png"
DEBUG = MAPS / "_qa-crops-resume-d" / "resume-d-edit-debug.png"
ASSETS = Path(
    r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets"
    r"\hidden-acres-grounds-illustrated-v-map-resume-d.png"
)


def bezier(p0, p1, p2, p3, n: int = 800) -> np.ndarray:
    ts = np.linspace(0, 1, n)
    p0, p1, p2, p3 = map(lambda p: np.array(p, float), (p0, p1, p2, p3))
    return np.array(
        [
            ((1 - t) ** 3) * p0
            + 3 * ((1 - t) ** 2) * t * p1
            + 3 * (1 - t) * (t**2) * p2
            + (t**3) * p3
            for t in ts
        ]
    )


def polyline(pts, n_per: int = 40) -> np.ndarray:
    out = []
    for i in range(len(pts) - 1):
        a = np.array(pts[i], float)
        b = np.array(pts[i + 1], float)
        for t in np.linspace(0, 1, n_per, endpoint=False):
            out.append(a * (1 - t) + b * t)
    out.append(np.array(pts[-1], float))
    return np.array(out)


def soft_stamp(mask: np.ndarray, curve: np.ndarray, radii) -> None:
    h, w = mask.shape
    yy2, xx2 = np.ogrid[-30:31, -30:31]
    for x, y in curve:
        ix, iy = int(round(x)), int(round(y))
        for rad, a in radii:
            stamp = ((xx2 * xx2 + yy2 * yy2) <= rad * rad).astype(np.float32) * a
            y0, y1 = iy - 30, iy + 31
            x0, x1 = ix - 30, ix + 31
            if y0 < 0 or x0 < 0 or y1 > h or x1 > w:
                continue
            mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], stamp)


def blur01(mask: np.ndarray, r: float = 1.6) -> np.ndarray:
    return (
        np.array(
            Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(r)
            )
        ).astype(np.float32)
        / 255.0
    )


def water_mask(work: np.ndarray) -> np.ndarray:
    """Resume-b pond is very dark teal, not bright blue."""
    r = work[..., 0].astype(np.int16)
    g = work[..., 1].astype(np.int16)
    b = work[..., 2].astype(np.int16)
    teal = (b > 50) & (b > r + 18) & (g < 115) & (r < 55)
    m = teal.astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((9, 9), np.uint8), iterations=2)
    return m > 0


def sample_dirt(work: np.ndarray) -> np.ndarray:
    patches = [work[1180:1280, 430:520], work[200:280, 700:820], work[1050:1120, 240:330]]
    samples = []
    for patch in patches:
        r, g, b = patch[..., 0], patch[..., 1], patch[..., 2]
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        sel = (lum > 125) & (r > b + 8) & (r >= g - 8) & (g > 90)
        if sel.sum() > 30:
            samples.append(patch[sel])
    if samples:
        return np.median(np.concatenate(samples, axis=0), axis=0)
    return np.array([168.0, 150.0, 112.0])


def sample_lawn(work: np.ndarray) -> np.ndarray:
    return work[430:560, 530:680].copy()


def erase_to_lawn(work: np.ndarray, erase_a: np.ndarray, lawn_tile: np.ndarray, rng) -> np.ndarray:
    fill = work.copy()
    th, tw = lawn_tile.shape[:2]
    ys, xs = np.where(erase_a > 0.03)
    for y, x in zip(ys, xs):
        ty = (y * 3 + 17 + int(rng.integers(-8, 9))) % max(th - 1, 1)
        tx = (x * 5 + 29 + int(rng.integers(-8, 9))) % max(tw - 1, 1)
        pix = lawn_tile[ty, tx].astype(np.float32).copy()
        pix[1] = np.clip(pix[1] * 1.04 + 4, 0, 255)
        pix[0] = np.clip(pix[0] * 0.97, 0, 255)
        fill[y, x] = pix
    fill = np.array(
        Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(0.7)
        )
    ).astype(np.float32)
    return work * (1 - erase_a[..., None]) + fill * erase_a[..., None]


def paint_path(
    work: np.ndarray,
    path_mask: np.ndarray,
    dirt_color: np.ndarray,
    rng,
    strength: float,
    forbid: np.ndarray | None = None,
) -> np.ndarray:
    pm = path_mask.copy()
    if forbid is not None:
        pm[forbid] = 0
    dirt_layer = np.clip(dirt_color + rng.normal(0, 3.5, work.shape), 0, 255)
    return work * (1 - pm[..., None] * strength) + dirt_layer * (pm[..., None] * strength)


def move_grooms(work: np.ndarray, rng) -> np.ndarray:
    """Nudge Groom's Quarters slightly north; leave a small grass gap south of it."""
    # Measured roof centroid on resume-b ~ (435, 605)
    x0, y0, x1, y1 = 370, 555, 500, 680
    shift = 36
    crop = work[y0:y1, x0:x1].copy()

    # Soft alpha preferring roof/wall pixels
    hh, ww = crop.shape[:2]
    cr, cg, cb = crop[..., 0], crop[..., 1], crop[..., 2]
    buildingish = (
        ((cr > 85) & (cr < 190) & (cr > cg + 8) & (cr > cb + 15))  # roof
        | ((cr > 110) & (cg > 95) & (cb > 70) & (cr < 200) & ((cr + cg + cb) > 300))  # walls
    )
    alpha = buildingish.astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)
    alpha = np.clip(alpha * 1.35, 0, 1)

    # Erase old footprint lightly (only where buildingish) then inpaint
    bgr = cv2.cvtColor(np.clip(work, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    mask = np.zeros(bgr.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = (alpha > 0.35).astype(np.uint8) * 255
    # protect courtyard east
    mask[580:720, 500:620] = 0
    # protect pond west
    mask[:, :300] = np.minimum(mask[:, :300], 0)
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)
    inpainted = cv2.inpaint(bgr, mask, 4, cv2.INPAINT_TELEA)
    rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB).astype(np.float32)

    # Lawn soften over erased footprint
    erase_a = blur01(mask.astype(np.float32) / 255.0, 2.0)
    lawn = sample_lawn(work)
    rgb = erase_to_lawn(rgb, erase_a * 0.55, lawn, rng)

    # Paste shifted north
    ny0, ny1 = y0 - shift, y1 - shift
    if ny0 < 0:
        return work
    dest = rgb[ny0:ny1, x0:x1]
    dest[:] = dest * (1 - alpha[..., None]) + crop * alpha[..., None]
    rgb[ny0:ny1, x0:x1] = dest

    # Small grass gap south of moved building (between groom and ballroom)
    gap = np.zeros(rgb.shape[:2], np.float32)
    cv2.rectangle(gap, (390, 648), (480, 678), 1.0, -1)
    gap = blur01(gap, 1.8)
    # don't erase courtyard paving
    gap[600:720, 500:650] = 0
    rgb = erase_to_lawn(rgb, gap * 0.85, lawn, rng)
    return rgb


def main() -> None:
    rng = np.random.default_rng(29)
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    assert (w, h) == (1024, 1536)
    work = np.array(img).astype(np.float32)
    lawn = sample_lawn(work)
    dirt = sample_dirt(work)
    forbid_water = water_mask(work)

    # 1) Groom nudge
    work = move_grooms(work, rng)
    forbid_water = water_mask(work)  # refresh

    # 2) Erase conflicting bits (chapel spur + old corner path)
    erase = np.zeros((h, w), np.float32)
    soft_stamp(erase, bezier((600, 190), (520, 230), (460, 280), (430, 320)), ((9, 1), (14, 0.5), (18, 0.2)))
    soft_stamp(erase, bezier((430, 340), (455, 430), (480, 530), (505, 610)), ((5, 1), (8, 0.45), (11, 0.2)))
    soft_stamp(erase, bezier((505, 610), (515, 625), (525, 635), (535, 645)), ((6, 1), (9, 0.4)))
    erase = blur01(erase, 1.8)
    erase[forbid_water] = 0
    work = erase_to_lawn(work, erase, lawn, rng)

    # 3) Continuous vehicle road — WEST of pond only (pond west edge ~x115-150)
    veh = np.zeros((h, w), np.float32)
    west_pts = [
        (245, 1140),  # parking NW
        (185, 1040),
        (130, 960),
        (100, 880),
        (92, 800),   # west of pond lobe (edge ~115+)
        (90, 720),
        (92, 640),
        (98, 560),
        (115, 470),
        (150, 380),  # NW approach to chapel back
        (230, 300),
        (320, 255),  # behind chapel
        (420, 245),
        (520, 265),  # mid-field cut
        (620, 310),
        (720, 380),
        (790, 470),
        (825, 560),  # join east approach
    ]
    soft_stamp(veh, polyline(west_pts, n_per=60), ((6.5, 1.0), (10, 0.55), (13, 0.2)))
    veh = blur01(veh, 1.4)
    veh[forbid_water] = 0
    work = paint_path(work, veh, dirt, rng, strength=0.9, forbid=forbid_water)

    # 4) Pedestrian chapel -> courtyard CENTER (fountain ~544,640) + silo fork + fade stub
    ped = np.zeros((h, w), np.float32)
    soft_stamp(
        ped,
        bezier((425, 345), (470, 430), (510, 530), (544, 615)),
        ((3.5, 1.0), (6, 0.55), (8, 0.2)),
    )
    soft_stamp(
        ped,
        bezier((544, 615), (544, 625), (544, 635), (544, 648)),
        ((4.5, 1.0), (7, 0.4)),
    )
    # silo fork (~670,550)
    soft_stamp(
        ped,
        bezier((520, 545), (575, 535), (630, 540), (665, 550)),
        ((3.2, 1.0), (5.5, 0.5), (7, 0.18)),
    )
    ped = blur01(ped, 1.1)
    ped[forbid_water] = 0
    light = dirt * np.array([1.03, 1.015, 0.98])
    work = paint_path(work, ped, light, rng, strength=0.74, forbid=forbid_water)

    fade = np.zeros((h, w), np.float32)
    soft_stamp(
        fade,
        bezier((445, 325), (495, 345), (540, 360), (585, 372)),
        ((2.8, 1.0), (4.5, 0.4), (6, 0.12)),
    )
    fade = blur01(fade, 1.3)
    # taper eastward
    fade *= np.clip(1.2 - (np.linspace(0, 1, w)[None, :] * 1.5), 0, 1)
    fade[forbid_water] = 0
    work = paint_path(work, fade, light, rng, strength=0.42, forbid=forbid_water)

    final = Image.fromarray(np.clip(work, 0, 255).astype(np.uint8))
    final.save(OUT_LIVE)
    final.save(OUT_D)
    ASSETS.parent.mkdir(parents=True, exist_ok=True)
    final.save(ASSETS)

    dbg = final.convert("RGBA")
    for color, m, a in (
        ((220, 40, 40), veh, 150),
        ((30, 200, 220), ped, 150),
        ((240, 220, 40), fade, 140),
        ((40, 40, 40), erase, 100),
    ):
        layer = Image.new("RGBA", (w, h), (*color, 0))
        layer.putalpha(Image.fromarray((np.clip(m, 0, 1) * a).astype(np.uint8)))
        dbg = Image.alpha_composite(dbg, layer)
    DEBUG.parent.mkdir(parents=True, exist_ok=True)
    dbg.convert("RGB").save(DEBUG)

    # quick QA metrics
    live = np.array(final)
    r, g, b = live[..., 0].astype(int), live[..., 1].astype(int), live[..., 2].astype(int)
    teal = (b > 80) & (b > r + 4) & (b + 20 > g) & (r < 170)
    pond_core = teal[500:750, 170:320]
    print(f"live={OUT_LIVE.stat().st_size} resume-d={OUT_D.stat().st_size}")
    print(f"pond_core_teal_frac={pond_core.mean():.3f} veh_px={(veh>0.2).sum()} ped_px={(ped>0.2).sum()}")


if __name__ == "__main__":
    main()
