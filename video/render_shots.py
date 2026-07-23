import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

SHOTS_DIR = Path(r"C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget\video\shots")
SRC_DIR = Path(r"C:\.playwright-mcp\shots")
FPS = 30
W, H = 1920, 1080

FONT_PATH = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SIZE = 64
MARGIN_X = 100
MARGIN_Y = 60
PADDING = 35
LINE_SPACING = 18

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

shots = {
    "01_home": [
        ("I'm proud to present HAL Budget to you.", 5),
        ("I'm the AI assistant behind it.", 4),
        ("Most finance apps send your money data to the cloud.", 4),
        ("I don't.", 2.5),
        ("I run Gemma 4 right on your machine.", 4),
        ("Your data lives in a local SQLite file.", 4),
        ("Ask plain-English questions about your finances.", 4),
        ("No cloud. No API keys.", 4),
        ("This is HAL Budget.", 4),
    ],
    "02_chat_amazon": [
        ("Let's chat.", 3),
        ("How much did I spend on Amazon?", 3),
        ("Gemma 4 turns it into a safe SQL query.", 4),
        ("The answer appears in plain English.", 4),
        ("All read-only. Nothing leaves your machine.", 5),
    ],
    "03_chat_coffee": [
        ("I can dig into itemized receipts.", 4),
        ("How much did I spend on coffee?", 3),
        ("I search every line item, not just merchants.", 4),
        ("You see exactly what you bought.", 4),
    ],
    "04_chat_guardrail": [
        ("I'm honest about what I can't do.", 4),
        ("Tell me you bought a car for $21,000.", 3),
        ("I won't fake an update.", 3),
        ("I only answer from data I can read.", 4),
    ],
    "05_scan_receipt": [
        ("Receipts are stored line by line.", 4),
        ("Scan a Walmart receipt.", 3),
        ("I extract the merchant, total, tax, and each item.", 5),
        ("Then I save it all to your local database.", 4),
    ],
    "06_dashboard": [
        ("The Dashboard shows your full financial picture.", 4),
        ("Income, spending, balances, and upcoming bills.", 4),
        ("All live from your local SQLite file.", 4),
    ],
    "07_transactions": [
        ("All Transactions is your searchable history.", 4),
        ("Filter by date, category, merchant, or payment method.", 4),
        ("Everything stays on your machine.", 3),
    ],
    "08_settings": [
        ("Settings shows your local AI status.", 4),
        ("Switch between Ollama models.", 3),
        ("If the model stops, restart it here.", 4),
        ("No cloud needed.", 3),
    ],
    "09_outro": [
        ("That's HAL Budget.", 3),
        ("Your money. Your machine. Your answers.", 4),
        ("Built by the HAL team and Steve for the Edge/On-Device track.", 5),
        ("Find the code at github.com/stevevogelaar/HAL-Budget.", 5),
        ("Thank you, judges.", 3),
    ],
}


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


def render_shot(name, captions):
    img_path = SRC_DIR / f"{name}.png"
    out_path = SHOTS_DIR / f"{name}.mp4"

    bg = Image.open(str(img_path)).convert("RGB")
    bg = bg.resize((W, H), Image.Resampling.LANCZOS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, FPS, (W, H))

    for caption, duration in captions:
        frame = bg.copy()
        draw = ImageDraw.Draw(frame)

        max_text_w = W - 2 * MARGIN_X
        lines = wrap_text(draw, caption, font, max_text_w)

        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
        total_h = sum(line_heights) + LINE_SPACING * (len(lines) - 1)

        box_w = W - 2 * MARGIN_X + 2 * PADDING
        box_h = total_h + 2 * PADDING
        box_x = MARGIN_X - PADDING
        box_y = MARGIN_Y - PADDING

        # Opaque dark background at top
        draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(15, 15, 15))

        y = MARGIN_Y
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            x = (W - text_w) // 2
            # shadow
            draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0))
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += line_heights[i] + LINE_SPACING

        cv_frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        for _ in range(int(FPS * duration)):
            writer.write(cv_frame)

    writer.release()
    total = sum(d for _, d in captions)
    print(f"Wrote {out_path} ({total:.1f}s)")


SHOTS_DIR.mkdir(parents=True, exist_ok=True)
for name, captions in shots.items():
    render_shot(name, captions)

print("All shots rendered.")
