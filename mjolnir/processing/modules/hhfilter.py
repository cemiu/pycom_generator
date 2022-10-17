import logging
import os
import random
import subprocess as sp
import time
from multiprocessing import JoinableQueue, Queue, Process

from mjolnir.processing import processor
from mjolnir.processing.data_mng import HHFILTER, database_step, MIN_BATCH_SIZE
from mjolnir.processing.processing_data import env_path
from mjolnir.util.error_util import silentremove
from mjolnir.util.exit_util import kill_signal
from mjolnir.util.format import split


def run(env, in_queue, out_queue, revert_queue):
    """Runs the hhfilter module."""
    while True:
        entry = in_queue.get()
        if entry is None:
            break  # kill signal

        in_queue.task_done()
        a3m_path = env_path(env, 'a3m', f'{entry}.a3m')
        oa3m_path = env_path(env, 'oa3m', f'{entry}.oa3m')
        aln_path = env_path(env, 'aln', f'{entry}.aln')

        hhfilter_cmd = f'hhfilter -id 90 -cov 75 -v 0 -i {a3m_path} -o {oa3m_path}'
        grep_cmd = f'egrep -v "^>" {oa3m_path} | sed "s/[a-z]//g" | sort -u > {aln_path}'

        time_start = time.time()
        sp.run(split(hhfilter_cmd), stdout=sp.DEVNULL, stderr=sp.DEVNULL)

        # check if hhfilter failed
        if not os.path.exists(oa3m_path):
            logging.warning(f'File {oa3m_path} not found, reverting')
            revert_queue.put(entry)
            del_list = [env_path(env, 'fasta', f'{entry}.fasta'),
                        env_path(env, 'hhr', f'{entry}.hhr'),
                        a3m_path, oa3m_path]
            [os.remove(en) for en in del_list if os.path.exists(en)]
            continue

        silentremove(a3m_path)

        sp.run(grep_cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)

        time_elapsed = time.time() - time_start
        logging.info(f'HHFilter {entry}: {time_elapsed:.2f}')

        out_queue.put((entry,))


def manager(env, handler, end_time, processes=1):
    start_time = time.time()
    in_queue, completed_queue, revert_queue = JoinableQueue(), Queue(), Queue()

    workers = [Process(target=run, args=(env, in_queue, completed_queue, revert_queue)) for _ in range(processes)]
    [worker.start() for worker in workers]

    while not (time.time() > end_time or kill_signal(env, start_time=start_time)):
        completed = processor.queue_to_list(completed_queue)
        reverted = processor.queue_to_list(revert_queue, revert=True)
        new_data = database_step(handler=handler, module=HHFILTER, num_to_load=max(MIN_BATCH_SIZE, 50 * processes),
                                 completed=completed, reverted=reverted)

        if new_data:
            logging.info(f'HHFilter: loaded {len(new_data)} new entries')
            for entry in new_data:
                in_queue.put(entry)
        else:
            time.sleep(360 + random.randint(0, 360))

        time.sleep(120 + random.randint(0, 120))
        in_queue.join()

    logging.info('HHFilter: finishing up')
    [in_queue.put(None) for _ in range(1000)]
    [worker.join() for worker in workers]
    logging.info('HHFilter: completed')

    completed = processor.queue_to_list(completed_queue, wait=True)
    reverted = processor.queue_to_list(revert_queue, revert=True, wait=True)
    database_step(handler=handler, module=HHFILTER, completed=completed, reverted=reverted)
