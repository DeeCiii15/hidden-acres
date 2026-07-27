"""Apply markup: remove Inn↔Chapel road; extend chapel-back road to wood-line."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public/maps/hidden-acres-grounds-illustrated-pre-road-edit.png"
MARK = ROOT / "public/maps/road-markup-reference.png"
OUT = ROOT / "public/maps/hidden-acres-grounds-illustrated.png"
ASSETS = Path(
    r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets\hidden-acres-grounds-illustrated.png"
)


def soft_line(mask: np.ndarray, pts: list[tuple[int, int]], width: int) -> None:
    im = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.line(pts, fill=255, width=width)
    arr = np.array(im.filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255.0
    np.maximum(mask, arr, out=mask)


def main() -> None:
    base = Image.open(SRC).convert("RGB")
    W, H = base.size
    work = np.array(base).astype(np.float32)
    rng = np.random.default_rng(7)

    mark = np.array(Image.open(MARK).convert("RGB"))
    mh, mw = mark.shape[:2]
    sx, sy = W / mw, H / mh
    r, g, b = [mark[:, :, i].astype(int) for i in range(3)]
    blue = (b > 170) & (r < 110) & (g < 170) & (b > r + 50)
    red = (r > 170) & (g < 110) & (b < 110) & (r > g + 70) & (r > b + 70)
    red &= np.arange(mh)[:, None] < int(mh * 0.42)

    # Blue centerline from markup columns → full-res waypoints, then extend to wood-line
    blue_pts: list[tuple[int, int]] = []
    ys, xs = np.where(blue)
    if len(xs):
        for x0 in range(xs.min(), xs.max() + 1, 8):
            col = ys[xs == x0]
            if len(col) == 0:
                continue
            blue_pts.append((int(x0 * sx), int(np.median(col) * sy)))
    # Ensure connection to right wood-line / entry road
    if blue_pts:
        blue_pts.append((int(W * 0.94), blue_pts[-1][1]))
        blue_pts.append((int(W * 0.96), int(blue_pts[-1][1] + 10)))

    # Red erase: markup centerline + known Inn→Chapel corridor
    red_pts: list[tuple[int, int]] = []
    ys, xs = np.where(red)
    if len(xs):
        # sort by y (Inn is higher / smaller y)
        order = np.argsort(ys)
        step = max(1, len(order) // 12)
        for i in order[::step]:
            red_pts.append((int(xs[i] * sx), int(ys[i] * sy)))
    # Always include Inn entrance → chapel fork corridor
    corridor = [
        (1035, 125),
        (1000, 145),
        (960, 170),
        (920, 200),
        (880, 230),
        (840, 255),
        (800, 285),
        (770, 305),
    ]

    # --- ERASE Inn–Chapel road ---
    erase = np.zeros((H, W), dtype=np.float32)
    soft_line(erase, corridor[1:-1], 52)
    if len(red_pts) >= 2:
        soft_line(erase, red_pts, 40)
    erase = np.where(erase > 0.28, 1.0, erase)
    # keep far-right main road
    erase[:, int(W * 0.92) :] = 0

    # Local grass fill from upper meadow
    wr, wg, wb = work[..., 0], work[..., 1], work[..., 2]
    lum = 0.299 * wr + 0.587 * wg + 0.114 * wb
    pathish = (lum > 140) & (wr > wb + 12)
    yy, xx = np.mgrid[0:H, 0:W]
    meadow = (xx > 750) & (xx < 1320) & (yy > 80) & (yy < 360)
    grass_ok = meadow & ~pathish & (erase < 0.3) & (wg > 75)
    gi = Image.fromarray(
        np.clip(work * grass_ok[..., None], 0, 255).astype(np.uint8)
    ).filter(ImageFilter.GaussianBlur(16))
    gm = Image.fromarray((grass_ok.astype(np.uint8) * 255)).filter(
        ImageFilter.GaussianBlur(16)
    )
    fill = np.array(gi).astype(np.float32) / np.maximum(
        np.array(gm).astype(np.float32)[..., None] / 255.0, 1e-3
    )
    fill = np.clip(fill + rng.normal(0, 3, work.shape), 0, 255)
    work = work * (1 - erase[..., None]) + fill * erase[..., None]

    # --- PAINT blue extension (do NOT mask by erase — different route) ---
    road = np.zeros((H, W), dtype=np.float32)
    if len(blue_pts) >= 2:
        soft_line(road, blue_pts, 22)
    road = np.clip(road, 0, 1)

    # Sample dirt from chapel-back path on ORIGINAL
    patch = np.array(base)[250:330, 600:740].astype(np.float32)
    pr, pg, pb = patch[..., 0], patch[..., 1], patch[..., 2]
    pl = 0.299 * pr + 0.587 * pg + 0.114 * pb
    sel = (pl > 145) & (pr > pb + 12)
    dirt = (
        np.median(patch[sel], axis=0)
        if sel.sum() > 15
        else np.array([166.0, 151.0, 114.0])
    )
    dirt_layer = np.clip(dirt + rng.normal(0, 5.5, work.shape), 0, 255)

    # Avoid painting over pins/water/Inn building roughly
    protect = (
        (work[:, :, 1] > 45)
        & (work[:, :, 1] < 125)
        & (work[:, :, 1] > work[:, :, 0] + 18)
        & (work[:, :, 0] < 85)
    ) | ((work[:, :, 2] > work[:, :, 0] + 25) & (work[:, :, 2] > 90))
    road[protect] = 0
    # Don't cover Inn roof area
    road[60:140, 1000:1180] = 0

    pa = (road**1.05)[..., None] * 0.92
    work = work * (1 - pa) + dirt_layer * pa

    # Final: if erase zone still looks like path, force grass
    wr, wg, wb = work[..., 0], work[..., 1], work[..., 2]
    lum = 0.299 * wr + 0.587 * wg + 0.114 * wb
    bad = (erase > 0.4) & (lum > 148) & (wr > wg)
    work[bad] = fill[bad]

    final = Image.fromarray(np.clip(work, 0, 255).astype(np.uint8))
    final.save(OUT, optimize=True)
    ASSETS.parent.mkdir(parents=True, exist_ok=True)
    final.save(ASSETS)
    print(f"saved {OUT}")
    print(f"blue_pts={len(blue_pts)} erase={(erase > 0.4).sum()} road={(road > 0.4).sum()}")


if __name__ == "__main__":
    main()
