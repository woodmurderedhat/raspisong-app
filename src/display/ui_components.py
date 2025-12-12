"""
Minimalist UI Component system for touchscreen interface.
Provides reusable Button and Slider components for the Waveshare 2.8" LCD.

Design Philosophy:
- Large, touch-friendly buttons (minimum 48x48 pixels)
- High contrast minimalist design
- Clear visual feedback for touch/press states
- Optimized for 240x320 resolution

Dependencies:
- PIL (Pillow) for drawing

Signals emitted: None
Signals received: None
"""

from PIL import Image, ImageDraw, ImageFont


# Color palette - minimalist dark theme
COLORS = {
    'background': (20, 20, 25),
    'surface': (35, 35, 45),
    'surface_light': (50, 50, 65),
    'primary': (0, 150, 255),
    'primary_dark': (0, 100, 180),
    'secondary': (100, 255, 150),
    'accent': (255, 100, 100),
    'text': (255, 255, 255),
    'text_dim': (150, 150, 160),
    'border': (80, 80, 100),
    'slider_track': (60, 60, 80),
    'slider_fill': (0, 150, 255),
}


class UIComponent:
    """Base class for all UI components."""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

    def contains_point(self, px, py):
        """Check if point is within component bounds."""
        return (self.x <= px < self.x + self.width and
                self.y <= py < self.y + self.height)

    def draw(self, draw, font=None):
        """Draw the component. Override in subclasses."""
        raise NotImplementedError


class Button(UIComponent):
    """
    Minimalist touch button with icon/text support.

    Features:
    - Large touch target
    - Pressed state visual feedback
    - Icon or text label
    - Rounded corners
    """

    def __init__(self, x, y, width, height, label="", icon=None,
                 color=None, on_press=None):
        super().__init__(x, y, width, height)
        self.label = label
        self.icon = icon  # Unicode character for simple icons
        self.color = color or COLORS['primary']
        self.on_press = on_press
        self.pressed = False

    def draw(self, draw, font=None):
        """Draw the button."""
        if not self.visible:
            return

        # Choose colors based on state
        if not self.enabled:
            bg_color = COLORS['surface']
            text_color = COLORS['text_dim']
        elif self.pressed:
            bg_color = COLORS['primary_dark']
            text_color = COLORS['text']
        else:
            bg_color = self.color
            text_color = COLORS['text']

        # Draw rounded rectangle background
        self._draw_rounded_rect(draw, bg_color, radius=8)

        # Draw border
        self._draw_rounded_rect_outline(draw, COLORS['border'], radius=8)

        # Draw label/icon centered
        if self.icon:
            self._draw_centered_text(draw, self.icon, text_color, font, size=24)
        elif self.label:
            self._draw_centered_text(draw, self.label, text_color, font, size=14)

    def _draw_rounded_rect(self, draw, color, radius=8):
        """Draw a filled rounded rectangle."""
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.width, self.y + self.height

        # Draw main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=color)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=color)

        # Draw corners
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=color)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=color)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=color)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=color)

    def _draw_rounded_rect_outline(self, draw, color, radius=8, width=1):
        """Draw rounded rectangle outline."""
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.width - 1, self.y + self.height - 1

        # Draw lines
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=color, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=color, width=width)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=color, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=color, width=width)

        # Draw arcs for corners
        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=color)
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=color)
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=color)
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=color)

    def _draw_centered_text(self, draw, text, color, font, size=14):
        """Draw text centered in button."""
        try:
            if font is None:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate centered position
        tx = self.x + (self.width - text_width) // 2
        ty = self.y + (self.height - text_height) // 2

        # Draw the text
        draw.text((tx, ty), text, fill=color, font=font)

    def handle_press(self, x, y):
        """Handle touch press on button."""
        if self.enabled and self.contains_point(x, y):
            self.pressed = True
            if self.on_press:
                self.on_press()
            return True
        return False

    def handle_release(self):
        """Handle touch release."""
        self.pressed = False


