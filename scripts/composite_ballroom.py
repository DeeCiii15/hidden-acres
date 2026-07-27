from PIL import Image
from pathlib import Path
import shutil

full_path = Path(r"C:\dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png")
crop_path = Path(r"C:\Users\livingt\.cursor\projects\c-dev-hidden-acres\assets\_crop-ballroom-fixed.png")

out_full = full_path
out_alt = Path(r"C:\dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated-v-chapel-groom.png")
out_crop_copy = Path(r"C:\dev\hidden-acres\public\maps\_crop-ballroom-fixed.png")
out_verify = Path(r"C:\dev\hidden-acres\public\maps\_crop-ballroom-after.png")

box = (0, 614, 716, 1536)  # left, top, right, bottom
target_w, target_h = 716, 922
feather = 20

full = Image.open(full_path).convert("RGBA")
crop = Image.open(crop_path).convert("RGBA")

print(f"Full map before: {full.size}")
print(f"Fixed crop before: {crop.size}")

if crop.size != (target_w, target_h):
    crop = crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
    print(f"Resized crop to: {crop.size}")

# Feather top and right edges of the paste
mask = Image.new("L", (target_w, target_h), 255)
pix = mask.load()
for y in range(feather):
    a = int(255 * (y + 1) / feather)
    for x in range(target_w):
        pix[x, y] = min(pix[x, y], a)
for x in range(feather):
    rx = target_w - 1 - x
    a = int(255 * (x + 1) / feather)
    for y in range(target_h):
        pix[rx, y] = min(pix[rx, y], a)

composited = full.copy()
composited.paste(crop, (box[0], box[1]), mask)

rgb = composited.convert("RGB")
rgb.save(out_full, "PNG")
rgb.save(out_alt, "PNG")
shutil.copy2(crop_path, out_crop_copy)

verify = rgb.crop(box)
verify.save(out_verify, "PNG")

print("---")
print(f"Composited full map: {rgb.size} -> {out_full}")
print(f"Alt copy: {Image.open(out_alt).size} -> {out_alt}")
print(f"Fixed crop copy: {Image.open(out_crop_copy).size} -> {out_crop_copy}")
print(f"Verification crop: {verify.size} -> {out_verify}")
print("DONE")
