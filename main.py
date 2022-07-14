import asyncio
from config import *
from constants import *
from menu import MenuManager
from utils import *

music_init = False

try:
    pygame.init()
    music_init = True
except pygame.error:
    try:
        pygame.mixer.init()
        music_init = True
    except pygame.error:
        music_init = False

pygame.key.set_repeat(500, 100)


# setting global variables default value

Globals.set(FIRST_TIME_PLAYED, False)
Globals.set(FULL_PLAYED, False)
Globals.set(RETRY_MESSAGE, '')
Globals.set(CURRENT_LEVEL, '')
Globals.set(UPCOMING_LEVEL, '')
Globals.set(MUSIC_INIT, music_init)
Globals.set(SOUND_VALUE, 0)
Globals.set(ELAPSED_TIME_FOR_SOUNDTRACK, 0)
Globals.set(TOTAL_DURATION_OF_SOUNDTRACK, 0)


# TODO add subtitle manager


class Game:
    def __init__(self):
        self.full_screen = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        self.manager = MenuManager()
        self.clock = pygame.time.Clock()

    async def run(self):
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        if self.manager.mode == 'home':
                            if Globals.get(FIRST_TIME_PLAYED):
                                sys.exit(0)
                        else:
                            self.manager.transition_manager.set_transition('fade')
                            self.manager.subtitle_manager.clear()
                            if self.manager.mode not in ('point', 'line', 'triangle'):
                                self.manager.switch_mode('home', reset=False, transition=True)
                        # sys.exit(0)
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
            await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(Game().run())
