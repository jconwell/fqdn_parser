=========
Changelog
=========

Version 1.0
===========

- First stable release

Version 2.0
===========

Changes To How "private suffixes" Are Handled
---------------------------------------------

The "Public Suffix List" (https://publicsuffix.org/list/public_suffix_list.dat) lists all known
public domain suffixes, including both single and multi-label TLDs (.com vs .co.uk).

It also has a section of "Private Suffixes". These are not considered TLDs, but instead are
domain names privately owned by companies that people can get subdomains under. A good example
of this are Dynamic DNS companies. For example, ``duckdns.org`` is a Dynamic DNS provider and you
can register subdomains under ``duckdns.org``.

In v1.0 of fqdn_parser private suffixes were handled just like multi-label TLDs and considered "Effective TLDs"
But this meant the FQDN ``www.duckdns.org`` would incorrectly be parsed with ``duckdns.org`` as the Effective TLD
and ``www`` as the Registrable Host.

v2.0 changes how private suffixes are handled, no longer considering them Effective TLDs, and instead adding a
new property: :code:`ParsedResult.private_suffix` to show the full private suffix substring within the FQDN.

Example:

``api.fake_aws_login.duckdns.org``

    :code:`tld` - org

    :code:`effective_tld` - org

    :code:`registrable_domain` - duckdns.org

    :code:`registrable_domain_host` - duckdns

    :code:`private_suffix` - duckdns.org

    :code:`fqdn` - api.fake_aws_login.duckdns.org

    :code:`pqdn` - api.fake_aws_login

A more complex example, using the private suffix ``cdn.prod.atlassian-dev.net``

``assets.some_company.cdn.prod.atlassian-dev.net``

    :code:`tld` - net

    :code:`effective_tld` - net

    :code:`registrable_domain` - atlassian-dev.net

    :code:`registrable_domain_host` - atlassian-dev

    :code:`private_suffix` - cdn.prod.atlassian-dev.net

    :code:`fqdn` - assets.some_company.cdn.prod.atlassian-dev.net

    :code:`pqdn` - assets.some_company

So if you want to know if a FQDN has a Private Suffix just check the :code:`ParsedResult.private_suffix` property.

Minor Changes:
--------------

- Significant refactor / restructure of the code directory to organize helper modules better.
- Removed skeleton.py as I don't think a CLI version is useful. This can be revisited later if needed
- Added more unit tests (yay!)

Version 2.1
===========

Domain Name & FQDN Entropy
--------------------------

- Added module to calculate entropy for domain names and FQDNs using a correct and up to date character probability distribution.

Version 2.2
===========

Updated TLD list from ICANN
--------------------------

- Updated the TLD registration date cache file. Total number of registered TLDs went from 1,506 in Feb 2023 down to 1,458 in Nov 2023.
