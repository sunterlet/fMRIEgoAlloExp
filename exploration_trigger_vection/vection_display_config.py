"""
Unified display configuration for snake_vection and one_target_vection.
Used when both run together in one_target_run.py - ensures identical sizing
of floor dots, minimap, spotlight, text, etc.

Display: true fullscreen on ONE monitor (hides menu bar and Dock on macOS).
Internal resolution: 1000x800 (aspect ratio 5:4), scaled to 75% of screen.
"""

import os
import sys


def prepare_fullscreen_display(screen_number=None):
    """
    Call BEFORE pygame.init(). Sets SDL env vars so fullscreen targets one monitor.
    Must be called before any pygame initialization.
    """
    display_index = screen_number if screen_number is not None else 0
    os.environ["SDL_VIDEO_FULLSCREEN_DISPLAY"] = str(display_index)
    # macOS: avoid Spaces-related issues
    if sys.platform == "darwin":
        os.environ["SDL_VIDEO_MAC_FULLSCREEN_SPACES"] = "0"


def setup_vection_display(screen_number=None):
    """
    Set up fullscreen display on ONE monitor. Hides menu bar and Dock (macOS).
    Returns (screen, screen_width, screen_height).
    Must call prepare_fullscreen_display(screen_number) before pygame.init().
    """
    import pygame

    # Ensure fullscreen targets one display (call before init if not already done)
    prepare_fullscreen_display(screen_number)

    if not pygame.get_init():
        pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    print(f"Fullscreen on display {screen_number or 0}: {screen_width}x{screen_height}")
    return screen, screen_width, screen_height

# Base resolution - both tasks draw at this size, then scale to 75% of screen
GAME_WIDTH = 1000
GAME_HEIGHT = 800
DISPLAY_SCALE = 0.75
FULLSCREEN_BACKGROUND = (3, 3, 1)  # Match task background (near-black)

# Arena
ARENA_DIAMETER = 6.6
ARENA_RADIUS = ARENA_DIAMETER / 2.0
BORDER_THRESHOLD = 0.1

# 3D Vection
EYE_HEIGHT = 1.6
GRID_EXTENT = 60
GRID_SPACING = 1.5
DOT_COLOR = (217, 217, 230)
DOT_ALPHA = 165
DOT_RADIUS_PX = 3
FOV_DEG = 90
PITCH_DOWN_DEG = -12
Z_NEAR = 0.5
Z_FAR = 14
DOTS_VISIBLE_RADIUS = 16
FADE_IN_SPEED = 5.0
TARGET_WORLD_RADIUS = 0.25

# Spotlight (gaze indicator)
GAZE_INDICATOR_WIDTH = 0.35
GAZE_INDICATOR_HEIGHT = 0.12
GAZE_INDICATOR_BOTTOM_MARGIN = 0.03
GAZE_INDICATOR_ALPHA = 80
GAZE_INDICATOR_COLOR = (220, 225, 240)

# Minimap
DEBUG_MINIMAP_SIZE = 180
DEBUG_MINIMAP_MARGIN = 12
DEBUG_MINIMAP_BG_COLOR = (3, 3, 1, 255)  # Same near-black as fullscreen task background
DEBUG_MINIMAP_GRID_COLOR = (80, 80, 90, 100)
# Match exploration_trigger/snake.py avatar (Folly)
DEBUG_MINIMAP_AVATAR_COLOR = (255, 67, 101)
DEBUG_MINIMAP_AVATAR_HEADING_COLOR = (200, 50, 80)
DEBUG_MINIMAP_ARENA_BORDER_COLOR = (120, 120, 130)

# Colors
BACKGROUND_COLOR = (3, 3, 1)  # Near-black for task content
TARGET_COLOR = (0, 217, 192)  # Turquoise
CLOCK_COLOR = (183, 173, 153)  # Khaki
WHITE = (255, 255, 255)

# Fonts
FONT_SIZE_INSTRUCTION = 20
FONT_SIZE_SCORE = 36
FONT_SIZE_COUNTER = 24

# 2D annotation scale (pixels per meter for 2D arena view)
SCALE_2D = 100  # 6.6m arena = 660px at this scale
