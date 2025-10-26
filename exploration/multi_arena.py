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
TR = 2.01  # Fixed TR for fMRI experiments

# Calculate multi-arena trial number for fMRI mode
if MODE == 'fmri':
    # In fMRI mode, trials alternate: snake, multi_arena, snake, multi_arena, etc.
    # Multi-arena trials occur at positions 2, 4, 6, 8, 10, 12
    # So trial 2 = multi-arena trial 1, trial 4 = multi-arena trial 2, etc.
    multi_arena_trial_number = (current_trial + 1) // 2
    total_multi_arena_trials = 6  # There are 6 multi-arena trials in the run
else:
    multi_arena_trial_number = 1
    total_multi_arena_trials = 1

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
    continuous_filename = os.path.join(results_dir, f"{player_initials}_FA_fa{current_trial}_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_FA_fa{current_trial}_discrete.csv")
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
# Sound paths (portable)
# ---------------------------
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")

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

# Create display based on screen parameter
if screen_number is not None:
    # Use specified screen number
    try:
        # Set the display environment variable for pygame
        os.environ['DISPLAY'] = f':0.{screen_number}'
        print(f"Setting display to screen {screen_number}")
        
        # Create fullscreen display on specified screen
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        print(f"Fullscreen mode on screen {screen_number}: {screen_width}x{screen_height}")
    except Exception as e:
        print(f"Failed to use specified screen {screen_number}, falling back to default: {e}")
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
else:
    # Use default fullscreen behavior
    try:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        print(f"Fullscreen mode (default): {screen_width}x{screen_height}")
    except Exception as e:
        print(f"Fullscreen failed, using windowed mode: {e}")
        screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        screen_width = WIN_WIDTH
        screen_height = WIN_HEIGHT

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

def draw_arena_intro(arena_name, arena_num, total_arenas, num_targets, hebrew_arena_names=None, continuous_log=None):
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
    
    # Draw arena number
    font = get_hebrew_font(24)
    num_text = render_hebrew_text(font, f"זירה {arena_num} מתוך {total_arenas}", WHITE)
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
    screen.fill(BACKGROUND_COLOR)
    game_surface.fill(BACKGROUND_COLOR)
    
    # Draw fixation cross using standardized format (200px text size equivalent)
    # Use font rendering for consistent appearance with PTSOD
    font = pygame.font.SysFont("Arial", 200)
    fixation_text = font.render('+', True, WHITE)
    text_rect = fixation_text.get_rect(center=CENTER_SCREEN)
    
    game_surface.blit(fixation_text, text_rect)
    screen.blit(game_surface, (offset_x, offset_y))
    pygame.display.flip()
    
    # Log fixation start event if continuous_log is provided
    if continuous_log is not None:
        fixation_start_time = time.time()
        entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": 0.0,  # Fixation is before trial starts
            "RoundName": trial_info if trial_info else "fixation",
            "visibility": "none",  # No visibility during fixation
            "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0,  # No position during fixation
            "y": 0.0,
            "rotation_angle": 0.0
        }
        continuous_log.append(entry)
    
    # Wait for specified duration
    start_time = time.time()
    while time.time() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_2:  # '2' key to skip fixation
                    print("Fixation skipped by '2' key press")
                    # Log fixation end event if continuous_log is provided
                    if continuous_log is not None:
                        entry = {
                            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                            "trial_time": time.time() - start_time,
                            "RoundName": trial_info if trial_info else "fixation",
                            "visibility": "none",
                            "phase": "fixation",
                            "event": "fixation_skipped",
                            "x": 0.0,
                            "y": 0.0,
                            "rotation_angle": 0.0
                        }
                        continuous_log.append(entry)
                    return
        clock.tick(15)
    
    # Log fixation end event if continuous_log is provided
    if continuous_log is not None:
        entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": duration,
            "RoundName": trial_info if trial_info else "fixation",
            "visibility": "none",
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0
        }
        continuous_log.append(entry)

