import pygame
import math

# ------------------------------------------------------------------
# 1) USER CONFIGURATION
# ------------------------------------------------------------------

# Arena
ARENA_RADIUS_M = 1.65  # 3.3 m diameter => radius = 1.65 m

# Screen (in pixels)
WIDTH, HEIGHT = 800, 600
ARENA_CENTER_PX = (WIDTH // 2, HEIGHT // 2)

# Scaling: how many pixels per meter
# We want the arena radius (1.65 m) to be comfortably drawn.
# For example, a scale of ~150 px/m makes the arena ~248 px in radius.
SCALE = 150
ARENA_RADIUS_PX = int(ARENA_RADIUS_M * SCALE)

# Avatar (the player)
AVATAR_SPEED_M_S = 1.0        # Avatar moves at 1.0 m/s
AVATAR_ROT_SPEED_DEG_S = 90.0 # 90 degrees per second rotation
AVATAR_RADIUS_M = 0.15        # ~15 cm from center to tip of the triangle
AVATAR_RADIUS_PX = AVATAR_RADIUS_M * SCALE

# Goals (in meters, radius = 0.15 m => diameter = 0.30 m)
# We do not draw them (they are invisible), but we track collisions.
GOAL_RADIUS_M = 0.15
GOAL_RADIUS_PX = GOAL_RADIUS_M * SCALE

# Real-world positions of each goal (x_m, y_m):
#   name       (x_m,  y_m)
goal_definitions = [
    ("Coral",       -0.38, -0.33),
    ("Octopus",      1.19,  0.46),
    ("Scuba-diver",  0.79, -0.39),
    ("Sea-turtle",   0.34,  0.34),
    ("Seaweed",      0.23, -0.70),
    ("Shark",       -0.65, -1.09),
    ("Whale",       -0.23,  0.63),
]

# File paths to the WAV sounds (adjust if needed)
# Make sure these files exist in the specified folder.
SOUND_FOLDER = "/Volumes/ramot/sunt/Navigation/SoundNavigation/Sounds/Dor/Underwater"
BEEP_SOUND_FILE = f"{SOUND_FOLDER}/beep.wav"  # You must have a beep.wav here
# Each goal's WAV must match the name exactly or be customized below:
goal_sound_files = {
    "Coral":       f"{SOUND_FOLDER}/Coral.wav",
    "Octopus":     f"{SOUND_FOLDER}/Octopus.wav",
    "Scuba-diver": f"{SOUND_FOLDER}/ScubaDiver.wav",
    "Sea-turtle":  f"{SOUND_FOLDER}/SeaTurtle.wav",
    "Seaweed":     f"{SOUND_FOLDER}/SeaWeed.wav",
    "Shark":       f"{SOUND_FOLDER}/Shark.wav",
    "Whale":       f"{SOUND_FOLDER}/Whale.wav",
}

# ------------------------------------------------------------------
# 2) SETUP PYGAME
# ------------------------------------------------------------------

pygame.init()
pygame.mixer.init()  # for sounds

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3.3m-Diameter Arena with Invisible Goals")
clock = pygame.time.Clock()

# Load sounds
beep_sound = pygame.mixer.Sound(BEEP_SOUND_FILE)
beep_sound.set_volume(1.0)  # volume 0.0 ~ 1.0

# Load each goal's sound
goal_sounds = {}
for name, path in goal_sound_files.items():
    snd = pygame.mixer.Sound(path)
    snd.set_volume(1.0)
    goal_sounds[name] = snd

# ------------------------------------------------------------------
# 3) DATA STRUCTURES
# ------------------------------------------------------------------

# Convert each goal to a dictionary with pixel position, name, etc.
def meters_to_pixels(x_m, y_m):
    """Convert from (x_m, y_m) in meters to (x_px, y_px) in pixels,
    placing (0,0) in the center of the arena and flipping y to match
    Pygame's downward axis."""
    x_px = ARENA_CENTER_PX[0] + int(SCALE * x_m)
    y_px = ARENA_CENTER_PX[1] - int(SCALE * y_m)
    return (x_px, y_px)

goals = []
for (name, gx_m, gy_m) in goal_definitions:
    goals.append({
        "name": name,
        "pos_m": (gx_m, gy_m),
        "pos_px": meters_to_pixels(gx_m, gy_m),
        "in_range": False,  # track if avatar is currently in this goal
    })

# Avatar state (in meters, angle in degrees)
avatar_x_m = 0.0
avatar_y_m = 0.0
avatar_angle_deg = 0.0

# To track beep looping
beep_playing = False

# For delta-time
last_time = pygame.time.get_ticks()

# ------------------------------------------------------------------
# 4) HELPER FUNCTIONS
# ------------------------------------------------------------------

def distance_m(x1, y1, x2, y2):
    """Euclidean distance in meters (since x,y are in meters)."""
    return math.hypot(x2 - x1, y2 - y1)

def distance_px(x1, y1, x2, y2):
    """Euclidean distance in pixels."""
    return math.hypot(x2 - x1, y2 - y1)

def draw_arena():
    """Draw the circular arena boundary in white."""
    pygame.draw.circle(screen, (255, 255, 255), ARENA_CENTER_PX, ARENA_RADIUS_PX, 2)

def draw_avatar():
    """Draw the triangular avatar based on its position (in meters) and angle (in degrees)."""
    # Convert avatar center from meters to pixels
    center_px = meters_to_pixels(avatar_x_m, avatar_y_m)
    angle_rad = math.radians(avatar_angle_deg)

    # Tip of the triangle (in front)
    tip_x = center_px[0] + AVATAR_RADIUS_PX * math.cos(angle_rad)
    tip_y = center_px[1] + AVATAR_RADIUS_PX * math.sin(angle_rad)

    # Two other corners, offset by ±140° from the tip
    left_angle = angle_rad + math.radians(140)
    right_angle = angle_rad - math.radians(140)

    left_x = center_px[0] + (AVATAR_RADIUS_PX * 0.8) * math.cos(left_angle)
    left_y = center_px[1] + (AVATAR_RADIUS_PX * 0.8) * math.sin(left_angle)

    right_x = center_px[0] + (AVATAR_RADIUS_PX * 0.8) * math.cos(right_angle)
    right_y = center_px[1] + (AVATAR_RADIUS_PX * 0.8) * math.sin(right_angle)

    pygame.draw.polygon(
        screen,
        (255, 0, 0),  # red
        [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]
    )

def is_on_border(x_m, y_m):
    """Return True if the avatar is at or beyond the arena boundary."""
    dist_from_center = distance_m(0.0, 0.0, x_m, y_m)
    # If the avatar's center + its radius is at least the arena radius, we consider it on the border
    return (dist_from_center + AVATAR_RADIUS_M) >= ARENA_RADIUS_M

# ------------------------------------------------------------------
# 5) MAIN LOOP
# ------------------------------------------------------------------

running = True
while running:
    # Calculate delta-time (in seconds) for smooth movement
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0
    last_time = current_time

    # Limit FPS to ~60
    clock.tick(60)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read keys
    keys = pygame.key.get_pressed()

    # Rotation (left/right)
    rotation_dir = 0.0
    if keys[pygame.K_LEFT]:
        # Rotate left (counterclockwise)
        rotation_dir = -1.0
    elif keys[pygame.K_RIGHT]:
        # Rotate right (clockwise)
        rotation_dir = 1.0

    avatar_angle_deg += rotation_dir * AVATAR_ROT_SPEED_DEG_S * dt
    avatar_angle_deg %= 360.0

    # Movement (up/down)
    move_dir = 0.0
    if keys[pygame.K_UP]:
        move_dir = 1.0
    elif keys[pygame.K_DOWN]:
        move_dir = -1.0

    # Move in the direction of avatar_angle_deg
    angle_rad = math.radians(avatar_angle_deg)
    proposed_x_m = avatar_x_m + move_dir * AVATAR_SPEED_M_S * dt * math.cos(angle_rad)
    proposed_y_m = avatar_y_m + move_dir * AVATAR_SPEED_M_S * dt * math.sin(angle_rad)

    # Check if staying in the arena
    dist_from_center = distance_m(0, 0, proposed_x_m, proposed_y_m)
    if dist_from_center + AVATAR_RADIUS_M <= ARENA_RADIUS_M:
        # Accept the move
        avatar_x_m = proposed_x_m
        avatar_y_m = proposed_y_m

    # Check border beep
    if is_on_border(avatar_x_m, avatar_y_m):
        # If not playing yet, start beep in a loop
        if not beep_playing:
            beep_sound.play(loops=-1)
            beep_playing = True
    else:
        # If we were playing, stop
        if beep_playing:
            beep_sound.stop()
            beep_playing = False

    # Check collisions with goals (they are invisible but we detect them)
    for goal in goals:
        gx_m, gy_m = goal["pos_m"]
        d = distance_m(avatar_x_m, avatar_y_m, gx_m, gy_m)
        # If inside the goal circle: radius = 0.15m + the avatar radius
        if d <= (GOAL_RADIUS_M + AVATAR_RADIUS_M):
            # We have "entered" this goal region
            if not goal["in_range"]:
                # Just now entered, play the goal sound once
                goal_sounds[goal["name"]].play()
                goal["in_range"] = True
        else:
            # Outside the goal region
            goal["in_range"] = False

    # Render
    screen.fill((0, 0, 0))  # black background
    draw_arena()
    draw_avatar()
    # The goals are invisible, so do NOT draw them.

    pygame.display.flip()

# Cleanup
beep_sound.stop()
pygame.quit()
