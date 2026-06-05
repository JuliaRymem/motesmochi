#!/usr/bin/env python3
"""Generate high-quality 3D-style mochi character icons."""

import os
import math
from PIL import Image, ImageDraw, ImageFilter

S = 400
ICONS = os.path.join(os.path.dirname(__file__), "icons")
PREVIEW = os.path.join(os.path.dirname(__file__), "preview")
os.makedirs(ICONS, exist_ok=True)
os.makedirs(PREVIEW, exist_ok=True)


def new_canvas():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def paste(base, layer):
    base.alpha_composite(layer)


# ── Core drawing helpers ────────────────────────────────────────────────────

def draw_body(img, cx, cy, rx, ry, base_color, squash=1.0):
    """Draw a round 3D mochi body with shading and highlight."""
    # shadow
    shadow = new_canvas()
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([cx - rx * 0.85, cy + ry * 0.6, cx + rx * 0.85, cy + ry * 1.0],
               fill=(0, 0, 0, 40))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    paste(img, shadow)

    # body layers — dark edge → base → highlight
    for i, (dr, alpha) in enumerate([
        (0,    255),   # base
        (-8,   180),   # slightly lighter inner
        (-22,  120),   # mid highlight
    ]):
        layer = new_canvas()
        ld = ImageDraw.Draw(layer)
        r = base_color
        lighten = i * 18
        c = tuple(min(255, r[j] + lighten) for j in range(3)) + (alpha,)
        ld.ellipse([cx - rx + dr // 2, cy - ry * squash + dr // 2,
                    cx + rx - dr // 2, cy + ry * squash - dr // 2],
                   fill=c)
        if i > 0:
            layer = layer.filter(ImageFilter.GaussianBlur(i * 6))
        paste(img, layer)

    # specular highlight (top-left)
    hl = new_canvas()
    hd = ImageDraw.Draw(hl)
    hx = cx - rx * 0.3
    hy = cy - ry * squash * 0.45
    hd.ellipse([hx - rx * 0.22, hy - ry * 0.18,
                hx + rx * 0.22, hy + ry * 0.18],
               fill=(255, 255, 255, 160))
    hl = hl.filter(ImageFilter.GaussianBlur(10))
    paste(img, hl)

    # secondary soft highlight
    hl2 = new_canvas()
    h2d = ImageDraw.Draw(hl2)
    h2d.ellipse([cx - rx * 0.6, cy - ry * squash * 0.7,
                 cx + rx * 0.0, cy - ry * squash * 0.2],
                fill=(255, 255, 255, 50))
    hl2 = hl2.filter(ImageFilter.GaussianBlur(20))
    paste(img, hl2)


def draw_eyes(img, cx, cy, spread=38, size=18, color=(50, 35, 40)):
    d = ImageDraw.Draw(img)
    for dx in (-spread // 2, spread // 2):
        x = cx + dx
        # eye white glow
        glow = new_canvas()
        gd = ImageDraw.Draw(glow)
        gd.ellipse([x - size, cy - size, x + size, cy + size],
                   fill=(255, 255, 255, 80))
        glow = glow.filter(ImageFilter.GaussianBlur(6))
        paste(img, glow)
        # pupil
        d.ellipse([x - size // 2, cy - size // 2,
                   x + size // 2, cy + size // 2], fill=color + (255,))
        # shine
        d.ellipse([x - size // 2 + 3, cy - size // 2 + 2,
                   x - size // 2 + 8, cy - size // 2 + 7],
                  fill=(255, 255, 255, 240))


def draw_smile(img, cx, cy, w=28, color=(70, 45, 50)):
    d = ImageDraw.Draw(img)
    d.arc([cx - w, cy - 10, cx + w, cy + 10],
          start=15, end=165, fill=color + (220,), width=4)


def draw_blush(img, cx, cy, spread=52, color=(255, 160, 155, 90)):
    b = new_canvas()
    bd = ImageDraw.Draw(b)
    for dx in (-spread, spread):
        bd.ellipse([cx + dx - 22, cy - 10, cx + dx + 22, cy + 20], fill=color)
    b = b.filter(ImageFilter.GaussianBlur(12))
    paste(img, b)


def gradient_bg(color1, color2):
    bg = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(bg)
    for y in range(S):
        t = y / S
        r = tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))
        d.line([(0, y), (S, y)], fill=r)
    return bg


def save(img, key, bg1, bg2):
    bg = gradient_bg(bg1, bg2).convert("RGBA")
    bg.alpha_composite(img)
    # save small icon (64px)
    small = bg.resize((64, 64), Image.LANCZOS).convert("RGBA")
    small.save(os.path.join(ICONS, f"{key}.png"))
    # save preview (400px)
    bg.convert("RGB").save(os.path.join(PREVIEW, f"{key}.png"))
    print(f"  {key}")


# ── Characters ───────────────────────────────────────────────────────────────

def make_vanilla():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 20
    draw_body(img, cx, cy, 148, 148, (238, 228, 212))
    draw_blush(img, cx, cy + 20)
    draw_eyes(img, cx, cy - 10)
    draw_smile(img, cx, cy + 28)
    d = ImageDraw.Draw(img)
    # flag pole
    px, py = cx + 80, cy - 148
    d.line([px, py + 10, px, py + 70], fill=(180, 140, 95, 230), width=5)
    # flag
    pts = [(px + 2, py + 10), (px + 52, py + 28), (px + 2, py + 46)]
    d.polygon(pts, fill=(220, 85, 75, 230))
    save(img, "vanilla", (252, 243, 230), (235, 220, 200))


def make_sakura():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 20
    draw_body(img, cx, cy, 148, 148, (245, 185, 200))
    draw_blush(img, cx, cy + 20, color=(255, 120, 145, 110))
    draw_eyes(img, cx, cy - 10)
    draw_smile(img, cx, cy + 28)
    d = ImageDraw.Draw(img)
    # flower petals on top
    for angle in range(0, 360, 72):
        a = math.radians(angle)
        px = cx + int(52 * math.cos(a))
        py = (cy - 148) + int(22 * math.sin(a))
        d.ellipse([px - 14, py - 10, px + 14, py + 10], fill=(255, 215, 225, 200))
    d.ellipse([cx - 14, cy - 158, cx + 14, cy - 130], fill=(255, 190, 205, 230))
    save(img, "sakura", (255, 235, 242), (250, 210, 228))


def make_matcha():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 20
    draw_body(img, cx, cy, 148, 148, (155, 200, 148))
    draw_blush(img, cx, cy + 20, color=(130, 190, 125, 100))
    draw_eyes(img, cx, cy - 10)
    draw_smile(img, cx, cy + 28)
    # steam
    d = ImageDraw.Draw(img)
    for ox, phase in [(-30, 0), (0, 8), (30, 4)]:
        for i in range(3):
            sy = cy - 148 - 20 - i * 22
            sx = cx + ox + int(8 * math.sin(i + phase))
            d.ellipse([sx - 6, sy - 8, sx + 6, sy + 8],
                      fill=(200, 230, 195, max(0, 160 - i * 50)))
    save(img, "matcha", (225, 242, 218), (195, 225, 185))


def make_sushi():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 20
    draw_body(img, cx, cy, 148, 148, (240, 235, 222))
    # nori band — drawn over body
    band = new_canvas()
    bd = ImageDraw.Draw(band)
    bd.rectangle([cx - 148, cy + 20, cx + 148, cy + 68], fill=(52, 58, 48, 215))
    # clip to circle
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([cx - 148, cy - 148, cx + 148, cy + 148], fill=255)
    band.putalpha(mask)
    paste(img, band)
    # salmon
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 52, cy - 185, cx + 52, cy - 128], fill=(238, 138, 108, 230))
    # highlight on salmon
    d.ellipse([cx - 30, cy - 180, cx - 5, cy - 158], fill=(255, 180, 158, 140))
    draw_blush(img, cx, cy - 10)
    draw_eyes(img, cx, cy - 20)
    draw_smile(img, cx, cy + 12)
    save(img, "sushi", (242, 238, 228), (218, 212, 195))


def make_cloud():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 20
    draw_body(img, cx, cy, 148, 148, (210, 228, 250))
    draw_blush(img, cx, cy + 20, color=(165, 198, 240, 100))
    draw_eyes(img, cx, cy - 10)
    draw_smile(img, cx, cy + 28)
    d = ImageDraw.Draw(img)
    # sun
    sx, sy = cx + 105, cy - 120
    d.ellipse([sx - 28, sy - 28, sx + 28, sy + 28], fill=(255, 222, 80, 235))
    for angle in range(0, 360, 40):
        a = math.radians(angle)
        d.line([sx + int(32 * math.cos(a)), sy + int(32 * math.sin(a)),
                sx + int(46 * math.cos(a)), sy + int(46 * math.sin(a))],
               fill=(255, 215, 60, 210), width=4)
    # sun highlight
    d.ellipse([sx - 12, sy - 16, sx + 4, sy - 4], fill=(255, 248, 200, 180))
    save(img, "cloud", (225, 238, 255), (198, 220, 248))


def make_kinoko():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 30
    draw_body(img, cx, cy, 140, 140, (235, 222, 212))
    draw_blush(img, cx, cy + 15)
    draw_eyes(img, cx, cy - 15)
    draw_smile(img, cx, cy + 22)
    d = ImageDraw.Draw(img)
    # mushroom cap
    cap = new_canvas()
    cd = ImageDraw.Draw(cap)
    cd.ellipse([cx - 148, cy - 200, cx + 148, cy - 48], fill=(205, 55, 48, 240))
    # cap highlight
    cd.ellipse([cx - 80, cy - 190, cx - 10, cy - 140], fill=(235, 95, 80, 120))
    # spots
    for sx2, sy2, sr in [(cx - 55, cy - 168, 20), (cx + 48, cy - 155, 18),
                          (cx + 5, cy - 185, 14), (cx - 20, cy - 128, 12)]:
        cd.ellipse([sx2 - sr, sy2 - sr, sx2 + sr, sy2 + sr],
                   fill=(255, 255, 255, 210))
    paste(img, cap)
    save(img, "kinoko", (252, 235, 225), (235, 210, 195))


def make_shiro():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 20
    draw_body(img, cx, cy, 148, 148, (245, 245, 248))
    # ear nubs
    d = ImageDraw.Draw(img)
    for ex, ey in [(cx - 105, cy - 130), (cx + 105, cy - 130)]:
        d.ellipse([ex - 28, ey - 28, ex + 28, ey + 28], fill=(242, 242, 246, 255))
    draw_blush(img, cx, cy + 20, color=(215, 198, 210, 110))
    draw_eyes(img, cx, cy - 10, color=(38, 38, 58))
    draw_smile(img, cx, cy + 28)
    save(img, "shiro", (245, 245, 250), (225, 225, 238))


def make_neko():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 25
    draw_body(img, cx, cy, 148, 148, (232, 212, 185))
    d = ImageDraw.Draw(img)
    # cat ears
    for side in [-1, 1]:
        ex = cx + side * 108
        pts_outer = [(ex - side * 10, cy - 108),
                     (ex + side * 35, cy - 188),
                     (ex + side * 52, cy - 88)]
        pts_inner = [(ex - side * 2, cy - 112),
                     (ex + side * 28, cy - 172),
                     (ex + side * 42, cy - 96)]
        d.polygon(pts_outer, fill=(232, 212, 185, 255))
        d.polygon(pts_inner, fill=(255, 185, 185, 180))
    draw_blush(img, cx, cy + 10, color=(228, 158, 128, 130))
    draw_eyes(img, cx, cy - 15, color=(70, 112, 55))
    # nose
    d.polygon([(cx, cy + 25), (cx - 10, cy + 10), (cx + 10, cy + 10)],
              fill=(218, 138, 148, 230))
    # whiskers
    for side in [-1, 1]:
        for wy in [cy + 8, cy + 18]:
            d.line([cx + side * 20, wy, cx + side * 75, wy - side * 4],
                   fill=(180, 158, 132, 150), width=2)
    draw_smile(img, cx, cy + 32)
    save(img, "neko", (248, 238, 222), (228, 212, 190))


def make_fuusen():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 10
    draw_body(img, cx, cy, 142, 155, (195, 195, 220), squash=1.05)
    draw_blush(img, cx, cy + 20, color=(175, 175, 215, 100))
    draw_eyes(img, cx, cy - 15)
    draw_smile(img, cx, cy + 28)
    d = ImageDraw.Draw(img)
    # balloon knot at bottom
    d.ellipse([cx - 10, cy + 148, cx + 10, cy + 170], fill=(175, 175, 205, 220))
    # string
    for i in range(20):
        sx = cx + int(8 * math.sin(i * 0.5))
        d.line([sx, cy + 165 + i * 5, sx + int(8 * math.sin((i + 1) * 0.5)),
                cy + 165 + (i + 1) * 5], fill=(155, 155, 190, 160), width=2)
    save(img, "fuusen", (228, 228, 245), (205, 205, 232))


def make_yoru():
    img = new_canvas()
    cx, cy = S // 2, S // 2 + 20
    draw_body(img, cx, cy, 148, 148, (168, 148, 208))
    draw_blush(img, cx, cy + 20, color=(195, 165, 228, 110))
    draw_eyes(img, cx, cy - 10, color=(48, 32, 68))
    draw_smile(img, cx, cy + 28)
    d = ImageDraw.Draw(img)
    # stars
    for sx2, sy2, sr in [(cx - 90, cy - 128, 12), (cx + 88, cy - 118, 10),
                          (cx + 20, cy - 158, 8), (cx - 30, cy - 105, 7)]:
        for a in range(0, 360, 72):
            ra = math.radians(a)
            d.line([sx2 + int(sr * 0.4 * math.cos(ra)),
                    sy2 + int(sr * 0.4 * math.sin(ra)),
                    sx2 + int(sr * math.cos(ra)),
                    sy2 + int(sr * math.sin(ra))],
                   fill=(255, 245, 155, 220), width=2)
        d.ellipse([sx2 - 3, sy2 - 3, sx2 + 3, sy2 + 3],
                  fill=(255, 252, 200, 255))
    save(img, "yoru", (232, 222, 250), (205, 188, 238))


if __name__ == "__main__":
    print("Generating mochi characters…")
    make_vanilla()
    make_sakura()
    make_matcha()
    make_sushi()
    make_cloud()
    make_kinoko()
    make_shiro()
    make_neko()
    make_fuusen()
    make_yoru()
    print("✅  Done! Icons → icons/   Previews → preview/")
