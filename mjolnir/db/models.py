
# todo: load queries dynamically from a model, instead of hardcoding them

"""sqlite models file"""
tables_and_indices = {
    'entry': ['''
    CREATE TABLE IF NOT EXISTS entry (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        dateModified TEXT,
        entryName TEXT,
        fullName TEXT,
        shortName TEXT,
        organismId TEXT,
        sequence TEXT,
        sequenceLength INTEGER,
        structHelix REAL,
        structTurn REAL,
        structStrand REAL,
        structure TEXT,
        hasAlphaFoldStructure BOOL,
        hasPTM BOOL
    )'''],  # index: entryId, organismId?, structH/T/S

    'organism': ['''
    CREATE TABLE IF NOT EXISTS organism (
        organismId TEXT PRIMARY KEY,
        nameScientific TEXT,
        nameCommon TEXT,
        taxonomy TEXT
    )'''],

    'disease': ['''
    CREATE TABLE IF NOT EXISTS disease (
        diseaseId TEXT PRIMARY KEY,
        diseaseName TEXT,
        diseaseAcronym TEXT,
        diseaseDescription TEXT,
        diseaseMIM TEXT
    )'''],

    # todo maybe change pk?
    'disease_entry': ['''
    CREATE TABLE IF NOT EXISTS disease_entry (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        diseaseId TEXT
    )'''],

    'keyword': ['''
    CREATE TABLE IF NOT EXISTS keyword (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        keyword TEXT
    )''', '''
    CREATE INDEX IF NOT EXISTS keyword_entryId ON keyword (entryId)
    '''],

    # removed composite pk
    'experimentPDB': ['''
    CREATE TABLE IF NOT EXISTS experimentPDB (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        pdbId TEXT
    )''', '''
    CREATE INDEX IF NOT EXISTS experimentPDB_entryId ON experimentPDB (entryId)
    '''],

    # no pk, index by entryId and (1,2,3,4)
    'enzyme_class': ['''
    CREATE TABLE IF NOT EXISTS enzyme_class (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        enzyme_1 TEXT,
        enzyme_2 TEXT,
        enzyme_3 TEXT,
        enzyme_4 TEXT
    )''', '''
    CREATE INDEX IF NOT EXISTS enzyme_class_entryId ON enzyme_class (entryId)
    ''', '''
    CREATE INDEX IF NOT EXISTS enzyme_class_ec ON enzyme_class (enzyme_1, enzyme_2, enzyme_3, enzyme_4)
    '''],

    'cath_class': ['''
    CREATE TABLE IF NOT EXISTS cath_class (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        cath_1 TEXT,
        cath_2 TEXT,
        cath_3 TEXT,
        cath_4 TEXT
    )''', '''
    CREATE INDEX IF NOT EXISTS cath_entryId ON cath_class (entryId)
    ''', '''
    CREATE INDEX IF NOT EXISTS cath_cath_id ON cath_class (cath_1, cath_2, cath_3, cath_4)
    '''],

    # create cofactorId <-> cofactorName table, and another entryId <-> cofactorId table, w/o duplicates in either
    'cofactor': ['''
    CREATE TABLE IF NOT EXISTS cofactor (
        cofactorId TEXT PRIMARY KEY,
        cofactorName TEXT
    )'''],

    'cofactor_entry': ['''
    CREATE TABLE IF NOT EXISTS cofactor_entry (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        cofactorId TEXT
    )'''],

    'substrate': ['''
    CREATE TABLE IF NOT EXISTS substrate (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        substrateName TEXT,
        enzymeClass TEXT,
        rheaId TEXT
    )'''],
}

"""
List of unused tables:

    # removed ability to query by secondary accession
    'entry_id_map': ['''
    CREATE TABLE IF NOT EXISTS entry_id_map (
        entryId TEXT,
        accessionId TEXT,
        PRIMARY KEY (entryId, accessionId)
    )''', '''
    CREATE INDEX IF NOT EXISTS entry_id_map_entryId ON entry_id_map (entryId)
    ''', '''
    CREATE INDEX IF NOT EXISTS entry_id_map_accessionId ON entry_id_map (accessionId)
    '''],
    
    # will instead store structures in main table, in a concatenated format
    'secondary_structure': ['''
    CREATE TABLE IF NOT EXISTS secondary_structure (
        entryId TEXT,
        type TEXT,
        begin INTEGER,
        end INTEGER,
        PRIMARY KEY (entryId, begin, end)
    )''', '''
    CREATE INDEX IF NOT EXISTS secondary_structure_entryId ON secondary_structure (entryId)
    '''],


"""
