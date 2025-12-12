"""
Main entry point for Raspberry Pi 5 LCD Media Player.

This application:
- Displays a minimalist button-centric media player UI on Waveshare 2.8" LCD
- Supports both touch input and GPIO button controls
- Controls VLC media player

Compatible with Raspberry Pi 5 using lgpio backend.

Dependencies:
- display.screen for LCD display management
- display.renderer for MediaPlayerUI
- input.touch for touchscreen handling
- input.gpio for button input handling
- vlc.controller for media player control
- config.settings for configuration management

Architecture:
- Single-responsibility modules communicate through direct method calls
- Main loop updates display at configured interval
- Touch and GPIO buttons trigger VLC controls
- All resources properly cleaned up on exit
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from display.screen import Screen
from display.renderer import MediaPlayerUI
from vlc.controller import VLCController
from input.gpio import GPIOHandler
from input.touch import TouchHandler
from config.settings import Config


class MediaPlayerApp:
    """
    Main application class for the LCD Media Player.
    Integrates display, touch, GPIO, and VLC control.
    """

    def __init__(self, config):
        self.config = config
        self.screen = None
        self.ui = None
        self.vlc_controller = None
        self.gpio_handler = None
        self.touch_handler = None
        self.running = False

    def initialize(self):
        """Initialize all components."""
        print("\nInitializing display...")
        self.screen = Screen(
            width=self.config.screen_width,
            height=self.config.screen_height
        )
        self.screen.initialize()

        # Initialize the Media Player UI
        print("Initializing UI...")
        self.ui = MediaPlayerUI(self.screen)

        # Initialize the VLC controller
        print("Initializing VLC controller...")
        self.vlc_controller = VLCController(media_path=self.config.vlc_media_path)
        self.vlc_controller.set_volume(self.config.vlc_volume)

        # Connect UI callbacks to VLC
        self._connect_ui_callbacks()

        # Initialize GPIO handler
        print("Initializing GPIO buttons...")
        self.gpio_handler = GPIOHandler(self.config.gpio_buttons, self.vlc_controller)

        # Initialize touch handler
        print("Initializing touch input...")
        self.touch_handler = TouchHandler(
            screen_width=self.config.screen_width,
            screen_height=self.config.screen_height
        )
        self._connect_touch_callbacks()
        self.touch_handler.start()

        # Auto-play if configured
        if self.config.vlc_autoplay and self.vlc_controller.media_list:
            print("Auto-playing media...")
            self.vlc_controller.play()

    def _connect_ui_callbacks(self):
        """Connect UI button callbacks to VLC controller actions."""
        self.ui.on_play_pause = self._on_play_pause
        self.ui.on_stop = self._on_stop
        self.ui.on_next = self._on_next
        self.ui.on_previous = self._on_previous
        self.ui.on_volume_change = self._on_volume_change

    def _connect_touch_callbacks(self):
        """Connect touch handler to UI."""
        self.touch_handler.on_touch_down = self._on_touch_down
        self.touch_handler.on_touch_up = self._on_touch_up
        self.touch_handler.on_touch_move = self._on_touch_move

    # VLC control callbacks
    def _on_play_pause(self):
        """Handle play/pause action."""
        if self.vlc_controller:
            if self.vlc_controller.is_playing():
                self.vlc_controller.pause()
                print("Paused")
            else:
                self.vlc_controller.play()
                print("Playing")

    def _on_stop(self):
        """Handle stop action."""
        if self.vlc_controller:
            self.vlc_controller.stop()
            print("Stopped")

    def _on_next(self):
        """Handle next track action."""
        if self.vlc_controller:
            self.vlc_controller.next()
            print("Next track")

    def _on_previous(self):
        """Handle previous track action."""
        if self.vlc_controller:
            self.vlc_controller.previous()
            print("Previous track")

    def _on_volume_change(self, volume):
        """Handle volume change."""
        if self.vlc_controller:
            self.vlc_controller.set_volume(int(volume))
            print(f"Volume: {int(volume)}")

    # Touch callbacks
    def _on_touch_down(self, x, y):
        """Handle touch press."""
        if self.ui:
            self.ui.handle_touch(x, y)

    def _on_touch_up(self, x, y):
        """Handle touch release."""
        if self.ui:
            self.ui.handle_release()

    def _on_touch_move(self, x, y):
        """Handle touch drag (for sliders)."""
        if self.ui:
            # Check volume slider
            volume_slider = self.ui.components.get('volume')
            if volume_slider:
                volume_slider.handle_touch(x, y)

    def update_ui_state(self):
        """Update UI with current VLC state."""
        if not self.vlc_controller or not self.ui:
            return

        status = self.vlc_controller.get_status()

        # Update playing state
        self.ui.set_playing(status['state'] == 'playing')

        # Update track info
        track_name = status.get('current_track', 'No Track')
        self.ui.set_track_info(track_name if track_name != 'None' else 'No Track')

        # Update progress
        position = status.get('position', 0)
        duration = status.get('duration', 0)
        self.ui.set_progress(position, duration)

        # Update volume
        volume = status.get('volume', 50)
        self.ui.set_volume(volume)

    def run(self):
        """Main application loop."""
        self.running = True
        update_interval = self.config.update_interval
        loop_count = 0

        print("\n" + "=" * 50)
        print("Application started successfully!")
        print("Touch screen or press buttons to control playback")
        print("Press Ctrl+C to exit")
        print("=" * 50 + "\n")

        while self.running:
            try:
                # Update UI state from VLC
                self.update_ui_state()

                # Render the UI
                self.ui.render()

                # Print status to console periodically
                if loop_count % 30 == 0:  # Every ~3 seconds at 0.1s interval
                    status = "Playing" if self.ui.is_playing else "Paused"
                    print(f"[{time.strftime('%H:%M:%S')}] {status} - {self.ui.current_track}")

                loop_count += 1
                time.sleep(update_interval)

            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(update_interval)

    def cleanup(self):
        """Clean up all resources."""
        self.running = False
        print("\nCleaning up resources...")

        if self.touch_handler:
            try:
                self.touch_handler.cleanup()
            except Exception as e:
                print(f"Error cleaning up touch: {e}")

        if self.gpio_handler:
            try:
                self.gpio_handler.cleanup()
            except Exception as e:
                print(f"Error cleaning up GPIO: {e}")

        if self.vlc_controller:
            try:
                self.vlc_controller.cleanup()
            except Exception as e:
                print(f"Error cleaning up VLC: {e}")

        if self.screen:
            try:
                self.screen.cleanup()
            except Exception as e:
                print(f"Error cleaning up screen: {e}")

        print("Application terminated.")
        print("=" * 50)


def main():
    """Main application entry point."""
    print("=" * 50)
    print("Raspberry Pi 5 LCD Media Player")
    print("Waveshare 2.8\" LCD (A) Touch + Buttons")
    print("=" * 50)

    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    config = Config(config_path)
    print("Configuration loaded")

    app = MediaPlayerApp(config)

    try:
        app.initialize()
        app.run()

    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal...")

    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        app.cleanup()


if __name__ == "__main__":
    main()