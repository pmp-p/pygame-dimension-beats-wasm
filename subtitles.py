import pygame
from utils import Timer, text
from config import WIDTH, HEIGHT
from typing import Union


class Subtitle:
    def __init__(self, name, time=None, size=35, pos=(WIDTH // 2, HEIGHT // 2), color='white'):
        self.timer = Timer(time if time else max(len(name) * 0.25, 0))
        self.done = False
        self.pos = pos
        self.text = text(name, size, color)

    def update(self):
        if self.timer.tick:
            self.done = True

    def draw(self, surf: pygame.Surface):
        surf.blit(self.text, self.text.get_rect(center=self.pos))


def get_typed_subtitles(_text, _time=2):
    subtitles = []
    for i in range(1, len(_text) - 1):
        subtitles.append(Subtitle(_text[0:i], 0.05))
    subtitles.append(Subtitle(_text, _time))
    return subtitles


class SubtitleManager:
    def __init__(self):
        self.subtitles = [
            # Subtitle('yo', 1),
            # Subtitle('wassup', 1),
            # *get_typed_subtitles('this is a typed text')
        ]
        self.current_subtitle: Union[Subtitle, None] = None

    def clear(self):
        self.subtitles.clear()

    def add(self, subtitle: Subtitle):
        self.subtitles.append(subtitle)

    def update(self):
        if self.current_subtitle:
            self.current_subtitle.update()
            if self.current_subtitle.done:
                self.current_subtitle = None
                try:
                    self.current_subtitle = self.subtitles.pop(0)
                    self.current_subtitle.timer.reset()
                except IndexError:
                    pass
        else:
            try:
                self.current_subtitle = self.subtitles.pop(0)
                self.current_subtitle.timer.reset()
            except IndexError:
                pass

    def draw(self, surf: pygame.Surface):
        if self.current_subtitle:
            self.current_subtitle.draw(surf)
