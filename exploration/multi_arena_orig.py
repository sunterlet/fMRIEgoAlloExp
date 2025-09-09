import pygame
import math
import sys
import time
import os
import random
import csv
from datetime import datetime
from pygame import mixer
from textwrap import wrap as _wrap

# Get player initials for file naming
player_initials = input("Enter player initials: ").strip()

# Create timestamp for the entire experiment
EXPERIMENT_TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")
# Global experiment start time
EXPERIMENT_START_TIME = time.time()

# ---------------------------
# Configuration parameters
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
BORDER_THRESHOLD = 0.1
TARGET_RADIUS = 0.3
ANNOTATION_RADIUS = 0.08  # Slightly smaller radius for annotations

# Debug mode
DEBUG_MODE = False

# Movement settings
MOVE_SPEED = 1.0
ROTATE_SPEED = 60.0
MOVEMENT_FADE_TIME = 0.1  # Time in seconds for movement indicator to fade out

# Scale factor: pixels per meter
SCALE = 200

# Window size
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# Results directory
RESULTS_DIR = "/Users/sunt/PhD/packngo/FullArena/results_FullArena"

# ---------------------------
# Custom Color Palette
# ---------------------------
BACKGROUND_COLOR = (3, 3, 1)        # Background: near-black
AVATAR_COLOR = (255, 67, 101)       # Avatar: Folly
BORDER_COLOR = (255, 255, 243)      # Arena border: Ivory
TARGET_COLOR = (0, 217, 192)        # Targets: Turquoise
ANNOTATION_COLOR = (183, 173, 153)  # Annotation: Khaki
WHITE = (255, 255, 255)

# ---------------------------
# Sound paths
# ---------------------------
SOUNDS_BASE_DIR = "/Users/sunt/PhD/packngo/FullArena/Sounds"
BEEP_SOUND_PATH = "/Users/sunt/PhD/packngo/FullArena/Sounds/beep.wav"

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

pygame.display.set_caption("Multi-Arena Experiment")
clock = pygame.time.Clock()

# ---------------------------
# Load sounds
# ---------------------------
def load_target_sounds(arena_name):
    """Load all target sounds from the arena's directory."""
    sounds = {}
    sounds_dir = os.path.join(SOUNDS_BASE_DIR, arena_name)
    
    # Check if directory exists
    if not os.path.exists(sounds_dir):
        print(f"Error: Sound directory not found: {sounds_dir}")
        return sounds
    
    # Load sounds
    for filename in os.listdir(sounds_dir):
        if filename.endswith('.mp3'):
            sound_path = os.path.join(sounds_dir, filename)
            try:
                sound = pygame.mixer.Sound(sound_path)
                # Store with lowercase key for case-insensitive matching
                sounds[filename[:-4].lower()] = sound
                print(f"Loaded sound: {filename}")
            except Exception as e:
                print(f"Error loading sound {filename}: {e}")
    
    return sounds

try:
    beep_sound = pygame.mixer.Sound(BEEP_SOUND_PATH)
except Exception as e:
    print("Error loading beep sound:", e)
    beep_sound = None

