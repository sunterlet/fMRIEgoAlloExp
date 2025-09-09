import pygame
import math
import sys
import time
import os
import random
import json
import csv

# ---------------------------
# Configuration parameters
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0   # 1.65 m
BORDER_THRESHOLD = 0.1              # threshold from border in meters

# Target parameters
TARGET_RADIUS = 0.1                 # reduced target radius in meters
DEFAULT_TARGET_COUNT = 3            # number of targets per trial

# Movement settings
MOVE_SPEED = 1.0                    # meters per second
ROTATE_SPEED = 90.0                 # degrees per second

# Scale factor: pixels per meter
SCALE = 200                         # 1 meter = 200 pixels

# Window size (to ensure the full arena is visible)
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HUD_COLOR = (0, 255, 0)
DEBUG_COLOR = (50, 50, 255)   # Used for debug visuals

# ---------------------------
# Sounds
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
# Predefined constant target positions per trial
# ---------------------------
PREDEFINED_TARGETS = {
    "training 1": [(-0.5, -1.0), (0.3, 0.8), (-1.0, 0.2)],
    "training 2": [(0.7, -0.8), (-0.4, 0.9), (0.0, -1.2)],
    "training 3": [(-0.8, -0.5), (0.5, 0.5), (0.2, -1.0)],
    "dark_training 1": [(-0.6, -0.9), (0.4, 0.7), (-0.9, 0.1)],
    "dark_training 2": [(0.2, -1.0), (-0.3, 0.8), (0.7, -0.6)],
    "test 1": [(0.0, 1.0), (-0.8, -0.2), (0.7, -0.7)],
    "test 2": [(-0.3, 0.7), (0.8, 0.2), (-0.9, -0.9)],
    "test 3": [(0.4, -0.4), (-0.6, 0.8), (0.2, 1.0)],
    "test 4": [(0.9, -0.3), (-0.4, -1.0), (0.0, 0.8)],
    "test 5": [(-0.2, -0.8), (0.5, 0.6), (-0.7, 0.0)]
}

# ---------------------------
# Initialize Pygame and Mixer
# ---------------------------
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("MRI Navigation Experiment")
clock = pygame.time.Clock()

# Load beep sound (for border)
try:
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
except Exception as e:
    print("Error loading beep sound:", e)
    beep_sound = None
beep_channel = None  # Global variable for looping beep sound

# Load constant target sound
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
    """Euclidean distance between two points (tuples)."""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_thermometer(distance_moved):
    """Draw a horizontal bar (thermometer) at the top-left showing distance moved."""
    bar_x, bar_y = 50, 50
    max_bar_width = 400
    bar_height = 20
    accumulation_factor = 200
    bar_width = min(max_bar_width, int(distance_moved * accumulation_factor))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    pygame.draw.rect(screen, HUD_COLOR, (bar_x, bar_y, bar_width, bar_height))

def draw_clock(angle_rotated):
    """Draw a clock-like dial at the top-right showing rotation angle."""
    dial_center = (WIN_WIDTH - 100, 100)
    dial_radius = 50
    pygame.draw.circle(screen, WHITE, dial_center, dial_radius, 2)
    rad = math.radians(angle_rotated)
    end_x = dial_center[0] + dial_radius * math.sin(rad)
    end_y = dial_center[1] - dial_radius * math.cos(rad)
    pygame.draw.line(screen, HUD_COLOR, dial_center, (int(end_x), int(end_y)), 4)
    font = pygame.font.SysFont("Arial", 20)
    angle_text = font.render(f"{angle_rotated:.1f}°", True, WHITE)
    screen.blit(angle_text, (dial_center[0] - 20, dial_center[1] - 10))

def draw_arena():
    """Draw the arena border as a circle centered on the screen."""
    pygame.draw.circle(screen, WHITE, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)

