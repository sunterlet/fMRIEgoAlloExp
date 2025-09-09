import pygame
import math
import sys
import time
import os
import random

# ---------------------------
# Configuration parameters
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0   # 1.65 m
BORDER_THRESHOLD = 0.2              # threshold from border in meters

# Target parameters
TARGET_RADIUS = 0.1                 # reduced target radius in meters
DEFAULT_TARGET_COUNT = 3            # number of targets per trial

# Movement settings
MOVE_SPEED = 1.0                    # meters per second
ROTATE_SPEED = 90.0                 # degrees per second

# Scale factor: pixels per meter
SCALE = 200                         # 1 meter = 200 pixels

# Window size (increased to ensure the full arena is visible)
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HUD_COLOR = (0, 255, 0)
DEBUG_COLOR = (50, 50, 255)   # Used for debug visuals

# Directory for target sounds (wav files)
TARGET_SOUND_DIR = "/Volumes/ramot/sunt/Navigation/SoundNavigation/Sounds/Dor/Underwater/"
# Beep sound file (do not use as target)
BEEP_SOUND_PATH = os.path.join(TARGET_SOUND_DIR, "beep.wav")

# ---------------------------
# Experiment parameters
# ---------------------------
TRAINING_SESSIONS = 3
TEST_TRIALS = 5

# ---------------------------
# Initialize Pygame and Mixer
# ---------------------------
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("MRI Navigation Experiment")
clock = pygame.time.Clock()

# Load beep sound
try:
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
except Exception as e:
    print("Error loading beep sound:", e)
    beep_sound = None
beep_channel = None  # Global variable for looping beep sound

# Helper: get list of available target sounds (exclude beep.wav)
def get_target_sound_files(directory):
    try:
        files = os.listdir(directory)
        target_files = [f for f in files if f.lower().endswith('.wav') and "beep" not in f.lower()]
        return [os.path.join(directory, f) for f in target_files]
    except Exception as e:
        print("Error listing target sound files:", e)
        return []

target_sound_files = get_target_sound_files(TARGET_SOUND_DIR)
if not target_sound_files:
    print("No target sound files found. Exiting.")
    pygame.quit()
    sys.exit()

