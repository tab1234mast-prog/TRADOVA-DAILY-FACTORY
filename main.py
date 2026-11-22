

import os
import math
import glob
import numpy as np
import imageio.v2 as imageio

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

# ==============================
# TRADOVA VIDEO ENGINE
# ==============================

W, H = 720, 1280
FPS = 24
DURATION = 12
TOTAL_FRAMES = FPS * DURATION

GOLD = (225, 177, 75)
LIGHT_GOLD = (255, 220, 145)
WHITE = (245, 242, 235)
MUTED = (155, 151, 145)
BLACK = (5, 5, 7)
GREEN = (65, 190, 135)
RED = (210, 80, 80)

OUTPUT = "tradova_daily.mp4"

# Find Arabic font
font_paths = [
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]

font_path = next((p for p in font_paths if os.path.exists(p)), None)

if not font_path:
    matches = glob.glob("/usr/share/fonts/**/*Arabic*.ttf", recursive=True)
    if matches:
        font_path = matches[0]

if not font_path:
    raise RuntimeError("Arabic font not found")

def font(size):
    return ImageFont.truetype(font_path, size)

def arabic(text):
    return get_display(arabic_reshaper.reshape(text))

def draw_center(draw, text, y, size, fill=WHITE):
    draw.text(
        (W // 2, y),
        arabic(text),
        font=font(size),
        fill=fill,
        anchor="mm",
        stroke_width=0
    )

def make_background():
    arr = np.zeros((H, W, 3), dtype=np.uint8)

    for y in range(H):
        ratio = y / H
        shade = int(5 + 8 * ratio)
        arr[y, :, :] = (shade, shade, shade + 2)

    return Image.fromarray(arr)

# Fixed candle data: realistic chart movement
candles = [
    (45, 58), (58, 52), (52, 65), (65, 60),
    (60, 72), (72, 68), (68, 80), (80, 75),
    (75, 86), (86, 79), (79, 91), (91, 84),
    (84, 96), (96, 89), (89, 101), (101, 95),
    (95, 108), (108, 102), (102, 115), (115, 109),
    (109, 120), (120, 113), (113, 126), (126, 119),
    (119, 132), (132, 124), (124, 137), (137, 130)
]

def draw_candles(image, progress):
    draw = ImageDraw.Draw(image, "RGBA")

    chart_x = 65
    chart_y = 470
    chart_w = 590
    chart_h = 370

    # Chart grid
    for i in range(5):
        y = chart_y + i * chart_h // 4
        draw.line(
            (chart_x, y, chart_x + chart_w, y),
            fill=(190, 160, 90, 28),
            width=1
        )

    visible = max(1, int(len(candles) * progress))
    candle_width = 11
    spacing = 20

    for i in range(visible):
        open_price, close_price = candles[i]

        x = chart_x + 12 + i * spacing
        center = chart_y + chart_h - (close_price - 40) * 5.4
        open_y = chart_y + chart_h - (open_price - 40) * 5.4

        high_y = min(center, open_y) - 24
        low_y = max(center, open_y) + 24

        rising = close_price >= open_price
        color = GREEN if rising else RED

        draw.line(
            (x + candle_width // 2, high_y,
             x + candle_width // 2, low_y),
            fill=(*color, 220),
            width=2
        )

        top = min(center, open_y)
        bottom = max(center, open_y)

        if bottom - top < 5:
            bottom = top + 5

        draw.rounded_rectangle(
            (x, top, x + candle_width, bottom),
            radius=2,
            fill=(*color, 230)
        )

    # Gold chart border
    draw.line(
        (chart_x, chart_y + chart_h + 25,
         chart_x + chart_w, chart_y + chart_h + 25),
        fill=(GOLD[0], GOLD[1], GOLD[2], 90),
        width=2
    )

def render_frame(frame_number):
    progress = frame_number / TOTAL_FRAMES

    image = make_background()

    # Soft gold lighting
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((170, 250, 550, 630), fill=(190, 130, 35, 28))
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    image = Image.alpha_composite(image.convert("RGBA"), glow)

    draw = ImageDraw.Draw(image)

    # Brand
    draw_center(draw, "TRADOVA", 105, 52, LIGHT_GOLD)

    draw.line(
        (190, 155, 530, 155),
        fill=(*GOLD, 150),
        width=2
    )

    # Main Arabic title
    draw_center(draw, "ليش السعر يضرب القمة ويرجع؟",
                255, 35, WHITE)

    draw_center(draw, "الجواب هو السيولة",
                325, 42, LIGHT_GOLD)

    # Chart
    draw_candles(image, progress)

    # Explanation
    draw = ImageDraw.Draw(image)

    draw_center(draw, "السوق يبحث عن أوامر المتداولين",
                940, 29, WHITE)

    draw_center(draw, "قبل أن يحدد اتجاهه",
                990, 31, LIGHT_GOLD)

    # Footer
    draw.line(
        (150, 1090, 570, 1090),
        fill=(*GOLD, 100),
        width=1
    )

    draw_center(draw, "تعلم التداول بفهم حركة السعر",
                1140, 23, MUTED)

    draw_center(draw, "TRADOVA",
                1200, 25, LIGHT_GOLD)

    return image.convert("RGB")

# ==============================
# VIDEO RENDER
# ==============================

with imageio.get_writer(
    OUTPUT,
    fps=FPS,
    codec="libx264",
    quality=8,
    macro_block_size=16
) as writer:

    for frame in range(TOTAL_FRAMES):
        img = render_frame(frame)
        writer.append_data(np.asarray(img))

print("TRADOVA video created successfully:", OUTPUT)
