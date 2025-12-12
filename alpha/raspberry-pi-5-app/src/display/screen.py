"""
Screen module for Waveshare 2.8" LCD display.
Handles initialization, rendering, and display updates.

Compatible with Raspberry Pi 5 using lgpio backend.

Dependencies:
- PIL (Pillow) for image manipulation
- spidev for SPI communication
- gpiozero for GPIO control (uses lgpio on Pi 5)

Signals emitted: None
Signals received: None
"""

from PIL import Image, ImageDraw, ImageFont
import spidev
from gpiozero import OutputDevice, PWMOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
import time

# Set lgpio as the default pin factory for Raspberry Pi 5 compatibility
try:
    from gpiozero import Device
    Device.pin_factory = LGPIOFactory()
except Exception as e:
    print(f"Warning: Could not set lgpio pin factory: {e}")

# Waveshare 2.8" LCD (A) Rev2.0 pin configuration
# Based on official Waveshare documentation
RST_PIN = 13      # Reset pin (GPIO 13, Physical Pin 33)
DC_PIN = 15       # Data/Command pin (GPIO 15, Physical Pin 10) - LCD_RS
BL_PIN = 18       # Backlight PWM pin (GPIO 18, Physical Pin 12)
CS_PIN = 8        # Chip Select (GPIO 8, Physical Pin 24) - CE0
MOSI_PIN = 10     # SPI MOSI (GPIO 10, Physical Pin 19)
SCLK_PIN = 11     # SPI SCLK (GPIO 11, Physical Pin 23)


