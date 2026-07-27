"""Rustic grade + remove Inn↔Chapel road + add chapel→wood-line path."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public/maps/hidden-acres-grounds-illustrated-pre-road-edit.png"
OUT = ROOT / "public/maps/hidden-acres-grounds-illustrated.png"
DEBUG = ROOT / "public/maps/_road-edit-debug.png"
ASSETS = Path(
    r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets\hidden-acres-grounds-illustrated.png"
)


def bezier(p0, p1, p2, p3, n: int = 600) -> np.ndarray:
    ts = np.linspace(0, 1, n)
    return np.array(
        [
            ((1 - t) ** 3) * np.array(p0, float)
            + 3 * ((1 - t) ** 2) * t * np.array(p1, float)
            + 3 * (1 - t) * (t**2) * np.array(p2, float)
            + (t**3) * np.array(p3, float)
            for t in ts
        ]
    )


def soft_stamp(mask: np.ndarray, curve: np.ndarray, radii) -> None:
    h, w = mask.shape
    yy2, xx2 = np.ogrid[-22:23, -22:23]
    for x, y in curve:
        ix, iy = int(round(x)), int(round(y))
        for rad, a in radii:
            stamp = ((xx2 * xx2 + yy2 * yy2) <= rad * rad).astype(np.float32) * a
            y0, y1 = iy - 22, iy + 23
            x0, x1 = ix - 22, ix + 23
            if y0 < 0 or x0 < 0 or y1 > h or x1 > w:
                continue
            mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], stamp)


def main() -> None:
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    work = np.array(img).astype(np.float32)
    rng = np.random.default_rng(11)

    # Rustic grade
    gray = work.mean(axis=2, keepdims=True)
    work = work * 0.68 + gray * 0.32
    work[:, :, 0] = np.clip(work[:, :, 0] * 1.06 + 5, 0, 255)
    work[:, :, 2] = np.clip(work[:, :, 2] * 0.95 - 4, 0, 255)
    work = np.clip((work - 128) * 0.88 + 132, 0, 255)
    vign = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vign).ellipse((-0.08 * w, -0.08 * h, 1.08 * w, 1.08 * h), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(100))
    v = 0.84 + 0.16 * (np.array(vign).astype(np.float32) / 255.0)
    work = np.clip(work * v[..., None], 0, 255)

    # Erase Inn↔Chapel connector (keep short chapel stub)
    waypoints = [
        (790, 290),
        (820, 270),
        (850, 250),
        (880, 230),
        (900, 215),
        (920, 200),
        (945, 180),
        (970, 160),
        (995, 145),
        (1020, 130),
    ]
    erase_img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(erase_img).line(waypoints, fill=255, width=58)
    erase_a = np.array(erase_img.filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255.0
    erase_a = np.where(erase_a > 0.25, 1.0, erase_a)

    # Greener lawn fill (not tan field)
    tile_a = work[560:700, 560:720].copy()
    tile_b = work[480:620, 300:460].copy()
    for tile in (tile_a, tile_b):
        tile[:, :, 1] = np.clip(tile[:, :, 1] * 1.1 + 10, 0, 255)
        tile[:, :, 0] = np.clip(tile[:, :, 0] * 0.94, 0, 255)
        tile[:, :, 2] = np.clip(tile[:, :, 2] * 0.92, 0, 255)

    fill = work.copy()
    ys, xs = np.where(erase_a > 0.02)
    for y, x in zip(ys, xs):
        tile = tile_b if ((x + y) % 5) == 0 else tile_a
        th, tw = tile.shape[:2]
        ty = (y * 3 + 17 + int(rng.integers(-12, 13))) % th
        tx = (x * 5 + 29 + int(rng.integers(-12, 13))) % tw
        pix = tile[ty, tx].copy()
        if rng.random() < 0.1:
            pix = np.clip(pix * 0.82, 0, 255)
        fill[y, x] = pix
    fill = np.array(
        Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(0.8)
        )
    ).astype(np.float32)
    work = work * (1 - erase_a[..., None]) + fill * erase_a[..., None]

    r, g, b = work[..., 0], work[..., 1], work[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    tan = (erase_a > 0.15) & (lum > 130) & (r >= g - 2)
    work[tan, 1] = np.clip(work[tan, 1] + 26, 0, 255)
    work[tan, 0] = np.clip(work[tan, 0] - 20, 0, 255)
    work = np.clip(work, 0, 255)

    # Dirt color
    patch = work[720:780, 400:520]
    pr, pg, pb = patch[..., 0], patch[..., 1], patch[..., 2]
    pl = 0.299 * pr + 0.587 * pg + 0.114 * pb
    sel = (pl > 140) & (pr > pb + 12)
    dirt_color = (
        np.median(patch[sel], axis=0)
        if sel.sum() > 20
        else np.array([170.0, 154.0, 118.0])
    )

    # New roads: chapel-behind → wood-line (NORTH of old corridor); Inn spur from wood-line
    path_mask = np.zeros((h, w), dtype=np.float32)
    soft_stamp(
        path_mask,
        bezier((730, 235), (900, 170), (1150, 150), (1435, 190)),
        ((7, 1.0), (11, 0.55), (14, 0.25)),
    )
    soft_stamp(
        path_mask,
        bezier((1430, 145), (1300, 115), (1180, 100), (1100, 95)),
        ((6, 1.0), (10, 0.4)),
    )
    path_mask = (
        np.array(
            Image.fromarray((np.clip(path_mask, 0, 1) * 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(1.5)
            )
        ).astype(np.float32)
        / 255.0
    )
    path_mask *= 1.0 - erase_a  # never redraw dirt on erased corridor

    protect = (
        (work[:, :, 1] > 45)
        & (work[:, :, 1] < 125)
        & (work[:, :, 1] > work[:, :, 0] + 18)
        & (work[:, :, 0] < 85)
    ) | ((work[:, :, 2] > work[:, :, 0] + 25) & (work[:, :, 2] > 90))
    path_mask[protect] = 0

    dirt_layer = np.clip(dirt_color + rng.normal(0, 4.5, work.shape), 0, 255)
    work = work * (1 - path_mask[..., None] * 0.8) + dirt_layer * (path_mask[..., None] * 0.8)

    # Final guard on erased corridor
    r, g, b = work[..., 0], work[..., 1], work[..., 2]
    tan2 = (erase_a > 0.2) & (r >= g - 3) & ((0.299 * r + 0.587 * g + 0.114 * b) > 130)
    work[tan2, 1] = np.clip(work[tan2, 1] + 24, 0, 255)
    work[tan2, 0] = np.clip(work[tan2, 0] - 18, 0, 255)

    final = Image.fromarray(np.clip(work, 0, 255).astype(np.uint8)).filter(
        ImageFilter.SMOOTH
    )
    final.save(OUT, optimize=True)
    ASSETS.parent.mkdir(parents=True, exist_ok=True)
    final.save(ASSETS)

    dbg = final.convert("RGBA")
    red = Image.new("RGBA", (w, h), (220, 30, 30, 0))
    red.putalpha(Image.fromarray((erase_a * 170).astype(np.uint8)))
    cyan = Image.new("RGBA", (w, h), (30, 200, 220, 0))
    cyan.putalpha(Image.fromarray((path_mask * 170).astype(np.uint8)))
    Image.alpha_composite(Image.alpha_composite(dbg, red), cyan).convert("RGB").save(
        DEBUG
    )
    print(f"saved {OUT} ({OUT.stat().st_size})")
    print(f"erase_px={(erase_a > 0.2).sum()} path_px={(path_mask > 0.2).sum()}")


if __name__ == "__main__":
    main()
