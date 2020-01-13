import itertools
import Bio.Seq


def count_freq(seq):
    combinations = itertools.product('ACGT', repeat=4)
    counts = {''.join(i): 0 for i in combinations}
    if 'N' not in seq:
        length = 4
        for chunk in [seq[0+i: length+i] for i in range(0, len(seq)-length)]:
            counts[chunk] += 1

    to_delete = set()
    for pair in counts.items():
        key = pair[0]
        reversed_key = Bio.Seq.reverse_complement(key)
        if reversed_key not in to_delete and reversed_key != key:  # if reverse have been in untouched.
            counts[reversed_key] += counts[key]
            to_delete.add(key)  # mark this element as to be deleted
    for key in to_delete:
        counts.pop(key)

    factor = sum(counts.values())
    if factor != 0:
        for k in counts:
            counts[k] = counts[k]/factor

    return counts
