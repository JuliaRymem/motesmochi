#!/usr/bin/env python3
"""Generate crisp 3D-style mochi characters."""

import os, math
from PIL import Image, ImageDraw, ImageFilter

S = 400
ICONS       = os.path.join(os.path.dirname(__file__), "icons")
PREVIEW     = os.path.join(os.path.dirname(__file__), "preview")
TRANSPARENT = os.path.join(os.path.dirname(__file__), "preview", "transparent")
os.makedirs(ICONS, exist_ok=True)
os.makedirs(PREVIEW, exist_ok=True)
os.makedirs(TRANSPARENT, exist_ok=True)


def new():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


# ── body: crisp circle + internal 3-D shading ───────────────────────────────

def body_layer(cx, cy, rx, ry, color):
    """Return RGBA image: solid ellipse with radial shading."""
    img = new()
    d = ImageDraw.Draw(img)
    # solid base
    d.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=color+(255,))

    # darken bottom-right edge
    dark = new()
    dd = ImageDraw.Draw(dark)
    dd.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=(0,0,0,0))
    edge = Image.new("RGBA",(S,S),(0,0,0,0))
    ed = ImageDraw.Draw(edge)
    ed.ellipse([cx-rx+6, cy-ry+6, cx+rx-6, cy+ry-6], fill=(0,0,0,0))
    # ring fill
    ring = new()
    rd = ImageDraw.Draw(ring)
    rd.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=(0,0,0,45))
    rd.ellipse([cx-rx+10, cy-ry+10, cx+rx-10, cy+ry-10], fill=(0,0,0,0))
    ring = ring.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(ring)

    # lighten top-left inner area
    lit = new()
    ld = ImageDraw.Draw(lit)
    ld.ellipse([cx-rx*0.7, cy-ry*0.75, cx+rx*0.05, cy+ry*0.05],
               fill=(255,255,255,35))
    lit = lit.filter(ImageFilter.GaussianBlur(22))
    img.alpha_composite(lit)

    # specular glint
    g = new()
    gd = ImageDraw.Draw(g)
    gd.ellipse([cx-rx*0.42, cy-ry*0.55, cx-rx*0.05, cy-ry*0.18],
               fill=(255,255,255,175))
    g = g.filter(ImageFilter.GaussianBlur(9))
    img.alpha_composite(g)

    # clip to ellipse
    mask = Image.new("L",(S,S),0)
    ImageDraw.Draw(mask).ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=255)
    img.putalpha(mask)
    return img


def draw_body(canvas, cx, cy, rx, ry, color):
    # drop shadow
    sh = new()
    sd = ImageDraw.Draw(sh)
    sd.ellipse([cx-rx*0.82, cy+ry*0.55, cx+rx*0.82, cy+ry*1.05],
               fill=(0,0,0,50))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(body_layer(cx,cy,rx,ry,color))


def eyes(canvas, cx, cy, spread=40, sz=16, col=(45,30,38)):
    d = ImageDraw.Draw(canvas)
    for dx in (-spread//2, spread//2):
        x = cx+dx
        d.ellipse([x-sz, cy-sz, x+sz, cy+sz], fill=col+(255,))
        d.ellipse([x-sz+4, cy-sz+3, x-sz+10, cy-sz+9], fill=(255,255,255,230))


def smile(canvas, cx, cy, w=30, col=(65,42,48)):
    ImageDraw.Draw(canvas).arc(
        [cx-w, cy-12, cx+w, cy+12], start=18, end=162,
        fill=col+(220,), width=4)


def blush(canvas, cx, cy, spread=54, col=(255,158,152,80)):
    b = new()
    ImageDraw.Draw(b).ellipse([0,0,0,0])  # dummy
    bd = ImageDraw.Draw(b)
    for dx in (-spread, spread):
        bd.ellipse([cx+dx-24,cy-12,cx+dx+24,cy+18], fill=col)
    b = b.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(b)


def gradient_bg(c1, c2):
    bg = Image.new("RGB",(S,S))
    d = ImageDraw.Draw(bg)
    for y in range(S):
        t = y/S
        d.line([(0,y),(S,y)],
               fill=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3)))
    return bg


def save(img, key, bg1, bg2):
    # transparent 400px
    img.save(os.path.join(TRANSPARENT, f"{key}.png"))
    # with background
    bg = gradient_bg(bg1, bg2).convert("RGBA")
    bg.alpha_composite(img)
    bg.resize((64,64), Image.LANCZOS).convert("RGBA").save(
        os.path.join(ICONS, f"{key}.png"))
    bg.convert("RGB").save(os.path.join(PREVIEW, f"{key}.png"))
    print(f"  {key}")


