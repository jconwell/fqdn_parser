from dataclasses import dataclass
import pickle


PUNY_PREFIX = "xn--"


def is_puny_code(label):
    return label[:4] == PUNY_PREFIX


class _Node:
    """A node in the trie structure"""

    def __init__(self, label, metadata):
        # the suffix label for this node
        self.label = label
        self.metadata = metadata

        # a dictionary of child labels
        self.children = {}


class _Trie(object):
    """The trie object"""

    def __init__(self):
        self.root = _Node("", None)

    def insert(self, suffix, metadata=None, is_public_suffix=None):
        """Insert a suffix into the trie"""
        node = self.root
        root_metadata = None

        # Loop through each label in suffix in reverse order
        labels = suffix.split(".")[::-1]
        for i, label in enumerate(labels):
            found_node = node.children.get(label)
            if found_node:
                node = found_node
                # set the root's metadata obj if not set yet
                if root_metadata is None:
                    root_metadata = node.metadata
            else:
                if metadata is None:
                    # if no metadata passed in, this is not a root TLD
                    node_suffix = ".".join(labels[0:i+1][::-1])
                    metadata = _SuffixInfo(node_suffix, is_public_suffix, root_metadata)
                new_node = _Node(label, metadata)
                node.children[label] = new_node
                node = new_node
                if isinstance(metadata, _SuffixInfo):
                    metadata = None

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

    def get_longest_sequence(self, fqdn, puny_suffixes):
        """
        Returns the longest trie sequence found in the trie tree
        """
        node = self.root
        labels = fqdn.split(".")
        rev_labels = labels[::-1]

        if is_puny_code(rev_labels[0]):
            # if puny code tld is passed in, turn it to unicode and look it up
            rev_labels[0] = puny_suffixes[rev_labels[0]]

        for i, label in enumerate(rev_labels):
            if label in node.children:
                node = node.children[label]
            else:
                break
        if node:
            return node.metadata, labels[:-i]
        return None


@dataclass
class _TLDInfo:
    """  """
    suffix: str
    puny: str
    tld_type: str
    registry: str
    create_date: object


@dataclass
class _SuffixInfo:
    """  """
    suffix: str
    is_public: bool
    root_suffix: object
    # is_dynamic_dns


def save_trie(cache_path, _suffix_trie, _puny_suffixes):
    with open(cache_path, 'wb') as handle:
        pickle.dump((_suffix_trie, _puny_suffixes), handle)


def load_trie(cache_path):
    with open(cache_path, 'rb') as handle:
        suffix_trie, puny_suffixes = pickle.load(handle)
        return suffix_trie, puny_suffixes
