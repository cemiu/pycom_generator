import os
import sqlite3
import time

# noinspection PyUnresolvedReferences
import __init__
import mjolnir.util.script_util as util

error_msg = "Usage: export_db_for_processing.py <db_file> <output_file> [--overwrite]"

table_processing = (
    '''CREATE TABLE IF NOT EXISTS proc.processing (
        entryId TEXT PRIMARY KEY,
        sequence TEXT,
        processingStep INTEGER,
        handlerId INTEGER,
        lastChange TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_sequence ON processing (sequence)',
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_processingStep ON processing (processingStep)',
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_handlerId ON processing (handlerId)',
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_lastChange ON processing (lastChange)',
    ))

if __name__ == '__main__':
    """
    Export the entry database to a processing database.
    Usage: export_db_for_processing.py <db_file> <output_file> [--overwrite]
    Selection conditions can be adjusted in the "INSERT INTO" query below.
    """
    print("Selecting all sequences up to length=500, can be changed in the code")
    entry_db, out_db, *args = util.args_to_tuple(num_min=2, num_max=3, error_msg=error_msg)
    util.file_exists(entry_db, exit_if_not_found=True, error_msg=f'{entry_db} not found')
    overwrite = args and args[0] == '--overwrite'
    if not overwrite:
        util.file_exists(out_db, exit_if_found=True, error_msg=f'{out_db} already exists, use --overwrite.')
    elif os.path.exists(out_db):
        os.remove(out_db)

    time_s = time.time()

    table, indices = table_processing
    with sqlite3.connect(entry_db, isolation_level='DEFERRED') as con:
        c = con.cursor()
        c.execute(f'ATTACH "{out_db}" AS proc')
        c.execute(table)

        # pull all entries into new DB
        c.execute('''
            INSERT INTO proc.processing (entryId, sequence, processingStep, handlerId, lastChange)
            SELECT entryId, sequence, 0, NULL, NULL
            FROM entry
            WHERE (length(sequence) <= 500 AND length(sequence) >= 5)
            GROUP BY sequence''')

        for index in indices:
            c.execute(index)

    print(f'Done in {time.time() - time_s:.2f} seconds.')
