import random
import os
import re
import time
import requests
from bs4 import BeautifulSoup

"""
The only place I found the TLD creation date was on the IANA page for each individual TLD.
This would take WAY too long (and not to mention probably make IANA mad) if this was parsed
each time the data cache was refreshed with live data. 

So this script parses the TLD creation dates from the IANA html and then saves it in a separate 
data file from the TLD data cache to be used when building the full TLD metadata data structure
"""

tld_list_url = "https://www.iana.org/domains/root/db"
delegation_link_prefix = "https://www.iana.org"
reg_date_prefix = "Registration date"
revoked_tld = "Not assigned"
reg_date_pattern = re.compile(r'.+Registration date \d{4}-\d{2}-\d{2}.+')


def get_http_response(url, attempts=3, backoff=2):
    for i in range(attempts):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"{url} error {response.status_code}")
            return response
        except Exception as e:
            print(f"Error getting {url}: {e}, attempt {i}")
            time.sleep(1 * backoff)
    raise Exception(f"Unable to get {url} after {attempts} attempts")


def collect_tld_reg_dates(writer, cache):
    response = get_http_response(tld_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", class_="iana-table", id="tld-table")
    table = table.find("tbody")
    tld_rows = table.find_all("tr")
    for i, tld_row in enumerate(tld_rows):
        data = tld_row.find_all("td")
        if len(data) != 3:
            raise Exception("IANA tld html format changed")
        # parse out tld and delegation record link
        link = data[0].find("a")
        delegation_link = delegation_link_prefix + link["href"]
        # this is brittle, but parsing out the right to left and L2R unicode chars
        tld = link.text.replace(".", "").replace('‏', '').replace('‎', '')
        if tld not in cache:
            # parse the TLD registry
            registry = data[2].text
            # only collect active TLDs
            if registry != revoked_tld:
                reg_date = collect_tld_reg_date(tld, delegation_link)
                writer.write(f"{tld},{reg_date}\n")
                # flush after each TLD just to be sure we get the line and don't have to reparse that page
                writer.flush()
                # let's not make IANA mad
                time.sleep(random.randint(1, 4))
                # if i % 60 == 0:
                print(f"Registration date for TLD '{tld}' is {reg_date} ({i} of {len(tld_rows)})")
            else:
                print(f"Skipping TLD '{tld}' because it was revoked")
        else:
            print(f"Skipping TLD '{tld}'")


def collect_tld_reg_date(tld, delegation_link):
    response = get_http_response(delegation_link)
    reg_date = None
    soup = BeautifulSoup(response.content, 'html.parser')
    lines = soup.find_all("i", string=reg_date_pattern)
    if len(lines) == 0:
        raise Exception(f"IANA tld html format changed for '{tld}': {delegation_link}")
    lines = lines[0].text.split("\n")
    for line in lines:
        line = line.strip()
        if "Registration date " in line:
            reg_date = line[18:28]
            break
    if reg_date is None:
        raise Exception(f"IANA tld html format changed for '{tld}': {delegation_link}")
    return reg_date


def main():
    version = "v2"
    tld_reg_date_path = f"tld_reg_dates_{version}.txt"
    cache = {}
    if os.path.exists(tld_reg_date_path):
        with open(tld_reg_date_path, "r") as handle:
            for line in handle.readlines():
                parts = line.strip().split(",")
                tld = parts[0]
                reg_date = parts[1]
                cache[tld] = reg_date
    with open(tld_reg_date_path, "a") as handle:
        collect_tld_reg_dates(handle, cache)


if __name__ == "__main__":
    main()
