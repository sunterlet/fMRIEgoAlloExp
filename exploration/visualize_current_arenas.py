#!/usr/bin/env python3
"""
Visualize the current arena configurations from Final111_New_Arenas.csv
"""
import pygame
import sys
import os
import csv
import math

# Try to import svgwrite for vector graphics
try:
    import svgwrite
    SVGWRITE_AVAILABLE = True
except ImportError:
    SVGWRITE_AVAILABLE = False
    print("Note: svgwrite not available. SVG export disabled.")

# Arena parameters (in meters)
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
TARGET_RADIUS = 0.25  # Match multi_arena.py
BORDER_THRESHOLD = 0.1
CENTER_THRESHOLD = 0.5

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

def to_screen_coords(pos):
    """Convert arena coordinates (in meters) to screen coordinates (in pixels)."""
    x, y = pos
    screen_x = CENTER_SCREEN[0] + int(x * SCALE)
    screen_y = CENTER_SCREEN[1] - int(y * SCALE)
    return (screen_x, screen_y)

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def svg_to_screen_coords(pos):
    """Convert arena coordinates to SVG screen coordinates."""
    x, y = pos
    screen_x = CENTER_SCREEN[0] + x * SCALE
    screen_y = CENTER_SCREEN[1] - y * SCALE
    return (screen_x, screen_y)

def load_arenas_from_csv(csv_path):
    """Load arena data from CSV file."""
    arenas = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            theme = row['theme']
            if theme not in arenas:
                arenas[theme] = {
                    'targets': [],
                    'hebrew_theme': row['hebrew_theme']
                }
            
            # Parse coordinates from string format "(x; y)"
            coords = row['coords'].strip('()').split(';')
            x, y = float(coords[0]), float(coords[1])
            
            arenas[theme]['targets'].append({
                'name': row['target'],
                'hebrew_name': row['hebrew_name'],
                'coords': (x, y)
            })
    
    return arenas

