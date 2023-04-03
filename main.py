import sys
from PyQt5.QtWidgets import QApplication
from iptv_player import IPTVPlayer

def main():
    app = QApplication(sys.argv)
    iptv_player = IPTVPlayer()
    iptv_player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
