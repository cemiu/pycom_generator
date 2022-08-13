import errno
import logging
import time
from random import random

import os


def retry(delay=1, tries=3, exception=Exception, match_err=None, msg=None):
    """Retry a function call if it fails."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(tries):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    if match_err and match_err != str(e):
                        raise e
                    if i == tries - 1:
                        if msg:
                            logging.error(f'{msg}: {func}, {args}{f" {kwargs}" if kwargs else ""}')
                        logging.error(e)

                        ##### TODO: remove unstable solution #####
                        # os.execv(shutil.which('python3'), ['python'] + sys.argv)
                        ##########################################

                        raise
                    if msg:
                        logging.warning(msg)
                    time.sleep(delay + random())

        return wrapper

    return decorator


def try_else(delay=1, exception=Exception, match_err=None, msg=None, else_=None):
    """Try a function call, if it fails, call else_."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                if match_err and match_err != str(e):
                    raise e
                if msg:
                    logging.error(f'TryElse: {str(e)} {msg}: {func}, {args}{f" {kwargs}" if kwargs else ""}')
                time.sleep(delay + random())
                else_()(**kwargs)
                return func(*args, **kwargs)

        return wrapper

    return decorator


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
