"""
Input module for handling user input from GPIO buttons and touchscreen.

This module provides:
- GPIOHandler: Handles physical button inputs via GPIO pins
- TouchHandler: Handles resistive touchscreen input via evdev

Compatible with Raspberry Pi 5 using lgpio backend.
"""

from .gpio import GPIOHandler
from .touch import TouchHandler

__all__ = [
    'GPIOHandler',
    'TouchHandler',
]