import logging
import os

def db(args):
    logging.info(args)  # TODO remove this line

    if args.init:
        logging.info(f'Initializing database at {args.location}')
        pass

    # check if specified database exists
    if not os.path.exists(args.location):
        logging.critical(f'Database {args.location} does not exist. Use [db --init] to create a new database.')
        return

    # print information about the database

    if args.load:
        logging.info(f'Loading data from {args.load}')
        pass

    if args.update:
        logging.info('Updating database from UniProt')
        pass
