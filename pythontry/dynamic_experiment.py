import pygame
import math
import sys
import time
import os
import random
import csv

# ---------------------------
# Configuration parameters (Experiment)
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0  # 1.65 m
BORDER_THRESHOLD = 0.1              # threshold from border in meters

# Target parameters
TARGET_RADIUS = 0.1                 # target radius in meters

# Movement settings
MOVE_SPEED = 1.0                    # meters per second
ROTATE_SPEED = 90.0                 # degrees per second

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
AVATAR_COLOR    = (255, 67, 101)    # Avatar: Folly
BORDER_COLOR    = (255, 255, 243)   # Border: Ivory
TARGET_COLOR    = (0, 217, 192)     # Target & thermometer: Turquoise
CLOCK_COLOR     = (183, 173, 153)   # Score & feedback avatar: Khaki
WHITE           = (255, 255, 255)
DEBUG_COLOR     = (50, 50, 255)

# ---------------------------
# Sounds & Paths
# ---------------------------
SOUNDS_DIR            = "/Volumes/ramot/sunt/Navigation/fMRI/sounds/"
TARGET_SOUND_PATH     = os.path.join(SOUNDS_DIR, "target.wav")
BEEP_SOUND_PATH       = os.path.join(SOUNDS_DIR, "beep.wav")
INSTRUCTIONS_DIR      = "/Volumes/ramot/sunt/Navigation/fMRI/pythontry/Instructions/"

# ---------------------------
# Experiment block counts
# ---------------------------
TRAINING_SESSIONS     = 3
DARK_TRAINING_TRIALS  = 2
TEST_TRIALS           = 5

# ---------------------------
# Initialize Pygame & Mixer
# ---------------------------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Exploration Experiment")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# ---------------------------
# Prompt for player initials and set filenames
# ---------------------------
player_initials = input("Enter player initials: ").strip()
results_dir = "/Volumes/ramot/sunt/Navigation/fMRI/pythontry/results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
discrete_filename   = os.path.join(results_dir, f"{player_initials}_discrete_log.csv")
continuous_filename = os.path.join(results_dir, f"{player_initials}_continuous_log.csv")

# ---------------------------
# Coordinate & Drawing Utils
# ---------------------------
def to_screen_coords(pos):
    x, y = pos
    screen_x = CENTER_SCREEN[0] + int(x * SCALE)
    screen_y = CENTER_SCREEN[1] - int(y * SCALE)
    return (screen_x, screen_y)

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_thermometer(distance_moved):
    bar_x, bar_y = 50, 30
    max_bar_width = int(ARENA_DIAMETER * SCALE)
    w = min(int(distance_moved * SCALE), max_bar_width)
    pygame.draw.rect(screen, TARGET_COLOR, (bar_x, bar_y, w, 10))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, max_bar_width, 10), 2)

