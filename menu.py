from utils import *


class Menu:
    """
    Base signature for all menus
    """

    def __init__(self, manager: 'MenuManager', name='menu'):
        self.manager = manager
        self.name = name

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        surf.blit(text(self.name), (50, 50))


class Home(Menu):
    pass


class Game(Menu):
    pass


class MenuManager:
    def __init__(self):
        self.menus = {
            'home': Home(self, 'Dimensions'),
            'game': Game(self, 'game'),
        }
        self.mode = 'home'
        self.menu = self.menus[self.mode]

    def switch_mode(self, mode, reset=False):
        if mode in self.menus:
            self.mode = mode
            self.menu = self.menus[self.mode]
            if reset:
                self.menu.__init__(self, self.menu.name)

    def update(self, events: list[pygame.event.Event]):
        self.menu.update(events)

    def draw(self, surf: pygame.Surface):
        self.menu.draw(surf)
