import idna
from unidecode import unidecode

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"


def ascii_ify_puny(puny_host) -> str:
    """ """
    unicode_host = idna.decode(puny_host)
    return ascii_ify_unicode(unicode_host)


def ascii_ify_unicode(unicode_host) -> str:
    """ """
    ascii_host = unidecode(unicode_host)
    return ascii_host


