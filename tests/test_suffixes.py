import pytest
from fqdn_parser.suffixes import Suffixes
from datetime import datetime, date

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"


def test_tld_types():
    """ return all known TLD categories, with and without counts """
    tld_types = ['country-code', 'generic', 'sponsored', 'generic-restricted', 'host_suffix', 'infrastructure']
    suffixes = Suffixes(read_cache=True)
    ret = suffixes.tld_types()
    assert sorted(ret) == sorted(tld_types)

    ret = suffixes.tld_types(counts=True)
    assert len(ret) == len(tld_types)
    for tld_type in tld_types:
        assert tld_type in ret


def test_get_all_tlds():
    """ return the set of all IANA registered TLDs (as of Feb, 2023) """
    suffixes = Suffixes(read_cache=True)
    tlds = suffixes.get_all_tlds()
    assert len(tlds) >= 1491


def test_tld_registries():
    """ return list of all registries, with and without counts """
    suffixes = Suffixes(read_cache=True)
    ret = suffixes.tld_registries()
    assert 'VeriSign Global Registry Services' in ret

    ret = suffixes.tld_registries(counts=True)
    assert ret['VeriSign Global Registry Services'] == 2  # .com and .net


def test_get_tlds_by_registry():
    """ return list of TLDs owned by a registry """
    suffixes = Suffixes(read_cache=True)
    registries = suffixes.tld_registries()
    assert len(registries) > 0
    for registry in registries:
        tlds = suffixes.get_tlds_by_registry(registry)
        assert len(tlds) > 0


def test_get_tld_dataframe():
    """ test Pandas dataframe of all TLDs """
    suffixes = Suffixes(read_cache=True)
    df = suffixes.get_tld_dataframe()
    assert df.shape == (1491, 5)


def test_get_tld():
    """ test parsing the IANA registered TLD from the FQDN """
    suffixes = Suffixes(read_cache=True)
    # test standard 1 label tld
    assert suffixes.get_tld("stuff.com") == "com"
    # test multi label tld
    assert suffixes.get_tld("stuff.co.uk") == "uk"
    # test private suffix
    assert suffixes.get_tld("stuff.duckdns.org") == "org"
    # test unicode tld
    assert suffixes.get_tld("stuff.手机") == "手机"
    # test puny code tld
    assert suffixes.get_tld("stuff.xn--kput3i") == "手机"
    # test tld that isn't real
    assert suffixes.get_tld("stuff.nottld") is None


def test_get_effective_tld():
    """ test parsing out the effective tld from the FQDN """
    suffixes = Suffixes(read_cache=True)
    # test standard 1 label tld
    assert suffixes.get_effective_tld("stuff.com") == "com"
    # test multi label tld
    assert suffixes.get_effective_tld("stuff.co.uk") == "co.uk"
    # test private suffix
    assert suffixes.get_effective_tld("stuff.duckdns.org") == "org"
    # test unicode tld
    assert suffixes.get_effective_tld("stuff.手机") == "手机"
    # test puny code tld
    assert suffixes.get_effective_tld("stuff.xn--kput3i") == "手机"
    # test tld that isn't real
    assert suffixes.get_effective_tld("stuff.nottld") is None


def test_parse_punycodeTLD():
    # test with unicode TLD
    fqdn = "www.stuff.手机"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "手机"
    assert result.tld_puny == "xn--kput3i"
    assert result.tld_type == "generic"
    assert result.tld_registry == "Beijing RITT-Net Technology Development Co., Ltd"
    assert result.tld_create_date == datetime.strptime('2014-06-05', '%Y-%m-%d').date()
    assert result.effective_tld == "手机"
    assert result.private_suffix is None
    assert result.registrable_domain == "stuff.手机"
    assert result.registrable_domain_host == "stuff"
    assert result.fqdn == "www.stuff.手机"
    assert result.pqdn == "www"
    assert_ip(result)
    # test with punycode TLD
    fqdn = "www.stuff.xn--kput3i"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "手机"
    assert result.tld_puny == "xn--kput3i"
    assert result.tld_type == "generic"
    assert result.tld_registry == "Beijing RITT-Net Technology Development Co., Ltd"
    assert result.tld_create_date == datetime.strptime('2014-06-05', '%Y-%m-%d').date()
    assert result.effective_tld == "手机"
    assert result.private_suffix is None
    assert result.registrable_domain == "stuff.手机"
    assert result.registrable_domain_host == "stuff"
    assert result.fqdn == "www.stuff.手机"
    assert result.pqdn == "www"
    assert_ip(result)


def test_parse_ccTLD():
    fqdn = "www.star-domain.jp"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "jp"
    assert result.tld_puny is None
    assert result.tld_type == "country-code"
    assert result.tld_registry == "Japan Registry Services Co., Ltd."
    assert result.tld_create_date == datetime.strptime('1986-08-05', '%Y-%m-%d').date()
    assert result.effective_tld == "jp"
    assert result.private_suffix is None
    assert result.registrable_domain == "star-domain.jp"
    assert result.registrable_domain_host == "star-domain"
    assert result.fqdn == "www.star-domain.jp"
    assert result.pqdn == "www"
    assert_ip(result)


