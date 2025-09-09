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
TARGET_PLACEMENT_DELAY_RANGE = (8, 15)  # seconds before target can be placed

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
BACKGROUND_COLOR = (3, 3, 1)        # Background: near-black
AVATAR_COLOR = (255, 67, 101)       # Avatar: Folly
BORDER_COLOR = (255, 255, 243)      # Arena border: Ivory
TARGET_COLOR = (0, 217, 192)        # Targets and thermometer: Turquoise
CLOCK_COLOR = (183, 173, 153)       # Clock rotation, Annotation and Feedback avatar: Khaki
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
                elif event.key == pygame.K_RETURN:
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
    """Draw a horizontal bar at the top-left showing distance moved."""
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
    """Draw the arena border as a circle centered on the screen."""
    pygame.draw.circle(screen, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)


def draw_player_avatar(pos, angle, color=AVATAR_COLOR):
    """Draw an elongated triangle representing the player."""
    p_screen = to_screen_coords(pos)
    tip_length = 30
    base_length = 20
    half_width = 17

    rad = math.radians(angle)
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


def draw_grid():
    """Overlay a grid showing visited-cell boundaries."""
    step = GRID_SIZE * SCALE
    cell_range = int(ARENA_RADIUS / GRID_SIZE)
    for i in range(-cell_range, cell_range + 1):
        x = CENTER_SCREEN[0] + int(i * step)
        pygame.draw.line(screen, DEBUG_COLOR, (x, 0), (x, WIN_HEIGHT), 1)
    for j in range(-cell_range, cell_range + 1):
        y = CENTER_SCREEN[1] - int(j * step)
        pygame.draw.line(screen, DEBUG_COLOR, (0, y), (WIN_WIDTH, y), 1)

# ---------------------------
# Trial function with logging (Experiment)
# ---------------------------

