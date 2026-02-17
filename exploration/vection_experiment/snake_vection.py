#!/usr/bin/env python3
"""
Vection + target game: first-person movement in darkness with floor dot grid.
User searches for blue target circles, reaches them for points, new target appears.
Uses snake game rules: arena radius, target/beep sounds, colors, practice/fMRI settings.

Controls:
  6 - rotate left
  7 - move forward
  8 - move backward
  9 - rotate right
  Escape - quit
"""

import argparse
import csv
import json
import math
import os
import random
import sys
import time
from datetime import datetime

import pygame

# -----------------------------------------------------------------------------
# Config (vection + snake rules)
# -----------------------------------------------------------------------------
# Arena (from snake_copy, doubled for vection)
ARENA_DIAMETER = 6.6
ARENA_RADIUS = ARENA_DIAMETER / 2.0
BORDER_THRESHOLD = 0.1
# Target: collected when avatar collides (distance < reach radius)
TARGET_REACH_RADIUS = 0.35
TARGET_WORLD_RADIUS = 0.25   # meters, for correct perspective scaling
# Gaze indicator: visual aid only
GAZE_INDICATOR_WIDTH = 0.35   # fraction of screen width
GAZE_INDICATOR_HEIGHT = 0.12  # fraction of screen height
GAZE_INDICATOR_BOTTOM_MARGIN = 0.03  # fraction from bottom
GAZE_INDICATOR_ALPHA = 80     # peak alpha at center (0–255)
GAZE_INDICATOR_COLOR = (220, 225, 240)  # soft spotlight tint

# Vection
EYE_HEIGHT = 1.6
MOVE_SPEED = 2.0
TURN_SPEED = 1.2
GRID_EXTENT = 60
GRID_SPACING = 1.5
DOT_COLOR = (217, 217, 230)
DOT_ALPHA = 165
BACKGROUND_COLOR = (3, 3, 1)  # from snake
FOV_DEG = 90
PITCH_DOWN_DEG = -12  # look slightly down so floor targets are visible (negative = tilt down)
DOT_RADIUS_PX = 3
Z_NEAR = 0.5
Z_FAR = 14
DOTS_VISIBLE_RADIUS = 16
FADE_IN_SPEED = 5.0

# Colors (from snake_copy)
TARGET_COLOR = (0, 217, 192)  # Turquoise
CLOCK_COLOR = (183, 173, 153)
WHITE = (255, 255, 255)

# Debug: top-down arena minimap
DEBUG_MINIMAP = True
DEBUG_MINIMAP_SIZE = 140
DEBUG_MINIMAP_MARGIN = 10

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Vection Target Game')
parser.add_argument('mode', choices=['practice', 'fmri', 'anatomical'],
                    help='Run mode: practice, fmri, or anatomical')
parser.add_argument('--participant', '-p', default='TEST', help='Participant initials')
parser.add_argument('--run', '-r', type=int, default=1, help='Run number for fMRI')
parser.add_argument('--trial', '-t', type=int, default=1, help='Current trial number')
parser.add_argument('--total-trials', '-tt', type=int, default=1, help='Total trials')
parser.add_argument('--screen', '-s', type=int, default=None, help='Screen number')
parser.add_argument('--debug', action='store_true', help='Show debug minimap')
args = parser.parse_args()

MODE = args.mode
player_initials = args.participant
run_number = args.run
current_trial = args.trial
total_trials = args.total_trials
screen_number = args.screen
TR = 2.01
if args.debug:
    DEBUG_MINIMAP = True

# Results
centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
if centralized_results_dir and os.path.exists(centralized_results_dir):
    results_dir = os.path.join(centralized_results_dir, player_initials)
else:
    results_dir = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(results_dir, exist_ok=True)

if MODE == 'fmri':
    run_context = "OT" if run_number == 1 else ("FA" if run_number == 2 else f"run{run_number}")
    continuous_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_vection{current_trial}_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_vection{current_trial}_discrete.csv")
elif MODE == 'anatomical':
    continuous_filename = os.path.join(results_dir, f"{player_initials}_anatomical_vection_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_anatomical_vection_discrete.csv")
else:
    continuous_filename = os.path.join(results_dir, f"{player_initials}_vection_practice_continuous_log.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_vection_practice_discrete_log.csv")

if MODE == 'fmri':
    TRIAL_TRs = random.randint(5, 7)
    TRIAL_DURATION = TRIAL_TRs * TR
elif MODE == 'anatomical':
    TRIAL_DURATION = None
