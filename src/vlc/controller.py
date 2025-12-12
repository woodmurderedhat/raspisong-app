"""
VLC Controller module for media playback control.
Provides interface to control VLC media player.

Dependencies:
- python-vlc for VLC bindings
- VLC media player must be installed on the system

Signals emitted: None (could be extended with EventBus)
Signals received: None
"""

import os

try:
    import vlc
except ImportError as e:
    raise ImportError(
        "python-vlc is not installed. Install it with: pip install python-vlc\n"
        f"Original error: {e}"
    )


class VLCController:
    """Controls VLC media player for playback operations."""

    def __init__(self, media_path=None):
        """
        Initialize VLC controller.

        Args:
            media_path: Optional default media file or directory path

        Raises:
            RuntimeError: If VLC is not installed or cannot be initialized
        """
        # Check if vlc.Instance exists (requires VLC to be installed)
        if not hasattr(vlc, 'Instance'):
            raise RuntimeError(
                "VLC media player is not installed or python-vlc cannot find it.\n"
                "Please install VLC:\n"
                "  - Windows: Download from https://www.videolan.org/vlc/\n"
                "  - Linux: sudo apt-get install vlc libvlc-dev\n"
                "  - macOS: brew install vlc"
            )

        try:
            self.instance = vlc.Instance('--no-video-title-show', '--quiet')
        except Exception as e:
            raise RuntimeError(
                f"Failed to create VLC instance: {e}\n"
                "Ensure VLC media player is properly installed."
            )

        if self.instance is None:
            raise RuntimeError(
                "VLC Instance returned None. VLC may not be properly installed."
            )

        self.player = self.instance.media_player_new()
        self.media_list = []
        self.current_index = 0

        # Expand ~ to user home directory
        if media_path:
            media_path = os.path.expanduser(media_path)
        self.media_path = media_path

        if media_path and os.path.exists(media_path):
            self.load_media_directory(media_path)

    def load_media_directory(self, directory_path):
        """
        Load all media files from a directory.

        Args:
            directory_path: Path to directory containing media files
        """
        if not os.path.exists(directory_path):
            print(f"Media directory not found: {directory_path}")
            return

        supported_formats = ('.mp3', '.mp4', '.avi', '.mkv', '.wav', '.flac', '.ogg')
        self.media_list = []

        for file in os.listdir(directory_path):
            if file.lower().endswith(supported_formats):
                full_path = os.path.join(directory_path, file)
                self.media_list.append(full_path)

        self.media_list.sort()
        print(f"Loaded {len(self.media_list)} media files")

        if self.media_list:
            self.load_media(self.media_list[0])

    def load_media(self, media_path):
        """
        Load a specific media file.

        Args:
            media_path: Path to media file
        """
        if not os.path.exists(media_path):
            print(f"Media file not found: {media_path}")
            return False

        try:
            media = self.instance.media_new(media_path)
            self.player.set_media(media)
            print(f"Loaded media: {os.path.basename(media_path)}")
            return True
        except Exception as e:
            print(f"Error loading media: {e}")
            return False

    def play(self):
        """Start or resume playback."""
        try:
            if self.player.get_state() == vlc.State.Paused:
                self.player.pause()  # Unpause
                print("Resumed playback")
            else:
                self.player.play()
                print("Started playback")
            return True
        except Exception as e:
            print(f"Error playing: {e}")
            return False

    def pause(self):
        """Pause playback."""
        try:
            if self.player.is_playing():
                self.player.pause()
                print("Paused playback")
                return True
            return False
        except Exception as e:
            print(f"Error pausing: {e}")
            return False

    def stop(self):
        """Stop playback."""
        try:
            self.player.stop()
            print("Stopped playback")
            return True
        except Exception as e:
            print(f"Error stopping: {e}")
            return False

    def next(self):
        """Play next track in playlist."""
        if not self.media_list:
            print("No media list loaded")
            return False

        self.current_index = (self.current_index + 1) % len(self.media_list)
        next_media = self.media_list[self.current_index]

        if self.load_media(next_media):
            self.play()
            print(f"Playing next: {os.path.basename(next_media)}")
            return True
        return False

    def previous(self):
        """Play previous track in playlist."""
        if not self.media_list:
            print("No media list loaded")
            return False

        self.current_index = (self.current_index - 1) % len(self.media_list)
        prev_media = self.media_list[self.current_index]

        if self.load_media(prev_media):
            self.play()
            print(f"Playing previous: {os.path.basename(prev_media)}")
            return True
        return False

    def set_volume(self, volume):
        """
        Set playback volume.

        Args:
            volume: Volume level (0-100)
        """
        try:
            volume = max(0, min(100, volume))  # Clamp to 0-100
            self.player.audio_set_volume(volume)
            print(f"Volume set to {volume}%")
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False

    def get_volume(self):
        """Get current volume level."""
        try:
            return self.player.audio_get_volume()
        except Exception:
            return 0

    def get_status(self):
        """
        Get current playback status.

        Returns:
            dict: Status information including state, position, duration
        """
        try:
            state = self.player.get_state()
            state_str = {
                vlc.State.NothingSpecial: "Idle",
                vlc.State.Opening: "Opening",
                vlc.State.Buffering: "Buffering",
                vlc.State.Playing: "Playing",
                vlc.State.Paused: "Paused",
                vlc.State.Stopped: "Stopped",
                vlc.State.Ended: "Ended",
                vlc.State.Error: "Error"
            }.get(state, "Unknown")

            return {
                'state': state_str,
                'is_playing': self.player.is_playing(),
                'position': self.player.get_position(),
                'time': self.player.get_time(),
                'length': self.player.get_length(),
                'volume': self.get_volume(),
                'current_track': os.path.basename(self.media_list[self.current_index]) if self.media_list else "None"
            }
        except Exception as e:
            print(f"Error getting status: {e}")
            return {'state': 'Error', 'is_playing': False}

    def is_playing(self):
        """Check if media is currently playing."""
        try:
            return self.player.is_playing()
        except Exception:
            return False

    def cleanup(self):
        """Clean up VLC resources."""
        try:
            self.stop()
            self.player.release()
            self.instance.release()
            print("VLC controller cleanup complete")
        except Exception as e:
            print(f"Error during VLC cleanup: {e}")