class Slider(UIComponent):
    """
    Minimalist horizontal slider for volume/progress control.

    Features:
    - Touch-draggable
    - Visual fill indicator
    - Optional label
    """

    def __init__(self, x, y, width, height, min_val=0, max_val=100,
                 value=50, label="", on_change=None):
        super().__init__(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self.on_change = on_change
        self.dragging = False

    @property
    def normalized_value(self):
        """Get value as 0-1 range."""
        range_val = self.max_val - self.min_val
        if range_val == 0:
            return 0
        return (self.value - self.min_val) / range_val

    def draw(self, draw, font=None):
        """Draw the slider."""
        if not self.visible:
            return

        track_height = min(8, self.height // 3)
        track_y = self.y + (self.height - track_height) // 2

        # Draw track background
        draw.rounded_rectangle(
            [self.x, track_y, self.x + self.width, track_y + track_height],
            radius=track_height // 2,
            fill=COLORS['slider_track']
        )

        # Draw filled portion
        fill_width = int(self.width * self.normalized_value)
        if fill_width > 0:
            draw.rounded_rectangle(
                [self.x, track_y, self.x + fill_width, track_y + track_height],
                radius=track_height // 2,
                fill=COLORS['slider_fill']
            )

        # Draw knob
        knob_radius = min(12, self.height // 2 - 2)
        knob_x = self.x + fill_width
        knob_y = self.y + self.height // 2
        draw.ellipse(
            [knob_x - knob_radius, knob_y - knob_radius,
             knob_x + knob_radius, knob_y + knob_radius],
            fill=COLORS['text'],
            outline=COLORS['border']
        )

        # Draw label if provided
        if self.label:
            try:
                if font is None:
                    font = ImageFont.truetype(
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
                    )
            except Exception:
                font = ImageFont.load_default()

            draw.text((self.x, self.y - 16), self.label,
                     fill=COLORS['text_dim'], font=font)

        # Draw value
        value_text = f"{int(self.value)}"
        try:
            if font is None:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
                )
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), value_text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text((self.x + self.width - text_width, self.y - 16),
                 value_text, fill=COLORS['text'], font=font)

    def handle_touch(self, x, y):
        """Handle touch on slider, update value based on position."""
        if not self.enabled or not self.visible:
            return False

        if self.contains_point(x, y):
            # Calculate new value based on x position
            relative_x = x - self.x
            normalized = max(0, min(1, relative_x / self.width))
            new_value = self.min_val + normalized * (self.max_val - self.min_val)

            if new_value != self.value:
                self.value = new_value
                if self.on_change:
                    self.on_change(self.value)
            return True
        return False


class ProgressBar(UIComponent):
    """
    Read-only progress bar for displaying playback position.
    """

    def __init__(self, x, y, width, height, value=0, max_val=100):
        super().__init__(x, y, width, height)
        self.value = value
        self.max_val = max_val

    @property
    def normalized_value(self):
        """Get value as 0-1 range."""
        if self.max_val == 0:
            return 0
        return min(1, max(0, self.value / self.max_val))

    def draw(self, draw, font=None):
        """Draw the progress bar."""
        if not self.visible:
            return

        # Draw track
        draw.rounded_rectangle(
            [self.x, self.y, self.x + self.width, self.y + self.height],
            radius=self.height // 2,
            fill=COLORS['slider_track']
        )

        # Draw fill
        fill_width = int(self.width * self.normalized_value)
        if fill_width > 0:
            draw.rounded_rectangle(
                [self.x, self.y, self.x + fill_width, self.y + self.height],
                radius=self.height // 2,
                fill=COLORS['secondary']
            )

    def set_progress(self, value, max_val=None):
        """Update progress value."""
        self.value = value
        if max_val is not None:
            self.max_val = max_val


class Label(UIComponent):
    """Simple text label component."""

    def __init__(self, x, y, text="", color=None, size=14, align="left"):
        super().__init__(x, y, 0, 0)  # Width/height calculated from text
        self.text = text
        self.color = color or COLORS['text']
        self.size = size
        self.align = align

    def draw(self, draw, font=None):
        """Draw the label."""
        if not self.visible or not self.text:
            return

        try:
            if font is None:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.size
                )
        except Exception:
            font = ImageFont.load_default()

        draw.text((self.x, self.y), self.text, fill=self.color, font=font)

