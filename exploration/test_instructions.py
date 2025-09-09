import pygame
import os
import time

# Initialize pygame
pygame.init()

# Create display
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Instruction Test")

# Load and display an instruction image
INSTRUCTIONS_DIR = os.path.join(os.path.dirname(__file__), "Instructions-he")
instruction_path = os.path.join(INSTRUCTIONS_DIR, "7.png")

print(f"Loading instruction: {instruction_path}")
print(f"File exists: {os.path.exists(instruction_path)}")

try:
    instruction_image = pygame.image.load(instruction_path)
    print("Image loaded successfully")
    
    # Center the image on the screen
    image_rect = instruction_image.get_rect()
    image_rect.center = (500, 400)  # Center of 1000x800 screen
    
    # Fill screen with background color and display image
    screen.fill((3, 3, 1))  # Same background color as original
    screen.blit(instruction_image, image_rect)
    pygame.display.flip()
    
    print("Image displayed. Press Enter to continue or 'ESC' to exit...")
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_RETURN:
                    print("Enter key pressed, exiting...")
                    waiting = False
        
        pygame.time.Clock().tick(15)
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")

pygame.quit() 