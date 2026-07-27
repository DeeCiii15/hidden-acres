from PIL import Image, ImageDraw
im=Image.open(r"C:\Dev\hidden-acres\public\maps\hidden-acres-grounds-illustrated.png").convert("RGB")
w,h=im.size
x,y=int(42.2/100*w), int(35.4/100*h)
box=(max(0,x-70),max(0,y-95),min(w,x+70),min(h,y+50))
crop=im.crop(box).copy(); cd=ImageDraw.Draw(crop)
lx,ly=x-box[0],y-box[1]
cd.ellipse([lx-5,ly-5,lx+5,ly+5], outline=(255,0,0), width=2)
crop.save(r"C:\Dev\hidden-acres\public\maps\_qa-crops-v12\tip-the-chapel-fixed.png")
print("ok", w, h, x, y)
