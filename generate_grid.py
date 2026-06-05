#!/usr/bin/env python3
"""Generate a 5x2 grid of all mochi characters."""

import os
from PIL import Image, ImageDraw, ImageFont

PREVIEW = os.path.join(os.path.dirname(__file__), "preview")
OUT = os.path.join(os.path.dirname(__file__), "preview", "grid.png")

CHARACTERS = [
    ("vanilla", "Vanilla"),
    ("sakura",  "Sakura"),
    ("matcha",  "Matcha"),
    ("sushi",   "Sushi"),
    ("cloud",   "Cloud"),
    ("kinoko",  "Kinoko"),
    ("shiro",   "Shiro"),
    ("neko",    "Neko"),
    ("fuusen",  "Fuusen"),
    ("yoru",    "Yoru"),
]

COLS = 5
ROWS = 2
CELL = 300
PADDING = 24
LABEL_H = 44
BG = (252, 248, 244)

W = COLS * CELL + (COLS + 1) * PADDING
H = ROWS * (CELL + LABEL_H) + (ROWS + 1) * PADDING + 80  # 80 for top title

grid = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(grid)

# title
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Futura.ttc", 42)
    font_label = ImageFont.truetype("/System/Library/Fonts/Supplemental/Futura.ttc", 22)
except Exception:
    font_title = ImageFont.load_default()
    font_label = font_title

title = "MötesMochi 🍡"
bbox = draw.textbbox((0, 0), title, font=font_title)
tx = (W - (bbox[2] - bbox[0])) // 2
draw.text((tx, 18), title, fill=(80, 60, 50), font=font_title)

for i, (key, name) in enumerate(CHARACTERS):
    col = i % COLS
    row = i // COLS

    x = PADDING + col * (CELL + PADDING)
    y = 80 + PADDING + row * (CELL + LABEL_H + PADDING)

    # load and resize preview
    img = Image.open(os.path.join(PREVIEW, f"{key}.png")).convert("RGB")
    img = img.resize((CELL, CELL), Image.LANCZOS)

    # rounded corners mask
    mask = Image.new("L", (CELL, CELL), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, CELL, CELL], radius=32, fill=255)
    img_rgba = img.convert("RGBA")
    img_rgba.putalpha(mask)
    grid.paste(img, (x, y), mask)

    # label
    bbox = draw.textbbox((0, 0), name, font=font_label)
    lw = bbox[2] - bbox[0]
    lx = x + (CELL - lw) // 2
    ly = y + CELL + 8
    draw.text((lx, ly), name, fill=(100, 80, 70), font=font_label)

grid.save(OUT)
print(f"✅  Grid saved to {OUT}")
