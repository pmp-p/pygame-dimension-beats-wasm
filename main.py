import pygame

from config import *
from menu import MenuManager
from utils import *
from constants import *
from sounds import SoundManager

try:
    pygame.init()
except pygame.error:
    try:
        pygame.mixer.init()
        SoundManager.init = True
    except pygame.error:
        SoundManager.init = False

pygame.key.set_repeat(500, 100)


Globals.set(FIRST_TIME_PLAYED, False)
Globals.set(FULL_PLAYED, False)

# TODO add subtitle manager


class Game:
    def __init__(self):
        self.full_screen = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        self.manager = MenuManager()
        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        sys.exit(0)
                    if e.key == pygame.K_f:
                        self.full_screen = not self.full_screen
                        if self.full_screen:
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                        else:
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            # self.screen.fill('black')
            self.manager.update(events)
            self.manager.draw(self.screen)
            pygame.draw.rect(self.screen, 'white', self.screen.get_rect(), 3)
            pygame.display.update()
            # print(self.clock.get_fps())
            self.clock.tick(FPS)


if __name__ == '__main__':
    Game().run()
