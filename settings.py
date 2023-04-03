import json
import os

class Settings:
    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.settings = {}

        if os.path.exists(self.settings_file):
            self.load_settings()
        else:
            self.initialize_settings()

    def initialize_settings(self):
        default_settings = {
            'xtream_update_interval': 24,
            'm3u_update_interval': 24,
            'epg_update_interval': 24
        }
        self.settings = default_settings
        self.save_settings()

    def load_settings(self):
        with open(self.settings_file, 'r') as f:
            self.settings = json.load(f)

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_setting(self, key):
        return self.settings.get(key, None)
