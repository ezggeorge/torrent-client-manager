import qbittorrentapi
import rich
from platformdirs import *
from pathlib import Path, PurePath
import yaml
import argparse
import io
import time
from rich.live import Live
from rich.table import Table
import math

DEFAULT_CONFIG_PATH = site_config_dir("TorrentClientManager")







# https://stackoverflow.com/a/14822210
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])



def init_config():
    Path(DEFAULT_CONFIG_PATH).mkdir(parents=True, exist_ok=True)
    config_file = Path(DEFAULT_CONFIG_PATH, 'config.yaml')
    # Check if json config exists, if not create it and exit with info message
    if config_file.is_file():
        with open(config_file,"r") as user_file:
            config_parsed = yaml.safe_load(user_file)
            return config_parsed

    else:
        data = {"tracker_messages": ["Torrent not registered with this tracker."],
                "clients": [{"connect":False ,"type":"qbittorrent","host": "localhost", "port": 8080, "username": "admin", "password": "adminadmin"},
                            ]}
        with io.open(config_file, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
        rich.print(
            f"[bold yellow]Config File not detected, create a template at {config_file}\nEdit this file with your qbittorrent credentials.")
        return False




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
        )

    def check_connection(self):
        try:
            self.client.auth_log_in()
            info = {"qbit_version":self.client.app.version,"qbit_webapi_version":self.client.app.web_api_version,"build_info": self.client.app.build_info.items(),"torrents_info":self.client.torrents_info()}
            return info
        except qbittorrentapi.LoginFailed as e:
            raise Exception("[bold red]Qbittorrent : Could not establish connection to the WEBGUI interface.")
    

    def clean_torrents(self,config,dry_run:bool=False,keep_files:bool=False):

        dead = []
        table = Table()

        with Live(table, refresh_per_second=4):
            table.add_column("[bold yellow]Dead")
            table.add_column("[bold yellow]Hash")
            table.add_column("[bold yellow]Name")
            table.add_column("[bold yellow]Size")
            for torrent in self.client.torrents_info():
                temp = self.client.torrents_trackers(torrent_hash=torrent.hash)
                if temp[3]['msg'] in config["tracker_messages"]:
                    dead.append(torrent.hash)
                    table.add_row("[GREEN]✓",str(torrent.hash), str(torrent.name),convert_size(torrent.size))
                else:
                    table.add_row("[red]X",str(torrent.hash), str(torrent.name), convert_size(torrent.size))
        if not dead and not dry_run:
            if keep_files:
                rich.print('[bold yellow]Please wait, removing torrents and deleting files....')
                self.client.torrents_delete(delete_files=True, torrent_hashes=dead)
            else:
                rich.print('[bold yellow]Please wait, removing torrents without deleting files....')
                self.client.torrents_delete(delete_files=False, torrent_hashes=dead)
        else:
            rich.print("There is nothing to do...")


    def auto_tag(self,dry_run:bool=False):
        pass





if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog='Torrent Client Manager',
    description='CLI Tool to help you manage your torrents.',
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
    config = init_config()
    if not config:
        rich.print("[bold red]Exiting...")
        exit()
    
    qbit = QBIT(host="192.168.1.10",username="qbittorrent",password="dietpi",port=1340,tracker_codes=config['tracker_messages'])
    status = qbit.check_connection()
    rich.print(f"[bold blue]Qbittorrent Version : [bold red]{status['qbit_version']}")
    rich.print(f"[bold blue]Qbittorrent WebAPI Version : [bold red]{status['qbit_version']}")
    rich.print(f"[bold blue]Torrents detected : [bold red]{len(status['torrents_info'])}")
    
    qbit.clean_torrents(config=init_config(),dry_run=True)