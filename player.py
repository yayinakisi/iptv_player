from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

class Player(QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)

    def play_stream(self, stream_url):
        self.setMedia(QMediaContent(QUrl(stream_url)))
        self.play()

    def pause_stream(self):
        self.pause()

    def stop_stream(self):
        self.stop()

    def set_volume(self, volume):
        self.setVolume(volume)