def test_parse_gTLD():
    fqdn = "www.stuffandthings.mba"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "mba"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "Binky Moon, LLC"
    assert result.tld_create_date == date(2015, 5, 14)
    assert result.effective_tld == "mba"
    assert result.private_suffix is None
    assert result.registrable_domain == "stuffandthings.mba"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == "www.stuffandthings.mba"
    assert result.pqdn == "www"
    assert_ip(result)


def test_parse_removed_gTLD():
    # test gTLD that was once delegated, but since removed
    fqdn = "stuffandthings.mcd"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result is None


def test_parse_ogTLD():
    fqdn = "www.stuffandthings.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "com"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "VeriSign Global Registry Services"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "com"
    assert result.private_suffix is None
    assert result.registrable_domain == "stuffandthings.com"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == "www.stuffandthings.com"
    assert result.pqdn == "www"
    assert_ip(result)


def test_parse_multi_label_tld():
    fqdn = "www.stuffandthings.co.uk"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "uk"
    assert result.tld_puny is None
    assert result.tld_type == "country-code"
    assert result.tld_registry == "Nominet UK"
    assert result.tld_create_date == datetime.strptime('1985-07-24', '%Y-%m-%d').date()
    assert result.effective_tld == "co.uk"
    assert result.private_suffix is None
    assert result.registrable_domain == "stuffandthings.co.uk"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == "www.stuffandthings.co.uk"
    assert result.pqdn == "www"
    assert_ip(result)


def test_parse_private_suffix():
    fqdn = "fake-apple-login.duckdns.org"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "org"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "Public Interest Registry (PIR)"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "org"
    assert result.private_suffix == "duckdns.org"
    assert result.registrable_domain == "duckdns.org"
    assert result.registrable_domain_host == "duckdns"
    assert result.fqdn == "fake-apple-login.duckdns.org"
    assert result.pqdn == "fake-apple-login"
    assert_ip(result)


def test_parse_private_suffix_multi_pqdn():
    fqdn = "api.fake-apple-login.duckdns.org"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "org"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "Public Interest Registry (PIR)"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "org"
    assert result.private_suffix == "duckdns.org"
    assert result.registrable_domain == "duckdns.org"
    assert result.registrable_domain_host == "duckdns"
    assert result.fqdn == "api.fake-apple-login.duckdns.org"
    assert result.pqdn == "api.fake-apple-login"
    assert_ip(result)


def test_parse_gt2_label_private_suffix():
    """ test for private multi label suffixes: s3.dualstack.ap-southeast-1.amazonaws.com """
    fqdn = "stuff.things.something.s3.dualstack.ap-southeast-1.amazonaws.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "com"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "VeriSign Global Registry Services"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "com"
    assert result.private_suffix == "s3.dualstack.ap-southeast-1.amazonaws.com"
    assert result.registrable_domain == "amazonaws.com"
    assert result.registrable_domain_host == "amazonaws"
    assert result.fqdn == "stuff.things.something.s3.dualstack.ap-southeast-1.amazonaws.com"
    assert result.pqdn == "stuff.things.something.s3.dualstack.ap-southeast-1"
    assert_ip(result)


def test_parse_private_suffix_with_multilabel_tld():
    """ Bytemark Hosting in the UK """
    fqdn = "fake-apple-login.vm.bytemark.co.uk"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "uk"
    assert result.tld_puny is None
    assert result.tld_type == "country-code"
    assert result.tld_registry == "Nominet UK"
    assert result.tld_create_date == datetime.strptime('1985-07-24', '%Y-%m-%d').date()
    assert result.effective_tld == "co.uk"
    assert result.private_suffix == "vm.bytemark.co.uk"
    assert result.registrable_domain == "bytemark.co.uk"
    assert result.registrable_domain_host == "bytemark"
    assert result.fqdn == "fake-apple-login.vm.bytemark.co.uk"
    assert result.pqdn == "fake-apple-login.vm"
    assert_ip(result)


def test_parse_sub_domain():
    fqdn = "login.mail.stuffandthings.co.uk"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "uk"
    assert result.tld_puny is None
    assert result.tld_type == "country-code"
    assert result.tld_registry == "Nominet UK"
    assert result.tld_create_date == datetime.strptime('1985-07-24', '%Y-%m-%d').date()
    assert result.effective_tld == "co.uk"
    assert result.private_suffix is None
    assert result.registrable_domain == "stuffandthings.co.uk"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == fqdn
    assert result.pqdn == "login.mail"


def test_parse_www_prefix():
    fqdn = "www.stuffandthings.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "com"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "VeriSign Global Registry Services"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "com"
    assert result.private_suffix is None
    assert result.registrable_domain == "stuffandthings.com"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == fqdn
    assert result.pqdn == "www"
    assert_ip(result)


def test_parse_invalid_fqdns():
    suffixes = Suffixes(read_cache=True)
    # not a real TLD
    fqdn = "login.mail.stuffandthings.co.zz"
    result = suffixes.parse(fqdn)
    assert result is None
    # no tld (no periods)
    fqdn = "loginmailstuffandthingscouk"
    result = suffixes.parse(fqdn)
    assert result is None


