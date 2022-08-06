import queue
import sqlite3
import time
from contextlib import closing
from mjolnir.util import retry

from .processing_data import *

HHBLITS = (0, 1, 2)
HHFILTER = (2, 3, 4)
CCMPRED = (4, 5, 6)
REVERT = (-1, -1, 0)

QUEUE = 0
LOCK = 1
COMPLETED = 2

error_msg_catch = 'disk I/O error'


class DataManager:
    """Class for managing data during processing."""

    def __init__(self, env_loc, modules):
        self.env = env_loc
        self.db_loc = env_path(self.env, 'db')
        self.db = lambda: sqlite3.connect(self.db_loc, isolation_level='DEFERRED', timeout=120)

        self.handler_id = self.setup()

        self.modules = modules
        self._completed_waiting = {}

    @retry(exception=sqlite3.OperationalError, match_err='disk I/O error', msg='Disk I/O failed, retrying.')
    def setup(self):
        with self.db() as con, closing(con.cursor()) as c:
            c.execute(dbvar['insert_handler'])
            handler_id = c.lastrowid
        return handler_id

    @retry(exception=sqlite3.OperationalError, match_err='disk I/O error', msg='Disk I/O failed, retrying.')
    def load_data(self, proc, num):
        """Request `num` entries to be loaded into the queues."""
        do_update = self._update_prep()
        with self.db() as con, closing(con.cursor()) as c:
            if do_update:
                self._update_completed(c)
            res = select_list(c, self.handler_id, proc, num)
            [self.modules[proc][QUEUE].put(i) for i in res]

    def task_done(self, entry, step, *data):
        self.modules[step][COMPLETED].put((*data, entry))

    @retry(exception=sqlite3.OperationalError, match_err='disk I/O error', msg='Disk I/O failed, retrying.')
    def revert(self, entry):
        with self.db() as con, closing(con.cursor()) as c:
            update_list(c, None, REVERT, (None, entry))

    @retry(exception=sqlite3.OperationalError, match_err='disk I/O error', msg='Disk I/O failed, retrying.')
    def update_completed(self, wait=False):
        if self._update_prep(wait=wait):
            with self.db() as con, closing(con.cursor()) as c:
                self._update_completed(c)

    def _update_prep(self, wait=False):
        """Prepare data for update, prior to acquiring DB lock."""
        if self._completed_waiting:
            return True

        any_completed = False

        for step, module in self.modules.items():
            step_list = []
            while True:
                try:
                    step_list.append(module[COMPLETED].get(block=wait, timeout=5))
                except queue.Empty:
                    break
            if step_list:
                self._completed_waiting[step] = step_list
                any_completed = True

        return any_completed

    def _update_completed(self, c):
        if not self._completed_waiting:
            self._update_prep()
        c.execute(f'UPDATE handlers SET lastUpdate=datetime("now") WHERE id={self.handler_id}')

        for step, step_list in self._completed_waiting.items():
            update_list(c, self.handler_id, step, step_list)
        self._completed_waiting.clear()

    @retry(exception=sqlite3.OperationalError, match_err='disk I/O error', msg='Disk I/O failed, retrying.')
    def finish(self):
        time.sleep(5)
        do_update = self._update_prep(wait=True)
        with self.db() as con, closing(con.cursor()) as c:
            if do_update:
                self._update_completed(c)
            c.execute(f'DELETE FROM handlers WHERE id={self.handler_id}')


def update_list(c, handler_id, step, entries):
    if not entries:
        return
    _, step_proc, step_after = step

    optional_neff = 'neff=?, ' if step in [HHBLITS, REVERT] else ''
    entry_select = f'AND processingStep={step_proc} AND handlerId={handler_id}' if step != REVERT else ''

    c.executemany(f'UPDATE processing '
                  f'SET {optional_neff} processingStep={step_after}, handlerId=NULL, lastChange=datetime("now") '
                  f'WHERE entryId=? {entry_select}', entries)


def select_list(c, handler_id, step, limit):
    step_pre, step_proc, _ = step

    # make sure that step_proc & handler_id & now are unique
    now = c.execute('SELECT datetime("now")').fetchone()[0]
    while c.execute(dbvar['mark_unique'], (step_proc, handler_id, now)).fetchone() is not None:
        time.sleep(1)
        now = c.execute('SELECT datetime("now")').fetchone()[0]

    # mark entries as being processed
    c.execute(dbvar['mark_update'](limit=limit), (step_proc, handler_id, now, step_pre))

    columns = 'entryId, sequence' if step == HHBLITS else 'entryId'
    resp = c.execute(dbvar['mark_select'](columns), (step_proc, handler_id, now)).fetchall()
    return (resp if step == HHBLITS else [entry for entry, *_ in resp]) if resp else []
