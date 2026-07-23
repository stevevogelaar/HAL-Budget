import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT_DIR = Path(r"C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget\video\subtitles")
OUT_DIR.mkdir(exist_ok=True)

W, H = 1920, 1080
FONT_PATH = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SIZE = 64
MARGIN_X = 100
MARGIN_Y = 60
PADDING = 35
LINE_SPACING = 18

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

subtitles = [
    ("subtitle_amazon.png", "Asking about Amazon spending"),
    ("subtitle_coffee.png", "Asking about coffee spending"),
    ("subtitle_guardrail.png", "Testing the guardrail"),
    ("subtitle_scan.png", "Scanning a Walmart receipt"),
    ("subtitle_transactions.png", "Searching all transactions"),
    ("subtitle_settings.png", "Model dropdown and demo reset"),
]


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for word in text.split(" "):
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


for filename, text in subtitles:
    # transparent background
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    max_text_w = W - 2 * MARGIN_X
    lines = wrap_text(draw, text, font, max_text_w)

    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    total_h = sum(line_heights) + LINE_SPACING * (len(lines) - 1)

    box_w = W - 2 * MARGIN_X + 2 * PADDING
    box_h = total_h + 2 * PADDING
    box_x = MARGIN_X - PADDING
    box_y = MARGIN_Y - PADDING

    # opaque dark bar
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(15, 15, 15, 255))

    y = MARGIN_Y
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w) // 2
        # shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_heights[i] + LINE_SPACING

    img.save(str(OUT_DIR / filename))
    print(f"Wrote {filename}")

print("All subtitle overlays done.")
