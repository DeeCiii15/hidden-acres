"""Remove vehicle road between chapel and pond; replace with lawn texture.

Method that worked (refine6): GenerateImage kept redrawing the road;
manual geometric mask + Telea inpaint + east-lawn texture blend.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

SRC = Path(
    r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets"
    r"\hidden-acres-grounds-illustrated-v-map-refine6-gen1.png"
)
MAPS = Path(r"C:\Dev\hidden-acres\public\maps")
OUT_ASSETS = Path(
    r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets"
    r"\hidden-acres-grounds-illustrated-v-map-refine6.png"
)


def main() -> None:
    src = cv2.imread(str(SRC))
    assert src is not None
    h, w = src.shape[:2]

    mask = np.zeros((h, w), np.uint8)
    pts = np.array(
        [
            [210, 600],
            [240, 610],
            [270, 625],
            [300, 635],
            [330, 645],
            [360, 655],
            [390, 665],
            [250, 590],
            [280, 605],
            [310, 618],
            [340, 630],
            [370, 642],
            [220, 620],
            [260, 635],
            [300, 650],
            [340, 660],
        ],
        dtype=np.int32,
    )
    for p in pts:
        cv2.circle(mask, tuple(map(int, p)), 18, 255, -1)

    poly = np.array(
        [
            [200, 585],
            [280, 595],
            [360, 625],
            [410, 655],
            [400, 685],
            [340, 690],
            [260, 670],
            [210, 640],
        ],
        dtype=np.int32,
    )
    cv2.fillPoly(mask, [poly], 255)
    mask = cv2.GaussianBlur(mask, (15, 15), 0)
    mask = (mask > 40).astype(np.uint8) * 255

    # Protect chapel footprint, pond water, west vertical road
    cv2.rectangle(mask, (300, 500), (430, 580), 0, -1)
    b, g, r = cv2.split(src)
    water = (b.astype(np.int16) - r.astype(np.int16)) > 18
    mask[water] = 0
    mask[:, :195] = 0

    base = cv2.inpaint(src, mask, 5, cv2.INPAINT_TELEA)
    clean = src[480:700, 450:720]
    ch, cw = clean.shape[:2]
    yy, xx = np.indices((h, w))
    src_y = ((yy - 540) % (ch - 20)) + 10
    src_x = ((xx - 150) % (cw - 20)) + 10
    lawn = clean[src_y, src_x]

    soft = cv2.GaussianBlur(mask, (31, 31), 0).astype(np.float32) / 255.0
    of = base.astype(np.float32)
    lf = lawn.astype(np.float32)
    for c in range(3):
        of[:, :, c] = of[:, :, c] * (1 - soft) + (lf[:, :, c] * 0.85 + of[:, :, c] * 0.15) * soft
    out = np.clip(of, 0, 255).astype(np.uint8)

    cv2.imwrite(str(OUT_ASSETS), out)
    cv2.imwrite(str(MAPS / "hidden-acres-grounds-illustrated-v-map-refine6.png"), out)
    cv2.imwrite(str(MAPS / "hidden-acres-grounds-illustrated.png"), out)
    print("mask pixels", int((mask > 0).sum()))
    print("wrote refine6 + live")


if __name__ == "__main__":
    main()