else:
    TRIAL_DURATION = 60.0

# Sounds (from snake_copy)
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
_spotlight_cache = {}  # (w, h) -> Surface


def make_spotlight_surface(width: int, height: int, color: tuple, peak_alpha: int):
    """Create a spotlight-style surface: radial gradient, brightest at center, fade to transparent at edges, no outline."""
    key = (width, height, color, peak_alpha)
    if key in _spotlight_cache:
        return _spotlight_cache[key]
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    cx, cy = width / 2.0, height / 2.0
    for y in range(height):
        for x in range(width):
            dx = (x - cx) / (cx + 1e-6)
            dy = (y - cy) / (cy + 1e-6)
            r = math.sqrt(dx * dx + dy * dy)
            if r >= 1.0:
                alpha = 0
            else:
                alpha = int(peak_alpha * (1.0 - r) ** 1.2)
            s.set_at((x, y), (*color, min(255, alpha)))
    _spotlight_cache[key] = s
    return s


def make_floor_dots(extent: float, spacing: float):
    points = []
    x = -extent
    while x <= extent:
        z = -extent
        while z <= extent:
            points.append((x, 0.0, z))
            z += spacing
        x += spacing
    return points


def world_to_camera(wx, wy, wz, px, py, pz, yaw):
    dx, dy, dz = wx - px, wy - py, wz - pz
    c, s = math.cos(yaw), math.sin(yaw)
    cx = dx * c - dz * s
    cy = dy
    cz = -dx * s - dz * c
    return cx, cy, cz


def project_to_screen(cx, cy, cz, width, height, fov_deg, pitch_deg=0.0):
    """Project camera-space (cx, cy, cz) to screen. pitch_deg tilts view down (positive = look at floor)."""
    if cz <= Z_NEAR or cz > Z_FAR:
        return None
    # Apply pitch: rotate around camera x-axis (tilt view down to see floor)
    if pitch_deg != 0:
        pitch = math.radians(pitch_deg)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cy_new = cy * cp - cz * sp
        cz_new = cy * sp + cz * cp
        cy, cz = cy_new, cz_new
        if cz <= Z_NEAR:
            return None
    fov_rad = math.radians(fov_deg)
    scale = (height / 2.0) / math.tan(fov_rad / 2.0)
    sx = width / 2.0 + (cx / cz) * scale
    sy = height / 2.0 - (cy / cz) * scale
    return sx, sy


def dist_2d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def within_arena(x, z):
    return math.hypot(x, z) <= ARENA_RADIUS


def random_target_in_arena():
    """Random position across the arena: near center, mid-range, or near border."""
    angle = random.uniform(0, 2 * math.pi)
    # Uniform in radius from 20% to 95% of arena - spread targets across full range
    r = ARENA_RADIUS * random.uniform(0.2, 0.95)
    return (r * math.cos(angle), r * math.sin(angle))


