"""Surgical edits: remove west-gable door+walkway; remove parking-fork road."""

from __future__ import annotations

import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public/maps"
SRC = MAPS / "hidden-acres-grounds-illustrated.png"
OUT = MAPS / "hidden-acres-grounds-illustrated.png"
OUT_COPY = MAPS / "hidden-acres-grounds-illustrated-v-chapel-groom.png"


def soft_mask_from_poly(
    shape: tuple[int, int],
    polygons: list[list[tuple[int, int]]],
    blur: float = 2.2,
) -> np.ndarray:
    h, w = shape
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    for poly in polygons:
        d.polygon(poly, fill=255)
    if blur > 0:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.array(im).astype(np.float32) / 255.0


def soft_mask_from_ellipse(
    shape: tuple[int, int],
    boxes: list[tuple[int, int, int, int]],
    blur: float = 1.8,
) -> np.ndarray:
    h, w = shape
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1 in boxes:
        d.ellipse([x0, y0, x1, y1], fill=255)
    if blur > 0:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.array(im).astype(np.float32) / 255.0


def soft_line_mask(
    shape: tuple[int, int],
    pts: list[tuple[int, int]],
    width: int,
    blur: float = 2.0,
) -> np.ndarray:
    h, w = shape
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    d.line(pts, fill=255, width=width)
    if blur > 0:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.array(im).astype(np.float32) / 255.0


