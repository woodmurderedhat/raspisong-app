"""
VLC Player module providing basic media player interface.

This is a simple wrapper around VLC's MediaPlayer for basic playback.
For full playlist and control features, use VLCController instead.

Dependencies:
- python-vlc for VLC bindings

Signals emitted: None
Signals received: None
"""

import vlc


class VLCPlayer:
    """
    Simple VLC media player wrapper.

    Provides basic media playback controls. For advanced features
    like playlist management, use VLCController instead.
    """

    def __init__(self):
        """Initialize the VLC media player."""
        self.player = vlc.MediaPlayer()

    def load_media(self, media_path):
        """
        Load a media file for playback.

        Args:
            media_path: Path to the media file
        """
        media = vlc.Media(media_path)
        self.player.set_media(media)

    def play(self):
        """Start or resume playback."""
        self.player.play()

    def pause(self):
        """Toggle pause state."""
        self.player.pause()

    def stop(self):
        """Stop playback."""
        self.player.stop()

    def is_playing(self):
        """
        Check if media is currently playing.

        Returns:
            bool: True if playing, False otherwise
        """
        return self.player.is_playing()

    def set_volume(self, volume):
        """
        Set playback volume.

        Args:
            volume: Volume level (0-100)
        """
        self.player.audio_set_volume(volume)

    def get_volume(self):
        """
        Get current volume level.

        Returns:
            int: Current volume (0-100)
        """
        return self.player.audio_get_volume()

    def release(self):
        """Release VLC player resources."""
        self.player.release()