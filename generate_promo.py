#!/usr/bin/env python3
import cv2
import numpy as np
import math
import os

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 60
TOTAL_FRAMES = FPS * DURATION
BAR_H = 120
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lazy_index_trading_promo.mp4")

# Brand colors
GOLD = (0, 195, 255)
DARK_BG = (15, 12, 10)
RED_LOSS = (50, 50, 220)
GREEN_WIN = (80, 200, 80)
WHITE = (255, 255, 255)
CYAN = (230, 180, 0)


def lerp(a, b, t):
    return a + (b - a) * max(0, min(1, t))


def lerp_color(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def add_grain(frame, intensity=15):
    noise = np.random.randint(-intensity, intensity, frame.shape, dtype=np.int16)
    return np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def add_letterbox(frame):
    frame[:BAR_H, :] = 0
    frame[HEIGHT - BAR_H:, :] = 0


def add_vignette(frame, strength=0.4):
    rows, cols = frame.shape[:2]
    X = np.arange(cols) - cols / 2
    Y = np.arange(rows) - rows / 2
    X, Y = np.meshgrid(X, Y)
    dist = np.sqrt(X**2 + Y**2) / (math.sqrt(cols**2 + rows**2) / 2)
    vignette = 1 - dist * strength
    vignette = np.clip(vignette, 0, 1)
    for c in range(3):
        frame[:, :, c] = (frame[:, :, c] * vignette).astype(np.uint8)


def draw_text_centered(frame, text, y, scale, color, thickness=2):
    font = cv2.FONT_HERSHEY_SIMPLEX
    sz = cv2.getTextSize(text, font, scale, thickness)[0]
    x = (WIDTH - sz[0]) // 2
    cv2.putText(frame, text, (x + 2, y + 2), font, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def draw_text_fade(frame, text, y, scale, color, thickness, opacity):
    if opacity <= 0:
        return
    overlay = frame.copy()
    draw_text_centered(overlay, text, y, scale, color, thickness)
    alpha = max(0, min(1, opacity))
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def generate_candles(n, trend="down", volatility=20):
    candles = []
    price = 100 if trend == "down" else 40
    for i in range(n):
        if trend == "down":
            change = np.random.uniform(-3, 1) * (volatility / 20)
        elif trend == "up":
            change = np.random.uniform(-1, 3) * (volatility / 20)
        else:
            change = np.random.uniform(-2, 2) * (volatility / 20)
        o = price
        c = price + change
        h = max(o, c) + abs(np.random.uniform(0, 2))
        l = min(o, c) - abs(np.random.uniform(0, 2))
        candles.append((o, h, l, c))
        price = c
    return candles


def draw_candles(frame, candles, region, offset=0, alpha=1.0):
    x0, y0, w, h = region
    n = len(candles)
    if n == 0:
        return
    all_prices = [p for c in candles for p in c]
    pmin, pmax = min(all_prices), max(all_prices)
    if pmax == pmin:
        pmax = pmin + 1
    cw = max(2, w // n - 2)

    overlay = frame.copy() if alpha < 1.0 else frame
    target = overlay

    for i, (o, hi, lo, c) in enumerate(candles):
        cx = x0 + int((i + 0.5 + offset) * w / n)
        oy = y0 + int((1 - (o - pmin) / (pmax - pmin)) * h)
        cy = y0 + int((1 - (c - pmin) / (pmax - pmin)) * h)
        hy = y0 + int((1 - (hi - pmin) / (pmax - pmin)) * h)
        ly = y0 + int((1 - (lo - pmin) / (pmax - pmin)) * h)
        color = GREEN_WIN if c >= o else RED_LOSS
        cv2.line(target, (cx, hy), (cx, ly), color, 1, cv2.LINE_AA)
        top = min(oy, cy)
        bot = max(oy, cy)
        if bot - top < 1:
            bot = top + 1
        cv2.rectangle(target, (cx - cw // 2, top), (cx + cw // 2, bot), color, -1)

    if alpha < 1.0:
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_equity_curve(frame, points, region, color, thickness=2, fill=False):
    x0, y0, w, h = region
    n = len(points)
    if n < 2:
        return
    pmin, pmax = min(points), max(points)
    if pmax == pmin:
        pmax = pmin + 1
    pts = []
    for i, p in enumerate(points):
        x = x0 + int(i * w / (n - 1))
        y = y0 + int((1 - (p - pmin) / (pmax - pmin)) * h)
        pts.append([x, y])
    arr = np.array(pts, dtype=np.int32)
    if fill:
        fill_pts = list(pts) + [[x0 + w, y0 + h], [x0, y0 + h]]
        fill_arr = np.array(fill_pts, dtype=np.int32)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [fill_arr], (*color[:3],))
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
    cv2.polylines(frame, [arr], False, color, thickness, cv2.LINE_AA)


def draw_clock(frame, cx, cy, radius, hour, minute):
    cv2.circle(frame, (cx, cy), radius, (60, 60, 60), 2, cv2.LINE_AA)
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = int(cx + (radius - 8) * math.cos(angle))
        y1 = int(cy + (radius - 8) * math.sin(angle))
        x2 = int(cx + radius * math.cos(angle))
        y2 = int(cy + radius * math.sin(angle))
        cv2.line(frame, (x1, y1), (x2, y2), (80, 80, 80), 1, cv2.LINE_AA)
    h_angle = math.radians((hour % 12 + minute / 60) * 30 - 90)
    hx = int(cx + radius * 0.5 * math.cos(h_angle))
    hy = int(cy + radius * 0.5 * math.sin(h_angle))
    cv2.line(frame, (cx, cy), (hx, hy), WHITE, 2, cv2.LINE_AA)
    m_angle = math.radians(minute * 6 - 90)
    mx = int(cx + radius * 0.75 * math.cos(m_angle))
    my = int(cy + radius * 0.75 * math.sin(m_angle))
    cv2.line(frame, (cx, cy), (mx, my), WHITE, 1, cv2.LINE_AA)


def draw_particles(frame, t, count=30, color=GOLD, speed=1.0):
    np.random.seed(77)
    for i in range(count):
        bx = np.random.randint(0, WIDTH)
        by = np.random.randint(BAR_H, HEIGHT - BAR_H)
        x = int((bx + t * speed * 15 * (i % 3 + 1)) % WIDTH)
        y = int(by + math.sin(t * 0.5 + i) * 30) % (HEIGHT - 2 * BAR_H) + BAR_H
        sz = max(1, int(1 + math.sin(t + i * 0.7)))
        c = tuple(int(v * (0.4 + 0.6 * abs(math.sin(t * 0.3 + i)))) for v in color)
        cv2.circle(frame, (x, y), sz, c, -1, cv2.LINE_AA)


def draw_glow_line(frame, y, color, t):
    alpha = 0.3 + 0.2 * math.sin(t * 2)
    overlay = frame.copy()
    cv2.line(overlay, (0, y), (WIDTH, y), color, 1, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def scene_manual_trader(frame, t, progress):
    """Scene 1: Manual trader struggling (0-12s)"""
    frame[:] = DARK_BG
    red_tint = int(20 + 10 * math.sin(t * 0.5))
    frame[:, :, 2] = np.clip(frame[:, :, 2].astype(np.int16) + red_tint, 0, 255).astype(np.uint8)

    np.random.seed(10)
    candles = generate_candles(60, "down", 25)
    visible = int(len(candles) * min(1, progress * 1.5))
    draw_candles(frame, candles[:max(1, visible)], (100, 200, 1200, 500))

    for i in range(3):
        gy = 250 + i * 150
        draw_glow_line(frame, gy, (30, 30, 80), t + i)

    hour = 2
    minute = int((t * 8) % 60)
    draw_clock(frame, 1650, 300, 60, hour, minute)
    draw_text_centered(frame, "02:00 AM", 400, 0.6, (100, 100, 150), 1)

    loss = -int(progress * 4800)
    loss_color = RED_LOSS
    draw_text_centered(frame, f"P&L: {loss:,} USD", 750, 1.2, loss_color, 2)

    fade_in = ease_in_out(min(1, progress * 3))
    draw_text_fade(frame, "MANUAL TRADING", 900, 1.0, (120, 120, 160), 2, fade_in)

    if progress > 0.3:
        stress_alpha = ease_in_out(min(1, (progress - 0.3) * 3))
        draw_text_fade(frame, "Stunden vor dem Chart...", 960, 0.7, (100, 100, 140), 1, stress_alpha)


def scene_frustration(frame, t, progress):
    """Scene 2: Escalating losses (12-22s)"""
    frame[:] = DARK_BG
    red_tint = int(30 + 20 * math.sin(t * 2))
    frame[:, :, 2] = np.clip(frame[:, :, 2].astype(np.int16) + red_tint, 0, 255).astype(np.uint8)

    np.random.seed(20)
    candles1 = generate_candles(40, "down", 35)
    candles2 = generate_candles(30, "down", 30)
    candles3 = generate_candles(35, "down", 25)

    draw_candles(frame, candles1, (50, 180, 550, 350))
    draw_candles(frame, candles2, (650, 180, 550, 350))
    draw_candles(frame, candles3, (1250, 180, 550, 350))

    shake_x = int(math.sin(t * 15) * 3 * progress)
    shake_y = int(math.cos(t * 12) * 2 * progress)
    M = np.float32([[1, 0, shake_x], [0, 1, shake_y]])
    cv2.warpAffine(frame, M, (WIDTH, HEIGHT), dst=frame, borderMode=cv2.BORDER_REFLECT)

    loss = -4800 - int(progress * 7200)
    draw_text_centered(frame, f"P&L: {loss:,} USD", 620, 1.5, RED_LOSS, 3)

    emotions = ["Emotionales Trading", "Overtrading", "Kein System"]
    for i, text in enumerate(emotions):
        show_at = i * 0.3
        if progress > show_at:
            alpha = ease_in_out(min(1, (progress - show_at) * 3))
            y = 720 + i * 60
            draw_text_fade(frame, text, y, 0.7, (140, 100, 100), 1, alpha)

    if progress > 0.7:
        flash = ease_in_out(min(1, (progress - 0.7) * 5))
        overlay = np.full_like(frame, (0, 0, 60))
        cv2.addWeighted(overlay, flash * 0.3, frame, 1, 0, frame)


def scene_transition(frame, t, progress):
    """Scene 3: Transition moment (22-28s)"""
    p = ease_in_out(progress)
    bg1 = DARK_BG
    bg2 = (25, 20, 15)
    bg = lerp_color(bg1, bg2, p)
    frame[:] = bg

    if progress < 0.5:
        fade = 1 - ease_in_out(progress * 2)
        np.random.seed(30)
        candles = generate_candles(30, "down", 20)
        draw_candles(frame, candles, (400, 250, 800, 400), alpha=fade)

    line_progress = ease_in_out(max(0, (progress - 0.2) * 1.5))
    if line_progress > 0:
        lx = int(WIDTH * 0.1 + WIDTH * 0.8 * line_progress)
        line_color = lerp_color(RED_LOSS, GOLD, progress)
        cv2.line(frame, (int(WIDTH * 0.1), HEIGHT // 2), (lx, HEIGHT // 2), line_color, 2, cv2.LINE_AA)

    text_fade = ease_in_out(max(0, (progress - 0.3) * 2))
    draw_text_fade(frame, "THERE IS", HEIGHT // 2 - 50, 1.5, WHITE, 3, text_fade)
    text_fade2 = ease_in_out(max(0, (progress - 0.5) * 2))
    draw_text_fade(frame, "A BETTER WAY", HEIGHT // 2 + 30, 1.8, GOLD, 3, text_fade2)

    draw_particles(frame, t, 15, GOLD, 0.5)


def scene_algo_trading(frame, t, progress):
    """Scene 4: Algo trading (28-42s)"""
    frame[:] = (20, 18, 12)
    gold_tint = int(10 + 5 * math.sin(t * 0.3))
    frame[:, :, 0] = np.clip(frame[:, :, 0].astype(np.int16) + gold_tint, 0, 255).astype(np.uint8)

    np.random.seed(40)
    candles = generate_candles(60, "up", 18)
    visible = int(len(candles) * min(1, progress * 1.3))
    draw_candles(frame, candles[:max(1, visible)], (100, 200, 1100, 450))

    eq_points = []
    val = 10000
    np.random.seed(41)
    for i in range(100):
        val += np.random.uniform(-50, 150)
        eq_points.append(val)
    vis_eq = int(len(eq_points) * min(1, progress * 1.2))
    if vis_eq > 1:
        draw_equity_curve(frame, eq_points[:vis_eq], (1250, 200, 550, 450), GREEN_WIN, 2, True)

    profit = int(progress * 12400)
    draw_text_centered(frame, f"+{profit:,} USD", 720, 1.3, GREEN_WIN, 3)

    if progress > 0.2:
        alpha = ease_in_out(min(1, (progress - 0.2) * 2.5))
        draw_text_fade(frame, "ALGORITHMIC TRADING", 810, 1.0, GOLD, 2, alpha)

    if progress > 0.5:
        alpha = ease_in_out(min(1, (progress - 0.5) * 3))
        draw_text_fade(frame, "Keine Emotionen. Kein Stress.", 870, 0.7, (180, 180, 160), 1, alpha)

    draw_particles(frame, t, 25, GOLD, 0.8)

    for i in range(5):
        gy = 250 + i * 100
        draw_glow_line(frame, gy, (20, 30, 10), t + i)


def scene_freedom(frame, t, progress):
    """Scene 5: Freedom - algo runs itself (42-52s)"""
    frame[:] = (22, 18, 10)

    strategies = ["Mean Reversion", "Breakout", "Seasonality", "Swing Trading"]
    np.random.seed(50)
    for i, name in enumerate(strategies):
        x0 = 80 + (i % 2) * 900
        y0 = 180 + (i // 2) * 350
        w, h = 780, 280
        cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (40, 35, 25), 1, cv2.LINE_AA)

        eq = []
        val = 1000
        for j in range(80):
            val += np.random.uniform(-20, 60)
            eq.append(val)
        vis = int(len(eq) * min(1, progress * 1.5))
        if vis > 1:
            draw_equity_curve(frame, eq[:vis], (x0 + 10, y0 + 30, w - 20, h - 60), GREEN_WIN, 2, True)

        show_at = i * 0.15
        if progress > show_at:
            alpha = ease_in_out(min(1, (progress - show_at) * 3))
            draw_text_fade(frame, name, y0 + 20, 0.6, GOLD, 1, alpha)
            status_color = GREEN_WIN
            draw_text_fade(frame, "ACTIVE", y0 + h - 15, 0.5, status_color, 1, alpha)

    if progress > 0.4:
        alpha = ease_in_out(min(1, (progress - 0.4) * 2.5))
        draw_text_fade(frame, "24/7 AUTOMATISIERT", 930, 0.9, GOLD, 2, alpha)

    draw_particles(frame, t, 35, GOLD, 0.6)


def scene_branding(frame, t, progress):
    """Scene 6: Branding finale (52-60s)"""
    frame[:] = (12, 10, 8)

    glow = ease_in_out(min(1, progress * 2))
    center_y = HEIGHT // 2
    for r in range(200, 0, -2):
        intensity = int(glow * 25 * (1 - r / 200))
        color = (intensity, int(intensity * 0.8), 0)
        cv2.circle(frame, (WIDTH // 2, center_y - 30), r, color, 1, cv2.LINE_AA)

    title_fade = ease_in_out(min(1, progress * 2.5))
    draw_text_fade(frame, "LAZY INDEX TRADING", center_y - 30, 2.2, GOLD, 4, title_fade)

    if progress > 0.25:
        sub_fade = ease_in_out(min(1, (progress - 0.25) * 3))
        draw_text_fade(frame, "Algo Trading. Einfach. Profitabel.", center_y + 40, 0.8, WHITE, 1, sub_fade)

    if progress > 0.45:
        url_fade = ease_in_out(min(1, (progress - 0.45) * 3))
        draw_text_fade(frame, "workshop.lazyindextrading.com", center_y + 100, 0.7, CYAN, 1, url_fade)

    if progress > 0.65:
        cta_fade = ease_in_out(min(1, (progress - 0.65) * 3))
        draw_text_fade(frame, "JETZT STARTEN", center_y + 170, 1.0, GOLD, 2, cta_fade)

    draw_particles(frame, t, 40, GOLD, 0.3)


def generate_video():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT, fourcc, FPS, (WIDTH, HEIGHT))
    if not out.isOpened():
        print("Error: Could not open video writer.")
        return

    print(f"Generating {DURATION}s promo video at {FPS}fps ({TOTAL_FRAMES} frames)...")

    scenes = [
        (0, 12, scene_manual_trader),
        (12, 22, scene_frustration),
        (22, 28, scene_transition),
        (28, 42, scene_algo_trading),
        (42, 52, scene_freedom),
        (52, 60, scene_branding),
    ]

    for frame_num in range(TOTAL_FRAMES):
        t = frame_num / FPS
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        for start, end, scene_fn in scenes:
            if start <= t < end:
                progress = (t - start) / (end - start)
                scene_fn(frame, t, progress)
                break

        add_vignette(frame, 0.5)
        frame = add_grain(frame, 12)
        add_letterbox(frame)
        out.write(frame)

        if frame_num % (FPS * 5) == 0:
            pct = frame_num / TOTAL_FRAMES * 100
            print(f"  {frame_num}/{TOTAL_FRAMES} frames ({pct:.0f}%)")

    out.release()
    size = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"\nDone! {OUTPUT} ({size:.1f} MB)")


if __name__ == "__main__":
    generate_video()
