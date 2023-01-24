import pytest
from fqdn_parser.suffixes import Suffixes
from datetime import datetime, date

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"

"""
Test Ideas:    
    parse of url arguments in case passed in
    puny code
    ascii-ify puny code: puny_domain = "xn--crdit-agricole-ckb.xn--scurvrification-bnbe.com"
    
    is_fqdn
    is_ip
    pqdn_label_length
    other new properties
"""


def test_get_tld():
    suffixes = Suffixes(read_cache=True)
    # test standard 1 label tld
    assert suffixes.get_tld("stuff.com") == "com"
    # test multi label tld
    assert suffixes.get_tld("stuff.co.uk") == "co.uk"
    # test unicode tld
    assert suffixes.get_tld("stuff.手机") == "手机"
    # test puny code tld
    assert suffixes.get_tld("stuff.xn--kput3i") == "手机"
    # test tld that isn't real
    assert suffixes.get_tld("stuff.nottld") is None


def test_parse_ccTLD():
    fqdn = "star-domain.jp"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "jp"
    assert result.tld_puny is None
    assert result.tld_type == "country-code"
    assert result.tld_registry == "Japan Registry Services Co., Ltd."
    assert result.tld_create_date == datetime.strptime('1986-08-05', '%Y-%m-%d').date()
    assert result.effective_tld == "jp"
    assert result.effective_tld_is_public is True
    assert result.registrable_domain == "star-domain.jp"
    assert result.registrable_domain_host == "star-domain"
    assert result.fqdn == "star-domain.jp"
    assert result.pqdn == ""
    assert_ip(result)


def test_parse_gTLD():
    fqdn = "stuffandthings.mba"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "mba"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "Binky Moon, LLC"
    assert result.tld_create_date == date(2015, 5, 14)
    assert result.effective_tld == "mba"
    assert result.effective_tld_is_public is True
    assert result.registrable_domain == "stuffandthings.mba"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == fqdn
    assert result.pqdn == ""
    assert_ip(result)


def test_parse_removed_gTLD():
    # test gTLD that was once delegated, but since removed
    fqdn = "stuffandthings.mcd"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result is None


def test_parse_ogTLD():
    fqdn = "stuffandthings.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "com"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "VeriSign Global Registry Services"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "com"
    assert result.effective_tld_is_public is True
    assert result.registrable_domain == "stuffandthings.com"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == fqdn
    assert result.pqdn == ""
    assert_ip(result)


def test_parse_multi_label_tld():
    fqdn = "stuffandthings.co.uk"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "uk"
    assert result.tld_puny is None
    assert result.tld_type == "country-code"
    assert result.tld_registry == "Nominet UK"
    assert result.tld_create_date == datetime.strptime('1985-07-24', '%Y-%m-%d').date()
    assert result.effective_tld == "co.uk"
    assert result.effective_tld_is_public is True
    assert result.registrable_domain == "stuffandthings.co.uk"
    assert result.registrable_domain_host == "stuffandthings"
    assert result.fqdn == fqdn
    assert result.pqdn == ""


def test_parse_private_multi_label_tld():
    fqdn = "fake-apple-login.duckdns.org"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "org"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "Public Interest Registry (PIR)"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "duckdns.org"
    assert result.effective_tld_is_public is False
    assert result.registrable_domain == "fake-apple-login.duckdns.org"
    assert result.registrable_domain_host == "fake-apple-login"
    assert result.fqdn == fqdn
    assert result.pqdn == ""


def test_parse_private_gt2_label_tld():
    fqdn = "stuff.things.something.s3.dualstack.ap-southeast-1.amazonaws.com"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "com"
    assert result.tld_puny is None
    assert result.tld_type == "generic"
    assert result.tld_registry == "VeriSign Global Registry Services"
    assert result.tld_create_date == datetime.strptime('1985-01-01', '%Y-%m-%d').date()
    assert result.effective_tld == "s3.dualstack.ap-southeast-1.amazonaws.com"
    assert result.effective_tld_is_public is False
    assert result.registrable_domain == "something.s3.dualstack.ap-southeast-1.amazonaws.com"
    assert result.registrable_domain_host == "something"
    assert result.fqdn == fqdn
    assert result.pqdn == "stuff.things"


def test_parse_sub_domain():
    fqdn = "login.mail.stuffandthings.co.uk"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert result.tld == "uk"
    assert result.tld_puny is None
    assert result.tld_type == "country-code"
    assert result.tld_registry == "Nominet UK"
    assert result.tld_create_date == datetime.strptime('1985-07-24', '%Y-%m-%d').date()
    assert result.effective_tld == "co.uk"
    assert result.effective_tld_is_public is True
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
    assert result.effective_tld_is_public is True
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


@pytest.mark.skip(reason="stubbing test out to be implemented later")
def test_parse_private_ipv4():
    # test the upper/lower ipv4 values for Class A, B, and C
    fqdn = "65.22.218.1"
    result = Suffixes(read_cache=True).parse(fqdn)
    assert False


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
    assert result.effective_tld_is_public is None
    assert result.registrable_domain is None
    assert result.registrable_domain_host is None
    assert result.pqdn is None
