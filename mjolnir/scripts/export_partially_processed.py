import os
import sqlite3
import time
from zipfile import ZipFile

# noinspection PyUnresolvedReferences
import __init__
import mjolnir.util.script_util as util

error_msg = "Usage: export_partially_processed.py <in_db> <processing_dir> <out_db> <out_zip> [--overwrite]"

table_transfer = (
    '''CREATE TABLE IF NOT EXISTS transfer.transfer (
        entryId TEXT PRIMARY KEY,
        sequence TEXT,
        processingStep INTEGER,
        handlerId INTEGER,
        lastChange TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS transfer_entryId_processingStep ON transfer (processingStep)',
    ))


def zstd_or_aln(en, path):
    f = os.path.join(path, f'{en}.aln.zstd')
    if os.path.exists(f):
        return f
    elif os.path.exists(f[:-5]):
        return f[:-5]
    return None


if __name__ == '__main__':
    """
    Export partially processed (HHBlits) to a transfer DB,
    and zip all aln / aln.zstd files.
    
    export_partially_processed.py <in_db> <processing_dir> <out_db> <out_zip> [--overwrite]
    """
    print("Selecting all sequences with processingStep = 2 (post-HHBlits)")

    in_db, proc_dir, out_db, out_zip, *args = util.args_to_tuple(num_min=4, num_max=5, error_msg=error_msg)
    util.file_exists(in_db, exit_if_not_found=True, error_msg=f'{in_db} not found')
    util.dir_exists(proc_dir, exit_if_not_found=True, error_msg=f'{proc_dir} directory not found')
    overwrite = args and args[0] == '--overwrite'
    if not overwrite:
        util.file_exists(out_db, exit_if_found=True, error_msg=f'{out_db} already exists, use --overwrite.')
        util.file_exists(out_zip, exit_if_found=True, error_msg=f'{out_zip} already exists, use --overwrite.')
    util.remove((out_db, out_zip))
    util.mkdir_f((out_db, out_zip))

    time_s = time.time()

    table, indices = table_transfer

    with sqlite3.connect(in_db, isolation_level='DEFERRED') as con:
        c = con.cursor()
        c.execute(f'ATTACH "{out_db}" AS transfer')

        c.execute(table)

        # pull all entries processed by HHBlits into new DB
        c.execute('''
            INSERT INTO transfer.transfer (entryId, sequence, processingStep, handlerId, lastChange)
            SELECT entryId, sequence, processingStep, handlerId, DATETIME('now')
            FROM processing
            WHERE processingStep = 2''')

        # # update 2 to 3 in processing table (mark exported) todo: change to 3
        c.execute('''
            UPDATE processing
            SET processingStep = 2,
                 lastChange = DATETIME('now')
            WHERE processingStep = 2''')

    with sqlite3.connect(out_db, isolation_level='DEFERRED') as con:
        c = con.cursor()
        for index in indices:
            c.execute(index)

        c.execute('''
            SELECT entryId
            FROM transfer
            WHERE processingStep = 2''')

    with ZipFile(out_zip, 'w') as z:
        for entry in c.fetchall():
            entry = entry[0]
            aln = zstd_or_aln(entry, proc_dir)
            if aln:
                z.write(aln, os.path.basename(aln))
            else:
                print(f'Critical: {entry} not found')

    print(f'Done in {time.time() - time_s:.2f} seconds.')
