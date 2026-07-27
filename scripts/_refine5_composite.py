from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path

src = Path(r"C:\dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
out_dir = Path(r"C:\dev\hidden-acres\public\maps")
assets = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets")

im = Image.open(src).convert("RGBA")
W, H = im.size
base = im.copy()


def soft_rect_mask(size, feather=12):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    w, h = size
    d.rectangle([feather, feather, w - 1 - feather, h - 1 - feather], fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather))


def clone_fill(dst, box):
    x0, y0, x1, y1 = box
    sw = x1 - x0
    sh = y1 - y0
    sx0 = max(0, x0 - sw - 20)
    sy0 = max(0, y0 - 10)
    sample = dst.crop((sx0, sy0, sx0 + sw, sy0 + sh))
    sx1 = min(W - sw, x1 + 10)
    sample2 = dst.crop((sx1, sy0, sx1 + sw, sy0 + sh))
    blended = Image.blend(sample, sample2, 0.35).filter(ImageFilter.GaussianBlur(1.2))
    mask = soft_rect_mask((sw, sh), feather=18)
    dst.paste(blended, (x0, y0), mask)


# --- 1) Move Groom's Quarters EAST ---
groom_box = (318, 888, 458, 1055)
shift = 55
gx0, gy0, gx1, gy1 = groom_box
groom_patch = base.crop(groom_box)
clone_fill(base, groom_box)
nx0 = gx0 + shift
ny0 = gy0
base.paste(groom_patch, (nx0, ny0), soft_rect_mask(groom_patch.size, feather=10))

# --- 2) Fat Ballroom T ---
stem_box = (430, 1125, 640, 1395)
sx0, sy0, sx1, sy1 = stem_box
stem = base.crop(stem_box)
scale_stem = 1.42
nsw = int(stem.size[0] * scale_stem)
nsh = stem.size[1]
stem_fat = stem.resize((nsw, nsh), Image.Resampling.LANCZOS)
scx = (sx0 + sx1) // 2
nsx0 = scx - nsw // 2
nsy0 = sy0
clone_fill(base, (sx0 - 30, sy0, sx1 + 30, sy1))
base.paste(stem_fat, (nsx0, nsy0), soft_rect_mask(stem_fat.size, feather=14))

cb_box = (290, 1045, 760, 1165)
cx0, cy0, cx1, cy1 = cb_box
cross = base.crop(cb_box)
ncw = int(cross.size[0] * 1.22)
nch = int(cross.size[1] * 1.28)
cross_fat = cross.resize((ncw, nch), Image.Resampling.LANCZOS)
ccx = (cx0 + cx1) // 2
ccy = (cy0 + cy1) // 2
ncx0 = ccx - ncw // 2
ncy0 = max(1025, ccy - nch // 2)
clone_fill(base, (cx0 - 40, cy0 - 10, cx1 + 40, cy1 + 20))
base.paste(cross_fat, (ncx0, ncy0), soft_rect_mask(cross_fat.size, feather=12))

result = base.convert("RGB")
cand = out_dir / "_refine5-pil-composite.png"
result.save(cand, quality=95)
result.save(assets / "hidden-acres-grounds-illustrated-v-map-refine5-pil.png", quality=95)

w, h = result.size
result.crop((int(w * 0.12), int(h * 0.45), int(w * 0.75), int(h * 0.82))).save(
    out_dir / "_qa-r5p-groom.png"
)
result.crop((int(w * 0.28), int(h * 0.55), int(w * 0.88), int(h * 0.95))).save(
    out_dir / "_qa-r5p-t.png"
)
result.crop((int(w * 0.18), int(h * 0.42), int(w * 0.92), int(h * 0.90))).save(
    out_dir / "_qa-r5p-cluster.png"
)
result.crop((0, int(h * 0.28), int(w * 0.55), int(h * 0.62))).save(
    out_dir / "_qa-r5p-bridge.png"
)
print("saved", cand)
print("groom shift", shift, "new x", nx0)
print("stem", nsx0, nsy0, nsw, nsh)
print("cross", ncx0, ncy0, ncw, nch)
