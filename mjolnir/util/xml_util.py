import xml.etree.ElementTree as ET
import gzip
import logging

# default uniprot xml tag
tag_up = '{http://uniprot.org/uniprot}'
tag_entry = f'{tag_up}entry'


def parse(file, mode=None, tag=tag_entry):
    """Return an iterative parser for XML files.

    Files can be either raw XML files or gzipped XML files. (xml.gz)
    Tarballs cannot be parsed.

    Usage:
        for entry in parse_xml(file):
            # do something with ET entry
    """
    logging.info(f'Parsing {file}')

    if mode is None:
        mode = 'gz' if file.endswith('.gz') else 'xml'
        logging.info(f'Parsing mode: {mode}')

    f = gzip.open if mode == 'gz' else (open if mode == 'xml' else None)

    if f is None:
        raise ValueError(f'Unknown mode {mode}, must be "xml" or "gz"')

    with f(file) as fh:
        for elem in iterparse(fh, tag=tag):
            yield elem


def iterparse(xml, tag=tag_entry):
    """Process XML files iteratively, directly from disk / a stream."""
    context = iter(ET.iterparse(xml, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag == tag:
            yield elem
            # clear root to keep memory usage low
            root.clear()
