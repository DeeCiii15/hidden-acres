"""QA GenerateImage result vs clean resume-c and markup."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "public" / "maps"
ASSETS = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")

CLEAN = ASSETS / "hidden-acres-grounds-illustrated-v-map-resume-c.png"
MARKUP = MAPS / "hidden-acres-grounds-illustrated-v-map-resume-c-markup.png"
GEN = ASSETS / "hidden-acres-grounds-illustrated-v-map-resume-f-gen.png"
QA = MAPS / "_qa-resume-f"


def main() -> None:
    QA.mkdir(exist_ok=True)
    clean = cv2.imread(str(CLEAN))
    markup = cv2.imread(str(MARKUP))
    gen = cv2.imread(str(GEN))
    print("sizes", clean.shape, markup.shape, gen.shape)

    if gen.shape[:2] != clean.shape[:2]:
        gen_r = cv2.resize(gen, (clean.shape[1], clean.shape[0]), interpolation=cv2.INTER_AREA)
        print("resized gen to", gen_r.shape)
    else:
        gen_r = gen

    hsv = cv2.cvtColor(gen_r, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(hsv)
    blue = ((H >= 95) & (H <= 135) & (S >= 100) & (V >= 80)).astype(np.uint8) * 255
    red = (((H <= 12) | (H >= 165)) & (S >= 100) & (V >= 80)).astype(np.uint8) * 255
    print("gen blue px", int(blue.sum() / 255), "red px", int(red.sum() / 255))

    mhsv = cv2.cvtColor(markup, cv2.COLOR_BGR2HSV)
    MH, MS, MV = cv2.split(mhsv)
    mblue = ((MH >= 95) & (MH <= 135) & (MS >= 80) & (MV >= 70)).astype(np.uint8) * 255
    mred = (((MH <= 12) | (MH >= 165)) & (MS >= 90) & (MV >= 70)).astype(np.uint8) * 255
    print("markup blue", int(mblue.sum() / 255), "red", int(mred.sum() / 255))

    diff = cv2.absdiff(clean, gen_r).mean(axis=2)
    print(
        "mean absdiff",
        float(diff.mean()),
        "p95",
        float(np.percentile(diff, 95)),
        "p99",
        float(np.percentile(diff, 99)),
    )

    heat = np.clip(diff * 4, 0, 255).astype(np.uint8)
    cv2.imwrite(str(QA / "diff-heat.png"), cv2.applyColorMap(heat, cv2.COLORMAP_INFERNO))
    cv2.imwrite(str(QA / "gen-full.png"), gen_r)
    cv2.imwrite(str(QA / "clean-full.png"), clean)

    # Along blue mask: is gen more road-like (tan/low sat) than clean?
    blue_dil = cv2.dilate(mblue, np.ones((9, 9), np.uint8), iterations=2)
    red_dil = cv2.dilate(mred, np.ones((11, 11), np.uint8), iterations=2)

    def roadish(img: np.ndarray, mask: np.ndarray) -> tuple[float, float]:
        hsv_i = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        m = mask > 0
        if not np.any(m):
            return 0.0, 0.0
        # tan gravel: moderate V, low-mid S, H near yellow/brown
        H_i, S_i, V_i = hsv_i[..., 0], hsv_i[..., 1], hsv_i[..., 2]
        tan = ((H_i >= 8) & (H_i <= 35) & (S_i < 120) & (V_i > 120) & (V_i < 230)).astype(np.float32)
        green = ((H_i >= 35) & (H_i <= 95) & (S_i > 40) & (V_i > 40)).astype(np.float32)
        return float(tan[m].mean()), float(green[m].mean())

    bt_c, bg_c = roadish(clean, blue_dil)
    bt_g, bg_g = roadish(gen_r, blue_dil)
    rt_c, rg_c = roadish(clean, red_dil)
    rt_g, rg_g = roadish(gen_r, red_dil)
    print(f"BLUE zone tan/green clean={bt_c:.3f}/{bg_c:.3f} gen={bt_g:.3f}/{bg_g:.3f}")
    print(f"RED  zone tan/green clean={rt_c:.3f}/{rg_c:.3f} gen={rt_g:.3f}/{rg_g:.3f}")

    crops = {
        "pond-west": (220, 520, 40, 360),
        "north-field": (60, 280, 250, 900),
        "courtyard-n": (680, 980, 380, 720),
        "far-right": (40, 420, 780, 1020),
        "parking-w": (900, 1120, 220, 520),
        "mid-cottage": (320, 560, 280, 560),
    }
    for name, (y0, y1, x0, x1) in crops.items():
        grid = np.hstack([clean[y0:y1, x0:x1], markup[y0:y1, x0:x1], gen_r[y0:y1, x0:x1]])
        cv2.imwrite(str(QA / f"cmp-{name}.png"), grid)

    print("wrote QA to", QA)


if __name__ == "__main__":
    main()
