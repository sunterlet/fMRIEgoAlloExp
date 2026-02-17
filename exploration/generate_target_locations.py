import random
import math
import json
import sys
import os
import csv

# Import pygame only when needed (for visualization)
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Visualization will be disabled.")

# Arena parameters (in meters)
# NOTE: These values must match multi_arena.py to ensure generated targets
# are correctly sized and non-overlapping in the actual experiment
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
TARGET_RADIUS = 0.25  # Match multi_arena.py target radius (line 86)
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

def generate_target_locations(num_targets, min_distance=0.55):
    """
    Generate random target locations that don't overlap with each other,
    the center, or the border. Ensures at least one target in each quartile.
    
    Args:
        num_targets: Number of targets to generate
        min_distance: Minimum distance between target centers (default 0.55m ensures
                     no overlap for targets with radius 0.25m, with small buffer)
    
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
    if not PYGAME_AVAILABLE:
        print("Error: pygame is required for visualization but is not installed.")
        return
    
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

def load_arenas_csv(csv_path):
    """Load arena data from CSV file and group by theme."""
    arenas = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            theme = row['theme']
            if theme not in arenas:
                arenas[theme] = []
            arenas[theme].append({
                'target': row['target'],
                'hebrew_name': row['hebrew_name'],
                'hebrew_theme': row['hebrew_theme']
            })
    
    return arenas

def update_arenas_csv(csv_path, arenas_with_coords):
    """Update CSV file with new target coordinates."""
    # Prepare rows for writing
    rows = []
    for theme, targets_data in arenas_with_coords.items():
        for target_data in targets_data:
            rows.append({
                'theme': theme,
                'target': target_data['target'],
                'coords': f"({target_data['coords'][0]:.2f}; {target_data['coords'][1]:.2f})",
                'hebrew_name': target_data['hebrew_name'],
                'hebrew_theme': target_data['hebrew_theme']
            })
    
    # Write to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['theme', 'target', 'coords', 'hebrew_name', 'hebrew_theme']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def visualize_all_arenas(all_arenas):
    """Visualize all arenas with their target locations."""
    if not PYGAME_AVAILABLE:
        print("Error: pygame is required for visualization but is not installed.")
        print("Install pygame using: pip install pygame")
        return
    
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
        theme, locations = all_arenas[current_arena]
        
        # Draw target locations
        for i, loc in enumerate(locations):
            screen_pos = to_screen_coords(loc)
            # Draw target
            pygame.draw.circle(screen, TARGET_COLOR, screen_pos, int(TARGET_RADIUS * SCALE))
            # Draw target number
            font = pygame.font.SysFont("Arial", 16)
            text = font.render(str(i+1), True, WHITE)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 35))
            screen.blit(text, text_rect)
        
        # Draw coordinates
        font = pygame.font.SysFont("Arial", 12)
        for i, loc in enumerate(locations):
            text = font.render(f"({loc[0]:.2f}, {loc[1]:.2f})", True, WHITE)
            screen_pos = to_screen_coords(loc)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] + 35))
            screen.blit(text, text_rect)
        
        # Draw arena info
        font = pygame.font.SysFont("Arial", 24)
        info_text = font.render(f"Arena: {theme} ({len(locations)} targets)", True, WHITE)
        screen.blit(info_text, (20, 20))
        
        # Draw arena counter
        counter_text = font.render(f"{current_arena + 1}/{len(all_arenas)}", True, WHITE)
        screen.blit(counter_text, (20, 50))
        
        # Draw navigation instructions
        font = pygame.font.SysFont("Arial", 16)
        nav_text = font.render("Use LEFT/RIGHT arrows to navigate between arenas (ESC to exit)", True, WHITE)
        screen.blit(nav_text, (20, WIN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    import os
    
    # Path to the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), "Final111_New_Arenas.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    print(f"Loading arena data from: {csv_path}")
    arenas = load_arenas_csv(csv_path)
    
    print(f"\nFound {len(arenas)} arenas:")
    for theme, targets in arenas.items():
        print(f"  {theme}: {len(targets)} targets")
    
    # Generate new locations for each arena
    arenas_with_coords = {}
    all_arenas = []  # For visualization
    
    for theme, targets in arenas.items():
        num_targets = len(targets)
        print(f"\nGenerating {num_targets} target locations for {theme}...")
        
        # Generate new non-overlapping locations
        locations = generate_target_locations(num_targets)
        
        # Assign locations to targets
        targets_with_coords = []
        for i, target_info in enumerate(targets):
            target_info['coords'] = locations[i]
            targets_with_coords.append(target_info)
            print(f"  {target_info['target']}: ({locations[i][0]:.2f}, {locations[i][1]:.2f})")
        
        arenas_with_coords[theme] = targets_with_coords
        all_arenas.append((theme, locations))
    
    # Update the CSV file
    print(f"\nUpdating CSV file: {csv_path}")
    update_arenas_csv(csv_path, arenas_with_coords)
    print("CSV file updated successfully!")
    
    # Also save individual JSON files for backup
    output_dir = os.path.join(os.path.dirname(__file__), "arena_configs")
    os.makedirs(output_dir, exist_ok=True)
    
    for theme, locations in all_arenas:
        filename = os.path.join(output_dir, f"{theme}_locations.json")
        save_locations(locations, filename)
    
    print(f"\nBackup JSON files saved to: {output_dir}")
    
    # Ask user if they want to visualize (only if pygame is available)
    if PYGAME_AVAILABLE:
        print("\nWould you like to visualize the arenas? (y/n): ", end='')
        try:
            response = input().strip().lower()
            if response == 'y':
                visualize_all_arenas(all_arenas)
        except (KeyboardInterrupt, EOFError):
            print("\nVisualization skipped.")
    else:
        print("\nVisualization not available (pygame not installed)")
    
    print("\nDone!") 