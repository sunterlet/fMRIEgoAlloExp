import pygame
import math
import sys
import time
import os
import random
import json
import csv

# ---------------------------
# Configuration parameters (Experiment)
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0   # 1.65 m
BORDER_THRESHOLD = 0.1              # threshold from border in meters

# Target parameters
TARGET_RADIUS = 0.1                 # reduced target radius in meters
GRID_SIZE = 0.1                     # size of grid cells for visited locations tracking

# Movement settings
MOVE_SPEED = 1.0                    # meters per second
ROTATE_SPEED = 90.0                 # degrees per second

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
SOUNDS_DIR = "/Volumes/ramot/sunt/Navigation/fMRI/sounds/"
TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")

# ---------------------------
# Experiment parameters
# ---------------------------
TRAINING_SESSIONS = 3
DARK_TRAINING_TRIALS = 2
TEST_TRIALS = 5

# ---------------------------
# Prompt for player initials and set filenames
# ---------------------------
player_initials = input("Enter player initials: ").strip()
results_dir = "/Volumes/ramot/sunt/Navigation/fMRI/pythontry/results"
discrete_filename = os.path.join(results_dir, f"{player_initials}_discrete_log.csv")
continuous_filename = os.path.join(results_dir, f"{player_initials}_continuous_log.csv")

# ---------------------------
# Path to instruction images
# ---------------------------
INSTRUCTIONS_DIR = "/Volumes/ramot/sunt/Navigation/fMRI/pythontry/Instructions/"

# ---------------------------
# Initialize Pygame and Mixer
# ---------------------------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Exploration Experiment")
clock = pygame.time.Clock()

# ---------------------------
# Initialize Sounds
# ---------------------------
try:
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
except Exception as e:
    print("Error loading beep sound:", e)
    beep_sound = None
beep_channel = None

try:
    target_sound_constant = pygame.mixer.Sound(TARGET_SOUND_PATH)
except Exception as e:
    print("Error loading target sound:", e)
    target_sound_constant = None

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

def draw_thermometer(distance_moved):
    """Draw a horizontal bar (thermometer) at the top-left showing distance moved."""
    bar_x, bar_y = 50, 30
    max_bar_width = int(ARENA_DIAMETER * SCALE)
    bar_height = 20
    accumulation_factor = 200
    bar_width = min(max_bar_width, int(distance_moved * accumulation_factor))
    
    font = pygame.font.SysFont("Arial", 20)
    label_text = font.render("Forward/Backward Movement", True, WHITE)
    screen.blit(label_text, (bar_x, bar_y - 25))
    
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    pygame.draw.rect(screen, TARGET_COLOR, (bar_x, bar_y, bar_width, bar_height))

def draw_clock(angle_rotated):
    """Draw a clock-like dial at the top-right showing rotation angle."""
    dial_center = (WIN_WIDTH - 100, 75)
    dial_radius = 50

    font = pygame.font.SysFont("Arial", 20)
    label_text = font.render("Rotation Angle", True, WHITE)
    label_rect = label_text.get_rect(center=(dial_center[0], dial_center[1] - dial_radius - 15))
    screen.blit(label_text, label_rect)

    pygame.draw.circle(screen, WHITE, dial_center, dial_radius, 2)
    rad = math.radians(angle_rotated)
    end_x = dial_center[0] + dial_radius * math.sin(rad)
    end_y = dial_center[1] - dial_radius * math.cos(rad)
    pygame.draw.line(screen, CLOCK_COLOR, dial_center, (int(end_x), int(end_y)), 4)
    angle_text = font.render(f"{angle_rotated:.1f}°", True, WHITE)
    screen.blit(angle_text, (dial_center[0] - 20, dial_center[1] - 10))

def draw_arena():
    """Draw the arena border as a circle centered on the screen (Ivory)."""
    pygame.draw.circle(screen, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)

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
    pygame.draw.polygon(screen, color, [tip, left, right])

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

# ---------------------------
# Function to display an instruction image
# ---------------------------
def show_image(image_path):
    """Load and display a PNG image (assumed 1000×800) on the screen,
       then wait for the user to press a key (except Escape, which exits)."""
    try:
        instruction_image = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return
    
    screen.blit(instruction_image, (0, 0))
    pygame.display.flip()
    
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
                elif event.key == pygame.K_RETURN:  # Only the Enter key will break the loop
                    waiting = False
        clock.tick(15)

