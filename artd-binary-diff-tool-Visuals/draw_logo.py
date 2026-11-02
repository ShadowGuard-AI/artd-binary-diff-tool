#!/usr/bin/env python3
"""Star ball logo: pierced brass globe at three quarter turn in oak cradle, one lit aperture.
v1: apertures even sized like rivets (named flaw). v2: no cradle, ball floats like a planet (flaw)."""
import sys, random, math
from PIL import Image, ImageDraw, ImageFont
random.seed(7); mode=sys.argv[1] if len(sys.argv)>1 else "ship"; out=sys.argv[2]
F="fonts/BadeenDisplay.ttf"; W,H=1200,1000
img=Image.new("RGB",(W,H),(26,74,48)); d=ImageDraw.Draw(img,"RGBA")
CREAM=(246,238,214)
cx,cy,R=600,360,258
# cradle ring gripping lower third (absent in v2)
if mode!="v2":
    d.polygon([(cx-110,cy+R+28),(cx+110,cy+R+28),(cx+160,cy+R+70),(cx-160,cy+R+70)],fill=(122,92,54))
d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(152,120,64),outline=(200,168,96),width=6)
# shading for three quarter turn
d.ellipse([cx-R+30,cy-R+24,cx+60,cy+120],fill=(168,134,74))
# apertures: big grouped at constellation patches, small scattered (even rivets in v1)
patches=[(cx-110,cy-90),(cx+120,cy-30),(cx-30,cy+110)]
for (px,py) in patches:
    for _ in range(16):
        x=px+random.randint(-58,58); y=py+random.randint(-44,44)
        if (x-cx)**2+(y-cy)**2<(R-24)**2:
            s=random.choice([13,16,19]) if mode!="v1" else 9
            d.ellipse([x-s/2,y-s/2,x+s/2,y+s/2],fill=(52,44,30),outline=(104,82,42),width=2)
for _ in range(120):
    a=random.uniform(0,6.28); rr=random.uniform(0,R-20); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr
    s=random.choice([5,6,8]) if mode!="v1" else 9
    d.ellipse([x-s/2,y-s/2,x+s/2,y+s/2],fill=(52,44,30))
# one lit aperture upper left
d.ellipse([cx-128,cy-122,cx-104,cy-98],fill=(255,250,226),outline=(255,244,200),width=3)
d.ellipse([cx-120,cy-114,cx-112,cy-106],fill=(255,255,244))
if mode!="v2":  # cradle ring over the lower third, gripping the ball
    d.arc([cx-R-24,cy-R+120,cx+R+24,cy+R-10],20,160,fill=(140,106,62),width=30)
try: f=ImageFont.truetype(F,62)
except: f=ImageFont.load_default()
d.text((600,760),"artd-binary-diff-tool",font=f,fill=CREAM,anchor="ma")
d.text((600,852),"The Planetarium's Star Ball",font=ImageFont.truetype(F,38),fill=(214,226,206),anchor="ma")
img.save(out)
if mode=="ship": img.resize((64,54)).save("scratch/logo64-ship.png")
print(out,mode)
