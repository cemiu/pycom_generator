import lxml.etree as etree
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

    stream = gzip.open(file) if mode == 'gz' else (file if mode == 'xml' else None)

    if stream is None:
        raise ValueError(f'Unknown mode {mode}, must be "xml" or "gz"')

    for elem in iterparse(stream, tag=tag):
        yield elem


def iterparse(xml, tag=tag_entry):
    """Process XML iteratively."""
    context = iter(etree.iterparse(xml, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag == tag:
            yield elem
            root.clear()  # clear root to keep memory usage low
