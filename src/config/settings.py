"""
Configuration settings module.
Loads configuration from YAML file and provides default settings.

Dependencies:
- pyyaml for YAML parsing

Signals emitted: None
Signals received: None
"""

import yaml
import os


# Default configuration values
# Updated for Raspberry Pi 5 and Waveshare 2.8" LCD (A) compatibility
DEFAULT_CONFIG = {
    'screen': {
        'width': 240,
        'height': 320,
        'rotation': 0,
        'spi_bus': 0,
        'spi_device': 0,
        'spi_speed_hz': 32000000
    },
    'vlc': {
        'default_media_path': '/home/pi/media',
        'volume': 50,
        'autoplay': False
    },
    'system': {
        'update_interval': 1,
        'display_info': {
            'cpu_usage': True,
            'memory_usage': True,
            'disk_space': True
        }
    },
    'gpio': {
        # Waveshare 2.8" LCD (A) onboard buttons
        # KEY1=GPIO4, KEY2=GPIO23, KEY3=GPIO24, KEY4=GPIO25
        'buttons': {
            'play_pause': 4,   # KEY1 - combined play/pause toggle
            'stop': 23,        # KEY2
            'next': 24,        # KEY3
            'previous': 25     # KEY4
        }
    }
}


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path='config.yaml'):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self):
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self._merge_config(self.config, yaml_config)
                        print(f"Configuration loaded from {self.config_path}")
                    else:
                        print(f"Empty config file, using defaults")
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
        else:
            print(f"Config file not found: {self.config_path}")
            print("Using default configuration")

    def _merge_config(self, default, override):
        """
        Recursively merge override config into default config.

        Args:
            default: Default configuration dictionary
            override: Override configuration dictionary
        """
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def get(self, *keys, default=None):
        """
        Get configuration value by key path.

        Args:
            *keys: Key path (e.g., 'screen', 'width')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def screen_width(self):
        """Get screen width."""
        return self.get('screen', 'width', default=240)

    @property
    def screen_height(self):
        """Get screen height."""
        return self.get('screen', 'height', default=320)

    @property
    def screen_rotation(self):
        """Get screen rotation."""
        return self.get('screen', 'rotation', default=0)

    @property
    def vlc_media_path(self):
        """Get VLC default media path with ~ expansion."""
        import os
        path = self.get('vlc', 'default_media_path', default='/home/pi/media')
        return os.path.expanduser(path)

    @property
    def vlc_volume(self):
        """Get VLC default volume."""
        return self.get('vlc', 'volume', default=50)

    @property
    def vlc_autoplay(self):
        """Get VLC autoplay setting."""
        return self.get('vlc', 'autoplay', default=False)

    @property
    def update_interval(self):
        """Get system update interval."""
        return self.get('system', 'update_interval', default=1)

    @property
    def gpio_buttons(self):
        """Get GPIO button configuration for Waveshare 2.8" LCD (A) onboard buttons."""
        return self.get('gpio', 'buttons', default={
            'play_pause': 4,   # KEY1 - GPIO 4
            'stop': 23,        # KEY2 - GPIO 23
            'next': 24,        # KEY3 - GPIO 24
            'previous': 25     # KEY4 - GPIO 25
        })

    @property
    def display_cpu_usage(self):
        """Check if CPU usage should be displayed."""
        return self.get('system', 'display_info', 'cpu_usage', default=True)

    @property
    def display_memory_usage(self):
        """Check if memory usage should be displayed."""
        return self.get('system', 'display_info', 'memory_usage', default=True)

    @property
    def display_disk_space(self):
        """Check if disk space should be displayed."""
        return self.get('system', 'display_info', 'disk_space', default=True)


# Legacy constants for backward compatibility
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320
SCREEN_ROTATION = 0

VLC_PATH = "/usr/bin/vlc"
VLC_ARGS = ["--no-video-title-show"]

# Waveshare 2.8" LCD (A) onboard buttons (updated for Pi 5)
GPIO_BUTTONS = {
    "play_pause": 4,   # KEY1 - GPIO 4
    "stop": 23,        # KEY2 - GPIO 23
    "next": 24,        # KEY3 - GPIO 24
    "previous": 25     # KEY4 - GPIO 25
}

UPDATE_INTERVAL = 1
