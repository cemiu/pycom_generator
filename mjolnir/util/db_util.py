import logging
import os
import sqlite3
import sys

from mjolnir import config
from .info_util import InfoUtil

_byte_info_cutoff = 1024 ** 3  # 1 GB


class DBUtil:
    def __init__(self, db_file, db_model, init=False, compression=True, read_only=False, commit_frequency=1):
        self.db_file = db_file
        self.db_model = db_model
        if not os.path.exists(db_file) and not init:
            raise Exception(f'Database {db_file} does not exist. Use [db --init] to create a new database.')

        self.last_commit = 0
        self.commit_frequency = commit_frequency

        self.con = _create_db(db_file, db_model, compression) if init else _load_db(db_file, compression, read_only)
        self.c = self.con.cursor()

        self.print_info = self.c.execute(
            'SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size()'
        ).fetchone()[0] > _byte_info_cutoff

    def insert(self, query, data):
        self.c.execute(query, data)
        self.soft_commit()

    def insert_many(self, query, data):
        if not data:
            return
        self.c.executemany(query, data)

    def indices_create(self):
        """Creates all indices in DB, from model."""
        _indices_create(self.c, self.db_model, self.print_info)
        self.hard_commit()

    def indices_drop(self):
        """Drops all indices in DB except for auto-indices."""
        _indices_drop(self.c, self.print_info)
        self.hard_commit()

    def calc_size(self):
        byte_count = self.print_info = self.c.execute(
            'SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size()'
        ).fetchone()[0]
        self.print_info = byte_count > _byte_info_cutoff
        return byte_count

    def soft_commit(self):
        """Commit to database if commit_frequency has been reached."""
        self.last_commit += 1
        if self.last_commit >= self.commit_frequency:
            self.hard_commit()

    def hard_commit(self):
        """Commit to database."""
        self.con.commit()
        self.last_commit = 0
        self.calc_size()

    def close(self):
        self.hard_commit()
        self.c.close()
        self.con.close()


_compression_ext = config['sqlite_zsdt_vfs_path']

_args_compression = 'vfs=zstd&level=6&outer_page_size=2048'
_args_read_only = 'mode=ro'


def _load_db(db_file, compression, read_only=False):
    """Opens an SQLite database."""
    con = sqlite3.connect(':memory:', isolation_level='DEFERRED')
    if compression:
        _load_extension(con)

    # args = '?a' | '?b' | '?a&b' | ''
    args_used = filter(None, [
        _args_read_only if read_only else None,
        _args_compression if compression else None,
    ])
    args = '&'.join(args_used)
    args = '?' + args if args else ''

    try:
        con = sqlite3.connect(f'file:{db_file}{args}', uri=True, isolation_level='DEFERRED')
    except sqlite3.OperationalError as e:
        if 'unable to open database file' not in str(e):
            logging.error(e)
        else:
            logging.error(f'Failed to open database {db_file}, is it already in use?.')
        sys.exit(1)

    con.execute('PRAGMA page_size=65536;')  # max page size
    con.execute('PRAGMA cache_size=-102400')  # 100 MB

    logging.info(f'Opened database {db_file}{args}.')

    return con


def _create_db(db_file, db_model, compression):
    """Used to initialize a new SQLite database."""
    db_folder = os.path.dirname(db_file)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    con = _load_db(db_file, compression)

    for table_query, _ in db_model.values():
        con.execute(table_query)

    con.commit()
    return con


def _indices_drop(c, log):
    c.execute('SELECT name FROM sqlite_master WHERE type == "index" and name NOT LIKE "sqlite_autoindex_%"')
    indices = [index[0] for index in c.fetchall()]
    if len(indices) == 0:
        return

    index_drop_info = InfoUtil(len(indices), action='dropping indices', intvl=1, rate_mult=1, log=log)

    for index in indices:
        c.execute(f'DROP INDEX IF EXISTS {index}')
        next(index_drop_info)

    index_drop_info.finish()


def _indices_create(c, db_model, log):
    number_of_indexes = sum(len(indices) for _, indices in db_model.values())
    info = InfoUtil(number_of_indexes, action='creating indices', intvl=1, rate_mult=1, log=log)

    info.log(f'Creating {number_of_indexes} indices. This may take a while.')
    info.log('Initial estimates will be multiple times the expected time.')

    for _, indices in db_model.values():
        for index in indices:
            c.execute(index)
            next(info)

    info.finish()


def _load_extension(con):
    """Loads the compression extension into the database."""
    if not os.path.exists(_compression_ext):
        logging.critical(f'Attempted to enable compression, but compression extension was '
                         f'not found at {_compression_ext}. Building instructions can be found at: '
                         f'https://github.com/mlin/sqlite_zstd_vfs, or set the path the config.')
        raise Exception(f'Compression extension not found at {_compression_ext}')
    con.enable_load_extension(True)
    try:
        con.load_extension(_compression_ext)
    except sqlite3.OperationalError as e:
        logging.critical(f'Failed to load compression extension at {_compression_ext}. '
                         f'Is your operating system supported?')
        raise e
    con.enable_load_extension(False)


__all__ = ['DBUtil']
