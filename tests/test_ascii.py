import pytest
from utils import ascii_ify

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"


def test_puny_ascii_ification():
    """ test the ascii'ification of puny code """
    # ascii-ify puny code: puny_domain = "xn--crdit-agricole-ckb.xn--scurvrification-bnbe.com"
    puny = "xn--crdit-agricole-ckb.xn--scurvrification-bnbe.com"
    ret = ascii_ify.ascii_ify_puny(puny)
    assert ret == "credit-agricole.securverification.com"


def test_unicode_ascii_ification():
    """ test the ascii'ification of puny code """
    # ascii-ify puny code: puny_domain = "xn--crdit-agricole-ckb.xn--scurvrification-bnbe.com"
    unicode_str = "crédit-agricole.sécurvérification.com"
    ret = ascii_ify.ascii_ify_puny(unicode_str)
    assert ret == "credit-agricole.securverification.com"