def draw_trial_counter():
    """Draw the trial counter in the bottom-right corner."""
    if MODE == 'fmri':
        counter_text = f"{current_trial}/{total_trials}"
        counter_font = pygame.font.SysFont("Arial", 24)
        counter_surface = counter_font.render(counter_text, True, WHITE)
        counter_rect = counter_surface.get_rect()
        counter_rect.bottomright = (WIN_WIDTH - 20, WIN_HEIGHT - 20)
        game_surface.blit(counter_surface, counter_rect)

def save_logs(discrete_logs, continuous_logs, player_initials, append=False):
    """Save both discrete and continuous logs to CSV files."""
    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # For fMRI mode, always write to single files (no appending)
    if MODE == 'fmri':
        # Open files for writing with UTF-8 encoding to handle Hebrew characters
        with open(discrete_filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["RoundName", "TypedName", "ChosenPosition", "TimeToAnnotation"])
            writer.writeheader()
            writer.writerows(discrete_logs)
        with open(continuous_filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["RealTime", "trial_time", "RoundName", "visibility", "phase", "event", "x", "y", "rotation_angle"])
            writer.writeheader()
            writer.writerows(continuous_logs)
        print(f"\nLog files created:")
        print(f"Discrete log: {discrete_filename}")
        print(f"Continuous log: {continuous_filename}")
    else:
        # Practice mode: append to keep all arenas in one file
        use_append = append or (MODE == 'practice')
        
        # Open files for appending or writing with UTF-8 encoding to handle Hebrew characters
        with open(discrete_filename, 'a' if use_append else 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["RoundName", "TypedName", "ChosenPosition", "TimeToAnnotation"])
            needs_header = (not os.path.exists(discrete_filename)) or (os.path.getsize(discrete_filename) == 0)
            if (not use_append) or needs_header:
                writer.writeheader()
            writer.writerows(discrete_logs)
        with open(continuous_filename, 'a' if use_append else 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["RealTime", "trial_time", "RoundName", "visibility", "phase", "event", "x", "y", "rotation_angle"])
            needs_header = (not os.path.exists(continuous_filename)) or (os.path.getsize(continuous_filename) == 0)
            if (not use_append) or needs_header:
                writer.writeheader()
            writer.writerows(continuous_logs)
        if not use_append:
            print(f"\nLog files created:")
            print(f"Discrete log: {discrete_filename}")
            print(f"Continuous log: {continuous_filename}")

