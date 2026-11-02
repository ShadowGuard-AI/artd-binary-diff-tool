#!/usr/bin/env python3
"""Planetarium banner: chamber, star ball on platform, curved seats, dot charts, cast brass title on platform front only.
v1: title on a wall chart frame (wrong carrier). v2: charts carry names/figures (flaw)."""
import sys, random, math
from PIL import Image, ImageDraw, ImageFont
random.seed(15); mode=sys.argv[1] if len(sys.argv)>1 else "ship"; out=sys.argv[2]
F="fonts/BadeenDisplay.ttf"; W,H=1600,900
img=Image.new("RGB",(W,H),(24,42,32)); d=ImageDraw.Draw(img,"RGBA")
CREAM=(246,238,214)
for y in range(0,500): d.line([(0,y),(W,y)],fill=(24+y//22,42+y//18,32+y//20))
for (cx,cy,r,n) in [(280,130,90,26),(740,84,120,34),(1200,140,100,28),(520,230,70,18),(1020,240,64,16)]:
    for _ in range(n):
        a=random.uniform(0,6.28); rr=random.uniform(0,r); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*0.6; s=random.choice([2,3,4]); d.ellipse([x,y,x+s,y+s],fill=CREAM)
for _ in range(110): x=random.randint(20,1580); y=random.randint(14,360); d.ellipse([x,y,x+2,y+2],fill=(220,214,190))
d.rectangle([0,420,W,620],fill=(52,44,32))
for x in range(0,W,120): d.line([(x,420),(x,620)],fill=(40,32,22),width=3)
# framed dot charts between doors, dots only (names in v2 flaw)
for (x,dense) in [(70,26),(420,10),(1180,22),(1420,12)]:
    d.rectangle([x,452,x+150,572],fill=(238,232,210),outline=(120,92,52),width=5)
    for _ in range(dense):
        px=x+random.randint(12,138); py=452+random.randint(12,108); d.ellipse([px,py,px+4,py+4],fill=(40,44,40))
    if mode=="v2":
        try: fs=ImageFont.truetype(F,22)
        except: fs=ImageFont.load_default()
        d.text((x+75,540),"Orion",font=fs,fill=(40,44,40),anchor="mm")
d.rectangle([730,452,790,572],fill=(30,28,24)); d.rectangle([1010,452,1070,572],fill=(30,28,24))  # doors
# curved rows of bottle green seats
for row,(y,w0) in enumerate([(690,1500),(770,1560)]):
    for x in range(60,W-160,190):
        d.rounded_rectangle([x,y,x+160,y+92],radius=24,fill=(26,74,48),outline=(18,52,34),width=3)
        if random.random()<0.4: px=x+random.randint(30,130); d.ellipse([px,y+16,px+5,y+21],fill=CREAM)
# platform centre + projector
d.polygon([(560,700),(1040,700),(1100,790),(500,790)],fill=(140,106,62))
d.rectangle([500,700,1100,742],fill=(122,92,54))
d.rectangle([716,470,884,560],fill=(30,34,30)); d.rectangle([736,448,864,474],fill=(44,48,44))
cx,cy,R=800,330,118
d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(152,120,64),outline=(200,168,96),width=5)
for _ in range(130):
    a=random.uniform(0,6.28); rr=random.uniform(0,R-12); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr; s=random.choice([3,5,7,10]); glow=random.random()<0.18
    d.ellipse([x-s/2,y-s/2,x+s/2,y+s/2],fill=(250,242,214) if glow else (52,44,30))
d.line([(620,690),(548,566)],fill=(196,170,110),width=6)  # lecturer pointer at rail
# control desk side with single lit dial
d.rectangle([1240,600,1420,690],fill=(36,40,36)); d.ellipse([1300,618,1352,670],outline=CREAM,width=3); d.ellipse([1322,640,1330,648],fill=CREAM)
# cast brass title across platform front (ship/v2); v1 wrongly on chart frame
try: fb=ImageFont.truetype(F,54)
except: fb=ImageFont.load_default()
if mode=="v1":
    d.rectangle([420,452,720,572],fill=(238,232,210),outline=(120,92,52),width=5)
    d.text((570,512),"artd-binary-diff-tool",font=ImageFont.truetype(F,26),fill=(40,44,40),anchor="mm")
else:
    d.text((800,720),"artd-binary-diff-tool",font=fb,fill=(206,172,96),anchor="mm")
img.save(out); print(out,mode)
