

def train_sample_generator(file):
    for line in file:
        if line[0] != '>':
            yield line.upper()


def fasta_sample_generator(file):
    lines = file.readlines()[1:]
    seq = ''.join(lines).replace('\n', '').upper()

    length = 1500
    step = 750
    for chunk in [seq[0+i: length+i] for i in range(0,  len(seq)-length, step)]:
        yield chunk
