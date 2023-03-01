===========
FQDN Parser
===========

-----------------
Update: Feb, 2023 - Project in Flux
-----------------

I'm thinking about adding in a whole bunch of other OSINT'y functionality related to domain names. Kind of a
one stop shop for "*get all the things about this FQDN*".

Not sure what the public API will ultimately look like, but it'll probably morph a bit over the
next few months as I add new things in.

- Domain name / FQDN entropy from an actual relevant character distribution
- WHOIS (via asyncwhois) to get Registrar and registration date, and maybe other fields
- NameServer collection
- x509 cert collection and parsing
- Full URL parsing and support for other protocols (maybe)
- *Anything else? Create an issue and I'll consider adding it*

-------
Install
-------

To install via Pypi

:code:`pip install fqdn-parser`

--------
Overview
--------

FQDN Parser (Fully Qualified Domain Name Parser) is a library used to parse FQDNs into their component parts,
including subdomains, domain names, and their `Public Suffix <https://publicsuffix.org/list/public_suffix_list.dat>`_.

It also provides additional contextual metadata about the domain's TLD including:

- International TLDs in both unicode and puny code format
- The TLD type: generic, generic-restricted, country-code, sponsored, test, infrastructure, and host_suffix (.onion)
- The date the TLD was registered with ICANN
- In the case of multi-label effective TLDs, is it public like :code:`.co.uk` which is owned by a Registrar or private like :code:`.duckdns.org` which is owned by a private company
- If the TLD (or any label in the FQDN) is puny code encoded, the ascii'ification of the unicode. This can be useful for identifying registrable domains that use unicode characters that are very similar to ascii characters used by legitimate domains, a common phishing technique.

The TLD metadata can be used as contextual features for machine learning models that generate predictions about domain names and FQDNs.

---------------------------------
Data sources used by FQDN Parser:
---------------------------------

- TLD metadata comes from the `IANA Root Zone Database <https://www.iana.org/domains/root/db>`_
- Multi-label suffix data comes from the `Mozilla Public Suffix List <https://publicsuffix.org/list/public_suffix_list.dat>`_

The first time fqdn_parser is run, it will perform two http calls to the links above to pull down the latest ICANN and
Public Suffix List information. This may take a few seconds to pull the data down, parse, and persist into a cache file.
Subsequent calls to fqdn_parser will use the existing cache file and be much faster. The cache file can be managed via
arguments to the :code:`Suffixes` class constructor.

Note: As of the last commit there are 9 country code TLDs listed in the Mozilla Public Suffix List that are `not` listed
in the IANA Root Zone Database for some reason. These TLDs are added to the parsing cache file, but you will see a
warning for each TLD like:

    :code:`WARNING: 澳门 not in IANA root zone database. Adding to list of TLDs`

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

--------------
Usage Examples
--------------

Parse the registrable domain host from a FQDN:

.. code-block:: python

    from fqdn_parser.suffixes import Suffixes
    suffixes = Suffixes(read_cache=True)
    fqdn = "login.mail.stuffandthings.co.uk"
    result = suffixes.parse(fqdn)
    # TLD metadata
    print(f"tld: {result.tld}")
    print(f"tld type: {result.tld_type}")
    print(f"tld registry: {result.tld_registry}")
    print(f"tld create date: {result.tld_create_date}")
    print(f"tld punycode: {result.is_tld_punycode}")
    print(f"is tld punycode: {result.tld_puny}")
    print(f"effective tld: {result.effective_tld}")
    print(f"is tld multi part: {result.is_tld_multi_part}")
    # domain name info
    print(f"registrable domain: {result.registrable_domain}")
    print(f"registrable domain host: {result.registrable_domain_host}")
    print(f"fqdn: {result.fqdn}")
    print(f"pqdn: {result.pqdn}")
    print(f"is fqdn (vs ip address): {result.is_fqdn}")
    print(f"is ip (vs fqdn): {result.is_ip}")
    # private suffix
    print(f"private suffix: {result.private_suffix}")

Results

.. code-block:: bash

    tld: uk
    tld type: country-code
    tld registry: Nominet UK
    tld create date: 1985-07-24
    tld punycode: False
    is tld punycode: None
    effective tld: co.uk
    is tld multi part: True
    registrable domain: stuffandthings.co.uk
    registrable domain host: stuffandthings
    fqdn: login.mail.stuffandthings.co.uk
    pqdn: login.mail
    is fqdn (vs ip address): True
    is ip (vs fqdn): False
    private suffix: None

----------------
Private Suffixes
----------------

The "Public Suffix List" also has a section of "Private Suffixes". These are not considered TLDs, but instead are
domain names privately owned by companies that people can purchase or register subdomains under.
A good example of this are Dynamic DNS providers. ``duckdns.org`` is a Dynamic DNS provider and you can
register subdomains under ``duckdns.org``.

Private Suffixes can be identified by inspecting the :code:`ParsedResult.private_suffix` property.

For example, using the above code the FQDN ``api.fake_aws_login.duckdns.org`` will return the following output:

.. code-block:: bash

    tld: org
    tld type: generic
    tld registry: Public Interest Registry (PIR)
    tld create date: 1985-01-01
    tld punycode: False
    is tld punycode: None
    effective tld: org
    is tld multi part: False
    registrable domain: duckdns.org
    registrable domain host: duckdns
    fqdn: api.fake_aws_login.duckdns.org
    pqdn: api.fake_aws_login
    is fqdn (vs ip address): True
    is ip (vs fqdn): False
    private suffix: duckdns.org

Some private suffixes have 3 or more labels. For example, using the private suffix ``cdn.prod.atlassian-dev.net``
the following is the output for the FQDN ``assets.some_company.cdn.prod.atlassian-dev.net``

.. code-block:: bash

    tld: net
    tld type: generic
    tld registry: VeriSign Global Registry Services
    tld create date: 1985-01-01
    tld punycode: False
    is tld punycode: None
    effective tld: net
    is tld multi part: False
    registrable domain: atlassian-dev.net
    registrable domain host: atlassian-dev
    fqdn: assets.some_company.cdn.prod.atlassian-dev.net
    pqdn: assets.some_company.cdn.prod
    is fqdn (vs ip address): True
    is ip (vs fqdn): False
    private suffix: cdn.prod.atlassian-dev.net

----------------------------------------------------------------
Doesn't tldextract do this for me? How is fqdn_parser different?
----------------------------------------------------------------

`tldextract <https://github.com/john-kurkowski/tldextract>`_ is a great library if all you need to do
is to parse a FQDN to get it's subdomain, domain, or full suffix.

But fqdn_parser adds a bit more contextual metadata about each TLD/suffix, as well as supports punycoded labels within FQDNs