class Screen:
    """Manages the Waveshare 2.8" LCD display."""

    def __init__(self, width=240, height=320):
        self.width = width
        self.height = height
        self.display = None
        self.spi = None
        self.image = None
        self.draw = None
        self.font = None
        # GPIO devices (using gpiozero for Pi 5 compatibility)
        self.rst_device = None
        self.dc_device = None
        self.bl_device = None

    def initialize(self):
        """Initialize the Waveshare display with SPI communication."""
        try:
            # Setup GPIO using gpiozero (compatible with Pi 5 via lgpio)
            self.rst_device = OutputDevice(RST_PIN, initial_value=True)
            self.dc_device = OutputDevice(DC_PIN, initial_value=True)
            # Use PWM for backlight control (Rev2.1 feature)
            try:
                self.bl_device = PWMOutputDevice(BL_PIN, initial_value=1.0)
            except Exception:
                # Fallback to simple output if PWM not available
                self.bl_device = OutputDevice(BL_PIN, initial_value=True)

            # Setup SPI
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # Bus 0, Device 0
            self.spi.max_speed_hz = 32000000
            self.spi.mode = 0

            # Reset display
            self._reset()

            # Initialize display
            self._init_display()

            # Turn on backlight
            self._set_backlight(True)

            # Create image buffer
            self.image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
            self.draw = ImageDraw.Draw(self.image)

            # Load default font
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except Exception:
                self.font = ImageFont.load_default()

            print("Display initialized successfully")

        except Exception as e:
            print(f"Error initializing display: {e}")
            raise

    def _set_backlight(self, on, brightness=1.0):
        """Control backlight on/off and brightness."""
        if hasattr(self.bl_device, 'value'):
            # PWM device
            self.bl_device.value = brightness if on else 0.0
        else:
            # Simple output device
            if on:
                self.bl_device.on()
            else:
                self.bl_device.off()

    def _reset(self):
        """Hardware reset the display."""
        self.rst_device.on()
        time.sleep(0.1)
        self.rst_device.off()
        time.sleep(0.1)
        self.rst_device.on()
        time.sleep(0.1)

    def _write_command(self, cmd):
        """Send command to display."""
        self.dc_device.off()
        self.spi.writebytes([cmd])

    def _write_data(self, data):
        """Send data to display."""
        self.dc_device.on()
        if isinstance(data, int):
            self.spi.writebytes([data])
        elif len(data) <= 4096:
            self.spi.writebytes(list(data))
        else:
            # Split large data into chunks (SPI buffer limit)
            for i in range(0, len(data), 4096):
                self.spi.writebytes(list(data[i:i + 4096]))

    def _init_display(self):
        """Initialize display with configuration commands."""
        # Basic initialization sequence for ILI9341
        self._write_command(0x01)  # Software reset
        time.sleep(0.15)

        self._write_command(0x28)  # Display off

        self._write_command(0xCF)
        self._write_data([0x00, 0x83, 0x30])

        self._write_command(0xED)
        self._write_data([0x64, 0x03, 0x12, 0x81])

        self._write_command(0xE8)
        self._write_data([0x85, 0x01, 0x79])

        self._write_command(0xCB)
        self._write_data([0x39, 0x2C, 0x00, 0x34, 0x02])

        self._write_command(0xF7)
        self._write_data([0x20])

        self._write_command(0xEA)
        self._write_data([0x00, 0x00])

        self._write_command(0xC0)  # Power control
        self._write_data([0x26])

        self._write_command(0xC1)  # Power control
        self._write_data([0x11])

        self._write_command(0xC5)  # VCOM control
        self._write_data([0x35, 0x3E])

        self._write_command(0xC7)  # VCOM control
        self._write_data([0xBE])

        self._write_command(0x36)  # Memory access control
        self._write_data([0x28])

        self._write_command(0x3A)  # Pixel format
        self._write_data([0x55])

        self._write_command(0xB1)  # Frame rate
        self._write_data([0x00, 0x1B])

        self._write_command(0xF2)  # 3Gamma function disable
        self._write_data([0x08])

        self._write_command(0x26)  # Gamma curve
        self._write_data([0x01])

        self._write_command(0x11)  # Exit sleep
        time.sleep(0.15)

        self._write_command(0x29)  # Display on
        time.sleep(0.15)

    def update_display(self, system_info):
        """Update the display with system information."""
        # Clear the image
        self.draw.rectangle([(0, 0), (self.width, self.height)], fill=(0, 0, 0))

        # Draw title
        self.draw.text((10, 10), "System Monitor", font=self.font, fill=(255, 255, 255))

        # Draw system info
        y_offset = 50
        for key, value in system_info.items():
            text = f"{key}: {value:.1f}" if isinstance(value, float) else f"{key}: {value}"
            self.draw.text((10, y_offset), text, font=self.font, fill=(0, 255, 0))
            y_offset += 30

        # Send image to display
        self._display_image(self.image)

    def _display_image(self, image):
        """Send image buffer to display with optimized bulk transfer."""
        # Convert image to RGB565 format
        img_rgb = image.convert('RGB')
        pixels = list(img_rgb.getdata())

        # Set window
        self._write_command(0x2A)  # Column address set
        self._write_data([0x00, 0x00, ((self.width - 1) >> 8) & 0xFF, (self.width - 1) & 0xFF])

        self._write_command(0x2B)  # Row address set
        self._write_data([0x00, 0x00, ((self.height - 1) >> 8) & 0xFF, (self.height - 1) & 0xFF])

        self._write_command(0x2C)  # Memory write

        # Convert all pixels to RGB565 and send in chunks for efficiency
        self.dc_device.on()

        # Build pixel buffer
        pixel_buffer = bytearray(len(pixels) * 2)
        for i, pixel in enumerate(pixels):
            r, g, b = pixel
            # Convert to RGB565
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixel_buffer[i * 2] = rgb565 >> 8
            pixel_buffer[i * 2 + 1] = rgb565 & 0xFF

        # Send in chunks (SPI has 4096 byte limit per transfer)
        chunk_size = 4096
        for i in range(0, len(pixel_buffer), chunk_size):
            self.spi.writebytes(list(pixel_buffer[i:i + chunk_size]))

    def clear_display(self):
        """Clear the display to black."""
        if self.draw:
            self.draw.rectangle([(0, 0), (self.width, self.height)], fill=(0, 0, 0))
            self._display_image(self.image)

    def draw_text(self, text, x, y, font_size=16, color=(255, 255, 255)):
        """Draw text on the display at (x, y)."""
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = self.font

        self.draw.text((x, y), text, font=font, fill=color)

    def cleanup(self):
        """Clean up GPIO and SPI resources."""
        try:
            # Turn off backlight
            self._set_backlight(False)

            # Close SPI
            if self.spi:
                self.spi.close()

            # Close GPIO devices (gpiozero handles cleanup automatically)
            if self.rst_device:
                self.rst_device.close()
            if self.dc_device:
                self.dc_device.close()
            if self.bl_device:
                self.bl_device.close()

            print("Display cleanup complete")
        except Exception as e:
            print(f"Error during cleanup: {e}")