def visualize_arenas(arenas):
    """Visualize all arenas with their target locations."""
    pygame.init()
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Arena Target Locations Visualization")
    clock = pygame.time.Clock()
    
    # Convert to list for easy navigation
    arena_list = [(name, data) for name, data in arenas.items()]
    current_arena = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
                    current_arena = (current_arena + 1) % len(arena_list)
                elif event.key == pygame.K_LEFT:
                    current_arena = (current_arena - 1) % len(arena_list)
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        
        # Draw arena border
        pygame.draw.circle(screen, BORDER_COLOR, CENTER_SCREEN, int(ARENA_RADIUS * SCALE), 2)
        
        # Draw center threshold
        pygame.draw.circle(screen, CENTER_COLOR, CENTER_SCREEN, int(CENTER_THRESHOLD * SCALE), 1)
        
        # Get current arena info
        theme, arena_data = arena_list[current_arena]
        targets = arena_data['targets']
        hebrew_theme = arena_data['hebrew_theme']
        
        # Draw target locations
        for i, target_data in enumerate(targets):
            coords = target_data['coords']
            screen_pos = to_screen_coords(coords)
            
            # Draw target circle
            pygame.draw.circle(screen, TARGET_COLOR, screen_pos, int(TARGET_RADIUS * SCALE))
            
            # Draw target number
            font = pygame.font.SysFont("Arial", 16, bold=True)
            text = font.render(str(i+1), True, WHITE)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 60))
            screen.blit(text, text_rect)
            
            # Draw target name (English)
            font_small = pygame.font.SysFont("Arial", 12)
            name_text = font_small.render(target_data['name'], True, WHITE)
            name_rect = name_text.get_rect(center=(screen_pos[0], screen_pos[1] - 42))
            screen.blit(name_text, name_rect)
            
            # Draw coordinates
            coord_text = font_small.render(f"({coords[0]:.2f}, {coords[1]:.2f})", True, WHITE)
            coord_rect = coord_text.get_rect(center=(screen_pos[0], screen_pos[1] + 60))
            screen.blit(coord_text, coord_rect)
        
        # Draw arena info at top
        font_title = pygame.font.SysFont("Arial", 32, bold=True)
        title_text = font_title.render(f"{theme.upper()}", True, TARGET_COLOR)
        screen.blit(title_text, (20, 20))
        
        # Draw Hebrew theme name
        font_hebrew = pygame.font.SysFont("Arial", 24)
        hebrew_text = font_hebrew.render(f"{hebrew_theme}", True, WHITE)
        screen.blit(hebrew_text, (20, 60))
        
        # Draw arena counter
        font_counter = pygame.font.SysFont("Arial", 20)
        counter_text = font_counter.render(f"Arena {current_arena + 1}/{len(arena_list)}", True, WHITE)
        screen.blit(counter_text, (20, 90))
        
        # Draw target count
        target_count_text = font_counter.render(f"Targets: {len(targets)}", True, WHITE)
        screen.blit(target_count_text, (20, 115))
        
        # Draw navigation instructions at bottom
        font_nav = pygame.font.SysFont("Arial", 16)
        nav_text = font_nav.render("LEFT/RIGHT arrows or SPACE to navigate | ESC or Q to exit", True, WHITE)
        screen.blit(nav_text, (WIN_WIDTH//2 - 320, WIN_HEIGHT - 30))
        
        # Calculate and display minimum distance between targets
        min_dist = float('inf')
        for i, t1 in enumerate(targets):
            for j, t2 in enumerate(targets):
                if i < j:
                    dist = math.hypot(t1['coords'][0] - t2['coords'][0], 
                                     t1['coords'][1] - t2['coords'][1])
                    min_dist = min(min_dist, dist)
        
        # Draw min distance info
        min_dist_text = font_nav.render(f"Min distance: {min_dist:.2f}m", True, WHITE)
        screen.blit(min_dist_text, (WIN_WIDTH - 200, 20))
        
        # Check if any targets overlap
        overlap_warning = ""
        if min_dist < 0.5:
            overlap_warning = "WARNING: TARGETS OVERLAP!"
            warning_text = font_nav.render(overlap_warning, True, (255, 0, 0))
            screen.blit(warning_text, (WIN_WIDTH - 250, 45))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def save_garden_arena_as_svg(arenas, output_path):
    """Save the garden arena as a true vector SVG file."""
    if not SVGWRITE_AVAILABLE:
        print("Error: svgwrite not available. Cannot save SVG.")
        return False
    
    if 'garden' not in arenas:
        print("Error: Garden arena not found in loaded data.")
        return False
    
    try:
        garden_data = arenas['garden']
        targets = garden_data['targets']
        
        # Create SVG drawing
        dwg = svgwrite.Drawing(output_path, size=(f'{WIN_WIDTH}px', f'{WIN_HEIGHT}px'))
        
        # Set background
        dwg.add(dwg.rect(insert=(0, 0), size=(f'{WIN_WIDTH}px', f'{WIN_HEIGHT}px'),
                        fill=rgb_to_hex(BACKGROUND_COLOR)))
        
        # Draw arena border
        dwg.add(dwg.circle(center=(CENTER_SCREEN[0], CENTER_SCREEN[1]),
                          r=int(ARENA_RADIUS * SCALE),
                          fill='none',
                          stroke=rgb_to_hex(BORDER_COLOR),
                          stroke_width=2))
        
        # Draw center threshold circle
        dwg.add(dwg.circle(center=(CENTER_SCREEN[0], CENTER_SCREEN[1]),
                          r=int(CENTER_THRESHOLD * SCALE),
                          fill='none',
                          stroke=rgb_to_hex(CENTER_COLOR),
                          stroke_width=1))
        
        # Draw all targets
        for i, target_data in enumerate(targets):
            coords = target_data['coords']
            screen_pos = svg_to_screen_coords(coords)
            
            # Draw target circle
            dwg.add(dwg.circle(center=(screen_pos[0], screen_pos[1]),
                              r=int(TARGET_RADIUS * SCALE),
                              fill=rgb_to_hex(TARGET_COLOR)))
            
            # Draw target number as text
            dwg.add(dwg.text(str(i+1),
                            insert=(screen_pos[0], screen_pos[1] - 60),
                            fill=rgb_to_hex(WHITE),
                            font_size='16px',
                            font_family='Arial',
                            font_weight='bold',
                            text_anchor='middle'))
            
            # Draw target name (English)
            dwg.add(dwg.text(target_data['name'],
                            insert=(screen_pos[0], screen_pos[1] - 42),
                            fill=rgb_to_hex(WHITE),
                            font_size='12px',
                            font_family='Arial',
                            text_anchor='middle'))
            
            # Draw coordinates
            coord_text = f"({coords[0]:.2f}, {coords[1]:.2f})"
            dwg.add(dwg.text(coord_text,
                            insert=(screen_pos[0], screen_pos[1] + 60),
                            fill=rgb_to_hex(WHITE),
                            font_size='12px',
                            font_family='Arial',
                            text_anchor='middle'))
        
        # Draw arena title
        dwg.add(dwg.text('GARDEN',
                        insert=(20, 50),
                        fill=rgb_to_hex(TARGET_COLOR),
                        font_size='32px',
                        font_family='Arial',
                        font_weight='bold'))
        
        # Draw Hebrew theme name
        hebrew_theme = garden_data['hebrew_theme']
        dwg.add(dwg.text(hebrew_theme,
                        insert=(20, 84),
                        fill=rgb_to_hex(WHITE),
                        font_size='24px',
                        font_family='Arial'))
        
        # Draw target count
        dwg.add(dwg.text(f'Targets: {len(targets)}',
                        insert=(20, 139),
                        fill=rgb_to_hex(WHITE),
                        font_size='20px',
                        font_family='Arial'))
        
        # Calculate and display minimum distance
        min_dist = float('inf')
        for i, t1 in enumerate(targets):
            for j, t2 in enumerate(targets):
                if i < j:
                    dist = math.hypot(t1['coords'][0] - t2['coords'][0],
                                     t1['coords'][1] - t2['coords'][1])
                    min_dist = min(min_dist, dist)
        
        dwg.add(dwg.text(f'Min distance: {min_dist:.2f}m',
                        insert=(WIN_WIDTH - 200, 36),
                        fill=rgb_to_hex(WHITE),
                        font_size='16px',
                        font_family='Arial'))
        
        # Save SVG file
        dwg.save()
        print(f"Garden arena saved as SVG: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error saving SVG: {e}")
        return False

if __name__ == "__main__":
    # Path to the CSV file - use absolute path
    csv_path = "/Volumes/ramot/sunt/Navigation/fMRI/exploration/Final111_New_Arenas.csv"
    
    # Fallback to relative path if absolute doesn't exist
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "Final111_New_Arenas.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    print(f"Loading arena data from: {csv_path}")
    arenas = load_arenas_from_csv(csv_path)
    
    print(f"\nFound {len(arenas)} arenas:")
    for theme, data in arenas.items():
        print(f"  {theme}: {len(data['targets'])} targets")
    
    # Save garden arena as SVG
    svg_output_path = os.path.join(os.path.dirname(__file__), "garden_arena.svg")
    save_garden_arena_as_svg(arenas, svg_output_path)
    
    print("\nStarting visualization...")
    print("Controls:")
    print("  - LEFT/RIGHT arrows or SPACE: Navigate between arenas")
    print("  - ESC or Q: Exit")
    
    visualize_arenas(arenas)
    
    print("\nVisualization complete!")