# ---------------------------
# Load & Display Instructions
# ---------------------------
def show_image(image_path):
    try:
        img = pygame.image.load(image_path)
    except pygame.error as e:
        print(f"Error loading {image_path}: {e}")
        return
    screen.blit(img, (0, 0))
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
# Practice Game
# ---------------------------
def run_practice_game():
    """Run the practice game where the player must reach a score of 15."""
    WIDTH, HEIGHT = WIN_WIDTH, WIN_HEIGHT
    arena_center = (WIDTH // 2, HEIGHT // 2)
    arena_radius = int(ARENA_RADIUS * SCALE)

    avatar_pos = [arena_center[0], arena_center[1]]
    avatar_angle = 0
    avatar_speed = 3             # pixels per frame
    rotation_speed = 3           # degrees per frame
    avatar_size = 15             # pixels
    score = 0

    # Initialize three random targets
    target_positions = []
    for _ in range(3):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, ARENA_RADIUS - BORDER_THRESHOLD)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        target_positions.append((x, y))

    running = True
    while running:
        # Frame cap at 60 FPS
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        # Rotation
        if keys[pygame.K_LEFT]:
            avatar_angle -= rotation_speed
        if keys[pygame.K_RIGHT]:
            avatar_angle += rotation_speed

        # Movement
        if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            dir_mult = 1 if keys[pygame.K_UP] else -1
            dx = dir_mult * avatar_speed * math.cos(math.radians(avatar_angle))
            dy = dir_mult * avatar_speed * math.sin(math.radians(avatar_angle))
            new_x = avatar_pos[0] + dx
            new_y = avatar_pos[1] + dy
            # Check arena boundary (in pixels)
            dist = math.hypot(new_x - arena_center[0], new_y - arena_center[1])
            if dist <= arena_radius - avatar_size:
                avatar_pos[0] = new_x
                avatar_pos[1] = new_y

        # Target capture
        for pos in list(target_positions):
            screen_pos = to_screen_coords(pos)
            if distance(screen_pos, avatar_pos) < avatar_size + TARGET_RADIUS * SCALE:
                pygame.mixer.Sound(TARGET_SOUND_PATH).play()
                score += 1
                target_positions.remove(pos)

        # Draw practice scene
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.circle(screen, BORDER_COLOR, arena_center, arena_radius, 4)
        # Draw avatar as triangle
        tip = (
            avatar_pos[0] + avatar_size * math.cos(math.radians(avatar_angle)),
            avatar_pos[1] + avatar_size * math.sin(math.radians(avatar_angle))
        )
        left = (
            avatar_pos[0] + avatar_size * math.cos(math.radians(avatar_angle + 140)),
            avatar_pos[1] + avatar_size * math.sin(math.radians(avatar_angle + 140))
        )
        right = (
            avatar_pos[0] + avatar_size * math.cos(math.radians(avatar_angle - 140)),
            avatar_pos[1] + avatar_size * math.sin(math.radians(avatar_angle - 140))
        )
        pygame.draw.polygon(screen, AVATAR_COLOR, [tip, left, right])

        # Draw targets
        for pos in target_positions:
            pygame.draw.circle(screen, TARGET_COLOR, to_screen_coords(pos), int(TARGET_RADIUS * SCALE))

        # Draw score
        score_surf = font.render(f"Score: {score}", True, CLOCK_COLOR)
        screen.blit(score_surf, (10, 10))

        pygame.display.flip()

        # End practice when score reaches 15
        if score >= 3:
            return

# ---------------------------
# Trial function with dynamic target drop
# ---------------------------
def run_practice_game():
    WIDTH, HEIGHT = WIN_WIDTH, WIN_HEIGHT
    arena_center = (WIDTH // 2, HEIGHT // 2)
    arena_radius = int(ARENA_RADIUS * SCALE)

    avatar_pos = [arena_center[0], arena_center[1]]
    avatar_angle = 0
    avatar_speed = 3
    rotation_speed = 3
    avatar_size = 15
    score = 0

    target_positions = []
    for _ in range(3):
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, ARENA_RADIUS - BORDER_THRESHOLD)
        x, y = r * math.cos(a), r * math.sin(a)
        target_positions.append((x, y))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            avatar_angle -= rotation_speed
        if keys[pygame.K_RIGHT]:
            avatar_angle += rotation_speed
        if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            dir_mult = 1 if keys[pygame.K_UP] else -1
            dx = dir_mult * avatar_speed * math.cos(math.radians(avatar_angle))
            dy = dir_mult * avatar_speed * math.sin(math.radians(avatar_angle))
            new_x = avatar_pos[0] + dx
            new_y = avatar_pos[1] + dy
            dist = math.hypot(new_x - arena_center[0], new_y - arena_center[1]) / SCALE
            if dist <= ARENA_RADIUS - BORDER_THRESHOLD:
                avatar_pos[0] = new_x
                avatar_pos[1] = new_y

        for pos in list(target_positions):
            if distance(to_screen_coords(pos), avatar_pos) < avatar_size + TARGET_RADIUS * SCALE:
                pygame.mixer.Sound(TARGET_SOUND_PATH).play()
                score += 1
                target_positions.remove(pos)

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.circle(screen, BORDER_COLOR, arena_center, arena_radius, 4)
        tip = (
            avatar_pos[0] + avatar_size * math.cos(math.radians(avatar_angle)),
            avatar_pos[1] + avatar_size * math.sin(math.radians(avatar_angle)),
        )
        left = (
            avatar_pos[0] + avatar_size * math.cos(math.radians(avatar_angle + 140)),
            avatar_pos[1] + avatar_size * math.sin(math.radians(avatar_angle + 140)),
        )
        right = (
            avatar_pos[0] + avatar_size * math.cos(math.radians(avatar_angle - 140)),
            avatar_pos[1] + avatar_size * math.sin(math.radians(avatar_angle - 140)),
        )
        pygame.draw.polygon(screen, AVATAR_COLOR, [tip, left, right])

        for pos in target_positions:
            pygame.draw.circle(screen, TARGET_COLOR, to_screen_coords(pos), int(TARGET_RADIUS * SCALE))

        scr = font.render(f"Score: {score}", True, CLOCK_COLOR)
        screen.blit(scr, (10, 10))

        pygame.display.flip()

        if score >= 15:
            return

