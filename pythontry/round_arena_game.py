import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Round Arena Goal Game")
clock = pygame.time.Clock()

# Arena settings
arena_center = (WIDTH // 2, HEIGHT // 2)
arena_radius = 250

# Avatar settings
avatar_pos = [arena_center[0], arena_center[1]]
avatar_angle = 0  # In degrees. 0 degrees points to the right.
avatar_speed = 3
rotation_speed = 3  # Degrees per frame
avatar_size = 15  # Length from center to tip of the triangle

# Goal settings
goal_radius = 10

def random_position_in_arena():
    """Generate a random (x, y) inside the arena circle."""
    angle = random.uniform(0, 2 * math.pi)
    # Use square root to ensure a uniform distribution in the circle
    r = arena_radius * math.sqrt(random.uniform(0, 1))
    x = arena_center[0] + r * math.cos(angle)
    y = arena_center[1] + r * math.sin(angle)
    return (x, y)

goal_pos = random_position_in_arena()

# Score
score = 0
font = pygame.font.SysFont(None, 36)

def draw_arena():
    # Draw the circular arena boundary
    pygame.draw.circle(screen, (255, 255, 255), arena_center, arena_radius, 2)

def draw_goal():
    pygame.draw.circle(screen, (0, 255, 0), (int(goal_pos[0]), int(goal_pos[1])), goal_radius)

def draw_avatar():
    # Compute the triangle's points based on the avatar's position and angle.
    angle_rad = math.radians(avatar_angle)
    tip = (avatar_pos[0] + avatar_size * math.cos(angle_rad),
           avatar_pos[1] + avatar_size * math.sin(angle_rad))
    
    # Calculate the two base points for the triangle, offset by ±140°
    left_angle = math.radians(avatar_angle + 140)
    right_angle = math.radians(avatar_angle - 140)
    left_point = (avatar_pos[0] + avatar_size * 0.8 * math.cos(left_angle),
                  avatar_pos[1] + avatar_size * 0.8 * math.sin(left_angle))
    right_point = (avatar_pos[0] + avatar_size * 0.8 * math.cos(right_angle),
                   avatar_pos[1] + avatar_size * 0.8 * math.sin(right_angle))
    
    pygame.draw.polygon(screen, (255, 0, 0), [tip, left_point, right_point])

def draw_score():
    score_text = font.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (10, 10))

def within_arena(new_pos):
    # Ensure the avatar remains within the arena boundaries.
    dist = math.hypot(new_pos[0] - arena_center[0], new_pos[1] - arena_center[1])
    return dist <= arena_radius - avatar_size

running = True
while running:
    clock.tick(60)  # Run at 60 frames per second

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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

    # Updated rotation: left arrow rotates counterclockwise, right arrow rotates clockwise.
    if keys[pygame.K_LEFT]:
        avatar_angle = (avatar_angle - rotation_speed) % 360
    if keys[pygame.K_RIGHT]:
        avatar_angle = (avatar_angle + rotation_speed) % 360

    # Check collision with the goal (using a simple distance check)
    if math.hypot(avatar_pos[0] - goal_pos[0], avatar_pos[1] - goal_pos[1]) < (goal_radius + avatar_size / 2):
        score += 1
        goal_pos = random_position_in_arena()

    # Drawing section
    screen.fill((0, 0, 0))  # Clear the screen with black
    draw_arena()
    draw_goal()
    draw_avatar()
    draw_score()
    pygame.display.flip()

pygame.quit()
