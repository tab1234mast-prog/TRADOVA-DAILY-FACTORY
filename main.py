
import os
import math
import glob
import numpy as np
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

W, H = 720, 1280
FPS = 24
DURATION = 10
OUTPUT = "tradova_daily.mp4"

def arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def get_font(size):
    paths = glob.glob("/usr/share/fonts/**/*NotoSansArabic*Regular.ttf",
                      recursive=True)
    paths += glob.glob("/usr/share/fonts/**/*NotoNaskhArabic*Regular.ttf",
                       recursive=True)
    if paths:
        return ImageFont.truetype(paths[0], size)
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
    )

def render_frame(t):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Gold-to-black background
    for y in range(H):
        ratio = y / H
        glow = max(0, 1 - ratio * 2)
        color = (
            int(12 + 22 * glow),
            int(10 + 15 * glow),
            int(8 + 2 * glow)
        )
        draw.line((0, y, W, y), fill=color)

    # Animated gold light
    glow_x = int(W / 2 + math.sin(t * 1.5) * 100)
    draw.ellipse(
        (glow_x-180, 180, glow_x+180, 540),
        fill=(35, 25, 8)
    )

    # Decorative frame
    draw.rounded_rectangle(
        (35, 35, W-35, H-35),
        radius=24, outline=(190, 145, 55), width=2
    )

    # Animated candlesticks
    for i in range(9):
        x = 100 + i * 65
        height = 100 + int(55 * math.sin(t * 2 + i))
        top = 650 - height
        draw.line((x+12, top-35, x+12, 700), fill=(218, 173, 75), width=3)
        draw.rectangle(
            (x, top, x+24, top+height//2),
            fill=(218, 173, 75)
        )

    # Main title
    title = arabic("تعلم التداول باحتراف")
    font = get_font(48)
    box = draw.textbbox((0, 0), title, font=font)
    draw.text(
        ((W-(box[2]-box[0]))//2, 300),
        title, font=font, fill=(245, 205, 115)
    )

    # Subtitle
    subtitle = arabic("السيولة هي مفتاح حركة السعر")
    font2 = get_font(30)
    box = draw.textbbox((0, 0), subtitle, font=font2)
    draw.text(
        ((W-(box[2]-box[0]))//2, 410),
        subtitle, font=font2, fill=(235, 235, 235)
    )

    # Brand
    brand_font = get_font(65)
    draw.text((W//2, 920), "TRADOVA",
              font=brand_font, fill=(218, 173, 75),
              anchor="mm")

    footer = arabic("معرفة اليوم، احتراف الغد")
    draw.text((W//2, 1000), footer,
              font=get_font(25), fill=(190, 190, 190),
              anchor="mm")

    return np.array(img)

def main():
    print("Starting TRADOVA video production...")
    writer = imageio.get_writer(
        OUTPUT, fps=FPS, codec="libx264",
        quality=8, macro_block_size=1
    )

    try:
        for frame in range(FPS * DURATION):
            t = frame / FPS
            writer.append_data(render_frame(t))
    finally:
        writer.close()

    print(f"Video ready: {OUTPUT}")

if __name__ == "__main__":
    main()
