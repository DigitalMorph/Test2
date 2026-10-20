#!/usr/bin/env python3
"""
Lazy Index Trading - 75-second cinematic promo video.
7 scenes, no audio (voiceover text shown as subtitles).
Requirements: pip install opencv-python-headless numpy
"""
import cv2
import numpy as np
import math
import os
from promo_helpers import (
    WIDTH, HEIGHT, BAR_H, FPS,
    GOLD, RED_LOSS, GREEN_WIN, WHITE, CYAN, BLUE_SCREEN,
    lerp, lerp_color, ease_in_out,
    add_grain, add_letterbox, add_vignette,
    draw_text_centered, draw_text_fade, draw_subtitle,
    draw_particles,
    generate_candles, draw_candles, draw_equity_curve, draw_grid,
    draw_clock, draw_nodes_network, apply_color_grade,
)

DURATION = 75
TOTAL_FRAMES = FPS * DURATION
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lazy_index_trading_75s.mp4")


# ============ SCENE 1 (0-8s): The Struggle ============
def scene_struggle(frame, t, progress):
    """Dark bedroom. Phone glow on face. Clock 3:00 AM."""
    frame[:] = (18, 14, 10)

    zoom = 1.0 + progress * 0.08
    cx, cy = WIDTH // 2, HEIGHT // 2

    phone_w = int(380 * zoom)
    phone_h = int(680 * zoom)
    px = cx - phone_w // 2
    py = cy - phone_h // 2 + int(60 * progress)

    for r in range(300, 0, -8):
        intensity = int(50 * (1 - r / 300) * (0.5 + 0.5 * math.sin(t * 0.5)))
        c = (int(intensity * 1.5), int(intensity * 0.8), int(intensity * 0.3))
        cv2.circle(frame, (cx, cy - 50), r, c, 2, cv2.LINE_AA)

    cv2.rectangle(frame, (px, py), (px + phone_w, py + phone_h), (8, 8, 10), -1)
    cv2.rectangle(frame, (px + 20, py + 60), (px + phone_w - 20, py + phone_h - 60),
                  BLUE_SCREEN, -1)

    for i in range(5):
        y = py + 100 + i * 90
        np.random.seed(i + 100)
        for j in range(np.random.randint(3, 7)):
            bx = px + 40 + j * 50
            cv2.rectangle(frame, (bx, y), (bx + 40, y + 10), (160, 120, 50), -1)
            cv2.rectangle(frame, (bx, y + 15), (bx + 60, y + 25), (120, 90, 40), -1)

    bar_y = py + phone_h - 40
    chart_h = 30
    np.random.seed(1)
    for i in range(30):
        bx = px + 20 + i * ((phone_w - 40) // 30)
        bh = int(np.random.uniform(5, chart_h))
        is_red = np.random.random() > 0.3
        c = (40, 40, 180) if is_red else (60, 160, 60)
        cv2.rectangle(frame, (bx, bar_y - bh), (bx + 8, bar_y), c, -1)

    clock_x = 220
    clock_y = HEIGHT - BAR_H - 200
    draw_clock(frame, clock_x, clock_y, 70, 3, int(progress * 20))
    cv2.putText(frame, "03:00 AM", (clock_x - 60, clock_y + 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 130), 1, cv2.LINE_AA)

    apply_color_grade(frame, -0.6)

    if progress < 0.3:
        vo = ""
    elif progress < 0.65:
        vo = "Drei Uhr morgens. Wieder dieser Blick aufs Handy."
    else:
        vo = "Wieder diese Frage: Habe ich das Richtige getan?"
    opacity = ease_in_out(min(1, progress * 4)) * ease_in_out(min(1, (1 - progress) * 4))
    draw_subtitle(frame, vo, opacity)


# ============ SCENE 2 (8-18s): The Chaos ============
def scene_chaos(frame, t, progress):
    """Fast cuts: crashing charts, coffee, flickering monitors, stressed eyes."""
    frame[:] = (14, 10, 18)

    cut_duration = 2.5
    cut_index = int(progress * 4) % 4

    if cut_index == 0:
        # Crashing red charts
        np.random.seed(200)
        candles = generate_candles(50, "down", 35)
        n_show = int(len(candles) * ((progress * 4) % 1))
        draw_candles(frame, candles[:max(1, n_show)], (150, 180, 1620, 700))
        draw_grid(frame, (150, 180, 1620, 700), (30, 20, 20))

    elif cut_index == 1:
        # Multiple monitors flickering
        for i in range(6):
            row = i // 3
            col = i % 3
            mx = 100 + col * 580
            my = 180 + row * 400
            cv2.rectangle(frame, (mx, my), (mx + 540, my + 360), (25, 20, 25), -1)
            cv2.rectangle(frame, (mx, my), (mx + 540, my + 360), (60, 50, 60), 2)
            np.random.seed(300 + i)
            cands = generate_candles(25, "down", 30)
            draw_candles(frame, cands, (mx + 15, my + 15, 510, 330))
            flicker = int(50 * abs(math.sin(t * 10 + i)))
            overlay = frame.copy()
            cv2.rectangle(overlay, (mx, my), (mx + 540, my + 360), (flicker, flicker // 2, flicker // 2), -1)
            cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)

    elif cut_index == 2:
        # Coffee mug close-up - simulated with circular shape and steam
        cx, cy = WIDTH // 2, HEIGHT // 2 + 100
        cv2.ellipse(frame, (cx, cy + 150), (280, 60), 0, 0, 180, (40, 30, 25), -1)
        cv2.rectangle(frame, (cx - 280, cy - 150), (cx + 280, cy + 150), (50, 35, 25), -1)
        cv2.rectangle(frame, (cx - 260, cy - 130), (cx + 260, cy + 130), (25, 18, 15), -1)
        cv2.ellipse(frame, (cx, cy - 130), (260, 40), 0, 0, 360, (15, 10, 8), -1)
        # Steam
        for i in range(8):
            steam_x = int(cx + math.sin(t * 2 + i) * 40)
            steam_y = int(cy - 150 - i * 40 - (t * 100) % 50)
            r = int(15 + i * 3)
            alpha_v = max(0, 1 - i / 8)
            steam_c = tuple(int(80 * alpha_v) for _ in range(3))
            cv2.circle(frame, (steam_x, steam_y), r, steam_c, -1, cv2.LINE_AA)
        # Trembling hand effect
        shake_x = int(math.sin(t * 20) * 4)
        shake_y = int(math.cos(t * 18) * 3)
        M = np.float32([[1, 0, shake_x], [0, 1, shake_y]])
        cv2.warpAffine(frame, M, (WIDTH, HEIGHT), dst=frame, borderMode=cv2.BORDER_REFLECT)

    else:
        # Stressed eyes close-up - simulated
        eye_y = HEIGHT // 2
        for side in [-1, 1]:
            ex = WIDTH // 2 + side * 350
            # Dark circles
            cv2.ellipse(frame, (ex, eye_y + 100), (180, 50), 0, 0, 360, (30, 25, 35), -1)
            # Eye shape
            cv2.ellipse(frame, (ex, eye_y), (200, 90), 0, 0, 360, (240, 230, 220), -1)
            cv2.ellipse(frame, (ex, eye_y), (200, 90), 0, 0, 360, (50, 40, 40), 3)
            # Iris
            cv2.circle(frame, (ex, eye_y), 70, (100, 70, 50), -1)
            # Red veins
            for v in range(5):
                np.random.seed(400 + v + side * 10)
                angle = np.random.uniform(0, 2 * math.pi)
                r1 = 90
                r2 = np.random.randint(130, 180)
                x1 = int(ex + r1 * math.cos(angle))
                y1 = int(eye_y + r1 * math.sin(angle) * 0.4)
                x2 = int(ex + r2 * math.cos(angle))
                y2 = int(eye_y + r2 * math.sin(angle) * 0.4)
                cv2.line(frame, (x1, y1), (x2, y2), (60, 60, 180), 1, cv2.LINE_AA)
            # Pupil
            cv2.circle(frame, (ex, eye_y), 30, (10, 10, 10), -1)
            # Highlight
            cv2.circle(frame, (ex - 15, eye_y - 10), 8, WHITE, -1)

    # Tension shake overlay
    shake = int(math.sin(t * 15) * 3)
    M = np.float32([[1, 0, shake], [0, 1, 0]])
    cv2.warpAffine(frame, M, (WIDTH, HEIGHT), dst=frame, borderMode=cv2.BORDER_REFLECT)

    apply_color_grade(frame, -0.4)

    # VO subtitles
    if progress < 0.25:
        vo = "Du analysierst Charts, bis die Augen brennen."
    elif progress < 0.55:
        vo = "Du liest Nachrichten, die deine Entscheidungen zunichtemachen."
    elif progress < 0.85:
        vo = "Du kämpfst gegen den Markt – und gegen dich selbst."
    else:
        vo = ""
    draw_subtitle(frame, vo, 1.0)


# ============ SCENE 3 (18-28s): The Shift ============
def scene_shift(frame, t, progress):
    """Silhouette walking toward window with morning light."""
    frame[:] = (20, 15, 12)

    # Color transition from cool to warm
    temp = -0.3 + progress * 0.8

    # Sunrise gradient on the right side
    sun_x = int(WIDTH * 0.75)
    sun_y = int(HEIGHT * 0.45)
    sun_r = int(ease_in_out(progress) * 400)

    for r in range(sun_r, 0, -4):
        intensity = (1 - r / sun_r) if sun_r > 0 else 0
        warmth = ease_in_out(progress)
        c = (
            int(100 * intensity * (1 - warmth * 0.3)),
            int(170 * intensity * (0.5 + warmth * 0.5)),
            int(220 * intensity * (0.4 + warmth * 0.6)),
        )
        cv2.circle(frame, (sun_x, sun_y), r, c, 3, cv2.LINE_AA)

    # Window frame
    win_x1, win_y1 = int(WIDTH * 0.5), BAR_H + 50
    win_x2, win_y2 = WIDTH - 150, HEIGHT - BAR_H - 50
    cv2.rectangle(frame, (win_x1, win_y1), (win_x2, win_y2), (40, 30, 20), 8)
    # Window cross
    cv2.line(frame, ((win_x1 + win_x2) // 2, win_y1), ((win_x1 + win_x2) // 2, win_y2),
             (40, 30, 20), 6)
    cv2.line(frame, (win_x1, (win_y1 + win_y2) // 2), (win_x2, (win_y1 + win_y2) // 2),
             (40, 30, 20), 6)

    # Silhouette of person moving toward window
    walk_progress = ease_in_out(progress)
    px = int(lerp(300, 650, walk_progress))
    py = HEIGHT // 2 + 50

    # Body silhouette
    cv2.ellipse(frame, (px, py - 180), (45, 55), 0, 0, 360, (5, 5, 8), -1)  # head
    pts = np.array([
        [px - 60, py - 125],
        [px + 60, py - 125],
        [px + 80, py + 200],
        [px - 80, py + 200],
    ], dtype=np.int32)
    cv2.fillPoly(frame, [pts], (5, 5, 8))
    # Arms
    cv2.rectangle(frame, (px - 90, py - 110), (px - 55, py + 50), (5, 5, 8), -1)
    cv2.rectangle(frame, (px + 55, py - 110), (px + 90, py + 50), (5, 5, 8), -1)

    # Light rays from window
    ray_alpha = ease_in_out(progress)
    for i in range(5):
        angle = -0.3 + i * 0.12
        ox = sun_x
        oy = sun_y
        ex = int(ox - 1500 * math.cos(angle))
        ey = int(oy + 1500 * math.sin(angle))
        overlay = frame.copy()
        cv2.line(overlay, (ox, oy), (ex, ey), (120, 180, 220), 40, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.08 * ray_alpha, frame, 1 - 0.08 * ray_alpha, 0, frame)

    # Dust particles in light
    if progress > 0.3:
        draw_particles(frame, t, 25, (150, 200, 230), 0.4, seed=503)

    apply_color_grade(frame, temp)

    # VO
    if progress < 0.35:
        vo = "Aber was, wenn du gar nicht kämpfen musst?"
    elif progress < 0.75:
        vo = "Was, wenn Zahlen für dich arbeiten – während du schläfst, während du lebst..."
    else:
        vo = "...während du einfach du bist?"
    draw_subtitle(frame, vo, 1.0)


# ============ SCENE 4 (28-45s): The System ============
def scene_system(frame, t, progress):
    """Data viz, algorithm nodes, server room, dashboard."""
    frame[:] = (18, 15, 10)

    section = int(progress * 3)  # 0, 1, 2

    if section == 0:
        # Green upward trending equity curves
        np.random.seed(600)
        for i in range(4):
            points = []
            val = 1000
            for j in range(120):
                val += np.random.uniform(-15, 50) + i * 2
                points.append(val)
            region_y = 200 + i * 180
            color = tuple(int(v * (0.6 + i * 0.1)) for v in GREEN_WIN)
            n_show = int(len(points) * min(1, progress * 4.5))
            if n_show > 1:
                draw_equity_curve(frame, points[:n_show], (120, region_y, 1680, 150), color, 2, True)

    elif section == 1:
        # Algorithm nodes network
        draw_nodes_network(frame, t, (100, 180, 1720, 700), CYAN, 35, seed=700)
        # Flowing data effect
        for i in range(10):
            fx = int((t * 300 + i * 200) % WIDTH)
            fy = int(HEIGHT // 2 + math.sin(t * 2 + i) * 150)
            cv2.circle(frame, (fx, fy), 3, GOLD, -1, cv2.LINE_AA)
            cv2.line(frame, (fx - 50, fy), (fx, fy), GOLD, 1, cv2.LINE_AA)

    else:
        # Clean dashboard with rising portfolio
        # Main chart
        np.random.seed(800)
        points = []
        val = 10000
        for i in range(100):
            val += np.random.uniform(-30, 150)
            points.append(val)
        draw_grid(frame, (120, 180, 1150, 600), (40, 35, 20))
        n_show = int(len(points) * min(1, (progress - 0.66) * 5))
        if n_show > 1:
            draw_equity_curve(frame, points[:n_show], (120, 180, 1150, 600), GREEN_WIN, 3, True)

        # Side stats
        stats_x = 1310
        cv2.rectangle(frame, (stats_x, 180), (1800, 780), (28, 24, 18), -1)
        cv2.rectangle(frame, (stats_x, 180), (1800, 780), (60, 55, 40), 1)

        stats = [
            ("Portfolio", f"{points[-1]:,.0f} USD", GREEN_WIN),
            ("CAR", "24.8%", GOLD),
            ("Win Rate", "68%", GREEN_WIN),
            ("Drawdown", "-8.2%", (120, 150, 200)),
            ("Sharpe", "2.14", GOLD),
            ("Trades", "1,247", WHITE),
        ]
        for i, (label, value, color) in enumerate(stats):
            yy = 230 + i * 92
            cv2.putText(frame, label, (stats_x + 25, yy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150, 140, 110), 1, cv2.LINE_AA)
            cv2.putText(frame, value, (stats_x + 25, yy + 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)
            cv2.line(frame, (stats_x + 20, yy + 60), (1780, yy + 60), (50, 45, 35), 1)

    # Text overlays
    # "LAZY INDEX TRADING" at 30s (progress ~ 0.117)
    if 0.11 < progress < 0.45:
        fade = ease_in_out(min(1, (progress - 0.11) * 8)) * ease_in_out(min(1, (0.45 - progress) * 8))
        draw_text_fade(frame, "LAZY INDEX TRADING", HEIGHT // 2, 2.0, GOLD, 4, fade * 0.85)

    # "Logik statt Bauchgefühl..." at 38s (progress ~ 0.588)
    if 0.55 < progress < 0.85:
        fade = ease_in_out(min(1, (progress - 0.55) * 8)) * ease_in_out(min(1, (0.85 - progress) * 8))
        draw_text_fade(frame, "Logik statt Bauchgefuehl.", HEIGHT // 2 - 40, 1.1, WHITE, 2, fade)
        draw_text_fade(frame, "Daten statt Hoffnung.", HEIGHT // 2 + 20, 1.1, GOLD, 2, fade)

    draw_particles(frame, t, 25, GOLD, 0.5, seed=850)
    apply_color_grade(frame, 0.3)

    # VO
    if progress < 0.17:
        vo = "Willkommen bei Lazy Index Trading."
    elif progress < 0.38:
        vo = "Ein System, das nicht auf Bauchgefuehl setzt, sondern auf Logik."
    elif progress < 0.6:
        vo = "Nicht auf Hoffnung, sondern auf Daten."
    elif progress < 0.85:
        vo = "Algorithmen, die niemals zoegern. Niemals zweifeln. Niemals schlafen."
    else:
        vo = ""
    draw_subtitle(frame, vo, 1.0)


# ============ SCENE 5 (45-60s): The Freedom ============
def scene_freedom(frame, t, progress):
    """Warm, human: family, hike, coffee, sunset."""
    frame[:] = (25, 30, 40)

    section = int(progress * 4)  # 0,1,2,3

    if section == 0:
        # Family at dinner table silhouette
        # Warm wall background
        for y in range(HEIGHT):
            warmth = y / HEIGHT
            c = (int(30 + warmth * 20), int(60 + warmth * 40), int(100 + warmth * 60))
            frame[y, :] = c
        # Table
        cv2.rectangle(frame, (200, HEIGHT - BAR_H - 200), (WIDTH - 200, HEIGHT - BAR_H - 50),
                      (20, 25, 40), -1)
        # Candle/lamp light
        lamp_x, lamp_y = WIDTH // 2, HEIGHT // 2 - 100
        for r in range(300, 0, -4):
            intensity = (1 - r / 300) * 0.9
            c = (int(60 * intensity), int(140 * intensity), int(200 * intensity))
            cv2.circle(frame, (lamp_x, lamp_y), r, c, 2, cv2.LINE_AA)
        # Silhouettes of people around table
        for i, px in enumerate([400, 800, 1200, 1600]):
            py = HEIGHT - BAR_H - 350
            cv2.ellipse(frame, (px, py), (40, 50), 0, 0, 360, (8, 8, 12), -1)
            pts = np.array([
                [px - 55, py + 45], [px + 55, py + 45],
                [px + 75, py + 250], [px - 75, py + 250]
            ], dtype=np.int32)
            cv2.fillPoly(frame, [pts], (8, 8, 12))

    elif section == 1:
        # Hiking at golden hour - mountain silhouette
        # Sky gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(220 * (1 - ratio * 0.5))
            g = int(150 * (1 - ratio * 0.3))
            b = int(70 + ratio * 60)
            frame[y, :] = (b, g, r)

        # Sun
        cv2.circle(frame, (WIDTH // 2 + 200, HEIGHT // 2 - 100), 120, (120, 200, 255), -1)
        cv2.circle(frame, (WIDTH // 2 + 200, HEIGHT // 2 - 100), 180, (90, 170, 230), 3, cv2.LINE_AA)

        # Mountain ridges (back to front)
        for layer, (color, offset) in enumerate([
            ((40, 50, 70), 400),
            ((25, 35, 55), 500),
            ((15, 20, 35), 600),
        ]):
            pts = [[0, HEIGHT]]
            for x in range(0, WIDTH + 50, 50):
                np.random.seed(x + layer * 100)
                y = offset + int(np.random.uniform(-60, 60)) + int(math.sin(x * 0.005) * 80)
                pts.append([x, y])
            pts.append([WIDTH, HEIGHT])
            cv2.fillPoly(frame, [np.array(pts, dtype=np.int32)], color)

        # Hiker silhouette on ridge
        hx = int(WIDTH * 0.3 + progress * 400)
        hy = 570
        cv2.ellipse(frame, (hx, hy - 50), (12, 14), 0, 0, 360, (0, 0, 0), -1)
        cv2.rectangle(frame, (hx - 15, hy - 35), (hx + 15, hy + 30), (0, 0, 0), -1)
        cv2.line(frame, (hx, hy + 30), (hx - 10, hy + 70), (0, 0, 0), 4)
        cv2.line(frame, (hx, hy + 30), (hx + 10, hy + 70), (0, 0, 0), 4)

    elif section == 2:
        # Coffee pour - slow and relaxed
        # Warm kitchen bg
        for y in range(HEIGHT):
            warmth = 1 - (y / HEIGHT) * 0.3
            frame[y, :] = (int(60 * warmth), int(90 * warmth), int(130 * warmth))

        # Table surface
        cv2.rectangle(frame, (0, HEIGHT - 350), (WIDTH, HEIGHT), (25, 40, 70), -1)

        # Coffee cup
        cx, cy = WIDTH // 2, HEIGHT // 2 + 120
        cv2.rectangle(frame, (cx - 150, cy - 100), (cx + 150, cy + 150), (15, 20, 30), -1)
        cv2.rectangle(frame, (cx - 140, cy - 90), (cx + 140, cy + 140), (240, 240, 245), -1)
        # Coffee in cup rising
        fill = int(200 * min(1, (progress * 4) % 1))
        cv2.rectangle(frame, (cx - 140, cy + 140 - fill), (cx + 140, cy + 140), (30, 60, 110), -1)

        # Pour stream from above
        stream_x = cx
        for py_s in range(100, cy - 100, 10):
            wobble = int(math.sin(t * 10 + py_s * 0.05) * 2)
            cv2.line(frame, (stream_x + wobble, py_s), (stream_x + wobble, py_s + 10),
                     (40, 80, 140), 6, cv2.LINE_AA)

        # Steam
        for i in range(10):
            sx = int(cx + math.sin(t * 2 + i * 0.5) * 50)
            sy = int(cy - 100 - i * 25 - (t * 60) % 25)
            r = int(8 + i * 2)
            alpha_v = max(0, 1 - i / 10)
            c = tuple(int(150 * alpha_v) for _ in range(3))
            cv2.circle(frame, (sx, sy), r, c, -1, cv2.LINE_AA)

    else:
        # Couple watching sunset
        # Sky gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(240 - ratio * 100)
            g = int(120 + ratio * 20)
            b = int(60 + ratio * 100)
            frame[y, :] = (b, g, r)

        # Sun on horizon
        horizon_y = int(HEIGHT * 0.6)
        cv2.circle(frame, (WIDTH // 2, horizon_y), 180, (160, 230, 255), -1)

        # Water reflection
        for y in range(horizon_y, HEIGHT):
            ratio = (y - horizon_y) / (HEIGHT - horizon_y)
            r = int(140 * (1 - ratio))
            g = int(90 * (1 - ratio))
            b = int(50 * (1 - ratio))
            wave = int(math.sin(y * 0.3 + t * 2) * 3)
            frame[y, max(0, WIDTH // 2 - 180 + wave):min(WIDTH, WIDTH // 2 + 180 + wave)] = (
                int(200 * (1 - ratio * 0.5)), int(170 * (1 - ratio * 0.3)), r + 50)

        # Ground
        cv2.rectangle(frame, (0, horizon_y + 50), (WIDTH, HEIGHT), (20, 30, 50), -1)

        # Couple silhouette
        cx = WIDTH // 2
        cy = horizon_y - 50
        for offset in [-70, 70]:
            px = cx + offset
            cv2.ellipse(frame, (px, cy - 150), (25, 32), 0, 0, 360, (0, 0, 0), -1)
            pts = np.array([
                [px - 35, cy - 110], [px + 35, cy - 110],
                [px + 50, cy + 200], [px - 50, cy + 200]
            ], dtype=np.int32)
            cv2.fillPoly(frame, [pts], (0, 0, 0))

    # Text overlay at 52s (progress ~ 0.467)
    if 0.42 < progress < 0.75:
        fade = ease_in_out(min(1, (progress - 0.42) * 8)) * ease_in_out(min(1, (0.75 - progress) * 8))
        draw_text_fade(frame, "Kein Panik-Verkauf. Kein FOMO. Nur Freiheit.",
                       120 + BAR_H // 2, 1.0, GOLD, 2, fade)

    draw_particles(frame, t, 20, (180, 220, 255), 0.3, seed=950)
    apply_color_grade(frame, 0.4)

    # VO
    if progress < 0.35:
        vo = "Kein Panik-Verkauf. Kein FOMO. Kein Stress."
    elif progress < 0.75:
        vo = "Nur ein klarer Plan..."
    else:
        vo = "...und die Freiheit, endlich wieder zu leben."
    draw_subtitle(frame, vo, 1.0)


# ============ SCENE 6 (60-72s): The Call ============
def scene_call(frame, t, progress):
    """Trading dashboard hero shot -> CTA screen."""
    frame[:] = (15, 12, 10)

    # First half: hero dashboard
    if progress < 0.5:
        local_p = progress * 2
        # Laptop frame
        lap_x1, lap_y1 = 200, BAR_H + 80
        lap_x2, lap_y2 = WIDTH - 200, HEIGHT - BAR_H - 80
        cv2.rectangle(frame, (lap_x1 - 20, lap_y1 - 20), (lap_x2 + 20, lap_y2 + 20),
                      (30, 30, 35), -1)
        cv2.rectangle(frame, (lap_x1, lap_y1), (lap_x2, lap_y2), (10, 10, 14), -1)
        # Screen glow
        for r in range(60, 0, -2):
            alpha = (1 - r / 60) * 0.03
            overlay = frame.copy()
            cv2.rectangle(overlay, (lap_x1 - r, lap_y1 - r), (lap_x2 + r, lap_y2 + r),
                          GOLD, 2, cv2.LINE_AA)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Dashboard content
        chart_x, chart_y = lap_x1 + 40, lap_y1 + 40
        chart_w, chart_h = (lap_x2 - lap_x1) * 2 // 3 - 40, lap_y2 - lap_y1 - 80
        draw_grid(frame, (chart_x, chart_y, chart_w, chart_h), (35, 30, 20))
        np.random.seed(1100)
        points = []
        val = 10000
        for i in range(80):
            val += np.random.uniform(-20, 180)
            points.append(val)
        n_show = int(len(points) * min(1, local_p * 2))
        if n_show > 1:
            draw_equity_curve(frame, points[:n_show], (chart_x, chart_y, chart_w, chart_h),
                              GREEN_WIN, 3, True)

        # Side panel
        side_x = chart_x + chart_w + 20
        side_w = lap_x2 - side_x - 40
        cv2.rectangle(frame, (side_x, chart_y), (side_x + side_w, chart_y + chart_h),
                      (25, 22, 15), -1)

        panels = [("+24.8%", "YTD Return"), ("1,247", "Algo Trades"), ("68%", "Win Rate")]
        for i, (big, small) in enumerate(panels):
            yy = chart_y + 50 + i * 160
            cv2.putText(frame, big, (side_x + 25, yy + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.4, GOLD, 3, cv2.LINE_AA)
            cv2.putText(frame, small, (side_x + 25, yy + 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 150, 110), 1, cv2.LINE_AA)
            cv2.line(frame, (side_x + 15, yy + 90), (side_x + side_w - 15, yy + 90),
                     (50, 45, 30), 1)

        # Fade out at the end of this half
        if progress > 0.42:
            fade = 1 - ease_in_out((progress - 0.42) * 12.5)
            overlay = np.zeros_like(frame)
            cv2.addWeighted(frame, fade, overlay, 1 - fade, 0, frame)

    else:
        # CTA screen
        local_p = (progress - 0.5) * 2

        # Golden glow background
        cx, cy = WIDTH // 2, HEIGHT // 2
        glow = ease_in_out(min(1, local_p * 2))
        for r in range(600, 0, -8):
            intensity = int(glow * 30 * (1 - r / 600))
            c = (int(intensity * 0.2), int(intensity * 0.6), int(intensity))
            cv2.circle(frame, (cx, cy), r, c, 2, cv2.LINE_AA)

        # "KOSTENLOSER WORKSHOP"
        title_fade = ease_in_out(min(1, local_p * 3))
        draw_text_fade(frame, "KOSTENLOSER WORKSHOP", cy - 30, 2.0, GOLD, 4, title_fade)

        # Subtext
        if local_p > 0.3:
            sub_fade = ease_in_out(min(1, (local_p - 0.3) * 3))
            draw_text_fade(frame, "Entdecke systematisches Trading",
                           cy + 60, 1.0, WHITE, 2, sub_fade)

        # CTA button
        if local_p > 0.55:
            btn_fade = ease_in_out(min(1, (local_p - 0.55) * 3))
            btn_w, btn_h = 400, 90
            bx1, by1 = cx - btn_w // 2, cy + 140
            bx2, by2 = cx + btn_w // 2, cy + 140 + btn_h
            overlay = frame.copy()
            cv2.rectangle(overlay, (bx1, by1), (bx2, by2), GOLD, -1)
            cv2.addWeighted(overlay, btn_fade, frame, 1 - btn_fade, 0, frame)
            cv2.putText(frame, "JETZT ANMELDEN", (bx1 + 35, by1 + 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (10, 10, 10), 2, cv2.LINE_AA)

        draw_particles(frame, t, 30, GOLD, 0.4, seed=1200)

    apply_color_grade(frame, 0.35)

    # VO
    if progress < 0.35:
        vo = "Entdecke, wie echtes systematisches Trading aussieht."
    elif progress < 0.75:
        vo = "Kostenloser Workshop."
    else:
        vo = "Jetzt anmelden."
    draw_subtitle(frame, vo, 1.0)


# ============ SCENE 7 (72-75s): The URL ============
def scene_url(frame, t, progress):
    """Final logo + URL frame."""
    frame[:] = (10, 8, 6)

    cx, cy = WIDTH // 2, HEIGHT // 2

    # Pulsing golden background
    pulse = ease_in_out(min(1, progress * 3))
    for r in range(800, 0, -6):
        intensity = int(pulse * 20 * (1 - r / 800))
        c = (int(intensity * 0.1), int(intensity * 0.5), int(intensity))
        cv2.circle(frame, (cx, cy), r, c, 2, cv2.LINE_AA)

    # Logo text
    logo_fade = ease_in_out(min(1, progress * 2))
    draw_text_fade(frame, "LAZY INDEX TRADING", cy - 60, 2.3, GOLD, 5, logo_fade)

    # Underline
    if progress > 0.2:
        line_p = ease_in_out(min(1, (progress - 0.2) * 3))
        line_w = int(600 * line_p)
        cv2.line(frame, (cx - line_w // 2, cy - 20), (cx + line_w // 2, cy - 20),
                 GOLD, 2, cv2.LINE_AA)

    # URL
    if progress > 0.35:
        url_fade = ease_in_out(min(1, (progress - 0.35) * 3))
        draw_text_fade(frame, "workshop.lazyindextrading.com", cy + 50,
                       1.3, WHITE, 2, url_fade)

    draw_particles(frame, t, 40, GOLD, 0.2, seed=1300)

    # Fade to black at very end
    if progress > 0.85:
        fade_out = ease_in_out((progress - 0.85) / 0.15)
        overlay = np.zeros_like(frame)
        cv2.addWeighted(frame, 1 - fade_out, overlay, fade_out, 0, frame)

    apply_color_grade(frame, 0.3)

    draw_subtitle(frame, "workshop.lazyindextrading.com", 1.0)


# ============ MAIN ============
def generate():
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT, fourcc, FPS, (WIDTH, HEIGHT))
    if not out.isOpened():
        print("Error: Could not open video writer.")
        return

    print(f"Generating {DURATION}s cinematic promo ({TOTAL_FRAMES} frames at {FPS}fps)")
    print(f"Resolution: {WIDTH}x{HEIGHT}")
    print(f"Output: {OUTPUT}\n")

    scenes = [
        (0, 8, scene_struggle, "Scene 1: The Struggle"),
        (8, 18, scene_chaos, "Scene 2: The Chaos"),
        (18, 28, scene_shift, "Scene 3: The Shift"),
        (28, 45, scene_system, "Scene 4: The System"),
        (45, 60, scene_freedom, "Scene 5: The Freedom"),
        (60, 72, scene_call, "Scene 6: The Call"),
        (72, 75, scene_url, "Scene 7: The URL"),
    ]

    last_scene = None
    for frame_num in range(TOTAL_FRAMES):
        t = frame_num / FPS
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        for start, end, fn, name in scenes:
            if start <= t < end:
                if name != last_scene:
                    print(f"  [{t:5.1f}s] {name}")
                    last_scene = name
                progress = (t - start) / (end - start)
                fn(frame, t, progress)
                break

        # Scene transition fades
        for start, end, _, _ in scenes:
            if abs(t - start) < 0.3 and t > 0:
                fade = 1 - min(1, (t - (start - 0.3)) / 0.6)
                overlay = np.zeros_like(frame)
                cv2.addWeighted(frame, 1 - fade * 0.7, overlay, fade * 0.7, 0, frame)

        add_vignette(frame, 0.4)
        frame = add_grain(frame, 10)
        add_letterbox(frame)

        out.write(frame)

        if frame_num % (FPS * 10) == 0 and frame_num > 0:
            pct = frame_num / TOTAL_FRAMES * 100
            print(f"    Progress: {pct:.0f}% ({frame_num}/{TOTAL_FRAMES})")

    out.release()
    size = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"\nDone! {OUTPUT} ({size:.1f} MB)")


if __name__ == "__main__":
    generate()
