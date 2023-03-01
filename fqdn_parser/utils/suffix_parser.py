import re
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from fqdn_parser.utils.trie import Trie

_logger = logging.getLogger(__name__)

# links to iana and icann sources for TLD / suffix information
TLD_LIST_URL = "https://www.iana.org/domains/root/db"
SUFFIX_LIST_URL = "https://publicsuffix.org/list/public_suffix_list.dat"

# manually parse all IANA TLD pages and pulled registration dates. This takes quite a while to do
# so shipping this resource file with the source
tld_reg_date_resource = "tld_reg_dates_v1.txt"

PUNY_PREFIX = "xn--"


def build_suffixes():
    tld_create_dates = _load_tld_create_dates()
    _suffix_trie = _load_all_tlds(tld_create_dates)
    _load_manual_tlds(_suffix_trie)
    _enrich_tld_suffixes(_suffix_trie)
    # create a punycode suffix reverse index
    _puny_suffixes = {}
    root_tlds = _suffix_trie.root.children
    for tld_node in root_tlds.values():
        if tld_node.puny:
            _puny_suffixes[tld_node.puny] = tld_node.label
    return _suffix_trie, _puny_suffixes


def _load_tld_create_dates():
    """ This resource file was created by parsing the individual IANA TLD pages. This takes way to long
    to do every time the TLD data cache is being rebuilt (and I don't want to piss IANA off), so
    I'm running this periodically and will update the source as new TLDs are created.
    """
    import importlib.resources
    import fqdn_parser as fp
    with importlib.resources.path(fp, tld_reg_date_resource) as resource:
        with open(resource, 'r') as handle:
            lines = handle.readlines()
    tld_create_dates = {}
    for line in lines:
        parts = line.strip().split(",")
        tld_create_dates[parts[0]] = datetime.strptime(parts[1], '%Y-%m-%d').date()
    return tld_create_dates


def _load_all_tlds(tld_create_dates):
    """ Load all known TLDs from iana. The html page has the TLD
    type and the registry information so I have to parse the html to get the info.
    Yup, totally know this is brittle.
    """
    trie = Trie()
    revoked_tld = "Not assigned"
    # regex for the IANA URL for idn TLDs
    PUNY_TLD_PATTERN = "^\/domains\/root\/db\/xn--(.+?)\.html"
    response = requests.get(TLD_LIST_URL)
    if response.status_code != 200:
        raise Exception(f"{TLD_LIST_URL} error {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", class_="iana-table", id="tld-table")
    table = table.find("tbody")
    tld_rows = table.find_all("tr")
    for tld_row in tld_rows:
        data = tld_row.find_all("td")
        if len(data) != 3:
            raise Exception("IANA tld html format changed")
        # parse out tld and delegation record link
        link = data[0].find("a")
        # this is brittle, but parsing out the right to left and L2R unicode chars
        tld = link.text.replace(".", "").replace('‏', '').replace('‎', '')
        # parse the TLD type
        tld_type = data[1].text
        # parse the TLD registry
        registry = data[2].text
        # only collect active TLDs
        if registry != revoked_tld:
            # check for punycode TLD (starts with xn--)
            delegation_link = link["href"]
            puny_tld = re.search(PUNY_TLD_PATTERN, delegation_link)
            if puny_tld:
                puny_tld = PUNY_PREFIX + puny_tld.group(1)
            # get the TLD registration date
            tld_reg_date = tld_create_dates.get(tld)
            if tld_reg_date is None:
                _logger.warning(f"Registration date not found for TLD '{tld}' ")
            # populate tld info
            trie.insert_tld_node(tld, puny_tld, tld_type, registry, tld_reg_date)
    return trie


def _load_manual_tlds(_suffix_trie: Trie):
    """ Add in any extra TLDs manually """
    # add in the onion TLD manually
    tld = "onion"
    _suffix_trie.insert_tld_node(tld, None, "host_suffix", "Tor", datetime.strptime("2015-09-15", '%Y-%m-%d').date())


def _enrich_tld_suffixes(_suffix_trie: Trie):
    """ Pull in all known public suffixes
    TODO: A lot of these are not considered multi label TLDs, like "co.uk", but instead are suffixes used
          by dynamic DNS providers. I need to figure out a way to differentiate the two and add dynamic dns
          as property on a suffix.
    """
    response = requests.get(SUFFIX_LIST_URL)
    if response.status_code != 200:
        raise Exception(f"{SUFFIX_LIST_URL} error {response.status_code}")
    suffix_list = response.content.decode('utf-8')
    suffix_list = suffix_list.split("\n")

    # add each sub suffix to its parent TLD
    is_private_suffix = False
    for i, line in enumerate(suffix_list):
        if line == "// ===BEGIN PRIVATE DOMAINS===":
            # set flag and continue
            is_private_suffix = True
            continue
        elif len(line) == 0 or line[:3] == "// ":
            # skip comments
            continue
        suffix = line.strip()
        # strip out wildcards
        if suffix[:2] == "*." or suffix[:2] == "!.":
            suffix = suffix[2:]
        if "." in suffix:
            # todo: check for puny tld
            # tld = suffix[suffix.rindex(".") + 1:]
            # add suffix to trie tree
            _suffix_trie.insert_suffix_node(suffix, is_private_suffix)
        else:
            # There are 9 IDN TLDs in the suffix list that are NOT listed in the iana root zone database
            # - so adding them here (they are all country code IDN TLDs)
            if _suffix_trie.get_node([suffix]) is None:
                print(f"WARNING: Suffix '{suffix}' found in Public Suffix List is not in IANA root zone database. Manually adding suffix to list of root TLDs")
                # parse out the puny code from the previous line if possible
                previous_line = suffix_list[i - 1]
                puny = None
                if "// xn--" in previous_line:
                    puny = previous_line[3:]
                    puny = puny[:puny.index(" ")]
                _suffix_trie.insert_tld_node(suffix, puny, "country-code", None, None)
