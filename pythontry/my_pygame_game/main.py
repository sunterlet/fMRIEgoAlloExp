import pygame, sys

def main():
    print("DEBUG: main() is running!")
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 0))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
