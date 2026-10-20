#!/usr/bin/env python3
"""
Lazy Index Trading - 75-second cinematic promo video (self-contained).
Requirements: pip install opencv-python-headless numpy
"""
import cv2
import numpy as np
import math
import os

WIDTH, HEIGHT = 1920, 1080
BAR_H = 110
FPS = 30
DURATION = 75
TOTAL_FRAMES = FPS * DURATION
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lazy_index_trading_75s.mp4")

GOLD = (0, 195, 255)
RED_LOSS = (50, 50, 220)
GREEN_WIN = (80, 210, 80)
WHITE = (255, 255, 255)
CYAN = (230, 180, 0)
BLUE_SCREEN = (180, 140, 60)


def lerp(a, b, t):
    return a + (b - a) * max(0, min(1, t))


def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def ease_in_out(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def add_grain(frame, intensity=10):
    noise = np.random.randint(-intensity, intensity, frame.shape, dtype=np.int16)
    return np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def add_letterbox(frame):
    frame[:BAR_H, :] = 0
    frame[HEIGHT - BAR_H:, :] = 0


def add_vignette(frame, strength=0.45):
    rows, cols = frame.shape[:2]
    X = np.arange(cols, dtype=np.float32) - cols / 2
    Y = np.arange(rows, dtype=np.float32) - rows / 2
    X, Y = np.meshgrid(X, Y)
    dist = np.sqrt(X ** 2 + Y ** 2) / (math.sqrt(cols ** 2 + rows ** 2) / 2)
    vignette = np.clip(1 - dist * strength, 0, 1)
    for c in range(3):
        frame[:, :, c] = (frame[:, :, c] * vignette).astype(np.uint8)


def draw_text_centered(frame, text, y, scale, color, thickness=2):
    font = cv2.FONT_HERSHEY_SIMPLEX
    sz = cv2.getTextSize(text, font, scale, thickness)[0]
    x = (WIDTH - sz[0]) // 2
    cv2.putText(frame, text, (x + 2, y + 2), font, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def draw_text_fade(frame, text, y, scale, color, thickness, opacity):
    if opacity <= 0.01:
        return
    overlay = frame.copy()
    draw_text_centered(overlay, text, y, scale, color, thickness)
    a = max(0, min(1, opacity))
    cv2.addWeighted(overlay, a, frame, 1 - a, 0, frame)


def draw_subtitle(frame, text, opacity=1.0):
    if opacity <= 0.01 or not text:
        return
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.65
    thickness = 1
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        sz = cv2.getTextSize(test, font, scale, thickness)[0]
        if sz[0] > WIDTH - 300:
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)

    base_y = HEIGHT - BAR_H - 40 - len(lines) * 38
    pad = 16
    max_w = max(cv2.getTextSize(ln, font, scale, thickness)[0][0] for ln in lines)
    rx1, ry1 = (WIDTH - max_w) // 2 - pad, base_y - 28 - pad
    rx2, ry2 = (WIDTH + max_w) // 2 + pad, base_y + (len(lines) - 1) * 38 + pad

    overlay = frame.copy()
    cv2.rectangle(overlay, (rx1, ry1), (rx2, ry2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55 * opacity, frame, 1 - 0.55 * opacity, 0, frame)

    for i, ln in enumerate(lines):
        y = base_y + i * 38
        sz = cv2.getTextSize(ln, font, scale, thickness)[0]
        x = (WIDTH - sz[0]) // 2
        cv2.putText(frame, ln, (x, y), font, scale, WHITE, thickness, cv2.LINE_AA)


def draw_particles(frame, t, count=30, color=GOLD, speed=1.0, seed=77):
    np.random.seed(seed)
    for i in range(count):
        bx = np.random.randint(0, WIDTH)
        by = np.random.randint(BAR_H + 20, HEIGHT - BAR_H - 20)
        x = int((bx + t * speed * 12 * (i % 3 + 1)) % WIDTH)
        y = int(by + math.sin(t * 0.5 + i) * 25)
        y = max(BAR_H + 5, min(HEIGHT - BAR_H - 5, y))
        sz = max(1, int(1 + math.sin(t + i * 0.7)))
        brightness = 0.3 + 0.7 * abs(math.sin(t * 0.3 + i))
        c = tuple(int(v * brightness) for v in color)
        cv2.circle(frame, (x, y), sz, c, -1, cv2.LINE_AA)


def generate_candles(n, trend="down", vol=20, seed=10):
    np.random.seed(seed)
    candles, price = [], 100 if trend == "down" else 40
    for i in range(n):
        if trend == "down":
            ch = np.random.uniform(-3, 0.8) * (vol / 20)
        elif trend == "up":
            ch = np.random.uniform(-0.8, 3) * (vol / 20)
        else:
            ch = np.random.uniform(-2, 2) * (vol / 20)
        o = price
        c = price + ch
        h = max(o, c) + abs(np.random.uniform(0, 1.5))
        l = min(o, c) - abs(np.random.uniform(0, 1.5))
        candles.append((o, h, l, c))
        price = c
    return candles


def draw_candles(frame, candles, region):
    x0, y0, w, h = region
    n = len(candles)
    if n == 0:
        return
    prices = [p for c in candles for p in c]
    pmin, pmax = min(prices), max(prices)
    if pmax == pmin:
        pmax += 1
    cw = max(2, w // n - 2)
    for i, (o, hi, lo, c) in enumerate(candles):
        cx = x0 + int((i + 0.5) * w / n)
        oy = y0 + int((1 - (o - pmin) / (pmax - pmin)) * h)
        cy = y0 + int((1 - (c - pmin) / (pmax - pmin)) * h)
        hy = y0 + int((1 - (hi - pmin) / (pmax - pmin)) * h)
        ly = y0 + int((1 - (lo - pmin) / (pmax - pmin)) * h)
        color = GREEN_WIN if c >= o else RED_LOSS
        cv2.line(frame, (cx, hy), (cx, ly), color, 1, cv2.LINE_AA)
        top, bot = min(oy, cy), max(oy, cy)
        if bot - top < 1:
            bot = top + 1
        cv2.rectangle(frame, (cx - cw // 2, top), (cx + cw // 2, bot), color, -1)


def draw_equity_curve(frame, points, region, color, thickness=2, fill=False):
    x0, y0, w, h = region
    n = len(points)
    if n < 2:
        return
    pmin, pmax = min(points), max(points)
    if pmax == pmin:
        pmax += 1
    pts = []
    for i, p in enumerate(points):
        x = x0 + int(i * w / (n - 1))
        y = y0 + int((1 - (p - pmin) / (pmax - pmin)) * h)
        pts.append([x, y])
    arr = np.array(pts, dtype=np.int32)
    if fill:
        fill_pts = list(pts) + [[x0 + w, y0 + h], [x0, y0 + h]]
        overlay = frame.copy()
        cv2.fillPoly(overlay, [np.array(fill_pts, np.int32)], color)
        cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)
    cv2.polylines(frame, [arr], False, color, thickness, cv2.LINE_AA)


def draw_grid(frame, region, color=(30, 30, 30), lines=6):
    x0, y0, w, h = region
    for i in range(lines + 1):
        y = y0 + int(i * h / lines)
        cv2.line(frame, (x0, y), (x0 + w, y), color, 1)
        x = x0 + int(i * w / lines)
        cv2.line(frame, (x, y0), (x, y0 + h), color, 1)


def draw_clock(frame, cx, cy, radius, hour, minute):
    cv2.circle(frame, (cx, cy), radius, (60, 60, 70), 2, cv2.LINE_AA)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        x1 = int(cx + (radius - 10) * math.cos(a))
        y1 = int(cy + (radius - 10) * math.sin(a))
        x2 = int(cx + radius * math.cos(a))
        y2 = int(cy + radius * math.sin(a))
        cv2.line(frame, (x1, y1), (x2, y2), (90, 90, 100), 1, cv2.LINE_AA)
    ha = math.radians((hour % 12 + minute / 60) * 30 - 90)
    cv2.line(frame, (cx, cy), (int(cx + radius * 0.5 * math.cos(ha)),
             int(cy + radius * 0.5 * math.sin(ha))), WHITE, 2, cv2.LINE_AA)
    ma = math.radians(minute * 6 - 90)
    cv2.line(frame, (cx, cy), (int(cx + radius * 0.7 * math.cos(ma)),
             int(cy + radius * 0.7 * math.sin(ma))), WHITE, 1, cv2.LINE_AA)


def draw_nodes_network(frame, t, region, color=CYAN, node_count=20, seed=60):
    x0, y0, w, h = region
    np.random.seed(seed)
    nodes = []
    for i in range(node_count):
        bx = np.random.randint(x0, x0 + w)
        by = np.random.randint(y0, y0 + h)
        ox = math.sin(t * 0.7 + i * 1.1) * 30
        oy = math.cos(t * 0.5 + i * 0.8) * 20
        nodes.append((int(bx + ox), int(by + oy)))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 200:
                alpha = 1 - dist / 200
                c = tuple(int(v * alpha * 0.5) for v in color)
                cv2.line(frame, nodes[i], nodes[j], c, 1, cv2.LINE_AA)
    for i, (nx, ny) in enumerate(nodes):
        r = int(3 + 2 * math.sin(t + i))
        bright = 0.5 + 0.5 * math.sin(t * 1.5 + i * 0.5)
        c = tuple(int(v * bright) for v in color)
        cv2.circle(frame, (nx, ny), r, c, -1, cv2.LINE_AA)
        if i % 4 == int(t * 3) % 4:
            cv2.circle(frame, (nx, ny), r + 5, c, 1, cv2.LINE_AA)


def apply_color_grade(frame, temperature):
    if temperature < 0:
        boost = int(abs(temperature) * 40)
        frame[:, :, 0] = np.clip(frame[:, :, 0].astype(np.int16) + boost, 0, 255).astype(np.uint8)
        frame[:, :, 2] = np.clip(frame[:, :, 2].astype(np.int16) - boost // 3, 0, 255).astype(np.uint8)
    elif temperature > 0:
        boost = int(temperature * 30)
        frame[:, :, 2] = np.clip(frame[:, :, 2].astype(np.int16) + boost // 2, 0, 255).astype(np.uint8)
        frame[:, :, 1] = np.clip(frame[:, :, 1].astype(np.int16) + boost // 4, 0, 255).astype(np.uint8)
        frame[:, :, 0] = np.clip(frame[:, :, 0].astype(np.int16) - boost // 4, 0, 255).astype(np.uint8)
