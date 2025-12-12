"""
Configuration module for application settings.

This module provides:
- Config: Configuration manager with YAML file support
- DEFAULT_CONFIG: Default configuration values
- Legacy constants for backward compatibility

Dependencies:
- pyyaml for YAML parsing
"""

from .settings import Config, DEFAULT_CONFIG
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_ROTATION
from .settings import VLC_PATH, VLC_ARGS, GPIO_BUTTONS, UPDATE_INTERVAL

__all__ = [
    'Config',
    'DEFAULT_CONFIG',
    'SCREEN_WIDTH',
    'SCREEN_HEIGHT',
    'SCREEN_ROTATION',
    'VLC_PATH',
    'VLC_ARGS',
    'GPIO_BUTTONS',
    'UPDATE_INTERVAL',
]