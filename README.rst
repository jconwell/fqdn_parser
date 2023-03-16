===========
FQDN Parser
===========

-------------------
Update: March, 2023
-------------------

I'm thinking about adding in a whole bunch of other OSINT'y functionality related to domain names. Kind of a
one stop shop for "*get all the things about this FQDN*".

- x509 cert collection and parsing
- WHOIS (via asyncwhois) to get Registrar and registration date, and maybe other fields
- NameServer collection
- Full URL parsing and support for other protocols (maybe)
- DNS record collection and parsing
- *Anything else? Create an issue and I'll consider adding it*

-------
Install
-------

To install via Pypi

:code:`pip install fqdn_parser==2.1.6`

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

Private Suffixes can be identified by checking the :code:`ParsedResult.is_private_suffix` property. To see the value of the private suffix use :code:`ParsedResult.private_suffix`.

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

--------------------------------------
Domain Name & FQDN Entropy Calculation
--------------------------------------

The entropy of a domain name or FQDN can be contextually useful when trying to assess if the domain or FQDN is malicious or not, i.e. if it was generated by a DGA (Domain Generation Algorithm).

I'm not going to go into the details of how entropy is calculated, but if you're interested in learning more about it, check out RedCanary's great `post on using entropy in threat hunting <https://redcanary.com/blog/threat-hunting-entropy/>`_.

One important aspect when calculating entropy is that it's done using an appropriate probability distribution. This means for domains and FQDNs you need a probability distribution of characters pulled from a large representative sample of internet traffic.

The following code example downloads the Cisco Umbrella Top 1 Million FQDNs and calculate the character probability distribution for both domain names and FQDNs to be used in entropy calculations, it then caches it for future uses.

.. code-block:: python

    from entropy.char_probabilities import update_char_probabilities
    from fqdn_parser.suffixes import Suffixes
    char_probs_file = "char_probs.cache"
    suffixes = Suffixes()
    char_probs = update_char_probabilities(suffixes, cache_path=char_probs_file)
    print("Domain Name Character Probability Distribution")
    print(char_probs.domain_char_probs)
    print("FQDN Character Probability Distribution")
    print(char_probs.fqdn_char_probs)

.. code-block:: bash

    Domain Name Character Probability Distribution
    {'-': 0.009153964706906638, '0': 0.0016562571439772676, '1': 0.0023782284412904448, '2': 0.0022458500651963502, '3': 0.0016058515315414393, '4': 0.0013960827201923356, '5': 0.001050371499546604, '6': 0.0009709444738901473, '7': 0.0007672854337453864, '8': 0.0009154473854507, '9': 0.0008355112121938813, 'a': 0.08520788751096577, 'b': 0.02146515368365743, 'c': 0.04584874141258929, 'd': 0.03435829836762188, 'e': 0.10087130428849932, 'f': 0.016597702624197647, 'g': 0.02409795592512883, 'h': 0.025066354661017164, 'i': 0.07043395159126445, 'j': 0.0039570951500127035, 'k': 0.015794267710826565, 'l': 0.048940794789587114, 'm': 0.033398555140939694, 'n': 0.061210742810708596, 'o': 0.06914784475275029, 'p': 0.03190777096708004, 'q': 0.0024668201237534157, 'r': 0.06578085167155703, 's': 0.06751399010318894, 't': 0.06583125728399286, 'u': 0.02948931986536101, 'v': 0.01482383238453678, 'w': 0.013819284169022747, 'x': 0.006708528782368422, 'y': 0.017273341489877893, 'z': 0.005012558125562927}
    FQDN Character Probability Distribution
    {'-': 0.03935146304604875, '0': 0.01137667745062195, '1': 0.015695464981033407, '2': 0.010750418092344973, '3': 0.008382589095779713, '4': 0.0075158871514849086, '5': 0.006856249546264456, '6': 0.0060167866356360235, '7': 0.005506159061413232, '8': 0.005164806882403787, '9': 0.004782506746876184, 'a': 0.07701803986960072, 'b': 0.02079500546986022, 'c': 0.048182095503032235, 'd': 0.04067491053735759, 'e': 0.08384591790596323, 'f': 0.017997669959947296, 'g': 0.02456907193095662, 'h': 0.01635373169396868, 'i': 0.05605912336564308, 'j': 0.00319274852816832, 'k': 0.012453364330598661, 'l': 0.03980957948534796, 'm': 0.030834407298296743, 'n': 0.05459673892143202, 'o': 0.061688603128709975, 'p': 0.03616217155059957, 'q': 0.002987829933540334, 'r': 0.05214641797170645, 's': 0.06301449438452718, 't': 0.05198459307804299, 'u': 0.026606098658707066, 'v': 0.01602358506929026, 'w': 0.015229659624134714, 'x': 0.008538811212277663, 'y': 0.011672849788232905, 'z': 0.006163472110150122}


