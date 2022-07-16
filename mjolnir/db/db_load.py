import time

from mjolnir.db import inserter
from mjolnir.util import xml_util

_PRINT_DATA = False

def load_from_file(db, file_location):

    count_entries = 0  # info
    count_organisms = 0
    time_start = time.time()
    time_last = time_start

    """Loads data from a file into a database."""
    for entry in xml_util.parse_uniprot(file_location):
        if _PRINT_DATA:
            print(entry, end='\n\n')

        # todo 0. check for conflict, clean up if needed

        # 1. check if organism+taxonomy exists, if not, insert
        organism_is_new = inserter.insert_organism(db, entry)

        # 2. check if diseases exists, if not, insert
        diseases_are_new = inserter.insert_diseases(db, entry)

        # 3. insert entry
        inserter.insert_entry(db, entry)

        count_entries += 1  # info
        if time.time() - time_last > 1:
            sec_for_1k = (time.time() - time_start) / (count_entries / 10000)
            print(f'{count_entries} entries inserted at {sec_for_1k:.2f} sec/10k')
            time_last = time.time()
