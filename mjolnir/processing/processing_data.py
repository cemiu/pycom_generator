import os

dbvar = {
    'table': '''CREATE TABLE IF NOT EXISTS proc.processing (
        entryId TEXT PRIMARY KEY,
        sequence TEXT,
        processingStep INTEGER,
        neff REAL,
        handlerId INTEGER,
        lastChange TEXT
    )''',
    'indices': (
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_sequence ON processing (sequence)',
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_processingStep ON processing (processingStep)',
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_handlerId ON processing (handlerId)',
        'CREATE INDEX IF NOT EXISTS proc.processing_entryId_lastChange ON processing (lastChange)',
    ),
    'table_handlers': '''CREATE TABLE IF NOT EXISTS proc.handlers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lastUpdate TEXT
    )''',
    'insert_handler': 'INSERT INTO handlers (lastUpdate) VALUES (datetime("now"))',
    'create_insert': lambda max_seq_len=500: f'''
            INSERT INTO proc.processing (entryId, sequence, processingStep, handlerId, lastChange)
            SELECT entryId, sequence, 0, NULL, NULL
            FROM entry
            WHERE length(sequence) <= {max_seq_len}
            GROUP BY sequence''',
    'mark_unique': 'SELECT NULL FROM processing WHERE processingStep = ? AND handlerId = ? AND lastChange= ? LIMIT 1',
    'mark_update': lambda limit=1: f'''
            UPDATE processing
            SET processingStep = ?, handlerId = ?, lastChange = ?
            WHERE entryId IN
                (SELECT entryId FROM processing
                 WHERE (processingStep = ? AND handlerId IS NULL)
                 LIMIT {limit})''',
    'mark_select': lambda columns='entryId, sequence': f'''
            SELECT {columns} FROM processing
            WHERE processingStep = ? AND handlerId = ? AND lastChange = ?'''
}

env_structure = {
    'fasta': 'proc/fasta',
    'hhr': 'proc/hhr',
    'a3m': 'proc/a3m',
    'oa3m': 'proc/oa3m',
    'aln': 'proc/aln',
    'mat': 'proc/mat',
    'fasta-done': 'extra/fasta',
    'hhr-done': 'extra/hhr',
    'a3m-done': 'extra/a3m',
    'oa3m-done': 'extra/oa3m',
    'aln-done': 'done/aln',
    'mat-done': 'done/mat',
}


def env_path(path, spec, file=None):
    if spec == 'db':
        return os.path.join(path, 'processing.db')
    dir_path = os.path.join(path, env_structure[spec])
    return os.path.join(dir_path, file) if file else dir_path


__all__ = ['env_path', 'env_structure', 'dbvar']