# ── characters ───────────────────────────────────────────────────────────────

def vanilla():
    img = new(); cx,cy = S//2, S//2+18
    draw_body(img,cx,cy,148,148,(238,228,210))
    blush(img,cx,cy+22)
    eyes(img,cx,cy-8)
    smile(img,cx,cy+30)
    d=ImageDraw.Draw(img)
    d.line([cx+88,cy-148, cx+88,cy-68], fill=(175,138,92,230), width=5)
    d.polygon([(cx+90,cy-148),(cx+140,cy-128),(cx+90,cy-108)],
              fill=(218,82,72,235))
    save(img,"vanilla",(252,244,232),(236,222,204))

def sakura():
    img = new(); cx,cy = S//2, S//2+18
    draw_body(img,cx,cy,148,148,(242,182,198))
    blush(img,cx,cy+22,col=(255,118,142,105))
    eyes(img,cx,cy-8)
    smile(img,cx,cy+30)
    d=ImageDraw.Draw(img)
    for a in range(0,360,72):
        r=math.radians(a)
        px=cx+int(54*math.cos(r)); py=(cy-148)+int(20*math.sin(r))
        d.ellipse([px-15,py-11,px+15,py+11],fill=(255,212,224,205))
    d.ellipse([cx-15,cy-160,cx+15,cy-130],fill=(252,188,205,230))
    save(img,"sakura",(255,236,244),(250,212,230))

def matcha():
    img = new(); cx,cy = S//2, S//2+18
    draw_body(img,cx,cy,148,148,(152,198,145))
    blush(img,cx,cy+22,col=(125,188,120,95))
    eyes(img,cx,cy-8)
    smile(img,cx,cy+30)
    d=ImageDraw.Draw(img)
    for ox,ph in [(-32,0),(0,6),(32,3)]:
        for i in range(4):
            sy=cy-148-15-i*20; sx=cx+ox+int(9*math.sin(i*1.2+ph))
            d.ellipse([sx-6,sy-9,sx+6,sy+9],
                      fill=(200,228,195,max(0,155-i*45)))
    save(img,"matcha",(226,242,220),(196,226,188))

def sushi():
    img = new(); cx,cy = S//2, S//2+18
    draw_body(img,cx,cy,148,148,(240,235,220))
    band=new(); bd=ImageDraw.Draw(band)
    bd.rectangle([cx-148,cy+50,cx+148,cy+82],fill=(60,68,55,200))
    body_mask=Image.new("L",(S,S),0)
    ImageDraw.Draw(body_mask).ellipse([cx-148,cy-148,cx+148,cy+148],fill=255)
    from PIL import ImageChops
    r2,g2,b2,a2=band.split()
    band=Image.merge("RGBA",[r2,g2,b2,ImageChops.multiply(a2,body_mask)])
    img.alpha_composite(band)
    d=ImageDraw.Draw(img)
    d.ellipse([cx-54,cy-188,cx+54,cy-128],fill=(236,136,106,232))
    d.ellipse([cx-32,cy-182,cx-6,cy-158],fill=(255,178,155,140))
    blush(img,cx,cy-30)
    eyes(img,cx,cy-45)
    smile(img,cx,cy-12)
    save(img,"sushi",(242,238,228),(218,212,196))

def cloud():
    img = new(); cx,cy = S//2, S//2+18
    draw_body(img,cx,cy,148,148,(208,226,250))
    blush(img,cx,cy+22,col=(162,196,240,95))
    eyes(img,cx,cy-8)
    smile(img,cx,cy+30)
    d=ImageDraw.Draw(img)
    sx,sy=cx+108,cy-115
    d.ellipse([sx-30,sy-30,sx+30,sy+30],fill=(255,222,78,238))
    for a in range(0,360,38):
        r=math.radians(a)
        d.line([sx+int(34*math.cos(r)),sy+int(34*math.sin(r)),
                sx+int(48*math.cos(r)),sy+int(48*math.sin(r))],
               fill=(255,212,55,215),width=4)
    d.ellipse([sx-14,sy-17,sx+2,sy-5],fill=(255,248,198,185))
    save(img,"cloud",(226,238,255),(198,222,250))

