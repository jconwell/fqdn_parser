
===========
FQDN Parser
===========

*Note: the API is still being fleshed out and subject to change*

--------
Overview
--------

FQDN Parser (Fully Qualified Domain Name Parser) is a library used to (surprise!) parse FQDNs into their component parts,
including subdomains, domain names, and the `public suffix <https://publicsuffix.org/list/public_suffix_list.dat>`_.

It also provides additional contextual metadata about the domain's publix suffix including:

- International TLDs in both unicode and puny code format
- The TLD type: generic, generic-restricted, country-code, sponsored, test, infrastructure, and host_suffix (.onion)
- The date the TLD was registered with ICANN
- In the case of multi-label effective TLDs, is it public like :code:`.co.uk` which is owned by a Registrar or private like :code:`.duckdns.org` which is owned by a private company
- If the TLD (or any label in the FQDN) is puny code encoded, the ascii'ification of the unicode. This can be useful for identifying registrable domains that use unicode characters that are very similar to ascii characters used by legitimate domains, a common phishing technique.

The suffix metadata can be used as contextual features for machine learning models that generate predictions about domain names and FQDNs.

---------------------------------
Data sources used by FQDN Parser:
---------------------------------

- TLD metadata comes from the `IANA Root Zone Database <https://www.iana.org/domains/root/db>`_
- Multi-label suffix data comes from the `Mozilla Public Suffix List <https://publicsuffix.org/list/public_suffix_list.dat>`_

The first time fqdn_parser is run, it will perform two http calls to the links above to pull down the latest ICANN and
Public Suffix List information. This may take a few seconds to pull the data down, parse, and persist into a cache file.
Subsequent calls to fqdn_parser will use the existing cache file and be much faster. The cache file can be managed via
arguments to the :code:`Suffixes` class constructor.

-----------
Terminology
-----------

Coming up with a consistent naming convention for each specific part of a FQDN can get a little inconsistent and
confusing.

Take for example :code:`somedomain.co.jp`; many people would call :code:`somedomain` the second level domain, or SLD,
but actually the `2nd` level domain is :code:`.co` and :code:`somedomain` is the `3rd` level domain. But since
most domain names have only 2 levels a lot of people have standardized on SLD. But when writing code logic to parse FQDNs
it is way more clear to be pedantic about naming.

This library uses a very specific naming convention in order to be explicitly clear about what every label means.

    :code:`tld` - the actual top level domain of the FQDN. This is the domain that is controlled by IANA.

    :code:`effective_tld` - this is the full domain suffix, which can be made up of 1 to many labels. The effective
    TLD is the thing a person chooses to register a domain under and is controlled by a Registrar, or in the case of
    private domain suffixes the company that owns the private suffix (like DuckDNS).

    :code:`registrable_domain` - this is the full domain name that a person registers with a Registrar and includes the
    effective tld.

    :code:`registrable_domain_host` - this is the label of the registrable domain without the effective tld. Most people
    call this the second level domain, but as you can see this can get confusing.

    :code:`fqdn` (Fully Qualified Domain Name) - this is the full list of labels.

    :code:`pqdn` (Partially Qualified Domain Name) - this is the  list of sub-domains in a FQDN, not including the
    registrable domain and the effective TLD.

To give a concrete example of these names, take the FQDN :code:`test.integration.api.somedomain.co.jp`

    :code:`tld` - jp

    :code:`effective_tld` - co.jp

    :code:`registrable_domain` - somedomain.co.jp

    :code:`registrable_domain_host` - somedomain

    :code:`fqdn` - test.integration.api.somedomain.co.jp

    :code:`pqdn` - test.integration.api

----------------------------------------------------------------
Doesn't tldextract do this for me? How is fqdn_parser different?
----------------------------------------------------------------

`tldextract <https://github.com/john-kurkowski/tldextract>`_ is a great library if all you need to do
is to parse a FQDN to get it's subdomain, domain, or full suffix.

But fqdn_parser adds a bit more contextual metadata about each TLD/suffix, as well as supports punycoded labels within FQDNs

--------------
Usage Examples
--------------

Parse the registrable domain host from a FQDN:

.. code-block:: python

    from fqdn_parser.suffixes import Suffixes
    suffixes = Suffixes(read_cache=True)
    fqdn = "login.mail.stuffandthings.co.uk"
    result = suffixes.parse(fqdn)
    print(result.registrable_domain_host)

-------
Install
-------

To install via Pypi

:code:`pip install fqdn-parser`

----------
To Do List
----------

- A lot of the suffixes listed in https://publicsuffix.org/list/public_suffix_list.dat are not actually
  recognized TLDs, but are suffixes used for Dynamic DNS (https://en.wikipedia.org/wiki/Dynamic_DNS).
  At some point I'd like parse that information and to pull out Dynamic DNS suffixes from actual TLDs.
- Probably more unit tests
