import logging
import subprocess as sp
import time

from mjolnir.processing.data_mng import HHFILTER
from mjolnir.processing.processing_data import env_path
from mjolnir.util.format import split


def run(env, processor):
    """Runs the hhfilter module."""
    while True:
        entry = processor.get_data(HHFILTER)
        if entry is None:
            break  # kill signal

        a3m_path = env_path(env, 'a3m', f'{entry}.a3m')
        oa3m_path = env_path(env, 'oa3m', f'{entry}.oa3m')
        aln_path = env_path(env, 'aln', f'{entry}.aln')

        hhfilter_cmd = f'hhfilter -id 90 -cov 75 -v 0 -i {a3m_path} -o {oa3m_path}'
        grep_cmd = f'egrep -v "^>" {oa3m_path} | sed "s/[a-z]//g" | sort -u > {aln_path}'

        time_start = time.time()
        sp.run(split(hhfilter_cmd), stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        sp.run(grep_cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)

        time_elapsed = time.time() - time_start
        logging.info(f'HHFilter {entry}: {time_elapsed:.2f}')

        processor.task_done(HHFILTER, entry)
