from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget

class Player(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_muted = False

    def play_pause_stream(self, stream_url=None):
        if stream_url and self.mediaStatus() == QMediaPlayer.NoMedia:
            self.setMedia(QMediaContent(QUrl(stream_url)))
            self.play()
        elif self.state() == QMediaPlayer.PlayingState:
            self.pause()
        else:
            self.play()

    def stop_stream(self):
        self.stop()

    def set_volume(self, volume):
        self.setVolume(volume)

    def mute_unmute(self):
        self.is_muted = not self.is_muted
        self.setMuted(self.is_muted)
