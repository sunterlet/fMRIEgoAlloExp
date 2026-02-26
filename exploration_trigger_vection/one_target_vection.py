#!/usr/bin/env python3
"""
One Target Experiment - Vection variant: 3D first-person exploration with 2D annotation.
Exploration: 3D arena (6.6m diameter) like snake_vection - floor dots, first-person view.
Annotation & Feedback: 2D top-down view, matching real arena coordinates (6.6m).
All task rules and requirements from one_target.py are preserved.
"""
import pygame
import sys
import math
import random
import time
import csv
import os
import argparse
from datetime import datetime
import json
# Optional exploration_trigger modules (run from parent dir or with path)
from fixation_utils import show_fixation_image
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

# ---------------------------
# Configuration parameters (Experiment)
# ---------------------------
# 
# STANDARDIZED FIXATION CROSS FORMAT:
# - Cross size: 200 pixels (standard text size equivalent)
# - Cross color: WHITE (255, 255, 255) on BLACK background
# - Background: BACKGROUND_COLOR (3, 3, 1) - near-black
# - Position: Center of screen (CENTER_SCREEN)
# - Uses pygame.font for consistent rendering (equivalent to PTSOD's DrawFormattedText)
# 
# Note: PTSOD uses BLACK cross on WHITE background with same dimensions
# ---------------------------
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
    FONT_SIZE_INSTRUCTION, FONT_SIZE_SCORE, FONT_SIZE_COUNTER, SCALE_2D,
)

# Target parameters
TARGET_RADIUS = 0.1
GRID_SIZE = 0.05

# Movement settings
MOVE_SPEED = 2.0
ROTATE_SPEED = 60.0
TURN_SPEED = 1.2
PRACTICE_ROTATE_SPEED = 70.0
MOVEMENT_FADE_TIME = 0.1

# Input buffering
INPUT_BUFFER_SIZE = 3
last_input_states = []
last_frame_time = 0

# 2D annotation scale (matches GAME_HEIGHT 800: 6.6m * SCALE_2D = 660px)
SCALE = SCALE_2D
SCALE_LEGACY = 200

# Window size (unified with snake_vection - same base resolution)
WIN_WIDTH = GAME_WIDTH
WIN_HEIGHT = GAME_HEIGHT
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# One-target-specific colors
AVATAR_COLOR = (255, 67, 101)       # Folly
BORDER_COLOR = (255, 255, 243)      # Ivory
DEBUG_COLOR = (50, 50, 255)

# ---------------------------
# Experiment parameters - only test trials (no training/dark_training)
# ---------------------------
TRAINING_SESSIONS = 0
DARK_TRAINING_TRIALS = 0
TEST_TRIALS = 3  # Number of test trials in practice mode

# ---------------------------
# Parse command line arguments
# ---------------------------
parser = argparse.ArgumentParser(description='One Target Experiment')
parser.add_argument('mode', choices=['practice', 'fmri'], 
                   help='Run mode: practice (outside magnet) or fmri (inside magnet)')
parser.add_argument('--participant', '-p', default='TEST', 
                   help='Participant initials (default: TEST)')
parser.add_argument('--run', '-r', type=int, default=1,
                   help='Run number for fMRI mode (default: 1)')
parser.add_argument('--trial', '-t', type=int, default=1,
                   help='Current trial number in sequence (default: 1)')
parser.add_argument('--total-trials', '-tt', type=int, default=None,
                   help='Total number of trials (practice: default 3; fmri: default 1)')
parser.add_argument('--screen', '-s', type=int, default=None,
                   help='Screen number to display on (default: None, uses fullscreen)')
parser.add_argument('--scanning', action='store_true',
                   help='Enable trigger functionality for fMRI scanning')
parser.add_argument('--com', type=str, default='com4',
                   help='Serial port for trigger (default: com4)')
parser.add_argument('--tr', type=float, default=2.01,
                   help='TR in seconds (default: 2.01)')
parser.add_argument('--debug', action='store_true', help='Show debug minimap at start')
args = parser.parse_args()

MODE = args.mode
player_initials = args.participant
run_number = args.run
current_trial = args.trial
total_trials = args.total_trials if args.total_trials is not None else (TEST_TRIALS if MODE == 'practice' else 1)
screen_number = args.screen
scanning = args.scanning
com_port = args.com
TR = args.tr  # TR from command line or default 2.01

# TR-aligned trial duration for fMRI mode
if MODE == 'fmri':
    # fMRI mode: Use random TR-aligned durations (8-13 seconds until target placement)
    # Convert to TRs: 8-13 seconds = 4-6.5 TRs, use 4-6 TRs
    EXPLORATION_TRs = random.randint(4, 6)  # 4-6 TRs = 8.04-12.06 seconds
    EXPLORATION_DURATION = EXPLORATION_TRs * TR
else:
    # Practice mode: Same random TR-aligned durations as fMRI mode
    EXPLORATION_TRs = random.randint(4, 6)  # 4-6 TRs = 8.04-12.06 seconds
    EXPLORATION_DURATION = EXPLORATION_TRs * TR

# Annotation phase timer (20 seconds aligned to TRs)
ANNOTATION_TRs = 10  # 10 TRs = 20.1 seconds (close to 20 seconds)
ANNOTATION_DURATION = ANNOTATION_TRs * TR

# Adjust parameters based on mode
if MODE == 'fmri':
    # fMRI mode: only test trials, single run
    TRAINING_SESSIONS = 0
    DARK_TRAINING_TRIALS = 0
    TEST_TRIALS = 1
    # Use centralized results directory if available, otherwise use local results directory
    centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
    if centralized_results_dir and os.path.exists(centralized_results_dir):
        # Create SubID subfolder in centralized directory
        results_dir = os.path.join(centralized_results_dir, player_initials)
        print(f"Using centralized results directory: {results_dir}")
    else:
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        print(f"Using local results directory: {results_dir}")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_OTV_ot{current_trial}_discrete.csv")
    continuous_filename = os.path.join(results_dir, f"{player_initials}_OTV_ot{current_trial}_continuous.csv")
else:
    # Practice mode: full sequence
    # Use centralized results directory if available, otherwise use local results directory
    centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
    if centralized_results_dir and os.path.exists(centralized_results_dir):
        # Create SubID subfolder in centralized directory
        results_dir = os.path.join(centralized_results_dir, player_initials)
        print(f"Using centralized results directory: {results_dir}")
    else:
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        print(f"Using local results directory: {results_dir}")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_one_target_practice_discrete_log.csv")
    continuous_filename = os.path.join(results_dir, f"{player_initials}_one_target_practice_continuous_log.csv")

# Ensure results directory exists
os.makedirs(results_dir, exist_ok=True)

# Enable debug mode if initials are '111'
DEBUG_MODE = (player_initials == '111')

# ---------------------------
# Path to instruction images
# ---------------------------
INSTRUCTIONS_DIR = os.path.join(os.path.dirname(__file__), "Instructions-he")

# ---------------------------
# Initialize Pygame and Mixer
# ---------------------------
# Must set fullscreen display before pygame.init()
prepare_fullscreen_display(screen_number)
pygame.init()

# Audio device selection - try to use a specific device to ensure all sounds go to same output
# List of common audio device names to try (in order of preference)
audio_devices_to_try = [
    "Outside (NVIDIA High Definition Audio)",
    "Speakers (NVIDIA High Definition Audio)",
    "Headphones (NVIDIA High Definition Audio)",
    "Default Audio Device",
    None  # Fallback to system default
]

audio_initialized = False
selected_device = None

for device in audio_devices_to_try:
    try:
        if device:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512, devicename=device)
            print(f"Audio mixer initialized successfully with device: {device}")
        else:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("Audio mixer initialized with system default device")
        audio_initialized = True
        selected_device = device
        break
    except Exception as e:
        print(f"Warning: Could not initialize with device '{device}': {e}")
        continue

if not audio_initialized:
    print("Error: Could not initialize audio mixer with any device")
    pygame.mixer.init()  # Last resort initialization

# Unified display setup: one screen, NOFRAME (same as snake_vection)
screen, screen_width, screen_height = setup_vection_display(screen_number)

# Hide cursor for experiment
pygame.mouse.set_visible(False)
print("Cursor hidden for experiment")

# Calculate the offset to center the game area (75% of screen, aspect ratio locked 1000:800)
# Fit game content within 75% of screen while preserving aspect ratio
max_display_w = int(screen_width * DISPLAY_SCALE)
max_display_h = int(screen_height * DISPLAY_SCALE)
scale_w = max_display_w / WIN_WIDTH
scale_h = max_display_h / WIN_HEIGHT
scale = min(scale_w, scale_h)  # Fit within 75% box, preserve aspect ratio
display_w = int(WIN_WIDTH * scale)
display_h = int(WIN_HEIGHT * scale)
display_offset_x = (screen_width - display_w) // 2
display_offset_y = (screen_height - display_h) // 2
offset_x = (screen_width - WIN_WIDTH) // 2  # legacy, used by fixation_utils
offset_y = (screen_height - WIN_HEIGHT) // 2

