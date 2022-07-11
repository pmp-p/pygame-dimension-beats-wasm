"""
Project Configuration
The project structure is meant to be organized but simple at the same time
Because there will be a web version porting of the same game simultanously
using p5.js
Hence the structure needs to be javascript[p5.js] compatible
"""

import os
import sys

import pygame

WIDTH = int(800 * 1.0)  # width of the screen
HEIGHT = int(600 * 1.0)  # height of the screen

VOLUME = 100  # sound volume

FPS = 60

ASSETS = 'assets'


class Globals:
    _config = {}

    @classmethod
    def pop(cls, key):
        try:
            cls._config.pop(key)
        except KeyError:
            pass

    @classmethod
    def set(cls, key, value):
        cls._config[key] = value

    @classmethod
    def get(cls, key):
        return cls._config.get(key)


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
    ASSETS = os.path.join(sys._MEIPASS, ASSETS)
    try:
        import pyi_splash

        pyi_splash.close()
    except ImportError:
        pass
else:
    print('running in a normal Python process')
