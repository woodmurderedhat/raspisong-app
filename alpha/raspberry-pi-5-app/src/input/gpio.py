"""
GPIO Input Handler module for button controls.
Manages GPIO button inputs and maps them to VLC controller actions.

Compatible with Raspberry Pi 5 using lgpio backend.

Dependencies:
- gpiozero for GPIO button handling (uses lgpio on Pi 5)
- vlc.controller for media control

Signals emitted: None (could be extended with EventBus)
Signals received: None
"""

from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause
import time

# Set lgpio as the default pin factory for Raspberry Pi 5 compatibility
try:
    from gpiozero import Device
    Device.pin_factory = LGPIOFactory()
except Exception as e:
    print(f"Warning: Could not set lgpio pin factory: {e}")


class GPIOHandler:
    """Handles GPIO button inputs and maps them to controller actions."""

    def __init__(self, button_config, vlc_controller=None):
        """
        Initialize GPIO handler with button configuration.

        Args:
            button_config: Dictionary mapping button names to GPIO pins
                          e.g., {'play': 17, 'pause': 27, 'stop': 22}
            vlc_controller: VLCController instance for media control
        """
        self.button_config = button_config
        self.vlc_controller = vlc_controller
        self.buttons = {}
        self.last_press_time = {}
        self.debounce_delay = 0.3  # 300ms debounce

        self._setup_buttons()

    def _setup_buttons(self):
        """Setup GPIO buttons with callbacks."""
        for action, pin in self.button_config.items():
            try:
                button = Button(pin, pull_up=True, bounce_time=0.1)
                self.buttons[action] = button
                self.last_press_time[action] = 0

                # Assign callback based on action
                if action == 'play':
                    button.when_pressed = self._on_play_pressed
                elif action == 'pause':
                    button.when_pressed = self._on_pause_pressed
                elif action == 'stop':
                    button.when_pressed = self._on_stop_pressed
                elif action == 'next':
                    button.when_pressed = self._on_next_pressed
                elif action == 'previous':
                    button.when_pressed = self._on_previous_pressed
                elif action == 'play_pause':
                    button.when_pressed = self._on_play_pause_pressed
                else:
                    button.when_pressed = lambda a=action: self._on_generic_press(a)

                print(f"Setup button '{action}' on GPIO pin {pin}")

            except Exception as e:
                print(f"Error setting up button '{action}' on pin {pin}: {e}")

    def _debounce_check(self, action):
        """
        Check if enough time has passed since last button press.

        Args:
            action: Button action name

        Returns:
            bool: True if debounce period has passed
        """
        current_time = time.time()
        if current_time - self.last_press_time.get(action, 0) > self.debounce_delay:
            self.last_press_time[action] = current_time
            return True
        return False

    def _on_play_pressed(self):
        """Handle play button press."""
        if self._debounce_check('play'):
            print("Play button pressed")
            if self.vlc_controller:
                self.vlc_controller.play()

    def _on_pause_pressed(self):
        """Handle pause button press."""
        if self._debounce_check('pause'):
            print("Pause button pressed")
            if self.vlc_controller:
                self.vlc_controller.pause()

    def _on_stop_pressed(self):
        """Handle stop button press."""
        if self._debounce_check('stop'):
            print("Stop button pressed")
            if self.vlc_controller:
                self.vlc_controller.stop()

    def _on_next_pressed(self):
        """Handle next button press."""
        if self._debounce_check('next'):
            print("Next button pressed")
            if self.vlc_controller:
                self.vlc_controller.next()

    def _on_previous_pressed(self):
        """Handle previous button press."""
        if self._debounce_check('previous'):
            print("Previous button pressed")
            if self.vlc_controller:
                self.vlc_controller.previous()

    def _on_play_pause_pressed(self):
        """Handle play/pause toggle button press."""
        if self._debounce_check('play_pause'):
            print("Play/Pause button pressed")
            if self.vlc_controller:
                if self.vlc_controller.is_playing():
                    self.vlc_controller.pause()
                else:
                    self.vlc_controller.play()

    def _on_generic_press(self, action):
        """Handle generic button press."""
        if self._debounce_check(action):
            print(f"Button '{action}' pressed")

    def set_vlc_controller(self, vlc_controller):
        """
        Set or update the VLC controller reference.

        Args:
            vlc_controller: VLCController instance
        """
        self.vlc_controller = vlc_controller
        print("VLC controller linked to GPIO handler")

    def cleanup(self):
        """Clean up GPIO resources."""
        try:
            for button in self.buttons.values():
                button.close()
            print("GPIO handler cleanup complete")
        except Exception as e:
            print(f"Error during GPIO cleanup: {e}")


# Example usage
if __name__ == "__main__":
    # Waveshare 2.8" LCD (A) onboard button configuration
    # KEY1=GPIO4, KEY2=GPIO23, KEY3=GPIO24, KEY4=GPIO25
    button_pins = {
        'play_pause': 4,   # KEY1 - combined play/pause toggle
        'stop': 23,        # KEY2
        'next': 24,        # KEY3
        'previous': 25     # KEY4
    }

    gpio_handler = GPIOHandler(button_pins)
    print("GPIO handler running. Press Ctrl+C to exit.")
    print("Button mapping:")
    print("  KEY1 (GPIO 4)  - Play/Pause")
    print("  KEY2 (GPIO 23) - Stop")
    print("  KEY3 (GPIO 24) - Next")
    print("  KEY4 (GPIO 25) - Previous")

    try:
        pause()  # Keep the program running to listen for button presses
    except KeyboardInterrupt:
        print("\nExiting...")
        gpio_handler.cleanup()