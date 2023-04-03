import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from PyQt5.QtCore import QTimer


class EPGManager:
    def __init__(self):
        self.epg_data = {}

    def load_epg_from_file(self, epg_file_path):
        try:
            with open(epg_file_path, 'r', encoding='utf-8') as epg_file:
                epg_content = epg_file.read()
                self.parse_epg(epg_content)
        except FileNotFoundError:
            print(f"EPG file not found: {epg_file_path}")
            return False
        except Exception as e:
            print(f"Error loading EPG from file: {str(e)}")
            return False

    def load_epg_from_url(self, epg_url):
        try:
            import requests
            response = requests.get(epg_url)
            if response.status_code == 200:
                epg_content = response.text
                self.parse_epg(epg_content)
            else:
                print(f"Error loading EPG from URL: {epg_url}. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error loading EPG from URL: {str(e)}")
            return False

    def parse_epg(self, epg_content):
        try:
            root = ET.fromstring(epg_content)
            for channel in root.findall('channel'):
                channel_id = channel.get('id')
                display_name = channel.find('display-name').text
                self.epg_data[channel_id] = {'name': display_name, 'programs': []}

            for program in root.findall('programme'):
                channel_id = program.get('channel')
                start_time = datetime.strptime(program.get('start'), "%Y%m%d%H%M%S %z")
                end_time = datetime.strptime(program.get('stop'), "%Y%m%d%H%M%S %z")
                title = program.find('title').text
                desc = program.find('desc')
                description = desc.text if desc is not None else ''

                if channel_id in self.epg_data:
                    self.epg_data[channel_id]['programs'].append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'title': title,
                        'description': description
                    })

        except Exception as e:
            print(f"Error parsing EPG data: {str(e)}")
            return False

    def get_current_program(self, channel_id):
        if channel_id not in self.epg_data:
            return None

        now = datetime.now()
        for program in self.epg_data[channel_id]['programs']:
            if program['start_time'].replace(tzinfo=None) <= now <= program['end_time'].replace(tzinfo=None):
                return program
        return None

    def get_upcoming_programs(self, channel_id, limit=5):
        if channel_id not in self.epg_data:
            return []

        now = datetime.now()
        upcoming_programs = []
        for program in self.epg_data[channel_id]['programs']:
            if program['start_time'].replace(tzinfo=None) > now:
                upcoming_programs.append(program)
                if len(upcoming_programs) == limit:
                    break

        return upcoming_programs

    def update_epg(self, epg_url, auto_epg_update_interval):
        self.epg_url = epg_url
        self.auto_epg_update_interval = auto_epg_update_interval

        if self.epg_url:
            self.load_epg_from_url(self.epg_url)

        if self.auto_epg_update_interval > 0:
            QTimer.singleShot(
                int(self.auto_epg_update_interval * 1000),
                lambda: self.update_epg(self.epg_url, self.auto_epg_update_interval)
            )

    def load_epg(self, epg_url):
        self.epg_url = epg_url
        if self.epg_url:
            self.load_epg_from_url(self.epg_url)