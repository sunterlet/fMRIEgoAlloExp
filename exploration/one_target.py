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
import argparse

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
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0   # 1.65 m
BORDER_THRESHOLD = 0.1              # threshold from border in meters

# Target parameters
TARGET_RADIUS = 0.1                 # reduced target radius in meters
GRID_SIZE = 0.05                    # size of grid cells for visited locations tracking (reduced from 0.1)

# Movement settings
MOVE_SPEED = 1.0                    # meters per second
ROTATE_SPEED = 60.0                 # degrees per second (reduced from 90.0)
PRACTICE_ROTATE_SPEED = 70.0        # degrees per second for practice game
MOVEMENT_FADE_TIME = 0.1            # Time in seconds for movement indicator to fade out

# Add input buffering settings
INPUT_BUFFER_SIZE = 3               # Number of input states to buffer
last_input_states = []              # Buffer for input states
last_frame_time = 0                 # Track last frame time for delta calculation

# Scale factor: pixels per meter
SCALE = 200                         # 1 meter = 200 pixels

# Window size (used for both practice and experiment)
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# ---------------------------
# Custom Color Palette
# ---------------------------
# Hex Colors:
# 1) Khaki:         #b7ad99 → (183, 173, 153)
# 2) Folly:         #ff4365 → (255, 67, 101)
# 3) Background:    #030301 → (3, 3, 1)
# 4) Turquoise:     #00d9c0 → (0, 217, 192)
# 5) Ivory:         #fffff3 → (255, 255, 243)

BACKGROUND_COLOR = (3, 3, 1)        # Background: near-black
AVATAR_COLOR = (255, 67, 101)       # Avatar: Folly
BORDER_COLOR = (255, 255, 243)      # Arena border: Ivory
TARGET_COLOR = (0, 217, 192)        # Targets and thermometer: Turquoise
CLOCK_COLOR = (183, 173, 153)       # Clock rotation, Annotation and Feedback avatar: Khaki

# We'll still use WHITE for text (except where updated) and debug visuals
WHITE = (255, 255, 255)
DEBUG_COLOR = (50, 50, 255)

# ---------------------------
# Sounds (Experiment)
# ---------------------------
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")

# ---------------------------
# Experiment parameters - will be set based on mode
# ---------------------------
TRAINING_SESSIONS = 3
DARK_TRAINING_TRIALS = 2  # Changed from 3 to 2 for practice mode
TEST_TRIALS = 3  # Changed from 5 to 3 for practice mode

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
parser.add_argument('--total-trials', '-tt', type=int, default=1,
                   help='Total number of trials in sequence (default: 1)')
parser.add_argument('--screen', '-s', type=int, default=None,
                   help='Screen number to display on (default: None, uses fullscreen)')
args = parser.parse_args()

MODE = args.mode
player_initials = args.participant
run_number = args.run
current_trial = args.trial
total_trials = args.total_trials
screen_number = args.screen
TR = 2.01  # Fixed TR for fMRI experiments

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
    discrete_filename = os.path.join(results_dir, f"{player_initials}_OT_ot{current_trial}_discrete.csv")
    continuous_filename = os.path.join(results_dir, f"{player_initials}_OT_ot{current_trial}_continuous.csv")
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
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    print(f"Fullscreen mode (default): {screen_width}x{screen_height}")

# Hide cursor for experiment
pygame.mouse.set_visible(False)
print("Cursor hidden for experiment")

# Calculate the offset to center the game area
offset_x = (screen_width - WIN_WIDTH) // 2
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
        beep_sound.set_volume(0.8)
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
    """Calculate the position of the player's tip."""
    tip_length = 30 / SCALE  # Convert pixels to meters
    rad = math.radians(player_angle)
    tip_x = player_pos[0] + tip_length * math.sin(rad)
    tip_y = player_pos[1] + tip_length * math.cos(rad)
    return (tip_x, tip_y)

