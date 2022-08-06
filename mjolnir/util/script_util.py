import os
import sys


def args_to_tuple(num=None, num_min=None, num_max=None, error_msg=None):
    """
    Returns a tuple of the arguments passed to the script, or halts the process.
    """
    num_args = len(sys.argv) - 1
    num_min, num_max = (num, num) if num is not None else (num_min, num_max)

    if (num_min is not None and num_min > num_args) or (num_max is not None and num_max < num_args):
        if error_msg is not None:
            print(error_msg)
        sys.exit(1)

    return tuple(sys.argv[1:])


def file_exists(file_path, exit_if_not_found=False, exit_if_found=False, error_msg=None):
    """
    Returns True if the file exists.
    """
    if exit_if_not_found and exit_if_found:
        raise ValueError('exit_if_not_found and exit_if_found cannot both be True')

    if not os.path.isfile(file_path) != exit_if_found:
        if exit_if_not_found or exit_if_found:
            if error_msg is not None:
                print(error_msg)
            sys.exit(1)
        return False
    return True

def dir_exists(dir_path, exit_if_not_found=False, error_msg=None):
    """
    Returns True if the directory exists.
    """
    if not os.path.isdir(dir_path):
        if exit_if_not_found:
            if error_msg is not None:
                print(error_msg)
            sys.exit(1)
        return False
    return True


def mkdir_f(files):
    """
    Creates a directory tree if it doesn't exist.
    """
    if type(files) not in (list, tuple):
        files = (files,)

    for file_path in files:
        dir_path = os.path.dirname(file_path)
        if not dir_exists(dir_path):
            os.makedirs(dir_path)

def remove(files):
    if type(files) not in (list, tuple):
        files = (files,)

    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)
