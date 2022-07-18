import lxml.etree as etree

from mjolnir.util import Reader, InfoUtil

tag_up = '{http://uniprot.org/uniprot}'
tag_entry = f'{tag_up}entry'


class Parser:
    """A parser for XML files"""

    def __init__(self, file, info=False):
        self.file = file
        self.reader = Reader(file)
        self.progress = self.reader.progress
        self.info = InfoUtil(file_progress=self.progress) if info else None

    def __iter__(self):
        for elem in _iterparse(self.reader):
            yield elem
            if self.info:
                next(self.info)
        if self.info:
            del self.info


class ModelParser(Parser):
    """A parser for XML files, taking in XPath parsing models."""

    def __init__(self, file, info=False, model=None):
        if model is None:
            raise ValueError('ModelParser requires a model')
        super().__init__(file, info)
        self.model = model

    def __iter__(self):
        """Return an iterative parser for XML files."""
        """Return an iterative parser for UniProt XML files."""
        for elem in super().__iter__():
            results = {}  # result dict

            for key, inst in self.model.items():
                xpath, extractor, *post_process = inst

                # extract data
                datum = extractor(elem, xpath)

                # apply post-processing, if specified
                for proc in post_process:
                    post_func, *fields = proc
                    req_results = [results[field] for field in fields]  # required results
                    datum = post_func(datum, *req_results)

                results[key] = datum

            yield results


def _iterparse(xml, tag=tag_entry):
    """Process XML iteratively."""
    context = iter(etree.iterparse(xml, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag == tag:
            yield elem
            root.clear()  # clear root to keep memory usage low
