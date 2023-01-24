from tranco import Tranco
from collections import Counter
import itertools


class TLDRanker:
    def __init__(self, suffixes, tranco=None):
        """ parse the TLD and effective TLD ranks from the Tranco top 1 million domains"""
        if tranco is None:
            tranco = Tranco()

        # parse all the domains in Tranco
        results = [suffixes.parse(domain) for domain in tranco.list().list]
        # filter out any null results
        results = itertools.filterfalse(lambda x: x is None, results)

        def get_tld_info(result):
            if result.effective_tld_is_public:
                return result.tld, result.effective_tld
            else:
                return result.tld, result.tld
        tlds, etds = zip(*[get_tld_info(result) for result in results])
        self.tlds = {tld: i for i, tld in enumerate(Counter(tlds), start=1)}
        self.etlds = {tld: i for i, tld in enumerate(Counter(etds), start=1)}

    def tld(self, tld):
        return self.tlds.get(tld, -1)

    def effective_tld(self, effective_tld):
        return self.etlds.get(effective_tld, -1)