def run_trial(is_training, target_sound, trial_info):
    global beep_channel
    if target_sound is None:
        target_sound = target_sound_constant

    # Sample a new random placement delay this trial
    placement_delay = random.uniform(*TARGET_PLACEMENT_DELAY_RANGE)
    movement_to_enter_time = None

    phase = "exploration"
    player_pos = [0.0, 0.0]
    player_angle = 0.0
    has_moved_forward = False
    has_rotated = False
    target_placed = False
    target_position = None
    visited_cells = set()
    movement_start_time = None
    continuous_log = []
    encountered_goal = None

    exploration_start_time = time.time()
    annotation_start_time = None
    annotation_marker_pos = [0.0, 0.0]
    annotation_marker_angle = 0.0
    trial_done = False

    while not trial_done:
        dt = clock.tick(60) / 1000.0
        current_time = time.time() - exploration_start_time

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
                        if movement_start_time:
                            movement_to_enter_time = time.time() - movement_start_time
                        phase = "annotation"
                        annotation_start_time = time.time()
                    elif phase == "annotation":
                        phase = "feedback"
                    elif phase == "feedback":
                        trial_done = True

        screen.fill(BACKGROUND_COLOR)

        if phase == "exploration":
            keys = pygame.key.get_pressed()
            moving = any(keys[k] for k in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT))

            # Start movement timer
            if moving and movement_start_time is None:
                movement_start_time = time.time()

            # Track movement & rotation
            if keys[pygame.K_UP]: has_moved_forward = True
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]: has_rotated = True

            # Update position
            if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                dir_mult = 1 if keys[pygame.K_UP] else -1
                rad = math.radians(player_angle)
                dx = dir_mult * MOVE_SPEED * dt * math.sin(rad)
                dy = dir_mult * MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[:] = [new_x, new_y]
            if keys[pygame.K_LEFT]: player_angle -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT]: player_angle += ROTATE_SPEED * dt

            # Border collision beep
            if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                if beep_sound and (beep_channel is None or not beep_channel.get_busy()):
                    beep_channel = beep_sound.play(loops=-1)
            else:
                if beep_channel: beep_channel.stop(); beep_channel = None

            # Target placement logic
            if not target_placed and movement_start_time:
                elapsed_move = time.time() - movement_start_time
                if elapsed_move >= placement_delay and has_moved_forward and has_rotated and moving:
                    if math.hypot(player_pos[0], player_pos[1]) <= (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD):
                        if not is_position_visited(player_pos, visited_cells):
                            target_position = tuple(player_pos)
                            target_placed = True
                            if target_sound: target_sound.play()

            # Mark visited
            add_visited_position(player_pos, visited_cells)

            # Draw
            draw_arena()
            draw_player_avatar(player_pos, player_angle)

            # K-key reveal
            if keys[pygame.K_k]:
                draw_grid()
                if target_placed:
                    tp = to_screen_coords(target_position)
                    pygame.draw.circle(screen, TARGET_COLOR, tp, int(TARGET_RADIUS * SCALE))

            # Continuous logging
            continuous_log.append({
                "trial_info": trial_info,
                "phase": "exploration",
                "time": current_time,
                "x": player_pos[0],
                "y": player_pos[1]
            })

        elif phase == "annotation":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: annotation_marker_angle -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT]: annotation_marker_angle += ROTATE_SPEED * dt
            if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                dir_mult = 1 if keys[pygame.K_UP] else -1
                rad = math.radians(annotation_marker_angle)
                dx = dir_mult * MOVE_SPEED * dt * math.sin(rad)
                dy = dir_mult * MOVE_SPEED * dt * math.cos(rad)
                new_x = annotation_marker_pos[0] + dx
                new_y = annotation_marker_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    annotation_marker_pos[:] = [new_x, new_y]
            draw_arena()
            font = pygame.font.SysFont("Arial", 20)
            text = font.render("Navigate to the target location and press Enter", True, WHITE)
            screen.blit(text, (20, 20))
            draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
            continuous_log.append({
                "trial_info": trial_info,
                "phase": "annotation",
                "time": time.time() - exploration_start_time,
                "x": annotation_marker_pos[0],
                "y": annotation_marker_pos[1]
            })

        else:  # feedback
            draw_arena()
            if target_placed:
                tp = to_screen_coords(target_position)
                pygame.draw.circle(screen, TARGET_COLOR, tp, int(TARGET_RADIUS * SCALE))
            draw_player_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)

        # Trial counter
        if trial_info.startswith("training"): total = TRAINING_SESSIONS
        elif trial_info.startswith("dark_training"): total = DARK_TRAINING_TRIALS
        elif trial_info.startswith("test"): total = TEST_TRIALS
        else: total = "?"
        current = trial_info.split()[1]
        cnt = f"{current}/{total}"
        font = pygame.font.SysFont("Arial", 24)
        surf = font.render(cnt, True, WHITE)
        rect = surf.get_rect(bottomright=(WIN_WIDTH-20, WIN_HEIGHT-20))
        screen.blit(surf, rect)

        pygame.display.flip()

    # Build discrete log
    annotation_time = time.time() - annotation_start_time if annotation_start_time else None
    error = distance(encountered_goal, annotation_marker_pos) if encountered_goal else None
    discrete_log = {
        "trial_info": trial_info,
        "trial_type": "training" if is_training else "test",
        "placement_delay": placement_delay,
        "movement_to_enter_time": movement_to_enter_time,
        "annotation_time": annotation_time,
        "encountered_goal": encountered_goal,
        "annotation": annotation_marker_pos,
        "error_distance": error
    }
    return discrete_log, continuous_log

# ---------------------------
# Logging functions
# ---------------------------

