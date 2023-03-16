import math
from collections import Counter
from fqdn_parser.entropy.char_probabilities import CharProbabilities, _get_reg_domain, _clean_fqdn
from fqdn_parser.suffixes import ParsedResult

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"


def relative_entropy(data: str, probabilities: dict, base:int=2):
    """ Calculate the relative entropy (Kullback-Leibler divergence) between the character data
    and the expected probabilities

    Args:
        data (str): string to calculate relative entropy against
        probabilities (dict): dictionary of ascii char probabilities to use in the entropy calculation
        base (int): log base to use

    Returns: entropy score

    """
    entropy = 0.0
    length = len(data) * 1.0
    if length > 0:
        cnt = Counter(data)
        for char, count in cnt.items():
            observed = count / length
            expected = probabilities[char]
            entropy += observed * math.log((observed / expected), base)
    return entropy


def domain_entropy(parsed_result: ParsedResult, char_probs: CharProbabilities, base: int = 2):
    """ Calculate the relative entropy of the characters in the registrable domain host against
    the domain name character probabilities.

    Note: this uses the registrable domain host, not the full domain name. So if stuffandthings.com is parsed,
    only the characters "stuffandthings" are used in the entropy calculation. The TLD and any subdomains are not used
    in the entropy calculation.

    Args:
        parsed_result (ParsedResult): ParsedResult object used to get the registrable domain host
        char_probs (CharProbabilities): CharProbabilities object that holds domain char probabilities
        base (int): log base to use

    Returns: entropy score

    """
    domain_name = _get_reg_domain(parsed_result)
    if domain_name:
        return relative_entropy(domain_name, char_probs.domain_char_probs, base)
    return 0


def fqdn_entropy(parsed_result: ParsedResult, char_probs: CharProbabilities, base: int=2):
    """ Calculate the relative entropy of the characters in the FQDN against the FQDN character probabilities

    Note: the fqdn entropy calculation uses the registrable domain host and all subdomain labels concatenated
    together without periods, and without the TLD. So if stuff.and.things.store.com is parsed, only the
    characters "stuffandthingsstore" are used in the entropy calculation.

    Args:
        parsed_result (ParsedResult): ParsedResult object used to get the full fqdn
        char_probs (CharProbabilities): CharProbabilities object that holds fqdn char probabilities
        base (int): log base to use

    Returns: entropy score

    """
    fqdn = _clean_fqdn(parsed_result)
    if fqdn:
        return relative_entropy(fqdn, char_probs.fqdn_char_probs, base)
    return 0
