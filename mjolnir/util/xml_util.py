import lxml.etree as etree

from mjolnir.util import Reader, InfoUtil

tag_up = '{http://uniprot.org/uniprot}'
tag_entry = f'{tag_up}entry'


class Parser:
    """A parser for XML files"""

    def __init__(self, file, info=False, skip=float('nan'), abort_after=float('nan')):
        self.file = file

        self.skip = float('nan') if skip == 0 else skip
        self.abort_after = float('nan') if abort_after is None else abort_after

        self.reader = Reader(file)
        self.progress = self.reader.progress
        self.info = InfoUtil(file_progress=self.progress, log=info)

    def __iter__(self):
        for elem in _iterparse(self.reader, skip=self.skip, abort_after=self.abort_after):
            yield elem
            next(self.info)
        self.info.finish()


class ModelParser(Parser):
    """A parser for XML files, taking in XPath parsing models."""

    def __init__(self, file, info=False, model=None, skip=float('nan'), abort_after=float('nan')):
        if model is None:
            raise ValueError('ModelParser requires a model')

        skip = float('nan') if skip == 0 else skip
        abort_after = float('nan') if abort_after is None else abort_after

        super().__init__(file, info, skip, abort_after)
        self.model = model

    def __iter__(self):
        """Return an iterative parser for XML files."""
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


def _iterparse(xml, tag=tag_entry, skip=float('nan'), abort_after=float('nan')):
    """Process XML iteratively."""
    context = iter(etree.iterparse(xml, events=('start', 'end')))
    _, root = next(context)
    entry_count = 0

    for event, elem in context:
        if event == 'end' and elem.tag == tag:
            entry_count += 1
            if not skip > entry_count:
                yield elem

            root.clear()  # clear root to keep memory usage low

            if abort_after <= entry_count:
                break
