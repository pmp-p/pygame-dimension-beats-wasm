import math
import os
import time
from config import ASSETS
from functools import lru_cache
from typing import Literal

import pygame
import pygame.gfxdraw

FONT = os.path.abspath(os.path.join(ASSETS, 'fonts', 'ARCADECLASSIC.TTF'))


# FONT = 'consolas'


def clamp(value, mini, maxi):
    """Clamp value between mini and maxi"""
    if value < mini:
        return mini
    elif maxi < value:
        return maxi
    else:
        return value


def distance(p1, p2):
    """Get distance between 2 points"""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def map_to_range(value, from_x, from_y, to_x, to_y):
    """map the value from one range to another"""
    return clamp(value * (to_y - to_x) / (from_y - from_x), to_x, to_y)


@lru_cache()
def load_image(path: str, alpha: bool = True, scale=1.0, color_key=None):
    img = pygame.image.load(path)
    img = pygame.transform.scale_by(img, scale)
    if color_key:
        img.set_colorkey(color_key)
    if alpha:
        return img.convert_alpha()
    else:
        return img.convert()


@lru_cache(maxsize=10)
def font(size):
    return pygame.font.Font(FONT, size)


@lru_cache(maxsize=100)
def text(msg: str, size=50, color=(255, 255, 255), aliased=False):
    msg = msg.replace(' ', '   ')
    return font(size).render(msg, aliased, color)


def dilute(color: tuple[int, int, int], factor):
    r, g, b = color
    r //= factor
    g //= factor
    b //= factor
    r = clamp(r, 0, 255)
    g = clamp(g, 0, 255)
    b = clamp(b, 0, 255)
    return r, g, b


# class Triangle:
#     def __init__(self, pos=(0, 0)):
#         self.pos = pygame.Vector2(pos)
#         # base triangle of side n
#         root_3 = math.sqrt(3)
#         self.points = [
#             [0, -root_3 / 4], [-1]
#         ]

def get_triangle1(length=50, pos=(150, 150), angle=45):
    root_3 = math.sqrt(3)
    pos = pygame.Vector2(pos)
    points = [
        pygame.Vector2(0, -root_3 / 4),
        pygame.Vector2(-0.5, root_3 / 4),
        pygame.Vector2(0.5, root_3 / 4)
    ]
    for i in points:
        i.rotate_ip(angle)
        i *= length
        i += pos
    return points


def get_triangle(length, pos, angle):
    pos = pygame.Vector2(pos)
    point_a = pygame.Vector2(0, -length)
    point_b = point_a.rotate(120)
    point_c = point_a.rotate(240)
    points = [point_a, point_b, point_c]
    for i in points:
        i.rotate_ip(angle)
        i += pos
    return points


def draw_triangle(surf: pygame.Surface, pos=(150, 150), color=(255, 255, 255), angle=45, length=50, width=0):
    points = get_triangle(length, pos, angle)
    pygame.draw.polygon(surf, color, points, width=width)
    # if width > 0:
    #     pygame.gfxdraw.polygon(surf, points, color)
    # else:
    #     pygame.gfxdraw.filled_polygon(surf, points, color)


class Timer:
    def __init__(self, timeout=0.0, callback=None):
        self.timeout = timeout
        self.timer = time.time()
        self.paused_timer = time.time()
        self.paused = False
        self.callback_done = False
        self.callable = callback

    def reset(self):
        self.timer = time.time()

    def pause(self):
        self.paused = True
        self.paused_timer = time.time()

    def resume(self):
        self.paused = False
        self.timer -= time.time() - self.paused_timer

    @property
    def elapsed(self):
        if self.paused:
            return time.time() - self.timer - (time.time() - self.paused_timer)
        return time.time() - self.timer

    @property
    def tick(self):
        if self.elapsed > self.timeout:
            self.timer = time.time()  # reset timer
            if self.callable is not None:
                self.callable()
            return True
        else:
            return False


class TimerSequence:
    def __init__(self, timestamps):
        # timestamps -> list [ list [ str (name), float (time), callback[optional] ] ]
        self.timestamps = timestamps
        self.current = timestamps.pop(0)
        self.current_timer = Timer(self.current[1], callback=self.current[2] if self.current[2] else None)

    def update(self):
        if self.current and self.current_timer:
            if self.current_timer.tick:
                try:
                    self.current = self.timestamps.pop(0)
                    self.current = Timer(self.current[1])
                except IndexError:
                    self.current_timer = None
                    self.current = None

    @property
    def phase(self):
        if self.current:
            return self.current[0]
        else:
            return 'none'


class SpriteSheet:
    """
    Class to load sprite-sheets
    """

    def __init__(self, sheet, rows, cols, images=None, alpha=True, scale=1.0, color_key=None):
        self._sheet = pygame.image.load(sheet)
        self._r = rows
        self._c = cols
        self._images = images if images else rows * cols
        self._alpha = alpha
        self._scale = scale
        self._color_key = color_key

    def __str__(self):
        return f'SpriteSheet Object <{self._sheet.__str__()}>'

    def get_images(self):
        w = self._sheet.get_width() // self._c
        h = self._sheet.get_height() // self._r
        images = [self._sheet.subsurface(pygame.Rect(i % self._c * w, i // self._c * h, w, h)) for i in range(self._r * self._c)][0:self._images]
        if self._color_key is not None:
            for i in images:
                i.set_colorkey(self._color_key)
        if self._alpha:
            for i in images:
                i.convert_alpha()
        else:
            for i in images:
                i.convert()
        return [pygame.transform.scale_by(i, self._scale) for i in images]


class LoopingSpriteSheet:
    def __init__(self, sheet, rows, cols, images=None, alpha=True, scale=1.0, color_key=None, timer=0.1,
                 mode: Literal['center', 'topleft'] = 'center'):
        self.timer = Timer(timeout=timer)
        self.images = SpriteSheet(sheet, rows, cols, images, alpha, scale, color_key).get_images()
        self.c = 0
        self.mode = mode

    def draw(self, surf: pygame.Surface, x, y):
        if self.timer.tick:
            self.c += 1
            self.c %= len(self.images)
        img = self.images[self.c]
        if self.mode == 'center':
            surf.blit(img, img.get_rect(center=(x, y)))
        else:
            surf.blit(img, (x, y))
