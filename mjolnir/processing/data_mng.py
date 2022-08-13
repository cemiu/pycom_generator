import logging
import sqlite3
import sys
import time
from contextlib import closing

import os

from mjolnir.util import retry
from .processing_data import *
from ..util.error_util import try_else

HHBLITS = (0, 1, 2)
HHFILTER = (2, 3, 4)
CCMPRED = (4, 5, 6)
REVERT = (-1, -1, 0)

MIN_BATCH_SIZE = 1500

err_disk = 'disk I/O error'
malformed_disk = 'database disk image is malformed'
db = lambda loc: sqlite3.connect(loc, isolation_level='EXCLUSIVE', timeout=120)


@retry(tries=10, exception=sqlite3.OperationalError, match_err=err_disk, msg=err_disk)
@try_else(delay=0, exception=sqlite3.DatabaseError, match_err=malformed_disk, msg=malformed_disk,
          else_=lambda: terminate)
def handler_setup(env):
    db_loc = env_path(env, 'db')
    with db(db_loc) as con, closing(con.cursor()) as c:
        c.execute(dbvar['insert_handler'])
        con.commit()
    return db_loc, c.lastrowid


# @retry(tries=3, delay=20, exception=sqlite3.DatabaseError, match_err=malformed_disk, msg=malformed_disk)
# @retry(tries=10, exception=sqlite3.OperationalError, match_err=err_disk, msg=err_disk)
# def load_data(handler, module, num_to_load):
#     """Request `num` entries to be loaded into the queues."""
#     db_loc, _ = handler
#     with db(db_loc) as con, closing(con.cursor()) as c:
#         return _select_list(c, handler, module, num_to_load)


# @retry(tries=3, delay=20, exception=sqlite3.DatabaseError, match_err=malformed_disk, msg=malformed_disk)
# @retry(tries=10, exception=sqlite3.OperationalError, match_err=err_disk, msg=err_disk)
# def revert(handler, entries):
#     db_loc, _ = handler
#     with db(db_loc) as con, closing(con.cursor()) as c:
#         _update_list(c, handler, REVERT, entries)


# @retry(tries=3, delay=20, exception=sqlite3.DatabaseError, match_err=malformed_disk, msg=malformed_disk)
# @retry(tries=10, exception=sqlite3.OperationalError, match_err=err_disk, msg=err_disk)
# def mark_completed(handler, module, entries):
#     db_loc, handler_id = handler
#     with db(db_loc) as con, closing(con.cursor()) as c:
#         _update_list(c, handler, module, entries)


@retry(tries=10, exception=sqlite3.OperationalError, match_err=err_disk, msg=err_disk)
@try_else(delay=0, exception=sqlite3.DatabaseError, match_err=malformed_disk, msg=malformed_disk,
          else_=lambda: terminate)
def database_step(handler, module, num_to_load=0, completed=None, reverted=None):
    db_loc, handler_id = handler
    if not (num_to_load or completed or reverted):
        return []

    with db(db_loc) as con, closing(con.cursor()) as c:
        loaded = _select_list(c, handler, module, num_to_load) if num_to_load else []
        if completed:
            _update_list(c, handler, module, completed)
        if reverted:
            _update_list(c, handler, REVERT, reverted)
        con.commit()

    return loaded


# @retry(tries=3, exception=sqlite3.OperationalError, match_err=err_disk, msg=err_disk)
# def reindex(env=None, handler=None, **kwargs):
#     if env:
#         db_loc = env_path(env, 'db')
#     elif handler:
#         db_loc, _ = handler
#     else:
#         raise ValueError('No environment or handler provided')
#
#     logging.warning(f'Reindexing {db_loc}')
#     with db(db_loc) as con, closing(con.cursor()) as c:
#         c.execute('REINDEX')
#         c.execute('VACUUM')
#         con.commit()
#     logging.warning(f'Reindexing {db_loc} complete')

def terminate(env=None, handler=None, **kwargs):
    if not env:
        if handler:
            env = os.path.dirname(handler[0])
        else:
            raise ValueError('No environment or handler provided')

    open(env_path(env, 'kill'), 'a').close()
    sys.exit(0)


def _update_list(c, handler, module, entries):
    _, handler_id = handler
    _, step_proc, step_after = module

    optional_neff = 'neff=?, ' if module in [HHBLITS, REVERT] else ''
    entry_select = f'AND processingStep={step_proc} AND handlerId={handler_id}' if module != REVERT else ''

    # entries = [(neff, entryId)] (hhblits, revert) or [(entryId,)]
    c.executemany(f'UPDATE processing '
                  f'SET {optional_neff} processingStep={step_after}, handlerId=NULL, lastChange=datetime("now") '
                  f'WHERE entryId=? {entry_select}', entries)


def _select_list(c, handler, module, limit):
    _, handler_id = handler
    step_pre, step_proc, _ = module

    # make sure that step_proc & handler_id & now are unique
    c.execute(dbvar['update_handler'], (handler_id,))

    now = c.execute('SELECT datetime("now")').fetchone()[0]
    while c.execute(dbvar['mark_unique'], (step_proc, handler_id, now)).fetchone() is not None:
        time.sleep(1)
        now = c.execute('SELECT datetime("now")').fetchone()[0]

    # mark entries as being processed
    c.execute(dbvar['mark_update'](limit=limit), (step_proc, handler_id, now, step_pre))

    columns = 'entryId, sequence' if module == HHBLITS else 'entryId'
    resp = c.execute(dbvar['mark_select'](columns), (step_proc, handler_id, now)).fetchall()
    return (resp if module == HHBLITS else [entry for entry, *_ in resp]) if resp else []
