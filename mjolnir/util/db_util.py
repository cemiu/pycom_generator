import logging
import os
import sqlite3

from mjolnir import config
from mjolnir.db import tables_and_indices
from mjolnir.experiment import p  # TODO remove


class DBUtil:
    def __init__(self, db_file, init=False, compression=True, read_only=False, commit_frequency=1):
        self.db_file = db_file
        if not os.path.exists(db_file) and not init:
            raise Exception(f'Database {db_file} does not exist. Use [db --init] to create a new database.')

        self.last_commit = 0
        self.commit_frequency = commit_frequency

        self.conn = _create_db(db_file, compression) if init else _load_db(db_file, compression, read_only)
        self.c = self.conn.cursor()

    def insert(self, query, data):
        self.c.execute(query, data)
        self.soft_commit()

    def insert_many(self, query, data):
        if not data:
            return
        self.c.executemany(query, data)

    def select_data(self, table_name, columns, where_clause):
        self.c.execute("SELECT {} FROM {} WHERE {}".format(columns, table_name, where_clause))
        return self.c.fetchall()

    def update_data(self, table_name, data, where_clause):
        self.c.execute("UPDATE {} SET {} WHERE {}".format(table_name, data, where_clause))
        self.soft_commit()

    def delete_data(self, table_name, where_clause):
        self.c.execute("DELETE FROM {} WHERE {}".format(table_name, where_clause))
        self.soft_commit()

    def exists(self, table_name, column, value):
        self.c.execute("SELECT COUNT(*) FROM {} WHERE {} = ?".format(table_name, column), (value,))
        return self.c.fetchone()[0] > 0

    def sql_query(self, query, hard_commit=False):
        self.c.execute(query)
        self.hard_commit() if hard_commit else self.soft_commit()
        return self.c.fetchall()

    def sql_post(self, query, hard_commit=False):
        self.c.execute(query)
        self.hard_commit() if hard_commit else self.soft_commit()

    def sql_get(self, query):
        self.c.execute(query)
        return self.c.fetchall()

    def soft_commit(self):
        self.last_commit += 1
        if self.last_commit >= self.commit_frequency:
            self.hard_commit()

    def hard_commit(self):
        self.conn.commit()
        self.last_commit = 0
        if config['_debug']:
            logging.info('Committed to database.')

    def close(self):
        self.hard_commit()
        self.c.close()
        self.conn.close()


_compression_ext = p.zsdt_vfs  # TODO give ability to override this with config

_args_compression = 'vfs=zstd&level=6&outer_page_size=2048'
_args_read_only = 'mode=ro'


def _load_db(db_file, compression, read_only=False):
    """Opens an SQLite database."""
    conn = sqlite3.connect(':memory:', isolation_level='DEFERRED')
    if compression:
        conn.enable_load_extension(True)
        conn.load_extension(_compression_ext)
        conn.enable_load_extension(False)

    # args = '?a' | '?b' | '?a&b' | ''
    args_used = filter(None, [
        _args_read_only if read_only else None,
        _args_compression if compression else None,
    ])
    args = '&'.join(args_used)
    args = '?' + args if args else ''

    conn = sqlite3.connect(f'file:{db_file}{args}', isolation_level='DEFERRED')
    logging.info(f'Opened database {db_file}{args}.')

    conn.execute('PRAGMA page_size=65536;')  # max page size
    conn.execute('PRAGMA cache_size=-102400')  # 100 MB

    return conn


def _create_db(db_file, compression):
    """Used to initialize a new SQLite database."""
    db_folder = os.path.dirname(db_file)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    conn = _load_db(db_file, compression)

    for table, queries in tables_and_indices.items():
        for query in queries:
            conn.execute(query)
            break  # only create tables, skip indices

    conn.commit()
    return conn


__all__ = ['DBUtil']
