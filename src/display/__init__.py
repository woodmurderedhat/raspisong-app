"""
Display module for Waveshare 2.8" LCD screen management.

This module provides:
- Screen: Low-level LCD display driver (ILI9341)
- MediaPlayerUI: Minimalist media player UI with touch-friendly buttons
- Renderer: Legacy renderer wrapper for backward compatibility
- UI components: Button, Slider, ProgressBar, Label

Compatible with Raspberry Pi 5 using lgpio backend.
"""

from .screen import Screen
from .renderer import MediaPlayerUI, Renderer
from .ui_components import Button, Slider, ProgressBar, Label, COLORS

__all__ = [
    'Screen',
    'MediaPlayerUI',
    'Renderer',
    'Button',
    'Slider',
    'ProgressBar',
    'Label',
    'COLORS',
]