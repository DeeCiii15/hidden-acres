"""Move Bridal Suite pin onto the bridal suite house without soft-fringe smudges.

Starts from the pristine user map, covers the old pin with a soft forest ellipse
sampled from real canopy elsewhere on the map, then hard-pastes the pin sprite
with tip anchored to the house roof center.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(
    r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets"
)
SRC = (
    ASSETS
    / "c__Users_livingt_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-ce1fd2c2-3182-49cb-937e-fa277298fd0b.png"
)
MAPS = ROOT / "public" / "maps"

# Original painted pin bbox on 682×1024 master
PIN_BOX = (490, 560, 536, 638)
# Tip target: center of bridal suite roof (south of silo)
TIP_X, TIP_Y = 455, 628


def extract_pin(base: np.ndarray) -> tuple[np.ndarray, np.ndarray, int, int]:
    bx0, by0, bx1, by1 = PIN_BOX
    crop = base[by0:by1, bx0:bx1].copy()
    ph, pw = crop.shape[:2]
    r, g, b = (crop[..., i].astype(np.int16) for i in range(3))
    body = (
        (g > 60)
        & (g < 130)
        & (r < 70)
        & (b < 75)
        & (g > r + 30)
        & (g > b + 25)
    )
    rim = (
        (g > 90)
        & (g < 160)
        & (r < 100)
        & (b < 100)
        & (g > r + 25)
        & (g > b + 20)
    )
    white = (r > 200) & (g > 200) & (b > 200)
    gold = (
        (r > 160)
        & (g > 120)
        & (g < 200)
        & (b < 100)
        & (r > g)
        & (r > b + 40)
    )
    raw = (body | rim | white | gold).astype(np.uint8)
    n, labels, stats, cents = cv2.connectedComponentsWithStats(raw, 8)
    cx0, cy0 = pw / 2, ph / 2
    keep = np.zeros_like(raw)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        cx, cy = cents[i]
        dist = ((cx - cx0) ** 2 + (cy - cy0) ** 2) ** 0.5
        if area > 20 and dist < 35:
            keep[labels == i] = 1
    mask = (keep * 255).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), 2)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(mask)
    cv2.drawContours(filled, cnts, -1, 255, thickness=-1)
    # Drop 1px fringe (tree bleed) but keep tip point
    eroded = cv2.erode(filled, np.ones((2, 2), np.uint8), 1)
    ys, xs = np.where(filled > 0)
    tip_ly = int(ys.max())
    tip_lx = int(np.mean(xs[ys >= tip_ly - 2]))
    mask = eroded
    mask[max(0, tip_ly - 10) : tip_ly + 1, :] = filled[
        max(0, tip_ly - 10) : tip_ly + 1, :
    ]
    ys, xs = np.where(mask > 0)
    tip_ly = int(ys.max())
    tip_lx = int(np.mean(xs[ys >= tip_ly - 2]))
    return crop, mask, tip_lx, tip_ly


def ellipse_stamp(h: int, w: int, cx: float, cy: float, rx: float, ry: float) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ell = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    s = np.zeros((h, w), np.float32)
    inside = ell <= 1.0
    s[inside] = (1.0 - ell[inside]) ** 1.2
    return cv2.GaussianBlur(s, (0, 0), 1.8)


def main() -> None:
    base = np.array(Image.open(SRC).convert("RGB"))
    h, w = base.shape[:2]
    crop, mask, tip_lx, tip_ly = extract_pin(base)
    ph, pw = crop.shape[:2]
    bx0, by0, bx1, by1 = PIN_BOX

    out = base.astype(np.float32)
    ocx = (bx0 + bx1) / 2.0
    ocy = (by0 + by1) / 2.0

    # Soft canopy cover — real foliage only, no pin-shaped hole
    stamp = np.clip(
        ellipse_stamp(h, w, ocx, ocy, 36, 46) * 1.25
        + ellipse_stamp(h, w, ocx + 6, ocy - 4, 22, 28) * 0.55,
        0,
        1,
    )
    sy0, sy1 = max(0, int(ocy - 55)), min(h, int(ocy + 55))
    sx0, sx1 = max(0, int(ocx - 45)), min(w, int(ocx + 45))
    fh, fw = sy1 - sy0, sx1 - sx0
    f1 = base[500:580, 600:680]
    f2 = base[730:820, 580:670]
    fill = (
        0.55
        * np.array(Image.fromarray(f1).resize((fw, fh), Image.Resampling.LANCZOS)).astype(
            np.float32
        )
        + 0.45
        * np.array(Image.fromarray(f2).resize((fw, fh), Image.Resampling.LANCZOS)).astype(
            np.float32
        )
    )
    a = stamp[sy0:sy1, sx0:sx1][..., None]
    out[sy0:sy1, sx0:sx1] = out[sy0:sy1, sx0:sx1] * (1 - a) + fill * a

    # Remove leftover pin-green near old location
    tmp = np.clip(out, 0, 255).astype(np.uint8)
    rr, gg, bb = (tmp[..., i].astype(np.int16) for i in range(3))
    remain = (
        (gg > 55)
        & (gg < 130)
        & (rr < 70)
        & (bb < 75)
        & (gg > rr + 30)
        & (gg > bb + 25)
    )
    region = np.zeros((h, w), dtype=bool)
    region[by0 - 4 : by1 + 4, bx0 - 4 : bx1 + 4] = True
    remain_u = cv2.dilate((remain & region).astype(np.uint8) * 255, np.ones((3, 3), np.uint8), 1) > 0
    shifted = np.roll(tmp, 40, axis=1)
    out[remain_u] = shifted[remain_u].astype(np.float32)

    # Hard paste pin tip on roof center
    dx0 = TIP_X - tip_lx
    dy0 = TIP_Y - tip_ly
    a = (mask > 0).astype(np.float32)[..., None]
    out[dy0 : dy0 + ph, dx0 : dx0 + pw] = (
        out[dy0 : dy0 + ph, dx0 : dx0 + pw] * (1 - a) + crop.astype(np.float32) * a
    )
    out_u = np.clip(out, 0, 255).astype(np.uint8)

    MAPS.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out_u).save(MAPS / "hidden-acres-grounds-illustrated-v-map-ballroom-t.png")
    Image.fromarray(out_u).resize((1024, 1536), Image.Resampling.LANCZOS).save(
        MAPS / "hidden-acres-grounds-illustrated.png"
    )
    qa_dir = MAPS / "_qa-crops-ballroom-t"
    qa_dir.mkdir(exist_ok=True)
    Image.fromarray(out_u[500:680, 380:560]).save(qa_dir / "bridal-pin-after.png")

    cx = (dx0 + pw / 2) / w * 100
    cy = (dy0 + ph / 2) / h * 100
    print(f"hotspot pct: {cx:.1f}, {cy:.1f}")
    print(f"tip: ({TIP_X}, {TIP_Y})")


if __name__ == "__main__":
    main()
