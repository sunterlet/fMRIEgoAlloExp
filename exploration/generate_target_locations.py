import random
import math
import json
import pygame
import sys
import os

# Arena parameters (in meters)
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
TARGET_RADIUS = 0.1
BORDER_THRESHOLD = 0.1
CENTER_THRESHOLD = 0.5  # Minimum distance from center

# Visualization parameters
SCALE = 200  # pixels per meter
WIN_WIDTH = 800
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# Colors
BACKGROUND_COLOR = (3, 3, 1)        # Background: near-black
BORDER_COLOR = (255, 255, 243)      # Arena border: Ivory
TARGET_COLOR = (0, 217, 192)        # Targets: Turquoise
CENTER_COLOR = (255, 67, 101)       # Center: Folly
WHITE = (255, 255, 255)

def generate_target_locations(num_targets, min_distance=0.3):
    """
    Generate random target locations that don't overlap with each other,
    the center, or the border. Ensures at least one target in each quartile.
    
    Args:
        num_targets: Number of targets to generate
        min_distance: Minimum distance between targets
    
    Returns:
        List of (x, y) coordinates for target centers
    """
    locations = []
    max_attempts = 1000  # Prevent infinite loops
    
    # Define quartile ranges (in radians)
    quartile_ranges = [
        (0, math.pi/2),           # Q1: top-right
        (math.pi/2, math.pi),     # Q2: top-left
        (math.pi, 3*math.pi/2),   # Q3: bottom-left
        (3*math.pi/2, 2*math.pi)  # Q4: bottom-right
    ]
    
    # First, ensure one target in each quartile
    for quartile_range in quartile_ranges:
        attempts = 0
        while attempts < max_attempts:
            # Generate random angle within the quartile
            angle = random.uniform(quartile_range[0], quartile_range[1])
            # Use square root of random number to get uniform distribution in circle
            r = random.uniform(CENTER_THRESHOLD, ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD)
            
            # Calculate position
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            
            # Check if this position is valid
            valid_position = True
            
            # Check distance from center
            if math.hypot(x, y) < CENTER_THRESHOLD:
                valid_position = False
            
            # Check distance from border
            if math.hypot(x, y) > (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD):
                valid_position = False
            
            # Check distance from other targets
            for loc in locations:
                if math.hypot(x - loc[0], y - loc[1]) < min_distance:
                    valid_position = False
                    break
            
            if valid_position:
                locations.append((x, y))
                break
            
            attempts += 1
    
    # Then fill the remaining targets
    while len(locations) < num_targets:
        # Generate random angle and radius
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(CENTER_THRESHOLD, ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD)
        
        # Calculate position
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        
        # Check if this position is valid
        valid_position = True
        
        # Check distance from center
        if math.hypot(x, y) < CENTER_THRESHOLD:
            valid_position = False
        
        # Check distance from border
        if math.hypot(x, y) > (ARENA_RADIUS - TARGET_RADIUS - BORDER_THRESHOLD):
            valid_position = False
        
        # Check distance from other targets
        for loc in locations:
            if math.hypot(x - loc[0], y - loc[1]) < min_distance:
                valid_position = False
                break
        
        if valid_position:
            locations.append((x, y))
    
    return locations

