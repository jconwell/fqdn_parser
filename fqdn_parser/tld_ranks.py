from tranco import Tranco
from collections import Counter
import itertools

from fqdn_parser.suffixes import Suffixes


class TLDRanker:
    def __init__(self, suffixes, tranco=None):
        """ parse the TLD and effective TLD ranks from the Tranco top 1 million domains"""
        if tranco is None:
            tranco = Tranco()  # cache_dir="cache"

        # parse all the domains in Tranco
        results = [suffixes.parse(domain) for domain in tranco.list().list]
        # filter out any null results
        results = itertools.filterfalse(lambda x: x is None, results)

        def get_tld_info(result):
            return result.tld, result.effective_tld
        tlds, etds = zip(*[get_tld_info(result) for result in results])
        self.tld_ranks = {tld: i for i, tld in enumerate(Counter(tlds), start=1)}
        self.effective_tlds_ranks = {tld: i for i, tld in enumerate(Counter(etds), start=1)}

    def tld(self, tld):
        return self.tld_ranks.get(tld, -1)

    def effective_tld(self, effective_tld):
        return self.effective_tlds_ranks.get(effective_tld, -1)


def main():
    suffixes = Suffixes(read_cache=True)
    ranker = TLDRanker(suffixes)
    print(ranker)


if __name__ == "__main__":
    main()
