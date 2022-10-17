import io
import logging
import random
import subprocess as sp
import time
from multiprocessing import JoinableQueue, Queue, Process

from mjolnir.processing import processor
from mjolnir.processing.data_mng import HHBLITS, database_step, MIN_BATCH_SIZE
from mjolnir.processing.processing_data import env_path
from mjolnir.util.error_util import silentremove
from mjolnir.util.exit_util import kill_signal
from mjolnir.util.format import seq_to_fasta, split


def run(env, in_queue, out_queue, cores, clustdb):
    """Runs the hhblits module."""
    while True:
        data = in_queue.get()
        if data is None:
            break  # kill signal

        in_queue.task_done()
        entry, seq = data

        fasta = seq_to_fasta(entry, seq)
        fasta_path = env_path(env, 'fasta', f'{entry}.fasta')
        hhr_path = env_path(env, 'hhr', f'{entry}.hhr')
        a3m_path = env_path(env, 'a3m', f'{entry}.a3m')

        with open(fasta_path, 'w') as f:
            f.write(fasta)

        hhblits_cmd = f'hhblits -B 100000 -v 2 -n 4 -cpu {cores} -nodiff -maxfilt 100000 -maxseq 2000000 ' \
                      f'-d {clustdb} -i {fasta_path} -o {hhr_path} -oa3m {a3m_path}'

        time_start = time.time()
        proc = sp.Popen(split(hhblits_cmd), stdout=sp.PIPE, stderr=sp.DEVNULL)

        neff = 0
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            if line.strip().startswith('Neff'):
                neff = float(line.split()[-1])
                break

        silentremove(hhr_path)

        time_elapsed = time.time() - time_start
        logging.info(f'HHBlits {entry}, neff={neff:.3f}: {time_elapsed:.2f}')

        out_queue.put((neff, entry))


def manager(env, handler, end_time, cores, clustdb):
    start_time = time.time()
    in_queue, completed_queue = JoinableQueue(), Queue()

    workers = [Process(target=run, args=(env, in_queue, completed_queue, core, clustdb)) for core in cores]
    [worker.start() for worker in workers]

    while not (time.time() > end_time or kill_signal(env, start_time=start_time)):
        completed = processor.queue_to_list(completed_queue)
        new_data = database_step(handler=handler, module=HHBLITS, num_to_load=MIN_BATCH_SIZE, completed=completed)

        if new_data:
            logging.info(f'HHBlits: loaded {len(new_data)} new entries')
            for entry_seq in new_data:
                in_queue.put(entry_seq)
        else:
            time.sleep(360 + random.randint(0, 360))

        time.sleep(120 + random.randint(0, 120))
        in_queue.join()

    logging.info('HHBlits: finishing up')
    [in_queue.put(None) for _ in range(1000)]
    [worker.join() for worker in workers]
    logging.info('HHBlits: completed')

    completed = processor.queue_to_list(completed_queue, wait=True)
    database_step(handler=handler, module=HHBLITS, completed=completed)
