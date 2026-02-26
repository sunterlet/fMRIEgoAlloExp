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

# Optional exploration_trigger modules (for scanner-ready features)
try:
    from fixation_utils import show_fixation_image
except ImportError:
    show_fixation_image = None
try:
    from trigger_utils import TriggerManager
except ImportError:
    TriggerManager = None
try:
    from sound_paths import SOUNDS_DIR, BEEP_SOUND_PATH, TARGET_SOUND_PATH
except ImportError:
    SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
    BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")
    TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
# Unified display config (snake_vection + one_target_vection)
from vection_display_config import (
    GAME_WIDTH, GAME_HEIGHT, DISPLAY_SCALE, FULLSCREEN_BACKGROUND, prepare_fullscreen_display, setup_vection_display,
    ARENA_DIAMETER, ARENA_RADIUS, BORDER_THRESHOLD,
    EYE_HEIGHT, GRID_EXTENT, GRID_SPACING, DOT_COLOR, DOT_ALPHA, DOT_RADIUS_PX,
    FOV_DEG, PITCH_DOWN_DEG, Z_NEAR, Z_FAR, DOTS_VISIBLE_RADIUS, FADE_IN_SPEED,
    TARGET_WORLD_RADIUS, GAZE_INDICATOR_WIDTH, GAZE_INDICATOR_HEIGHT,
    GAZE_INDICATOR_BOTTOM_MARGIN, GAZE_INDICATOR_ALPHA, GAZE_INDICATOR_COLOR,
    DEBUG_MINIMAP_SIZE, DEBUG_MINIMAP_MARGIN, DEBUG_MINIMAP_BG_COLOR,
    DEBUG_MINIMAP_GRID_COLOR, DEBUG_MINIMAP_AVATAR_COLOR,
    DEBUG_MINIMAP_AVATAR_HEADING_COLOR, DEBUG_MINIMAP_ARENA_BORDER_COLOR,
    BACKGROUND_COLOR, TARGET_COLOR, CLOCK_COLOR, WHITE,
    FONT_SIZE_SCORE, FONT_SIZE_COUNTER,
)

# Snake-specific
TARGET_REACH_RADIUS = 0.35   # used for minimap target circle size
AVATAR_TIP_OFFSET = 0.2     # world-space distance from avatar center to "tip" (forward) for collection
TARGET_MIN_DISTANCE = 1.2
MOVE_SPEED = 2.0
TURN_SPEED = 1.2
DEBUG_MINIMAP = True
DEBUG_MINIMAP_WORLD_RADIUS = max(ARENA_RADIUS * 1.5, 5)

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Vection Target Game')
parser.add_argument('mode', choices=['practice', 'fmri', 'shimming'],
                    help='Run mode: practice, fmri, or shimming (endless practice during shimming)')
parser.add_argument('--participant', '-p', default='TEST', help='Participant initials')
parser.add_argument('--run', '-r', type=int, default=1, help='Run number for fMRI')
parser.add_argument('--trial', '-t', type=int, default=1, help='Current trial number')
parser.add_argument('--total-trials', '-tt', type=int, default=1, help='Total trials')
parser.add_argument('--screen', '-s', type=int, default=None, help='Screen number')
parser.add_argument('--mt-run', '-mtr', type=int, default=None, help='Multi target run identifier for logging')
parser.add_argument('--snake-trial', '-st', type=int, default=None, help='Snake-specific trial number for display')
parser.add_argument('--scanning', action='store_true', help='Enable trigger functionality for fMRI scanning')
parser.add_argument('--com', type=str, default='com4', help='Serial port for trigger')
parser.add_argument('--tr', type=float, default=2.01, help='TR in seconds')
parser.add_argument('--debug', action='store_true', help='Show debug minimap')
args = parser.parse_args()

MODE = args.mode
player_initials = args.participant
run_number = args.run
current_trial = args.trial
total_trials = args.total_trials
screen_number = args.screen
mt_run_number = args.mt_run
scanning = args.scanning
com_port = args.com
TR = args.tr
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
    if mt_run_number is not None:
        run_context = f"MT{mt_run_number}V"
    elif run_number == 1:
        run_context = "OTV"
    elif run_number == 2:
        run_context = "MTV"
    else:
        run_context = f"run{run_number}V"
    continuous_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_snake{current_trial}_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_snake{current_trial}_discrete.csv")
