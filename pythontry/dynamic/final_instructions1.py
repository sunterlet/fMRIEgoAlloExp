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
GRID_SIZE = 0.05                    # size of grid cells for visited locations tracking (reduced from 0.1)

# Movement settings
MOVE_SPEED = 1.0                    # meters per second
ROTATE_SPEED = 60.0                 # degrees per second (reduced from 90.0)
PRACTICE_ROTATE_SPEED = 70.0        # degrees per second for practice game

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
DARK_TRAINING_TRIALS = 3
TEST_TRIALS = 5

# ---------------------------
# Prompt for player initials and set filenames
# ---------------------------
player_initials = input("Enter player initials: ").strip()
results_dir = "/Volumes/ramot/sunt/Navigation/fMRI/pythontry/dynamic/results"
discrete_filename = os.path.join(results_dir, f"{player_initials}_discrete_log.csv")
continuous_filename = os.path.join(results_dir, f"{player_initials}_continuous_log.csv")

# Ensure results directory exists
os.makedirs(results_dir, exist_ok=True)

# Enable debug mode if initials are '111'
DEBUG_MODE = (player_initials == '111')

# ---------------------------
# Path to instruction images
# ---------------------------
INSTRUCTIONS_DIR = "/Volumes/ramot/sunt/Navigation/fMRI/pythontry/Instructions/"

# ---------------------------
# Initialize Pygame and Mixer
# ---------------------------
pygame.init()
pygame.mixer.init()

# Create fullscreen display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Calculate the offset to center the game area
offset_x = (screen_width - WIN_WIDTH) // 2
offset_y = (screen_height - WIN_HEIGHT) // 2

