import sys
import vlc
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QVBoxLayout, QHBoxLayout, QSplitter, QTreeView, QListView, QLabel,
                             QFrame, QTextBrowser, QSlider, QStatusBar, QSizePolicy, QTimeEdit, QLabel, QInputDialog, QFileDialog,
                             QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QListWidget, QMessageBox)
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings
from playlist_manager import PlaylistManager
from epg_manager import EPGManager
from PyQt5.QtWidgets import QListWidgetItem


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        layout = QFormLayout()

        self.update_xtream = QLineEdit()
        self.auto_xtream_update_interval = QSpinBox()
        self.auto_xtream_update_interval.setRange(1, 1000)

        self.update_m3u_url = QLineEdit()
        self.auto_m3u_url_update_interval = QSpinBox()
        self.auto_m3u_url_update_interval.setRange(1, 1000)

        self.epg_url = QLineEdit()
        self.auto_epg_update_interval = QDoubleSpinBox()
        self.auto_epg_update_interval.setRange(0.1, 1000)

        layout.addRow("Update Xtream:", self.update_xtream)
        layout.addRow("Auto Xtream Update Interval:", self.auto_xtream_update_interval)

        layout.addRow("Update m3u URL:", self.update_m3u_url)
        layout.addRow("Auto m3u URL Update Interval:", self.auto_m3u_url_update_interval)

        layout.addRow("EPG URL:", self.epg_url)
        layout.addRow("Auto EPG Update Interval:", self.auto_epg_update_interval)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addRow(button_box)
        self.setLayout(layout)


class XtreamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Xtream API Credentials")

        layout = QFormLayout()

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.server_url = QLineEdit()

        layout.addRow("Username:", self.username)
        layout.addRow("Password:", self.password)
        layout.addRow("Server URL:", self.server_url)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addRow(button_box)
        self.setLayout(layout)


class IPTVPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IPTV Player')

        self.playlist_manager = PlaylistManager()
        self.epg_manager = EPGManager()

        self.load_settings()

        # Menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        open_m3u_url_action = QAction('Open m3u URL', self)
        open_m3u_url_action.triggered.connect(self.on_open_m3u_url)
        menu_bar.addAction(open_m3u_url_action)

        open_m3u_file_action = QAction('Open m3u File', self)
        open_m3u_file_action.triggered.connect(self.on_open_m3u_file)
        menu_bar.addAction(open_m3u_file_action)

        xtream_action = QAction('Xtream', self)
        xtream_action.triggered.connect(self.on_xtream)
        menu_bar.addAction(xtream_action)

        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.on_settings)
        menu_bar.addAction(settings_action)

        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(self.close)
        menu_bar.addAction(quit_action)

        # Add clock to the menu bar
        current_time = QTimeEdit(QTime.currentTime())
        current_time.setReadOnly(True)
        current_time.setButtonSymbols(QTimeEdit.NoButtons)
        current_time.setFont(QFont("Arial", 12))
        menu_bar.setCornerWidget(current_time, Qt.TopRightCorner)

        # Main layout and window
        central_widget = QFrame(self)
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Splitter for the main layout
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # First part: Groups and Channels
        self.channel_list = QListWidget()  # Create the channel_list attribute here
        self.channel_list.setFont(QFont("Arial", 12))
        splitter.addWidget(self.channel_list)

        # Second part: EPG Information
        epg_info = QListView()
        epg_info.setFont(QFont("Arial", 12))
        splitter.addWidget(epg_info)
        
        # EPG labels
        epg_layout = QVBoxLayout()
        self.epg_now_label = QLabel()
        self.epg_now_label.setFont(QFont("Arial", 12))
        epg_layout.addWidget(self.epg_now_label)

        self.epg_next_label = QLabel()
        self.epg_next_label.setFont(QFont("Arial", 12))
        epg_layout.addWidget(self.epg_next_label)

        self.epg_now_time_label = QLabel()
        self.epg_now_time_label.setFont(QFont("Arial", 12))
        epg_layout.addWidget(self.epg_now_time_label)

        self.epg_next_time_label = QLabel()
        self.epg_next_time_label.setFont(QFont("Arial", 12))
        epg_layout.addWidget(self.epg_next_time_label)

        epg_info.setLayout(epg_layout)

        # Third part: Player and EPG data of the current program
        player_layout = QVBoxLayout()

        self.player_label = QLabel()
        self.player_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.player_label.setStyleSheet("QLabel { background-color : black; }")
        self.player_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        player_layout.addWidget(self.player_label)

        # Initialize the VLC player
        self.vlc_instance = vlc.Instance()
        self.vlc_player = self.vlc_instance.media_player_new()

        # Connect the channel list click event to the play_channel function
        self.channel_list.itemDoubleClicked.connect(self.play_channel)

        # EPG update timer
        self.epg_update_timer = QTimer(self)
        self.epg_update_timer.timeout.connect(self.update_gui)
        self.epg_update_timer.start(60000)  # Update EPG every minute

        # Player controls
        controls_layout = QHBoxLayout()

        play_button = QLabel()
        play_button.setPixmap(self.style().standardIcon(self.style().SP_MediaPlay).pixmap(32, 32))
        controls_layout.addWidget(play_button)

        pause_button = QLabel()
        pause_button.setPixmap(self.style().standardIcon(self.style().SP_MediaPause).pixmap(32, 32))
        controls_layout.addWidget(pause_button)

        stop_button = QLabel()
        stop_button.setPixmap(self.style().standardIcon(self.style().SP_MediaStop).pixmap(32, 32))
        controls_layout.addWidget(stop_button)

        elapsed_time_label = QLabel('00:00')
        elapsed_time_label.setFont(QFont("Arial", 12))
        controls_layout.addWidget(elapsed_time_label)

        progress_bar = QSlider(Qt.Horizontal)
        progress_bar.setFixedHeight(32)
        controls_layout.addWidget(progress_bar)

        remaining_time_label = QLabel('-00:00')
        remaining_time_label.setFont(QFont("Arial", 12))
        controls_layout.addWidget(remaining_time_label)

        volume_label = QLabel('Vol:')
        volume_label.setFont(QFont("Arial", 12))
        controls_layout.addWidget(volume_label)

        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setFixedHeight(32)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.valueChanged.connect(self.update_volume_percentage)
        controls_layout.addWidget(volume_slider)

        self.volume_percentage = QLabel('100%')
        self.volume_percentage.setFont(QFont("Arial", 12))
        controls_layout.addWidget(self.volume_percentage)

        player_layout.addLayout(controls_layout)

        self.epg_data = QTextBrowser()
        self.epg_data.setPlaceholderText('Full EPG data of the current program')
        self.epg_data.setFont(QFont("Arial", 12))
        player_layout.addWidget(self.epg_data)

        self.epg_upcoming_list = []

        player_frame = QFrame()
        player_frame.setLayout(player_layout)
        splitter.addWidget(player_frame)

        splitter.setSizes([1, 1, 1])

        self.setGeometry(100, 100, 1600, 1200)

    def update_volume_percentage(self, value):
        self.volume_percentage.setText(f"{value}%")

    def on_open_m3u_url(self):
        url, ok = QInputDialog.getText(self, 'Open m3u URL', 'Enter the m3u URL:')
        if ok and url:
            # Call the load_m3u_from_url function from the playlist_manager.py
            self.playlist_manager.load_m3u_from_url(url)
            # You may also want to update the GUI after loading the m3u URL
            self.update_gui()

    def on_open_m3u_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open m3u File", "", "m3u Files (*.m3u);;All Files (*)")
        if file_path:
            # Call the load_m3u_from_file function from the playlist_manager.py
            self.playlist_manager.load_m3u_from_file(file_path)
            # You may also want to update the GUI after loading the m3u file
            self.update_gui()

    def on_xtream(self):
        xtream_dialog = XtreamDialog(self)
        result = xtream_dialog.exec_()

        if result == QDialog.Accepted:
            username = xtream_dialog.username.text()
            password = xtream_dialog.password.text()
            server_url = xtream_dialog.server_url.text()

            # Call the load_xtream function from the playlist_manager.py
            self.playlist_manager.load_xtream(username, password, server_url)
            # You may also want to update the GUI after loading the Xtream data
            self.update_gui()

    def get_channels(self):
        return self.channels

    def load_settings(self):
        settings = QSettings("YourOrganizationName", "IPTVPlayer")

        self.update_xtream = settings.value("update_xtream", "")
        self.auto_xtream_update_interval = settings.value("auto_xtream_update_interval", 1, int)

        self.update_m3u_url = settings.value("update_m3u_url", "")
        self.auto_m3u_url_update_interval = settings.value("auto_m3u_url_update_interval", 1, int)

        self.epg_url = settings.value("epg_url", "")
        self.auto_epg_update_interval = settings.value("auto_epg_update_interval", 0.1, float)

        # Apply the settings to your app
        self.playlist_manager.update_xtream(self.update_xtream, self.auto_xtream_update_interval)
        self.playlist_manager.update_m3u_url(self.update_m3u_url, self.auto_m3u_url_update_interval)
        self.epg_manager.update_epg(self.epg_url, self.auto_epg_update_interval)

    def save_settings(self):
        settings = QSettings("YourOrganizationName", "IPTVPlayer")

        settings.setValue("update_xtream", self.update_xtream)
        settings.setValue("auto_xtream_update_interval", self.auto_xtream_update_interval)

        settings.setValue("update_m3u_url", self.update_m3u_url)
        settings.setValue("auto_m3u_url_update_interval", self.auto_m3u_url_update_interval)

        settings.setValue("epg_url", self.epg_url)
        settings.setValue("auto_epg_update_interval", self.auto_epg_update_interval)

    def on_settings(self):
        settings_dialog = SettingsDialog(self)
        
        # Load the current settings into the dialog
        settings_dialog.update_xtream.setText(self.update_xtream)
        settings_dialog.auto_xtream_update_interval.setValue(self.auto_xtream_update_interval)

        settings_dialog.update_m3u_url.setText(self.update_m3u_url)
        settings_dialog.auto_m3u_url_update_interval.setValue(self.auto_m3u_url_update_interval)

        settings_dialog.epg_url.setText(self.epg_url)
        settings_dialog.auto_epg_update_interval.setValue(self.auto_epg_update_interval)
        
        result = settings_dialog.exec_()

        if result == QDialog.Accepted:
            self.update_xtream = settings_dialog.update_xtream.text()
            self.auto_xtream_update_interval = settings_dialog.auto_xtream_update_interval.value()

            self.update_m3u_url = settings_dialog.update_m3u_url.text()
            self.auto_m3u_url_update_interval = settings_dialog.auto_m3u_url_update_interval.value()

            self.epg_url = settings_dialog.epg_url.text()
            self.auto_epg_update_interval = settings_dialog.auto_epg_update_interval.value()

            self.save_settings()
            self.load_settings()

    def update_channel_list(self):
        self.channel_list.clear()
        for channel in self.playlist_manager.get_channels():
            item = QListWidgetItem(channel["name"])
            item.setData(Qt.UserRole, channel)
            self.channel_list.addItem(item)

    def update_gui(self):
        self.update_channel_list()
        # self.update_epg_data()

    def play_channel(self, item):
        channel = item.data(Qt.UserRole)
        media = self.vlc_instance.media_new(channel["url"])
        self.vlc_player.set_media(media)
        self.vlc_player.play()

        # Set the video widget to the player
        self.vlc_player.set_fullscreen(True)
        self.vlc_player.video_set_scale(0)
        self.vlc_player.set_hwnd(self.player_label.winId())

        # Update EPG data
        self.update_epg_data(channel)

    def update_epg_data(self, channel):
        current_program = self.epg_manager.get_current_program(channel["tvg_id"])
        upcoming_programs = self.epg_manager.get_upcoming_programs(channel["tvg_id"])

        if current_program:
            self.epg_now_label.setText(current_program['title'])
            start_time = current_program['start_time'].strftime('%H:%M')
            end_time = current_program['end_time'].strftime('%H:%M')
            self.epg_now_time_label.setText(f"{start_time} - {end_time}")

            # Display full EPG data of the current program
            self.epg_data.setPlainText(current_program['description'])
        else:
            self.epg_now_label.setText("No EPG data available")
            self.epg_now_time_label.setText("")
            self.epg_data.setPlainText("No EPG data available")

        if upcoming_programs:
            self.epg_upcoming_list.clear()
            for program in upcoming_programs:
                start_time = program['start_time'].strftime('%H:%M')
                end_time = program['end_time'].strftime('%H:%M')
                self.epg_upcoming_list.append(f"{start_time} - {end_time} {program['title']}")
        else:
            self.epg_upcoming_list.clear()
            self.epg_upcoming_list.append("No EPG data available")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    iptv_player = IPTVPlayer()
    iptv_player.show()
    sys.exit(app.exec_())
