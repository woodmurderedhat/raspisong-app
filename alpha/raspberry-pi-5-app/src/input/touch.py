"""
Touch Input Handler module for Waveshare 2.8" LCD (A) resistive touchscreen.
Uses the ADS7846 touch controller via evdev input events.

Compatible with Raspberry Pi 5.

Dependencies:
- evdev for reading touch events from /dev/input/event*

Signals emitted: None (could be extended with EventBus)
Signals received: None
"""

import threading
import time

try:
    from evdev import InputDevice, ecodes, list_devices
    EVDEV_AVAILABLE = True
except ImportError:
    EVDEV_AVAILABLE = False
    print("Warning: evdev not available. Touch input disabled.")


class TouchHandler:
    """
    Handles resistive touchscreen input from ADS7846 controller.

    The touch coordinates are read from evdev and mapped to screen coordinates.
    Touch events are dispatched to registered callbacks.
    """

    # ADS7846 raw coordinate ranges (may need calibration)
    RAW_X_MIN = 198
    RAW_X_MAX = 3679
    RAW_Y_MIN = 292
    RAW_Y_MAX = 3800

    def __init__(self, screen_width=240, screen_height=320, swap_axes=True):
        """
        Initialize touch handler.

        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
            swap_axes: Whether to swap X/Y axes (common for this display)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.swap_axes = swap_axes

        self.device = None
        self.running = False
        self.thread = None

        # Current touch state
        self.touch_x = 0
        self.touch_y = 0
        self.is_touching = False

        # Callbacks
        self.on_touch_down = None
        self.on_touch_up = None
        self.on_touch_move = None

        # Touch regions (for button detection)
        self.touch_regions = {}

        self._find_touch_device()

    def _find_touch_device(self):
        """Find the ADS7846 touchscreen device."""
        if not EVDEV_AVAILABLE:
            return

        try:
            devices = [InputDevice(path) for path in list_devices()]
            for dev in devices:
                if 'ADS7846' in dev.name or 'ads7846' in dev.name.lower():
                    self.device = dev
                    print(f"Touch device found: {dev.name} at {dev.path}")
                    return

            # Fallback: try common touch device names
            for dev in devices:
                if 'touch' in dev.name.lower():
                    self.device = dev
                    print(f"Touch device found: {dev.name} at {dev.path}")
                    return

            print("Warning: No ADS7846 touchscreen device found")
        except Exception as e:
            print(f"Error finding touch device: {e}")

    def _map_coordinates(self, raw_x, raw_y):
        """Map raw touch coordinates to screen coordinates."""
        # Clamp to valid range
        raw_x = max(self.RAW_X_MIN, min(self.RAW_X_MAX, raw_x))
        raw_y = max(self.RAW_Y_MIN, min(self.RAW_Y_MAX, raw_y))

        # Normalize to 0-1 range
        norm_x = (raw_x - self.RAW_X_MIN) / (self.RAW_X_MAX - self.RAW_X_MIN)
        norm_y = (raw_y - self.RAW_Y_MIN) / (self.RAW_Y_MAX - self.RAW_Y_MIN)

        # Map to screen coordinates
        if self.swap_axes:
            screen_x = int(norm_y * self.screen_width)
            screen_y = int(norm_x * self.screen_height)
        else:
            screen_x = int(norm_x * self.screen_width)
            screen_y = int(norm_y * self.screen_height)

        return screen_x, screen_y

    def register_region(self, name, x, y, width, height, callback):
        """
        Register a touch region with a callback.

        Args:
            name: Unique identifier for the region
            x, y: Top-left corner of the region
            width, height: Size of the region
            callback: Function to call when region is touched
        """
        self.touch_regions[name] = {
            'x': x, 'y': y,
            'width': width, 'height': height,
            'callback': callback
        }

    def unregister_region(self, name):
        """Remove a registered touch region."""
        if name in self.touch_regions:
            del self.touch_regions[name]

    def clear_regions(self):
        """Remove all registered touch regions."""
        self.touch_regions.clear()


    def _read_events(self):
        """Background thread to read touch events."""
        if not self.device:
            return

        raw_x = 0
        raw_y = 0

        try:
            for event in self.device.read_loop():
                if not self.running:
                    break

                if event.type == ecodes.EV_ABS:
                    if event.code == ecodes.ABS_X:
                        raw_x = event.value
                    elif event.code == ecodes.ABS_Y:
                        raw_y = event.value

                elif event.type == ecodes.EV_KEY:
                    if event.code == ecodes.BTN_TOUCH:
                        if event.value == 1:  # Touch down
                            self.touch_x, self.touch_y = self._map_coordinates(raw_x, raw_y)
                            self.is_touching = True
                            if self.on_touch_down:
                                self.on_touch_down(self.touch_x, self.touch_y)
                            self._check_regions(self.touch_x, self.touch_y)
                        else:  # Touch up
                            self.is_touching = False
                            if self.on_touch_up:
                                self.on_touch_up(self.touch_x, self.touch_y)

                elif event.type == ecodes.EV_SYN and self.is_touching:
                    new_x, new_y = self._map_coordinates(raw_x, raw_y)
                    if new_x != self.touch_x or new_y != self.touch_y:
                        self.touch_x, self.touch_y = new_x, new_y
                        if self.on_touch_move:
                            self.on_touch_move(self.touch_x, self.touch_y)

        except Exception as e:
            if self.running:
                print(f"Touch event read error: {e}")

    def start(self):
        """Start reading touch events in background thread."""
        if not self.device or not EVDEV_AVAILABLE:
            print("Touch input not available")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._read_events, daemon=True)
        self.thread.start()
        print("Touch handler started")
        return True

    def stop(self):
        """Stop reading touch events."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("Touch handler stopped")

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        if self.device:
            self.device.close()
        print("Touch handler cleanup complete")


# Example usage
if __name__ == "__main__":
    def on_touch(x, y):
        print(f"Touch at ({x}, {y})")

    def on_release(x, y):
        print(f"Release at ({x}, {y})")

    def on_region(name, x, y):
        print(f"Region '{name}' touched at ({x}, {y})")

    handler = TouchHandler()
    handler.on_touch_down = on_touch
    handler.on_touch_up = on_release

    # Register some test regions
    handler.register_region("play", 10, 200, 60, 60, on_region)
    handler.register_region("stop", 90, 200, 60, 60, on_region)

    if handler.start():
        print("Touch handler running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            handler.cleanup()
    else:
        print("Touch input not available on this system.")

