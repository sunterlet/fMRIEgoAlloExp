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
from screeninfo import get_monitors
from fixation_utils import show_fixation_image
from trigger_utils import TriggerManager
from sound_paths import SOUNDS_DIR, BEEP_SOUND_PATH, TARGET_SOUND_PATH
# Fallback (uncomment if sound_paths fails on PC):
# SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
# TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
# BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")

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
# Configuration parameters
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0   # 1.65 m
BORDER_THRESHOLD = 0.1              # threshold from border in meters

# Scale factor: pixels per meter
SCALE = 200                         # 1 meter = 200 pixels

# Window size
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# ---------------------------
# Custom Color Palette
# ---------------------------
BACKGROUND_COLOR = (3, 3, 1)        # Background: near-black
AVATAR_COLOR = (255, 67, 101)       # Avatar: Folly
BORDER_COLOR = (255, 255, 243)      # Arena border: Ivory
TARGET_COLOR = (0, 217, 192)        # Targets: Turquoise
CLOCK_COLOR = (183, 173, 153)       # Score: Khaki
WHITE = (255, 255, 255)

# ---------------------------
# Movement settings
# ---------------------------
MOVE_SPEED = 1.0                    # meters per second
PRACTICE_ROTATE_SPEED = 70.0        # degrees per second for practice game

# ---------------------------
# Parse command line arguments
# ---------------------------
parser = argparse.ArgumentParser(description='Snake Practice Game')
parser.add_argument('mode', choices=['practice', 'fmri', 'anatomical'], 
                   help='Run mode: practice (outside magnet), fmri (inside magnet), or anatomical (during anatomical scan)')
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
parser.add_argument('--fa-run', '-far', type=int, default=None,
                    help='Full arena run identifier for logging (default: None)')
parser.add_argument('--snake-trial', '-st', type=int, default=None,
                    help='Snake-specific trial number (for sequential numbering, default: None, will be calculated)')
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
screen_number = args.screen
fa_run_number = args.fa_run
scanning = args.scanning
com_port = args.com
TR = args.tr  # TR from command line or default 2.01

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
    # Determine run context based on run_number
    # Run 1 = One Target Run, Run 2 = Full Arena Run
    if fa_run_number is not None:
        run_context = f"FA{fa_run_number}"
    elif run_number == 1:
        run_context = "OT"
    elif run_number == 2:
        run_context = "FA"
    else:
        # Fallback for any other run numbers
        run_context = f"run{run_number}"
else:
    run_context = None

snake_trial_number = current_trial
snake_total_trials = total_trials

if MODE == 'fmri':
    # Snake trials alternate with other trial types
    # Use provided snake_trial number if available (for display purposes only)
    # Filenames use current_trial (overall run position) to match one_target and multi_arena
    if args.snake_trial is not None:
        snake_trial_number = args.snake_trial
    else:
        # Fallback: compute snake-specific numbering assuming alternating pattern
        snake_trial_number = (current_trial + 1) // 2
    snake_total_trials = math.ceil(total_trials / 2)
    # Use current_trial (overall run position) for filenames to match participant's view (e.g., snake1, OT2, snake3)
    continuous_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_snake{current_trial}_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_snake{current_trial}_discrete.csv")
elif MODE == 'anatomical':
    # Anatomical mode: use special naming for anatomical scan period
    continuous_filename = os.path.join(results_dir, f"{player_initials}_anatomical_snake_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_anatomical_snake_discrete.csv")
else:
    continuous_filename = os.path.join(results_dir, f"{player_initials}_snake_practice_continuous_log.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_snake_practice_discrete_log.csv")

# Ensure results directory exists
os.makedirs(results_dir, exist_ok=True)

# Set trial duration based on mode
if MODE == 'fmri':
    # fMRI mode: Use random TR-aligned durations (10-15 seconds)
    # Convert to TRs: 10-15 seconds = 5-7.5 TRs, use 5-7 TRs
    TRIAL_TRs = random.randint(5, 7)  # 5-7 TRs = 10.05-14.07 seconds
    TRIAL_DURATION = TRIAL_TRs * TR
elif MODE == 'anatomical':
    # Anatomical mode: No time limit (endless gameplay)
    TRIAL_DURATION = None