def save_continuous_log(logs, filename):
    """Save continuous log to CSV file (as in snake_copy)."""
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    fieldnames = ["RealTime", "trial_time", "trial", "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y"]
    try:
        with open(filename, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in logs:
                filtered = {k: v for k, v in row.items() if k in fieldnames}
                w.writerow(filtered)
        print(f"Continuous log saved successfully to: {filename}")
    except Exception as e:
        print(f"Error saving continuous log: {e}")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = filename.replace('.csv', f'_backup_{ts}.csv')
        try:
            with open(backup, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for row in logs:
                    filtered = {k: v for k, v in row.items() if k in fieldnames}
                    w.writerow(filtered)
            print(f"Continuous log saved as backup to: {backup}")
        except Exception as e2:
            print(f"Failed to save backup: {e2}")


def save_discrete_log(logs, filename):
    """Save discrete log to CSV file (as in snake_copy)."""
    base = filename.replace('.csv', '')
    final = filename
    n = 1
    while os.path.exists(final):
        final = f"{base}_{n}.csv"
        n += 1
    fieldnames = ["trial", "final_score", "trial_duration", "target_locations", "target_reach_times", "game_duration"]
    try:
        with open(final, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for log in logs:
                w.writerow(log)
        print(f"Discrete log saved successfully to: {final}")
    except Exception as e:
        print(f"Error saving discrete log: {e}")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"{base}_backup_{ts}.csv"
        try:
            with open(backup, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                for log in logs:
                    w.writerow(log)
            print(f"Discrete log saved as backup to: {backup}")
        except Exception as e2:
            print(f"Failed to save backup: {e2}")


INSTRUCTIONS_DIR = os.path.join(os.path.dirname(__file__), "Instructions-he")


def show_fixation(screen, duration, clock):
    """Display fixation cross for duration (seconds)."""
    font = pygame.font.SysFont("Arial", 200)
    cross = font.render('+', True, WHITE)
    rect = cross.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    start = time.time()
    while time.time() - start < duration:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return False
        screen.fill(BACKGROUND_COLOR)
        screen.blit(cross, rect)
        pygame.display.flip()
        clock.tick(60)
    return True


def show_instruction(screen, path, duration, clock):
    """Show instruction image for duration. Skips if file missing."""
    if not os.path.exists(path):
        return True
    try:
        img = pygame.image.load(path)
        # Scale to fit
        sw, sh = screen.get_size()
        iw, ih = img.get_size()
        scale = min(sw / iw, sh / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        img = pygame.transform.scale(img, (nw, nh))
        rect = img.get_rect(center=(sw // 2, sh // 2))
    except Exception:
        return True
    start = time.time()
    while time.time() - start < duration:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return False
        screen.fill(BACKGROUND_COLOR)
        screen.blit(img, rect)
        pygame.display.flip()
        clock.tick(60)
    return True


# -----------------------------------------------------------------------------
# Main game
# -----------------------------------------------------------------------------
def _make_beep_sound():
    """Generate a simple beep if file fails to load (e.g. sounds/ not present)."""
    try:
        import numpy as np
        init = pygame.mixer.get_init()
        if init is None:
            return None
        sr, fmt, chans = init  # e.g. 44100, -16, 2
        duration = 0.15
        n = int(sr * duration)
        t = np.linspace(0, duration, n, False)
        tone = (np.sin(2 * np.pi * 440 * t) * 0.3 * 32767).astype(np.int16)
        stereo = np.column_stack([tone, tone])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


def run_game():
    pygame.init()

    # Audio first (as in snake_copy - before display)
    pygame.mixer.quit()
    audio_devices_to_try = [
        "Outside (NVIDIA High Definition Audio)",
        "Speakers (NVIDIA High Definition Audio)",
        "Headphones (NVIDIA High Definition Audio)",
        "Default Audio Device",
        None,
    ]
    audio_initialized = False
    selected_device = None
    for device in audio_devices_to_try:
        try:
            if device:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512, devicename=device)
                print(f"Audio mixer initialized with device: {device}")
            else:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                print("Audio mixer initialized with system default")
            audio_initialized = True
            selected_device = device
            break
        except Exception as e:
            print(f"Warning: Could not use device '{device}': {e}")
            continue
    if not audio_initialized:
        pygame.mixer.init()

    beep_sound = None
    target_sound = None
    try:
        beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
        beep_sound.set_volume(0.8)
        print("Beep sound loaded successfully")
    except Exception as e:
        print(f"Error loading beep sound: {e}, using fallback tone")
        beep_sound = _make_beep_sound()
        if beep_sound:
            beep_sound.set_volume(0.8)
    try:
        target_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)
        target_sound.set_volume(1.0)
        print("Target sound loaded successfully")
    except Exception as e:
        print(f"Error loading target sound: {e}")

    try:
        pygame.mixer.set_reserved(2)
        beep_channel = pygame.mixer.Channel(0)
        target_channel = pygame.mixer.Channel(1)
        print(f"Audio channels reserved (device: {selected_device or 'System Default'})")
    except Exception as e:
        print(f"Warning: Could not reserve audio channels: {e}")
        beep_channel = None
        target_channel = None

    width, height = 1280, 720
    if screen_number is not None:
        try:
            display_count = pygame.display.get_num_displays()
            if 0 <= screen_number < display_count:
                os.environ['SDL_VIDEO_FULLSCREEN_DISPLAY'] = str(screen_number)
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except Exception:
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    pygame.display.set_caption("Vection Target — 6: left | 7: forward | 8: back | 9: right")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # Pre-game: fMRI fixation + instruction (with logging), or practice instruction
    fixation_logs = []
    if MODE == 'fmri':
        trial_info_log = str(run_number)
        # Trigger log if env set
        trigger_time = os.getenv('TRIGGER_RECEIVED_TIME')
        if trigger_time:
            fixation_logs.append({
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": 0.0,
                "trial": trial_info_log,
                "phase": "trigger",
                "event": "trigger_received",
                "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": 0,
                "target_x": 0.0, "target_y": 0.0,
            })
        fixation_trs = 8 if current_trial == 1 else 4
        fixation_logs.append({
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": 0.0, "trial": trial_info_log, "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": 0,
            "target_x": 0.0, "target_y": 0.0,
        })
        if not show_fixation(screen, fixation_trs * TR, clock):
            pygame.quit()
            return
        fixation_logs.append({
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": fixation_trs * TR, "trial": trial_info_log, "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": 0,
            "target_x": 0.0, "target_y": 0.0,
        })
        if not show_instruction(screen, os.path.join(INSTRUCTIONS_DIR, "2.png"), TR, clock):
            pygame.quit()
            return
    elif MODE == 'practice':
        # Practice: show instruction, wait for key
        inst_path = os.path.join(INSTRUCTIONS_DIR, "1.png")
        if os.path.exists(inst_path):
            try:
                img = pygame.image.load(inst_path)
                sw, sh = screen.get_size()
                iw, ih = img.get_size()
                scale = min(sw / iw, sh / ih)
                img = pygame.transform.scale(img, (int(iw * scale), int(ih * scale)))
                rect = img.get_rect(center=(sw // 2, sh // 2))
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                            pygame.quit()
                            return
                        if e.type == pygame.KEYDOWN and e.key in (pygame.K_1, pygame.K_RETURN):
                            waiting = False
                    screen.fill(BACKGROUND_COLOR)
                    screen.blit(img, rect)
                    pygame.display.flip()
                    clock.tick(60)
            except Exception:
                pass

    dots = make_floor_dots(GRID_EXTENT, GRID_SPACING)
    px, py, pz = 0.0, EYE_HEIGHT, 0.0
    yaw = 0.0
    keys_held = set()
    clock = pygame.time.Clock()
    fade_factor = 0.0

    target_xz = random_target_in_arena()
    score = 0
    target_locations = []
    target_reach_times = []
    continuous_log = []
    game_start = time.time()
    running = True
    trial_info = str(run_number) if MODE == 'fmri' else ("anatomical" if MODE == 'anatomical' else "practice")

    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time() - game_start

        # Log (snake-compatible: x, y=z, rotation_angle=yaw, target_x, target_y=tz)
        entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": round(current_time, 3),
            "trial": trial_info,
            "phase": "gameplay",
            "event": None,
            "x": round(px, 3),
            "y": round(pz, 3),
            "rotation_angle": round(yaw, 3),
            "score": score,
            "target_x": round(target_xz[0], 3),
            "target_y": round(target_xz[1], 3),
        }
        continuous_log.append(entry)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                else:
                    keys_held.add(e.key)
            elif e.type == pygame.KEYUP:
                keys_held.discard(e.key)

        forward_x = -math.sin(yaw)
        forward_z = -math.cos(yaw)

        if pygame.K_7 in keys_held or pygame.K_KP7 in keys_held:
            new_px = px + forward_x * MOVE_SPEED * dt
            new_pz = pz + forward_z * MOVE_SPEED * dt
            if within_arena(new_px, new_pz):
                px, pz = new_px, new_pz
        if pygame.K_8 in keys_held or pygame.K_KP8 in keys_held:
            new_px = px - forward_x * MOVE_SPEED * dt
            new_pz = pz - forward_z * MOVE_SPEED * dt
            if within_arena(new_px, new_pz):
                px, pz = new_px, new_pz
        if pygame.K_6 in keys_held or pygame.K_KP6 in keys_held:
            yaw += TURN_SPEED * dt
        if pygame.K_9 in keys_held or pygame.K_KP9 in keys_held:
            yaw -= TURN_SPEED * dt

        # Clamp to arena
        dist_from_center = math.hypot(px, pz)
        if dist_from_center > ARENA_RADIUS:
            scale = ARENA_RADIUS / dist_from_center
            px *= scale
            pz *= scale

        # Border beep (as in snake_copy)
        if dist_from_center >= (ARENA_RADIUS - BORDER_THRESHOLD):
            if beep_sound is not None and beep_channel is not None:
                if not beep_channel.get_busy():
                    beep_channel.play(beep_sound, loops=-1)
        else:
            if beep_channel is not None and beep_channel.get_busy():
                beep_channel.stop()

        # Draw
        screen.fill(BACKGROUND_COLOR)
        w, h = screen.get_size()

        # Gaze indicator rect (bottom center)
        gi_w = int(w * GAZE_INDICATOR_WIDTH)
        gi_h = int(h * GAZE_INDICATOR_HEIGHT)
        gi_bottom = h - int(h * GAZE_INDICATOR_BOTTOM_MARGIN)
        gaze_rect = pygame.Rect(w // 2 - gi_w // 2, gi_bottom - gi_h, gi_w, gi_h)

        # Target: project for rendering; collect on avatar collision (aligned in both views)
        tx, tz = target_xz
        t_cx, t_cy, t_cz = world_to_camera(tx, 0.0, tz, px, py, pz, yaw)
        target_pt = project_to_screen(t_cx, t_cy, t_cz, w, h, FOV_DEG, PITCH_DOWN_DEG)

        # Collect when avatar collides with target (distance-based, same logic in both views)
        if dist_2d((px, pz), (tx, tz)) < TARGET_REACH_RADIUS:
            score += 1
            target_locations.append([round(target_xz[0], 3), round(target_xz[1], 3)])
            target_reach_times.append(round(current_time, 3))
            continuous_log.append({
                **entry,
                "event": "target_reached",
                "score": score,
            })
            target_xz = random_target_in_arena()
            if target_sound is not None and target_channel is not None:
                target_channel.play(target_sound)
            elif target_sound is not None:
                target_sound.play()

        moving = any(k in keys_held for k in [
            pygame.K_6, pygame.K_KP6, pygame.K_7, pygame.K_KP7,
            pygame.K_8, pygame.K_KP8, pygame.K_9, pygame.K_KP9
        ])
        if moving:
            fade_factor = min(1.0, fade_factor + FADE_IN_SPEED * dt)

        if fade_factor > 0.01:
            alpha = int(DOT_ALPHA * fade_factor)
            dot_color_rgba = (*DOT_COLOR, alpha)
            layer = pygame.Surface((w, h), pygame.SRCALPHA)
            radius_sq = DOTS_VISIBLE_RADIUS * DOTS_VISIBLE_RADIUS
            for (wx, wy, wz) in dots:
                if (wx - px) ** 2 + (wz - pz) ** 2 > radius_sq:
                    continue
                cx, cy, cz = world_to_camera(wx, wy, wz, px, py, pz, yaw)
                pt = project_to_screen(cx, cy, cz, w, h, FOV_DEG, PITCH_DOWN_DEG)
                if pt:
                    sx, sy = int(pt[0]), int(pt[1])
                    if 0 <= sx < w and 0 <= sy < h:
                        pygame.draw.circle(layer, dot_color_rgba, (sx, sy), DOT_RADIUS_PX)
            screen.blit(layer, (0, 0))

        # Target (turquoise circle on floor) - perspective-correct size (further = smaller)
        if target_pt is not None and t_cz > Z_NEAR:
            sx, sy = int(target_pt[0]), int(target_pt[1])
            fov_rad = math.radians(FOV_DEG)
            scale = (h / 2.0) / math.tan(fov_rad / 2.0)
            radius_px = max(4, int(TARGET_WORLD_RADIUS * scale / t_cz))
            if 0 <= sx < w and 0 <= sy < h:
                pygame.draw.circle(screen, TARGET_COLOR, (sx, sy), radius_px)

        # Spotlight gaze indicator at bottom center (no outline)
        gaze_layer = make_spotlight_surface(gi_w, gi_h, GAZE_INDICATOR_COLOR, GAZE_INDICATOR_ALPHA)
        screen.blit(gaze_layer, gaze_rect.topleft)

        # Debug: top-down arena minimap
        if DEBUG_MINIMAP:
            map_sz = DEBUG_MINIMAP_SIZE
            map_margin = DEBUG_MINIMAP_MARGIN
            map_x = w - map_sz - map_margin
            map_y = map_margin
            map_cx = map_x + map_sz // 2
            map_cy = map_y + map_sz // 2
            map_radius = (map_sz // 2) - 4
            # Backdrop
            map_surf = pygame.Surface((map_sz, map_sz), pygame.SRCALPHA)
            map_surf.fill((0, 0, 0, 100))
            pygame.draw.circle(map_surf, (80, 80, 90, 180), (map_sz // 2, map_sz // 2), map_radius)
            pygame.draw.circle(map_surf, (120, 120, 130), (map_sz // 2, map_sz // 2), map_radius, 1)
            screen.blit(map_surf, (map_x, map_y))
            # World to minimap: (px, pz) in [-ARENA_RADIUS, ARENA_RADIUS] -> map coords
            def to_map(x, z):
                sx = map_cx + int((x / ARENA_RADIUS) * map_radius)
                sy = map_cy - int((z / ARENA_RADIUS) * map_radius)  # -z up (forward)
                return sx, sy
            # Target (radius = reach zone, so collision in minimap matches first-person)
            tmx, tmz = to_map(target_xz[0], target_xz[1])
            tr = max(2, int((TARGET_REACH_RADIUS / ARENA_RADIUS) * map_radius))
            pygame.draw.circle(screen, TARGET_COLOR, (tmx, tmz), tr)
            # User (with heading)
            umx, umz = to_map(px, pz)
            pygame.draw.circle(screen, (255, 80, 100), (umx, umz), 4)
            # User forward direction (forward = -sin(yaw), -cos(yaw) in x,z)
            fx = umx - int(math.sin(yaw) * 12)
            fz = umz + int(math.cos(yaw) * 12)
            pygame.draw.line(screen, (255, 120, 140), (umx, umz), (fx, fz), 2)

        # Score & timer
        font = pygame.font.SysFont("Arial", 36)
        score_text = font.render(f"Score: {score}", True, CLOCK_COLOR)
        screen.blit(score_text, (10, 10))
        if TRIAL_DURATION is not None:
            remaining = max(0, TRIAL_DURATION - current_time)
            timer_text = font.render(f"{int(remaining // 60):02d}:{int(remaining % 60):02d}", True, CLOCK_COLOR)
            screen.blit(timer_text, (10, 50))

        if MODE == 'fmri':
            cf = pygame.font.SysFont("Arial", 24)
            cf_surf = cf.render(f"{current_trial}/{total_trials}", True, WHITE)
            cf_rect = cf_surf.get_rect(bottomright=(w - 20, h - 20))
            screen.blit(cf_surf, cf_rect)

        pygame.display.flip()

        if TRIAL_DURATION is not None and current_time >= TRIAL_DURATION:
            running = False

    if beep_channel is not None:
        beep_channel.stop()
    if target_channel is not None:
        target_channel.stop()

    game_duration = time.time() - game_start

    # Post-game: fMRI end fixation (with logging), practice final instruction
    end_fixation_logs = []
    if MODE == 'fmri':
        end_fixation_logs.append({
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": game_duration, "trial": trial_info, "phase": "fixation",
            "event": "end_fixation_start",
            "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": score,
            "target_x": 0.0, "target_y": 0.0,
        })
        show_fixation(screen, 4 * TR, clock)
        end_fixation_logs.append({
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": game_duration + 4 * TR, "trial": trial_info, "phase": "fixation",
            "event": "end_fixation_end",
            "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": score,
            "target_x": 0.0, "target_y": 0.0,
        })
    elif MODE == 'practice':
        inst_path = os.path.join(INSTRUCTIONS_DIR, "10.png")
        if os.path.exists(inst_path):
            try:
                img = pygame.image.load(inst_path)
                sw, sh = screen.get_size()
                iw, ih = img.get_size()
                scale = min(sw / iw, sh / ih)
                img = pygame.transform.scale(img, (int(iw * scale), int(ih * scale)))
                rect = img.get_rect(center=(sw // 2, sh // 2))
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                            waiting = False
                            break
                        if e.type == pygame.KEYDOWN and e.key in (pygame.K_1, pygame.K_RETURN):
                            waiting = False
                    screen.fill(BACKGROUND_COLOR)
                    screen.blit(img, rect)
                    pygame.display.flip()
                    clock.tick(60)
            except Exception:
                pass

    # Combine logs: fixation + gameplay + end fixation (as in snake_copy)
    full_continuous_log = fixation_logs + continuous_log + end_fixation_logs
    save_continuous_log(full_continuous_log, continuous_filename)
    save_discrete_log([{
        "trial": trial_info,
        "final_score": score,
        "trial_duration": TRIAL_DURATION if TRIAL_DURATION else "endless",
        "target_locations": json.dumps(target_locations),
        "target_reach_times": json.dumps(target_reach_times),
        "game_duration": round(game_duration, 2),
    }], discrete_filename)

    pygame.quit()
    print(f"Vection target game complete. Score: {score}. Data: {continuous_filename}")


if __name__ == "__main__":
    print(f"Mode: {MODE}, Participant: {player_initials}")
    if TRIAL_DURATION:
        print(f"Trial duration: {TRIAL_DURATION}s")
    else:
        print("Trial duration: endless (anatomical)")
    run_game()
    sys.exit(0)
