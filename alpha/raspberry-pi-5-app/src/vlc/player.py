class VLCPlayer:
    def __init__(self):
        import vlc
        self.player = vlc.MediaPlayer()

    def load_media(self, media_path):
        media = vlc.Media(media_path)
        self.player.set_media(media)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def is_playing(self):
        return self.player.is_playing()

    def set_volume(self, volume):
        self.player.audio_set_volume(volume)

    def get_volume(self):
        return self.player.audio_get_volume()