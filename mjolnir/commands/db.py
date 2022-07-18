import logging
import os

from mjolnir import config
from mjolnir.util import DBUtil
from mjolnir.db import db_load


def db(args):
    database = None

    if args.init:
        # todo remove: temp: remove database if extension is .db
        if os.path.exists(args.location) and os.path.splitext(args.location)[1] == '.db':
            os.remove(args.location)
        logging.info(f'Initializing database at {args.location}')
        database = DBUtil(args.location, init=True,
                          compression=config['enable_compression'], commit_frequency=config['commit_frequency'])

    if not os.path.exists(args.location):
        logging.critical(f'Database {args.location} does not exist. Use [db --init] to create a new database.')
        return

    logging.info('Database found.')
    if database is None:
        database = DBUtil(args.location,
                          compression=config['enable_compression'], commit_frequency=config['commit_frequency'])

    # todo print info about the database later?

    if args.load:  # todo accept multiple files
        logging.info(f'Loading data from {args.load}')
        db_load.load_from_file(database, args.load)
        pass

    if args.update:
        logging.info('Updating database from UniProt')
        pass
