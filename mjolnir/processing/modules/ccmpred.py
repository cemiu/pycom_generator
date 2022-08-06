import logging
import shutil
import subprocess as sp
import time

import os

from mjolnir.processing.data_mng import CCMPRED
from mjolnir.processing.processing_data import env_path
from mjolnir.util.format import split


def run(env, processor, gpu_num):
    """Runs the hhfilter module."""
    while True:
        entry = processor.get_data(CCMPRED)
        if entry is None:
            break  # kill signal

        aln_path = env_path(env, 'aln', f'{entry}.aln')
        mat_path = env_path(env, 'mat', f'{entry}.mat')

        gpu_cmd = f'ccmpred -d {gpu_num} {aln_path} {mat_path}'

        time_start = time.time()
        sp.run(split(gpu_cmd), stdout=sp.DEVNULL, stderr=sp.DEVNULL)

        time_elapsed = time.time() - time_start
        logging.info(f'CCMpred {entry}: {time_elapsed:.2f}')

        file_move_pairs = [
            (env_path(env, 'fasta', f'{entry}.fasta'), env_path(env, 'fasta-done', f'{entry}.fasta')),
            (env_path(env, 'hhr', f'{entry}.hhr'), env_path(env, 'hhr-done', f'{entry}.hhr')),
            (env_path(env, 'a3m', f'{entry}.a3m'), env_path(env, 'a3m-done', f'{entry}.a3m')),
            (env_path(env, 'oa3m', f'{entry}.oa3m'), env_path(env, 'oa3m-done', f'{entry}.oa3m')),
            (aln_path, env_path(env, 'aln-done', f'{entry}.aln')),
            (mat_path, env_path(env, 'mat-done', f'{entry}.mat')),
        ]

        for src, dst in file_move_pairs:
            try:
                shutil.move(src, dst)
            except FileNotFoundError:
                if dst.startwith('extra'):
                    continue

                logging.warning(f'File {src} not found, reverting')
                for src_a, dst_a in file_move_pairs:
                    if os.path.exists(src_a):
                        os.remove(src_a)
                    if os.path.exists(dst_a):
                        os.remove(dst_a)
                processor.revert(entry)
                return

        processor.task_done(CCMPRED, entry)
