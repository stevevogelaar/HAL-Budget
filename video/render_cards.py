import cv2
import numpy as np
from PIL import Image
from pathlib import Path

VIDEO_DIR = Path(r"C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget\video")
FPS = 30
DURATION = 10
W, H = 1920, 1080


def render_from_png(name):
    png_path = VIDEO_DIR / f"{name}.png"
    mp4_path = VIDEO_DIR / f"{name}_10s.mp4"

    img = Image.open(str(png_path)).convert("RGB")
    img = img.resize((W, H), Image.Resampling.LANCZOS)
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(mp4_path), fourcc, FPS, (W, H))

    for _ in range(FPS * DURATION):
        writer.write(frame)

    writer.release()
    print(f"Wrote {mp4_path}")


render_from_png("intro_card")
render_from_png("outro_card")
print("Done")
