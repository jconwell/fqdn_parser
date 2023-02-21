import pytest

from entropy.char_probabilities import load_char_probabilities, update_char_probabilities
from entropy.domain_entropy import domain_entropy, fqdn_entropy
from fqdn_parser.suffixes import Suffixes

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"


_char_probs = None


@pytest.fixture()
def char_probs(): return load_char_probabilities()


@pytest.fixture()
def suffixes(): return Suffixes(read_cache=True)


def test_domain_entropy(char_probs, suffixes):
    """ test registrable domain host entropy """
    result = suffixes.parse("amazon.com")
    entropy = domain_entropy(result, char_probs)
    assert entropy == pytest.approx(2.380875)


def test_domain_entropy_on_fqdn(char_probs, suffixes):
    """ should ignore subdomains """
    result = suffixes.parse("stuff.and.things.amazon.com")
    entropy = domain_entropy(result, char_probs)
    assert entropy == pytest.approx(2.380875)


def test_keyboard_smash_domain_name(char_probs, suffixes):
    """ should have higher entropy """
    result = suffixes.parse("lk3k3l24jlk23.com")
    entropy = domain_entropy(result, char_probs)
    assert entropy == pytest.approx(4.533291)


def test_domain_entropy_different_base(char_probs, suffixes):
    # test different log base
    result = suffixes.parse("amazon.com")
    entropy = domain_entropy(result, char_probs, 10)
    assert entropy == pytest.approx(0.7167148)


def test_fqdn_entropy(char_probs, suffixes):
    result = suffixes.parse("stuff.things.amazon.com.com")
    entropy = fqdn_entropy(result, char_probs)
    assert entropy == pytest.approx(1.104753)


def test_fqdn_entropy_on_domain_name(char_probs, suffixes):
    """ this should be different from the domain name entropy of the same chars becase
    the char probabilities used are fqdn probabilities, not domain name probabilities"""
    result = suffixes.parse("amazon.com")
    entropy = fqdn_entropy(result, char_probs)
    assert entropy == pytest.approx(2.476048)


def test_fqdn_entropy_different_base(char_probs, suffixes):
    # test different log base
    result = suffixes.parse("stuff.things.amazon.com.com")
    entropy = fqdn_entropy(result, char_probs, 10)
    assert entropy == pytest.approx(0.332564)