# ---------------------------
# Trial function with dynamic target drop
# ---------------------------
def run_trial(is_training, target_sound, trial_info, display_on_border=False):
    current_target_positions = []
    target_dropped = False
    dropped_target_pos = None
    show_target_location = False

    has_moved_forward = False
    has_rotated = False
    movement_started = False
    movement_start_time = None
    spawn_delay = random.uniform(8.0, 15.0)

    player_pos = list(CENTER_SCREEN)
    player_angle = 0
    avatar_size = 10

    continuous_log = []

    trial_start_time = time.time()
    annotation_start_time = None
    phase = "exploration"

    while True:
        dt = clock.tick(60) / 1000.0
        current_trial_time = time.time() - trial_start_time

        keys = pygame.key.get_pressed()
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
                        annotation_start_time = time.time()
                    elif phase == "annotation":
                        phase = "feedback"
                    else:
                        return discrete_log, continuous_log
                if event.key == pygame.K_k and target_dropped:
                    show_target_location = True

        moving = keys[pygame.K_UP] or keys[pygame.K_DOWN]
        rotating = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
        if keys[pygame.K_UP]:
            has_moved_forward = True
        if rotating:
            has_rotated = True
        if moving and not movement_started:
            movement_started = True
            movement_start_time = current_trial_time

        if not is_training and not target_dropped:
            if movement_started and has_moved_forward and has_rotated and moving:
                elapsed = current_trial_time - movement_start_time
                if elapsed >= spawn_delay or elapsed >= 15.0:
                    ax = (player_pos[0] - CENTER_SCREEN[0]) / SCALE
                    ay = (CENTER_SCREEN[1] - player_pos[1]) / SCALE
                    current_target_positions.append((ax, ay))
                    dropped_target_pos = (ax, ay)
                    target_dropped = True

        # Movement & rotation
        if phase in ("exploration", "annotation"):
            if keys[pygame.K_LEFT]:
                player_angle -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT]:
                player_angle += ROTATE_SPEED * dt
            if moving:
                dir_mult = 1 if keys[pygame.K_UP] else -1
                dx = dir_mult * MOVE_SPEED * dt * math.cos(math.radians(player_angle)) * SCALE
                dy = dir_mult * MOVE_SPEED * dt * math.sin(math.radians(player_angle)) * SCALE
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                dist = math.hypot(new_x - CENTER_SCREEN[0], new_y - CENTER_SCREEN[1]) / SCALE
                if dist <= ARENA_RADIUS - BORDER_THRESHOLD:
                    player_pos[0] = new_x
                    player_pos[1] = new_y

        # Continuous logging
        if phase in ("exploration", "annotation"):
            entry = {
                "trial_info": trial_info,
                "phase": phase,
                "time": current_trial_time,
                "x": (player_pos[0] - CENTER_SCREEN[0]) / SCALE,
                "y": (CENTER_SCREEN[1] - player_pos[1]) / SCALE
            }
            continuous_log.append(entry)

        # Draw scene
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.circle(screen, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 4)
        tip = (
            player_pos[0] + avatar_size * math.cos(math.radians(player_angle)),
            player_pos[1] + avatar_size * math.sin(math.radians(player_angle))
        )
        left = (
            player_pos[0] + avatar_size * math.cos(math.radians(player_angle + 140)),
            player_pos[1] + avatar_size * math.sin(math.radians(player_angle + 140))
        )
        right = (
            player_pos[0] + avatar_size * math.cos(math.radians(player_angle - 140)),
            player_pos[1] + avatar_size * math.sin(math.radians(player_angle - 140))
        )
        pygame.draw.polygon(screen, AVATAR_COLOR, [tip, left, right])

        for pos in current_target_positions:
            pygame.draw.circle(screen, TARGET_COLOR, to_screen_coords(pos), int(TARGET_RADIUS * SCALE))

        if show_target_location and dropped_target_pos:
            pygame.draw.circle(screen, (255, 0, 0), to_screen_coords(dropped_target_pos), int(TARGET_RADIUS * SCALE) + 5, 3)

        pygame.display.flip()

    # Discrete logging
    exploration_time = (annotation_start_time - trial_start_time) if annotation_start_time else 0
    annotation_time = (time.time() - annotation_start_time) if annotation_start_time else 0
    fx, fy = None, None
    error_distance = None
    if dropped_target_pos:
        fx = (player_pos[0] - CENTER_SCREEN[0]) / SCALE
        fy = (CENTER_SCREEN[1] - player_pos[1]) / SCALE
        error_distance = math.hypot(fx - dropped_target_pos[0], fy - dropped_target_pos[1])

    discrete_log = {
        "trial_info": trial_info,
        "trial_type": "training" if is_training else "test",
        "exploration_time": exploration_time,
        "annotation_time": annotation_time,
        "encountered_goal": dropped_target_pos,
        "annotation": (fx, fy) if dropped_target_pos else None,
        "error_distance": error_distance
    }
    return discrete_log, continuous_log

