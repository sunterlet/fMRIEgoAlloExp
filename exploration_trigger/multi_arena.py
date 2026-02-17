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
from pygame import mixer
from screeninfo import get_monitors
from fixation_utils import show_fixation_image
from trigger_utils import TriggerManager
from sound_paths import SOUNDS_DIR, BEEP_SOUND_PATH
# Fallback (uncomment if sound_paths fails on PC):
# SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
# BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    print("Warning: pyserial not available. Trigger functionality will be disabled.")
    SERIAL_AVAILABLE = False

# ---------------------------
# STANDARDIZED FIXATION CROSS FORMAT:
# - Cross size: 200 pixels (standard text size equivalent)
# - Cross color: WHITE (255, 255, 255) on BLACK background
# - Background: BACKGROUND_COLOR (3, 3, 1) - near-black
# - Position: Center of screen (CENTER_SCREEN)
# - Uses pygame.font for consistent rendering (equivalent to PTSOD's DrawFormattedText)
# 
# Note: PTSOD uses BLACK cross on WHITE background with same dimensions
# ---------------------------
# Parse command line arguments
# ---------------------------
parser = argparse.ArgumentParser(description='Multi-Arena Experiment')
parser.add_argument('mode', choices=['practice', 'fmri'], 
                   help='Run mode: practice (outside magnet) or fmri (inside magnet)')
parser.add_argument('--participant', '-p', default='TEST', 
                   help='Participant initials (default: TEST)')
parser.add_argument('--run', '-r', type=int, default=1,
                   help='Run number for fMRI mode (default: 1)')
parser.add_argument('--trial', '-t', type=int, default=1,
                   help='Current trial number in sequence (default: 1)')
parser.add_argument('--total-trials', '-tt', type=int, default=1,
                   help='Total number of trials in sequence (default: 1)')
parser.add_argument('--arena', '-a', default='arena1',
                   help='Arena name to run (default: arena1)')
parser.add_argument('--visibility', '-v', choices=['full', 'limited', 'none'], default='full',
                   help='Visibility mode: full, limited, or none (default: full)')
parser.add_argument('--num-trials', '-n', type=int, default=1,
                   help='Number of trials to run for this condition (default: 1)')
parser.add_argument('--arena-number', '-an', type=int, default=1,
                   help='Arena number within condition (1 or 2) (default: 1)')
parser.add_argument('--arenas-per-condition', '-apc', type=int, default=2,
                   help='Total number of arenas per condition (default: 2)')
parser.add_argument('--screen', '-s', type=int, default=None,
                   help='Screen number to display on (default: None, uses fullscreen)')
parser.add_argument('--fa-run', '-far', type=int, default=None,
                   help='Full arena run identifier for logging (default: None)')
parser.add_argument('--scanning', action='store_true',
                    help='Enable trigger functionality for fMRI scanning')
parser.add_argument('--com', type=str, default='com4',
                    help='Serial port for trigger (default: com4)')
parser.add_argument('--tr', type=float, default=2.01,
                    help='TR in seconds (default: 2.01)')
args = parser.parse_args()

MODE = args.mode
player_initials = args.participant
run_number = args.run
current_trial = args.trial
total_trials = args.total_trials
arena_name = args.arena
visibility_mode = args.visibility
num_trials = args.num_trials
arena_number = args.arena_number
arenas_per_condition = args.arenas_per_condition
screen_number = args.screen
fa_run_number = args.fa_run
scanning = args.scanning
com_port = args.com
TR = args.tr  # TR from command line or default 2.01

# Use passed arena number and total arenas from command-line arguments
# These are set by full_arena_run.py based on the run configuration
multi_arena_trial_number = arena_number
total_multi_arena_trials = arenas_per_condition

# Create timestamp for the entire experiment
EXPERIMENT_TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")
# Global experiment start time
EXPERIMENT_START_TIME = time.time()

# ---------------------------
# Configuration parameters
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
BORDER_THRESHOLD = 0.1
TARGET_RADIUS = 0.25
ANNOTATION_RADIUS = 0.08  # Slightly smaller radius for annotations

# Debug mode
SHOW_TARGETS_DEBUG = False
SHOW_ARENA_DEBUG = False

# Movement settings
MOVE_SPEED = 1.0
ROTATE_SPEED = 60.0
MOVEMENT_FADE_TIME = 0.1  # Time in seconds for movement indicator to fade out

# Scale factor: pixels per meter
SCALE = 200

# Window size
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# ---------------------------
# Set up logging files
# ---------------------------
# Use centralized results directory if available, otherwise use local results directory
centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
if centralized_results_dir and os.path.exists(centralized_results_dir):
    # Create SubID subfolder in centralized directory
    results_dir = os.path.join(centralized_results_dir, player_initials)
    print(f"Using centralized results directory: {results_dir}")
else:
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    print(f"Using local results directory: {results_dir}")

if MODE == 'fmri':
    run_prefix = f"FA{fa_run_number}" if fa_run_number is not None else "FA"
    continuous_filename = os.path.join(results_dir, f"{player_initials}_{run_prefix}_fa{current_trial}_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_{run_prefix}_fa{current_trial}_discrete.csv")
else:
    # Practice mode: Use unified single file approach (no arena-specific suffixes)
    continuous_filename = os.path.join(results_dir, f"{player_initials}_multi_arena_practice_continuous_log.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_multi_arena_practice_discrete_log.csv")

# Ensure results directory exists
os.makedirs(results_dir, exist_ok=True)

# ---------------------------
# Custom Color Palette
# ---------------------------
BACKGROUND_COLOR = (3, 3, 1)        # Background: near-black
AVATAR_COLOR = (255, 67, 101)       # Avatar: Folly
BORDER_COLOR = (255, 255, 243)      # Arena border: Ivory
TARGET_COLOR = (0, 217, 192)        # Targets: Turquoise
ANNOTATION_COLOR = (183, 173, 153)  # Annotation: Khaki
WHITE = (255, 255, 255)

# ---------------------------
# Initialize Pygame and Mixer
# ---------------------------
pygame.init()

# Initialize mixer with explicit settings for consistent audio output
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512, devicename=None)
    print("Audio mixer initialized with explicit settings")
except Exception as e:
    print(f"Warning: Could not initialize audio with explicit settings: {e}")
    try:
        pygame.mixer.init()
        print("Audio mixer initialized with default settings")
    except Exception as e2:
        print(f"Error: Could not initialize audio mixer: {e2}")
        pygame.mixer.init()

# Create display using improved screen selection
try:
    # Import screen utilities
    from screen_utils import setup_screen_selection
    
    # Set up screen with proper Windows compatibility
    screen, screen_width, screen_height = setup_screen_selection(screen_number)
    print(f"Screen setup completed: {screen_width}x{screen_height}")
    
