import logging
import os
import shutil
import sys
import time


def kill_signal(env, start_time=0, recent_time=0):
    kill_file = os.path.join(env, 'kill')
    if not os.path.exists(kill_file):
        return False

    try:
        if recent_time:
            return time.time() - os.path.getmtime(kill_file) < recent_time
        return os.path.getmtime(kill_file) > start_time
    except OSError:
        return True

def err_exit(msg, do_exit=True):
    if not do_exit:
        return
    for line in msg.split('\n'):
        logging.error(line)
    sys.exit(1)


def which_exit(cmd, reason=None):
    reason = f' but is needed by {reason}' if reason else ''
    err_exit(f'{cmd} is not installed{reason}. Please install {cmd} and add it to the path.', not shutil.which(cmd))
