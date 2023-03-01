from dataclasses import dataclass
import pickle

__author__ = "John Conwell"
__copyright__ = "John Conwell"
__license__ = "MIT"

PUNY_PREFIX = "xn--"


def is_punycode(label: str):
    """ Check if string is punycode

    Args:
        label (str): string to be checked

    Returns: True if string is punycode
    """
    return label[:4] == PUNY_PREFIX


class SuffixNode:
    def __init__(self, label, puny, tld_type, registry, create_date, suffix, is_private):
        # the label for this node in the trie structure
        self.label = label
        # punycode value of the TLD
        self.puny = puny
        # the type of TLD
        self.tld_type = tld_type
        # the registry that owns the TLD
        self.registry = registry
        # date the TLD was created
        self.create_date = create_date
        # The suffix for this node. This is the label concatenated with all parent nodes
        self.suffix = suffix
        # if this suffix private
        self.is_private = is_private
        # a dictionary of child labels
        self.children = {}
        # pointer up to the parent node
        self.parent = None

    def get_tld_node(self):
        node = self
        while len(node.parent.label) > 0:
            # loop until we hit the root trie node with no label
            node = node.parent
        return node

    def get_effective_tld_node(self):
        node = self
        while node.is_private:
            node = node.parent
        return node

    def __str__(self):
        return f"{self.label} ({len(self.children)} children)"


class Trie(object):
    """The trie object"""

    def __init__(self):
        # init trie with empty node
        self.root = SuffixNode("", None, None, None, None, None, None)

    def insert_tld_node(self, label, puny, tld_type, registry, create_date):
        """Insert a tld node into the trie"""
        node = SuffixNode(label, puny, tld_type, registry, create_date, label, False)
        # set parent and children
        node.parent = self.root
        self.root.children[node.label] = node

    def insert_suffix_node(self, suffix, is_private_suffix: bool):
        parent_node = self.root
        # Loop through each label in suffix in reverse order
        labels = suffix.split(".")[::-1]
        for i, label in enumerate(labels):
            found_node = parent_node.children.get(label)
            if found_node:
                parent_node = found_node
            else:
                # found a new suffix in trie
                node_suffix = ".".join(labels[0:i + 1][::-1])
                node = SuffixNode(label, parent_node.puny, parent_node.tld_type, parent_node.registry,
                                  parent_node.create_date, node_suffix, is_private_suffix)
                # set parent and children
                node.parent = parent_node
                parent_node.children[label] = node
                # set parent for the next label in the loop
                parent_node = node

    def get_node(self, labels):
        node = self.root
        labels = labels[::-1]
        for i, label in enumerate(labels):
            tmp = node.children.get(label)
            if tmp:
                node = tmp
        if node == self.root:
            return None
        return node

    def get_longest_sequence(self, fqdn, puny_suffixes, public_only=False):
        """
        Returns the longest trie sequence found in the trie tree
        """
        node = self.root
        labels = fqdn.split(".")
        rev_labels = labels[::-1]

        if is_punycode(rev_labels[0]):
            # if puny code tld is passed in, turn it to unicode and look it up
            rev_labels[0] = puny_suffixes[rev_labels[0]]

        i = 0
        for label in rev_labels:
            if label in node.children:
                tmp = node.children[label]
                if public_only and tmp.is_private:
                    # if the next node is private suffix, and we want only public then shortcut the search
                    break
                if tmp.is_private is False:
                    # only increment i for public suffixes
                    i += 1
                node = node.children[label]
            else:
                break
        if node and len(node.label) > 0:
            return node, labels[:-i]
        return None, None


def save_trie(cache_path, _suffix_trie, _puny_suffixes):
    with open(cache_path, 'wb') as handle:
        pickle.dump((_suffix_trie, _puny_suffixes), handle)


def load_trie(cache_path):
    with open(cache_path, 'rb') as handle:
        suffix_trie, puny_suffixes = pickle.load(handle)
        return suffix_trie, puny_suffixes