def clone_patch(
    img: np.ndarray,
    mask: np.ndarray,
    src_offset: tuple[int, int],
    jitter: float = 0.0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Clone pixels from (x+dx, y+dy) into masked region with soft alpha."""
    h, w = mask.shape
    dx, dy = src_offset
    out = img.copy()
    ys, xs = np.where(mask > 0.02)
    if len(xs) == 0:
        return out
    for y, x in zip(ys, xs):
        sx = int(np.clip(x + dx, 0, w - 1))
        sy = int(np.clip(y + dy, 0, h - 1))
        a = float(mask[y, x])
        pix = img[sy, sx].astype(np.float32)
        if rng is not None and jitter > 0:
            pix = np.clip(pix + rng.normal(0, jitter, 3), 0, 255)
        out[y, x] = (1 - a) * img[y, x] + a * pix
    return out


def sample_fill(
    img: np.ndarray,
    mask: np.ndarray,
    sample_box: tuple[int, int, int, int],
    rng: np.random.Generator,
) -> np.ndarray:
    """Fill masked area by randomly sampling pixels from sample_box (textured)."""
    x0, y0, x1, y1 = sample_box
    patch = img[y0:y1, x0:x1]
    ph, pw = patch.shape[:2]
    out = img.copy().astype(np.float32)
    ys, xs = np.where(mask > 0.02)
    for y, x in zip(ys, xs):
        a = float(mask[y, x])
        sy = int(rng.integers(0, ph))
        sx = int(rng.integers(0, pw))
        pix = patch[sy, sx].astype(np.float32)
        # slight local tint variation
        pix = np.clip(pix + rng.normal(0, 2.5, 3), 0, 255)
        out[y, x] = (1 - a) * out[y, x] + a * pix
    return np.clip(out, 0, 255).astype(np.uint8)


def inpaint_masked(img: np.ndarray, mask: np.ndarray, radius: int = 4) -> np.ndarray:
    m = (mask > 0.35).astype(np.uint8) * 255
    # Feather: inpaint hard core, then blend soft edge with original via mask
    inpainted = cv2.inpaint(img, m, radius, cv2.INPAINT_TELEA)
    a = mask[..., None]
    return np.clip((1 - a) * img.astype(np.float32) + a * inpainted.astype(np.float32), 0, 255).astype(
        np.uint8
    )


def main() -> None:
    rng = np.random.default_rng(42)
    img = np.array(Image.open(SRC).convert("RGB"))
    H, W = img.shape[:2]
    assert (W, H) == (1024, 1536), f"unexpected size {(W, H)}"

    # ------------------------------------------------------------------
    # Target 1: door + white walkway on west gable facing parking.
    # This feature sits on Groom's Quarters west gable (pin ~38%,58%),
    # left end facing the parking lot — dark door + bright walkway.
    # Door bbox (abs): ~ (333, 1006)-(352, 1036)
    # Walkway: diagonal strip from door base toward parking SW.
    # ------------------------------------------------------------------
    door_poly = [
        (333, 1005),
        (352, 1005),
        (353, 1036),
        (332, 1036),
    ]
    # Small stoop / white landing immediately below door
    stoop_poly = [
        (328, 1032),
        (354, 1032),
        (350, 1042),
        (324, 1044),
    ]
    walk_pts = [
        (340, 1036),
        (328, 1048),
        (315, 1062),
        (300, 1076),
        (285, 1088),
        (270, 1098),
    ]

    door_mask = soft_mask_from_poly((H, W), [door_poly], blur=1.6)
    stoop_mask = soft_mask_from_poly((H, W), [stoop_poly], blur=1.8)
    walk_mask = soft_line_mask((H, W), walk_pts, width=14, blur=2.4)
    # Expand walk slightly with color confirmation near path
    region = img[1025:1105, 265:360]
    rr, gg, bb = [region[:, :, i].astype(int) for i in range(3)]
    bright = (rr > 195) & (gg > 170) & (bb > 115) & (rr > bb + 35)
    color_walk = np.zeros((H, W), dtype=np.float32)
    color_walk[1025:1105, 265:360] = bright.astype(np.float32)
    # blur color walk
    cw = Image.fromarray((color_walk * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    color_walk = np.array(cw).astype(np.float32) / 255.0

    door_full = np.clip(door_mask + stoop_mask * 0.85, 0, 1)
    walk_full = np.clip(np.maximum(walk_mask, color_walk * 0.95), 0, 1)
    # Don't erase bushes heavily — reduce walk mask where green vegetation
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    green = (hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 95) & (hsv[:, :, 1] > 50) & (hsv[:, :, 2] > 45)
    walk_full = np.where(green, walk_full * 0.15, walk_full)

    door_box = (
        int(np.where(door_full > 0.2)[1].min()),
        int(np.where(door_full > 0.2)[0].min()),
        int(np.where(door_full > 0.2)[1].max()),
        int(np.where(door_full > 0.2)[0].max()),
    )
    walk_box = (
        int(np.where(walk_full > 0.2)[1].min()),
        int(np.where(walk_full > 0.2)[0].min()),
        int(np.where(walk_full > 0.2)[1].max()),
        int(np.where(walk_full > 0.2)[0].max()),
    )
    print(f"DOOR mask bbox (x0,y0,x1,y1): {door_box}")
    print(f"WALK mask bbox (x0,y0,x1,y1): {walk_box}")

    # Debug door region
    dbg = Image.fromarray(img).crop((290, 980, 390, 1110))
    dbg.save(MAPS / "_debug-door-region.png")

    # Clone wall siding from above/right of door onto door
    work = clone_patch(img, door_full, src_offset=(10, -28), jitter=1.5, rng=rng)
    # Also blend a second sample from left-of-door wall strip upward
    work = clone_patch(work, door_full * 0.55, src_offset=(-8, -22), jitter=1.2, rng=rng)
    # Inpaint residual door seam
    work = inpaint_masked(work, door_full, radius=3)

    # Walkway -> grass sampled from nearby lawn (left/below of path)
    work = sample_fill(work, walk_full, sample_box=(280, 1055, 320, 1095), rng=rng)
    work = inpaint_masked(work, walk_full * 0.75, radius=4)

    # ------------------------------------------------------------------
    # Target 2: gravel/dirt fork between Groom's Quarters & Courtyard
    # that connects into the parking lot (top-right corner of lot).
    # ------------------------------------------------------------------
    # Centerline of fork connector: from parking NE corner up between buildings
    fork_pts = [
        (355, 980),  # near parking / lawn edge below groom-court gap
        (365, 960),
        (378, 940),
        (390, 920),
        (400, 900),
        (412, 880),
        (425, 860),
    ]
    # Also the strip between groom and courtyard leading toward parking
    fork_pts_b = [
        (380, 1000),
        (390, 980),
        (400, 960),
        (410, 940),
        (418, 920),
        (428, 900),
    ]
    fork_mask = soft_line_mask((H, W), fork_pts, width=22, blur=2.6)
    fork_mask = np.maximum(fork_mask, soft_line_mask((H, W), fork_pts_b, width=18, blur=2.4))

    # Color assist: tan path pixels in the corridor (not courtyard stone, not roof)
    y0, y1, x0, x1 = 850, 1020, 340, 450
    region = work[y0:y1, x0:x1]
    rr, gg, bb = [region[:, :, i].astype(int) for i in range(3)]
    tan = (
        (rr > 145)
        & (gg > 130)
        & (bb > 95)
        & (bb < 155)
        & (np.abs(rr - gg) < 35)
        & (rr > bb + 18)
        & (gg > bb + 12)
    )
    # Exclude greener lawn
    tan &= ~((gg > rr - 5) & (gg > bb + 20) & (gg > 100))
    # Exclude building browns (lower total / more R dominant with low B)
    tan &= ~((rr > 100) & (bb < 90) & (rr > gg + 25) & (rr + gg + bb < 380))
    color_fork = np.zeros((H, W), dtype=np.float32)
    color_fork[y0:y1, x0:x1] = tan.astype(np.float32)
    cf = Image.fromarray((color_fork * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.8))
    color_fork = np.array(cf).astype(np.float32) / 255.0

    fork_full = np.clip(np.maximum(fork_mask, color_fork * 0.9), 0, 1)
    # Protect building / courtyard / water: reduce where not grass-or-path corridor
    # Keep mask only in a polygon corridor
    corridor = soft_mask_from_poly(
        (H, W),
        [
            [
                (350, 1010),
                (375, 1010),
                (430, 880),
                (455, 860),
                (445, 850),
                (400, 870),
                (360, 950),
                (345, 1000),
            ]
        ],
        blur=2.0,
    )
    fork_full *= corridor
    # Don't eat green trees heavily
    fork_full = np.where(green & (hsv[:, :, 2] < 90), fork_full * 0.1, fork_full)

    if (fork_full > 0.2).any():
        fork_box = (
            int(np.where(fork_full > 0.2)[1].min()),
            int(np.where(fork_full > 0.2)[0].min()),
            int(np.where(fork_full > 0.2)[1].max()),
            int(np.where(fork_full > 0.2)[0].max()),
        )
        print(f"FORK mask bbox (x0,y0,x1,y1): {fork_box}")
    else:
        fork_box = (0, 0, 0, 0)
        print("FORK mask empty!")

    # Fill fork with grass sampled from adjacent lawn (west of corridor)
    work = sample_fill(work, fork_full, sample_box=(300, 920, 345, 980), rng=rng)
    work = sample_fill(work, fork_full * 0.5, sample_box=(355, 1000, 385, 1040), rng=rng)
    work = inpaint_masked(work, fork_full * 0.65, radius=5)

    # Soft local blur on edited seams
    for m in (door_full, walk_full, fork_full):
        edge = (m > 0.08) & (m < 0.85)
        if not edge.any():
            continue
        blurred = cv2.GaussianBlur(work, (3, 3), 0)
        a = (edge.astype(np.float32) * 0.45)[..., None]
        work = np.clip((1 - a) * work.astype(np.float32) + a * blurred.astype(np.float32), 0, 255).astype(
            np.uint8
        )

    Image.fromarray(work).save(OUT)
    shutil.copy2(OUT, OUT_COPY)
    print(f"Wrote {OUT}")
    print(f"Copied {OUT_COPY}")

    # QA crops
    Image.fromarray(work).crop((300, 990, 380, 1100)).save(MAPS / "_qa-door-after.png")
    Image.fromarray(work).crop((330, 850, 470, 1020)).save(MAPS / "_qa-fork-after.png")
    Image.fromarray(work).crop((200, 750, 560, 1420)).save(MAPS / "_qa-cluster-after.png")
    print("Saved QA crops: _qa-door-after.png, _qa-fork-after.png, _qa-cluster-after.png")

    # Mask overlay debug
    ov = work.copy()
    ov[door_full > 0.3] = (255, 40, 40)
    ov[walk_full > 0.3] = (40, 220, 255)
    ov[fork_full > 0.3] = (255, 220, 40)
    Image.fromarray(ov).crop((250, 820, 480, 1120)).save(MAPS / "_debug-masks-overlay.png")


if __name__ == "__main__":
    main()
