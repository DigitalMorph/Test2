#!/usr/bin/env python3
"""
Generate a 60-second animated video with colorful visuals and a countdown timer.
"""

import cv2
import numpy as np
import math
import os

# Video settings
WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 60  # seconds
TOTAL_FRAMES = FPS * DURATION
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_60s.mp4")


def hsv_to_bgr(h, s, v):
    """Convert HSV (0-360, 0-1, 0-1) to BGR tuple."""
    color = np.uint8([[[int(h / 2), int(s * 255), int(v * 255)]]])
    bgr = cv2.cvtColor(color, cv2.COLOR_HSV2BGR)
    return int(bgr[0, 0, 0]), int(bgr[0, 0, 1]), int(bgr[0, 0, 2])


def draw_gradient_background(frame, hue_offset):
    """Draw a smooth animated gradient background."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        h1 = (hue_offset) % 360
        h2 = (hue_offset + 120) % 360
        h = h1 + (h2 - h1) * ratio
        color = hsv_to_bgr(h % 360, 0.6, 0.3)
        frame[y, :] = color


def draw_rotating_circles(frame, t, cx, cy):
    """Draw orbiting circles around a center point."""
    num_circles = 6
    radius_orbit = 200
    for i in range(num_circles):
        angle = t * 1.5 + (2 * math.pi * i / num_circles)
        x = int(cx + radius_orbit * math.cos(angle))
        y = int(cy + radius_orbit * math.sin(angle))
        hue = (i * 60 + t * 30) % 360
        color = hsv_to_bgr(hue, 0.9, 0.9)
        cv2.circle(frame, (x, y), 30, color, -1, cv2.LINE_AA)
        # Glow effect
        cv2.circle(frame, (x, y), 45, color, 2, cv2.LINE_AA)


def draw_pulsing_ring(frame, t, cx, cy):
    """Draw a pulsing ring in the center."""
    base_radius = 120
    pulse = math.sin(t * 2) * 30
    radius = int(base_radius + pulse)
    hue = (t * 40) % 360
    color = hsv_to_bgr(hue, 0.8, 0.85)
    cv2.circle(frame, (cx, cy), radius, color, 3, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), radius + 15, color, 1, cv2.LINE_AA)


def draw_floating_particles(frame, t):
    """Draw small floating particles across the screen."""
    np.random.seed(42)
    num_particles = 50
    for i in range(num_particles):
        base_x = np.random.randint(0, WIDTH)
        base_y = np.random.randint(0, HEIGHT)
        offset_x = math.sin(t * 0.8 + i * 0.5) * 40
        offset_y = math.cos(t * 0.6 + i * 0.3) * 40
        x = int((base_x + offset_x + t * 20 * (i % 3 + 1)) % WIDTH)
        y = int((base_y + offset_y) % HEIGHT)
        hue = (i * 15 + t * 20) % 360
        color = hsv_to_bgr(hue, 0.7, 0.8)
        size = int(2 + math.sin(t + i) * 2)
        cv2.circle(frame, (x, y), max(1, size), color, -1, cv2.LINE_AA)


def draw_wave(frame, t):
    """Draw an animated sine wave across the bottom."""
    points = []
    wave_y_base = HEIGHT - 150
    for x in range(0, WIDTH, 4):
        y = int(wave_y_base + math.sin(x * 0.01 + t * 2) * 40 + math.sin(x * 0.005 + t) * 20)
        points.append([x, y])
    if len(points) > 1:
        pts = np.array(points, dtype=np.int32)
        hue = (t * 25) % 360
        color = hsv_to_bgr(hue, 0.7, 0.7)
        cv2.polylines(frame, [pts], False, color, 2, cv2.LINE_AA)


def draw_spinning_polygon(frame, t, cx, cy, sides, radius, speed, hue_base):
    """Draw a spinning polygon."""
    angle_offset = t * speed
    points = []
    for i in range(sides):
        angle = angle_offset + (2 * math.pi * i / sides)
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))
        points.append([x, y])
    pts = np.array(points, dtype=np.int32)
    hue = (hue_base + t * 20) % 360
    color = hsv_to_bgr(hue, 0.8, 0.8)
    cv2.polylines(frame, [pts], True, color, 2, cv2.LINE_AA)


def draw_countdown(frame, seconds_left):
    """Draw the countdown timer in the center."""
    minutes = int(seconds_left) // 60
    secs = int(seconds_left) % 60
    text = f"{minutes}:{secs:02d}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 3.0
    thickness = 6

    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    tx = (WIDTH - text_size[0]) // 2
    ty = (HEIGHT + text_size[1]) // 2

    # Shadow
    cv2.putText(frame, text, (tx + 3, ty + 3), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    # Main text
    cv2.putText(frame, text, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)


def draw_progress_bar(frame, progress):
    """Draw a progress bar at the bottom."""
    bar_height = 8
    bar_y = HEIGHT - 40
    bar_x_start = 100
    bar_x_end = WIDTH - 100
    bar_width = bar_x_end - bar_x_start

    # Background
    cv2.rectangle(frame, (bar_x_start, bar_y), (bar_x_end, bar_y + bar_height), (50, 50, 50), -1)

    # Fill
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        hue = progress * 120  # green to red
        color = hsv_to_bgr(120 - hue, 0.8, 0.9)
        cv2.rectangle(frame, (bar_x_start, bar_y), (bar_x_start + fill_width, bar_y + bar_height), color, -1)


def draw_title(frame, t):
    """Draw an animated title at the top."""
    text = "60 Second Video"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    thickness = 3

    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    tx = (WIDTH - text_size[0]) // 2
    ty = 80

    alpha = 0.7 + 0.3 * math.sin(t * 1.5)
    brightness = int(255 * alpha)
    color = (brightness, brightness, brightness)

    cv2.putText(frame, text, (tx + 2, ty + 2), font, font_scale, (0, 0, 0), thickness + 1, cv2.LINE_AA)
    cv2.putText(frame, text, (tx, ty), font, font_scale, color, thickness, cv2.LINE_AA)


def generate_video():
    """Generate the 60-second video."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (WIDTH, HEIGHT))

    if not out.isOpened():
        print("Error: Could not open video writer.")
        return

    cx, cy = WIDTH // 2, HEIGHT // 2

    print(f"Generating {DURATION}s video at {FPS}fps ({TOTAL_FRAMES} frames)...")
    print(f"Resolution: {WIDTH}x{HEIGHT}")
    print(f"Output: {OUTPUT_FILE}")

    for frame_num in range(TOTAL_FRAMES):
        t = frame_num / FPS  # time in seconds
        progress = frame_num / TOTAL_FRAMES
        seconds_left = DURATION - t

        # Create frame
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        # Draw layers
        draw_gradient_background(frame, t * 15)
        draw_floating_particles(frame, t)
        draw_wave(frame, t)
        draw_spinning_polygon(frame, t, 300, 300, 5, 80, 1.0, 0)
        draw_spinning_polygon(frame, t, WIDTH - 300, 300, 6, 70, -0.8, 180)
        draw_spinning_polygon(frame, t, 300, HEIGHT - 300, 3, 90, 1.2, 90)
        draw_spinning_polygon(frame, t, WIDTH - 300, HEIGHT - 300, 8, 60, -0.6, 270)
        draw_pulsing_ring(frame, t, cx, cy)
        draw_rotating_circles(frame, t, cx, cy)
        draw_countdown(frame, seconds_left)
        draw_title(frame, t)
        draw_progress_bar(frame, progress)

        out.write(frame)

        if frame_num % (FPS * 5) == 0:
            print(f"  Progress: {frame_num}/{TOTAL_FRAMES} frames ({progress * 100:.0f}%)")

    out.release()
    file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"\nDone! Video saved to: {OUTPUT_FILE}")
    print(f"File size: {file_size:.1f} MB")


if __name__ == "__main__":
    generate_video()
