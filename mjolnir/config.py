import logging
import os
from configparser import ConfigParser

_config_path = os.path.expanduser('~/.mjolnir_prot')
_config_file = f'{_config_path}/config.ini'


config = {
    'default_proc_env_location': './mjolnir_db/processing/',
    'default_entry_db_location': './mjolnir_db/prot.db',
    'default_seq_db_location': './mjolnir_db/seq.db',
    'commit_frequency': 50000,
    'enable_compression_entries': False,
    'enable_compression_seq': 'False',
    'sqlite_zsdt_vfs_path': '~/.mjolnir_prot/zsdt_vfs.so',
}


def init():
    """Loads config from a file, or creates it."""
    if not os.path.exists(_config_file):
        _create_config()

    config_parser = ConfigParser()
    config_parser.read(_config_file)
    for section in config_parser.sections():
        for key, value in config_parser.items(section):
            config[key] = value

    for field, func in post_load.items():
        if field in config:
            config[field] = func(config[field])


def _create_config():
    if not os.path.exists(_config_path):
        os.makedirs(_config_path)

    config_file = open(_config_file, 'w')
    config_file.write(_default_config)
    config_file.close()
    logging.info(f'Created config file at {_config_file}')


_default_config = """[mjolnir]

[Database]
# Entry database: DB containing all entries and their metadata
default_entry_db_location = ./mjolnir_db/prot.db

# Sequence database: Used as part of processing entries
default_seq_db_location = ./mjolnir_db/seq.db
commit_frequency = 50000

# To enable compression of SQLite, you need the `sqlite_zstd_vfs` extension;
# Building instructions can be found on: https://github.com/mlin/sqlite_zstd_vfs
enable_compression_entries = False
enable_compression_seq = False
sqlite_zsdt_vfs_path = ~/.mjolnir_prot/zsdt_vfs.so

[Processing]

default_proc_env_location = ./mjolnir_db/processing/


# Most likely you want to use Uniclust (https://uniclust.mmseqs.com/)
# The path should point to the folder containing ffdata / ffindex files.
# Other databases are also available, see https://github.com/soedinglab/hh-suite for details.
hh_suite_db_location = ./hh-suite/

# Set the upper limit on processors to use for processing.
"""

post_load = {'commit_frequency': int, 'enable_compression_entries': lambda x: x.casefold() == 'true',
             'enable_compression_results': lambda x: x.casefold() == 'true', }

init()

if __name__ == '__main__':
    print(config)
