
from mjolnir.db import inserter
from mjolnir.parsing import uniprot_model
from mjolnir.util import ModelParser


def load_from_file(db, file_location):
    """Loads data from a file into a database."""
    for entry in ModelParser(file_location, info=True, model=uniprot_model):
        # 1. check if organism+taxonomy exists, if not, insert
        inserter.insert_organism(db, entry)

        # 2. check if diseases exists, if not, insert
        inserter.insert_diseases(db, entry)

        # 3. insert entry
        inserter.insert_entry(db, entry)

    db.hard_commit()
