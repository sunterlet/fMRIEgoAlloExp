import pygame
import math
import sys
import time
import os
import csv

# ---------------------------
# Configuration parameters (Experiment)
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0  # 1.65 m
BORDER_THRESHOLD = 0.1              # threshold from border in meters

# Window dimensions (pixels)
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# Scaling and grid
SCALE = 200                         # 1 meter = 200 pixels
CELL_SIZE = 0.2                     # meters per grid cell

# Avatar parameters
TIP_PIXELS = 30                     # pixels from center to tip
AVATAR_COLOR = (255, 67, 101)       # Folly
ROTATE_SPEED = 90                   # degrees/sec
MOVE_SPEED = 1.0                    # m/s

# Target parameters
TARGET_COLOR = (0, 217, 192)        # Turquoise
TARGET_RADIUS = 0.1                 # meters

# Colors
BACKGROUND_COLOR = (3, 3, 1)        # near-black
WHITE = (255, 255, 255)
BORDER_COLOR = (255, 255, 243)      # Ivory
CLOCK_COLOR = (183, 173, 153)       # Khaki

# Sound files
default_sound_dir = "sounds"
TARGET_SOUND_PATH = os.path.join(default_sound_dir, "target.wav")
BEEP_SOUND_PATH = os.path.join(default_sound_dir, "beep.wav")

pygame.init()
font = pygame.font.SysFont("Arial", 20)

# Utility

def to_screen_coords(pos):
    x, y = pos
    return (CENTER_SCREEN[0] + int(x * SCALE), CENTER_SCREEN[1] - int(y * SCALE))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# Drawing

def draw_arena():
    pygame.draw.circle(screen, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)


def draw_thermometer(distance_moved):
    bar_x, bar_y = 50, 30
    max_bar_width = int(ARENA_DIAMETER * SCALE)
    bar_height = 20
    bar_width = min(max_bar_width, int(distance_moved * SCALE))
    label = font.render("Movement", True, WHITE)
    screen.blit(label, (bar_x, bar_y - 25))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    pygame.draw.rect(screen, TARGET_COLOR, (bar_x, bar_y, bar_width, bar_height))


def draw_clock(angle_diff):
    dial_center = (WIN_WIDTH - 100, 75)
    dial_radius = 50
    label = font.render("Rotation", True, WHITE)
    lbl_rect = label.get_rect(center=(dial_center[0], dial_center[1] - dial_radius - 15))
    screen.blit(label, lbl_rect)
    if angle_diff is None:
        return
    pygame.draw.circle(screen, WHITE, dial_center, dial_radius, 2)
    rad = math.radians(angle_diff)
    end_x = dial_center[0] + dial_radius * math.sin(rad)
    end_y = dial_center[1] - dial_radius * math.cos(rad)
    pygame.draw.line(screen, CLOCK_COLOR, dial_center, (int(end_x), int(end_y)), 4)
    angle_lbl = font.render(f"{angle_diff:.1f}°", True, WHITE)
    screen.blit(angle_lbl, (dial_center[0] - 20, dial_center[1] - 10))


def draw_player_avatar(pos, angle):
    """Draw an elongated triangle representing the player at pos with heading angle."""
    p = to_screen_coords(pos)
    # Triangle parameters
    tip_length = TIP_PIXELS
    base_length = 20
    half_width = 17
    rad = math.radians(angle)
    # Compute triangle points
    tip = (
        p[0] + int(tip_length * math.sin(rad)),
        p[1] - int(tip_length * math.cos(rad))
    )
    base_center = (
        p[0] - int(base_length * math.sin(rad)),
        p[1] + int(base_length * math.cos(rad))
    )
    left = (
        base_center[0] + int(half_width * math.sin(rad + math.pi/2)),
        base_center[1] - int(half_width * math.cos(rad + math.pi/2))
    )
    right = (
        base_center[0] + int(half_width * math.sin(rad - math.pi/2)),
        base_center[1] - int(half_width * math.cos(rad - math.pi/2))
    )
    pygame.draw.polygon(screen, AVATAR_COLOR, [tip, left, right])

# Logging

def save_discrete_log(logs, filename):
    keys = ["trial_info","trial_type","exploration_time","annotation_time","encountered_goal","annotation","error_distance"]
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(logs)


def save_continuous_log(log, filename):
    keys = ["trial_info","phase","time","x","y"]
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(log)

# Trial

