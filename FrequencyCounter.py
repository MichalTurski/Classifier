import itertools
import biopython.bio

from FileParser import *


def count_freq(seq):
    combinations = itertools.combinations_with_replacement('ACGT', 4)
    counts = {i: 0 for i in combinations}
    length = 4
    for chunk in [seq[0+i: length+i] for i in range(0, len(seq)-length)]:
        counts[chunk] += 1

    to_delete = {}
    for pair in counts.items():
        key = pair[0]
        reversed_key = biopython.bio.reverse_complement(key)
        if reversed_key not in to_delete:  # if reverse have been in untouched.
            counts[reversed_key] += counts[key]
            to_delete.add(key)  # mark this element as to be deleted
    for key in to_delete:
        counts.pop(key)

    return counts
