import os
import sqlite3
from mjolnir.experiment import p  # TODO remove


class DBUtil:
    def __init__(self, db_file, init=False, compression=True, read_only=False):
        self.db_file = db_file
        if not os.path.exists(db_file) or init:
            raise Exception(f'Database {db_file} does not exist. Use [db --init] to create a new database.')

        self.conn = _create_db(db_file, compression) if init else _load_db(db_file, compression, read_only)
        self.c = self.conn.cursor()

    def create_table(self, table_name, columns):
        self.c.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, columns))
        self.conn.commit()

    def insert_data(self, table_name, data):
        self.c.execute("INSERT INTO {} VALUES {}".format(table_name, data))
        self.conn.commit()

    def select_data(self, table_name, columns, where_clause):
        self.c.execute("SELECT {} FROM {} WHERE {}".format(columns, table_name, where_clause))
        return self.c.fetchall()

    def update_data(self, table_name, data, where_clause):
        self.c.execute("UPDATE {} SET {} WHERE {}".format(table_name, data, where_clause))
        self.conn.commit()

    def delete_data(self, table_name, where_clause):
        self.c.execute("DELETE FROM {} WHERE {}".format(table_name, where_clause))
        self.conn.commit()

    def close(self):
        self.conn.close()
        self.c.close()
        self.conn = None
        self.c = None
        self.db_file = None


_compression_ext = p.zsdt_vfs  # TODO give ability to override this with config

_args_compression = 'vfs=zstd&level=6&outer_page_size=2048'
_args_read_only = 'mode=ro'

def _load_db(db_file, compression, read_only=False):
    conn = sqlite3.connect(':memory:')
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

    conn = sqlite3.connect(f'file:{db_file}{args}')

    conn.execute('PRAGMA page_size=65536;')  # max page size
    conn.execute('PRAGMA cache_size=-102400')  # 100 MB

    return conn


def _create_db(db_file, compression):
    conn = _load_db(db_file, compression)
    # TODO ...
    pass


__all__ = ['DBUtil']
