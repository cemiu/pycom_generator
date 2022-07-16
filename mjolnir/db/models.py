

"""sqlite models file"""
tables_and_indices = {
    'entry': ['''
    CREATE TABLE IF NOT EXISTS entry (
        entryId TEXT PRIMARY KEY,
        dateModified TEXT,
        entryName TEXT,
        fullName TEXT,
        shortName TEXT,
        organismId TEXT,
        sequence TEXT,
        sequenceLength INTEGER,
        makeupHelix REAL,
        makeupTurn REAL,
        makeupStrand REAL,
        hasAlphaFoldStructure BOOL,
        hasPTM BOOL
    )''', '''
    CREATE INDEX IF NOT EXISTS entry_organismId ON entry (organismId)
    ''', '''
    CREATE INDEX IF NOT EXISTS entry_helix ON entry (makeupHelix)
    ''', '''
    CREATE INDEX IF NOT EXISTS entry_turn ON entry (makeupTurn)
    ''', '''
    CREATE INDEX IF NOT EXISTS entry_strand ON entry (makeupStrand)
    '''],
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
    'disease_entry': ['''
    CREATE TABLE IF NOT EXISTS disease_entry (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        diseaseId TEXT,
        description TEXT
    )''', '''
    CREATE INDEX IF NOT EXISTS disease_entry_entryId ON disease_entry (entryId)
    '''],
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
    'keyword': ['''
    CREATE TABLE IF NOT EXISTS keyword (
        entryId TEXT,
        keyword TEXT,
        PRIMARY KEY (entryId, keyword)
    )''', '''
    CREATE INDEX IF NOT EXISTS keyword_entryId ON keyword (entryId)
    '''],
    'experimentPDB': ['''
    CREATE TABLE IF NOT EXISTS experimentPDB (
        entryId TEXT,
        pdbId TEXT,
        PRIMARY KEY (entryId, pdbId)
    )''', '''
    CREATE INDEX IF NOT EXISTS experimentPDB_entryId ON experimentPDB (entryId)
    '''],
    'enzyme_class': ['''
    CREATE TABLE IF NOT EXISTS enzyme_class (
        entryId TEXT,
        enzymeClass TEXT,
        PRIMARY KEY (entryId, enzymeClass)
    )''', '''
    CREATE INDEX IF NOT EXISTS enzyme_class_entryId ON enzyme_class (entryId)
    '''],
    'cath_class': ['''
    CREATE TABLE IF NOT EXISTS cath_class (
        entryId TEXT,
        cathClass TEXT,
        PRIMARY KEY (entryId, cathClass)
    )''', '''
    CREATE INDEX IF NOT EXISTS cath_class_entryId ON cath_class (entryId)
    '''],
    'cofactor': ['''
    CREATE TABLE IF NOT EXISTS cofactor (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        cofactorId TEXT,
        cofactorName TEXT
    )''', '''
    CREATE INDEX IF NOT EXISTS cofactor_entryId ON cofactor (entryId)
    '''],
    'substrate': ['''
    CREATE TABLE IF NOT EXISTS substrate (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        substrateName TEXT,
        enzymeClass TEXT,
        rheaId TEXT
    )''', '''
    CREATE INDEX IF NOT EXISTS substrate_entryId ON substrate (entryId)
    '''],
}

"""
List of unused tables:

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
    
    


"""
