import pygame
import math
import sys
import time

# ---------------------------
# Configuration parameters
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3           # in meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0  # 1.65 m
BORDER_THRESHOLD = 0.2         # threshold from border in meters

# Target parameters (in meters)
TARGET_RADIUS = 0.3            # target radius in meters

# Define four arbitrary target positions (all completely within the arena)
# (Ensure that the target centers are at most (ARENA_RADIUS - TARGET_RADIUS) = 1.35 m from center)
target_positions = [
    (-0.65, -1.09),
    (1.0, 0.5),
    (-1.0, 0.8),
    (0.5, -1.2)
]

# Movement settings
MOVE_SPEED = 1.0               # meters per second
ROTATE_SPEED = 90.0            # degrees per second

# Scale factor for display: pixels per meter
SCALE = 200  # 1 meter = 200 pixels

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HUD_COLOR = (0, 255, 0)
DEBUG_COLOR = (50, 50, 255)   # Used for drawing arena border in test mode

# Window size (increased to ensure the full arena is visible)
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# Sound file paths (update these paths as needed)
TARGET_SOUND_PATH = "/Volumes/ramot/sunt/Navigation/SoundNavigation/Sounds/Dor/Underwater/Shark.wav"
BEEP_SOUND_PATH   = "/Volumes/ramot/sunt/Navigation/SoundNavigation/Sounds/Dor/Underwater/beep.wav"

# ---------------------------
# Ask for testing mode option
# ---------------------------
show_debug = input("Show player and borders? (Y/N): ").strip().lower() == 'y'

# ---------------------------
# Initialize Pygame and Mixer
# ---------------------------
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("MRI Exploration Task")
clock = pygame.time.Clock()

# Load sounds
try:
    target_sound = pygame.mixer.Sound(TARGET_SOUND_PATH)
except Exception as e:
    print("Error loading target sound:", e)
    target_sound = None

try:
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
except Exception as e:
    print("Error loading beep sound:", e)
    beep_sound = None

# Beep sound channel for looping beep when near border
beep_channel = None

# ---------------------------
# Global state variables
# ---------------------------
phase = "exploration"  # phases: "exploration", "annotation", "feedback"

# Exploration phase player state
player_pos = [0.0, 0.0]        # in meters, starting at center (0,0)
player_angle = 0.0             # in degrees; 0 means facing "up" (positive y)

# For logging movement during a single key press (exploration phase)
move_key_pressed = None        # 'up' or 'down'
move_start_pos = None          # starting position for movement measurement

rotate_key_pressed = None      # 'left' or 'right'
rotate_start_angle = None      # starting angle for rotation measurement

# Variable to track if the player was inside a target area (for playing target sound)
target_was_inside = False

# Annotation phase state
annotation_marker_pos = [0.0, 0.0]  # starts at center in arena coordinates

# ---------------------------
# Helper functions
# ---------------------------
def to_screen_coords(pos):
    """
    Convert arena coordinates (in meters) to screen coordinates (pixels).
    The arena's center (0,0) maps to the center of the screen.
    Note: In arena coordinates, y increases upward; in screen coordinates, y increases downward.
    """
    x, y = pos
    screen_x = CENTER_SCREEN[0] + int(x * SCALE)
    screen_y = CENTER_SCREEN[1] - int(y * SCALE)
    return (screen_x, screen_y)

def distance(a, b):
    """Euclidean distance between points a and b (both tuples)."""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_thermometer(distance_moved):
    """
    Draw a horizontal bar (thermometer) at the top-left showing
    the distance (in meters) moved during a single key press.
    The accumulation is slowed using an accumulation factor.
    """
    bar_x, bar_y = 50, 50
    max_bar_width = 400  # maximum width in pixels
    bar_height = 20
    accumulation_factor = 200  # pixels per meter (saturates at 2 m = 400 pixels)
    bar_width = min(max_bar_width, int(distance_moved * accumulation_factor))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    pygame.draw.rect(screen, HUD_COLOR, (bar_x, bar_y, bar_width, bar_height))

def draw_clock(angle_rotated):
    """
    Draw a clock-like dial at the top-right showing the rotation angle (in degrees)
    during a single key press. The hand points in the direction of rotation:
      - A negative angle indicates counterclockwise (left arrow).
      - A positive angle indicates clockwise (right arrow).
    """
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
    """
    Draw the arena border as a circle centered on the screen.
    In annotation and feedback phases, the border is drawn regardless of test mode.
    """
    pygame.draw.circle(screen, WHITE, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)