# ---------------------------
# Helper: generate random target positions
# ---------------------------
def generate_random_targets(n):
    """
    Generate n random target positions inside the arena such that:
      1. Each target's center lies within a circle of radius (ARENA_RADIUS - TARGET_RADIUS).
      2. The distance between any two target centers is at least 2 * TARGET_RADIUS.
      3. The target's center is at least TARGET_RADIUS away from the arena center.
    """
    targets = []
    valid_radius = ARENA_RADIUS - TARGET_RADIUS  # Maximum allowed radius for target centers
    attempts = 0
    max_attempts = 1000
    while len(targets) < n and attempts < max_attempts:
        angle = random.uniform(0, 2 * math.pi)
        r = valid_radius * math.sqrt(random.uniform(0, 1))
        candidate = (r * math.cos(angle), r * math.sin(angle))
        # Ensure the candidate does not overlap the arena center.
        if math.hypot(candidate[0], candidate[1]) < TARGET_RADIUS:
            attempts += 1
            continue
        overlap = False
        for t in targets:
            if math.hypot(candidate[0] - t[0], candidate[1] - t[1]) < 2 * TARGET_RADIUS:
                overlap = True
                break
        if not overlap:
            targets.append(candidate)
        attempts += 1
    if len(targets) < n:
        print("Warning: Could not generate all targets without overlap.")
    return targets

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
    accumulation_factor = 200  # pixels per meter; saturates at 2 m = 400 pixels
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
# Trial (session) function
# ---------------------------
def run_trial(is_training, target_sound):
    global beep_channel, BLACK
    if target_sound is None:
        target_sound = pygame.mixer.Sound(random.choice(target_sound_files))
    phase = "exploration"  # phases: exploration, annotation, feedback
    # Exploration phase state:
    player_pos = [0.0, 0.0]
    player_angle = 0.0
    move_key_pressed = None
    move_start_pos = None
    rotate_key_pressed = None
    rotate_start_angle = None
    target_was_inside = False
    current_target_positions = generate_random_targets(DEFAULT_TARGET_COUNT)
    annotation_marker_pos = [0.0, 0.0]
    
    trial_done = False
    while not trial_done:
        dt = clock.tick(60) / 1000.0
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
                        phase = "annotation"
                        annotation_marker_pos = [0.0, 0.0]
                        if beep_channel is not None:
                            beep_channel.stop()
                            beep_channel = None
                    elif phase == "annotation":
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
            encountered_target = None
            for pos in current_target_positions:
                if distance(player_pos, pos) <= TARGET_RADIUS:
                    is_inside_target = True
                    encountered_target = pos
                    break
            if not target_was_inside and is_inside_target:
                if target_sound is not None:
                    target_sound.play()
                print("Target reached at:", encountered_target)
                current_target_positions = [encountered_target]
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
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                new_y = annotation_marker_pos[1] + MOVE_SPEED * dt
                if math.hypot(annotation_marker_pos[0], new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[1] = new_y
            if keys[pygame.K_DOWN]:
                new_y = annotation_marker_pos[1] - MOVE_SPEED * dt
                if math.hypot(annotation_marker_pos[0], new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[1] = new_y
            if keys[pygame.K_LEFT]:
                new_x = annotation_marker_pos[0] - MOVE_SPEED * dt
                if math.hypot(new_x, annotation_marker_pos[1]) <= ARENA_RADIUS:
                    annotation_marker_pos[0] = new_x
            if keys[pygame.K_RIGHT]:
                new_x = annotation_marker_pos[0] + MOVE_SPEED * dt
                if math.hypot(new_x, annotation_marker_pos[1]) <= ARENA_RADIUS:
                    annotation_marker_pos[0] = new_x
            draw_arena()
            marker_screen = to_screen_coords(annotation_marker_pos)
            pygame.draw.circle(screen, (0, 0, 255), marker_screen, 5)
            font = pygame.font.SysFont("Arial", 20)
            instr = font.render("Annotation: Move marker with arrow keys. Press Enter when done.", True, WHITE)
            screen.blit(instr, (20, 20))

        elif phase == "feedback":
            draw_arena()
            # Draw the full target area as a filled circle.
            if current_target_positions:
                target_screen = to_screen_coords(current_target_positions[0])
                pygame.draw.circle(screen, (255, 255, 0), target_screen, int(TARGET_RADIUS * SCALE), 0)
            # Then draw the player's annotation marker on top.
            marker_screen = to_screen_coords(annotation_marker_pos)
            pygame.draw.circle(screen, (0, 0, 255), marker_screen, 5)
            font = pygame.font.SysFont("Arial", 20)
            instr = font.render("Feedback: Real target shown under your selection. Press Enter to finish trial.", True, WHITE)
            screen.blit(instr, (20, 20))
        
        pygame.display.flip()
    return annotation_marker_pos

def run_experiment():
    print("Starting Training Block")
    for session in range(1, TRAINING_SESSIONS + 1):
        print(f"Training Session {session} of {TRAINING_SESSIONS}")
        training_mode = True
        tsound_path = random.choice(target_sound_files)
        try:
            training_target_sound = pygame.mixer.Sound(tsound_path)
        except Exception as e:
            print("Error loading training target sound:", e)
            training_target_sound = None
        print(f"Using training target sound: {os.path.basename(tsound_path)}")
        run_trial(training_mode, training_target_sound)
        print("Training session complete. Press Enter to continue to next session.")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False
            clock.tick(15)
    
    print("Starting Test Block")
    for trial in range(1, TEST_TRIALS + 1):
        print(f"Test Trial {trial} of {TEST_TRIALS}")
        test_mode = False
        run_trial(test_mode, None)
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
