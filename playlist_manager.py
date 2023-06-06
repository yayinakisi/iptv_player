import requests
import json
import os
import time
import re
from typing import List
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QTimer


class PlaylistManager:
    def __init__(self):
        self.channels = []
        self.categories = []

    def load_m3u_from_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                m3u_content = file.read()
            self.parse_m3u(m3u_content)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error while loading M3U file: {e}")

    def load_m3u_from_url(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            m3u_content = response.text
            self.parse_m3u(m3u_content)
        except requests.exceptions.RequestException as e:
            print(f"Error while loading M3U from URL: {e}")
        except Exception as e:
            print(f"Error while processing M3U content from URL: {e}")

    def load_xtream(self, server_url: str, username: str, password: str):
        try:
            # Get user info
            user_info_url = f"{server_url}/player_api.php?username={username}&password={password}&action=user&output=json"
            response = requests.get(user_info_url)
            response.raise_for_status()
            user_info = response.json()

            if user_info.get("user_info") and user_info["user_info"].get("status") == "Active":
                # Get live categories
                live_categories_url = f"{server_url}/player_api.php?username={username}&password={password}&action=get_live_categories&output=json"
                response = requests.get(live_categories_url)
                response.raise_for_status()
                live_categories = response.json()

                # Get VOD categories
                vod_categories_url = f"{server_url}/player_api.php?username={username}&password={password}&action=get_vod_categories&output=json"
                response = requests.get(vod_categories_url)
                response.raise_for_status()
                vod_categories = response.json()

                # Get series categories
                series_categories_url = f"{server_url}/player_api.php?username={username}&password={password}&action=get_series_categories&output=json"
                response = requests.get(series_categories_url)
                response.raise_for_status()
                series_categories = response.json()

                # Process the categories and channels
                self.process_xtream_categories_and_channels(live_categories, vod_categories, series_categories, server_url, username, password)
            else:
                print("Error: Xtream account is not active or invalid.")

        except requests.exceptions.RequestException as e:
            print(f"Error while loading Xtream: {e}")
        except Exception as e:
            print(f"Error while processing Xtream content: {e}")

    def parse_m3u(self, m3u_content):
        channels = []
        categories_dict = {}  # Create a dictionary to store categories

        lines = m3u_content.splitlines()
        for ind, line in enumerate(lines):
            line = line.strip()

            if line.startswith("#EXTM3U"):
                continue

            if line.startswith("#EXTINF"):
                # Extract group and channel information
                tvgid_match = re.search(r'tvg-id="(.*?)"', line)
                group_match = re.search(r'group-title="(.*?)"', line)
                name_match = re.search(r'tvg-name="(.*?)"', line)
                logo_match = re.search(r'tvg-logo="(.*?)"', line)

                if group_match:
                    current_group = group_match.group(1)
                #this breaks loading m3u from file and url. #EXGRP
                # else:
                #     current_group = lines[ind+1].split(":")[-1]
                #     # Add the group to the dictionary if it's not already there
                    if current_group not in categories_dict:
                        categories_dict[current_group] = []

                channel = {
                    "name": name_match.group(1) if name_match else "",
                    "logo": logo_match.group(1) if logo_match else "",
                    "group": current_group,
                    "tvg_id": tvgid_match.group(1) if tvgid_match else "",
                }
                channels.append(channel)
                # Add the channel to the corresponding group
                if current_group in categories_dict:
                    categories_dict[current_group].append(channel)

            elif line.startswith("http"):
                # Add the stream URL to the last channel
                channels[-1]["url"] = line

        self.channels = channels
        self.categories = [{"name": group, "channels": channels} for group, channels in categories_dict.items()]


    def parse_epg(self, epg_content):
        epg = {}
        root = ET.fromstring(epg_content)

        for channel in root.findall("channel"):
            channel_id = channel.get("id")
            display_name = channel.find("display-name")
            icon = channel.find("icon")

            epg[channel_id] = {
                "name": display_name.text if display_name is not None else "",
                "logo": icon.get("src") if icon is not None else "",
                "programs": []
            }

        for program in root.findall("programme"):
            channel_id = program.get("channel")
            start_time = program.get("start")
            stop_time = program.get("stop")
            title = program.find("title")
            desc = program.find("desc")

            epg[channel_id]["programs"].append({
                "start": start_time,
                "stop": stop_time,
                "title": title.text if title is not None else "",
                "description": desc.text if desc is not None else ""
            })

        self.epg = epg


    def save_profile(self, profile_name, profile_data):
        profiles_directory = "profiles"
        if not os.path.exists(profiles_directory):
            os.makedirs(profiles_directory)

        profile_file = os.path.join(profiles_directory, f"{profile_name}.json")
        with open(profile_file, "w") as file:
            json.dump(profile_data, file)

    def load_profile(self, profile_name):
        profiles_directory = "profiles"
        profile_file = os.path.join(profiles_directory, f"{profile_name}.json")

        if os.path.exists(profile_file):
            with open(profile_file, "r") as file:
                profile_data = json.load(file)
                return profile_data
        else:
            return None

    def process_xtream_categories_and_channels(self, live_categories, vod_categories, series_categories, server_url, username, password):
        categories = []
        channels = []

        try:
            # Process live categories
            for category in live_categories:
                category_id = category.get("category_id")
                category_name = category.get("category_name")
                

                # Get live channels for this category
                live_channels_url = f"{server_url}/player_api.php?username={username}&password={password}&action=get_live_streams&category_id={category_id}&output=json"
                response = requests.get(live_channels_url)
                response.raise_for_status()
                live_channels = response.json()

                for channel in live_channels:
                    channel_info = {
                        "id": channel.get("stream_id"),
                        "name": channel.get("name"),
                        "logo": channel.get("stream_icon"),
                        "category_id": category_id
                    }
                    channels.append(channel_info)
                    categories.append({"id": category_id, "name": category_name, "type": "live", "channels": channel_info})

            # Process VOD categories
            for category in vod_categories:
                category_id = category.get("category_id")
                category_name = category.get("category_name")
                categories.append({"id": category_id, "name": category_name, "type": "vod"})

                # Get VOD channels for this category
                vod_channels_url = f"{server_url}/player_api.php?username={username}&password={password}&action=get_vod_streams&category_id={category_id}&output=json"
                response = requests.get(vod_channels_url)
                response.raise_for_status()
                vod_channels = response.json()

                for channel in vod_channels:
                    channel_info = {
                        "id": channel.get("stream_id"),
                        "name": channel.get("name"),
                        "logo": channel.get("stream_icon"),
                        "category_id": category_id
                    }
                    channels.append(channel_info)

            # Process series categories
            for category in series_categories:
                category_id = category.get("category_id")
                category_name = category.get("category_name")
                categories.append({"id": category_id, "name": category_name, "type": "series"})

                # Get series channels for this category
                series_channels_url = f"{server_url}/player_api.php?username={username}&password={password}&action=get_series&category_id={category_id}&output=json"
                response = requests.get(series_channels_url)
                response.raise_for_status()
                series_channels = response.json()

                for channel in series_channels:
                    channel_info = {
                        "id": channel.get("series_id"),
                        "name": channel.get("name"),
                        "logo": channel.get("cover"),
                        "category_id": category_id
                    }
                    channels.append(channel_info)

            self.categories = categories
            self.channels = channels

        except requests.exceptions.RequestException as e:
            print(f"Error while loading channels for Xtream categories: {e}")
        except Exception as e:
            print(f"Error while processing Xtream channels: {e}")

    def update_xtream(self, xtream_credentials, update_interval):
        self.xtream_credentials = xtream_credentials
        self.auto_xtream_update_interval = update_interval
        
        if len(self.xtream_credentials) == 3:
            base_url, username, password = self.xtream_credentials
            self.load_xtream(base_url, username, password)

        # Schedule automatic updates
        if self.auto_xtream_update_interval > 0:
            QTimer.singleShot(
                int(self.auto_xtream_update_interval * 1000),
                lambda: self.update_xtream(self.xtream_credentials, self.auto_xtream_update_interval)  # Update this line
            )

    def update_m3u_url(self, m3u_url, auto_m3u_update_interval):
        self.m3u_url = m3u_url
        self.auto_m3u_update_interval = auto_m3u_update_interval

        if self.m3u_url:  # Add this line
            self.load_m3u_from_url(self.m3u_url)

        # Schedule automatic updates
        if self.auto_m3u_update_interval > 0:
            QTimer.singleShot(
                int(self.auto_m3u_update_interval * 1000),
                lambda: self.update_m3u_url(self.m3u_url, self.auto_m3u_update_interval)
            )

    def get_channels(self):
        return self.channels

    def get_categories(self):  # Add this method
        return self.categories

class Channel:
    def __init__(self, name: str, url: str, logo: str, epg_data: List[dict]):
        self.name = name
        self.url = url
        self.logo = logo
        self.epg_data = epg_data
