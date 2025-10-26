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
args = parser.parse_args()

MODE = args.mode
player_initials = args.participant
run_number = args.run
current_trial = args.trial
total_trials = args.total_trials
screen_number = args.screen
TR = 2.01  # Fixed TR for fMRI experiments

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
    if run_number == 1:
        run_context = "OT"
    elif run_number == 2:
        run_context = "FA"
    else:
        # Fallback for any other run numbers
        run_context = f"run{run_number}"
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
# Sounds
# ---------------------------
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")

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
        beep_sound.set_volume(0.8)
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
        counter_text = f"{current_trial}/{total_trials}"
        counter_font = pygame.font.SysFont("Arial", 24)
        counter_surface = counter_font.render(counter_text, True, WHITE)
        counter_rect = counter_surface.get_rect()
        counter_rect.bottomright = (WIN_WIDTH - 20, WIN_HEIGHT - 20)
        game_surface.blit(counter_surface, counter_rect)

# ---------------------------
# Logging functions
# ---------------------------
def save_continuous_log(logs, filename):
    """Save continuous log to CSV file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    try:
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["RealTime", "trial_time", "trial", "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y"]
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
                fieldnames = ["RealTime", "trial_time", "trial", "phase", "event", "x", "y", "rotation_angle", "score", "target_x", "target_y"]
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
            "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0,  # No position during fixation
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
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
                            "phase": "fixation",
                            "event": "fixation_skipped",
                            "x": 0.0,
                            "y": 0.0,
                            "rotation_angle": 0.0,
                            "score": 0,
                            "target_x": 0.0,
                            "target_y": 0.0
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
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
        }
        continuous_log.append(entry)

# ---------------------------
# Practice Game
# ---------------------------
def run_practice_game():
    """Run the practice game with different targets based on mode."""
    
    print(f"Starting snake game - Mode: {MODE}, Trial Duration: {TRIAL_DURATION} seconds")
    
    # Trigger handling moved to MATLAB level
    trigger_manager = None
    
    # Show instructions based on mode
    if MODE == 'practice':
        # Practice mode: show 1.png and wait for key press
        show_image(os.path.join(INSTRUCTIONS_DIR, "1.png"))
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
                "trial": str(run_number),
                "phase": "trigger",
                "event": "trigger_received",
                "x": 0.0,
                "y": 0.0,
                "rotation_angle": 0.0,
                "score": 0,
                "target_x": 0.0,
                "target_y": 0.0
            }
            print(f"Logged trigger received at time: {trigger_time}")
        
        # Create fixation log entries to be added to the continuous log
        fixation_logs = []
        
        # Add trigger entry if available
        if trigger_received_time:
            fixation_logs.append(trigger_entry)
        
        # Log fixation start event
        if MODE == 'fmri':
            trial_info = str(run_number)
        elif MODE == 'anatomical':
            trial_info = "anatomical"
        else:
            trial_info = "practice"
        fixation_start_entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": 0.0,  # Fixation is before trial starts
            "trial": trial_info,
            "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0,  # No position during fixation
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
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
            "trial": trial_info,
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
        }
        fixation_logs.append(fixation_end_entry)
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
    
    # Initialize logging
    continuous_log = []
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
            trial_info = str(run_number)
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
                elif event.key in [pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]:
                    active_keys.add(event.key)
            if event.type == pygame.KEYUP:
                # Remove keys when released
                if event.key in [pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]:
                    active_keys.discard(event.key)

        # Handle movement with number keys - compatible with MRI control box
        # Use both active_keys tracking and get_pressed() for maximum compatibility
        
        # Rotation controls
        if pygame.K_7 in active_keys or pygame.key.get_pressed()[pygame.K_7]:  # Rotate left
            player_angle -= PRACTICE_ROTATE_SPEED * dt
        if pygame.K_0 in active_keys or pygame.key.get_pressed()[pygame.K_0]:  # Rotate right
            player_angle += PRACTICE_ROTATE_SPEED * dt
            
        # Movement controls
        if pygame.K_8 in active_keys or pygame.key.get_pressed()[pygame.K_8]:  # Move forward
            rad = math.radians(player_angle)
            dx = MOVE_SPEED * dt * math.sin(rad)
            dy = MOVE_SPEED * dt * math.cos(rad)
            new_x = player_pos[0] + dx
            new_y = player_pos[1] + dy
            if within_arena([new_x, new_y]):
                player_pos[0] = new_x
                player_pos[1] = new_y
                
        if pygame.K_9 in active_keys or pygame.key.get_pressed()[pygame.K_9]:  # Move backward
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
    
    # Add fixation logs to the beginning of continuous_log if in fMRI mode
    if MODE == 'fmri' and 'fixation_logs' in locals():
        continuous_log = fixation_logs + continuous_log
    
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
        print(f"Trial {current_trial}/{total_trials} completed")
    print(f"Data saved to: {continuous_filename}")

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