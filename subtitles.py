import pygame
from utils import Timer, text
from config import WIDTH, HEIGHT
from typing import Union


class Subtitle:
    def __init__(self, name, time=None, size=35, pos=(WIDTH // 2, HEIGHT // 2), color='white', callback=None):
        self.timer = Timer(time if time and type(time) != str else max(len(name) * 0.25, 0))
        self._time = time
        self.done = False
        self.pos = pos
        self.callback = callback
        self.text = text(name, size, color)

    def update(self):
        if self.timer.tick:
            if self._time != 'inf':
                self.done = True
                if self.callback is not None:
                    self.callback()

    def draw(self, surf: pygame.Surface):
        surf.blit(self.text, self.text.get_rect(center=self.pos))


def get_typed_subtitles(_text, _time=2, pos=None, callback=None):
    if pos is None:
        pos = (WIDTH // 2, HEIGHT // 2)
    subtitles = []
    for i in range(1, len(_text) - 2):
        subtitles.append(Subtitle(_text[0:i], 0.05, pos=pos))
    subtitles.append(Subtitle(_text[0:-1], 0.05, pos=pos, callback=callback))
    subtitles.append(Subtitle(_text, _time, pos=pos))
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
        self.current_subtitle = None

    def add(self, subtitle: Subtitle):
        self.subtitles.append(subtitle)

    def update(self):
        if self.current_subtitle:
            self.current_subtitle.update()
            try:
                if self.current_subtitle.done:
                    self.current_subtitle = None
                    try:
                        self.current_subtitle = self.subtitles.pop(0)
                        self.current_subtitle.timer.reset()
                    except IndexError:
                        pass
            except Exception as e:
                print(e)
        else:
            try:
                self.current_subtitle = self.subtitles.pop(0)
                self.current_subtitle.timer.reset()
            except IndexError:
                pass

    def draw(self, surf: pygame.Surface):
        if self.current_subtitle:
            self.current_subtitle.draw(surf)
