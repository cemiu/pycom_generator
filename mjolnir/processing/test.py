import time
from multiprocessing import Queue, Lock

from mjolnir.processing.data_mng import DataManager, HHBLITS, HHFILTER, CCMPRED, QUEUE, LOCK

if __name__ == '__main__':
    modules = {
        HHBLITS: {QUEUE: Queue(), LOCK: Lock()},
        HHFILTER: {QUEUE: Queue(), LOCK: Lock()},
        CCMPRED: {QUEUE: Queue(), LOCK: Lock()}
    }

    data_mngr = DataManager('/mnt/s/testing/env', modules)

    # data_mngr.load_data(HHFILTER, 20)
    # data_mngr.load_data(HHBLITS, 5)
    # data_mngr.load_data(CCMPRED, 5)

    total_time = 0
    start_time = time.time()

    data_mngr.load_data(HHBLITS, 10)

    elapsed_time = time.time() - start_time
    total_time += elapsed_time

    while not modules[HHBLITS][QUEUE].empty():
        entry, seq = modules[HHBLITS][QUEUE].get()
        print('blits', entry, f'{elapsed_time:.3f}', f'{seq[:20 - len(seq)]}...')
        data_mngr.task_done(entry, HHBLITS)

    print(f'{total_time}')

    # while not queues[HHFILTER].empty():
    #     entry = queues[HHFILTER].get()
    #     print('filter', entry)
    #     data_mngr.set_done(entry, HHFILTER)
    #
    # while not queues[CCMPRED].empty():
    #     entry = queues[CCMPRED].get()
    #     print('ccmpred', entry)
    #     data_mngr.set_done(entry, CCMPRED)

    del data_mngr
