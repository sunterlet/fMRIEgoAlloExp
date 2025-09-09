import pygame
import os

# Initialize Pygame
pygame.init()

# Screen dimensions (matching the experiment)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Colors
BACKGROUND_COLOR = (0, 0, 0)  # Black
WHITE = (255, 255, 255)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fixation Cross")

# Fill background
screen.fill(BACKGROUND_COLOR)

# Fixation cross parameters (matching the experiment)
cross_size = 20
cross_thickness = 3
center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Draw fixation cross (consistent with experiment)
# Horizontal line
pygame.draw.line(screen, WHITE, 
                (center_x - cross_size, center_y), 
                (center_x + cross_size, center_y), cross_thickness)
# Vertical line
pygame.draw.line(screen, WHITE, 
                (center_x, center_y - cross_size), 
                (center_x, center_y + cross_size), cross_thickness)

# Update display
pygame.display.flip()

# Save the screen as PNG
output_filename = "fixation_cross.png"
pygame.image.save(screen, output_filename)
print(f"Fixation cross saved as: {output_filename}")

# Wait a moment to show the screen
pygame.time.wait(2000)

# Quit Pygame
pygame.quit()

print(f"Fixation cross PNG file created: {os.path.abspath(output_filename)}") 