def kinoko():
    img = new(); cx,cy = S//2, S//2+30
    draw_body(img,cx,cy,140,140,(235,222,210))
    blush(img,cx,cy+15)
    eyes(img,cx,cy-15)
    smile(img,cx,cy+22)
    cap=new(); cd=ImageDraw.Draw(cap)
    cd.ellipse([cx-152,cy-205,cx+152,cy-45],fill=(202,52,46,242))
    cd.ellipse([cx-82,cy-195,cx-8,cy-142],fill=(232,92,78,125))
    for bx,by,br in [(cx-58,cy-170,21),(cx+50,cy-158,19),
                      (cx+5,cy-190,15),(cx-18,cy-132,13)]:
        cd.ellipse([bx-br,by-br,bx+br,by+br],fill=(255,255,255,215))
    img.alpha_composite(cap)
    save(img,"kinoko",(252,236,226),(235,212,196))

def shiro():
    img = new(); cx,cy = S//2, S//2+18
    d=ImageDraw.Draw(img)
    for ex,ey in [(cx-108,cy-128),(cx+108,cy-128)]:
        d.ellipse([ex-30,ey-30,ex+30,ey+30],fill=(244,244,248,255))
    draw_body(img,cx,cy,148,148,(246,246,250))
    blush(img,cx,cy+22,col=(212,195,210,105))
    eyes(img,cx,cy-8,col=(36,36,58))
    smile(img,cx,cy+30)
    save(img,"shiro",(246,246,252),(226,226,240))

def neko():
    img = new(); cx,cy = S//2, S//2+25
    d=ImageDraw.Draw(img)
    for side in [-1,1]:
        ex=cx+side*108
        d.polygon([(ex-side*12,cy-105),(ex+side*38,cy-192),(ex+side*55,cy-85)],
                  fill=(232,212,184,255))
        d.polygon([(ex-side*4,cy-110),(ex+side*30,cy-175),(ex+side*44,cy-94)],
                  fill=(255,182,182,185))
    draw_body(img,cx,cy,148,148,(230,210,182))
    blush(img,cx,cy+12,col=(226,156,125,125))
    eyes(img,cx,cy-15,col=(68,110,52))
    d=ImageDraw.Draw(img)
    d.polygon([(cx,cy+28),(cx-11,cy+12),(cx+11,cy+12)],fill=(216,135,145,232))
    for side in [-1,1]:
        for wy in [cy+8,cy+19]:
            d.line([cx+side*18,wy,cx+side*78,wy-side*5],
                   fill=(175,155,128,145),width=2)
    smile(img,cx,cy+35)
    save(img,"neko",(248,238,222),(228,212,190))

def fuusen():
    img = new(); cx,cy = S//2, S//2+8
    draw_body(img,cx,cy,142,158,(192,192,220))
    blush(img,cx,cy+22,col=(172,172,215,95))
    eyes(img,cx,cy-15)
    smile(img,cx,cy+30)
    d=ImageDraw.Draw(img)
    d.ellipse([cx-11,cy+150,cx+11,cy+172],fill=(172,172,208,225))
    pts=[(cx,cy+162)]
    for i in range(18):
        pts.append((cx+int(10*math.sin(i*0.6)), cy+168+i*5))
    d.line(pts,fill=(150,150,192,155),width=2)
    save(img,"fuusen",(228,228,246),(206,206,234))

def yoru():
    img = new(); cx,cy = S//2, S//2+18
    draw_body(img,cx,cy,148,148,(165,145,208))
    blush(img,cx,cy+22,col=(192,162,228,105))
    eyes(img,cx,cy-8,col=(46,30,68))
    smile(img,cx,cy+30)
    d=ImageDraw.Draw(img)
    for bx,by,br in [(cx-92,cy-130,13),(cx+90,cy-120,11),
                      (cx+18,cy-162,9),(cx-28,cy-108,8)]:
        for a in range(0,360,72):
            r=math.radians(a)
            d.line([bx+int(br*0.4*math.cos(r)),by+int(br*0.4*math.sin(r)),
                    bx+int(br*math.cos(r)),by+int(br*math.sin(r))],
                   fill=(255,245,148,225),width=2)
        d.ellipse([bx-4,by-4,bx+4,by+4],fill=(255,252,195,255))
    save(img,"yoru",(232,222,252),(205,188,240))


if __name__=="__main__":
    print("Generating v3 mochi characters…")
    vanilla(); sakura(); matcha(); sushi(); cloud()
    kinoko(); shiro(); neko(); fuusen(); yoru()
    print("✅  Done!")
