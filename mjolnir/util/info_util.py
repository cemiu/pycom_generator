import time
import logging


class InfoUtil:
    """Produces progress info about the progress over some batch.

    Usage:
    info = InfoUtil(size_of_batch : int, [interval=[how_often_to_log_info : int])  # initialize
    next(info)  # call after processing any entry
    del info    # call after processing all entries
    """
    def __init__(self, entry_count, interval=1000, formatting='%H:%M:%S', action=''):
        self.c_cur = 0
        self.c_total = entry_count
        self.c_len = len(str(self.c_total))

        self.info_interval = interval
        self.format = formatting
        self.action = action

        self.start_time = time.time()
        self.last_time = self.start_time

        self.time_start = time.time()

    def __next__(self):
        self.c_cur += 1
        if self.c_cur % self.info_interval == 0:
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
        logging.info(f'Done{action}in {out_time}.')


def format_info(time_start, c_total, c_cur, c_len=5, formatting='%H:%M:%S', action=''):
    """Formats the info about the progress."""
    time_cur = time.time()
    avg_time = (time_cur - time_start) / c_cur if c_cur > 0 else 1
    eta = (c_total - c_cur) * avg_time

    out_progress = f'{c_cur: >{c_len}}/{c_total}'
    out_rate = f'{(avg_time * 10000):.2f}s/10k'
    out_eta = f'{time.strftime(formatting, time.gmtime(eta))}h left'
    action = f'{action}: ' if action else ''
    return f'{action}{out_progress}; {out_rate}; {out_eta}.'


__all__ = ['InfoUtil']
