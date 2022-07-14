import os
import time

import pygame
import numpy

from typing import Union

from config import *
from constants import *

from utils import map_to_range, clamp


class SoundManager1:
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

    def set_sound_value(self):
        if self.sound:
            if self.snd is not None:
                Globals.set(SOUND_VALUE, self.get_sound_value())
                if pygame.mixer.music.get_busy():
                    self.sound = None
                    self.snd = None

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
        pygame.mixer.music.stop()

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
            # self.snd = numpy.load(path, allow_pickle=False, fix_imports=False)
        self.sound = pygame.mixer.Sound(array=self.snd)
        # pygame.mixer.music.load(os.path.join(ASSETS, 'sounds', f'{sound}.ogg'))
        # pygame.mixer.music.play()
        self.sound.play(fade_ms=100)
        # self.sound_length = self.sound.get_length()
        # self.sound.stop()
        self._time = time.time()

    def get_sound_value(self):
        if self.sound is not None:
            if self.snd is not None:
                value = self.snd[self.get_index()]
                v = clamp(sum(value), 0, 10000 * 2)
                v = map_to_range(v, 0, 10000 * 2, 0, 10)
                return v
            else:
                return 0
        else:
            return 0

    def get_index(self):
        if self.sound is not None:
            if self.snd is not None:
                return round(map_to_range(time.time() - self._time, 0, self.total_length, 0, len(self.snd) - 1))
            else:
                return 0
        else:
            return 0

    def start_at(self, dt):
        self._time += dt
        if self.sound:
            if self.snd is not None:
                self.sound.stop()

    @property
    def total_length(self):
        if self.sound:
            return self.sound.get_length()
        else:
            return 0

    @property
    def elapsed_time(self):
        if self.sound:
            return time.time() - self._time


class SoundManager:
    def __init__(self):
        self.config = {
            'ping': 'ping.ogg',
        }
        self.current = ''
        self.sound_durations = {
            'points': 153,
            'lines': 103,
            'triangles': 84 - 5,
        }
        for i in self.config.keys():
            self.config[i] = os.path.abspath(os.path.join(ASSETS, 'sounds', self.config[i]))
        init = Globals.get(MUSIC_INIT)
        if init is not None:
            self.init = Globals.get(MUSIC_INIT)
        else:
            self.init = False
        self._time = time.time()
        self._paused_timer = time.time()
        self._paused = False
        self.current_sound = ''

    def update_init(self):
        init = Globals.get(MUSIC_INIT)
        if init is not None:
            self.init = Globals.get(MUSIC_INIT)

    def update_time(self):
        Globals.set(ELAPSED_TIME_FOR_SOUNDTRACK, self.elapsed_time)

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

    def pause(self):
        pygame.mixer.music.pause()
        self._paused_timer = time.time()
        self._paused = True

    def resume(self):
        pygame.mixer.music.unpause()
        print(time.time() - self._paused_timer)
        self._time += time.time() - self._paused_timer
        self._paused = False

    def toggle_pause(self):
        self._paused = not self._paused
        if self._paused:
            self.pause()
        else:
            self.resume()

    @staticmethod
    def stop():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        Globals.set(ELAPSED_TIME_FOR_SOUNDTRACK, 0)

    @staticmethod
    def fade(fade_ms=1):
        pygame.mixer.music.fadeout(fade_ms)

    def reset(self):
        self.play(self.current_sound)

    def play(self, sound, start=0):
        # for playing a bgm track
        self.current_sound = sound
        pygame.mixer.music.load(os.path.join(ASSETS, 'sounds', f'{sound}.ogg'))
        duration = self.sound_durations.get(sound)
        Globals.set(TOTAL_DURATION_OF_SOUNDTRACK, duration if duration else 0)
        pygame.mixer.music.play(start=start)
        self._time = time.time()
        self._time -= start

    def skip_to(self, _time):
        if _time < 0:
            _time = 0
        print(_time, '[[[[[[[[[[[[[[[[[')
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=_time)
        # pygame.mixer.music.set_pos(_time)
        self._time = time.time()
        self._time -= _time

    @property
    def total_length(self):
        return Globals.get(TOTAL_DURATION_OF_SOUNDTRACK)

    @property
    def elapsed_time(self):
        if not self._paused:
            return time.time() - self._time
        else:
            return self._paused_timer - self._time
