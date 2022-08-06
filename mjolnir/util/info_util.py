import time

from .format import human_num

_format = '%H:%M:%S'


class InfoUtil:
    """Produces progress info about the progress over some batch.

    Usage:
    info    = InfoUtil(size_of_batch : int)  # will log every 5 seconds
            = InfoUtil(size_of_batch, intvl=10)  # will log every 10 seconds
            = InfoUtil(size_of_batch, intvl_mode='count', intvl=5000)  # will log once per 5000 entries
    next(info)     # call after processing any entry
    info.finish()  # call after processing all entries

    Note:   The second interval will be exceeded by, on average, half the time it takes to process
            each entry.
    """

    def __init__(self,
                 entry_count=None,
                 file_progress=None,
                 intvl_mode='sec',
                 intvl=None,
                 action='',
                 rate_mult=10000,
                 log=True):
        if ((entry_count is not None) and (file_progress is not None)) \
                or ((entry_count is None) and (file_progress is None)):
            raise ValueError('Must specify either entry_count or file_progress, but not both.')

        self.count = 0

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
        self.rate_mult = rate_mult

        self.start_time = time.time()
        self.last_time = self.start_time
        self.do_log = log

    def __next__(self):
        self.count += 1

        if not self.do_log:
            return

        # determine if info should be logged
        if self.is_intvl_sec:
            if time.time() - self.last_time >= self.intvl:
                self.log(self)
                self.last_time = time.time()
        elif self.count % self.intvl == 0:
            self.log(self)

        return self.count

    def __str__(self):
        return format_info(self.start_time, self.is_mode_progress, self.count,
                           c_total=self.c_total, progress=self.progress,
                           c_len=self.c_len, action=self.action,
                           rate_mult=self.rate_mult)

    def finish(self):
        if not self.do_log:
            return

        self.log(self)
        time_fin = time.time() - self.start_time
        out_time = f'{time.strftime(_format, time.gmtime(time_fin))}h'
        action = f' {self.action} ' if self.action else ' '
        out_days = f'{int(time_fin // (24 * 3600))}d ' if time_fin // (24 * 3600) >= 1 else ''
        self.log(f'Done{action}in {out_days}{out_time}.')

    def log(self, msg):
        if self.do_log:
            print(msg, end='\r')


def format_info(time_start, is_mode_progress, count, c_total=None, progress=None, c_len=0, action='', rate_mult=10000):
    """Formats the info about the progress."""
    avg_time = (time.time() - time_start) / count if count > 0 else 1

    count_delim = f'{count:,}'
    out_progress = f'{count_delim:>{c_len}}'
    if c_total is not None:
        out_progress = f'{count_delim:>{c_len}}/{c_total:,}'
    out_rate = f'{(avg_time * rate_mult):.2f}s/{human_num(rate_mult)}'

    if is_mode_progress:
        out_eta = f'; {progress}'
    else:
        eta = (c_total - count) * avg_time
        eta_days = f'{int(eta // (24 * 3600))}d ' if eta // (24 * 3600) >= 1 else ''
        out_eta = f'; {eta_days}{time.strftime(_format, time.gmtime(eta))}h left'

    action = f'{action}: ' if action else ''
    return f'{action}{out_progress}; {out_rate}{out_eta}.'
