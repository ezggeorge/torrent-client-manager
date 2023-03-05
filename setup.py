from setuptools import setup

setup(
    name='torrentcm',
    version='0.0.6',    
    description='Torrent Client Manager is a CLI utility for managing torrent client instances.',
    url='https://github.com/ezggeorge/torrent-client-manager',
    author='EZGGeorge',
    license='BSD 2-clause',
    
    install_requires=['argparse','rich','qbittorrent-api','platformdirs','pyyaml',
                      ],
    entry_points = {
        'console_scripts': ['torrentcm=torrentcm.torrentcm:main'],
    }
)