# Create a surface for the game content
game_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

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
def show_image(image_path):
    """Load and display a PNG image (assumed 1000×800) on the screen,
       then wait for the user to press a key (except Escape, which exits)."""
    try:
        instruction_image = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        return
    
    game_surface.blit(instruction_image, (0, 0))
    screen.blit(game_surface, (offset_x, offset_y))
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
    game_surface.blit(label_text, (bar_x, bar_y - 25))
    
    pygame.draw.rect(game_surface, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    pygame.draw.rect(game_surface, TARGET_COLOR, (bar_x, bar_y, bar_width, bar_height))

def draw_clock(angle_rotated):
    """Draw a clock-like dial at the top-right showing rotation angle."""
    dial_center = (WIN_WIDTH - 100, 75)
    dial_radius = 50

    font = pygame.font.SysFont("Arial", 20)
    label_text = font.render("Rotation Angle", True, WHITE)
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
def run_trial(is_training, target_sound, trial_info, display_on_border=False):
    global beep_channel, BACKGROUND_COLOR
    if target_sound is None:
        target_sound = target_sound_constant
    phase = "exploration"  # phases: exploration, annotation, feedback

    # Generate random target placement delay (whole number between 8-15 seconds)
    target_placement_delay = random.randint(8, 15)
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

    # For target placement tracking
    visited_cells = set()
    target_placed = False
    target_position = None
    movement_start_time = None
    target_placed_time = None  # Track when target was actually placed
    has_moved_forward = False
    has_rotated = False
    is_moving = False

    trial_start_time = time.time()
    exploration_start_time = trial_start_time
    annotation_start_time = None
    continuous_log = []
    encountered_goal = None

    trial_done = False

    # Add this before the main loop in run_trial:
    last_tip_cell = None
    current_tip_cell = None

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
                # Check if player is moving forward/backward (UP/DOWN) and not rotating (LEFT/RIGHT)
                keys = pygame.key.get_pressed()
                is_moving_forward_backward = keys[pygame.K_UP] or keys[pygame.K_DOWN]
                is_rotating = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
                
                # Check all conditions for target placement
                if (has_moved_forward and 
                    has_rotated and 
                    is_moving_forward_backward and 
                    not is_rotating and
                    distance_from_center >= 0.5 and
                    distance_from_center <= (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD)):
                    target_position = (player_pos[0], player_pos[1])
                    target_placed = True
                    target_placed_time = time.time()  # Record when target was placed
                    if target_sound is not None:
                        target_sound.play()

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
                
                entry = {
                    "trial_info": trial_info,
                    "phase": "exploration",
                    "trial_time": round(current_trial_time, 3),
                    "event": current_event,
                    "x": round(player_pos[0], 3),
                    "y": round(player_pos[1], 3)
                }
                if DEBUG_MODE and current_event:
                    print(f"DEBUG: Adding log entry with event: {current_event}")
            else:
                entry = {
                    "trial_info": trial_info,
                    "phase": "annotation",
                    "trial_time": round(current_trial_time, 3),
                    "event": None,  # No events during annotation phase
                    "x": round(annotation_marker_pos[0], 3),
                    "y": round(annotation_marker_pos[1], 3)
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
                        # Add target_annotated event when Enter is pressed in annotation phase
                        entry = {
                            "trial_info": trial_info,
                            "phase": "annotation",
                            "trial_time": round(current_trial_time, 3),
                            "event": "target_annotated",
                            "x": round(annotation_marker_pos[0], 3),
                            "y": round(annotation_marker_pos[1], 3)
                        }
                        continuous_log.append(entry)
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
                if event.key == pygame.K_k:
                    pass
            if event.type == pygame.KEYUP:
                if phase == "exploration":
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        move_key_pressed = None
                        move_start_pos = None
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        rotate_key_pressed = None
                        rotate_start_angle = None

        screen.fill(BACKGROUND_COLOR)  # Fill the fullscreen with background color
        game_surface.fill(BACKGROUND_COLOR)

        if phase == "exploration":
            keys = pygame.key.get_pressed()
            current_is_moving = keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
            current_is_moving_forward_backward = keys[pygame.K_UP] or keys[pygame.K_DOWN]  # Track forward/backward movement
            current_is_rotating = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]  # Track rotation
            
            # Reset movement tracking when movement stops
            if not current_is_moving_forward_backward:
                distance_moved = 0.0
            if not current_is_rotating:
                angle_rotated = 0.0
                rotation_start_angle = None
            
            # Start movement timer on first movement
            if current_is_moving and movement_start_time is None:
                movement_start_time = time.time()
            
            # Track movement and rotation
            if keys[pygame.K_UP]:
                has_moved_forward = True
                is_moving_forward_backward = True
            if keys[pygame.K_DOWN]:
                is_moving_forward_backward = True
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                has_rotated = True
                is_moving_forward_backward = False  # Reset forward/backward movement flag during rotation
                # Set rotation start angle when rotation begins
                if rotation_start_angle is None:
                    rotation_start_angle = player_angle

            # Update player position and angle
            old_pos = list(player_pos)  # Store old position
            old_angle = player_angle    # Store old angle
            
            if keys[pygame.K_UP]:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
            if keys[pygame.K_DOWN]:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] - dx
                new_y = player_pos[1] - dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
            if keys[pygame.K_LEFT]:
                player_angle -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT]:
                player_angle += ROTATE_SPEED * dt

            # Update movement tracking
            if current_is_moving_forward_backward:
                # Calculate distance moved (forward/backward only)
                distance_moved += math.hypot(player_pos[0] - old_pos[0], player_pos[1] - old_pos[1])
            
            # Update rotation tracking with signed values
            if current_is_rotating and rotation_start_angle is not None:
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

            # If we've moved to a new cell, mark the previous cell as visited
            if last_tip_cell is not None and current_tip_cell != last_tip_cell:
                visited_cells.add(last_tip_cell)

            # Check border collision and play beep sound
            if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                if beep_sound is not None:
                    if beep_channel is None or not beep_channel.get_busy():
                        beep_channel = beep_sound.play(loops=-1)
            else:
                if beep_channel is not None:
                    beep_channel.stop()
                    beep_channel = None

            # Check if all conditions are met
            all_conditions_met = (
                target_placement_time is not None and
                time.time() >= target_placement_time and
                has_moved_forward and
                has_rotated and
                (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and
                not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and
                math.hypot(player_pos[0], player_pos[1]) >= 0.5 and
                math.hypot(player_pos[0], player_pos[1]) <= (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD)
            )

            # Check if current cell has been visited before
            is_new_location = current_tip_cell not in visited_cells
            entered_new_cell = last_tip_cell is None or current_tip_cell != last_tip_cell

            # Check if player is at target position
            if target_position is not None:
                if distance(player_pos, target_position) <= TARGET_RADIUS:
                    if not target_was_inside:
                        if DEBUG_MODE:
                            print(f"DEBUG: Target reached at time {time.time() - trial_start_time:.2f}")
                            print(f"DEBUG: Target was placed at {target_placed_time - trial_start_time:.2f}")
                        if target_sound is not None:
                            target_sound.play()
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
                                "trial_info": trial_info,
                                "phase": "exploration",
                                "trial_time": round(current_trial_time, 3),
                                "event": current_event,
                                "x": round(player_pos[0], 3),
                                "y": round(player_pos[1], 3)
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
                is_new_location):
                
                if DEBUG_MODE:
                    print("DEBUG: Placing target - all conditions met")
                
                # Place the target so its border is at the tip position
                rad = math.radians(player_angle)
                target_center_x = tip_pos[0] - TARGET_RADIUS * math.sin(rad)
                target_center_y = tip_pos[1] - TARGET_RADIUS * math.cos(rad)
                target_position = (target_center_x, target_center_y)
                target_placed = True
                target_placed_time = time.time()  # Record when target was placed
                if target_sound is not None:
                    target_sound.play()
                if DEBUG_MODE:
                    print(f"DEBUG: Target placed at time {time.time() - trial_start_time:.2f}")
                current_event = "target_placed"

            # Always update last_tip_cell
            last_tip_cell = current_tip_cell

            # Draw arena and player
            if "dark_training" in trial_info:
                # In dark training, show avatar at start and when near border
                if not current_is_moving and movement_start_time is None:
                    # Show avatar and arena only at the very start (before first movement)
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
                elif math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                    # Show avatar and arena when near border
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            elif "test" in trial_info:
                # In test trials, show avatar only at start
                if not current_is_moving and movement_start_time is None:
                    # Show avatar and arena only at the very start (before first movement)
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            else:
                # In normal trials, always show arena and avatar
                draw_arena()
                draw_player_avatar(player_pos, player_angle)

            # Draw movement indicators only when moving
            if current_is_moving_forward_backward:
                draw_thermometer(distance_moved)
            if current_is_rotating:
                draw_clock(angle_rotated)

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

            # Add continuous logging for annotation phase
            entry = {
                "trial_info": trial_info,
                "phase": "annotation",
                "trial_time": round(current_trial_time, 3),
                "event": None,  # No events during annotation phase
                "x": round(annotation_marker_pos[0], 3),
                "y": round(annotation_marker_pos[1], 3)
            }
            continuous_log.append(entry)

            draw_arena()
            # Add instruction text in the top-left corner
            font = pygame.font.SysFont("Arial", 20)
            instruction_text = font.render("Navigate to the location of the target, and press Enter to finalize your decision", True, WHITE)
            game_surface.blit(instruction_text, (20, 20))
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
            entry = {
                "trial_info": trial_info,
                "phase": "feedback",
                "trial_time": round(current_trial_time, 3),
                "event": None,  # No events during feedback phase
                "x": round(annotation_marker_pos[0], 3),
                "y": round(annotation_marker_pos[1], 3)
            }
            continuous_log.append(entry)

            draw_arena()
            if target_position is not None:
                target_screen = to_screen_coords(target_position)
                pygame.draw.circle(game_surface, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 0)
            # Draw feedback avatar in Khaki (CLOCK_COLOR)
            draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
        
        # Draw trial counter
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
        game_surface.blit(counter_surface, counter_rect)

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
                    if not current_is_moving and movement_start_time is None:
                        draw_arena()
                        draw_player_avatar(player_pos, player_angle)
                    elif math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                        draw_arena()
                        draw_player_avatar(player_pos, player_angle)
                elif "test" in trial_info:
                    # In test trials, show avatar only at start
                    if not current_is_moving and movement_start_time is None:
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

        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()

    exploration_time = time.time() - exploration_start_time if exploration_start_time is not None else 0
    annotation_time = time.time() - annotation_start_time if annotation_start_time is not None else 0
    error_distance = None
    if encountered_goal is not None:
        error_distance = distance(encountered_goal, annotation_marker_pos)
    
    discrete_log = {
        "trial": trial_info,
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
    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "trial",
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

def save_continuous_log(logs, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["trial_info", "phase", "trial_time", "event", "x", "y"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in logs:
            # Only write fields that exist in the row
            filtered_row = {k: v for k, v in row.items() if k in fieldnames}
            writer.writerow(filtered_row)

# ---------------------------
# Practice Game (Pre-Experiment)
# ---------------------------
def run_practice_game():
    """Run the practice game where the player must reach a score of 15."""
    # Get the current display info
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    
    # Calculate the offset to center the game area
    offset_x = (screen_width - WIN_WIDTH) // 2
    offset_y = (screen_height - WIN_HEIGHT) // 2
    
    # Create a surface for the game content
    game_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
    
    arena_center = (WIN_WIDTH // 2, WIN_HEIGHT // 2)
    arena_radius = int(ARENA_RADIUS * SCALE)  # 1.65 * 200 = 330 pixels

    # Avatar settings (practice)
    avatar_pos = [arena_center[0], arena_center[1]]
    avatar_angle = 0
    avatar_speed = 3
    avatar_size = 15

    # Goal settings (practice)
    goal_radius = 10

    # Sound settings
    beep_channel = None

    def random_position_in_arena():
        angle = random.uniform(0, 2 * math.pi)
        r = arena_radius * math.sqrt(random.uniform(0, 1))
        x = arena_center[0] + r * math.cos(angle)
        y = arena_center[1] + r * math.sin(angle)
        return (x, y)

    goal_pos = random_position_in_arena()
    score = 0
    font = pygame.font.SysFont(None, 36)

    def draw_arena():
        pygame.draw.circle(game_surface, BORDER_COLOR, arena_center, arena_radius, 2)

    def draw_goal():
        pygame.draw.circle(game_surface, TARGET_COLOR, (int(goal_pos[0]), int(goal_pos[1])), goal_radius)

    def draw_avatar():
        tip_length = 30
        base_length = 20
        half_width = 17

        angle_rad = math.radians(avatar_angle)
        tip = (avatar_pos[0] + tip_length * math.cos(angle_rad),
               avatar_pos[1] + tip_length * math.sin(angle_rad))
        base_center = (avatar_pos[0] - base_length * math.cos(angle_rad),
                       avatar_pos[1] - base_length * math.sin(angle_rad))
        left_point = (base_center[0] + half_width * math.cos(angle_rad + math.pi/2),
                      base_center[1] + half_width * math.sin(angle_rad + math.pi/2))
        right_point = (base_center[0] + half_width * math.cos(angle_rad - math.pi/2),
                       base_center[1] + half_width * math.sin(angle_rad - math.pi/2))
        pygame.draw.polygon(game_surface, AVATAR_COLOR, [tip, left_point, right_point])

    def draw_score():
        # Render score in Khaki (CLOCK_COLOR)
        score_text = font.render(f"Score: {score}", True, CLOCK_COLOR)
        game_surface.blit(score_text, (10, 10))

    def within_arena(new_pos):
        dist = math.hypot(new_pos[0] - arena_center[0], new_pos[1] - arena_center[1])
        return dist <= arena_radius - avatar_size

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Get time since last frame in seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    running = False

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_UP]:
            dx += avatar_speed * math.cos(math.radians(avatar_angle))
            dy += avatar_speed * math.sin(math.radians(avatar_angle))
        if keys[pygame.K_DOWN]:
            dx -= avatar_speed * math.cos(math.radians(avatar_angle))
            dy -= avatar_speed * math.sin(math.radians(avatar_angle))
        new_pos = [avatar_pos[0] + dx, avatar_pos[1] + dy]
        if within_arena(new_pos):
            avatar_pos = new_pos

        if keys[pygame.K_LEFT]:
            avatar_angle -= PRACTICE_ROTATE_SPEED * dt  # Use practice rotation speed
        if keys[pygame.K_RIGHT]:
            avatar_angle += PRACTICE_ROTATE_SPEED * dt  # Use practice rotation speed

        # Check border collision and play beep sound
        if math.hypot(avatar_pos[0] - arena_center[0], avatar_pos[1] - arena_center[1]) >= (arena_radius - BORDER_THRESHOLD * SCALE):
            if beep_sound is not None:
                if beep_channel is None or not beep_channel.get_busy():
                    beep_channel = beep_sound.play(loops=-1)
        else:
            if beep_channel is not None:
                beep_channel.stop()
                beep_channel = None

        # Check collision with the goal using the tip of the avatar
        tip_length = 30
        rad = math.radians(avatar_angle)
        tip_x = avatar_pos[0] + tip_length * math.cos(rad)
        tip_y = avatar_pos[1] + tip_length * math.sin(rad)
        if math.hypot(tip_x - goal_pos[0], tip_y - goal_pos[1]) < (goal_radius + 5):
            score += 1
            goal_pos = random_position_in_arena()
            if target_sound_constant is not None:
                target_sound_constant.play()

        screen.fill(BACKGROUND_COLOR)  # Fill the fullscreen with background color
        game_surface.fill(BACKGROUND_COLOR)
        draw_arena()
        draw_goal()
        draw_avatar()
        draw_score()
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()

        if score >= 5:
            running = False

# ---------------------------
# Main Experiment Loop
# ---------------------------
def run_experiment():
    """Run the experiment with all trials."""
    # 1. Show Welcome
    show_image(os.path.join(INSTRUCTIONS_DIR, "1.png"))
    
    # 2. Show Practice Game instructions
    show_image(os.path.join(INSTRUCTIONS_DIR, "2.png"))
    
    # 3. Run Practice Game
    run_practice_game()

    # 4. Show Training Block instructions
    show_image(os.path.join(INSTRUCTIONS_DIR, "3.png"))

    # Load the training target sound
    training_target_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)

    # Initialize lists for logs
    all_discrete_logs = []
    all_continuous_logs = []

    # Training trials
    for i in range(1, TRAINING_SESSIONS + 1):
        trial_info = f"training {i}"
        discrete_log, continuous_log = run_trial(True, training_target_sound, trial_info)
        all_discrete_logs.append(discrete_log)
        all_continuous_logs.extend(continuous_log)
        # Save after each training trial
        save_discrete_log(all_discrete_logs, discrete_filename)
        save_continuous_log(all_continuous_logs, continuous_filename)

    # 5. Show Dark Training instructions
    show_image(os.path.join(INSTRUCTIONS_DIR, "4.png"))

    # Dark training trials
    for i in range(1, DARK_TRAINING_TRIALS + 1):
        trial_info = f"dark_training {i}"
        discrete_log, continuous_log = run_trial(True, training_target_sound, trial_info)
        all_discrete_logs.append(discrete_log)
        all_continuous_logs.extend(continuous_log)
        # Save after each dark training trial
        save_discrete_log(all_discrete_logs, discrete_filename)
        save_continuous_log(all_continuous_logs, continuous_filename)

    # 6. Show Testing Block instructions
    show_image(os.path.join(INSTRUCTIONS_DIR, "5.png"))

    # Test trials
    for i in range(1, TEST_TRIALS + 1):
        trial_info = f"test {i}"
        discrete_log, continuous_log = run_trial(False, training_target_sound, trial_info)
        all_discrete_logs.append(discrete_log)
        all_continuous_logs.extend(continuous_log)
        # Save after each test trial
        save_discrete_log(all_discrete_logs, discrete_filename)
        save_continuous_log(all_continuous_logs, continuous_filename)

    # 7. Show Final instructions
    show_image(os.path.join(INSTRUCTIONS_DIR, "6.png"))

    print("Experiment complete. Press Escape to exit.")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False
        clock.tick(15)

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

    # Create timing information dictionary
    timings = {
        "Trial Time": f"{current_time - trial_start_time:.2f}s",
        "Time Since First Move": f"{current_time - movement_start_time:.2f}" if movement_start_time else "Not started",
        "Assigned Delay": f"{assigned_delay}s",
        "Time Until Target": f"{time_until_target:.2f}s" if isinstance(time_until_target, (int, float)) else time_until_target,
        "Target Placement Time": f"{target_placed_time - movement_start_time:.2f}s" if target_placed_time is not None and movement_start_time is not None else "Not placed",
        "Exploration Time": f"{current_time - exploration_start_time:.2f}s",
        "Annotation Time": f"{current_time - annotation_start_time:.2f}s" if annotation_start_time else "Not started"
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
    run_experiment()