def draw_debug_items(player_pos, player_angle, current_target_positions):
    """Draw debug visuals: arena border, player marker, and target outlines."""
    pygame.draw.circle(screen, DEBUG_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)
    for pos in current_target_positions:
        target_screen = to_screen_coords(pos)
        pygame.draw.circle(screen, DEBUG_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 2)
    p_screen = to_screen_coords(player_pos)
    pygame.draw.circle(screen, (255, 0, 0), p_screen, 5)
    rad = math.radians(player_angle)
    line_length = 20
    end_x = p_screen[0] + int(line_length * math.sin(rad))
    end_y = p_screen[1] - int(line_length * math.cos(rad))
    pygame.draw.line(screen, (255, 0, 0), p_screen, (end_x, end_y), 2)

# ---------------------------
# Trial (session) function with logging
# ---------------------------
# New parameter: display_on_border controls dark trials.
def run_trial(is_training, target_sound, trial_info, display_on_border=False):
    global beep_channel, BLACK
    if target_sound is None:
        target_sound = target_sound_constant
    phase = "exploration"  # phases: exploration, annotation, feedback

    # Use predefined constant target positions for this trial.
    if trial_info in PREDEFINED_TARGETS:
        current_target_positions = PREDEFINED_TARGETS[trial_info].copy()
    else:
        current_target_positions = []  # fallback (should not occur)

    # Exploration state:
    player_pos = [0.0, 0.0]
    player_angle = 0.0
    move_key_pressed = None
    move_start_pos = None
    rotate_key_pressed = None
    rotate_start_angle = None
    target_was_inside = False
    annotation_marker_pos = [0.0, 0.0]
    # Initialize annotation marker angle for annotation phase:
    annotation_marker_angle = 0.0

    # Logging variables:
    trial_start_time = time.time()
    exploration_start_time = trial_start_time
    annotation_start_time = None
    continuous_log = []  # rows: trial_info, phase, time, x, y
    encountered_goal = None

    trial_done = False
    while not trial_done:
        dt = clock.tick(60) / 1000.0
        current_trial_time = time.time() - trial_start_time

        # Log continuous data during exploration and annotation phases.
        if phase in ["exploration", "annotation"]:
            if phase == "exploration":
                entry = {"trial_info": trial_info, "phase": "exploration", "time": current_trial_time, "x": player_pos[0], "y": player_pos[1]}
            else:
                entry = {"trial_info": trial_info, "phase": "annotation", "time": current_trial_time, "x": annotation_marker_pos[0], "y": annotation_marker_pos[1]}
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
                        # Reset annotation marker and its angle.
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
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        if move_key_pressed is None:
                            move_key_pressed = event.key
                            move_start_pos = list(player_pos)
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        if rotate_key_pressed is None:
                            rotate_key_pressed = event.key
                            rotate_start_angle = player_angle
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        move_key_pressed = None
                        move_start_pos = None
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        rotate_key_pressed = None
                        rotate_start_angle = None
            elif phase == "annotation":
                # In annotation phase, now use same control as exploration:
                if event.type == pygame.KEYDOWN:
                    # Up/Down move marker forward/backward relative to its current angle.
                    if event.key == pygame.K_UP:
                        # Move forward.
                        pass  # We'll handle movement continuously.
                    if event.key == pygame.K_DOWN:
                        pass
                    if event.key == pygame.K_LEFT:
                        # Rotate the annotation marker.
                        pass
                    if event.key == pygame.K_RIGHT:
                        pass

        # Clear screen.
        screen.fill(BLACK)

        if phase == "exploration":
            keys = pygame.key.get_pressed()
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

            if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                if beep_sound is not None:
                    if beep_channel is None or not beep_channel.get_busy():
                        beep_channel = beep_sound.play(loops=-1)
            else:
                if beep_channel is not None:
                    beep_channel.stop()
                    beep_channel = None

            is_inside_target = False
            encountered = None
            for pos in current_target_positions:
                if distance(player_pos, pos) <= TARGET_RADIUS:
                    is_inside_target = True
                    encountered = pos
                    break
            if not target_was_inside and is_inside_target:
                if target_sound is not None:
                    target_sound.play()
                print("Target reached at:", encountered)
                if encountered_goal is None:
                    encountered_goal = encountered
                current_target_positions = [encountered]
            target_was_inside = is_inside_target

            if is_training:
                draw_arena()
                p_screen = to_screen_coords(player_pos)
                pygame.draw.circle(screen, (255, 0, 0), p_screen, 5)
                rad = math.radians(player_angle)
                line_length = 20
                end_x = p_screen[0] + int(line_length * math.sin(rad))
                end_y = p_screen[1] - int(line_length * math.cos(rad))
                pygame.draw.line(screen, (255, 0, 0), p_screen, (end_x, end_y), 2)
                if keys[pygame.K_k]:
                    for pos in current_target_positions:
                        target_screen = to_screen_coords(pos)
                        pygame.draw.circle(screen, WHITE, target_screen, int(TARGET_RADIUS * SCALE), 2)
            else:
                if display_on_border:
                    if keys[pygame.K_k]:
                        draw_debug_items(player_pos, player_angle, current_target_positions)
                    else:
                        if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                            draw_arena()
                            p_screen = to_screen_coords(player_pos)
                            pygame.draw.circle(screen, (255, 0, 0), p_screen, 5)
                            rad = math.radians(player_angle)
                            line_length = 20
                            end_x = p_screen[0] + int(line_length * math.sin(rad))
                            end_y = p_screen[1] - int(line_length * math.cos(rad))
                            pygame.draw.line(screen, (255, 0, 0), p_screen, (end_x, end_y), 2)
                            # In dark training, if "k" is pressed, show target outlines.
                            if keys[pygame.K_k]:
                                for pos in current_target_positions:
                                    target_screen = to_screen_coords(pos)
                                    pygame.draw.circle(screen, WHITE, target_screen, int(TARGET_RADIUS * SCALE), 2)
                        else:
                            font = pygame.font.SysFont("Arial", 20)
                            instr = font.render("Exploration (Dark Training): Use arrow keys. Press Enter to annotate.", True, WHITE)
                            screen.blit(instr, (20, 20))
                else:
                    if keys[pygame.K_k]:
                        draw_debug_items(player_pos, player_angle, current_target_positions)
                    else:
                        font = pygame.font.SysFont("Arial", 20)
                        instr = font.render("Exploration (Dark): Use arrow keys. Press Enter to annotate.", True, WHITE)
                        screen.blit(instr, (20, 20))
            if move_key_pressed is not None and move_start_pos is not None:
                moved_distance = math.hypot(player_pos[0] - move_start_pos[0], player_pos[1] - move_start_pos[1])
                draw_thermometer(moved_distance)
            if rotate_key_pressed is not None and rotate_start_angle is not None:
                angle_diff = player_angle - rotate_start_angle
                draw_clock(angle_diff)

        elif phase == "annotation":
            # Annotation phase now uses the same movement as exploration.
            # We control the annotation marker with its own angle.
            keys = pygame.key.get_pressed()
            # Rotate annotation marker.
            if keys[pygame.K_LEFT]:
                annotation_marker_angle -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT]:
                annotation_marker_angle += ROTATE_SPEED * dt
            # Move annotation marker forward/backward relative to its angle.
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
            marker_screen = to_screen_coords(annotation_marker_pos)
            pygame.draw.circle(screen, (0, 0, 255), marker_screen, 5)
            # Draw a line to indicate the marker's orientation.
            rad = math.radians(annotation_marker_angle)
            line_length = 20
            end_x = marker_screen[0] + int(line_length * math.sin(rad))
            end_y = marker_screen[1] - int(line_length * math.cos(rad))
            pygame.draw.line(screen, (0, 0, 255), marker_screen, (end_x, end_y), 2)
            font = pygame.font.SysFont("Arial", 20)
            instr = font.render("Annotation: Use arrow keys to move and rotate. Press Enter when done.", True, WHITE)
            screen.blit(instr, (20, 20))

        elif phase == "feedback":
            draw_arena()
            if current_target_positions:
                target_screen = to_screen_coords(current_target_positions[0])
                pygame.draw.circle(screen, (255, 255, 0), target_screen, int(TARGET_RADIUS * SCALE), 0)
            marker_screen = to_screen_coords(annotation_marker_pos)
            pygame.draw.circle(screen, (0, 0, 255), marker_screen, 5)
            font = pygame.font.SysFont("Arial", 20)
            instr = font.render("Feedback: Real target shown under your selection. Press Enter to finish trial.", True, WHITE)
            screen.blit(instr, (20, 20))
        
        pygame.display.flip()
    # After trial, compute discrete log values.
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
# Functions to save logs to CSV
# ---------------------------
def save_discrete_log(logs, filename):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["trial_info", "trial_type", "exploration_time", "annotation_time", "encountered_goal", "annotation", "error_distance"]
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
# Main Experiment Loop with Logging
# ---------------------------
all_discrete_logs = []
all_continuous_logs = []  # Each row will have trial_info added.
training_trial = 1
dark_training_trial = 1
test_trial = 1