else:
    # Practice mode: Fixed 1 minute duration
    TRIAL_DURATION = 60.0  # 1 minute = 60 seconds

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

# Hide cursor for experiment
pygame.mouse.set_visible(False)
print("Cursor hidden for experiment")

# Calculate the offset to center the game area
offset_x = (screen_width - WIN_WIDTH) // 2
offset_y = (screen_height - WIN_HEIGHT) // 2

# Create a surface for the game content
game_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

pygame.display.set_caption("Practice Game")
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
# Helper functions
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

def draw_arena():
    """Draw the arena border as a circle centered on the screen."""
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

def draw_target(target_pos):
    """Draw the target as a circle."""
    target_screen = to_screen_coords(target_pos)
    pygame.draw.circle(game_surface, TARGET_COLOR, target_screen, 10)

def draw_score_and_timer(score, time_remaining):
    """Draw the score and timer in the top-left corner."""
    font = pygame.font.SysFont("Arial", 36)
    score_text = font.render(f"Score: {score}", True, CLOCK_COLOR)
    
    # Format timer as 00:XX (minutes:seconds) or show nothing for anatomical mode
    if time_remaining is not None:
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, CLOCK_COLOR)
        game_surface.blit(score_text, (10, 10))
        game_surface.blit(timer_text, (10, 50))
    else:
        # Anatomical mode: only show score, no timer
        game_surface.blit(score_text, (10, 10))

def draw_trial_counter():
    """Draw the trial counter in the bottom-right corner."""
    if MODE == 'fmri':
        # Use overall trial numbers from the sequence (e.g., 1/12, 2/12, etc.)
        counter_text = f"{current_trial}/{total_trials}"
        counter_font = pygame.font.SysFont("Arial", 24)
        counter_surface = counter_font.render(counter_text, True, WHITE)
        counter_rect = counter_surface.get_rect()
        counter_rect.bottomright = (WIN_WIDTH - 20, WIN_HEIGHT - 20)
        game_surface.blit(counter_surface, counter_rect)

# ---------------------------
# Logging functions
# ---------------------------
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
        "trial_type": "error",
        "RoundName": trial_info if trial_info else "error",
        "condition_type": "error",
        "visibility": "none",
        "phase": "error",
        "event": f"ERROR: {error_message}",
        "x": 0.0,
        "y": 0.0,
        "rotation_angle": 0.0,
        "score": 0.0
    }
    continuous_log.append(error_entry)
    print(f"ERROR LOGGED: {error_message} (trial: {trial_number})")

def save_continuous_log(logs, filename):
    """Save continuous log to CSV file."""
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

