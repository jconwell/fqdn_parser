












def main():
    """
    Compare two versions of the tld_reg_dates files to see what changed between versions
    """
    version_a = "v1"
    version_b = "v2"
    path_a = f"tld_reg_dates_{version_a}.txt"
    path_b = f"tld_reg_dates_{version_b}.txt"
    cache_a = set()
    with open(path_a, "r") as handle:
        for line in handle.readlines():
            parts = line.strip().split(",")
            tld = parts[0]
            cache_a.add(tld)
    cache_b = set()
    with open(path_b, "r") as handle:
        for line in handle.readlines():
            parts = line.strip().split(",")
            tld = parts[0]
            cache_b.add(tld)

    print(f'Version {version_a} has {len(cache_a)} TLDs')
    print(f'Version {version_b} has {len(cache_b)} TLDs')
    delta_a = cache_a - cache_b
    print(f'{len(delta_a)} TLDs in {version_a} but not in {version_b}')
    for tld in delta_a:
        print(f"\tOnly in {version_a}: {tld}")
    delta_b = cache_b - cache_a
    print(f'{len(delta_b)} TLDs in {version_b} but not in {version_a}')
    for tld in delta_b:
        print(f"\tOnly in {version_b}: {tld}")
    print(f'{len(delta_a.intersection(delta_b))} TLDs in both versions')


if __name__ == "__main__":
    main()