def save_locations(locations, filename):
    """Save locations to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(locations, f, indent=2)

def to_screen_coords(pos):
    """Convert arena coordinates (in meters) to screen coordinates (in pixels)."""
    x, y = pos
    screen_x = CENTER_SCREEN[0] + int(x * SCALE)
    screen_y = CENTER_SCREEN[1] - int(y * SCALE)
    return (screen_x, screen_y)

def visualize_locations(locations):
    """Visualize the arena and target locations."""
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Target Locations Visualization")
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        
        # Draw arena border
        pygame.draw.circle(screen, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)
        
        # Draw center threshold
        pygame.draw.circle(screen, CENTER_COLOR, CENTER_SCREEN, int(CENTER_THRESHOLD * SCALE), 1)
        
        # Draw target locations
        for i, loc in enumerate(locations):
            screen_pos = to_screen_coords(loc)
            # Draw target
            pygame.draw.circle(screen, TARGET_COLOR, screen_pos, int(TARGET_RADIUS * SCALE))
            # Draw target number
            font = pygame.font.SysFont("Arial", 16)
            text = font.render(str(i+1), True, WHITE)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 20))
            screen.blit(text, text_rect)
        
        # Draw coordinates
        font = pygame.font.SysFont("Arial", 12)
        for i, loc in enumerate(locations):
            text = font.render(f"({loc[0]:.2f}, {loc[1]:.2f})", True, WHITE)
            screen_pos = to_screen_coords(loc)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] + 20))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    import os
    
    # Create directory if it doesn't exist
    output_dir = "/Users/sunt/PhD/packngo/FullArena/Arenas"
    os.makedirs(output_dir, exist_ok=True)
    
    # Store all generated arenas
    all_arenas = []
    
    # Generate 3 arenas with 5 targets
    for i in range(3):
        locations = generate_target_locations(5)
        filename = os.path.join(output_dir, f"arena_5targets_{i+1}.json")
        save_locations(locations, filename)
        print(f"\nGenerated arena {i+1} with 5 targets:")
        for j, loc in enumerate(locations):
            print(f"Target {j+1}: ({loc[0]:.3f}, {loc[1]:.3f})")
        all_arenas.append(("5 targets", i+1, locations))
    
    # Generate 3 arenas with 7 targets
    for i in range(3):
        locations = generate_target_locations(7)
        filename = os.path.join(output_dir, f"arena_7targets_{i+1}.json")
        save_locations(locations, filename)
        print(f"\nGenerated arena {i+1} with 7 targets:")
        for j, loc in enumerate(locations):
            print(f"Target {j+1}: ({loc[0]:.3f}, {loc[1]:.3f})")
        all_arenas.append(("7 targets", i+1, locations))
    
    # Visualize all arenas sequentially
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Target Locations Visualization")
    clock = pygame.time.Clock()
    
    current_arena = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    current_arena = (current_arena + 1) % len(all_arenas)
                elif event.key == pygame.K_LEFT:
                    current_arena = (current_arena - 1) % len(all_arenas)
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        
        # Draw arena border
        pygame.draw.circle(screen, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)
        
        # Draw center threshold
        pygame.draw.circle(screen, CENTER_COLOR, CENTER_SCREEN, int(CENTER_THRESHOLD * SCALE), 1)
        
        # Get current arena info
        target_type, arena_num, locations = all_arenas[current_arena]
        
        # Draw target locations
        for i, loc in enumerate(locations):
            screen_pos = to_screen_coords(loc)
            # Draw target
            pygame.draw.circle(screen, TARGET_COLOR, screen_pos, int(TARGET_RADIUS * SCALE))
            # Draw target number
            font = pygame.font.SysFont("Arial", 16)
            text = font.render(str(i+1), True, WHITE)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 20))
            screen.blit(text, text_rect)
        
        # Draw coordinates
        font = pygame.font.SysFont("Arial", 12)
        for i, loc in enumerate(locations):
            text = font.render(f"({loc[0]:.2f}, {loc[1]:.2f})", True, WHITE)
            screen_pos = to_screen_coords(loc)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] + 20))
            screen.blit(text, text_rect)
        
        # Draw arena info
        font = pygame.font.SysFont("Arial", 24)
        info_text = font.render(f"Arena {arena_num} ({target_type})", True, WHITE)
        screen.blit(info_text, (20, 20))
        
        # Draw navigation instructions
        font = pygame.font.SysFont("Arial", 16)
        nav_text = font.render("Use LEFT/RIGHT arrows to navigate between arenas", True, WHITE)
        screen.blit(nav_text, (20, WIN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit() 