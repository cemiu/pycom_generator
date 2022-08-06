import logging
import shutil
import sys


def err_exit(msg, do_exit=True):
    if not do_exit:
        return
    for line in msg.split('\n'):
        logging.error(line)
    sys.exit(1)


def which_exit(cmd, reason=None):
    reason = f' but is needed by {reason}' if reason else ''
    err_exit(f'{cmd} is not installed{reason}. Please install {cmd} and add it to the path.', not shutil.which(cmd))
