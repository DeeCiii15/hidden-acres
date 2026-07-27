"""Apply satellite-guided layout fixes to the illustrated map.

ONLY:
1) Move Ceremony Pond bridge from east/north channel to south tip of island
2) Replace north roof wing (under Courtyard pin) with open courtyard + small fountain
   so the main building stops on the Bridal↔Courtyard pin line (capital-T)

Outside the allowed edit mask the output is pixel-identical to the source.
Preserves color scheme, art style, building style, landscaping style.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")
SRC = (
    ASSETS
    / "c__Users_livingt_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_base-ebc3b292-917f-4bef-9209-e9e70e868491.png"
)
MAPS = ROOT / "public" / "maps"
QA = MAPS / "_qa-crops-ballroom-t"
OUT_MASTER = MAPS / "hidden-acres-grounds-illustrated-v-map-ballroom-t.png"
OUT_LIVE = MAPS / "hidden-acres-grounds-illustrated.png"
FOUNTAIN_SRC = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-s.png"
FOUNTAIN_SRC_BOX = (368, 605, 408, 642)

# Bridge source (east channel) and south destination — satellite: south of island
BRIDGE_BOX = (205, 632, 258, 665)  # full span across east channel
BRIDGE_DEST = (185, 706)  # top-left paste on south tip
# Extra forced water strip if mask misses part of the deck
BRIDGE_FORCE_STRIP = (210, 640, 250, 656)

# Courtyard: north of bridal↔courtyard pin line; between groom (W) and bridal (E)
CUT_Y = 778
COURT_BOX = (300, 702, 392, CUT_Y)
FOUNTAIN_CENTER = (346, 738)

SILO_PROTECT = (340, 610, 410, 700)  # keep silo untouched
BRIDAL_X_MIN = 398  # do not write into bridal suite / trees east


def is_water(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (b > r + 8) & (g > 35) & (r < 105) & (b > 45) & (g < 150)


def is_grass(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (g > r + 10) & (g > b + 5) & (g > 55)


def is_roof(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (r > 95) & (r < 200) & (r > g + 10) & (r > b + 18) & (g < 155) & (b < 130)


def is_building(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    green = is_grass(rgb)
    warm = (r > 90) & (r < 215) & (r > g + 8) & (r > b + 14) & (g < 175)
    lum = (r.astype(np.int32) + g + b) / 3.0
    wall = (
        (lum > 125)
        & (r > 125)
        & (g > 115)
        & (b > 85)
        & ~((g > r + 5) & (g > b + 5))
    )
    eave = (lum < 100) & (lum > 28) & (r >= g - 6) & (g < 115) & ~((g > r + 8) & (g > b + 5))
    return ((is_roof(rgb) | warm | wall | eave) & ~green).astype(np.uint8)


def is_pin(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    return (g > 55) & (g < 140) & (r < 80) & (b < 85) & (g > r + 25)


def bridge_deck_mask(crop: np.ndarray) -> np.ndarray:
    """Only the thin span over water — not shore stones/grass."""
    h, w = crop.shape[:2]
    water = is_water(crop)
    grass = is_grass(crop)
    r, g, b = (crop[..., i].astype(np.int16) for i in range(3))
    deck = (
        ~water
        & ~grass
        & (r > 60)
        & (r < 160)
        & (g < 130)
        & (b < 120)
        & (r >= g - 8)
    )
    mask = np.zeros((h, w), np.uint8)
    for y in range(h):
        left_w = float(water[y, : max(1, w // 4)].mean())
        right_w = float(water[y, 3 * w // 4 :].mean())
        # Prefer rows that still have water nearby (channel crossing)
        mid_w = float(water[y, w // 4 : 3 * w // 4].mean())
        if left_w + mid_w + right_w < 0.15:
            continue
        row = deck[y].copy()
        # drop rightmost shore column band
        row[int(w * 0.82) :] = False
        if row.sum() >= 3:
            mask[y] = row.astype(np.uint8) * 255

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((2, 3), np.uint8), 1)
    n, lab, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8), 8)
    if n > 1:
        best, score = 1, -1.0
        for i in range(1, n):
            # prefer wide + short (horizontal bridge)
            ww = stats[i, cv2.CC_STAT_WIDTH]
            hh = max(1, stats[i, cv2.CC_STAT_HEIGHT])
            area = stats[i, cv2.CC_STAT_AREA]
            s = ww / hh * area
            if area > 12 and s > score:
                best, score = i, s
        mask = (lab == best).astype(np.uint8) * 255
    # slight vertical thicken so deck is continuous
    mask = cv2.dilate(mask, np.ones((2, 1), np.uint8), 1)
    return mask


def fill_hole_with_water(out: np.ndarray, hole: np.ndarray, water_donor: np.ndarray) -> np.ndarray:
    """Clone real water pixels into hole; light TELEA only on 1px rim."""
    ys, xs = np.where(hole > 0)
    if len(ys) == 0:
        return out
    donor_water = is_water(water_donor)
    if not donor_water.any():
        # expand search in out around hole bbox
        y0, y1 = max(0, ys.min() - 20), min(out.shape[0], ys.max() + 21)
        x0, x1 = max(0, xs.min() - 40), min(out.shape[1], xs.max() + 5)
        water_donor = out[y0:y1, x0:x1]
        donor_water = is_water(water_donor)
        dy0, dx0 = y0, x0
    else:
        dy0 = dx0 = 0
        # water_donor is already a crop; map via relative coords below
        pass

    # Prefer donor as absolute region left of bridge
    abs_donor = out[ys.min() - 2 : ys.max() + 3, max(0, xs.min() - 36) : xs.min()]
    abs_w = is_water(abs_donor)
    mean_w = (
        abs_donor[abs_w].mean(axis=0).astype(np.uint8)
        if abs_w.any()
        else np.array([45, 95, 110], np.uint8)
    )

    result = out.copy()
    rng = np.random.default_rng(7)
    for y, x in zip(ys, xs):
        local = abs_donor
        lw = abs_w
        if lw.any():
            ly, lx = np.where(lw)
            # pick nearby donor by row preference
            row_mask = np.abs(ly - (y - (ys.min() - 2))) <= 2
            if row_mask.any():
                ly, lx = ly[row_mask], lx[row_mask]
            j = int(rng.integers(0, len(ly)))
            result[y, x] = local[ly[j], lx[j]]
        else:
            result[y, x] = mean_w

    # Soft rim blend only
    rim = cv2.dilate(hole, np.ones((3, 3), np.uint8), 1)
    rim = cv2.subtract(rim, cv2.erode(hole, np.ones((3, 3), np.uint8), 1))
    bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
    result = cv2.cvtColor(cv2.inpaint(bgr, rim, 2, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    # Restore solid hole interior from clone (TELEA can muddy center)
    solid = cv2.erode(hole, np.ones((3, 3), np.uint8), 1)
    # re-clone solid interior
    tmp = result.copy()
    for y, x in zip(*np.where(solid > 0)):
        if abs_w.any():
            ly, lx = np.where(abs_w)
            j = int(((y * 17) + x) % len(ly))
            tmp[y, x] = abs_donor[ly[j], lx[j]]
        else:
            tmp[y, x] = mean_w
    result[solid > 0] = tmp[solid > 0]
    return result


def move_bridge(base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    out = base.copy()
    x0, y0, x1, y1 = BRIDGE_BOX
    crop = base[y0:y1, x0:x1].copy()
    mask = bridge_deck_mask(crop)
    ph, pw = crop.shape[:2]

    hole = np.zeros(out.shape[:2], np.uint8)
    hole[y0:y1, x0:x1] = mask
    fx0, fy0, fx1, fy1 = BRIDGE_FORCE_STRIP
    ly0, ly1 = max(0, fy0 - y0), min(y1 - y0, fy1 - y0)
    lx0, lx1 = max(0, fx0 - x0), min(x1 - x0, fx1 - x0)
    if ly1 > ly0 and lx1 > lx0:
        sub = crop[ly0:ly1, lx0:lx1]
        # Clear non-grass pixels in the known deck corridor (bridge + water edge)
        force = ((~is_grass(sub)).astype(np.uint8) * 255)
        hole[y0 + ly0 : y0 + ly1, x0 + lx0 : x0 + lx1] = np.maximum(
            hole[y0 + ly0 : y0 + ly1, x0 + lx0 : x0 + lx1], force
        )
    hole = cv2.dilate(hole, np.ones((3, 3), np.uint8), 1)
    # Do not erase island tree canopy west of the channel
    xx = np.arange(out.shape[1])[None, :]
    hole[is_grass(out) & (xx < 212)] = 0
    out = fill_hole_with_water(out, hole, out[y0:y1, max(0, x0 - 36) : x0])

    # Paste south — hard alpha from deck mask only
    dx, dy = BRIDGE_DEST
    a2 = (mask > 0).astype(np.float32)
    a2 = cv2.GaussianBlur(a2, (0, 0), 0.4)
    a2 = np.clip(a2 * 1.35, 0, 1)
    dest_rgb = out[dy : dy + ph, dx : dx + pw]
    # Do not overwrite dense grass/trees at dest with shore leftovers
    dest_block = is_grass(dest_rgb) & (a2 < 0.85)
    a2 = np.where(dest_block, 0.0, a2)
    a = a2[..., None]
    dest = dest_rgb.astype(np.float32)
    out[dy : dy + ph, dx : dx + pw] = np.clip(
        dest * (1.0 - a) + crop.astype(np.float32) * a, 0, 255
    ).astype(np.uint8)

    wrote = hole.astype(bool)
    wrote[dy : dy + ph, dx : dx + pw] |= a2 > 0.05
    return out, wrote


def sample_paving(base: np.ndarray, h: int, w: int) -> np.ndarray:
    # Existing stone/path textures near pond & main complex
    samples = [
        base[560:600, 295:355],
        base[700:740, 245:305],
        base[575:615, 270:330],
        base[790:830, 320:380],
    ]
    tiles = [
        np.array(Image.fromarray(s).resize((w, h), Image.Resampling.LANCZOS)).astype(np.float32)
        for s in samples
    ]
    return (0.4 * tiles[0] + 0.25 * tiles[1] + 0.2 * tiles[2] + 0.15 * tiles[3]).clip(0, 255).astype(
        np.uint8
    )


def make_courtyard(base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    out = base.copy()
    wrote = np.zeros(base.shape[:2], dtype=bool)
    x0, y0, x1, y1 = COURT_BOX
    x1 = min(x1, BRIDAL_X_MIN)
    # stay below silo
    y0 = max(y0, SILO_PROTECT[3] + 2)

    region = out[y0:y1, x0:x1]
    h, w = region.shape[:2]
    bld = is_building(region)
    # Dilate slightly so roof edges clear, but not into trees
    bld_u = cv2.dilate(bld, np.ones((3, 3), np.uint8), 1)
    pin = is_pin(region)
    trees = is_grass(region)

    paving = sample_paving(base, h, w).astype(np.float32)
    alpha = bld_u.astype(np.float32)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.0)
    alpha = np.where(pin | trees, 0.0, alpha)
    interior = cv2.erode(bld_u, np.ones((2, 2), np.uint8), 1) > 0
    alpha = np.where(interior & ~(pin | trees), np.maximum(alpha, 0.92), alpha)

    blended = np.clip(
        region.astype(np.float32) * (1.0 - alpha[..., None]) + paving * alpha[..., None],
        0,
        255,
    ).astype(np.uint8)
    out[y0:y1, x0:x1] = blended
    wrote[y0:y1, x0:x1] |= alpha > 0.05

    # Fountain sprite from resume-s — soft circular composite
    if FOUNTAIN_SRC.exists():
        src = np.array(Image.open(FOUNTAIN_SRC).convert("RGB"))
        fx0, fy0, fx1, fy1 = FOUNTAIN_SRC_BOX
        sprite = src[fy0:fy1, fx0:fx1].copy()
        sh, sw = sprite.shape[:2]
        rr, gg, bb = (sprite[..., i].astype(np.int16) for i in range(3))
        green = (gg > rr + 12) & (gg > bb + 8) & (gg > 55)
        smask = (~green).astype(np.float32)
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        cy_s, cx_s = sh / 2.0, sw / 2.0
        rad = min(sh, sw) / 2.15
        circ = np.clip(1.0 - (((xx - cx_s) / rad) ** 2 + ((yy - cy_s) / rad) ** 2), 0, 1)
        smask = cv2.GaussianBlur(smask * circ, (0, 0), 0.9)
        fcx, fcy = FOUNTAIN_CENTER
        px0, py0 = fcx - sw // 2, fcy - sh // 2
        a = smask[..., None]
        dest = out[py0 : py0 + sh, px0 : px0 + sw].astype(np.float32)
        scale = (dest.mean() + 1e-3) / (sprite.astype(np.float32).mean() + 1e-3)
        sprite_f = np.clip(sprite.astype(np.float32) * float(np.clip(scale, 0.88, 1.18)), 0, 255)
        out[py0 : py0 + sh, px0 : px0 + sw] = np.clip(
            dest * (1.0 - a) + sprite_f * a, 0, 255
        ).astype(np.uint8)
        wrote[py0 : py0 + sh, px0 : px0 + sw] |= smask > 0.05

    return out, wrote


def main() -> None:
    assert SRC.exists(), SRC
    base = np.array(Image.open(SRC).convert("RGB"))
    assert base.shape[:2] == (1024, 682), base.shape

    work, wrote_b = move_bridge(base)
    work, wrote_c = make_courtyard(work)
    wrote = wrote_b | wrote_c

    # Hard protect silo + bridal east
    sx0, sy0, sx1, sy1 = SILO_PROTECT
    wrote[sy0:sy1, sx0:sx1] = False
    wrote[:, BRIDAL_X_MIN:] = False

    out = base.copy()
    out[wrote] = work[wrote]

    outside = ~wrote
    max_out = int(np.abs(base.astype(np.int16) - out.astype(np.int16))[outside].max()) if outside.any() else 0
    print(f"Edit pixels: {int(wrote.sum())}")
    print(f"Max absdiff outside allowed: {max_out}")

    Image.fromarray(out).save(OUT_MASTER)
    Image.fromarray(out).resize((1024, 1536), Image.Resampling.LANCZOS).save(OUT_LIVE)
    Image.fromarray(out).save(ASSETS / "hidden-acres-grounds-illustrated-sat-guided.png")

    QA.mkdir(parents=True, exist_ok=True)

    def sbs(box, name, asset_name):
        x0, y0, x1, y1 = box
        gap = np.full((y1 - y0, 4, 3), 230, np.uint8)
        img = np.concatenate([base[y0:y1, x0:x1], gap, out[y0:y1, x0:x1]], 1)
        Image.fromarray(img).save(QA / name)
        Image.fromarray(img).save(ASSETS / asset_name)

    sbs((140, 540, 280, 760), "cmp-pond-bridge.png", "_qa-cmp-pond-bridge.png")
    sbs((250, 640, 460, 920), "cmp-courtyard-t.png", "_qa-cmp-courtyard-t.png")
    Image.fromarray(out[540:760, 140:280]).save(QA / "pond-bridge-after.png")
    Image.fromarray(out[640:920, 250:460]).save(QA / "courtyard-t-after.png")
    print("saved live + master + QA")


if __name__ == "__main__":
    main()
