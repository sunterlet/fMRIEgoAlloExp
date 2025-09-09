import pygame
import math
import sys

# ----- Configuration -----
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3          # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0  # 1.65 m

# Target parameters
TARGET_CENTER = (-0.65, -1.09)  # in meters, relative to arena center
TARGET_DIAMETER = 0.30         # m
TARGET_RADIUS = TARGET_DIAMETER / 2.0  # 0.15 m

# Player parameters for navigation phase
START_POS = (0.0, 0.0)
START_ANGLE = 0.0            # radians (0 rad = facing "up" on screen)

# Movement speeds
MOVE_SPEED = 1.0             # meters per second
ROTATE_SPEED = math.radians(90)  # 90 degrees per second (in radians)

# Overhead map scaling (pixels per meter)
SCALE = 200                  # so arena diameter in pixels = 3.3*200 = 660 pixels

# Screen sizes for each phase
NAV_WIDTH, NAV_HEIGHT = 800, 600  # navigation phase window
MAP_WIDTH, MAP_HEIGHT = 800, 800  # overhead map window

# Sound file paths
SOUND_SHARK_PATH = "/Volumes/ramot/sunt/Navigation/SoundNavigation/Sounds/Dor/Underwater/Shark.wav"
SOUND_BEEP_PATH = "/Volumes/ramot/sunt/Navigation/SoundNavigation/Sounds/Dor/Underwater/beep.wav"

# ----- Initialize Pygame -----
pygame.init()
pygame.mixer.init()

# Create window for navigation phase
screen = pygame.display.set_mode((NAV_WIDTH, NAV_HEIGHT))
pygame.display.set_caption("Navigation Phase")

clock = pygame.time.Clock()

# Load sounds
try:
    shark_sound = pygame.mixer.Sound(SOUND_SHARK_PATH)
    beep_sound = pygame.mixer.Sound(SOUND_BEEP_PATH)
except Exception as e:
    print("Error loading sound files:", e)
    sys.exit(1)

# Dedicated channel for beep sound
beep_channel = pygame.mixer.Channel(0)

# ----- Game State Variables -----
phase = "navigation"  # "navigation" or "annotation" or "feedback"

# Player state in navigation phase (position in meters, angle in radians)
player_x, player_y = START_POS
player_angle = START_ANGLE

# Flag to ensure target (Shark) sound is played only once
shark_sound_played = False

# In annotation phase, the guess marker starts at center of arena
guess_x, guess_y = 0.0, 0.0

# ----- Helper Functions -----
def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def update_navigation(dt):
    global player_x, player_y, player_angle, shark_sound_played

    keys = pygame.key.get_pressed()
    # Rotation: left/right arrows
    if keys[pygame.K_LEFT]:
        player_angle -= ROTATE_SPEED * dt
    if keys[pygame.K_RIGHT]:
        player_angle += ROTATE_SPEED * dt

    # Movement: up/down arrows (move along current facing direction)
    dx = math.sin(player_angle) * MOVE_SPEED * dt
    dy = -math.cos(player_angle) * MOVE_SPEED * dt

    # Calculate potential new position
    new_x, new_y = player_x, player_y
    if keys[pygame.K_UP]:
        new_x += dx
        new_y += dy
    if keys[pygame.K_DOWN]:
        new_x -= dx
        new_y -= dy

    # Clamp new position to arena boundary if necessary
    r = math.hypot(new_x, new_y)
    if r > ARENA_RADIUS:
        angle = math.atan2(new_y, new_x)
        new_x = ARENA_RADIUS * math.cos(angle)
        new_y = ARENA_RADIUS * math.sin(angle)

    player_x, player_y = new_x, new_y

    # Check if player is in target region (play Shark sound once)
    if not shark_sound_played:
        if distance(player_x, player_y, TARGET_CENTER[0], TARGET_CENTER[1]) <= TARGET_RADIUS:
            shark_sound.play()
            shark_sound_played = True

    # Border beep handling: if player's position is essentially on the border, play beep continuously.
    if math.isclose(math.hypot(player_x, player_y), ARENA_RADIUS, rel_tol=1e-5):
        if not beep_channel.get_busy():
            beep_channel.play(beep_sound, loops=-1)
    else:
        if beep_channel.get_busy():
            beep_channel.stop()

