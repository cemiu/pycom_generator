import queue
import time
from multiprocessing import Process

from mjolnir.processing import data_mng
from mjolnir.processing.modules import hhblits, hhfilter, ccmpred


class Processor:
    def __init__(self, params):
        self.params = params
        self.env = params['env']

        # self params
        self.run_hhblits = params['run_hhblits']
        self.run_hhfilter = params['run_hhfilter']
        self.run_ccmpred = params['run_ccmpred']

        # module params
        self.handler = data_mng.handler_setup(env=self.env)
        self.end_time = (time.time() + (params['max_time']) if 'max_time' in params else float('inf'))

        self.clustdb = params['clustdb'] if 'clustdb' in params else None
        self.hhblits_cores = params['hhblits_cores'] if 'hhblits_cores' in params else []
        self.hhfilter_threads = params['hhfilter_threads'] if 'hhfilter_threads' in params else 1
        self.ccmpred_gpus = params['gpu_count'] if 'gpu_count' in params else 0

    def run(self):
        """Runs the processor."""
        if self.run_hhblits:
            Process(target=hhblits.manager,
                    args=(self.env, self.handler, self.end_time, self.hhblits_cores, self.clustdb)).start()

        if self.run_hhfilter:
            Process(target=hhfilter.manager, args=(self.env, self.handler, self.end_time, self.hhfilter_threads))\
                .start()

        if self.run_ccmpred:
            Process(target=ccmpred.manager, args=(self.env, self.handler, self.end_time, self.ccmpred_gpus)).start()


def queue_to_list(in_queue, revert=False, wait=False):
    out_list = []
    while True:
        try:
            if revert:
                out_list.append((None, in_queue.get(block=wait, timeout=5)))
            else:
                out_list.append(in_queue.get(block=wait, timeout=5))
        except queue.Empty:
            break
    return out_list
