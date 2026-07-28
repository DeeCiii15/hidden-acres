"""Remove opaque backgrounds from generated seal/twine PNGs."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

brand = Path(__file__).resolve().parents[1] / "public" / "brand"


def analyze(path: Path) -> None:
    im = Image.open(path).convert("RGB")
    a = np.asarray(im)
    corners = [a[0, 0], a[0, -1], a[-1, 0], a[-1, -1]]
    print(path.name, "corners", [tuple(int(x) for x in c) for c in corners])


def process_seal() -> None:
    path = brand / "wax-seal-ha.png"
    analyze(path)
    arr = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    # Dark / green wax body vs light backdrop
    keep = np.clip((205 - lum) / 60.0, 0, 1)
    greenish = (g >= r - 8) & (g >= b - 12) & (lum < 215)
    keep = np.maximum(keep, np.where(greenish, 0.9, 0.0))
    keep = np.where(lum > 235, 0.0, keep)
    keep = np.where(
        (lum > 215) & (np.abs(r - g) < 14) & (np.abs(g - b) < 14),
        keep * 0.12,
        keep,
    )

    alpha = (keep * 255).astype(np.uint8)
    mask = alpha > 35
    mask = ndimage.binary_opening(mask, iterations=1)
    mask = ndimage.binary_closing(mask, iterations=2)
    labeled, n = ndimage.label(mask)
    if n:
        sizes = ndimage.sum(mask, labeled, range(1, n + 1))
        biggest = int(np.argmax(sizes)) + 1
        mask = labeled == biggest

    dist_in = ndimage.distance_transform_edt(mask)
    soft = np.clip(dist_in / 2.0, 0, 1)
    alpha_final = (np.maximum(keep, soft) * 255 * mask).astype(np.uint8)

    out = arr.copy()
    out[:, :, 3] = alpha_final
    Image.fromarray(out.astype(np.uint8), "RGBA").save(path, optimize=True)
    print("seal alpha%", round(float((alpha_final > 20).mean()) * 100, 1))


def process_twine() -> None:
    path = brand / "twine-wrap.png"
    analyze(path)
    arr = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    neutral = (np.abs(r - g) < 18) & (np.abs(g - b) < 18) & (np.abs(r - b) < 18)
    warm = (r > g - 8) & (g > b - 5) & ((r - b) > 12)
    bg = (lum > 220) | ((lum > 195) & neutral & ~warm)

    score = np.where(bg, 0.0, 1.0)
    score = np.where(warm & (lum < 225), np.maximum(score, 0.95), score)
    score = np.where(
        (lum > 200) & (lum <= 235) & ~warm,
        np.clip((230 - lum) / 30.0, 0, 1) * 0.45,
        score,
    )
    score = np.where(lum > 240, 0.0, score)

    mask = score > 0.28
    mask = ndimage.binary_opening(mask, structure=np.ones((2, 2)), iterations=1)
    mask = ndimage.binary_closing(mask, iterations=2)
    labeled, n = ndimage.label(mask)
    if n:
        sizes = ndimage.sum(mask, labeled, range(1, n + 1))
        keep_labels = {i + 1 for i, s in enumerate(sizes) if s > 120}
        mask = np.isin(labeled, list(keep_labels))

    dist_in = ndimage.distance_transform_edt(mask)
    soft = np.clip(dist_in / 1.6, 0, 1) * np.clip(score, 0.35, 1.0)
    alpha = (soft * 255).astype(np.uint8)

    out = arr.copy()
    out[:, :, 3] = alpha
    Image.fromarray(out.astype(np.uint8), "RGBA").save(path, optimize=True)
    print("twine alpha%", round(float((alpha > 20).mean()) * 100, 1))


if __name__ == "__main__":
    process_seal()
    process_twine()
    print("done")
