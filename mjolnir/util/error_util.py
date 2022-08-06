import logging
import time


def retry(delay=1, tries=3, exception=Exception, match_err=None, msg=None):
    """Retry a function call if it fails."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(tries):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    if i == tries - 1 or (match_err and match_err != str(e)):
                        raise
                    if msg:
                        logging.warning(msg)
                    time.sleep(delay)

        return wrapper

    return decorator