Note: generating character probabilities will takes a few minutes. If you don't want to wait this repo has a cache file checked into it. Feel free to download the file ``char_probs.cache`` to use for the character probability distribution, but note it will not be up to date.

Load cached character probability distributions from file:

.. code-block:: python

    from entropy.char_probabilities import load_char_probabilities
    char_probs_file = "char_probs.cache"
    char_probs = load_char_probabilities(cache_path=char_probs_file)

Calculate entropy of domain names. Note the higher entropy score for the random keyboard-smash domain name):

.. code-block:: python

    from entropy.char_probabilities import load_char_probabilities
    from entropy.domain_entropy import domain_entropy
    from fqdn_parser.suffixes import Suffixes
    char_probs_file = "char_probs.cache"
    char_probs = load_char_probabilities(cache_path=char_probs_file)
    suffixes = Suffixes()
    # normal domain name
    result = suffixes.parse("amazon.com")
    entropy = domain_entropy(result, char_probs)
    print(f"Entropy for {result.registrable_domain_host}: {entropy}")
    # random keyboard smash domain name
    result = suffixes.parse("lk3k3l24jlk23.com")
    entropy = domain_entropy(result, char_probs)
    print(f"Entropy for {result.registrable_domain_host}: {entropy}")

.. code-block:: bash

    Entropy for amazon: 2.3374190580082232
    Entropy for lk3k3l24jlk23: 4.775453277222541

Calculate entropy of the full FQDNs:

.. code-block:: python

    from entropy.char_probabilities import load_char_probabilities
    from entropy.domain_entropy import fqdn_entropy
    from fqdn_parser.suffixes import Suffixes
    char_probs_file = "char_probs.cache"
    char_probs = load_char_probabilities(cache_path=char_probs_file)
    suffixes = Suffixes()
    # normal FQDN labels
    result = suffixes.parse("stuff.things.amazon.com")
    entropy = fqdn_entropy(result, char_probs)
    print(f"Entropy for fqdn {result.fqdn}: {entropy}")
    # random chars for FQSN labels
    result = suffixes.parse("sdlfkjj.slkfdjs.lk3k3l24jlk23.com")
    entropy = fqdn_entropy(result, char_probs)
    print(f"Entropy for fqdn {result.fqdn}: {entropy}")

.. code-block:: bash

    Entropy for fqdn stuff.things.amazon.com: 1.2618222896338356
    Entropy for fqdn sdlfkjj.slkfdjs.lk3k3l24jlk23.com: 2.9639747128498106

Calculating the entropy of each label in a FQDN separately can be useful when DGAs are used to generate subdomains on non-DGA domain names:

.. code-block:: python

    from entropy.char_probabilities import load_char_probabilities
    from entropy.domain_entropy import relative_entropy
    from fqdn_parser.suffixes import Suffixes
    char_probs_file = "char_probs.cache"
    char_probs = load_char_probabilities(cache_path=char_probs_file)
    suffixes = Suffixes()
    # normal domain name with DGA looking subdomain labels
    result = suffixes.parse("h3ksd7.8c3hs.somecooldomain.com")
    for label in result.host_labels:
        entropy = relative_entropy(label, char_probs.fqdn_char_probs)
        print(f"Entropy for label {label}: {entropy}")

.. code-block:: bash

    Entropy for label h3ksd7: 3.293799636685838
    Entropy for label 8c3hs: 3.4367171238803156
    Entropy for label somecooldomain: 1.1479845021804367

Note the higher entropy scores for the DGA looking subdomain labels compared to the entropy of the registrable domain name.