def run_experiment():
    global all_discrete_logs, all_continuous_logs, training_trial, dark_training_trial, test_trial
    print("Starting Training Block")
    for session in range(1, TRAINING_SESSIONS + 1):
        trial_info = f"training {training_trial}"
        print(f"Training Session {session} ({trial_info})")
        training_mode = True
        training_target_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)
        print(f"Using training target sound: {os.path.basename(TARGET_SOUND_PATH)}")
        discrete_log, continuous_log = run_trial(training_mode, training_target_sound, trial_info)
        discrete_log["trial_info"] = trial_info
        for row in continuous_log:
            row["trial_info"] = trial_info
        all_discrete_logs.append(discrete_log)
        all_continuous_logs.extend(continuous_log)
        training_trial += 1
        save_discrete_log(all_discrete_logs, discrete_filename)
        save_continuous_log(all_continuous_logs, continuous_filename)
        print("Training session complete. Press Enter to continue to next session.")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
            clock.tick(15)
    
    print("Starting Dark Training Block")
    for d in range(1, DARK_TRAINING_TRIALS + 1):
        trial_info = f"dark_training {dark_training_trial}"
        print(f"Dark Training Trial {d} ({trial_info})")
        dark_training_mode = False
        # In dark training, display_on_border is True.
        discrete_log, continuous_log = run_trial(dark_training_mode, target_sound_constant, trial_info, display_on_border=True)
        discrete_log["trial_info"] = trial_info
        for row in continuous_log:
            row["trial_info"] = trial_info
        all_discrete_logs.append(discrete_log)
        all_continuous_logs.extend(continuous_log)
        dark_training_trial += 1
        save_discrete_log(all_discrete_logs, discrete_filename)
        save_continuous_log(all_continuous_logs, continuous_filename)
        print("Dark training trial complete. Press Enter to continue to next trial.")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
            clock.tick(15)
    
    print("Starting Test Block")
    for t in range(1, TEST_TRIALS + 1):
        trial_info = f"test {test_trial}"
        print(f"Test Trial {t} ({trial_info})")
        test_mode = False
        discrete_log, continuous_log = run_trial(test_mode, None, trial_info, display_on_border=False)
        discrete_log["trial_info"] = trial_info
        for row in continuous_log:
            row["trial_info"] = trial_info
        all_discrete_logs.append(discrete_log)
        all_continuous_logs.extend(continuous_log)
        test_trial += 1
        save_discrete_log(all_discrete_logs, discrete_filename)
        save_continuous_log(all_continuous_logs, continuous_filename)
        print("Test trial complete. Press Enter to continue to next trial.")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
            clock.tick(15)
    print("Experiment complete. Press Escape to exit.")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False
        clock.tick(15)

run_experiment()
pygame.quit()
sys.exit()