# ---------------------------
# Trial function with logging (Experiment)
# ---------------------------
def run_trial(is_training, target_sound, trial_info, display_on_border=False):
    global beep_channel, BACKGROUND_COLOR
    if target_sound is None:
        target_sound = target_sound_constant
    phase = "exploration"  # phases: exploration, annotation, feedback

    # Generate random target placement delay between 8-15 seconds
    target_placement_delay = random.uniform(8, 15)
    target_placement_time = time.time() + target_placement_delay

    player_pos = [0.0, 0.0]
    player_angle = 0.0
    move_key_pressed = None
    move_start_pos = None
    rotate_key_pressed = None
    rotate_start_angle = None
    target_was_inside = False
    annotation_marker_pos = [0.0, 0.0]
    annotation_marker_angle = 0.0

    # For target placement tracking
    visited_cells = set()
    target_placed = False
    target_position = None
    movement_start_time = None
    has_moved_forward = False
    has_rotated = False
    is_moving = False

    trial_start_time = time.time()
    exploration_start_time = trial_start_time
    annotation_start_time = None
    continuous_log = []
    encountered_goal = None

    trial_done = False
    while not trial_done:
        dt = clock.tick(60) / 1000.0
        current_trial_time = time.time() - trial_start_time

        if phase in ["exploration", "annotation"]:
            if phase == "exploration":
                entry = {
                    "trial_info": trial_info,
                    "phase": "exploration",
                    "time": current_trial_time,
                    "x": player_pos[0],
                    "y": player_pos[1]
                }
            else:
                entry = {
                    "trial_info": trial_info,
                    "phase": "annotation",
                    "time": current_trial_time,
                    "x": annotation_marker_pos[0],
                    "y": annotation_marker_pos[1]
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
                if event.key == pygame.K_RETURN:
                    if phase == "exploration":
                        exploration_time = time.time() - exploration_start_time
                        phase = "annotation"
                        annotation_start_time = time.time()
                        annotation_marker_pos = [0.0, 0.0]
                        annotation_marker_angle = 0.0
                        if beep_channel is not None:
                            beep_channel.stop()
                            beep_channel = None
                    elif phase == "annotation":
                        annotation_time = time.time() - annotation_start_time
                        phase = "feedback"
                    elif phase == "feedback":
                        trial_done = True
                if phase == "exploration":
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        if move_key_pressed is None:
                            move_key_pressed = event.key
                            move_start_pos = list(player_pos)
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        if rotate_key_pressed is None:
                            rotate_key_pressed = event.key
                            rotate_start_angle = player_angle
            if event.type == pygame.KEYUP:
                if phase == "exploration":
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        move_key_pressed = None
                        move_start_pos = None
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        rotate_key_pressed = None
                        rotate_start_angle = None

        screen.fill(BACKGROUND_COLOR)

        if phase == "exploration":
            keys = pygame.key.get_pressed()
            current_is_moving = keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
            
            # Start movement timer on first movement
            if current_is_moving and movement_start_time is None:
                movement_start_time = time.time()
            
            # Track movement and rotation
            if keys[pygame.K_UP]:
                has_moved_forward = True
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                has_rotated = True

            # Update player position and angle
            if keys[pygame.K_UP]:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
                    add_visited_position(player_pos, visited_cells)
            if keys[pygame.K_DOWN]:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] - dx
                new_y = player_pos[1] - dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
                    add_visited_position(player_pos, visited_cells)
            if keys[pygame.K_LEFT]:
                player_angle -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT]:
                player_angle += ROTATE_SPEED * dt

            # Check border collision and play beep sound
            if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                if beep_sound is not None:
                    if beep_channel is None or not beep_channel.get_busy():
                        beep_channel = beep_sound.play(loops=-1)
            else:
                if beep_channel is not None:
                    beep_channel.stop()
                    beep_channel = None

            # Place target if conditions are met
            if not target_placed and movement_start_time is not None:
                current_time = time.time()
                if current_time >= target_placement_time and has_moved_forward and has_rotated and current_is_moving:
                    # Check if current position is not too close to border
                    if math.hypot(player_pos[0], player_pos[1]) <= (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD):
                        target_pos = player_pos.copy()
                        target_placed = True
                        if target_sound is not None:
                            target_sound.play()

            # Check if player is at target position
            if target_position is not None:
                if distance(player_pos, target_position) <= TARGET_RADIUS:
                    if not target_was_inside:
                        if target_sound is not None:
                            target_sound.play()
                        encountered_goal = target_position
                    target_was_inside = True
                else:
                    target_was_inside = False

            # Draw arena and player
            draw_arena()
            draw_player_avatar(player_pos, player_angle)

            # Draw target if K is pressed and target is placed
            if keys[pygame.K_k] and target_placed and target_position is not None:
                target_screen = to_screen_coords(target_position)
                pygame.draw.circle(screen, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 0)

            # Draw movement indicators
            if move_key_pressed is not None and move_start_pos is not None:
                moved_distance = math.hypot(player_pos[0] - move_start_pos[0], player_pos[1] - move_start_pos[1])
                draw_thermometer(moved_distance)
            if rotate_key_pressed is not None and rotate_start_angle is not None:
                angle_diff = player_angle - rotate_start_angle
                draw_clock(angle_diff)

        elif phase == "annotation":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                annotation_marker_angle -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT]:
                annotation_marker_angle += ROTATE_SPEED * dt
            if keys[pygame.K_UP]:
                rad = math.radians(annotation_marker_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = annotation_marker_pos[0] + dx
                new_y = annotation_marker_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[0] = new_x
                    annotation_marker_pos[1] = new_y
            if keys[pygame.K_DOWN]:
                rad = math.radians(annotation_marker_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = annotation_marker_pos[0] - dx
                new_y = annotation_marker_pos[1] - dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[0] = new_x
                    annotation_marker_pos[1] = new_y
            draw_arena()
            # Add instruction text in the top-left corner
            font = pygame.font.SysFont("Arial", 20)
            instruction_text = font.render("Navigate to the location of the target, and press Enter to finalize your decision", True, WHITE)
            screen.blit(instruction_text, (20, 20))
            # Draw annotation avatar in Khaki (CLOCK_COLOR)
            draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)

        elif phase == "feedback":
            draw_arena()
            if target_position is not None:
                target_screen = to_screen_coords(target_position)
                pygame.draw.circle(screen, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 0)
            # Draw feedback avatar in Khaki (CLOCK_COLOR)
            draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
        
        if trial_info.startswith("training"):
            total_trials = TRAINING_SESSIONS
        elif trial_info.startswith("dark_training"):
            total_trials = DARK_TRAINING_TRIALS
        elif trial_info.startswith("test"):
            total_trials = TEST_TRIALS
        else:
            total_trials = "?"
        current_trial = trial_info.split()[1]
        counter_text = f"{current_trial}/{total_trials}"
        counter_font = pygame.font.SysFont("Arial", 24)
        counter_surface = counter_font.render(counter_text, True, WHITE)
        counter_rect = counter_surface.get_rect()
        counter_rect.bottomright = (WIN_WIDTH - 20, WIN_HEIGHT - 20)
        screen.blit(counter_surface, counter_rect)

        pygame.display.flip()

    exploration_time = time.time() - exploration_start_time if exploration_start_time is not None else 0
    annotation_time = time.time() - annotation_start_time if annotation_start_time is not None else 0
    error_distance = None
    if encountered_goal is not None:
        error_distance = distance(encountered_goal, annotation_marker_pos)
    discrete_log = {
        "trial_type": "training" if is_training else "test",
        "exploration_time": exploration_time,
        "annotation_time": annotation_time,
        "encountered_goal": encountered_goal,
        "annotation": annotation_marker_pos,
        "error_distance": error_distance
    }
    return discrete_log, continuous_log

# ---------------------------
# Functions to save logs to CSV (Experiment)
# ---------------------------
def save_discrete_log(logs, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "trial_info", "trial_type", "exploration_time", "annotation_time",
            "encountered_goal", "annotation", "error_distance"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            log_copy = log.copy()
            log_copy["encountered_goal"] = json.dumps(log_copy["encountered_goal"])
            log_copy["annotation"] = json.dumps(log_copy["annotation"])
            writer.writerow(log_copy)

def save_continuous_log(logs, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["trial_info", "phase", "time", "x", "y"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in logs:
            writer.writerow(row)

# ---------------------------
# Main Experiment Loop
# ---------------------------
def run_experiment():
    """Run a single training trial."""
    # Initialize Pygame and audio
    pygame.init()
    pygame.mixer.init()
    # Create display and clock
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Single Training Trial")
    clock = pygame.time.Clock()

    # Load the training target sound
    training_target_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)

    # Run one training trial
    trial_info = "training 1"
    discrete_log, continuous_log = run_trial(True, training_target_sound, trial_info)

    # Save logs for this single trial
    save_discrete_log([discrete_log], f"{player_initials}_training1_discrete.csv")
    save_continuous_log(continuous_log, f"{player_initials}_training1_continuous.csv")

    # Clean up and exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_experiment()
