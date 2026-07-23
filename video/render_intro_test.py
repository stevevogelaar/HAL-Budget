import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Paths
img_path = Path(r"C:\.playwright-mcp\shot_home.png")
out_path = Path(r"C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget\video\test_intro.mp4")

# Video settings
fps = 30
width, height = 1920, 1080
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

# Font
font_path = r"C:\Windows\Fonts\segoeui.ttf"
try:
    font = ImageFont.truetype(font_path, 64)
except Exception:
    font = ImageFont.load_default()

# Load background and resize to HD
bg = Image.open(str(img_path)).convert("RGB")
bg = bg.resize((width, height), Image.Resampling.LANCZOS)

# Captions: one concise sentence at a time, top of screen
captions = [
    ("Hi. I'm the AI assistant behind HAL Budget.", 4),
    ("Most finance apps send your money data to the cloud.", 4),
    ("I don't.", 3),
    ("I run Gemma 4 right on your machine.", 4),
    ("Your data lives in a local SQLite file.", 4),
    ("Ask plain-English questions about your finances.", 4),
    ("No cloud. No API keys.", 4),
    ("This is HAL Budget.", 4),
]

margin_x = 100
margin_y = 60
max_text_w = width - 2 * margin_x
line_spacing = 18
padding = 35


def wrap_text(text, font, max_width):
    lines = []
    words = text.split(" ")
    current = ""
    for word in words:
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


for caption, duration in captions:
    frame = bg.copy()
    draw = ImageDraw.Draw(frame)

    lines = []
    words = caption.split(" ")
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_text_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    # Measure total text block height
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    total_h = sum(line_heights) + line_spacing * (len(lines) - 1)

    box_w = width - 2 * margin_x + 2 * padding
    box_h = total_h + 2 * padding
    box_x = margin_x - padding
    box_y = margin_y - padding

    # Opaque dark background bar at top
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(15, 15, 15))

    # Draw text
    y = margin_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        # subtle shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += line_heights.pop(0) + line_spacing

    # Write frames
    cv_frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
    for _ in range(int(fps * duration)):
        writer.write(cv_frame)

writer.release()
print(f"Wrote {out_path}")
print(f"Total duration: {sum(d for _, d in captions)}s")
