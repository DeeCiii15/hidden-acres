"""Build a clean deckle mask from the polaroid reference silhouette.

Removes thin twine/seal protrusions, then restores a pulpy torn edge
matching the reference paper character.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "public" / "brand"
OUT_W, OUT_H = 900, 1120


def hash_noise(x: float, y: float) -> float:
    n = math.sin(x * 127.1 + y * 311.7) * 43758.5453
    return n - math.floor(n)


def value_noise(x: float, y: float) -> float:
    x0, y0 = math.floor(x), math.floor(y)
    xf, yf = x - x0, y - y0
    xf = xf * xf * (3 - 2 * xf)
    yf = yf * yf * (3 - 2 * yf)
    n00 = hash_noise(x0, y0)
    n10 = hash_noise(x0 + 1, y0)
    n01 = hash_noise(x0, y0 + 1)
    n11 = hash_noise(x0 + 1, y0 + 1)
    nx0 = n00 * (1 - xf) + n10 * xf
    nx1 = n01 * (1 - xf) + n11 * xf
    return nx0 * (1 - yf) + nx1 * yf


def fbm(x: float, y: float, octaves: int = 5) -> float:
    v = 0.0
    a = 1.0
    f = 1.0
    s = 0.0
    for _ in range(octaves):
        v += (value_noise(x * f, y * f) * 2 - 1) * a
        s += a
        a *= 0.5
        f *= 2.1
    return v / s


def main() -> None:
    ref = Image.open(BRAND / "polaroid-style-ref.png").convert("RGB")
    arr = np.asarray(ref).astype(np.float32)
    h, w = arr.shape[:2]
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    # Non-background
    card = lum <= 246
    card = ndimage.binary_fill_holes(card)
    labeled, n = ndimage.label(card)
    sizes = ndimage.sum(card, labeled, range(1, n + 1))
    card = labeled == (int(np.argmax(sizes)) + 1)
    card = ndimage.binary_fill_holes(card)

    # Strip thin twine whiskers / seal blobs that stick past the paper body
    body = ndimage.binary_opening(card, structure=np.ones((7, 7)), iterations=2)
    body = ndimage.binary_closing(body, structure=np.ones((9, 9)), iterations=2)
    body = ndimage.binary_fill_holes(body)
    labeled, n = ndimage.label(body)
    sizes = ndimage.sum(body, labeled, range(1, n + 1))
    body = labeled == (int(np.argmax(sizes)) + 1)

    ys, xs = np.where(body)
    top_y, bot_y = int(ys.min()), int(ys.max())
    left_x, right_x = int(xs.min()), int(xs.max())
    pad = 6
    x0, y0 = max(0, left_x - pad), max(0, top_y - pad)
    x1, y1 = min(w - 1, right_x + pad), min(h - 1, bot_y + pad)
    crop = body[y0 : y1 + 1, x0 : x1 + 1]

    # Upscale body to working size
    crop_im = Image.fromarray((crop.astype(np.uint8) * 255), "L")
    base = np.asarray(
        crop_im.resize((OUT_W, OUT_H), Image.Resampling.NEAREST)
    ) > 128

    # Rebuild a highly irregular deckle around the cleaned body silhouette
    # by warping the distance-to-edge with multi-scale noise (reference-like pulp)
    dist_in = ndimage.distance_transform_edt(base)
    dist_out = ndimage.distance_transform_edt(~base)
    # Signed distance: + inside, - outside
    signed = np.where(base, dist_in, -dist_out).astype(np.float32)

    yy, xx = np.mgrid[0:OUT_H, 0:OUT_W].astype(np.float32)
    # Normalize coords
    nx = xx / OUT_W
    ny = yy / OUT_H

    # Edge displacement field in pixels — large bites + fine tooth like handmade paper
    amp = 14.0
    noise = np.zeros_like(signed)
    # Sample noise densely near the edge only for speed
    edge_band = np.abs(signed) < 28
    ey, ex = np.where(edge_band)
    for y, x in zip(ey, ex):
        t = x / OUT_W
        u = y / OUT_H
        n1 = fbm(t * 4.2 + 1.1, u * 3.8 + 2.4)
        n2 = fbm(t * 11.0 + 4.0, u * 9.5 + 0.7)
        n3 = fbm(t * 28.0 + 8.0, u * 24.0 + 3.1)
        n4 = fbm(t * 64.0, u * 58.0 + 9.0)
        tear = 0.0
        if n3 > 0.38:
            tear = (n3 - 0.38) * amp * 2.4
        if n2 < -0.42:
            tear += (-n2 - 0.42) * amp * 1.5
        noise[y, x] = amp * (0.4 * n1 + 0.28 * n2 + 0.18 * n3 + 0.14 * n4) - tear

    # Positive noise eats inward on the outside / builds outward — displace the threshold
    deckle = signed > noise

    # Fiber nicks along the rim
    rim = deckle ^ ndimage.binary_erosion(deckle, iterations=2)
    rng = np.random.RandomState(77)
    ry, rx = np.where(rim)
    for y, x in zip(ry, rx):
        r = rng.random()
        if r < 0.08:
            length = rng.randint(2, 8)
            ang = rng.uniform(0, math.tau)
            for k in range(length):
                xx_ = int(x + math.cos(ang) * k)
                yy_ = int(y + math.sin(ang) * k)
                if 0 <= xx_ < OUT_W and 0 <= yy_ < OUT_H:
                    deckle[yy_, xx_] = False
                    if rng.random() < 0.4:
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            xa, ya = xx_ + dx, yy_ + dy
                            if 0 <= xa < OUT_W and 0 <= ya < OUT_H and rng.random() < 0.55:
                                deckle[ya, xa] = False
        elif r < 0.14:
            length = rng.randint(1, 5)
            ang = rng.uniform(0, math.tau)
            for k in range(length):
                xx_ = int(x + math.cos(ang) * k)
                yy_ = int(y + math.sin(ang) * k)
                if 0 <= xx_ < OUT_W and 0 <= yy_ < OUT_H:
                    deckle[yy_, xx_] = True

    deckle = ndimage.binary_fill_holes(deckle)
    mask_im = Image.fromarray((deckle.astype(np.uint8) * 255), "L").filter(
        ImageFilter.GaussianBlur(0.45)
    )
    Image.merge("RGB", (mask_im, mask_im, mask_im)).save(
        BRAND / "polaroid-deckle-mask.png", optimize=True
    )
    print("saved polaroid-deckle-mask.png")

    # White fibrous core — slightly larger, brighter fringe
    fiber = ndimage.binary_dilation(deckle, iterations=4)
    f_rim = fiber ^ ndimage.binary_erosion(fiber, iterations=2)
    fy, fx = np.where(f_rim)
    for y, x in zip(fy[::1], fx[::1]):
        if rng.random() < 0.22:
            length = rng.randint(1, 6)
            ang = rng.uniform(0, math.tau)
            for k in range(length):
                xx_ = int(x + math.cos(ang) * k)
                yy_ = int(y + math.sin(ang) * k)
                if 0 <= xx_ < OUT_W and 0 <= yy_ < OUT_H:
                    fiber[yy_, xx_] = True
    fiber_im = Image.fromarray((fiber.astype(np.uint8) * 255), "L").filter(
        ImageFilter.GaussianBlur(0.4)
    )
    Image.merge("RGB", (fiber_im, fiber_im, fiber_im)).save(
        BRAND / "polaroid-deckle-fiber.png", optimize=True
    )
    print("saved polaroid-deckle-fiber.png")
    print("fill%", round(float(deckle.mean()) * 100, 1))


if __name__ == "__main__":
    main()