except ImportError:
    # Fallback to original method if screen_utils is not available
    print("Warning: screen_utils not available, using fallback method")
    
    if screen_number is not None:
        # Use specified screen number with screeninfo
        try:
            # Get list of monitors
            monitors = get_monitors()
            if screen_number >= len(monitors):
                print(f"Invalid monitor index {screen_number}. Only {len(monitors)} monitors available.")
                print("Falling back to default screen.")
                screen_number = None
            else:
                monitor = monitors[screen_number]
                os.environ['SDL_VIDEO_WINDOW_POS'] = f"{monitor.x},{monitor.y}"
                print(f"Setting display to screen {screen_number} (position: {monitor.x}, {monitor.y})")
                
                # Create borderless window covering entire monitor (avoids fullscreen issues)
                screen = pygame.display.set_mode((monitor.width, monitor.height), pygame.NOFRAME)
                screen_width = monitor.width
                screen_height = monitor.height
                print(f"Borderless window on screen {screen_number}: {screen_width}x{screen_height}")
        except Exception as e:
            print(f"Failed to use specified screen {screen_number}, falling back to default: {e}")
            screen_number = None
    
    if screen_number is None:
        # Use hardcoded default screen 0 (primary monitor)
        screen_number = 0
        try:
            monitors = get_monitors()
            if screen_number < len(monitors):
                monitor = monitors[screen_number]
                os.environ['SDL_VIDEO_WINDOW_POS'] = f"{monitor.x},{monitor.y}"
                screen = pygame.display.set_mode((monitor.width, monitor.height), pygame.NOFRAME)
                screen_width = monitor.width
                screen_height = monitor.height
                print(f"Borderless window on hardcoded screen {screen_number}: {screen_width}x{screen_height}")
            else:
                # Fallback to fullscreen if no monitors detected
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                screen_info = pygame.display.Info()
                screen_width = screen_info.current_w
                screen_height = screen_info.current_h
                print(f"Fullscreen mode (fallback): {screen_width}x{screen_height}")
        except Exception as e:
            print(f"Failed to use screeninfo, falling back to fullscreen: {e}")
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            screen_info = pygame.display.Info()
            screen_width = screen_info.current_w
            screen_height = screen_info.current_h
            print(f"Fullscreen mode (fallback): {screen_width}x{screen_height}")

# Hide cursor for experiment (will be shown during annotation phase)
pygame.mouse.set_visible(False)
print("Cursor hidden for experiment (will be shown during annotation phase)")

# Calculate the offset to center the game area
offset_x = (screen_width - WIN_WIDTH) // 2
offset_y = (screen_height - WIN_HEIGHT) // 2

# Create a surface for the game content
game_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

pygame.display.set_caption("Multi-Arena Experiment")
clock = pygame.time.Clock()

# ---------------------------
# Load sounds
# ---------------------------
def load_target_sounds(arena_name):
    """Load all target sounds from the arena's directory."""
    sounds = {}
    
    # Extract base arena name from trial name (e.g., "garden_training_1" -> "garden")
    base_arena_name = arena_name.split('_')[0]
    
    # Try new arena structure first, then fall back to old structure
    sounds_dir = os.path.join(SOUNDS_DIR, "arenas", base_arena_name)
    
    if not os.path.exists(sounds_dir):
        # Fall back to old structure
        sounds_dir = os.path.join(SOUNDS_DIR, base_arena_name)
        print(f"Using old sound directory structure: {sounds_dir}")
    else:
        print(f"Using new sound directory structure: {sounds_dir}")
    
    # Check if directory exists
    if not os.path.exists(sounds_dir):
        print(f"Warning: Sound directory not found: {sounds_dir}")
        return sounds
    
    # Load sounds
    for filename in os.listdir(sounds_dir):
        if filename.endswith('.wav') or filename.endswith('.mp3'):
            sound_path = os.path.join(sounds_dir, filename)
            
            try:
                sound = pygame.mixer.Sound(sound_path)
                # Store with lowercase key for case-insensitive matching
                sounds[filename[:-4].lower()] = sound
                print(f"Loaded sound: {filename}")
            except Exception as e:
                print(f"Error loading sound {filename}: {e}")
    
    return sounds

try:
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
    beep_sound.set_volume(1.0)
except Exception as e:
    print("Error loading beep sound:", e)
    beep_sound = None

# Create single dedicated channel for all audio output
try:
    pygame.mixer.set_reserved(1)
    audio_channel = pygame.mixer.Channel(0)
    print("Audio channel reserved successfully")
except Exception as e:
    print(f"Warning: Could not reserve audio channel: {e}")
    audio_channel = None

