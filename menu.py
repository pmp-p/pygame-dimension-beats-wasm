import random
import sys

import pygame

from transition import TransitionManager
from subtitles import SubtitleManager, Subtitle, get_typed_subtitles
from utils import *
from objects import *
from config import WIDTH, HEIGHT, Globals
from sounds import SoundManager
from constants import *


class Menu:
    """
    Base signature for all menus
    """

    def __init__(self, manager: 'MenuManager', name='menu'):
        self.manager = manager
        self.name = name
        self.background = 'black'
        self.manager.subtitle_manager.clear()
        self.manager.object_manager.clear()

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)
        pygame.draw.rect(surf, 'white', surf.get_rect().inflate(-20, -200).move(0, 100 - 10), 3)
        # pygame.draw.rect(surf, 'white', surf.get_rect().inflate(-20, -HEIGHT + 170).move(0, -HEIGHT // 2 + 95), 3)
        surf.blit(text(self.name, size=100, aliased=False), (50, 50))


class Home(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.options = [
            'quit', 'help', 'settings', 'play'
        ]
        self.actions = [
            lambda: self.manager.switch_mode('quit'),
            lambda: self.manager.switch_mode('help'),
            lambda: ...,
            lambda: self.manager.switch_mode('point')
        ]
        self.selected = -1

    def update(self, events: list[pygame.event.Event]):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.selected += 1
                    self.selected %= len(self.options)
                    SoundManager.play('ping')
                if e.key == pygame.K_UP:
                    self.selected -= 1
                    self.selected %= len(self.options)
                    SoundManager.play('ping')
                if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                    try:
                        self.actions[self.selected]()
                    except IndexError:
                        self.manager.switch_mode('game', reset=True, transition=False)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        for i in range(len(self.options)):
            y = 200 + i * 75
            surf.blit(text(self.options[i], 50, 'orange' if i == self.selected else 'white'), (150, y))


class Quit(Menu):
    def __init__(self, manager, name):
        super().__init__(manager, name)
        if Globals.get(FIRST_TIME_PLAYED):
            sys.exit(0)
        else:
            _text = random.choice(
                [
                    'Play The Game First Idiot!',
                    'Never Quit!',
                    'Just Play The Game!'
                ]
            ).split(' ')

            for i in range(len(_text)):
                self.manager.subtitle_manager.add(
                    Subtitle(
                        ' '.join(_text[0:i + 1]),
                        time=0.3 if i != len(_text) - 1 else 2
                    )
                )

    def update(self, events: list[pygame.event.Event]):
        manager = self.manager.subtitle_manager
        if not manager.subtitles and not manager.current_subtitle:
            self.manager.switch_mode('home', reset=False)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)


class Help(Menu):
    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        t = text('We dont do that here')
        surf.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


class Game(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.options = [
            'play', 'the', 'game'
        ]
        self.actions = [

        ]
        self.selected = 0

    def update(self, events: list[pygame.event.Event]):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.selected += 1
                    self.selected %= len(self.options)
                if e.key == pygame.K_UP:
                    self.selected -= 1
                    self.selected %= len(self.options)
                if e.key == pygame.K_RETURN or e.key == pygame.K_KP_ENTER:
                    try:
                        self.actions[self.selected]()
                    except IndexError:
                        self.manager.switch_mode('home', reset=False, transition=False)

    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        for i in range(len(self.options)):
            y = 200 + i * 75
            surf.blit(text(self.options[i], 50, 'orange' if i == self.selected else 'white'), (150, y))


class Intro(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        _text = [
            'What is Dimensions ?',
            'Some another random line',
            'One more',
            'yea one more',
            'XDXD'
        ]
        _subtitles = []
        for i in _text:
            # _subtitles.append(Subtitle(i, 1))
            for j in get_typed_subtitles(i, 1):
                self.manager.subtitle_manager.add(j)

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)


class PointEnemyScene(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.manager.object_manager.init()
        self.manager.object_manager.add(BulletEnemy())

    def update(self, events: list[pygame.event.Event]):
        if not self.manager.object_manager.objects:
            self.manager.switch_mode('line')

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)


class LineEnemyScene(Menu):
    def __init__(self, manager: 'MenuManager', name='menu'):
        super().__init__(manager, name)
        self.manager.object_manager.init()
        self.manager.object_manager.add(LineEnemy())

    def update(self, events: list[pygame.event.Event]):
        if not self.manager.object_manager.objects:
            self.manager.switch_mode('home')

    def draw(self, surf: pygame.Surface):
        surf.fill(self.background)


class MenuManager:
    def __init__(self):
        self.to_switch = 'none'  # to switch menu after transition
        self.to_reset = False
        self.transition_manager: TransitionManager = TransitionManager()
        self.subtitle_manager: SubtitleManager = SubtitleManager()
        self.object_manager: ObjectManager = ObjectManager()
        self.menus = {
            'home': Home(self, 'Dimensions'),
            'game': Game(self, 'game'),
            'intro': Intro(self, 'intro'),
            'quit': Quit(self, 'quit'),
            'help': Help(self, 'help'),

            'point': PointEnemyScene(self, 'point'),
            'line': LineEnemyScene(self, 'line'),

        }
        self.subtitle_manager.clear()
        self.object_manager.clear()
        self.mode = 'home'
        self.menu = self.menus[self.mode]
        self.menu.__init__(self, self.menu.name)

    def switch_mode(self, mode, reset=True, transition=False):
        if mode in self.menus:
            if transition:
                self.to_switch = mode
                self.transition_manager.close()
            else:
                self.mode = mode
                self.menu = self.menus[self.mode]
                if reset:
                    self.menu.__init__(self, self.menu.name)
            # self.subtitle_manager.clear()

    def update(self, events: list[pygame.event.Event]):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.object_manager.add(
                        PointClicked(*pygame.mouse.get_pos())
                    )
        if self.to_switch != 'none':
            if self.transition_manager.transition.status == 'closed':
                self.switch_mode(self.to_switch, self.to_reset, transition=False)
                self.to_switch = 'none'
                self.to_reset = False
                self.transition_manager.open()
        self.menu.update(events)
        self.object_manager.update(events)
        self.transition_manager.update(events)
        self.subtitle_manager.update()

    def draw(self, surf: pygame.Surface):
        self.menu.draw(surf)
        self.object_manager.draw(surf)
        self.transition_manager.draw(surf)
        self.subtitle_manager.draw(surf)
        # surf.blit(text(self.transition_manager.transition.status), (0, 0))
