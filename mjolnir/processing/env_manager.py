import logging
import os
import sqlite3
import time

from .processing_data import env_structure, env_path, dbvar


def init_environment(entry_db, env_location):
    logging.info(f'Initializing processing environment at {env_location}.')
    for spec in env_structure:
        os.makedirs(env_path(env_location, spec), exist_ok=True)

    init_db(entry_db, env_location)
    logging.info(f'Finished initializing processing environment.')


def init_db(entry_db, env_location):
    process_db = env_path(env_location, 'db')
    max_seq_len = 500  # sequences with length > max_seq_len will be ignored

    logging.info(f'Creating processing DB from entry DB {entry_db}, filtering sequences longer than {max_seq_len}.')
    time_start = time.time()

    with sqlite3.connect(entry_db, isolation_level='DEFERRED') as con:
        c = con.cursor()
        c.execute(f'ATTACH "{process_db}" AS proc')

        c.execute(dbvar['table'])
        c.execute(dbvar['table_handlers'])
        c.execute(dbvar['create_insert'](max_seq_len=max_seq_len))
        [c.execute(index) for index in dbvar['indices']]

    logging.info(f'Finished processing DB creation in {time.time() - time_start:.2f} seconds.')
