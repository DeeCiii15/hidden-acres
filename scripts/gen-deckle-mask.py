"""Generate irregular torn-paper deckle masks for Polaroid cards."""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "public" / "brand"

W, H = 900, 1120


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


def fbm(x: float, y: float, octaves: int = 6) -> float:
    v = 0.0
    a = 1.0
    f = 1.0
    s = 0.0
    for _ in range(octaves):
        v += (value_noise(x * f, y * f) * 2 - 1) * a
        s += a
        a *= 0.52
        f *= 2.15
    return v / s


def edge_offset(t: float, side: int, amp: float) -> float:
    # Large irregular bites + fine tooth
    n1 = fbm(t * 3.2 + side * 19.1, side * 4.7)
    n2 = fbm(t * 9.5 + side * 7.3, side * 13.2 + 1.4)
    n3 = fbm(t * 28.0 + side * 2.8, side * 6.1 + 9.2)
    n4 = fbm(t * 64.0 + side * 41.0, side * 22.0)
    tear = 0.0
    # Occasional deep hand-torn bites
    if n3 > 0.42:
        tear = (n3 - 0.42) * amp * 2.6
    if n2 < -0.48:
        tear += (-n2 - 0.48) * amp * 1.7
    return amp * (0.42 * n1 + 0.28 * n2 + 0.18 * n3 + 0.12 * n4) - tear


def build_polygon(inset_base: float, amp: float) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    steps = 520
    for i in range(steps + 1):
        t = i / steps
        x = inset_base + t * (W - 2 * inset_base)
        y = inset_base + edge_offset(t, 0, amp)
        pts.append((x, y))
    for i in range(1, steps + 1):
        t = i / steps
        x = W - inset_base + edge_offset(t, 1, amp)
        y = inset_base + t * (H - 2 * inset_base)
        pts.append((x, y))
    for i in range(1, steps + 1):
        t = i / steps
        x = W - inset_base - t * (W - 2 * inset_base)
        y = H - inset_base + edge_offset(t, 2, amp)
        pts.append((x, y))
    for i in range(1, steps):
        t = i / steps
        x = inset_base + edge_offset(t, 3, amp)
        y = H - inset_base - t * (H - 2 * inset_base)
        pts.append((x, y))
    return pts


def add_fiber_nicks(mask: Image.Image, seed: int = 99) -> Image.Image:
    dil = mask.filter(ImageFilter.MaxFilter(9))
    ero = mask.filter(ImageFilter.MinFilter(9))
    ring = ImageChops.subtract(dil, ero)
    px = ring.load()
    mp = mask.load()
    rnd = random.Random(seed)
    for y in range(0, H, 1):
        for x in range(0, W, 1):
            if px[x, y] < 30:
                continue
            r = rnd.random()
            if r < 0.07:
                # Deep inward nick
                length = rnd.randint(2, 7)
                ang = rnd.uniform(0, math.tau)
                for k in range(length):
                    xx = int(x + math.cos(ang) * k)
                    yy = int(y + math.sin(ang) * k)
                    if 0 <= xx < W and 0 <= yy < H:
                        mp[xx, yy] = 0
                        if rnd.random() < 0.45:
                            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                                xa, ya = xx + dx, yy + dy
                                if 0 <= xa < W and 0 <= ya < H and rnd.random() < 0.5:
                                    mp[xa, ya] = 0
            elif r < 0.12:
                # Fibrous outward whisker
                length = rnd.randint(1, 5)
                ang = rnd.uniform(0, math.tau)
                for k in range(length):
                    xx = int(x + math.cos(ang) * k)
                    yy = int(y + math.sin(ang) * k)
                    if 0 <= xx < W and 0 <= yy < H:
                        mp[xx, yy] = 255
    return mask


def save_mask(mask: Image.Image, path: Path, blur: float = 0.35) -> None:
    # Hard torn silhouette — minimal AA only
    mask_aa = mask.filter(ImageFilter.GaussianBlur(radius=blur))
    out = Image.merge("RGB", (mask_aa, mask_aa, mask_aa))
    out.save(path, optimize=True)
    print(f"saved {path} ({os.path.getsize(path)} bytes)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cream card silhouette — aggressive irregular tears
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(build_polygon(inset_base=34, amp=22), fill=255)
    mask = add_fiber_nicks(mask, seed=101)
    save_mask(mask, OUT_DIR / "polaroid-deckle-mask.png", blur=0.4)

    # Outer white fibrous core — only slightly larger, thin fringe
    fiber = Image.new("L", (W, H), 0)
    ImageDraw.Draw(fiber).polygon(build_polygon(inset_base=26, amp=24), fill=255)
    fiber = add_fiber_nicks(fiber, seed=55)
    save_mask(fiber, OUT_DIR / "polaroid-deckle-fiber.png", blur=0.35)


if __name__ == "__main__":
    main()