elif MODE == 'shimming':
    continuous_filename = os.path.join(results_dir, f"{player_initials}_shimming_snake_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_shimming_snake_discrete.csv")
else:
    continuous_filename = os.path.join(results_dir, f"{player_initials}_snake_practice_continuous_log.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_snake_practice_discrete_log.csv")

if MODE == 'fmri':
    TRIAL_TRs = random.randint(5, 7)
    TRIAL_DURATION = TRIAL_TRs * TR
elif MODE == 'shimming':
    TRIAL_DURATION = None
else:
    TRIAL_DURATION = 90.0  # practice: 90 s

# Sounds: from sound_paths (exploration_trigger) or local fallback


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


def world_to_minimap(wx, wz, px, pz, map_size, world_radius):
    """Convert world (x,z) to minimap pixel - avatar-centered (arena moves). Used for dots."""
    scale = map_size / (2.0 * world_radius)
    mx = map_size / 2.0 + (wx - px) * scale
    my = map_size / 2.0 + (wz - pz) * scale
    return mx, my


def world_to_minimap_arena_fixed(wx, wz, map_sz, map_radius):
    """Convert world (x,z) to minimap pixel - arena fixed at center, avatar moves within it. +x right, -z up (forward)."""
    map_cx = map_sz / 2.0
    map_cy = map_sz / 2.0
    scale = map_radius / ARENA_RADIUS
    mx = map_cx + wx * scale
    my = map_cy + wz * scale  # +z down, -z up (forward = north = up on minimap)
    return mx, my


def world_to_camera(wx, wy, wz, px, py, pz, yaw):
    """Transform world coords to camera space. Same as run_vection_pygame."""
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


def random_target_in_arena_min_dist(px, pz, min_dist=TARGET_MIN_DISTANCE):
    """Random target position at least min_dist meters from (px, pz)."""
    for _ in range(50):
        cand = random_target_in_arena()
        if dist_2d((px, pz), cand) >= min_dist:
            return cand
    return random_target_in_arena()  # fallback if no valid position found


CONTINUOUS_LOG_FIELDS = [
    "RealTime", "trial_time", "trial", "trial_type", "RoundName", "condition_type", "visibility",
    "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y", "trigger_received_time"
]


def log_error_to_continuous_log(continuous_log, error_message, trial_number=None, trial_info=None):
    """Log an error message to the continuous log before exiting."""
    entry = {
        "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
        "trial_time": 0.0,
        "trial": trial_number if trial_number is not None else "N/A",
        "trial_type": "error",
        "RoundName": trial_info if trial_info else "error",
        "condition_type": "error",
        "visibility": "none",
        "phase": "error",
        "event": f"ERROR: {error_message}",
        "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": 0,
        "target_x": 0.0, "target_y": 0.0,
    }
    continuous_log.append(entry)
    print(f"ERROR LOGGED: {error_message} (trial: {trial_number})")


def save_continuous_log(logs, filename):
    """Save continuous log to CSV file (exploration_trigger compatible)."""
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    fieldnames = CONTINUOUS_LOG_FIELDS
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
        screen.fill(FULLSCREEN_BACKGROUND)
        screen.blit(cross, rect)
        pygame.display.flip()
        clock.tick(60)
    return True


