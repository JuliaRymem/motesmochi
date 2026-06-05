#!/usr/bin/env python3
"""Generate mochi character icons for MötesMochi."""

import os
import math
from PIL import Image, ImageDraw

SIZE = 64
OUT = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT, exist_ok=True)


def new_img():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def draw_mochi_body(draw, color, shadow_color=None):
    """Draw the round mochi body with a soft shadow."""
    if shadow_color:
        draw.ellipse([6, 10, SIZE - 4, SIZE - 2], fill=shadow_color)
    draw.ellipse([4, 4, SIZE - 4, SIZE - 8], fill=color)


def draw_eyes(draw, y=28, spread=10, color=(60, 40, 40, 255)):
    cx = SIZE // 2
    for dx in (-spread // 2, spread // 2):
        x = cx + dx
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=color)
        draw.ellipse([x - 1, y - 4, x + 1, y - 2], fill=(255, 255, 255, 180))


def draw_smile(draw, y=36, width=10, color=(60, 40, 40, 255)):
    cx = SIZE // 2
    draw.arc([cx - width, y - 4, cx + width, y + 4], start=10, end=170, fill=color, width=2)


def draw_blush(draw, y=34, spread=14, color=(255, 160, 160, 120)):
    cx = SIZE // 2
    for dx in (-spread, spread):
        x = cx + dx
        draw.ellipse([x - 5, y - 3, x + 5, y + 3], fill=color)


# ── 1. Vanilla — plain warm white with a tiny flag ──────────────────────────
def make_vanilla():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (240, 228, 210, 255), (200, 185, 165, 80))
    draw_blush(d)
    draw_eyes(d)
    draw_smile(d)
    # flag pole
    d.line([SIZE // 2 + 8, 8, SIZE // 2 + 8, 22], fill=(160, 120, 80, 220), width=2)
    d.polygon([(SIZE // 2 + 9, 8), (SIZE // 2 + 18, 12), (SIZE // 2 + 9, 16)], fill=(230, 80, 80, 220))
    img.save(os.path.join(OUT, "vanilla.png"))


# ── 2. Sakura — soft pink ────────────────────────────────────────────────────
def make_sakura():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (250, 190, 200, 255), (210, 150, 165, 80))
    draw_blush(d, color=(255, 120, 140, 140))
    draw_eyes(d)
    draw_smile(d)
    # tiny petal on top
    for angle, r in [(0, 7), (72, 7), (144, 7), (216, 7), (288, 7)]:
        a = math.radians(angle)
        px = SIZE // 2 + int(r * math.cos(a))
        py = 7 + int(r * math.sin(a))
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 210, 220, 200))
    d.ellipse([SIZE // 2 - 3, 4, SIZE // 2 + 3, 10], fill=(255, 180, 195, 255))
    img.save(os.path.join(OUT, "sakura.png"))


# ── 3. Matcha — green tea ────────────────────────────────────────────────────
def make_matcha():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (170, 210, 160, 255), (130, 170, 120, 80))
    draw_blush(d, color=(140, 200, 130, 120))
    draw_eyes(d)
    draw_smile(d)
    # steam wisps
    for ox in (-6, 0, 6):
        x = SIZE // 2 + ox
        d.arc([x - 3, 1, x + 3, 9], start=200, end=340, fill=(200, 230, 195, 180), width=2)
    img.save(os.path.join(OUT, "matcha.png"))


# ── 4. Sushi — white with nori band ─────────────────────────────────────────
def make_sushi():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (240, 235, 225, 255), (200, 195, 180, 80))
    # nori band
    d.rectangle([4, 34, SIZE - 4, 44], fill=(50, 55, 45, 210))
    draw_blush(d)
    draw_eyes(d, y=26)
    draw_smile(d, y=32)
    # salmon on top
    d.ellipse([SIZE // 2 - 10, 3, SIZE // 2 + 10, 14], fill=(240, 140, 110, 230))
    img.save(os.path.join(OUT, "sushi.png"))


# ── 5. Cloud — light blue with tiny sun ─────────────────────────────────────
def make_cloud():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (220, 235, 250, 255), (180, 200, 225, 80))
    draw_blush(d, color=(170, 200, 240, 120))
    draw_eyes(d)
    draw_smile(d)
    # sun
    sx, sy = SIZE - 14, 8
    d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=(255, 220, 80, 230))
    for angle in range(0, 360, 45):
        a = math.radians(angle)
        d.line([sx + int(6 * math.cos(a)), sy + int(6 * math.sin(a)),
                sx + int(10 * math.cos(a)), sy + int(10 * math.sin(a))],
               fill=(255, 220, 80, 200), width=1)
    img.save(os.path.join(OUT, "cloud.png"))


# ── 6. Kinoko — mushroom, red cap ────────────────────────────────────────────
def make_kinoko():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (235, 225, 215, 255), (195, 180, 165, 80))
    draw_blush(d)
    draw_eyes(d)
    draw_smile(d)
    # mushroom cap
    d.ellipse([8, 2, SIZE - 8, 24], fill=(210, 60, 50, 230))
    for cx2, cy2, r in [(20, 10, 4), (32, 6, 3), (43, 11, 4)]:
        d.ellipse([cx2 - r, cy2 - r, cx2 + r, cy2 + r], fill=(255, 255, 255, 200))
    img.save(os.path.join(OUT, "kinoko.png"))


# ── 7. Shiro — pure white seal-like ─────────────────────────────────────────
def make_shiro():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (248, 248, 248, 255), (210, 210, 215, 80))
    draw_blush(d, color=(220, 200, 210, 130))
    draw_eyes(d, color=(40, 40, 60, 255))
    draw_smile(d)
    # tiny ear nubs
    d.ellipse([10, 3, 18, 11], fill=(245, 245, 248, 255))
    d.ellipse([SIZE - 18, 3, SIZE - 10, 11], fill=(245, 245, 248, 255))
    img.save(os.path.join(OUT, "shiro.png"))


