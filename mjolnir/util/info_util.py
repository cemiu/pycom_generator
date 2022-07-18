import time
import logging

_format = '%H:%M:%S'

class InfoUtil:
    """Produces progress info about the progress over some batch.

    Usage:
    info    = InfoUtil(size_of_batch : int)  # will log every 5 seconds
            = InfoUtil(size_of_batch, intvl=10)  # will log every 10 seconds
            = InfoUtil(size_of_batch, intvl_mode='count', intvl=5000)  # will log once per 5000 entries
    next(info)  # call after processing any entry
    del info    # call after processing all entries

    Note:   The second interval will be exceeded by, on average, half the time it takes to process
            each entry.
    """
    def __init__(self,
                 entry_count=None,
                 file_progress=None,
                 intvl_mode='sec',
                 intvl=None,
                 action=''):
        if ((entry_count is not None) and (file_progress is not None))\
                or ((entry_count is None) and (file_progress is None)):
            raise ValueError('Must specify either entry_count or file_progress, but not both.')

        self.c_cur = 0

        # entry count
        self.c_total = entry_count
        self.c_len = len(f'{self.c_total:,}') if entry_count is not None else 0

        # file progress
        self.progress = file_progress
        self.is_mode_progress = file_progress is not None

        if intvl_mode not in ['sec', 'count']:
            raise ValueError(f'Invalid interval mode: {intvl_mode}, must be "sec" or "count" '
                             f'and [intvl=no_of_seconds_or_entries_between_logging_info]')

        # default interval is once per second or once per 10000 entries
        self.is_intvl_sec = intvl_mode == 'sec'
        self.intvl = intvl if intvl is not None else (1 if self.is_intvl_sec else 10000)
        self.action = action

        self.start_time = time.time()
        self.last_time = self.start_time

    def __next__(self):
        self.c_cur += 1

        # determine if info should be logged
        if self.is_intvl_sec:
            if time.time() - self.last_time >= self.intvl:
                logging.info(self)
                self.last_time = time.time()
        elif self.c_cur % self.intvl == 0:
            logging.info(self)

        return self.c_cur

    def __str__(self):
        return format_info(self.start_time, self.is_mode_progress, self.c_cur,
                           c_total=self.c_total, progress=self.progress,
                           c_len=self.c_len, action=self.action)

    def __del__(self):
        logging.info(self)
        time_fin = time.time() - self.start_time
        out_time = f'{time.strftime(_format, time.gmtime(time_fin))}h'
        action = f' {self.action} ' if self.action else ' '
        out_days = f'{int(time_fin // (24 * 3600))}d ' if time_fin // (24 * 3600) >= 1 else ''
        logging.info(f'Done{action}in {out_days}{out_time}.')


def format_info(time_start, is_mode_progress, c_cur, c_total=None, progress=None, c_len=0, action=''):
    """Formats the info about the progress."""
    avg_time = (time.time() - time_start) / c_cur if c_cur > 0 else 1

    c_cur_delim = f'{c_cur:,}'
    out_progress = f'{c_cur_delim:>{c_len}}'
    if c_total is not None:
        out_progress = f'{c_cur_delim:>{c_len}}/{c_total:,}'
    out_rate = f'{(avg_time * 10000):.2f}s/10k'

    out_eta = None
    if is_mode_progress:
        out_eta = f'; {progress}'
    else:
        eta = (c_total - c_cur) * avg_time
        eta_days = f'{int(eta // (24 * 3600))}d ' if eta // (24 * 3600) >= 1 else ''
        out_eta = f'; {eta_days}{time.strftime(_format, time.gmtime(eta))}h left'

    action = f'{action}: ' if action else ''
    return f'{action}{out_progress}; {out_rate}{out_eta}.'