# Create a surface for the game content
game_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

pygame.display.set_caption("Exploration Experiment")
clock = pygame.time.Clock()

# ---------------------------
# Initialize Sounds - Unified Audio Device
# ---------------------------
# Load sounds
try:
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
    print("Beep sound loaded successfully")
except Exception as e:
    print(f"Error loading beep sound: {e}")
    beep_sound = None

try:
    target_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)
    print("Target sound loaded successfully")
except Exception as e:
    print(f"Error loading target sound: {e}")
    target_sound = None

# Reserve two channels for audio - both will use the same audio device
try:
    pygame.mixer.set_reserved(2)
    beep_channel = pygame.mixer.Channel(0)
    target_channel = pygame.mixer.Channel(1)
    print("Audio channels reserved successfully")
    print(f"Both channels will use audio device: {selected_device or 'System Default'}")
    
    # Set sound volumes
    if beep_sound is not None:
        beep_sound.set_volume(1.0)
    if target_sound is not None:
        target_sound.set_volume(1.0)
        
except Exception as e:
    print(f"Warning: Could not reserve audio channels: {e}")
    beep_channel = None
    target_channel = None

# ---------------------------
# Helper functions for visited locations tracking
# ---------------------------
def get_grid_cell(pos):
    """Convert a position to a grid cell coordinate."""
    x, y = pos
    grid_x = int(x / GRID_SIZE)
    grid_y = int(y / GRID_SIZE)
    return (grid_x, grid_y)

def is_position_visited(pos, visited_cells):
    """Check if a position has been visited based on grid cells."""
    cell = get_grid_cell(pos)
    return cell in visited_cells

def add_visited_position(pos, visited_cells):
    """Add a position to the visited cells set."""
    cell = get_grid_cell(pos)
    visited_cells.add(cell)

def get_player_tip_position(player_pos, player_angle):
    """Calculate the position of the player's tip (2D coords for annotation).
    angle 0 = north = -z, so tip is in -z direction."""
    tip_length = 0.15
    rad = math.radians(player_angle)
    tip_x = player_pos[0] + tip_length * math.sin(rad)
    tip_z = player_pos[1] - tip_length * math.cos(rad)  # -cos: forward = -z (north)
    return (tip_x, tip_z)


def get_player_tip_position_3d(px, pz, yaw):
    """Calculate tip position in 3D world (floor point in front of player)."""
    tip_length = 0.15
    tip_x = px - math.sin(yaw) * tip_length
    tip_z = pz - math.cos(yaw) * tip_length
    return (tip_x, tip_z)


# --- 3D Vection helpers (from snake_vection) ---
def make_floor_dots(extent: float, spacing: float):
    """Build list of (x, y, z) floor dot positions."""
    points = []
    x = -extent
    while x <= extent:
        z = -extent
        while z <= extent:
            points.append((x, 0.0, z))
            z += spacing
        x += spacing
    return points


def world_to_minimap_arena_fixed(wx, wz, map_sz, map_radius):
    """Convert world (x,z) to minimap pixel - arena fixed at center, avatar moves within it. +x right, -z up (forward)."""
    map_cx = map_sz / 2.0
    map_cy = map_sz / 2.0
    scale = map_radius / ARENA_RADIUS
    mx = map_cx + wx * scale
    my = map_cy + wz * scale
    return mx, my


def world_to_camera(wx, wy, wz, px, py, pz, yaw):
    """Transform world point to camera space. Same as run_vection_pygame."""
    dx, dy, dz = wx - px, wy - py, wz - pz
    c, s = math.cos(yaw), math.sin(yaw)
    cx = dx * c - dz * s
    cy = dy
    cz = -dx * s - dz * c
    return cx, cy, cz


