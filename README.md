# torrent-client-manager
 Torrent Client Manager is a CLI utility for managing torrent client instances

# Installation

requirements
```
pip install pyyaml rich qbittorrent-api argparse platformdirs
```

and now you can do
```
pip install torrentcm
```

# Usage
```
-dr , --dry-run # Does not interact with torrent clients.

-k' , --keep-files # Does not delete files when removing torrents.

-c , --clean #Removes torrents with tracker codes matching the list in the config file.
```