# ---------------------------
# Load arena data
# ---------------------------
def load_arena_data():
    """Load arena data from CSV file."""
    arenas = {}
    with open("Arenas.csv", 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            arena_name, target_name, coords = row
            # Parse coordinates from string format "(x; y)"
            coords = coords.strip('()').split(';')
            x, y = float(coords[0]), float(coords[1])
            if arena_name not in arenas:
                arenas[arena_name] = {}
            arenas[arena_name][target_name] = (x, y)
    return arenas

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
    """Draw the arena border."""
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

def draw_targets(targets, show_names=False):
    """Draw all targets and optionally their names."""
    for target_name, target_pos in targets.items():
        target_screen = to_screen_coords(target_pos)
        pygame.draw.circle(game_surface, TARGET_COLOR, target_screen, int(TARGET_RADIUS * SCALE))
        if show_names:
            font = pygame.font.SysFont("Arial", 16)
            text = font.render(target_name, True, WHITE)
            text_rect = text.get_rect(center=(target_screen[0], target_screen[1] - 20))
            game_surface.blit(text, text_rect)

def draw_annotations(annotations, current_pos=None, typing_active=False, current_name=""):
    """Draw all annotations with their names and highlight current selection."""
    # Draw all previous annotations
    for pos, name in annotations.items():
        if name:  # Only draw if a name has been assigned
            # Parse position from string
            x, y = map(float, pos.split(','))
            target_screen = to_screen_coords((x, y))
            # Draw filled circle for confirmed annotations
            pygame.draw.circle(game_surface, ANNOTATION_COLOR, target_screen, int(ANNOTATION_RADIUS * SCALE))
            font = pygame.font.SysFont("Arial", 16)
            text = font.render(name, True, WHITE)
            text_rect = text.get_rect(center=(target_screen[0], target_screen[1] - 25))
            game_surface.blit(text, text_rect)
    
    # Draw current selection if it exists
    if current_pos is not None:
        target_screen = to_screen_coords(current_pos)
        # Draw outlined circle for current selection
        pygame.draw.circle(game_surface, ANNOTATION_COLOR, target_screen, int(ANNOTATION_RADIUS * SCALE), 2)
        # Draw a pulsing effect
        pulse_radius = int(ANNOTATION_RADIUS * SCALE * (1 + 0.2 * math.sin(time.time() * 5)))
        pygame.draw.circle(game_surface, ANNOTATION_COLOR, target_screen, pulse_radius, 1)
        
        # Draw current name being typed above the selection
        if typing_active:
            font = pygame.font.SysFont("Arial", 16)
            text = font.render(current_name, True, WHITE)
            text_rect = text.get_rect(center=(target_screen[0], target_screen[1] - 25))
            game_surface.blit(text, text_rect)

def draw_finished_button():
    """Draw the 'Finished' button."""
    button_rect = pygame.Rect(WIN_WIDTH - 150, WIN_HEIGHT - 50, 120, 40)
    pygame.draw.rect(game_surface, ANNOTATION_COLOR, button_rect)
    font = pygame.font.SysFont("Arial", 20)
    text = font.render("Finished", True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    game_surface.blit(text, text_rect)
    return button_rect

def draw_timer(time_left):
    """Draw the remaining time."""
    font = pygame.font.SysFont("Arial", 24)
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    # Draw "Time" label
    label_text = font.render("Time", True, WHITE)
    # Draw the actual time
    timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
    # Position timer in middle left, next to arena
    timer_x = CENTER_SCREEN[0] - int(ARENA_RADIUS * SCALE) - 100
    timer_y = CENTER_SCREEN[1]
    # Draw label and timer on separate lines
    game_surface.blit(label_text, (timer_x, timer_y))
    game_surface.blit(timer_text, (timer_x, timer_y + 30))

def draw_instruction(text):
    """Draw instruction text at the bottom of the screen."""
    font = pygame.font.SysFont("Arial", 20)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(centerx=WIN_WIDTH//2, bottom=WIN_HEIGHT-30)
    game_surface.blit(text_surface, text_rect)

def draw_thermometer(distance_moved, is_moving_forward_backward, movement_stop_time, current_time):
    """Draw a horizontal bar (thermometer) at the top-left showing distance moved."""
    # Only show if currently moving or within delay time
    should_show = is_moving_forward_backward or (movement_stop_time is not None and 
        current_time - movement_stop_time <= MOVEMENT_FADE_TIME)
    
    if not should_show:
        return 0.0  # Reset distance when indicator disappears
    
    bar_x, bar_y = 50, 30
    max_bar_width = int(ARENA_DIAMETER * SCALE)
    bar_height = 20
    accumulation_factor = 200
    bar_width = min(max_bar_width, int(distance_moved * accumulation_factor))
    
    # Draw label
    font = pygame.font.SysFont("Arial", 20)
    label_text = font.render("Forward/Backward Movement", True, WHITE)
    game_surface.blit(label_text, (bar_x, bar_y - 25))
    
    # Draw the empty bar (border)
    pygame.draw.rect(game_surface, WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
    
    # Draw the filled portion only if we should show
    if should_show:
        pygame.draw.rect(game_surface, TARGET_COLOR, (bar_x, bar_y, bar_width, bar_height))
    
    return distance_moved  # Return current distance

def draw_clock(angle_rotated, is_rotating, rotation_stop_time, current_time):
    """Draw a clock-like dial at the top-right showing rotation angle."""
    # Only show if currently rotating or within delay time
    should_show = is_rotating or (rotation_stop_time is not None and 
        current_time - rotation_stop_time <= MOVEMENT_FADE_TIME)
    
    if not should_show:
        return 0.0  # Reset angle when indicator disappears

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
    pygame.draw.line(game_surface, ANNOTATION_COLOR, dial_center, (int(end_x), int(end_y)), 4)
    
    # Draw the angle text with sign
    angle_text = font.render(f"{int(angle_rotated)}°", True, WHITE)
    text_rect = angle_text.get_rect(center=(dial_center[0], dial_center[1] - 10))
    game_surface.blit(angle_text, text_rect)
    
    return angle_rotated  # Return current angle

def draw_feedback(targets, annotations):
    """Draw feedback showing targets and annotations."""
    # Draw real targets first
    draw_targets(targets, show_names=True)
    
    # Draw annotations with a different color to distinguish them
    for pos_key, name in annotations.items():
        x, y = map(float, pos_key.split(','))
        screen_pos = to_screen_coords((x, y))
        
        # Draw a semi-transparent circle for the selected target
        overlay_surface = pygame.Surface((int(TARGET_RADIUS * SCALE * 2), int(TARGET_RADIUS * SCALE * 2)), pygame.SRCALPHA)
        pygame.draw.circle(overlay_surface, (*ANNOTATION_COLOR, 128), (int(TARGET_RADIUS * SCALE), int(TARGET_RADIUS * SCALE)), int(TARGET_RADIUS * SCALE))
        game_surface.blit(overlay_surface, (screen_pos[0] - int(TARGET_RADIUS * SCALE), screen_pos[1] - int(TARGET_RADIUS * SCALE)))
        
        # Draw the target name
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(name, True, ANNOTATION_COLOR)
        text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - int(TARGET_RADIUS * SCALE) - 10))
        game_surface.blit(text, text_rect)
    
    # Draw legend
    legend_x = 20
    legend_y = 20
    dot_radius = 8
    font = pygame.font.SysFont("Arial", 16)
    legend_items = [
        (TARGET_COLOR, "Real Target"),
        ((*ANNOTATION_COLOR, 128), "Selected Target")
    ]
    legend_height = len(legend_items) * 28 + 10
    legend_width = 140
    # Draw legend background
    legend_surface = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
    legend_surface.fill((0, 0, 0, 128))
    game_surface.blit(legend_surface, (legend_x - 10, legend_y - 10))
    # Draw each legend item aligned
    for i, (color, label) in enumerate(legend_items):
        y = legend_y + i * 28
        dot_center = (legend_x + dot_radius, y + dot_radius + 2)
        if label == "Real Target":
            pygame.draw.circle(game_surface, color, dot_center, dot_radius)
        else:
            overlay_surface = pygame.Surface((dot_radius*2, dot_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(overlay_surface, color, (dot_radius, dot_radius), dot_radius)
            game_surface.blit(overlay_surface, (dot_center[0] - dot_radius, dot_center[1] - dot_radius))
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(midleft=(legend_x + dot_radius*2 + 8, dot_center[1]))
        game_surface.blit(text, text_rect)
    # Draw instruction
    font = pygame.font.SysFont("Arial", 24)
    text = font.render("Review your annotations. Press Enter to continue.", True, WHITE)
    text_rect = text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT-50))
    game_surface.blit(text, text_rect)

def draw_arena_intro(arena_name, arena_num, total_arenas, num_targets, targets=None):
    """Draw the arena introduction screen."""
    game_surface.fill(BACKGROUND_COLOR)
    y = WIN_HEIGHT // 2 - 80
    # Arena name (capitalize Practice)
    font = pygame.font.SysFont("Arial", 36)
    arena_label = arena_name.replace('practice', 'Practice ')
    name_text = font.render(f"Arena: {arena_label}", True, WHITE)
    name_rect = name_text.get_rect(center=(WIN_WIDTH//2, y))
    game_surface.blit(name_text, name_rect)
    y += 45
    # Arena number
    font_small = pygame.font.SysFont("Arial", 24)
    num_text = font_small.render(f"Arena {arena_num} of {total_arenas}", True, WHITE)
    num_rect = num_text.get_rect(center=(WIN_WIDTH//2, y))
    game_surface.blit(num_text, num_rect)
    y += 35
    # Number of targets
    targets_text = font_small.render(f"Number of targets: {num_targets}", True, WHITE)
    targets_rect = targets_text.get_rect(center=(WIN_WIDTH//2, y))
    game_surface.blit(targets_text, targets_rect)
    y += 35
    # Targets list for practice arenas
    if targets is not None and arena_name.startswith('practice'):
        font_targets = pygame.font.SysFont("Arial", 24)
        target_names = ', '.join(targets.keys())
        targets_line = font_targets.render(f"Targets: {target_names}", True, WHITE)
        targets_line_rect = targets_line.get_rect(center=(WIN_WIDTH//2, y))
        game_surface.blit(targets_line, targets_line_rect)
        y += 45
    # Instruction
    font_instr = pygame.font.SysFont("Arial", 20)
    instruction_text = font_instr.render("Press Enter to begin exploration", True, WHITE)
    instruction_rect = instruction_text.get_rect(center=(WIN_WIDTH//2, y + 20))
    game_surface.blit(instruction_text, instruction_rect)
    screen.blit(game_surface, (offset_x, offset_y))
    pygame.display.flip()

def save_logs(discrete_log, continuous_log, player_initials, append=False):
    """Save both discrete and continuous logs to CSV files."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    discrete_filename = os.path.join(RESULTS_DIR, f"{player_initials}_discrete_log_{EXPERIMENT_TIMESTAMP}.csv")
    continuous_filename = os.path.join(RESULTS_DIR, f"{player_initials}_continuous_log_{EXPERIMENT_TIMESTAMP}.csv")
    write_headers = not append or not os.path.exists(discrete_filename)
    with open(discrete_filename, 'a' if append else 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["RoundName", "TypedName", "ChosenPosition", "TimeToAnnotation"])
        if write_headers:
            writer.writeheader()
        writer.writerows(discrete_log)
    with open(continuous_filename, 'a' if append else 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["RealTime", "Time", "RoundName", "phase", "event", "x", "y", "rotation_angle"])
        if write_headers:
            writer.writeheader()
        writer.writerows(continuous_log)
    if not append:
        print(f"\nLog files created:")
        print(f"Discrete log: {discrete_filename}")
        print(f"Continuous log: {continuous_filename}")

def get_player_tip_position(player_pos, player_angle):
    """Calculate the position of the player's tip (in arena coordinates)."""
    tip_length = 30 / SCALE  # 30 pixels, converted to meters
    rad = math.radians(player_angle)
    tip_x = player_pos[0] + tip_length * math.sin(rad)
    tip_y = player_pos[1] + tip_length * math.cos(rad)
    return (tip_x, tip_y)

def draw_exit_button():
    button_width, button_height = 120, 40
    button_x = 20
    button_y = WIN_HEIGHT - button_height - 20
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(game_surface, (200, 60, 60), button_rect)
    font = pygame.font.SysFont("Arial", 20)
    text = font.render("Exit", True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    game_surface.blit(text, text_rect)
    return button_rect

def run_arena(arena_name, targets, arena_num, total_arenas):
    """Run a single arena trial."""
    target_sounds = load_target_sounds(arena_name)
    print(f"\nLoaded {len(target_sounds)} sounds for arena {arena_name}")
    player_pos = [0.0, 0.0]
    player_angle = 0.0
    phase = "exploration"
    exploration_start_time = time.time()  # For annotation timing only
    annotation_start_time = None
    found_targets = set()
    target_was_inside = {name: False for name in targets.keys()}  # Track if player was inside each target's area
    annotations = {}
    current_annotation_pos = None
    current_annotation_name = ""
    typing_active = False
    beep_channel = None
    continuous_log = []
    discrete_log = []
    distance_moved = 0.0
    angle_rotated = 0.0  # Will be positive for right, negative for left
    last_pos = [0.0, 0.0]
    last_angle = 0.0
    is_moving_forward_backward = False
    is_rotating = False
    rotation_direction = None  # 'left' or 'right'
    movement_stop_time = None
    rotation_stop_time = None  # Add this line for rotation stop tracking
    has_moved_in_trial = False  # Track if any movement has occurred in this trial
    last_log_time = time.time()
    LOG_INTERVAL = 0.1
    # Set exploration time based on arena type
    if arena_name.startswith('practice'):
        exploration_time = 90  # 1.5 minutes for practice arenas
    else:
        exploration_time = 120  # 2 minutes for all non-practice arenas
    running = True
    annotation_saved = False  # Add a flag to prevent double-saving
    exit_to_feedback = False
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time()
        experiment_time = current_time - EXPERIMENT_START_TIME
        if experiment_time - (last_log_time - EXPERIMENT_START_TIME) >= LOG_INTERVAL:
            log_entry = {
                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                "Time": round(experiment_time, 3),
                "RoundName": arena_name,
                "phase": phase,
                "event": "",
                "x": round(player_pos[0], 3),
                "y": round(player_pos[1], 3),
                "rotation_angle": round(player_angle, 3)
            }
            continuous_log.append(log_entry)
            save_logs([], [log_entry], player_initials, append=True)
            last_log_time = current_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Ignore window close events to prevent accidental exit
                pass
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_ESCAPE and phase == "annotation" and typing_active:
                    typing_active = False
                    current_annotation_pos = None
                    current_annotation_name = ""
                elif event.key in (pygame.K_LMETA, pygame.K_RMETA):
                    global DEBUG_MODE
                    if player_initials == "111":
                        DEBUG_MODE = not DEBUG_MODE
                elif event.key == pygame.K_RETURN:
                    if phase == "exploration":
                        time_left = exploration_time - (current_time - exploration_start_time)
                        # Allow skipping in practice arenas or if initials are '111' or timer expired
                        if arena_name.startswith('practice') or player_initials == "111" or time_left <= 0:
                            # Reset position and angle BEFORE logging phase change
                            player_pos = [0.0, 0.0]
                            player_angle = 0.0
                            # Stop beep sound if it's playing
                            if beep_channel is not None:
                                beep_channel.stop()
                                beep_channel = None
                            phase = "annotation"
                            annotation_start_time = time.time()
                            phase_change_log = {
                                "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                                "Time": round(time.time() - EXPERIMENT_START_TIME, 3),
                                "RoundName": arena_name,
                                "phase": phase,
                                "event": "phase_change",
                                "x": round(player_pos[0], 3),
                                "y": round(player_pos[1], 3),
                                "rotation_angle": round(player_angle, 3)
                            }
                            continuous_log.append(phase_change_log)
                            save_logs([], [phase_change_log], player_initials, append=True)
                    elif phase == "annotation":
                        if not typing_active:
                            current_annotation_pos = (player_pos[0], player_pos[1])
                            typing_active = True
                            current_annotation_name = ""
                            annotation_saved = False
                        elif typing_active and not annotation_saved:
                            if current_annotation_name:
                                pos_key = f"{current_annotation_pos[0]:.3f},{current_annotation_pos[1]:.3f}"
                                if pos_key not in annotations:
                                    annotations[pos_key] = current_annotation_name
                                    discrete_entry = {
                                        "RoundName": arena_name,
                                        "TypedName": current_annotation_name,
                                        "ChosenPosition": pos_key,
                                        "TimeToAnnotation": round(time.time() - annotation_start_time, 3)
                                    }
                                    discrete_log.append(discrete_entry)
                                    save_logs([discrete_entry], [], player_initials, append=True)
                                    annotation_log = {
                                        "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                                        "Time": round(time.time() - EXPERIMENT_START_TIME, 3),
                                        "RoundName": arena_name,
                                        "phase": phase,
                                        "event": f"{current_annotation_name}_annotated",
                                        "x": round(player_pos[0], 3),
                                        "y": round(player_pos[1], 3),
                                        "rotation_angle": round(player_angle, 3)
                                    }
                                    continuous_log.append(annotation_log)
                                    save_logs([], [annotation_log], player_initials, append=True)
                                annotation_saved = True
                            typing_active = False
                            current_annotation_pos = None
                            current_annotation_name = ""
                    elif phase == "feedback":
                        return discrete_log, continuous_log, exit_to_feedback
                elif phase == "annotation" and typing_active:
                    if event.key == pygame.K_BACKSPACE:
                        current_annotation_name = current_annotation_name[:-1]
                    elif event.unicode.isprintable():
                        current_annotation_name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                adjusted_mouse_pos = (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y)
                if exit_button_rect.collidepoint(adjusted_mouse_pos):
                    exit_to_feedback = True
                    running = False
                    break
                if phase == "annotation":
                    if finished_button_rect.collidepoint(adjusted_mouse_pos):
                        if typing_active and current_annotation_name and not annotation_saved:
                            pos_key = f"{current_annotation_pos[0]:.3f},{current_annotation_pos[1]:.3f}"
                            if pos_key not in annotations:
                                annotations[pos_key] = current_annotation_name
                                discrete_entry = {
                                    "RoundName": arena_name,
                                    "TypedName": current_annotation_name,
                                    "ChosenPosition": pos_key,
                                    "TimeToAnnotation": round(time.time() - annotation_start_time, 3)
                                }
                                discrete_log.append(discrete_entry)
                                save_logs([discrete_entry], [], player_initials, append=True)
                                annotation_log = {
                                    "Time": round(time.time() - EXPERIMENT_START_TIME, 3),
                                    "RoundName": arena_name,
                                    "phase": phase,
                                    "event": f"{current_annotation_name}_annotated",
                                    "x": round(player_pos[0], 3),
                                    "y": round(player_pos[1], 3),
                                    "rotation_angle": round(player_angle, 3)
                                }
                                continuous_log.append(annotation_log)
                                save_logs([], [annotation_log], player_initials, append=True)
                            annotation_saved = True
                        typing_active = False
                        current_annotation_pos = None
                        phase = "feedback"
                        finish_log = {
                            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                            "Time": round(time.time() - EXPERIMENT_START_TIME, 3),
                            "RoundName": arena_name,
                            "phase": phase,
                            "event": "finish_press",
                            "x": round(player_pos[0], 3),
                            "y": round(player_pos[1], 3),
                            "rotation_angle": round(player_angle, 3)
                        }
                        continuous_log.append(finish_log)
                        save_logs([], [finish_log], player_initials, append=True)
        
        keys = pygame.key.get_pressed()
        if phase in ["exploration", "annotation"]:
            old_pos = list(player_pos)
            old_angle = player_angle
            
            if keys[pygame.K_UP]:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
                    is_moving_forward_backward = True
                    has_moved_in_trial = True
            if keys[pygame.K_DOWN]:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] - dx
                new_y = player_pos[1] - dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
                    is_moving_forward_backward = True
                    has_moved_in_trial = True
            if keys[pygame.K_LEFT]:
                player_angle = (player_angle - ROTATE_SPEED * dt) % 360
                is_rotating = True
                if rotation_direction != 'left':
                    rotation_direction = 'left'
                    angle_rotated = 0
                angle_rotated -= ROTATE_SPEED * dt
                if angle_rotated <= -360:
                    angle_rotated = 0
                has_moved_in_trial = True
            if keys[pygame.K_RIGHT]:
                player_angle = (player_angle + ROTATE_SPEED * dt) % 360
                is_rotating = True
                if rotation_direction != 'right':
                    rotation_direction = 'right'
                    angle_rotated = 0
                angle_rotated += ROTATE_SPEED * dt
                if angle_rotated >= 360:
                    angle_rotated = 0
                has_moved_in_trial = True
            
            if is_moving_forward_backward:
                distance_moved += math.hypot(player_pos[0] - old_pos[0], player_pos[1] - old_pos[1])
            
            if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                if is_moving_forward_backward:
                    movement_stop_time = current_time
                is_moving_forward_backward = False
            else:
                movement_stop_time = None

            # Reset rotation tracking when rotation stops
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                if is_rotating:  # Only set stop time if we were rotating
                    rotation_stop_time = current_time
                is_rotating = False
                rotation_direction = None
                # Don't reset angle_rotated here - keep it for fade-out period
            else:
                rotation_stop_time = None  # Reset stop time when rotating

            # Reset indicators after fade time elapses
            if movement_stop_time is not None and current_time - movement_stop_time > MOVEMENT_FADE_TIME:
                distance_moved = 0.0
                movement_stop_time = None

            if rotation_stop_time is not None and current_time - rotation_stop_time > MOVEMENT_FADE_TIME:
                angle_rotated = 0.0  # Only reset angle after fade time elapses
                rotation_stop_time = None
        
        if math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
            if beep_sound is not None:
                if beep_channel is None or not beep_channel.get_busy():
                    beep_channel = beep_sound.play(loops=-1)
        else:
            if beep_channel is not None:
                beep_channel.stop()
                beep_channel = None
        
        if phase == "exploration":
            tip_pos = get_player_tip_position(player_pos, player_angle)
            for target_name, target_pos in targets.items():
                is_inside = distance(tip_pos, target_pos) <= TARGET_RADIUS
                if is_inside and not target_was_inside[target_name]:
                    target_was_inside[target_name] = True
                    encounter_log = {
                        "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                        "Time": round(current_time - EXPERIMENT_START_TIME, 3),
                        "RoundName": arena_name,
                        "phase": "exploration",
                        "event": f"found_{target_name}",
                        "x": round(tip_pos[0], 3),
                        "y": round(tip_pos[1], 3),
                        "rotation_angle": round(player_angle, 3)
                    }
                    continuous_log.append(encounter_log)
                    save_logs([], [encounter_log], player_initials, append=True)
                    target_name_lower = target_name.lower()
                    if target_name_lower in target_sounds:
                        try:
                            target_sounds[target_name_lower].play()
                            print(f"Playing sound for {target_name}")
                        except Exception as e:
                            print(f"Error playing sound for {target_name}: {e}")
                    else:
                        print(f"Warning: No sound found for {target_name} (tried {target_name_lower})")
                elif not is_inside and target_was_inside[target_name]:
                    target_was_inside[target_name] = False
        
        screen.fill(BACKGROUND_COLOR)
        game_surface.fill(BACKGROUND_COLOR)
        
        if phase == "exploration":
            if DEBUG_MODE:
                draw_arena()
                draw_player_avatar(player_pos, player_angle)
            elif arena_name == "practice1":
                draw_arena()
                draw_player_avatar(player_pos, player_angle)
            elif arena_name == "practice2":
                if (abs(player_pos[0]) < 0.01 and abs(player_pos[1]) < 0.01) and not has_moved_in_trial or \
                   math.hypot(player_pos[0], player_pos[1]) >= (ARENA_RADIUS - BORDER_THRESHOLD):
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            else:
                if abs(player_pos[0]) < 0.01 and abs(player_pos[1]) < 0.01 and not has_moved_in_trial:
                    draw_arena()
                    draw_player_avatar(player_pos, player_angle)
            
            if DEBUG_MODE:
                draw_targets(targets, show_names=True)
            
            if is_moving_forward_backward or (movement_stop_time is not None and 
                current_time - movement_stop_time <= MOVEMENT_FADE_TIME):
                distance_moved = draw_thermometer(distance_moved, is_moving_forward_backward, 
                               movement_stop_time, current_time)
            if is_rotating or (rotation_stop_time is not None and 
                current_time - rotation_stop_time <= MOVEMENT_FADE_TIME):
                angle_rotated = draw_clock(angle_rotated, is_rotating, rotation_stop_time, current_time)
            
            time_left = exploration_time - (current_time - exploration_start_time)
            if time_left > 0:
                draw_timer(time_left)
                if player_initials == "111":
                    draw_instruction("Press Enter when you're ready to annotate the target locations")
            else:
                player_pos = [0.0, 0.0]
                player_angle = 0.0
                if beep_channel is not None:
                    beep_channel.stop()
                    beep_channel = None
                phase = "annotation"
                annotation_start_time = time.time()
                phase_change_log = {
                    "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    "Time": round(time.time() - EXPERIMENT_START_TIME, 3),
                    "RoundName": arena_name,
                    "phase": phase,
                    "event": "phase_change",
                    "x": round(player_pos[0], 3),
                    "y": round(player_pos[1], 3),
                    "rotation_angle": round(player_angle, 3)
                }
                continuous_log.append(phase_change_log)
                save_logs([], [phase_change_log], player_initials, append=True)
        
        elif phase == "annotation":
            draw_arena()
            draw_player_avatar(player_pos, player_angle)
            if DEBUG_MODE:
                draw_targets(targets, show_names=True)
            draw_annotations(annotations, current_annotation_pos, typing_active, current_annotation_name)
            
            if is_moving_forward_backward or (movement_stop_time is not None and 
                current_time - movement_stop_time <= MOVEMENT_FADE_TIME):
                distance_moved = draw_thermometer(distance_moved, is_moving_forward_backward, 
                               movement_stop_time, current_time)
            if is_rotating or (rotation_stop_time is not None and 
                current_time - rotation_stop_time <= MOVEMENT_FADE_TIME):
                angle_rotated = draw_clock(angle_rotated, is_rotating, rotation_stop_time, current_time)
            
            if arena_name == "practice1":
                finished_button_rect = draw_finished_button()
                font = pygame.font.SysFont("Arial", 20)
                text = font.render("Press when done annotating the arena", True, WHITE)
                text_rect = text.get_rect(midright=(WIN_WIDTH - 150 - 50, WIN_HEIGHT - 50 + 20))
                game_surface.blit(text, text_rect)
                
                if int(time.time() * 2) % 2:
                    arrow_points = [
                        (WIN_WIDTH - 150 - 20, WIN_HEIGHT - 50 + 20),
                        (WIN_WIDTH - 150 - 40, WIN_HEIGHT - 50 + 10),
                        (WIN_WIDTH - 150 - 40, WIN_HEIGHT - 50 + 30)
                    ]
                    pygame.draw.polygon(game_surface, WHITE, arrow_points)
                
                if typing_active:
                    font = pygame.font.SysFont("Arial", 24)
                    text = font.render("Type the target name and press Enter to confirm", True, WHITE)
                    text_rect = text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT//2))
                    game_surface.blit(text, text_rect)
                else:
                    font = pygame.font.SysFont("Arial", 24)
                    text = font.render("Navigate to a location and press Enter to annotate", True, WHITE)
                    text_rect = text.get_rect(center=(WIN_WIDTH//2, WIN_HEIGHT//2))
                    game_surface.blit(text, text_rect)
            else:
                finished_button_rect = draw_finished_button()
                if typing_active:
                    draw_instruction("Type the target name and press Enter to confirm")
                else:
                    draw_instruction("Navigate to a location and press Enter to annotate")
        
        elif phase == "feedback":
            draw_arena()
            draw_feedback(targets, annotations)
        
        exit_button_rect = draw_exit_button()
        
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()
        if exit_to_feedback:
            break
    return discrete_log, continuous_log, exit_to_feedback

def show_feedback_screen():
    """Display a feedback prompt and collect user input."""
    input_active = True
    font = pygame.font.SysFont("Arial", 24)
    user_input = ""
    button_font = pygame.font.SysFont("Arial", 24)
    button_text = button_font.render("Submit", True, WHITE)
    button_width, button_height = 140, 50
    button_x = WIN_WIDTH // 2 - button_width // 2
    button_y = WIN_HEIGHT - 60
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    input_box_x = 40
    input_box_y = 100
    input_box_width = WIN_WIDTH - 80
    input_box_height = WIN_HEIGHT - 200
    input_box_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    user_input += '\n'
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_TAB:
                    pass
                elif event.unicode.isprintable():
                    user_input += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                adjusted_mouse_pos = (mouse_pos[0] - offset_x, mouse_pos[1] - offset_y)
                if button_rect.collidepoint(adjusted_mouse_pos):
                    input_active = False
        game_surface.fill(BACKGROUND_COLOR)
        prompt_font = pygame.font.SysFont("Arial", 28)
        prompt_text = prompt_font.render("Type your feedback here", True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WIN_WIDTH // 2, input_box_y - 30))
        game_surface.blit(prompt_text, prompt_rect)
        pygame.draw.rect(game_surface, (30, 30, 30), input_box_rect)
        pygame.draw.rect(game_surface, WHITE, input_box_rect, 2)
        input_y = input_box_y + 10
        input_lines = user_input.split('\n')
        for line in input_lines:
            text_surface = font.render(line, True, WHITE)
            game_surface.blit(text_surface, (input_box_x + 10, input_y))
            input_y += 32
        pygame.draw.rect(game_surface, (60, 60, 60), button_rect)
        pygame.draw.rect(game_surface, WHITE, button_rect, 2)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        game_surface.blit(button_text, button_text_rect)
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()
        clock.tick(30)
    # Save feedback
    feedback_text = user_input.strip()
    feedback_filename = os.path.join(RESULTS_DIR, f"{player_initials}_feedback_{EXPERIMENT_TIMESTAMP}.txt")
    with open(feedback_filename, 'w') as f:
        f.write(feedback_text)
    print(f"Feedback saved to {feedback_filename}")
    # Show final instruction image instead of thank you screen
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/8.png")

def show_image(image_path):
    """Display an image in its original size and wait for Enter key to continue."""
    try:
        image = pygame.image.load(image_path)
        image_rect = image.get_rect()
        image_rect.center = (screen_width // 2, screen_height // 2)
        
        screen.fill(BACKGROUND_COLOR)
        screen.blit(image, image_rect)
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # For the final instruction (8.png), use Q to exit instead of Enter
                    if "8.png" in image_path:
                        if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                    else:
                        if event.key == pygame.K_RETURN:
                            waiting = False
        
        # Only clear screen and continue if not the final instruction
        if "8.png" not in image_path:
            screen.fill(BACKGROUND_COLOR)
            pygame.display.flip()
        
    except pygame.error as e:
        print(f"Error loading image {image_path}: {e}")
        pygame.quit()
        sys.exit()

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def run_practice_game():
    """Run the practice game where the player must reach a score of 5."""
    arena_center = (WIN_WIDTH // 2, WIN_HEIGHT // 2)
    arena_radius = int(ARENA_RADIUS * SCALE)
    avatar_pos = [arena_center[0], arena_center[1]]
    avatar_angle = 0
    avatar_speed = 3
    avatar_size = 15
    goal_radius = 10
    global beep_sound
    beep_channel = None
    try:
        practice_target_sound = pygame.mixer.Sound("/Users/sunt/PhD/packngo/FullArena/Sounds/target.wav")
    except Exception as e:
        practice_target_sound = None
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
        score_text = font.render(f"Score: {score}", True, ANNOTATION_COLOR)
        game_surface.blit(score_text, (10, 10))
    def within_arena(new_pos):
        dist = math.hypot(new_pos[0] - arena_center[0], new_pos[1] - arena_center[1])
        return dist <= arena_radius - avatar_size
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    # Only allow skipping if initials are '111'
                    if player_initials == "111":
                        # Stop beep sound if it's playing
                        if beep_channel is not None:
                            beep_channel.stop()
                            beep_channel = None
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
            avatar_angle -= 70.0 * dt
        if keys[pygame.K_RIGHT]:
            avatar_angle += 70.0 * dt
        if math.hypot(avatar_pos[0] - arena_center[0], avatar_pos[1] - arena_center[1]) >= (arena_radius - BORDER_THRESHOLD * SCALE):
            if beep_sound is not None:
                if beep_channel is None or not beep_channel.get_busy():
                    beep_channel = beep_sound.play(loops=-1)
        else:
            if beep_channel is not None:
                beep_channel.stop()
                beep_channel = None
        tip_length = 30
        rad = math.radians(avatar_angle)
        tip_x = avatar_pos[0] + tip_length * math.cos(rad)
        tip_y = avatar_pos[1] + tip_length * math.sin(rad)
        if math.hypot(tip_x - goal_pos[0], tip_y - goal_pos[1]) < (goal_radius + 5):
            score += 1
            goal_pos = random_position_in_arena()
            if practice_target_sound is not None:
                practice_target_sound.play()
        screen.fill(BACKGROUND_COLOR)
        game_surface.fill(BACKGROUND_COLOR)
        draw_arena()
        draw_goal()
        draw_avatar()
        draw_score()
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()
        if score >= 5:
            if beep_channel is not None:
                beep_channel.stop()
                beep_channel = None
            running = False

def main():
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/1.png")
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/2.png")
    run_practice_game()
    arenas = load_arena_data()
    practice_arenas = ['practice1', 'practice2']
    other_arenas = [name for name in arenas.keys() if name not in practice_arenas]
    random.shuffle(other_arenas)
    arena_names = practice_arenas + other_arenas
    all_discrete_log = []
    all_continuous_log = []
    save_logs([], [], player_initials)
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/3.png")
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/4.png")
    i = 1
    draw_arena_intro('practice1', i, len(arena_names), len(arenas['practice1']), targets=arenas['practice1'])
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
    discrete_log, continuous_log, exit_to_feedback = run_arena('practice1', arenas['practice1'], i, len(arena_names))
    all_discrete_log.extend(discrete_log)
    all_continuous_log.extend(continuous_log)
    if exit_to_feedback:
        show_feedback_screen()
        return
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/5.png")
    i = 2
    draw_arena_intro('practice2', i, len(arena_names), len(arenas['practice2']), targets=arenas['practice2'])
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
    discrete_log, continuous_log, exit_to_feedback = run_arena('practice2', arenas['practice2'], i, len(arena_names))
    all_discrete_log.extend(discrete_log)
    all_continuous_log.extend(continuous_log)
    if exit_to_feedback:
        show_feedback_screen()
        return
    if other_arenas:
        show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/6.png")
    for j, arena_name in enumerate(other_arenas, 3):
        draw_arena_intro(arena_name, j, len(arena_names), len(arenas[arena_name]), targets=None)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
        discrete_log, continuous_log, exit_to_feedback = run_arena(arena_name, arenas[arena_name], j, len(arena_names))
        all_discrete_log.extend(discrete_log)
        all_continuous_log.extend(continuous_log)
        if exit_to_feedback:
            show_feedback_screen()
            return
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/7.png")
    show_feedback_screen()
    show_image("/Users/sunt/PhD/packngo/FullArena/Instructions/8.png")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main() 