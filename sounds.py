import os
import time

import pygame
import numpy

from typing import Union

from config import *
from constants import *


class SoundManager:
    def __init__(self):
        self.config = {
            'ping': 'ping.ogg',
        }
        self.current = ''
        for i in self.config.keys():
            self.config[i] = os.path.abspath(os.path.join(ASSETS, 'sounds', self.config[i]))
        init = Globals.get(MUSIC_INIT)
        if init is not None:
            self.init = Globals.get(MUSIC_INIT)
        else:
            self.init = False
        self.snd = None
        self.sound: Union[pygame.mixer.Sound, None] = None
        self._time = time.time()

    def update_init(self):
        init = Globals.get(MUSIC_INIT)
        if init is not None:
            self.init = Globals.get(MUSIC_INIT)

    def play_sound(self, sound):
        # for playing a single sound effect
        if not self.init:
            return
        for i in range(8):
            if not pygame.mixer.Channel(i).get_busy():
                self.current = sound
                pygame.mixer.Channel(i).play(pygame.mixer.Sound(self.config[sound]))
                # pygame.mixer.Channel(i).set_volume(0)
                return
        if sound == self.current and pygame.mixer.music.get_busy():
            return
        self.current = sound
        # pygame.mixer.music.play()

    def stop(self):
        if self.sound:
            self.sound.stop()
        self.sound = None
        self.snd = None

    def fade(self, fade_ms=1):
        if self.sound:
            self.sound.fadeout(fade_ms)

    def reset(self):
        pass

    def play(self, sound):
        # for playing a bgm track
        if not self.init:
            return
        if self.snd is None:
            path = os.path.join(ASSETS, 'sounds', f'{sound}.npy')
            self.snd = numpy.load(path, allow_pickle=False, fix_imports=False)
        self.sound = pygame.mixer.Sound(array=self.snd)
        self.sound.play()

    def get_sound_value(self):
        pass

    @property
    def total_length(self):
        if self.sound:
            return self.sound.get_length()

    @property
    def elapsed_time(self):
        if self.sound:
            return time.time() - self._time
