
"""sqlite models file"""
entry_model = {
    'entry': ('''
    CREATE TABLE IF NOT EXISTS entry (
        pk INTEGER PRIMARY KEY,
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
        hasPTM BOOL,
        resultId INTEGER, /* 0+:id, -1:processing */
        resultDate TEXT
    )''', ('CREATE INDEX IF NOT EXISTS entry_entryId ON entry (entryId)',
           'CREATE INDEX IF NOT EXISTS entry_organismId ON entry (organismId)',
           'CREATE INDEX IF NOT EXISTS entry_structH ON entry (structHelix)',
           'CREATE INDEX IF NOT EXISTS entry_structT ON entry (structTurn)',
           'CREATE INDEX IF NOT EXISTS entry_structS ON entry (structStrand)',
           'CREATE INDEX IF NOT EXISTS entry_sequence ON entry (sequence)',)),

    'organism': ('''
    CREATE TABLE IF NOT EXISTS organism (
        organismId TEXT PRIMARY KEY,
        nameScientific TEXT,
        nameCommon TEXT,
        taxonomy TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS organism_taxonomy ON organism (taxonomy)',
    )),

    'disease': ('''
    CREATE TABLE IF NOT EXISTS disease (
        diseaseId TEXT PRIMARY KEY,
        diseaseName TEXT,
        diseaseAcronym TEXT,
        diseaseDescription TEXT,
        diseaseMIM TEXT
    )''', ()),

    'disease_entry': ('''
    CREATE TABLE IF NOT EXISTS disease_entry (
        pk INTEGER PRIMARY KEY,
        entryId TEXT,
        diseaseId TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS disease_entry_entryId ON disease_entry (entryId)',
        'CREATE INDEX IF NOT EXISTS disease_entry_diseaseId ON disease_entry (diseaseId)',
    )),

    'keyword': ('''
    CREATE TABLE IF NOT EXISTS keyword (
        pk INTEGER PRIMARY KEY,
        entryId TEXT,
        keyword TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS keyword_entryId ON keyword (entryId)',
        'CREATE INDEX IF NOT EXISTS keyword_keyword ON keyword (keyword)',
    )),

    # removed composite pk
    'experimentPDB': ('''
    CREATE TABLE IF NOT EXISTS experimentPDB (
        pk INTEGER PRIMARY KEY,
        entryId TEXT,
        pdbId TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS experimentPDB_entryId ON experimentPDB (entryId)',
        'CREATE INDEX IF NOT EXISTS experimentPDB_pdbId ON experimentPDB (pdbId)',
    )),

    # no pk, index by entryId and (1,2,3,4)
    'enzyme_class': ('''
    CREATE TABLE IF NOT EXISTS enzyme_class (
        pk INTEGER PRIMARY KEY,
        entryId TEXT,
        enzyme_1 TEXT,
        enzyme_2 TEXT,
        enzyme_3 TEXT,
        enzyme_4 TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS enzyme_class_entryId ON enzyme_class (entryId)',
        'CREATE INDEX IF NOT EXISTS enzyme_class_ecId ON enzyme_class (enzyme_1, enzyme_2, enzyme_3, enzyme_4)',
    )),

    'cath_class': ('''
    CREATE TABLE IF NOT EXISTS cath_class (
        pk INTEGER PRIMARY KEY,
        entryId TEXT,
        cath_1 TEXT,
        cath_2 TEXT,
        cath_3 TEXT,
        cath_4 TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS cath_class_entryId ON cath_class (entryId)',
        'CREATE INDEX IF NOT EXISTS cath_class_cathId ON cath_class (cath_1, cath_2, cath_3, cath_4)',
    )),

    'cofactor': ('''
    CREATE TABLE IF NOT EXISTS cofactor (
        cofactorId TEXT PRIMARY KEY,
        cofactorName TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS cofactor_cofactorId ON cofactor (cofactorId)',
    )),

    'cofactor_entry': ('''
    CREATE TABLE IF NOT EXISTS cofactor_entry (
        pk INTEGER PRIMARY KEY,
        entryId TEXT,
        cofactorId TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS cofactor_entry_entryId ON cofactor_entry (entryId)',
        'CREATE INDEX IF NOT EXISTS cofactor_entry_cofactorId ON cofactor_entry (cofactorId)',
    )),

    'substrate': ('''
    CREATE TABLE IF NOT EXISTS substrate (
        pk INTEGER PRIMARY KEY,
        entryId TEXT,
        substrateName TEXT,
        enzymeClass TEXT,
        rheaId TEXT
    )''', (
        'CREATE INDEX IF NOT EXISTS substrate_entryId ON substrate (entryId)',
    )),
}

result_model = {
    'result': ('''
    CREATE TABLE IF NOT EXISTS result (
        resultId INTEGER PRIMARY KEY,
        resultDate TEXT,
        entryId TEXT,
        result TEXT
    )''', ())
}