def run_arena(arena_name, targets, arena_num, total_arenas, visibility="full", hebrew_names=None):
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
        # Annotation time: 1 minute aligned to TRs
        ANNOTATION_TRs = 30  # 30 TRs = 60.3 seconds
        annotation_time = ANNOTATION_TRs * TR
    else:
        # fMRI mode: Use TR-aligned durations
        # Convert to TRs: 120 seconds = 60 TRs, use 60 TRs for exploration
        EXPLORATION_TRs = 60  # 60 TRs = 120.6 seconds
        exploration_time = EXPLORATION_TRs * TR
        # Annotation time: 1 minute aligned to TRs
        ANNOTATION_TRs = 30  # 30 TRs = 60.3 seconds
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
            if keys[pygame.K_7]:  # Rotate left
                player_angle = (player_angle - ROTATE_SPEED * dt) % 360
                # Reset rotation tracking if starting new rotation
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle
            if keys[pygame.K_0]:  # Rotate right
                player_angle = (player_angle + ROTATE_SPEED * dt) % 360
                # Reset rotation tracking if starting new rotation
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle
                
            # Movement controls
            if keys[pygame.K_8]:  # Move forward
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
                    
            if keys[pygame.K_9]:  # Move backward
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
            if not (keys[pygame.K_8] or keys[pygame.K_9]):
                if is_moving_forward_backward:
                    movement_stop_time = current_time
                is_moving_forward_backward = False
            else:
                movement_stop_time = None

            # Reset rotation tracking when rotation stops
            if not (keys[pygame.K_7] or keys[pygame.K_0]):
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
    
    # Trigger handling moved to MATLAB level
    trigger_manager = None
    
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
        # fMRI mode: Show fixation at start - 8 TRs for first trial, 4 TRs for subsequent trials
        if current_trial == 1:
            fixation_trs = 8
            print('Starting 8 TRs fixation (first trial)...')
        else:
            fixation_trs = 4
            print(f'Starting 4 TRs fixation (trial {current_trial})...')
        
        # Check for trigger received time from environment variable
        trigger_received_time = os.getenv('TRIGGER_RECEIVED_TIME')
        if trigger_received_time:
            trigger_time = float(trigger_received_time)
            # Log trigger received event
            trigger_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": 0.0,
                "RoundName": f"{arena_name}_test_run{run_number}",
                "visibility": "none",
                "phase": "trigger",
                "event": "trigger_received",
                "x": 0.0,
                "y": 0.0,
                "rotation_angle": 0.0
            }
            print(f"Logged trigger received at time: {trigger_time}")
        
        # Create fixation log entries to be added to the continuous log
        fixation_logs = []
        
        # Add trigger entry if available
        if trigger_received_time:
            fixation_logs.append(trigger_entry)
        
        # Log fixation start event
        trial_info = f"{arena_name}_test_run{run_number}"
        fixation_start_entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": 0.0,  # Fixation is before trial starts
            "RoundName": trial_info,
            "visibility": "none",  # No visibility during fixation
            "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0,  # No position during fixation
            "y": 0.0,
            "rotation_angle": 0.0
        }
        fixation_logs.append(fixation_start_entry)
        
        # Show fixation for the determined number of TRs (no frame-by-frame logging)
        fixation_start_time = time.time()
        while time.time() - fixation_start_time < (fixation_trs * TR):
            screen.fill(BACKGROUND_COLOR)
            game_surface.fill(BACKGROUND_COLOR)
            
            # Draw fixation cross using standardized format (200px text size equivalent)
            # Use font rendering for consistent appearance with PTSOD
            font = pygame.font.SysFont("Arial", 200)
            fixation_text = font.render('+', True, WHITE)
            text_rect = fixation_text.get_rect(center=CENTER_SCREEN)
            
            game_surface.blit(fixation_text, text_rect)
            
            screen.blit(game_surface, (offset_x, offset_y))
            pygame.display.flip()
            
            # Check for ESC key to exit
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Log fixation end event
        fixation_end_entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": fixation_trs * TR,
            "RoundName": trial_info,
            "visibility": "none",
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0
        }
        fixation_logs.append(fixation_end_entry)
        print(f"Fixation complete.")
        
        print('Fixation complete. Showing instruction for 1 TR...')
        show_image(os.path.join(INSTRUCTIONS_DIR, "8.png"), duration=TR, continuous_log=fixation_logs, trial_info=trial_info)
        
        # fMRI mode: 1 test trial only (no visibility)
        print("Running fMRI test trial...")
        
        # Show arena intro screen before running the arena
        draw_arena_intro(arena_name, multi_arena_trial_number, total_multi_arena_trials, len(targets), hebrew_arena_names, continuous_log=fixation_logs)
        
        trial_start_time = time.time()
        discrete_log, continuous_log = run_arena(f"{arena_name}_test_run{run_number}", targets, 1, 1, visibility="no_visibility", hebrew_names=arena_hebrew_names)
        
        # Add fixation logs to the beginning of continuous_log
        continuous_log = fixation_logs + continuous_log
        
        # TR alignment: Show fixation until end of current TR
        if MODE == 'fmri' and current_trial < total_trials:
            print('TR alignment: Showing fixation until end of current TR...')
            current_time = time.time()
            elapsed_TRs = int((current_time - trial_start_time) / TR)
            next_TR_start = trial_start_time + ((elapsed_TRs + 1) * TR)
            
            # Wait until the next TR boundary
            if current_time < next_TR_start:
                wait_time = next_TR_start - current_time
                print(f'Trial completed early. Waiting {wait_time:.2f} seconds for TR alignment...')
                
                # Log TR alignment fixation start event
                tr_fixation_start_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": current_time - trial_start_time,
                    "RoundName": trial_info,
                    "visibility": "none",
                    "phase": "fixation",
                    "event": "tr_alignment_fixation_start",
                    "x": 0.0,
                    "y": 0.0,
                    "rotation_angle": 0.0
                }
                continuous_log.append(tr_fixation_start_entry)
                
                # Show TR alignment fixation (no frame-by-frame logging)
                while time.time() < next_TR_start:
                    screen.fill(BACKGROUND_COLOR)
                    game_surface.fill(BACKGROUND_COLOR)
                    
                    # Draw fixation cross using standardized format (200px text size equivalent)
                    # Use font rendering for consistent appearance with PTSOD
                    font = pygame.font.SysFont("Arial", 200)
                    fixation_text = font.render('+', True, WHITE)
                    text_rect = fixation_text.get_rect(center=CENTER_SCREEN)
                    
                    game_surface.blit(fixation_text, text_rect)
                    screen.blit(game_surface, (offset_x, offset_y))
                    pygame.display.flip()
                    
                    # Check for ESC key to exit
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                
                # Log TR alignment fixation end event
                tr_fixation_end_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": time.time() - trial_start_time,
                    "RoundName": trial_info,
                    "visibility": "none",
                    "phase": "fixation",
                    "event": "tr_alignment_fixation_end",
                    "x": 0.0,
                    "y": 0.0,
                    "rotation_angle": 0.0
                }
                continuous_log.append(tr_fixation_end_entry)
                print(f"TR alignment fixation complete.")
        else:
            # Only show final fixation and thank you screen for the last trial
            if current_trial == total_trials:
                # Final trial: Show 4 TRs fixation followed by thank you screen
                print('Final trial: Showing 4 TRs fixation followed by thank you screen...')
                
                # Log final fixation start event
                final_fixation_start_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": time.time() - trial_start_time,
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
                final_fixation_start_time = time.time()
                while time.time() - final_fixation_start_time < (4 * TR):
                    screen.fill(BACKGROUND_COLOR)
                    game_surface.fill(BACKGROUND_COLOR)
                    
                    # Draw fixation cross using standardized format (200px text size equivalent)
                    # Use font rendering for consistent appearance with PTSOD
                    font = pygame.font.SysFont("Arial", 200)
                    fixation_text = font.render('+', True, WHITE)
                    text_rect = fixation_text.get_rect(center=CENTER_SCREEN)
                    
                    game_surface.blit(fixation_text, text_rect)
                    screen.blit(game_surface, (offset_x, offset_y))
                    pygame.display.flip()
                    
                    # Check for ESC key to exit
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                
                # Log final fixation end event
                final_fixation_end_entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": time.time() - trial_start_time,
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
                
                # Show thank you screen
                print("Showing thank you screen...")
                show_image(os.path.join(INSTRUCTIONS_DIR, "10.png"), continuous_log=continuous_log, trial_info=trial_info)
            else:
                print(f"Trial {current_trial}/{total_trials} complete - no final fixation or thank you screen (not final trial).")
        
        # Save logs after all fixation data is included
        save_logs(discrete_log, continuous_log, player_initials)
    
    print(f"Multi-arena experiment complete!")
    if MODE == 'fmri':
        print(f"Trial {current_trial}/{total_trials} completed")
    print(f"Data saved to: {continuous_filename}")

if __name__ == "__main__":
    run_multi_arena_experiment()
    pygame.quit()
    sys.exit() 