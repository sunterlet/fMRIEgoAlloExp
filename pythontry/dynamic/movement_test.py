import pygame
import math
import time
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Movement Test")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player settings
player_pos = [WIDTH // 2, HEIGHT // 2]
player_angle = 0
player_speed = 3
rotation_speed = 3

# Target settings
target_radius = 10
target_placed = False
target_position = None
target_placement_time = time.time() + random.uniform(2, 5)  # Shorter delay for testing

# Movement tracking
has_moved_forward = False
has_rotated = False
is_moving_forward_backward = False
is_rotating = False

def draw_player():
    # Draw player as a triangle
    points = [
        (player_pos[0] + 20 * math.cos(math.radians(player_angle)),
         player_pos[1] + 20 * math.sin(math.radians(player_angle))),
        (player_pos[0] + 10 * math.cos(math.radians(player_angle + 120)),
         player_pos[1] + 10 * math.sin(math.radians(player_angle + 120))),
        (player_pos[0] + 10 * math.cos(math.radians(player_angle - 120)),
         player_pos[1] + 10 * math.sin(math.radians(player_angle - 120)))
    ]
    pygame.draw.polygon(screen, BLUE, points)

def draw_target():
    if target_placed and target_position:
        pygame.draw.circle(screen, GREEN, target_position, target_radius)

def draw_conditions():
    font = pygame.font.SysFont(None, 24)
    y = 20
    
    conditions = {
        "Time elapsed": time.time() >= target_placement_time,
        "Moved forward": has_moved_forward,
        "Rotated": has_rotated,
        "Moving forward/backward": is_moving_forward_backward,
        "Not rotating": not is_rotating
    }
    
    for condition, met in conditions.items():
        color = GREEN if met else RED
        text = f"{condition}: {'✓' if met else '✗'}"
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (20, y))
        y += 30

def check_target_placement():
    global target_placed, target_position
    if (not target_placed and 
        time.time() >= target_placement_time and 
        has_moved_forward and 
        has_rotated and 
        is_moving_forward_backward and 
        not is_rotating):
        target_position = (int(player_pos[0]), int(player_pos[1]))
        target_placed = True
        return target_position
    return None

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get keyboard state
    keys = pygame.key.get_pressed()
    
    # Update movement states
    is_moving_forward_backward = keys[pygame.K_UP] or keys[pygame.K_DOWN]
    is_rotating = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
    
    # Handle movement
    if keys[pygame.K_UP]:
        has_moved_forward = True
        player_pos[0] += player_speed * math.cos(math.radians(player_angle))
        player_pos[1] += player_speed * math.sin(math.radians(player_angle))
    if keys[pygame.K_DOWN]:
        player_pos[0] -= player_speed * math.cos(math.radians(player_angle))
        player_pos[1] -= player_speed * math.sin(math.radians(player_angle))
    if keys[pygame.K_LEFT]:
        has_rotated = True
        player_angle -= rotation_speed
    if keys[pygame.K_RIGHT]:
        has_rotated = True
        player_angle += rotation_speed
    
    # Check for target placement
    new_target = check_target_placement()
    if new_target:
        target_position = new_target
    
    # Draw everything
    screen.fill(BLACK)
    draw_player()
    draw_target()
    draw_conditions()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()