def show_instruction(screen, path, duration, clock):
    """Show instruction image at original size, centered. Skips if file missing."""
    if not os.path.exists(path):
        return True
    try:
        img = pygame.image.load(path)
        sw, sh = screen.get_size()
        iw, ih = img.get_size()
        rect = img.get_rect(center=(sw // 2, sh // 2))
    except Exception:
        return True
    start = time.time()
    while time.time() - start < duration:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_k:
                print("Instruction skipped by K key")
                return True
        screen.fill(FULLSCREEN_BACKGROUND)
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
    prepare_fullscreen_display(screen_number)  # Must be before pygame.init()
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
        beep_sound.set_volume(1.0)
        print("Beep sound loaded successfully")
    except Exception as e:
        print(f"Error loading beep sound: {e}, using fallback tone")
        beep_sound = _make_beep_sound()
        if beep_sound:
            beep_sound.set_volume(1.0)
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

    # Unified display setup: one screen, NOFRAME (avoids both-screens-black)
    screen, screen_width, screen_height = setup_vection_display(screen_number)

    pygame.display.set_caption("Vection Target — 6: left | 7: forward | 8: back | 9: right")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # 75% display area, centered, base resolution 1000x800 (unified with one_target_vection)
    max_display_w = int(screen_width * DISPLAY_SCALE)
    max_display_h = int(screen_height * DISPLAY_SCALE)
    scale_w = max_display_w / GAME_WIDTH
    scale_h = max_display_h / GAME_HEIGHT
    scale = min(scale_w, scale_h)
    display_w = int(GAME_WIDTH * scale)
    display_h = int(GAME_HEIGHT * scale)
    display_offset_x = (screen_width - display_w) // 2
    display_offset_y = (screen_height - display_h) // 2
    game_surface_main = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

    # Initialize logging early for error handling
    continuous_log = []
    fixation_logs = []

    # Trigger manager (exploration_trigger)
    trigger_manager = None
    trigger_time_value = None
    if TriggerManager is not None and scanning:
        trigger_manager = TriggerManager(scanning=scanning, com_port=com_port)
        if not trigger_manager.init_trigger():
            error_msg = "Failed to initialize trigger connection"
            print(f"CRITICAL: {error_msg}. Exiting.")
            log_error_to_continuous_log(continuous_log, error_msg, current_trial, f"snake_trial{current_trial}")
            try:
                save_continuous_log(continuous_log, continuous_filename)
            except Exception as e:
                print(f"Warning: Could not save error log: {e}")
            trigger_manager.close_trigger()
            pygame.quit()
            return

    # Pre-game: fMRI fixation + instruction (with logging), or practice instruction
    trial_info_log = str(current_trial) if MODE == 'fmri' else ("shimming" if MODE == 'shimming' else "practice")
    if MODE == 'fmri':
        # Wait for scanner trigger when scanning
        if scanning and trigger_manager is not None:
            trigger_timeout = 60.0 if current_trial == 1 else 40.0
            print(f'Waiting for scanner trigger before trial {current_trial} (timeout: {trigger_timeout:.0f}s)...')
            success, trigger_time = trigger_manager.wait_for_trigger(timeout=trigger_timeout)
            if not success:
                error_msg = f"Failed to receive trigger within {trigger_timeout:.0f}s (trial {current_trial})"
                print(f"CRITICAL: {error_msg}. Exiting.")
                log_error_to_continuous_log(continuous_log, error_msg, current_trial, f"snake_trial{current_trial}")
                try:
                    save_continuous_log(continuous_log, continuous_filename)
                except Exception as e:
                    print(f"Warning: Could not save error log: {e}")
                trigger_manager.close_trigger()
                pygame.quit()
                return
            trigger_time_value = trigger_time
            print(f"Trigger received at time: {trigger_time_value:.3f}s")
        else:
            trigger_time_value = os.getenv('TRIGGER_RECEIVED_TIME')
            if trigger_time_value is not None:
                trigger_time_value = float(trigger_time_value)

        if trigger_time_value is not None:
            fixation_logs.append({
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": 0.0, "trial": str(current_trial), "trial_type": "snake",
                "RoundName": trial_info_log, "condition_type": "trigger", "visibility": "none",
                "phase": "trigger", "event": "trigger_received",
                "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": 0,
                "target_x": 0.0, "target_y": 0.0, "trigger_received_time": trigger_time_value,
            })

        if scanning:
            fixation_trs = 8 if current_trial == 1 else 4
            fixation_duration = fixation_trs * TR
            if show_fixation_image is not None:
                game_surface = pygame.Surface(screen.get_size())
                show_fixation_image(screen, game_surface, 0, 0, fixation_duration,
                                   "white_on_black", fixation_logs, current_trial, trial_info_log, FULLSCREEN_BACKGROUND)
            else:
                fixation_logs.append({
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": 0.0, "trial": str(current_trial), "trial_type": "snake",
                    "RoundName": trial_info_log, "condition_type": "fixation", "visibility": "none",
                    "phase": "fixation", "event": "fixation_start",
                    "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": 0,
                    "target_x": 0.0, "target_y": 0.0,
                })
                if not show_fixation(screen, fixation_duration, clock):
                    pygame.quit()
                    return
                fixation_logs.append({
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": fixation_duration, "trial": str(current_trial), "trial_type": "snake",
                    "RoundName": trial_info_log, "condition_type": "fixation", "visibility": "none",
                    "phase": "fixation", "event": "fixation_end",
                    "x": 0.0, "y": 0.0, "rotation_angle": 0.0, "score": 0,
                    "target_x": 0.0, "target_y": 0.0,
                })
        else:
            print('Skipping fixation (not scanning).')
        # Show snake instruction screen for 1 TR before trial (same logic as one_target_vection OT-screen.png)
        if not show_instruction(screen, os.path.join(INSTRUCTIONS_DIR, "snake-screen.png"), TR, clock):
            pygame.quit()
            return
    elif MODE == 'practice':
        # Practice: show snake instructions (snake-ins.png) before trial
        snake_instructions_dir = os.path.join(os.path.dirname(__file__), "Instructions-he")
        inst_path = os.path.join(snake_instructions_dir, "snake-ins.png")
        if os.path.exists(inst_path):
            try:
                img = pygame.image.load(inst_path)
                sw, sh = screen.get_size()
                rect = img.get_rect(center=(sw // 2, sh // 2))
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                            pygame.quit()
                            return
                        if e.type == pygame.KEYDOWN and e.key in (pygame.K_1, pygame.K_RETURN):
                            waiting = False
                        if e.type == pygame.KEYDOWN and e.key == pygame.K_k:
                            print("Instruction skipped by K key")
                            waiting = False
                    screen.fill(FULLSCREEN_BACKGROUND)
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

    target_xz = random_target_in_arena_min_dist(px, pz)
    score = 0
    target_locations = []
    target_reach_times = []
    game_start = time.time()
    running = True
    trial_info = str(current_trial) if MODE == 'fmri' else ("shimming" if MODE == 'shimming' else "practice")
    # Practice: minimap on for first 30 s then auto-hide; B still toggles. fMRI/shimming: minimap off until B
    PRACTICE_MINIMAP_DURATION = 30.0
    show_debug_minimap = (MODE == 'practice')
    minimap_auto_hidden = False
    target_was_in_view = False

    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time() - game_start
        if MODE == 'practice' and not minimap_auto_hidden and current_time >= PRACTICE_MINIMAP_DURATION:
            show_debug_minimap = False
            minimap_auto_hidden = True

        # Log (exploration_trigger compatible: trial_type, RoundName, condition_type, visibility)
        entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": round(current_time, 3),
            "trial": trial_info,
            "trial_type": "snake",
            "RoundName": trial_info,
            "condition_type": "gameplay",
            "visibility": "none",
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
                elif e.key == pygame.K_k:
                    running = False
                elif e.key == pygame.K_b:
                    show_debug_minimap = not show_debug_minimap
                else:
                    keys_held.add(e.key)
            elif e.type == pygame.KEYUP:
                keys_held.discard(e.key)

        # Movement logic: match run_vection_pygame exactly
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
            yaw += TURN_SPEED * dt  # 6: rotate left (match run_vection: avatar ccw, dots cw)
        if pygame.K_9 in keys_held or pygame.K_KP9 in keys_held:
            yaw -= TURN_SPEED * dt  # 9: rotate right (match run_vection: avatar cw, dots ccw)

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

        # Draw to game surface (1000x800 base resolution)
        game_surface_main.fill(BACKGROUND_COLOR)
        w, h = GAME_WIDTH, GAME_HEIGHT

        # Spotlight at bottom center = egocentric gaze; avatar position (px, pz) drives both 3D view and minimap
        gi_w = int(w * GAZE_INDICATOR_WIDTH)
        gi_h = int(h * GAZE_INDICATOR_HEIGHT)
        gi_bottom = h - int(h * GAZE_INDICATOR_BOTTOM_MARGIN)
        gaze_rect = pygame.Rect(w // 2 - gi_w // 2, gi_bottom - gi_h, gi_w, gi_h)

        # Target: project for rendering
        tx, tz = target_xz
        t_cx, t_cy, t_cz = world_to_camera(tx, 0.0, tz, px, py, pz, yaw)
        target_pt = project_to_screen(t_cx, t_cy, t_cz, w, h, FOV_DEG, PITCH_DOWN_DEG)

        # In view = in front of camera and projection on screen
        target_in_view = (
            target_pt is not None
            and 0 <= target_pt[0] < w
            and 0 <= target_pt[1] < h
        )
        # Collect as soon as target disappears from field of view (was visible, now not)
        if target_was_in_view and not target_in_view:
            score += 1
            target_locations.append([round(target_xz[0], 3), round(target_xz[1], 3)])
            target_reach_times.append(round(current_time, 3))
            continuous_log.append({
                **entry,
                "event": "target_reached",
                "score": score,
                "trial_type": "snake",
                "RoundName": trial_info,
                "condition_type": "gameplay",
                "visibility": "none",
            })
            target_xz = random_target_in_arena_min_dist(px, pz)
            target_was_in_view = False
            if target_sound is not None and target_channel is not None:
                target_channel.play(target_sound)
            elif target_sound is not None:
                target_sound.play()
        else:
            target_was_in_view = target_in_view

        # Floor dots and spotlight visible from trial start at full opacity (no fade in/out)
        dot_color_rgba = (*DOT_COLOR, DOT_ALPHA)
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
        game_surface_main.blit(layer, (0, 0))

        # Target (turquoise circle on floor) - perspective-correct size (further = smaller)
        if target_pt is not None and t_cz > Z_NEAR:
            sx, sy = int(target_pt[0]), int(target_pt[1])
            fov_rad = math.radians(FOV_DEG)
            scale = (h / 2.0) / math.tan(fov_rad / 2.0)
            radius_px = max(4, int(TARGET_WORLD_RADIUS * scale / t_cz))
            if 0 <= sx < w and 0 <= sy < h:
                pygame.draw.circle(game_surface_main, TARGET_COLOR, (sx, sy), radius_px)

        # Spotlight gaze indicator at bottom center (no outline)
        gaze_layer = make_spotlight_surface(gi_w, gi_h, GAZE_INDICATOR_COLOR, GAZE_INDICATOR_ALPHA)
        game_surface_main.blit(gaze_layer, gaze_rect.topleft)

        # Debug: top-down arena minimap (toggle with B key) - arena fixed, avatar moves within it
        if show_debug_minimap:
            map_sz = DEBUG_MINIMAP_SIZE
            map_margin = DEBUG_MINIMAP_MARGIN
            map_x = w - map_sz - map_margin
            map_y = map_margin
            map_radius = (map_sz // 2) - 4

            layer = pygame.Surface((map_sz, map_sz), pygame.SRCALPHA)
            layer.fill(DEBUG_MINIMAP_BG_COLOR)

            # Arena border (fixed circle at center)
            map_cx, map_cy = map_sz / 2.0, map_sz / 2.0
            pygame.draw.circle(layer, DEBUG_MINIMAP_ARENA_BORDER_COLOR, (int(map_cx), int(map_cy)), map_radius, 1)

            # Floor dots (sparse sample, within arena)
            for (wx, _wy, wz) in dots:
                if wx * wx + wz * wz > ARENA_RADIUS * ARENA_RADIUS:
                    continue
                mmx, mmy = world_to_minimap_arena_fixed(wx, wz, map_sz, map_radius)
                if 0 <= mmx < map_sz and 0 <= mmy < map_sz:
                    pygame.draw.circle(layer, DEBUG_MINIMAP_GRID_COLOR, (int(mmx), int(mmy)), 1)

            # Target (arena-fixed position)
            tmx, tmy = world_to_minimap_arena_fixed(target_xz[0], target_xz[1], map_sz, map_radius)
            tr = max(2, int((TARGET_REACH_RADIUS / ARENA_RADIUS) * map_radius))
            if 0 <= tmx < map_sz and 0 <= tmy < map_sz:
                pygame.draw.circle(layer, TARGET_COLOR, (int(tmx), int(tmy)), tr)

            # Avatar: triangle at (px, pz), pointing in facing direction - moves with avatar
            umx, umy = world_to_minimap_arena_fixed(px, pz, map_sz, map_radius)
            tip_len = 10
            base_len = 6
            fx, fz = -math.sin(yaw), -math.cos(yaw)  # Forward in world
            rx, rz = math.cos(yaw), -math.sin(yaw)   # Right in world
            tip_x = umx + fx * tip_len
            tip_y = umy + fz * tip_len
            base_left_x = umx - fx * base_len - rx * base_len
            base_left_y = umy - fz * base_len - rz * base_len
            base_right_x = umx - fx * base_len + rx * base_len
            base_right_y = umy - fz * base_len + rz * base_len
            if 0 <= umx < map_sz and 0 <= umy < map_sz:
                pygame.draw.polygon(layer, DEBUG_MINIMAP_AVATAR_COLOR, [
                    (tip_x, tip_y), (base_left_x, base_left_y), (base_right_x, base_right_y)
                ])
                pygame.draw.polygon(layer, DEBUG_MINIMAP_AVATAR_HEADING_COLOR, [
                    (tip_x, tip_y), (base_left_x, base_left_y), (base_right_x, base_right_y)
                ], 1)

            game_surface_main.blit(layer, (map_x, map_y))

        # Score & timer
        font = pygame.font.SysFont("Arial", FONT_SIZE_SCORE)
        score_text = font.render(f"Score: {score}", True, CLOCK_COLOR)
        game_surface_main.blit(score_text, (10, 10))
        if TRIAL_DURATION is not None:
            remaining = max(0, TRIAL_DURATION - current_time)
            timer_text = font.render(f"{int(remaining // 60):02d}:{int(remaining % 60):02d}", True, CLOCK_COLOR)
            game_surface_main.blit(timer_text, (10, 50))

        if MODE == 'fmri':
            cf = pygame.font.SysFont("Arial", FONT_SIZE_COUNTER)
            cf_surf = cf.render(f"{current_trial}/{total_trials}", True, WHITE)
            cf_rect = cf_surf.get_rect(bottomright=(w - 20, h - 20))
            game_surface_main.blit(cf_surf, cf_rect)

        # Blit scaled game surface centered on fullscreen black
        scaled = pygame.transform.smoothscale(game_surface_main, (display_w, display_h))
        screen.fill(FULLSCREEN_BACKGROUND)
        screen.blit(scaled, (display_offset_x, display_offset_y))
        pygame.display.flip()

        if TRIAL_DURATION is not None and current_time >= TRIAL_DURATION:
            running = False

    if beep_channel is not None:
        beep_channel.stop()
    if target_channel is not None:
        target_channel.stop()

    game_duration = time.time() - game_start

    # Post-game: practice final instruction — Done.png (fMRI: no end fixation; thank-you handled by one_target)
    if MODE == 'practice':
        snake_instructions_dir = os.path.join(os.path.dirname(__file__), "Instructions-he")
        inst_path = os.path.join(snake_instructions_dir, "Done.png")
        if os.path.exists(inst_path):
            try:
                img = pygame.image.load(inst_path)
                sw, sh = screen.get_size()
                rect = img.get_rect(center=(sw // 2, sh // 2))
                waiting = True
                while waiting:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                            waiting = False
                            break
                        if e.type == pygame.KEYDOWN and e.key in (pygame.K_1, pygame.K_RETURN):
                            waiting = False
                        if e.type == pygame.KEYDOWN and e.key == pygame.K_k:
                            print("Instruction skipped by K key")
                            waiting = False
                    screen.fill(FULLSCREEN_BACKGROUND)
                    screen.blit(img, rect)
                    pygame.display.flip()
                    clock.tick(60)
            except Exception:
                pass

    # Combine logs: fixation + gameplay (exploration_trigger compatible)
    full_continuous_log = fixation_logs + continuous_log
    save_continuous_log(full_continuous_log, continuous_filename)
    save_discrete_log([{
        "trial": trial_info,
        "final_score": score,
        "trial_duration": TRIAL_DURATION if TRIAL_DURATION else "endless",
        "target_locations": json.dumps(target_locations),
        "target_reach_times": json.dumps(target_reach_times),
        "game_duration": round(game_duration, 2),
    }], discrete_filename)

    if scanning and trigger_manager is not None:
        trigger_manager.close_trigger()

    pygame.quit()
    print(f"Vection target game complete. Score: {score}. Data: {continuous_filename}")


if __name__ == "__main__":
    print(f"Mode: {MODE}, Participant: {player_initials}")
    if TRIAL_DURATION:
        print(f"Trial duration: {TRIAL_DURATION}s")
    else:
        print("Trial duration: endless (shimming)")
    run_game()
    sys.exit(0)
