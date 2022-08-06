import logging
import os
import queue
import time
from multiprocessing import Lock, Process, Queue

from mjolnir.processing.data_mng import DataManager, HHBLITS, HHFILTER, CCMPRED, QUEUE, LOCK, COMPLETED
from mjolnir.processing.modules import hhblits, hhfilter, ccmpred


class Processor:
    def __init__(self, params):
        self.params = params
        self.env = params['env']

        self.run_hhblits = params['run_hhblits']
        self.run_hhfilter = params['run_hhfilter']
        self.run_ccmpred = params['run_ccmpred']

        self.modules = {}

        self.end_time = (time.time() + (params['max_time']) if 'max_time' in params else float('inf'))

        self.hhblits_cores = params['hhblits_cores'] if 'hhblits_cores' in params else []
        self.clustdb = params['clustdb'] if 'clustdb' in params else None
        self.ccmpred_gpus = params['gpu_count'] if 'gpu_count' in params else 0

        self.data_manager = DataManager(self.env, self.modules)
        self.kill_signal = lambda: os.path.exists(os.path.join(self.env, 'kill'))
        self.kill_signal_sent = Lock()

    def task_done(self, step, entry, *data):
        """Called when a task is done."""
        self.data_manager.task_done(entry, step, *data)

    def revert(self, entry):
        """Reverts an entry to the start."""
        self.data_manager.revert(entry)

    def get_data(self, proc):
        while True:
            try:
                return self.modules[proc][QUEUE].get(timeout=15)
            except queue.Empty:
                self._request_data(proc)
                continue

    def _request_data(self, proc):
        if not self.modules[proc][LOCK].acquire(False):
            self.modules[proc][LOCK].acquire()
            self.modules[proc][LOCK].release()
            return

        if time.time() > self.end_time or self.kill_signal():  # send kill signal
            logging.info(f'Killing all processes.')
            [self.modules[proc][QUEUE].put(None) for _ in range(1000)]
            time.sleep(5)
            self.modules[proc][LOCK].release()
            return

        num = 20  # TODO determine num
        self.data_manager.load_data(proc, num)
        time.sleep(0.1)  # let queue sync up
        self.modules[proc][LOCK].release()
        return

    def run(self):
        """Runs the processor."""
        processes = []
        if self.run_hhblits:
            self.modules[HHBLITS] = {QUEUE: Queue(), LOCK: Lock(), COMPLETED: Queue()}
            for cores in self.hhblits_cores:
                processes.append(Process(target=hhblits.run, args=(self.env, self, cores, self.clustdb)))
                processes[-1].start()

        if self.run_hhfilter:
            self.modules[HHFILTER] = {QUEUE: Queue(), LOCK: Lock(), COMPLETED: Queue()}
            processes.append(Process(target=hhfilter.run, args=(self.env, self)))
            processes[-1].start()

        if self.run_ccmpred:
            self.modules[CCMPRED] = {QUEUE: Queue(), LOCK: Lock(), COMPLETED: Queue()}
            for gpu_num in range(self.ccmpred_gpus):
                processes.append(Process(target=ccmpred.run, args=(self.env, self, gpu_num)))
                processes[-1].start()

        for p in processes:
            p.join()

        self.data_manager.finish()
        logging.info('Processor finished.')
