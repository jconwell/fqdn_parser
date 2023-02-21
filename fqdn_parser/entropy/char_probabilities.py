import logging
import os
import pickle
from io import BytesIO

import pandas as pd
import requests

from fqdn_parser.suffixes import ParsedResult

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

feed_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"


class CharProbabilities:
    def __init__(self, domain_char_probs, fqdn_char_probs):
        self.domain_char_probs = domain_char_probs
        self.fqdn_char_probs = fqdn_char_probs


def _download_top1mill_feed():
    """ Download Cisco umbrella top 1 million into memory

    Returns: byte array of zipped feed
    """
    response = requests.get(feed_url)
    feed_bytes = response.content
    return feed_bytes


def _read_top1mill_feed(feed_path):
    """ Read top 1 million into memory from file

    Returns: byte array of zipped feed
    """
    with open(feed_path, mode="rb") as zip_file:
        feed_bytes = zip_file.read()
    return feed_bytes


def _load_top1mill_dataframe(feed_bytes):
    """ Load DataFrame from byte array of zipped feed

    Args:
        feed_bytes (): byte array of top 1 million feed

    Returns: DataFrame of top 1 million feed
    """
    with BytesIO(feed_bytes) as feed_stream:
        feed_df = pd.read_csv(feed_stream, compression='zip', header=None, names=["rank", "fqdn"])
    return feed_df


def _parse_fqdn(suffixes, fqdn):
    try:
        result = suffixes.parse(fqdn)
        if result:
            return result
    except Exception as ex:
        _logger.warning(f"Could not parse fqdn: {fqdn}")
    return None


def _get_reg_domain(result: ParsedResult):
    if result and result.is_fqdn:
        return result.registrable_domain_host
    return None


def _clean_fqdn(result: ParsedResult):
    """ pull out TLD, dots, and any leading "www"
    Note: there are about 8k FQDNs that don't have an existing public suffix, so these get filtered out
    """
    if result and result.is_fqdn:
        # remove the effective tld from the fqdn
        fqdn = '.'.join(result.host_labels)
        # remove leading "www."
        if fqdn[0:4] == "www.":
            fqdn = fqdn[4:]
        # remove all dots
        fqdn = fqdn.replace(".", "")
        return fqdn
    return None


def _log_info(info, verbose):
    if verbose:
        _logger.info(info)


def _calc_probs(df, col, verbose):
    # drop duplicates and create new domain name series
    rows = df[col].drop_duplicates()
    # get char counts for domain column
    chars = rows.apply(lambda val: list(val))
    chars = chars.explode(ignore_index=True)
    total_chars = chars.shape[0]
    _log_info(f"Total Characters From Column  '{col}': {total_chars}", verbose)
    char_probs = {}
    for index, value in chars.value_counts().sort_index().items():
        char_probs[index[0]] = value / total_chars
    _log_info(f"Column '{col}' Character Probabilities", verbose)
    _log_info(char_probs, verbose)
    return char_probs


def _calc_char_probabilities(suffixes, df, top_n_fqdns, verbose=False):
    # take the top n fqdns
    if top_n_fqdns and top_n_fqdns > 0:
        df = df.head(top_n_fqdns)
    # lower case the fqdn just in case
    df["fqdn"] = df["fqdn"].str.lower()
    # filter out punycode fqdn's as this would throw off char probabilities
    df = df[~df.fqdn.str.contains("xn--")].copy()
    # parse fqdns
    df['result'] = df.apply(lambda row: _parse_fqdn(suffixes, row.fqdn), axis=1)
    # pull out the registrable domain host of the fqdn
    df['domain'] = df.apply(lambda row: _get_reg_domain(row.result), axis=1)
    # create cleaned fqdn col
    df["cleaned_fqdn"] = df.apply(lambda row: _clean_fqdn(row.result), axis=1)
    # parse out rows where fqdn couldn't be parsed
    df.dropna(inplace=True)

    domain_char_probs = _calc_probs(df, "domain", verbose)
    fqdn_char_probs = _calc_probs(df, "cleaned_fqdn", verbose)

    return domain_char_probs, fqdn_char_probs


def update_char_probabilities(suffixes, top_n_fqdns=None, cache_path="char_probs.cache"):
    _logger.info("loading Cisco Umbrella Top 1 Million feed")
    feed_bytes = _download_top1mill_feed()
    # feed_bytes = _read_top1mill_feed("../top-1m.csv.zip")
    feed_df = _load_top1mill_dataframe(feed_bytes)
    del feed_bytes
    _logger.info("calculating character probabilities")
    domain_char_probs, fqdn_char_probs = _calc_char_probabilities(suffixes, feed_df, top_n_fqdns, True)
    _logger.info("saving character probabilities to cache file")
    with open(cache_path, 'wb') as handle:
        pickle.dump((domain_char_probs, fqdn_char_probs), handle)
    return CharProbabilities(domain_char_probs, fqdn_char_probs)


def load_char_probabilities(cache_path="char_probs.cache"):
    if cache_path and os.path.exists(cache_path):
        _logger.info("loading char probabilities from cache")
        with open(cache_path, 'rb') as handle:
            domain_char_probs, fqdn_char_probs = pickle.load(handle)
        return CharProbabilities(domain_char_probs, fqdn_char_probs)
    else:
        raise FileNotFoundError("The file char_probs.cache was not found. Please run update_char_probabilities to build new probabilities cache file")


def main():
    from fqdn_parser.suffixes import Suffixes
    suffixes = Suffixes()
    update_char_probabilities(suffixes)
    char_probs = load_char_probabilities()
    print(char_probs)


if __name__ == "__main__":
    main()
