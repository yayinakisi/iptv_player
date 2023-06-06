import requests
import json

# Replace these with your Xtream Codes API details
xtream_url = 'sezonhd.xyz:8080'
username = 'ysyinakisi'
password = 'mKpYNKZZSx'
headers = {
    'Accept': '*/*',
    'Host': xtream_url,
    'User-Agent': 'TiviMate/4.6.1 (Linux; Android 11)',
    # 'User-Agent': 'iPlayTV/1.1.0',
    'Connection': 'keep-alive',
    'Accept-Language': 'en-TR;q=1, tr-TR;q=0.9',
}
api = f'http://{xtream_url}/player_api.php?username={username}&password={password}'

# Request user info, which includes the user status and other details
user_info = requests.get(f'{api}&action=user&username={username}&password={password}', headers=headers)
user_info = json.loads(user_info.text)

# If user status is active then proceed
if user_info['user_info']['status'] == 'Active':
    # Get live categories
    live_categories = requests.get(f'{api}&action=get_live_categories', headers=headers)
    live_categories = json.loads(live_categories.text)

    # Open a new M3U file and write the header
    with open('output.m3u', 'w', encoding="utf-8") as f:
        f.write('#EXTM3U\n')

        # For each category, get the streams and write them to the M3U file
        for category in live_categories:
            cat_id = category['category_id']
            cat_name = category['category_name']

            streams = requests.get(f'{api}&action=get_live_streams&category_id={cat_id}', headers=headers)
            streams = json.loads(streams.text)

            for stream in streams:
                stream_id = stream['stream_id']
                epg_channel_id = stream['epg_channel_id']
                stream_logo = stream.get('stream_icon', '')  # assuming the stream icon is available
                stream_name = stream['name']
                stream_url = f'http://{xtream_url}/live/{username}/{password}/{stream_id}'

                f.write(f'#EXTINF:-1 tvg-id="{epg_channel_id}" tvg-name="{stream_name}" tvg-logo="{stream_logo}" group-title="{cat_name}",{stream_name}\n{stream_url}\n')

print('M3U file has been written to output.m3u')