# ---------------------------
# Function to display an instruction image
# ---------------------------
def show_image(image_path, duration=None):
    """Load and display a PNG image (assumed 1000×800) on the screen.
       If duration is provided, wait for that many seconds.
       Otherwise, wait for the user to press a key (except Escape, which exits)."""
    try:
        instruction_image = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return
    
    game_surface.blit(instruction_image, (0, 0))
    screen.blit(game_surface, (offset_x, offset_y))
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
            "trial": trial_counter if trial_counter is not None else "fixation",
            "condition_type": trial_info.split()[0] if trial_info and " " in trial_info else "fixation",
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
                elif event.key == pygame.K_k:  # 'K' key to skip fixation
                    print("Fixation skipped by 'K' key press")
                    # Log fixation end event if continuous_log is provided
                    if continuous_log is not None:
                        entry = {
                            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                            "trial_time": time.time() - start_time,
                            "trial": trial_counter if trial_counter is not None else "fixation",
                            "condition_type": trial_info.split()[0] if trial_info and " " in trial_info else "fixation",
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
            "trial": trial_counter if trial_counter is not None else "fixation",
            "condition_type": trial_info.split()[0] if trial_info and " " in trial_info else "fixation",
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0
        }
        continuous_log.append(entry)

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

# ---------------------------
# Helper drawing functions
# ---------------------------
def to_screen_coords(pos):
    """Convert arena coordinates (in meters) to screen coordinates (in pixels)."""
    x, y = pos
    screen_x = CENTER_SCREEN[0] + int(x * SCALE)
    screen_y = CENTER_SCREEN[1] - int(y * SCALE)
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
    
    font = get_hebrew_font(20)
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
        grid_y = CENTER_SCREEN[1] - cell[1] * grid_cell_size  # Flip y-coordinate
        # Create a surface for the visited cell
        cell_surface = pygame.Surface((grid_cell_size, grid_cell_size), pygame.SRCALPHA)
        cell_surface.fill(visited_color)
        game_surface.blit(cell_surface, (grid_x - grid_cell_size/2, grid_y - grid_cell_size/2))
    
    # Draw vertical lines
    for i in range(-num_cells//2, num_cells//2 + 1):
        x = CENTER_SCREEN[0] + i * grid_cell_size
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
def run_trial(is_training, target_sound_param, trial_info, trial_counter):
    global BACKGROUND_COLOR, target_sound
    # Use the global target_sound if parameter is None
    if target_sound_param is None:
        target_sound_param = target_sound
    phase = "exploration"  # phases: exploration, annotation, feedback

    # current_trial is already defined globally from command line arguments

    # Generate random target placement delay (whole number between 8-13 seconds)
    target_placement_delay = random.randint(8, 13)
    target_placement_time = None  # Will be set when movement starts

    player_pos = [0.0, 0.0]
    player_angle = 0.0
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

    while not trial_done:
        dt = clock.tick(60) / 1000.0
        current_trial_time = time.time() - trial_start_time

        # Check if trial duration has elapsed
        if phase == "exploration" and movement_start_time is not None:
            # Set target placement time when movement starts
            if target_placement_time is None:
                target_placement_time = movement_start_time + target_placement_delay
            
            # Calculate distance from center
            distance_from_center = math.hypot(player_pos[0], player_pos[1])
            
            # When time elapses, try to place target if conditions are met
            if not target_placed and target_placement_time is not None and time.time() >= target_placement_time:
                # Check if player is moving forward/backward (8/9) and not rotating (7/0)
                keys = pygame.key.get_pressed()
                is_moving_forward_backward = (pygame.K_8 in active_keys or keys[pygame.K_8] or
                    pygame.K_9 in active_keys or keys[pygame.K_9])
                is_rotating = (pygame.K_7 in active_keys or keys[pygame.K_7] or
                    pygame.K_0 in active_keys or keys[pygame.K_0])
                
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
                if target_position is not None and distance(player_pos, target_position) <= TARGET_RADIUS:
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
                            annotation_marker_pos = [0.0, 0.0]
                            annotation_marker_angle = 0.0
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
                        
                        # Note: TR alignment fixation will be handled after the trial is completely finished
                        # to avoid visual artifacts from returning to the main game loop
                if phase == "exploration":
                    if event.key in (pygame.K_8, pygame.K_9):  # Number keys for movement
                        if move_key_pressed is None:
                            move_key_pressed = event.key
                            move_start_pos = list(player_pos)
                    if event.key in (pygame.K_7, pygame.K_0):  # Number keys for rotation
                        if rotate_key_pressed is None:
                            rotate_key_pressed = event.key
                            rotate_start_angle = player_angle
                # Track number key presses for MRI control box
                if event.key in [pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_1, pygame.K_RETURN]:
                    active_keys.add(event.key)
                if event.key == pygame.K_k:
                    pass
            if event.type == pygame.KEYUP:
                if phase == "exploration":
                    if event.key in (pygame.K_8, pygame.K_9):  # Number keys for movement
                        move_key_pressed = None
                        move_start_pos = None
                    if event.key in (pygame.K_7, pygame.K_0):  # Number keys for rotation
                        rotate_key_pressed = None
                        rotate_start_angle = None
                # Remove keys when released
                if event.key in [pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_1, pygame.K_RETURN]:
                    active_keys.discard(event.key)

        screen.fill(BACKGROUND_COLOR)  # Fill the fullscreen with background color
        game_surface.fill(BACKGROUND_COLOR)

        if phase == "exploration":
            keys = pygame.key.get_pressed()
            # Use both active_keys tracking and get_pressed() for maximum compatibility with MRI control box
            current_is_moving = (pygame.K_7 in active_keys or keys[pygame.K_7] or 
                               pygame.K_8 in active_keys or keys[pygame.K_8] or 
                               pygame.K_9 in active_keys or keys[pygame.K_9] or 
                               pygame.K_0 in active_keys or keys[pygame.K_0])
            current_is_moving_forward_backward = (pygame.K_8 in active_keys or keys[pygame.K_8] or 
                                                pygame.K_9 in active_keys or keys[pygame.K_9])  # Track forward/backward movement
            current_is_rotating = (pygame.K_7 in active_keys or keys[pygame.K_7] or 
                                 pygame.K_0 in active_keys or keys[pygame.K_0])  # Track rotation
            
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
            if pygame.K_8 in active_keys or keys[pygame.K_8]:  # Move forward
                has_moved_forward = True
            if pygame.K_9 in active_keys or keys[pygame.K_9]:  # Move backward
                pass  # No special tracking needed
            if (pygame.K_7 in active_keys or keys[pygame.K_7] or 
                pygame.K_0 in active_keys or keys[pygame.K_0]):  # Rotate left or right
                has_rotated = True
                # Set rotation start angle when rotation begins
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle

            # Update player position and angle
            old_pos = list(player_pos)  # Store old position
            old_angle = player_angle    # Store old angle
            
            if pygame.K_8 in active_keys or keys[pygame.K_8]:  # Move forward
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
            if pygame.K_9 in active_keys or keys[pygame.K_9]:  # Move backward
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
            if pygame.K_7 in active_keys or keys[pygame.K_7]:  # Rotate left
                player_angle -= ROTATE_SPEED * dt
                # Reset rotation tracking if starting new rotation
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle
            if pygame.K_0 in active_keys or keys[pygame.K_0]:  # Rotate right
                player_angle += ROTATE_SPEED * dt
                # Reset rotation tracking if starting new rotation
                if not is_rotating or rotation_stop_time is not None:
                    angle_rotated = 0.0
                    rotation_stop_time = None
                is_rotating = True
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle

            # Update movement tracking
            if is_moving_forward_backward:
                # Calculate distance moved (forward/backward only)
                distance_moved += math.hypot(player_pos[0] - old_pos[0], player_pos[1] - old_pos[1])
            
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

            # Get current tip position and cell
            tip_pos = get_player_tip_position(player_pos, player_angle)
            current_tip_cell = get_grid_cell(tip_pos)

            # Check border collision and play beep sound
            if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
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
                (pygame.K_8 in active_keys or keys[pygame.K_8] or pygame.K_9 in active_keys or keys[pygame.K_9]) and
                not (pygame.K_7 in active_keys or keys[pygame.K_7] or pygame.K_0 in active_keys or keys[pygame.K_0]) and
                math.hypot(player_pos[0], player_pos[1]) >= 0.5 and
                math.hypot(player_pos[0], player_pos[1]) <= (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD)
            )

            # Check if we've entered a new cell
            entered_new_cell = last_tip_cell is None or current_tip_cell != last_tip_cell

            # Check if player is at target position
            if target_position is not None:
                if distance(player_pos, target_position) <= TARGET_RADIUS:
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
                                "x": round(player_pos[0], 3),
                                "y": round(player_pos[1], 3),
                                "rotation_angle": round(player_angle, 3)
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
                
                # Calculate where the target center would be placed
                rad = math.radians(player_angle)
                target_center_x = tip_pos[0] - TARGET_RADIUS * math.sin(rad)
                target_center_y = tip_pos[1] - TARGET_RADIUS * math.cos(rad)
                
                # Place the target immediately since we already checked the tip cell is unvisited
                target_position = (target_center_x, target_center_y)
                target_placed = True
                target_placed_time = time.time()  # Record when target was placed
                # Play target sound when target is placed
                if target_sound_param is not None and target_channel is not None:
                    target_channel.play(target_sound_param)
                elif target_sound_param is not None:
                    target_sound_param.play()
                if DEBUG_MODE:
                    print(f"DEBUG: Target placed at time {time.time() - trial_start_time:.2f}")
                current_event = "target_placed"
                # Add target_placed event to continuous log
                entry = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "trial_time": round(current_trial_time, 3),
                    "trial": trial_counter,  # Use actual trial number instead of trial_info
                    "condition_type": "test" if MODE == 'fmri' else (trial_info.split()[0] if " " in trial_info else "practice"),
                    "phase": "exploration",
                    "event": current_event,
                    "x": round(player_pos[0], 3),
                    "y": round(player_pos[1], 3),
                    "rotation_angle": round(player_angle, 3)
                }
                continuous_log.append(entry)

            # If we've moved to a new cell, mark the previous cell as visited
            if last_tip_cell is not None and current_tip_cell != last_tip_cell:
                visited_cells.add(last_tip_cell)
                if DEBUG_MODE:
                    print(f"DEBUG: Marked previous cell {last_tip_cell} as visited")

            # Always update last_tip_cell
            last_tip_cell = current_tip_cell

            # Draw arena and player
            if "dark_training" in trial_info:
                # In dark training, show avatar at start and when near border
                if not current_is_moving and not trial_movement_started:
                    # Show avatar and arena only at the very start (before first movement)
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
                elif math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                    # Show avatar and arena when near border
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            elif "test" in trial_info:
                # In test trials, show avatar only at start
                if not current_is_moving and not trial_movement_started:
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            else:
                # In normal trials, always show arena and avatar
                draw_arena()
                draw_player_avatar(player_pos, player_angle)

            # Add instruction text for exploration phase
            font = get_hebrew_font(20)
            instruction_text = render_hebrew_text(font, "למעבר סימון המטרה לחצ/י RETNE", WHITE)
            # Position text in the middle under the arena
            text_rect = instruction_text.get_rect(centerx=WIN_WIDTH//2, bottom=WIN_HEIGHT-30)
            game_surface.blit(instruction_text, text_rect)

            # Draw movement indicators with fade-out behavior
            if is_moving_forward_backward or (movement_stop_time is not None and 
                time.time() - movement_stop_time <= MOVEMENT_FADE_TIME):
                distance_moved = draw_thermometer(distance_moved, is_moving_forward_backward, 
                               movement_stop_time, time.time())
            if is_rotating or (rotation_stop_time is not None and 
                time.time() - rotation_stop_time <= MOVEMENT_FADE_TIME):
                angle_rotated = draw_clock(angle_rotated, is_rotating, rotation_stop_time, time.time())

            # Add debug timing panel
            draw_debug_timing_panel(
                trial_start_time,
                movement_start_time,
                target_placement_time,
                exploration_start_time,
                annotation_start_time,
                target_placed_time
            )

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
            if pygame.K_7 in active_keys or keys[pygame.K_7]:  # Rotate left
                annotation_marker_angle -= ROTATE_SPEED * dt
            if pygame.K_0 in active_keys or keys[pygame.K_0]:  # Rotate right
                annotation_marker_angle += ROTATE_SPEED * dt
            if pygame.K_8 in active_keys or keys[pygame.K_8]:  # Move forward
                rad = math.radians(annotation_marker_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = annotation_marker_pos[0] + dx
                new_y = annotation_marker_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[0] = new_x
                    annotation_marker_pos[1] = new_y
            if pygame.K_9 in active_keys or keys[pygame.K_9]:  # Move backward
                rad = math.radians(annotation_marker_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = annotation_marker_pos[0] - dx
                new_y = annotation_marker_pos[1] - dy
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
            font = get_hebrew_font(20)
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
            # In practice mode, use internal trial counting
            if trial_info.startswith("training"):
                internal_total = TRAINING_SESSIONS
                internal_current = trial_info.split()[1] if len(trial_info.split()) > 1 else "1"
            elif trial_info.startswith("dark_training"):
                internal_total = DARK_TRAINING_TRIALS
                internal_current = trial_info.split()[1] if len(trial_info.split()) > 1 else "1"
            elif trial_info.startswith("test"):
                internal_total = TEST_TRIALS
                # Handle both "test 1" and "test_run1" formats
                if "run" in trial_info:
                    # Extract run number from "test_run1" format
                    internal_current = trial_info.split("run")[1]
                else:
                    internal_current = trial_info.split()[1] if len(trial_info.split()) > 1 else "1"
            else:
                internal_total = "?"
                internal_current = "1"
            counter_text = f"{internal_current}/{internal_total}"
        counter_font = pygame.font.SysFont("Arial", 24)
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
                "x": round(player_pos[0], 3),
                "y": round(player_pos[1], 3),
                "rotation_angle": round(player_angle, 3)
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

        # Check if K is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_k]:
            # Show all elements when K is pressed
            draw_arena()
            if phase == "exploration":
                draw_player_avatar(player_pos, player_angle)
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
            # Normal drawing logic when K is not pressed
            if phase == "exploration":
                if "dark_training" in trial_info:
                    # In dark training, show avatar at start and when near border
                    if not current_is_moving and not trial_movement_started:
                        draw_arena()
                        draw_player_avatar(player_pos, player_angle)
                    elif math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                        draw_arena()
                        draw_player_avatar(player_pos, player_angle)
                elif "test" in trial_info:
                    # In test trials, show avatar only at start
                    if not current_is_moving and not trial_movement_started:
                        draw_arena()
                        draw_player_avatar(player_pos, player_angle)
                else:
                    # In normal trials, always show arena and avatar
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
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
                font = get_hebrew_font(20)
                text = render_hebrew_text(font, "לחצ/י RETNE להמשך", WHITE)
                text_rect = text.get_rect(centerx=WIN_WIDTH//2, bottom=WIN_HEIGHT-30)
                game_surface.blit(text, text_rect)

        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()

    exploration_time = time.time() - exploration_start_time if exploration_start_time is not None else 0
    annotation_time = time.time() - annotation_start_time if annotation_start_time is not None else 0
    error_distance = None
    # Calculate error distance between target location and annotation position
    # This should always be calculated if a target was placed, regardless of whether player returned to it
    if target_position is not None:
        error_distance = distance(target_position, annotation_marker_pos)
    
    # Stop all sounds when trial ends
    if beep_channel is not None:
        beep_channel.stop()
    if target_channel is not None:
        target_channel.stop()
    
    # Add TR alignment fixation for fMRI mode after trial is completely finished
    if MODE == 'fmri' and current_trial < total_trials:
        print('TR alignment: Checking if fixation needed until end of current TR...')
        current_time = time.time()
        
        # Use trigger time as reference if available, otherwise use trial start time
        trigger_received_time = os.getenv('TRIGGER_RECEIVED_TIME')
        if trigger_received_time:
            reference_time = float(trigger_received_time)
        else:
            reference_time = trial_start_time
        
        elapsed_TRs = int((current_time - reference_time) / TR)
        next_TR_start = reference_time + ((elapsed_TRs + 1) * TR)
        
        # Only show fixation if trial completed mid-TR
        if current_time < next_TR_start:
            wait_time = next_TR_start - current_time
            print(f'Trial completed mid-TR. Waiting {wait_time:.2f} seconds for TR alignment...')
            
            # Clear the screen completely before showing fixation to avoid glimpse of previous trial phase
            screen.fill(BACKGROUND_COLOR)
            game_surface.fill(BACKGROUND_COLOR)
            screen.blit(game_surface, (offset_x, offset_y))
            pygame.display.flip()
            
            # Log TR alignment fixation start event
            tr_fixation_start_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": current_time - trial_start_time,
                "trial": trial_counter,
                "condition_type": "test",
                "phase": "fixation",
                "event": "tr_alignment_fixation_start",
                "x": round(annotation_marker_pos[0], 3),
                "y": round(annotation_marker_pos[1], 3),
                "rotation_angle": round(annotation_marker_angle, 3)
            }
            continuous_log.append(tr_fixation_start_entry)
            
            # Show TR alignment fixation using standardized format (no frame-by-frame logging)
            while time.time() < next_TR_start:
                screen.fill(BACKGROUND_COLOR)
                game_surface.fill(BACKGROUND_COLOR)
                
                # Draw standardized fixation cross using standardized format (200px text size equivalent)
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
                "trial": trial_counter,
                "condition_type": "test",
                "phase": "fixation",
                "event": "tr_alignment_fixation_end",
                "x": round(annotation_marker_pos[0], 3),
                "y": round(annotation_marker_pos[1], 3),
                "rotation_angle": round(annotation_marker_angle, 3)
            }
            continuous_log.append(tr_fixation_end_entry)
            print(f"TR alignment fixation complete.")
        else:
            print(f'Trial completed at TR boundary - no alignment fixation needed.')
    
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

def save_continuous_log(logs, filename):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    try:
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["RealTime", "trial_time", "trial", "condition_type", "phase", "event", "x", "y", "rotation_angle"]
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
                fieldnames = ["RealTime", "trial_time", "trial", "condition_type", "phase", "event", "x", "y", "rotation_angle"]
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
    
    # Trigger handling moved to MATLAB level
    trigger_manager = None

    # Initialize lists for logs
    all_discrete_logs = []
    all_continuous_logs = []
    
    # Initialize trial counter for proper numbering
    trial_counter = 1

    if MODE == 'practice':
        # Practice mode: full sequence outside magnet
        print("Running practice mode (outside magnet)")
        
        # 1. Show Training Block instructions
        show_image(os.path.join(INSTRUCTIONS_DIR, "3.png"))

        # Training trials
        for i in range(1, TRAINING_SESSIONS + 1):
            trial_info = f"training {i}"
            discrete_log, continuous_log = run_trial(True, training_target_sound, trial_info, trial_counter)
            all_discrete_logs.append(discrete_log)
            all_continuous_logs.extend(continuous_log)
            trial_counter += 1
            # Save after each training trial
            save_discrete_log(all_discrete_logs, discrete_filename)
            save_continuous_log(all_continuous_logs, continuous_filename)

        # 2. Show Dark Training instructions
        show_image(os.path.join(INSTRUCTIONS_DIR, "4.png"))

        # Dark training trials
        for i in range(1, DARK_TRAINING_TRIALS + 1):
            trial_info = f"dark_training {i}"
            discrete_log, continuous_log = run_trial(True, training_target_sound, trial_info, trial_counter)
            all_discrete_logs.append(discrete_log)
            all_continuous_logs.extend(continuous_log)
            trial_counter += 1
            # Save after each dark training trial
            save_discrete_log(all_discrete_logs, discrete_filename)
            save_continuous_log(all_continuous_logs, continuous_filename)

        # 3. Show Testing Block instructions
        show_image(os.path.join(INSTRUCTIONS_DIR, "5.png"))

        # Test trials
        for i in range(1, TEST_TRIALS + 1):
            trial_info = f"test {i}"
            discrete_log, continuous_log = run_trial(False, training_target_sound, trial_info, trial_counter)
            all_discrete_logs.append(discrete_log)
            all_continuous_logs.extend(continuous_log)
            trial_counter += 1
            # Save after each test trial
            save_discrete_log(all_discrete_logs, discrete_filename)
            save_continuous_log(all_continuous_logs, continuous_filename)

        # Show final instruction image for practice mode
        show_image(os.path.join(INSTRUCTIONS_DIR, "10.png"))
        
        print("Practice session complete.")

    elif MODE == 'fmri':
        # fMRI mode: single test trial inside magnet
        print(f"Running fMRI mode (inside magnet) - Run {run_number}")
        
        # Set experiment start time for fMRI mode
        experiment_start_time = time.time()
        
        # Check for trigger received time from environment variable
        trigger_received_time = os.getenv('TRIGGER_RECEIVED_TIME')
        if trigger_received_time:
            trigger_time = float(trigger_received_time)
            # Log trigger received event
            trigger_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": 0.0,
                "trial": current_trial,
                "condition_type": "test",
                "phase": "trigger",
                "event": "trigger_received",
                "x": 0.0,
                "y": 0.0,
                "rotation_angle": 0.0
            }
            all_continuous_logs.append(trigger_entry)
            print(f"Logged trigger received at time: {trigger_time}")
        
        # Show fixation at start - 8 TRs for first trial, 4 TRs for subsequent trials
        if current_trial == 1:
            fixation_trs = 8
            print('Starting 8 TRs fixation (first trial)...')
        else:
            fixation_trs = 4
            print(f'Starting 4 TRs fixation (trial {current_trial})...')
        
        # Add trigger entry if available
        if trigger_received_time:
            all_continuous_logs.append(trigger_entry)
        
        # Log fixation start event
        trial_info = f"test_run{run_number}"
        fixation_start_entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": 0.0,  # Fixation is before trial starts
            "trial": current_trial,
            "condition_type": "test",
            "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0,  # No position during fixation
            "y": 0.0,
            "rotation_angle": 0.0
        }
        all_continuous_logs.append(fixation_start_entry)
        
        # Show fixation for the determined number of TRs using standardized format (no frame-by-frame logging)
        fixation_start_time = time.time()
        while time.time() - fixation_start_time < (fixation_trs * TR):
            screen.fill(BACKGROUND_COLOR)
            game_surface.fill(BACKGROUND_COLOR)
            
            # Draw standardized fixation cross using standardized format (200px text size equivalent)
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
            "trial": current_trial,
            "condition_type": "test",
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0
        }
        all_continuous_logs.append(fixation_end_entry)
        print(f"Fixation complete.")
        
        print('Fixation complete. Showing instruction for 1 TR...')
        show_image(os.path.join(INSTRUCTIONS_DIR, "6.png"), duration=TR)
        
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
            # Show 4 TRs fixation at end followed by thank you screen
            print('Showing 4 TRs final fixation followed by thank you screen (final trial)...')
            
            # Log final fixation start event
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
            
            # Show 4 TRs fixation using standardized format
            final_fixation_start_time = time.time()
            while time.time() - final_fixation_start_time < (4 * TR):
                screen.fill(BACKGROUND_COLOR)
                game_surface.fill(BACKGROUND_COLOR)
                
                # Draw standardized fixation cross using standardized format (200px text size equivalent)
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
            
            # Show thank you screen
            print("Showing thank you screen...")
            show_image(os.path.join(INSTRUCTIONS_DIR, "10.png"))
        else:
            print(f"Trial {current_trial}/{total_trials} complete - no final fixation or thank you screen (not final trial).")
        
        print("One Target Run complete.")
        print(f"Trial {current_trial}/{total_trials} completed")
    
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
