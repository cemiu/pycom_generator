import time
import logging


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

    def __init__(self, entry_count, intvl_mode='sec', intvl=None, formatting='%H:%M:%S', action=''):
        self.pause = False
        self.c_cur = 0
        self.c_total = entry_count
        self.c_len = len(str(self.c_total))

        if intvl_mode not in ['sec', 'count']:
            raise ValueError(f'Invalid interval mode: {intvl_mode}, must be "sec" or "count" '
                             f'and [intvl=no_of_seconds_or_entries_between_logging_info]')

        self.is_intvl_sec = intvl_mode == 'sec'
        # default interval is once per second or once per 10000 entries
        self.intvl = intvl if intvl is not None else (1 if self.is_intvl_sec else 10000)
        self.format = formatting
        self.action = action

        self.start_time = time.time()
        self.last_time = self.start_time

        self.time_start = time.time()
        if self.is_intvl_sec:
            self.last_interval = self.time_start

    def __next__(self):
        self.c_cur += 1

        if self.pause:
            return self.c_cur

        # should info be logged
        if self.is_intvl_sec:
            if time.time() - self.last_time >= self.intvl:
                logging.info(self)
                self.last_time = time.time()
        elif self.c_cur % self.intvl == 0:
            logging.info(self)

        return self.c_cur

    def __str__(self):
        return format_info(self.time_start, self.c_total, self.c_cur,
                           c_len=self.c_len, formatting=self.format, action=self.action)

    def __del__(self):
        logging.info(self)
        time_fin = time.time() - self.time_start
        out_time = f'{time.strftime(self.format, time.gmtime(time_fin))}h'
        action = f' {self.action} ' if self.action else ' '
        out_days = f'{int(time_fin // (24 * 3600))}d ' if time_fin // (24 * 3600) >= 1 else ''
        logging.info(f'Done{action}in {out_days}{out_time}.')

    def pause(self, should_pause):
        self.pause = should_pause


def format_info(time_start, c_total, c_cur, c_len=5, formatting='%H:%M:%S', action=''):
    """Formats the info about the progress."""
    time_cur = time.time()
    avg_time = (time_cur - time_start) / c_cur if c_cur > 0 else 1
    eta = (c_total - c_cur) * avg_time

    out_progress = f'{c_cur: >{c_len}}/{c_total}'
    out_rate = f'{(avg_time * 10000):.2f}s/10k'
    eta_days = f'{int(eta // (24 * 3600))}d ' if eta // (24 * 3600) >= 1 else ''
    out_eta = f'{eta_days}{time.strftime(formatting, time.gmtime(eta))}h left'
    action = f'{action}: ' if action else ''
    return f'{action}{out_progress}; {out_rate}; {out_eta}.'


__all__ = ['InfoUtil']