def test_parse_skip_ip_check():
    suffixes = Suffixes(read_cache=True)
    # test public IP address
    fqdn = "65.22.218.1"
    # test default behavior
    result = suffixes.parse(fqdn, skip_ip_check=False)
    assert result is not None
    # test skipping IP check
    result = suffixes.parse(fqdn, skip_ip_check=True)
    assert result is None


def test_parse_fqdn_as_ipv4():
    suffixes = Suffixes(read_cache=True)
    # test public IP address
    fqdn = "65.22.218.1"
    result = suffixes.parse(fqdn)
    assert result.fqdn == fqdn
    assert_ip(result, True)
    assert result.is_ipv4_private() is False
    # test private IP address
    fqdn = "10.55.55.55"
    result = suffixes.parse(fqdn)
    assert result.fqdn == fqdn
    assert_ip(result, True)
    assert result.is_ipv4_private() is True


def test_parse_fqdn_as_ipv6():
    suffixes = Suffixes(read_cache=True)
    fqdn = "2a01:8840:d5:0:0:0:0:1"
    result = suffixes.parse(fqdn)
    assert result.fqdn == fqdn
    assert_ip(result, False)


def test_parse_remove_protocol():
    fqdn = "https://www.stuffandthings.com"
    # test skipping protocol check
    result = Suffixes(read_cache=True).parse(fqdn, skip_protocol_check=True)
    assert result.registrable_domain == "stuffandthings.com"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == "https://www.stuffandthings.com"
    assert result.pqdn == "https://www"
    assert_ip(result)
    # test with protocol parsing
    result = Suffixes(read_cache=True).parse(fqdn, skip_protocol_check=False)
    assert result.registrable_domain == "stuffandthings.com"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == "www.stuffandthings.com"
    assert result.pqdn == "www"
    assert_ip(result)
    # test check for protocol, but not passed in
    fqdn = "www.stuffandthings.com"
    result = Suffixes(read_cache=True).parse(fqdn, skip_protocol_check=False)
    assert result.registrable_domain == "stuffandthings.com"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == "www.stuffandthings.com"
    assert result.pqdn == "www"
    assert_ip(result)


def test_urls():
    """ test parsing out URL arguments """
    suffixes = Suffixes(read_cache=True)
    url = "https://www.google.com/search?q=urls+with+arguments&client=firefox-b-1-d&ei=IsnqY5TBB9270PEP_8efQA&"
    result = suffixes.parse(url)
    assert result.tld == "com"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "VeriSign Global Registry Services"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "com"
    assert result.private_suffix is None
    assert result.registrable_domain == "google.com"
    assert result.registrable_domain_host == "google"
    assert result.fqdn == "www.google.com"
    assert result.pqdn == "www"
    assert_ip(result)


def test_parsed_result_pqdn_labels():
    """ test getting list of pqdn labels """
    fqdn = "test.api.integration.stuff.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.pqdn_labels == ["test", "api", "integration"]
    # no subdomains
    fqdn = "stuff.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.pqdn_labels == []


def test_parsed_result_is_fqdn():
    """ test getting list of pqdn labels """
    fqdn = "stuff.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_fqdn
    # not FQDN
    fqdn = "10.55.55.55"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_fqdn is False


def test_parsed_result_is_ip():
    """ test getting list of pqdn labels """
    fqdn = "stuff.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_ip is False
    # is ip
    fqdn = "10.55.55.55"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_ip


def test_parsed_result_is_tld_multi_part():
    """ test checking for multi label effective tld"""
    fqdn = "stuff.co.uk"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_tld_multi_part
    # not multi part tld
    fqdn = "duckdns.org"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_tld_multi_part is False


def test_parsed_result_is_tld_punycode():
    """ test checking for punycode tld """
    fqdn = "stuff.xn--kput3i"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_tld_punycode
    # not multi part tld
    fqdn = "duckdns.org"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.is_tld_punycode is False




"""
Unit Test Helper Functions
"""


def assert_ip(result, assert_ipv4=None):
    """ None implies fqdn is not an IP address,
    True means check ipv4,
    and False means check ipv6
    """
    if assert_ipv4 is None:
        # not IP address
        assert result.ipv4 is False
        assert result.ipv6 is False
    elif assert_ipv4 is True:
        assert_ip_result_null_values(result)
        parts = result.fqdn.split(".")
        assert len(parts) == 4
        for part in parts:
            assert 0 <= int(part) <= 255
        assert result.ipv4 is True
        assert result.ipv6 is False
    elif assert_ipv4 is False:
        assert_ip_result_null_values(result)
        assert result.ipv4 is False
        assert result.ipv6 is True


def assert_ip_result_null_values(result):
    assert result.tld is None
    assert result.tld_puny is None
    assert result.tld_type is None
    assert result.tld_registry is None
    assert result.tld_create_date is None
    assert result.effective_tld is None
    assert result.private_suffix is None
    assert result.registrable_domain is None
    assert result.registrable_domain_host is None
    assert result.pqdn is None