def project_to_screen(cx, cy, cz, width, height, fov_deg, pitch_deg=0.0):
    """Project camera-space point to screen. pitch_deg tilts view down."""
    if cz <= Z_NEAR or cz > Z_FAR:
        return None
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
    """2D distance (works with (x,z) or (x,y))."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def within_arena(x, z):
    """Check if (x, z) is inside arena."""
    return math.hypot(x, z) <= ARENA_RADIUS


_spotlight_cache = {}


def make_spotlight_surface(width: int, height: int, color: tuple, peak_alpha: int):
    """Create spotlight-style surface: radial gradient, brightest at center, fade to transparent."""
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

# ---------------------------
# Function to display an instruction image
# ---------------------------
def show_image(image_path, duration=None):
    """Load and display instruction image at original size, centered.
       If duration is provided, wait for that many seconds.
       Otherwise, wait for the user to press a key (except Escape, which exits)."""
    try:
        instruction_image = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return

    sw, sh = screen.get_size()
    rect = instruction_image.get_rect(center=(sw // 2, sh // 2))
    screen.fill(FULLSCREEN_BACKGROUND)
    screen.blit(instruction_image, rect)
    pygame.display.flip()
    
    if duration is not None:
        # Wait for specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            clock.tick(15)
    else:
        # Wait for key press (6 key)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:  # Use 1 or ENTER key to break the loop
                        waiting = False
            clock.tick(15)

# ---------------------------
# Function to show fixation cross
# ---------------------------
def show_fixation(duration=6.0, continuous_log=None, trial_counter=None, trial_info=None):
    """Display a fixation cross for the specified duration."""
    show_fixation_image(screen, game_surface, offset_x, offset_y, duration, 
                       "white_on_black", continuous_log, trial_counter, trial_info, FULLSCREEN_BACKGROUND)

# ---------------------------
# Helper functions for Hebrew text
# ---------------------------
def get_hebrew_font(size):
    """Load custom font supporting Hebrew."""
    try:
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Gisha.ttf")
        return pygame.font.Font(font_path, size)
    except Exception as e:
        print(f"Could not load custom font, using default. Error: {e}")
        return pygame.font.SysFont("Arial", size)

def render_hebrew_text(font, text, color):
    """Render Hebrew text with proper right-to-left handling."""
    # For Hebrew text, we need to reverse the character order for proper RTL display
    # This is a simple approach - for more complex RTL handling, you might need a library like python-bidi
    if any('\u0590' <= char <= '\u05FF' for char in text):  # Hebrew Unicode range
        # Reverse the text for proper RTL display
        reversed_text = text[::-1]
        return font.render(reversed_text, True, color)
    else:
        return font.render(text, True, color)

def draw_one_target_trial_intro(trial_num, total_trials):
    """Draw trial intro screen: זירת מטרה אחת, זירה X/3. Wait for Enter."""
    screen.fill(FULLSCREEN_BACKGROUND)
    game_surface.fill(BACKGROUND_COLOR)
    font_title = get_hebrew_font(36)
    title_text = render_hebrew_text(font_title, "זירת מטרה אחת", WHITE)
    title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 40))
    game_surface.blit(title_text, title_rect)
    font_num = get_hebrew_font(24)
    # RTL: write "3\1" to display as "1/3"
    num_text = render_hebrew_text(font_num, f"זירה {total_trials}\\{trial_num}", WHITE)
    num_rect = num_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
    game_surface.blit(num_text, num_rect)
    font_inst = get_hebrew_font(20)
    inst_text = render_hebrew_text(font_inst, "לחצו RETNE כדי להתחיל", WHITE)
    inst_rect = inst_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 60))
    game_surface.blit(inst_text, inst_rect)
    screen.blit(game_surface, (offset_x, offset_y))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_1, pygame.K_RETURN):
                waiting = False
        clock.tick(60)
    screen.fill(FULLSCREEN_BACKGROUND)
    pygame.display.flip()

# ---------------------------
# Helper drawing functions
# ---------------------------
def to_screen_coords(pos):
    """Convert arena coordinates (in meters) to screen coordinates for 2D annotation.
    pos = (x, z) in world coords. -z = north = up (matches minimap and exploration)."""
    x, z = pos
    screen_x = CENTER_SCREEN[0] + int(x * SCALE)
    screen_y = CENTER_SCREEN[1] + int(z * SCALE)  # -z = north = up (aligns with minimap)
    return (screen_x, screen_y)

def distance(a, b):
    """Euclidean distance between two points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_thermometer(distance_moved, is_moving_forward_backward, movement_stop_time, current_time):
    """Draw a horizontal bar (thermometer) at the top-left showing distance moved."""
    # Only show if currently moving or within delay time
    should_show = is_moving_forward_backward or (movement_stop_time is not None and 
        current_time - movement_stop_time <= MOVEMENT_FADE_TIME)
    
    if not should_show:
        return 0.0  # Reset distance when indicator disappears
    
    bar_x, bar_y = 50, 30
    max_bar_width = int(ARENA_DIAMETER * SCALE)
    bar_height = 20
    accumulation_factor = 200
    bar_width = min(max_bar_width, int(distance_moved * accumulation_factor))
    
    font = get_hebrew_font(FONT_SIZE_INSTRUCTION)
    label_text = render_hebrew_text(font, "תנועה קדימה/אחורה", WHITE)
    game_surface.blit(label_text, (bar_x, bar_y - 25))
    
    pygame.draw.rect(game_surface, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    pygame.draw.rect(game_surface, TARGET_COLOR, (bar_x, bar_y, bar_width, bar_height))
    
    return distance_moved  # Return current distance

def draw_clock(angle_rotated, is_rotating, rotation_stop_time, current_time):
    """Draw a clock-like dial at the top-right showing rotation angle."""
    # Only show if currently rotating or within delay time
    should_show = is_rotating or (rotation_stop_time is not None and 
        current_time - rotation_stop_time <= MOVEMENT_FADE_TIME)
    
    if not should_show:
        return 0.0  # Reset angle when indicator disappears

    dial_center = (WIN_WIDTH - 100, 75)
    dial_radius = 50

    font = get_hebrew_font(FONT_SIZE_INSTRUCTION)
    label_text = render_hebrew_text(font, "זווית סיבוב", WHITE)
    label_rect = label_text.get_rect(center=(dial_center[0], dial_center[1] - dial_radius - 15))
    game_surface.blit(label_text, label_rect)

    # Draw the clock circle
    pygame.draw.circle(game_surface, WHITE, dial_center, dial_radius, 2)
    
    # Draw the rotation indicator
    rad = math.radians(angle_rotated)
    end_x = dial_center[0] + dial_radius * math.sin(rad)
    end_y = dial_center[1] - dial_radius * math.cos(rad)
    pygame.draw.line(game_surface, CLOCK_COLOR, dial_center, (int(end_x), int(end_y)), 4)
    
    # Draw the angle text with sign
    angle_text = font.render(f"{int(angle_rotated)}°", True, WHITE)
    text_rect = angle_text.get_rect(center=(dial_center[0], dial_center[1] - 10))
    game_surface.blit(angle_text, text_rect)
    
    return angle_rotated  # Return current angle

def draw_arena():
    """Draw the arena border as a circle centered on the screen (Ivory)."""
    pygame.draw.circle(game_surface, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)

def draw_player_avatar(player_pos, player_angle, color=AVATAR_COLOR):
    """Draw an elongated triangle representing the player."""
    p_screen = to_screen_coords(player_pos)
    tip_length = 30
    base_length = 20
    half_width = 17

    rad = math.radians(player_angle)
    tip = (
        p_screen[0] + int(tip_length * math.sin(rad)),
        p_screen[1] - int(tip_length * math.cos(rad))
    )
    base_center = (
        p_screen[0] - int(base_length * math.sin(rad)),
        p_screen[1] + int(base_length * math.cos(rad))
    )
    left = (
        base_center[0] + int(half_width * math.sin(rad + math.pi/2)),
        base_center[1] - int(half_width * math.cos(rad + math.pi/2))
    )
    right = (
        base_center[0] + int(half_width * math.sin(rad - math.pi/2)),
        base_center[1] - int(half_width * math.cos(rad - math.pi/2))
    )
    pygame.draw.polygon(game_surface, color, [tip, left, right])

def draw_grid(visited_cells):
    """Draw a grid of the arena to show visited locations."""
    # Calculate grid dimensions
    grid_cell_size = GRID_SIZE * SCALE
    num_cells = int(ARENA_DIAMETER / GRID_SIZE)
    
    # Draw visited cells first (underneath the grid)
    visited_color = (*TARGET_COLOR, 180)  # More opaque turquoise
    for cell in visited_cells:
        grid_x = CENTER_SCREEN[0] + cell[0] * grid_cell_size
        grid_y = CENTER_SCREEN[1] + cell[1] * grid_cell_size  # cell[1]=z, matches to_screen
        # Create a surface for the visited cell
        cell_surface = pygame.Surface((grid_cell_size, grid_cell_size), pygame.SRCALPHA)
        cell_surface.fill(visited_color)
        game_surface.blit(cell_surface, (grid_x - grid_cell_size/2, grid_y - grid_cell_size/2))
    
    # Draw vertical lines
    for i in range(-num_cells//2, num_cells//2 + 1):
        x = CENTER_SCREEN[0] + i * grid_cell_size
        # North (-z) at top, south (+z) at bottom (matches to_screen)
        pygame.draw.line(game_surface, DEBUG_COLOR, 
                        (x, CENTER_SCREEN[1] - ARENA_RADIUS * SCALE),
                        (x, CENTER_SCREEN[1] + ARENA_RADIUS * SCALE), 1)
    
    # Draw horizontal lines
    for i in range(-num_cells//2, num_cells//2 + 1):
        y = CENTER_SCREEN[1] + i * grid_cell_size
        pygame.draw.line(game_surface, DEBUG_COLOR,
                        (CENTER_SCREEN[0] - ARENA_RADIUS * SCALE, y),
                        (CENTER_SCREEN[0] + ARENA_RADIUS * SCALE, y), 1)

def draw_conditions(target_placement_time, current_trial_time, has_moved_forward, has_rotated, 
                   is_moving_forward_backward, is_rotating, distance_from_center, player_pos, player_angle, visited_cells, trial_start_time):
    """Draw indicators showing which target placement conditions are met."""
    # All condition checks are still needed for target placement logic, but we don't display them
    time_remaining = max(0, target_placement_time - time.time())
    time_elapsed = time_remaining <= 0
    
    tip_pos = get_player_tip_position(player_pos, player_angle)
    tip_cell = get_grid_cell(tip_pos)
    is_new_location = tip_cell not in visited_cells

# ---------------------------
# Trial function with logging (Experiment)
# ---------------------------
def run_trial(is_training, target_sound_param, trial_info, trial_counter, show_minimap_at_start=False):
    global BACKGROUND_COLOR, target_sound
    # Use the global target_sound if parameter is None
    if target_sound_param is None:
        target_sound_param = target_sound
    phase = "exploration"  # phases: exploration, annotation, feedback

    # current_trial is already defined globally from command line arguments

    # Generate random target placement delay (whole number between 8-13 seconds)
    target_placement_delay = random.randint(8, 13)
    target_placement_time = None  # Will be set when movement starts

    # 3D state for exploration (px, pz = floor position; yaw in radians)
    px, py, pz = 0.0, EYE_HEIGHT, 0.0
    yaw = 0.0
    # 2D alias for code that expects player_pos/player_angle (annotation/feedback use these)
    player_pos = [0.0, 0.0]  # used in annotation phase
    player_angle = 0.0
    dots_3d = make_floor_dots(GRID_EXTENT, GRID_SPACING)  # precompute floor dots
    move_key_pressed = None
    move_start_pos = None
    rotate_key_pressed = None
    rotate_start_angle = None
    target_was_inside = False
    annotation_marker_pos = [0.0, 0.0]
    annotation_marker_angle = 0.0

    # Add movement tracking variables
    distance_moved = 0.0
    angle_rotated = 0.0  # This will now be signed (negative for left, positive for right)
    last_pos = [0.0, 0.0]
    last_angle = 0.0
    is_moving_forward_backward = False
    is_rotating = False
    rotation_start_angle = None  # Track the angle when rotation starts
    movement_stop_time = None
    rotation_stop_time = None

    # For target placement tracking
    visited_cells = set()
    target_placed = False
    target_position = None
    movement_start_time = None
    target_placed_time = None  # Track when target was actually placed
    has_moved_forward = False
    has_rotated = False
    is_moving = False
    trial_movement_started = False  # Track if movement has started in current trial

    trial_start_time = time.time()
    exploration_start_time = trial_start_time
    annotation_start_time = None
    continuous_log = []
    encountered_goal = None

    trial_done = False

    # Add this before the main loop in run_trial:
    last_tip_cell = None
    current_tip_cell = None
    
    # Track active keys for MRI control box compatibility
    active_keys = set()
    
    # Debug minimap: practice trial 1 starts with minimap on; else B toggles (or args.debug)
    show_debug_minimap = show_minimap_at_start or args.debug
    # Trial 1: target on minimap hidden until user toggles with B; trials 2-3: show target when minimap is on
    show_target_on_minimap = not show_minimap_at_start

    while not trial_done:
        dt = clock.tick(60) / 1000.0
        current_trial_time = time.time() - trial_start_time

        # Check if trial duration has elapsed
        if phase == "exploration" and movement_start_time is not None:
            # Set target placement time when movement starts
            if target_placement_time is None:
                target_placement_time = movement_start_time + target_placement_delay
            
            # Calculate distance from center (3D: use px, pz)
            distance_from_center = math.hypot(px, pz)
            
            # When time elapses, try to place target if conditions are met
            if not target_placed and target_placement_time is not None and time.time() >= target_placement_time:
                # Check if player is moving forward/backward (8/9) and not rotating (7/0)
                keys = pygame.key.get_pressed()
                is_moving_forward_backward = (pygame.K_7 in active_keys or keys[pygame.K_7] or
                    pygame.K_8 in active_keys or keys[pygame.K_8])
                is_rotating = (pygame.K_6 in active_keys or keys[pygame.K_6] or
                    pygame.K_9 in active_keys or keys[pygame.K_9])
                
                # OLD TARGET PLACEMENT LOGIC - REMOVED
                # This was placing targets without visited cell checks
                # Now using the new logic below with proper visited cell validation

        if phase in ["exploration", "annotation"]:
            if phase == "exploration":
                # Only set event when it actually occurs
                current_event = None
                
                # Check for "started moving" event - only once at the start of movement
                if movement_start_time is not None and not any(log.get("event") == "started moving" for log in continuous_log):
                    current_event = "started moving"
                
                # Check for "target_placed" event - only once when target is placed
                if target_placed and not any(log.get("event") == "target_placed" for log in continuous_log):
                    current_event = "target_placed"
                    if DEBUG_MODE:
                        print("DEBUG: Setting event to target_placed")
                
                # Check for "returned_to_target" event - every time target is reached except first placement
                if target_position is not None and dist_2d((px, pz), target_position) <= TARGET_RADIUS:
                    if DEBUG_MODE:
                        print(f"DEBUG: Inside target area check")
                        print(f"DEBUG: target_was_inside = {target_was_inside}")
                        print(f"DEBUG: current_event = {current_event}")
                    
                    if not target_was_inside:  # Only log when entering the target area
                        if DEBUG_MODE:
                            print("DEBUG: Player just entered target area")
                        
                        # Don't log for initial placement (which happens in the same frame)
                        if current_event != "target_placed" and target_placed_time and time.time() - target_placed_time > 0.1:
                            if DEBUG_MODE:
                                print("DEBUG: Setting event to returned_to_target")
                            current_event = "returned_to_target"
                            encountered_goal = target_position
                            encountered_goal_time = time.time()
                    target_was_inside = True
                else:
                    target_was_inside = False
                
                if DEBUG_MODE:
                    print(f"DEBUG: Final current_event = {current_event}")
                
                # REMOVED: This was creating duplicate incomplete entries
                # entry = {
                #     "trial_info": trial_info,
                #     "phase": "exploration",
                #     "trial_time": round(current_trial_time, 3),
                #     "event": current_event,
                #     "x": round(player_pos[0], 3),
                #     "y": round(player_pos[1], 3)
                # }
                # if DEBUG_MODE and current_event:
                #     print(f"DEBUG: Adding log entry with event: {current_event}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_1 or event.key == pygame.K_RETURN:
                    if phase == "exploration":
                        # Only allow proceeding to annotation if target has been placed
                        if target_placed:
                            exploration_time = time.time() - exploration_start_time
                            phase = "annotation"
                            annotation_start_time = time.time()
                            annotation_marker_pos = [0.0, 0.0]  # (x, z) in world coords
                            annotation_marker_angle = 0.0  # reorient to north (facing up on 2D map)
                            print(f"Annotation phase started. Timer: {ANNOTATION_DURATION:.1f} seconds ({ANNOTATION_TRs} TRs)")
                            # Stop any playing sounds when transitioning to annotation
                            if beep_channel is not None:
                                beep_channel.stop()
                            if target_channel is not None:
                                target_channel.stop()
                        # If target hasn't been placed, ignore the key press
                    elif phase == "annotation":
                        # Add target_annotated event when 1 or ENTER is pressed in annotation phase
                        entry = {
                            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                            "trial_time": round(current_trial_time, 3),
                            "trial": trial_counter,  # Use actual trial number instead of trial_info
                            "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                            "phase": "annotation",
                            "event": "target_annotated",
                            "x": round(annotation_marker_pos[0], 3),
                            "y": round(annotation_marker_pos[1], 3),
                            "rotation_angle": round(annotation_marker_angle, 3)
                        }
                        continuous_log.append(entry)
                        annotation_time = time.time() - annotation_start_time
                        phase = "feedback"
                    elif phase == "feedback":
                        trial_done = True
                elif event.key == pygame.K_2:
                    # Debug feature: Press 2 to force target placement
                    if phase == "exploration" and not target_placed:
                        print("DEBUG: Force placing target with key 2")
                        tip_x, tip_z = get_player_tip_position_3d(px, pz, yaw)
                        target_position = (tip_x, tip_z)
                        target_placed = True
                        target_placed_time = time.time()
                        
                        # Play target sound when target is placed
                        if target_sound_param is not None and target_channel is not None:
                            target_channel.play(target_sound_param)
                        elif target_sound_param is not None:
                            target_sound_param.play()
                        
                        # Add target_placed event to continuous log
                        entry = {
                            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                            "trial_time": round(current_trial_time, 3),
                            "trial": trial_counter,
                            "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                            "phase": "exploration",
                            "event": "target_placed_debug",
                            "x": round(px, 3),
                            "y": round(pz, 3),
                            "rotation_angle": round(math.degrees(yaw), 3)
                        }
                        continuous_log.append(entry)
                        print(f"DEBUG: Target placed at time {time.time() - trial_start_time:.2f}")
                if phase == "exploration":
                    if event.key in (pygame.K_7, pygame.K_8):  # Number keys for movement
                        if move_key_pressed is None:
                            move_key_pressed = event.key
                            move_start_pos = [px, pz]
                    if event.key in (pygame.K_6, pygame.K_9):  # Number keys for rotation
                        if rotate_key_pressed is None:
                            rotate_key_pressed = event.key
                            rotate_start_angle = math.degrees(yaw)
                # Track number key presses for MRI control box
                if event.key in [pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_1, pygame.K_2, pygame.K_RETURN]:
                    active_keys.add(event.key)
                if event.key == pygame.K_k:
                    pass
                elif event.key == pygame.K_b:
                    if show_minimap_at_start:
                        show_target_on_minimap = not show_target_on_minimap
                    else:
                        show_debug_minimap = not show_debug_minimap
            if event.type == pygame.KEYUP:
                if phase == "exploration":
                    if event.key in (pygame.K_7, pygame.K_8):  # Number keys for movement
                        move_key_pressed = None
                        move_start_pos = None
                    if event.key in (pygame.K_6, pygame.K_9):  # Number keys for rotation
                        rotate_key_pressed = None
                        rotate_start_angle = None
                # Remove keys when released
                if event.key in [pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_1, pygame.K_2, pygame.K_RETURN]:
                    active_keys.discard(event.key)

        screen.fill(FULLSCREEN_BACKGROUND)  # Black fullscreen, 75% content centered
        game_surface.fill(BACKGROUND_COLOR)

        if phase == "exploration":
            keys = pygame.key.get_pressed()
            # Use both active_keys tracking and get_pressed() for maximum compatibility with MRI control box
            current_is_moving = (pygame.K_6 in active_keys or keys[pygame.K_6] or 
                               pygame.K_7 in active_keys or keys[pygame.K_7] or 
                               pygame.K_8 in active_keys or keys[pygame.K_8] or 
                               pygame.K_9 in active_keys or keys[pygame.K_9])
            current_is_moving_forward_backward = (pygame.K_7 in active_keys or keys[pygame.K_7] or 
                                                pygame.K_8 in active_keys or keys[pygame.K_8])  # Track forward/backward movement
            current_is_rotating = (pygame.K_6 in active_keys or keys[pygame.K_6] or 
                                 pygame.K_9 in active_keys or keys[pygame.K_9])  # Track rotation
            
            # Reset movement tracking when movement stops
            if not current_is_moving_forward_backward:
                if is_moving_forward_backward:
                    movement_stop_time = time.time()
                is_moving_forward_backward = False
            else:
                movement_stop_time = None

            if not current_is_rotating:
                if is_rotating:
                    rotation_stop_time = time.time()
                is_rotating = False
                rotation_start_angle = None
            else:
                rotation_stop_time = None

            # Reset indicators after fade time elapses
            if movement_stop_time is not None and time.time() - movement_stop_time > MOVEMENT_FADE_TIME:
                distance_moved = 0.0
                movement_stop_time = None

            if rotation_stop_time is not None and time.time() - rotation_stop_time > MOVEMENT_FADE_TIME:
                angle_rotated = 0.0
                rotation_stop_time = None
            
            # Start movement timer on first movement
            if current_is_moving and movement_start_time is None:
                movement_start_time = time.time()
                trial_movement_started = True
            
            # Track movement and rotation
            if pygame.K_7 in active_keys or keys[pygame.K_7]:  # Move forward
                has_moved_forward = True
            if pygame.K_8 in active_keys or keys[pygame.K_8]:  # Move backward
                pass  # No special tracking needed
            if (pygame.K_6 in active_keys or keys[pygame.K_6] or 
                pygame.K_9 in active_keys or keys[pygame.K_9]):  # Rotate left or right
                has_rotated = True
                # Set rotation start angle when rotation begins
                if rotation_start_angle is None:
                    rotation_start_angle = math.degrees(yaw)

            # Update player position and angle (3D: px, pz, yaw)
            old_px, old_pz = px, pz
            forward_x = -math.sin(yaw)
            forward_z = -math.cos(yaw)
            
            # Movement logic: match run_vection_pygame exactly
            if pygame.K_7 in active_keys or keys[pygame.K_7]:  # Move forward
                new_px = px + forward_x * MOVE_SPEED * dt
                new_pz = pz + forward_z * MOVE_SPEED * dt
                if within_arena(new_px, new_pz):
                    px, pz = new_px, new_pz
                    if not is_moving_forward_backward or movement_stop_time is not None:
                        distance_moved = 0.0
                        movement_stop_time = None
                    is_moving_forward_backward = True
            if pygame.K_8 in active_keys or keys[pygame.K_8]:  # Move backward
                new_px = px - forward_x * MOVE_SPEED * dt
                new_pz = pz - forward_z * MOVE_SPEED * dt
                if within_arena(new_px, new_pz):
                    px, pz = new_px, new_pz
                    if not is_moving_forward_backward or movement_stop_time is not None:
                        distance_moved = 0.0
                        movement_stop_time = None
                    is_moving_forward_backward = True
            if pygame.K_6 in active_keys or keys[pygame.K_6]:  # 6: rotate left (match run_vection: avatar ccw, dots cw)
                yaw += TURN_SPEED * dt
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = math.degrees(yaw)
            if pygame.K_9 in active_keys or keys[pygame.K_9]:  # 9: rotate right (match run_vection: avatar cw, dots ccw)
                yaw -= TURN_SPEED * dt
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = math.degrees(yaw)

            # Update movement tracking
            if is_moving_forward_backward:
                distance_moved += math.hypot(px - old_px, pz - old_pz)
            
            # Update rotation tracking with signed values
            if is_rotating and rotation_start_angle is not None:
                angle_diff = math.degrees(yaw) - rotation_start_angle
                # Normalize angle difference to be between -180 and 180 degrees
                while angle_diff > 180:
                    angle_diff -= 360
                while angle_diff < -180:
                    angle_diff += 360
                angle_rotated = angle_diff

            # Get current tip position and cell (3D)
            tip_pos = get_player_tip_position_3d(px, pz, yaw)
            current_tip_cell = get_grid_cell(tip_pos)

            # Check border collision and play beep sound
            if math.hypot(px, pz) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                if beep_sound is not None and beep_channel is not None:
                    if not beep_channel.get_busy():
                        beep_channel.play(beep_sound, loops=-1)
            else:
                if beep_channel is not None:
                    if beep_channel.get_busy():
                        beep_channel.stop()

            # Check if all conditions are met
            all_conditions_met = (
                target_placement_time is not None and
                time.time() >= target_placement_time and
                has_moved_forward and
                has_rotated and
                (pygame.K_7 in active_keys or keys[pygame.K_7] or pygame.K_8 in active_keys or keys[pygame.K_8]) and
                not (pygame.K_6 in active_keys or keys[pygame.K_6] or pygame.K_9 in active_keys or keys[pygame.K_9]) and
                math.hypot(px, pz) >= 0.5 and
                math.hypot(px, pz) <= (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD)
            )

            # Check if we've entered a new cell
            entered_new_cell = last_tip_cell is None or current_tip_cell != last_tip_cell

            # Check if player is at target position
            if target_position is not None:
                if dist_2d((px, pz), target_position) <= TARGET_RADIUS:
                    if not target_was_inside:
                        if DEBUG_MODE:
                            print(f"DEBUG: Target reached at time {time.time() - trial_start_time:.2f}")
                            print(f"DEBUG: Target was placed at {target_placed_time - trial_start_time:.2f}")
                        # Play target sound when reaching target
                        if target_sound_param is not None and target_channel is not None:
                            target_channel.play(target_sound_param)
                        elif target_sound_param is not None:
                            target_sound_param.play()
                        # Set returned_to_target event here, when we actually detect reaching the target
                        # Don't set it for the initial placement
                        if target_placed_time and time.time() - target_placed_time > 0.1:
                            current_event = "returned_to_target"
                            encountered_goal = target_position
                            encountered_goal_time = time.time()
                            if DEBUG_MODE:
                                print("DEBUG: Setting returned_to_target event")
                            # Add the event to the log immediately
                            entry = {
                                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                                "trial_time": round(current_trial_time, 3),
                                "trial": trial_counter,  # Use actual trial number instead of trial_info
                                "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                                "phase": "exploration",
                                "event": current_event,
                                "x": round(px, 3),
                                "y": round(pz, 3),
                                "rotation_angle": round(math.degrees(yaw), 3)
                            }
                            continuous_log.append(entry)
                            if DEBUG_MODE:
                                print(f"DEBUG: Adding log entry with event: {current_event}")
                    target_was_inside = True
                else:
                    if target_was_inside and DEBUG_MODE:
                        print("DEBUG: Player left target area")
                    target_was_inside = False  # Reset when player leaves target area

            # Place target when all conditions are met and tip enters a new, unvisited cell
            if (not target_placed and 
                movement_start_time is not None and 
                all_conditions_met and
                entered_new_cell and
                current_tip_cell not in visited_cells):
                
                if DEBUG_MODE:
                    print(f"DEBUG: Target placement check - current_tip_cell: {current_tip_cell}")
                    print(f"DEBUG: Target placement check - visited_cells contains: {list(visited_cells)[:10]}...")  # Show first 10 cells
                    print(f"DEBUG: Target placement check - current_tip_cell in visited_cells: {current_tip_cell in visited_cells}")
                
                if DEBUG_MODE:
                    print("DEBUG: Placing target - all conditions met")
                
                # Place target at tip position (3D: tip_pos is already (tx, tz) on floor)
                target_position = (tip_pos[0], tip_pos[1])
                target_placed = True
                target_placed_time = time.time()  # Record when target was placed
                # Play target sound when target is placed
                if target_sound_param is not None and target_channel is not None:
                    target_channel.play(target_sound_param)
                elif target_sound_param is not None:
                    target_sound_param.play()
                if DEBUG_MODE:
                    print(f"DEBUG: Target placed at time {time.time() - trial_start_time:.2f}")
                # Add target_placed event to continuous log (explicit entry, don't also set current_event)
                entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": round(current_trial_time, 3),
                    "trial": trial_counter,  # Use actual trial number instead of trial_info
                    "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                    "phase": "exploration",
                    "event": "target_placed",
                    "x": round(px, 3),
                    "y": round(pz, 3),
                    "rotation_angle": round(math.degrees(yaw), 3)
                }
                continuous_log.append(entry)
                # Don't set current_event here - we've already logged it explicitly above

            # If we've moved to a new cell, mark the previous cell as visited
            if last_tip_cell is not None and current_tip_cell != last_tip_cell:
                visited_cells.add(last_tip_cell)
                if DEBUG_MODE:
                    print(f"DEBUG: Marked previous cell {last_tip_cell} as visited")

            # Always update last_tip_cell
            last_tip_cell = current_tip_cell

            # 3D exploration: floor dots and spotlight visible from trial start, no fading
            w, h = WIN_WIDTH, WIN_HEIGHT

            game_surface.fill(BACKGROUND_COLOR)

            # Floor dots: visible from trial start at full opacity (no fade in/out)
            dot_color_rgba = (*DOT_COLOR, DOT_ALPHA)
            layer = pygame.Surface((w, h), pygame.SRCALPHA)
            radius_sq = DOTS_VISIBLE_RADIUS * DOTS_VISIBLE_RADIUS
            for (wx, wy, wz) in dots_3d:
                if (wx - px) ** 2 + (wz - pz) ** 2 > radius_sq:
                    continue
                cx, cy, cz = world_to_camera(wx, wy, wz, px, py, pz, yaw)
                pt = project_to_screen(cx, cy, cz, w, h, FOV_DEG, PITCH_DOWN_DEG)
                if pt:
                    sx, sy = int(pt[0]), int(pt[1])
                    if 0 <= sx < w and 0 <= sy < h:
                        pygame.draw.circle(layer, dot_color_rgba, (sx, sy), DOT_RADIUS_PX)
            game_surface.blit(layer, (0, 0))

            # Target: NOT visible during exploration - only sound when placed. Visible only in feedback phase.

            # Spotlight: always visible
            gi_w = int(w * GAZE_INDICATOR_WIDTH)
            gi_h = int(h * GAZE_INDICATOR_HEIGHT)
            gi_bottom = h - int(h * GAZE_INDICATOR_BOTTOM_MARGIN)
            gaze_rect = pygame.Rect(w // 2 - gi_w // 2, gi_bottom - gi_h, gi_w, gi_h)
            gaze_layer = make_spotlight_surface(gi_w, gi_h, GAZE_INDICATOR_COLOR, GAZE_INDICATOR_ALPHA)
            game_surface.blit(gaze_layer, gaze_rect.topleft)

            # No arena border during exploration (only floor dots + spotlight)

            # Draw UI overlays (no thermometer/clock - movement indicators not needed)
            font = get_hebrew_font(FONT_SIZE_INSTRUCTION)
            instruction_text = render_hebrew_text(font, "למעבר סימון המטרה לחצ/י RETNE", WHITE)
            text_rect = instruction_text.get_rect(centerx=WIN_WIDTH//2, bottom=WIN_HEIGHT-30)
            game_surface.blit(instruction_text, text_rect)

            draw_debug_timing_panel(
                trial_start_time,
                movement_start_time,
                target_placement_time,
                exploration_start_time,
                annotation_start_time,
                target_placed_time
            )

            # Debug: top-down arena minimap (toggle with B key) - matches snake_vection: arena fixed, avatar moves
            if show_debug_minimap:
                map_sz = DEBUG_MINIMAP_SIZE
                map_margin = DEBUG_MINIMAP_MARGIN
                map_x = w - map_sz - map_margin
                map_y = map_margin
                map_radius = (map_sz // 2) - 4

                layer = pygame.Surface((map_sz, map_sz), pygame.SRCALPHA)
                layer.fill(DEBUG_MINIMAP_BG_COLOR)

                map_cx, map_cy = map_sz / 2.0, map_sz / 2.0
                pygame.draw.circle(layer, DEBUG_MINIMAP_ARENA_BORDER_COLOR, (int(map_cx), int(map_cy)), map_radius, 1)

                for (wx, _wy, wz) in dots_3d:
                    if wx * wx + wz * wz > ARENA_RADIUS * ARENA_RADIUS:
                        continue
                    mmx, mmy = world_to_minimap_arena_fixed(wx, wz, map_sz, map_radius)
                    if 0 <= mmx < map_sz and 0 <= mmy < map_sz:
                        pygame.draw.circle(layer, DEBUG_MINIMAP_GRID_COLOR, (int(mmx), int(mmy)), 1)

                if target_placed and target_position is not None and (show_target_on_minimap or not show_minimap_at_start):
                    tmx, tmy = world_to_minimap_arena_fixed(target_position[0], target_position[1], map_sz, map_radius)
                    tr = max(2, int((TARGET_RADIUS / ARENA_RADIUS) * map_radius))
                    if 0 <= tmx < map_sz and 0 <= tmy < map_sz:
                        pygame.draw.circle(layer, TARGET_COLOR, (int(tmx), int(tmy)), tr)

                umx, umy = world_to_minimap_arena_fixed(px, pz, map_sz, map_radius)
                tip_len = 10
                base_len = 6
                fx, fz = -math.sin(yaw), -math.cos(yaw)
                rx, rz = math.cos(yaw), -math.sin(yaw)
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

                game_surface.blit(layer, (map_x, map_y))

        elif phase == "annotation":
            # Check if annotation timer has expired
            annotation_elapsed_time = time.time() - annotation_start_time
            if annotation_elapsed_time >= ANNOTATION_DURATION:
                # Timer expired - automatically proceed to feedback phase
                print(f"Annotation timer expired after {annotation_elapsed_time:.1f} seconds. Proceeding to feedback phase.")
                entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": round(current_trial_time, 3),
                    "trial": trial_counter,  # Use actual trial number instead of trial_info
                    "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                    "phase": "annotation",
                    "event": "annotation_timeout",
                    "x": round(annotation_marker_pos[0], 3),
                    "y": round(annotation_marker_pos[1], 3),
                    "rotation_angle": round(annotation_marker_angle, 3)
                }
                continuous_log.append(entry)
                annotation_time = time.time() - annotation_start_time
                phase = "feedback"
            
            keys = pygame.key.get_pressed()
            if pygame.K_6 in active_keys or keys[pygame.K_6]:  # 6 = counterclockwise (left)
                annotation_marker_angle -= ROTATE_SPEED * dt
            if pygame.K_9 in active_keys or keys[pygame.K_9]:  # 9 = clockwise (right)
                annotation_marker_angle += ROTATE_SPEED * dt
            if pygame.K_7 in active_keys or keys[pygame.K_7]:  # Move forward (angle 0 = north = -z)
                rad = math.radians(annotation_marker_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = -MOVE_SPEED * dt * math.cos(rad)  # -cos: forward = -z (north)
                new_x = annotation_marker_pos[0] + dx
                new_y = annotation_marker_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[0] = new_x
                    annotation_marker_pos[1] = new_y
            if pygame.K_8 in active_keys or keys[pygame.K_8]:  # Move backward
                rad = math.radians(annotation_marker_angle)
                dx = -MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = annotation_marker_pos[0] + dx
                new_y = annotation_marker_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[0] = new_x
                    annotation_marker_pos[1] = new_y

            # Add continuous logging for annotation phase
            # REMOVED: This was causing duplicate entries since main game loop already logs all phases
            # entry = {
            #     "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            #     "trial_time": round(current_trial_time, 3),
            #     "trial": current_trial,  # Use actual trial number instead of trial_info
            #     "phase": "annotation",
            #     "event": None,  # No events during annotation phase
            #     "x": round(annotation_marker_pos[0], 3),
            #     "y": round(annotation_marker_pos[1], 3),
            #     "rotation_angle": round(annotation_marker_angle, 3)
            # }
            # continuous_log.append(entry)

            draw_arena()
            # Add instruction text in the middle under the arena
            font = get_hebrew_font(FONT_SIZE_INSTRUCTION)
            instruction_text = render_hebrew_text(font, "נווט/י למיקום המטרה ולאישור לחצ/י RETNE", WHITE)
            text_rect = instruction_text.get_rect(centerx=WIN_WIDTH//2, bottom=WIN_HEIGHT-30)
            game_surface.blit(instruction_text, text_rect)
            # Draw annotation avatar in Khaki (CLOCK_COLOR)
            draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)

            # Add debug timing panel in annotation phase
            draw_debug_timing_panel(
                trial_start_time,
                movement_start_time,
                target_placement_time,
                exploration_start_time,
                annotation_start_time,
                target_placed_time
            )

        elif phase == "feedback":
            # Add continuous logging for feedback phase
            # REMOVED: This was causing duplicate entries since main game loop already logs all phases
            # entry = {
            #     "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            #     "trial_time": round(current_trial_time, 3),
            #     "trial": current_trial,  # Use actual trial number instead of trial_info
            #     "phase": "feedback",
            #     "event": None,  # No events during feedback phase
            #     "x": round(annotation_marker_pos[0], 3),
            #     "y": round(annotation_marker_pos[1], 3),
            #     "rotation_angle": round(annotation_marker_angle, 3)
            # }
            # continuous_log.append(entry)

            draw_arena()
            if target_position is not None:
                target_screen = to_screen_coords(target_position)
                pygame.draw.circle(game_surface, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 0)
            # Draw feedback avatar in Khaki (CLOCK_COLOR)
            draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
        
        # Draw trial counter
        if MODE == 'fmri':
            # In fMRI mode, use the sequence trial numbers (within the single run)
            counter_text = f"{current_trial}/{total_trials}"
        else:
            # In practice mode: only test trials
            internal_total = TEST_TRIALS
            if "run" in trial_info:
                internal_current = trial_info.split("run")[1]
            else:
                internal_current = trial_info.split()[1] if len(trial_info.split()) > 1 else "1"
            counter_text = f"{internal_current}/{internal_total}"
        counter_font = pygame.font.SysFont("Arial", FONT_SIZE_COUNTER)
        counter_surface = counter_font.render(counter_text, True, WHITE)
        counter_rect = counter_surface.get_rect()
        counter_rect.bottomright = (WIN_WIDTH - 20, WIN_HEIGHT - 20)
        game_surface.blit(counter_surface, counter_rect)

        # Add continuous logging for all phases (every frame)
        if phase == "exploration":
            entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": round(current_trial_time, 3),
                "trial": trial_counter,  # Use actual trial number instead of trial_info
                "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                "phase": "exploration",
                "event": current_event,
                "x": round(px, 3),
                "y": round(pz, 3),
                "rotation_angle": round(math.degrees(yaw), 3)
            }
            continuous_log.append(entry)
            current_event = None  # Reset event after logging
        elif phase == "annotation":
            entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": round(current_trial_time, 3),
                "trial": trial_counter,  # Use actual trial number instead of trial_info
                "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                "phase": "annotation",
                "event": None,  # No events during annotation phase
                "x": round(annotation_marker_pos[0], 3),
                "y": round(annotation_marker_pos[1], 3),
                "rotation_angle": round(annotation_marker_angle, 3)
            }
            continuous_log.append(entry)
        elif phase == "feedback":
            entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": round(current_trial_time, 3),
                "trial": trial_counter,  # Use actual trial number instead of trial_info
                "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                "phase": "feedback",
                "event": None,  # No events during feedback phase
                "x": round(annotation_marker_pos[0], 3),
                "y": round(annotation_marker_pos[1], 3),
                "rotation_angle": round(annotation_marker_angle, 3)
            }
            continuous_log.append(entry)

        # Check if K is pressed (debug: show 2D map)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_k]:
            # Show all elements when K is pressed
            draw_arena()
            if phase == "exploration":
                draw_player_avatar([px, pz], 180 - math.degrees(yaw))  # 3D pos/angle to 2D
            elif phase == "annotation":
                draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
            elif phase == "feedback":
                draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
            
            # Show target if it's placed
            if target_placed and target_position is not None:
                target_screen = to_screen_coords(target_position)
                pygame.draw.circle(game_surface, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 0)
            
            # Show grid
            draw_grid(visited_cells)

        else:
            # Normal drawing logic when K is not pressed (exploration uses 3D, drawn above)
            if phase == "exploration":
                pass  # 3D already drawn in exploration block
            elif phase == "annotation":
                draw_arena()
                draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
            elif phase == "feedback":
                draw_arena()
                if target_position is not None:
                    target_screen = to_screen_coords(target_position)
                    pygame.draw.circle(game_surface, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 0)
                draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
                # Draw instruction text
                font = get_hebrew_font(FONT_SIZE_INSTRUCTION)
                text = render_hebrew_text(font, "לחצ/י RETNE להמשך", WHITE)
                text_rect = text.get_rect(centerx=WIN_WIDTH//2, bottom=WIN_HEIGHT-30)
                game_surface.blit(text, text_rect)

        # Blit at 75% scale, centered
        scaled = pygame.transform.smoothscale(game_surface, (display_w, display_h))
        screen.fill(FULLSCREEN_BACKGROUND)
        screen.blit(scaled, (display_offset_x, display_offset_y))
        pygame.display.flip()

    exploration_time = time.time() - exploration_start_time if exploration_start_time is not None else 0
    annotation_time = time.time() - annotation_start_time if annotation_start_time is not None else 0
    error_distance = None
    # Calculate error distance between target location and annotation position
    # This should always be calculated if a target was placed, regardless of whether player returned to it
    if target_position is not None:
        error_distance = dist_2d(target_position, annotation_marker_pos)
    
    # Stop all sounds when trial ends
    if beep_channel is not None:
        beep_channel.stop()
    if target_channel is not None:
        target_channel.stop()
    
    # Note: TR alignment is no longer needed since we wait for triggers before each trial
    # The trigger ensures trials start at TR boundaries, so no alignment is necessary
    
    discrete_log = {
        "trial": trial_counter,  # Use actual trial number instead of trial_info
        "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"), # Add condition type
        "assigned_delay": target_placement_delay,  # The randomly assigned delay (8-15s)
        "movement_start_time": round(movement_start_time - trial_start_time, 2) if movement_start_time is not None else None,  # Time from trial start to first movement
        "target_placement_time": round(target_placed_time - trial_start_time, 2) if target_placed_time is not None else None,  # Time from trial start to target placement
        "exploration_time": round(exploration_time, 2),  # Time from trial start to Enter press
        "annotation_time": round(annotation_time, 2),  # Time spent in annotation phase
        "target_location": json.dumps([round(x, 2) for x in target_position]) if target_position is not None else None,
        "target_annotation": json.dumps([round(x, 2) for x in annotation_marker_pos]),
        "error_distance": round(error_distance, 2) if error_distance is not None else None
    }
    return discrete_log, continuous_log

# ---------------------------
# Functions to save logs to CSV (Experiment)
# ---------------------------
def save_discrete_log(logs, filename):
    # Delete previous file if it exists to avoid multiple files
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"Deleted previous file: {filename}")
        except Exception as e:
            print(f"Warning: Could not delete previous file {filename}: {e}")
    
    try:
        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "trial",
                "condition_type",
                "assigned_delay",
                "movement_start_time",
                "target_placement_time",
                "exploration_time",
                "annotation_time",
                "target_location",
                "target_annotation",
                "error_distance"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log in logs:
                writer.writerow(log)
        print(f"Discrete log saved successfully to: {filename}")
    except Exception as e:
        print(f"Error saving discrete log: {e}")
        # Try to save with a timestamp as last resort
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = filename.replace('.csv', f'_backup_{timestamp}.csv')
        try:
            with open(backup_filename, "w", newline="") as csvfile:
                fieldnames = [
                    "trial",
                    "condition_type",
                    "assigned_delay",
                    "movement_start_time",
                    "target_placement_time",
                    "exploration_time",
                    "annotation_time",
                    "target_location",
                    "target_annotation",
                    "error_distance"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for log in logs:
                    writer.writerow(log)
            print(f"Discrete log saved as backup to: {backup_filename}")
        except Exception as backup_e:
            print(f"Failed to save backup file: {backup_e}")

def log_error_to_continuous_log(continuous_log, error_message, trial_number=None, trial_info=None):
    """
    Log an error message to the continuous log before exiting.
    
    Args:
        continuous_log: List to append error entry to
        error_message: Error message to log
        trial_number: Current trial number (if available)
        trial_info: Trial info string (if available)
    """
    error_entry = {
        "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
        "trial_time": 0.0,
        "trial": trial_number if trial_number is not None else "N/A",
        "condition_type": "error",
        "phase": "error",
        "event": f"ERROR: {error_message}",
        "x": 0.0,
        "y": 0.0,
        "rotation_angle": 0.0
    }
    continuous_log.append(error_entry)
    print(f"ERROR LOGGED: {error_message} (trial: {trial_number})")

def save_continuous_log(logs, filename):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    try:
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["RealTime", "trial_time", "trial", "trial_type", "RoundName", "condition_type", "visibility", "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in logs:
                # Only write fields that exist in the row
                filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(filtered_row)
        print(f"Continuous log saved successfully to: {filename}")
    except Exception as e:
        print(f"Error saving continuous log: {e}")
        # Try to save with a timestamp as last resort
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = filename.replace('.csv', f'_backup_{timestamp}.csv')
        try:
            with open(backup_filename, "w", newline="") as csvfile:
                fieldnames = ["RealTime", "trial_time", "trial", "trial_type", "RoundName", "condition_type", "visibility", "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in logs:
                    filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                    writer.writerow(filtered_row)
            print(f"Continuous log saved as backup to: {backup_filename}")
        except Exception as backup_e:
            print(f"Failed to save backup file: {backup_e}")



# ---------------------------
# Main Experiment Loop
# ---------------------------
def run_experiment():
    """Run the experiment with all trials based on mode."""
    # Use the global target sound
    training_target_sound = target_sound
    
    # Initialize trigger manager if scanning is enabled
    trigger_manager = TriggerManager(scanning=scanning, com_port=com_port)
    if scanning:
        if not trigger_manager.init_trigger():
            error_msg = "Failed to initialize trigger connection"
            print(f"CRITICAL: {error_msg}. Exiting.")
            # Try to log error if all_continuous_logs exists
            if 'all_continuous_logs' in globals():
                log_error_to_continuous_log(all_continuous_logs, error_msg)
                try:
                    save_continuous_log(all_continuous_logs, continuous_filename)
                except:
                    pass
            trigger_manager.close_trigger()
            sys.exit(1)

    # Initialize lists for logs
    all_discrete_logs = []
    all_continuous_logs = []
    
    # Initialize trial counter for proper numbering
    trial_counter = 1

    if MODE == 'practice':
        # Practice mode: OT-ins.png once, then trial intro (זירת מטרה אחת, זירה X/3) before each trial
        print("Running practice mode (outside magnet)")
        show_image(os.path.join(INSTRUCTIONS_DIR, "OT-ins.png"))

        for i in range(1, total_trials + 1):
            draw_one_target_trial_intro(i, total_trials)
            trial_info = f"test {i}"
            # Trial 1: minimap visible; trials 2-3: minimap hidden (B toggles)
            show_minimap = (i == 1)
            discrete_log, continuous_log = run_trial(False, training_target_sound, trial_info, trial_counter, show_minimap_at_start=show_minimap)
            all_discrete_logs.append(discrete_log)
            all_continuous_logs.extend(continuous_log)
            trial_counter += 1
            save_discrete_log(all_discrete_logs, discrete_filename)
            save_continuous_log(all_continuous_logs, continuous_filename)

        show_image(os.path.join(INSTRUCTIONS_DIR, "Done.png"))
        
        print("Practice session complete.")

    elif MODE == 'fmri':
        # fMRI mode: single test trial inside magnet
        print(f"Running fMRI mode (inside magnet) - Run {run_number}")
        
        # Wait for trigger before starting trial
        trigger_received_time = None
        trigger_time_value = None
        
        if scanning:
            # Wait for trigger from scanner
            # First trial gets 60 seconds, subsequent trials get 40 seconds
            trigger_timeout = 60.0 if current_trial == 1 else 40.0
            print(f'Waiting for scanner trigger before trial {current_trial} (timeout: {trigger_timeout:.0f}s)...')
            success, trigger_time = trigger_manager.wait_for_trigger(timeout=trigger_timeout)
            if not success:
                error_msg = f"Failed to receive trigger within {trigger_timeout:.0f} seconds timeout (trial {current_trial})"
                print(f"CRITICAL: {error_msg}. Exiting.")
                # Log error to continuous log before exiting
                log_error_to_continuous_log(all_continuous_logs, error_msg, current_trial)
                try:
                    save_continuous_log(all_continuous_logs, continuous_filename)
                    print(f"Error logged to: {continuous_filename}")
                except Exception as e:
                    print(f"Warning: Could not save error log: {e}")
                trigger_manager.close_trigger()
                sys.exit(1)
            trigger_time_value = trigger_time
            trigger_received_time = trigger_time
            print(f"Trigger received at time: {trigger_time_value:.3f} seconds")
        else:
            # Not scanning - use environment variable if available (for compatibility)
            trigger_received_time = os.getenv('TRIGGER_RECEIVED_TIME')
            if trigger_received_time:
                trigger_time_value = float(trigger_received_time)
        
        # Set experiment start time for fMRI mode
        experiment_start_time = time.time()
        
        # Log trigger received event - always log when we have a trigger time
        # When scanning is enabled, we always wait for and receive a trigger for each trial
        if trigger_time_value is not None:
            trigger_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": 0.0,
                "trial": current_trial,
                "condition_type": "test",
                "phase": "trigger",
                "event": "trigger_received",
                "x": 0.0,
                "y": 0.0,
                "rotation_angle": 0.0,
                "trigger_received_time": trigger_time_value
            }
            all_continuous_logs.append(trigger_entry)
            print(f"Logged trigger received at time: {trigger_time_value:.3f} (trial {current_trial})")
        elif scanning:
            # This should never happen when scanning is enabled (we wait for trigger)
            print(f"WARNING: Scanning enabled but no trigger time available for trial {current_trial}")
        
        # Show fixation at start only when scanning (8 TRs first trial, 4 TRs subsequent)
        if scanning:
            if current_trial == 1:
                fixation_trs = 8
                print('Fixation: 8 TRs (4 dummy + 4 trial 1)')
            else:
                fixation_trs = 4
                print(f'Fixation: 4 TRs (trial {current_trial})')
            trial_info = f"test_run{run_number}"
            fixation_duration = fixation_trs * TR
            show_fixation_image(screen, game_surface, offset_x, offset_y, fixation_duration, 
                               "white_on_black", all_continuous_logs, current_trial, trial_info, FULLSCREEN_BACKGROUND)
            if all_continuous_logs:
                for entry in all_continuous_logs[-2:]:
                    if entry.get("event") in ["fixation_start", "fixation_end"]:
                        entry["condition_type"] = "test"
            print(f"Fixation complete.")
            print('Fixation complete. Showing instruction for 1 TR...')
            show_image(os.path.join(INSTRUCTIONS_DIR, "OT-screen.png"), duration=TR)
        else:
            print('Skipping fixation (not scanning). Showing instruction...')
            show_image(os.path.join(INSTRUCTIONS_DIR, "OT-screen.png"), duration=1.5)
        
        # Single test trial
        trial_info = f"test_run{run_number}"
        trial_start_time = time.time()
        discrete_log, continuous_log = run_trial(False, training_target_sound, trial_info, current_trial)
        all_discrete_logs.append(discrete_log)
        all_continuous_logs.extend(continuous_log)
        
        # Save results
        save_discrete_log(all_discrete_logs, discrete_filename)
        save_continuous_log(all_continuous_logs, continuous_filename)
        
        # Only show final fixation and thank you screen for the last trial
        if current_trial == total_trials:
            if scanning:
                # Show 4 TRs fixation at end when scanning
                print('Final fixation: 4 TRs')
                final_fixation_start_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": time.time() - experiment_start_time,
                    "trial": current_trial,
                    "condition_type": "test",
                    "phase": "fixation",
                    "event": "final_fixation_start",
                    "x": 0.0,
                    "y": 0.0,
                    "rotation_angle": 0.0
                }
                all_continuous_logs.append(final_fixation_start_entry)
                final_fixation_duration = 4 * TR
                show_fixation_image(screen, game_surface, offset_x, offset_y, final_fixation_duration, 
                                   "white_on_black", None, None, None, FULLSCREEN_BACKGROUND)
                final_fixation_end_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": time.time() - experiment_start_time,
                    "trial": current_trial,
                    "condition_type": "test",
                    "phase": "fixation",
                    "event": "final_fixation_end",
                    "x": 0.0,
                    "y": 0.0,
                    "rotation_angle": 0.0
                }
                all_continuous_logs.append(final_fixation_end_entry)
                print(f"Final fixation complete.")
            else:
                print('Skipping final fixation (not scanning).')
            
            # Show thank you screen
            print("Showing thank you screen...")
            show_image(os.path.join(INSTRUCTIONS_DIR, "Done.png"))
        else:
            print(f"Trial {current_trial}/{total_trials} complete - no final fixation or thank you screen (not final trial).")
        
        print("One Target Run complete.")
        print(f"Trial {current_trial}/{total_trials} completed")
        
        # Close trigger connection if scanning
        if scanning and trigger_manager is not None:
            trigger_manager.close_trigger()
    
    # Clean up and exit
    pygame.quit()
    sys.exit()

# Add new function for drawing debug timing panel:
def draw_debug_timing_panel(trial_start_time, movement_start_time, target_placement_time, exploration_start_time, annotation_start_time=None, target_placed_time=None):
    """Draw timing information panel in debug mode."""
    if not DEBUG_MODE:
        return

    current_time = time.time()
    font = pygame.font.SysFont("Arial", 16)
    x, y = WIN_WIDTH - 300, 20  # Position panel on the right side
    spacing = 25
    panel_color = (50, 50, 50)  # Dark gray background
    text_color = WHITE

    # Calculate the actual delay that was assigned
    assigned_delay = int(target_placement_time - movement_start_time) if target_placement_time is not None and movement_start_time is not None else "Not set"

    # Calculate time until target placement
    time_until_target = None
    if movement_start_time is not None:
        if target_placement_time is not None:
            time_until_target = max(0, target_placement_time - current_time)
        else:
            time_until_target = assigned_delay
    else:
        time_until_target = "Not started"

    # Calculate annotation timer information
    annotation_time_remaining = None
    if annotation_start_time is not None:
        annotation_elapsed = current_time - annotation_start_time
        annotation_time_remaining = max(0, ANNOTATION_DURATION - annotation_elapsed)

    # Create timing information dictionary
    timings = {
        "Trial Time": f"{current_time - trial_start_time:.2f}s",
        "Time Since First Move": f"{current_time - movement_start_time:.2f}" if movement_start_time else "Not started",
        "Assigned Delay": f"{assigned_delay}s",
        "Time Until Target": f"{time_until_target:.2f}s" if isinstance(time_until_target, (int, float)) else time_until_target,
        "Target Placement Time": f"{target_placed_time - movement_start_time:.2f}s" if target_placed_time is not None and movement_start_time is not None else "Not placed",
        "Exploration Time": f"{current_time - exploration_start_time:.2f}s",
        "Annotation Time": f"{current_time - annotation_start_time:.2f}s" if annotation_start_time else "Not started",
        "Annotation Timer": f"{annotation_time_remaining:.2f}s" if annotation_time_remaining is not None else "Not started"
    }

    # Draw panel background
    panel_height = (len(timings) + 1) * spacing
    panel_surface = pygame.Surface((280, panel_height))
    panel_surface.fill(panel_color)
    panel_surface.set_alpha(200)  # Semi-transparent
    game_surface.blit(panel_surface, (x - 10, y - 10))

    # Draw title
    title = font.render("DEBUG TIMING PANEL", True, TARGET_COLOR)
    game_surface.blit(title, (x, y))
    y += spacing

    # Draw timing information
    for label, value in timings.items():
        text = font.render(f"{label}: {value}", True, text_color)
        game_surface.blit(text, (x, y))
        y += spacing

if __name__ == "__main__":
    print(f"Starting One Target Experiment")
    print(f"Mode: {MODE}")
    print(f"Participant: {player_initials}")
    if MODE == 'fmri':
        print(f"Run: {run_number}")
    run_experiment()
