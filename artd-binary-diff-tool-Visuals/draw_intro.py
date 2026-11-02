#!/usr/bin/env python3
"""Planetarium intro, nothing readable. v1: charts carry dot names/marks (flaw: figures on charts).
v2: star ball drawn as a smooth planet globe with no apertures (flaw). Ship: pierced ball, dot-only charts."""
import sys, random, math
from PIL import Image, ImageDraw
random.seed(31); mode=sys.argv[1] if len(sys.argv)>1 else "ship"; out=sys.argv[2]
W,H=1600,900
img=Image.new("RGB",(W,H),(24,42,32)); d=ImageDraw.Draw(img,"RGBA")
# dome
for y in range(0,520):
    c=(24+y//22,42+y//18,32+y//20); d.line([(0,y),(W,y)],fill=c)
# projected sky: clusters + sparse fields
clusters=[(300,140,90,26),(760,90,120,34),(1220,150,100,28),(560,240,70,18)]
for (cx,cy,r,n) in clusters:
    for _ in range(n):
        a=random.uniform(0,6.28); rr=random.uniform(0,r); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*0.6; s=random.choice([2,3,3,4])
        d.ellipse([x,y,x+s,y+s],fill=(246,238,214))
for _ in range(120):
    x=random.randint(20,1580); y=random.randint(16,380); d.ellipse([x,y,x+2,y+2],fill=(220,214,190))
# chamber wall + oak panelling, framed dot charts (dots only)
d.rectangle([0,430,W,640],fill=(52,44,32))
for x in range(0,W,120): d.line([(x,430),(x,640)],fill=(40,32,22),width=3)
for (x,dense) in [(90,26),(1330,10)]:
    d.rectangle([x,462,x+180,592],fill=(238,232,210),outline=(120,92,52),width=6)
    for _ in range(dense):
        px=x+random.randint(14,166); py=462+random.randint(14,116); d.ellipse([px,py,px+4,py+4],fill=(40,44,40))
    if mode=="v1":
        for k in range(3): d.line([(x+20,500+k*26),(x+120,500+k*26)],fill=(40,44,40),width=4)
# oak platform edge lower centre
d.polygon([(520,900),(1080,900),(980,690),(620,690)],fill=(122,92,54)); d.rectangle([600,672,1000,694],fill=(140,106,62))
# mechanism housing + pointer leaning on rail
d.rectangle([716,540,884,676],fill=(30,34,30)); d.rectangle([736,516,864,544],fill=(44,48,44))
d.line([(640,700),(560,560)],fill=(196,170,110),width=6); d.ellipse([554,552,568,566],fill=(196,170,110))
# star ball sphere lit from within
cx,cy,R=800,392,148
d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(150,118,62),outline=(196,164,92),width=5)
if mode!="v2":
    for _ in range(210):
        a=random.uniform(0,6.28); rr=random.uniform(0,R-14); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr
        s=random.choice([3,4,5,7,9,12]); glow=random.random()<0.16
        d.ellipse([x-s/2,y-s/2,x+s/2,y+s/2],fill=(250,242,214) if glow else (52,44,30),outline=(110,86,44))
    d.ellipse([cx-92,cy-104,cx-76,cy-88],fill=(255,250,226))  # single bright aperture upper left area cluster
# light thrown upward (soft rays)
for a in range(-70,71,20): d.line([(cx,cy-120),(cx+math.sin(math.radians(a))*360,cy-330)],fill=(250,242,214,26),width=10)
# nearest bottle green seats, close, soft: headrests with stray points
for (x,y,w) in [(60,730,420),(590,756,420),(1120,730,420)]:
    d.rounded_rectangle([x,y,x+w,y+170],radius=40,fill=(26,74,48),outline=(18,52,34),width=4)
    d.rounded_rectangle([x+30,y+18,x+w-30,y+76],radius=22,fill=(32,88,58))
    for _ in range(2):
        px=x+random.randint(50,w-50); py=y+random.randint(28,60); d.ellipse([px,py,px+5,py+5],fill=(246,238,214))
img.save(out); print(out,mode)
