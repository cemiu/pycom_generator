ns = {'up': 'http://uniprot.org/uniprot'}


def getattrib(x, at):
    """Get attribute from element.
    Returns attribute string or None"""
    return x.attrib[at] if x is not None else None


def find(e, x):
    """Find element by (simplified) xpath.
    Returns element or None"""
    return e.find(x, namespaces=ns)


def findtext(e, x):
    """Find text of element by (simplified) xpath.
    Returns text or None"""
    return e.findtext(x, namespaces=ns)


def findattrib(e, x, at):
    """Find attribute of element by (simplified) xpath.
    Returns attribute string or None"""
    return getattrib(find(e, x), at)


def findall(e, x):
    """Find all elements by (simplified) xpath.
    Returns list of elements, or empty list"""
    return e.findall(x, namespaces=ns)


def findalltext(e, x):
    """Find text of all elements by (simplified) xpath.
    Returns list of text, or empty list"""
    return [e.text for e in findall(e, x)]


def findallattrib(e, x, at):
    """Find attribute of all elements by (simplified) xpath.
    Returns list of attribute strings, or empty list"""
    return [e.attrib[at] for e in findall(e, x)]


def findxpath(e, x):
    """Find elements by xpath.
    Returns list of elements, or empty list"""
    return e.xpath(x, namespaces=ns)


def findxpathsingle(e, x):
    """Find single element by xpath.
    Returns element or None"""
    return (findxpath(e, x) or [None])[0]


def exists(f, *args):
    """Check if element exists. True or False."""
    return lambda e, x: f(*args)(e, x) not in [None, [], (0.0, [])]


def first():
    """Get the first element found, or None."""
    return find


def text():
    """Get text of element, or None."""
    return findtext


def attrib(at):
    """Get attribute of element, or None."""
    return lambda e, x: findattrib(e, x, at)


def allraw():
    """Get all elements found, or empty list."""
    return findall


def alltext():
    """Get text of all elements, or empty list."""
    return findalltext


def allattrib(at):
    """Get attribute of all elements, or empty list."""
    return lambda e, x: findallattrib(e, x, at)


def xpath():
    """Get elements by xpath, or empty list."""
    return findxpath


__all__ = ['exists', 'first', 'text', 'attrib', 'allraw', 'alltext', 'allattrib', 'xpath']
