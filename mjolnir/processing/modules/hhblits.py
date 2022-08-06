import io
import logging
import subprocess as sp
import time

from mjolnir.processing.data_mng import HHBLITS
from mjolnir.processing.processing_data import env_path
from mjolnir.util.format import seq_to_fasta, split


def run(env, processor, cores, clustdb):
    """Runs the hhblits module."""
    while True:
        data = processor.get_data(HHBLITS)
        if data is None:
            break  # kill signal

        entry, seq = data

        fasta = seq_to_fasta(entry, seq)
        fasta_path = env_path(env, 'fasta', f'{entry}.fasta')
        hhr_path = env_path(env, 'hhr', f'{entry}.hhr')
        a3m_path = env_path(env, 'a3m', f'{entry}.a3m')

        with open(fasta_path, 'w') as f:
            f.write(fasta)

        hhblits_cmd = f'hhblits -B 100000 -v 2 -n 2 -cpu {cores} -nodiff -maxfilt 100000 -maxseq 2000000 ' \
                      f'-d {clustdb} -i {fasta_path} -o {hhr_path} -oa3m {a3m_path}'

        time_start = time.time()
        proc = sp.Popen(split(hhblits_cmd), stdout=sp.PIPE, stderr=sp.DEVNULL)

        neff = 0
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            if line.strip().startswith('Neff'):
                neff = float(line.split()[-1])
                break

        time_elapsed = time.time() - time_start
        logging.info(f'HHBlits {entry}, neff={neff:.3f}: {time_elapsed:.2f}')

        processor.task_done(HHBLITS, entry, neff)
