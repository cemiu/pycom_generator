from mjolnir.parsing.post_processing import *
from mjolnir.parsing.xpath import *


_all_names = '*[self::up:recommendedName or self::up:alternativeName]'

"""Structure defining the extraction strategy for the UniProt XML fields.

Definition: field_name: [xpath, extractor, [post_process]]

Performance notes:
    single > all > xpath
    specify index [1] where possible
"""
struct = {
    'entryId': [
        './up:accession[1]',
        text(),
    ],
    'entryName': [
        './up:name[1]',
        text(),
    ],
    'fullName': [
        './up:protein[1]/up:recommendedName[1]/up:fullName',
        text(),
    ],
    'shortName': [
        './up:protein[1]/up:recommendedName[1]/up:shortName',
        text(),
    ],
    'taxonomy': [
        './up:organism[1]/up:lineage[1]/up:taxon',
        alltext(),
    ],
    'organismNcbiId': [
        './up:organism[1]/up:dbReference',
        attrib('id'),
    ],
    'organismScientificName': [
        './up:organism[1]/up:name[@type="scientific"]',
        text(),
    ],
    'organismCommonName': [
        './up:organism[1]/up:name[@type="common"]',
        text(),
    ],
    'sequenceLength': [
        './up:sequence',
        attrib('length'),
        post(int_cast),
    ],
    'sequence': [
        './up:sequence',
        text(),
    ],
    'pdbIds': [
        './up:dbReference[@type="PDB"]',
        allattrib('id'),
    ],
    'hasAlphaFoldStructure': [
        './up:dbReference[@type="AlphaFoldDB"]',
        exists(first),
    ],
    'enzymeClassId': [  # enzyme classes can be '1.-.-.-' @ Q5ATG9
        f'./up:protein[1]/{_all_names}/up:ecNumber/text()',
        xpath(),
    ],
    'cathClassId': [  # can have multiple ids?
        './up:dbReference[@type="Gene3D"]',
        allattrib('id'),
    ],
    'structureHelix': [
        './up:feature[@type="helix"]/up:location',
        allraw(),
        post(post_struc, 'sequenceLength'),
    ],
    'structureTurn': [
        './up:feature[@type="turn"]/up:location',
        allraw(),
        post(post_struc, 'sequenceLength'),
    ],
    'structureStrand': [
        './up:feature[@type="strand"]/up:location',
        allraw(),
        post(post_struc, 'sequenceLength'),
    ],
    'keywords': [
        './up:keyword',
        alltext(),
    ],
    'diseaseId': [  # TODO not all diseases have ids! P14568
        './up:comment[@type="disease"]/up:disease',
        allattrib('id'),
    ],
    'diseases': [  # id <-> name mapping
        './up:comment[@type="disease"]',
        allraw(),
    ],
    'hasPTM': [
        './up:comment[@type="PTM"]',
        exists(first),
    ],
    'cofactors': [  # name or id?
        './up:comment[@type="cofactor"]/up:cofactor',
        allraw(),
    ],
    # 'substrate': [  # txt or db?
    #     './up:comment[@type="catalytic activity"]/up:reaction/up:text',
    #     alltext(),
    # ],
    'substrates': [
        './up:comment[@type="catalytic activity"]/up:reaction',
        allraw(),
        post(post_substrate),
    ],
    'isDnaBinding': [
        './up:dbReference[@type="GO"]/up:property[@type="term" and contains(@value, "DNA binding")]',
        exists(xpath),
    ],
}

"""
Struct removed entries:

    # 'accessions': [
    #     './up:accession',
    #     alltext(),
    # ],
    
"""

max_key_len = max(len(k) for k in struct)
