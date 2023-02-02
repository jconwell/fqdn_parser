
===============
FQDN Parser
===============

*Note: the API is still being fleshed out and subject to change*

-------
Install
-------

To install the release on Pypi (coming soon)

:code:`pip install fqdn-parser`

----
Goal
----

FQDN Parser (Fully Qualified Domain Name Parser) is a library for parsing FQDNs into their component parts,
as well as providing additional contextual information about TLDs, multi-label domain suffixes such as
:code:`.co.uk`, and known private multi-label suffixes, such as :code:`.duckdns.org`.

Data sources used by FQDN Parser:

- TLD data came from parsing the `IANA Root Zone Database <https://www.iana.org/domains/root/db>`_
- Multi-label suffix data came from parsing the `Mozilla Public Suffix List <https://publicsuffix.org/list/public_suffix_list.dat>`_

The library also parses out the "second level domain" and all sub-domains of an FQDN.

-----------
Terminology
-----------

Coming up with a consistent naming convention for each specific part of a FQDN can get a little inconsistent and
confusing.

Take for example :code:`somedomain.co.jp`; many people would call :code:`somedomain` the second level domain (SLD),
but actually the `2nd` level domain is :code:`.co` and :code:`somedomain` is the `3rd` level domain. But since
most domain names have only 2 levels a lot of people have standardized on SLD. But when coding logic to parse FQDNs
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

To give a concrete example take the FQDN :code:`test.integration.api.somedomain.co.jp`

    :code:`tld` - jp

    :code:`effective_tld` - co.jp

    :code:`registrable_domain` - somedomain.co.jp

    :code:`registrable_domain_host` - somedomain

    :code:`fqdn` - test.integration.api.somedomain.co.jp

    :code:`pqdn` - test.integration.api

------------------------------------------------
How is fqdn_parser different than tldextract
------------------------------------------------

`tldextract <https://github.com/john-kurkowski/tldextract>`_ is a great library if all you need to do
is to parse a FQDN to get it's subdomain, domain, or full suffix.

fqdn_parser adds a bit more contextual metadata about each TLD/suffix to use mostly as features in
machine learning projects, including:

- International TLDs in both unicode and puny code format
- The TLD type: generic, generic-restricted, country-code, sponsored, test, infrastructure, and host_suffix (.onion)
- The date the TLD was registered by ICANN
- In the case of multi-label effective TLDs, is it public (owned by a Registrar) or private (owned by a private company)
- If the TLD (or any label in the FQDN) is puny code encoded, the ascii'ification of the unicode. This can be useful for identifying registrable domains that using unicode characters that are very similar to the ascii character used by legitimate domains, a common phishing technique.

-----
Usage
-----

.. code-block:: python

    from fqdn_parser.suffixes import Suffixes
    suffixes = Suffixes(read_cache=True)
    fqdn = "login.mail.stuffandthings.co.uk"
    result = suffixes.parse(fqdn)
    print(result.registrable_domain_host)

----------
TO DO List
----------

- A lot of the suffixes listed in https://publicsuffix.org/list/public_suffix_list.dat are not actually
  recognized TLDs, but are suffixes used for Dynamic DNS (https://en.wikipedia.org/wiki/Dynamic_DNS).
  At some point I'd like parse that information and to pull out Dynamic DNS suffixes from actual TLDs.
- Probably more unit tests
