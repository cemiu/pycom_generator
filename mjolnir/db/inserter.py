import lxml.etree as ET
from datetime import datetime

from mjolnir import config
from mjolnir.parsing.xpath import *

def insert_organism(db, entry):
    """Inserts an organism into the database, if it doesn't exist."""
    # organism_exists = db.exists('organism', 'organismId', entry['organismNcbiId'])
    organism_exists = False  # todo remove
    if not organism_exists:
        db.insert_data('organism', {
            'organismId': entry['organismNcbiId'],
            'nameScientific': entry['organismScientificName'],
            'nameCommon': entry['organismCommonName'],
            'taxonomy': ':'.join(entry['taxonomy']),
        }, ignore_duplicates=True)

    return organism_exists


def insert_diseases(db, entry):
    """Inserts a disease into the database, if it doesn't exist."""
    inserted = False
    for disease in entry['diseases']:
        disease_id = attrib('id')(disease, './up:disease')
        if disease_id is None:
            continue

        # disease_exists = db.exists('disease', 'diseaseId', disease_id)
        disease_exists = False
        if disease_exists:
            continue

        disease_data = {
            'diseaseId': disease_id,
            'diseaseName': text()(disease, './up:disease/up:name'),
            'diseaseAcronym': text()(disease, './up:disease/up:acronym'),
            'diseaseDescription': text()(disease, './up:disease/up:description'),
            'diseaseMIM': attrib('id')(disease, './up:disease/up:dbReference[@type="MIM"]')
        }

        db.insert_data('disease', disease_data, ignore_duplicates=True)
        inserted = True

    return inserted


def insert_entry(db, entry):
    sec_struct = {
        'helix': entry['structureHelix'],
        'turn': entry['structureTurn'],
        'strand': entry['structureStrand'],
    }

    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    entry_data = {
        'entryId': entry['entryId'],
        'dateModified': current_date,
        'entryName': entry['entryName'],
        'fullName': entry['fullName'],
        'shortName': entry['shortName'],
        'organismId': entry['organismNcbiId'],
        'sequence': entry['sequence'],
        'sequenceLength': entry['sequenceLength'],
        'makeupHelix': sec_struct['helix'][0],
        'makeupTurn': sec_struct['turn'][0],
        'makeupStrand': sec_struct['strand'][0],
        'hasAlphaFoldStructure': entry['hasAlphaFoldStructure'],
        'hasPTM': entry['hasPTM'],
    }

    db.insert_data('entry', entry_data)

    for accession in entry['accessions']:
        db.insert_data('entry_id_map', {
            'entryId': entry['entryId'],
            'accessionId': accession,
        })

    for keyword in entry['keywords']:
        db.insert_data('keyword', {
            'entryId': entry['entryId'],
            'keyword': keyword,
        })

    for disease in entry['diseases']:
        db.insert_data('disease_entry', {
            'entryId': entry['entryId'],
            'diseaseId': attrib('id')(disease, './up:disease'),
            'description': text()(disease, './up:text'),
        })

    for pdb in entry['experimentPDBIds']:
        db.insert_data('experimentPDB', {
            'entryId': entry['entryId'],
            'pdbId': pdb,
        })

    for ec in entry['enzymeClassId']:
        db.insert_data('enzyme_class', {
            'entryId': entry['entryId'],
            'enzymeClass': ec,
        }, ignore_duplicates=True)

    for cath in entry['cathClassId']:
        db.insert_data('cath_class', {
            'entryId': entry['entryId'],
            'cathClass': cath,
        })

    for strucType, composition in sec_struct.items():
        for r in composition[1]:
            db.insert_data('secondary_structure', {
                'entryId': entry['entryId'],
                'type': strucType,
                'begin': r[0],
                'end': r[1],
            })

    for cofactor in entry['cofactors']:
        c_name = text()(cofactor, './up:name')
        c_id = attrib('id')(cofactor, './up:dbReference[@type="ChEBI"]')
        db.insert_data('cofactor', {
            'entryId': entry['entryId'],
            'cofactorName': c_name,
            'cofactorId': c_id,
        })

    for substrate in entry['substrates']:
        name, ec, rhea = substrate
        db.insert_data('substrate', {
            'entryId': entry['entryId'],
            'substrateName': name,
            'enzymeClass': ec,
            'rheaId': rhea,
        })
