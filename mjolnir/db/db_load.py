import logging

from mjolnir.db import inserter
from mjolnir.parsing import uniprot_model
from mjolnir.util import ModelParser


def load_from_file(db, files, start=0, end=None):
    """Loads data from a file into a database."""
    # drop indices before loading data, for performance
    logging.info('Dropping indices before loading data, if any exist. This may take a while.')
    db.indices_drop()
    logging.info('Dropped indices.')

    for file in files:
        logging.info(f'Loading data from {file}')
        if start >= 2:
            logging.info(f'Skipping first {start} entries in file.')

        parser = ModelParser(file, info=True, model=uniprot_model, skip=start, abort_after=end)
        for entry in parser:
            inserter.insert_organism(db, entry)
            inserter.insert_diseases(db, entry)
            inserter.insert_entry(db, entry)

        logging.info(f'Finished loading {parser.info.count} entries from {file}')

    db.hard_commit()

    logging.info('Finished loading all data. Staring indexing.')

    db.indices_create()

    logging.info('Finished indexing.')
