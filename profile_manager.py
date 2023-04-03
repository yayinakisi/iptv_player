import json
import os

class ProfileManager:
    def __init__(self, profiles_file='profiles.json'):
        self.profiles_file = profiles_file
        self.profiles = []

        if os.path.exists(self.profiles_file):
            self.load_profiles()
        else:
            self.initialize_profiles()

    def initialize_profiles(self):
        self.profiles = []
        self.save_profiles()

    def load_profiles(self):
        with open(self.profiles_file, 'r') as f:
            self.profiles = json.load(f)

    def save_profiles(self):
        with open(self.profiles_file, 'w') as f:
            json.dump(self.profiles, f, indent=4)

    def add_profile(self, profile):
        self.profiles.append(profile)
        self.save_profiles()

    def remove_profile(self, profile_name):
        self.profiles = [profile for profile in self.profiles if profile['name'] != profile_name]
        self.save_profiles()

    def update_profile(self, profile_name, updated_profile):
        for profile in self.profiles:
            if profile['name'] == profile_name:
                profile.update(updated_profile)
                self.save_profiles()
                break

    def get_profile(self, profile_name):
        for profile in self.profiles:
            if profile['name'] == profile_name:
                return profile
        return None

    def get_all_profiles(self):
        return self.profiles
