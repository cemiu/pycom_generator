import json
from datetime import datetime

from mjolnir.parsing.xpath import *

q_organism = 'INSERT OR IGNORE INTO organism (organismId, nameScientific, nameCommon, taxonomy) VALUES (?, ?, ?, ?)'
q_disease = 'INSERT OR IGNORE INTO disease (diseaseId, diseaseName, diseaseAcronym, diseaseDescription, ' \
            'diseaseMIM) VALUES (?, ?, ?, ?, ?)'

q_entry = 'INSERT INTO entry (entryId, dateModified, entryName, fullName, shortName, organismId, sequence, ' \
          'sequenceLength, structHelix, structTurn, structStrand, structure, hasAlphaFoldStructure, hasPTM) ' \
          'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
q_keyword = 'INSERT INTO keyword (entryId, keyword) VALUES (?, ?)'
q_disease_entry = 'INSERT INTO disease_entry (entryId, diseaseId) VALUES (?, ?)'
q_pdb = 'INSERT INTO experimentPDB (entryId, pdbId) VALUES (?, ?)'
q_ec = 'INSERT INTO enzyme_class (entryId, enzyme_1, enzyme_2, enzyme_3, enzyme_4) VALUES (?, ?, ?, ?, ?)'
q_cath = 'INSERT INTO cath_class (entryId, cath_1, cath_2, cath_3, cath_4) VALUES (?, ?, ?, ?, ?)'
q_cofactor = 'INSERT OR IGNORE INTO cofactor (cofactorId, cofactorName) VALUES (?, ?)'
q_cofactor_entry = 'INSERT INTO cofactor_entry (entryId, cofactorId) VALUES (?, ?)'
q_substrate = 'INSERT INTO substrate (entryId, substrateName, enzymeClass, rheaId) VALUES (?, ?, ?, ?)'


def insert_organism(db, entry):
    """Inserts an organism into the database, if it doesn't exist."""
    organism_data = (
        entry['organismNcbiId'],  # organismId
        entry['organismScientificName'],  # nameScientific
        entry['organismCommonName'],  # nameCommon
        f":{':'.join(entry['taxonomy'])}:"  # taxonomy
    )
    db.insert(q_organism, organism_data)


def insert_diseases(db, entry):
    """Inserts a disease into the database, if it doesn't exist."""
    for disease in entry['diseases']:
        disease_id = attrib('id')(disease, './up:disease')
        if disease_id is None:
            continue

        # disease_exists = db.exists('disease', 'diseaseId', disease_id)
        disease_exists = False
        if disease_exists:
            continue

        disease_data = (
            disease_id,  # diseaseId
            text()(disease, './up:disease/up:name'),  # diseaseName
            text()(disease, './up:disease/up:acronym'),  # diseaseAcronym
            text()(disease, './up:disease/up:description'),  # diseaseDescription
            attrib('id')(disease, './up:disease/up:dbReference[@type="MIM"]')  # diseaseMIM
        )

        db.insert(q_disease, disease_data)


def insert_entry(db, entry):
    sec_struct = {
        'helix': entry['structureHelix'],
        'turn': entry['structureTurn'],
        'strand': entry['structureStrand'],
    }

    sec_struct_ranges = {}
    for struct_type, ranges in sec_struct.items():
        sec_struct_ranges[struct_type] = ranges[1]

    struct_ranges_json = json.dumps(sec_struct_ranges)

    entry_id = entry['entryId']
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    entry_data = (
        entry_id,  # entryId
        current_date,  # dateModified
        entry['entryName'],  # entryName
        entry['fullName'],  # fullName
        entry['shortName'],  # shortName
        entry['organismNcbiId'],  # organismId
        entry['sequence'],  # sequence
        entry['sequenceLength'],  # sequenceLength
        sec_struct['helix'][0],  # structHelix
        sec_struct['turn'][0],  # structTurn
        sec_struct['strand'][0],  # structStrand
        struct_ranges_json,  # structure
        entry['hasAlphaFoldStructure'],  # hasAlphaFoldStructure
        entry['hasPTM'],  # hasPTM
    )

    db.insert(q_entry, entry_data)

    # Keywords: entryId, keyword
    keyword_data = [(entry_id, keyword) for keyword in entry['keywords']]
    db.insert_many(q_keyword, keyword_data)

    # Diseases: entryId, diseaseId
    disease_data = [(
        entry_id,  # entryId
        attrib('id')(disease, './up:disease')  # diseaseId
    ) for disease in entry['diseases']]
    db.insert_many(q_disease_entry, disease_data)

    # Experiment PDBs
    pdb_data = [(entry_id, pdb_id) for pdb_id in entry['pdbIds']]
    db.insert_many(q_pdb, pdb_data)

    # Enzyme Class: entryId, enzyme_1, enzyme_2, enzyme_3, enzyme_4
    ec_dict = {}
    for ec in entry['enzymeClassId']:
        ec_dict[ec] = tuple([entry_id] + ec.split('.'))

    db.insert_many(q_ec, ec_dict.values())

    # Cath Class
    cath_data = [tuple([entry_id] + cath_id.split('.')) for cath_id in entry['cathClassId']]
    db.insert_many(q_cath, cath_data)

    # Cofactor & Cofactor Entries
    cofactor_entries, cofactor_data = {}, []

    for cofactor in entry['cofactors']:
        c_name = text()(cofactor, './up:name')
        c_id = attrib('id')(cofactor, './up:dbReference[@type="ChEBI"]')

        cofactor_data.append((c_id, c_name))
        cofactor_entries[c_id] = (entry['entryId'], c_id)

    db.insert_many(q_cofactor, cofactor_data)
    db.insert_many(q_cofactor_entry, cofactor_entries.values())

    # Substrate: entryId, substrateName, enzymeClass, rheaId
    substrate_data = [(entry_id,) + substrate for substrate in entry['substrates']]
    db.insert_many(q_substrate, substrate_data)