def run_trial(is_training, trial_info, target_sound, beep_sound):
    # init state
    player_pos = [0.0, 0.0]
    player_angle = 0.0
    phase = "exploration"
    start_time = None
    moved_forward = False
    # flags
    rotated_flag = False
    target_was_inside = False
    visited = set()
    encountered_goal = None

    move_start_pos = None
    rotate_start_angle = None
    beep_channel = None

    expl_start = time.time()
    cont_log = []

    running = True
    while running:
        dt = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if phase == "exploration":
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        if start_time is None:
                            start_time = time.time()
                            move_start_pos = player_pos.copy()
                        moved_forward = True
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        if rotate_start_angle is None:
                            rotate_start_angle = player_angle
                        rotated_flag = True
                    if event.key == pygame.K_RETURN:
                        phase = "annotation"
                        annotation_start = time.time()
                        if beep_channel: beep_channel.stop()
                else:
                    if event.key == pygame.K_RETURN:
                        running = False
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    rotated_flag = False
                    rotate_start_angle = None

        keys = pygame.key.get_pressed()
                # movement & border handling
        rad = math.radians(player_angle)
        move_dx = 0.0
        move_dy = 0.0
        if keys[pygame.K_UP]:
            move_dx = MOVE_SPEED * dt * math.sin(rad)
            move_dy = MOVE_SPEED * dt * math.cos(rad)
        elif keys[pygame.K_DOWN]:
            move_dx = -MOVE_SPEED * dt * math.sin(rad)
            move_dy = -MOVE_SPEED * dt * math.cos(rad)
        if move_dx != 0 or move_dy != 0:
            new_x = player_pos[0] + move_dx
            new_y = player_pos[1] + move_dy
            # only move if inside border
            if distance((new_x, new_y), (0, 0)) <= ARENA_RADIUS - BORDER_THRESHOLD:
                player_pos[0], player_pos[1] = new_x, new_y
            else:
                # play beep and do not move
                if not beep_channel or not beep_channel.get_busy():
                    beep_channel = beep_sound.play(loops=-1)
        else:
            # stop beep when not pressing movement
            if beep_channel and beep_channel.get_busy():
                beep_channel.stop()

        # rotation
        if keys[pygame.K_LEFT]:
            player_angle -= ROTATE_SPEED * dt
        if keys[pygame.K_RIGHT]:
            player_angle += ROTATE_SPEED * dt
        if keys[pygame.K_LEFT]: player_angle -= ROTATE_SPEED*dt
        if keys[pygame.K_RIGHT]: player_angle += ROTATE_SPEED*dt

        # border check & beep
        if distance(player_pos, [0,0]) > ARENA_RADIUS - BORDER_THRESHOLD:
            angle_off = math.atan2(player_pos[1], player_pos[0])
            player_pos[0] = (ARENA_RADIUS - BORDER_THRESHOLD)*math.cos(angle_off)
            player_pos[1] = (ARENA_RADIUS - BORDER_THRESHOLD)*math.sin(angle_off)
            if not beep_channel or not beep_channel.get_busy():
                beep_channel = beep_sound.play(loops=-1)
        else:
            if beep_channel and beep_channel.get_busy(): beep_channel.stop()

        # continuous logging
        t_rel = time.time() - (expl_start if phase=="exploration" else annotation_start)
        cont_log.append({"trial_info":trial_info, "phase":phase, "time":t_rel,
                         "x":player_pos[0], "y":player_pos[1]})

        # dynamic target drop
        if phase=="exploration" and not encountered_goal and start_time:
            elapsed = time.time() - start_time
            cell = (math.floor(player_pos[0]/CELL_SIZE), math.floor(player_pos[1]/CELL_SIZE))
            if elapsed>=10 and moved_forward and rotated_flag and cell not in visited and (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                rad = math.radians(player_angle)
                off = TIP_PIXELS/SCALE
                gx = player_pos[0] + off*math.sin(rad)
                gy = player_pos[1] + off*math.cos(rad)
                encountered_goal = [gx, gy]
                target_sound.play()
            visited.add(cell)

        # play sound when encountering target
        if encountered_goal and not target_was_inside:
            if distance(player_pos, encountered_goal) <= TARGET_RADIUS:
                target_sound.play()
                target_was_inside = True

        # render
        screen.fill(BACKGROUND_COLOR)
        draw_arena()
        draw_player_avatar(player_pos, player_angle)
        if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            distm = distance(player_pos, move_start_pos) if move_start_pos else 0
            draw_thermometer(distm)
        if rotated_flag and rotate_start_angle is not None:
            draw_clock(player_angle - rotate_start_angle)
        # show target on K
        if keys[pygame.K_k] and encountered_goal:
            px = to_screen_coords(encountered_goal)
            pygame.draw.circle(screen, TARGET_COLOR, px, int(TARGET_RADIUS*SCALE))
        pygame.display.flip()

    # discrete log
    exploration_time = annotation_start - expl_start
    annotation_time = time.time() - annotation_start
    err = None
    if encountered_goal: err = 0
    disc = {"trial_info":trial_info, "trial_type":"training" if is_training else "test",
            "exploration_time":exploration_time, "annotation_time":annotation_time,
            "encountered_goal":encountered_goal, "annotation":None, "error_distance":err}
    return disc, cont_log

# Experiment runner
def run_experiment():
    global screen, clock
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Single Training Trial")
    clock = pygame.time.Clock()

    initials = input("Enter player initials: ").strip()
    tgt_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)
    beep_snd = pygame.mixer.Sound(BEEP_SOUND_PATH)
    discrete, continuous = run_trial(True, "training 1", tgt_sound, beep_snd)
    save_discrete_log([discrete], f"{initials}_training1_discrete.csv")
    save_continuous_log(continuous, f"{initials}_training1_continuous.csv")
    pygame.quit(); sys.exit()

if __name__=="__main__":
    run_experiment()
