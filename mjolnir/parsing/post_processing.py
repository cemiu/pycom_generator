import lxml.etree as ET

def post(f, *fields):
    return f, *fields


def int_cast(x):
    return int(x) if x else None


def post_struc(structures, sequence_length):
    """Extract fraction and ranges of secondary structures."""
    ranges = []
    tally = 0

    for structure in structures:
        begin, end = structure.getchildren()
        begin, end = int(begin.attrib['position']), int(end.attrib['position'])
        ranges.append((begin, end))
        tally += end - begin + 1

    percent = tally / sequence_length if sequence_length else 0
    # print(f'{percent:.2%}')
    return percent, ranges


__all__ = ['post', 'int_cast', 'post_struc']
