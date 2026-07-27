"""Surgical topology edits on locked resume-b (682x1024) -> live + resume-g.

Only: chapel path -> courtyard center, silo fork, silo north nudge,
ballroom left T-wing, groom north nudge. No northern-road redraw.
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
OUT_G = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-g.png"
QA = MAPS / "_qa-crops-resume-g"


def bezier(p0, p1, p2, p3, n: int = 700) -> np.ndarray:
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


def soft_stamp(mask: np.ndarray, curve: np.ndarray, radii) -> None:
    h, w = mask.shape
    yy2, xx2 = np.ogrid[-28:29, -28:29]
    for x, y in curve:
        ix, iy = int(round(x)), int(round(y))
        for rad, a in radii:
            stamp = ((xx2 * xx2 + yy2 * yy2) <= rad * rad).astype(np.float32) * a
            y0, y1 = iy - 28, iy + 29
            x0, x1 = ix - 28, ix + 29
            if y0 < 0 or x0 < 0 or y1 > h or x1 > w:
                continue
            mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], stamp)


def blur01(mask: np.ndarray, r: float = 1.4) -> np.ndarray:
    return (
        np.array(
            Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(r)
            )
        ).astype(np.float32)
        / 255.0
    )


def sample_dirt(work: np.ndarray) -> np.ndarray:
    patches = [work[780:860, 280:360], work[140:200, 450:540], work[700:760, 160:230]]
    samples = []
    for patch in patches:
        r, g, b = patch[..., 0], patch[..., 1], patch[..., 2]
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        sel = (lum > 120) & (r > b + 8) & (r >= g - 8) & (g > 85)
        if sel.sum() > 20:
            samples.append(patch[sel])
    if samples:
        return np.median(np.concatenate(samples, axis=0), axis=0)
    return np.array([168.0, 150.0, 112.0])


def sample_lawn(work: np.ndarray) -> np.ndarray:
    return work[300:400, 340:450].copy()


def erase_to_lawn(work: np.ndarray, erase_a: np.ndarray, lawn_tile: np.ndarray, rng) -> np.ndarray:
    fill = work.copy()
    th, tw = lawn_tile.shape[:2]
    ys, xs = np.where(erase_a > 0.02)
    for y, x in zip(ys, xs):
        ty = (y * 3 + 17 + int(rng.integers(-8, 9))) % max(th - 1, 1)
        tx = (x * 5 + 29 + int(rng.integers(-8, 9))) % max(tw - 1, 1)
        pix = lawn_tile[ty, tx].astype(np.float32).copy()
        pix[1] = np.clip(pix[1] * 1.03 + 3, 0, 255)
        pix[0] = np.clip(pix[0] * 0.98, 0, 255)
        fill[y, x] = pix
    fill = np.array(
        Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(0.55)
        )
    ).astype(np.float32)
    a = erase_a[..., None]
    return work * (1 - a) + fill * a


def paint_path(work: np.ndarray, path_mask: np.ndarray, dirt_color: np.ndarray, rng, strength: float) -> np.ndarray:
    dirt_layer = np.clip(dirt_color + rng.normal(0, 2.8, work.shape), 0, 255)
    a = path_mask[..., None] * strength
    return work * (1 - a) + dirt_layer * a


def roof_mask(crop: np.ndarray) -> np.ndarray:
    cr, cg, cb = crop[..., 0], crop[..., 1], crop[..., 2]
    roof = (cr > 90) & (cr < 195) & (cr > cg + 10) & (cr > cb + 18) & (cg < 150)
    alpha = roof.astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    return np.clip(alpha * 1.5, 0, 1)


def building_alpha(crop: np.ndarray) -> np.ndarray:
    cr, cg, cb = crop[..., 0], crop[..., 1], crop[..., 2]
    buildingish = (
        ((cr > 85) & (cr < 195) & (cr > cg + 8) & (cr > cb + 15))
        | ((cr > 105) & (cg > 95) & (cb > 70) & (cr < 205) & ((cr + cg + cb) > 290))
    )
    alpha = buildingish.astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
    return np.clip(alpha * 1.45, 0, 1)


def pin_alpha(crop: np.ndarray) -> np.ndarray:
    """Dark forest-green teardrop map pins already on resume-b."""
    cr, cg, cb = crop[..., 0], crop[..., 1], crop[..., 2]
    pin = (cg > 55) & (cg < 145) & (cr < 75) & (cb < 75) & (cg > cr + 25) & (cg > cb + 20)
    alpha = pin.astype(np.float32)
    alpha = cv2.dilate(alpha, np.ones((3, 3), np.uint8), iterations=1)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    return np.clip(alpha * 1.6, 0, 1)


def shift_region_north(
    work: np.ndarray,
    box: tuple[int, int, int, int],
    shift: int,
    lawn: np.ndarray,
    rng,
    protect: tuple[slice, slice] | None = None,
    include_pin: bool = False,
) -> np.ndarray:
    x0, y0, x1, y1 = box
    crop = work[y0:y1, x0:x1].copy()
    alpha = building_alpha(crop)
    if include_pin:
        alpha = np.maximum(alpha, pin_alpha(crop))

    bgr = cv2.cvtColor(np.clip(work, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    mask = np.zeros(bgr.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = (alpha > 0.25).astype(np.uint8) * 255
    if protect is not None:
        mask[protect] = 0
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    inpainted = cv2.inpaint(bgr, mask, 3, cv2.INPAINT_TELEA)
    rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB).astype(np.float32)

    erase_a = blur01(mask.astype(np.float32) / 255.0, 1.2)
    rgb = erase_to_lawn(rgb, erase_a * 0.35, lawn, rng)

    ny0, ny1 = y0 - shift, y1 - shift
    if ny0 < 0:
        return work
    dest = rgb[ny0:ny1, x0:x1]
    dest[:] = dest * (1 - alpha[..., None]) + crop * alpha[..., None]
    rgb[ny0:ny1, x0:x1] = dest
    return rgb


def add_left_ballroom_wing(work: np.ndarray) -> np.ndarray:
    """Clone right-wing roof band, flip, paste on left of stem to form a T."""
    # Right wing roof band only (avoid bridal suite further east)
    rx0, ry0, rx1, ry1 = 398, 638, 448, 698
    right = work[ry0:ry1, rx0:rx1].copy()
    alpha = roof_mask(right)

    # Keep only the western portion of this crop (ballroom wing, not bridal)
    ww = rx1 - rx0
    fade = np.linspace(1.0, 0.15, ww, dtype=np.float32)
    alpha = alpha * fade[None, :]
    alpha = np.clip(alpha, 0, 1)

    mirrored = np.ascontiguousarray(right[:, ::-1])
    alpha_m = np.ascontiguousarray(alpha[:, ::-1])

    # Stem left edge ~ x=332 at this band; place wing immediately west
    lx1 = 336
    lx0 = lx1 - ww
    ly0, ly1 = ry0, ry1

    # Soft edge falloff
    edge = np.ones_like(alpha_m)
    edge[:2, :] *= 0.4
    edge[-2:, :] *= 0.55
    edge[:, :3] *= 0.45
    edge[:, -2:] *= 0.7
    alpha_m = cv2.GaussianBlur(np.clip(alpha_m * edge, 0, 1), (3, 3), 0)

    dest = work[ly0:ly1, lx0:lx1]
    dest[:] = dest * (1 - alpha_m[..., None]) + mirrored * alpha_m[..., None]
    work[ly0:ly1, lx0:lx1] = dest
    return work


def main() -> None:
    rng = np.random.default_rng(47)
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    assert (w, h) == (682, 1024), f"expected 682x1024, got {w}x{h}"
    work = np.array(img).astype(np.float32)
    lawn = sample_lawn(work)
    dirt = sample_dirt(work)

    # 1) Rusted Silo + pin — nudge north ~12px
    work = shift_region_north(
        work,
        box=(405, 430, 520, 575),
        shift=12,
        lawn=lawn,
        rng=rng,
        protect=(slice(545, 655), slice(300, 455)),
        include_pin=True,
    )

    # 2) Groom's Quarters + pin — subtle north nudge ~12px
    work = shift_region_north(
        work,
        box=(200, 500, 345, 690),
        shift=12,
        lawn=lawn,
        rng=rng,
        protect=(slice(545, 655), slice(340, 480)),
        include_pin=True,
    )
    gap = np.zeros(work.shape[:2], np.float32)
    cv2.rectangle(gap, (248, 668), (318, 686), 1.0, -1)
    gap = blur01(gap, 1.2)
    gap[545:655, 340:480] = 0
    work = erase_to_lawn(work, gap * 0.55, lawn, rng)

    # 3) Erase old NW-corner chapel approach (lower half of spur)
    erase = np.zeros((h, w), np.float32)
    soft_stamp(
        erase,
        bezier((318, 390), (335, 450), (348, 505), (362, 545)),
        ((5.5, 1.0), (8.5, 0.55), (11, 0.22)),
    )
    soft_stamp(
        erase,
        bezier((362, 545), (370, 552), (382, 560), (395, 568)),
        ((6.0, 1.0), (9.0, 0.45), (11, 0.18)),
    )
    # also erase faint NW corner stub on paving edge
    soft_stamp(
        erase,
        bezier((360, 555), (368, 558), (375, 560), (382, 562)),
        ((4.0, 0.7), (6.0, 0.3)),
    )
    erase = blur01(erase, 1.3)
    # keep deep courtyard interior + pins
    erase[575:650, 355:470] *= 0.05
    pin_full = pin_alpha(work)
    erase = erase * (1.0 - np.clip(pin_full * 1.2, 0, 1))
    work = erase_to_lawn(work, erase * 0.92, lawn, rng)

    # 4) New path into courtyard CENTER (fountain ~ x410)
    ped = np.zeros((h, w), np.float32)
    # keep upper chapel path, bend mid-field into centerline
    soft_stamp(
        ped,
        bezier((320, 350), (345, 410), (375, 470), (405, 520)),
        ((3.0, 1.0), (5.0, 0.55), (7.0, 0.2)),
    )
    soft_stamp(
        ped,
        bezier((405, 520), (408, 535), (410, 550), (410, 568)),
        ((3.8, 1.0), (6.0, 0.5), (7.5, 0.18)),
    )
    # 5) Silo fork from the new center path
    soft_stamp(
        ped,
        bezier((400, 515), (425, 505), (450, 500), (468, 505)),
        ((2.8, 1.0), (4.5, 0.5), (6.0, 0.16)),
    )
    ped = blur01(ped, 1.05)
    light = dirt * np.array([1.035, 1.02, 0.98])
    work = paint_path(work, ped, light, rng, strength=0.82)

    # 6) Ballroom left T-wing
    work = add_left_ballroom_wing(work)

    final = Image.fromarray(np.clip(work, 0, 255).astype(np.uint8))
    final.save(OUT_LIVE)
    final.save(OUT_G)

    QA.mkdir(exist_ok=True)
    final.crop((200, 280, 560, 720)).save(QA / "after-cluster.png")
    final.crop((250, 580, 520, 760)).save(QA / "after-ball-t.png")
    final.crop((300, 380, 460, 590)).save(QA / "after-path.png")
    final.crop((380, 470, 520, 580)).save(QA / "after-silo.png")
    final.crop((220, 540, 360, 700)).save(QA / "after-groom.png")
    Image.open(SRC).crop((250, 580, 520, 760)).save(QA / "before-ball-t.png")
    Image.open(SRC).crop((300, 380, 460, 590)).save(QA / "before-path.png")

    # metrics
    before = np.array(Image.open(SRC).convert("RGB"))
    after = np.array(final)

    def dirt_score(im, box):
        x0, y0, x1, y1 = box
        p = im[y0:y1, x0:x1].astype(int)
        r, g, b = p[..., 0], p[..., 1], p[..., 2]
        dirt = (r > 140) & (g > 120) & (b > 80) & (r > b + 15) & (r >= g - 8)
        return float(dirt.mean())

    def roof_score(im, box):
        x0, y0, x1, y1 = box
        p = im[y0:y1, x0:x1].astype(int)
        r, g, b = p[..., 0], p[..., 1], p[..., 2]
        roof = (r > 95) & (r < 185) & (r > g + 12) & (r > b + 20) & (g < 145)
        return float(roof.mean())

    def silo_cy(im):
        r, g, b = im[..., 0].astype(int), im[..., 1].astype(int), im[..., 2].astype(int)
        rust = (r > 100) & (r < 180) & (r > g + 20) & (r > b + 25) & (g < 140)
        m = np.zeros_like(rust)
        m[470:560, 410:500] = rust[470:560, 410:500]
        ys, xs = np.where(m)
        return float(ys.mean()) if len(ys) else None

    def groom_cy(im):
        r, g, b = im[..., 0].astype(int), im[..., 1].astype(int), im[..., 2].astype(int)
        roof = (r > 95) & (r < 185) & (r > g + 12) & (r > b + 20) & (g < 145)
        m = np.zeros_like(roof)
        m[540:690, 220:340] = roof[540:690, 220:340]
        ys = np.where(m)[0]
        return float(ys.mean()) if len(ys) else None

    print("NW dirt", dirt_score(before, (350, 540, 390, 575)), "->", dirt_score(after, (350, 540, 390, 575)))
    print("CTR dirt", dirt_score(before, (390, 540, 430, 575)), "->", dirt_score(after, (390, 540, 430, 575)))
    print("FORK dirt", dirt_score(before, (400, 500, 460, 530)), "->", dirt_score(after, (400, 500, 460, 530)))
    print("L-wing roof", roof_score(before, (286, 638, 336, 698)), "->", roof_score(after, (286, 638, 336, 698)))
    print("R-wing roof", roof_score(before, (398, 638, 448, 698)), "->", roof_score(after, (398, 638, 448, 698)))
    print("silo cy", silo_cy(before), "->", silo_cy(after))
    print("groom cy", groom_cy(before), "->", groom_cy(after))
    print(f"live={OUT_LIVE.stat().st_size} resume-g={OUT_G.stat().st_size}")
    print("DONE")


if __name__ == "__main__":
    main()
