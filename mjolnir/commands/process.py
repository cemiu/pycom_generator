import logging
import multiprocessing as mp
import os
import re

from mjolnir.processing import init_environment, Processor
from mjolnir.util import gpu_util, exit_util as eu


def process(args):
    if not (args.init_env or args.run):
        eu.err_exit('No action specified. Please run `mjolnir process --help` for more information.')

    if args.init_env:
        eu.err_exit(do_exit=(not os.path.exists(args.location)),
                    msg=f'The specified entry DB {args.location} does not exist.\n'
                        f'Please specify a valid entry DB location or create it using `mjolnir db [args]`.')

        eu.err_exit(do_exit=(os.path.exists(args.env) and len(os.listdir(args.env)) > 0),
                    msg=f'The specified environment {args.env} already exists.')

        init_environment(args.location, args.env)

    if args.run:
        eu.err_exit(do_exit=(not os.path.exists(args.env)),
                    msg=f'The specified processing environment {args.env} does not exist.\n'
                        f'Please run `mjolnir process --init-env` to create the environment.')

        run_hhblits = 'hhblits' in args.run or 'all' in args.run
        run_hhfilter = 'hhfilter' in args.run or 'all' in args.run
        run_ccmpred = 'ccmpred' in args.run or 'all' in args.run

        process_params = validate_setup(args, run_hhblits, run_hhfilter, run_ccmpred)

        logging.info(f'Starting processing with: {",".join(args.run)}')
        Processor(process_params).run()


def validate_setup(args, r_hhblits, r_hhfilter, r_ccmpred):
    results = {
        'env': args.env,
        'run_hhblits': r_hhblits,
        'run_hhfilter': r_hhfilter,
        'run_ccmpred': r_ccmpred
    }

    os.path.join(args.env, 'process.db')

    cpu_count = min(args.cpu_count, mp.cpu_count()) if args.cpu_count else mp.cpu_count()

    if r_hhfilter:
        eu.which_exit('hhfilter')
        [eu.which_exit(t, reason='hhfilter for generating .aln files') for t in ['egrep', 'sed', 'sort']]
        results['hhfilter_threads'] = args.hhfilter_threads if args.hhfilter_threads else 1
        cpu_count -= 1

    if r_ccmpred:
        eu.which_exit('ccmpred')
        eu.which_exit('nvidia-smi', reason='ccmpred')
        gpu_count = min(args.gpu_count, gpu_util.gpu_count()) if args.gpu_count else gpu_util.gpu_count()
        eu.err_exit(do_exit=(gpu_count == 0), msg='No GPUs found. CCMPred requires CUDA GPUs and drivers.')
        results['gpu_count'] = gpu_count
        cpu_count -= int(gpu_count / 4)

    if r_hhblits:
        eu.which_exit('hhblits')
        # aim for 6 logical cores per hhblits instance
        hhblits_processes = max(cpu_count // 6, 1)
        # divvy up the threads among the hhblits instances
        cores_per_process = [cpu_count // hhblits_processes] * hhblits_processes
        for i in range(cpu_count % hhblits_processes):
            cores_per_process[i] += 1
        results['hhblits_cores'] = cores_per_process

        clustdb_path = args.clustdb if args.clustdb else os.environ['CLUSTDB'] if 'CLUSTDB' in os.environ else None
        if clustdb_path:
            if os.path.exists(f'{clustdb_path}_a3m.ffdata'):
                results['clustdb'] = clustdb_path
            elif os.path.isdir(clustdb_path):
                for file in os.listdir(clustdb_path):
                    if file.endswith('_a3m.ffdata'):
                        results['clustdb'] = clustdb_path[:-len('_a3m.ffdata')]
                        break

        eu.err_exit(do_exit=('clustdb' not in results),
                    msg='Clustering DB for HHBlits needs to be specified through --clustdb or $CLUSTDB env entry.\n'
                        'Should point to directory containing the clustering ffindex / ffdata files\n'
                        'Either in `/path/to/db/` or `/path/to/db/UniRef30_2022_02` format.\n'
                        'More info here: https://github.com/soedinglab/hh-suite')

    if args.max_time:
        eu.err_exit(do_exit=not re.match(r'^(\d+):(\d+):(\d+)$', args.max_time), msg='Invalid max time format. Must '
                                                                                     'be HH:MM:SS.')
        h, m, s = args.max_time.split(':')
        results['max_time'] = int(h) * 3600 + int(m) * 60 + int(s)

    return results