def save_discrete_log(logs, filename):
    """Save discrete log to CSV file."""
    # Check if file exists and find next available suffix
    base_name = filename.replace('.csv', '')
    counter = 1
    final_filename = filename
    
    while os.path.exists(final_filename):
        final_filename = f"{base_name}_{counter}.csv"
        counter += 1
    
    try:
        with open(final_filename, "w", newline="") as csvfile:
            fieldnames = ["trial", "final_score", "trial_duration", "target_locations", "target_reach_times", "game_duration"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log in logs:
                writer.writerow(log)
        print(f"Discrete log saved successfully to: {final_filename}")
    except Exception as e:
        print(f"Error saving discrete log: {e}")
        # Try to save with a timestamp as last resort
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{base_name}_backup_{timestamp}.csv"
        try:
            with open(backup_filename, "w", newline="") as csvfile:
                fieldnames = ["trial", "final_score", "trial_duration", "target_locations", "target_reach_times", "game_duration"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for log in logs:
                    writer.writerow(log)
            print(f"Discrete log saved as backup to: {backup_filename}")
        except Exception as backup_e:
            print(f"Failed to save backup file: {backup_e}")

def random_position_in_arena():
    """Generate a random position within the arena."""
    angle = random.uniform(0, 2 * math.pi)
    r = ARENA_RADIUS * math.sqrt(random.uniform(0, 0.8))  # Keep away from edges
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    return (x, y)

def within_arena(pos):
    """Check if a position is within the arena bounds."""
    return math.hypot(pos[0], pos[1]) <= ARENA_RADIUS

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
                    elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:  # Use 1 or ENTER key to proceed
                        waiting = False
                    elif event.key == pygame.K_k:  # 'K' key to skip instruction
                        print("Instruction skipped by 'K' key press")
                        waiting = False
            clock.tick(15)

# ---------------------------
# Function to show fixation cross
# ---------------------------
def show_fixation(duration=6.0, continuous_log=None, trial_counter=None, trial_info=None):
    """Display a fixation cross for the specified duration."""
    show_fixation_image(screen, game_surface, offset_x, offset_y, duration, 
                       "white_on_black", continuous_log, trial_counter, trial_info, BACKGROUND_COLOR)

# ---------------------------
# Practice Game
# ---------------------------
def run_practice_game():
    """Run the practice game with different targets based on mode."""
    
    print(f"Starting snake game - Mode: {MODE}, Trial Duration: {TRIAL_DURATION} seconds")
    
    # Initialize logging early (before trigger wait) for error handling
    continuous_log = []
    
    # Initialize trigger manager if scanning is enabled
    trigger_manager = TriggerManager(scanning=scanning, com_port=com_port)
    if scanning:
        if not trigger_manager.init_trigger():
            error_msg = "Failed to initialize trigger connection"
            print(f"CRITICAL: {error_msg}. Exiting.")
            # Try to log error if continuous_log exists
            # Log error to continuous log
            log_error_to_continuous_log(continuous_log, error_msg, current_trial, f"snake_trial{current_trial}")
            try:
                save_continuous_log(continuous_log, continuous_filename)
                print(f"Error logged to: {continuous_filename}")
            except Exception as e:
                print(f"Warning: Could not save error log: {e}")
            trigger_manager.close_trigger()
            sys.exit(1)
    
    # Show instructions based on mode
    if MODE == 'practice':
        # Practice mode: show 1.png and wait for key press
        show_image(os.path.join(INSTRUCTIONS_DIR, "1.png"))
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
                log_error_to_continuous_log(continuous_log, error_msg, current_trial, f"snake_trial{current_trial}")
                try:
                    save_continuous_log(continuous_log, continuous_filename)
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
        
        # Show fixation at start - 8 TRs for first trial, 4 TRs for subsequent trials
        if current_trial == 1:
            fixation_trs = 8
            print('Starting 8 TRs fixation (first trial)...')
        else:
            fixation_trs = 4
            print(f'Starting 4 TRs fixation (trial {current_trial})...')
        
        # Create fixation log entries to be added to the continuous log
        fixation_logs = []
        
        # Log trigger received event - always log when we have a trigger time
        # When scanning is enabled, we always wait for and receive a trigger for each trial
        if trigger_time_value is not None:
            trigger_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": 0.0,
                "trial": str(current_trial),
                "phase": "trigger",
                "event": "trigger_received",
                "x": 0.0,
                "y": 0.0,
                "rotation_angle": 0.0,
                "score": 0,
                "target_x": 0.0,
                "target_y": 0.0,
                "trigger_received_time": trigger_time_value
            }
            fixation_logs.append(trigger_entry)
            print(f"Logged trigger received at time: {trigger_time_value:.3f} (trial {current_trial})")
        elif scanning:
            # This should never happen when scanning is enabled (we wait for trigger)
            print(f"WARNING: Scanning enabled but no trigger time available for trial {current_trial}")
        
        # Prepare trial info for fixation logging
        if MODE == 'fmri':
            trial_info = str(current_trial)
        elif MODE == 'anatomical':
            trial_info = "anatomical"
        else:
            trial_info = "practice"
        
        # Show fixation for the determined number of TRs (no frame-by-frame logging)
        # show_fixation_image() will handle logging fixation_start and fixation_end
        fixation_duration = fixation_trs * TR
        show_fixation_image(screen, game_surface, offset_x, offset_y, fixation_duration, 
                           "white_on_black", fixation_logs, current_trial, trial_info, BACKGROUND_COLOR)
        print(f"Fixation complete.")
        
        print('Fixation complete. Showing instruction for 1 TR...')
        show_image(os.path.join(INSTRUCTIONS_DIR, "2.png"), duration=TR)
    
    # Initialize player position and angle
    player_pos = [0.0, 0.0]  # Start at center
    player_angle = 0.0
    
    # Initialize target
    target_pos = random_position_in_arena()
    
    # Game state
    score = 0
    target_radius = 0.1  # meters
    
    # Track active keys for MRI control box compatibility
    active_keys = set()
    
    # Initialize logging (continuous_log already initialized earlier)
    target_locations = []
    target_reach_times = []
    game_start_time = time.time()
    last_target_time = game_start_time
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Get time since last frame in seconds
        current_time = time.time() - game_start_time
        
        # Continuous logging
        if MODE == 'fmri':
            trial_info = str(current_trial)
        elif MODE == 'anatomical':
            trial_info = "anatomical"
        else:
            trial_info = "practice"
        entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": round(current_time, 3),
            "trial": trial_info,
            "phase": "gameplay",
            "event": None,
            "x": round(player_pos[0], 3),
            "y": round(player_pos[1], 3),
            "rotation_angle": round(player_angle, 3),
            "score": score,
            "target_x": round(target_pos[0], 3),
            "target_y": round(target_pos[1], 3)
        }
        continuous_log.append(entry)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_k:  # Only 'K' key can end the game
                    running = False
                # Track number key presses for MRI control box
                elif event.key in [pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    active_keys.add(event.key)
            if event.type == pygame.KEYUP:
                # Remove keys when released
                if event.key in [pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    active_keys.discard(event.key)

        # Handle movement with number keys - compatible with MRI control box
        # Use both active_keys tracking and get_pressed() for maximum compatibility
        
        # Rotation controls
        if pygame.K_6 in active_keys or pygame.key.get_pressed()[pygame.K_6]:  # Rotate left
            player_angle -= PRACTICE_ROTATE_SPEED * dt
        if pygame.K_9 in active_keys or pygame.key.get_pressed()[pygame.K_9]:  # Rotate right
            player_angle += PRACTICE_ROTATE_SPEED * dt
            
        # Movement controls
        if pygame.K_7 in active_keys or pygame.key.get_pressed()[pygame.K_7]:  # Move forward
            rad = math.radians(player_angle)
            dx = MOVE_SPEED * dt * math.sin(rad)
            dy = MOVE_SPEED * dt * math.cos(rad)
            new_x = player_pos[0] + dx
            new_y = player_pos[1] + dy
            if within_arena([new_x, new_y]):
                player_pos[0] = new_x
                player_pos[1] = new_y
                
        if pygame.K_8 in active_keys or pygame.key.get_pressed()[pygame.K_8]:  # Move backward
            rad = math.radians(player_angle)
            dx = MOVE_SPEED * dt * math.sin(rad)
            dy = MOVE_SPEED * dt * math.cos(rad)
            new_x = player_pos[0] - dx
            new_y = player_pos[1] - dy
            if within_arena([new_x, new_y]):
                player_pos[0] = new_x
                player_pos[1] = new_y

        # Check border collision and play beep sound
        if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
            if beep_sound is not None and beep_channel is not None:
                if not beep_channel.get_busy():
                    beep_channel.play(beep_sound, loops=-1)
        else:
            if beep_channel is not None:
                if beep_channel.get_busy():
                    beep_channel.stop()

        # Check collision with the target using the tip of the avatar
        tip_length = 30 / SCALE  # Convert pixels to meters
        rad = math.radians(player_angle)
        tip_x = player_pos[0] + tip_length * math.sin(rad)
        tip_y = player_pos[1] + tip_length * math.cos(rad)
        
        if distance([tip_x, tip_y], target_pos) < target_radius:
            score += 1
            
            # Log target reached event
            target_reach_time = time.time() - game_start_time
            target_locations.append([round(target_pos[0], 3), round(target_pos[1], 3)])
            target_reach_times.append(round(target_reach_time, 3))
            
            # Add event to continuous log
            event_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "trial_time": round(target_reach_time, 3),
                "trial": "anatomical" if MODE == 'anatomical' else trial_info,
                "phase": "gameplay",
                "event": "target_reached",
                "x": round(player_pos[0], 3),
                "y": round(player_pos[1], 3),
                "rotation_angle": round(player_angle, 3),
                "score": score,
                "target_x": round(target_pos[0], 3),
                "target_y": round(target_pos[1], 3)
            }
            continuous_log.append(event_entry)
            
            # Always place new target (no score limit)
            target_pos = random_position_in_arena()
            # Play target sound when reaching target
            if target_sound is not None and target_channel is not None:
                target_channel.play(target_sound)
            elif target_sound is not None:
                target_sound.play()

        # Draw everything
        screen.fill(BACKGROUND_COLOR)  # Fill the fullscreen with background color
        game_surface.fill(BACKGROUND_COLOR)
        
        draw_arena()
        draw_target(target_pos)
        draw_player_avatar(player_pos, player_angle)
        # Calculate time remaining (only for timed modes)
        if TRIAL_DURATION is not None:
            time_remaining = max(0, TRIAL_DURATION - current_time)
        else:
            time_remaining = None
        
        draw_score_and_timer(score, time_remaining)
        draw_trial_counter()
        
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()

        # Check if time has elapsed (only for timed modes)
        if TRIAL_DURATION is not None and current_time >= TRIAL_DURATION:
            running = False

    # Stop all sounds when trial ends
    if beep_channel is not None:
        beep_channel.stop()
    if target_channel is not None:
        target_channel.stop()
    
    # Create discrete log entry
    game_duration = time.time() - game_start_time
    discrete_log = {
        "trial": trial_info,
        "final_score": score,
        "trial_duration": TRIAL_DURATION if TRIAL_DURATION is not None else "endless",
        "target_locations": json.dumps(target_locations),
        "target_reach_times": json.dumps(target_reach_times),
        "game_duration": round(game_duration, 2)
    }
    
    # Add fixation logs (including trigger events) to the beginning of continuous_log if in fMRI mode
    # fixation_logs is always initialized in fMRI mode, so merge it into continuous_log
    if MODE == 'fmri' and 'fixation_logs' in locals():
        continuous_log = fixation_logs + continuous_log
        print(f"Added {len(fixation_logs)} fixation/trigger log entries to continuous log (trial {current_trial})")
    
    # Show final instruction image for practice mode only
    # No TR alignment needed for fMRI mode since snake trials are already TR-aligned
    if MODE == 'practice':
        show_image(os.path.join(INSTRUCTIONS_DIR, "10.png"))
    elif MODE == 'fmri':
        # Snake trials are TR-aligned (duration = exact multiple of TRs)
        # No additional TR alignment fixation needed
        if 'TRIAL_TRs' in locals():
            print(f'Snake trial completed at TR boundary (duration: {TRIAL_TRs} TRs = {TRIAL_DURATION}s)')
        else:
            print(f'Snake trial completed at TR boundary (duration: {TRIAL_DURATION}s)')
        # Thank you screen is handled by the final one_target trial, not snake trials
    elif MODE == 'anatomical':
        # Anatomical mode: no final instruction needed, game ends when manually terminated
        print('Anatomical scan snake game completed (manually terminated)')
    
    # Save logs after all fixation data is included
    save_continuous_log(continuous_log, continuous_filename)
    save_discrete_log([discrete_log], discrete_filename)
    
    if TRIAL_DURATION is not None:
        print(f"Snake game complete! Final score: {score} in {TRIAL_DURATION} seconds")
    else:
        print(f"Snake game complete! Final score: {score} (endless anatomical scan mode)")
    if MODE == 'fmri':
        print(f"Trial {snake_trial_number}/{snake_total_trials} completed")
    print(f"Data saved to: {continuous_filename}")
    
    # Close trigger connection if scanning
    if scanning and trigger_manager is not None:
        trigger_manager.close_trigger()

if __name__ == "__main__":
    print(f"Starting Snake Game")
    print(f"Mode: {MODE}")
    print(f"Participant: {player_initials}")
    if TRIAL_DURATION is not None:
        print(f"Trial Duration: {TRIAL_DURATION} seconds")
    else:
        print("Trial Duration: Endless (anatomical scan mode)")
    if MODE == 'fmri':
        print(f"Run: {run_number}")
    
    run_practice_game()
    pygame.quit()
    sys.exit() 