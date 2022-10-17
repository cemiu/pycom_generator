import logging
import os
import random
import shutil
import subprocess as sp
import time
from multiprocessing import Process, JoinableQueue, Queue

from mjolnir.processing import processor
from mjolnir.processing.data_mng import CCMPRED, database_step, MIN_BATCH_SIZE
from mjolnir.processing.processing_data import env_path
from mjolnir.util.exit_util import kill_signal
from mjolnir.util.format import split


def run(env, in_queue, out_queue, revert_queue, gpu_num):
    """Runs the hhfilter module."""
    while True:
        entry = in_queue.get()
        if entry is None:
            break  # kill signal

        in_queue.task_done()
        aln_path = env_path(env, 'aln', f'{entry}.aln')
        mat_path = env_path(env, 'mat', f'{entry}.mat')

        gpu_cmd = f'ccmpred -d {gpu_num} {aln_path} {mat_path}'

        time_start = time.time()
        sp.run(split(gpu_cmd), stdout=sp.DEVNULL, stderr=sp.DEVNULL)

        time_elapsed = time.time() - time_start
        logging.info(f'CCMpred {entry}: {time_elapsed:.2f}')

        file_move_pairs = {
            'fasta': (env_path(env, 'fasta', f'{entry}.fasta'), env_path(env, 'fasta-done', f'{entry}.fasta')),
            'hhr': (env_path(env, 'hhr', f'{entry}.hhr'), env_path(env, 'hhr-done', f'{entry}.hhr')),
            'a3m': (env_path(env, 'a3m', f'{entry}.a3m'), env_path(env, 'a3m-done', f'{entry}.a3m')),
            'oa3m': (env_path(env, 'oa3m', f'{entry}.oa3m'), env_path(env, 'oa3m-done', f'{entry}.oa3m')),
            'aln': (aln_path, env_path(env, 'aln-done', f'{entry}.aln')),
            'mat': (mat_path, env_path(env, 'mat-done', f'{entry}.mat')),
        }

        for ext, (src, dst) in file_move_pairs.items():
            try:
                if ext in ['fasta', 'oa3m', 'aln', 'mat']:
                    shutil.move(src, dst)
                else:
                    os.remove(src)
            except FileNotFoundError:
                if ext not in ['fasta', 'oa3m', 'aln', 'mat']:
                    # logging.warning(f'{src} not found, ignoring')
                    continue

                logging.warning(f'File {src} not found, reverting')
                revert_queue.put(entry)
                for file_pair in file_move_pairs.values():
                    try:
                        [os.remove(en) for en in file_pair if os.path.exists(en)]
                    except FileNotFoundError:
                        pass
                break

        out_queue.put((entry,))


def manager(env, handler, end_time, gpu_num):
    start_time = time.time()
    in_queue, completed_queue, revert_queue = JoinableQueue(), Queue(), Queue()

    workers = [Process(target=run, args=(env, in_queue, completed_queue, revert_queue, gpu)) for gpu in range(gpu_num)]
    [worker.start() for worker in workers]

    while not (time.time() > end_time or kill_signal(env, start_time=start_time)):
        completed = processor.queue_to_list(completed_queue)
        reverted = processor.queue_to_list(revert_queue, revert=True)
        new_data = database_step(handler=handler, module=CCMPRED, num_to_load=max(MIN_BATCH_SIZE, 100*gpu_num),
                                 completed=completed, reverted=reverted)
        if new_data:
            logging.info(f'CCMpred: loaded {len(new_data)} new entries')
            for entry in new_data:
                in_queue.put(entry)
        else:
            time.sleep(360 + random.randint(0, 360))

        time.sleep(120 + random.randint(0, 120))
        in_queue.join()

    logging.info('CCMpred: finishing up')
    [in_queue.put(None) for _ in range(1000)]
    [worker.join() for worker in workers]
    logging.info('CCMpred: completed')

    completed = processor.queue_to_list(completed_queue, wait=True)
    reverted = processor.queue_to_list(revert_queue, revert=True, wait=True)
    database_step(handler=handler, module=CCMPRED, completed=completed, reverted=reverted)
