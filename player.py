from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget

class NetworkAccessManager(QNetworkAccessManager):
    def createRequest(self, operation, request, device=None):
        req = QNetworkRequest(request)
        req.setRawHeader(b"Accept", b"*/*")
        req.setRawHeader(b"Host", b"sezonhd.xyz:8080")
        req.setRawHeader(b"User-Agent", b"TiviMate/4.6.1 (Linux; Android 11)")
        req.setRawHeader(b"Connection", b"keep-alive")
        req.setRawHeader(b"Accept-Language", b"en-TR;q=1, tr-TR;q=0.9")

        return QNetworkAccessManager.createRequest(self, operation, req, device)


class Player(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_muted = False
        self.manager = NetworkAccessManager()

    def play_pause_stream(self, stream_url=None):
        if stream_url and self.mediaStatus() == QMediaPlayer.NoMedia:
            self.setMedia(QMediaContent(QUrl(stream_url)), self.manager)
            # self.setMedia(QMediaContent())
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
