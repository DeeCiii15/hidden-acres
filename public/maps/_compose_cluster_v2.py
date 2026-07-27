from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageChops
import os

base_path = r"C:\Dev\hidden-acres\public\maps\ref-cluster-preferred-base-1024.png"
# v2 has clearer long N-S hall + white roof north of courtyard
patch_path = r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets\cluster-patch-earth-arch-v2.png"
out_live = r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png"
out_backup = r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated-v-map-cluster-v2.png"
qa_dir = r"C:\Dev\hidden-acres\public\maps\_qa-crops-cluster-v2"
os.makedirs(qa_dir, exist_ok=True)

base = Image.open(base_path).convert("RGBA")
patch = Image.open(patch_path).convert("RGBA")
print("base", base.size, "patch", patch.size)

pw, ph = patch.size
# Trim outer trees; cut south trailers (not on preferred)
left = int(pw * 0.05)
top = int(ph * 0.02)
right = int(pw * 0.97)
bottom = int(ph * 0.86)
patch_c = patch.crop((left, top, right, bottom))

# Larger placement to cover preferred old Groom's (NW near pond) + full cluster
target_w = 540
aspect = patch_c.height / patch_c.width
target_h = int(target_w * aspect)
patch_r = patch_c.resize((target_w, target_h), Image.Resampling.LANCZOS)
print("patch resized", patch_r.size)

# Shift up/left enough to cover old Groom's Quarters near pond edge
px = 250
py = 860

# Soft mask — stronger center, long feather
mask = Image.new("L", patch_r.size, 0)
draw = ImageDraw.Draw(mask)
inset = 22
draw.rounded_rectangle(
    [inset, inset, patch_r.width - inset - 1, patch_r.height - inset - 1],
    radius=70,
    fill=255,
)
mask = mask.filter(ImageFilter.GaussianBlur(radius=32))

# Gentle style match toward preferred softness
patch_r = ImageEnhance.Contrast(patch_r).enhance(0.90)
patch_r = ImageEnhance.Color(patch_r).enhance(0.93)
patch_r = ImageEnhance.Sharpness(patch_r).enhance(0.85)

out = base.copy()
out.paste(patch_r, (px, py), mask)

# Extra soft cleanup: hide leftover preferred Groom's near pond (NW of new cluster)
# Sample lawn color near (340, 980) and soft-paint a small oval if old building ghosts
# Use a tiny grass clone from preferred lawn north of cluster
lawn_src = base.crop((400, 780, 520, 860)).resize((140, 100), Image.Resampling.LANCZOS)
lawn_mask = Image.new("L", lawn_src.size, 0)
ld = ImageDraw.Draw(lawn_mask)
ld.ellipse([8, 8, lawn_src.width - 9, lawn_src.height - 9], fill=200)
lawn_mask = lawn_mask.filter(ImageFilter.GaussianBlur(radius=12))
# Place over typical old Groom's location (near pond SE edge)
out.paste(lawn_src, (320, 900), lawn_mask)

rgb = out.convert("RGB")
rgb.save(out_live, optimize=True)
rgb.save(out_backup, optimize=True)

# QA
qa = out.copy()
d = ImageDraw.Draw(qa)
d.rectangle([px, py, px + target_w, py + target_h], outline=(255, 0, 0, 180), width=3)
qa.convert("RGB").save(os.path.join(qa_dir, "composite-placement-v2.png"))
rgb.crop((220, 820, 820, 1400)).save(os.path.join(qa_dir, "result-cluster-crop-v2.png"))
rgb.crop((0, 0, 1024, 1536)).save(os.path.join(qa_dir, "result-full.png"))

print("saved", out_live, rgb.size)
print("placement", px, py, target_w, target_h)
