import pytest
from fqdn_parser.skeleton import get_tld, main

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"


def test_get_tld():
    # test standard 1 label tld
    assert get_tld("stuff.com") == "com"
    # test multi label tld
    assert get_tld("stuff.co.uk") == "co.uk"
    # test unicode tld
    assert get_tld("stuff.手机") == "手机"
    # test puny code tld
    assert get_tld("stuff.xn--kput3i") == "手机"
    # test tld that isn't real
    assert get_tld("stuff.nottld") is None


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["stuff.com"])
    captured = capsys.readouterr()
    assert "com" in captured.out
