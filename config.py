"""
Project Configuration
The project structure is meant to be organized but simple at the same time
Because there will be a web version porting of the same game simultanously
using p5.js
Hence the structure needs to be javascript[p5.js] compatible
"""

import os
import sys

WIDTH = 1280  # width of the screen
HEIGHT = 720  # height of the screen

VOLUME = 100  # sound volume

FPS = 60

ASSETS = 'assets'

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