def save_discrete_log(logs, filename):
    with open(filename, "w", newline="") as f:
        fieldnames = [
            "trial_info", "trial_type", "placement_delay",
            "movement_to_enter_time", "annotation_time",
            "encountered_goal", "annotation", "error_distance"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            row = log.copy()
            row["encountered_goal"] = json.dumps(row["encountered_goal"])
            row["annotation"] = json.dumps(row["annotation"])
            writer.writerow(row)


def save_continuous_log(logs, filename):
    with open(filename, "w", newline="") as f:
        fieldnames = ["trial_info", "phase", "time", "x", "y"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in logs:
            writer.writerow(r)

# ---------------------------
# Practice Game (Pre-Experiment)
# ---------------------------
def run_practice_game():
    WIDTH, HEIGHT = WIN_WIDTH, WIN_HEIGHT
    center = (WIDTH//2, HEIGHT//2)
    radius_px = int(ARENA_RADIUS * SCALE)
    avatar_pos = [center[0], center[1]]
    avatar_angle = 0
    speed = 3
    rot_speed = 3
    score = 0
    font = pygame.font.SysFont(None, 36)
    beep_ch = None

    def rand_pos():
        ang = random.uniform(0, 2*math.pi)
        r = radius_px * math.sqrt(random.uniform(0,1))
        return (center[0]+r*math.cos(ang), center[1]+r*math.sin(ang))

    goal = rand_pos()
    while score < 5:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: return
        keys = pygame.key.get_pressed()
        dx = (math.cos(math.radians(avatar_angle))*speed if keys[pygame.K_UP] else
              -math.cos(math.radians(avatar_angle))*speed if keys[pygame.K_DOWN] else 0)
        dy = (math.sin(math.radians(avatar_angle))*speed if keys[pygame.K_UP] else
              -math.sin(math.radians(avatar_angle))*speed if keys[pygame.K_DOWN] else 0)
        new = [avatar_pos[0]+dx, avatar_pos[1]+dy]
        if math.hypot(new[0]-center[0], new[1]-center[1]) <= radius_px: avatar_pos[:] = new
        if keys[pygame.K_LEFT]: avatar_angle = (avatar_angle-rot_speed)%360
        if keys[pygame.K_RIGHT]: avatar_angle = (avatar_angle+rot_speed)%360
        if math.hypot(avatar_pos[0]-goal[0], avatar_pos[1]-goal[1]) < 15:
            score+=1; goal=rand_pos();
            if target_sound_constant: target_sound_constant.play()
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.circle(screen, BORDER_COLOR, center, radius_px, 2)
        pygame.draw.circle(screen, TARGET_COLOR, (int(goal[0]), int(goal[1])), 10)
        draw_player_avatar([ (avatar_pos[0]-center[0])/SCALE, (center[1]-avatar_pos[1])/SCALE ], avatar_angle)
        scr = font.render(f"Score: {score}", True, CLOCK_COLOR)
        screen.blit(scr, (10,10))
        pygame.display.flip()

# ---------------------------
# Main Experiment Loop
# ---------------------------
def run_experiment():
    show_image(os.path.join(INSTRUCTIONS_DIR, "1.png"))
    show_image(os.path.join(INSTRUCTIONS_DIR, "2.png"))
    run_practice_game()
    show_image(os.path.join(INSTRUCTIONS_DIR, "3.png"))
    training_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)
    all_discrete, all_cont = [], []
    for i in range(1, TRAINING_SESSIONS+1):
        ti = f"training {i}"
        d, c = run_trial(True, training_sound, ti)
        all_discrete.append(d); all_cont.extend(c)
    show_image(os.path.join(INSTRUCTIONS_DIR, "4.png"))
    for i in range(1, DARK_TRAINING_TRIALS+1):
        ti = f"dark_training {i}"
        d, c = run_trial(True, training_sound, ti)
        all_discrete.append(d); all_cont.extend(c)
    show_image(os.path.join(INSTRUCTIONS_DIR, "5.png"))
    for i in range(1, TEST_TRIALS+1):
        ti = f"test {i}"
        d, c = run_trial(False, training_sound, ti)
        all_discrete.append(d); all_cont.extend(c)
    show_image(os.path.join(INSTRUCTIONS_DIR, "6.png"))
    save_discrete_log(all_discrete, discrete_filename)
    save_continuous_log(all_cont, continuous_filename)
    print("Experiment complete. Press Escape to exit.")
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                waiting = False
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_experiment()
