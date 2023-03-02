import qbittorrentapi
import rich
from platformdirs import *
from pathlib import Path,PurePath
import json


DEFAULT_CONFIG_PATH = site_config_dir("TorrentClientManager")




def init():
    Path(DEFAULT_CONFIG_PATH).mkdir(parents=True, exist_ok=True)
    config_file = Path(DEFAULT_CONFIG_PATH,'config.json')
    print(config_file)
    if config_file.is_file():
        print('ok')
    else:
        json_object = [{"host":"localhost","port":8080,"username":"admin","password":"adminadmin"}]
        with open(config_file, "w") as outfile:
            json.dump(json_object,outfile)
    """
    # Check if json config exists, if not create it and exit with info message
    client = qbittorrentapi.Client(
        host='localhost',
        port=8080,
        username='admin',
        password='adminadmin'
    )
    try:
        client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)
        """

init()