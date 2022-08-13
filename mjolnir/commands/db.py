import logging
import os

from mjolnir import config
from mjolnir.db import db_load, models
from mjolnir.util import DBUtil

from mjolnir.util import exit_util as eu
from mjolnir.util.error_util import silentremove


def db(args):
    if not (args.init or args.init_force or args.load or args.build_index):
        eu.err_exit('No action specified. Please run `mjolnir db --help` for more information.')

    database = None

    if args.init or args.init_force:
        if os.path.exists(args.location):
            if not args.init_force:
                eu.err_exit(f'Database already exists at {args.location}. Use --init-force to overwrite.')
            try:
                silentremove(args.location)
            except OSError:
                eu.err_exit(f'Could not remove database at {args.location}. Is it open in another program?')

        os.makedirs(os.path.dirname(args.location), exist_ok=True)

        logging.info(f'Initializing database at {args.location}')
        database = DBUtil(args.location,
                          models.entry_model,
                          init=True,
                          compression=config['enable_compression_entries'],
                          commit_frequency=config['commit_frequency'])

    if not os.path.exists(args.location):
        eu.err_exit(f'Database {args.location} does not exist. Use [db --init] to create a new database.')

    if database is None:
        database = DBUtil(args.location,
                          models.entry_model,
                          compression=config['enable_compression_entries'],
                          commit_frequency=config['commit_frequency'])

    if args.load:
        logging.info(f'Loading data from {len(args.load)} file{"s" if len(args.load) > 1 else ""}: '
                     f'{", ".join(args.load)}')
        if len(args.load) > 1 and (args.start or args.end is not None):
            eu.err_exit('Cannot specify --start or --end when loading multiple files. Aborting.')

        if (args.end is not None and (args.start > args.end)) or args.start < 0:
            eu.err_exit('Start index must be less than end index cannot be negative. Aborting.')

        db_load.load_from_file(database, args.load, start=args.start, end=args.end)

    if args.build_index:
        logging.info('Creating all missing indices.')
        database.indices_create()
