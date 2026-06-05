#!/usr/bin/env python3
"""Generate large preview images of all mochi characters with backgrounds."""

import os
from PIL import Image, ImageDraw, ImageFilter

SIZE = 400
OUT = os.path.join(os.path.dirname(__file__), "preview")
ICONS = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT, exist_ok=True)

CHARACTERS = [
    ("vanilla",  "Vanilla",  (252, 243, 230), (238, 224, 204)),
    ("sakura",   "Sakura",   (255, 235, 240), (255, 210, 225)),
    ("matcha",   "Matcha",   (225, 242, 218), (198, 228, 188)),
    ("sushi",    "Sushi",    (240, 238, 230), (215, 210, 195)),
    ("cloud",    "Cloud",    (225, 238, 255), (198, 220, 248)),
    ("kinoko",   "Kinoko",   (252, 235, 225), (238, 210, 195)),
    ("shiro",    "Shiro",    (245, 245, 250), (225, 225, 235)),
    ("neko",     "Neko",     (248, 238, 220), (230, 215, 192)),
    ("fuusen",   "Fuusen",   (228, 228, 245), (205, 205, 230)),
    ("yoru",     "Yoru",     (230, 220, 248), (205, 190, 235)),
]


def draw_gradient_bg(img, color1, color2):
    draw = ImageDraw.Draw(img)
    for y in range(SIZE):
        t = y / SIZE
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))


def make_preview(key, name, bg1, bg2):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw_gradient_bg(img, bg1, bg2)

    # soft vignette circle in center
    vignette = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    pad = 40
    vd.ellipse([pad, pad, SIZE - pad, SIZE - pad], fill=(*bg1, 60))
    vignette = vignette.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, vignette)

    # load and scale icon
    icon = Image.open(os.path.join(ICONS, f"{key}.png")).convert("RGBA")
    icon_size = 260
    icon = icon.resize((icon_size, icon_size), Image.LANCZOS)

    # soft drop shadow
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    shadow_icon = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_icon)
    sd.ellipse([20, icon_size - 50, icon_size - 20, icon_size - 10],
               fill=(0, 0, 0, 50))
    shadow_icon = shadow_icon.filter(ImageFilter.GaussianBlur(12))
    ox = (SIZE - icon_size) // 2
    oy = (SIZE - icon_size) // 2 + 8
    shadow.paste(shadow_icon, (ox, oy), shadow_icon)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, shadow)

    # paste icon centered
    x = (SIZE - icon_size) // 2
    y = (SIZE - icon_size) // 2 - 10
    img.paste(icon, (x, y), icon)

    # convert to RGB for saving as PNG with white bg
    final = Image.new("RGB", (SIZE, SIZE), bg1)
    final.paste(img, mask=img.split()[3])
    final.save(os.path.join(OUT, f"{key}.png"))
    print(f"  {key}.png")


if __name__ == "__main__":
    print(f"Generating previews → {OUT}/")
    for args in CHARACTERS:
        make_preview(*args)
    print("✅  Done!")
