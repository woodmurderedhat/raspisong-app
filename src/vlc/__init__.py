"""
VLC module for media playback control.

This module provides:
- VLCController: High-level media player controller with playlist support
- VLCPlayer: Simple VLC media player wrapper

Dependencies:
- python-vlc for VLC bindings
"""

from .controller import VLCController
from .player import VLCPlayer

__all__ = [
    'VLCController',
    'VLCPlayer',
]