# ---------------------------
# Load arena data
# ---------------------------
def load_arena_data():
    """Load arena data from CSV file."""
    arenas = {}
    hebrew_names = {}  # Dictionary to store Hebrew names
    hebrew_arena_names = {}  # Dictionary to store Hebrew arena names
    # Load from Final111_New_Arenas.csv
    arena_file = os.path.join(os.path.dirname(__file__), "Final111_New_Arenas.csv")
    print(f"Using arena file: {arena_file}")
    
    if not os.path.exists(arena_file):
        print(f"Error: Arena file not found: {arena_file}")
        sys.exit(1)
    
    with open(arena_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            if len(row) >= 5:
                # New format with Hebrew arena names
                arena_name_csv, target_name, coords, hebrew_name, hebrew_arena_name = row
                # Parse coordinates from string format "(x; y)"
                coords = coords.strip('()').split(';')
                if len(coords) == 2:
                    try:
                        x, y = float(coords[0]), float(coords[1])
                        
                        if arena_name_csv not in arenas:
                            arenas[arena_name_csv] = {}
                            hebrew_names[arena_name_csv] = {}
                        arenas[arena_name_csv][target_name] = (x, y)
                        hebrew_names[arena_name_csv][target_name] = hebrew_name
                        hebrew_arena_names[arena_name_csv] = hebrew_arena_name
                    except ValueError:
                        print(f"Warning: Could not parse coordinates: {coords}")
            elif len(row) >= 4:
                # Handle 4-column format (without Hebrew arena names)
                arena_name_csv, target_name, coords, hebrew_name = row
                # Parse coordinates from string format "(x; y)"
                coords = coords.strip('()').split(';')
                if len(coords) == 2:
                    try:
                        x, y = float(coords[0]), float(coords[1])
                        
                        if arena_name_csv not in arenas:
                            arenas[arena_name_csv] = {}
                            hebrew_names[arena_name_csv] = {}
                        arenas[arena_name_csv][target_name] = (x, y)
                        hebrew_names[arena_name_csv][target_name] = hebrew_name
                    except ValueError:
                        print(f"Warning: Could not parse coordinates: {coords}")
            elif len(row) >= 3:
                # Handle old 3-column format for backward compatibility
                arena_name_csv, target_name, coords = row
                # Parse coordinates from string format "(x; y)"
                coords = coords.strip('()').split(';')
                if len(coords) == 2:
                    try:
                        x, y = float(coords[0]), float(coords[1])
                        
                        if arena_name_csv not in arenas:
                            arenas[arena_name_csv] = {}
                            hebrew_names[arena_name_csv] = {}
                        arenas[arena_name_csv][target_name] = (x, y)
                        hebrew_names[arena_name_csv][target_name] = target_name  # Use English name as fallback
                    except ValueError:
                        print(f"Warning: Could not parse coordinates: {coords}")
    return arenas, hebrew_names, hebrew_arena_names

# ---------------------------
# Helper functions
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


def to_screen_coords(pos):
    """Convert arena coordinates (in meters) to screen coordinates (in pixels)."""
    x, y = pos
    screen_x = CENTER_SCREEN[0] + int(x * SCALE)
    screen_y = CENTER_SCREEN[1] - int(y * SCALE)
    return (screen_x, screen_y)

def distance(a, b):
    """Euclidean distance between two points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_arena():
    """Draw the arena border."""
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

def draw_targets(targets, show_names=False, hebrew_names=None):
    """Draw all targets and optionally their names."""
    for target_name, target_pos in targets.items():
        target_screen = to_screen_coords(target_pos)
        pygame.draw.circle(game_surface, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE))
        if show_names:
            font = get_hebrew_font(16)
            # Use Hebrew name if available, otherwise use English name
            display_name = target_name
            if hebrew_names and target_name in hebrew_names:
                display_name = hebrew_names[target_name]
            text = render_hebrew_text(font, display_name, WHITE)
            text_rect = text.get_rect(center=(target_screen[0], target_screen[1] - 35))
            game_surface.blit(text, text_rect)

def draw_annotations(annotations, current_pos=None, typing_active=False, current_name=""):
    """Draw all annotations with their names and highlight current selection."""
    # Draw all previous annotations
    for pos, name in annotations.items():
        if name:  # Only draw if a name has been assigned
            # Parse position from string
            x, y = map(float, pos.split(','))
            target_screen = to_screen_coords((x, y))
            # Draw filled circle for confirmed annotations
            pygame.draw.circle(game_surface, ANNOTATION_COLOR, target_screen, int(ANNOTATION_RADIUS * SCALE))
            font = get_hebrew_font(16)
            text = render_hebrew_text(font, name, WHITE)
            text_rect = text.get_rect(center=(target_screen[0], target_screen[1] - 25))
            game_surface.blit(text, text_rect)
    
    # Draw current selection if it exists
    if current_pos is not None:
        target_screen = to_screen_coords(current_pos)
        # Draw outlined circle for current selection
        pygame.draw.circle(game_surface, ANNOTATION_COLOR, target_screen, int(ANNOTATION_RADIUS * SCALE), 2)
        # Draw a pulsing effect
        pulse_radius = int(ANNOTATION_RADIUS * SCALE * (1 + 0.2 * math.sin(time.time() * 5)))
        pygame.draw.circle(game_surface, ANNOTATION_COLOR, target_screen, pulse_radius, 1)
        
        # Draw current name being typed above the selection
        if typing_active:
            font = get_hebrew_font(16)
            text = render_hebrew_text(font, current_name, WHITE)
            text_rect = text.get_rect(center=(target_screen[0], target_screen[1] - 25))
            game_surface.blit(text, text_rect)

def draw_finished_button():
    """Draw the 'Finished' button."""
    button_rect = pygame.Rect(WIN_WIDTH - 200, WIN_HEIGHT - 50, 120, 40)
    pygame.draw.rect(game_surface, ANNOTATION_COLOR, button_rect)
    font = get_hebrew_font(20)
    text = render_hebrew_text(font, "סיימתי", WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    game_surface.blit(text, text_rect)
    return button_rect

def draw_timer(time_left):
    """Draw the remaining time."""
    font = get_hebrew_font(24)
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    # Draw "Time" label
    label_text = render_hebrew_text(font, "זמן", WHITE)
    # Draw the actual time
    timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
    # Position timer in middle left, next to arena
    timer_x = CENTER_SCREEN[0] - int(ARENA_RADIUS * SCALE) - 100
    timer_y = CENTER_SCREEN[1]
    # Draw label and timer on separate lines
    game_surface.blit(label_text, (timer_x, timer_y))
    game_surface.blit(timer_text, (timer_x, timer_y + 30))

def draw_instruction(text):
    """Draw instruction text at the bottom of the screen."""
    font = get_hebrew_font(20)
    text_surface = render_hebrew_text(font, text, WHITE)
    text_rect = text_surface.get_rect(centerx=WIN_WIDTH//2, bottom=WIN_HEIGHT-30)
    game_surface.blit(text_surface, text_rect)

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
    
    # Draw label
    font = get_hebrew_font(20)
    label_text = render_hebrew_text(font, "תנועה קדימה/אחורה", WHITE)
    game_surface.blit(label_text, (bar_x, bar_y - 25))
    
    # Draw the empty bar (border)
    pygame.draw.rect(game_surface, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    
    # Draw the filled portion only if we should show
    if should_show:
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

    font = get_hebrew_font(20)
    label_text = render_hebrew_text(font, "זווית סיבוב", WHITE)
    label_rect = label_text.get_rect(center=(dial_center[0], dial_center[1] - dial_radius - 15))
    game_surface.blit(label_text, label_rect)

    # Draw the clock circle
    pygame.draw.circle(game_surface, WHITE, dial_center, dial_radius, 2)
    
    # Draw the rotation indicator
    rad = math.radians(angle_rotated)
    end_x = dial_center[0] + dial_radius * math.sin(rad)
    end_y = dial_center[1] - dial_radius * math.cos(rad)
    pygame.draw.line(game_surface, ANNOTATION_COLOR, dial_center, (int(end_x), int(end_y)), 4)
    
    # Draw the angle text with sign
    angle_text = font.render(f"{int(angle_rotated)}°", True, WHITE)
    text_rect = angle_text.get_rect(center=(dial_center[0], dial_center[1] - 10))
    game_surface.blit(angle_text, text_rect)
    
    return angle_rotated  # Return current angle

def draw_feedback(targets, annotations, hebrew_names=None):
    """Draw feedback showing targets and annotations."""
    # Draw arena border
    draw_arena()
    # Draw targets first
    draw_targets(targets, show_names=True, hebrew_names=hebrew_names)
    # Then draw annotations so they appear above targets
    draw_annotations(annotations, None)
    # Draw instruction
    font = get_hebrew_font(20)
    text = render_hebrew_text(font, "עיינ/י בסימונים שלך. לחצ/י RETNE להמשך.", WHITE)
    text_rect = text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT-50))
    game_surface.blit(text, text_rect)

def draw_arena_intro(arena_name, arena_num, total_arenas, num_targets, hebrew_arena_names=None, continuous_log=None, trial_number=None):
    """Draw the arena introduction screen and wait for Enter key press."""
    game_surface.fill(BACKGROUND_COLOR)
    
    # Get Hebrew arena name from CSV data or use English if not found
    hebrew_arena_name = arena_name
    if hebrew_arena_names and arena_name in hebrew_arena_names:
        hebrew_arena_name = hebrew_arena_names[arena_name]
    
    # Draw arena name
    font = get_hebrew_font(36)
    name_text = render_hebrew_text(font, f"זירה: {hebrew_arena_name}", WHITE)
    name_rect = name_text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT//2 - 50))
    game_surface.blit(name_text, name_rect)
    
    # Draw arena number with backslash format (e.g., "זירה 1\2" or "זירה 2\2")
    # Swap order for RTL display: write "2\1" to display as "1\2"
    font = get_hebrew_font(24)
    num_text = render_hebrew_text(font, f"זירה {total_arenas}\\{arena_num}", WHITE)
    num_rect = num_text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT//2))
    game_surface.blit(num_text, num_rect)
    
    # Draw number of targets
    targets_text = render_hebrew_text(font, f"מספר מטרות: {num_targets}", WHITE)
    targets_rect = targets_text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT//2 + 50))
    game_surface.blit(targets_text, targets_rect)
    
    # Draw instruction
    font = get_hebrew_font(20)
    instruction_text = render_hebrew_text(font, "לחצו RETNE כדי להתחיל", WHITE)
    instruction_rect = instruction_text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT//2 + 100))
    game_surface.blit(instruction_text, instruction_rect)
    
    screen.blit(game_surface, (offset_x, offset_y))
    pygame.display.flip()
    
    # Wait for Enter key press
    waiting = True
    print("Arena intro displayed, waiting for Enter key press...")
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:
                    print("'1' or ENTER key pressed, starting arena...")
                    
                    # Log the Enter key press in continuous log if provided
                    if continuous_log is not None:
                        entry = {
                            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                            "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                            "trial": str(trial_number) if trial_number is not None else "",
                            "RoundName": arena_name,
                            "visibility": "none",  # No visibility during intro
                            "phase": "intro",
                            "event": "enter_pressed_start_arena",
                            "x": 0.0,  # No position during intro
                            "y": 0.0,
                            "rotation_angle": 0.0
                        }
                        continuous_log.append(entry)
                    
                    waiting = False
    
    # Clear screen after key press
    screen.fill(BACKGROUND_COLOR)
    pygame.display.flip()

# ---------------------------
# Function to display an instruction image
# ---------------------------
def show_image(image_path, duration=None, continuous_log=None, trial_info=None):
    """Display an image in its original size and wait for Enter key to continue."""
    try:
        image = pygame.image.load(image_path)
        print(f"Successfully loaded image: {image_path}")
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return
    
    # Center the image on the screen
    image_rect = image.get_rect()
    image_rect.center = (screen_width // 2, screen_height // 2)
    
    # Fill screen with background color and display image
    screen.fill(BACKGROUND_COLOR)
    screen.blit(image, image_rect)
    pygame.display.flip()
    
    print("Image displayed, waiting for user input...")
    
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
        print(f"Duration completed ({duration} seconds)")
    else:
        # Wait for 1 or ENTER key press (matching multi_arena.py behavior)
        waiting = True
        print("Press '1' or ENTER to continue...")
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:  # Use 1 or ENTER key
                        print("'1' or ENTER key pressed, continuing...")
                        
                        # Log the Enter key press in continuous log if provided
                        if continuous_log is not None and trial_info is not None:
                            entry = {
                                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                                "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                                "RoundName": trial_info,
                                "visibility": "none",  # No visibility during instruction
                                "phase": "instruction",
                                "event": "enter_pressed_continue",
                                "x": 0.0,  # No position during instruction
                                "y": 0.0,
                                "rotation_angle": 0.0
                            }
                            continuous_log.append(entry)
                        
                        waiting = False
        
        # Only clear screen and continue if not the final instruction
        if "10.png" not in image_path:  # Don't clear screen for thank you screen
            screen.fill(BACKGROUND_COLOR)
            pygame.display.flip()

# ---------------------------
# Function to show fixation cross
# ---------------------------
def show_fixation(duration=6.0, continuous_log=None, trial_counter=None, trial_info=None):
    """Display a fixation cross for the specified duration."""
    show_fixation_image(screen, game_surface, offset_x, offset_y, duration, 
                       "white_on_black", continuous_log, trial_counter, trial_info, BACKGROUND_COLOR)

def draw_trial_counter():
    """Draw the trial counter in the bottom-right corner."""
    if MODE == 'fmri':
        counter_text = f"{current_trial}/{total_trials}"
        counter_font = pygame.font.SysFont("Arial", 24)
        counter_surface = counter_font.render(counter_text, True, WHITE)
        counter_rect = counter_surface.get_rect()
        counter_rect.bottomright = (WIN_WIDTH - 20, WIN_HEIGHT - 20)
        game_surface.blit(counter_surface, counter_rect)

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
        "trial": str(trial_number) if trial_number is not None else "N/A",
        "RoundName": trial_info if trial_info else "error",
        "visibility": "none",
        "phase": "error",
        "event": f"ERROR: {error_message}",
        "x": 0.0,
        "y": 0.0,
        "rotation_angle": 0.0
    }
    continuous_log.append(error_entry)
    print(f"ERROR LOGGED: {error_message} (trial: {trial_number})")

def save_logs(discrete_logs, continuous_logs, player_initials, append=False):
    """Save both discrete and continuous logs to CSV files."""
    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    def _write_csv(filename, fieldnames, rows, use_append):
        """Write rows to CSV respecting append behavior and ensuring header."""
        mode = 'a' if use_append else 'w'
        needs_header = True
        if mode == 'a':
            needs_header = (not os.path.exists(filename)) or (os.path.getsize(filename) == 0)

        with open(filename, mode, newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            if needs_header:
                writer.writeheader()
            if rows:
                writer.writerows(rows)
            elif needs_header and not rows:
                # Ensure header is written even when no rows are provided
                f.flush()

    if MODE == 'fmri':
        # fMRI mode should respect append flag to avoid overwriting continuous logs mid-run
        if discrete_logs or not append:
            _write_csv(
                discrete_filename,
                ["RoundName", "TypedName", "ChosenPosition", "TimeToAnnotation"],
                discrete_logs,
                append
            )
        _write_csv(
            continuous_filename,
            ["RealTime", "trial_time", "trial", "trial_type", "RoundName", "condition_type", "visibility", "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y"],
            continuous_logs,
            append
        )
        if not append:
            print(f"\nLog files created:")
            print(f"Discrete log: {discrete_filename}")
            print(f"Continuous log: {continuous_filename}")
    else:
        # Practice mode: append to keep all arenas in one file
        use_append = append or (MODE == 'practice')

        if discrete_logs or not use_append:
            _write_csv(
                discrete_filename,
                ["RoundName", "TypedName", "ChosenPosition", "TimeToAnnotation"],
                discrete_logs,
                use_append
            )
        _write_csv(
            continuous_filename,
            ["RealTime", "trial_time", "trial", "trial_type", "RoundName", "condition_type", "visibility", "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y"],
            continuous_logs,
            use_append
        )
        if not use_append:
            print(f"\nLog files created:")
            print(f"Discrete log: {discrete_filename}")
            print(f"Continuous log: {continuous_filename}")

def run_arena(arena_name, targets, arena_num, total_arenas, visibility="full", hebrew_names=None, trial_number=None):
    """Run a single arena trial."""
    target_sounds = load_target_sounds(arena_name)
    print(f"\nLoaded {len(target_sounds)} sounds for arena {arena_name}")
    player_pos = [0.0, 0.0]
    player_angle = 0.0
    phase = "exploration"
    exploration_start_time = time.time()  # For annotation timing only
    annotation_start_time = None
    found_targets = set()
    annotations = {}
    current_annotation_pos = None
    current_annotation_name = ""
    typing_active = False
    beep_channel = None
    target_audio_channel = None  # Separate channel for target sounds
    global audio_channel  # Use global audio_channel for beep sounds
    # Track which targets the player is currently inside
    currently_inside_targets = set()
    continuous_log = []
    discrete_log = []
    distance_moved = 0.0
    angle_rotated = 0.0
    last_pos = [0.0, 0.0]
    last_angle = 0.0
    is_moving_forward_backward = False
    is_rotating = False
    rotation_start_angle = None
    movement_stop_time = None
    rotation_stop_time = None
    last_log_time = time.time()
    LOG_INTERVAL = 0.1
    # Track initial visibility state
    trial_started = False
    first_movement_occurred = False
    # Set exploration time based on mode
    if MODE == 'practice':
        # Practice mode: Same TR-aligned durations as fMRI mode
        EXPLORATION_TRs = 60  # 60 TRs = 120.6 seconds
        exploration_time = EXPLORATION_TRs * TR
        # Annotation time: 2 minutes aligned to TRs
        ANNOTATION_TRs = 60  # 60 TRs = 120.6 seconds
        annotation_time = ANNOTATION_TRs * TR
    else:
        # fMRI mode: Use TR-aligned durations
        # Convert to TRs: 120 seconds = 60 TRs, use 60 TRs for exploration
        EXPLORATION_TRs = 60  # 60 TRs = 120.6 seconds
        exploration_time = EXPLORATION_TRs * TR
        # Annotation time: 2 minutes aligned to TRs
        ANNOTATION_TRs = 60  # 60 TRs = 120.6 seconds
        annotation_time = ANNOTATION_TRs * TR
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time()
        experiment_time = current_time - EXPERIMENT_START_TIME
        if experiment_time - (last_log_time - EXPERIMENT_START_TIME) >= LOG_INTERVAL:
            log_entry = {
                "RoundName": arena_name,
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": round(current_time - EXPERIMENT_START_TIME, 3),
                "visibility": visibility,
                "phase": phase,
                "event": "",
                "x": round(player_pos[0], 3),
                "y": round(player_pos[1], 3),
                "rotation_angle": round(player_angle, 3)
            }
            continuous_log.append(log_entry)
            save_logs([], [log_entry], player_initials, append=True)
            last_log_time = current_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_log = {
                    "RoundName": arena_name,
                    "RealTime": round(time.time() - EXPERIMENT_START_TIME, 3),
                    "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                    "trial": str(trial_number) if trial_number is not None else "",
                    "visibility": visibility,
                    "phase": phase,
                    "event": "quit",
                    "x": round(player_pos[0], 3),
                    "y": round(player_pos[1], 3),
                    "rotation_angle": round(player_angle, 3)
                }
                continuous_log.append(quit_log)
                save_logs([], [quit_log], player_initials, append=True)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit_log = {
                        "RoundName": arena_name,
                        "RealTime": round(time.time() - EXPERIMENT_START_TIME, 3),
                        "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                        "visibility": visibility,
                        "phase": phase,
                        "event": "quit",
                        "x": round(player_pos[0], 3),
                        "y": round(player_pos[1], 3),
                        "rotation_angle": round(player_angle, 3)
                    }
                    continuous_log.append(quit_log)
                    save_logs([], [quit_log], player_initials, append=True)
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_ESCAPE and phase == "annotation" and typing_active:
                    typing_active = False
                    current_annotation_pos = None
                    current_annotation_name = ""

                elif event.key == pygame.K_5:
                    global SHOW_TARGETS_DEBUG, SHOW_ARENA_DEBUG
                    SHOW_TARGETS_DEBUG = not SHOW_TARGETS_DEBUG
                    SHOW_ARENA_DEBUG = not SHOW_ARENA_DEBUG
                    print(f"Debug mode: Targets={'ON' if SHOW_TARGETS_DEBUG else 'OFF'}, Arena={'ON' if SHOW_ARENA_DEBUG else 'OFF'}")
                elif event.key == pygame.K_2:  # Use 2 key to skip timer (debugging)
                    if phase == "exploration":
                        # Skip timer by setting exploration time to 0
                        exploration_start_time = time.time() - exploration_time
                elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:  # Use 1 or ENTER key for annotation functionality
                    if phase == "annotation":
                        if current_annotation_pos is None:
                            current_annotation_pos = (player_pos[0], player_pos[1])
                            typing_active = True
                            current_annotation_name = ""
                        elif typing_active:
                            if current_annotation_name:
                                pos_key = f"{current_annotation_pos[0]:.3f},{current_annotation_pos[1]:.3f}"
                                if pos_key not in annotations:
                                    annotations[pos_key] = current_annotation_name
                                    discrete_entry = {
                                        "RoundName": arena_name,
                                        "TypedName": current_annotation_name,
                                        "ChosenPosition": pos_key,
                                        "TimeToAnnotation": round(time.time() - annotation_start_time, 3)
                                    }
                                    discrete_log.append(discrete_entry)
                                    save_logs([discrete_entry], [], player_initials, append=True)
                                    annotation_log = {
                                        "RoundName": arena_name,
                                        "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                                        "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                                        "trial": str(trial_number) if trial_number is not None else "",
                                        "phase": phase,
                                        "event": f"{current_annotation_name}_annotated",
                                        "x": round(player_pos[0], 3),
                                        "y": round(player_pos[1], 3),
                                        "rotation_angle": round(player_angle, 3)
                                    }
                                    continuous_log.append(annotation_log)
                                    save_logs([], [annotation_log], player_initials, append=True)
                                typing_active = False
                                current_annotation_pos = None
                    elif phase == "feedback":
                        # Hide cursor when transitioning to feedback phase
                        pygame.mouse.set_visible(False)
                        return discrete_log, continuous_log
                elif phase == "annotation" and typing_active:
                    if event.key == pygame.K_BACKSPACE:
                        current_annotation_name = current_annotation_name[:-1]
                    elif event.unicode.isprintable():
                        current_annotation_name += event.unicode
            
            # Handle mouse clicks for the Finished button
            if event.type == pygame.MOUSEBUTTONDOWN and phase == "annotation":
                mouse_pos = pygame.mouse.get_pos()
                # Adjust mouse position for screen offset
                adjusted_mouse_pos = (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y)
                if finished_button_rect.collidepoint(adjusted_mouse_pos):
                    # If user is typing an annotation, save it before finishing
                    if typing_active and current_annotation_name:
                        pos_key = f"{current_annotation_pos[0]:.3f},{current_annotation_pos[1]:.3f}"
                        if pos_key not in annotations:
                            annotations[pos_key] = current_annotation_name
                            discrete_entry = {
                                "RoundName": arena_name,
                                "TypedName": current_annotation_name,
                                "ChosenPosition": pos_key,
                                "TimeToAnnotation": round(time.time() - annotation_start_time, 3)
                            }
                            discrete_log.append(discrete_entry)
                            save_logs([discrete_entry], [], player_initials, append=True)
                            annotation_log = {
                                "RoundName": arena_name,
                                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                                "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                                "trial": str(trial_number) if trial_number is not None else "",
                                "phase": phase,
                                "event": f"{current_annotation_name}_annotated",
                                "x": round(player_pos[0], 3),
                                "y": round(player_pos[1], 3),
                                "rotation_angle": round(player_angle, 3)
                            }
                            continuous_log.append(annotation_log)
                            save_logs([], [annotation_log], player_initials, append=True)
                        typing_active = False
                        current_annotation_pos = None
                    # Log finish button press
                    finish_log = {
                        "RoundName": arena_name,
                        "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                        "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                        "trial": str(trial_number) if trial_number is not None else "",
                        "visibility": visibility,
                        "phase": "annotation",
                        "event": "finish_press",
                        "x": round(player_pos[0], 3),
                        "y": round(player_pos[1], 3),
                        "rotation_angle": round(player_angle, 3)
                    }
                    continuous_log.append(finish_log)
                    # Save only the finish_log; discrete entries were already appended when created
                    save_logs([], [finish_log], player_initials, append=True)
                    if MODE == 'fmri':
                        running = False
                    else:
                        phase = "feedback"
                        feedback_start_time = time.time()
        
        # Handle movement with number keys - compatible with MRI control box
        keys = pygame.key.get_pressed()
        
        if phase in ["exploration", "annotation"]:
            old_pos = list(player_pos)  # Store old position
            old_angle = player_angle    # Store old angle
            
            # Rotation controls
            if keys[pygame.K_6]:  # Rotate left
                player_angle = (player_angle - ROTATE_SPEED * dt) % 360
                # Reset rotation tracking if starting new rotation
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle
            if keys[pygame.K_9]:  # Rotate right
                player_angle = (player_angle + ROTATE_SPEED * dt) % 360
                # Reset rotation tracking if starting new rotation
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle
                
            # Movement controls
            if keys[pygame.K_7]:  # Move forward
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
                    # Reset movement tracking if starting new movement
                    if not is_moving_forward_backward or movement_stop_time is not None:
                        distance_moved = 0.0
                        movement_stop_time = None
                    is_moving_forward_backward = True
                    
            if keys[pygame.K_8]:  # Move backward
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] - dx
                new_y = player_pos[1] - dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
                    # Reset movement tracking if starting new movement
                    if not is_moving_forward_backward or movement_stop_time is not None:
                        distance_moved = 0.0
                        movement_stop_time = None
                    is_moving_forward_backward = True
            
            # Update movement tracking
            if is_moving_forward_backward:
                # Calculate distance moved (forward/backward only)
                distance_moved += math.hypot(player_pos[0] - old_pos[0], player_pos[1] - old_pos[1])
                # Mark first movement occurred
                if not first_movement_occurred:
                    first_movement_occurred = True
                    print("First movement detected - hiding arena and avatar")
            
            # Update rotation tracking with signed values
            if is_rotating and rotation_start_angle is not None:
                # Calculate the angle difference from when rotation started
                angle_diff = player_angle - rotation_start_angle
                # Normalize angle difference to be between -180 and 180 degrees
                while angle_diff > 180:
                    angle_diff -= 360
                while angle_diff < -180:
                    angle_diff += 360
                angle_rotated = angle_diff
            
            # Reset movement tracking when movement stops
            if not (keys[pygame.K_7] or keys[pygame.K_8]):
                if is_moving_forward_backward:
                    movement_stop_time = current_time
                is_moving_forward_backward = False
            else:
                movement_stop_time = None

            # Reset rotation tracking when rotation stops
            if not (keys[pygame.K_6] or keys[pygame.K_9]):
                if is_rotating:  # Only set stop time if we were rotating
                    rotation_stop_time = current_time
                is_rotating = False
                rotation_start_angle = None
                # Don't reset angle_rotated here - keep it for fade-out period
            else:
                rotation_stop_time = None  # Reset stop time when rotating

            # Reset indicators after fade time elapses
            if movement_stop_time is not None and current_time - movement_stop_time > MOVEMENT_FADE_TIME:
                distance_moved = 0.0
                movement_stop_time = None

            if rotation_stop_time is not None and current_time - rotation_stop_time > MOVEMENT_FADE_TIME:
                angle_rotated = 0.0  # Only reset angle after fade time elapses
                rotation_stop_time = None
        
        # Check border collision
        if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
            if beep_sound is not None:
                if audio_channel is None or not audio_channel.get_busy():
                    audio_channel = beep_sound.play(loops=-1)
        else:
            if audio_channel is not None:
                audio_channel.stop()
                audio_channel = None
        
        # Check target encounters
        if phase == "exploration":
            for target_name, target_pos in targets.items():
                if distance(player_pos, target_pos) <= TARGET_RADIUS:
                    # Check if this is a new entry (player just entered the target area)
                    if target_name not in currently_inside_targets:
                        # Player just entered this target area
                        currently_inside_targets.add(target_name)
                        
                        # Log first encounter only
                        if target_name not in found_targets:
                            found_targets.add(target_name)
                            encounter_log = {
                                "RoundName": arena_name,
                                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                                "trial_time": round(current_time - EXPERIMENT_START_TIME, 3),
                                "visibility": visibility,
                                "phase": "exploration",
                                "event": f"found_{target_name}",
                                "x": round(player_pos[0], 3),
                                "y": round(player_pos[1], 3),
                                "rotation_angle": round(player_angle, 3)
                            }
                            continuous_log.append(encounter_log)
                            save_logs([], [encounter_log], player_initials, append=True)
                        
                        # Play sound every time player enters the target area
                        target_name_lower = target_name.lower()
                        if target_name_lower in target_sounds:
                            try:
                                # Use a separate channel for target sounds to avoid conflicts with beep
                                if target_audio_channel is None or not target_audio_channel.get_busy():
                                    target_audio_channel = target_sounds[target_name_lower].play()
                                    print(f"Playing sound for {target_name}")
                                else:
                                    # If channel is busy, stop current sound and play new one
                                    target_audio_channel.stop()
                                    target_audio_channel = target_sounds[target_name_lower].play()
                                    print(f"Playing sound for {target_name} (replaced previous)")
                            except Exception as e:
                                print(f"Error playing sound for {target_name}: {e}")
                        else:
                            print(f"Warning: No sound found for {target_name} (tried {target_name_lower})")
                else:
                    # Player is outside this target - mark as not inside anymore
                    if target_name in currently_inside_targets:
                        currently_inside_targets.remove(target_name)
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        game_surface.fill(BACKGROUND_COLOR)
        
        if phase == "exploration":
            # Handle visibility conditions based on visibility parameter
            if visibility == "full":
                # Full visibility: Always show avatar and border
                draw_arena()
                draw_player_avatar(player_pos, player_angle)
            elif visibility == "limited":
                # Limited visibility: Show avatar and border at start, then only when near border
                if not first_movement_occurred or math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            else:
                # No visibility: Show avatar and border at start, then hide after first movement
                if not first_movement_occurred:
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            
            # Show arena and avatar when 9 key is pressed (debug mode)
            if SHOW_ARENA_DEBUG:
                draw_arena()
                draw_player_avatar(player_pos, player_angle)
            
            # Show targets when 9 key is pressed
            if SHOW_TARGETS_DEBUG:
                draw_targets(targets, show_names=True, hebrew_names=hebrew_names)
            
            # Draw movement indicators with fade-out behavior
            if is_moving_forward_backward or (movement_stop_time is not None and 
                current_time - movement_stop_time <= MOVEMENT_FADE_TIME):
                distance_moved = draw_thermometer(distance_moved, is_moving_forward_backward, 
                               movement_stop_time, current_time)
            if is_rotating or (rotation_stop_time is not None and 
                current_time - rotation_stop_time <= MOVEMENT_FADE_TIME):
                angle_rotated = draw_clock(angle_rotated, is_rotating, rotation_stop_time, current_time)
            
            # Draw timer
            time_left = exploration_time - (current_time - exploration_start_time)
            if time_left > 0:
                draw_timer(time_left)
            else:
                # Reset position and angle BEFORE logging phase change
                player_pos = [0.0, 0.0]
                player_angle = 0.0
                phase = "annotation"
                annotation_start_time = time.time()
                
                # Show cursor for annotation phase
                pygame.mouse.set_visible(True)
                
                phase_change_log = {
                    "RoundName": arena_name,
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                    "visibility": visibility,
                    "phase": phase,
                    "event": "phase_change",
                    "x": round(player_pos[0], 3),
                    "y": round(player_pos[1], 3),
                    "rotation_angle": round(player_angle, 3)
                }
                continuous_log.append(phase_change_log)
                save_logs([], [phase_change_log], player_initials, append=True)
        
        elif phase == "annotation":
            # In annotation phase, always show avatar and border
            draw_arena()
            draw_player_avatar(player_pos, player_angle)
            # Show targets when 9 key is pressed
            if SHOW_TARGETS_DEBUG:
                draw_targets(targets, show_names=True, hebrew_names=hebrew_names)
            draw_annotations(annotations, current_annotation_pos, typing_active, current_annotation_name)
            
            # Show cursor during annotation phase for better interaction
            pygame.mouse.set_visible(True)
            
            # Draw movement indicators with fade-out behavior
            if is_moving_forward_backward or (movement_stop_time is not None and 
                current_time - movement_stop_time <= MOVEMENT_FADE_TIME):
                distance_moved = draw_thermometer(distance_moved, is_moving_forward_backward, 
                               movement_stop_time, current_time)
            if is_rotating or (rotation_stop_time is not None and 
                current_time - rotation_stop_time <= MOVEMENT_FADE_TIME):
                angle_rotated = draw_clock(angle_rotated, is_rotating, rotation_stop_time, current_time)
            
            # Draw Finished button
            finished_button_rect = draw_finished_button()
            
            # Check annotation time limit (fMRI mode only)
            if MODE == 'fmri':
                annotation_time_left = annotation_time - (current_time - annotation_start_time)
                if annotation_time_left > 0:
                    draw_timer(annotation_time_left)
                else:
                    # fMRI: end trial immediately (no feedback phase)
                    phase_change_log = {
                        "RoundName": arena_name,
                        "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                        "trial_time": round(time.time() - EXPERIMENT_START_TIME, 3),
                        "visibility": visibility,
                        "phase": "annotation",
                        "event": "annotation_time_elapsed",
                        "x": round(player_pos[0], 3),
                        "y": round(player_pos[1], 3),
                        "rotation_angle": round(player_angle, 3)
                    }
                    continuous_log.append(phase_change_log)
                    save_logs([], [phase_change_log], player_initials, append=True)
                    
                    # Hide cursor when trial ends
                    pygame.mouse.set_visible(False)
                    running = False
            
            if typing_active:
                draw_instruction("הקלד/י את שם המטרה ולחצ/י RETNE לאישור")
            else:
                draw_instruction("נווט/י למיקום אחת המטרות ולחצ/י RETNE כדי לסמן אותה")
        
        elif phase == "feedback" and MODE != 'fmri':
            draw_feedback(targets, annotations, hebrew_names)
            
            # Check for ENTER or 1 key to end feedback phase
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_1:
                        # End feedback phase and finish trial
                        running = False
                        break
        
        # Draw trial counter
        draw_trial_counter()
        
        # Draw debug mode indicators
        if SHOW_TARGETS_DEBUG or SHOW_ARENA_DEBUG:
            font = get_hebrew_font(16)
            debug_text = []
            if SHOW_TARGETS_DEBUG:
                debug_text.append("TARGETS VISIBLE")
            if SHOW_ARENA_DEBUG:
                debug_text.append("ARENA VISIBLE")
            
            debug_display = " | ".join(debug_text)
            debug_surface = font.render(debug_display, True, (0, 255, 0))
            game_surface.blit(debug_surface, (10, WIN_HEIGHT - 50))
        
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()
    
    # Stop all sounds when trial ends
    if beep_channel is not None:
        beep_channel.stop()
    if target_audio_channel is not None:
        target_audio_channel.stop()
    if audio_channel is not None:
        audio_channel.stop()
    
    # Hide cursor when trial ends
    pygame.mouse.set_visible(False)
    
    return discrete_log, continuous_log

def run_multi_arena_experiment():
    """Run the multi-arena experiment with mode-specific behavior."""
    
    print(f"Starting Multi-Arena Experiment")
    print(f"Mode: {MODE}")
    print(f"Participant: {player_initials}")
    print(f"Arena: {arena_name}")
    print(f"Visibility: {visibility_mode}")
    if MODE == 'fmri':
        print(f"Run: {run_number}")
        print(f"Trial: {current_trial}/{total_trials}")
    
    print(f"Pygame display info: {pygame.display.Info()}")
    print(f"Screen size: {screen.get_size()}")
    print(f"Game surface size: {game_surface.get_size()}")
    
    # Initialize logging early (before trigger wait) for error handling
    # This will be used for fMRI mode; practice mode uses practice_continuous_log
    continuous_log = []
    trial_info = f"{arena_name}_test_run{run_number}" if MODE == 'fmri' else None
    
    # Initialize trigger manager if scanning is enabled
    trigger_manager = TriggerManager(scanning=scanning, com_port=com_port)
    if scanning:
        if not trigger_manager.init_trigger():
            error_msg = "Failed to initialize trigger connection"
            print(f"CRITICAL: {error_msg}. Exiting.")
            # Log error to continuous log
            log_error_to_continuous_log(continuous_log, error_msg, current_trial, trial_info)
            try:
                save_logs([], continuous_log, player_initials, append=False)
                print(f"Error logged to: {continuous_filename}")
            except Exception as e:
                print(f"Warning: Could not save error log: {e}")
            trigger_manager.close_trigger()
            sys.exit(1)
    
    # Load arena data
    arenas, hebrew_names, hebrew_arena_names = load_arena_data()
    
    # Special cases that don't need arena data
    if arena_name in ['thank_you', 'instructions']:
        targets = []  # Empty targets for special cases
        arena_hebrew_names = {}
    else:
        # Check if the specified arena exists
        if arena_name not in arenas:
            print(f"Error: Arena '{arena_name}' not found in arena data")
            return
        
        targets = arenas[arena_name]
        arena_hebrew_names = hebrew_names.get(arena_name, {})
    
    # Show instructions based on mode
    INSTRUCTIONS_DIR = os.path.join(os.path.dirname(__file__), "Instructions-he")
    
    if MODE == 'practice':
        # Create continuous log for practice mode
        practice_continuous_log = []
        
        # Special case: Show thank you screen
        if arena_name == 'thank_you':
            print("Showing thank you screen...")
            show_image(os.path.join(INSTRUCTIONS_DIR, "10.png"), continuous_log=practice_continuous_log, trial_info=f"{arena_name}_practice")
            return
        
        # Special case: Show instructions only
        if arena_name == 'instructions':
            print(f"Showing instructions for {visibility_mode} visibility...")
            instruction_path = ""
            if visibility_mode == 'full':
                instruction_path = os.path.join(INSTRUCTIONS_DIR, "7.png")
            elif visibility_mode == 'limited':
                instruction_path = os.path.join(INSTRUCTIONS_DIR, "77.png")
            elif visibility_mode == 'none':
                instruction_path = os.path.join(INSTRUCTIONS_DIR, "777.png")
            
            print(f"Loading instruction image: {instruction_path}")
            if os.path.exists(instruction_path):
                print("Instruction image found, displaying...")
                show_image(instruction_path, continuous_log=practice_continuous_log, trial_info=f"{visibility_mode}_instructions")
                print("Instruction display completed.")
            else:
                print(f"Error: Instruction image not found: {instruction_path}")
            return
        
        # Practice mode: Single trial with specified visibility (no instructions)
        print(f"Running practice trial with {visibility_mode} visibility...")
        
        # Show arena intro screen before running the arena
        draw_arena_intro(arena_name, arena_number, arenas_per_condition, len(targets), hebrew_arena_names, continuous_log=practice_continuous_log)
        
        # Run single trial without showing instructions
        discrete_log, continuous_log = run_arena(f"{arena_name}_practice", targets, 1, 1, visibility=visibility_mode, hebrew_names=arena_hebrew_names)
        
        # In practice mode, all discrete and continuous entries were incrementally appended during the trial.
        # Avoid bulk re-saving to prevent duplicates.
        # Save nothing here.
        
    elif MODE == 'fmri':
        # fMRI mode: Wait for trigger before starting trial
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
                log_error_to_continuous_log(continuous_log, error_msg, current_trial, trial_info)
                try:
                    save_logs([], continuous_log, player_initials, append=False)
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
        
        # Show fixation at start - 8 TRs for first trial (4 TRs dummy + 4 TRs trial), 4 TRs for subsequent trials
        if current_trial == 1:
            fixation_trs = 8
            print('Fixation: 8 TRs (4 dummy + 4 trial 1)')
        else:
            fixation_trs = 4
            print(f'Fixation: 4 TRs (trial {current_trial})')
        
        # Create fixation log entries to be added to the continuous log
        fixation_logs = []
        
        # Log trigger received event - always log when we have a trigger time
        # When scanning is enabled, we always wait for and receive a trigger for each trial
        if trigger_time_value is not None:
            trigger_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": 0.0,
                "trial": str(current_trial),
                "trial_type": "FA",  # Add missing field
                "RoundName": f"{arena_name}_test_run{run_number}",
                "condition_type": "",  # Add missing field
                "visibility": "none",
                "phase": "trigger",
                "event": "trigger_received",
                "x": 0.0,
                "y": 0.0,
                "rotation_angle": 0.0,
                "score": "",  # Add missing field
                "target_x": "",  # Add missing field
                "target_y": ""  # Add missing field
            }
            fixation_logs.append(trigger_entry)
            print(f"Logged trigger received at time: {trigger_time_value:.3f} (trial {current_trial})")
        elif scanning:
            # This should never happen when scanning is enabled (we wait for trigger)
            print(f"WARNING: Scanning enabled but no trigger time available for trial {current_trial}")
        
        # Show fixation for the determined number of TRs (no frame-by-frame logging)
        # show_fixation_image() will handle logging fixation_start and fixation_end
        # trial_info already defined earlier
        fixation_duration = fixation_trs * TR
        show_fixation_image(screen, game_surface, offset_x, offset_y, fixation_duration, 
                           "white_on_black", fixation_logs, current_trial, trial_info, BACKGROUND_COLOR)
        
        # Add RoundName, visibility, and trial number to the fixation entries that were just logged by show_fixation_image()
        # (fixation_utils.py doesn't handle these fields, so we add them here)
        if fixation_logs:
            # Find the last two entries (fixation_start and fixation_end) and add RoundName, visibility, and trial
            for entry in fixation_logs[-2:]:
                if entry.get("event") in ["fixation_start", "fixation_end"]:
                    entry["RoundName"] = trial_info
                    entry["visibility"] = "none"
                    entry["trial"] = str(current_trial)
        
        print(f"Fixation complete.")
        
        print('Fixation complete. Showing instruction for 1 TR...')
        show_image(os.path.join(INSTRUCTIONS_DIR, "8.png"), duration=TR, continuous_log=fixation_logs, trial_info=trial_info)
        
        # fMRI mode: 1 test trial only (no visibility)
        print("Running fMRI test trial...")
        
        # Show arena intro screen before running the arena
        draw_arena_intro(arena_name, multi_arena_trial_number, total_multi_arena_trials, len(targets), hebrew_arena_names, continuous_log=fixation_logs, trial_number=current_trial)
        
        trial_start_time = time.time()
        discrete_log, continuous_log = run_arena(f"{arena_name}_test_run{run_number}", targets, 1, 1, visibility="no_visibility", hebrew_names=arena_hebrew_names, trial_number=current_trial)
        
        # Add fixation logs (including trigger events) to the beginning of continuous_log
        continuous_log = fixation_logs + continuous_log
        print(f"Added {len(fixation_logs)} fixation/trigger log entries to continuous log (trial {current_trial})")
        
        # For non-final trials, we need to overwrite the file with the complete log including fixation_logs
        # because run_arena() wrote incrementally with append=True, but we need the trigger entries at the start
        if current_trial != total_trials:
            # Save complete log (including fixation_logs) with append=False to overwrite the file
            save_logs(discrete_log, continuous_log, player_initials, append=False)
            print(f"Saved complete log with trigger entries for trial {current_trial}")
        
        # Note: TR alignment is no longer needed since we wait for triggers before each trial
        # The trigger ensures trials start at TR boundaries, so no alignment is necessary
        
        if current_trial == total_trials:
            # Only show final fixation and thank you screen for the last trial
            if current_trial == total_trials:
                # Final trial: Show 4 TRs fixation followed by thank you screen
                print('Final fixation: 4 TRs')
                
                # Log final fixation start event
                final_fixation_start_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": time.time() - trial_start_time,
                    "trial": str(current_trial),
                    "RoundName": trial_info,
                    "visibility": "none",
                    "phase": "fixation",
                    "event": "final_fixation_start",
                    "x": 0.0,
                    "y": 0.0,
                    "rotation_angle": 0.0
                }
                continuous_log.append(final_fixation_start_entry)
                
                # Show 4 TRs fixation
                final_fixation_duration = 4 * TR
                show_fixation_image(screen, game_surface, offset_x, offset_y, final_fixation_duration, 
                                   "white_on_black", None, None, None, BACKGROUND_COLOR)
                
                # Log final fixation end event
                final_fixation_end_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": time.time() - trial_start_time,
                    "trial": str(current_trial),
                    "RoundName": trial_info,
                    "visibility": "none",
                    "phase": "fixation",
                    "event": "final_fixation_end",
                    "x": 0.0,
                    "y": 0.0,
                    "rotation_angle": 0.0
                }
                continuous_log.append(final_fixation_end_entry)
                print(f"Final fixation complete.")
                
                # Save logs immediately after final_fixation_end (before thank you screen)
                # This ensures the log ends with final_fixation_end
                save_logs(discrete_log, continuous_log, player_initials)
                
                # Show thank you screen (without logging to avoid entries after final_fixation_end)
                print("Showing thank you screen...")
                show_image(os.path.join(INSTRUCTIONS_DIR, "10.png"), continuous_log=None, trial_info=None)
            else:
                print(f"Trial {current_trial}/{total_trials} complete - no final fixation or thank you screen (not final trial).")
                # Logs already saved above for non-final trials, no need to save again
    
    print(f"Multi-arena experiment complete!")
    if MODE == 'fmri':
        print(f"Trial {current_trial}/{total_trials} completed")
    print(f"Data saved to: {continuous_filename}")
    
    # Close trigger connection if scanning
    if scanning and trigger_manager is not None:
        trigger_manager.close_trigger()

if __name__ == "__main__":
    run_multi_arena_experiment()
    pygame.quit()
    sys.exit() 