def draw_navigation():
    # Draw a top-down view for the navigation phase.
    screen.fill((50, 50, 50))
    center = (NAV_WIDTH // 2, NAV_HEIGHT // 2)
    
    # Draw arena circle
    arena_radius_px = int(ARENA_RADIUS * SCALE)
    pygame.draw.circle(screen, (200, 200, 200), center, arena_radius_px, 2)
    
    # Draw target (blue filled circle)
    target_px = center[0] + int(TARGET_CENTER[0] * SCALE)
    target_py = center[1] - int(TARGET_CENTER[1] * SCALE)
    pygame.draw.circle(screen, (0, 100, 200), (target_px, target_py), int(TARGET_RADIUS * SCALE))
    
    # Draw player's avatar (as an arrow triangle)
    player_px = center[0] + int(player_x * SCALE)
    player_py = center[1] - int(player_y * SCALE)
    
    # Compute the forward vector (0 rad means upward)
    forward = (math.sin(player_angle), -math.cos(player_angle))
    tip_length = 15  # in pixels
    base_length = 5  # offset behind the player's position
    half_width = 5   # half the width of the base
    
    tip = (player_px + tip_length * forward[0],
           player_py + tip_length * forward[1])
    
    # Base center (a little behind the player's current position)
    base_center = (player_px - base_length * forward[0],
                   player_py - base_length * forward[1])
    
    # Perpendicular vector for the base (rotate forward by 90° clockwise)
    perp = (math.cos(player_angle), math.sin(player_angle))
    left_base = (base_center[0] + half_width * perp[0],
                 base_center[1] + half_width * perp[1])
    right_base = (base_center[0] - half_width * perp[0],
                  base_center[1] - half_width * perp[1])
    
    pygame.draw.polygon(screen, (255, 0, 0), [tip, left_base, right_base])
    
    # Display instructions and current position
    font = pygame.font.SysFont(None, 28)
    instruct_text = font.render("Navigation Phase: Use arrow keys. Press Enter to mark target location.", True, (255, 255, 255))
    pos_text = font.render(f"Pos: ({player_x:.2f}, {player_y:.2f})", True, (255, 255, 255))
    screen.blit(instruct_text, (20, 20))
    screen.blit(pos_text, (20, 50))
    
    pygame.display.flip()

def run_navigation_phase():
    global phase
    running = True
    while running and phase == "navigation":
        dt = clock.tick(60) / 1000.0  # seconds since last frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Transition to annotation phase on Enter key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    phase = "annotation"
                    running = False

        update_navigation(dt)
        draw_navigation()

def draw_overhead_map(guess_x, guess_y, show_target=False):
    """
    Draw the overhead map for annotation and feedback.
    If show_target is False, the actual target is hidden.
    """
    screen.fill((30, 30, 30))
    center = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
    # Draw arena circle
    pygame.draw.circle(screen, (200, 200, 200), center, int(ARENA_RADIUS * SCALE), 2)
    
    # Optionally draw the actual target (only during feedback)
    if show_target:
        target_px = center[0] + int(TARGET_CENTER[0] * SCALE)
        target_py = center[1] - int(TARGET_CENTER[1] * SCALE)
        pygame.draw.circle(screen, (0, 100, 200), (target_px, target_py), int(TARGET_RADIUS * SCALE))
    
    # Draw guess marker (red cross)
    guess_px = center[0] + int(guess_x * SCALE)
    guess_py = center[1] - int(guess_y * SCALE)
    marker_size = 10
    pygame.draw.line(screen, (255, 0, 0), (guess_px - marker_size, guess_py), (guess_px + marker_size, guess_py), 2)
    pygame.draw.line(screen, (255, 0, 0), (guess_px, guess_py - marker_size), (guess_px, guess_py + marker_size), 2)
    
    font = pygame.font.SysFont(None, 28)
    instruct_text = font.render("Annotation Phase: Move marker with arrow keys. Press Enter to finalize guess.", True, (255, 255, 255))
    screen.blit(instruct_text, (20, 20))
    
    pygame.display.flip()

def run_annotation_phase():
    global phase, guess_x, guess_y
    # Switch to annotation phase window size.
    pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
    pygame.display.set_caption("Annotation Phase (Overhead Map)")
    
    running = True
    while running and phase == "annotation":
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    phase = "feedback"
                    running = False
        
        keys = pygame.key.get_pressed()
        guess_speed = 1.0  # m/s for marker movement
        if keys[pygame.K_LEFT]:
            guess_x -= guess_speed * dt
        if keys[pygame.K_RIGHT]:
            guess_x += guess_speed * dt
        if keys[pygame.K_UP]:
            guess_y += guess_speed * dt   # Up arrow moves marker upward (in our coordinate system)
        if keys[pygame.K_DOWN]:
            guess_y -= guess_speed * dt
        
        # Clamp the guess marker within the arena circle.
        r = math.hypot(guess_x, guess_y)
        if r > ARENA_RADIUS:
            angle = math.atan2(guess_y, guess_x)
            guess_x = ARENA_RADIUS * math.cos(angle)
            guess_y = ARENA_RADIUS * math.sin(angle)
        
        draw_overhead_map(guess_x, guess_y, show_target=False)

def run_feedback_phase():
    # Calculate error distance (in meters) between guess and actual target.
    error = distance(guess_x, guess_y, TARGET_CENTER[0], TARGET_CENTER[1])
    
    # First, draw the overhead map with the actual target shown.
    draw_overhead_map(guess_x, guess_y, show_target=True)
    
    # Then, overlay feedback information.
    font = pygame.font.SysFont(None, 36)
    feedback_text = font.render(f"Your guess was off by {error:.2f} meters.", True, (255, 255, 255))
    instructions = font.render("Press Esc or close window to exit.", True, (255, 255, 255))
    screen.blit(feedback_text, (50, MAP_HEIGHT // 2 - 20))
    screen.blit(instructions, (50, MAP_HEIGHT // 2 + 20))
    pygame.display.flip()
    
    # Wait for the player to exit.
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

# ----- Main Loop -----
if __name__ == "__main__":
    run_navigation_phase()
    run_annotation_phase()
    run_feedback_phase()
