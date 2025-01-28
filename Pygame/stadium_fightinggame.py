import pygame
from pygame.locals import *


class Stadium:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 1000

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (100, 100, 100)
        self.BLUE = (50, 150, 255)
        self.DARK_BLUE = (30, 30, 120)

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Fighting game stadium")
        self.clock = pygame.time.Clock()

    def draw_background(self):
        for y in range(self.SCREEN_HEIGHT):
            color = (
                self.DARK_BLUE[0] + (self.BLUE[0] - self.DARK_BLUE[0]) * y // self.SCREEN_HEIGHT,
                self.DARK_BLUE[1] + (self.BLUE[1] - self.DARK_BLUE[1]) * y // self.SCREEN_HEIGHT,
                self.DARK_BLUE[2] + (self.BLUE[2] - self.DARK_BLUE[2]) * y // self.SCREEN_HEIGHT
            )
            pygame.draw.line(self.screen, color, (0, y), (self.SCREEN_WIDTH, y))

        pygame.draw.polygon(self.screen, self.GRAY, [(0, self.SCREEN_HEIGHT), (300, 500), (500, self.SCREEN_HEIGHT)])
        pygame.draw.polygon(self.screen, self.GRAY, [(500, self.SCREEN_HEIGHT), (700, 400), (900, self.SCREEN_HEIGHT)])

    def draw_platform(self):
        platform_width1 = 600
        platform_height = 20
        platform_x1 = (self.SCREEN_WIDTH - platform_width1) // 2
        platform_y1 = 600
        platform_width2 = 100
        platform_x2 = (self.SCREEN_WIDTH - platform_width2) // 2.25
        platform_y2 = 300
        platform_x3 = (self.SCREEN_WIDTH - platform_width2) // 1.75
        platform_y3 = 450

        #platforms of the stadium
        pygame.draw.rect(self.screen, self.DARK_BLUE, (platform_x1, platform_y1, platform_width1, platform_height))
        pygame.draw.rect(self.screen, self.WHITE, (platform_x1, platform_y1, platform_width1, 5))
        pygame.draw.rect(self.screen, self.DARK_BLUE, (platform_x2, platform_y2, platform_width2, platform_height))
        pygame.draw.rect(self.screen, self.WHITE, (platform_x2, platform_y2, platform_width2, 5))
        pygame.draw.rect(self.screen, self.DARK_BLUE, (platform_x3, platform_y3, platform_width2, platform_height))
        pygame.draw.rect(self.screen, self.WHITE, (platform_x3, platform_y3, platform_width2, 5))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.screen.fill(self.BLACK)
            self.draw_background()
            self.draw_platform()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()