def draw_debug_items():
    """
    Draw debug visuals for exploration phase: arena border, player marker, and target outlines.
    Only used in test mode.
    """
    pygame.draw.circle(screen, DEBUG_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)
    for pos in target_positions:
        target_screen = to_screen_coords(pos)
        pygame.draw.circle(screen, DEBUG_COLOR, target_screen, int(TARGET_RADIUS * SCALE), 2)
    player_screen = to_screen_coords(player_pos)
    pygame.draw.circle(screen, (255, 0, 0), player_screen, 5)
    rad = math.radians(player_angle)
    line_length = 20
    end_x = player_screen[0] + int(line_length * math.sin(rad))
    end_y = player_screen[1] - int(line_length * math.cos(rad))
    pygame.draw.line(screen, (255, 0, 0), player_screen, (end_x, end_y), 2)

# ---------------------------
# Main game loop
# ---------------------------
running = True

while running:
    dt = clock.tick(60) / 1000.0  # frame time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Global key: Escape exits
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # Phase switching with Enter key
            if event.key == pygame.K_RETURN:
                if phase == "exploration":
                    phase = "annotation"
                    annotation_marker_pos = [0.0, 0.0]
                    if beep_channel is not None:
                        beep_channel.stop()
                        beep_channel = None
                elif phase == "annotation":
                    phase = "feedback"
        # Process events only for exploration phase
        if phase == "exploration":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    if move_key_pressed is None:
                        move_key_pressed = event.key
                        move_start_pos = player_pos.copy()
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
        # Update movement: forward/backward with current player_angle.
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
        # Update rotation: left arrow rotates left (counterclockwise), right arrow rotates right (clockwise).
        if keys[pygame.K_LEFT]:
            player_angle -= ROTATE_SPEED * dt
        if keys[pygame.K_RIGHT]:
            player_angle += ROTATE_SPEED * dt

        # Border detection: if near arena edge, play beep sound.
        player_distance_from_center = math.hypot(player_pos[0], player_pos[1])
        border_limit = ARENA_RADIUS - BORDER_THRESHOLD
        near_border = player_distance_from_center >= border_limit
        if near_border:
            if beep_sound is not None:
                if beep_channel is None or not beep_channel.get_busy():
                    beep_channel = beep_sound.play(loops=-1)
        else:
            if beep_channel is not None:
                beep_channel.stop()
                beep_channel = None

        # Target detection in exploration phase.
        is_inside_target = False
        encountered_target = None
        for pos in target_positions:
            if distance(player_pos, pos) <= TARGET_RADIUS:
                is_inside_target = True
                encountered_target = pos
                break
        if not target_was_inside and is_inside_target:
            if target_sound is not None:
                target_sound.play()
            print("Target reached at position:", encountered_target)
            target_positions = [encountered_target]
        target_was_inside = is_inside_target

        # Drawing for exploration phase.
        if show_debug:
            draw_debug_items()
        else:
            # In non-test mode, do not display border, player, or target.
            font = pygame.font.SysFont("Arial", 20)
            instruction_text = font.render("Exploration: Use arrow keys to move/rotate. Press Enter to annotate.", True, WHITE)
            screen.blit(instruction_text, (20, 20))
        # Draw HUD feedback for movement and rotation if keys are pressed.
        if move_key_pressed is not None and move_start_pos is not None:
            moved_distance = math.hypot(player_pos[0] - move_start_pos[0], player_pos[1] - move_start_pos[1])
            draw_thermometer(moved_distance)
        if rotate_key_pressed is not None and rotate_start_angle is not None:
            angle_diff = player_angle - rotate_start_angle
            draw_clock(angle_diff)

    elif phase == "annotation":
        # Annotation phase: arrow keys move the annotation marker (starting at center) without rotation.
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

        # Drawing for annotation phase: always show the arena border.
        draw_arena()
        marker_screen = to_screen_coords(annotation_marker_pos)
        pygame.draw.circle(screen, (0, 0, 255), marker_screen, 5)
        font = pygame.font.SysFont("Arial", 20)
        instruction_text = font.render("Annotation: Move marker with arrow keys. Press Enter when done.", True, WHITE)
        screen.blit(instruction_text, (20, 20))

    elif phase == "feedback":
        # Feedback phase: display the arena border, the annotation marker, and a small dot at the real target's center.
        draw_arena()
        marker_screen = to_screen_coords(annotation_marker_pos)
        pygame.draw.circle(screen, (0, 0, 255), marker_screen, 5)
        if target_positions:
            target_screen = to_screen_coords(target_positions[0])
            pygame.draw.circle(screen, (255, 255, 0), target_screen, 5, 0)  # small dot as feedback
        font = pygame.font.SysFont("Arial", 20)
        instruction_text = font.render("Feedback: Real target center shown. Press Escape to exit.", True, WHITE)
        screen.blit(instruction_text, (20, 20))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