# ── 8. Neko — cat with pointy ears ──────────────────────────────────────────
def make_neko():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (235, 215, 185, 255), (195, 172, 145, 80))
    draw_blush(d, color=(230, 160, 130, 140))
    # cat ears
    d.polygon([(10, 14), (6, 2), (18, 10)], fill=(235, 215, 185, 255))
    d.polygon([(SIZE - 10, 14), (SIZE - 6, 2), (SIZE - 18, 10)], fill=(235, 215, 185, 255))
    d.polygon([(12, 13), (9, 5), (17, 10)], fill=(255, 180, 180, 180))
    d.polygon([(SIZE - 12, 13), (SIZE - 9, 5), (SIZE - 17, 10)], fill=(255, 180, 180, 180))
    draw_eyes(d, color=(80, 120, 60, 255))
    # cat nose + whiskers
    cx = SIZE // 2
    d.ellipse([cx - 2, 33, cx + 2, 37], fill=(220, 140, 150, 255))
    for wx in [(-14, -8), (-14, -6), (8, -8), (8, -6)]:
        d.line([cx + wx[0], 34 + wx[1] // 2, cx + wx[0] + 6, 34], fill=(160, 140, 120, 160), width=1)
    img.save(os.path.join(OUT, "neko.png"))


# ── 9. Fuusen — balloon, silver/lilac ───────────────────────────────────────
def make_fuusen():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (200, 200, 220, 255), (160, 160, 185, 80))
    draw_blush(d, color=(180, 180, 210, 130))
    draw_eyes(d)
    draw_smile(d)
    # highlight
    d.ellipse([14, 8, 26, 18], fill=(230, 230, 245, 160))
    # string
    d.line([SIZE // 2, SIZE - 8, SIZE // 2 + 4, SIZE - 2], fill=(160, 160, 180, 180), width=1)
    img.save(os.path.join(OUT, "fuusen.png"))


# ── 10. Yoru — night/lavender with stars ────────────────────────────────────
def make_yoru():
    img = new_img(); d = ImageDraw.Draw(img)
    draw_mochi_body(d, (175, 155, 210, 255), (135, 115, 175, 80))
    draw_blush(d, color=(200, 170, 230, 130))
    draw_eyes(d, color=(50, 35, 70, 255))
    draw_smile(d)
    # small stars
    for sx2, sy2 in [(12, 8), (SIZE - 13, 10), (SIZE // 2 + 12, 5)]:
        for a in range(0, 360, 72):
            ra = math.radians(a)
            d.line([sx2 + int(2 * math.cos(ra)), sy2 + int(2 * math.sin(ra)),
                    sx2 + int(5 * math.cos(ra)), sy2 + int(5 * math.sin(ra))],
                   fill=(255, 240, 150, 200), width=1)
    img.save(os.path.join(OUT, "yoru.png"))


if __name__ == "__main__":
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
    print(f"✅  10 mochi icons saved to {OUT}/")
