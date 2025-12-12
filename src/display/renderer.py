"""
Renderer module for the minimalist button-centric media player UI.
Displays large touch-friendly buttons and sliders optimized for 240x320 screen.

Compatible with Raspberry Pi 5 and Waveshare 2.8" LCD (A).

Dependencies:
- PIL (Pillow) for image manipulation
- ui_components for Button, Slider, etc.

Signals emitted: None
Signals received: None
"""

from PIL import Image, ImageDraw, ImageFont
from .ui_components import Button, Slider, ProgressBar, Label, COLORS


class MediaPlayerUI:
    """
    Minimalist media player UI with large buttons and sliders.

    Layout (240x320):
    ┌─────────────────────────┐
    │  Now Playing Title      │  <- 40px header
    │  Artist                 │
    ├─────────────────────────┤
    │  ═══════════════════    │  <- Progress bar (touch-seekable)
    │  0:00         3:45      │
    ├─────────────────────────┤
    │                         │
    │   ◄◄    ▶/▮▮    ►►     │  <- Large control buttons (80px)
    │                         │
    ├─────────────────────────┤
    │  🔊 ═════════════════   │  <- Volume slider
    ├─────────────────────────┤
    │  ■ Stop    ⚙ Settings  │  <- Secondary buttons
    └─────────────────────────┘
    """

    # Layout constants for 240x320 display
    SCREEN_WIDTH = 240
    SCREEN_HEIGHT = 320
    PADDING = 8
    BUTTON_SIZE = 56
    SMALL_BUTTON_SIZE = 40

    def __init__(self, screen):
        """
        Initialize the media player UI.

        Args:
            screen: Screen instance for display output
        """
        self.screen = screen
        self.components = {}
        self.font = None
        self.font_small = None

        # State
        self.is_playing = False
        self.current_track = "No Track"
        self.current_artist = ""
        self.current_time = 0
        self.total_time = 0
        self.volume = 50

        # Callbacks (set by main app)
        self.on_play_pause = None
        self.on_stop = None
        self.on_next = None
        self.on_previous = None
        self.on_volume_change = None
        self.on_seek = None

        self._load_fonts()
        self._create_components()

    def _load_fonts(self):
        """Load fonts for rendering."""
        try:
            self.font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14
            )
            self.font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11
            )
            self.font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20
            )
        except Exception:
            self.font = ImageFont.load_default()
            self.font_small = self.font
            self.font_large = self.font

    def _create_components(self):
        """Create all UI components."""
        p = self.PADDING
        w = self.SCREEN_WIDTH
        btn = self.BUTTON_SIZE

        # Progress bar (y=80)
        self.components['progress'] = ProgressBar(
            x=p, y=80, width=w - 2 * p, height=6,
            value=0, max_val=100
        )

        # Main control buttons (y=130, centered)
        button_y = 140
        center_x = w // 2

        # Previous button
        self.components['btn_prev'] = Button(
            x=center_x - btn - btn // 2 - p,
            y=button_y,
            width=btn, height=btn,
            label="◄◄",
            color=COLORS['surface_light'],
            on_press=self._on_previous
        )

        # Play/Pause button (larger, centered)
        self.components['btn_play'] = Button(
            x=center_x - btn // 2,
            y=button_y - 4,
            width=btn + 8, height=btn + 8,
            label="▶",
            color=COLORS['primary'],
            on_press=self._on_play_pause
        )

        # Next button
        self.components['btn_next'] = Button(
            x=center_x + btn // 2 + p,
            y=button_y,
            width=btn, height=btn,
            label="►►",
            color=COLORS['surface_light'],
            on_press=self._on_next
        )

        # Volume slider (y=220)
        self.components['volume'] = Slider(
            x=p + 30, y=230, width=w - 2 * p - 30, height=24,
            min_val=0, max_val=100, value=50,
            label="Vol",
            on_change=self._on_volume
        )

        # Stop button (bottom left)
        self.components['btn_stop'] = Button(
            x=p, y=280,
            width=self.SMALL_BUTTON_SIZE + 20, height=self.SMALL_BUTTON_SIZE,
            label="■ Stop",
            color=COLORS['accent'],
            on_press=self._on_stop
        )


    # Callback handlers
    def _on_play_pause(self):
        """Handle play/pause button press."""
        if self.on_play_pause:
            self.on_play_pause()

    def _on_stop(self):
        """Handle stop button press."""
        if self.on_stop:
            self.on_stop()

    def _on_next(self):
        """Handle next button press."""
        if self.on_next:
            self.on_next()

    def _on_previous(self):
        """Handle previous button press."""
        if self.on_previous:
            self.on_previous()

    def _on_volume(self, value):
        """Handle volume change."""
        self.volume = int(value)
        if self.on_volume_change:
            self.on_volume_change(self.volume)

    # State updates
    def set_playing(self, playing):
        """Update play/pause button state."""
        self.is_playing = playing
        btn = self.components.get('btn_play')
        if btn:
            btn.label = "▮▮" if playing else "▶"

    def set_track_info(self, title, artist=""):
        """Update track information display."""
        self.current_track = title or "No Track"
        self.current_artist = artist

    def set_progress(self, current_time, total_time):
        """Update playback progress."""
        self.current_time = current_time
        self.total_time = total_time
        progress = self.components.get('progress')
        if progress and total_time > 0:
            progress.set_progress(current_time, total_time)

    def set_volume(self, volume):
        """Update volume slider."""
        self.volume = volume
        slider = self.components.get('volume')
        if slider:
            slider.value = volume

    # Touch handling
    def handle_touch(self, x, y):
        """Handle touch event, check all components."""
        # Check buttons
        for name, comp in self.components.items():
            if hasattr(comp, 'handle_press'):
                if comp.handle_press(x, y):
                    return name
            elif hasattr(comp, 'handle_touch'):
                if comp.handle_touch(x, y):
                    return name
        return None

    def handle_release(self):
        """Handle touch release, reset button states."""
        for comp in self.components.values():
            if hasattr(comp, 'handle_release'):
                comp.handle_release()

    # Rendering
    def render(self):
        """Render the complete UI to the screen."""
        if not self.screen or not self.screen.image:
            return

        draw = self.screen.draw

        # Clear background
        draw.rectangle(
            [(0, 0), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)],
            fill=COLORS['background']
        )

        # Draw header area
        self._draw_header(draw)

        # Draw all components
        for comp in self.components.values():
            comp.draw(draw, self.font)

        # Draw time labels
        self._draw_time_labels(draw)

        # Send to display
        self.screen._display_image(self.screen.image)

    def _draw_header(self, draw):
        """Draw the header with track info."""
        p = self.PADDING

        # Track title
        draw.text(
            (p, p), self.current_track[:24],
            fill=COLORS['text'], font=self.font_large
        )

        # Artist (if present)
        if self.current_artist:
            draw.text(
                (p, 35), self.current_artist[:30],
                fill=COLORS['text_dim'], font=self.font
            )

        # Playing indicator
        status = "▶ Playing" if self.is_playing else "▮▮ Paused"
        draw.text(
            (p, 58), status,
            fill=COLORS['primary'] if self.is_playing else COLORS['text_dim'],
            font=self.font_small
        )

    def _draw_time_labels(self, draw):
        """Draw current/total time labels."""
        p = self.PADDING

        current_str = self._format_time(self.current_time)
        total_str = self._format_time(self.total_time)

        draw.text(
            (p, 90), current_str,
            fill=COLORS['text_dim'], font=self.font_small
        )

        # Right-aligned total time
        bbox = draw.textbbox((0, 0), total_str, font=self.font_small)
        text_width = bbox[2] - bbox[0]
        draw.text(
            (self.SCREEN_WIDTH - p - text_width, 90), total_str,
            fill=COLORS['text_dim'], font=self.font_small
        )

        # Volume icon
        draw.text(
            (p, 232), "🔊",
            fill=COLORS['text_dim'], font=self.font_small
        )

    def _format_time(self, seconds):
        """Format seconds as MM:SS."""
        if seconds < 0:
            seconds = 0
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins}:{secs:02d}"

    def get_touch_regions(self):
        """
        Get touch regions for all interactive components.
        Returns dict mapping region name to (x, y, width, height, callback).
        """
        regions = {}
        for name, comp in self.components.items():
            if hasattr(comp, 'on_press') or hasattr(comp, 'on_change'):
                callback = getattr(comp, 'on_press', None) or getattr(comp, 'on_change', None)
                regions[name] = {
                    'x': comp.x, 'y': comp.y,
                    'width': comp.width, 'height': comp.height,
                    'callback': callback
                }
        return regions


# Legacy Renderer class for backward compatibility
class Renderer:
    """Legacy renderer - wraps MediaPlayerUI for backward compatibility."""

    def __init__(self, screen):
        self.screen = screen
        self.ui = MediaPlayerUI(screen)

    def clear(self):
        """Clear the display."""
        if self.screen and self.screen.draw:
            self.screen.draw.rectangle(
                [(0, 0), (self.screen.width, self.screen.height)],
                fill=COLORS['background']
            )

    def draw_text(self, text, x, y, font_size=16, color=(255, 255, 255)):
        """Draw text on the display."""
        if self.screen:
            self.screen.draw_text(text, x, y, font_size, color)

    def render(self):
        """Render the UI."""
        self.ui.render()

    def draw_system_info(self, system_info):
        """Draw system info (legacy method)."""
        self.clear()
        y_offset = 10
        for key, value in system_info.items():
            text = f"{key}: {value:.1f}" if isinstance(value, float) else f"{key}: {value}"
            self.draw_text(text, 10, y_offset)
            y_offset += 20