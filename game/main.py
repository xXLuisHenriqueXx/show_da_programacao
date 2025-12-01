import pygame
import sys

def main():
    pygame.init()

    # Create window
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("PyGame Docker Test")

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill screen with black
        screen.fill((0, 0, 0))
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
