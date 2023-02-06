import logging
from collections import Counter
from typing import List, Optional
import re
import os
from dataclasses import dataclass
import idna
from unidecode import unidecode
from fqdn_parser.suffix_parser import build_suffixes
from fqdn_parser.trie import save_trie, load_trie, _TLDInfo, _SuffixInfo

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

# links to iana and icann sources for TLD / suffix information
TLD_LIST_URL = "https://www.iana.org/domains/root/db"
SUFFIX_LIST_URL = "https://publicsuffix.org/list/public_suffix_list.dat"

# manually parse all IANA TLD pages and pulled registration dates. This takes quite a while to do
# so shipping this resource file with the source
tld_reg_date_resource = "tld_reg_dates_v1.txt"

ipv4_pattern = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
ipv6_pattern = re.compile(r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))')
# via MS Defender Blog Post
private_ipv4_pattern = re.compile(r'(^127\.)|(^10\.)|(^172\.1[6-9]\.|^172\.2[0-9]\.|^172\.3[0-1]\.)|(^192\.168\.)')


@dataclass
class ParsedResult:
    """
    tld: the actual top level domain
    effective_tld: the full public (or private) suffix, which may consist of multiple labels
    registrable_domain: domain name plus the effective TLD. Essentially the thing a person purchases from a Registrar
    registrable_domain_host: the domain name without the effective TLD
    fqdn: fully qualified domain name
    pqdn: partially qualified domain name: all the stuff to the left of the registrable domain
    """
    tld: str
    tld_puny: str
    tld_type: str
    tld_registry: str
    tld_create_date: object
    effective_tld: str
    effective_tld_is_public: bool
    host_labels: List[str]
    ipv4: bool = False
    ipv6: bool = False

    @property
    def registrable_domain(self) -> Optional[str]:
        if self.is_fqdn:
            return f"{self.host_labels[-1]}.{self.effective_tld}"
        return None

    @property
    def registrable_domain_host(self) -> Optional[str]:
        if self.is_fqdn:
            return self.host_labels[-1]
        return None

    @property
    def fqdn(self) -> str:
        if self.is_fqdn:
            return f"{'.'.join(self.host_labels)}.{self.effective_tld}"
        # just return the IP address
        return self.host_labels[0]

    @property
    def pqdn(self) -> Optional[str]:
        if self.is_fqdn:
            return '.'.join(self.host_labels[:-1])
        return None

    @property
    def pqdn_labels(self) -> Optional[List[str]]:
        if self.is_fqdn:
            return self.host_labels[:-1]
        return None

    @property
    def is_fqdn(self) -> bool:
        return not self.is_ip and len(self.host_labels) > 0

    @property
    def is_ip(self) -> bool:
        return self.ipv4 or self.ipv6

    @property
    def is_tld_multi_part(self) -> bool:
        return self.tld != self.effective_tld

    @property
    def is_punycode(self) -> bool:
        return self.tld_puny is not None

    def ascii_ify_tld(self) -> str:
        if self.is_punycode:
            return self.ascii_ify_puny(self.tld_puny)
        return self.tld

    @staticmethod
    def ascii_ify_puny(self, puny_host) -> str:
        unicode_host = idna.decode(puny_host)
        return ParsedResult.ascii_ify_unicode(unicode_host)

    @staticmethod
    def ascii_ify_unicode(unicode_host) -> str:
        ascii_host = unidecode(unicode_host)
        return ascii_host

    def is_ipv4_private(self) -> Optional[bool]:
        if self.ipv4:
            return private_ipv4_pattern.match(self.fqdn) is not None
        return None


class Suffixes:
    def __init__(self, read_cache=True, save_cache=True, cache_path="suffix_data.cache"):
        if read_cache and cache_path and os.path.exists(cache_path):
            _logger.info("loading suffix data from cache")
            suffix_trie, puny_suffixes = load_trie(cache_path)
            self._suffix_trie = suffix_trie
            self._puny_suffixes = puny_suffixes
        else:
            _logger.info("manually collecting and parsing domain suffix data")
            suffix_trie, puny_suffixes = build_suffixes()
            self._suffix_trie = suffix_trie
            self._puny_suffixes = puny_suffixes
            if save_cache and cache_path:
                _logger.info("saving domain suffix data to cache")
                save_trie(cache_path, self._suffix_trie, self._puny_suffixes)

    def tld_types(self, counts=False):
        """ Return either the distinct set of TLD types or the count of distinct TLD types"""
        tld_types = [node.metadata.tld_type for node in self._suffix_trie.root.children.values()]
        if counts:
            return Counter(tld_types)
        return list(set(tld_types))

    def get_all_tlds(self):
        """ Just return the effective TLD for the FQDN """
        tlds = [node for node in self._suffix_trie.root.children]
        return tlds

    def get_tld(self, fqdn):
        """ Just return the effective TLD for the FQDN """
        node, _ = self._suffix_trie.get_longest_sequence(fqdn, self._puny_suffixes)
        if node:
            return node.suffix
        return None

    def parse(self, fqdn, skip_ip_check=False, skip_protocol_check=False):
        """ Parse a fqdn or url and return a ParsedResult object

        Args:
            fqdn (string): the fqdn or url to be parsed
            skip_ip_check (bool): True to skip checking if fqdn contains an IP address
            skip_protocol_check (bool): True to skip check for `protocol://` at the beginning of the fqdn. If False
            and the fqdn includes a protocol, the protocol string will be interpreted as a subdomain.

        Returns: ParseResult

        Notes: When parsing a list of FQDNs and you know the list does not include any
        IP addresses or protocol strings, set skip_ip_check=True and skip_protocol_check=True for improved
        processing speed
        """
        fqdn = fqdn.lower()
        if not skip_ip_check:
            if ipv4_pattern.match(fqdn):
                return self._ip_result(fqdn, True)
            if ipv6_pattern.match(fqdn):
                return self._ip_result(fqdn, False)

        # check for protocol prefix
        if skip_protocol_check is False and "://" in fqdn:
            print("doing check")
            index = fqdn.index("://")
            fqdn = fqdn[index + 3:]

        node, host_labels = self._suffix_trie.get_longest_sequence(fqdn, self._puny_suffixes)
        if not node:
            return None
        if isinstance(node, _TLDInfo):
            return ParsedResult(
                node.suffix,
                node.puny,
                node.tld_type,
                node.registry,
                node.create_date,
                node.suffix,
                True,
                host_labels)
        elif isinstance(node, _SuffixInfo):
            return ParsedResult(
                node.root_suffix.suffix,
                node.root_suffix.puny,
                node.root_suffix.tld_type,
                node.root_suffix.registry,
                node.root_suffix.create_date,
                node.suffix,
                node.is_public,
                host_labels)
        else:
            raise Exception("Invalid Suffix Note Type")

    @staticmethod
    def _ip_result(ip, is_ipv4):
        return ParsedResult(None, None, None, None, None, None, None, [ip], is_ipv4, not is_ipv4)


def run_test():
    from tld_ranks import TLDRanker
    from tranco import Tranco
    suffixes = Suffixes(read_cache=False)
    types = suffixes.tld_types()

    # tranco = Tranco(cache=True, cache_dir='.tranco')
    # tld_ranker = TLDRanker(suffixes, tranco)

    fqdn = "login.mail.stuffandthings.co.uk"
    # fqdn = "Amazon"
    result = suffixes.parse(fqdn)
    print(result.registrable_domain_host)
    # print(tld_ranker.tld(result.tld))
    # print(tld_ranker.effective_tld(result.effective_tld))


def main():
    run_test()


if __name__ == "__main__":
    main()