# ---------------------------
# CSV Saving
# ---------------------------
def save_discrete_log(logs, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(logs[0].keys()))
        writer.writeheader()
        for row in logs:
            writer.writerow(row)

def save_continuous_log(logs, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(logs[0].keys()))
        writer.writeheader()
        for row in logs:
            writer.writerow(row)

# ---------------------------
# Full Experiment Flow
# ---------------------------
def run_experiment():
    all_discrete, all_continuous = [], []

    # 1. Welcome & Practice
    show_image(os.path.join(INSTRUCTIONS_DIR, "1.png"))
    show_image(os.path.join(INSTRUCTIONS_DIR, "2.png"))
    run_practice_game()

    # 2. Training
    show_image(os.path.join(INSTRUCTIONS_DIR, "3.png"))
    for t in range(1, TRAINING_SESSIONS + 1):
        info = f"training {t}"
        dlog, clog = run_trial(True, None, info)
        all_discrete.append(dlog)
        all_continuous.extend(clog)
        save_discrete_log(all_discrete, discrete_filename)
        save_continuous_log(all_continuous, continuous_filename)

    # 3. Dark Training
    show_image(os.path.join(INSTRUCTIONS_DIR, "4.png"))
    for d in range(1, DARK_TRAINING_TRIALS + 1):
        info = f"dark_training {d}"
        dlog, clog = run_trial(True, None, info, display_on_border=True)
        all_discrete.append(dlog)
        all_continuous.extend(clog)
        save_discrete_log(all_discrete, discrete_filename)
        save_continuous_log(all_continuous, continuous_filename)

    # 4. Test
    show_image(os.path.join(INSTRUCTIONS_DIR, "5.png"))
    for x in range(1, TEST_TRIALS + 1):
        info = f"test {x}"
        dlog, clot = run_trial(False, None, info)
        all_discrete.append(dlog)
        all_continuous.extend(clot)
        save_discrete_log(all_discrete, discrete_filename)
        save_continuous_log(all_continuous, continuous_filename)

    # 5. Final
    show_image(os.path.join(INSTRUCTIONS_DIR, "6.png"))
    print("Experiment complete. Press Escape to exit.")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False
        clock.tick(15)

if __name__ == "__main__":
    run_experiment()
    pygame.quit()
    sys.exit()
