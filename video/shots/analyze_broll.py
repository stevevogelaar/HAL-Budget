import cv2
import numpy as np
from pathlib import Path

path = Path(r"C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget\video\shots\b-roll.mp4")
cap = cv2.VideoCapture(str(path))
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
total = total_frames / fps
print(f"Duration: {total:.2f}s, FPS: {fps:.2f}, Frames: {total_frames:.0f}")

sample_interval = 0.5  # seconds
n = int(total / sample_interval) + 1

prev = None
times = []
diffs = []
for i in range(n):
    t = i * sample_interval
    if t > total:
        break
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if prev is not None:
        diff = np.mean(np.abs(gray.astype(float) - prev.astype(float)))
        diffs.append(diff)
        times.append(t)
    prev = gray

cap.release()

diffs = np.array(diffs)
# Threshold for "motion" based on percentile
lo, hi = np.percentile(diffs, [20, 80])
print(f"Diff range: {diffs.min():.1f} - {diffs.max():.1f}, p20={lo:.1f}, p80={hi:.1f}")

# Simple state machine: static vs active
threshold = lo + (hi - lo) * 0.5
states = diffs > threshold

# Group into segments (active vs static)
segments = []
current_state = states[0]
start = times[0] - sample_interval/2
for i, active in enumerate(states):
    if active != current_state:
        end = times[i] - sample_interval/2
        segments.append((start, end, current_state, end - start))
        start = end
        current_state = active
# close last
segments.append((start, total, current_state, total - start))

print("\nAll segments (active=True means motion/typing/scrolling):")
for seg in segments:
    start, end, active, dur = seg
    print(f"{start:6.1f}s - {end:6.1f}s  {dur:5.1f}s  {'ACTIVE' if active else 'static'}")

# Pick out likely demo segments: active segments longer than 2s
print("\nCandidate demo segments (active, >2s):")
candidates = [s for s in segments if s[2] and s[3] > 2.0]
for seg in candidates:
    start, end, active, dur = seg
    print(f"{start:6.1f}s - {end:6.1f}s  {dur:5.1f}s")

# Save thumbnails at segment midpoints for visual identification
thumb_dir = path.parent / "b-roll_thumbs"
thumb_dir.mkdir(exist_ok=True)
cap2 = cv2.VideoCapture(str(path))
for idx, seg in enumerate(candidates):
    mid = (seg[0] + seg[1]) / 2
    cap2.set(cv2.CAP_PROP_POS_MSEC, mid * 1000)
    ret, frame = cap2.read()
    if ret:
        small = cv2.resize(frame, (320, 180))
        cv2.imwrite(str(thumb_dir / f"seg_{idx:02d}_{mid:05.1f}s.jpg"), small)
cap2.release()
print(f"\nThumbnails saved to {thumb_dir}")
