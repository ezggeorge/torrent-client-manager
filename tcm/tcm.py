import qbittorrentapi
import rich
from platformdirs import *
from pathlib import Path, PurePath
import yaml
import argparse
import io

DEFAULT_CONFIG_PATH = site_config_dir("TorrentClientManager")

parser = argparse.ArgumentParser(
    prog='Torrent Client Manager',
    description='CLI Tool to help you manage many torrents across different clients',
    epilog='Made with ❤')

parser.add_argument('-dr', '--dry-run',
                    action='store_true', help='Does not interact with torrent clients.')
parser.add_argument('-k', '--keep-files',
                    action='store_true', help='Does not delete files when removing torrents.')
parser.add_argument('-c', '--clean',
                    action='store_true', help='Removes torrents that are not registered with their trackers.')
parser.add_argument('-autotag',
                    action='store_true', help='Automatically tags your torrents based on filenames.')
args = parser.parse_args()


def init_config():
    Path(DEFAULT_CONFIG_PATH).mkdir(parents=True, exist_ok=True)
    config_file = Path(DEFAULT_CONFIG_PATH, 'config.yaml')
    print(config_file)
    # Check if json config exists, if not create it and exit with info message
    if config_file.is_file():
        with open(config_file,"r") as user_file:
            config_parsed = yaml.safe_load(user_file)
            return config_parsed

    else:
        data = {"tracker_messages": ["Torrent not registered with this tracker."],
                "clients": [{"type":"qbittorrent","host": "localhost", "port": 8080, "username": "admin", "password": "adminadmin"},
                            {"type":"transmission","host": "localhost", "port": 8080, "username": "admin", "password": "adminadmin"},
                            {"type":"deluge","host": "localhost", "port": 8080, "username": "admin", "password": "adminadmin"},
                            {"type":"rutorrent","host": "localhost", "port": 8080, "username": "admin", "password": "adminadmin"}]}
        with io.open(config_file, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
        rich.print(
            f"Config File not detected, create a template at {config_file}\nEdit this file with your qbittorrent credentials.\nFor multiple clients, add another dictionary")




class QBIT():
    def __init__(self,host,username,password,port,tracker_codes):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.tracker = tracker_codes
        self.client = qbittorrentapi.Client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            REQUESTS_ARGS={'timeout': (5, 30)},
            SIMPLE_RESPONSES=True,
        )

    def check_connection(self):
        try:
            self.client.auth_log_in()
            info = {"qbit_version":self.client.app.version,"qbit_webapi_version":self.client.app.web_api_version,"build_info": self.client.app.build_info.items(),"torrents_info":self.client.torrents_info()}
            return info
        except qbittorrentapi.LoginFailed as e:
            raise Exception("Qbittorrent : Could not establish connection to the WEBGUI interface.")
    

    def clean_torrents(self,config,dry_run:bool=False,keep_files:bool=False):
        dead = []
        for torrent in self.client.torrents_info():
            temp = self.client.torrents_trackers(torrent_hash=torrent.hash)
            if temp[3]['msg'] == 'Torrent not registered with this tracker.':
                rich.print(f'Detected {torrent.name} with hash {torrent.hash}')
                dead.append(torrent.hash)
        if not dry_run:
            if keep_files:
                print('Please wait, removing torrents and deleting files....')
                self.client.torrents_delete(delete_files=True, torrent_hashes=dead)
            else:
                print('Please wait, removing torrents without deleting files....')
                self.client.torrents_delete(delete_files=False, torrent_hashes=dead)



    def auto_tag(self,dry_run:bool=False):
        pass


qbit = QBIT(host="192.168.1.10",username="qbittorrent",password="dietpi",port=1340,tracker_codes=init_config()['tracker_messages'])
print(qbit.check_connection())