import sys
import vlc
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QAction, QVBoxLayout, QHBoxLayout, QSplitter, QTreeView, QListView, QLabel, QStyle,
                             QFrame, QTextBrowser, QSlider, QStatusBar, QSizePolicy, QTimeEdit, QLabel, QInputDialog, QFileDialog, QToolButton, QStyleOptionSlider,
                             QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QListWidget, QMessageBox, QPushButton, QComboBox)
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings
from playlist_manager import PlaylistManager
from epg_manager import EPGManager
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QSlider


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
        
        self.channel_list = QListWidget() 
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

        # First part: Categories and Channels
        self.group_list = QListWidget()
        self.group_list.setFont(QFont("Arial", 12))
        splitter.addWidget(self.group_list)
        self.group_list.itemClicked.connect(self.update_channel_list)

        # Second part: Channels
        self.channel_list.setFont(QFont("Arial", 12))
        splitter.addWidget(self.channel_list)
        self.channel_list.itemDoubleClicked.connect(self.play_channel)

        # Third part: EPG Information
        epg_info = QFrame()
        epg_layout = QVBoxLayout(epg_info)
        epg_layout.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(epg_info)

        # Add the following lines to create the new QListWidget
        self.epg_all_programs_list = QListWidget()
        self.epg_all_programs_list.setFont(QFont("Arial", 12))
        epg_layout.addWidget(self.epg_all_programs_list)

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

        # Fourth part: Player and EPG data of the current program
        player_layout = QVBoxLayout()

        self.player_label = QLabel()
        self.player_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.player_label.setStyleSheet("QLabel { background-color : black; }")
        self.player_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        player_layout.addWidget(self.player_label)

        # Initialize the VLC player
        self.vlc_instance = vlc.Instance('--no-xlib')
        self.vlc_player = self.vlc_instance.media_player_new()

        # Connect the channel list click event to the play_channel function
        self.channel_list.itemDoubleClicked.connect(self.play_channel)

        # EPG update timer
        self.epg_update_timer = QTimer(self)
        self.epg_update_timer.timeout.connect(self.update_gui)
        self.epg_update_timer.start(60000)  # Update EPG every minute

        # Player controls
        controls_layout = QHBoxLayout()

        play_button = QToolButton()
        play_button.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        play_button.clicked.connect(self.play)
        controls_layout.addWidget(play_button)

        pause_button = QToolButton()
        pause_button.setIcon(self.style().standardIcon(self.style().SP_MediaPause))
        pause_button.clicked.connect(self.pause)
        controls_layout.addWidget(pause_button)

        stop_button = QToolButton()
        stop_button.setIcon(self.style().standardIcon(self.style().SP_MediaStop))
        stop_button.clicked.connect(self.stop)
        controls_layout.addWidget(stop_button)

        prev_channel_button = QToolButton()
        prev_channel_button.setIcon(self.style().standardIcon(self.style().SP_ArrowLeft))
        prev_channel_button.clicked.connect(self.prev_channel)
        controls_layout.addWidget(prev_channel_button)

        next_channel_button = QToolButton()
        next_channel_button.setIcon(self.style().standardIcon(self.style().SP_ArrowRight))
        next_channel_button.clicked.connect(self.next_channel)
        controls_layout.addWidget(next_channel_button)

        self.remaining_time_label = QLabel()
        self.remaining_time_label.setAlignment(Qt.AlignRight)
        self.remaining_time_label.setText("-00:00")
        controls_layout.addWidget(self.remaining_time_label)
        self.elapsed_time_label = QLabel('00:00')
        self.elapsed_time_label.setFont(QFont("Arial", 12))
        controls_layout.addWidget(self.elapsed_time_label)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.seek)
        controls_layout.addWidget(self.position_slider)

        self.position_update_timer = QTimer(self)
        self.position_update_timer.timeout.connect(self.update_position_slider)
        self.position_update_timer.start(1000)


        # Fullscreen toggle button
        self.fullscreen_button = QPushButton("Toggle Fullscreen", self)
        controls_layout.addWidget(self.fullscreen_button)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        volume_label = QLabel('Vol:')
        volume_label.setFont(QFont("Arial", 12))
        controls_layout.addWidget(volume_label)

        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setFixedHeight(32)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.valueChanged.connect(self.set_volume)
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

        splitter.setSizes([20, 20, 30, 30])
        self.setGeometry(100, 100, 1600, 1200)


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
            username = "M6JRJyi6"#xtream_dialog.username.text()
            password = "i8h2wUXX"#xtream_dialog.password.text()
            server_url = "http://epgxtream.xyz"#xtream_dialog.server_url.text()

            # Call the load_xtream function from the playlist_manager.py
            self.playlist_manager.load_xtream(server_url, username, password)
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

    def update_channel_list(self, group_item):
        self.channel_list.clear()
        category = group_item.data(Qt.UserRole)
        channels = category["channels"]
        for channel in channels:
            channel_item = QListWidgetItem("  " + channel["name"])
            channel_item.setData(Qt.UserRole, channel)
            self.channel_list.addItem(channel_item)


    def update_gui(self):
        self.group_list.clear()
        categories = self.playlist_manager.get_categories()
        for category in categories:
            group_item = QListWidgetItem(category["name"])
            group_item.setData(Qt.UserRole, category)
            self.group_list.addItem(group_item)

    def play_channel(self, item):
        channel = item.data(Qt.UserRole)
        media = self.vlc_instance.media_new(channel["url"])
        self.vlc_player.set_media(media)
        self.vlc_player.play()

        # Set the custom video widget (QVideoWidget) to the VLC player
        self.vlc_player.set_fullscreen(True)
        self.vlc_player.video_set_scale(0)
        self.vlc_player.set_hwnd(int(self.player_label.winId()))

        # Connect the endReached signal to the update_time_labels method
        self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.update_time_labels)


    def update_epg_data(self, channel):
        current_program, next_program, all_programs = self.epg_manager.get_current_next_all_programs(channel["tvg_id"])

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

        if next_program:
            self.epg_next_label.setText(next_program['title'])
            start_time = next_program['start_time'].strftime('%H:%M')
            end_time = next_program['end_time'].strftime('%H:%M')
            self.epg_next_time_label.setText(f"{start_time} - {end_time}")
        else:
            self.epg_next_label.setText("No EPG data available")
            self.epg_next_time_label.setText("")

        if all_programs:
            self.epg_all_programs_list.clear()
            for program in all_programs:
                program_item = QListWidgetItem(program)
                self.epg_all_programs_list.addItem(program_item)
        else:
            self.epg_all_programs_list.clear()
            no_epg_item = QListWidgetItem("No EPG data available")
            self.epg_all_programs_list.addItem(no_epg_item)

    def play(self):
        if self.vlc_player.is_playing():
            self.vlc_player.pause()
        else:
            self.vlc_player.play()

    def pause(self):
        self.vlc_player.pause()

    def stop(self):
        self.vlc_player.stop()

    def prev_channel(self):
        current_row = self.channel_list.currentRow()
        if current_row > 0:
            self.channel_list.setCurrentRow(current_row - 1)
            self.play_channel(self.channel_list.item(current_row - 1))

    def next_channel(self):
        current_row = self.channel_list.currentRow()
        if current_row < self.channel_list.count() - 1:
            self.channel_list.setCurrentRow(current_row + 1)
            self.play_channel(self.channel_list.item(current_row + 1))

    def toggle_fullscreen(self):
        is_fullscreen = self.vlc_player.get_fullscreen()
        self.vlc_player.set_fullscreen(not is_fullscreen)

    def update_time_labels(self, *args):
        elapsed_time = self.vlc_player.get_time() // 1000
        remaining_time = (self.vlc_player.get_length() - self.vlc_player.get_time()) // 1000

        elapsed_minutes, elapsed_seconds = divmod(elapsed_time, 60)
        remaining_minutes, remaining_seconds = divmod(remaining_time, 60)

        self.elapsed_time_label.setText(f'{elapsed_minutes:02d}:{elapsed_seconds:02d}')
        self.remaining_time_label.setText(f'-{remaining_minutes:02d}:{remaining_seconds:02d}')

        # Update the progress bar value
        self.position_slider.setValue(int((elapsed_time / (self.vlc_player.get_length() // 1000)) * 1000))

        if self.vlc_player.get_state() == vlc.State.Ended:
            self.position_slider.setValue(0)
            self.elapsed_time_label.setText('00:00')
            self.remaining_time_label.setText('-00:00')


    def update_volume_percentage(self, value):
        self.volume_percentage.setText(f"{value}%")
        self.vlc_player.audio_set_volume(value)

    def closeEvent(self, event):
        self.vlc_player.stop()
        self.epg_update_timer.stop()
        self.save_settings()
        super().closeEvent(event)

    def set_volume(self, value):
        self.vlc_player.audio_set_volume(value)
        self.volume_percentage.setText(f"{value}%")

    def seek(self, value):
        self.vlc_player.set_fullscreen(False)
        self.vlc_player.set_time(int(value * self.vlc_player.get_length() / 1000))
        self.update_time_labels_while_seeking(value)

    def update_position_slider(self):
        media = self.vlc_player.get_media()
        if media is not None:
            media_duration = media.get_duration()
            if media_duration > 0:
                position = int(self.vlc_player.get_time() * 100 / media_duration)
                self.position_slider.setValue(position)



    def update_time_labels_while_seeking(self, value):
        media = self.vlc_player.get_media()
        if media is not None:
            media_duration = media.get_duration()
            elapsed_time = int(value * media_duration / 100)
            remaining_time = media_duration - elapsed_time

            elapsed_minutes = elapsed_time // 60000
            elapsed_seconds = (elapsed_time % 60000) // 1000
            self.elapsed_time_label.setText(f'{elapsed_minutes:02d}:{elapsed_seconds:02d}')

            remaining_minutes = remaining_time // 60000
            remaining_seconds = (remaining_time % 60000) // 1000
            self.remaining_time_label.setText(f'-{remaining_minutes:02d}:{remaining_seconds:02d}')








if __name__ == '__main__':
    app = QApplication(sys.argv)
    iptv_player = IPTVPlayer()
    iptv_player.show()
    sys.exit(app.exec_())
