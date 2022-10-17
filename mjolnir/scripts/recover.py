import logging
import os
import re
import shutil
import sys

import sqlite3
import time

from contextlib import closing


_SELECT_ANY_UNSTARTED = '''
    SELECT *
    FROM processing
    WHERE processingStep != 0
    LIMIT 1'''


_INSERT_COMPLETED = '''
    UPDATE processing
    SET processingStep=?, neff=?, handlerId=NULL, lastChange=datetime("now")
    WHERE entryId=?
'''

env_structure = {
    'fasta': 'proc/fasta',
    'hhr': 'proc/hhr',
    'a3m': 'proc/a3m',
    'oa3m': 'proc/oa3m',
    'aln': 'proc/aln',
    'mat': 'proc/mat',
    'fasta-done': 'done/fasta',
    'hhr-done': 'extra/hhr',
    'a3m-done': 'extra/a3m',
    'oa3m-done': 'done/oa3m',
    'aln-done': 'done/aln',
    'mat-done': 'done/mat',
}


def env_path(path, spec, fi=None):
    if spec == 'db':
        return os.path.join(path, 'processing.db')
    dir_path = os.path.join(path, env_structure[spec])
    return os.path.join(dir_path, fi) if fi else dir_path


def module_num(module_name):
    modules = ['HHBlits', 'HHFilter', 'CCMpred']
    return (modules.index(module_name) + 1) * 2 if module_name in modules else 0


if __name__ == '__main__':
    """Re-add lost data to backup DB.
    
    Arguments: recover.py <db_location> <new_db_location> <log_location> <out_file_location> [-f]"""
    if len(sys.argv) not in [5, 6]:
        print(f'Usage: {sys.argv[0]} <db_location> <new_db_location> <log_location> <env_location> [-f]')
        sys.exit(1)

    db_location = sys.argv[1]
    new_db_location = sys.argv[2]
    log_location = sys.argv[3]
    env = sys.argv[4]
    force = len(sys.argv) == 6 and sys.argv[5] == '-f'

    if os.path.exists(new_db_location):
        if force:
            logging.info(f'Removing existing database {new_db_location}')
            os.remove(new_db_location)
        else:
            print(f'{new_db_location} already exists. Use -f to overwrite.')
            sys.exit(1)

    with sqlite3.connect(db_location) as con, closing(con.cursor()) as c:
        c.execute(_SELECT_ANY_UNSTARTED)
        if c.fetchone():
            print('Input DB needs to be empty')
            sys.exit(1)

    shutil.copy(db_location, new_db_location)

    entry_dict = {}

    start_time = time.time()

    # iterate over all log files
    for log_file in os.listdir(log_location):
        log_file_path = os.path.join(log_location, log_file)
        if not os.path.isfile(log_file_path) or not log_file.endswith('.log'):
            continue

        with open(log_file_path, 'r') as f:
            for line in f:
                if 'INFO: ' not in line:
                    continue
                line = line.split('INFO: ')[1]
                reg = r'HHBlits ([^,:]+), neff=(.*):'
                m = re.search(reg, line)
                if not m:
                    continue
                entry, neff, *_ = m.groups()

                if entry not in entry_dict and neff:
                    entry_dict[entry] = [None, float(neff)]
                elif entry in entry_dict and neff:
                    # noinspection PyUnresolvedReferences
                    entry_dict[entry][1] = min(entry_dict[entry][1], float(neff))
                elif not neff:
                    print(f'No neff for {entry}, reverting to start')
                    print(line)
                    entry_dict.pop(entry)

                required_files = {
                    'HHBlits': [
                        env_path(env, 'fasta', f'{entry}.fasta'),
                        env_path(env, 'a3m', f'{entry}.a3m')
                    ],
                    'HHFilter': [
                        env_path(env, 'fasta', f'{entry}.fasta'),
                        env_path(env, 'oa3m', f'{entry}.oa3m'),
                        env_path(env, 'aln', f'{entry}.aln')
                    ],
                    'CCMpred': [
                        env_path(env, 'fasta-done', f'{entry}.fasta'),
                        env_path(env, 'oa3m-done', f'{entry}.oa3m'),
                        env_path(env, 'aln-done', f'{entry}.aln'),
                        env_path(env, 'mat-done', f'{entry}.mat')
                    ],
                }

                for module, files in required_files.items():
                    all_files_exist = True
                    for file in files:
                        if not os.path.exists(file):
                            all_files_exist = False
                            break
                    if all_files_exist:
                        # noinspection PyTypeChecker
                        entry_dict[entry][0] = module
                        break

                if not entry_dict[entry][0]:
                    print(f'No module found for {entry}, reverting to start')

    db_tuples = []

    count_dict = {
        'HHBlits': 0,
        'HHFilter': 0,
        'CCMpred': 0,
        None: 0
    }

    for entry, (module, neff) in entry_dict.items():
        if module:
            count_dict[module] += 1
            db_tuples.append((module_num(module), neff, entry))
        else:
            count_dict[None] += 1

    print(count_dict)

    print(f'Recovered information in {time.time() - start_time} seconds')

    with sqlite3.connect(new_db_location) as con, closing(con.cursor()) as c:
        c.executemany(_INSERT_COMPLETED, db_tuples)
        con.commit()

    print(f'Recovered database in {time.time() - start_time} seconds')
