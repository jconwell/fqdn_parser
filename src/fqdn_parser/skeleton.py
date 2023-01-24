"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         get_tld = fqdn_parser.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the following commands inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys

from fqdn_parser import __version__

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"

from fqdn_parser.suffixes import Suffixes

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from fqdn_parser.skeleton import get_tld`,
# when using this Python module as a library.

def get_tld(fqdn):
    """ return the longest known TLD/suffix for a FQDN """
    suffix = Suffixes().get_tld(fqdn)
    return suffix


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Parse FQDNs to return the TLD or longest known public domain suffix")
    parser.add_argument(
        "--version",
        action="version",
        version="fqdn_parser {ver}".format(ver=__version__),
    )
    parser.add_argument(
        dest="fqdn",
        help="return the tld for the fqdn",
        type=str,
        metavar="STR"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing :func:`get_tld` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`get_tld`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting TLD parser")
    print(f"The tld for {args.fqdn} is {get_tld(args.fqdn)}")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m fqdn_parser.skeleton 42
    #
    run()
