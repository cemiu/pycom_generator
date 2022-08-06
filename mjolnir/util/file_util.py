import gzip
import logging
import os
import time
from io import BufferedReader

from .format import format_bytes

_print_verbose = False


class Reader(BufferedReader):
    """A buffered reader for files with callback."""

    def __init__(self, file, mode=None):
        if mode is None:
            mode = 'gz' if file.endswith('.gz') else 'xml'
            logging.info(f'Parsing mode: {mode}')

        stream = gzip.open(file) if mode == 'gz' else (open(file, 'rb') if mode == 'xml' else None)

        if stream is None:
            raise ValueError(f'Unknown mode {mode}, must be "xml" or "gz"')

        # parse file progress rather than data progress for gzip files
        if mode == 'gz':
            # noinspection PyUnresolvedReferences
            stream.tell = stream.fileobj.tell

        self.reader = stream
        self.length = os.stat(file).st_size

        self.progress = Progress(self.length)
        self._callback = self.progress.update

        # noinspection PyTypeChecker
        super().__init__(raw=stream)

    def read(self, size=None):
        self._callback(position=self.tell(), total_sz=self.length)
        return super(Reader, self).read(size)


class Progress:
    """A progress tracker for files"""

    def __init__(self, total_sz):
        self.position = 0
        self.read_sz = 0
        self.total_sz = total_sz
        self.start = time.time()

    def update(self, position, total_sz):
        self.position = position
        self.total_sz = total_sz

    def __str__(self):
        percent = self.position / self.total_sz
        sz_cur = format_bytes(self.position)
        sz_total = format_bytes(self.total_sz)

        time_elapsed = time.time() - self.start
        speed = self.position / time_elapsed
        speed_info = ''
        if speed > 0:
            eta = self.total_sz / speed - time_elapsed
            eta_days = f'{int(eta // (24 * 3600))}d ' if eta // (24 * 3600) >= 1 else ''
            out_eta = f'; {eta_days}{time.strftime("%H:%M:%S", time.gmtime(eta))}h left'
            speed_format = f'{format_bytes(speed)}/s' if _print_verbose else ''
            speed_info = f'; {speed_format}{out_eta}'
        return f'{percent:.2%}; {sz_cur}/{sz_total}{speed_info}'

